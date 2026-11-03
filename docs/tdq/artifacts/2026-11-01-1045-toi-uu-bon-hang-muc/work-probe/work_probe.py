"""Emit observed per-case work, including Python CLI descendants."""
import hashlib
import json
import os
from pathlib import Path

import pytest


@pytest.hookimpl(wrapper=True)
def pytest_runtest_protocol(item, nextitem):
    previous = os.environ.get("TDQ_SCOPE_ACTIVE_CASE")
    os.environ["TDQ_SCOPE_ACTIVE_CASE"] = item.nodeid
    try:
        result = yield
    finally:
        if previous is None:
            os.environ.pop("TDQ_SCOPE_ACTIVE_CASE", None)
        else:
            os.environ["TDQ_SCOPE_ACTIVE_CASE"] = previous
        path = Path(os.environ["TDQ_SCOPE_WORK_LOG"])
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []
        rows = [row for row in rows if row["case_id"] == item.nodeid]
        counts = {kind: sum(row["kind"] == kind for row in rows)
                  for kind in ("git", "process", "calibration")}
        case_log = path.with_name(path.stem + "-" + hashlib.sha256(item.nodeid.encode()).hexdigest()[:12] + ".jsonl")
        case_log.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
        row = {"case_id": item.nodeid,
               "source_file_sha256": hashlib.sha256(Path(item.path).read_bytes()).hexdigest(),
               "subprocess_calls": counts["git"] + counts["process"],
               "calibration_calls": counts["calibration"], "git_calls": counts["git"],
               "observation_log": str(case_log), "observation_sha256": hashlib.sha256(case_log.read_bytes()).hexdigest()}
        print("\nTDQ_SCOPE_WORK " + json.dumps(row), flush=True)
    return result
