"""Repeat the six diagnostic assertions with a populated, private plugin inventory."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

A = Path(__file__).resolve().parent
ROOT = A.parents[3]
real_home = Path.home()
config = real_home / ".claude" / "CLAUDE.md"
before = hashlib.sha256(config.read_bytes()).hexdigest()
start = time.perf_counter()
with tempfile.TemporaryDirectory(prefix="tdq-review-token-fixture-") as tmp:
    home = Path(tmp)
    claude = home / ".claude"
    (claude / "plugins").mkdir(parents=True)
    settings = json.loads((real_home / ".claude" / "settings.json").read_text(encoding="utf-8"))
    (claude / "settings.json").write_text(json.dumps({"enabledPlugins": settings.get("enabledPlugins", {})}), encoding="utf-8")
    installed = (real_home / ".claude" / "plugins" / "installed_plugins.json").read_bytes()
    (claude / "plugins" / "installed_plugins.json").write_bytes(installed)
    env = dict(os.environ, HOME=str(home), USERPROFILE=str(home), TDQ_KHONG_CHAM_MAY="1", TDQ_KHOI_TAO_NEN="0")
    command = [sys.executable, "-X", "utf8", str(A / "review_diagnostics.py"), "--token-child"]
    with (A / "review-tokenizer-populated.stdout.txt").open("wb") as out, (A / "review-tokenizer-populated.stderr.txt").open("wb") as err:
        proc = subprocess.run(command, cwd=ROOT, env=env, stdout=out, stderr=err, timeout=300)
result = {"exit_code": proc.returncode, "seconds": round(time.perf_counter() - start, 3),
          "real_user_config_unchanged": hashlib.sha256(config.read_bytes()).hexdigest() == before,
          "fixture": "Private HOME with enabledPlugins and installed plugin path registry; real skill files read only; no settings content retained in artifacts",
          "scope": "Six existing assertions with skip decorator unwrapped in memory; not a fix to standard discovery"}
(A / "review-tokenizer-populated.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result))
sys.exit(proc.returncode)
