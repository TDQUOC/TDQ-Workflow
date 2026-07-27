"""B2 — edit_gate.py: block edits pre-approval, protect state.json, quick log-first."""
import datetime
import json
import os
import tempfile
import unittest

from helper import run_hook, load_fixture, write_state, write_file, decision


def now_iso(offset_sec=0):
    dt = datetime.datetime.now().astimezone() + datetime.timedelta(seconds=offset_sec)
    return dt.isoformat(timespec="seconds")


class TestEditGate(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def edit(self, fixture, rel=None):
        payload = load_fixture(fixture, cwd=self.cwd)
        if rel is not None:
            payload["tool_input"] = {"file_path": os.path.join(self.cwd, rel)}
        return run_hook("edit_gate.py", payload)

    def test_deny_src_when_full_unapproved(self):
        write_state(self.cwd, active_request="r1", lane="full", phase="spec")
        rc, out, _ = self.edit("edit_src.json")
        self.assertEqual(rc, 0)
        dec, reason = decision(out)
        self.assertEqual(dec, "deny")
        self.assertIn("tdq-approve spec", reason)
        self.assertIn("docs/", reason)

    def test_deny_src_when_plan_pending(self):
        write_state(self.cwd, active_request="r1", lane="full", phase="plan",
                    spec_file="docs/tdq/spec/x.md", spec_approved=True,
                    spec_sha256="abc", spec_approved_at=now_iso())
        rc, out, _ = self.edit("edit_src.json")
        dec, reason = decision(out)
        self.assertEqual(dec, "deny")
        self.assertIn("tdq-approve plan", reason)

    def test_allow_docs_edit_while_blocked(self):
        write_state(self.cwd, active_request="r1", lane="full", phase="spec")
        rc, out, _ = self.edit("edit_docs_spec.json")
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")

    def test_deny_state_json_always(self):
        rc, out, _ = self.edit("edit_state_json.json")
        dec, reason = decision(out)
        self.assertEqual(dec, "deny")
        self.assertIn("state.json", reason)
        write_state(self.cwd, active_request="r1", lane="full", spec_approved=True,
                    plan_approved=True)
        rc, out, _ = self.edit("edit_state_json.json")
        dec, _ = decision(out)
        self.assertEqual(dec, "deny")

    def test_quick_deny_unapproved(self):
        write_state(self.cwd, active_request="r1", lane="quick")
        rc, out, _ = self.edit("edit_src.json")
        dec, reason = decision(out)
        self.assertEqual(dec, "deny")
        self.assertIn("tdq-approve quick", reason)

    def test_quick_deny_log_not_updated(self):
        approved = now_iso()
        write_state(self.cwd, active_request="r1", lane="quick",
                    quick_approved=True, quick_approved_at=approved)
        today = datetime.date.today().strftime("%Y-%m-%d")
        log = write_file(self.cwd, f"docs/workinglog/{today}.md", "# log\n")
        old = datetime.datetime.fromisoformat(approved).timestamp() - 100
        os.utime(log, (old, old))
        rc, out, _ = self.edit("edit_src.json")
        dec, reason = decision(out)
        self.assertEqual(dec, "deny")
        self.assertIn("workinglog", reason)

    def test_quick_allow_after_log_appended(self):
        approved = now_iso()
        write_state(self.cwd, active_request="r1", lane="quick",
                    quick_approved=True, quick_approved_at=approved)
        today = datetime.date.today().strftime("%Y-%m-%d")
        log = write_file(self.cwd, f"docs/workinglog/{today}.md", "# log + plan summary\n")
        new = datetime.datetime.fromisoformat(approved).timestamp() + 100
        os.utime(log, (new, new))
        rc, out, _ = self.edit("edit_src.json")
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")

    def test_full_approved_silent_when_sha_matches(self):
        spec = write_file(self.cwd, "docs/tdq/spec/x.md", "# spec\n")
        import tdq_state
        write_state(self.cwd, active_request="r1", lane="full", phase="implement",
                    spec_file="docs/tdq/spec/x.md", spec_approved=True,
                    spec_sha256=tdq_state.sha256_file(spec), spec_approved_at=now_iso(),
                    plan_file="docs/tdq/plan/x.md", plan_approved=True,
                    plan_sha256="p", plan_approved_at=now_iso())
        rc, out, _ = self.edit("edit_src.json")
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")

    def test_full_approved_warns_on_sha_drift(self):
        write_file(self.cwd, "docs/tdq/spec/x.md", "# spec changed after approval\n")
        write_state(self.cwd, active_request="r1", lane="full", phase="implement",
                    spec_file="docs/tdq/spec/x.md", spec_approved=True,
                    spec_sha256="deadbeef", spec_approved_at=now_iso(),
                    plan_file="docs/tdq/plan/x.md", plan_approved=True,
                    plan_sha256="p", plan_approved_at=now_iso())
        rc, out, _ = self.edit("edit_src.json")
        self.assertEqual(rc, 0)
        data = json.loads(out)
        self.assertIn("sha256", data.get("systemMessage", ""))

    def test_no_state_allows(self):
        rc, out, _ = self.edit("edit_src.json")
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")


if __name__ == "__main__":
    unittest.main()
