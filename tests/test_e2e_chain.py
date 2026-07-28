"""E1 — simulated end-to-end hook chains for both lanes (full + quick)."""
import datetime
import json
import os
import tempfile
import time
import unittest

from helper import run_hook, load_fixture, read_state, write_file, run_state_cli, decision


def today():
    return datetime.date.today().strftime("%Y-%m-%d")


class ChainBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def edit_src(self):
        payload = load_fixture("edit_src.json", cwd=self.cwd)
        return decision(run_hook("edit_gate.py", payload)[1])

    def approve(self, target):
        return run_hook("approve_gate.py",
                        load_fixture("approve.json", cwd=self.cwd, command_args=target))

    def stop(self):
        return run_hook("stop_gate.py", load_fixture("stop.json", cwd=self.cwd))


class TestFullLaneChain(ChainBase):
    def test_full_chain(self):
        # 1. intake: init state, lane full
        rc, _, err = run_state_cli(self.cwd, "init", f"{today()}-demo", "full")
        self.assertEqual(rc, 0, err)

        # 2. pre-approval: src edit denied with spec hint, docs edit allowed
        dec, reason = self.edit_src()
        self.assertEqual(dec, "deny")
        self.assertIn("tdq-approve spec", reason)

        # 3. spec written in docs (allowed) and registered
        write_file(self.cwd, "docs/tdq/spec/demo.md", "# spec demo\nnoi dung\n")
        run_state_cli(self.cwd, "set", "phase=spec", "spec_file=docs/tdq/spec/demo.md")

        # 4. user approves spec
        rc, out, err = self.approve("spec")
        self.assertEqual(rc, 0, err)
        self.assertIn("APPROVED SPEC", out)

        # 5. still blocked: plan pending
        dec, reason = self.edit_src()
        self.assertEqual(dec, "deny")
        self.assertIn("tdq-approve plan", reason)

        # 6. plan written + registered, user approves plan
        write_file(self.cwd, "docs/tdq/plan/demo.md", "# plan demo\n- [ ] T1\n")
        run_state_cli(self.cwd, "set", "phase=plan", "plan_file=docs/tdq/plan/demo.md")
        # plan chưa khai báo mode thực thi → gate chặn, kể cả khi state đã có mode
        run_state_cli(self.cwd, "set", "implement_mode=main")
        rc, _, err = self.approve("plan")
        self.assertEqual(rc, 2)
        self.assertIn("mode", err)

        write_file(self.cwd, "docs/tdq/plan/demo.md",
                   "# plan demo\nMode thực thi: main — plan 1 task.\n- [ ] T1\n")
        rc, out, err = self.approve("plan")
        self.assertEqual(rc, 0, err)
        self.assertIn("APPROVED PLAN", out)
        self.assertIn("main", out)

        # 7. implement unlocked
        run_state_cli(self.cwd, "set", "phase=implement")
        dec, reason = self.edit_src()
        self.assertIsNone(dec, reason)

        # 8. repo changed, log stale -> Stop blocks; log appended -> silent
        log = write_file(self.cwd, f"docs/workinglog/{today()}.md", "# log\n")
        os.utime(log, (time.time() - 300, time.time() - 300))
        write_file(self.cwd, "src/app.py", "print('mvp')\n")
        rc, out, _ = self.stop()
        self.assertEqual(json.loads(out)["decision"], "block")
        write_file(self.cwd, f"docs/workinglog/{today()}.md", "# log\n- entry moi\n")
        rc, out, _ = self.stop()
        self.assertEqual(out, "")

        # final state sane
        state = read_state(self.cwd)
        self.assertTrue(state["spec_approved"] and state["plan_approved"])


class TestQuickLaneChain(ChainBase):
    def test_quick_chain(self):
        # 1. intake quick
        rc, _, err = run_state_cli(self.cwd, "init", f"{today()}-hotfix", "quick")
        self.assertEqual(rc, 0, err)

        # 2. pre-approval: denied with quick hint
        dec, reason = self.edit_src()
        self.assertEqual(dec, "deny")
        self.assertIn("tdq-approve quick", reason)

        # 3. user approves quick
        rc, out, err = self.approve("quick")
        self.assertEqual(rc, 0, err)
        self.assertIn("workinglog", out)

        # 4. still denied: plan summary not yet logged
        dec, reason = self.edit_src()
        self.assertEqual(dec, "deny")
        self.assertIn("workinglog", reason)

        # 5. log appended after approval -> unlocked
        approved_at = read_state(self.cwd)["quick_approved_at"]
        log = write_file(self.cwd, f"docs/workinglog/{today()}.md", "# log\n- plan quick: sua bug X\n")
        ts = datetime.datetime.fromisoformat(approved_at).timestamp() + 60
        os.utime(log, (ts, ts))
        dec, reason = self.edit_src()
        self.assertIsNone(dec, reason)


if __name__ == "__main__":
    unittest.main()
