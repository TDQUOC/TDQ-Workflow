"""Giữ báo cáo tương thích đa nền tảng khỏi mục theo thời gian.

Báo cáo nói những con số ("18 chỗ `subprocess` thiếu `encoding=`", "0 chỗ `open()` thiếu") và
những vị trí `file:dòng`. Cả hai loại đều mục ngay khi mã nguồn đổi. Bộ test này đếm lại bằng
chính script `tools_kiem/dem_da_nen_tang.py` và đối chiếu với con số đã ghi trong báo cáo; nó
cũng mở từng `file:dòng` xem còn trỏ vào file thật không.

Test ĐỎ ở đây nghĩa là báo cáo cần cập nhật, không nhất thiết là mã nguồn hỏng.
"""
import os
import re
import sys
import unittest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "tools_kiem"))

import dem_da_nen_tang  # noqa: E402

THU_MUC_BC = os.path.join(GOC, "docs", "tdq", "report")
SLUG = "2026-09-03-1648-kiem-da-nen-tang-host"
DUONG_TUONG_THICH = os.path.join(THU_MUC_BC, f"{SLUG}-tuong-thich.md")
DUONG_LENH = os.path.join(THU_MUC_BC, f"{SLUG}-lenh-kiem.md")

# Năm trường bắt buộc của một khối phát hiện.
TRUONG_BAT_BUOC = ("**Nhãn:**", "**Triệu chứng:**", "**Vị trí:**", "**Hệ dính:**", "**Mức nguy:**")
NHAN_HOP_LE = ("đọc mã", "giả lập", "tài liệu")
# Câu chữ bị cấm: không có máy thật thì không được nói là đã chạy được.
CAU_CAM = re.compile(r"đã chạy được trên (linux|windows)", re.IGNORECASE)
# `path/file.py:123` — chỉ bắt file mã nguồn, không bắt đường dẫn tài liệu.
VI_TRI = re.compile(r"`((?:scripts|hooks|tools_kiem|tests)/[\w/.-]+\.py):(\d+)`")


def _doc(duong):
    with open(duong, encoding="utf-8") as f:
        return f.read()


def _khoi_phat_hien(noi_dung):
    """{mã: nội dung khối} cho mọi tiêu đề dạng `## P1 — ...`."""
    khoi = {}
    hien_tai = None
    for dong in noi_dung.splitlines():
        moc = re.match(r"^## (P\d) — ", dong)
        if moc:
            hien_tai = moc.group(1)
            khoi[hien_tai] = []
        elif dong.startswith("## "):
            hien_tai = None
        elif hien_tai:
            khoi[hien_tai].append(dong)
    return {k: "\n".join(v) for k, v in khoi.items()}


class KhoiPhatHienTest(unittest.TestCase):
    def test_du_bon_khoi_moi_khoi_du_truong_va_nhan(self):
        khoi = _khoi_phat_hien(_doc(DUONG_TUONG_THICH))
        self.assertGreaterEqual(len(khoi), 4, "báo cáo phải có ít nhất 4 phát hiện P1–P4")
        for ma, than in khoi.items():
            with self.subTest(ma=ma):
                for truong in TRUONG_BAT_BUOC:
                    self.assertIn(truong, than, f"{ma} thiếu trường {truong}")
                self.assertIn("Cách sửa đề xuất", than, f"{ma} thiếu cách sửa đề xuất")
                nhan = than.split("**Nhãn:**", 1)[1].splitlines()[0]
                self.assertTrue(any(n in nhan for n in NHAN_HOP_LE),
                                f"{ma} mang nhãn lớp bằng chứng không hợp lệ: {nhan!r}")

    def test_moi_doan_nhan_tai_lieu_deu_co_link(self):
        noi_dung = _doc(DUONG_TUONG_THICH)
        for dong in noi_dung.splitlines():
            if "nguồn:" in dong:
                with self.subTest(dong=dong[:50]):
                    self.assertIn("http", dong, "đoạn dẫn nguồn phải kèm link")


class ViTriThatTest(unittest.TestCase):
    def test_moi_vi_tri_tro_dung_file_va_so_dong_nam_trong_file(self):
        vi_tri = VI_TRI.findall(_doc(DUONG_TUONG_THICH))
        self.assertGreaterEqual(len(vi_tri), 4, "báo cáo phải nêu vị trí `file:dòng` cụ thể")
        for duong, so in vi_tri:
            with self.subTest(vi_tri=f"{duong}:{so}"):
                that = os.path.join(GOC, duong)
                self.assertTrue(os.path.isfile(that), f"{duong} không tồn tại")
                with open(that, encoding="utf-8") as f:
                    tong = len(f.read().splitlines())
                self.assertLessEqual(int(so), tong, f"{duong} chỉ có {tong} dòng")


class SoLieuTest(unittest.TestCase):
    """Con số trong báo cáo phải khớp số đếm lại bằng `ast` ngay lúc này."""

    @classmethod
    def setUpClass(cls):
        cls.dem = dem_da_nen_tang.dem_tat_ca(GOC)
        cls.noi_dung = _doc(DUONG_TUONG_THICH)

    def test_diem_manh_du_ba_muc(self):
        phan = self.noi_dung.split("## Điểm mạnh", 1)
        self.assertEqual(len(phan), 2, "báo cáo thiếu mục điểm mạnh")
        muc = [d for d in phan[1].splitlines() if d.startswith("- **")]
        self.assertGreaterEqual(len(muc), 3, "mục điểm mạnh phải có ít nhất 3 gạch đầu dòng")

    def test_so_open_thieu_encoding_khop(self):
        that = len(self.dem["open_thieu_encoding"])
        moc = re.search(r"`open\(\)` chế độ văn bản thiếu `encoding=`: \*\*(\d+)\*\*",
                        self.noi_dung)
        self.assertIsNotNone(moc, "báo cáo không còn nêu số open() thiếu encoding")
        self.assertEqual(int(moc.group(1)), that)

    def test_so_import_posix_khop(self):
        that = len(self.dem["import_chi_posix"])
        moc = re.search(r"`resource`\): \*\*(\d+)\*\*", self.noi_dung)
        self.assertIsNotNone(moc, "báo cáo không còn nêu số import chỉ có trên POSIX")
        self.assertEqual(int(moc.group(1)), that)

    def test_so_subprocess_thieu_encoding_khop(self):
        that = len(self.dem["subprocess_thieu_encoding"])
        moc = re.search(r"\*\*(\d+)\*\* chỗ gọi `subprocess`", self.noi_dung)
        self.assertIsNotNone(moc, "báo cáo không còn nêu số subprocess thiếu encoding")
        self.assertEqual(int(moc.group(1)), that)

    def test_moi_hook_van_goi_python3(self):
        """P1 chỉ còn đúng khi các hook vẫn gọi thẳng `python3`."""
        for ten, so in self.dem["hook_goi_python3"].items():
            with self.subTest(nguon=ten):
                if not so["co_file"]:
                    continue
                self.assertEqual(so["python3"], so["tong"],
                                 f"{ten}: số command gọi python3 đã đổi — cập nhật P1")


class LenhKiemTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.noi_dung = _doc(DUONG_LENH)

    def test_du_lenh_va_du_hai_nhom(self):
        ma = re.findall(r"\*\*(L\d+) —", self.noi_dung)
        self.assertGreaterEqual(len(ma), 6, "phải có ít nhất 6 lệnh")
        self.assertEqual(len(ma), len(set(ma)), "mã lệnh bị trùng")
        self.assertIn("## Nhóm Linux", self.noi_dung)
        self.assertIn("## Nhóm Windows", self.noi_dung)

    def test_moi_lenh_du_hai_dong_ket_qua(self):
        khoi = re.split(r"\*\*(L\d+) —", self.noi_dung)[1:]
        for ma, than in zip(khoi[::2], khoi[1::2]):
            with self.subTest(ma=ma):
                self.assertIn("- Đạt:", than, f"{ma} thiếu dòng 'đạt là thấy gì'")
                self.assertIn("- Hỏng:", than, f"{ma} thiếu dòng 'hỏng là thấy gì'")

    def test_windows_thuan_khong_muon_shell_posix(self):
        win = self.noi_dung.split("## Nhóm Windows", 1)[1]
        for cam in ("bash", "sh -c", "wsl", "/dev/null"):
            with self.subTest(cam=cam):
                self.assertNotIn(cam, win,
                                 f"nhóm Windows không được dùng {cam} — user đã chốt PowerShell thuần")

    def test_chua_chot_noi_toi_lenh_co_that(self):
        bao_cao = _doc(DUONG_TUONG_THICH)
        phan = bao_cao.split("## Chưa chốt được", 1)
        self.assertEqual(len(phan), 2, "báo cáo thiếu mục chưa chốt được")
        muc = re.findall(r"- \*\*(C\d) —", phan[1])
        self.assertGreaterEqual(len(muc), 3, "phải có ít nhất 3 điểm chưa chốt")
        co_that = set(re.findall(r"\*\*(L\d+) —", self.noi_dung))
        for ma_c in muc:
            than = phan[1].split(f"- **{ma_c} —", 1)[1].split("\n- **")[0]
            nhac = set(re.findall(r"\*\*(L\d+)\*\*", than))
            with self.subTest(ma=ma_c):
                self.assertTrue(nhac, f"{ma_c} không trỏ tới lệnh kiểm nào")
                self.assertTrue(nhac <= co_that, f"{ma_c} trỏ tới mã lệnh không tồn tại: {nhac - co_that}")


class KhongKhangDinhQuaTayTest(unittest.TestCase):
    """Không có máy thật → cấm mọi câu nói phần mềm đã chạy được trên Linux/Windows."""

    def test_khong_cau_khang_dinh_da_chay_that(self):
        for duong in (DUONG_TUONG_THICH, DUONG_LENH):
            with self.subTest(file=os.path.basename(duong)):
                for so, dong in enumerate(_doc(duong).splitlines(), 1):
                    if CAU_CAM.search(dong) and "không chỗ nào" not in dong:
                        self.fail(f"{duong}:{so} khẳng định quá tay: {dong.strip()}")


if __name__ == "__main__":
    unittest.main()
