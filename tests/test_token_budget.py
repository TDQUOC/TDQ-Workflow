"""P5 — ngân sách token của spec §2.7, đo thật chứ không phải khuyến nghị.

Mỗi ký tự hook bơm vào ngữ cảnh là ký tự user phải trả tiền, và với model nhỏ thì
context dài còn làm loãng chỉ dẫn. Vượt trần = FAIL, không có ngoại lệ mềm.
"""
import json
import os
import tempfile
import unittest

from helper import ROOT, decision, load_fixture, run_hook, tdq_state, write_file, write_state

PHASES = ("analyze", "spec", "plan", "implement", "qc", "report")


def budget(test, text, max_lines, max_chars, label):
    test.assertLessEqual(len(text.splitlines()), max_lines, f"{label}: quá số dòng")
    test.assertLessEqual(len(text), max_chars, f"{label}: quá số ký tự")


class TokenBudgetTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def each_phase(self):
        """Sinh state cho mọi phase — trần phải đúng ở phase dài nhất, không chỉ phase dễ."""
        for phase in PHASES:
            write_state(self.cwd, active_request="2026-07-28-mot-request-ten-kha-dai",
                        lane="full", phase=phase, spec_approved=True, plan_approved=True,
                        implement_mode="subagent",
                        spec_file="docs/tdq/spec/x.md", plan_file="docs/tdq/plan/x.md")
            yield phase

    def test_session_start(self):
        for phase in self.each_phase():
            _, out, _ = run_hook("session_start.py", {"cwd": self.cwd, "session_id": "b1"})
            budget(self, out, 12, 600, f"SessionStart/{phase}")

    def test_user_prompt_submit(self):
        for phase in self.each_phase():
            payload = load_fixture("prompt.json", cwd=self.cwd, session_id=f"b2{phase}")
            _, out, _ = run_hook("prompt_context.py", payload)
            budget(self, out, 3, 240, f"UserPromptSubmit/{phase}")

    def test_pre_tool_use(self):
        write_file(self.cwd, "src/app.py")
        for phase in self.each_phase():
            payload = load_fixture("edit_src.json", cwd=self.cwd, session_id=f"b3{phase}")
            _, out, _ = run_hook("edit_gate.py", payload)
            _, context = decision(out)
            budget(self, context, 3, 200, f"PreToolUse/{phase}")

    def test_stop(self):
        for phase in self.each_phase():
            payload = load_fixture("stop.json", cwd=self.cwd, session_id=f"b4{phase}")
            _, out, _ = run_hook("stop_gate.py", payload)
            reason = json.loads(out).get("reason", "") if out else ""
            budget(self, reason, 4, 300, f"Stop/{phase}")

    def test_state_md_mirror(self):
        for phase in self.each_phase():
            state = tdq_state.load(self.cwd)
            text = tdq_state.render_state_md(self.cwd, state)
            self.assertLessEqual(len(text.splitlines()), 30, f"STATE.md/{phase}")

    def test_next_output(self):
        for phase in self.each_phase():
            state = tdq_state.load(self.cwd)
            full = tdq_state.render_next(self.cwd, state)
            self.assertLessEqual(len(full.splitlines()), 20, f"next/{phase}")
            brief = tdq_state.render_next(self.cwd, state, brief=True)
            self.assertEqual(len(brief.strip().splitlines()), 1, f"next --brief/{phase}")

    def test_skill_descriptions_total(self):
        """description của mọi skill luôn nằm trong context — tổng phải gọn."""
        total = 0
        skills_dir = os.path.join(ROOT, "skills")
        for name in sorted(os.listdir(skills_dir)):
            path = os.path.join(skills_dir, name, "SKILL.md")
            if not os.path.isfile(path):
                continue
            with open(path, encoding="utf-8") as f:
                for line in f:
                    if line.startswith("description:"):
                        total += len(line.split(":", 1)[1].strip())
                        break
        self.assertGreater(total, 0, "không đọc được description nào")
        self.assertLessEqual(total, 900, f"tổng description = {total} ký tự")

    def test_reference_files_bounded(self):
        for root in (os.path.join(ROOT, "skills"), os.path.join(ROOT, "portable")):
            for dirpath, _, files in os.walk(root):
                if os.path.basename(dirpath) != "references":
                    continue
                for name in sorted(files):
                    if not name.endswith(".md"):
                        continue
                    path = os.path.join(dirpath, name)
                    with open(path, encoding="utf-8") as f:
                        count = len(f.read().splitlines())
                    self.assertLessEqual(count, 200, f"{path}: {count} dòng")


if __name__ == "__main__":
    unittest.main()
