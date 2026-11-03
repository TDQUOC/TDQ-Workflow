"""Own test process trees and isolate jobs without changing the caller's HOME.

Windows starts a stdlib-only bootstrap waiting for a pipe message. The target
cannot start until assignment to a kill-on-close Job Object succeeds. POSIX
uses a new process group; children that deliberately leave it are unsupported.
Load this module as a pytest plugin to isolate xdist worker homes as well.
Logs contain lifecycle metadata only; TDQ_LOG=0 disables them.
"""
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time


_BOOTSTRAP = (
    "import json,subprocess,sys; "
    "command=json.loads(sys.stdin.buffer.readline()); "
    "child=subprocess.Popen(command,stdin=subprocess.DEVNULL); "
    "sys.exit(child.wait())"
)


def _private_environment(root):
    home = root / "home"
    scratch = root / "tmp"
    for directory in (home, scratch, home / "roaming", home / "local"):
        directory.mkdir(parents=True, exist_ok=True)
    return {
        "HOME": str(home), "USERPROFILE": str(home),
        "TMP": str(scratch), "TEMP": str(scratch), "TMPDIR": str(scratch),
        "APPDATA": str(home / "roaming"), "LOCALAPPDATA": str(home / "local"),
        "XDG_CONFIG_HOME": str(home / ".config"),
        "XDG_CACHE_HOME": str(home / ".cache"),
        "PYTHONUSERBASE": str(home / ".python"),
        "CODEX_HOME": str(home / ".codex"),
        "CLAUDE_CONFIG_DIR": str(home / ".claude"),
        "HOMEDRIVE": home.drive, "HOMEPATH": str(home)[len(home.drive):],
        "TDQ_KHOI_TAO_NEN": "0", "TDQ_KHONG_CHAM_MAY": "1",
    }


def pytest_load_initial_conftests(early_config, parser, args):
    """Set a worker's private home before importing project conftest/tests."""
    root = os.environ.get("TDQ_TEST_JOB_ROOT")
    if not root:
        return
    worker = os.environ.get("PYTEST_XDIST_WORKER", "controller")
    if not worker.replace("-", "").isalnum():
        raise ValueError("Invalid worker identity")
    os.environ.update(_private_environment(Path(root) / "workers" / worker))
    tempfile.tempdir = None


class _BasicLimits(ctypes.Structure):
    _fields_ = [
        ("process_time", ctypes.c_int64), ("job_time", ctypes.c_int64),
        ("flags", wintypes.DWORD), ("minimum", ctypes.c_size_t),
        ("maximum", ctypes.c_size_t), ("active_limit", wintypes.DWORD),
        ("affinity", ctypes.c_size_t), ("priority", wintypes.DWORD),
        ("scheduling", wintypes.DWORD),
    ]


class _IoCounters(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint64) for name in
                ("reads", "writes", "others", "read_bytes", "write_bytes",
                 "other_bytes")]


class _ExtendedLimits(ctypes.Structure):
    _fields_ = [
        ("basic", _BasicLimits), ("io", _IoCounters),
        ("process_memory", ctypes.c_size_t), ("job_memory", ctypes.c_size_t),
        ("peak_process_memory", ctypes.c_size_t),
        ("peak_job_memory", ctypes.c_size_t),
    ]


class _Accounting(ctypes.Structure):
    _fields_ = [
        ("user_time", ctypes.c_int64), ("kernel_time", ctypes.c_int64),
        ("period_user", ctypes.c_int64), ("period_kernel", ctypes.c_int64),
        ("page_faults", wintypes.DWORD), ("total", wintypes.DWORD),
        ("active", wintypes.DWORD), ("terminated", wintypes.DWORD),
    ]


def _kernel_api():
    api = ctypes.WinDLL("kernel32", use_last_error=True)
    declarations = {
        "CreateJobObjectW": ([ctypes.c_void_p, wintypes.LPCWSTR], wintypes.HANDLE),
        "SetInformationJobObject": ([wintypes.HANDLE, ctypes.c_int,
                                     ctypes.c_void_p, wintypes.DWORD], wintypes.BOOL),
        "AssignProcessToJobObject": ([wintypes.HANDLE, wintypes.HANDLE], wintypes.BOOL),
        "TerminateJobObject": ([wintypes.HANDLE, wintypes.UINT], wintypes.BOOL),
        "QueryInformationJobObject": ([wintypes.HANDLE, ctypes.c_int,
                                       ctypes.c_void_p, wintypes.DWORD,
                                       ctypes.c_void_p], wintypes.BOOL),
        "CloseHandle": ([wintypes.HANDLE], wintypes.BOOL),
        "OpenProcess": ([wintypes.DWORD, wintypes.BOOL, wintypes.DWORD], wintypes.HANDLE),
        "WaitForSingleObject": ([wintypes.HANDLE, wintypes.DWORD], wintypes.DWORD),
    }
    for name, (arguments, result) in declarations.items():
        function = getattr(api, name)
        function.argtypes, function.restype = arguments, result
    return api


def _windows_pid_alive(pid):
    """Inspect a PID for smoke evidence; never terminate by this identity."""
    api = _kernel_api()
    handle = api.OpenProcess(0x00100000, False, pid)  # SYNCHRONIZE
    if not handle:
        if ctypes.get_last_error() == 87:  # ERROR_INVALID_PARAMETER: no PID
            return False
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        return api.WaitForSingleObject(handle, 0) == 258  # WAIT_TIMEOUT
    finally:
        api.CloseHandle(handle)


class _WindowsJob:
    mechanism = "windows-job"

    def __init__(self):
        self.api = _kernel_api()
        self.handle = self.api.CreateJobObjectW(None, None)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())
        limits = _ExtendedLimits()
        limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not self.api.SetInformationJobObject(
                self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)):
            error = ctypes.WinError(ctypes.get_last_error())
            self.close()
            raise error

    def assign(self, child):
        if not self.api.AssignProcessToJobObject(self.handle, int(child._handle)):
            raise ctypes.WinError(ctypes.get_last_error())

    def stop(self, deadline=None):
        if not self.api.TerminateJobObject(self.handle, 1):
            raise ctypes.WinError(ctypes.get_last_error())
        deadline = time.monotonic() + 5 if deadline is None else deadline
        while time.monotonic() < deadline:
            account = _Accounting()
            if not self.api.QueryInformationJobObject(
                    self.handle, 1, ctypes.byref(account), ctypes.sizeof(account), None):
                raise ctypes.WinError(ctypes.get_last_error())
            if account.active == 0:
                return True
            time.sleep(.01)
        return False

    def close(self):
        if self.handle:
            self.api.CloseHandle(self.handle)
            self.handle = None


class _PosixGroup:
    mechanism = "posix-process-group"

    def __init__(self):
        self.pid = None

    def assign(self, child):
        self.pid = child.pid

    def stop(self, deadline=None):
        if self.pid is None:
            return True
        try:
            os.killpg(self.pid, signal.SIGKILL)
        except ProcessLookupError:
            return True
        return True

    def verify(self, deadline=None):
        if self.pid is None:
            return True
        deadline = time.monotonic() + 5 if deadline is None else deadline
        while time.monotonic() < deadline:
            try:
                os.killpg(self.pid, 0)
            except ProcessLookupError:
                return True
            time.sleep(.01)
        return False

    def close(self):
        pass


class OwnedProcessJob:
    """Own a process tree with bounded cleanup while preserving caller env."""

    def __init__(self, repo, *, timeout_seconds=1800, env=None,
                 temp_parent=None, cancel_event=None):
        if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be finite and positive")
        self.repo = Path(repo).resolve(strict=True)
        if not self.repo.is_dir():
            raise ValueError("repo must be a directory")
        self.original_env = dict(os.environ)
        self.env = {**self.original_env, **(env or {})}
        self.timeout_seconds = timeout_seconds
        self.cancel_event = cancel_event
        self.temp_parent = temp_parent
        self.root = None
        self.deadline = None
        self._temporary = None
        self._sequence = 0

    def __enter__(self):
        self.deadline = time.monotonic() + self.timeout_seconds
        self._cleanup_deadline = None
        self._temporary = tempfile.TemporaryDirectory(prefix="tdq-", dir=self.temp_parent)
        self.root = Path(self._temporary.name).resolve()
        return self

    def __exit__(self, exc_type, exc, traceback):
        deadline = self._cleanup_deadline
        if deadline is None:
            deadline = time.monotonic() + 5
        try:
            while True:
                try:
                    self._temporary.cleanup()
                    break
                except OSError as error:
                    # Windows can report zero active processes before inherited
                    # output handles finish closing. Spend only the budget left.
                    remaining = deadline - time.monotonic()
                    if getattr(error, "winerror", None) != 32 or remaining <= 0:
                        raise
                    time.sleep(min(.01, remaining))
        finally:
            self.deadline = None

    def _log(self, result):
        if self.env.get("TDQ_LOG") == "0":
            return
        stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        print(f"[{stamp}] tdq_test_process reason={result['reason']} "
              f"phase={result['phase']} "
              f"exit_code={result['exit_code']} "
              f"wall={result['duration_seconds']:.6f} "
              f"cleanup={result['cleanup_seconds']:.6f} "
              f"cleanup_complete={result['cleanup_complete']}", file=sys.stderr)

    def _interruption(self):
        if self.cancel_event is not None and self.cancel_event.is_set():
            return "cancelled"
        if time.monotonic() >= self.deadline:
            return "timeout"
        return None

    def _wait(self, child):
        while True:
            reason = self._interruption()
            if reason:
                return None, reason
            try:
                return child.wait(timeout=min(.05, max(.001, self.deadline - time.monotonic()))), "exited"
            except subprocess.TimeoutExpired:
                continue
            except KeyboardInterrupt:
                return None, "cancelled"

    def _launch(self, argv, owner, stdout, stderr):
        options = {"start_new_session": True} if os.name != "nt" else {
            "creationflags": subprocess.CREATE_NO_WINDOW}
        child = subprocess.Popen(
            [sys.executable, "-I", "-S", "-c", _BOOTSTRAP],
            cwd=self.repo, env=self.env, stdin=subprocess.PIPE,
            stdout=stdout, stderr=stderr, **options)
        try:
            owner.assign(child)
            child.stdin.write(json.dumps([os.fspath(arg) for arg in argv]).encode("utf-8") + b"\n")
            child.stdin.close()
            return child
        except BaseException:
            child.stdin.close()
            child.kill()
            child.wait(timeout=5)
            raise

    @staticmethod
    def _cleanup(owner, child):
        started = time.monotonic()
        deadline = started + 5
        complete = True
        try:
            if owner is not None:
                complete = owner.stop(deadline=deadline)
            if child is not None:
                child.wait(timeout=max(0, deadline - time.monotonic()))
            if isinstance(owner, _PosixGroup):
                complete = owner.verify(deadline=deadline) and complete
        except (OSError, subprocess.TimeoutExpired):
            complete = False
        finally:
            if owner is not None:
                owner.close()
        return complete, time.monotonic() - started

    def _execute(self, argv, stdout, stderr):
        owner = child = None
        exit_code = None
        reason = self._interruption()
        try:
            if reason is None:
                owner = _WindowsJob() if os.name == "nt" else _PosixGroup()
                child = self._launch(argv, owner, stdout, stderr)
                exit_code, reason = self._wait(child)
        except KeyboardInterrupt:
            reason = "cancelled"
        except (OSError, subprocess.SubprocessError):
            reason = "launch-error"
        finally:
            self._cleanup_deadline = time.monotonic() + 5
            complete, cleanup_seconds = self._cleanup(owner, child)
        return {
            "exit_code": exit_code, "reason": reason,
            "timed_out": reason == "timeout", "cancelled": reason == "cancelled",
            "cleanup_complete": complete, "cleanup_seconds": cleanup_seconds,
            "ownership": {"mechanism": owner.mechanism if owner else "not-started",
                          "root_pid": child.pid if child else None,
                          "assignment_verified": child is not None,
                          "verified": child is not None and complete,
                          "cleanup_scope": "job-object" if os.name == "nt"
                          else "process-group"},
        }

    def run(self, argv, *, phase):
        """Return process facts, not test PASS; duration_seconds aliases wall.

        wall_seconds includes cleanup_seconds. execute_seconds excludes cleanup;
        consumers must not add wall/duration to cleanup when aggregating time.
        """
        if self.deadline is None:
            raise RuntimeError("Process job must be entered before run")
        if not argv:
            raise ValueError("argv must not be empty")
        started = time.monotonic()
        self._sequence += 1
        out_path = self.root / f"{self._sequence}.out"
        err_path = self.root / f"{self._sequence}.err"
        with out_path.open("wb") as stdout, err_path.open("wb") as stderr:
            result = self._execute(argv, stdout, stderr)
        wall_seconds = time.monotonic() - started
        result.update({
            "schema_version": 1, "phase": phase,
            "stdout": out_path.read_text(encoding="utf-8", errors="replace"),
            "stderr": err_path.read_text(encoding="utf-8", errors="replace"),
            "duration_seconds": wall_seconds, "wall_seconds": wall_seconds,
            "execute_seconds": max(0.0, wall_seconds - result["cleanup_seconds"]),
            "paths": {"home": self.env.get("HOME"), "temp": self.env.get("TMP", self.env.get("TEMP")),
                      "basetemp": str(self.root / "pytest")},
        })
        self._log(result)
        return result


class IsolatedJob(OwnedProcessJob):
    """Layer private pytest homes onto the shared process ownership primitive."""

    def __init__(self, repo, *, timeout_seconds=1800, env=None,
                 temp_parent=None, cancel_event=None):
        super().__init__(repo, timeout_seconds=timeout_seconds, env=env,
                         temp_parent=temp_parent, cancel_event=cancel_event)
        for key in ("PYTEST_XDIST_WORKER", "PYTEST_XDIST_WORKER_COUNT",
                    "PYTEST_XDIST_TESTRUNUID", "PYTEST_CURRENT_TEST"):
            self.env.pop(key, None)

    def __enter__(self):
        super().__enter__()
        try:
            self.env.update(_private_environment(self.root / "workers" / "controller"))
            scripts = str(Path(__file__).resolve().parent)
            self.env["PYTHONPATH"] = scripts + os.pathsep + self.env.get("PYTHONPATH", "")
            self.env["TDQ_TEST_JOB_ROOT"] = str(self.root)
            return self
        except BaseException:
            super().__exit__(*sys.exc_info())
            raise

    def pytest_args(self):
        """Return plugin and per-job basetemp arguments, preserving tmpdir."""
        return ["-p", "tdq_test_process", "--basetemp=" + str(self.root / "pytest")]
