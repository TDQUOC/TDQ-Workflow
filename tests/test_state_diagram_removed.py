"""Bộ máy sơ đồ đã bị gỡ khỏi `tdq_state.py` — chỉ còn lối báo lỗi có nghĩa.

Bất biến khoá ở đây:
1. Module không còn khoá `diagrams`, không còn hàm `diagram_entries` /
   `diagram_pending` / `_diagram_register`, và `diagram` không còn là đích duyệt.
2. State cũ mang khoá `diagrams` vẫn nạp được; ghi lại state thì khoá biến mất.
3. Ba lệnh cũ (`approve diagram`, `diagram add`, `diagram list`) thoát khác 0 và
   nói rõ pha đã bị gỡ, chứ không rơi vào lỗi "lệnh lạ" chung chung.
4. Bảng trạng thái không còn dòng `Diagrams`, usage không còn chữ `diagram`.
"""
import json
import os
import tempfile
import unittest

from helper import run_state_cli, tdq_state


def doc_state(cwd):
    with open(os.path.join(cwd, "docs", "tdq", "state.json"), encoding="utf-8") as f:
        return json.load(f)


def ghi_state(cwd, state):
    with open(os.path.join(cwd, "docs", "tdq", "state.json"), "w",
               encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False)


def mo_request(cwd):
    ma, _, err = run_state_cli(cwd, "init", "2026-09-01-1800-bo-so-do", "chuyen-sau")
    assert ma == 0, err


class ApiDaGoTest(unittest.TestCase):
    def test_module_khong_con_ham_so_do(self):
        for ten in ("DIAGRAM_KEY", "diagram_entries", "diagram_pending",
                    "_diagram_register", "_heal_diagrams", "_diagram_id",
                    "_cli_approve_diagram", "_cli_diagram"):
            self.assertFalse(hasattr(tdq_state, ten),
                             f"{ten} lẽ ra đã bị gỡ khỏi tdq_state")

    def test_diagram_khong_con_la_dich_duyet(self):
        self.assertNotIn("diagram", tdq_state.APPROVE_TARGETS)

    def test_usage_khong_con_chu_diagram(self):
        self.assertNotIn("diagram", tdq_state.USAGE)


class StateCuTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        self.addCleanup(self._tmp.cleanup)
        mo_request(self.cwd)
        state = doc_state(self.cwd)
        state["diagrams"] = [{"file": "docs/tdq/mind-map/dang-nhap.md",
                              "approved": False, "approved_at": None,
                              "approved_by": None}]
        ghi_state(self.cwd, state)

    def test_state_cu_van_doc_duoc(self):
        ma, out, err = run_state_cli(self.cwd, "next")
        self.assertEqual(ma, 0, err)
        self.assertNotIn("Diagrams", out)

    def test_ghi_lai_thi_khoa_diagrams_bien_mat(self):
        ma, _, err = run_state_cli(self.cwd, "set", "spec_file=docs/tdq/spec/x.md")
        self.assertEqual(ma, 0, err)
        self.assertNotIn("diagrams", doc_state(self.cwd))

    def test_init_moi_khong_sinh_khoa_diagrams(self):
        mo_request(self.cwd)
        self.assertNotIn("diagrams", doc_state(self.cwd))


class LenhCuTest(unittest.TestCase):
    """Lệnh cũ phải báo đúng nguyên nhân, không phải lỗi cú pháp chung chung."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        self.addCleanup(self._tmp.cleanup)
        mo_request(self.cwd)

    def _kiem_lenh_cu(self, *argv):
        ma, out, err = run_state_cli(self.cwd, *argv)
        self.assertNotEqual(ma, 0, f"{argv} lẽ ra phải thoát khác 0")
        loi = (out + err).lower()
        self.assertIn("removed", loi, f"{argv}: thông điệp phải nói pha đã bị gỡ")
        return loi

    def test_lenh_cu_approve_diagram(self):
        self._kiem_lenh_cu("approve", "diagram", "docs/tdq/mind-map/x.md")

    def test_lenh_cu_diagram_add(self):
        self._kiem_lenh_cu("diagram", "add", "docs/tdq/mind-map/x.md")

    def test_lenh_cu_diagram_list(self):
        self._kiem_lenh_cu("diagram", "list")


class BangTrangThaiTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        self.addCleanup(self._tmp.cleanup)
        mo_request(self.cwd)

    def test_bang_trang_thai_khong_con_dong_diagrams(self):
        for lenh in (("next",), ("next", "--brief")):
            ma, out, err = run_state_cli(self.cwd, *lenh)
            self.assertEqual(ma, 0, err)
            self.assertNotIn("Diagrams", out + err)

    def test_cong_plan_khong_doi_so_do(self):
        for pair in ("phase=spec", "spec_file=docs/tdq/spec/x.md"):
            ma, _, err = run_state_cli(self.cwd, "set", pair)
            self.assertEqual(ma, 0, err)
        ma, _, err = run_state_cli(self.cwd, "approve", "spec", "--by", "duyệt spec")
        self.assertEqual(ma, 0, err)
        ma, out, err = run_state_cli(self.cwd, "set", "phase=plan")
        self.assertEqual(ma, 0, f"{out}{err}")


if __name__ == "__main__":
    unittest.main()
