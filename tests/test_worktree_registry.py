"""Khoá hành vi của sổ worktree — thứ giữ cho worktree không bị bỏ quên ăn disk.

Sổ là NGUỒN SỰ THẬT DUY NHẤT về worktree đang mở: `tdq_team.py` ghi vào, `tdq_state.py`
đọc để chặn phase, hook đọc để nhắc. Vì ba nơi cùng đọc, schema lệch một trường là ba nơi
lệch theo mà không phép kiểm nào bắt được — nên schema bị khoá cứng ở đây.
"""
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import tdq_worktree_registry as so  # noqa: E402


class RepoTam(unittest.TestCase):
    """Mỗi test một thư mục project riêng — cấm chạm sổ thật của repo."""

    def setUp(self):
        self.tam = tempfile.TemporaryDirectory()
        self.project = self.tam.name
        os.makedirs(os.path.join(self.project, "docs", "tdq"), exist_ok=True)

    def tearDown(self):
        self.tam.cleanup()

    def _mo(self, ma="T1.1", slug="2026-01-01-0000-thu", tao_luc="2026-01-01T00:00:00"):
        return so.mo_dong(self.project, slug=slug, ma_task=ma,
                          nhanh=f"tdq/{slug}/{ma.lower()}",
                          duong_dan=os.path.join(self.project, ".tdq-worktrees",
                                                 slug, ma.lower()),
                          tao_luc=tao_luc)


class SchemaTest(RepoTam):

    def test_mo_dong_ghi_du_bay_truong(self):
        ban_ghi = self._mo()
        self.assertEqual(sorted(ban_ghi), sorted(so.TRUONG))
        self.assertEqual(len(so.TRUONG), 7)

    def test_doc_lai_ra_dung_dong_vua_mo(self):
        self._mo()
        dong = so.doc(self.project)["dong"]
        self.assertEqual(len(dong), 1)
        self.assertEqual(dong[0]["ma_task"], "T1.1")
        self.assertEqual(dong[0]["trang_thai"], "mo")
        self.assertIsNone(dong[0]["dong_luc"])

    def test_dong_dong_doi_trang_thai_va_dong_moc_thoi_gian(self):
        self._mo()
        so.dong_dong(self.project, "2026-01-01-0000-thu", "T1.1", ly_do="merged")
        dong = so.doc(self.project)["dong"][0]
        self.assertEqual(dong["trang_thai"], "dong")
        self.assertTrue(dong["dong_luc"], "đóng dòng mà không ghi mốc thời gian")

    def test_mo_hai_lan_cung_task_thi_bao_loi(self):
        self._mo()
        with self.assertRaises(so.LoiSo):
            self._mo()

    def test_dong_mo_chi_tra_dong_con_mo(self):
        self._mo("T1.1")
        self._mo("T1.2")
        so.dong_dong(self.project, "2026-01-01-0000-thu", "T1.1", ly_do="merged")
        con = so.dong_mo(self.project)
        self.assertEqual([d["ma_task"] for d in con], ["T1.2"])

    def test_so_song_xuyen_request_khong_bi_slug_khac_xoa(self):
        """Đúng lý do sổ tách khỏi state.json: `init` xoá state, sổ thì không."""
        self._mo("T1.1", slug="slug-cu")
        self._mo("T1.1", slug="slug-moi")
        self.assertEqual(len(so.doc(self.project)["dong"]), 2)


class FileHongTest(RepoTam):
    """Sổ hỏng KHÔNG được phép kéo theo cả workflow — hook cũng đọc file này."""

    def _lam_hong(self):
        duong = so.duong_so(self.project)
        os.makedirs(os.path.dirname(duong), exist_ok=True)
        with open(duong, "w", encoding="utf-8") as f:
            f.write("{ đây không phải json")
        return duong

    def test_doc_file_hong_tra_so_rong(self):
        self._lam_hong()
        self.assertEqual(so.doc(self.project)["dong"], [])

    def test_doc_file_hong_khong_ghi_de(self):
        duong = self._lam_hong()
        goc = open(duong, encoding="utf-8").read()
        so.doc(self.project)
        so.dong_mo(self.project)
        self.assertEqual(open(duong, encoding="utf-8").read(), goc,
                         "đọc sổ hỏng mà ghi đè lên nó = mất dữ liệu người dùng")

    def test_ghi_len_so_hong_thi_bao_loi_chu_khong_am_tham_mat(self):
        self._lam_hong()
        with self.assertRaises(so.LoiSo):
            self._mo()

    def test_thieu_file_khong_phai_loi(self):
        self.assertEqual(so.doc(self.project)["dong"], [])
        self.assertEqual(so.dong_mo(self.project), [])


class RenderTest(RepoTam):

    def test_render_hai_lan_giong_het_nhau(self):
        self._mo("T1.1")
        self._mo("T1.2")
        a = so.render_md(so.doc(self.project))
        b = so.render_md(so.doc(self.project))
        self.assertEqual(a, b)

    def test_render_khong_phu_thuoc_thu_tu_ghi(self):
        """Sổ xáo thứ tự mà bản .md đổi theo thì mọi diff đều nhiễu."""
        self._mo("T1.2")
        self._mo("T1.1")
        xuoi = so.render_md(so.doc(self.project))
        du_lieu = so.doc(self.project)
        du_lieu["dong"].reverse()
        self.assertEqual(so.render_md(du_lieu), xuoi)

    def test_ghi_md_tao_dung_file(self):
        self._mo()
        duong = so.ghi_md(self.project)
        self.assertTrue(os.path.exists(duong))
        noi_dung = open(duong, encoding="utf-8").read()
        self.assertIn("T1.1", noi_dung)

    def test_so_rong_van_render_ra_file_hop_le(self):
        duong = so.ghi_md(self.project)
        self.assertTrue(os.path.exists(duong))


class GoiYTest(unittest.TestCase):
    """Tập lý do là tập ĐÓNG. Lý do lạ phải nổ, vì khối rỗng = worktree bị quên."""

    def test_moi_ly_do_deu_co_it_nhat_mot_phuong_an(self):
        for ly_do, phuong_an in so.LY_DO_CHAN.items():
            with self.subTest(ly_do=ly_do):
                self.assertTrue(phuong_an["phuong_an"],
                                f"{ly_do} không có phương án nào")

    def test_moi_phuong_an_deu_co_lenh_chay_duoc(self):
        for ly_do, phuong_an in so.LY_DO_CHAN.items():
            for pa in phuong_an["phuong_an"]:
                with self.subTest(ly_do=ly_do, pa=pa["mo_ta"]):
                    self.assertIn("lenh", pa)

    def test_ly_do_ngoai_tap_thi_no(self):
        with self.assertRaises(so.LoiSo):
            so.khoi_goi_y([{"ma_task": "T1.1", "duong_dan": "/x",
                            "nhanh": "n", "ly_do": "khong-ton-tai"}])

    def test_khoi_goi_y_in_du_task_va_lenh(self):
        khoi = so.khoi_goi_y([
            {"ma_task": "T1.1", "duong_dan": "/x/t1.1", "nhanh": "tdq/s/t1.1",
             "ly_do": "ban", "chi_tiet": "3 file"},
        ])
        self.assertIn("T1.1", khoi)
        self.assertIn("/x/t1.1", khoi)
        self.assertIn("3 file", khoi)
        # Đường dẫn thật phải được thay vào lệnh, không để lại placeholder.
        self.assertNotIn("{duong_dan}", khoi)

    def test_khong_con_gi_thi_khong_in_khoi(self):
        self.assertEqual(so.khoi_goi_y([]), "")


class LogTest(RepoTam):

    def test_mo_dong_ghi_mot_dong_log(self):
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            self._mo()
        self.assertIn("T1.1", buf.getvalue())

    def test_tdq_log_0_tat_log(self):
        import io
        import contextlib
        buf = io.StringIO()
        cu = os.environ.get("TDQ_LOG")
        os.environ["TDQ_LOG"] = "0"
        try:
            with contextlib.redirect_stderr(buf):
                self._mo()
        finally:
            if cu is None:
                del os.environ["TDQ_LOG"]
            else:
                os.environ["TDQ_LOG"] = cu
        self.assertEqual(buf.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
