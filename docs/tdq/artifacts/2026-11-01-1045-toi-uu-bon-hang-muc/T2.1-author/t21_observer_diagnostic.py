"""One observer diagnostic; preserve baseline test bytes and real CLI returns."""
import hashlib
import json
import os
from pathlib import Path
import runpy
import sys
import uuid

import pytest


HERE = Path(__file__).resolve().parent
CASE = "tests/test_tdq_test.py::So::test_so_json_dem_va_ngan_sach"


def _read_fixture(repo):
    ledger = repo / "docs/tdq/.tdq-test.jsonl"
    rows = ledger.read_text(encoding="utf-8") if ledger.is_file() else ""
    results = []
    for path in sorted((repo / "docs/tdq/cache").rglob("result.json")):
        content = path.read_bytes()
        results.append({"path": str(path), "sha256": hashlib.sha256(content).hexdigest(),
                        "payload": json.loads(content)})
    return {"ledger": rows, "results": results}


@pytest.hookimpl(wrapper=True)
def pytest_runtest_call(item):
    """Observe the selected case's actual CLI return, output and private ledger."""
    if item.nodeid != CASE:
        return (yield)
    original = item.module.chay_lenh
    folder = HERE / ("observer-diagnostic-" + uuid.uuid4().hex)
    folder.mkdir()
    calls = []

    def observed(repo, command, *args, **kwargs):
        result = original(repo, command, *args, **kwargs)
        row = {"command": [command, *args], "returncode": result.returncode,
               "stdout": result.stdout, "stderr": result.stderr,
               **_read_fixture(Path(repo))}
        calls.append(row)
        path = folder / (str(len(calls)) + ".json")
        path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        print("TDQ_T21_CALL " + json.dumps({"command": row["command"],
              "returncode": result.returncode, "artifact": str(path),
              "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}), flush=True)
        return result

    item.module.chay_lenh = observed
    try:
        result = yield
    finally:
        item.module.chay_lenh = original
        manifest = {"classification": "diagnostic only; no task certification",
                    "case_id": item.nodeid,
                    "source_file_sha256": hashlib.sha256(Path(item.path).read_bytes()).hexdigest(),
                    "plugin_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    "calls": len(calls)}
        (folder / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print("TDQ_T21_DIAGNOSTIC " + str(folder / "manifest.json"), flush=True)
    return result


if __name__ == "__main__":
    os.environ["PYTHONPATH"] = str(HERE) + os.pathsep + os.environ.get("PYTHONPATH", "")
    observer = HERE.parent / "measure_work.py"
    sys.argv = [str(observer), "-p", Path(__file__).stem, CASE]
    runpy.run_path(str(observer), run_name="__main__")
