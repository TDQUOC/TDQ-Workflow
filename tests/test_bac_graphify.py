"""Bậc 7 (đồ thị graphify) phải kiểm bằng HIỆU ỨNG — đồ thị cũ hơn mã nguồn — không kiểm sự tồn tại.

Tách ra từ `test_bac_lumen_hieu_ung.py` ở 0.58.0, khi bậc lumen bị gỡ và thang còn 7 bậc.
Mọi ca đều vá lớp chạm máy thật để suite chạy được trên máy chưa cài gì. Chạy riêng: `-k graphify`.
"""
import os
import shutil
import sys
import tempfile
import time
import unittest
from unittest import mock

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_lsp  # noqa: E402


class Bac7Graphify(unittest.TestCase):
    """Ca `graphify` — tầng bản đồ của bộ tìm kiếm 3 tầng.

    Đo được 2026-09-28: đồ thị của repo này cũ 8 ngày, 34% node (845/2415) trỏ vào một thư mục
    đã bị xoá. Không ai dựng lại, và không ai bị chặn vì không dựng lại — nên thang bậc phải nói.
    """

    def setUp(self):
        self.thu_muc = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.thu_muc, True)

    def _ghi_do_thi(self, tuoi_giay):
        duong = os.path.join(self.thu_muc, "graphify-out")
        os.makedirs(duong, exist_ok=True)
        tep = os.path.join(duong, "graph.json")
        with open(tep, "w", encoding="utf-8") as fh:
            fh.write("{}")
        moc = time.time() - tuoi_giay
        os.utime(tep, (moc, moc))
        return tep

    def test_graphify_thieu_binary_thi_canh_bao_kem_lenh_cai(self):
        with mock.patch.object(tdq_lsp.shutil, "which", return_value=None):
            b = tdq_lsp.bac7_graphify(self.thu_muc)
        self.assertFalse(b.dat)
        self.assertTrue(b.chi_canh_bao, "graphify là lớp bổ trợ — thiếu thì cảnh báo, không chặn")
        self.assertIn("graphify", b.lenh_cai)

    def test_graphify_chua_co_do_thi_thi_canh_bao(self):
        with mock.patch.object(tdq_lsp.shutil, "which", return_value="/usr/bin/graphify"), \
                mock.patch.object(tdq_lsp, "_moc_code_moi_nhat", return_value=time.time()):
            b = tdq_lsp.bac7_graphify(self.thu_muc)
        self.assertFalse(b.dat)
        self.assertIn("extract", b.lenh_cai)

    def test_graphify_do_thi_cu_hon_ma_nguon_thi_canh_bao(self):
        self._ghi_do_thi(tuoi_giay=7200)
        with mock.patch.object(tdq_lsp.shutil, "which", return_value="/usr/bin/graphify"), \
                mock.patch.object(tdq_lsp, "_moc_code_moi_nhat", return_value=time.time()):
            b = tdq_lsp.bac7_graphify(self.thu_muc)
        self.assertFalse(b.dat)
        self.assertIn("cũ hơn", b.chi_tiet)

    def test_graphify_do_thi_moi_hon_ma_nguon_thi_dat(self):
        self._ghi_do_thi(tuoi_giay=0)
        with mock.patch.object(tdq_lsp.shutil, "which", return_value="/usr/bin/graphify"), \
                mock.patch.object(tdq_lsp, "_moc_code_moi_nhat", return_value=time.time() - 3600):
            b = tdq_lsp.bac7_graphify(self.thu_muc)
        self.assertTrue(b.dat, b.chi_tiet)

    def test_graphify_khong_co_file_ma_nguon_thi_khong_ket_luan_cu(self):
        """Không có file mã nguồn nào để so thì bậc không được bịa ra một phán quyết."""
        self._ghi_do_thi(tuoi_giay=7200)
        with mock.patch.object(tdq_lsp.shutil, "which", return_value="/usr/bin/graphify"), \
                mock.patch.object(tdq_lsp, "_moc_code_moi_nhat", return_value=None):
            b = tdq_lsp.bac7_graphify(self.thu_muc)
        self.assertTrue(b.dat)

    def test_graphify_nam_trong_thang_bac(self):
        """Thang có đúng 8 bậc đánh số liền; graphify là bậc 7, module LSP là bậc 8 (0.59.0)."""
        b = tdq_lsp.chay_kiem(ROOT)
        self.assertEqual([x.so for x in b], [1, 2, 3, 4, 5, 6, 7, 8])
        self.assertEqual(b[6].ten, "đồ thị graphify")


if __name__ == "__main__":
    unittest.main()
