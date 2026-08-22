#!/usr/bin/env python3
"""Test cho scripts/doc_dup.py — bộ dò đoạn văn trùng giữa các file tài liệu.

Mọi test chạm file đều dựng thư mục tạm bằng tempfile: chạy trên repo thật là cấm
(luật số 7 của plan 2026-08-22-1231-ra-soat-toi-uu-workflow).
"""

import os
import subprocess
import sys
import tempfile
import unittest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "scripts"))

import doc_dup  # noqa: E402

LENH = [sys.executable, os.path.join(GOC, "scripts", "doc_dup.py")]


def _ghi(thu_muc, ten, noi_dung):
    duong = os.path.join(thu_muc, ten)
    os.makedirs(os.path.dirname(duong), exist_ok=True)
    with open(duong, "w", encoding="utf-8") as f:
        f.write(noi_dung)
    return duong


DOAN_CHUNG = "Luật số một của bộ này.\nLuật số hai của bộ này.\nLuật số ba của bộ này.\n"


class ShingleTest(unittest.TestCase):
    """Nhóm `shingle`: dò đúng khối trùng, và không báo nhầm khi đã đổi chữ."""

    def test_hai_file_trung_ba_dong_thi_ra_dung_mot_cap(self):
        with tempfile.TemporaryDirectory() as tmp:
            _ghi(tmp, "a.md", "# A\n\n" + DOAN_CHUNG + "\nĐuôi riêng của A.\n")
            _ghi(tmp, "b.md", "# B\n\nMở đầu riêng của B.\n\n" + DOAN_CHUNG)
            cap = doc_dup.quet([tmp], min_dong=3, dem_token=False)
            self.assertEqual(len(cap), 1, f"phải ra đúng một cặp, đang ra {cap}")
            self.assertEqual(cap[0]["so_dong"], 3)

    def test_doi_mot_chu_trong_doan_thi_khong_ra_cap_nao(self):
        with tempfile.TemporaryDirectory() as tmp:
            _ghi(tmp, "a.md", "# A\n\n" + DOAN_CHUNG)
            _ghi(tmp, "b.md", "# B\n\n" + DOAN_CHUNG.replace("hai", "bốn"))
            self.assertEqual(doc_dup.quet([tmp], min_dong=3, dem_token=False), [])

    def test_khoi_trung_dai_hon_min_dong_thi_gop_lam_mot_cap(self):
        """Năm dòng trùng liền nhau là MỘT cặp năm dòng, không phải ba cặp ba dòng."""
        nam = "".join(f"Dòng luật số {i}.\n" for i in range(5))
        with tempfile.TemporaryDirectory() as tmp:
            _ghi(tmp, "a.md", nam)
            _ghi(tmp, "b.md", "Mở đầu.\n" + nam)
            cap = doc_dup.quet([tmp], min_dong=3, dem_token=False)
            self.assertEqual(len(cap), 1)
            self.assertEqual(cap[0]["so_dong"], 5)

    def test_dong_trong_va_khoang_trang_duoi_dong_khong_lam_lech_ket_qua(self):
        with tempfile.TemporaryDirectory() as tmp:
            _ghi(tmp, "a.md", DOAN_CHUNG)
            _ghi(tmp, "b.md", DOAN_CHUNG.replace("\n", "   \n\n"))
            self.assertEqual(len(doc_dup.quet([tmp], min_dong=3, dem_token=False)), 1)

    def test_so_dong_bao_ve_la_so_dong_that_trong_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            _ghi(tmp, "a.md", "# A\n\n" + DOAN_CHUNG)
            _ghi(tmp, "b.md", DOAN_CHUNG)
            cap = doc_dup.quet([tmp], min_dong=3, dem_token=False)[0]
            theo_file = {cap["file_a"]: cap["dong_a"], cap["file_b"]: cap["dong_b"]}
            self.assertEqual(theo_file[os.path.join(tmp, "a.md")], 3)
            self.assertEqual(theo_file[os.path.join(tmp, "b.md")], 1)

    def test_trung_trong_cung_mot_file_cung_bi_bat(self):
        with tempfile.TemporaryDirectory() as tmp:
            _ghi(tmp, "a.md", DOAN_CHUNG + "\nĐoạn giữa.\n\n" + DOAN_CHUNG)
            cap = doc_dup.quet([tmp], min_dong=3, dem_token=False)
            self.assertEqual(len(cap), 1)
            self.assertEqual(cap[0]["file_a"], cap[0]["file_b"])

    def test_chi_quet_file_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            _ghi(tmp, "a.md", DOAN_CHUNG)
            _ghi(tmp, "b.py", DOAN_CHUNG)
            self.assertEqual(doc_dup.quet([tmp], min_dong=3, dem_token=False), [])

    def test_vung_tro_thang_vao_mot_file_van_chay(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = _ghi(tmp, "a.md", DOAN_CHUNG)
            b = _ghi(tmp, "sau/b.md", DOAN_CHUNG)
            self.assertEqual(len(doc_dup.quet([a, b], min_dong=3, dem_token=False)), 1)


class TokenTest(unittest.TestCase):
    """Nhóm `token`: đếm bằng bộ đếm thật, cấm ước lượng ký-tự-chia-bốn."""

    def test_cap_trung_co_so_token_lon_hon_khong(self):
        with tempfile.TemporaryDirectory() as tmp:
            _ghi(tmp, "a.md", DOAN_CHUNG)
            _ghi(tmp, "b.md", DOAN_CHUNG)
            cap = doc_dup.quet([tmp], min_dong=3, dem_token=True)
            self.assertGreater(cap[0]["token"], 0)

    def test_khong_dem_token_thi_cot_token_de_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            _ghi(tmp, "a.md", DOAN_CHUNG)
            _ghi(tmp, "b.md", DOAN_CHUNG)
            self.assertIsNone(doc_dup.quet([tmp], min_dong=3, dem_token=False)[0]["token"])

    def test_thieu_thu_vien_dem_thi_nem_loi_chu_khong_uoc_luong(self):
        with tempfile.TemporaryDirectory() as tmp:
            _ghi(tmp, "a.md", DOAN_CHUNG)
            _ghi(tmp, "b.md", DOAN_CHUNG)
            that = doc_dup.dem_token_loat
            doc_dup.dem_token_loat = _nem_thieu
            try:
                with self.assertRaises(doc_dup.ThieuThuVienDem):
                    doc_dup.quet([tmp], min_dong=3, dem_token=True)
            finally:
                doc_dup.dem_token_loat = that


def _nem_thieu(_doan):
    raise doc_dup.ThieuThuVienDem("thiếu thư viện đếm")


class LogTest(unittest.TestCase):
    """Nhóm `log`: log ra stderr, bật mặc định, tắt được, bảng luôn ra stdout."""

    def _chay(self, tmp, *them, moi_truong=None):
        env = dict(os.environ)
        env.update(moi_truong or {})
        return subprocess.run(LENH + ["--vung", tmp, *them],
                              capture_output=True, text=True, env=env)

    def _dung_hai_file(self, tmp):
        _ghi(tmp, "a.md", DOAN_CHUNG)
        _ghi(tmp, "b.md", DOAN_CHUNG)

    def test_mac_dinh_co_log_kem_timestamp_o_stderr(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._dung_hai_file(tmp)
            proc = self._chay(tmp)
            self.assertRegex(proc.stderr, r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")

    def test_co_quiet_thi_stderr_rong(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._dung_hai_file(tmp)
            self.assertEqual(self._chay(tmp, "--quiet").stderr, "")

    def test_bien_moi_truong_tat_duoc_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._dung_hai_file(tmp)
            self.assertEqual(self._chay(tmp, moi_truong={"TDQ_DUP_LOG": "0"}).stderr, "")

    def test_bang_luon_ra_stdout_ke_ca_khi_tat_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._dung_hai_file(tmp)
            self.assertIn("|", self._chay(tmp, "--quiet").stdout)

    def test_khong_co_cap_nao_van_in_mot_dong_bao(self):
        with tempfile.TemporaryDirectory() as tmp:
            _ghi(tmp, "a.md", "Chỉ một dòng.\n")
            proc = self._chay(tmp, "--quiet")
            self.assertEqual(proc.returncode, 0)
            self.assertTrue(proc.stdout.strip())


class ThoatTest(unittest.TestCase):
    """Nhóm `thoat`: 0 chạy xong · 2 sai cú pháp · 3 thiếu thư viện đếm."""

    def test_chay_xong_thoat_0(self):
        with tempfile.TemporaryDirectory() as tmp:
            _ghi(tmp, "a.md", DOAN_CHUNG)
            _ghi(tmp, "b.md", DOAN_CHUNG)
            proc = subprocess.run(LENH + ["--vung", tmp, "--quiet"],
                                  capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0)

    def test_sai_cu_phap_thoat_2(self):
        proc = subprocess.run(LENH + ["--khong-co-co-nay"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)

    def test_vung_khong_ton_tai_thoat_2(self):
        proc = subprocess.run(LENH + ["--vung", "/khong/ton/tai/that"],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)

    def test_ma_thoat_thieu_thu_vien_la_3(self):
        self.assertEqual(doc_dup.EXIT_THIEU_THU_VIEN, 3)

    def test_min_dong_nho_hon_1_bi_tu_choi(self):
        with tempfile.TemporaryDirectory() as tmp:
            _ghi(tmp, "a.md", DOAN_CHUNG)
            proc = subprocess.run(LENH + ["--vung", tmp, "--min-dong", "0"],
                                  capture_output=True, text=True)
            self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()
