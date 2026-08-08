"""Contract test cho skill docs.

Đối tượng: luật nhãn (mcp) của tdq-plan, lane quick, các luật cắt token.
Chỉ đọc file, không chạy engine.
"""
import os
import re
import unittest

from helper import ROOT


def _read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


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

    def test_lane_decision_points_at_reference(self):
        self.assertIn("quick-lane.md",
                      _read("skills", "tdq-intake", "references", "lane-decision.md"))


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
                      ):
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

    def test_intake_giao_research_cho_subagent(self):
        """B1 — research chạy trong subagent, main chỉ nhận digest ≤1.500 ký tự."""
        # T3.1 tách Phần B ra references/analyze-full.md.
        text = _read("skills", "tdq-intake", "references", "analyze-full.md")
        self.assertIn("general-purpose", text)
        self.assertIn("1.500 ký tự", text)


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
        self.assertIn("<model>-<effort>-", self.conv)

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

    def test_khuon_mau_co_option_moi_dong(self):
        self.assertGreaterEqual(
            len(self.OPTION_LINE.findall(self.ref)), 2,
            "interview.md thiếu khuôn `- A (đề xuất): …` mỗi option một dòng")

    def test_de_xuat_dat_o_option_dau(self):
        first = self.OPTION_LINE.search(self.ref)
        self.assertIsNotNone(first, "interview.md không có option nào")
        self.assertIn("(đề xuất)", first.group(0),
                      "option đầu tiên phải là phương án đề xuất")

    def test_cam_gop_option_vao_doan_van(self):
        flat = re.sub(r"\s+", " ", self.ref)
        self.assertRegex(flat, r"(?i)(cấm|không) gộp.{0,60}(một dòng|đoạn văn)")

    def test_chot_lane_cung_dung_khuon(self):
        self.assertRegex(self.skill, r"- A \(đề xuất\): \*{0,2}quick")
        self.assertRegex(self.skill, r"- B: \*{0,2}full")

    def test_khong_con_uu_tien_askuserquestion(self):
        for name, text in (("interview.md", self.ref),
                           ("SKILL.md", self.skill)):
            with self.subTest(file=name):
                self.assertNotIn("AskUserQuestion nếu có", text)

    def test_luat_hoi_bang_danh_sach_trong_chat(self):
        self.assertRegex(self.ref, r"(?i)luôn hỏi bằng danh sách")


if __name__ == "__main__":
    unittest.main()
