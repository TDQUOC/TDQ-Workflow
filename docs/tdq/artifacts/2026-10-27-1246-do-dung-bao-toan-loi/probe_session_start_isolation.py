"""Reproduce the existing hook write safely in a private HOME; retain metadata only."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path.cwd()
sys.path.insert(0, str(root / "scripts"))
import tdq_setup

real_config = Path.home() / ".claude" / "CLAUDE.md"
before = hashlib.sha256(real_config.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix="tdq-session-start-probe-") as temp:
    home = Path(temp) / "home"
    project = Path(temp) / "project"
    home.mkdir()
    (project / ".git").mkdir(parents=True)
    env = dict(os.environ, HOME=str(home), USERPROFILE=str(home),
               TDQ_PROJECT_DIR=str(project), TDQ_KHONG_CHAM_MAY="1",
               TDQ_KHOI_TAO_NEN="0", TDQ_LOG="0")
    proc = subprocess.run([sys.executable, str(root / "hooks/scripts/session_start.py")],
                          input=json.dumps({"cwd": str(project), "session_id": "qc-isolated-probe",
                                            "hook_event_name": "SessionStart"}),
                          env=env, capture_output=True, text=True, encoding="utf-8", timeout=40)
    fake_config = home / ".claude" / "CLAUDE.md"
    checks = {
        "hook_exit_zero": proc.returncode == 0,
        "fake_home_config_created_despite_safety_flag": fake_config.is_file(),
        "managed_block_points_to_checkout": fake_config.is_file() and
            tdq_setup.khoi_huong_dan(str(root)) in fake_config.read_text(encoding="utf-8"),
        "real_user_config_unchanged": hashlib.sha256(real_config.read_bytes()).hexdigest() == before,
    }
    output = {"checks": checks,
              "scope": "Existing SessionStart version-upgrade branch; not changed by phase 1",
              "safety": "Private HOME/USERPROFILE/project; no raw user config or hook payload retained",
              "source": ["hooks/scripts/session_start.py:235", "scripts/tdq_setup.py:1200",
                         "tests/test_tu_khoi_tao.py:346", "tests/helper.py:25"]}
print(json.dumps(output, ensure_ascii=False, indent=2))
sys.exit(0 if all(checks.values()) else 1)
