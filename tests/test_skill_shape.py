"""P3 — hình dạng bắt buộc của 6 skill sau khi gộp 9 → 5 (+conventions).

Mục tiêu: model yếu vẫn đi đúng. Nên mỗi skill phải có bước ĐÁNH SỐ liên tục,
mốc `Xong khi:` và con trỏ `Bước kế tiếp:` — không để agent tự đoán đi đâu.
"""
import os
import re
import unittest

from helper import ROOT, tdq_state
import doc_lint

SKILLS = os.path.join(ROOT, "skills")
# tên skill → trần số dòng SKILL.md (spec §2.4). Một nguồn duy nhất, dùng chung
# với scripts/doc_lint.py để hai nơi không lệch ngưỡng.
LIMITS = doc_lint.SKILL_LINE_LIMITS
# `(?!-)` để "tdq-qc-tester"/"tdq-implementer" (tên agent còn dùng) không bị tính là
# tham chiếu tới skill "tdq-qc"/"tdq-implement" đã xoá.
GONE = ["tdq-approve", "tdq-start", "tdq-analyze", "tdq-implement", "tdq-qc", "tdq-report"]
GONE_RE = {old: re.compile(re.escape(old) + r"(?![-\w])") for old in GONE}
STEP = re.compile(r"^(\d+)\.\s+\S", re.MULTILINE)


def read(name):
    with open(os.path.join(SKILLS, name, "SKILL.md"), encoding="utf-8") as f:
        return f.read()


class ReadOnlyAgentToolsTest(unittest.TestCase):
    """A11 — agent chỉ-đọc phải khai `tools:` không có Edit/Write (mặc định là ALL)."""

    NAMES = ("tdq-qc-tester.md", "tdq-reviewer.md")

    def test_frontmatter_tools_read_only(self):
        for name in self.NAMES:
            with self.subTest(agent=name):
                path = os.path.join(ROOT, "agents", name)
                with open(path, encoding="utf-8") as f:
                    head = f.read().split("---", 2)[1]
                match = re.search(r"^tools:\s*(.+)$", head, re.MULTILINE)
                self.assertIsNotNone(match, f"{name} thiếu dòng tools:")
                self.assertNotIn("Edit", match.group(1))
                self.assertNotIn("Write", match.group(1))


class SkillShapeTest(unittest.TestCase):
    def assert_shape(self, name):
        path = os.path.join(SKILLS, name, "SKILL.md")
        self.assertTrue(os.path.isfile(path), f"thiếu {path}")
        text = read(name)
        self.assertLessEqual(len(text.splitlines()), LIMITS[name], f"{name} quá dài")
        self.assertTrue(text.startswith("---\n"), f"{name}: thiếu frontmatter")
        self.assertIn("name: " + name, text)
        self.assertIn("description:", text)
        return text

    def assert_steps(self, name, text):
        numbers = [int(n) for n in STEP.findall(text)]
        self.assertTrue(numbers, f"{name}: không có bước đánh số")
        self.assertEqual(numbers[0], 1, f"{name}: bước đầu phải là 1")
        for prev, cur in zip(numbers, numbers[1:]):
            self.assertIn(cur, (prev + 1, 1), f"{name}: số bước nhảy {prev} → {cur}")
        # Từ 2026-08-22 thân skill viết tiếng Anh; nhận cả hai cách viết hai mốc này.
        self.assertTrue(any(m in text for m in ("Done when:", "Xong khi:")),
                        f"{name}: thiếu mốc hoàn thành")
        self.assertTrue(any(m in text for m in ("Next step:", "Bước kế tiếp:")),
                        f"{name}: thiếu con trỏ bước sau")

    def test_intake_shape(self):
        text = self.assert_shape("tdq-intake")
        self.assert_steps("tdq-intake", text)
        for ref in ("references/lane-decision.md", "references/interview.md"):
            self.assertIn(ref, text)
            self.assertTrue(os.path.isfile(os.path.join(SKILLS, "tdq-intake", ref)), ref)

    def test_spec_shape(self):
        text = self.assert_shape("tdq-spec")
        self.assert_steps("tdq-spec", text)
        self.assertIn("references/spec-template.md", text)
        self.assertTrue(os.path.isfile(
            os.path.join(SKILLS, "tdq-spec", "references", "spec-template.md")))

    def test_plan_shape(self):
        text = self.assert_shape("tdq-plan")
        self.assert_steps("tdq-plan", text)
        self.assertIn("references/plan-template.md", text)
        self.assertTrue(os.path.isfile(
            os.path.join(SKILLS, "tdq-plan", "references", "plan-template.md")))

    def test_build_shape(self):
        text = self.assert_shape("tdq-build")
        self.assert_steps("tdq-build", text)
        for ref in ("references/qc.md", "references/report-template.md"):
            self.assertIn(ref, text)
            self.assertTrue(os.path.isfile(os.path.join(SKILLS, "tdq-build", ref)), ref)

    def test_status_shape(self):
        text = self.assert_shape("tdq-status")
        # C5: status phải hiện mode thực thi và ai đã duyệt
        self.assertIn("implement_mode", text)
        self.assertIn("_approved_by", text)

    def test_check_status_shape(self):
        text = self.assert_shape("tdq-check-status")
        self.assert_steps("tdq-check-status", text)
        for ref in ("references/report-template.md", "references/bang-lech.md"):
            self.assertIn(ref, text)
            self.assertTrue(os.path.isfile(
                os.path.join(SKILLS, "tdq-check-status", ref)), ref)
        # luật không mất dữ liệu phải nằm ở THÂN skill, không đẩy xuống reference
        self.assertTrue(any(m in text for m in ("Absolutely banned:", "Cấm tuyệt đối")),
                        "thiếu luật cấm init/reset ở thân skill")
        for ho in ("tdq_state.py set", "tdq_state.py approve"):
            self.assertIn(ho, text)

    def test_conventions_shape(self):
        text = self.assert_shape("tdq-conventions")
        for ref in ("references/phases.md", "references/approval.md",
                    "references/reminder-codes.md", "references/tavily.md"):
            self.assertIn(ref, text)
            self.assertTrue(os.path.isfile(os.path.join(SKILLS, "tdq-conventions", ref)), ref)

    def test_exactly_six_skills(self):
        dirs = sorted(d for d in os.listdir(SKILLS)
                      if os.path.isdir(os.path.join(SKILLS, d)))
        self.assertEqual(dirs, sorted(LIMITS))

    def test_no_stale_skill_refs(self):
        roots = [SKILLS, os.path.join(ROOT, "agents"), os.path.join(ROOT, "hooks"),
                 ]
        hits = []
        for root in roots:
            for dirpath, _, files in os.walk(root):
                for fname in files:
                    if not fname.endswith((".md", ".py", ".json")):
                        continue
                    path = os.path.join(dirpath, fname)
                    with open(path, encoding="utf-8", errors="replace") as f:
                        body = f.read()
                    for old, pattern in GONE_RE.items():
                        if pattern.search(body):
                            hits.append(f"{path}: {old}")
        readme = os.path.join(ROOT, "README.md")
        with open(readme, encoding="utf-8") as f:
            body = f.read()
        hits += [f"README.md: {old}" for old, p in GONE_RE.items() if p.search(body)]
        self.assertEqual(hits, [], "còn tham chiếu skill đã xoá")

    def test_reminder_codes_doc_lists_every_code(self):
        path = os.path.join(SKILLS, "tdq-conventions", "references", "reminder-codes.md")
        with open(path, encoding="utf-8") as f:
            text = f.read()
        for code in ("TDQ:NEXT", "TDQ:APPROVE", "TDQ:LOG", "TDQ:STATE", "TDQ:GIT"):
            self.assertIn(code, text)

    def test_conventions_matches_constant(self):
        """SKILL.md của conventions phải trỏ tới doc phase tự sinh, không chép tay."""
        text = read("tdq-conventions")
        self.assertIn("references/phases.md", text)
        for cmd in {row["cmd"] for row in tdq_state.PHASE_TABLE.values()}:
            self.assertNotIn(cmd, text.replace("phases.md", ""),
                             "conventions chép lại lệnh phase — phải trỏ sang phases.md")


if __name__ == "__main__":
    unittest.main()
