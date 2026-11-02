"""Shared Ultracode contract: finite orchestration under TDQ state/Git ownership."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def text(path):
    return (ROOT / path).read_text(encoding="utf-8")


class UltracodeSharedContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.body = text("skills/tdq-conventions/references/ultracode.md")

    def test_inherited_subtask_contract(self):
        for term in ("Inherited subtask", "no intake", "state", "approval", "commit", "push",
                     "finite", "structured result", "assigned report path"):
            self.assertIn(term, self.body)

    def test_no_token_ceiling_but_finite_termination(self):
        self.assertIn("No token ceiling", self.body)
        self.assertIn("budget.total == null", self.body)
        self.assertIn("never loop on budget.remaining", self.body)

    def test_completion_accounting_is_fail_closed(self):
        for term in ("expected", "completed", "null", "errors", "omitted", "truncated", "complete=false"):
            self.assertIn(term, self.body)

    def test_resume_snapshot_is_bound(self):
        for term in ("request", "phase", "HEAD", "dirty", "spec", "plan"):
            self.assertIn(term, self.body)


class UltracodeHostContract(unittest.TestCase):
    def test_three_hosts_and_denial_fallback(self):
        body = text("skills/tdq-conventions/references/ultracode.md")
        for term in ("interactive", "claude -p", "Agent SDK", "raw human", "permission envelope",
                     "structured output fallback"):
            self.assertIn(term, body)


class UltracodeOwnershipContract(unittest.TestCase):
    def test_team_owns_implementation_worktrees(self):
        body = text("skills/tdq-conventions/references/ultracode.md") + text("skills/tdq-build/references/team-mode.md")
        for term in ("tdq_team.py", "assign", "audit", "open", "check", "merge", "tick", "sweep"):
            self.assertIn(term, body)
        self.assertIn("no Workflow-native isolation", body)

    def test_qc_accounting_does_not_add_items(self):
        wrapper = text("skills/tdq-build/references/qc.md")
        contract = text("skills/tdq-conventions/references/ultracode.md")
        self.assertIn("Ultracode", wrapper)
        self.assertIn("DoD", contract)
        self.assertIn("QC-F1", contract)
        self.assertIn("complete=false", contract)

    def test_eval_is_quality_first(self):
        body = text("skills/tdq-build/references/skill-eval.md")
        for term in ("Ultracode", "unique verified findings", "completeness", "false-positive", "token"):
            self.assertIn(term, body)


if __name__ == "__main__":
    unittest.main()
