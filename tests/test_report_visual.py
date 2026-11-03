"""Contract: một chuẩn report Markdown + Archify HTML cho cả Deep và Express."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def text(path):
    return (ROOT / path).read_text(encoding="utf-8")


class ReportVisualContract(unittest.TestCase):
    def test_both_lanes_enter_shared_report_and_write_pair(self):
        corpus = "\n".join(text(p) for p in (
            "skills/tdq-intake/references/quick-lane.md",
            "skills/tdq-build/SKILL.md",
            "skills/tdq-build/references/report-template.md",
        ))
        for value in ("docs/tdq/reports/<slug>.md", "docs/tdq/reports/<slug>.html", "phase=report"):
            self.assertIn(value, corpus)
        self.assertNotIn("phase `report` is the whole of Part C", text("skills/tdq-build/SKILL.md"))

    def test_html_reports_actual_result_with_honest_fallback(self):
        corpus = "\n".join(text(p) for p in (
            "skills/tdq-build/references/report-template.md",
            "skills/tdq-build/references/archify-lifecycle.md",
        ))
        for value in ("task", "DoD", "QC", "Giới hạn", "evidence-kind working-tree", "fallback", "stale"):
            self.assertIn(value.lower(), corpus.lower())
        self.assertIn("never pass `actual`", corpus)

    def test_express_reports_do_not_invent_a_second_gate_or_renderer(self):
        law = text("skills/tdq-intake/references/quick-lane.md")
        handoff = text("skills/tdq-intake/references/quick-lane-qc.md")
        self.assertIn("No new approval gate", handoff)
        self.assertNotIn("renderer", law.lower())
        self.assertNotIn("approve report", handoff.lower())


if __name__ == "__main__":
    unittest.main()
