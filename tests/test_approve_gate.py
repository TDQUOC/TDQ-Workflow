"""B1 — approve_gate.py: validate by state + registered detail file."""
import tempfile
import unittest

from helper import run_hook, load_fixture, write_state, read_state, write_file
import tdq_state


def approve(cwd, arg):
    return run_hook("approve_gate.py", load_fixture("approve.json", cwd=cwd, command_args=arg))


class TestApproveGate(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def test_green_spec_sets_detail(self):
        write_state(self.cwd, active_request="r1", lane="full", phase="spec",
                    spec_file="docs/tdq/spec/x.md")
        path = write_file(self.cwd, "docs/tdq/spec/x.md", "# spec noi dung\n")
        rc, out, err = approve(self.cwd, "spec")
        self.assertEqual(rc, 0, err)
        self.assertIn("APPROVED SPEC", out)
        state = read_state(self.cwd)
        self.assertTrue(state["spec_approved"])
        self.assertEqual(state["spec_sha256"], tdq_state.sha256_file(path))
        self.assertIsNotNone(state["spec_approved_at"])

    def test_red_plan_before_spec(self):
        write_state(self.cwd, active_request="r1", lane="full", phase="plan",
                    plan_file="docs/tdq/plan/x.md")
        write_file(self.cwd, "docs/tdq/plan/x.md")
        rc, _, err = approve(self.cwd, "plan")
        self.assertEqual(rc, 2)
        self.assertIn("thứ tự", err)
        self.assertFalse(read_state(self.cwd)["plan_approved"])

    def test_red_spec_file_missing(self):
        write_state(self.cwd, active_request="r1", lane="full",
                    spec_file="docs/tdq/spec/missing.md")
        rc, _, err = approve(self.cwd, "spec")
        self.assertEqual(rc, 2)
        self.assertIn("không tồn tại", err)
        self.assertFalse(read_state(self.cwd)["spec_approved"])

    def test_red_spec_file_empty(self):
        write_state(self.cwd, active_request="r1", lane="full",
                    spec_file="docs/tdq/spec/empty.md")
        write_file(self.cwd, "docs/tdq/spec/empty.md", "")
        rc, _, err = approve(self.cwd, "spec")
        self.assertEqual(rc, 2)
        self.assertIn("rỗng", err)

    def test_red_spec_not_registered(self):
        write_state(self.cwd, active_request="r1", lane="full")
        rc, _, err = approve(self.cwd, "spec")
        self.assertEqual(rc, 2)
        self.assertIn("đăng ký", err)

    def test_red_no_active_request(self):
        rc, _, err = approve(self.cwd, "spec")
        self.assertEqual(rc, 2)
        self.assertIn("request", err.lower())

    def test_red_already_approved(self):
        write_state(self.cwd, active_request="r1", lane="full",
                    spec_file="docs/tdq/spec/x.md", spec_approved=True,
                    spec_approved_at="2026-07-27T10:00:00+07:00")
        write_file(self.cwd, "docs/tdq/spec/x.md")
        rc, _, err = approve(self.cwd, "spec")
        self.assertEqual(rc, 2)
        self.assertIn("rồi", err)

    def test_green_plan_after_spec(self):
        write_state(self.cwd, active_request="r1", lane="full", phase="plan",
                    spec_file="docs/tdq/spec/x.md", spec_approved=True,
                    spec_sha256="abc", spec_approved_at="2026-07-27T10:00:00+07:00",
                    plan_file="docs/tdq/plan/x.md")
        write_file(self.cwd, "docs/tdq/spec/x.md")
        write_file(self.cwd, "docs/tdq/plan/x.md", "# plan\nMode thực thi: main — plan nhỏ.\n")
        rc, out, err = approve(self.cwd, "plan main")
        self.assertEqual(rc, 0, err)
        self.assertIn("APPROVED PLAN", out)
        state = read_state(self.cwd)
        self.assertTrue(state["plan_approved"])
        self.assertIsNotNone(state["plan_sha256"])

    def test_green_quick(self):
        write_state(self.cwd, active_request="r1", lane="quick")
        rc, out, err = approve(self.cwd, "quick")
        self.assertEqual(rc, 0, err)
        self.assertIn("workinglog", out)
        self.assertTrue(read_state(self.cwd)["quick_approved"])

    def test_red_quick_wrong_lane(self):
        write_state(self.cwd, active_request="r1", lane="full")
        rc, _, err = approve(self.cwd, "quick")
        self.assertEqual(rc, 2)
        self.assertIn("lane", err)
        self.assertFalse(read_state(self.cwd)["quick_approved"])

    def plan_state(self, **overrides):
        write_state(self.cwd, active_request="r1", lane="full", phase="plan",
                    spec_approved=True, plan_file="docs/tdq/plan/p.md", **overrides)

    def test_red_plan_without_mode_argument(self):
        # Mode is the USER's decision -> the approve command must carry it.
        self.plan_state()
        write_file(self.cwd, "docs/tdq/plan/p.md",
                   "# plan\nMode thực thi: main — plan nhỏ.\n- [ ] t1\n")
        rc, _, err = approve(self.cwd, "plan")
        self.assertEqual(rc, 2)
        self.assertIn("mode", err.lower())
        self.assertIn("subagent", err)
        self.assertFalse(read_state(self.cwd)["plan_approved"])
        self.assertIsNone(read_state(self.cwd)["implement_mode"])

    def test_red_plan_without_proposed_mode_line(self):
        self.plan_state()
        write_file(self.cwd, "docs/tdq/plan/p.md", "# plan\n- [ ] t1\n")
        rc, _, err = approve(self.cwd, "plan main")
        self.assertEqual(rc, 2)
        self.assertIn("Mode thực thi", err)
        # message phải chỉ đúng file cần sửa
        self.assertIn("docs/tdq/plan/p.md", err)
        self.assertFalse(read_state(self.cwd)["plan_approved"])

    def test_green_proposal_line_accepts_wording_variants(self):
        # Gate không được ép đúng MỘT chuỗi: mọi nhãn chứa "mode" + ":" + giá trị
        # đều là đề xuất hợp lệ (plan thật viết "Đề xuất mode: **main**").
        variants = [
            "Mode thực thi: main — tuần tự.",
            "**Mode thực thi**: main",
            "Ngày: x · Lane: full · Đề xuất mode: **main**",
            "Mode đề xuất: `main`",
            "Implement mode: MAIN",
        ]
        for line in variants:
            with self.subTest(line=line):
                self.plan_state()
                write_file(self.cwd, "docs/tdq/plan/p.md", f"# plan\n{line}\n- [ ] t1\n")
                rc, out, err = approve(self.cwd, "plan main")
                self.assertEqual(rc, 0, err)
                self.assertEqual(read_state(self.cwd)["implement_mode"], "main")

    def test_red_mode_word_without_label_is_not_a_proposal(self):
        # "main" xuất hiện lung tung trong plan không được tính là đề xuất mode.
        self.plan_state()
        write_file(self.cwd, "docs/tdq/plan/p.md",
                   "# plan\n- [ ] merge nhánh main vào release\n- [ ] load model chính\n")
        rc, _, err = approve(self.cwd, "plan main")
        self.assertEqual(rc, 2)
        self.assertIn("Mode thực thi", err)

    def test_green_plan_mode_from_user_command(self):
        self.plan_state()
        write_file(self.cwd, "docs/tdq/plan/p.md",
                   "# plan\n**Mode thực thi**: subagent — 3 phase độc lập.\n- [ ] t1\n")
        rc, out, err = approve(self.cwd, "plan subagent")
        self.assertEqual(rc, 0, err)
        self.assertIn("subagent", out)
        state = read_state(self.cwd)
        self.assertTrue(state["plan_approved"])
        self.assertEqual(state["implement_mode"], "subagent")

    def test_green_user_mode_overrides_plan_proposal(self):
        # Plan proposes subagent, user types main -> the user wins, loudly.
        self.plan_state(implement_mode="subagent")
        write_file(self.cwd, "docs/tdq/plan/p.md",
                   "# plan\nMode thực thi: subagent — nhiều phase.\n- [ ] t1\n")
        rc, out, err = approve(self.cwd, "plan main")
        self.assertEqual(rc, 0, err)
        self.assertEqual(read_state(self.cwd)["implement_mode"], "main")
        self.assertIn("đề xuất", out.lower() + err.lower())

    def test_red_plan_state_mode_cannot_bypass_command(self):
        # Model pre-set implement_mode in state -> worthless without the user's word.
        self.plan_state(implement_mode="main")
        write_file(self.cwd, "docs/tdq/plan/p.md",
                   "# plan\nMode thực thi: main — tuần tự.\n- [ ] t1\n")
        rc, _, err = approve(self.cwd, "plan")
        self.assertEqual(rc, 2)
        self.assertIn("mode", err.lower())
        self.assertFalse(read_state(self.cwd)["plan_approved"])

    def test_plan_output_does_not_forbid_asking(self):
        self.plan_state()
        write_file(self.cwd, "docs/tdq/plan/p.md",
                   "# plan\nMode thực thi: main — tuần tự.\n- [ ] t1\n")
        rc, out, err = approve(self.cwd, "plan main")
        self.assertEqual(rc, 0, err)
        self.assertNotIn("do NOT ask again", out)

    def test_hooks_json_matcher_fullmatches_namespaced_command(self):
        # Claude Code full-matches matcher against the FULL command name
        # (plugin prefix included). A bare "tdq-approve" matcher never fires.
        import json
        import os
        import re
        hooks_path = os.path.join(os.path.dirname(__file__), "..", "hooks", "hooks.json")
        with open(hooks_path, encoding="utf-8") as f:
            wiring = json.load(f)
        matcher = wiring["hooks"]["UserPromptExpansion"][0]["matcher"]
        self.assertIsNotNone(re.fullmatch(matcher, "tdq-workflow:tdq-approve"))
        self.assertIsNotNone(re.fullmatch(matcher, "tdq-approve"))

    def test_red_bad_argument(self):
        write_state(self.cwd, active_request="r1", lane="full")
        rc, _, err = approve(self.cwd, "banana")
        self.assertEqual(rc, 2)
        self.assertIn("Cách dùng", err)


if __name__ == "__main__":
    unittest.main()
