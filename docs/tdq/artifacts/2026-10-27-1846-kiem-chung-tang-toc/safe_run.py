"""Request-local normal-user test harness; receipts are evidence, not cache eligibility."""
import argparse
import ctypes
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import re
import signal
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import uuid

SCHEMA = "tdq-safe-run/v1"
GENERATED_PREFIXES = (".tdq-worktrees/", "logs/", "graphify-out/",
                      "docs/working-log/", "docs/workinglog/",
                      "docs/tdq/artifacts/", "docs/tdq/cache/", "docs/tdq/reports/",
                      "docs/tdq/report/", "docs/tdq/brief/", "docs/tdq/spec/",
                      "docs/tdq/plan/", "docs/tdq/qc/", "docs/tdq/team/",
                      "docs/tdq/requests/", "docs/tdq/questions/")
GENERATED_FILES = {"docs/tdq/state.json", "docs/tdq/STATE.md",
                   "docs/tdq/timing.jsonl", "docs/tdq/stop_streak.json",
                   "docs/tdq/token-budget.json", "docs/architecture/status.json"}


def digest(value):
    """Hash canonical JSON without publishing its values."""
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def file_hash(path):
    """Hash a file, retaining missing as an explicit state."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    """Atomically publish JSON."""
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def elevated():
    """Return whether this process has administrator/root privileges."""
    if os.name == "nt":
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    return os.geteuid() == 0


def source_snapshot(root):
    """Hash tracked and untracked inputs, excluding generated request evidence."""
    command = ["git", "ls-files", "-co", "--exclude-standard", "-z"]
    result = subprocess.run(command, cwd=root, capture_output=True, check=True)
    files = {}
    for name in sorted(set(result.stdout.decode("utf-8").split("\0")) - {""}):
        if name.startswith(GENERATED_PREFIXES) or name in GENERATED_FILES:
            continue
        path = root / name
        files[name] = file_hash(path) if path.is_file() else "MISSING"
    return {"sha256": digest(files), "files": files,
            "scope": "git inputs; explicit generated exclusions, not hermetic eligibility",
            "excluded_prefixes": list(GENERATED_PREFIXES),
            "excluded_files": sorted(GENERATED_FILES)}


def config_snapshot(home):
    """Record protected configuration digests only, never copy personal content."""
    names = [".claude/CLAUDE.md", ".claude/settings.json", ".claude.json",
             ".codex/AGENTS.md", ".codex/config.toml", ".codex/auth.json"]
    return {name: file_hash(home / name) if (home / name).is_file() else "MISSING"
            for name in names}


def sanitize(text, environment):
    """Redact credential values from command output before persisting it."""
    for key, value in environment.items():
        if len(value) >= 4 and re.search("TOKEN|SECRET|PASSWORD|API_KEY", key, re.I):
            text = text.replace(value, "[REDACTED]")
    text = re.sub(r"(?i)(bearer\s+)[\w.\-]+", r"\1[REDACTED]", text)
    return re.sub(r"(?i)((?:token|password|api_key|secret)\s*[=:]\s*)[^\s,;]+",
                  r"\1[REDACTED]", text)


def resolve_dependencies(root):
    """Discover installed public binaries before HOME isolation; never run setup."""
    path = root / "scripts/archify_delivery.py"
    name = "_tdq_harness_archify_delivery"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
        found = module.find_archify_root()
        entrypoint = module.get_archify_bin(found) if found else None
    finally:
        sys.modules.pop(name, None)
    files, archify_root = {}, None
    if entrypoint is not None:
        entrypoint = entrypoint.resolve(strict=True)
        archify_root = str(entrypoint.parent.parent)
        for target in (entrypoint, entrypoint.parent.parent / "package.json"):
            files[str(target)] = file_hash(target) if target.is_file() else "MISSING"
        node = shutil.which("node")
        if node:
            binary = Path(node).resolve(strict=True)
            files[str(binary)] = file_hash(binary)
    return {"archify_root": archify_root, "archify_chrome": None, "files": files,
            "scope": "Archify entrypoint/package, Node and explicit browser binaries; not transitive dependency eligibility"}


def bind_browser(dependencies, browser):
    """Bind a public ARCHIFY_CHROME override without changing browser flags."""
    if browser is None:
        return dependencies
    path = Path(browser).resolve(strict=True)
    if not path.is_file():
        raise ValueError("ARCHIFY_CHROME must name an installed browser executable")
    return {**dependencies, "archify_chrome": str(path),
            "files": {**dependencies["files"], str(path): file_hash(path)}}


def dependency_snapshot(dependencies):
    return {**dependencies, "files": {path: file_hash(path) if Path(path).is_file() else "MISSING"
                                      for path in dependencies["files"]}}


def isolated_environment(job):
    """Build a private home/config/temp environment without secrets."""
    environment = os.environ.copy()
    for key in list(environment):
        if re.search("TOKEN|SECRET|PASSWORD|API_KEY", key, re.I):
            del environment[key]
    for name in ("home", "temp", "config", "project"):
        (job / name).mkdir(parents=True, exist_ok=True)
    environment.update(HOME=str(job / "home"), USERPROFILE=str(job / "home"),
                       TMP=str(job / "temp"), TEMP=str(job / "temp"),
                       TMPDIR=str(job / "temp"), XDG_CONFIG_HOME=str(job / "config"),
                       CODEX_HOME=str(job / "home/.codex"),
                       CLAUDE_CONFIG_DIR=str(job / "home/.claude"),
                       TDQ_PROJECT_DIR=str(job / "project"),
                       TDQ_KHONG_CHAM_MAY="1", TDQ_KHOI_TAO_NEN="0")
    environment.pop("PYTHONUTF8", None)
    return environment


def windows_process(command, root, environment, stdout, stderr, timeout, record=None):
    """Assign a suspended child to a kill-on-close job before any child code runs."""
    import msvcrt
    import win32api
    import win32event
    import win32job
    import win32process
    job = win32job.CreateJobObject(None, "")
    info = win32job.QueryInformationJobObject(job, 9)
    info["BasicLimitInformation"]["LimitFlags"] = 0x2000
    win32job.SetInformationJobObject(job, 9, info)
    startup = win32process.STARTUPINFO()
    startup.dwFlags = 0x100
    with open(os.devnull, "rb") as stdin:
        handles = [msvcrt.get_osfhandle(f.fileno()) for f in (stdin, stdout, stderr)]
        for handle in handles:
            os.set_handle_inheritable(handle, True)
        startup.hStdInput, startup.hStdOutput, startup.hStdError = handles
        process, thread, pid, _ = win32process.CreateProcess(
            None, subprocess.list2cmdline(command), None, None, True,
            0x4 | 0x08000000, environment, str(root), startup)
    timed_out = False
    if record is not None:
        record["pid"] = pid
    try:
        win32job.AssignProcessToJobObject(job, process)
        win32process.ResumeThread(thread)
        deadline = time.monotonic() + timeout
        while win32event.WaitForSingleObject(process, 100) == 258:
            if time.monotonic() >= deadline:
                timed_out = True
                win32job.TerminateJobObject(job, 124)
                break
        win32event.WaitForSingleObject(process, 5000)
        code = win32process.GetExitCodeProcess(process)
        if record is not None:
            record.update(exit_code=124 if timed_out else code, timed_out=timed_out)
    except BaseException:
        win32process.TerminateProcess(process, 125)
        raise
    finally:
        win32api.CloseHandle(job)
        win32api.CloseHandle(thread)
        win32api.CloseHandle(process)
    return (124 if timed_out else code), timed_out, pid


def posix_process(command, root, environment, stdout, stderr, timeout, record=None):
    """Own a new process group and terminate it on timeout or cancellation."""
    process = subprocess.Popen(command, cwd=root, env=environment, stdout=stdout,
                               stderr=stderr, start_new_session=True)
    timed_out = False
    if record is not None:
        record["pid"] = process.pid
    try:
        code = process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out, code = True, 124
    finally:
        if record is not None and "code" in locals():
            record.update(exit_code=code, timed_out=timed_out)
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass  # The owned group already exited; no other PID is touched.
        process.wait(timeout=5)
    return code, timed_out, process.pid


def record_failure(record, stage, error):
    """Retain sanitized failure facts without discarding an observed child exit."""
    record["failures"].append({"stage": stage, "type": type(error).__name__,
        "message": sanitize(str(error), os.environ)[:2000]})


def capture_command(command, root, environment, timeout, job, record):
    """Capture redacted outputs even when child launch or cancellation fails."""
    execution = windows_process if os.name == "nt" else posix_process
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        try:
            code, timeout_hit, pid = execution(command, root, environment, stdout, stderr, timeout, record)
            record.update(exit_code=code, timed_out=timeout_hit, pid=pid)
        except (Exception, KeyboardInterrupt) as error:
            record_failure(record, "execution", error)
        for name, stream in (("stdout.txt", stdout), ("stderr.txt", stderr)):
            try:
                stream.seek(0)
                output = sanitize(stream.read().decode("utf-8", errors="replace"), os.environ)
                (job / name).write_text(output, encoding="utf-8")
                record["artifacts"][name] = file_hash(job / name)
                record["capture"][name] = "complete"
            except Exception as error:
                record["capture"][name] = "failed"
                record["artifacts"].pop(name, None)
                record_failure(record, "capture_" + name, error)


def retry_readonly_cleanup(operation, path, error, sandbox):
    """Reset one owned readonly entry once; never follow a reparse point."""
    if not isinstance(error, PermissionError) or operation not in (os.unlink, os.remove, os.rmdir):
        raise error
    raw = str(path)
    if raw.startswith("\\\\?\\UNC\\"):
        raw = "\\\\" + raw[8:]
    elif raw.startswith("\\\\?\\"):
        raw = raw[4:]
    target = Path(os.path.abspath(raw))
    if not target.is_relative_to(sandbox) or target.resolve() != target:
        raise ValueError("Refusing permission reset outside the owned sandbox") from error
    current = target
    while True:
        metadata = current.lstat()
        if stat.S_ISLNK(metadata.st_mode) or getattr(metadata, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise ValueError("Refusing permission reset through a reparse point") from error
        if current == sandbox:
            break
        current = current.parent
    mode = target.lstat().st_mode
    if mode & stat.S_IWRITE:
        raise error
    os.chmod(path, mode | stat.S_IWRITE)
    operation(path)  # A genuine lock/error propagates; no recursive retry loop.


def cleanup_sandbox(sandbox, temp_parent):
    """Delete only the exact owned temporary root, with Windows long-path support."""
    resolved = sandbox.resolve()
    parent = temp_parent.resolve()
    if resolved != sandbox or resolved.parent != parent or not resolved.name.startswith("tdq-"):
        raise ValueError("Refusing cleanup outside the allocated sandbox parent")
    target = str(resolved)
    if os.name == "nt" and not target.startswith("\\\\?\\"):
        target = "\\\\?\\UNC\\" + target[2:] if target.startswith("\\\\") else "\\\\?\\" + target
    shutil.rmtree(target, onexc=lambda operation, path, error:
                  retry_readonly_cleanup(operation, path, error, resolved))
    if sandbox.exists():
        raise RuntimeError("Owned sandbox still exists after cleanup")


def guarded_snapshot(record, key, operation):
    """A missing post-run guard is failure evidence, never equality of two Nones."""
    try:
        record[key] = operation()
    except (Exception, KeyboardInterrupt) as error:
        record_failure(record, key, error)


def finalize_guards(record, sandbox, temp_parent, personal_home, root):
    if sandbox is not None:
        try:
            cleanup_sandbox(sandbox, temp_parent)
            record["isolation"]["cleanup"] = "complete"
        except (Exception, KeyboardInterrupt) as error:
            record["isolation"]["cleanup"] = "failed"
            record_failure(record, "cleanup", error)
    guarded_snapshot(record, "config_after", lambda: config_snapshot(personal_home))
    guarded_snapshot(record, "source_after", lambda: source_snapshot(root))
    if record["dependency_before"] is not None:
        guarded_snapshot(record, "dependency_after", lambda: dependency_snapshot(record["dependency_before"]))
    for field in ("config", "source", "dependency"):
        before, after = record[field + "_before"], record[field + "_after"]
        if before is not None and after is not None and before != after:
            record_failure(record, field + "_guard", ValueError(field + " changed during command"))


def receipt_exit(record):
    code = record["exit_code"]
    if type(code) is int and code != 0:
        return code
    if record["failures"]:
        return 126 if all(item["stage"] in {"config_guard", "source_guard", "dependency_guard"}
                          for item in record["failures"]) else 125
    successful = (code == 0 and record["timed_out"] is False and record["elevated"] is False
                  and bool(record["config_before"]) and bool(record["source_before"])
                  and record["config_before"] == record["config_after"]
                  and record["source_before"] == record["source_after"]
                  and record["dependency_before"] is not None
                  and record["dependency_before"] == record["dependency_after"]
                  and record["isolation"]["cleanup"] == "complete"
                  and all(state == "complete" for state in record["capture"].values()))
    return 0 if successful else 125


def run_command(command, label, evidence, timeout, root, protected_home=None, archify_chrome=None):
    """Execute one command and publish an integrity-checkable receipt."""
    if elevated():
        raise RuntimeError("Refusing elevated test execution")
    if type(timeout) not in (int, float) or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be finite and positive")
    job = evidence / "runs" / (re.sub(r"[^\w.-]", "_", label) + "-" + uuid.uuid4().hex)
    job.mkdir(parents=True)
    personal_home = protected_home or Path.home()
    record = {"schema": SCHEMA, "label": label, "command": [sanitize(item, os.environ) for item in command],
              "started": time.time(), "exit_code": None, "timed_out": False, "pid": None,
              "elevated": elevated(), "failures": [], "config_before": None, "config_after": None,
              "source_before": None, "source_after": None, "environment_sha256": None,
              "dependency_before": None, "dependency_after": None,
              "python": sys.version, "os": platform.platform(), "packages": [], "artifacts": {},
              "capture": {"stdout.txt": "not_started", "stderr.txt": "not_started"},
              "isolation": {"cleanup": "not_started"}}
    sandbox = temp_parent = None
    stage = "artifact_setup"
    try:
        for name in record["capture"]:
            (job / name).write_text("", encoding="utf-8")
            record["artifacts"][name] = file_hash(job / name)
        stage = "config_before"
        record["config_before"] = config_snapshot(personal_home)
        stage = "source_before"
        record["source_before"] = source_snapshot(root)
        stage = "package_inventory"
        record["packages"] = sorted((d.metadata["Name"], d.version) for d in importlib.metadata.distributions())
        stage = "dependency_before"
        browser = archify_chrome if archify_chrome is not None else os.environ.get("ARCHIFY_CHROME")
        record["dependency_before"] = bind_browser(resolve_dependencies(root), browser)
        stage = "sandbox_setup"
        temp_parent = Path(tempfile.gettempdir()).resolve()
        sandbox = Path(tempfile.mkdtemp(prefix="tdq-", dir=temp_parent)).resolve()
        record["isolation"].update(home=str(sandbox / "home"), temp=str(sandbox / "temp"),
            project=str(sandbox / "project"), sandbox=str(sandbox), parent=str(temp_parent))
        environment = isolated_environment(sandbox)
        if record["dependency_before"]["archify_root"] is not None:
            environment["ARCHIFY_ROOT"] = record["dependency_before"]["archify_root"]
        if record["dependency_before"]["archify_chrome"] is not None:
            environment["ARCHIFY_CHROME"] = record["dependency_before"]["archify_chrome"]
        record["environment_sha256"] = digest(environment)
        stage = "capture"
        capture_command(command, root, environment, timeout, job, record)
    except (Exception, KeyboardInterrupt) as error:
        record_failure(record, stage, error)
    finally:
        finalize_guards(record, sandbox, temp_parent, personal_home, root)
    code = receipt_exit(record)
    record.update(finished=time.time(), harness_exit_code=code, verdict="PASS" if code == 0 else "FAIL")
    first = record["failures"][0] if record["failures"] else {}
    record.update(failure=first.get("message"), failure_stage=first.get("stage"), failure_type=first.get("type"))
    record["sha256"] = digest(record)
    write_json(job / "receipt.json", record)
    print(json.dumps({"receipt": str(job / "receipt.json"), "exit_code": code,
                      "child_exit_code": record["exit_code"], "verdict": record["verdict"]}), flush=True)
    return code, job / "receipt.json"


def normal_dispatch(arguments, evidence, timeout):
    """Ask the existing Explorer desktop to launch us; child rechecks privilege."""
    import win32com.client
    evidence.mkdir(parents=True, exist_ok=True)
    reply = evidence / ("normal-launch-" + uuid.uuid4().hex + ".json")
    args = [str(Path(__file__).resolve()), "--dispatch-reply", str(reply), *arguments]
    windows = win32com.client.Dispatch("Shell.Application").Windows()
    for index in range(windows.Count):
        window = windows.Item(index)
        if str(window.FullName).lower().endswith("explorer.exe"):
            window.Document.Application.ShellExecute(
                sys.executable, subprocess.list2cmdline(args), str(Path.cwd()), "open", 0)
            break
    else:
        raise RuntimeError("No normal Explorer desktop available; run harness in normal terminal")
    deadline = time.monotonic() + timeout + 60
    while time.monotonic() < deadline:
        result = read_dispatch_reply(reply)
        if result is not None:
            print(json.dumps(result), flush=True)
            return result["exit_code"]
        time.sleep(0.2)
    raise RuntimeError("Normal launch did not return; no successful receipt claimed")


def read_dispatch_reply(path):
    """Retry transient Windows publication races under the caller's deadline."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (PermissionError, FileNotFoundError, json.JSONDecodeError):
        return None


def self_test(evidence, root):
    """Exercise actual children plus negative evidence/config/timeout cases."""
    import verify_dod
    checks = []
    code = ("import os,pathlib; h=pathlib.Path.home(); "
            "assert h == pathlib.Path(os.environ['HOME']); "
            "assert h.name == 'home'; assert pathlib.Path(os.environ['TMP']).name == 'temp'; "
            "p=pathlib.Path(os.environ['TMP'])/'pytest-of-admin'/'pytest-999'/"
            "'test_plugin_inventory_nested0'/'.claude'/'plugins'/'cache'/"
            "'tdq-local'/'tdq-workflow'/'0.84.2'/'skills'/'tdq-conventions'/"
            "'references'/'deep-fixture.txt'; "
            "assert len(str(p)) < 260; p.parent.mkdir(parents=True); "
            "p.write_text('fixture'); assert p.read_text() == 'fixture'")
    rc, receipt_path = run_command([sys.executable, "-c", code], "self-isolation", evidence, 10, root)
    assert rc == 0
    verify_dod.validate_receipt(receipt_path, root)
    checks.append("isolated_home_normal_privilege")
    original = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert original["isolation"]["cleanup"] == "complete"
    assert not Path(original["isolation"]["sandbox"]).exists()
    for bad in ({"verdict": "PASS"}, {**original, "exit_code": 42}):
        write_json(receipt_path, bad)
        try:
            verify_dod.validate_receipt(receipt_path, root)
        except (ValueError, KeyError):
            checks.append("forged_receipt_rejected")
        else:
            raise AssertionError("forged evidence accepted")
    write_json(receipt_path, original)
    (receipt_path.parent / "stdout.txt").write_text("tampered", encoding="utf-8")
    try:
        verify_dod.validate_receipt(receipt_path, root)
    except ValueError:
        checks.append("artifact_digest_rejected")
    else:
        raise AssertionError("tampered artifact accepted")
    with tempfile.TemporaryDirectory(prefix="tdq-harness-") as directory:
        fixture = Path(directory)
        (fixture / ".claude").mkdir()
        config = fixture / ".claude/CLAUDE.md"
        config.write_text("before", encoding="utf-8")
        mutation = "from pathlib import Path; Path(" + repr(str(config)) + ").write_text('after')"
        rc, _ = run_command([sys.executable, "-c", mutation], "self-config", evidence, 10, root, fixture)
        assert rc == 126
        checks.append("config_mutation_rejected")
    child_pid_path = evidence / "self-child.pid"
    child_pid_path.unlink(missing_ok=True)
    script = ("import subprocess,sys,time,pathlib; "
              "p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)']); "
              "pathlib.Path(" + repr(str(child_pid_path)) + ").write_text(str(p.pid)); "
              "time.sleep(30)")
    command = [sys.executable, "-c", script]
    rc, timeout_receipt = run_command(command, "self-timeout", evidence, 1, root)
    assert rc == 124
    import psutil
    pid = json.loads(timeout_receipt.read_text())["pid"]
    assert not psutil.pid_exists(pid)
    child_pid = int(child_pid_path.read_text())
    deadline = time.monotonic() + 3
    while psutil.pid_exists(child_pid) and time.monotonic() < deadline:
        time.sleep(0.05)
    assert not psutil.pid_exists(child_pid)
    checks.append("owned_process_and_grandchild_timeout")
    check_junit_properties(evidence)
    checks.append("junit_properties_accepted_failure_rejected")
    check_dispatch_retry()
    checks.append("dispatch_reply_transient_read_retry")
    check_terminal_failures(evidence, root)
    checks.append("post_execution_guard_failure_retains_receipt")
    check_cleanup_and_source(evidence, root)
    checks.append("cleanup_failure_source_drift_and_scope_rejected")
    check_long_path_cleanup(evidence, root)
    checks.append("owned_long_path_sandbox_cleanup")
    check_readonly_git_cleanup(evidence, root)
    checks.append("owned_readonly_git_objects_cleanup")
    check_cleanup_permission_boundaries()
    checks.append("readonly_retry_rejects_escape_reparse_and_locked_file")
    check_dependency_isolation(evidence, root)
    checks.append("explicit_archify_dependency_isolated_and_mutation_rejected")
    semantic = verify_dod.self_test()
    assert semantic["status"] == "PASS" and semantic["simulation_only"] is True
    checks.append("semantic_verifier_rejects_false_pass")
    try:
        verify_dod.verify("D1", evidence, root)
    except (ValueError, FileNotFoundError):
        checks.append("missing_evidence_rejected")
    else:
        raise AssertionError("missing DoD evidence accepted")
    result = {"schema": "tdq-harness-self-test/v1", "checks": checks,
              "count": len(checks), "elevated": elevated(), "exit_code": 0}
    write_json(evidence / "harness-self-test.json", result)
    print(json.dumps(result), flush=True)
    return 0


def check_terminal_failures(evidence, root):
    """Inject a post-child read failure; successful child output must survive."""
    from unittest.mock import patch
    original = config_snapshot
    calls = []
    def unreadable(home):
        calls.append(1)
        if len(calls) == 2:
            raise PermissionError("simulated post-run config read failure")
        return original(home)
    with patch.dict(run_command.__globals__, config_snapshot=unreadable):
        rc, path = run_command([sys.executable, "-c", "print('retained-child-output')"],
                               "self-post-read", evidence, 10, root)
    receipt = json.loads(path.read_text(encoding="utf-8"))
    assert rc != 0 and receipt["exit_code"] == 0 and receipt["verdict"] == "FAIL"
    assert receipt["failure_stage"] == "config_after" and receipt["failure_type"] == "PermissionError"
    assert "retained-child-output" in (path.parent / "stdout.txt").read_text(encoding="utf-8")
    assert_failed_integrity(path, root)


def assert_failed_integrity(path, root):
    import verify_dod
    assert verify_dod.validate_integrity(path)["verdict"] == "FAIL"
    try:
        verify_dod.validate_receipt(path, root)
    except ValueError:
        return
    raise AssertionError("Failed harness receipt accepted as successful proof")


def check_cleanup_and_source(evidence, root):
    from unittest.mock import patch
    command = [sys.executable, "-c", "print('successful child before guard failure')"]
    clean = cleanup_sandbox
    with patch.dict(run_command.__globals__, cleanup_sandbox=lambda *args: (_ for _ in ()).throw(PermissionError("simulated cleanup failure"))):
        rc, path = run_command(command, "self-cleanup", evidence, 10, root)
    receipt = json.loads(path.read_text(encoding="utf-8"))
    assert rc == 125 and receipt["exit_code"] == 0
    assert receipt["isolation"]["cleanup"] == "failed"
    assert_failed_integrity(path, root)
    clean(Path(receipt["isolation"]["sandbox"]), Path(receipt["isolation"]["parent"]))
    before = source_snapshot(root)
    after = {**before, "files": {**before["files"], "simulation-only-input": "changed"}}
    after["sha256"] = digest(after["files"])
    with patch.dict(run_command.__globals__, source_snapshot=lambda _root: snapshots.pop(0)):
        snapshots = [before, after]
        rc, path = run_command(command, "self-source-drift", evidence, 10, root)
    assert rc == 126
    assert_failed_integrity(path, root)
    try:
        clean(root, Path(tempfile.gettempdir()).resolve())
    except ValueError:
        assert root.is_dir()
    else:
        raise AssertionError("Cleanup accepted an unowned path")


def check_long_path_cleanup(evidence, root):
    import verify_dod
    code = ("import os,pathlib; p=pathlib.Path(os.environ['TMP']); "
            "p=p/('a'*80)/('b'*80)/('c'*80)/'fixture.txt'; "
            "p=pathlib.Path('\\\\\\\\?\\\\'+str(p)) if os.name=='nt' else p; "
            "p.parent.mkdir(parents=True); p.write_text('owned fixture'); "
            "assert p.read_text()=='owned fixture'; print('long-path-created')")
    rc, path = run_command([sys.executable, "-c", code], "self-long-cleanup", evidence, 10, root)
    assert rc == 0
    receipt = verify_dod.validate_receipt(path, root)
    assert not Path(receipt["isolation"]["sandbox"]).exists()


def check_readonly_git_cleanup(evidence, root):
    """A real Git object is readonly on Windows and still must be removed."""
    import verify_dod
    code = """import os,pathlib,stat,subprocess
p=pathlib.Path(os.environ['TMP'])/'git-fixture'
subprocess.run(['git','init','-q',str(p)],check=True)
blob=subprocess.run(['git','-C',str(p),'hash-object','-w','--stdin'],input=b'owned git fixture',capture_output=True,check=True).stdout.decode().strip()
obj=p/'.git'/'objects'/blob[:2]/blob[2:]
obj.chmod(stat.S_IREAD)
assert obj.is_file() and not obj.stat().st_mode & stat.S_IWRITE
print('readonly-git-object-created')
"""
    rc, path = run_command([sys.executable, "-c", code], "self-readonly-git", evidence, 10, root)
    assert rc == 0, str(path)
    receipt = verify_dod.validate_receipt(path, root)
    assert not Path(receipt["isolation"]["sandbox"]).exists()


def check_cleanup_permission_boundaries():
    """Permission repair must not escape or turn a genuine lock into success."""
    from unittest.mock import patch
    from types import SimpleNamespace
    parent = Path(tempfile.gettempdir()).resolve()
    sandbox = Path(tempfile.mkdtemp(prefix="tdq-", dir=parent)).resolve()
    target = sandbox / "readonly.txt"
    target.write_text("owned fixture", encoding="utf-8")
    target.chmod(stat.S_IREAD)
    error = PermissionError("simulated denied cleanup")
    try:
        for path in (parent / "outside-readonly.txt", target):
            with patch.object(Path, "lstat", return_value=SimpleNamespace(st_mode=stat.S_IFREG | stat.S_IREAD,
                    st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT)), patch.object(os, "chmod") as chmod:
                try:
                    retry_readonly_cleanup(os.unlink, str(path), error, sandbox)
                except ValueError:
                    chmod.assert_not_called()
                else:
                    raise AssertionError("Unsafe readonly reset accepted")
        if os.name == "nt":
            import win32file
            handle = win32file.CreateFile(str(target), win32file.GENERIC_READ, 0, None,
                                          win32file.OPEN_EXISTING, 0, None)
            try:
                try:
                    cleanup_sandbox(sandbox, parent)
                except PermissionError:
                    assert target.exists()
                else:
                    raise AssertionError("Locked readonly file silently ignored")
            finally:
                handle.Close()
    finally:
        cleanup_sandbox(sandbox, parent)


def check_dependency_isolation(evidence, root):
    """Use an owned fake binary to prove propagation and post-child hash guards."""
    from unittest.mock import patch
    import verify_dod
    with tempfile.TemporaryDirectory(prefix="tdq-dependency-") as directory:
        fixture = Path(directory)
        entrypoint = fixture / "bin/archify.mjs"
        entrypoint.parent.mkdir()
        entrypoint.write_text("// simulation fixture\n", encoding="utf-8")
        browser = fixture / "fixture-browser.exe"
        browser.write_text("simulation identity only; never executed", encoding="utf-8")
        with patch.dict(os.environ, ARCHIFY_ROOT=str(fixture)):
            dependencies = resolve_dependencies(root)
        assert dependencies["archify_root"] == str(fixture.resolve())
        assert dependencies["files"][str(entrypoint)] == file_hash(entrypoint)
        with patch.dict(os.environ, ARCHIFY_ROOT=str(fixture / "missing")):
            assert resolve_dependencies(root)["archify_root"] is None
        code = ("import os,pathlib; assert os.environ['ARCHIFY_ROOT']==" + repr(str(fixture)) +
                "; assert os.environ['ARCHIFY_CHROME']==" + repr(str(browser)) +
                "; assert pathlib.Path.home()!=pathlib.Path(os.environ['ARCHIFY_ROOT']); print('explicit dependency')")
        with patch.dict(os.environ, ARCHIFY_ROOT=str(fixture), ARCHIFY_CHROME=str(fixture / "stale-browser.exe")):
            rc, path = run_command([sys.executable, "-c", code], "self-deps", evidence, 10, root,
                                   archify_chrome=browser)
            assert rc == 0
            valid = verify_dod.validate_receipt(path, root)
            assert valid["dependency_before"]["files"][str(browser)] == file_hash(browser)
        with patch.dict(run_command.__globals__, resolve_dependencies=lambda _root: dependencies):
            mutate = "from pathlib import Path; Path(" + repr(str(entrypoint)) + ").write_text('// changed fixture')"
            rc, path = run_command([sys.executable, "-c", mutate], "self-deps-drift", evidence, 10, root)
        receipt = json.loads(path.read_text(encoding="utf-8"))
        assert rc == 126 and receipt["exit_code"] == 0 and receipt["failure_stage"] == "dependency_guard"
        assert_failed_integrity(path, root)
        dependencies = dependency_snapshot(dependencies)
        mutate = "from pathlib import Path; Path(" + repr(str(browser)) + ").write_text('changed identity')"
        with patch.dict(run_command.__globals__, resolve_dependencies=lambda _root: dependencies):
            rc, path = run_command([sys.executable, "-c", mutate], "self-browser", evidence, 10, root,
                                   archify_chrome=browser)
        assert rc == 126
        assert_failed_integrity(path, root)


def check_junit_properties(evidence):
    """Accept passed JUnit metadata while rejecting a real failure node."""
    import verify_dod
    junit = evidence / "self-properties.xml"
    node = '<testcase classname="fixture" name="case">'
    properties = '<properties><property name="kind" value="fixture"/></properties>'
    entry = {"cases": [{"junit": junit.name, "nodeid": "fixture::case"}]}
    junit.write_text('<testsuite>' + node + properties +
                     '<system-out>output</system-out></testcase></testsuite>', encoding="utf-8")
    verify_dod.validate_cases(entry, evidence, {junit.name: file_hash(junit)})
    junit.write_text('<testsuite>' + node + properties +
                     '<failure>actual failure</failure></testcase></testsuite>', encoding="utf-8")
    try:
        verify_dod.validate_cases(entry, evidence, {junit.name: file_hash(junit)})
    except ValueError:
        return
    raise AssertionError("JUnit failure accepted")


def check_dispatch_retry():
    """Verify transient read failures remain pending until a valid reply arrives."""
    from unittest.mock import patch
    replies = [PermissionError("publication race"), FileNotFoundError("not yet"),
               '{"exit_code":', '{"exit_code": 0}']
    with patch.object(Path, "read_text", side_effect=replies) as read:
        path = Path("fixture-reply.json")
        assert read_dispatch_reply(path) is None
        assert read_dispatch_reply(path) is None
        assert read_dispatch_reply(path) is None
        assert read_dispatch_reply(path) == {"exit_code": 0}
        assert read.call_count == 4


def parse_arguments():
    """Validate CLI options before starting any child."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", default="check")
    parser.add_argument("--evidence-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--timeout-seconds", type=float, default=12000)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--dispatch-reply", type=Path)
    parser.add_argument("--archify-chrome", type=Path,
                        help="Explicit installed browser for Archify's public ARCHIFY_CHROME override")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    arguments = parser.parse_args()
    if not math.isfinite(arguments.timeout_seconds) or arguments.timeout_seconds <= 0:
        parser.error("timeout must be finite and positive")
    command = arguments.command[1:] if arguments.command[:1] == ["--"] else arguments.command
    if not command and not arguments.self_test:
        parser.error("command or --self-test required")
    return arguments, command


def main():
    """Run the requested isolated command or the harness self-test."""
    arguments, command = parse_arguments()
    evidence = arguments.evidence_dir.resolve()
    root = Path.cwd().resolve()
    receipt_path, failure = None, None
    try:
        if elevated() and arguments.dispatch_reply is None and os.name == "nt":
            forwarded = ["--label", arguments.label, "--evidence-dir", str(evidence),
                         "--timeout-seconds", str(arguments.timeout_seconds)]
            if arguments.self_test:
                forwarded.append("--self-test")
            if arguments.archify_chrome is not None:
                forwarded += ["--archify-chrome", str(arguments.archify_chrome.resolve(strict=True))]
            if command:
                forwarded += ["--", *command]
            return normal_dispatch(forwarded, evidence, arguments.timeout_seconds)
        if elevated():
            raise RuntimeError("Normal-user privilege check failed")
        evidence.mkdir(parents=True, exist_ok=True)
        if arguments.self_test:
            code = self_test(evidence, root)
        else:
            code, receipt_path = run_command(command, arguments.label, evidence,
                                             arguments.timeout_seconds, root,
                                             archify_chrome=arguments.archify_chrome)
            if code:
                saved = json.loads(receipt_path.read_text(encoding="utf-8"))
                failure = (saved.get("failures") or [None])[0]
    except (Exception, KeyboardInterrupt) as error:
        failure = {"stage": "harness", "type": type(error).__name__,
                   "message": sanitize(str(error), os.environ)[:2000]}
        print(json.dumps(failure), file=sys.stderr)
        code = 125
    if arguments.dispatch_reply:
        write_json(arguments.dispatch_reply, {"exit_code": code, "elevated": elevated(),
                                            "self_test": arguments.self_test,
                                            "evidence_dir": str(evidence),
                                            "receipt": str(receipt_path) if receipt_path else None,
                                            "failure": failure})
    return code


if __name__ == "__main__":
    raise SystemExit(main())
