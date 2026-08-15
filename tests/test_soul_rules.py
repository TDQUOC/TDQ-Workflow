"""Soul của workflow + thư viện rule kỹ thuật (request 2026-08-14-0900-set-soul-workflow).

Bất biến giữ ở đây:
1. `soul.md` tồn tại, nêu đúng thứ tự ưu tiên chất lượng → runtime → context cost,
   và có mục phạm vi nêu tên đủ 5 loại tài liệu request.
2. Tầng luôn nạp (SKILL.md conventions) và bản portable đều trỏ về soul.
"""
import json
import os
import re
import unittest

from helper import ROOT

SOUL = os.path.join(ROOT, "skills", "tdq-conventions", "references", "soul.md")
CONV_SKILL = os.path.join(ROOT, "skills", "tdq-conventions", "SKILL.md")
AGENTS = os.path.join(ROOT, "portable", "AGENTS.md")
PRIORITY = "chất lượng > runtime > context cost"
DOC_KINDS = ("brief", "spec", "plan", "qc", "report")


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


class SoulFile(unittest.TestCase):
    def test_thu_tu_uu_tien(self):
        self.assertTrue(os.path.exists(SOUL), "chưa có soul.md")
        text = _read(SOUL)
        line = next(
            (l for l in text.splitlines()
             if "chất lượng" in l and "runtime" in l and "context cost" in l),
            None,
        )
        self.assertIsNotNone(line, "soul.md thiếu dòng nêu đủ 3 tầng ưu tiên")
        self.assertLess(line.index("chất lượng"), line.index("runtime"),
                        "chất lượng phải đứng trước runtime")
        self.assertLess(line.index("runtime"), line.index("context cost"),
                        "runtime phải đứng trước context cost")
        self.assertRegex(line, r"chất lượng\s*>\s*runtime\s*>\s*context cost",
                         "3 tầng phải nối bằng dấu > để trích lại được nguyên văn")

    def test_thu_tu_pham_vi_va_do_dai(self):
        self.assertTrue(os.path.exists(SOUL), "chưa có soul.md")
        text = _read(SOUL)
        scope_line = next(
            (l for l in text.splitlines()
             if all(k in l.lower() for k in DOC_KINDS)),
            None,
        )
        self.assertIsNotNone(
            scope_line,
            "soul.md phải có một dòng phạm vi nêu tên đủ brief/spec/plan/qc/report")
        self.assertLess(len(text.splitlines()), 150,
                        "soul.md phải dưới 150 dòng — soul dài là soul không ai đọc")


TEMPLATES = (
    ("skills", "tdq-intake", "SKILL.md"),
    ("skills", "tdq-spec", "references", "spec-template.md"),
    ("skills", "tdq-plan", "references", "plan-template.md"),
    ("skills", "tdq-build", "references", "qc.md"),
    ("skills", "tdq-build", "references", "report-template.md"),
)


class SoulTrongKhuon(unittest.TestCase):
    def test_khuon_tai_lieu(self):
        """5 khuôn tài liệu request đều phát dòng `Soul:` nguyên văn (spec đầu ra 14)."""
        for parts in TEMPLATES:
            with self.subTest(path="/".join(parts)):
                lines = _read(os.path.join(ROOT, *parts)).splitlines()
                soul = [l for l in lines if l.startswith("Soul:")]
                self.assertTrue(soul, "khuôn thiếu dòng bắt đầu bằng `Soul:`")
                self.assertIn(PRIORITY, soul[0],
                              "dòng Soul: phải chép nguyên văn thứ tự ưu tiên")
                self.assertIn("references/soul.md", soul[0],
                              "dòng Soul: phải trỏ về file luật gốc")


class SoulRequestDangMo(unittest.TestCase):
    """Soul phải nằm trong tài liệu của request ĐANG MỞ (spec đầu ra 15).

    Soi theo `active_request` của state.json nên test này giữ luật cho mọi request
    về sau, không riêng request tạo ra soul. File chưa sinh (vd plan khi đang phase
    spec) thì bỏ qua; không có request mở thì skip.
    """

    def test_soul_request_dang_mo(self):
        state_path = os.path.join(ROOT, "docs", "tdq", "state.json")
        if not os.path.exists(state_path):
            self.skipTest("chưa có state.json")
        with open(state_path, encoding="utf-8") as f:
            state = json.load(f)
        slug = state.get("active_request")
        if not slug or state.get("phase") in (None, "idle"):
            self.skipTest("không có request đang mở")
        found_any = False
        for kind in ("brief", "spec", "plan"):
            path = os.path.join(ROOT, "docs", "tdq", kind, f"{slug}.md")
            if not os.path.exists(path):
                continue
            found_any = True
            with self.subTest(kind=kind):
                head = _read(path).splitlines()[:6]
                soul = [l for l in head if l.startswith("Soul:")]
                self.assertTrue(
                    soul, f"{kind}/{slug}.md thiếu dòng `Soul:` trong 6 dòng đầu")
                self.assertIn(PRIORITY, soul[0])
        self.assertTrue(found_any, "request mở mà không có tài liệu nào để soi")


class SoulPointers(unittest.TestCase):
    def test_dong_tro_soul(self):
        for path, anchor in ((CONV_SKILL, "references/soul.md"), (AGENTS, "soul")):
            with self.subTest(path=os.path.relpath(path, ROOT)):
                text = _read(path)
                self.assertIn(PRIORITY, text,
                              "tầng luôn nạp phải in nguyên văn thứ tự ưu tiên")
                self.assertIn(anchor, text, "thiếu dòng trỏ về soul")


if __name__ == "__main__":
    unittest.main()
