"""Test thư viện rule kỹ thuật đa ngôn ngữ ở skills/tdq-build/references/rules/.

T4.2: `khuon_ngon_ngu` — đúng 10 file, mỗi file đủ khuôn 7 mục và dưới 150 dòng;
`chi_muc` — index.md nhắc đúng mọi file rule, không dòng thừa. Lưu ý cho người viết
index.md: chỉ được nhắc tên `.md` là file rule (file khác ghi không kèm đuôi .md).
Các test chung / them_ngon_ngu / nguon bổ sung ở T4.3 / T4.12 / T4.13.
"""
import re
import unittest
from pathlib import Path

from helper import ROOT

RULES_DIR = Path(ROOT) / "skills" / "tdq-build" / "references" / "rules"
RESEARCH = Path(ROOT) / "docs" / "tdq" / "research" / "2026-08-14-set-soul-workflow.md"

# 10 file bắt buộc: 7 ngôn ngữ + chung + index + quy trình thêm ngôn ngữ.
EXPECTED_FILES = [
    "chung.md", "index.md", "python.md", "csharp.md", "typescript-js.md",
    "go.md", "rust.md", "cpp.md", "html.md", "them-ngon-ngu.md",
]

# Khuôn 7 mục — heading cấp 2, so không phân biệt hoa thường, bỏ qua khối fence.
KHUON_7_MUC = [
    "## nguồn",
    "## khi nào áp dụng",
    "## luật intentionality",
    "## ngưỡng đo được",
    "## làm gì",
    "## tự kiểm",
    "## ví dụ đúng/sai",
]


def _headings(text):
    """Trả về các heading cấp 2 đã lowercase, bỏ dòng nằm trong fence ```."""
    out, fenced = [], False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            fenced = not fenced
            continue
        if not fenced and stripped.startswith("## "):
            out.append(stripped.lower())
    return out


class KhuonNgonNgu(unittest.TestCase):
    def test_khuon_ngon_ngu(self):
        self.assertTrue(RULES_DIR.is_dir(), f"Chưa có thư mục {RULES_DIR}")
        with self.subTest(ten="du_10_file"):
            actual = sorted(p.name for p in RULES_DIR.glob("*.md"))
            self.assertEqual(
                actual, sorted(EXPECTED_FILES),
                "rules/ phải có đúng 10 file theo plan, không thừa không thiếu")
        for name in EXPECTED_FILES:
            with self.subTest(ten=name.removesuffix(".md")):
                self.assertTrue((RULES_DIR / name).is_file(), f"chưa có {name}")
                text = (RULES_DIR / name).read_text(encoding="utf-8")
                self.assertLess(
                    len(text.splitlines()), 150, f"{name} phải dưới 150 dòng")
                headings = _headings(text)
                for muc in KHUON_7_MUC:
                    self.assertTrue(
                        any(h == muc for h in headings),
                        f"{name} thiếu mục '{muc}'")


class ChungMd(unittest.TestCase):
    def test_chung(self):
        path = RULES_DIR / "chung.md"
        self.assertTrue(path.is_file(), "Chưa có rules/chung.md")
        text = path.read_text(encoding="utf-8")
        for attr in ("Consistent", "Intentional", "Adaptable", "Responsible"):
            self.assertIn(attr, text, f"chung.md thiếu thuộc tính {attr}")
        self.assertIn("59,6", text, "chung.md thiếu số 59,6% (ưu tiên Intentionality)")
        for nguong in ("≤ 10", "≤ 15", "≤ 25"):
            self.assertIn(nguong, text, f"chung.md thiếu ngưỡng '{nguong}'")
        # Rule viết tiếng Anh từ 2026-08-19 (hướng A hybrid): luật không đổi, chỉ đổi
        # ngôn ngữ của từ khoá được soi (ghi đè → override).
        self.assertIn("override", text, "chung.md thiếu cách ghi đè ngưỡng")
        self.assertIn("OWASP", text, "chung.md thiếu checklist OWASP")


class ChiMuc(unittest.TestCase):
    def test_chi_muc(self):
        index = RULES_DIR / "index.md"
        self.assertTrue(index.is_file(), "Chưa có rules/index.md")
        text = index.read_text(encoding="utf-8")
        mentioned = set(re.findall(r"[a-z0-9-]+\.md", text)) - {"index.md"}
        # Chỉ mục phải khớp danh sách plan; file tồn tại ngoài danh sách do
        # khuon_ngon_ngu bắt (thư mục == EXPECTED), nên hai test gộp lại bảo đảm
        # chỉ mục == thư mục ở trạng thái cuối.
        self.assertEqual(
            mentioned, set(EXPECTED_FILES) - {"index.md"},
            "index.md phải nhắc đúng 9 file rule theo plan, không thừa không thiếu")
        tren_dia = {p.name for p in RULES_DIR.glob("*.md")} - {"index.md"}
        self.assertTrue(
            tren_dia <= mentioned,
            f"File có trên đĩa nhưng thiếu trong chỉ mục: {sorted(tren_dia - mentioned)}")


class ThemNgonNgu(unittest.TestCase):
    def test_them_ngon_ngu(self):
        """T4.12: quy trình thêm ngôn ngữ — 4 truy vấn cố định, duyệt TRƯỚC khi ghi."""
        path = RULES_DIR / "them-ngon-ngu.md"
        self.assertTrue(path.is_file(), "Chưa có rules/them-ngon-ngu.md")
        text = path.read_text(encoding="utf-8")
        for truy_van in (
            "official style guide",
            "linter static analysis",
            "code smells common mistakes",
            "cognitive complexity threshold",
        ):
            self.assertIn(truy_van, text, f"thiếu truy vấn cố định '{truy_van}'")
        self.assertIn("trình nháp", text, "thiếu bước trình nháp trong chat")
        vi_tri_duyet = text.find("chờ user duyệt")
        vi_tri_ghi = text.find("~/.claude/skills/tdq-rules")
        self.assertNotEqual(vi_tri_duyet, -1, "thiếu bước 'chờ user duyệt'")
        self.assertNotEqual(vi_tri_ghi, -1, "thiếu đích ghi ~/.claude/skills/tdq-rules")
        self.assertLess(
            vi_tri_duyet, vi_tri_ghi,
            "bước 'chờ user duyệt' phải đứng TRƯỚC bước ghi ra ~/.claude")
        self.assertIn("SKILL.md", text, "skill mới phải có SKILL.md")


class Nguon(unittest.TestCase):
    def test_nguon(self):
        """T4.13: mọi URL trong rules/ phải có mặt trong file research — 0 URL lạ."""
        self.assertTrue(RESEARCH.is_file(), f"Chưa có file research {RESEARCH}")
        research_text = RESEARCH.read_text(encoding="utf-8")
        url_la = []
        for duong_dan in sorted(RULES_DIR.glob("*.md")):
            text = duong_dan.read_text(encoding="utf-8")
            for url in re.findall(r"https?://[^\s)>\]`]+", text):
                url = url.rstrip(".,;:!?")
                if url not in research_text:
                    url_la.append(f"{duong_dan.name}: {url}")
        self.assertEqual(
            url_la, [],
            f"URL trong rules/ không truy được về research (cấm bịa nguồn): {url_la}")
