"""test_spec_template.py — Kiểm thử tự động cấu trúc khuôn mẫu Spec Template và các thành phần Fresher-Centric.

Đảm bảo Spec trong TDQ Workflow luôn bắt buộc trực quan hóa luồng hoạt động (Mermaid),
đối chiếu Trước vs Sau, bóc tách giải thuật step-by-step và xây dựng Mental Model cho Fresher.
"""
import io
import os
import unittest

from helper import ROOT

PATH_TEMPLATE = os.path.join(ROOT, "skills", "tdq-spec", "references", "spec-template.md")
PATH_HUONG_DAN = os.path.join(ROOT, "skills", "tdq-spec", "references", "spec-template-huong-dan.md")
PATH_SKILL = os.path.join(ROOT, "skills", "tdq-spec", "SKILL.md")


def _read_file(path):
    with io.open(path, encoding="utf-8") as fh:
        return fh.read()


class TestSpecTemplateStructure(unittest.TestCase):
    """Kiểm tra cấu trúc khuôn mẫu spec-template.md."""

    def setUp(self):
        self.content = _read_file(PATH_TEMPLATE)

    def test_muc_luc_chua_du_3_phan_fresher(self):
        """Mục lục phải liệt kê các section 2c, 3c, 3d."""
        self.assertIn("- 2c. Luồng hoạt động & Sơ đồ kiến trúc", self.content)
        self.assertIn("- 3c. Giải thuật & Xử lý cốt lõi", self.content)
        self.assertIn("- 3d. Mental Model cho Fresher Dev", self.content)

    def test_section_2c_luong_va_so_do(self):
        """Mục 2c phải có sơ đồ Mermaid và bảng đối chiếu Trước vs Sau."""
        self.assertIn("## 2c. Luồng hoạt động & Sơ đồ kiến trúc", self.content)
        self.assertIn("```mermaid", self.content)
        self.assertIn("sequenceDiagram", self.content)
        self.assertIn("| Khía cạnh | Hiện trạng (Trước) | Thiết kế mới (Sau) |", self.content)

    def test_section_3c_giai_thuat_cot_loi(self):
        """Mục 3c phải có từng bước giải thuật, độ phức tạp và ca góc hiểm."""
        self.assertIn("## 3c. Giải thuật & Xử lý cốt lõi", self.content)
        self.assertIn("Từng bước giải thuật", self.content)
        self.assertIn("Time Complexity", self.content)
        self.assertIn("Space Complexity", self.content)
        self.assertIn("Edge Cases", self.content)

    def test_section_3d_mental_model_fresher(self):
        """Mục 3d phải có ẩn dụ trực quan và glossary giải nghĩa thuật ngữ."""
        self.assertIn("## 3d. Mental Model cho Fresher Dev", self.content)
        self.assertIn("Ẩn dụ trực quan", self.content)
        self.assertIn("Thuật ngữ dự án", self.content)


class TestSpecHuongDanAndSkill(unittest.TestCase):
    """Kiểm tra cẩm nang hướng dẫn và SKILL wrapper đồng bộ quy chuẩn mới."""

    def test_checklist_fresher_accessibility(self):
        """spec-template-huong-dan.md phải có checklist Fresher Accessibility Check."""
        content = _read_file(PATH_HUONG_DAN)
        self.assertIn("Fresher Accessibility Check", content)
        self.assertIn("Sơ đồ luồng (§2c)", content)
        self.assertIn("Trước vs Sau (§2c)", content)
        self.assertIn("Giải thuật 1-2-3 (§3c)", content)

    def test_skill_spec_yeu_cau_fresher_elements(self):
        """SKILL.md phải yêu cầu các section 2c, 3c, 3d và tóm tắt chat block."""
        content = _read_file(PATH_SKILL)
        self.assertIn("Luồng & Sơ đồ kiến trúc", content)
        self.assertIn("Giải thuật cốt lõi", content)
        self.assertIn("Mental Model cho Fresher", content)
        self.assertIn("Fresher Accessibility", content)
        self.assertIn("**Luồng & Giải thuật:**", content)


if __name__ == "__main__":
    unittest.main()
