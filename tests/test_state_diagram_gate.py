"""Phase `diagram` — danh sách sơ đồ của request và lệnh duyệt TỪNG sơ đồ.

Bất biến của T2.4 (nhóm `danh_sach`):
1. Phase `diagram` có mặt trong `VALID_PHASES`, `PHASE_TABLE`, `PHASE_ORDER`,
   chen đúng giữa `spec` và `plan`.
2. `init` mở request mới thì danh sách sơ đồ là RỖNG; state cũ không có khoá
   vẫn đọc được, khoá bằng None (tương thích ngược).
3. Đăng ký một sơ đồ hai lần không nhân đôi phần tử, không xoá trạng thái duyệt.
4. Duyệt một sơ đồ theo đường dẫn KHÔNG làm sơ đồ khác thành đã duyệt, và ghi
   lại câu duyệt nguyên văn cùng mốc thời gian.
"""
import json
import os
import tempfile
import unittest

from helper import run_state_cli, tdq_state

SO_DO_A = "docs/tdq/mind-map/dang-nhap.md"
SO_DO_B = "docs/tdq/mind-map/mua-hang.md"


def doc_state(cwd):
    with open(os.path.join(cwd, "docs", "tdq", "state.json"), encoding="utf-8") as f:
        return json.load(f)


def danh_sach(cwd):
    return doc_state(cwd).get(tdq_state.DIAGRAM_KEY)


def mo_request(cwd):
    ma, _, err = run_state_cli(cwd, "init", "2026-08-23-1623-so-do", "chuyen-sau")
    assert ma == 0, err
    return ma


class DanhSachSoDoTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        os.makedirs(os.path.join(self.cwd, "docs", "tdq"), exist_ok=True)

    def tearDown(self):
        self._tmp.cleanup()

    # --------------------------------------------------------- phase diagram
    def test_danh_sach_phase_diagram_chen_giua_spec_va_plan(self):
        self.assertIn("diagram", tdq_state.VALID_PHASES)
        self.assertIn("diagram", tdq_state.PHASE_TABLE)
        row = tdq_state.PHASE_TABLE["diagram"]
        for truong in ("entry", "action", "cmd", "checklist", "done_when", "forbidden"):
            with self.subTest(truong=truong):
                self.assertTrue(row.get(truong), f"phase diagram thiếu trường {truong}")
        order = tdq_state.PHASE_ORDER
        self.assertEqual(order.index("diagram"), order.index("spec") + 1)
        self.assertEqual(order.index("plan"), order.index("diagram") + 1)

    def test_danh_sach_set_phase_diagram_duoc_chap_nhan(self):
        mo_request(self.cwd)
        ma, _, err = run_state_cli(self.cwd, "set", "phase=diagram")
        self.assertEqual(ma, 0, err)
        self.assertEqual(doc_state(self.cwd)["phase"], "diagram")

    # ------------------------------------------------- khoá danh sách sơ đồ
    def test_danh_sach_state_cu_thieu_khoa_van_doc_duoc(self):
        """Tương thích ngược: state cũ không có khoá → load bình thường, khoá = None."""
        cu = {"schema_version": 4, "active_request": "2026-08-01-1000-cu",
              "lane": "full", "phase": "spec", "spec_approved": True}
        with open(os.path.join(self.cwd, "docs", "tdq", "state.json"), "w",
                  encoding="utf-8") as f:
            json.dump(cu, f)
        state = tdq_state.load(self.cwd)
        self.assertIsNotNone(state)
        self.assertEqual(state["active_request"], "2026-08-01-1000-cu")
        self.assertIsNone(state[tdq_state.DIAGRAM_KEY],
                          "state cũ phải phân biệt được với danh sách rỗng")
        self.assertIsNone(tdq_state.diagram_entries(state))
        ma, _, err = run_state_cli(self.cwd, "next", "--brief")
        self.assertEqual(ma, 0, err)

    def test_danh_sach_init_tao_danh_sach_rong(self):
        mo_request(self.cwd)
        self.assertEqual(danh_sach(self.cwd), [])
        self.assertEqual(tdq_state.diagram_entries(tdq_state.load(self.cwd)), [])

    def test_danh_sach_dang_ky_so_do(self):
        mo_request(self.cwd)
        ma, _, err = run_state_cli(self.cwd, "diagram", "add", SO_DO_A)
        self.assertEqual(ma, 0, err)
        ds = danh_sach(self.cwd)
        self.assertEqual(len(ds), 1)
        phan_tu = ds[0]
        self.assertEqual(phan_tu["file"], SO_DO_A)
        self.assertFalse(phan_tu["approved"])
        self.assertIsNone(phan_tu["approved_at"])
        self.assertIsNone(phan_tu["approved_by"])

    def test_danh_sach_dang_ky_trung_khong_nhan_doi(self):
        mo_request(self.cwd)
        run_state_cli(self.cwd, "diagram", "add", SO_DO_A)
        run_state_cli(self.cwd, "diagram", "add", "./" + SO_DO_A)
        self.assertEqual(len(danh_sach(self.cwd)), 1)

    def test_danh_sach_dang_ky_trung_khong_xoa_trang_thai_da_duyet(self):
        mo_request(self.cwd)
        run_state_cli(self.cwd, "diagram", "add", SO_DO_A)
        run_state_cli(self.cwd, "approve", "diagram", SO_DO_A, "--by", "ok sơ đồ này")
        run_state_cli(self.cwd, "diagram", "add", SO_DO_A)
        ds = danh_sach(self.cwd)
        self.assertEqual(len(ds), 1)
        self.assertTrue(ds[0]["approved"], "đăng ký lại đã xoá mất trạng thái duyệt")

    # ------------------------------------------------------ duyệt từng cái
    def test_danh_sach_duyet_doc_lap(self):
        """Duyệt một sơ đồ KHÔNG làm sơ đồ còn lại thành đã duyệt."""
        mo_request(self.cwd)
        run_state_cli(self.cwd, "diagram", "add", SO_DO_A)
        run_state_cli(self.cwd, "diagram", "add", SO_DO_B)
        ma, _, err = run_state_cli(self.cwd, "approve", "diagram", SO_DO_A,
                                   "--by", "duyệt sơ đồ đăng nhập")
        self.assertEqual(ma, 0, err)
        theo_file = {p["file"]: p for p in danh_sach(self.cwd)}
        self.assertTrue(theo_file[SO_DO_A]["approved"])
        self.assertFalse(theo_file[SO_DO_B]["approved"],
                         "duyệt một sơ đồ đã lây sang sơ đồ khác")
        self.assertIsNone(theo_file[SO_DO_B]["approved_at"])
        self.assertIsNone(theo_file[SO_DO_B]["approved_by"])

    def test_danh_sach_duyet_ghi_cau_duyet_va_moc_thoi_gian(self):
        mo_request(self.cwd)
        run_state_cli(self.cwd, "diagram", "add", SO_DO_A)
        run_state_cli(self.cwd, "approve", "diagram", SO_DO_A,
                      "--by", "ừ sơ đồ này đúng rồi, làm đi")
        phan_tu = danh_sach(self.cwd)[0]
        self.assertTrue(phan_tu["approved"])
        self.assertEqual(phan_tu["approved_by"], "ừ sơ đồ này đúng rồi, làm đi")
        self.assertTrue(phan_tu["approved_at"], "thiếu mốc thời gian duyệt")

    def test_danh_sach_duyet_khong_dung_cac_cong_khac(self):
        """Duyệt sơ đồ không được bật spec_approved/plan_approved/quick_approved."""
        mo_request(self.cwd)
        run_state_cli(self.cwd, "diagram", "add", SO_DO_A)
        run_state_cli(self.cwd, "approve", "diagram", SO_DO_A, "--by", "ok")
        state = doc_state(self.cwd)
        for khoa in ("spec_approved", "plan_approved", "quick_approved"):
            with self.subTest(khoa=khoa):
                self.assertFalse(state.get(khoa))
        self.assertNotIn("diagram_approved", state)

    def test_danh_sach_duyet_thieu_duong_dan_la_loi_cu_phap(self):
        mo_request(self.cwd)
        ma, _, _ = run_state_cli(self.cwd, "approve", "diagram")
        self.assertEqual(ma, tdq_state.EXIT_SYNTAX)

    def test_danh_sach_lenh_list_in_du_hai_so_do(self):
        mo_request(self.cwd)
        run_state_cli(self.cwd, "diagram", "add", SO_DO_A)
        run_state_cli(self.cwd, "diagram", "add", SO_DO_B)
        run_state_cli(self.cwd, "approve", "diagram", SO_DO_A, "--by", "ok")
        ma, out, err = run_state_cli(self.cwd, "diagram", "list")
        self.assertEqual(ma, 0, err)
        self.assertIn(SO_DO_A, out)
        self.assertIn(SO_DO_B, out)


if __name__ == "__main__":
    unittest.main()
