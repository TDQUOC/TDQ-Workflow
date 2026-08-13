"""edit_gate.py (0.4.0) — quan sát vào sổ turn + nhắc; chỉ TDQ:TICK chặn."""
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

    def test_plan_pending_mode_placeholder_lists_modes(self):
        write_state(self.cwd, active_request="r1", lane="full", phase="plan",
                    spec_file="docs/tdq/spec/x.md", spec_approved=True,
                    spec_sha256="abc", spec_approved_at=now_iso())
        rc, out, _ = self.edit("edit_src.json")
        self.assert_remind(out, "main|subagent")

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

    def test_never_denies_outside_tick(self):
        """Ngoài TDQ:TICK, mọi ca khác chỉ nhắc — không ca nào deny."""
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


class TickBlockTest(unittest.TestCase):
    """TDQ:TICK — chặn sửa mã nguồn khi implement mà plan chưa có `[~]`. Miễn trừ tests/**."""

    PLAN_REL = os.path.join("docs", "tdq", "plan", "r1.md")
    CHUA_LAM = "- [ ] **T1** a — Test: x\n- [ ] **T2** b — Test: x\n"
    DANG_LAM = "- [~] **T1** a — Test: x\n- [ ] **T2** b — Test: x\n"
    HAI_DANG_LAM = "- [~] **T1** a — Test: x\n- [~] **T2** b — Test: x\n"
    XONG_HET = "- [x] **T1** a — Test: x\n- [x] **T2** b — Test: x\n"
    DANG_LAM_KHAC = "- [x] **T1** a — Test: x\n- [~] **T2** b — Test: x\n"

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        self.addCleanup(self._tmp.cleanup)
        write_file(self.cwd, today_log_rel(), "# log\n")

    def dung_state(self, phase="implement", plan=None):
        write_state(self.cwd, active_request="r1", lane="full", phase=phase,
                    spec_file="docs/tdq/spec/r1.md", spec_approved=True,
                    spec_sha256="abc", spec_approved_at=now_iso(),
                    plan_file=self.PLAN_REL, plan_approved=True,
                    plan_sha256="def", plan_approved_at=now_iso(),
                    implement_mode="main")
        if plan is not None:
            write_file(self.cwd, self.PLAN_REL, plan)

    def sua(self, rel="src/a.py"):
        payload = load_fixture("edit_src.json", cwd=self.cwd, session_id="s-tick")
        payload["tool_input"] = {"file_path": os.path.join(self.cwd, rel)}
        return run_hook("edit_gate.py", payload)

    def test_implement_chua_tick_thi_chan(self):
        self.dung_state(plan=self.CHUA_LAM)
        rc, out, _ = self.sua()
        self.assertEqual(rc, 0)
        self.assertIn("deny", out)
        self.assertIn("TDQ:TICK", out)

    def test_chan_lap_lai_khong_dedupe(self):
        """Chặn phải lặp: dedupe sẽ cho lần sửa thứ hai lọt trong khi plan vẫn chưa tick."""
        self.dung_state(plan=self.CHUA_LAM)
        self.assertIn("deny", self.sua()[1])
        self.assertIn("deny", self.sua("src/b.py")[1])

    def test_sua_file_test_thi_khong_chan(self):
        """red→green: viết test đỏ trước khi có gì để tick."""
        self.dung_state(plan=self.CHUA_LAM)
        out = self.sua(os.path.join("tests", "test_moi.py"))[1]
        self.assertNotIn("TDQ:TICK", out)
        self.assertNotIn("deny", out)

    def test_da_co_dau_nga_thi_im(self):
        self.dung_state(plan=self.DANG_LAM)
        self.assertNotIn("TDQ:TICK", self.sua()[1])

    def test_plan_xong_het_thi_im(self):
        self.dung_state(plan=self.XONG_HET)
        self.assertNotIn("TDQ:TICK", self.sua()[1])

    def test_khong_co_file_plan_thi_im(self):
        self.dung_state(plan=None)
        self.assertNotIn("TDQ:TICK", self.sua()[1])

    def test_phase_ngoai_implement_qc_thi_im(self):
        self.dung_state(phase="report", plan=self.CHUA_LAM)
        self.assertNotIn("TDQ:TICK", self.sua()[1])

    def test_phase_qc_van_chan(self):
        self.dung_state(phase="qc", plan=self.CHUA_LAM)
        out = self.sua()[1]
        self.assertIn("TDQ:TICK", out)
        self.assertIn("deny", out)

    def test_sua_trong_docs_thi_im(self):
        self.dung_state(plan=self.CHUA_LAM)
        self.assertNotIn("TDQ:TICK", self.sua("docs/ghi-chu.md")[1])

    def test_hai_task_cung_doing_thi_chan(self):
        self.dung_state(plan=self.HAI_DANG_LAM)
        out = self.sua()[1]
        self.assertIn("deny", out)
        self.assertIn("TDQ:TICK", out)

    def test_dung_mot_task_doing_thi_khong_chan_vi_ca_nay(self):
        self.dung_state(plan=self.DANG_LAM)
        self.assertNotIn("TDQ:TICK", self.sua()[1])

    def test_streak_3_lan_sua_lien_tiep_khong_tick_thi_chan_lan_4(self):
        self.dung_state(plan=self.DANG_LAM)
        for i in range(3):
            out = self.sua(f"src/streak{i}.py")[1]
            self.assertNotIn("deny", out)
        out4 = self.sua("src/streak3.py")[1]
        self.assertIn("deny", out4)
        self.assertIn("TDQ:TICK", out4)

    def test_streak_reset_khi_plan_doi_sau_tick(self):
        self.dung_state(plan=self.DANG_LAM)
        for i in range(3):
            self.sua(f"src/reset{i}.py")
        write_file(self.cwd, self.PLAN_REL, self.DANG_LAM_KHAC)
        out = self.sua("src/reset3.py")[1]
        self.assertNotIn("deny", out)

    def test_streak_khong_tinh_sua_trong_tests(self):
        self.dung_state(plan=self.DANG_LAM)
        for i in range(5):
            out = self.sua(os.path.join("tests", f"test_streak{i}.py"))[1]
            self.assertNotIn("deny", out)
