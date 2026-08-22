"""Lane quick: QC bám DoD (mặc định BẬT) + vòng fix trần 3 vòng.

Khoá cứng 4 nguồn sự thật phải phát biểu CÙNG một luật:
  N1 skills/tdq-intake/references/quick-lane.md
  N2 skills/tdq-intake/SKILL.md
  N3 scripts/tdq_state.py  (PHASE_TABLE["quick"], default_state, _parse_approve_args)
  N4 phases.md             (doc TỰ SINH từ PHASE_TABLE — không sửa tay)
Spec: docs/tdq/spec/2026-08-07-0900-siet-qc-lane-quick.md
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
N4_PHASES = os.path.join(ROOT, "skills", "tdq-conventions", "references", "phases.md")

# Luật vòng fix phát biểu ĐỦ ở N1; từ Đ3 (0.16.0) N2 chỉ còn dòng trỏ sang N1 để thân
# skill khỏi nạp nhánh quick mỗi lần gọi. Bất biến "luật không được biến mất" vẫn kiểm:
# N1 phải nêu đủ, N2 phải trỏ đúng chỗ (test_skill_body_points_to_quick_lane).
LAW_DOCS = (N1,)

# Từ 2026-08-22 luật viết tiếng Anh; nhận cả hai cách viết các mốc dưới đây.
FIX_CAP = ("3-round cap", "trần 3 vòng")
FIX_HEADING = ("QC vòng N — fix",)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


class QuickQcDocTest(unittest.TestCase):
    """N1: quick-lane.md phải định nghĩa QC, không chỉ nói 'chạy validate'."""

    def test_quick_lane_has_qc_section(self):
        text = read(N1)
        self.assertTrue(any(m in text for m in
                            ("## QC in the express pipeline", "## QC ở chế độ nhanh")))

    def test_quick_lane_ties_qc_items_to_dod(self):
        # Luật mới: số hạng mục QC bằng số dòng DoD, không phải danh sách cố định.
        text = read(N1)
        self.assertTrue(any(m in text for m in
                            ("as many items as the mini-plan\nhas DoD lines",
                             "số hạng mục bằng số dòng DoD")))
        self.assertNotIn("3 hạng mục", text)

    def test_skill_body_points_to_quick_lane(self):
        # N2 không còn chép luật, nhưng BẮT BUỘC trỏ sang mục chín bước ở N1.
        text = read(N2)
        self.assertIn("references/quick-lane.md", text)
        self.assertTrue(any(m in text for m in
                            ("The nine execution steps", "Chín bước thi hành")))

    def test_law_docs_rerun_only_failed_items(self):
        # Vòng fix không chạy lại toàn bộ nữa — chỉ hạng mục FAIL + hạng mục bị ảnh hưởng.
        for path in LAW_DOCS:
            with self.subTest(doc=os.path.relpath(path, ROOT)):
                van = read(path)
                self.assertTrue(any(m in van for m in
                                    ("re-run the items that FAILed", "hạng mục đã FAIL")))

    def test_law_docs_state_fix_round_cap(self):
        for path in LAW_DOCS:
            with self.subTest(doc=os.path.relpath(path, ROOT)):
                van = read(path)
                self.assertTrue(any(m in van for m in FIX_CAP))

    def test_law_docs_state_fix_round_heading(self):
        for path in LAW_DOCS:
            with self.subTest(doc=os.path.relpath(path, ROOT)):
                van = read(path)
                self.assertTrue(any(m in van for m in FIX_HEADING))


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
        run_state_cli(self.cwd, "init", "2026-08-07-0900-demo", "quick")

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


class QuickQcPhasesDocTest(unittest.TestCase):
    """N4: phases.md là doc tự sinh — khớp render_phases_md() từng ký tự."""

    def test_phases_doc_regenerated(self):
        self.assertEqual(read(N4_PHASES), tdq_state.render_phases_md(plugin_root=True))


class QuickQcApprovalHintTest(unittest.TestCase):
    """Hook phải mách user đúng biến thể, và không lọc nó thành câu hỏi."""

    def test_hook_hint_offers_no_qc_variant(self):
        self.assertIn("no QC", _common.APPROVE_HINTS["quick"])

    def test_hook_reads_no_qc_sentence_as_approval(self):
        self.assertTrue(
            prompt_context.looks_like_approval("duyệt quick không QC", "quick"))


if __name__ == "__main__":
    unittest.main()
