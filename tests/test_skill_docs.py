"""Contract test cho skill docs — request skill-vao-goi-external (P4).

Đối tượng: khuôn AGENTS.md, khuôn gói external, nhánh external của tdq-build,
luật nhãn (mcp) của tdq-plan, quick lane. Chỉ đọc file, không chạy engine.
"""
import os
import re
import unittest

from helper import ROOT


def _read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class AgentsMdTemplateTest(unittest.TestCase):
    """T4.1 — skills/tdq-build/references/agents-md.md: nội dung AGENTS.md
    trong code fence, ≤60 dòng, mệnh lệnh tiếng Việt, đủ cụm bắt buộc."""

    def setUp(self):
        self.text = _read("skills", "tdq-build", "references", "agents-md.md")

    def _fence_body(self):
        match = re.search(r"```markdown\n(.*?)```", self.text, re.DOTALL)
        self.assertIsNotNone(match, "thiếu khối ```markdown chứa AGENTS.md")
        return match.group(1)

    def test_fence_at_most_60_lines(self):
        lines = self._fence_body().rstrip("\n").split("\n")
        self.assertLessEqual(len(lines), 60,
                             f"AGENTS.md trong fence {len(lines)} dòng (>60)")

    def test_required_phrases_in_fence(self):
        body = self._fence_body()
        low = body.lower()
        self.assertIn("`tests/`", body)          # unittest chạy từ tests/
        self.assertIn("python3 -m unittest", body)
        self.assertIn("red", low)                # red → green
        self.assertIn("green", low)
        self.assertIn("không commit", low)       # cấm engine commit
        self.assertIn('"kind"', body)            # format report kind=plan
        self.assertIn("test_result", body)

    def test_doc_says_delete_before_merge(self):
        low = self.text.lower()
        self.assertIn("xóa", low)
        self.assertIn("merge", low)


class ExternalTaskTemplateSkillTest(unittest.TestCase):
    """T4.2 — khuôn gói external-task.md: mục `## SKILL <tên> — <file>` đặt
    CUỐI gói + sinh bằng `skill-dump`, cho CẢ khuôn task đơn lẫn khuôn plan."""

    def setUp(self):
        self.text = _read("skills", "tdq-build", "references",
                          "external-task.md")

    def _fences(self):
        return re.findall(r"```markdown\n(.*?)```", self.text, re.DOTALL)

    def test_both_templates_end_with_skill_section(self):
        fences = [f for f in self._fences()
                  if f.startswith("# TASK") or f.startswith("# GÓI PLAN")]
        self.assertEqual(len(fences), 2, "phải có khuôn task đơn + khuôn plan")
        for fence in fences:
            with self.subTest(fence=fence.splitlines()[0]):
                pos = fence.find("## SKILL")
                self.assertGreater(pos, -1, "khuôn thiếu mục ## SKILL")
                # luật parser: từ dòng ## SKILL đầu tiên trở đi không còn TASK
                self.assertNotIn("## TASK", fence[pos:])

    def test_mentions_skill_dump_command(self):
        self.assertIn("skill-dump", self.text)


class TdqBuildExternalBranchTest(unittest.TestCase):
    """T4.3 — nhánh external của tdq-build SKILL.md: 6 cụm contract mới
    + 2 agent runner có `--plan-file`."""

    def setUp(self):
        self.text = _read("skills", "tdq-build", "SKILL.md")

    def test_six_contract_phrases(self):
        low = self.text.lower()
        self.assertIn("kể cả plan ≤6 task", low)          # LUÔN split-plan
        self.assertIn("split-plan", low)
        self.assertIn("agents-md.md", low)                # sinh AGENTS.md từ khuôn
        self.assertIn("skill-dump", low)                  # chép skill vào gói
        self.assertIn('"mcp": true', low)                 # gói mcp Claude tự làm
        self.assertIn("--plan-file", self.text)           # lệnh mẫu run-plan
        self.assertRegex(low, r"xóa `?agents\.md`? .*trước")  # xóa trước diff/merge

    def test_runner_agents_have_plan_file_flag(self):
        for name in ("codex-runner.md", "agy-runner.md"):
            with self.subTest(agent=name):
                self.assertIn("--plan-file", _read("agents", name))


class TdqPlanMcpLabelTest(unittest.TestCase):
    """T4.4 — tdq-plan SKILL.md + plan-template.md: luật bắt buộc nhãn `(mcp)`
    theo cú pháp chuẩn spec §1, ghi ngay trong bước lập plan."""

    def test_skill_md_states_mcp_label_law(self):
        text = _read("skills", "tdq-plan", "SKILL.md")
        self.assertIn("(mcp)", text)
        self.assertIn("MCP", text)

    def test_plan_template_shows_canonical_syntax(self):
        text = _read("skills", "tdq-plan", "references", "plan-template.md")
        self.assertIn("` (mcp)", text)      # nhãn NGOÀI backtick, cuối dòng
        self.assertIn("Dùng:", text)


class QuickLaneExternalSkillTest(unittest.TestCase):
    """T4.5 — quick external: gói task đơn cũng chép skill (skill-dump);
    task quick dùng skill (mcp) → không duyệt external."""

    def test_tdq_build_quick_packet_gets_skill_dump(self):
        text = _read("skills", "tdq-build", "SKILL.md")
        self.assertRegex(
            text, re.compile(r"quick.*?skill-dump|skill-dump.*?quick",
                             re.IGNORECASE | re.DOTALL))

    def test_tdq_intake_blocks_mcp_quick_external(self):
        text = _read("skills", "tdq-intake", "SKILL.md")
        self.assertIn("(mcp)", text)
        self.assertRegex(text, r"(?i)không.*duyệt.*external|external.*không")


class QuickLaneThinkingStepsTest(unittest.TestCase):
    """P4 — lane quick giữ đủ bước tư duy (search + interview) và gộp tài liệu
    thành MỘT file mini-spec/plan với đúng MỘT gate duyệt."""

    def setUp(self):
        self.skill = _read("skills", "tdq-intake", "SKILL.md")
        self.ref = _read("skills", "tdq-intake", "references", "quick-lane.md")

    def test_quick_keeps_search_and_interview(self):
        self.assertIn("tavily-primary", self.skill)
        self.assertIn("interview.md", self.skill)

    def test_quick_writes_one_merged_file(self):
        self.assertIn("mini-spec/plan", self.skill)
        self.assertIn("docs/tdq/plan/<slug>.md", self.skill)

    def test_reference_documents_the_template_and_limit(self):
        self.assertIn("40 dòng", self.ref)
        self.assertIn("Definition of Done", self.ref)
        self.assertIn("(mcp)", self.ref)

    def test_lane_decision_points_at_reference(self):
        self.assertIn("quick-lane.md",
                      _read("skills", "tdq-intake", "references", "lane-decision.md"))


class PortableExternalSyncTest(unittest.TestCase):
    """T5.1 — portable 03-plan/04-build phải mang cùng luật mới (mcp, split-plan
    luôn chạy, AGENTS.md, skill-dump, --plan-file) như bản skill."""

    def test_04_build_has_new_external_rules(self):
        text = re.sub(r"\s+", " ", _read("portable", "workflow", "04-build.md"))
        for phrase in ("kể cả plan ≤6 task", "skill-dump", "AGENTS.md",
                       "--plan-file", '"mcp": true'):
            self.assertIn(phrase, text, phrase)

    def test_03_plan_has_mcp_label_law(self):
        text = _read("portable", "workflow", "03-plan.md")
        self.assertIn("(mcp)", text)


if __name__ == "__main__":
    unittest.main()
