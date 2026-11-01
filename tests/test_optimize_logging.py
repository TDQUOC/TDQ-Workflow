"""Log risky orchestration paths without exposing input or child payloads."""
import datetime
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import tdq_bench as bench
import tdq_test as runner
import tdq_test_process as process
import tdq_test_report as report


SECRET = "optimize-secret-fixture-713e"
RAW = "raw-codex-prompt-and-child-output-209a"


@pytest.fixture(params=[True, False], ids=["default-on", "disabled"])
def logging_enabled(request, monkeypatch):
    if request.param:
        monkeypatch.delenv("TDQ_LOG", raising=False)
    else:
        monkeypatch.setenv("TDQ_LOG", "0")
    return request.param


def assert_metadata(text, enabled, tokens):
    assert SECRET not in text and RAW not in text
    lines = [line for line in text.splitlines() if line.startswith("[")]
    if not enabled:
        assert not lines
        return
    assert lines
    for line in lines:
        stamp, message = line[1:].split("] ", 1)
        assert datetime.datetime.fromisoformat(stamp)
        assert message
    metadata = "\n".join(lines)
    for token in tokens:
        assert token in metadata, metadata


def child_command():
    return [sys.executable, "-c", f"import sys; print({SECRET!r}); print({RAW!r},file=sys.stderr)"]


def test_owned_cleanup_failure_log_is_explicit(tmp_path, capsys, monkeypatch, logging_enabled):
    cleanup = process.OwnedProcessJob._cleanup
    def verification_failed(owner, child):
        complete, elapsed = cleanup(owner, child)
        assert complete  # Close/stop the actual owned process before simulating failure.
        return False, elapsed
    monkeypatch.setattr(process.OwnedProcessJob, "_cleanup", staticmethod(verification_failed))
    with process.OwnedProcessJob(tmp_path, timeout_seconds=10) as job:
        result = job.run(child_command(), phase="owned-cleanup-check")
    assert result["exit_code"] == 0 and result["reason"] == "exited"
    assert not result["cleanup_complete"] and not result["ownership"]["verified"]
    assert SECRET in result["stdout"] and RAW in result["stderr"]
    assert_metadata(capsys.readouterr().err, logging_enabled,
                    ["phase=owned-cleanup-check", "reason=exited", "cleanup_complete=False"])


def test_owned_timeout_logs_cleanup_without_printing_payload(tmp_path, capsys, logging_enabled):
    command = [sys.executable, "-c", "import sys,time; "
               f"print({SECRET!r},flush=True); print({RAW!r},file=sys.stderr,flush=True); time.sleep(20)"]
    with process.OwnedProcessJob(tmp_path, timeout_seconds=1.5) as job:
        result = job.run(command, phase="owned-timeout")
    assert result["timed_out"] and result["cleanup_complete"]
    assert result["ownership"]["verified"]
    assert SECRET in result["stdout"] and RAW in result["stderr"]
    assert_metadata(capsys.readouterr().err, logging_enabled,
                    ["phase=owned-timeout", "reason=timeout", "cleanup_complete=True"])


def test_calibration_rejects_short_log_without_logging_input_or_measuring(
        tmp_path, capsys, monkeypatch, logging_enabled):
    source, output = tmp_path / "codex.log", tmp_path / "constants.json"
    lines = [f'[2026-11-01T00:00:0{index}+00:00] luot T1.{index} · model=fixture · '
             f'home=/owned · {seconds}s · xong · sha256=fixture · dau="{RAW}"'
             for index, seconds in enumerate((1.0, 2.0))]
    source.write_text("\n".join(lines) + "\n" + SECRET + "\n", encoding="utf-8")
    def forbidden(*args, **kwargs):
        raise AssertionError("Early rejection must not launch machine calibration")
    monkeypatch.setattr(bench, "_do_mot_luot", forbidden)
    code = bench.main(["calibrate", "--log-codex", str(source), "--ra", str(output)])
    captured = capsys.readouterr()
    assert code == 1 and not output.exists()
    assert captured.out == ""
    assert "3" in captured.err and "sample" in captured.err.lower()
    assert_metadata(captured.err, logging_enabled, ["calibrate"])


def test_export_rollback_logs_safe_reason_and_preserves_bundle(
        tmp_path, capsys, monkeypatch, logging_enabled):
    source, prefix = tmp_path / "input.json", tmp_path / "output"
    source.write_text(json.dumps({"status": "FAIL", "exit_code": 1, "schema_version": 2,
                                  "private_payload": SECRET, "case_outcomes": [{
        "case_id": "tests/test_case.py::test_fixture", "outcome": "fail", "reason": RAW,
        "phases": [{"phase": phase, "outcome": "pass", "reason": RAW, "duration_seconds": .1}
                   for phase in ("setup", "call", "teardown")]}]}), encoding="utf-8")
    original_input = source.read_bytes()
    previous = {tmp_path / (prefix.name + suffix): ("old" + suffix).encode()
                for suffix in (".md", ".html", ".json")}
    for path, content in previous.items():
        path.write_bytes(content)
    replace, denied = report.os.replace, []
    def fail_html_once(origin, destination):
        if Path(destination) == tmp_path / "output.html" and not denied:
            denied.append(True)
            raise OSError(SECRET + " " + RAW)
        return replace(origin, destination)
    monkeypatch.setattr(report.os, "replace", fail_html_once)
    code = runner.main(["report", "--result", str(source), "--out-prefix", str(prefix)])
    captured = capsys.readouterr()
    assert code == 1 and denied
    assert source.read_bytes() == original_input
    assert all(path.read_bytes() == content for path, content in previous.items())
    assert "TDQ_REPORT" not in captured.out
    assert "report failed:" in captured.err and "OSError" in captured.err
    assert_metadata(captured.err, logging_enabled, ["stage=rollback", "stage=failed", "error=OSError"])
