from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

artifact = Path(__file__).resolve().parent
root = artifact.parents[3]
inventory = json.loads((artifact / "review-collection.json").read_text(encoding="utf-8"))
nodeids = [item["nodeid"] for item in inventory["pytest_cases_not_in_previous_evidence"]]
assert len(nodeids) == 16
config = Path.home() / ".claude" / "CLAUDE.md"
before = hashlib.sha256(config.read_bytes()).hexdigest()
started = time.perf_counter()
with tempfile.TemporaryDirectory(prefix="tdq-review-missing-") as temporary:
    home = Path(temporary) / "home"
    home.mkdir()
    env = dict(os.environ, HOME=str(home), USERPROFILE=str(home),
               TDQ_KHONG_CHAM_MAY="1", TDQ_KHOI_TAO_NEN="0")
    command = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
               "--basetemp=" + str(Path(temporary) / "pytest"),
               "--junitxml=" + str(artifact / "review-missing.xml"), "--durations=10", *nodeids]
    with (artifact / "review-missing.stdout.txt").open("wb") as stdout, (artifact / "review-missing.stderr.txt").open("wb") as stderr:
        process = subprocess.run(command, cwd=root, env=env, stdout=stdout, stderr=stderr, timeout=120)
result = {"at": datetime.now().astimezone().isoformat(timespec="seconds"), "command": command,
          "seconds": round(time.perf_counter() - started, 3), "exit_code": process.returncode,
          "real_user_config_unchanged": hashlib.sha256(config.read_bytes()).hexdigest() == before,
          "scope": "16 previously uncollected pytest cases in a mixed unittest/pytest module",
          "isolation": "Private HOME/USERPROFILE and pytest basetemp; no global UTF8 environment override"}
(artifact / "review-missing.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
print((artifact / "review-missing.stdout.txt").read_text(encoding="utf-8", errors="replace"))
sys.exit(0 if process.returncode == 0 and result["real_user_config_unchanged"] else 1)
