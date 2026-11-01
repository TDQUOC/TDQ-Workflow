"""End-to-end integration and cross-layer edge test suite for TDQ Eval (O1-O7).

Verifies strict invariants across tdq_eval_contract, tdq_eval_hosts, tdq_skill_eval,
and tdq_eval manifest compatibility:
- O1: Pure contract validation, canonical hashing, schedule balance, cell recommendations.
- O2: CLI workflow pipeline (plan, check, run, report, and Markdown rendering).
- O3: Host adapters, private environment isolation, trace streaming, and quota limits.
- O4: Workflow gate stages (pre_implement, pre_report) and user waivers.
- O5: Manifest validation and legacy historical record classification.
- O6: Packaging constraints, stdlib purity, and zero-model-call invariance.
- O7: Evidence binding, artifact hashes, and streaming SHA-256 verification.
- 11 cross-cutting edge conditions: nonfinite numbers, duplicate trials/cases, path
  traversals, stale hashes, model aliases, mismatched permissions/cache, holdout mutations,
  partial transport usage, budget overruns, unmeasured model cells, and moving branches.
"""

from copy import deepcopy
import json
import math
import os
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import tdq_eval_contract
import tdq_eval_hosts
import tdq_skill_eval
import tdq_eval

H40 = "b" * 40
H64 = "a" * 64
SAMPLE_MODEL = "claude-3-5-sonnet-20241022"


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)


def make_cell(host="claude", model=SAMPLE_MODEL, permission_profile="isolated",
              tool_aliases=None, cache_profile="cold"):
    return {
        "host": host,
        "model": model,
        "permission_profile": permission_profile,
        "tool_aliases": tool_aliases or {"shell": ["Bash"]},
        "cache_profile": cache_profile,
    }


def make_plan(**overrides):
    plan = {
        "plan_version": "v1",
        "experiment_id": "exp-e2e-001",
        "targets": {"skills/tdq-build/SKILL.md": H64},
        "base_identity": H40,
        "candidate_identity": "planned",
        "change_kind": "behavioral",
        "hypothesis": "Refactor evaluator contracts without regression",
        "evaluation_kind": "mechanism",
        "corpus_id": "corpus-skill-eval-v1",
        "dev_cases_sha256": "c" * 64,
        "holdout_cases_sha256": "d" * 64,
        "rubric_version": "v1.0",
        "scorer_version": "v2-temporal",
        "expected_triggers": ["case-trigger-pos"],
        "negative_cases": ["case-trigger-neg"],
        "required_metrics": ["trigger_accuracy", "outcome_quality", "efficiency_metrics"],
        "cells": [make_cell()],
        "repetitions": 1,
        "order_policy": "AB_BA",
        "thresholds": {"min_pairs": 1, "quality_margin": 0.05, "efficiency_margin": 0.1},
    }
    plan.update(overrides)
    return plan


def make_manifest(cell=None, **overrides):
    c = cell or make_cell()
    mf = {
        **c,
        "base_commit": H40,
        "candidate_commit": "e" * 64,
        "scorer_version": "v2-temporal",
        "corpus_version": "corpus-skill-eval-v1",
        "check_set": ["rule_compliance"],
        "evaluation_kind": "mechanism",
        "rubric_version": "v1.0",
    }
    mf.update(overrides)
    return mf


def make_trial_record(plan, trial, score=1.0, tokens=None, **overrides):
    case_id = trial.get("case_id", plan["expected_triggers"][0])
    expected_trigger = case_id in plan["expected_triggers"]
    trial_with_case = dict(trial, case_id=case_id)
    mf = make_manifest(
        cell={k: trial_with_case[k] for k in tdq_eval_contract.CELL_FIELDS},
        candidate_commit=plan["candidate_identity"],
    )
    rec = {
        **trial_with_case,
        "base_identity": plan["base_identity"],
        "candidate_identity": plan["candidate_identity"],
        "targets": plan["targets"],
        "dev_cases_sha256": plan["dev_cases_sha256"],
        "holdout_cases_sha256": plan["holdout_cases_sha256"],
        "scorer_version": plan["scorer_version"],
        "rubric_version": plan["rubric_version"],
        "evaluation_kind": plan["evaluation_kind"],
        "raw_trace_sha256": "f" * 64,
        "outcome_sha256": "1" * 64,
        "provenance": "synthetic/offline" if plan["evaluation_kind"] == "mechanism" else "live",
        "expected_trigger": expected_trigger,
        "observed_trigger": overrides.get("observed_trigger", expected_trigger),
        "trigger_provenance": "event:tool_use:test",
        "execution_status": "completed" if score > 0 else "failed",
        "passed": score == 1.0,
        "score": score,
        "checks": {"rule_compliance": score == 1.0},
        "manifest": mf,
        "tool_calls_count": 2,
        "model_calls_count": 1,
        "retries_count": 0,
        "user_interventions_count": 0,
        "tokens": tokens or {
            "input_tokens": 100,
            "output_tokens": 200,
            "cache_read_tokens": 50,
            "cache_write_tokens": 0,
        },
        "total_cost_usd": 0.005,
        "billed_cost_usd": 0.005,
        "wall_latency_seconds": 1.25,
    }
    rec.update(overrides)
    return rec


def build_evidence_records(plan):
    exp_hash = tdq_eval_contract.compute_experiment_hash(plan)
    cases = plan["expected_triggers"] + plan["negative_cases"]
    schedule = tdq_eval_contract.build_ab_ba_schedule(cases, plan["cells"], plan["repetitions"], exp_hash)
    records = [make_trial_record(plan, trial) for trial in schedule]
    return schedule, records


# ===================================================================
# 11 Cross-Layer Edge Tests
# ===================================================================

def test_edge_nonfinite_rejected_in_plan_metrics_and_policy():
    """Nonfinite floats (nan, inf, -inf) are rejected across plan, metrics, and policy."""
    # 1. Rejected in validate_eval_plan
    bad_plan = make_plan()
    bad_plan["thresholds"]["quality_margin"] = float("nan")
    res = tdq_eval_contract.validate_eval_plan(bad_plan)
    assert not res["valid"]

    bad_plan2 = make_plan()
    bad_plan2["thresholds"]["min_pairs"] = float("inf")
    res2 = tdq_eval_contract.validate_eval_plan(bad_plan2)
    assert not res2["valid"]

    # 2. Rejected in normalize_trial_metrics
    with pytest.raises(ValueError, match="metric must be finite/nonnegative"):
        tdq_eval_contract.normalize_trial_metrics({"score": float("nan")})

    with pytest.raises(ValueError, match="metric must be finite/nonnegative"):
        tdq_eval_contract.normalize_trial_metrics({"total_cost_usd": float("inf")})

    with pytest.raises(ValueError, match="metric must be finite/nonnegative"):
        tdq_eval_contract.normalize_trial_metrics({"wall_latency_seconds": -float("inf")})

    # 3. Rejected in evaluate_cell_recommendation policy
    pair = {
        "pair_id": "p1",
        "baseline": make_trial_record(make_plan(candidate_identity="e" * 64), {"host": "claude", "model": SAMPLE_MODEL, "permission_profile": "isolated", "tool_aliases": {"shell": ["Bash"]}, "cache_profile": "cold", "experiment_hash": H64, "case_id": "c1"}),
        "candidate": make_trial_record(make_plan(candidate_identity="e" * 64), {"host": "claude", "model": SAMPLE_MODEL, "permission_profile": "isolated", "tool_aliases": {"shell": ["Bash"]}, "cache_profile": "cold", "experiment_hash": H64, "case_id": "c1"}),
    }
    rec_nan = tdq_eval_contract.evaluate_cell_recommendation([pair], policy={"min_pairs": 1, "quality_margin": float("nan"), "efficiency_margin": 0.1})
    assert rec_nan["verdict"] == "INCONCLUSIVE"
    assert "metric must be finite/nonnegative" in rec_nan["reason"]


def test_edge_duplicate_cases_and_trials():
    """Duplicate cases, cells, pair IDs, and trial records are strictly rejected."""
    # 1. Duplicate cases in build_ab_ba_schedule
    with pytest.raises(ValueError, match="duplicate cases"):
        tdq_eval_contract.build_ab_ba_schedule(["case-1", "case-1"], [make_cell()], 1, H64)

    # 2. Duplicate cells in build_ab_ba_schedule
    with pytest.raises(ValueError, match="duplicate cells"):
        tdq_eval_contract.build_ab_ba_schedule(["case-1"], [make_cell(), make_cell()], 1, H64)

    # 3. Duplicate pair_id in evaluate_cell_recommendation
    p = make_plan(candidate_identity="e" * 64)
    cell = make_cell()
    base = make_trial_record(p, dict(cell, experiment_hash=H64, case_id="c1", repetition=1, variant="A"))
    cand = make_trial_record(p, dict(cell, experiment_hash=H64, case_id="c1", repetition=1, variant="B"))
    dup_pairs = [
        {"pair_id": "dup-pair-id", "baseline": base, "candidate": cand},
        {"pair_id": "dup-pair-id", "baseline": base, "candidate": cand},
    ]
    rec_res = tdq_eval_contract.evaluate_cell_recommendation(dup_pairs, policy={"min_pairs": 1, "quality_margin": 0.05, "efficiency_margin": 0.1})
    assert rec_res["verdict"] == "INCONCLUSIVE"
    assert rec_res["reason"] == "duplicate_pair"

    # 4. Duplicate trial record in check_eval_gate(stage="pre_report")
    plan = make_plan(candidate_identity="e" * 64)
    schedule, records = build_evidence_records(plan)
    # duplicate the first record to simulate duplicate trial ID
    dup_records = [records[0], records[0]]
    gate_res = tdq_eval_contract.check_eval_gate(
        plan,
        stage="pre_report",
        actual_target_hashes=plan["targets"],
        evidence_records=dup_records,
    )
    assert gate_res["verdict"] == "INCOMPLETE"
    assert gate_res["reason"] in ("incomplete_trial_coverage", "duplicate_trial")


def test_edge_path_traversal_and_unnormalized_paths():
    """Path traversals, absolute paths, colons, and unnormalized paths fail closed."""
    unsafe_paths = [
        "../secret.txt",
        "../../etc/passwd",
        "/absolute/path/file.py",
        "\\windows\\system32\\cmd.exe",
        "C:/Windows/explorer.exe",
        "dir/trailing space /file.py",
        " trailing.py",
        "colon:in:name.py",
    ]
    for bad_path in unsafe_paths:
        res = tdq_eval_contract.classify_target(bad_path)
        assert res["change_kind"] == "review-required"
        assert res["requires_eval"] is True

    unsafe_trial_ids = [
        "../evil",
        "..",
        ".",
        "trial:1",
        "trial/1",
        "trial\\1",
        "   ",
        "trial%1",
    ]
    for bad_id in unsafe_trial_ids:
        with pytest.raises(ValueError, match="invalid trial_id"):
            tdq_eval_hosts.prepare_trial_environment(
                base_dir=tempfile.gettempdir(),
                host="claude",
                trial_id=bad_id,
            )

    # validate_eval_plan rejects unsafe targets
    plan = make_plan(targets={"../outside.py": H64})
    assert not tdq_eval_contract.validate_eval_plan(plan)["valid"]


def test_edge_hash_mismatch_and_stale_target_and_planned_candidate():
    """pre_report gate rejects planned candidate, stale target hashes, or stale experiment hash."""
    plan = make_plan()
    # 1. Candidate is still "planned"
    gate_planned = tdq_eval_contract.check_eval_gate(
        plan,
        stage="pre_report",
        actual_target_hashes=plan["targets"],
        evidence_records=[],
    )
    assert gate_planned["verdict"] == "INCOMPLETE"
    assert gate_planned["reason"] == "planned_candidate"

    # 2. Resolved candidate, but target hash mismatched
    resolved_plan = make_plan(candidate_identity="e" * 64)
    _, records = build_evidence_records(resolved_plan)
    stale_targets = {"skills/tdq-build/SKILL.md": "0" * 64}
    gate_stale_target = tdq_eval_contract.check_eval_gate(
        resolved_plan,
        stage="pre_report",
        actual_target_hashes=stale_targets,
        evidence_records=records,
    )
    assert gate_stale_target["verdict"] == "INCOMPLETE"
    assert gate_stale_target["reason"] == "stale_target_hash"

    # 3. Plan experiment_hash tamper
    tampered_plan = dict(resolved_plan, experiment_hash="bad_hash" * 4)
    gate_tamper = tdq_eval_contract.check_eval_gate(
        tampered_plan,
        stage="pre_report",
        actual_target_hashes=resolved_plan["targets"],
        evidence_records=records,
    )
    assert gate_tamper["verdict"] == "INCOMPLETE"
    assert gate_tamper["reason"] == "stale_experiment_hash"


def test_edge_unresolved_model_aliases():
    """Unresolved aliases ('latest', 'default', 'auto', '') are rejected in plan and host check."""
    aliases = ["latest", "default", "auto", "", "claude-latest", "gpt-4-default", "model:auto"]
    for alias in aliases:
        bad_plan = make_plan(cells=[make_cell(model=alias)])
        val = tdq_eval_contract.validate_eval_plan(bad_plan)
        assert not val["valid"]
        assert any("unresolved host/model" in err for err in val["errors"])

        with pytest.raises(ValueError, match="unresolved host/model"):
            tdq_eval_contract.build_ab_ba_schedule(["case-1"], [make_cell(model=alias)], 1, H64)

    # Host preflight rejects unsupported host
    unsupported_pf = tdq_eval_hosts.preflight_host("unsupported-llm-host")
    assert unsupported_pf["status"] == "UNSUPPORTED"
    assert not unsupported_pf["ready"]
    assert unsupported_pf["paid_model_calls"] == 0


def test_edge_mismatched_permissions_tools_cache_manifest():
    """validate_paired_identity detects and lists every control variable mismatch."""
    base_m = make_manifest()

    # Mismatched permission profile
    cand_perm = make_manifest(permission_profile="full-access")
    res = tdq_eval_contract.validate_paired_identity(base_m, cand_perm)
    assert not res["valid"]
    assert "permission_profile" in res["mismatched_fields"]

    # Mismatched tool aliases
    cand_tool = make_manifest(tool_aliases={"shell": ["PowerShell"]})
    res_tool = tdq_eval_contract.validate_paired_identity(base_m, cand_tool)
    assert not res_tool["valid"]
    assert "tool_aliases" in res_tool["mismatched_fields"]

    # Mismatched cache profile
    cand_cache = make_manifest(cache_profile="warm")
    res_cache = tdq_eval_contract.validate_paired_identity(base_m, cand_cache)
    assert not res_cache["valid"]
    assert "cache_profile" in res_cache["mismatched_fields"]

    # Mismatched model
    cand_model = make_manifest(model="claude-3-opus-20240229")
    res_model = tdq_eval_contract.validate_paired_identity(base_m, cand_model)
    assert not res_model["valid"]
    assert "model" in res_model["mismatched_fields"]


def test_edge_holdout_or_dev_split_mutation():
    """Tampering with holdout_cases_sha256 or dev_cases_sha256 invalidates locked plan."""
    plan = make_plan(candidate_identity="e" * 64)
    original_hash = tdq_eval_contract.compute_experiment_hash(plan)

    # 1. Mutating holdout changes experiment hash
    mutated_plan = dict(plan, holdout_cases_sha256="9" * 64)
    new_hash = tdq_eval_contract.compute_experiment_hash(mutated_plan)
    assert original_hash != new_hash

    # 2. Locked plan with previous hash rejects mutated holdout
    locked_plan = dict(plan, experiment_hash=original_hash, holdout_cases_sha256="9" * 64)
    gate_stale_hash = tdq_eval_contract.check_eval_gate(
        locked_plan,
        stage="pre_report",
        actual_target_hashes=plan["targets"],
        evidence_records=[],
    )
    assert gate_stale_hash["verdict"] == "INCOMPLETE"
    assert gate_stale_hash["reason"] == "stale_experiment_hash"

    # 3. Evidence row carrying mismatched holdout hash rejected
    mut_sched, mut_records = build_evidence_records(mutated_plan)
    mut_records[0]["holdout_cases_sha256"] = "0" * 64  # tamper one record
    gate_stale_binding = tdq_eval_contract.check_eval_gate(
        mutated_plan,
        stage="pre_report",
        actual_target_hashes=plan["targets"],
        evidence_records=mut_records,
    )
    assert gate_stale_binding["verdict"] == "INCOMPLETE"
    assert gate_stale_binding["reason"] == "stale_evidence_binding"


def test_edge_transport_error_partial_usage_no_zero_dollars():
    """Partial usage from transport drops does not claim 'available' and never defaults to $0.00."""
    partial_record = {
        "execution_status": "failed",
        "tokens": {"input_tokens": 150},  # missing output, cache_read, cache_write
    }
    metrics = tdq_eval_contract.normalize_trial_metrics(partial_record)
    tok = metrics["efficiency_metrics"]["tokens"]
    assert tok["availability"] == "partial"
    assert tok["input_tokens"] == 150
    assert tok["output_tokens"] is None

    cost = metrics["efficiency_metrics"]["cost"]
    assert cost["availability"] == "unavailable"
    assert cost["total_cost_usd"] is None
    assert cost["total_cost_usd"] != 0.00
    assert cost["source"] is None

    # Estimate with rate card also yields None under partial availability
    rate_card = {
        "source": "anthropic-pricing",
        "snapshot_at": "2026-11-01T00:00:00Z",
        "rates": {
            "input_per_mtok": 3.0,
            "output_per_mtok": 15.0,
            "cache_read_per_mtok": 0.3,
            "cache_write_per_mtok": 3.75,
        },
    }
    metrics_with_rate = tdq_eval_contract.normalize_trial_metrics(partial_record, rate_card=rate_card)
    assert metrics_with_rate["efficiency_metrics"]["cost"]["rate_estimate"] is None


def test_edge_event_and_byte_budget_exceeded():
    """Over-budget trace streams return failed budget_exceeded without silent truncation."""
    # 1. Byte limit exceeded
    large_line = json.dumps({"type": "progress", "msg": "x" * 200}) + "\n"
    res_bytes = tdq_eval_hosts.parse_trace_stream(
        [large_line, large_line],
        max_bytes=150,  # limit below size of two lines
        max_events=1000,
    )
    assert res_bytes["execution_status"] == "failed"
    assert res_bytes["reason"] == "budget_exceeded"
    assert res_bytes["truncated"] is True
    assert res_bytes["paid_model_calls"] == 0

    # 2. Event count limit exceeded
    small_line = json.dumps({"type": "progress"}) + "\n"
    res_events = tdq_eval_hosts.parse_trace_stream(
        [small_line, small_line, small_line],
        max_bytes=10000,
        max_events=2,  # limit below 3 events
    )
    assert res_events["execution_status"] == "failed"
    assert res_events["reason"] == "budget_exceeded"
    assert res_events["truncated"] is True
    assert res_events["paid_model_calls"] == 0


def test_edge_unmeasured_model_cell_inconclusive():
    """Unmeasured cells or insufficient pairs return INCONCLUSIVE."""
    # Empty pair list
    res_empty = tdq_eval_contract.evaluate_cell_recommendation([], policy={"min_pairs": 1, "quality_margin": 0.05, "efficiency_margin": 0.1})
    assert res_empty["verdict"] == "INCONCLUSIVE"
    assert res_empty["reason"] == "missing_pairs"
    assert res_empty["sample_count"] == 0

    # Insufficient pair count
    p = make_plan(candidate_identity="e" * 64)
    cell = make_cell()
    base = make_trial_record(p, dict(cell, experiment_hash=H64, case_id="c1", repetition=1, variant="A"))
    cand = make_trial_record(p, dict(cell, experiment_hash=H64, case_id="c1", repetition=1, variant="B"))
    one_pair = [{"pair_id": "pair-1", "baseline": base, "candidate": cand}]

    res_insuf = tdq_eval_contract.evaluate_cell_recommendation(one_pair, policy={"min_pairs": 5, "quality_margin": 0.05, "efficiency_margin": 0.1})
    assert res_insuf["verdict"] == "INCONCLUSIVE"
    assert res_insuf["reason"] == "insufficient_pairs"
    assert res_insuf["sample_count"] == 1


def test_edge_moving_branch_rejected_in_plan():
    """Branch names (e.g. 'main', 'HEAD') are rejected in place of fixed commit hashes."""
    moving_branches = ["main", "master", "HEAD", "feature/new-skill", "v1.0.0"]
    for branch_name in moving_branches:
        bad_base = make_plan(base_identity=branch_name)
        val_base = tdq_eval_contract.validate_eval_plan(bad_base)
        assert not val_base["valid"]
        assert any("unresolved base identity" in e for e in val_base["errors"])

        bad_cand = make_plan(candidate_identity=branch_name)
        val_cand = tdq_eval_contract.validate_eval_plan(bad_cand)
        assert not val_cand["valid"]
        assert any("unresolved candidate" in e for e in val_cand["errors"])


# ===================================================================
# O1: Pure Evaluation Contract
# ===================================================================

class TestO1CoreContract:
    def test_plan_creation_and_canonical_hash(self):
        plan = tdq_eval_contract.create_eval_plan(**make_plan())
        h1 = tdq_eval_contract.compute_experiment_hash(plan)
        h2 = tdq_eval_contract.compute_experiment_hash(plan)
        assert h1 == h2
        assert len(h1) == 64

    def test_schedule_ab_ba_alternation(self):
        plan = make_plan(repetitions=2)
        exp_hash = tdq_eval_contract.compute_experiment_hash(plan)
        schedule = tdq_eval_contract.build_ab_ba_schedule(
            plan["expected_triggers"] + plan["negative_cases"],
            plan["cells"],
            repetitions=2,
            experiment_hash=exp_hash,
        )
        assert len(schedule) == 2 * 2 * 1 * 2  # cases * reps * cells * 2 variants = 8
        rep1_variants = [t["variant"] for t in schedule if t["repetition"] == 1]
        rep2_variants = [t["variant"] for t in schedule if t["repetition"] == 2]
        assert "A" in rep1_variants and "B" in rep1_variants
        assert "A" in rep2_variants and "B" in rep2_variants

    def test_target_classification_scopes(self):
        assert tdq_eval_contract.classify_target("skills/build/SKILL.md")["change_kind"] == "behavioral"
        assert tdq_eval_contract.classify_target("docs/tdq/plan/foo.md")["change_kind"] == "bookkeeping"
        assert tdq_eval_contract.classify_target("README.md")["change_kind"] == "docs_only"
        assert tdq_eval_contract.classify_target("src/main.py")["change_kind"] == "app_code"

    def test_recommendation_verdicts_keep_trim_drop(self):
        p = make_plan(candidate_identity="e" * 64)
        cell = make_cell()

        def make_pair(pid, b_score, c_score, b_tok=1000, c_tok=1000):
            base = make_trial_record(p, dict(cell, experiment_hash=H64, case_id=f"c_{pid}", repetition=1, variant="A"), score=b_score, tokens={"input_tokens": b_tok, "output_tokens": 100, "cache_read_tokens": 0, "cache_write_tokens": 0})
            cand = make_trial_record(p, dict(cell, experiment_hash=H64, case_id=f"c_{pid}", repetition=1, variant="B"), score=c_score, tokens={"input_tokens": c_tok, "output_tokens": 100, "cache_read_tokens": 0, "cache_write_tokens": 0})
            return {"pair_id": pid, "baseline": base, "candidate": cand}

        policy = {"min_pairs": 2, "quality_margin": 0.05, "efficiency_margin": 0.20}

        # 1. KEEP: quality improved
        keep_pairs = [make_pair("p1", 0.70, 0.95), make_pair("p2", 0.75, 0.95)]
        assert tdq_eval_contract.evaluate_cell_recommendation(keep_pairs, policy)["verdict"] == "KEEP"

        # 2. DROP: quality regressed
        drop_pairs = [make_pair("p1", 0.90, 0.60), make_pair("p2", 0.95, 0.65)]
        assert tdq_eval_contract.evaluate_cell_recommendation(drop_pairs, policy)["verdict"] == "DROP"

        # 3. TRIM: quality equal, efficiency gained > 20%
        trim_pairs = [make_pair("p1", 0.90, 0.90, b_tok=1000, c_tok=500), make_pair("p2", 0.90, 0.90, b_tok=1000, c_tok=500)]
        assert tdq_eval_contract.evaluate_cell_recommendation(trim_pairs, policy)["verdict"] == "TRIM"


# ===================================================================
# O2: Skill Evaluation CLI & Reports
# ===================================================================

class TestO2SkillEvalCLIAndReport:
    def test_plan_eval_workflow(self, temp_dir):
        plan_dict = make_plan()
        res = tdq_skill_eval.plan_eval(plan_dict, out_path=temp_dir / "plan_out.json")
        assert res["valid"]
        assert res["experiment_hash"] is not None
        assert (temp_dir / "plan_out.json").exists()

    def test_check_eval_pre_implement(self):
        plan_dict = make_plan()
        res = tdq_skill_eval.check_eval(plan_dict, stage="pre_implement")
        assert res["gate"]["verdict"] == "PASS"

    def test_generate_report_markdown_and_json(self, temp_dir):
        p = make_plan(candidate_identity="e" * 64)
        _, records = build_evidence_records(p)
        results_dir = temp_dir / "results"
        results_dir.mkdir()
        for idx, rec in enumerate(records):
            (results_dir / f"trial_{idx}.json").write_text(json.dumps(rec), encoding="utf-8")

        out_json = temp_dir / "report.json"
        out_md = temp_dir / "report.md"
        report_data = tdq_skill_eval.generate_report(results_dir, out_json=out_json, out_md=out_md)

        assert out_json.exists()
        assert out_md.exists()
        assert tdq_skill_eval.SOUL_LINE in out_md.read_text(encoding="utf-8")
        assert report_data["total_records"] == len(records)
        assert len(report_data["cells"]) == 1

    def test_run_eval_bounded_quota_stop(self, temp_dir):
        plan_dict = make_plan(candidate_identity="e" * 64)
        plan_file = temp_dir / "plan.json"
        plan_file.write_text(json.dumps(plan_dict), encoding="utf-8")

        cases_file = temp_dir / "cases.json"
        cases_file.write_text(json.dumps(["case-trigger-pos", "case-trigger-neg"]), encoding="utf-8")

        profile_file = temp_dir / "profile.json"
        # Zero quota forces early exit
        profile_file.write_text(json.dumps({"quota_usd": -1.0}), encoding="utf-8")

        out_dir = temp_dir / "run_out"
        summary = tdq_skill_eval.run_eval(plan_file, cases_file, profile_file, out_dir)
        assert summary["completed_trials"] == 0
        assert (out_dir / "run_summary.json").exists()


# ===================================================================
# O3: Host Adapters and Execution Primitives
# ===================================================================

class TestO3HostAdaptersAndStreaming:
    def test_canonical_host_names(self):
        assert tdq_eval_hosts.canonical_host_name("claude-code") == "claude"
        assert tdq_eval_hosts.canonical_host_name("CODEX") == "codex"
        assert tdq_eval_hosts.canonical_host_name("other") == "other"

    def test_trial_environment_private_directories(self, temp_dir):
        profile = tdq_eval_hosts.prepare_trial_environment(
            base_dir=temp_dir,
            host="claude",
            trial_id="trial-001",
        )
        assert Path(profile["workspace_dir"]).exists()
        assert Path(profile["config_dir"]).exists()
        assert Path(profile["home_dir"]).exists()
        assert profile["home_dir"] != str(Path.home().resolve())
        assert profile["env"]["CLAUDE_CONFIG_DIR"] == profile["config_dir"]
        assert profile["env"]["TDQ_DISABLE_GLOBAL_PLUGINS"] == "1"

    def test_parse_trace_stream_claude_events(self):
        events = [
            json.dumps({"type": "api-request"}) + "\n",
            json.dumps({
                "type": "assistant",
                "message": {
                    "content": [{"type": "tool_use", "name": "Bash"}],
                    "usage": {"input_tokens": 120, "output_tokens": 30, "cache_read_input_tokens": 10},
                },
            }) + "\n",
            json.dumps({"type": "user", "message": {"content": [{"type": "text", "text": "continue"}]}}) + "\n",
        ]
        res = tdq_eval_hosts.parse_trace_stream(events, expected_trigger=True)
        assert res["execution_status"] == "completed"
        assert res["model_calls_count"] == 1
        assert res["tool_calls_count"] == 1
        assert res["user_interventions_count"] == 1
        assert res["observed_trigger"] is True
        assert res["tokens"]["input_tokens"] == 120
        assert res["tokens"]["output_tokens"] == 30
        assert res["tokens"]["cache_read_tokens"] == 10

    def test_parse_trace_stream_codex_events(self):
        events = [
            json.dumps({"type": "response_item", "payload": {"type": "message", "role": "assistant"}}) + "\n",
            json.dumps({"type": "response_item", "payload": {"type": "function_call", "name": "execute_command"}}) + "\n",
            json.dumps({"type": "event_msg", "payload": {"type": "token_count", "usage": {"input_tokens": 200, "output_tokens": 50, "cached_input_tokens": 20}}}) + "\n",
        ]
        res = tdq_eval_hosts.parse_trace_stream(events)
        assert res["execution_status"] == "completed"
        assert res["model_calls_count"] == 1
        assert res["tool_calls_count"] == 1
        assert res["tokens"]["input_tokens"] == 200
        assert res["tokens"]["output_tokens"] == 50
        assert res["tokens"]["cache_read_tokens"] == 20


# ===================================================================
# O4: Workflow Gate Integration & User Waiver
# ===================================================================

class TestO4WorkflowGateIntegration:
    def test_valid_user_waiver_handling(self):
        plan = make_plan()
        valid_waiver = {
            "by": "user:admin",
            "reason": "Emergency doc-only exemption approved by lead",
            "scope": "docs_only",
        }
        gate_res = tdq_eval_contract.check_eval_gate(plan, stage="pre_implement", waiver=valid_waiver)
        assert gate_res["verdict"] == "WAIVED_USER"
        assert gate_res["live_run_authorized"] is False
        assert not gate_res["passed"]

    def test_invalid_waiver_rejected(self):
        plan = make_plan()
        # Missing 'user:' prefix
        bad_waiver = {
            "by": "system",
            "reason": "Automated skip",
            "scope": "all",
        }
        gate_res = tdq_eval_contract.check_eval_gate(plan, stage="pre_implement", waiver=bad_waiver)
        assert gate_res["verdict"] != "WAIVED_USER"

    def test_pre_report_gate_complete_evidence_pass(self):
        plan = make_plan(candidate_identity="e" * 64)
        _, records = build_evidence_records(plan)
        gate_res = tdq_eval_contract.check_eval_gate(
            plan,
            stage="pre_report",
            actual_target_hashes=plan["targets"],
            evidence_records=records,
        )
        assert gate_res["verdict"] == "PASS"
        assert gate_res["passed"] is True


# ===================================================================
# O5: Manifest and Legacy Compatibility
# ===================================================================

class TestO5ManifestAndLegacyCompatibility:
    def test_historical_unverified_record_classification(self):
        # Missing host or model classifies as historical_unverified
        legacy_rec = {"tokens": {"input_tokens": 100}}
        prov = tdq_eval_contract.classify_record_provenance(legacy_rec)
        assert prov == "historical_unverified"

        # Missing experiment_hash
        almost_valid = {
            "host": "claude",
            "model": SAMPLE_MODEL,
            "raw_trace_sha256": H64,
            "provenance": "synthetic/offline",
        }
        assert tdq_eval_contract.classify_record_provenance(almost_valid) == "historical_unverified"

    def test_tdq_eval_wrapper_imports_and_manifest_compatibility(self):
        assert hasattr(tdq_eval, "validate_paired_identity")
        assert hasattr(tdq_eval, "classify_record_provenance")
        m1 = make_manifest()
        m2 = make_manifest()
        res = tdq_eval.validate_paired_identity(m1, m2)
        assert res["valid"]


# ===================================================================
# O6: Packaging Constraints and Zero-Model Calls
# ===================================================================

class TestO6PackagingAndDependencyConstraints:
    def test_contract_uses_standard_library_only(self):
        contract_module = sys.modules["tdq_eval_contract"]
        for key, val in contract_module.__dict__.items():
            if hasattr(val, "__file__") and val.__file__:
                mod_path = Path(val.__file__).resolve()
                assert "site-packages" not in str(mod_path).lower(), f"Unauthorized external package: {key}"

    def test_preflight_and_check_never_call_model(self):
        # preflight_host on claude with mock version
        with patch.object(tdq_eval_hosts.OwnedProcessJob, "run", return_value={"exit_code": 0, "stdout": "claude 1.0.0"}):
            with tempfile.TemporaryDirectory() as tmp_dir:
                profile = tdq_eval_hosts.prepare_trial_environment(tmp_dir, "claude", "trial-pf")
                res = tdq_eval_hosts.preflight_host("claude", profile=profile)
                assert res["status"] == "READY"
                assert res["paid_model_calls"] == 0


# ===================================================================
# O7: Evidence Auditing and Artifact Verification
# ===================================================================

class TestO7EvidenceAndArtifactAuditing:
    def test_streaming_sha256_hashing(self, temp_dir):
        sample_file = temp_dir / "sample.bin"
        content = b"Evaluation artifact chunking test " * 5000
        sample_file.write_bytes(content)

        stream_hash = tdq_eval_hosts.hash_file_streaming(sample_file)
        import hashlib
        direct_hash = hashlib.sha256(content).hexdigest()
        assert stream_hash == direct_hash

    def test_evidence_manifest_commit_binding(self):
        plan = make_plan(candidate_identity="e" * 64)
        _, records = build_evidence_records(plan)
        rec = records[0]
        assert rec["manifest"]["base_commit"] == plan["base_identity"]
        assert rec["manifest"]["candidate_commit"] == plan["candidate_identity"]
        assert rec["manifest"]["scorer_version"] == plan["scorer_version"]
