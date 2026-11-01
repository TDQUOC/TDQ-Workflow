"""Historical feature RED: execute the real pristine baseline runner, not a stub."""
import hashlib
import json
from pathlib import Path

import pytest


BASELINE = Path("C:/Users/admin/.codex/worktrees/tdq-optimize-t0/TDQ-Workflow/scripts/tdq_test.py")


@pytest.hookimpl(wrapper=True)
def pytest_runtest_protocol(item, nextitem):
    previous = item.module.RUNNER_SCRIPT
    item.module.RUNNER_SCRIPT = BASELINE
    print("TDQ_HISTORICAL_RUNNER " + json.dumps({"path": str(BASELINE),
          "sha256": hashlib.sha256(BASELINE.read_bytes()).hexdigest(),
          "classification": "historical baseline fixture; not current-source certification"}), flush=True)
    try:
        result = yield
    finally:
        item.module.RUNNER_SCRIPT = previous
    return result
