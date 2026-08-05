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
        # T2.3 (toi-uu-p0-p1-workflow) tách "Nhánh external" ra khỏi SKILL.md —
        # 6 cụm contract giờ sống ở references/external-build.md.
        self.text = _read("skills", "tdq-build", "references", "external-build.md")

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
        # T2.3 tách nội dung này ra references/external-build.md.
        text = _read("skills", "tdq-build", "references", "external-build.md")
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


class TokenOptimRulesTest(unittest.TestCase):
    """Request thuc-thi-p0-token — 5 luật P0 cắt carry-cost phải nằm trong skill
    (không nằm ở ~/.claude/CLAUDE.md, để context nền không phình)."""

    def test_status_goi_next_brief(self):
        """A4b — `next` đầy đủ 1.350 ký tự, `--brief` 121."""
        self.assertIn("next --brief", _read("skills", "tdq-status", "SKILL.md"))

    def test_conventions_cam_lint_ca_thu_muc(self):
        """A5′ — nguồn thật của 2,6M carry-cost là lint cả thư mục (8.092 ký tự)."""
        text = _read("skills", "tdq-conventions", "SKILL.md")
        self.assertIn("doc_lint", text)
        self.assertRegex(text, r"(?i)cấm.{0,40}thư mục|thư mục.{0,40}cấm")

    def test_khong_skill_nao_con_day_lint_ca_thu_muc(self):
        pattern = re.compile(r"doc_lint\.py[^\n]*\sdocs/tdq(?![\w/])")
        for parts in (("skills", "tdq-conventions", "SKILL.md"),
                      ("skills", "tdq-spec", "SKILL.md"),
                      ("skills", "tdq-plan", "SKILL.md"),
                      ("skills", "tdq-build", "references", "qc.md"),
                      ("portable", "workflow", "02-spec.md"),
                      ("portable", "workflow", "03-plan.md")):
            with self.subTest(file=parts[-1]):
                self.assertIsNone(pattern.search(_read(*parts)),
                                  "còn dạy lint cả thư mục docs/tdq")

    def test_conventions_co_luat_gop_lenh_bash(self):
        """D1 — gộp 2–5 lệnh Bash độc lập vào 1 call (mỗi call = 1 API call)."""
        text = _read("skills", "tdq-conventions", "SKILL.md")
        self.assertRegex(text, r"(?i)gộp.{0,80}lệnh|lệnh.{0,80}gộp")
        self.assertIn("&&", text)

    def test_build_chay_test_theo_module(self):
        """D2 — implement chạy test module; full suite đúng 1 lần ở QC."""
        text = _read("skills", "tdq-build", "SKILL.md")
        self.assertIn("test của module", text)
        self.assertRegex(text, r"(?i)full suite.{0,120}(qc|đúng 1 lần|một lần)")

    def test_intake_giao_research_cho_search_scout(self):
        """B1 — research chạy trong subagent, main chỉ nhận digest ≤1.500 ký tự."""
        # T3.1 tách Phần B ra references/analyze-full.md.
        text = _read("skills", "tdq-intake", "references", "analyze-full.md")
        self.assertIn("search-scout", text)
        self.assertIn("1.500 ký tự", text)

    def test_portable_mang_cung_luat(self):
        self.assertIn("search-scout",
                      _read("portable", "workflow", "references", "analyze-full.md"))
        self.assertIn("test của module", _read("portable", "workflow", "04-build.md"))


class TokenOptimVong2RulesTest(unittest.TestCase):
    """Request toi-uu-token-vong-2 (P4) — 8 luật vòng 2 phải nằm trong skill,
    không nằm ở `~/.claude/CLAUDE.md`."""

    def setUp(self):
        self.conv = _read("skills", "tdq-conventions", "SKILL.md")

    def test_b3_khong_chay_lai_next_khi_hook_da_in(self):
        self.assertIn("[TDQ:NEXT]", self.conv)
        self.assertRegex(self.conv, r"(?i)\[TDQ:NEXT\][^\n]{0,120}(không chạy|cấm chạy)")

    def test_b2_gop_tool_call_doc_lap_trong_mot_luot(self):
        self.assertRegex(self.conv, r"(?i)2–5 tool call|2-5 tool call")
        self.assertRegex(self.conv, r"(?i)(cùng một lượt|cùng 1 lượt|một lượt)")

    def test_c1_working_log_ghi_bang_tdq_finish(self):
        self.assertIn("tdq_finish.py", self.conv)
        self.assertRegex(self.conv, r"(?i)(cấm|không) Read lại")

    def test_c2_nguong_200_dong_moi_read_theo_offset(self):
        self.assertRegex(self.conv, r"(?i)200 dòng")
        self.assertIn("offset", self.conv)

    def test_d1_ten_agent_co_model_va_effort(self):
        self.assertIn("<model>-<effort>_", self.conv)

    def test_e2_khong_doi_model_effort_giua_phase_build(self):
        self.assertRegex(
            self.conv,
            r"(?i)(không|cấm) đổi (model|`model`)[^\n]{0,80}(effort|`effort`)[^\n]{0,80}(phase|giữa chừng)")

    def test_d4_plan_tren_6_task_de_xuat_subagent(self):
        text = _read("skills", "tdq-plan", "SKILL.md")
        self.assertRegex(text, r"(?i)(>|trên |hơn )\s?6 task")
        self.assertRegex(text, r"(?i)đề xuất[^\n]{0,80}subagent")
        self.assertRegex(text, r"(?i)user[^\n]{0,60}chốt")

    def test_t43_build_dung_mot_lenh_tdq_finish(self):
        text = _read("skills", "tdq-build", "SKILL.md")
        self.assertIn("tdq_finish.py", text)

    def test_portable_mang_cung_luat_vong_2(self):
        self.assertIn("tdq_finish.py", _read("portable", "workflow", "04-build.md"))
        self.assertRegex(_read("portable", "workflow", "03-plan.md"),
                         r"(?i)(>|trên |hơn )\s?6 task")


class OptionMotDongTest(unittest.TestCase):
    """Request format-cau-hoi-interview — mọi câu hỏi có option phải xuống dòng
    từng option theo khuôn `- A (đề xuất): nội dung`, không gộp vào đoạn văn,
    và không còn ưu tiên AskUserQuestion."""

    # option có thể nằm trong khối lệnh thụt lề của danh sách đánh số → cho phép
    # khoảng trắng đầu dòng, nhưng nhãn phải là đúng 1 chữ HOA rồi tới dấu `:`.
    OPTION_LINE = re.compile(r"^\s*- [A-Z](?: \(đề xuất\))?: ", re.MULTILINE)

    def setUp(self):
        self.ref = _read("skills", "tdq-intake", "references", "interview.md")
        self.skill = _read("skills", "tdq-intake", "SKILL.md")
        self.portable = _read("portable", "workflow", "01-intake.md")
        # T3.1 tách phần "Vòng interview" (kèm luật cấm gộp option) ra
        # references/analyze-full.md ở cả hai bản skill lẫn portable.
        self.portable_analyze = _read("portable", "workflow", "references", "analyze-full.md")

    def test_khuon_mau_co_option_moi_dong(self):
        for name, text in (("interview.md", self.ref),
                           ("01-intake.md", self.portable)):
            with self.subTest(file=name):
                self.assertGreaterEqual(
                    len(self.OPTION_LINE.findall(text)), 2,
                    f"{name} thiếu khuôn `- A (đề xuất): …` mỗi option một dòng")

    def test_de_xuat_dat_o_option_dau(self):
        for name, text in (("interview.md", self.ref),
                           ("01-intake.md", self.portable)):
            with self.subTest(file=name):
                first = self.OPTION_LINE.search(text)
                self.assertIsNotNone(first, f"{name} không có option nào")
                self.assertIn("(đề xuất)", first.group(0),
                              f"{name}: option đầu tiên phải là phương án đề xuất")

    def test_cam_gop_option_vao_doan_van(self):
        for name, text in (("interview.md", self.ref),
                           ("analyze-full.md", self.portable_analyze)):
            with self.subTest(file=name):
                flat = re.sub(r"\s+", " ", text)
                self.assertRegex(flat, r"(?i)(cấm|không) gộp.{0,60}(một dòng|đoạn văn)")

    def test_chot_lane_cung_dung_khuon(self):
        for name, text in (("SKILL.md", self.skill),
                           ("01-intake.md", self.portable)):
            with self.subTest(file=name):
                self.assertRegex(text, r"- A \(đề xuất\): \*{0,2}quick")
                self.assertRegex(text, r"- B: \*{0,2}full")

    def test_khong_con_uu_tien_askuserquestion(self):
        for name, text in (("interview.md", self.ref),
                           ("SKILL.md", self.skill),
                           ("01-intake.md", self.portable)):
            with self.subTest(file=name):
                self.assertNotIn("AskUserQuestion nếu có", text)

    def test_luat_hoi_bang_danh_sach_trong_chat(self):
        self.assertRegex(self.ref, r"(?i)luôn hỏi bằng danh sách")


if __name__ == "__main__":
    unittest.main()
