"""Inspect declared unittest skips without executing the suite again."""
import json
from pathlib import Path
import unittest

tests = Path.cwd() / "tests"
suite = unittest.TestLoader().discover(str(tests), top_level_dir=str(tests))
pending = [suite]
skips = []
count = 0
while pending:
    case = pending.pop()
    if isinstance(case, unittest.TestSuite):
        pending.extend(case)
        continue
    count += 1
    method = getattr(case, case._testMethodName)
    if getattr(case, "__unittest_skip__", False):
        skips.append({"id": case.id(), "reason": case.__unittest_skip_why__})
    elif getattr(method, "__unittest_skip__", False):
        skips.append({"id": case.id(), "reason": method.__unittest_skip_why__})
print(json.dumps({"discovered_cases": count, "declared_skips": sorted(skips, key=lambda row: row["id"]),
                  "declared_skip_count": len(skips), "method": "discovery only, no test execution"},
                 ensure_ascii=False, indent=2))
