"""Prove when the QC radius reuses the same full-suite evidence; run no tests."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path.cwd() / "scripts"))
import tdq_test
import tdq_test_result

BASE = "3e0ef5f8a148cbf8aae1e932995e844e8f62ccd9"
REQUEST = "2026-10-27-1246-do-dung-bao-toan-loi"
root = str(Path.cwd())
head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
artifact_dir = Path("docs/tdq/artifacts") / REQUEST
context = json.loads((artifact_dir / "QC-F1-after-QC2.context.json").read_text(encoding="utf-8"))
receipt = json.loads((artifact_dir / "QC-F1-after-QC2.json").read_text(encoding="utf-8"))
changed = subprocess.check_output(
    ["git", "diff", "--name-only", BASE, "HEAD"], text=True).splitlines()
files = [name for name in changed if name.startswith(("scripts/", "tests/"))]
selected, reason = tdq_test.ban_kinh(files, root)
inventory = tdq_test._result_inventory(root)
full_rows = [row for row in tdq_test._doc_so(root)
             if row.get("kind") == "tron-bo" and row.get("request") == REQUEST]
full = full_rows[-1] if full_rows else {}
extra_label = "QC-F2-pytest-isolated"
extra_context = json.loads((artifact_dir / f"{extra_label}.context.json").read_text(encoding="utf-8"))
extra_receipt = json.loads((artifact_dir / f"{extra_label}.json").read_text(encoding="utf-8"))
xml = (artifact_dir / f"{extra_label}.xml").read_text(encoding="utf-8")
extra = tdq_test_result.from_junit_xml(xml, extra_receipt["exit_code"], inventory)
extra_modules, extra_complete = tdq_test._junit_modules(xml, inventory)
combined = set(full.get("modules", [])) | set(extra_modules)
consumers = ["test_tdq_finish.py", "test_archify_finish.py", "test_next_tron_bo.py",
             "test_token_audit.py", "test_step_budget.py"]
checks = {
    "fallback_selects_full": bool(reason) and selected == inventory,
    "full_pass": full.get("status") == "PASS" and full.get("details_complete") is True,
    "same_selected_inventory": full.get("selected_modules") == inventory,
    "all_selected_collected_in_combined_runs": set(selected) <= combined,
    "supplement_pass_complete": extra["status"] == "PASS" and extra["details_complete"] and extra_complete,
    "supplement_only_missing_modules": set(extra_modules) == set(inventory) - set(full.get("modules", [])),
    "supplement_same_head_and_source": extra_context["head"] == context["head"] and extra_context["source_sha256"] == context["source_sha256"],
    "supplement_normal_without_utf8_override": extra_context["elevated"] is False and all(value is None for value in extra_context["utf8_env"].values()),
    "consumers_collected": set(consumers) <= set(full.get("modules", [])),
    "changed_tests_collected": {Path(name).name for name in files if name.startswith("tests/")}
                               <= set(full.get("modules", [])),
    "same_source_head": head == context["head"],
    "same_source_bytes": all(Path(name).is_file() and hashlib.sha256(Path(name).read_bytes()).hexdigest() == digest
                             for name, digest in context["source_sha256"].items()),
    "final_command_pass": receipt["exit_code"] == 0,
    "normal_integrity_context": context["elevated"] is False,
    "no_global_utf8_override": all(value is None for value in context["utf8_env"].values()),
    "clean_source_tree": subprocess.run(
        ["git", "diff", "--quiet", "HEAD", "--", "scripts", "tests", "skills"]).returncode == 0,
}
output = {"head": head, "files": files, "selection_reason": reason,
          "selected_modules": selected, "full_record_timestamp": full.get("ts"),
          "full_tests_run": full.get("tests_run"), "full_collected_module_count": len(full.get("modules", [])),
          "supplement": extra, "supplement_modules": extra_modules,
          "combined_collected_module_count": len(combined), "checks": checks,
          "source_sha256": {name: hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in files}}
print(json.dumps(output, ensure_ascii=False, indent=2))
sys.exit(0 if all(checks.values()) else 1)
