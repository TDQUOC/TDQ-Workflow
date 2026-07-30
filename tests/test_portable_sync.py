"""P4 — bản portable (chạy ngoài Claude Code) phải tồn tại và KHÔNG lệch với skills.

Lệch nội dung giữa hai bản là lỗi âm thầm nguy hiểm nhất của bộ này: agent ngoài
Claude Code sẽ đi theo phiên bản cũ mà không ai biết. Nên danh sách bước phải khớp
từng dòng sau khi chuẩn hoá (bỏ thứ riêng của Claude Code).
"""
import os
import re
import unittest

from helper import ROOT

PORTABLE = os.path.join(ROOT, "portable")
SKILLS = os.path.join(ROOT, "skills")
# file portable → skill tương ứng
MAPPING = {
    "01-intake.md": "tdq-intake",
    "02-spec.md": "tdq-spec",
    "03-plan.md": "tdq-plan",
    "04-build.md": "tdq-build",
}
STEP = re.compile(r"^(\d+)\.\s+(.+)$", re.MULTILINE)
LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def steps(text):
    """Danh sách bước đã chuẩn hoá: bỏ link, bỏ đậm, bỏ đường dẫn riêng của plugin."""
    out = []
    for _, body in STEP.findall(text):
        body = LINK.sub(r"\1", body).replace("**", "").replace('"', "")
        # plugin chạy script qua ${CLAUDE_PLUGIN_ROOT}, portable chạy bản copy trong repo
        body = body.replace("${CLAUDE_PLUGIN_ROOT}/scripts/", "scripts/")
        out.append(re.sub(r"\s+", " ", body).strip().lower())
    return out


class PortableSyncTest(unittest.TestCase):
    def test_agents_md_shape(self):
        path = os.path.join(PORTABLE, "AGENTS.md")
        self.assertTrue(os.path.isfile(path), "thiếu portable/AGENTS.md")
        text = read(path)
        self.assertLessEqual(len(text.splitlines()), 200, "AGENTS.md quá dài")
        # harness ngoài không có hook → phải tự gọi `next`
        self.assertIn("scripts/tdq_state.py next", text)
        self.assertNotIn("CLAUDE_PLUGIN_ROOT", text)
        for name in MAPPING:
            self.assertIn(f"workflow/{name}", text, f"AGENTS.md không trỏ tới {name}")

    def test_workflow_files_exist_and_bounded(self):
        for name in MAPPING:
            path = os.path.join(PORTABLE, "workflow", name)
            with self.subTest(file=name):
                self.assertTrue(os.path.isfile(path), f"thiếu {path}")
                text = read(path)
                self.assertLessEqual(len(text.splitlines()), 200, f"{name} quá dài")
                self.assertNotIn("CLAUDE_PLUGIN_ROOT", text)
                self.assertIn("Xong khi:", text)
                self.assertIn("Bước kế tiếp:", text)

    def test_readme_bounded(self):
        path = os.path.join(PORTABLE, "README.md")
        self.assertTrue(os.path.isfile(path), "thiếu portable/README.md")
        text = read(path)
        self.assertLessEqual(len(text.splitlines()), 10, "README portable quá dài")
        self.assertIn("Python 3", text)
        self.assertIn("AGENTS.md", text)

    def test_steps_match_skills(self):
        for name, skill in MAPPING.items():
            with self.subTest(file=name):
                want = steps(read(os.path.join(SKILLS, skill, "SKILL.md")))
                got = steps(read(os.path.join(PORTABLE, "workflow", name)))
                self.assertEqual(want, got, f"{name} lệch bước so với {skill}")


if __name__ == "__main__":
    unittest.main()
