import contextlib
from datetime import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
import xml.etree.ElementTree as ET

artifact = Path(__file__).resolve().parent
root = artifact.parents[3]
os.chdir(root)
sys.path.insert(0, str(root / "tests"))
sys.path.insert(0, str(root / "scripts"))
config = Path.home() / ".claude" / "CLAUDE.md"
config_before = hashlib.sha256(config.read_bytes()).hexdigest()
started = time.perf_counter()

def flatten(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from flatten(test)
        else:
            yield test

class Inventory:
    def __init__(self):
        self.items = []

    def pytest_collection_finish(self, session):
        self.items = [{"nodeid": item.nodeid, "kind": type(item).__name__}
                      for item in session.items]

buffer = io.StringIO()
with tempfile.TemporaryDirectory(prefix="tdq-review-collection-") as temporary:
    home = Path(temporary) / "home"
    home.mkdir()
    os.environ.update(HOME=str(home), USERPROFILE=str(home),
                      TDQ_KHONG_CHAM_MAY="1", TDQ_KHOI_TAO_NEN="0",
                      PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
        unittest_cases = list(flatten(unittest.defaultTestLoader.discover(str(root / "tests"))))
        unittest_ids = {test.id().removeprefix("tests.") for test in unittest_cases}
        import pytest
        plugin = Inventory()
        exit_code = pytest.main(["tests", "--collect-only", "-q", "-p", "no:cacheprovider"], plugins=[plugin])

prior_xml = ET.fromstring((artifact / "QC-F2-pytest-isolated.xml").read_text(encoding="utf-8"))
prior_extra = {(node.attrib["classname"] + "." + node.attrib["name"]).removeprefix("tests.")
               for node in prior_xml.iter("testcase")}
covered = unittest_ids | prior_extra
missing = []
for item in plugin.items:
    parts = item["nodeid"].split("::")
    normalized = ".".join([Path(parts[0]).stem] + parts[1:])
    item["normalized"] = normalized
    if normalized not in covered:
        missing.append(item)
pytest_ids = {item["normalized"] for item in plugin.items}
result = {
    "at": datetime.now().astimezone().isoformat(timespec="seconds"),
    "seconds": round(time.perf_counter() - started, 3),
    "pytest_exit_code": int(exit_code),
    "unittest_count": len(unittest_cases), "unittest_unique_ids": len(unittest_ids),
    "pytest_count": len(plugin.items), "previous_pytest_supplement": len(prior_extra),
    "previous_combined_unique_ids": len(covered),
    "unittest_missing_from_pytest": sorted(unittest_ids - pytest_ids),
    "pytest_cases_not_in_previous_evidence": missing,
    "checks": {"collection_success": exit_code == 0,
               "no_unittest_loader_errors": not any(isinstance(test, unittest.loader._FailedTest) for test in unittest_cases),
               "same_unittest_count_as_full": len(unittest_cases) == 3206,
               "all_pytest_cases_previously_covered": not missing,
               "real_user_config_unchanged": hashlib.sha256(config.read_bytes()).hexdigest() == config_before},
    "unittest_ids": sorted(unittest_ids), "pytest_items": plugin.items,
}
(artifact / "review-collection.stdout.txt").write_text(buffer.getvalue(), encoding="utf-8")
(artifact / "review-collection.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({key: value for key, value in result.items() if key not in {"unittest_ids", "pytest_items"}}, ensure_ascii=False, indent=2))
sys.exit(0 if all(result["checks"].values()) else 1)
