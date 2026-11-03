"""Check report statements against retained receipts, hashes and actual linked content."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

root = Path.cwd()
slug = "2026-10-27-1246-do-dung-bao-toan-loi"
art = root / "docs/tdq/artifacts" / slug
report_path = root / f"docs/tdq/reports/{slug}.md"
qc_path = root / f"docs/tdq/qc/{slug}.md"
report = report_path.read_text(encoding="utf-8")
qc = qc_path.read_text(encoding="utf-8")

def read_json(name):
    return json.loads((art / name).read_text(encoding="utf-8"))

full = read_json("QC-F1-after-QC2.json")
context = read_json("QC-F1-after-QC2.context.json")
full_err = (art / full["stderr"]).read_text(encoding="utf-8")
pytest = read_json("QC-F2-pytest-isolated.json")
pytest_out = (art / pytest["stdout"]).read_text(encoding="utf-8")
combined = read_json("QC-F2-combined-proof.stdout.txt")
ledger = read_json("QC-ledger-final.stdout.txt")
binding = read_json("D7-final-binding.json")
repair = read_json("QC-user-config-final-repair.stdout.txt")
links = []
for document in [report_path, qc_path]:
    for target in re.findall(r"\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
        if "://" not in target and not target.startswith("#"):
            path = (document.parent / target.split("#", 1)[0]).resolve()
            links.append({"document": str(document.relative_to(root)), "target": target,
                          "readable_nonempty": path.is_file() and len(path.read_bytes()) > 0})
checks = {
    "full_counts_and_exit": full["exit_code"] == 0 and "Ran 3206 tests in 686.773s" in full_err and "OK (skipped=10)" in full_err,
    "pytest_counts_and_exit": pytest["exit_code"] == 0 and "82 passed, 2 skipped in 6.45s" in pytest_out,
    "full_duration_matches_report": full["seconds"] == 688.269 and "688.269s" in report,
    "supplement_duration_matches_report": pytest["seconds"] == 6.845 and "6.845s" in report,
    "combined_inventory_167": combined["combined_collected_module_count"] == 167 and all(combined["checks"].values()),
    "ledger_history_preserved": ledger["tron_bo"] == 3 and ledger["ngan_sach"] == 3 and ledger["bo_sot"] == 5 and ledger["radius_complete"] is True,
    "timing_stdout_verbatim": report.endswith((art / "report-timing.stdout.txt").read_text(encoding="utf-8")),
    "preview_binding_and_source_drift_explicit": all(binding["checks"].values()) and binding["source_drift_count"] == 14 and "14 file" in report,
    "preview_html_hash_unchanged": hashlib.sha256((root / f"docs/tdq/spec/{slug}-preview.html").read_bytes()).hexdigest() == binding["html_sha256"],
    "same_source_head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip() == context["head"],
    "same_all_342_source_hashes": len(context["source_sha256"]) == 342 and all(hashlib.sha256((root / path).read_bytes()).hexdigest() == digest for path, digest in context["source_sha256"].items()),
    "user_config_still_restored": hashlib.sha256(Path("C:/Users/admin/.claude/CLAUDE.md").read_bytes()).hexdigest() == repair["after_sha256"],
    "all_links_readable_nonempty": all(row["readable_nonempty"] for row in links),
    "limits_not_hidden": all(term in report for term in ["12 skip", "chưa chứng minh giảm runtime", "63 finding cũ", "chưa được sửa", "Chưa cài", "bo_sot=5"]),
}
print(json.dumps({"checks": checks, "linked_content_count": len(links),
                  "missing_links": [row for row in links if not row["readable_nonempty"]],
                  "source_head": context["head"],
                  "report_sha256": hashlib.sha256(report_path.read_bytes()).hexdigest(),
                  "qc_sha256": hashlib.sha256(qc_path.read_bytes()).hexdigest()}, ensure_ascii=False, indent=2))
sys.exit(0 if all(checks.values()) else 1)
