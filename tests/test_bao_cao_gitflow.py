"""Giữ báo cáo phương án nhánh git khỏi mục theo thời gian.

Phương án nói những vị trí `file:dòng` và những tên nhánh mẫu. Cả hai loại đều mục ngay khi mã
nguồn hoặc luật đổi. Bộ test này mở từng vị trí xem còn trỏ vào file thật không, và ném từng tên
nhánh mẫu qua chính `git check-ref-format` để chắc git chấp nhận.

Test ĐỎ ở đây nghĩa là báo cáo cần cập nhật, không nhất thiết là mã nguồn hỏng.
"""
import os
import re
import subprocess
import unittest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THU_MUC_BC = os.path.join(GOC, "docs", "tdq", "report")
SLUG = "2026-09-05-0037-nghien-cuu-gitflow-branch"
DUONG_PHUONG_AN = os.path.join(THU_MUC_BC, f"{SLUG}-phuong-an.md")
DUONG_BAO_CAO = os.path.join(THU_MUC_BC, f"{SLUG}.md")

# Sáu khoảng trống của spec §1 — phương án phải lấp đủ, không thiếu cái nào.
MA_KHOANG_TRONG = ("G1", "G2", "G3", "G4", "G5", "G6")
# Ba mô hình nhánh của bảng so sánh; mỗi dòng phải kèm nguồn.
TEN_MO_HINH = ("Gitflow đầy đủ", "GitHub Flow có phân loại", "Trunk-based thuần")
# Luật §7 của tdq-conventions: tên nhánh không được mở đầu bằng bốn chữ này.
TIEN_TO_CAM = ("claude", "antigravity", "gemini", "codex")
# Loại request user đã chốt ở brief mục `## Hỏi đáp` (câu 1, phương án A).
LOAI_REQUEST = ("feature", "bugfix", "hotfix", "chore", "docs")
# Sáu chốt của user: mỗi chốt một mẩu chữ phải xuất hiện nguyên vẹn trong phương án.
SAU_CHOT = (
    "gộp vào câu hỏi chọn lane",
    "tầng `nhỏ`",
    "--no-ff",
    "git branch -d",
    "thay vai",
    "dọn worktree ngay",
)
# `path/file.py:123` hoặc `path/file.md:123` — chỉ bắt file trong repo.
VI_TRI = re.compile(r"`((?:scripts|hooks|tools_kiem|tests|skills|docs)/[\w/.-]+\.(?:py|md)):(\d+)`")
# Tên nhánh mẫu: token trong backtick, mở đầu bằng một loại request đã chốt.
TEN_NHANH = re.compile(r"`((?:%s)/[\w./-]+)`" % "|".join(LOAI_REQUEST))
# Bất kỳ token nào trong backtick trông như tên nhánh, để soi tiền tố bị cấm.
NHANH_BAT_KY = re.compile(r"`([a-zA-Z][\w.-]*/[\w./-]+)`")
# Câu chữ bị cấm: request này chỉ nghiên cứu, chưa thi hành gì.
CAU_CAM = re.compile(r"đã (thi hành|áp dụng|triển khai|sửa xong)", re.IGNORECASE)


def _doc(duong):
    with open(duong, encoding="utf-8") as f:
        return f.read()


def _muc(noi_dung, mau_tieu_de):
    """{mã: thân} cho mọi tiêu đề khớp mẫu, thân chạy tới tiêu đề cùng cấp kế tiếp."""
    ra = {}
    hien_tai = None
    cap = None
    for dong in noi_dung.splitlines():
        moc = re.match(mau_tieu_de, dong)
        if moc:
            hien_tai = moc.group(1)
            cap = dong.split(" ", 1)[0]
            ra[hien_tai] = []
        elif hien_tai and dong.startswith(f"{cap} "):
            hien_tai = None
        elif hien_tai:
            ra[hien_tai].append(dong)
    return {k: "\n".join(v) for k, v in ra.items()}


def _duong_dan_trong(dong):
    """Các token backtick trên một dòng trông như đường dẫn file/thư mục trong repo."""
    return [t for t in re.findall(r"`([^`]+)`", dong)
            if "/" in t and not t.startswith(("http", "git "))]


class SauMucKhoangTrongTest(unittest.TestCase):
    def test_dem_sau_muc(self):
        muc = _muc(_doc(DUONG_PHUONG_AN), r"^## (G\d) — ")
        self.assertEqual(sorted(muc), list(MA_KHOANG_TRONG),
                         "phương án phải có đúng sáu mục G1–G6")

    def test_cham_tro_dung(self):
        muc = _muc(_doc(DUONG_PHUONG_AN), r"^## (G\d) — ")
        self.assertTrue(muc, "chưa có mục G nào để kiểm")
        for ma, than in muc.items():
            with self.subTest(ma=ma):
                dong_cham = [d for d in than.splitlines() if d.strip().startswith("**Chạm:**")]
                self.assertEqual(len(dong_cham), 1, f"{ma} phải có đúng một dòng **Chạm:**")
                duong = _duong_dan_trong(dong_cham[0])
                self.assertTrue(duong, f"{ma}: dòng **Chạm:** không nêu đường dẫn nào")
                for d in duong:
                    self.assertTrue(os.path.exists(os.path.join(GOC, d)),
                                    f"{ma}: {d} không tồn tại trên đĩa")


class BangSoSanhTest(unittest.TestCase):
    def test_bang_so_sanh(self):
        noi_dung = _doc(DUONG_PHUONG_AN)
        for ten in TEN_MO_HINH:
            with self.subTest(mo_hinh=ten):
                dong = [d for d in noi_dung.splitlines()
                        if d.startswith("|") and ten in d]
                self.assertEqual(len(dong), 1, f"bảng so sánh phải có đúng một dòng cho {ten}")
                self.assertIn("http", dong[0], f"dòng {ten} thiếu link nguồn")


class VongDoiTest(unittest.TestCase):
    def test_co_lenh_git(self):
        buoc = _muc(_doc(DUONG_PHUONG_AN), r"^### (B\d) — ")
        self.assertGreaterEqual(len(buoc), 4, "vòng đời phải có ít nhất 4 bước B1–B4")
        for ma, than in buoc.items():
            with self.subTest(ma=ma):
                self.assertTrue(any(d.strip().startswith("git ") for d in than.splitlines()),
                                f"{ma} không có lệnh git nào chạy được")

    def test_ten_nhanh_hop_le(self):
        ten = sorted(set(TEN_NHANH.findall(_doc(DUONG_PHUONG_AN))))
        self.assertGreaterEqual(len(ten), 3, "phương án phải nêu ít nhất 3 tên nhánh mẫu")
        for nhanh in ten:
            with self.subTest(nhanh=nhanh):
                ket_qua = subprocess.run(
                    ["git", "check-ref-format", "--branch", nhanh],
                    capture_output=True, text=True, encoding="utf-8", cwd=GOC)
                self.assertEqual(ket_qua.returncode, 0,
                                 f"git từ chối tên nhánh {nhanh!r}")

    def test_khong_pham_luat_bay(self):
        for nhanh in set(NHANH_BAT_KY.findall(_doc(DUONG_PHUONG_AN))):
            with self.subTest(nhanh=nhanh):
                self.assertFalse(nhanh.lower().startswith(TIEN_TO_CAM),
                                 f"{nhanh} phạm luật §7 của tdq-conventions")


class LoTrinhTest(unittest.TestCase):
    def test_giai_doan(self):
        giai_doan = _muc(_doc(DUONG_PHUONG_AN), r"^### (GĐ\d) — ")
        self.assertGreaterEqual(len(giai_doan), 3, "lộ trình phải có ít nhất 3 giai đoạn")
        for ma, than in giai_doan.items():
            with self.subTest(ma=ma):
                self.assertIn("- Chạm:", than, f"{ma} thiếu dòng file bị chạm")
                self.assertIn("- Rủi ro:", than, f"{ma} thiếu dòng rủi ro riêng")


class SauChotUserTest(unittest.TestCase):
    def test_sau_chot_user(self):
        noi_dung = _doc(DUONG_PHUONG_AN)
        for chot in SAU_CHOT:
            with self.subTest(chot=chot):
                self.assertIn(chot, noi_dung, f"phương án đánh rơi chốt của user: {chot!r}")

    def test_du_nam_loai_request(self):
        noi_dung = _doc(DUONG_PHUONG_AN)
        for loai in LOAI_REQUEST:
            with self.subTest(loai=loai):
                self.assertIn(f"`{loai}/", noi_dung, f"thiếu loại request {loai}")


class ViTriThatTest(unittest.TestCase):
    def test_vi_tri_that(self):
        vi_tri = VI_TRI.findall(_doc(DUONG_PHUONG_AN))
        self.assertGreaterEqual(len(vi_tri), 4, "phương án phải nêu vị trí `file:dòng` cụ thể")
        for duong, so in vi_tri:
            with self.subTest(vi_tri=f"{duong}:{so}"):
                that = os.path.join(GOC, duong)
                self.assertTrue(os.path.isfile(that), f"{duong} không tồn tại")
                with open(that, encoding="utf-8") as f:
                    tong = len(f.read().splitlines())
                self.assertLessEqual(int(so), tong, f"{duong} chỉ có {tong} dòng")


class KhongKhangDinhQuaTayTest(unittest.TestCase):
    """Request này chỉ nghiên cứu — cấm mọi câu nói phương án đã được thi hành."""

    def test_khong_khang_dinh_qua_tay(self):
        for duong in (DUONG_PHUONG_AN, DUONG_BAO_CAO):
            with self.subTest(file=os.path.basename(duong)):
                for so, dong in enumerate(_doc(duong).splitlines(), 1):
                    if CAU_CAM.search(dong) and "chưa" not in dong.lower():
                        self.fail(f"{duong}:{so} khẳng định quá tay: {dong.strip()}")


if __name__ == "__main__":
    unittest.main()
