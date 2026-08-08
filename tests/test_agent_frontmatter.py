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


class AgentDigestLimitTest(unittest.TestCase):
    """Request toi-uu-token-vong-2 (T5.1/T5.2) — agent trả DIGEST, không trả
    nguyên output tool: thân agent phải nêu ngưỡng ≤ 1.500 ký tự và cấm dán thô."""

    def agent_files(self):
        return sorted(n for n in os.listdir(AGENTS) if n.endswith(".md"))

    def _body(self, name):
        with open(os.path.join(AGENTS, name), encoding="utf-8") as f:
            text = f.read()
        return text.split("---", 2)[2] if text.startswith("---\n") else text

    def test_moi_agent_neu_nguong_digest(self):
        for name in self.agent_files():
            with self.subTest(agent=name):
                self.assertIn("1.500 ký tự", self._body(name),
                              f"{name}: thiếu ngưỡng digest ≤ 1.500 ký tự")

    def test_moi_agent_cam_dan_output_tool_tho(self):
        pattern = re.compile(r"(?i)(cấm|không) dán[^\n]{0,60}(thô|nguyên văn output|toàn bộ output)")
        for name in self.agent_files():
            with self.subTest(agent=name):
                self.assertRegex(self._body(name), pattern,
                                 f"{name}: thiếu câu cấm dán kết quả tool thô")


if __name__ == "__main__":
    unittest.main()
