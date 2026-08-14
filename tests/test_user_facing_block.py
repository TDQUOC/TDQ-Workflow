"""Khuôn khối nói với user (conventions §1 mục 6).

Ba bất biến dễ trôi:
1. File khuôn tồn tại và nêu đủ 5 thành phần + 7 chỗ phải dùng.
2. Khuôn cấm emoji — và bản thân file khuôn cũng không được chứa emoji.
3. Mọi skill có chỗ nói với user đều trỏ về file khuôn thay vì tự chế khuôn riêng.
"""
import os
import re
import unittest

from helper import ROOT

SKILLS = os.path.join(ROOT, "skills")
BLOCK = os.path.join(SKILLS, "tdq-conventions", "references", "user-facing-block.md")
# Dải emoji hay gặp; `➤` (U+27A4) nằm ngoài các dải này nên vẫn hợp lệ.
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-⛿✅❌⚠]")
# Skill nào có chỗ hỏi/trình cho user thì phải trỏ về khuôn chung.
POINTERS = (
    ("tdq-conventions", "SKILL.md"),
    ("tdq-spec", "SKILL.md"),
    ("tdq-plan", "SKILL.md"),
    # Khối hỏi commit của tdq-build nằm ở references/report-template.md từ Đ3
    # (thân SKILL.md chỉ còn dòng trỏ) — kiểm đúng chỗ đang giữ khuôn.
    ("tdq-build", "references", "report-template.md"),
    ("tdq-intake", "references", "lane-decision.md"),
    ("tdq-intake", "references", "interview.md"),
    ("tdq-intake", "references", "quick-lane.md"),
)


def read(*parts):
    with open(os.path.join(*parts), encoding="utf-8") as f:
        return f.read()


class UserFacingBlockTest(unittest.TestCase):
    def test_block_file_exists(self):
        self.assertTrue(os.path.isfile(BLOCK), "thiếu references/user-facing-block.md")

    def test_lists_five_components(self):
        text = read(BLOCK)
        for token in ("Câu dẫn", "Nội dung", "Đường dẫn file", "Đường kẻ ngăn", "Khối trả lời"):
            with self.subTest(component=token):
                self.assertIn(token, text, f"khuôn thiếu thành phần: {token}")

    def test_lists_seven_touchpoints(self):
        text = read(BLOCK)
        for token in ("pipeline", "interview", "spec", "plan", "mode",
                      "chế độ nhanh", "commit"):
            with self.subTest(touchpoint=token):
                self.assertIn(token, text, f"khuôn thiếu chỗ giao tiếp: {token}")

    def test_bans_emoji_and_has_no_emoji_itself(self):
        text = read(BLOCK)
        self.assertIn("Không emoji", text, "khuôn không nêu luật cấm emoji")
        found = EMOJI.search(text)
        self.assertIsNone(found, f"chính file khuôn còn emoji: {found and found.group(0)!r}")

    def test_every_user_facing_skill_points_here(self):
        for parts in POINTERS:
            with self.subTest(file="/".join(parts)):
                self.assertIn("user-facing-block", read(SKILLS, *parts),
                              "file này nói với user nhưng không trỏ về khuôn chung")


if __name__ == "__main__":
    unittest.main()
