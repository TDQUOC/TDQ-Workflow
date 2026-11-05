#!/usr/bin/env python3
"""Unit tests for eval workflow gate in tdq_state.py (T3.1 / Q8)."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import tdq_state  # noqa: E402
import tdq_eval_contract  # noqa: E402


class TestEvalWorkflowGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = Path(self.tmp.name)
        os.makedirs(self.cwd / "docs" / "tdq", exist_ok=True)
        os.makedirs(self.cwd / "docs" / "tdq" / "plan", exist_ok=True)
        os.makedirs(self.cwd / "docs" / "tdq" / "artifacts" / "2026-11-01-0001-test", exist_ok=True)
        self.slug = "2026-11-01-0001-test"
        self._old_env = os.environ.get("TDQ_PROJECT_DIR")
        os.environ["TDQ_PROJECT_DIR"] = str(self.cwd)

    def tearDown(self):
        if self._old_env is not None:
            os.environ["TDQ_PROJECT_DIR"] = self._old_env
        else:
            os.environ.pop("TDQ_PROJECT_DIR", None)
        self.tmp.cleanup()

    def _run_state(self, *args, check=False):
        env = os.environ.copy()
        env["TDQ_PROJECT_DIR"] = str(self.cwd)
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "tdq_state.py"), *args],
            cwd=str(self.cwd),
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=check,
        )

    def _init_state(self, lane="full"):
        self._run_state("init", self.slug, lane, "--lang", "vi", "--bo-qua-lsp", "test", check=True)
        self._run_state("set", "phase=spec", check=True)
        plan_rel = f"docs/tdq/plan/{self.slug}.md"
        plan_file = self.cwd / plan_rel
        plan_file.write_text("# Plan\n- [ ] **T1.1** test\n", encoding="utf-8")
        spec_rel = f"docs/tdq/spec/{self.slug}.md"
        spec_file = self.cwd / spec_rel
        spec_file.parent.mkdir(parents=True, exist_ok=True)
        spec_file.write_text("## 1. Mục tiêu\nTest\n", encoding="utf-8")
        self._run_state("set", f"spec_file={spec_rel}", check=True)
        self._run_state("approve", "spec", "--by", "user approved", "--bo-qua-do", "test", check=True)
        self._run_state("set", f"plan_file={plan_rel}", check=True)
        self._run_state("approve", "plan", "--by", "user approved", "--mode", "main", check=True)

    def test_implement_requires_eval_plan_when_behavioral_targets_present(self):
        self._init_state()
        plan_file = self.cwd / f"docs/tdq/plan/{self.slug}.md"
        plan_file.write_text(
            "# Plan\n- [ ] **T1.1** test\n  - Chạm: `skills/tdq-build/SKILL.md`\n",
            encoding="utf-8"
        )
        # Not opted in: gate skipped
        proc = self._run_state("set", "phase=implement")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        # Opted in without eval-plan: blocked
        self._run_state("set", "phase=plan")
        self._run_state("eval-enable", "--by", "user approved", check=True)
        proc = self._run_state("set", "phase=implement")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("eval-plan", proc.stderr.lower())

    def test_implement_allows_exempt_targets_without_eval_plan(self):
        self._init_state()
        plan_file = self.cwd / f"docs/tdq/plan/{self.slug}.md"
        plan_file.write_text(
            "# Plan\n- [ ] **T1.1** test\n  - Chạm: `README.md`, `docs/tdq/STATE.md`\n",
            encoding="utf-8"
        )
        proc = self._run_state("set", "phase=implement")
        self.assertEqual(proc.returncode, 0)
        st = tdq_state.load(str(self.cwd))
        self.assertEqual(st.get("phase"), "implement")

    def _write_skill_plan(self):
        plan_file = self.cwd / f"docs/tdq/plan/{self.slug}.md"
        plan_file.write_text(
            "# Plan\n- [ ] **T1.1** test\n  - Chạm: `skills/tdq-build/SKILL.md`\n",
            encoding="utf-8"
        )

    def test_eval_enable_records_by_and_at(self):
        self._init_state()
        proc = self._run_state("eval-enable", "--by", "user approved")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        st = tdq_state.load(str(self.cwd))
        self.assertEqual(st["eval_enabled"]["by"], "user approved")
        self.assertTrue(st["eval_enabled"]["at"])

    def test_eval_enable_requires_by(self):
        self._init_state()
        self.assertNotEqual(self._run_state("eval-enable").returncode, 0)
        self.assertNotEqual(self._run_state("eval-enable", "--by", "").returncode, 0)
        self.assertFalse(tdq_state.load(str(self.cwd)).get("eval_enabled"))

    def test_eval_waive_command_removed(self):
        self._init_state()
        proc = self._run_state("eval-waive", "--reason", "x", "--by", "user approved")
        self.assertNotEqual(proc.returncode, 0)

    def test_legacy_eval_waiver_key_is_ignored(self):
        self._init_state()
        self._write_skill_plan()
        state_path = Path(tdq_state.state_path(str(self.cwd)))
        st = json.loads(state_path.read_text(encoding="utf-8"))
        st["eval_waiver"] = {"verdict": "WAIVED_USER", "by": "old", "reason": "old"}
        state_path.write_text(json.dumps(st), encoding="utf-8")
        proc = self._run_state("set", "phase=implement")
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_report_gate_blocks_when_evidence_missing_or_incomplete(self):
        self._init_state()
        plan_file = self.cwd / f"docs/tdq/plan/{self.slug}.md"
        plan_file.write_text(
            "# Plan\n- [ ] **T1.1** test\n  - Chạm: `skills/tdq-build/SKILL.md`\n",
            encoding="utf-8"
        )
        # Register a valid eval plan file
        eval_plan_path = self.cwd / "eval-plan.json"
        plan_data = tdq_eval_contract.create_eval_plan(
            experiment_id="exp-test",
            targets={"skills/tdq-build/SKILL.md": "a" * 64},
            base_identity="b" * 40,
            candidate_identity="planned",
            change_kind="behavioral",
            hypothesis="test",
            evaluation_kind="mechanism",
            corpus_id="corpus-1",
            dev_cases_sha256="c" * 64,
            holdout_cases_sha256="d" * 64,
            rubric_version="r1",
            scorer_version="s1",
            expected_triggers=["case-1"],
            negative_cases=["case-2"],
            required_metrics=["trigger_accuracy", "outcome_quality"],
            cells=[{"host": "claude", "model": "sonnet", "permission_profile": "p", "tool_aliases": {}, "cache_profile": "c"}],
            repetitions=1,
            order_policy="AB_BA",
            thresholds={"quality_pass_rate": 1.0},
        )
        eval_plan_path.write_text(json.dumps(plan_data), encoding="utf-8")
        self._run_state("set", f"eval_plan_file={eval_plan_path}", check=True)
        self._run_state("eval-enable", "--by", "user approved", check=True)
        self._run_state("set", "phase=implement", check=True)

        # Attempting to move to report without certified evidence
        proc_rep = self._run_state("set", "phase=report")
        self.assertNotEqual(proc_rep.returncode, 0)
        self.assertIn("incomplete", proc_rep.stderr.lower())

    def test_report_gate_skipped_without_eval_enable(self):
        self._init_state()
        self._write_skill_plan()
        self._run_state("set", "phase=implement", check=True)
        proc = self._run_state("set", "phase=report")
        self.assertEqual(proc.returncode, 0, proc.stderr)


class TestEvalOptInRules(unittest.TestCase):
    """Eval is opt-in: no rule file forces an eval-plan on skill changes."""
    FORCING = {
        "skills/tdq-build/SKILL.md": "Skill changes require valid eval-plan",
        "skills/tdq-build/references/qc.md": "skill edits require certified evidence",
        "skills/tdq-spec/SKILL.md": "eval-plan for skill changes",
        "skills/tdq-spec/references/spec-template.md": "cần eval-plan trước implement",
        "skills/tdq-plan/SKILL.md": "eval-plan if skills change",
        "skills/tdq-intake/SKILL.md": "eval need for skill changes",
    }

    def test_no_rule_forces_eval_plan(self):
        for rel, phrase in self.FORCING.items():
            self.assertNotIn(phrase, (ROOT / rel).read_text(encoding="utf-8"), rel)

    def test_opt_in_stated_where_eval_is_defined(self):
        for rel in ("skills/tdq-build/SKILL.md", "skills/tdq-build/references/skill-eval.md"):
            body = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("eval-enable", body, rel)
            self.assertIn("opt-in", body, rel)


if __name__ == "__main__":
    unittest.main()
