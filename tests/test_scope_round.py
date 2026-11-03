"""Vòng scope — tầng tổng quát đứng trước vòng câu hỏi chi tiết của interview.

Bốn bất biến dễ trôi nhất nếu ai đó rút gọn file luật sau này:
1. Đủ 5 mục: khi nào chạy · chọn mặt · bối cảnh · suy mức đầu tư · ghi lại.
2. "Có điều kiện" phải có tiêu chí: danh sách dấu hiệu kích hoạt + luật ghi lý do khi BỎ.
3. Cấm hỏi mức độ trừu tượng ("gọn hay đầy đủ"), phải hỏi bối cảnh bằng số.
4. Mọi link tương đối trong file trỏ tới file có thật.
"""
import os
import re
import unittest

from helper import ROOT

SCOPE_ROUND = os.path.join(ROOT, "skills", "tdq-intake", "references", "scope-round.md")
LINK = re.compile(r"\[[^\]]+\]\(([^)#]+\.md)[^)]*\)")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


class ScopeRoundTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(os.path.exists(SCOPE_ROUND), "thiếu file luật scope-round.md")
        self.text = read(SCOPE_ROUND)

    def test_has_five_sections(self):
        heads = [ln for ln in self.text.splitlines() if ln.startswith("## ")]
        self.assertGreaterEqual(len(heads), 5, f"scope-round.md chỉ có {len(heads)} mục")

    def test_trigger_signs_are_a_closed_list(self):
        """Không liệt kê dấu hiệu thì 'có điều kiện' thành tuỳ hứng bỏ vòng scope."""
        for n in ("1.", "2.", "3.", "4."):
            self.assertIn(f"\n{n} ", self.text, f"thiếu dấu hiệu kích hoạt số {n}")

    def test_skipping_requires_a_written_reason(self):
        self.assertIn("Vòng scope: BỎ", self.text,
                      "scope-round.md: bỏ vòng scope mà không buộc ghi lý do")

    def test_bans_the_abstract_level_question(self):
        """Hỏi 'gọn hay đầy đủ' bắt user tự quy đổi thứ họ chưa biết — user đã loại."""
        self.assertRegex(self.text,
                         r"(?i)(BANNED[\s\S]{0,200}?minimal|cấm[\s\S]{0,200}?gọn nhất)",
                         "scope-round.md: thiếu luật cấm hỏi mức độ trừu tượng")

    def test_context_questions_ask_for_numbers(self):
        for token in ("CCU", "R&D", "target"):
            with self.subTest(token=token):
                self.assertIn(token, self.text, f"thiếu nhóm câu bối cảnh: {token}")

    def test_level_is_inferred_and_shown_back(self):
        self.assertIn("Tôi hiểu là", self.text,
                      "scope-round.md: suy ra mức đầu tư mà không nói lại cho user")

    def test_result_is_anchored_in_brief_and_spec(self):
        self.assertIn("### Phạm vi đã chốt", self.text)
        self.assertRegex(self.text, r"(?i)ngoài phạm vi",
                         "scope-round.md: mặt bị loại không được neo sang spec")

    def test_links_resolve(self):
        base = os.path.dirname(SCOPE_ROUND)
        for target in LINK.findall(self.text):
            with self.subTest(link=target):
                self.assertTrue(os.path.exists(os.path.join(base, target)),
                                f"link hỏng trong scope-round.md: {target}")


class ScopeRoundIsWiredTest(unittest.TestCase):
    """File luật có mà không chỗ nào trỏ tới thì vòng scope không bao giờ chạy."""

    CALLERS = (
        ("skills", "tdq-intake", "references", "interview.md"),
        ("skills", "tdq-intake", "references", "analyze-full.md"),
        ("skills", "tdq-intake", "references", "quick-lane.md"),
        ("skills", "tdq-intake", "SKILL.md"),
    )

    def test_every_caller_links_the_scope_round(self):
        for parts in self.CALLERS:
            with self.subTest(file=parts[-1]):
                self.assertIn("scope-round.md", read(os.path.join(ROOT, *parts)),
                              f"{parts[-1]}: không trỏ tới scope-round.md")

    def test_interview_keeps_the_detail_tier_inside_chosen_areas(self):
        text = read(os.path.join(ROOT, "skills", "tdq-intake", "references", "interview.md"))
        self.assertRegex(text, r"(?i)(tier 1[\s\S]{0,400}?tier 2|tầng 1[\s\S]{0,400}?tầng 2)",
                         "interview.md: mất thứ tự hai tầng tổng quát → chi tiết")


if __name__ == "__main__":
    unittest.main()
