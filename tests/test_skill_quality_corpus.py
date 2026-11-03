"""Integrity and contract integration tests for evals/skill-quality/corpus.json."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = ROOT / "evals" / "skill-quality" / "corpus.json"
SPEC = importlib.util.spec_from_file_location("tdq_eval_contract", ROOT / "scripts" / "tdq_eval_contract.py")
contract = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(contract)

REQUIRED_CASE_FIELDS = {
    "case_id",
    "split",
    "category",
    "target_skill",
    "prompt",
    "changed_files",
    "expected_trigger",
    "expected_requires_eval",
    "oracle",
    "evaluation_kind",
}
VALID_CATEGORIES = {
    "positive_trigger",
    "negative_no_trigger",
    "docs_exempt",
    "app_code_exempt",
    "error_handling",
}
FORBIDDEN_PROMPT_LEAKS = re.compile(
    r"\bL\d{3}\b|tdq_state\.py|tdq_eval_contract|classify_targets|expected_trigger"
    r"|expected_requires_eval|SKILL\.md|--bo-qua-lsp",
    re.I,
)


def _load_corpus():
    assert CORPUS_PATH.is_file(), f"Missing corpus file: {CORPUS_PATH}"
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


def _canonical_sha256(value):
    payload = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def test_corpus_top_level_metadata_and_live_separation():
    corpus = _load_corpus()
    assert corpus["corpus_id"] == "tdq-skill-quality"
    assert corpus["corpus_version"] == "skill-quality-v1"
    assert corpus["schema_version"] == "v1"
    assert corpus["evaluation_scope"] == "synthetic-fixture-and-case-definitions"
    assert corpus["live_effectiveness_certified"] is False
    assert corpus["rubric_version"] == "rubric-v1"
    assert corpus["scorer_version"] == "v2-temporal"
    assert set(corpus["splits"].keys()) == {"dev", "holdout"}
    assert len(corpus["splits"]["dev"]) >= 6
    assert len(corpus["splits"]["holdout"]) >= 4


def test_dev_holdout_disjoint_and_case_schema():
    corpus = _load_corpus()
    dev_cases = corpus["splits"]["dev"]
    holdout_cases = corpus["splits"]["holdout"]
    dev_ids = {c["case_id"] for c in dev_cases}
    holdout_ids = {c["case_id"] for c in holdout_cases}
    dev_prompts = {c["prompt"].strip() for c in dev_cases}
    holdout_prompts = {c["prompt"].strip() for c in holdout_cases}

    assert len(dev_ids) == len(dev_cases)
    assert len(holdout_ids) == len(holdout_cases)
    assert dev_ids.isdisjoint(holdout_ids)
    assert dev_prompts.isdisjoint(holdout_prompts)

    all_cases = dev_cases + holdout_cases
    for split_name, group in (("dev", dev_cases), ("holdout", holdout_cases)):
        for case in group:
            assert REQUIRED_CASE_FIELDS <= set(case.keys())
            assert case["split"] == split_name
            assert case["category"] in VALID_CATEGORIES
            assert isinstance(case["target_skill"], str) and case["target_skill"].strip()
            assert isinstance(case["changed_files"], list) and case["changed_files"]
            assert isinstance(case["expected_trigger"], bool)
            assert isinstance(case["expected_requires_eval"], bool)
            assert case["evaluation_kind"] in {"mechanism", "agent-effectiveness"}
            oracle = case["oracle"]
            assert isinstance(oracle, dict)
            assert isinstance(oracle.get("required_checks"), list) and oracle["required_checks"]
            assert isinstance(oracle.get("forbidden_actions"), list) and oracle["forbidden_actions"]
            assert isinstance(oracle.get("expected_outcome"), str) and oracle["expected_outcome"].strip()

    categories = {c["category"] for c in all_cases}
    assert {"positive_trigger", "negative_no_trigger", "docs_exempt", "app_code_exempt"} <= categories
    assert any(c["expected_trigger"] is True for c in all_cases)
    assert any(c["expected_trigger"] is False for c in all_cases)
    assert {c["evaluation_kind"] for c in all_cases} == {"mechanism", "agent-effectiveness"}


def test_forward_test_prompts_do_not_leak_internal_answers():
    corpus = _load_corpus()
    for case in corpus["splits"]["dev"] + corpus["splits"]["holdout"]:
        prompt = case["prompt"]
        assert isinstance(prompt, str) and len(prompt.strip()) >= 20
        assert FORBIDDEN_PROMPT_LEAKS.search(prompt) is None, f"Leak in {case['case_id']}: {prompt}"


def test_contract_classify_targets_and_eval_plan_binding():
    corpus = _load_corpus()
    all_cases = corpus["splits"]["dev"] + corpus["splits"]["holdout"]
    for case in all_cases:
        classification = contract.classify_targets(case["changed_files"])
        assert classification["requires_eval"] is case["expected_requires_eval"], case["case_id"]
        if case["category"] == "docs_exempt":
            assert classification["change_kind"] == "docs_only"
        elif case["category"] == "app_code_exempt":
            assert classification["change_kind"] == "app_code"

    dev_sha = _canonical_sha256(corpus["splits"]["dev"])
    holdout_sha = _canonical_sha256(corpus["splits"]["holdout"])
    positive_ids = [c["case_id"] for c in all_cases if c["expected_trigger"]]
    negative_ids = [c["case_id"] for c in all_cases if not c["expected_trigger"]]

    plan = contract.create_eval_plan(
        experiment_id="exp-skill-quality-corpus-v1",
        targets={"skills/tdq-intake/SKILL.md": "a" * 64},
        base_identity="b" * 40,
        candidate_identity="planned",
        change_kind="behavioral",
        hypothesis="Corpus dev and holdout bind cleanly into v1 eval plan",
        evaluation_kind="mechanism",
        corpus_id=corpus["corpus_id"],
        dev_cases_sha256=dev_sha,
        holdout_cases_sha256=holdout_sha,
        rubric_version=corpus["rubric_version"],
        scorer_version=corpus["scorer_version"],
        expected_triggers=positive_ids,
        negative_cases=negative_ids,
        required_metrics=["trigger_accuracy", "outcome_quality", "efficiency_metrics"],
        cells=[{
            "host": "claude-code",
            "model": "claude-sonnet-4-20250514",
            "permission_profile": "isolated-worktree",
            "tool_aliases": {"shell": ["Bash", "PowerShell"]},
            "cache_profile": "cold",
        }],
        repetitions=2,
        order_policy="AB_BA",
        thresholds={"min_pairs": 2, "quality_margin": 0.02, "efficiency_margin": 0.1},
    )
    validation = contract.validate_eval_plan(plan)
    assert validation == {"valid": True, "errors": []}


def test_synthetic_traces_normalization_and_fail_closed_semantics():
    corpus = _load_corpus()
    traces = corpus["synthetic_traces"]
    assert isinstance(traces, dict)
    required_keys = {
        "completed_full_usage",
        "partial_tokens_missing_cost",
        "tool_error_false_success_text",
        "missing_tool_result",
        "unknown_schema_trace",
    }
    assert required_keys <= set(traces.keys())

    for name, trace in traces.items():
        assert trace.get("live_effectiveness_certified") is False, name
        assert contract.classify_record_provenance(trace) != "live_unverified", name

    full = contract.normalize_trial_metrics(traces["completed_full_usage"])
    assert full["outcome_quality"]["passed"] is True
    assert full["efficiency_metrics"]["tokens"]["availability"] == "available"
    assert full["efficiency_metrics"]["cost"]["availability"] == "available"
    assert full["efficiency_metrics"]["cost"]["total_cost_usd"] == 0.0125

    partial = contract.normalize_trial_metrics(traces["partial_tokens_missing_cost"])
    assert partial["efficiency_metrics"]["tokens"]["availability"] == "partial"
    assert partial["efficiency_metrics"]["cost"]["total_cost_usd"] is None
    assert partial["efficiency_metrics"]["cost"]["availability"] == "unavailable"

    for bad_key in ("tool_error_false_success_text", "missing_tool_result", "unknown_schema_trace"):
        normalized = contract.normalize_trial_metrics(traces[bad_key])
        assert normalized["outcome_quality"]["passed"] is not True, bad_key

    err_trace = traces["tool_error_false_success_text"]
    assert err_trace["is_error"] is True
    assert "Thành công" in err_trace["final_text"]
    err_norm = contract.normalize_trial_metrics(err_trace)
    assert err_norm["outcome_quality"]["passed"] is False
    assert err_norm["outcome_quality"]["score"] == 0.0

    missing_norm = contract.normalize_trial_metrics(traces["missing_tool_result"])
    assert missing_norm["outcome_quality"]["passed"] is None
    assert missing_norm["outcome_quality"]["availability"] == "unavailable"

    unknown_norm = contract.normalize_trial_metrics(traces["unknown_schema_trace"])
    assert unknown_norm["outcome_quality"]["passed"] is None
    assert unknown_norm["outcome_quality"]["availability"] == "unavailable"
