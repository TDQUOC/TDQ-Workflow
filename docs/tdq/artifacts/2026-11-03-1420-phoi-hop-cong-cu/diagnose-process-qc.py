"""Reproduce timeout cleanup failures inside the real isolated runner."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
from tdq_test_process import IsolatedJob

CHILD = r'''
import sys, traceback
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import tdq_test_process
original = tdq_test_process.OwnedProcessJob.__exit__
def diagnostic_exit(self, *args):
    try:
        return original(self, *args)
    except OSError as exc:
        print("CLEANUP_DIAGNOSTIC", repr(exc), "winerror=", getattr(exc, "winerror", None), "filename=", exc.filename, file=sys.stderr)
        traceback.print_exc()
        raise
tdq_test_process.OwnedProcessJob.__exit__ = diagnostic_exit
import pytest
raise SystemExit(pytest.main([sys.argv[2], "-q", "-s", "--tb=short", "-k", "treo_thi_qua_han or version_timeout_owns or windows_cmd_descendant", "-p", "no:cacheprovider"]))
'''
with IsolatedJob(ROOT, timeout_seconds=120) as job:
    result = job.run([sys.executable, "-c", CHILD, str(ROOT / "scripts"),
                      str(ROOT / "tests/test_codex_cli.py")], phase="diagnose-codex-cleanup")
ART = Path(__file__).parent
(ART / "process-diagnostic.stdout.txt").write_text(result["stdout"], encoding="utf-8")
(ART / "process-diagnostic.stderr.txt").write_text(result["stderr"], encoding="utf-8")
print(json.dumps({k: result[k] for k in ("exit_code", "reason", "cleanup_complete", "duration_seconds")}))
print(result["stdout"][-2500:])
print(result["stderr"][-4500:])
