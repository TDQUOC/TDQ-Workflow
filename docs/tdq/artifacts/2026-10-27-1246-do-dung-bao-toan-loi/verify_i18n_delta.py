"""Compare existing i18n findings with the approved baseline, without waivers."""
import collections
import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path.cwd() / "scripts"))
import i18n_check

BASE = "3e0ef5f8a148cbf8aae1e932995e844e8f62ccd9"
FILES = [
    "scripts/tdq_transcript.py", "scripts/tdq_test_result.py",
    "scripts/token_audit.py", "scripts/tdq_timing.py", "scripts/tdq_test.py",
    "scripts/tdq_state.py", "scripts/step_audit.py",
    "skills/tdq-build/references/report-template.md", "skills/tdq-status/SKILL.md",
]
rows = []
with tempfile.TemporaryDirectory(prefix="tdq-i18n-baseline-") as directory:
    for name in FILES:
        old = subprocess.run(["git", "show", BASE + ":" + name], capture_output=True)
        target = Path(directory) / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(old.stdout if old.returncode == 0 else b"")
        before = i18n_check.scan_file(str(target))
        after = i18n_check.scan_file(name)
        key = lambda finding: (finding["kind"], finding["text"])
        added = collections.Counter(map(key, after)) - collections.Counter(map(key, before))
        rows.append({"file": name, "baseline": len(before), "current": len(after),
                     "new_findings": [{"kind": k[0], "text": k[1], "count": v}
                                      for k, v in added.items()]})
result = {"baseline_commit": BASE, "files": rows,
          "baseline_findings": sum(row["baseline"] for row in rows),
          "current_findings": sum(row["current"] for row in rows),
          "new_findings": sum(len(row["new_findings"]) for row in rows)}
print(json.dumps(result, ensure_ascii=False, indent=2))
sys.exit(1 if result["new_findings"] else 0)
