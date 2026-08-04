"""P2 — mọi agent phải khai rõ `model` và `effort` trong frontmatter.

Lý do: `effort` CHỈ đặt được ở frontmatter (Agent tool không có tham số `effort`),
nên bỏ trống = agent chạy theo mức của phiên, không kiểm soát được chi phí/chất
lượng. `model` khai sẵn để agent cơ học không đắt theo model user đang bật.
Bảng mặc định + lý do: skills/tdq-conventions/references/subagent-tuning.md.
"""
import os
import re
import unittest

from helper import ROOT

AGENTS = os.path.join(ROOT, "agents")
MODEL_ALIASES = {"sonnet", "opus", "haiku", "fable", "inherit"}
MODEL_ID = re.compile(r"^claude-[\w.-]+$")
EFFORTS = {"low", "medium", "high", "xhigh", "max"}
FIELD = r"^{}:\s*(.+?)\s*$"


def frontmatter(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if not text.startswith("---\n"):
        return None
    return text.split("---", 2)[1]


def field(head, name):
    match = re.search(FIELD.format(name), head, re.MULTILINE)
    return match.group(1) if match else None


class AgentFrontmatterTest(unittest.TestCase):
    def agent_files(self):
        names = sorted(n for n in os.listdir(AGENTS) if n.endswith(".md"))
        self.assertTrue(names, "không tìm thấy file agent nào")
        return names

    def test_every_agent_declares_model_and_effort(self):
        for name in self.agent_files():
            with self.subTest(agent=name):
                head = frontmatter(os.path.join(AGENTS, name))
                self.assertIsNotNone(head, f"{name}: thiếu frontmatter")
                model = field(head, "model")
                effort = field(head, "effort")
                self.assertIsNotNone(model, f"{name}: thiếu trường model")
                self.assertIsNotNone(effort, f"{name}: thiếu trường effort")
                self.assertTrue(
                    model in MODEL_ALIASES or MODEL_ID.match(model),
                    f"{name}: model {model!r} không hợp lệ")
                self.assertIn(effort, EFFORTS, f"{name}: effort {effort!r} không hợp lệ")

    def test_mechanical_runners_stay_cheap(self):
        """Runner chỉ bọc script — để mức cao là đốt tiền vô ích."""
        for name in ("codex-runner.md", "agy-runner.md", "search-runner.md"):
            with self.subTest(agent=name):
                head = frontmatter(os.path.join(AGENTS, name))
                self.assertEqual(field(head, "effort"), "low")
                self.assertEqual(field(head, "model"), "haiku")

    def test_quality_agents_are_not_throttled(self):
        """Agent làm việc chất lượng không được ép nghĩ nông (effort thấp)."""
        for name in ("tdq-implementer.md", "tdq-qc-tester.md", "tdq-reviewer.md"):
            with self.subTest(agent=name):
                head = frontmatter(os.path.join(AGENTS, name))
                self.assertIn(field(head, "effort"), {"high", "xhigh", "max"})

    def test_tuning_reference_exists_and_lists_every_agent(self):
        ref = os.path.join(ROOT, "skills", "tdq-conventions", "references",
                           "subagent-tuning.md")
        self.assertTrue(os.path.isfile(ref), "thiếu references/subagent-tuning.md")
        with open(ref, encoding="utf-8") as f:
            text = f.read()
        for name in self.agent_files():
            self.assertIn(name[:-3], text, f"subagent-tuning.md thiếu dòng cho {name}")


if __name__ == "__main__":
    unittest.main()
