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


PLAN_DOD = """## P1 — a
- [x] **T1.1** (n3) viec mot — Test: x
- [ ] **T1.2** (n3) viec hai — Test: x

## Definition of Done
- [x] Q1 dieu kien mot — lenh
- [x] Q2 dieu kien hai — lenh
- [ ] Q3 dieu kien ba — lenh
- [ ] Q4 dieu kien bon — lenh
- [ ] Q5 dieu kien nam — lenh
"""

PLAN_DOD_KHUON_CU = """## P1 — a
- [ ] **T1.1** (n3) viec mot — Test: x

## Definition of Done
- Q1 dieu kien mot — lenh
- Q2 dieu kien hai — lenh
"""

PLAN_DOD_XONG = """## P1 — a
- [x] **T1.1** (n3) viec mot — Test: x

## Definition of Done
- [x] Q1 dieu kien mot — lenh
"""

PLAN_DOD_CO_MUC_SAU = """## Definition of Done
- [ ] Q1 dieu kien mot — lenh

## Ghi chu them
- [ ] khong phai DoD — dong nay nam ngoai muc
"""


class DodTickTest(unittest.TestCase):
    """Bo dem o tick RIENG cho muc `## Definition of Done`."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def _state(self, noi_dung):
        write_state(self.cwd, active_request="2026-08-12-0900-abc", lane="full",
                    phase="report", plan_file=PLAN_REL)
        write_file(self.cwd, PLAN_REL, noi_dung)

    def test_dod_dem_dung_tong_va_xong(self):
        self._state(PLAN_DOD)
        info = tdq_state.dod_tick_state(self.cwd)
        self.assertTrue(info["exists"])
        self.assertEqual(info["total"], 5)
        self.assertEqual(info["done"], 2)
        self.assertFalse(info["all_done"])

    def test_dod_khuon_cu_khong_o_tick_thi_tong_bang_khong(self):
        self._state(PLAN_DOD_KHUON_CU)
        info = tdq_state.dod_tick_state(self.cwd)
        self.assertTrue(info["exists"])
        self.assertEqual(info["total"], 0)
        self.assertFalse(info["all_done"])

    def test_dod_khong_lan_o_tick_cua_task(self):
        self._state(PLAN_DOD)
        self.assertEqual(tdq_state.dod_tick_state(self.cwd)["total"], 5)
        self.assertEqual(tdq_state.plan_tick_state(self.cwd)["total"], 2)

    def test_dod_dung_o_muc_ke_tiep(self):
        self._state(PLAN_DOD_CO_MUC_SAU)
        self.assertEqual(tdq_state.dod_tick_state(self.cwd)["total"], 1)

    def test_dod_tick_du_thi_all_done(self):
        self._state(PLAN_DOD_XONG)
        info = tdq_state.dod_tick_state(self.cwd)
        self.assertEqual(info["total"], 1)
        self.assertTrue(info["all_done"])

    def test_dod_khong_co_plan_thi_khong_nem_loi(self):
        write_state(self.cwd, active_request="2026-08-12-0900-abc", lane="full",
                    phase="report")
        info = tdq_state.dod_tick_state(self.cwd)
        self.assertFalse(info["exists"])
        self.assertEqual(info["total"], 0)

    def test_dod_khong_co_muc_definition_of_done(self):
        self._state(PLAN_CHUA_LAM)
        info = tdq_state.dod_tick_state(self.cwd)
        self.assertTrue(info["exists"])
        self.assertEqual(info["total"], 0)


QC_REL = os.path.join("docs", "tdq", "qc", "2026-08-12-0900-abc.md")

QC_TOAN_PASS = """# QC — abc

| # | Hang muc | Lenh | Ket qua | PASS/FAIL |
|---|---|---|---|---|
| Q1 | mot | lenh | ok | PASS |
| Q2 | hai | lenh | ok | PASS |
| Q3 | ba | lenh | ok | PASS |

## Ket luan
PASS toan bo.
"""

QC_CO_FAIL = """# QC — abc

| # | Hang muc | Lenh | Ket qua | PASS/FAIL |
|---|---|---|---|---|
| Q1 | mot | lenh | ok | PASS |
| Q2 | hai | lenh | sai | FAIL |
"""


class QcKetQuaTest(unittest.TestCase):
    """Bo doc ket qua PASS/FAIL tu file qc cua request dang active."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def _state(self, noi_dung=None):
        write_state(self.cwd, active_request="2026-08-12-0900-abc", lane="full",
                    phase="report", plan_file=PLAN_REL)
        if noi_dung is not None:
            write_file(self.cwd, QC_REL, noi_dung)

    def test_qcket_dem_dung_so_pass(self):
        self._state(QC_TOAN_PASS)
        info = tdq_state.qc_result_state(self.cwd)
        self.assertTrue(info["exists"])
        self.assertEqual(info["passed"], 3)
        self.assertEqual(info["failed"], 0)
        self.assertTrue(info["all_pass"])

    def test_qcket_dem_dung_so_fail(self):
        self._state(QC_CO_FAIL)
        info = tdq_state.qc_result_state(self.cwd)
        self.assertEqual(info["passed"], 1)
        self.assertEqual(info["failed"], 1)
        self.assertFalse(info["all_pass"])

    def test_qcket_thieu_file_thi_khong_nem_loi(self):
        self._state(None)
        info = tdq_state.qc_result_state(self.cwd)
        self.assertFalse(info["exists"])
        self.assertEqual(info["passed"], 0)
        self.assertFalse(info["all_pass"])

    def test_qcket_khong_co_request_thi_rong(self):
        write_state(self.cwd, lane="full", phase="report")
        info = tdq_state.qc_result_state(self.cwd)
        self.assertFalse(info["exists"])

    def test_qcket_bo_qua_dong_tieu_de_bang(self):
        self._state(QC_TOAN_PASS)
        self.assertEqual(tdq_state.qc_result_state(self.cwd)["passed"], 3)


class HoiQuyBoDemTaskTest(unittest.TestCase):
    """Muc DoD co o tick KHONG duoc lam lech bo dem task cu."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def _dem(self, noi_dung):
        write_state(self.cwd, active_request="2026-08-12-0900-abc", lane="full",
                    phase="implement", plan_file=PLAN_REL)
        write_file(self.cwd, PLAN_REL, noi_dung)
        return tdq_state.plan_tick_state(self.cwd)

    def test_o_tick_dod_khong_lam_lech_so_task(self):
        khong_dod = self._dem(PLAN_CHUA_LAM)
        co_dod = self._dem(PLAN_CHUA_LAM + "\n## Definition of Done\n"
                           "- [ ] Q1 dieu kien mot — lenh\n"
                           "- [ ] Q2 dieu kien hai — lenh\n")
        self.assertEqual(co_dod["total"], khong_dod["total"])
        self.assertEqual(co_dod["all_done"], khong_dod["all_done"])

    def test_dod_tick_du_khong_bat_all_done_cua_task(self):
        info = self._dem("## P1 — a\n- [ ] **T1.1** viec — Test: x\n"
                         "\n## Definition of Done\n- [x] Q1 dieu kien — lenh\n")
        self.assertEqual(info["total"], 1)
        self.assertFalse(info["all_done"])

    def test_khoa_bo_khoa_tra_ve_cua_plan_tick_state(self):
        info = self._dem(PLAN_CHUA_LAM)
        self.assertEqual(
            sorted(info),
            sorted(["path", "exists", "sha", "has_doing", "all_done", "total",
                    "doing_count", "dispatched_count", "dispatched_ids"]))


if __name__ == "__main__":
    unittest.main()


PLAN_DOD_HAI_MUC = """## Definition of Done
- [x] Q1 dieu kien mot — lenh

## Ghi chu

## Definition of Done
- [ ] Q2 dieu kien hai — lenh
- [ ] Q3 dieu kien ba — lenh
"""

PLAN_DOD_TIEU_DE_BIEN_THE = """## definition of done (19)
- [x] Q1 dieu kien mot — lenh
- [ ] Q2 dieu kien hai — lenh
"""

PLAN_DOD_TRONG_RAO = """## Khuon mau

```markdown
## Definition of Done
- [ ] Q1 <dieu kien> — <lenh>
```

## Definition of Done
- [x] Q1 dieu kien that — lenh
"""

QC_CO_CHUA_KET_LUAN = """# QC — abc

| # | Hang muc | Lenh | Ket qua | PASS/FAIL |
|---|---|---|---|---|
| Q1 | mot | lenh | ok | PASS |
| Q2 | hai | lenh | chua chay | SKIP |
"""


class DodCaBienTest(unittest.TestCase):
    """Ca bien cua bo dem DoD: tieu de trung, bien the, nam trong rao, file hong ma."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def _state(self, noi_dung):
        write_state(self.cwd, active_request="2026-08-12-0900-abc", lane="full",
                    phase="report", plan_file=PLAN_REL)
        write_file(self.cwd, PLAN_REL, noi_dung)

    def test_trung_hai_muc_dod_thi_dem_ca_hai(self):
        self._state(PLAN_DOD_HAI_MUC)
        info = tdq_state.dod_tick_state(self.cwd)
        self.assertEqual(info["total"], 3)
        self.assertEqual(info["done"], 1)
        self.assertFalse(info["all_done"])

    def test_biento_tieu_de_khac_hoa_thuong_va_co_duoi(self):
        self._state(PLAN_DOD_TIEU_DE_BIEN_THE)
        info = tdq_state.dod_tick_state(self.cwd)
        self.assertEqual(info["total"], 2)
        self.assertEqual(info["done"], 1)

    def test_rao_tieu_de_trong_khoi_rao_khong_duoc_dem(self):
        self._state(PLAN_DOD_TRONG_RAO)
        info = tdq_state.dod_tick_state(self.cwd)
        self.assertEqual(info["total"], 1)
        self.assertTrue(info["all_done"])

    def test_utf_plan_khong_phai_utf8_thi_khong_nem_loi(self):
        self._state(PLAN_DOD)
        with open(os.path.join(self.cwd, PLAN_REL), "wb") as f:
            f.write(b"## Definition of Done\n- [ ] Q1 \xff\xfe hong ma\n")
        info = tdq_state.dod_tick_state(self.cwd)
        self.assertFalse(info["exists"])
        self.assertEqual(info["total"], 0)

    def test_utf_task_open_count_chiu_duoc_file_hong_ma(self):
        self._state(PLAN_DOD)
        with open(os.path.join(self.cwd, PLAN_REL), "wb") as f:
            f.write(b"- [ ] **T1.1** \xff\xfe hong ma\n")
        self.assertEqual(tdq_state.task_open_count(self.cwd), 0)

    def test_utf_qc_khong_phai_utf8_thi_khong_nem_loi(self):
        self._state(PLAN_DOD)
        write_file(self.cwd, QC_REL, "x")
        with open(os.path.join(self.cwd, QC_REL), "wb") as f:
            f.write(b"| Q1 | \xff\xfe | PASS |\n")
        info = tdq_state.qc_result_state(self.cwd)
        self.assertFalse(info["exists"])
        self.assertFalse(info["all_pass"])

    def test_qcket_o_chua_ket_luan_khong_tinh_la_xong(self):
        write_state(self.cwd, active_request="2026-08-12-0900-abc", lane="full",
                    phase="report", plan_file=PLAN_REL)
        write_file(self.cwd, QC_REL, QC_CO_CHUA_KET_LUAN)
        info = tdq_state.qc_result_state(self.cwd)
        self.assertEqual(info["passed"], 1)
        self.assertEqual(info["pending"], 1)
        self.assertFalse(info["all_pass"])
