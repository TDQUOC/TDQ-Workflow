"""Process ownership and isolation are checked with real child processes."""
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import tdq_test_process as process


def python(code):
    return [sys.executable, "-c", code]


def test_isolation_and_parent_environment(tmp_path):
    original = dict(os.environ)
    with process.IsolatedJob(tmp_path) as job:
        result = job.run(python(
            "import os,json,tempfile; print(json.dumps({k:os.environ[k] "
            "for k in ['HOME','USERPROFILE','TMP','TEMP',"
            "'TDQ_KHONG_CHAM_MAY','TDQ_KHOI_TAO_NEN']}))"), phase="run")
        private = json.loads(result["stdout"])
        assert private["HOME"] == private["USERPROFILE"]
        assert Path(private["HOME"]).is_relative_to(job.root)
        assert private["TDQ_KHONG_CHAM_MAY"] == "1"
        assert private["TDQ_KHOI_TAO_NEN"] == "0"
        assert result["exit_code"] == 0
        assert result["cleanup_complete"]
        root = job.root
    assert not root.exists()
    assert dict(os.environ) == original


def test_nonzero_and_large_output(tmp_path):
    with process.IsolatedJob(tmp_path) as job:
        result = job.run(python(
            "import sys; print('a'*150000); print('b'*150000, "
            "file=sys.stderr); sys.exit(7)"), phase="run")
    assert result["exit_code"] == 7
    assert len(result["stdout"]) >= 150000
    assert len(result["stderr"]) >= 150000
    assert result["cleanup_complete"]
    assert not result["timed_out"]
    assert result["duration_seconds"] == result["wall_seconds"]
    assert result["execute_seconds"] + result["cleanup_seconds"] == pytest.approx(
        result["wall_seconds"])


def test_timeout_shared_across_phases(tmp_path):
    with process.IsolatedJob(tmp_path, timeout_seconds=1.3) as job:
        first = job.run(python("import time; time.sleep(.7)"), phase="collect")
        second = job.run(python("import time; time.sleep(2)"), phase="execute")
    assert first["exit_code"] == 0
    assert second["timed_out"]
    assert second["cleanup_complete"]
    assert second["duration_seconds"] < 1.2


def test_cancel_event(tmp_path):
    cancel = threading.Event()
    timer = threading.Timer(.4, cancel.set)
    with process.IsolatedJob(tmp_path, cancel_event=cancel) as job:
        timer.start()
        result = job.run(python("import time; time.sleep(20)"), phase="run")
    timer.join()
    assert result["cancelled"]
    assert not result["timed_out"]
    assert result["cleanup_complete"]


def test_keyboard_interrupt_cleans_real_process(tmp_path, monkeypatch):
    def interrupt(child):
        time.sleep(.2)
        raise KeyboardInterrupt
    with process.IsolatedJob(tmp_path) as job:
        monkeypatch.setattr(job, "_wait", interrupt)
        result = job.run(python("import time; time.sleep(20)"), phase="run")
    assert result["cancelled"]
    assert result["cleanup_complete"]


@pytest.mark.parametrize("value", [0, -1, float("nan"), float("inf")])
def test_invalid_timeout(tmp_path, value):
    with pytest.raises(ValueError):
        process.IsolatedJob(tmp_path, timeout_seconds=value)


def test_no_spawn_after_deadline(tmp_path):
    marker = tmp_path / "unexpected"
    with process.IsolatedJob(tmp_path, timeout_seconds=.02) as job:
        time.sleep(.04)
        result = job.run(python(f"open({str(marker)!r},'w').close()"), phase="run")
    assert result["timed_out"]
    assert not marker.exists()


def test_owned_job_preserves_environment_without_pytest_layer(tmp_path, monkeypatch):
    caller = {"HOME": str(tmp_path / "caller-home"), "USERPROFILE": str(tmp_path / "caller-profile"),
              "CODEX_HOME": str(tmp_path / "codex"), "TDQ_TEST_JOB_ROOT": "caller-marker",
              "PYTHONPATH": "caller-pythonpath", "PYTEST_CURRENT_TEST": "caller-test"}
    for name, value in caller.items():
        monkeypatch.setenv(name, value)
    expected = dict(os.environ)
    with process.OwnedProcessJob(tmp_path) as job:
        root = job.root
        result = job.run(python("import json,os,sys; print(json.dumps({k:os.environ.get(k) for k in "
            + repr(list(caller)) + "})); print(json.dumps({'eof':sys.stdin.read() == '', 'tty':sys.stdin.isatty()}))"), phase="owned")
        environment, stdin = map(json.loads, result["stdout"].splitlines())
        assert environment == caller
        assert stdin == {"eof": True, "tty": os.name == "nt"}  # Windows NUL reports isatty.
        assert result["cleanup_complete"] and result["ownership"]["verified"]
        assert job.env == expected
        assert root.is_dir()
    assert not root.exists()
    assert dict(os.environ) == expected


def test_isolated_sanitizes_pytest_identity_before_enter(tmp_path):
    identities = {key: "caller" for key in ("PYTEST_XDIST_WORKER", "PYTEST_XDIST_WORKER_COUNT",
        "PYTEST_XDIST_TESTRUNUID", "PYTEST_CURRENT_TEST")}
    job = process.IsolatedJob(tmp_path, env=identities)
    assert not set(identities).intersection(job.env)


def test_cleanup_shares_one_budget(monkeypatch):
    clock = [100.0]
    waits = []
    class Owner:
        def stop(self, deadline):
            assert deadline == 105.0
            clock[0] = 104.75
            return True
        def close(self):
            waits.append("closed")
    class Child:
        def wait(self, timeout):
            waits.append(timeout)
            clock[0] += timeout
            return 0
    monkeypatch.setattr(process.time, "monotonic", lambda: clock[0])
    complete, elapsed = process.OwnedProcessJob._cleanup(Owner(), Child())
    assert complete
    assert waits == [.25, "closed"]
    assert elapsed == 5.0


def test_missing_command_is_error(tmp_path):
    with process.IsolatedJob(tmp_path) as job:
        result = job.run([str(tmp_path / "missing-executable")], phase="run")
    assert result["exit_code"] != 0
    assert result["cleanup_complete"]


@pytest.mark.skipif(os.name != "nt", reason="Windows Job Object proof")
@pytest.mark.parametrize("mode", ["timeout", "cancel", "parent-exit"])
def test_owned_grandchildren_stop_but_control_survives(tmp_path, mode):
    heartbeat = tmp_path / "heartbeat"
    child_pid = tmp_path / "pid"
    grandchild = (
        "import time,os; from pathlib import Path; "
        f"Path({str(child_pid)!r}).write_text(str(os.getpid())); "
        f"p=Path({str(heartbeat)!r}); "
        "exec('while True:\\n p.write_text(str(time.time_ns()))\\n time.sleep(.03)')"
    )
    parent = (
        "import subprocess,sys,time; "
        f"subprocess.Popen([sys.executable,'-c',{grandchild!r}]); "
        + ("time.sleep(.5)" if mode == "parent-exit" else "time.sleep(30)")
    )
    cancel = threading.Event()
    timer = threading.Timer(1.0, cancel.set)
    control = subprocess.Popen(python("import time; time.sleep(30)"))
    try:
        with process.IsolatedJob(tmp_path, timeout_seconds=1.5,
                                 cancel_event=cancel) as job:
            if mode == "cancel":
                timer.start()
            result = job.run(python(parent), phase="tree")
        assert child_pid.exists(), result
        assert result["cleanup_complete"], result
        assert result["ownership"]["mechanism"] == "windows-job"
        last = heartbeat.read_text()
        time.sleep(.15)
        assert heartbeat.read_text() == last
        assert not process._windows_pid_alive(int(child_pid.read_text()))
        assert control.poll() is None
    finally:
        timer.cancel()
        control.terminate()
        control.wait(timeout=5)


@pytest.mark.skipif(os.name != "nt", reason="Windows assign-before-launch proof")
def test_assign_failure_never_launches_target(tmp_path, monkeypatch):
    marker = tmp_path / "should-not-run"
    def reject(self, child):
        raise OSError("simulated assignment denial")
    monkeypatch.setattr(process._WindowsJob, "assign", reject)
    with process.IsolatedJob(tmp_path) as job:
        result = job.run(python(f"open({str(marker)!r},'w').close()"), phase="run")
    assert result["reason"] == "launch-error"
    assert result["exit_code"] is None
    assert not marker.exists()
    assert result["cleanup_complete"]


@pytest.mark.skipif(os.name != "nt", reason="Windows owner crash proof")
def test_owner_crash_closes_job_handle(tmp_path):
    heartbeat = tmp_path / "crash-heartbeat"
    pid_file = tmp_path / "crash-pid"
    child = (
        "import time,os; from pathlib import Path; "
        f"Path({str(pid_file)!r}).write_text(str(os.getpid())); "
        f"p=Path({str(heartbeat)!r}); "
        "exec('while True:\\n p.write_text(str(time.time_ns()))\\n time.sleep(.03)')"
    )
    owner_code = (
        f"import sys; sys.path.insert(0,{str(Path(process.__file__).parent)!r}); "
        "from tdq_test_process import IsolatedJob; "
        f"job=IsolatedJob({str(tmp_path)!r}); job.__enter__(); "
        f"job.run([sys.executable,'-c',{child!r}],phase='owner-crash')"
    )
    owner = subprocess.Popen(python(owner_code), stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
    try:
        deadline = time.monotonic() + 5
        while not heartbeat.exists() and time.monotonic() < deadline:
            time.sleep(.03)
        assert heartbeat.exists()
        owner.kill()
        owner.wait(timeout=5)
        pid = int(pid_file.read_text())
        deadline = time.monotonic() + 3
        while process._windows_pid_alive(pid) and time.monotonic() < deadline:
            time.sleep(.03)
        assert not process._windows_pid_alive(pid)
    finally:
        if owner.poll() is None:
            owner.kill()
            owner.wait(timeout=5)


@pytest.mark.skipif(os.name == "nt", reason="POSIX proof requires actual POSIX host")
def test_posix_process_group_cleanup(tmp_path):
    marker = tmp_path / "posix-heartbeat"
    child = ("import time; from pathlib import Path; "
             f"p=Path({str(marker)!r}); "
             "exec('while True:\\n p.write_text(str(time.time_ns()))\\n time.sleep(.03)')")
    parent = ("import subprocess,sys,time; "
              f"subprocess.Popen([sys.executable,'-c',{child!r}]); time.sleep(20)")
    with process.IsolatedJob(tmp_path, timeout_seconds=1) as job:
        result = job.run(python(parent), phase="group")
    assert result["timed_out"]
    assert result["cleanup_complete"]
    previous = marker.read_text()
    time.sleep(.15)
    assert marker.read_text() == previous


def test_worker_homes_and_tmp_path(tmp_path):
    (tmp_path / "conftest.py").write_text(
        "import os,pytest\nCAPTURED=os.environ['HOME']\n"
        "@pytest.fixture\ndef collected_home():\n return CAPTURED\n",
        encoding="utf-8")
    for index in range(2):
        (tmp_path / f"test_{index}.py").write_text(
            "import os,json\nfrom pathlib import Path\n"
            "def test_private(tmp_path,collected_home):\n"
            " worker=os.environ['PYTEST_XDIST_WORKER']\n"
            " home=Path(os.environ['HOME'])\n"
            " assert str(home) == collected_home\n"
            " assert home.name == 'home'\n"
            " assert home.parent.name == worker\n"
            " assert tmp_path.exists()\n"
            f" Path({str(tmp_path)!r},worker+'.json').write_text("
            "json.dumps([str(home),str(tmp_path)]))\n", encoding="utf-8")
    with process.IsolatedJob(tmp_path) as job:
        result = job.run([sys.executable, "-m", "pytest", "-q", "-n", "2",
                          "--dist=loadfile", *job.pytest_args(), str(tmp_path)],
                         phase="pytest")
    assert result["exit_code"] == 0, result
    records = [json.loads(p.read_text()) for p in tmp_path.glob("gw*.json")]
    assert len(records) == 2
    assert len({row[0] for row in records}) == 2
    assert len({row[1] for row in records}) == 2


def test_log_scrubs_command_and_can_disable(tmp_path, capsys):
    secret = "secret-value-not-a-log"
    with process.IsolatedJob(tmp_path) as job:
        job.run(python(f"print({secret!r})"), phase="run")
    log = capsys.readouterr().err
    assert "tdq_test_process" in log
    assert secret not in log
    with process.IsolatedJob(tmp_path, env={"TDQ_LOG": "0"}) as job:
        job.run(python("pass"), phase="run")
    assert capsys.readouterr().err == ""
