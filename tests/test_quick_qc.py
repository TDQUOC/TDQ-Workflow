"""Lane quick: QC 3 hạng mục (mặc định BẬT) + vòng fix bắt buộc trần 3 vòng.

Khoá cứng 5 nguồn sự thật phải phát biểu CÙNG một luật:
  N1 skills/tdq-intake/references/quick-lane.md
  N2 skills/tdq-intake/SKILL.md
  N3 scripts/tdq_state.py  (PHASE_TABLE["quick"], default_state, _parse_approve_args)
  N4 portable/workflow/**  (mirror cho agent ngoài Claude Code)
  N5 phases.md × 2 bản     (doc TỰ SINH từ PHASE_TABLE — không sửa tay)
Spec: docs/tdq/spec/2026-08-07-siet-qc-lane-quick.md
"""
import os
import sys
import tempfile
import unittest

from helper import ROOT, HOOKS, run_state_cli, tdq_state

sys.path.insert(0, HOOKS)
import _common  # noqa: E402
import prompt_context  # noqa: E402

N1 = os.path.join(ROOT, "skills", "tdq-intake", "references", "quick-lane.md")
N2 = os.path.join(ROOT, "skills", "tdq-intake", "SKILL.md")
N4_QUICK = os.path.join(ROOT, "portable", "workflow", "references", "quick-lane.md")
N5_PLUGIN = os.path.join(ROOT, "skills", "tdq-conventions", "references", "phases.md")
N5_PORTABLE = os.path.join(ROOT, "portable", "workflow", "phases.md")

# 3 file văn bản người đọc (N1, N2, N4) phải cùng nêu luật vòng fix.
LAW_DOCS = (N1, N2, N4_QUICK)

FIX_CAP = "trần 3 vòng"
FIX_HEADING = "QC vòng N — fix"


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


class QuickQcDocTest(unittest.TestCase):
    """N1: quick-lane.md phải định nghĩa QC, không chỉ nói 'chạy validate'."""

    def test_quick_lane_has_qc_section(self):
        self.assertIn("## QC ở quick", read(N1))

    def test_quick_lane_lists_three_qc_items(self):
        text = read(N1)
        # 3 hạng mục chốt ở interview câu 1 (đáp A).
        self.assertIn("test", text.lower())
        for phrase in ("Definition of Done", "biên", "đường lỗi"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_law_docs_state_fix_round_cap(self):
        for path in LAW_DOCS:
            with self.subTest(doc=os.path.relpath(path, ROOT)):
                self.assertIn(FIX_CAP, read(path))

    def test_law_docs_state_fix_round_heading(self):
        for path in LAW_DOCS:
            with self.subTest(doc=os.path.relpath(path, ROOT)):
                self.assertIn(FIX_HEADING, read(path))


class QuickQcPhaseTableTest(unittest.TestCase):
    """N3: PHASE_TABLE là nguồn sự thật máy-đọc cho lane quick."""

    def test_quick_checklist_mentions_qc(self):
        items = [c for c in tdq_state.PHASE_TABLE["quick"]["checklist"] if "QC" in c]
        self.assertGreaterEqual(len(items), 2, tdq_state.PHASE_TABLE["quick"]["checklist"])

    def test_quick_cmd_offers_no_qc_flag(self):
        self.assertIn("[--no-qc]", tdq_state.PHASE_TABLE["quick"]["cmd"])

    def test_default_state_has_skip_field_without_duplicate(self):
        state = tdq_state.default_state()
        self.assertIs(state["quick_qc_skipped"], False)
        # quick_approved_by đã giữ nguyên văn cùng câu duyệt — field _by riêng là trùng.
        self.assertNotIn("quick_qc_skipped_by", state)


class QuickQcApproveCliTest(unittest.TestCase):
    """N3: cờ --no-qc là đường opt-out DUY NHẤT, và phải để lại dấu vết."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)
        run_state_cli(self.cwd, "init", "2026-08-07-demo", "quick")

    def test_approve_quick_no_qc_records_skip(self):
        said = "duyệt quick không QC"
        rc, _, _ = run_state_cli(self.cwd, "approve", "quick", "--no-qc", "--by", said)
        self.assertEqual(rc, 0)
        state = tdq_state.load(self.cwd)
        self.assertIs(state["quick_qc_skipped"], True)
        self.assertEqual(state["quick_approved_by"], said)

    def test_approve_quick_no_qc_logs_timestamped_line(self):
        rc, _, err = run_state_cli(self.cwd, "approve", "quick", "--no-qc",
                                   "--by", "duyệt quick không QC")
        self.assertEqual(rc, 0)
        # timestamp chỉ ra từ _info/_warn → stderr; dòng ✅ stdout không có timestamp.
        self.assertRegex(err, r"\[\d{4}-\d{2}-\d{2}T")

    def test_approve_quick_no_qc_requires_by(self):
        """Quyết định 9: bỏ QC vẫn phải để lại nguyên văn câu user."""
        rc, _, err = run_state_cli(self.cwd, "approve", "quick", "--no-qc")
        self.assertNotEqual(rc, 0)
        self.assertIn("--by", err)
        self.assertIs(tdq_state.load(self.cwd)["quick_qc_skipped"], False)

    def test_approve_spec_rejects_no_qc(self):
        """Phải từ chối bằng thông báo NÊU TÊN cờ, không phải bằng USAGE chung."""
        rc, _, err = run_state_cli(self.cwd, "approve", "spec", "--no-qc", "--by", "x")
        self.assertNotEqual(rc, 0)
        first = err.splitlines()[0] if err else ""
        self.assertIn("--no-qc", first)
        self.assertIn("quick", first)


class QuickQcPortableParityTest(unittest.TestCase):
    """N4 + N5: bản cho agent ngoài Claude Code phải nói cùng luật."""

    def test_portable_quick_lane_parity(self):
        plugin, portable = read(N1), read(N4_QUICK)
        for phrase in (FIX_CAP, FIX_HEADING, "## QC ở quick"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, plugin)
                self.assertIn(phrase, portable)

    def test_portable_phases_doc_regenerated(self):
        """N5 là doc tự sinh — nội dung phải khớp render_phases_md() từng ký tự."""
        self.assertEqual(read(N5_PLUGIN), tdq_state.render_phases_md(plugin_root=True))
        self.assertEqual(read(N5_PORTABLE), tdq_state.render_phases_md())


class QuickQcApprovalHintTest(unittest.TestCase):
    """Hook phải mách user đúng biến thể, và không lọc nó thành câu hỏi."""

    def test_hook_hint_offers_no_qc_variant(self):
        self.assertIn("không QC", _common.APPROVE_HINTS["quick"])

    def test_hook_reads_no_qc_sentence_as_approval(self):
        self.assertTrue(
            prompt_context.looks_like_approval("duyệt quick không QC", "quick"))


if __name__ == "__main__":
    unittest.main()
