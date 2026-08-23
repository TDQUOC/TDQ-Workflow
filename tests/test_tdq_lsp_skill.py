"""P3 — khoá luật ưu tiên tìm kiếm ở đúng 5 chỗ móc, khớp từng chữ với file luật gốc.

Luật viết 1 chỗ (`skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md`), trích ở 5 chỗ.
Không có test này thì sửa 1 chỗ là 4 chỗ kia trôi mà không ai biết: mỗi phase sẽ đọc
một thứ tự tìm kiếm khác nhau. Test so câu trích với câu gốc sau khi chuẩn hoá khoảng
trắng, nên xuống dòng ở đâu là tuỳ file, còn chữ thì phải y nguyên.
"""
import os
import re
import unittest

from helper import ROOT

GOC = os.path.join(ROOT, "skills", "tdq-lsp-setup", "references", "uu-tien-tim-kiem.md")

# 5 chỗ móc — đúng bảng §5 của file luật gốc.
CHO_MOC = [
    os.path.join(ROOT, "skills", "tdq-intake", "SKILL.md"),
    os.path.join(ROOT, "skills", "tdq-intake", "references", "analyze-full.md"),
    os.path.join(ROOT, "skills", "tdq-spec", "SKILL.md"),
    os.path.join(ROOT, "skills", "tdq-plan", "SKILL.md"),
    os.path.join(ROOT, "skills", "tdq-build", "SKILL.md"),
]


def doc(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def gon(text):
    """Chuẩn hoá khoảng trắng + bỏ dấu trích dẫn markdown để so chữ, không so cách ngắt dòng."""
    text = re.sub(r"(?m)^\s*>\s?", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def cau_goc():
    """Lấy câu luật chuẩn: khối blockquote đầu tiên của §1 trong file luật gốc."""
    src = doc(GOC)
    khoi = re.search(r"(?m)^((?:>.*\n)+)", src)
    assert khoi, "file luật gốc không còn khối blockquote nào — câu luật chuẩn đã mất"
    return gon(khoi.group(1))


class LuatUuTienTimKiem(unittest.TestCase):
    def setUp(self):
        self.cau = cau_goc()

    def test_cau_goc_du_ba_lop(self):
        """Câu chuẩn phải nêu đủ 3 lớp theo đúng thứ tự: LSP → lumen → grep."""
        for manh in ("mcp__lsp__", "lumen", "grep"):
            self.assertIn(manh, self.cau, f"câu luật gốc thiếu lớp {manh}")
        self.assertLess(self.cau.index("mcp__lsp__"), self.cau.index("lumen"))
        self.assertLess(self.cau.index("lumen"), self.cau.index("grep"))

    def test_nam_cho_moc_deu_co_cau_luat(self):
        """Xoá câu luật ở bất kỳ file móc nào → test này ĐỎ."""
        for path in CHO_MOC:
            with self.subTest(file=os.path.relpath(path, ROOT)):
                self.assertIn(
                    self.cau,
                    gon(doc(path)),
                    "câu luật lệch hoặc đã mất — chép lại nguyên văn từ uu-tien-tim-kiem.md",
                )

    def test_nam_cho_moc_deu_tro_ve_file_luat_goc(self):
        """Trích không kèm đường dẫn gốc thì người đọc không lần được về luật đầy đủ."""
        for path in CHO_MOC:
            with self.subTest(file=os.path.relpath(path, ROOT)):
                self.assertIn("uu-tien-tim-kiem.md", doc(path))

    def test_bang_cho_moc_trong_file_goc_khop_danh_sach_that(self):
        """§5 liệt kê chỗ móc nào thì test phải khoá đúng chừng ấy file."""
        src = doc(GOC)
        for path in CHO_MOC:
            ten = os.path.basename(path)
            self.assertIn(ten, src, f"§5 của file luật gốc chưa nhắc {ten}")


if __name__ == "__main__":
    unittest.main()
