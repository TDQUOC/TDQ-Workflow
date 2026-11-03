import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

A = Path(__file__).resolve().parent
ROOT = A.parents[3]
collection = json.loads((A / "review-collection.json").read_text(encoding="utf-8"))
context = json.loads((A / "QC-F1-after-QC2.context.json").read_text(encoding="utf-8"))
ids = set(collection["unittest_ids"])
xml_summaries = []
for filename in ("QC-F2-pytest-isolated.xml", "review-missing.xml"):
    tree = ET.parse(A / filename)
    cases = list(tree.iter("testcase"))
    ids.update((c.attrib["classname"] + "." + c.attrib["name"]).removeprefix("tests.") for c in cases)
    xml_summaries.append({"file": filename, "cases": len(cases),
                          "skips": sum(c.find("skipped") is not None for c in cases),
                          "failures_or_errors": sum(c.find("failure") is not None or c.find("error") is not None for c in cases)})
expected = {item["normalized"] for item in collection["pytest_items"]}
source = context["source_sha256"]
checks = {
    "case_inventory_matches_combined_scope": ids == expected,
    "3306_unique_cases": len(ids) == 3306,
    "supplement_results_have_no_failures": all(x["failures_or_errors"] == 0 for x in xml_summaries),
    "head_unchanged": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == context["head"],
    "all_source_hashes_unchanged": all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == digest for p, digest in source.items()),
    "no_dirty_production_paths": not subprocess.check_output(["git", "status", "--porcelain", "--", "scripts", "tests", "hooks", "skills"], cwd=ROOT, text=True).strip(),
}
result = {"checks": checks, "source_file_count": len(source), "combined_cases": len(ids),
          "standard_skips": 13, "xml_summaries": xml_summaries,
          "qualification": "Standard unittest evidence reused from earlier same-source run, with fresh discovery mapping; diagnostic parallel ERROR and tokenizer FAIL are separate open findings, not erased by scope checks"}
(A / "review-final-proof.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
raise SystemExit(0 if all(checks.values()) else 1)
