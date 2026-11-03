"""Rules 2026-11-02: read-only sub-agents in every phase, and a ready-made PR body in the report."""
import io
import os
import unittest

from helper import ROOT


def _doc(*parts):
    with io.open(os.path.join(ROOT, *parts), encoding="utf-8") as fh:
        return fh.read()


class TestLuatSubagent(unittest.TestCase):
    def test_subagent_conventions_mo_moi_phase_chi_doc(self):
        self.assertIn("read-only sub-agents in any phase",
                      _doc("skills", "tdq-conventions", "SKILL.md"))
        body = _doc("skills", "tdq-conventions", "references", "subagent-tuning.md")
        for needle in ("any phase", "one job per sub-agent", "docs/", "before phase `implement`",
                       "TDQ:TEAM"):
            self.assertIn(needle, body)

    def test_subagent_reminder_code_noi_ca_moi(self):
        body = _doc("skills", "tdq-conventions", "references", "reminder-codes.md")
        self.assertIn("`agent_id`", body)


class TestLuatPr(unittest.TestCase):
    def test_pr_report_co_than_pr_soan_san(self):
        body = _doc("skills", "tdq-build", "references", "report-template.md")
        self.assertIn("## Thân PR (soạn sẵn)", body)
        self.assertIn("never opens the PR itself", body)


if __name__ == "__main__":
    unittest.main()
