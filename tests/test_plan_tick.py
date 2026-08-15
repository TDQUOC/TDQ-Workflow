"""P1 — đọc trạng thái tick của plan (hàng rào ép tick task khi implement).

Hàng rào chỉ đúng khi nó phân biệt được "plan đã động trong turn này" với
"plan đứng yên". Nền của việc đó là `plan_tick_state` + `plan_sha`.
"""
import os
import tempfile
import unittest

from helper import tdq_state, write_state, write_file

PLAN_REL = os.path.join("docs", "tdq", "plan", "2026-08-12-0900-abc.md")

PLAN_CHUA_LAM = """## P1 — a
- [ ] **T1.1** (n3) viec mot — Test: x
- [ ] **T1.2** (n3) viec hai — Test: x
"""

PLAN_DANG_LAM = """## P1 — a
- [~] **T1.1** (n3) viec mot — Test: x
- [ ] **T1.2** (n3) viec hai — Test: x
"""

PLAN_XONG_HET = """## P1 — a
- [x] **T1.1** (n3) viec mot — Test: x
- [x] **T1.2** (n3) viec hai — Test: x
"""

PLAN_HAI_DANG_LAM = """## P1 — a
- [~] **T1.1** (n3) viec mot — Test: x
- [~] **T1.2** (n3) viec hai — Test: x
"""


class PlanTickStateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def _state(self, plan=PLAN_CHUA_LAM, plan_file=PLAN_REL):
        write_state(self.cwd, active_request="2026-08-12-0900-abc", lane="full",
                    phase="implement", plan_file=plan_file)
        if plan is not None:
            write_file(self.cwd, PLAN_REL, plan)

    def test_dang_lam_thi_has_doing(self):
        self._state(PLAN_DANG_LAM)
        info = tdq_state.plan_tick_state(self.cwd)
        self.assertTrue(info["exists"])
        self.assertTrue(info["has_doing"])
        self.assertFalse(info["all_done"])
        self.assertEqual(info["total"], 2)

    def test_doing_count_dem_dung_so_task_dang_lam(self):
        self._state(PLAN_CHUA_LAM)
        self.assertEqual(tdq_state.plan_tick_state(self.cwd)["doing_count"], 0)
        self._state(PLAN_DANG_LAM)
        self.assertEqual(tdq_state.plan_tick_state(self.cwd)["doing_count"], 1)
        self._state(PLAN_HAI_DANG_LAM)
        self.assertEqual(tdq_state.plan_tick_state(self.cwd)["doing_count"], 2)

    def test_xong_het_thi_all_done(self):
        self._state(PLAN_XONG_HET)
        info = tdq_state.plan_tick_state(self.cwd)
        self.assertTrue(info["all_done"])
        self.assertFalse(info["has_doing"])

    def test_chua_lam_gi_thi_ca_hai_co_deu_tat(self):
        self._state(PLAN_CHUA_LAM)
        info = tdq_state.plan_tick_state(self.cwd)
        self.assertFalse(info["has_doing"])
        self.assertFalse(info["all_done"])

    def test_khong_co_file_plan(self):
        self._state(plan=None)
        info = tdq_state.plan_tick_state(self.cwd)
        self.assertFalse(info["exists"])
        self.assertFalse(info["has_doing"])
        self.assertFalse(info["all_done"])
        self.assertEqual(info["sha"], "")

    def test_thieu_plan_file_thi_suy_tu_active_request(self):
        write_state(self.cwd, active_request="2026-08-12-0900-abc", lane="full",
                    phase="implement")
        write_file(self.cwd, PLAN_REL, PLAN_DANG_LAM)
        info = tdq_state.plan_tick_state(self.cwd)
        self.assertTrue(info["exists"])
        self.assertTrue(info["has_doing"])

    def test_plan_khong_co_task_nao(self):
        self._state("# PLAN\nChi co van xuoi.\n")
        info = tdq_state.plan_tick_state(self.cwd)
        self.assertTrue(info["exists"])
        self.assertEqual(info["total"], 0)
        self.assertFalse(info["all_done"])

    def test_sha_doi_khi_tick_doi(self):
        self._state(PLAN_CHUA_LAM)
        truoc = tdq_state.plan_tick_state(self.cwd)["sha"]
        write_file(self.cwd, PLAN_REL, PLAN_DANG_LAM)
        sau = tdq_state.plan_tick_state(self.cwd)["sha"]
        self.assertTrue(truoc)
        self.assertNotEqual(truoc, sau)


class TurnSnapshotPlanShaTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def test_snapshot_co_plan_sha_va_giu_khoa_cu(self):
        write_state(self.cwd, active_request="2026-08-12-0900-abc", lane="full",
                    phase="implement", plan_file=PLAN_REL)
        write_file(self.cwd, PLAN_REL, PLAN_CHUA_LAM)
        snap = tdq_state.turn_snapshot(self.cwd)
        for khoa in ("log_rel", "log_sha", "repo_sha", "repo_paths", "plan_sha"):
            self.assertIn(khoa, snap)
        truoc = snap["plan_sha"]
        write_file(self.cwd, PLAN_REL, PLAN_DANG_LAM)
        self.assertNotEqual(truoc, tdq_state.turn_snapshot(self.cwd)["plan_sha"])

    def test_khong_co_plan_thi_plan_sha_rong(self):
        write_state(self.cwd, active_request="2026-08-12-0900-abc", lane="full",
                    phase="implement")
        self.assertEqual(tdq_state.turn_snapshot(self.cwd)["plan_sha"], "")


if __name__ == "__main__":
    unittest.main()
