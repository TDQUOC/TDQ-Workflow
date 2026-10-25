"""Keep BA authoring in the existing approval gates with usable CLI examples."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def text(path):
    return (ROOT / path).read_text(encoding="utf-8")


class ArchifyWorkflowContract(unittest.TestCase):
    def test_full_has_direct_reference_and_no_broken_open_command(self):
        skill = text("skills/tdq-spec/SKILL.md")
        self.assertIn("references/archify-ba.md", skill)
        self.assertNotIn("`python3 scripts/tdq_archify.py open`", skill)

    def test_quick_and_build_references_are_direct(self):
        self.assertIn("references/archify-quick.md", text("skills/tdq-intake/SKILL.md"))
        self.assertIn("references/archify-lifecycle.md", text("skills/tdq-build/SKILL.md"))

    def test_render_examples_use_named_flags_and_plugin_root(self):
        for path in ("skills/tdq-spec/references/archify-ba.md",
                     "skills/tdq-intake/references/archify-quick.md"):
            with self.subTest(path=path):
                body = text(path)
                self.assertIn('${CLAUDE_PLUGIN_ROOT}/scripts/tdq_archify.py', body)
                for flag in ("--type", "--candidate", "--out", "--document", "--lane"):
                    self.assertIn(flag, body)
                self.assertIn("agent", body.lower())
                self.assertIn("no extra approval gate", body.lower())

    def test_lifecycle_checks_binding_and_freshness(self):
        body = text("skills/tdq-build/references/archify-lifecycle.md")
        for term in ("verify", "--manifest", "status", "sync-master", "--model",
                     "stale", "planned", "committed"):
            self.assertIn(term, body)
        self.assertIn("Do not", body)

    def test_templates_do_not_use_positional_render(self):
        for path in ("skills/tdq-spec/references/spec-template.md",
                     "skills/tdq-intake/references/quick-lane.md"):
            self.assertNotIn("tdq_archify.py render workflow", text(path))
            self.assertNotIn("tdq_archify.py render <type>", text(path))

    def test_plan_reuses_approved_preview(self):
        self.assertIn("manifest", text("skills/tdq-plan/references/plan-template.md"))
