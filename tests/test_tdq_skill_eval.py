"""Tests for tdq_skill_eval.py (O2 entry point and compatibility).

Covers:
1. `plan` command: offline plan validation, hash calculation, invalid plan rejection.
2. `check` command: host preflight and gate verification without model calls.
3. `run` command: balanced AB/BA schedule, bounded trial execution, normalized records.
4. `report` command: offline aggregation, per-(host, model) cell grouping,
   deterministic recommendations (KEEP/TRIM/DROP/INCONCLUSIVE), JSON and Markdown outputs.
5. Integration with `tdq_eval.py`: classify_record_provenance on historical 60 records,
   rescore_append_only with provenance tracking.
"""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

GOC = Path(__file__).resolve().parent.parent
SCRIPTS = GOC / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import tdq_eval_contract
import tdq_eval_hosts
import tdq_eval
import tdq_skill_eval


def make_valid_plan(evaluation_kind="mechanism", repetitions=1):
    return {
        "plan_version": "v1",
        "experiment_id": "exp-skill-001",
        "targets": ["skills/tdq-build/SKILL.md"],
        "base_identity": "a" * 40,
        "candidate_identity": "b" * 64,
        "change_kind": "behavioral",
        "hypothesis": "Refining instructions improves compliance",
        "evaluation_kind": evaluation_kind,
        "corpus_id": "corpus-skill-v1",
        "dev_cases_sha256": "c" * 64,
        "holdout_cases_sha256": "d" * 64,
        "rubric_version": "rubric-v1",
        "scorer_version": "v2-temporal",
        "expected_triggers": ["pos_case_01", "pos_case_02"],
        "negative_cases": ["neg_case_01"],
        "required_metrics": ["trigger_accuracy", "outcome_quality"],
        "cells": [
            {
                "host": "claude",
                "model": "claude-sonnet-4-5",
                "permission_profile": "offline-mock",
                "tool_aliases": {"bash": ["sh", "bash"]},
                "cache_profile": "ephemeral",
            }
        ],
        "repetitions": repetitions,
        "order_policy": "AB_BA",
        "thresholds": {
            "min_pairs": 1,
            "quality_margin": 0.05,
            "efficiency_margin": 0.1,
        },
    }


def make_paired_records(plan, cell, score_delta=0.1, count=1):
    """Generate synthetic paired trial records matching plan and cell for testing report."""
    exp_hash = tdq_eval_contract.compute_experiment_hash(plan)
    records = []
    cases = plan["expected_triggers"] + plan["negative_cases"]

    for rep in range(1, count + 1):
        for case_id in cases:
            for variant in ("A", "B"):
                trial = dict(
                    cell,
                    case_id=case_id,
                    repetition=rep,
                    variant=variant,
                    experiment_hash=exp_hash,
                )
                trial_id = tdq_eval_contract._digest(trial)
                is_candidate = variant == "B"
                base_score = 0.8
                cand_score = min(1.0, base_score + score_delta) if score_delta >= 0 else max(0.0, base_score + score_delta)
                score = cand_score if is_candidate else base_score
                expected_trig = case_id in plan["expected_triggers"]

                checks = {"L001": "dat", "L002": "dat"} if score > 0.7 else {"L001": "dat", "L002": "truot"}
                manifest = dict(
                    cell,
                    base_commit=plan["base_identity"],
                    candidate_commit=plan["candidate_identity"],
                    corpus_version=plan["corpus_id"],
                    scorer_version=plan["scorer_version"],
                    rubric_version=plan["rubric_version"],
                    evaluation_kind=plan["evaluation_kind"],
                    check_set=list(checks.keys()),
                )

                rec = dict(
                    trial,
                    trial_id=trial_id,
                    base_identity=plan["base_identity"],
                    candidate_identity=plan["candidate_identity"],
                    targets=plan["targets"],
                    dev_cases_sha256=plan["dev_cases_sha256"],
                    holdout_cases_sha256=plan["holdout_cases_sha256"],
                    scorer_version=plan["scorer_version"],
                    rubric_version=plan["rubric_version"],
                    evaluation_kind=plan["evaluation_kind"],
                    raw_trace_sha256="1" * 64,
                    outcome_sha256="2" * 64,
                    provenance="synthetic/offline" if plan["evaluation_kind"] == "mechanism" else "live",
                    expected_trigger=expected_trig,
                    observed_trigger=expected_trig,
                    trigger_provenance="event:tool_use:test",
                    execution_status="completed",
                    passed=score >= 0.7,
                    score=score,
                    checks=checks,
                    manifest=manifest,
                    tool_calls_count=2,
                    model_calls_count=1,
                    retries_count=0,
                    user_interventions_count=0,
                    tokens={
                        "input_tokens": 100,
                        "output_tokens": 50,
                        "cache_read_tokens": 20,
                        "cache_write_tokens": 10,
                    },
                    total_cost_usd=None,
                    billed_cost_usd=None,
                    wall_latency_seconds=1.5,
                )
                records.append(rec)
    return records


class TestTdqSkillEvalPlan(unittest.TestCase):
    """Test `plan` subcommand: offline validation, hashing, rejection."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def test_plan_valid_file_and_hash(self):
        plan = make_valid_plan()
        plan_file = self.tmp_path / "plan.json"
        plan_file.write_text(json.dumps(plan), encoding="utf-8")

        res = tdq_skill_eval.plan_eval(str(plan_file))
        self.assertTrue(res["valid"])
        self.assertEqual(len(res["errors"]), 0)
        self.assertEqual(len(res["experiment_hash"]), 64)

    def test_plan_rejects_invalid_plan(self):
        plan = make_valid_plan()
        del plan["cells"]  # invalid
        plan_file = self.tmp_path / "invalid_plan.json"
        plan_file.write_text(json.dumps(plan), encoding="utf-8")

        res = tdq_skill_eval.plan_eval(str(plan_file))
        self.assertFalse(res["valid"])
        self.assertGreater(len(res["errors"]), 0)

    def test_plan_cli_exit_codes(self):
        plan = make_valid_plan()
        plan_file = self.tmp_path / "plan.json"
        plan_file.write_text(json.dumps(plan), encoding="utf-8")

        rc = tdq_skill_eval.main(["plan", "--plan", str(plan_file)])
        self.assertEqual(rc, 0)

        # Invalid plan -> exit 1
        bad_plan_file = self.tmp_path / "bad.json"
        bad_plan_file.write_text(json.dumps({"invalid": True}), encoding="utf-8")
        rc_bad = tdq_skill_eval.main(["plan", "--plan", str(bad_plan_file)])
        self.assertEqual(rc_bad, 1)


class TestTdqSkillEvalCheck(unittest.TestCase):
    """Test `check` subcommand: preflight and gate check without model calls."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def test_check_preflight_and_gate_pass(self):
        plan = make_valid_plan()
        plan_file = self.tmp_path / "plan.json"
        plan_file.write_text(json.dumps(plan), encoding="utf-8")

        with mock.patch("tdq_eval_hosts.preflight_host") as mock_preflight:
            mock_preflight.return_value = {
                "host": "claude",
                "status": "READY",
                "ready": True,
                "paid_model_calls": 0,
            }
            res = tdq_skill_eval.check_eval(str(plan_file), stage="pre_implement")
            self.assertTrue(res["ready"])
            self.assertEqual(res["gate"]["verdict"], "PASS")
            self.assertEqual(res["gate"]["live_run_authorized"], False)
            self.assertEqual(mock_preflight.call_count, 1)

    def test_check_blocks_when_preflight_fails(self):
        plan = make_valid_plan()
        plan_file = self.tmp_path / "plan.json"
        plan_file.write_text(json.dumps(plan), encoding="utf-8")

        with mock.patch("tdq_eval_hosts.preflight_host") as mock_preflight:
            mock_preflight.return_value = {
                "host": "claude",
                "status": "BLOCKED",
                "ready": False,
                "reason": "isolation_not_satisfied",
                "paid_model_calls": 0,
            }
            res = tdq_skill_eval.check_eval(str(plan_file), stage="pre_implement")
            self.assertFalse(res["ready"])
            self.assertEqual(mock_preflight.call_count, 1)


class TestTdqSkillEvalRun(unittest.TestCase):
    """Test `run` subcommand: schedule creation and trial execution."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def test_run_builds_schedule_and_executes_trials(self):
        plan = make_valid_plan(repetitions=1)
        plan_file = self.tmp_path / "plan.json"
        plan_file.write_text(json.dumps(plan), encoding="utf-8")

        cases = [
            {"case_id": "pos_case_01", "kind": "positive"},
            {"case_id": "pos_case_02", "kind": "positive"},
            {"case_id": "neg_case_01", "kind": "negative"},
        ]
        cases_file = self.tmp_path / "cases.json"
        cases_file.write_text(json.dumps(cases), encoding="utf-8")

        profile = {
            "timeout_seconds": 10,
            "max_retries": 1,
            "quota_usd": 1.0,
        }
        profile_file = self.tmp_path / "profile.json"
        profile_file.write_text(json.dumps(profile), encoding="utf-8")

        out_dir = self.tmp_path / "results"

        with mock.patch("tdq_eval_hosts.run_host_trial") as mock_run_trial:
            mock_run_trial.return_value = {
                "execution_status": "completed",
                "reason": "success",
                "observed_trigger": True,
                "trigger_provenance": "event:tool_use:test",
                "tool_calls_count": 1,
                "model_calls_count": 1,
                "retries_count": 0,
                "attempts": [{"exit_code": 0, "raw_trace_sha256": "1" * 64}],
                "tokens": {"input_tokens": 50, "output_tokens": 20, "cache_read_tokens": 0, "cache_write_tokens": 0},
            }

            res = tdq_skill_eval.run_eval(
                plan_path=str(plan_file),
                cases_path=str(cases_file),
                profile_path=str(profile_file),
                out_dir=str(out_dir),
            )

            # 3 cases * 1 cell * 1 repetition * 2 variants (AB) = 6 trials
            self.assertEqual(res["total_trials"], 6)
            self.assertEqual(res["completed_trials"], 6)
            self.assertTrue(out_dir.exists())
            result_files = list(out_dir.glob("trial_*.json"))
            self.assertEqual(len(result_files), 6)


class TestTdqSkillEvalReport(unittest.TestCase):
    """Test `report` subcommand: offline grouping by cell, recommendations, json and md."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def test_report_cell_recommendation_keep(self):
        plan = make_valid_plan(repetitions=1)
        cell = plan["cells"][0]
        # Candidate score significantly higher -> KEEP
        records = make_paired_records(plan, cell, score_delta=0.2, count=1)

        results_dir = self.tmp_path / "results"
        results_dir.mkdir()
        for idx, r in enumerate(records):
            (results_dir / f"trial_{idx}.json").write_text(json.dumps(r), encoding="utf-8")

        out_json = self.tmp_path / "report.json"
        out_md = self.tmp_path / "report.md"

        res = tdq_skill_eval.generate_report(
            results_dir=str(results_dir),
            out_json=str(out_json),
            out_md=str(out_md),
            policy={"min_pairs": 1, "quality_margin": 0.05, "efficiency_margin": 0.1},
        )

        self.assertIn("cells", res)
        cell_key = f"{cell['host']}:{cell['model']}"
        self.assertIn(cell_key, res["cells"])
        cell_res = res["cells"][cell_key]
        self.assertEqual(cell_res["recommendation"]["verdict"], "KEEP")
        self.assertEqual(cell_res["sample_count"], 3)  # 3 cases
        self.assertTrue(out_json.exists())
        self.assertTrue(out_md.exists())

        md_content = out_md.read_text(encoding="utf-8")
        self.assertIn("KEEP", md_content)
        self.assertIn(cell["host"], md_content)
        self.assertIn(cell["model"], md_content)

    def test_report_cell_recommendation_drop_on_regression(self):
        plan = make_valid_plan(repetitions=1)
        cell = plan["cells"][0]
        # Candidate score drops -> DROP
        records = make_paired_records(plan, cell, score_delta=-0.3, count=1)

        results_dir = self.tmp_path / "results"
        results_dir.mkdir()
        for idx, r in enumerate(records):
            (results_dir / f"trial_{idx}.json").write_text(json.dumps(r), encoding="utf-8")

        res = tdq_skill_eval.generate_report(
            results_dir=str(results_dir),
            policy={"min_pairs": 1, "quality_margin": 0.05, "efficiency_margin": 0.1},
        )
        cell_key = f"{cell['host']}:{cell['model']}"
        self.assertEqual(res["cells"][cell_key]["recommendation"]["verdict"], "DROP")

    def test_report_preserves_null_metrics_without_defaulting_zero(self):
        plan = make_valid_plan(repetitions=1)
        cell = plan["cells"][0]
        records = make_paired_records(plan, cell, score_delta=0.0, count=1)
        # Clear tokens and cost
        for r in records:
            r["tokens"] = {"input_tokens": None, "output_tokens": None, "cache_read_tokens": None, "cache_write_tokens": None}
            r["total_cost_usd"] = None

        results_dir = self.tmp_path / "results"
        results_dir.mkdir()
        for idx, r in enumerate(records):
            (results_dir / f"trial_{idx}.json").write_text(json.dumps(r), encoding="utf-8")

        res = tdq_skill_eval.generate_report(
            results_dir=str(results_dir),
            policy={"min_pairs": 1, "quality_margin": 0.05, "efficiency_margin": 0.1},
        )
        cell_key = f"{cell['host']}:{cell['model']}"
        metrics = res["cells"][cell_key]["metrics"]
        self.assertIsNone(metrics["mean_cost_usd"])
        self.assertEqual(metrics["token_availability"], "unavailable")


class TestTdqEvalCompatibility(unittest.TestCase):
    """Test compatibility with tdq_eval.py and 60 historical benchmark records."""

    def test_60_historical_records_classify_as_historical_unverified(self):
        bench_dir = GOC / "docs" / "tdq" / "bench" / "tuan-thu"
        self.assertTrue(bench_dir.exists(), f"Benchmark directory {bench_dir} must exist")
        json_files = list(bench_dir.glob("*.json"))
        # Must have exactly 60 historical records
        self.assertEqual(len(json_files), 60)

        for jf in json_files:
            with open(jf, "r", encoding="utf-8") as f:
                rec = json.load(f)
            provenance = tdq_eval_contract.classify_record_provenance(rec)
            self.assertEqual(
                provenance,
                "historical_unverified",
                f"File {jf.name} must classify as historical_unverified, got {provenance}",
            )

    def test_rescore_append_only_preserves_provenance(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        tmp_dir = Path(tmp.name)

        # Create dummy trace and record
        trace = tmp_dir / "trace.jsonl"
        trace.write_text('{"type": "result", "result": "PASS"}\n', encoding="utf-8")

        rec = {
            "ca": "T01",
            "nhanh": "viet",
            "lan": 1,
            "trang_thai": "xong",
            "transcript": str(trace),
            "ma_thoat": 0,
            "ket_qua": {"L001": "dat"},
            "kiem": ["L001"],
        }
        rec_file = tmp_dir / "T01__viet__1.json"
        rec_file.write_text(json.dumps(rec), encoding="utf-8")

        manifest = tdq_eval.tao_manifest_eval(
            base_commit="ea0cdbd",
            candidate_commit="f620094",
            corpus_version="tuan-thu-v1",
            check_set=["L001"],
            scorer_version="v2-temporal",
        )

        xong, bo_qua = tdq_eval.rescore_append_only(str(tmp_dir), phien_ban=2, manifest=manifest)
        self.assertEqual(len(xong), 1)
        self.assertEqual(len(bo_qua), 0)

        v2_file = tmp_dir / "T01__viet__1__v2.json"
        self.assertTrue(v2_file.exists())
        with open(v2_file, "r", encoding="utf-8") as f:
            v2_rec = json.load(f)
        self.assertEqual(v2_rec.get("provenance"), "historical_unverified")
