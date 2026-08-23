"""P1 — lệnh `next`, `next --brief`, `get <key>` (spec §2.2)."""
import os
import tempfile
import unittest

from helper import run_state_cli, tdq_state

PARTS = ("[TDQ:NEXT]", "Next:", "Command:", "Checklist (copy into your answer, tick as you go):",
         "Done when:")


class NextTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def test_next_no_state(self):
        rc, out, _ = run_state_cli(self.cwd, "next")
        self.assertEqual(rc, 0)
        for part in PARTS:
            self.assertIn(part, out)
        self.assertIn("init", out)
        self.assertIn("YYYY-MM-DD", out)          # công thức slug

    def test_next_all_phases(self):
        run_state_cli(self.cwd, "init", "2026-07-29-0900-demo", "full")
        # Phase `plan` nằm sau cổng sơ đồ: `set phase=plan` bị từ chối khi danh sách
        # sơ đồ rỗng hoặc còn phần tử chưa duyệt. Đăng ký + duyệt một sơ đồ ngay từ
        # đầu để vòng lặp đi được hết mọi phase, đúng luồng spec → diagram → plan.
        so_do = "docs/tdq/mind-map/demo.md"
        run_state_cli(self.cwd, "diagram", "add", so_do)
        rc, _, err = run_state_cli(self.cwd, "approve", "diagram", so_do,
                                   "--by", "duyệt sơ đồ demo")
        self.assertEqual(rc, 0, err)
        for phase in sorted(tdq_state.VALID_PHASES):
            with self.subTest(phase=phase):
                rc, _, err = run_state_cli(self.cwd, "set", f"phase={phase}")
                self.assertEqual(rc, 0, err)
                rc, out, err = run_state_cli(self.cwd, "next")
                self.assertEqual(rc, 0, err)
                for part in PARTS:
                    self.assertIn(part, out, f"{phase}: thiếu {part}")
                self.assertIn(f"phase {phase}", out)
                self.assertLessEqual(len(out.splitlines()), 20, f"{phase} vượt 20 dòng")
                self.assertIn("- [ ] ", out)

    def test_next_quick_lane(self):
        run_state_cli(self.cwd, "init", "2026-07-29-0900-demo", "quick")
        rc, out, _ = run_state_cli(self.cwd, "next")
        self.assertEqual(rc, 0)
        # lane quick mới: mini-spec/plan GỘP một file, có bước phân tích + interview
        self.assertIn("mini spec/plan", out)
        self.assertIn("docs/tdq/plan/", out)
        self.assertIn("approve quick", out)

    def test_next_analyze_asks_for_the_scope_round(self):
        """Checklist phase analyze phải nhắc vòng scope, nếu không nó sẽ bị bỏ im lặng."""
        run_state_cli(self.cwd, "init", "2026-07-29-0900-demo", "full")
        run_state_cli(self.cwd, "set", "phase=analyze")
        rc, out, _ = run_state_cli(self.cwd, "next")
        self.assertEqual(rc, 0)
        self.assertIn("scope", out.lower(), out)

    def test_next_brief_single_line(self):
        run_state_cli(self.cwd, "init", "2026-07-29-0900-demo", "full")
        rc, out, _ = run_state_cli(self.cwd, "next", "--brief")
        self.assertEqual(rc, 0)
        self.assertEqual(len(out.splitlines()), 1, out)
        self.assertTrue(out.startswith("[TDQ:NEXT]"))
        self.assertIn("Project: ", out)

    def test_get_key(self):
        run_state_cli(self.cwd, "init", "2026-07-29-0900-demo", "full")
        rc, out, _ = run_state_cli(self.cwd, "get", "lane")
        self.assertEqual((rc, out), (0, "full"))
        rc, out, _ = run_state_cli(self.cwd, "get", "spec_approved")
        self.assertEqual((rc, out), (0, "false"))
        rc, out, _ = run_state_cli(self.cwd, "get", "plan_file")
        self.assertEqual((rc, out), (0, ""))
        rc, out, err = run_state_cli(self.cwd, "get", "khong_ton_tai")
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")
        self.assertIn("Key not in state", err)

    def test_headline_shows_quick_for_quick_lane(self):
        """QC1.1 — tiêu đề phải nói đúng phase mà thân bài đang dùng.

        Lane quick giữ `phase` thô là `idle`, nhưng checklist lấy từ row `quick`;
        in `phase idle` khiến model tin là không còn việc gì.
        """
        run_state_cli(self.cwd, "init", "2026-07-29-0900-quick", "quick")
        rc, out, _ = run_state_cli(self.cwd, "next")
        self.assertEqual(rc, 0)
        head = out.splitlines()[0]
        self.assertIn("phase quick", head, head)
        self.assertNotIn("phase idle", head, head)
        rc, brief, _ = run_state_cli(self.cwd, "next", "--brief")
        self.assertEqual((rc, brief), (0, head))

    def test_get_full_json_unchanged(self):
        run_state_cli(self.cwd, "init", "2026-07-29-0900-demo", "full")
        rc, out, _ = run_state_cli(self.cwd, "get")
        self.assertEqual(rc, 0)
        import json
        self.assertEqual(json.loads(out)["active_request"], "2026-07-29-0900-demo")


if __name__ == "__main__":
    unittest.main()
