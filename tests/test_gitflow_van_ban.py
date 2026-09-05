"""Luật mở/gộp nhánh git nằm trong VĂN BẢN skill, nên phải khoá bằng test văn bản.

Ba file mang luật: `tdq-intake` (mở nhánh), khuôn báo cáo (gộp về nhánh gốc), `tdq-conventions`
(hình dạng tên nhánh). Test ĐỎ ở đây nghĩa là một trong ba chỗ đã mất luật, hoặc tên nhánh mẫu
viết sai dạng — `git check-ref-format` là trọng tài, không phải mắt người.
"""
import os
import re
import subprocess
import unittest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTAKE = os.path.join(GOC, "skills", "tdq-intake", "SKILL.md")
KHUON_BAO_CAO = os.path.join(GOC, "skills", "tdq-build", "references", "report-template.md")
CONVENTIONS = os.path.join(GOC, "skills", "tdq-conventions", "SKILL.md")
BUNDLE_CLAUDE = os.path.join(GOC, "portable_claude")

LOAI = ("feature", "bugfix", "hotfix", "chore", "docs")
TIEN_TO_CAM = ("claude", "antigravity", "gemini", "codex")
# Tên nhánh mẫu trong tài liệu luôn nằm trong backtick, hai đoạn, đuôi kebab: `feature/login-gui`.
# `docs/` vừa là một loại request vừa là thư mục thật, nên chuỗi nào TRỎ TỚI file/thư mục có
# thật trong repo thì đó là đường dẫn tài liệu, không phải tên nhánh mẫu — xem `_la_ten_nhanh`.
TEN_NHANH = re.compile(r"`((?:" + "|".join(LOAI) + r")/[a-z0-9]+(?:-[a-z0-9]+)*)`")
# Bốn gạch đầu dòng sẵn có của `## 7. Git` — thêm luật mới không được đẩy mất cái nào.
GACH_CU = ("never** start with", "generated with", "commit or push before the user asks",
           "you may init git or a worktree")


def _doc(duong):
    with open(duong, encoding="utf-8") as f:
        return f.read()


def _la_ten_nhanh(ten):
    return not os.path.exists(os.path.join(GOC, ten))


def _muc(noi_dung, dau, cuoi):
    """Phần văn bản giữa hai mốc; rỗng khi không tìm thấy mốc đầu."""
    if dau not in noi_dung:
        return ""
    sau = noi_dung.split(dau, 1)[1]
    return sau.split(cuoi, 1)[0] if cuoi in sau else sau


class IntakeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.noi_dung = _doc(INTAKE)

    def test_de_xuat_loai_nam_trong_cau_hoi_chon_lane(self):
        """Chốt C2: đề xuất loại request gộp vào chính câu hỏi chọn lane, không hỏi thêm câu nào."""
        buoc2 = _muc(self.noi_dung, "2. **Propose a lane", "3. **Init state")
        self.assertTrue(buoc2, "intake không còn bước 2 chọn lane")
        for loai in LOAI:
            with self.subTest(loai=loai):
                self.assertIn(loai, buoc2, f"câu hỏi chọn lane chưa nêu loại {loai}")
        self.assertIn("loai_request", buoc2,
                      "bước 2 phải nói rõ câu trả lời được ghi vào khoá loai_request")

    def test_mo_nhanh_dung_lane(self):
        """Chốt C3: chỉ lane `full` và `quick` mở nhánh; tầng `nhỏ` thì không."""
        buoc = _muc(self.noi_dung, "**Open the request branch", "\n4. **Branch:")
        self.assertTrue(buoc, "intake thiếu bước mở nhánh cho request")
        for tu in ("full", "quick", "nhỏ"):
            with self.subTest(tu=tu):
                self.assertIn(tu, buoc, f"bước mở nhánh chưa nói tới {tu}")
        self.assertIn("nhanh_goc", buoc, "bước mở nhánh phải ghi lại nhánh gốc")
        self.assertIn("nhanh_request", buoc, "bước mở nhánh phải ghi lại nhánh vừa mở")
        self.assertRegex(buoc, r"git switch -c|git checkout -b",
                         "bước mở nhánh phải nêu lệnh git thật")

    def test_repo_ban_thi_dung_va_hoi(self):
        """Chốt G-C: repo bẩn lúc mở request thì DỪNG, in file bẩn, hỏi user."""
        buoc = _muc(self.noi_dung, "**Open the request branch", "\n4. **Branch:")
        self.assertIn("git status", buoc, "bước mở nhánh phải kiểm git status trước")
        self.assertIn("STOP", buoc, "repo bẩn thì phải DỪNG, không tự stash")
        self.assertNotIn("git stash", buoc, "user đã chốt: không tự stash")


class KhuonBaoCaoTest(unittest.TestCase):
    def test_buoc_muoi_du_hai_nhanh_tra_loi(self):
        """Chốt C4 + G-B: cả 'commit' lẫn 'chưa' đều merge về nhánh gốc."""
        buoc10 = _muc(_doc(KHUON_BAO_CAO), "10. **Ask the user whether to commit",
                      "Done when: the report is written")
        self.assertTrue(buoc10, "khuôn báo cáo không còn bước 10")
        self.assertIn("git merge --no-ff", buoc10, "bước 10 phải merge --no-ff về nhánh gốc")
        self.assertIn("git branch -d", buoc10, "merge xong phải xoá nhánh request")
        self.assertIn("nhanh_goc", buoc10, "bước 10 phải đọc nhánh gốc từ state")
        for tra_loi in ('"commit"', '"chưa"'):
            with self.subTest(tra_loi=tra_loi):
                self.assertIn(tra_loi, buoc10, f"bước 10 thiếu nhánh trả lời {tra_loi}")
        self.assertIn("git status", buoc10,
                      "bước 10 phải kiểm working tree trước khi chuyển nhánh")


class LuatTenNhanhTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.muc7 = _muc(_doc(CONVENTIONS), "## 7. Git", "\n## 8.")

    def test_luat_ten_nhanh_du_nam_loai_va_giu_gach_cu(self):
        self.assertTrue(self.muc7, "tdq-conventions không còn mục `## 7. Git`")
        for loai in LOAI:
            with self.subTest(loai=loai):
                self.assertIn(f"`{loai}/", self.muc7, f"mục 7 chưa nêu loại {loai}")
        for gach in GACH_CU:
            with self.subTest(gach=gach[:24]):
                self.assertIn(gach, self.muc7, "luật mới đã đẩy mất một gạch đầu dòng cũ")
        self.assertIn("check-ref-format", self.muc7,
                      "phải nêu lý do dùng `/`: git từ chối dạng kia")


class TenNhanhMauTest(unittest.TestCase):
    """Mọi tên nhánh mẫu trong ba file luật phải là tên nhánh git hợp lệ thật."""

    @classmethod
    def setUpClass(cls):
        cls.mau = sorted({t for duong in (INTAKE, KHUON_BAO_CAO, CONVENTIONS)
                          for t in TEN_NHANH.findall(_doc(duong)) if _la_ten_nhanh(t)})

    def test_ten_nhanh_hop_le(self):
        self.assertTrue(self.mau, "không tìm thấy tên nhánh mẫu nào trong tài liệu luật")
        for ten in self.mau:
            with self.subTest(ten=ten):
                xong = subprocess.run(["git", "check-ref-format", "--branch", ten],
                                      capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(xong.returncode, 0, f"git từ chối tên nhánh mẫu {ten!r}")

    def test_khong_tien_to_cam(self):
        for ten in self.mau:
            with self.subTest(ten=ten):
                self.assertFalse(ten.lower().startswith(TIEN_TO_CAM),
                                 f"tên nhánh mẫu {ten!r} mở đầu bằng tiền tố bị cấm")


class BundleTest(unittest.TestCase):
    """Luật tên nhánh phải có mặt trong bundle đã dựng, không chỉ trong repo nguồn.

    Bundle sinh ra từ `build_portable.py`; ai sửa luật mà quên dựng lại thì ca này ĐỎ.
    """

    @classmethod
    def setUpClass(cls):
        cls.conventions = os.path.join(
            BUNDLE_CLAUDE, ".claude", "skills", "tdq-conventions", "SKILL.md")
        cls.intake = os.path.join(
            BUNDLE_CLAUDE, ".claude", "skills", "tdq-intake", "SKILL.md")
        cls.rule = os.path.join(
            BUNDLE_CLAUDE, ".claude", "skills", "tdq-intake", "references", "nhanh-request.md")

    def test_du_ba_file_luat_trong_bundle(self):
        for duong in (self.conventions, self.intake, self.rule):
            with self.subTest(file=os.path.basename(duong)):
                self.assertTrue(os.path.isfile(duong), f"bundle thiếu {duong}")

    def test_bundle_mang_du_nam_loai_va_buoc_mo_nhanh(self):
        luat = _doc(self.rule)
        for loai in LOAI:
            with self.subTest(loai=loai):
                self.assertIn(loai, luat, f"file luật trong bundle thiếu loại {loai}")
        self.assertIn("git switch -c", _doc(self.intake), "bundle thiếu bước mở nhánh")

    def test_ten_nhanh_mau_trong_bundle_hop_le(self):
        mau = sorted({t for duong in (self.conventions, self.intake, self.rule)
                      for t in TEN_NHANH.findall(_doc(duong)) if _la_ten_nhanh(t)})
        self.assertTrue(mau, "bundle không còn tên nhánh mẫu nào")
        for ten in mau:
            with self.subTest(ten=ten):
                xong = subprocess.run(["git", "check-ref-format", "--branch", ten],
                                      capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(xong.returncode, 0, f"git từ chối tên nhánh mẫu {ten!r}")


if __name__ == "__main__":
    unittest.main()
