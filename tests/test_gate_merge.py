"""P3 — luật gộp gate: duyệt spec → plan NGAY, duyệt plan+mode → build NGAY.

Bốn bất biến dễ trôi ngược nhất khi ai đó sửa skill sau này:
1. Không skill nào bắt user chờ sang "turn mới" giữa spec → plan → build.
2. `tdq-reviewer` chỉ còn là lựa chọn gọi tay, không phải bước bắt buộc.
3. `PHASE_TABLE` (nguồn sự thật của hook) không còn cấm viết plan cùng turn với spec.
4. Vòng interview luôn kết thúc bằng câu hỏi mở cho user bổ sung.
"""
import os
import re
import unittest

from helper import ROOT, tdq_state

SKILLS = os.path.join(ROOT, "skills")
GATE_SKILLS = ("tdq-spec", "tdq-plan", "tdq-build")
# "turn mới"/"turn tiếp theo" = bắt user nhắn thêm một lượt nữa — chính thứ đã bỏ.
NEW_TURN = re.compile(r"turn\s+(mới|tiếp theo)", re.IGNORECASE)
ASK_MORE = "Bạn muốn bổ sung thêm gì không?"


def read(*parts):
    with open(os.path.join(*parts), encoding="utf-8") as f:
        return f.read()


class GateMergeTest(unittest.TestCase):
    def test_no_skill_forces_a_new_turn(self):
        for name in GATE_SKILLS:
            with self.subTest(skill=name):
                text = read(SKILLS, name, "SKILL.md")
                self.assertIsNone(NEW_TURN.search(text),
                                  f"{name}: còn bắt sang turn mới giữa spec/plan/build")

    def test_intake_hands_over_without_a_new_turn(self):
        text = read(SKILLS, "tdq-intake", "SKILL.md")
        self.assertIsNone(NEW_TURN.search(text), "tdq-intake: còn bắt sang turn mới")

    def test_reviewer_is_optional_only(self):
        for name in ("tdq-spec", "tdq-plan"):
            with self.subTest(skill=name):
                lines = [l for l in read(SKILLS, name, "SKILL.md").splitlines()
                         if "tdq-reviewer" in l]
                self.assertLessEqual(len(lines), 1,
                                     f"{name}: nhắc tdq-reviewer nhiều hơn 1 dòng")
                if lines:
                    self.assertRegex(lines[0], r"user yêu cầu|tùy chọn|khi cần",
                                     f"{name}: tdq-reviewer vẫn ở dạng bước bắt buộc")

    def test_phase_table_allows_same_turn_chain(self):
        spec = tdq_state.PHASE_TABLE["spec"]
        plan = tdq_state.PHASE_TABLE["plan"]
        self.assertNotIn("cùng turn với spec", spec["forbidden"])
        self.assertIn("CÙNG turn", " ".join(spec["checklist"]))
        self.assertIn("CÙNG turn", " ".join(plan["checklist"]))
        self.assertFalse(plan["checklist"][0].startswith("Hỏi user mode"),
                         "phase plan vẫn hỏi mode riêng một lượt")

    def test_interview_always_ends_with_open_question(self):
        text = read(SKILLS, "tdq-intake", "references", "interview.md")
        self.assertIn(ASK_MORE, text,
                      "interview.md thiếu câu hỏi mở bắt buộc cuối mỗi vòng")

    def test_route_section_is_required(self):
        """Bước quyết lộ trình phải có mặt ở intake (ghi) và spec (chép lại)."""
        self.assertIn("Lộ trình", read(SKILLS, "tdq-intake", "SKILL.md"))
        self.assertIn("Lộ trình", read(SKILLS, "tdq-spec", "SKILL.md"))
        self.assertIn("Lộ trình",
                      read(SKILLS, "tdq-spec", "references", "spec-template.md"))


if __name__ == "__main__":
    unittest.main()
