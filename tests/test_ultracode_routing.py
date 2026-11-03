"""Contract tests for Ultracode as a lane modifier, never a TDQ lane/state."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def text(path):
    return (ROOT / path).read_text(encoding="utf-8")


class UltracodeLaneContract(unittest.TestCase):
    def test_lane_suffix_is_policy_and_cli_stays_canonical(self):
        body = text("skills/tdq-intake/references/lane-decision.md")
        for value in ("express_ultracode", "deep_ultracode", "1a_ultracode"):
            self.assertIn(value, body)
        self.assertIn("raw-human", body)
        self.assertIn("quick|full", body)
        self.assertNotIn('"express_ultracode"', text("scripts/tdq_state.py"))

    def test_intake_strips_suffix_before_init(self):
        wrapper = text("skills/tdq-intake/SKILL.md")
        contract = text("skills/tdq-intake/references/lane-decision.md")
        self.assertIn("_ultracode", wrapper)
        self.assertIn("Strip `_ultracode`", contract)
        self.assertIn("never pass", contract)


class UltracodeExpressContract(unittest.TestCase):
    def test_express_routes_finite_workflow_without_gate(self):
        body = text("skills/tdq-intake/references/quick-lane.md")
        for term in ("express_ultracode", "finite", "route", "fallback", "accounting"):
            self.assertIn(term, body.lower())
        self.assertIn("exactly one gate", body)


class UltracodeDeepContract(unittest.TestCase):
    def test_deep_routes_are_optional_without_new_state(self):
        corpus = "\n".join(text(p) for p in (
            "skills/tdq-intake/references/analyze-full.md",
            "skills/tdq-spec/SKILL.md",
            "skills/tdq-plan/SKILL.md",
            "skills/tdq-build/SKILL.md",
        ))
        for term in ("deep_ultracode", "spec review", "plan review", "Workflow implement"):
            self.assertIn(term, corpus)
        self.assertIn("no new gate", corpus)
        self.assertNotIn("isolation: 'worktree'", corpus)


if __name__ == "__main__":
    unittest.main()
