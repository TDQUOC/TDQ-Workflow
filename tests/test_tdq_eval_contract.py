"""Offline contract checks; synthetic records never certify agent effectiveness."""
import ast
from copy import deepcopy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("eval_contract_test", ROOT / "scripts/tdq_eval_contract.py")
contract = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(contract)
H = "a" * 64
CELL = {"host": "fixture", "model": "offline-evaluator-v1", "permission_profile": "isolated",
        "tool_aliases": {"shell": ["Bash"]}, "cache_profile": "cold"}


def plan_data():
    return dict(plan_version="v1", experiment_id="experiment-1",
                targets={"skills/build/SKILL.md": H}, base_identity="b" * 40,
                candidate_identity="planned", change_kind="behavioral", hypothesis="Preserve checks",
                evaluation_kind="mechanism", corpus_id="corpus-v1", dev_cases_sha256="c" * 64,
                holdout_cases_sha256="d" * 64, rubric_version="v1", scorer_version="v1",
                expected_triggers=["positive"], negative_cases=["negative"],
                required_metrics=["trigger_accuracy", "outcome_quality", "efficiency_metrics"],
                cells=[deepcopy(CELL)], repetitions=2, order_policy="AB_BA",
                thresholds={"min_pairs": 2, "quality_margin": 0.01, "efficiency_margin": 0.1})


def manifest():
    return dict(deepcopy(CELL), base_commit="b" * 40, candidate_commit="e" * 64,
                scorer_version="v1", corpus_version="corpus-v1", check_set=["oracle"],
                evaluation_kind="mechanism", rubric_version="v1")


def record(score=0.8, tokens=1000):
    return dict(deepcopy(CELL), manifest=manifest(), raw_trace_sha256=H,
                outcome_sha256=H, experiment_hash=H, provenance="synthetic/offline",
                evaluation_kind="mechanism", execution_status="completed", passed=score == 1,
                score=score, checks={"oracle": score == 1}, expected_trigger=True,
                observed_trigger=True, trigger_provenance="fixture-event",
                tokens={"input_tokens": tokens, "output_tokens": 100,
                        "cache_read_tokens": 0, "cache_write_tokens": 0})


def pairs(base=0.8, candidate=0.8, tokens=1000):
    return [dict(pair_id=f"p{i}", baseline=record(base), candidate=record(candidate, tokens))
            for i in range(3)]


def evidence(plan):
    schedule = contract.build_ab_ba_schedule(
        plan["expected_triggers"] + plan["negative_cases"], plan["cells"],
        plan["repetitions"], contract.compute_experiment_hash(plan))
    rows = []
    for trial in schedule:
        row = dict(record(1), **trial)
        row.update({k: deepcopy(plan[k]) for k in (
            "base_identity", "candidate_identity", "targets", "dev_cases_sha256",
            "holdout_cases_sha256", "scorer_version", "rubric_version", "evaluation_kind")})
        row["expected_trigger"] = trial["case_id"] in plan["expected_triggers"]
        row["observed_trigger"] = row["expected_trigger"]
        rows.append(row)
    return rows


@pytest.mark.parametrize("path", ["skills/build/SKILL.md", "skills/build/references/qc.md",
    "agents/build.md", "hooks/check.py", ".claude-plugin/plugin.json", ".agents/plugins/a.json",
    ".opencode/plugins/a.js", "manifest.json"])
def test_behavioral(path):
    assert contract.classify_target(path)["change_kind"] == "behavioral"


def test_runtime_requires_explicit_context():
    path = "scripts/tdq_app.py"
    assert not contract.classify_target(path)["requires_eval"]
    assert contract.classify_targets(path, runtime_plugin_targets=[path])["behavioral_targets"] == [path]


@pytest.mark.parametrize("path,kind", [("README.md", "docs_only"), ("CHANGELOG-1.md", "docs_only"),
    ("docs/guide.md", "docs_only"), ("docs/tdq/plan/a.md", "bookkeeping"),
    ("graphify-out/a.json", "bookkeeping"), ("src/main.py", "app_code")])
def test_exempt(path, kind):
    result = contract.classify_target(path)
    assert result["change_kind"] == kind
    assert result["requires_eval"] is False


@pytest.mark.parametrize("path", ["", "../a", "skills/../README.md", "/tmp/a", "C:\\a",
    "docs/a.md:stream", "docs//a.md", "docs/a.md ", "docs/./a.md", "unknown.conf"])
def test_fail_closed_paths(path):
    assert contract.classify_target(path)["change_kind"] == "review-required"


def test_bookkeeping_only_when_diff_proves_no_instruction_change():
    path = "skills/build/SKILL.md"
    assert not contract.classify_target(path, "-- [ ] task\n+- [x] task")["requires_eval"]
    assert contract.classify_target(path, "-- [ ] old rule\n+- [x] new rule")["requires_eval"]
    assert not contract.classify_target(path, "-Ngày: 2026-01-01\n+Ngày: 2026-02-01")["requires_eval"]
    assert contract.classify_target(path, "-Ngày: old\n+Ngày: skip safety checks")["requires_eval"]
    assert contract.classify_target("README.md", "new file mode 120000")["requires_eval"]
    assert contract.classify_targets([])["requires_eval"]
    assert contract.phan_loai_target(path) == contract.classify_target(path)


def test_plan_create_hash_and_no_mutation():
    raw = plan_data()
    plan = contract.create_eval_plan(**raw)
    assert contract.validate_eval_plan(plan)["valid"]
    assert contract.compute_experiment_hash(plan) == contract.compute_experiment_hash(dict(reversed(list(plan.items()))))
    before = contract.compute_experiment_hash(plan)
    plan["holdout_cases_sha256"] = "f" * 64
    assert contract.compute_experiment_hash(plan) != before
    assert raw["holdout_cases_sha256"] == "d" * 64


@pytest.mark.parametrize("field", list(plan_data()))
def test_missing_plan_fields(field):
    plan = plan_data()
    del plan[field]
    assert not contract.validate_eval_plan(plan)["valid"]


@pytest.mark.parametrize("value", ["latest", "default", "auto", "", "model-latest"])
def test_model_alias(value):
    plan = plan_data()
    plan["cells"][0]["model"] = value
    assert not contract.validate_eval_plan(plan)["valid"]


@pytest.mark.parametrize("field,value", [("repetitions", True), ("repetitions", 0),
    ("base_identity", "main"), ("candidate_identity", "branch"), ("targets", {}),
    ("cells", []), ("order_policy", "AB"), ("evaluation_kind", "unknown"),
    ("thresholds", {"x": float("nan")}), ("thresholds", {"x": float("inf")})])
def test_bad_plan(field, value):
    plan = plan_data()
    plan[field] = value
    assert not contract.validate_eval_plan(plan)["valid"]


def test_gate_complete_coverage_and_staleness():
    plan = plan_data()
    assert contract.check_eval_gate(plan)["verdict"] == "PASS"
    assert contract.check_eval_gate(plan, "pre_report")["verdict"] == "INCOMPLETE"
    plan["candidate_identity"] = "e" * 64
    rows = evidence(plan)
    assert contract.check_eval_gate(plan, "pre_report", plan["targets"], rows)["verdict"] == "PASS"
    for incomplete in ([], rows[:-1], rows + [rows[0]]):
        assert contract.check_eval_gate(plan, "pre_report", plan["targets"], incomplete)["verdict"] == "INCOMPLETE"
    assert contract.check_eval_gate(plan, "pre_report", {}, rows)["reason"] == "stale_target_hash"
    for field in ("experiment_hash", "raw_trace_sha256", "candidate_identity", "evaluation_kind",
                  "holdout_cases_sha256", "permission_profile", "scorer_version", "provenance"):
        stale = deepcopy(rows)
        stale[0][field] = "stale"
        assert contract.check_eval_gate(plan, "pre_report", plan["targets"], stale)["verdict"] == "INCOMPLETE", field


def test_gate_unavailable_metrics_and_wrong_claim():
    plan = plan_data()
    plan["candidate_identity"] = "e" * 64
    rows = evidence(plan)
    del rows[0]["observed_trigger"]
    assert contract.check_eval_gate(plan, "pre_report", plan["targets"], rows)["verdict"] == "INCOMPLETE"
    plan["evaluation_kind"] = "agent-effectiveness"
    rows = evidence(plan)
    assert contract.check_eval_gate(plan, "pre_report", plan["targets"], rows)["verdict"] == "INCOMPLETE"


def test_waiver_not_pass_or_live_authorization():
    waiver = {"reason": "mechanism only", "by": "user:explicit", "scope": "request-1"}
    result = contract.check_eval_gate(None, waiver=waiver)
    assert result["verdict"] == "WAIVED_USER"
    assert result["passed"] is False
    assert result["live_run_authorized"] is False
    assert contract.check_eval_gate(None, waiver=dict(waiver, by="agent"))["verdict"] != "WAIVED_USER"
    assert contract.check_eval_gate(plan_data(), stage="typo")["verdict"] != "PASS"


@pytest.mark.parametrize("field", ["host", "model", "permission_profile", "scorer_version",
    "corpus_version", "check_set", "tool_aliases", "cache_profile", "evaluation_kind", "rubric_version"])
def test_identity_mismatch_and_missing(field):
    base = manifest()
    assert contract.validate_paired_identity(base, deepcopy(base))["valid"]
    candidate = deepcopy(base)
    candidate[field] = "different"
    result = contract.validate_paired_identity(base, candidate)
    assert not result["valid"] and field in result["mismatched_fields"]
    del candidate[field]
    assert not contract.validate_paired_identity(base, candidate)["valid"]


def test_baseline_probes_and_legacy_never_certified():
    baseline = json.loads((ROOT / "docs/tdq/artifacts/2026-11-01-1854-eval-chat-luong-skill/analysis-baseline.json").read_text(encoding="utf-8"))
    assert len(baseline["mismatched_identity_probes"]) == 4
    for probe in baseline["mismatched_identity_probes"]:
        candidate = manifest()
        candidate[probe["changed_field"]] = "mismatch"
        assert not contract.validate_paired_identity(manifest(), candidate)["accepted"]
    for field in ("host", "model", "raw_trace_sha256", "experiment_hash"):
        old = record()
        del old[field]
        assert contract.classify_record_provenance(old) == "historical_unverified"
    assert contract.classify_record_provenance(record()) == "synthetic/offline"
    assert not contract.validate_paired_identity(manifest(), dict(manifest(), candidate_commit="main"))["valid"]


def test_metrics_missing_zero_partial_and_no_mutation():
    raw = {}
    result = contract.normalize_trial_metrics(raw)
    assert raw == {}
    assert result["trigger_accuracy"]["matched"] is None
    assert result["outcome_quality"]["passed"] is None
    efficiency = result["efficiency_metrics"]
    assert efficiency["cost"]["total_cost_usd"] is None
    assert efficiency["cost"]["availability"] == "unavailable"
    for key in ("wall_latency_seconds", "tool_calls_count", "model_calls_count", "retries_count", "user_interventions_count"):
        assert efficiency[key] is None
    result = contract.normalize_trial_metrics({"tokens": {"input_tokens": 0}, "total_cost_usd": 0})
    assert result["efficiency_metrics"]["tokens"]["availability"] == "partial"
    assert result["efficiency_metrics"]["cost"]["observed_usage"] == 0


@pytest.mark.parametrize("status", ["failed", "timeout", "missing", "unknown_schema", "unexpected"])
def test_failure_never_pass(status):
    result = contract.normalize_trial_metrics(dict(record(1), execution_status=status))
    assert result["outcome_quality"]["passed"] is not True
    assert result["outcome_quality"]["score"] != 1


def test_trigger_requires_boolean_observation_and_provenance():
    for overrides in ({"observed_trigger": None}, {"observed_trigger": "yes"}, {"trigger_provenance": ""}):
        assert contract.normalize_trial_metrics(dict(record(), **overrides))["trigger_accuracy"]["matched"] is None


def test_rate_estimate_is_not_bill_and_requires_complete_usage():
    card = {"source": "test-snapshot", "snapshot_at": "2026-11-01T00:00:00Z",
            "rates": {"input_per_mtok": 3, "output_per_mtok": 15,
                      "cache_read_per_mtok": 1, "cache_write_per_mtok": 4}}
    raw = record()
    raw.update(total_cost_usd=0.2, billed_cost_usd=0.3)
    cost = contract.normalize_trial_metrics(raw, card)["efficiency_metrics"]["cost"]
    assert cost["observed_usage"] == 0.2
    assert cost["provider_billed"] == 0.3
    assert cost["rate_estimate"] == pytest.approx(0.0045)
    del raw["tokens"]["cache_read_tokens"]
    assert contract.normalize_trial_metrics(raw, card)["efficiency_metrics"]["cost"]["rate_estimate"] is None
    with pytest.raises(ValueError):
        contract.normalize_trial_metrics(raw, {"rates": {}})


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -1, True, "12"])
def test_invalid_numeric_metric_rejected(value):
    with pytest.raises(ValueError):
        contract.normalize_trial_metrics({"total_cost_usd": value})


def test_schedule_deterministic_unique_balanced():
    args = (["one", "two"], [CELL], 2, H)
    schedule = contract.build_ab_ba_schedule(*args)
    assert schedule == contract.build_ab_ba_schedule(*args)
    assert len(schedule) == len({r["trial_id"] for r in schedule}) == 8
    assert [r["variant"] for r in schedule if r["case_id"] == "one"] == ["A", "B", "B", "A"]
    assert all(r["experiment_hash"] == H for r in schedule)
    with pytest.raises(ValueError):
        contract.build_ab_ba_schedule(["one", "one"], [CELL], 2, H)


@pytest.mark.parametrize("base,candidate,tokens,verdict", [(1, 1, 1000, "INCONCLUSIVE"),
    (1, 1, 600, "TRIM"), (0.5, 1, 1000, "KEEP"), (1, 0.5, 1000, "DROP")])
def test_recommendation(base, candidate, tokens, verdict):
    result = contract.evaluate_cell_recommendation(pairs(base, candidate, tokens), plan_data()["thresholds"])
    assert result["verdict"] == verdict
    assert result["auto_mutate_allowed"] is False
    assert result["sample_count"] == 3
    assert result["provenance"] == "synthetic/offline"


def test_no_recommendation_from_missing_policy_samples_or_invalid_pairs():
    assert contract.evaluate_cell_recommendation(pairs(1, 0))["verdict"] == "INCONCLUSIVE"
    policy = plan_data()["thresholds"]
    assert contract.evaluate_cell_recommendation(pairs(1, 0)[:1], policy)["verdict"] == "INCONCLUSIVE"
    for field in ("model", "experiment_hash", "manifest", "observed_trigger", "raw_trace_sha256"):
        rows = pairs(1, 0)
        del rows[0]["candidate"][field]
        assert contract.evaluate_cell_recommendation(rows, policy)["verdict"] == "INCONCLUSIVE"
    rows = pairs(1, 0)
    rows.append(rows[0])
    assert contract.evaluate_cell_recommendation(rows, policy)["verdict"] == "INCONCLUSIVE"


def test_pair_manifest_binds_cell_and_complexity_savings():
    policy = plan_data()["thresholds"]
    rows = pairs(0.5, 1)
    rows[0]["baseline"]["manifest"]["host"] = "other"
    rows[0]["candidate"]["manifest"]["host"] = "other"
    assert contract.evaluate_cell_recommendation(rows, policy)["verdict"] == "INCONCLUSIVE"
    rows = pairs(1, 1)
    for row in rows:
        row["baseline"]["complexity_count"] = 20
        row["candidate"]["complexity_count"] = 10
    assert contract.evaluate_cell_recommendation(rows, policy)["verdict"] == "TRIM"


def test_malformed_schema_never_crashes_gate():
    for field, value in (("evaluation_kind", []), ("change_kind", {}), ("cells", [None])):
        plan = plan_data()
        plan[field] = value
        assert contract.check_eval_gate(plan)["verdict"] == "INCOMPLETE"


def test_logging_and_pure_core(monkeypatch, capsys):
    monkeypatch.delenv("TDQ_LOG", raising=False)
    monkeypatch.delenv("TDQ_EVAL_LOG", raising=False)
    contract.log("check", experiment="exp-1", reason="token=secret", prompt="raw prompt")
    output = capsys.readouterr().err
    assert "experiment=exp-1" in output and "thong-tin" in output
    assert "secret" not in output and "raw prompt" not in output
    monkeypatch.setenv("TDQ_LOG", "off")
    contract.log("silent")
    assert capsys.readouterr().err == ""
    tree = ast.parse((ROOT / "scripts/tdq_eval_contract.py").read_text(encoding="utf-8"))
    imports = [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
    imports += [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
    assert not ({"subprocess", "hooks", "pathlib"} & set(imports))
