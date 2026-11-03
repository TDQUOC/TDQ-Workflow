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

import ast
import hashlib
import inspect
import json
import marshal
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types
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


def _cognitive_score(node, depth=0):
    # Conservative AST count: boolean operators and comprehensions also count.
    control = isinstance(node, (ast.If, ast.IfExp, ast.For, ast.While, ast.ExceptHandler))
    score = 1 + depth if control else 0
    if isinstance(node, (ast.BoolOp, ast.comprehension)):
        score += 1
    for child in ast.iter_child_nodes(node):
        elif_branch = isinstance(node, ast.If) and child in node.orelse and isinstance(child, ast.If)
        score += _cognitive_score(child, depth + int(control and not elif_branch))
    return score


def test_refactored_functions_stay_within_size_and_branch_limits():
    targets = {
        tdq_skill_eval: "_validate_scorer_dependencies scorer_identity "
        "_trial_identity _build_trial_record _validate_run_plan _index_cases "
        "_verify_corpus_hashes _load_bound_cases _read_snapshot _bind_snapshots _validate_cost_quota "
        "_validate_scorer_outcome _score_trial _execute_trial run_eval _render_markdown_report "
        "_report_provenance _group_report_cells generate_report",
        tdq_eval_hosts: "_valid_trace_content _valid_trace_usage _validate_trace_fields "
        "_decode_trace_event _bind_trace_model _validate_trace_event _process_codex_response "
        "_consume_trace_event _trace_result parse_trace_stream _record_attempt _parse_attempt "
        "_run_attempts _trial_output run_host_trial",
    }
    for module, names in targets.items():
        functions = {node.name: node for node in ast.parse(inspect.getsource(module)).body
                     if isinstance(node, ast.FunctionDef)}
        for name in names.split():
            node = functions[name]
            assert node.end_lineno - node.lineno + 1 <= 50, name
            branches = sum(
                len(child.values) - 1 if isinstance(child, ast.BoolOp) else
                len(child.ifs) + 1 if isinstance(child, ast.comprehension) else 1
                for child in ast.walk(node)
                if isinstance(child, (ast.If, ast.IfExp, ast.For, ast.While,
                                      ast.ExceptHandler, ast.BoolOp, ast.comprehension))
            )
            assert branches + 1 <= 10, (name, branches + 1)
            assert _cognitive_score(node) <= 15, (name, _cognitive_score(node))


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

        cases = [
            {"case_id": "pos_case_01", "kind": "positive"},
            {"case_id": "pos_case_02", "kind": "positive"},
            {"case_id": "neg_case_01", "kind": "negative"},
        ]
        for case in cases:
            case.update(prompt=f"Handle {case['case_id']}", split="dev")
        cases_file = self.tmp_path / "cases.json"
        cases_file.write_text(json.dumps(cases), encoding="utf-8")
        plan["dev_cases_sha256"] = tdq_eval_contract._digest(cases)
        plan["holdout_cases_sha256"] = tdq_eval_contract._digest([])

        profile = {
            "timeout_seconds": 10,
            "max_retries": 1,
        }
        profile["sources"] = {}
        target = plan["targets"][0]
        for variant in ("A", "B"):
            source = self.tmp_path / variant
            path = source / target
            path.parent.mkdir(parents=True)
            path.write_text(f"Instructions {variant}", encoding="utf-8")
            profile["sources"][variant] = {
                "root": str(source), "hashes": {target: tdq_eval_hosts.hash_file_streaming(path)},
            }
        plan["targets"] = profile["sources"]["B"]["hashes"]
        plan["base_identity"] = tdq_eval_contract._digest(profile["sources"]["A"]["hashes"])
        plan["candidate_identity"] = tdq_eval_contract._digest(plan["targets"])
        plan_file.write_text(json.dumps(plan), encoding="utf-8")
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


def _score_response(case, response):
    passed = all(text in response["response_text"] for text in case["required"])
    return {"passed": passed, "score": float(passed),
            "checks": {"rule_compliance": "pass" if passed else "fail"}}


class TestEvaluatorBinding(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.plan = make_valid_plan()
        self.cases = [{"id": "pos_case_01", "split": "dev", "prompt": "Inspect title",
                       "required": ["verify title"], "forbidden": ["install"]}]
        self.plan["expected_triggers"] = ["pos_case_01"]
        self.plan["negative_cases"] = []
        self.plan["dev_cases_sha256"] = tdq_eval_contract._digest(self.cases)
        self.plan["holdout_cases_sha256"] = tdq_eval_contract._digest([])
        self.profile = {"sources": {}}
        target = self.plan["targets"][0]
        for variant in ("A", "B"):
            source = self.root / variant
            path = source / target
            path.parent.mkdir(parents=True)
            path.write_text(f"Instructions {variant}", encoding="utf-8")
            hashes = {target: tdq_eval_hosts.hash_file_streaming(path)}
            self.profile["sources"][variant] = {"root": str(source), "hashes": hashes}
        self.plan["targets"] = self.profile["sources"]["B"]["hashes"]
        self.plan["base_identity"] = tdq_eval_contract._digest(self.profile["sources"]["A"]["hashes"])
        self.plan["candidate_identity"] = tdq_eval_contract._digest(self.plan["targets"])
        for name, data in (("plan", self.plan), ("cases", {"cases": self.cases}), ("profile", self.profile)):
            (self.root / f"{name}.json").write_text(json.dumps(data), encoding="utf-8")

    def run_eval(self, **kwargs):
        return tdq_skill_eval.run_eval(self.root / "plan.json", self.root / "cases.json",
                                       self.root / "profile.json", self.root / "out", **kwargs)

    def bind_scorer(self, scorer):
        binding = {"module": scorer.__module__, "qualname": scorer.__qualname__,
                   "source_sha256": hashlib.sha256(inspect.getsource(scorer).encode("utf-8")).hexdigest(),
                   "code_sha256": hashlib.sha256(marshal.dumps(scorer.__code__)).hexdigest(),
                   "rubric_version": self.plan["rubric_version"]}
        self.plan["scorer_version"] = "sha256:" + tdq_eval_contract._digest(binding)
        (self.root / "plan.json").write_text(json.dumps(self.plan), encoding="utf-8")

    def test_shadowed_builtin_scorer_rejected_before_launch(self):
        self.bind_scorer(_score_response)
        altered = types.FunctionType(_score_response.__code__,
                                     dict(_score_response.__globals__, all=lambda values: True))
        self.assertFalse(_score_response(self.cases[0], {"response_text": "wrong"})["passed"])
        self.assertTrue(altered(self.cases[0], {"response_text": "wrong"})["passed"])
        with mock.patch("tdq_eval_hosts.run_host_trial") as run:
            with self.assertRaisesRegex(ValueError, "unsupported_scorer_identity"):
                self.run_eval(scorer=altered)
            run.assert_not_called()

    def test_custom_builtins_scorer_rejected(self):
        altered = types.FunctionType(_score_response.__code__,
                                     dict(_score_response.__globals__, __builtins__={"all": lambda xs: True}))
        with self.assertRaisesRegex(ValueError, "unsupported_scorer_identity"):
            tdq_skill_eval.scorer_identity(altered, "rubric-v1")

    def test_global_dependency_in_nested_code_rejected(self):
        def scorer(case, response):
            return all(os.name for text in case["required"])

        with self.assertRaisesRegex(ValueError, "unsupported_scorer_identity"):
            tdq_skill_eval.scorer_identity(scorer, "rubric-v1")

    def test_nonlocal_dependency_rejected(self):
        threshold = 1
        def scorer(case, response):
            return threshold

        with self.assertRaisesRegex(ValueError, "unsupported_scorer_identity"):
            tdq_skill_eval.scorer_identity(scorer, "rubric-v1")

    def test_mutated_code_rejected_before_launch(self):
        self.bind_scorer(_score_response)
        code = _score_response.__code__
        altered = types.FunctionType(code.replace(co_consts=tuple(
            "different_check" if value == "rule_compliance" else value for value in code.co_consts
        )), _score_response.__globals__)
        with mock.patch("tdq_eval_hosts.run_host_trial") as run:
            with self.assertRaisesRegex(ValueError, "scorer_binding_mismatch"):
                self.run_eval(scorer=altered)
            run.assert_not_called()

    def test_changed_scorer_rejected_before_launch(self):
        self.bind_scorer(_score_response)

        def changed(case, response):
            return {"passed": True, "score": 1.0, "checks": {"rule_compliance": "pass"}}

        changed.__qualname__ = _score_response.__qualname__
        with mock.patch("tdq_eval_hosts.run_host_trial") as run:
            with self.assertRaisesRegex(ValueError, "scorer_binding_mismatch"):
                self.run_eval(scorer=changed)
            run.assert_not_called()
        self.assertFalse((self.root / "out").exists())

    def test_changed_rubric_rejected_before_launch(self):
        self.bind_scorer(_score_response)
        self.plan["rubric_version"] = "different-rubric"
        (self.root / "plan.json").write_text(json.dumps(self.plan), encoding="utf-8")
        with mock.patch("tdq_eval_hosts.run_host_trial") as run:
            with self.assertRaisesRegex(ValueError, "scorer_binding_mismatch"):
                self.run_eval(scorer=_score_response)
            run.assert_not_called()

    def test_scorer_identity_matches_locked_binding(self):
        self.bind_scorer(_score_response)
        self.assertEqual(tdq_skill_eval.scorer_identity(_score_response, self.plan["rubric_version"]),
                         self.plan["scorer_version"])

    def test_callable_without_source_rejected_before_launch(self):
        with mock.patch("tdq_eval_hosts.run_host_trial") as run:
            with self.assertRaisesRegex(ValueError, "unsupported_scorer_identity"):
                self.run_eval(scorer=mock.Mock())
            run.assert_not_called()

    def test_unbound_scorer_rejected_before_launch(self):
        with mock.patch("tdq_eval_hosts.run_host_trial") as run:
            with self.assertRaisesRegex(ValueError, "scorer_binding_mismatch"):
                self.run_eval(scorer=_score_response)
            run.assert_not_called()

    def test_completed_is_not_quality_oracle(self):
        trial = tdq_eval_contract.build_ab_ba_schedule(["pos_case_01"], self.plan["cells"], 1, "e" * 64)[0]
        rec = tdq_skill_eval._build_trial_record(self.plan, trial, {"execution_status": "completed"}, "f" * 64)
        self.assertIsNone(rec["passed"])
        self.assertIsNone(rec["score"])
        self.assertEqual(rec["checks"], {"rule_compliance": "unavailable"})

    def test_case_model_and_distinct_sources_reach_runner(self):
        with mock.patch("tdq_eval_hosts.run_host_trial", return_value={"execution_status": "incomplete"}) as run:
            self.run_eval()
        specs = [call.kwargs["trial_spec"] for call in run.call_args_list]
        self.assertEqual(len(specs), 2)
        self.assertEqual([s["prompt"] for s in specs], ["Inspect title"] * 2)
        self.assertEqual([s["model"] for s in specs], [self.plan["cells"][0]["model"]] * 2)
        self.assertIn("Instructions A", specs[0]["instructions"])
        self.assertIn("Instructions B", specs[1]["instructions"])
        self.assertNotEqual(specs[0]["source_sha256"], specs[1]["source_sha256"])
        rec = json.loads(next((self.root / "out").glob("trial_*.json")).read_text(encoding="utf-8"))
        self.assertIsNone(rec["score"])

    def test_finite_quota_blocks_before_launch_without_cost_enforcement(self):
        for quota in (0, 1.0):
            self.profile["quota_usd"] = quota
            (self.root / "profile.json").write_text(json.dumps(self.profile), encoding="utf-8")
            with mock.patch("tdq_eval_hosts.run_host_trial") as run:
                with self.assertRaisesRegex(ValueError, "cost_quota_unavailable"):
                    self.run_eval()
                run.assert_not_called()
            self.assertFalse((self.root / "out").exists())

    def test_missing_latency_stays_unavailable_in_record(self):
        trial = tdq_eval_contract.build_ab_ba_schedule(["pos_case_01"], self.plan["cells"], 1, "e" * 64)[0]
        rec = tdq_skill_eval._build_trial_record(self.plan, trial, {}, "f" * 64)
        self.assertIsNone(rec["wall_latency_seconds"])
        rec = tdq_skill_eval._build_trial_record(self.plan, trial, {"wall_latency_seconds": 1.25}, "f" * 64)
        self.assertEqual(rec["wall_latency_seconds"], 1.25)

    def test_changed_corpus_blocks_before_launch(self):
        self.cases[0]["prompt"] = "changed"
        (self.root / "cases.json").write_text(json.dumps({"cases": self.cases}), encoding="utf-8")
        with mock.patch("tdq_eval_hosts.run_host_trial") as run:
            with self.assertRaisesRegex(ValueError, "corpus_hash_mismatch"):
                self.run_eval()
            run.assert_not_called()

    def test_changed_source_blocks_before_launch(self):
        (self.root / "A" / next(iter(self.plan["targets"]))).write_text("changed", encoding="utf-8")
        with mock.patch("tdq_eval_hosts.run_host_trial") as run:
            with self.assertRaisesRegex(ValueError, "source_hash_mismatch"):
                self.run_eval()
            run.assert_not_called()

    def test_baseline_identity_blocks_rebound_snapshot(self):
        source = self.profile["sources"]["A"]
        target = next(iter(source["hashes"]))
        path = Path(source["root"]) / target
        path.write_text("Different baseline", encoding="utf-8")
        source["hashes"][target] = tdq_eval_hosts.hash_file_streaming(path)
        (self.root / "profile.json").write_text(json.dumps(self.profile), encoding="utf-8")
        with mock.patch("tdq_eval_hosts.run_host_trial") as run:
            with self.assertRaisesRegex(ValueError, "unbound_baseline_snapshot"):
                self.run_eval()
            run.assert_not_called()

    def test_cli_without_scorer_blocks_before_launch(self):
        with mock.patch("tdq_skill_eval.run_eval", return_value={"completed_trials": 2, "total_trials": 2}) as run, mock.patch("builtins.print") as output:
            rc = tdq_skill_eval.main([
                "run", "--plan", str(self.root / "plan.json"),
                "--cases", str(self.root / "cases.json"),
                "--profile", str(self.root / "profile.json"), "--out-dir", str(self.root / "out"),
            ])
        self.assertEqual(rc, 1)
        run.assert_not_called()
        self.assertEqual(json.loads(output.call_args.args[0])["reason"], "missing_scorer")

    def test_verified_response_without_scorer_stays_unavailable(self):
        response = {"execution_status": "completed", "response_text": "verify title",
                    "observed_model": self.plan["cells"][0]["model"], "host": "claude",
                    "outcome": {"passed": True, "score": 1, "checks": {"rule_compliance": "pass"}}}
        with mock.patch("tdq_eval_hosts.run_host_trial", return_value=response):
            self.run_eval()
        records = [json.loads(p.read_text(encoding="utf-8")) for p in (self.root / "out").glob("trial_*.json")]
        self.assertEqual(len(records), 2)
        for record in records:
            self.assertIsNone(record["passed"])
            self.assertIsNone(record["score"])
            self.assertEqual(record["outcome_availability"], "unavailable")
            self.assertEqual(record["outcome_reason"], "missing_scorer")

    def test_explicit_scorer_can_pass_verified_response(self):
        response = {"execution_status": "completed", "response_text": "verify title",
                    "observed_model": self.plan["cells"][0]["model"], "host": "claude"}
        self.bind_scorer(_score_response)
        with mock.patch("tdq_eval_hosts.run_host_trial", return_value=response):
            self.run_eval(scorer=_score_response)
        records = [json.loads(p.read_text(encoding="utf-8")) for p in (self.root / "out").glob("trial_*.json")]
        self.assertEqual(len(records), 2)
        for record in records:
            self.assertIs(record["passed"], True)
            self.assertEqual(record["score"], 1.0)
            self.assertEqual(record["outcome_reason"], "explicit_scorer")

    def test_unverified_model_never_reaches_scorer(self):
        response = {"execution_status": "completed", "response_text": "verify title",
                    "observed_model": "different-model", "host": "claude"}
        def scorer(case, response):
            raise AssertionError("unverified response reached scorer")

        self.bind_scorer(scorer)
        with mock.patch("tdq_eval_hosts.run_host_trial", return_value=response):
            self.run_eval(scorer=scorer)
        records = [json.loads(p.read_text(encoding="utf-8")) for p in (self.root / "out").glob("trial_*.json")]
        self.assertEqual(len(records), 2)
        for record in records:
            self.assertIsNone(record["score"])
            self.assertEqual(record["outcome_reason"], "unverified_response")

    def test_explicit_scorer_grades_observed_response(self):
        response = {"execution_status": "completed", "response_text": "wrong answer",
                    "observed_model": self.plan["cells"][0]["model"], "host": "claude"}
        self.bind_scorer(_score_response)
        with mock.patch("tdq_eval_hosts.run_host_trial", return_value=response):
            self.run_eval(scorer=_score_response)
        records = [json.loads(p.read_text(encoding="utf-8")) for p in (self.root / "out").glob("trial_*.json")]
        self.assertTrue(all(r["passed"] is False and r["score"] == 0 for r in records))


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

    def test_report_provenance_matches_records(self):
        for labels, expected in ((["live"], "live"), (["synthetic/offline"], "synthetic/offline"),
                                 (["live", "synthetic/offline"], "mixed"), ([None], "unavailable")):
            with self.subTest(labels=labels):
                results_dir = self.tmp_path / expected.replace('/', '-')
                results_dir.mkdir()
                for idx, label in enumerate(labels):
                    (results_dir / f"trial_{idx}.json").write_text(
                        json.dumps({"provenance": label}), encoding="utf-8")
                out_md = self.tmp_path / f"{expected.replace('/', '-')}.md"
                report = tdq_skill_eval.generate_report(results_dir, out_md=out_md)
                self.assertEqual(report["provenance"], expected)
                self.assertIn(f"Nguồn gốc bản ghi: {expected}", out_md.read_text(encoding="utf-8"))

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
