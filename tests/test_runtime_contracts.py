"""Cross-layer contracts exercised with isolated, tiny real projects."""
import ast
import hashlib
import io
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile

import pytest

from helper import ROOT
import tdq_state
import tdq_test as runner


RUNTIME_MODULES = ("tdq_test", "tdq_test_manifest", "tdq_test_result",
                   "tdq_test_process", "tdq_test_receipt", "tdq_readiness",
                   "tdq_transcript", "tdq_transcript_cache", "tdq_runtime_bench")
STATE_READ_CALLS = {"now_iso", "log_enabled", "resolve_project_dir"}


def boundary_violations(source, module):
    """Inspect imports and calls, including aliases; not comments/path literals."""
    tree = ast.parse(source)
    aliases, violations = {}, []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            aliases.update({item.asname or item.name: item.name for item in node.names})
        elif isinstance(node, ast.ImportFrom):
            aliases.update({item.asname or item.name: (node.module or "") + "." + item.name
                            for item in node.names})
    for name in aliases.values():
        if name.split(".")[0] in {"hooks", "tests"}:
            violations.append("reverse dependency: " + name)
        if name.split(".")[0] == "tdq_state" and module != "tdq_test":
            violations.append("state dependency: " + name)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = ast.unparse(node.func)
        head, _, tail = function.partition(".")
        qualified = aliases.get(head, head) + ("." + tail if tail else "")
        if qualified.startswith("tdq_state.") and qualified.removeprefix("tdq_state.") not in STATE_READ_CALLS:
            violations.append("state write dependency: " + qualified)
    return violations


@pytest.mark.parametrize("module", RUNTIME_MODULES)
def test_runtime_dependency_boundary(module):
    source = Path(ROOT, "scripts", module + ".py").read_text(encoding="utf-8")
    assert boundary_violations(source, module) == []


@pytest.mark.parametrize("source", [
    "import hooks.scripts.stop_gate as gate\ngate.main()",
    "from tests.helper import ROOT",
    "import tdq_state as state\nstate.save_state('project', {})",
    "from tdq_state import save_state as write\nwrite('project', {})",
])
def test_dependency_guard_detects_reverse_import_and_aliased_state_write(source):
    assert boundary_violations(source, "tdq_test")
    assert not boundary_violations(
        "import tdq_state as state\nstate.log_enabled()\n"
        "text = 'hooks/scripts/stop_gate.py and state.json'", "tdq_test")


@pytest.fixture
def project():
    # Short owned root avoids adding long pytest node names to receipt paths on Windows.
    with tempfile.TemporaryDirectory(prefix="tdq-contract-") as directory:
        root = Path(directory)
        (root / "tests").mkdir()
        (root / "docs/tdq").mkdir(parents=True)
        (root / "docs/tdq/state.json").write_text(json.dumps({
            "active_request": "contract", "phase": "implement", "lane": "full"}), encoding="utf-8")
        yield root


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_project(project, **options):
    return runner.chay_tron_bo_result(project, io.StringIO(), request="contract",
                                      job_kind="correctness", timeout_seconds=30, **options)


def declare_fixture(project):
    source = project / "tests/test_case.py"
    proof = project / "dependency_proof.py"
    proof.write_text("def test_proof(): assert 2 + 3 == 5\n", encoding="utf-8")
    declaration = {"hermetic": True, "no_network": True, "no_live_clock": True,
                   "no_personal_config": True, "external_inputs": [], "env_names": [],
                   "input_paths": ["tests/test_case.py"], "test_source_sha256": digest(source),
                   "proof": {"test_id": "dependency_proof.py::test_proof",
                             "test_path": proof.name, "source_sha256": digest(proof)}}
    (project / "docs/tdq/reuse-policy.json").write_text(json.dumps({
        "schema_version": 1, "cases": {"tests/test_case.py::test_ok": declaration}}), encoding="utf-8")


def test_mixed_failure_survives_artifact_ledger_and_existing_state_consumer(project):
    source = '''import pytest, unittest
def test_pass(): assert 2 + 3 == 5
def test_skip(): pytest.skip()
@pytest.fixture
def finalizer():
    yield
    raise RuntimeError("contract teardown failure")
def test_error(finalizer): assert True
class Legacy(unittest.TestCase):
    def test_children(self):
        with self.subTest(value=1): self.fail("contract subtest failure")
'''
    (project / "tests/test_case.py").write_text(source, encoding="utf-8")
    state_path = project / "docs/tdq/state.json"
    state_before = state_path.read_bytes()
    ledger = project / "docs/tdq/.tdq-test.jsonl"
    legacy = {"kind": "tron-bo", "request": "contract", "ok": True}
    ledger.write_text("\n".join(json.dumps(row) for row in [legacy] * 3) + "\n", encoding="utf-8")
    result = run_project(project)
    assert result["status"] == "ERROR" and result["tests_run"] == 4
    assert not result["details_complete"] and not result["coverage"]["complete"]
    assert result["failed_modules"] == ["test_case.py"]
    failures = json.dumps(result["failures"])
    assert "contract teardown failure" in failures and "contract subtest failure" in failures
    assert result["process"]["execution"]["exit_code"] == 1
    assert result["process"]["execution"]["cleanup_complete"]
    marker = result["result_artifact"]
    assert digest(marker["path"]) == marker["sha256"]
    persisted = json.loads(Path(marker["path"]).read_text(encoding="utf-8"))
    for item in persisted["evidence"].values():
        assert digest(item["path"]) == item["sha256"]
    row = json.loads(ledger.read_text(encoding="utf-8").splitlines()[-1])
    assert row["status"] == persisted["status"] == "ERROR"
    assert row["failures"] == persisted["failures"] == result["failures"]
    assert row["result_artifact"] == marker and row["timings"] == result["timings"]
    assert "case_outcomes" not in row and row["coverage_summary"]["complete"] is False
    with ledger.open("a", encoding="utf-8") as stream:
        for action in ("reused", "joined"):
            stream.write(json.dumps(dict(row, action=action)) + "\n")
    counts = runner.dem_repo(project, "contract")
    assert (counts["tron_bo"], counts["ngan_sach"]) == (4, 3)
    assert tdq_state._tron_bo_vuot(project, json.loads(state_before)) == (4, 3)
    cli = subprocess.run([sys.executable, str(Path(ROOT, "scripts/tdq_test.py")),
                          "so", "--repo", str(project), "--json"],
                         capture_output=True, text=True, encoding="utf-8", timeout=15)
    assert cli.returncode == 0, cli.stderr
    assert json.loads(cli.stdout) == counts
    assert state_path.read_bytes() == state_before


def test_fresh_off_rollback_revokes_warm_receipt_and_preserves_timing_accounting(project):
    (project / "tests/test_case.py").write_text("def test_ok(): assert 2 + 3 == 5\n", encoding="utf-8")
    declare_fixture(project)
    state_path = project / "docs/tdq/state.json"
    before = state_path.read_bytes()
    environment = dict(os.environ)
    options = ({"reuse": "auto"}, {"reuse": "auto"},
               {"reuse": "off", "fresh": True}, {"reuse": "auto"}, {})
    runs = [run_project(project, environment=environment, **option) for option in options]
    assert [result["action"] for result in runs] == ["executed", "reused", "executed", "executed", "executed"]
    assert all(result["status"] == "PASS" for result in runs)
    assert runs[1]["source_receipt_id"] == runs[0]["source_receipt_id"]
    assert runs[2]["source_receipt_id"] is runs[4]["source_receipt_id"] is None
    assert runs[3]["source_receipt_id"] != runs[0]["source_receipt_id"]
    assert runs[1]["timings"]["execute_seconds"] == runs[1]["timings"]["wait_seconds"] == 0
    for result in runs:
        assert all(type(value) in (int, float) and math.isfinite(value) and value >= 0
                   for value in result["timings"].values())
        timings = result["timings"]
        assert timings["wall_seconds"] >= sum(timings[key] for key in
            ("collection_seconds", "execute_seconds", "wait_seconds", "verify_seconds"))
    assert runner.dem_repo(project, "contract")["tron_bo"] == 4
    assert tdq_state._tron_bo_vuot(project, json.loads(before)) == (4, 2)
    assert state_path.read_bytes() == before


def test_document_noop_never_launches_or_consumes_full_budget(project, monkeypatch, capsys):
    state = project / "docs/tdq/state.json"
    before = state.read_bytes()
    (project / "README.md").write_text("documentation only\n", encoding="utf-8")
    def unexpected_job(*args, **kwargs):
        pytest.fail("A document-only no-op launched a test job")
    monkeypatch.setattr(runner, "IsolatedJob", unexpected_job)
    assert runner.main(["vung-cham", "--repo", str(project), "--files", "README.md"]) == 0
    assert "SKIP" in capsys.readouterr().out
    row = json.loads((project / "docs/tdq/.tdq-test.jsonl").read_text(encoding="utf-8"))
    assert row["status"] == "SKIP" and row["tests_run"] == 0 and row["ok"] is None
    assert not runner.co_vung_cham([row], "contract")
    assert runner.dem_repo(project, "contract")["tron_bo"] == 0
    assert tdq_state._tron_bo_vuot(project, json.loads(before)) is None
    assert state.read_bytes() == before
