"""`approve spec` runs doc_lint R14 on spec_file: a numeric threshold without a prior
measurement and a fallback blocks the approval, unless the user passes --bo-qua-do."""
import os
import re
import tempfile
import unittest

from helper import read_state, run_state_cli
import tdq_state

SLUG_MOI = "2026-10-03-0800-demo-moi"
SLUG_CU = "2026-09-01-1000-demo-cu"

HEADER = ("| ID | Mục | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |\n"
          "|---|---|---|---|---|\n")
DONG_THIEU = "| Q1 | Installer | bộ cài ≤ 200 MB | — | — |\n"
DONG_DU = "| Q1 | Installer | bộ cài ≤ 200 MB | 180 MB (đo 2026-10-02) | tách gói phụ |\n"
BANG_CU = ("| ID | Mục | Điều kiện PASS |\n"
           "|---|---|---|\n"
           "| Q1 | Installer | bộ cài ≤ 200 MB |\n")


def _spec(bang):
    return "# Spec demo\n\n## 1. Mục tiêu\n\nDemo.\n\n## 6. Định nghĩa xong\n\n" + bang + "\n"


class _Base(unittest.TestCase):
    slug = SLUG_MOI

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def dung(self, noi_dung, slug=None):
        slug = slug or self.slug
        rc, _, err = run_state_cli(self.cwd, "init", slug, "full")
        self.assertEqual(rc, 0, err)
        rc, _, err = run_state_cli(self.cwd, "set", "phase=spec")
        self.assertEqual(rc, 0, err)
        rel = f"docs/tdq/spec/{slug}.md"
        os.makedirs(os.path.join(self.cwd, "docs", "tdq", "spec"), exist_ok=True)
        with open(os.path.join(self.cwd, rel), "w", encoding="utf-8") as f:
            f.write(noi_dung)
        rc, _, err = run_state_cli(self.cwd, "set", f"spec_file={rel}")
        self.assertEqual(rc, 0, err)
        return rel


class TestDefaultState(unittest.TestCase):
    def test_default_state_co_khoa_bo_qua_do(self):
        state = tdq_state.default_state()
        self.assertIn("spec_bo_qua_do", state)
        self.assertIsNone(state["spec_bo_qua_do"])


class TestApproveDoTruoc(_Base):
    def test_tu_choi_khi_thieu_do_truoc(self):
        rel = self.dung(_spec(HEADER + DONG_THIEU))
        rc, _, err = run_state_cli(self.cwd, "approve", "spec", "--by", "duyệt")
        self.assertNotEqual(rc, 0)
        self.assertIn("[R14]", err)
        self.assertIn(rel, err)
        self.assertIn("--bo-qua-do", err)
        state = read_state(self.cwd)
        self.assertFalse(state["spec_approved"])
        self.assertIsNone(state["spec_approved_at"])
        self.assertIsNone(state.get("spec_bo_qua_do"))

    def test_tu_choi_moi_hang_mot_dong(self):
        bang = HEADER + DONG_THIEU + "| Q2 | Tốc độ | mở app < 3 giây | | |\n"
        self.dung(_spec(bang))
        rc, _, err = run_state_cli(self.cwd, "approve", "spec", "--by", "ok")
        self.assertNotEqual(rc, 0)
        self.assertEqual(len(re.findall(r"\[R14\]", err)), 2, err)

    def test_qua_khi_hang_du_cot(self):
        self.dung(_spec(HEADER + DONG_DU))
        rc, out, err = run_state_cli(self.cwd, "approve", "spec", "--by", "duyệt spec")
        self.assertEqual(rc, 0, err)
        self.assertNotIn("[R14]", err)
        state = read_state(self.cwd)
        self.assertTrue(state["spec_approved"])
        self.assertIsNone(state.get("spec_bo_qua_do"))

    def test_bo_qua_do_van_duyet_va_luu_ly_do(self):
        self.dung(_spec(HEADER + DONG_THIEU))
        rc, _, err = run_state_cli(self.cwd, "approve", "spec", "--by", "duyệt",
                                   "--bo-qua-do", "user accepts")
        self.assertEqual(rc, 0, err)
        state = read_state(self.cwd)
        self.assertTrue(state["spec_approved"])
        self.assertEqual(state["spec_approved_by"], "duyệt")
        bq = state["spec_bo_qua_do"]
        self.assertEqual(bq["ly_do"], "user accepts")
        self.assertTrue(bq["at"])
        self.assertEqual(bq["so_loi"], 1)

    def test_bo_qua_do_dat_truoc_by_van_parse_dung(self):
        self.dung(_spec(HEADER + DONG_THIEU))
        rc, _, err = run_state_cli(self.cwd, "approve", "spec", "--bo-qua-do", "ok để sau",
                                   "--by", "duyệt")
        self.assertEqual(rc, 0, err)
        state = read_state(self.cwd)
        self.assertEqual(state["spec_approved_by"], "duyệt")
        self.assertEqual(state["spec_bo_qua_do"]["ly_do"], "ok để sau")

    def test_bo_qua_do_ly_do_rong_bi_tu_choi(self):
        self.dung(_spec(HEADER + DONG_THIEU))
        for rong in ("", "   "):
            with self.subTest(ly_do=repr(rong)):
                rc, _, _ = run_state_cli(self.cwd, "approve", "spec", "--by", "duyệt",
                                         "--bo-qua-do", rong)
                self.assertNotEqual(rc, 0)
                state = read_state(self.cwd)
                self.assertFalse(state["spec_approved"])
                self.assertIsNone(state.get("spec_bo_qua_do"))

    def test_bo_qua_do_thieu_gia_tri_bi_tu_choi(self):
        self.dung(_spec(HEADER + DONG_THIEU))
        rc, _, _ = run_state_cli(self.cwd, "approve", "spec", "--bo-qua-do")
        self.assertNotEqual(rc, 0)
        self.assertFalse(read_state(self.cwd)["spec_approved"])

    def test_cu_spec_cu_khong_cot_van_duyet(self):
        self.dung(_spec(BANG_CU), slug=SLUG_CU)
        rc, _, err = run_state_cli(self.cwd, "approve", "spec", "--by", "duyệt")
        self.assertEqual(rc, 0, err)
        self.assertNotIn("[R14]", err)
        state = read_state(self.cwd)
        self.assertTrue(state["spec_approved"])
        self.assertIsNone(state.get("spec_bo_qua_do"))

    def test_cu_plan_khong_bi_cham(self):
        # The gate is spec-only: approving the plan never runs R14.
        self.dung(_spec(HEADER + DONG_DU))
        rc, _, err = run_state_cli(self.cwd, "approve", "spec", "--by", "ok")
        self.assertEqual(rc, 0, err)
        rc, _, err = run_state_cli(self.cwd, "approve", "plan", "--by", "ok", "--mode", "inline")
        self.assertEqual(rc, 0, err)
        self.assertNotIn("[R14]", err)

    def test_spec_file_khong_doc_duoc_van_duyet(self):
        self.dung(_spec(HEADER + DONG_THIEU))
        os.remove(os.path.join(self.cwd, "docs", "tdq", "spec", f"{SLUG_MOI}.md"))
        rc, _, err = run_state_cli(self.cwd, "approve", "spec", "--by", "ok")
        self.assertEqual(rc, 0, err)
        self.assertTrue(read_state(self.cwd)["spec_approved"])


class TestLog(_Base):
    ISO = r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}\]"

    def test_log_tu_choi_co_dong_iso(self):
        self.dung(_spec(HEADER + DONG_THIEU))
        _, _, err = run_state_cli(self.cwd, "approve", "spec", "--by", "ok")
        self.assertRegex(err, self.ISO + r".*R14")

    def test_log_bo_qua_co_dong_iso(self):
        self.dung(_spec(HEADER + DONG_THIEU))
        _, _, err = run_state_cli(self.cwd, "approve", "spec", "--by", "ok",
                                  "--bo-qua-do", "user accepts")
        self.assertRegex(err, self.ISO + r".*--bo-qua-do")

    def test_log_tat_bang_tdq_log_0(self):
        self.dung(_spec(HEADER + DONG_THIEU))
        cu = os.environ.get("TDQ_LOG")
        os.environ["TDQ_LOG"] = "0"
        try:
            rc, _, err = run_state_cli(self.cwd, "approve", "spec", "--by", "ok",
                                       "--bo-qua-do", "user accepts")
        finally:
            if cu is None:
                os.environ.pop("TDQ_LOG", None)
            else:
                os.environ["TDQ_LOG"] = cu
        self.assertEqual(rc, 0)
        self.assertNotRegex(err, self.ISO)
        self.assertTrue(read_state(self.cwd)["spec_approved"])


if __name__ == "__main__":
    unittest.main()
