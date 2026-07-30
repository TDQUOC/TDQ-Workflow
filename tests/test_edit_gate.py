"""edit_gate.py (0.3.0) — quan sát vào sổ turn + nhắc; không bao giờ chặn."""
import datetime
import os
import tempfile
import unittest

from helper import run_hook, load_fixture, write_state, write_file, decision, tdq_state


def now_iso(offset_sec=0):
    dt = datetime.datetime.now().astimezone() + datetime.timedelta(seconds=offset_sec)
    return dt.isoformat(timespec="seconds")


def today_log_rel():
    return os.path.join("docs", "workinglog", datetime.date.today().strftime("%Y-%m-%d") + ".md")


class TestEditGate(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def edit(self, fixture, rel=None, session="s1"):
        payload = load_fixture(fixture, cwd=self.cwd, session_id=session)
        if rel is not None:
            payload["tool_input"] = {"file_path": os.path.join(self.cwd, rel)}
        return run_hook("edit_gate.py", payload)

    def with_log(self):
        write_file(self.cwd, today_log_rel(), "# log\n")

    def assert_remind(self, out, *needles):
        dec, context = decision(out)
        self.assertEqual(dec, "allow")
        self.assertNotIn("deny", out)
        for needle in needles:
            self.assertIn(needle, context)
        return context

    def test_remind_src_when_full_unapproved(self):
        write_state(self.cwd, active_request="r1", lane="full", phase="spec")
        rc, out, _ = self.edit("edit_src.json")
        self.assertEqual(rc, 0)
        self.assert_remind(out, "[TDQ:APPROVE]", "spec chưa được ghi nhận duyệt", "approve spec")

    def test_remind_src_when_plan_pending(self):
        write_state(self.cwd, active_request="r1", lane="full", phase="plan",
                    spec_file="docs/tdq/spec/x.md", spec_approved=True,
                    spec_sha256="abc", spec_approved_at=now_iso())
        rc, out, _ = self.edit("edit_src.json")
        self.assert_remind(out, "[TDQ:APPROVE]", "plan chưa được ghi nhận duyệt", "approve plan")

    def test_plan_pending_mode_placeholder_lists_external(self):
        write_state(self.cwd, active_request="r1", lane="full", phase="plan",
                    spec_file="docs/tdq/spec/x.md", spec_approved=True,
                    spec_sha256="abc", spec_approved_at=now_iso())
        rc, out, _ = self.edit("edit_src.json")
        self.assert_remind(out, "main|subagent|external")

    def test_docs_edit_is_silent(self):
        write_state(self.cwd, active_request="r1", lane="full", phase="spec")
        rc, out, _ = self.edit("edit_docs_spec.json")
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")

    def test_state_json_reminds_but_allows(self):
        rc, out, _ = self.edit("edit_state_json.json")
        self.assert_remind(out, "[TDQ:STATE]", "tdq_state.py")
        write_state(self.cwd, active_request="r1", lane="full", spec_approved=True,
                    plan_approved=True)
        rc, out, _ = self.edit("edit_state_json.json", session="s2")
        self.assert_remind(out, "[TDQ:STATE]")

    def test_state_md_mirror_also_reminds(self):
        rc, out, _ = self.edit("edit_src.json", rel=os.path.join("docs", "tdq", "STATE.md"))
        self.assert_remind(out, "[TDQ:STATE]")

    def test_quick_remind_unapproved(self):
        write_state(self.cwd, active_request="r1", lane="quick")
        rc, out, _ = self.edit("edit_src.json")
        self.assert_remind(out, "[TDQ:APPROVE]", "quick chưa được ghi nhận duyệt", "approve quick")

    def test_remind_log_when_today_file_missing(self):
        write_state(self.cwd, active_request="r1", lane="quick",
                    quick_approved=True, quick_approved_at=now_iso())
        rc, out, _ = self.edit("edit_src.json")
        self.assert_remind(out, "[TDQ:LOG]", "workinglog")

    def test_silent_after_log_exists(self):
        write_state(self.cwd, active_request="r1", lane="quick",
                    quick_approved=True, quick_approved_at=now_iso())
        self.with_log()
        rc, out, _ = self.edit("edit_src.json")
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")

    def test_full_approved_silent(self):
        spec = write_file(self.cwd, "docs/tdq/spec/x.md", "# spec\n")
        self.with_log()
        write_state(self.cwd, active_request="r1", lane="full", phase="implement",
                    spec_file="docs/tdq/spec/x.md", spec_approved=True,
                    spec_sha256=tdq_state.sha256_file(spec), spec_approved_at=now_iso(),
                    plan_file="docs/tdq/plan/x.md", plan_approved=True,
                    plan_sha256="p", plan_approved_at=now_iso())
        rc, out, _ = self.edit("edit_src.json")
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")

    def test_observes_edit_and_log_rows(self):
        write_state(self.cwd, active_request="r1", lane="full", phase="implement",
                    spec_approved=True, plan_approved=True)
        self.edit("edit_src.json")
        self.edit("edit_src.json", rel=today_log_rel())
        rows = tdq_state.turn_log_read(self.cwd, session="s1")
        events = [r.get("event") for r in rows if r.get("kind") == "observe"]
        self.assertIn("edit", events)
        self.assertIn("log_written", events)

    def test_no_state_silent(self):
        rc, out, _ = self.edit("edit_src.json")
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")

    def test_never_denies_in_any_scenario(self):
        scenarios = [
            dict(active_request="r1", lane="full", phase="spec"),
            dict(active_request="r1", lane="quick"),
            dict(active_request="r1", lane="full", phase="plan", spec_approved=True),
        ]
        for i, overrides in enumerate(scenarios):
            write_state(self.cwd, **overrides)
            for fixture in ("edit_src.json", "edit_state_json.json", "edit_docs_spec.json"):
                rc, out, _ = self.edit(fixture, session=f"sc{i}-{fixture}")
                self.assertEqual(rc, 0)
                self.assertNotIn('"deny"', out, f"{overrides} / {fixture}")


if __name__ == "__main__":
    unittest.main()
