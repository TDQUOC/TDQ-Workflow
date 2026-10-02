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
# 2026-10-02: luật tick, QC của lane này và vòng fix tách sang file em TẦNG 1 `quick-lane-qc.md`
# — không phần nào cần ở bước 1, nên nạp chúng lúc mở lane là trả tiền trước cho ba việc chưa tới
# (đo: 1.120 token trong một file 4.356). Bất biến vẫn là "luật phải nêu ĐỦ ở nguồn N1", nên N1 nay
# là CẶP file, và phép kiểm đọc cả hai.
N1_QC = os.path.join(ROOT, "skills", "tdq-intake", "references", "quick-lane-qc.md")
N2 = os.path.join(ROOT, "skills", "tdq-intake", "SKILL.md")
N4_PHASES = os.path.join(ROOT, "skills", "tdq-conventions", "references", "phases.md")

# Luật vòng fix phát biểu ĐỦ ở N1; từ Đ3 (0.16.0) N2 chỉ còn dòng trỏ sang N1 để thân
# skill khỏi nạp nhánh quick mỗi lần gọi. Bất biến "luật không được biến mất" vẫn kiểm:
# N1 phải nêu đủ, N2 phải trỏ đúng chỗ (test_skill_body_points_to_quick_lane).
LAW_DOCS = (N1, N1_QC)

# Từ 2026-08-22 luật viết tiếng Anh; nhận cả hai cách viết các mốc dưới đây.
FIX_CAP = ("3-round cap", "trần 3 vòng")
FIX_HEADING = ("QC vòng N — fix",)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


class QuickQcDocTest(unittest.TestCase):
    """N1: quick-lane.md phải định nghĩa QC, không chỉ nói 'chạy validate'."""

    def test_quick_lane_has_qc_section(self):
        text = read(N1) + read(N1_QC)
        self.assertTrue(any(m in text for m in
                            ("## QC in the express pipeline", "## QC ở chế độ nhanh")))

    def test_quick_lane_ties_qc_items_to_dod(self):
        # Luật mới: số hạng mục QC bằng số dòng DoD, không phải danh sách cố định.
        # 2026-09-23: so khớp sau khi gộp khoảng trắng — luật nằm ở NỘI DUNG câu, còn chỗ ngắt
        # dòng đổi mỗi lần ai đó sửa câu bên cạnh, và một test đỏ vì xuống dòng là test nhiễu.
        text = read(N1) + read(N1_QC)
        goi = " ".join(text.split())
        self.assertTrue(any(m in goi for m in
                            ("as many items as the mini-plan has DoD lines",
                             "số hạng mục bằng số dòng DoD")))
        self.assertNotIn("3 hạng mục", text)

    def test_skill_body_points_to_quick_lane(self):
        # N2 không còn chép luật, nhưng BẮT BUỘC trỏ sang mục các bước thi hành ở N1.
        # 2026-09-01: chín bước → mười, do lane nhanh có thêm bước ghi kết quả phân tích
        # vào brief (pha `quick_analyze`, không kèm cổng duyệt).
        text = read(N2)
        self.assertIn("references/quick-lane.md", text)
        self.assertTrue(any(m in text for m in
                            ("The ten execution steps", "Mười bước thi hành")))

    def test_law_docs_rerun_only_failed_items(self):
        # Vòng fix không chạy lại toàn bộ nữa — chỉ hạng mục FAIL + hạng mục bị ảnh hưởng.
        # 2026-10-02: hỏi trên CẶP file, không hỏi từng file. Luật này phát biểu ở `quick-lane-qc.md`
        # sau khi tách, và bắt mỗi file phải tự nêu đủ sẽ buộc chép lại — đúng thứ việc tách đi cắt.
        van = "".join(read(p) for p in LAW_DOCS)
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

    def test_quick_cmd_khong_con_co_no_qc(self):
        """2026-09-23: cờ bỏ QC được thay bằng thang mức `muc_qc`, một cơ chế duy nhất."""
        self.assertNotIn("--no-qc", tdq_state.PHASE_TABLE["quick"]["cmd"])

    def test_quick_checklist_nhac_muc_qc(self):
        joined = " ".join(tdq_state.PHASE_TABLE["quick"]["checklist"])
        self.assertIn("muc_qc", joined, "lane quick phải biết hỏi mức QC")
        self.assertNotIn("--no-qc", joined)

    def test_default_state_khong_con_khoa_bo_qc(self):
        state = tdq_state.default_state()
        self.assertNotIn("quick_qc_skipped", state,
                         "khoá cũ phải biến mất cùng cờ, không để lại field chết")
        self.assertEqual(state["muc_qc"], "full")


class QuickQcApproveCliTest(unittest.TestCase):
    """2026-09-23: cờ --no-qc đã gỡ. Lệnh cũ phải chết CÓ CHỈ ĐƯỜNG — im lặng chấp nhận là tệ
    nhất (user tưởng đã bỏ QC), mà báo lỗi cụt cũng tệ (user không biết đi đường nào)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)
        run_state_cli(self.cwd, "init", "2026-08-07-0900-demo", "quick")

    def test_approve_quick_co_cu_chet_co_chi_duong(self):
        rc, _, err = run_state_cli(self.cwd, "approve", "quick", "--no-qc",
                                   "--by", "duyệt quick không QC")
        self.assertNotEqual(rc, 0)
        first = err.splitlines()[0] if err else ""
        self.assertIn("--no-qc", first, "thông báo phải nêu tên cờ user vừa gõ")
        self.assertIn("muc_qc=off", first, "và phải chỉ đúng đường thay thế")

    def test_approve_quick_co_cu_khong_ghi_gi_vao_state(self):
        run_state_cli(self.cwd, "approve", "quick", "--no-qc", "--by", "x")
        state = tdq_state.load(self.cwd)
        self.assertIs(state["quick_approved"], False, "lệnh chết không được ghi nửa vời")
        self.assertNotIn("quick_qc_skipped", state)

    def test_approve_quick_binh_thuong_van_chay(self):
        said = "duyệt nhanh"
        rc, _, err = run_state_cli(self.cwd, "approve", "quick", "--by", said)
        self.assertEqual(rc, 0, err)
        state = tdq_state.load(self.cwd)
        self.assertIs(state["quick_approved"], True)
        self.assertEqual(state["quick_approved_by"], said)

    def test_approve_spec_cung_tu_choi_co_cu(self):
        rc, _, err = run_state_cli(self.cwd, "approve", "spec", "--no-qc", "--by", "x")
        self.assertNotEqual(rc, 0)
        self.assertIn("--no-qc", err.splitlines()[0] if err else "")


class QuickQcPhasesDocTest(unittest.TestCase):
    """N4: phases.md là doc tự sinh — khớp render_phases_md() từng ký tự."""

    def test_phases_doc_regenerated(self):
        self.assertEqual(read(N4_PHASES), tdq_state.render_phases_md(plugin_root=True))


class QuickQcApprovalHintTest(unittest.TestCase):
    """Hook phải mách user đúng biến thể, và không lọc nó thành câu hỏi."""

    def test_hook_hint_khong_moi_bo_qc(self):
        """Quyết định 2026-09-23: `off` tồn tại nhưng KHÔNG bao giờ được bày ra. Lời mời bỏ QC
        nằm ngay trong dòng nhắc là bày ra ở chỗ dễ thấy nhất."""
        hint = _common.APPROVE_HINTS["quick"]
        self.assertNotIn("skip QC", hint)
        self.assertNotIn("no QC", hint)

    def test_hook_reads_no_qc_sentence_as_approval(self):
        self.assertTrue(
            prompt_context.looks_like_approval("duyệt quick không QC", "quick"))


if __name__ == "__main__":
    unittest.main()
