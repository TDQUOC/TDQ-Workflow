"""Mode đội: leader phân công cả plan, agent con chạy song song, merge có kiểm.

Luật khoá ở đây: `[>]` (đã giao cho agent con) là trạng thái THỨ TƯ của checkbox,
khác hẳn `[~]` (leader đang tự làm). Hàng rào ép tick vẫn chỉ cho MỘT `[~]`, nhưng
phải cho NHIỀU `[>]` — nếu không thì không thể có đội.
"""
import datetime
import json
import os
import re
import subprocess
import tempfile
import unittest

from helper import (tdq_state, write_state, write_file, run_state_cli,
                    run_team_cli, run_hook, load_fixture, run_checkstatus_cli)
import tdq_team                                  # sau helper: helper bơm scripts/ vào sys.path

PLAN_REL = os.path.join("docs", "tdq", "plan", "2026-08-17-1828-x.md")

PLAN_MOT_DOI_BON_GIAO = """## P1 — a
- [~] **T1.1** (n3 e5m) leader tu lam — Test: x
- [>] **T1.2** (n3 e5m) giao agent — Test: x
- [>] **T1.3** (n3 e5m) giao agent — Test: x
- [>] **T1.4** (n3 e5m) giao agent — Test: x
- [>] **T1.5** (n3 e5m) giao agent — Test: x
"""

PLAN_TRON_10 = """## P1 — a
- [x] **T1.1** (n3 e5m) xong — Test: x
- [x] **T1.2** (n3 e5m) xong — Test: x
- [x] **T1.3** (n3 e5m) xong — Test: x
- [>] **T1.4** (n3 e5m) giao — Test: x
- [>] **T1.5** (n3 e5m) giao — Test: x
- [>] **T1.6** (n3 e5m) giao — Test: x
- [>] **T1.7** (n3 e5m) giao — Test: x
- [~] **T1.8** (n3 e5m) dang lam — Test: x
- [ ] **T1.9** (n3 e5m) chua lam — Test: x
- [ ] **T1.10** (n3 e5m) chua lam — Test: x
"""

PLAN_KHONG_GIAO = """## P1 — a
- [~] **T1.1** (n3 e5m) dang lam — Test: x
- [ ] **T1.2** (n3 e5m) chua lam — Test: x
"""


class TickStateTest(unittest.TestCase):
    """T1.1 + T1.3 — `plan_tick_state` hiểu dấu `[>]`."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def _state(self, plan):
        write_state(self.cwd, active_request="2026-08-17-1828-x", lane="full",
                    phase="implement", implement_mode="subagent", plan_file=PLAN_REL)
        write_file(self.cwd, PLAN_REL, plan)
        return tdq_state.plan_tick_state(self.cwd)

    def test_tick_state_dem_rieng_dang_lam_va_da_giao(self):
        info = self._state(PLAN_MOT_DOI_BON_GIAO)
        self.assertEqual(info["doing_count"], 1)
        self.assertEqual(info["dispatched_count"], 4)
        self.assertEqual(info["total"], 5)

    def test_tick_state_liet_ke_ma_task_da_giao(self):
        info = self._state(PLAN_MOT_DOI_BON_GIAO)
        self.assertEqual(info["dispatched_ids"], ["T1.2", "T1.3", "T1.4", "T1.5"])

    def test_tick_state_khong_giao_thi_rong(self):
        info = self._state(PLAN_KHONG_GIAO)
        self.assertEqual(info["dispatched_count"], 0)
        self.assertEqual(info["dispatched_ids"], [])
        self.assertEqual(info["doing_count"], 1)

    def test_tick_state_da_giao_van_tinh_la_dang_chay(self):
        """`[>]` phải làm `has_doing` bật — nếu không, hàng rào sẽ đòi thêm `[~]`."""
        plan = PLAN_MOT_DOI_BON_GIAO.replace("- [~] **T1.1**", "- [ ] **T1.1**")
        info = self._state(plan)
        self.assertEqual(info["doing_count"], 0)
        self.assertEqual(info["dispatched_count"], 4)
        self.assertTrue(info["has_doing"])

    def test_tick_state_giu_nguyen_cach_dem_cu(self):
        """T1.3 — thêm `[>]` không được làm sai `total` hay tiến độ `[x]`."""
        info = self._state(PLAN_TRON_10)
        self.assertEqual(info["total"], 10)
        self.assertEqual(info["doing_count"], 1)
        self.assertEqual(info["dispatched_count"], 4)
        self.assertFalse(info["all_done"])

    def test_tick_state_all_done_khong_bi_pha_boi_dau_moi(self):
        plan = "## P1 — a\n- [x] **T1.1** (n3 e5m) xong — Test: x\n"
        info = self._state(plan)
        self.assertTrue(info["all_done"])
        self.assertEqual(info["dispatched_count"], 0)


class PhaseRowTest(unittest.TestCase):
    """T1.2 — phase implement có bản riêng cho mode đội."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def _state(self, mode):
        return write_state(self.cwd, active_request="2026-08-17-1828-x", lane="full",
                           phase="implement", implement_mode=mode,
                           plan_approved=True, plan_file=PLAN_REL)

    def test_mode_main_giu_nguyen_dong_cu(self):
        state = self._state("main")
        row = tdq_state.phase_row(state)
        self.assertIs(row, tdq_state.PHASE_TABLE["implement"])

    def test_mode_subagent_doi_sang_dong_doi(self):
        state = self._state("subagent")
        row = tdq_state.phase_row(state)
        self.assertIs(row, tdq_state.IMPLEMENT_SUBAGENT_ROW)
        noi_dung = row["action"] + " ".join(row["checklist"])
        self.assertIn("[>]", noi_dung)
        self.assertIn("tdq_team.py", noi_dung)
        self.assertIn("phan-cong", noi_dung)

    def test_next_in_dong_doi_khi_mode_subagent(self):
        self._state("subagent")
        write_file(self.cwd, PLAN_REL, PLAN_KHONG_GIAO)
        rc, out, _err = run_state_cli(self.cwd, "next")
        self.assertEqual(rc, 0, out)
        self.assertIn("tdq_team.py", out)
        self.assertIn("phase implement", out)

    def test_next_mode_main_khong_nhac_tdq_team(self):
        self._state("main")
        write_file(self.cwd, PLAN_REL, PLAN_KHONG_GIAO)
        rc, out, _err = run_state_cli(self.cwd, "next")
        self.assertEqual(rc, 0, out)
        self.assertNotIn("tdq_team.py", out)

    def test_bien_the_doi_khong_phai_mot_phase(self):
        """Biến thể đội KHÔNG được thành phase thứ 11: không vào PHASE_TABLE,
        không vào PHASE_ORDER, không vào VALID_PHASES, không mọc dòng trong doc."""
        self.assertNotIn("implement_subagent", tdq_state.PHASE_TABLE)
        self.assertNotIn("implement_subagent", tdq_state.PHASE_ORDER)
        self.assertNotIn("implement_subagent", tdq_state.VALID_PHASES)
        self.assertNotIn("implement_subagent", tdq_state.render_phases_md())


LENH_CON = ["phan-cong", "kiem-ke", "cum", "mo", "kiem", "hop", "don"]


class CliTest(unittest.TestCase):
    """T2.1 — khung CLI + log service của scripts/tdq_team.py."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def test_help_exit_0_va_liet_ke_du_7_lenh_con(self):
        rc, out, _err = run_team_cli(self.cwd, "--help")
        self.assertEqual(rc, 0, out)
        for lenh in LENH_CON:
            self.assertIn(lenh, out)

    def test_khong_co_lenh_con_thi_exit_2(self):
        rc, _out, err = run_team_cli(self.cwd)
        self.assertEqual(rc, 2, err)

    def test_lenh_con_la_thi_exit_2(self):
        rc, _out, err = run_team_cli(self.cwd, "khong-co-lenh-nay")
        self.assertEqual(rc, 2, err)

    def test_log_bat_mac_dinh_co_timestamp_iso(self):
        rc, _out, err = run_team_cli(self.cwd, "--help")
        self.assertEqual(rc, 0)
        # --help không chạy việc gì; log service chỉ cần chứng minh ở lệnh thật.
        rc, _out, err = run_team_cli(self.cwd, "kiem-ke")
        self.assertRegex(err, r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\]")

    def test_tat_log_bang_bien_moi_truong(self):
        rc, _out, err = run_team_cli(self.cwd, "kiem-ke", env={"TDQ_LOG": "0"})
        self.assertNotIn("[20", err)


PLAN_TRON = """# PLAN — mau

## P1 — nen
- [ ] **T1.1** (n3 e5m) sua alpha — Test: `true`
  - Chạm: `scripts/alpha.py`
- [ ] **T1.2** (n3 e5m) sua beta — Test: `true`
  - Chạm: `scripts/beta.py`
- [ ] **T1.3** (n3 e5m) sua gamma — Test: `true`
  - Chạm: `scripts/gamma.py`
- [ ] **T1.4** (n3 e5m) chay sau khi T1.1 xong — Test: `true`
  - Chạm: `scripts/delta.py`
- [ ] **T1.5** (n3 e5m) tra cuu tai lieu ngoai — Test: `true`
  - Chạm: `scripts/epsilon.py`
  - Dùng: `context7` (mcp)
"""

PLAN_CHUNG_FILE = """# PLAN — mau

## P1 — nen
- [ ] **T1.1** (n3 e5m) sua alpha lan mot — Test: `true`
  - Chạm: `scripts/alpha.py`
- [ ] **T1.2** (n3 e5m) sua alpha lan hai — Test: `true`
  - Chạm: `scripts/alpha.py`
"""

PLAN_8_TASK = """# PLAN — mau

## P1 — nen
- [ ] **T1.1** (n3 e5m) viec a — Test: `true`
  - Chạm: `scripts/a.py`
- [ ] **T1.2** (n3 e5m) viec b — Test: `true`
  - Chạm: `scripts/b.py`
- [ ] **T1.3** (n3 e5m) viec c — Test: `true`
  - Chạm: `scripts/c.py`

## P2 — tang tren
- [ ] **T2.1** (n3 e5m) viec d — Test: `true`
  - Chạm: `scripts/d.py`
- [ ] **T2.2** (n3 e5m) viec e — Test: `true`
  - Chạm: `scripts/e.py`
- [ ] **T2.3** (n3 e5m) viec f — Test: `true`
  - Chạm: `scripts/f.py`
- [ ] **T2.4** (n3 e5m) viec g — Test: `true`
  - Chạm: `scripts/g.py`
- [ ] **T2.5** (n3 e5m) viec h — Test: `true`
  - Chạm: `scripts/h.py`
"""

PLAN_CAN = """# PLAN — mau

## P1 — nen
- [ ] **T1.1** (n3 e5m) dung nen — Test: `true`
  - Chạm: `scripts/a.py`
- [ ] **T1.2** (n3 e5m) doc ket qua cua T1.1 — Test: `true`
  - Chạm: `scripts/b.py`
  - Cần: T1.1
- [ ] **T1.3** (n3 e5m) can hai task truoc — Test: `true`
  - Chạm: `scripts/c.py`
  - Cần: T1.1, T1.2
- [ ] **T1.4** (n3 e5m) khong can gi — Test: `true`
  - Chạm: `scripts/d.py`
"""

PLAN_CAN_CHEO = """# PLAN — mau

## P1 — nen
- [ ] **T1.1** (n3 e5m) viec a — Test: `true`
  - Chạm: `scripts/a.py`
- [ ] **T1.2** (n3 e5m) viec b — Test: `true`
  - Chạm: `scripts/b.py`
  - Cần: T1.1

## P2 — tang tren
- [ ] **T2.1** (n3 e5m) khong dinh gi toi P1 — Test: `true`
  - Chạm: `scripts/c.py`
- [ ] **T2.2** (n3 e5m) cham chung file voi T2.1 — Test: `true`
  - Chạm: `scripts/c.py`
"""

PLAN_N_ROI = "# PLAN — mau\n\n## P1 — nen\n" + "".join(
    f"- [ ] **T1.{i}** (n3 e5m) viec {i} — Test: `true`\n  - Chạm: `scripts/f{i}.py`\n" for i in range(1, 10))

PLAN_CAN_VONG = """# PLAN — mau

## P1 — nen
- [ ] **T1.1** (n3 e5m) a — Test: `true`
  - Chạm: `scripts/a.py`
  - Cần: T1.2
- [ ] **T1.2** (n3 e5m) b — Test: `true`
  - Chạm: `scripts/b.py`
  - Cần: T1.1
"""

SLUG = "2026-08-17-1828-x"
BAN_DO_REL = os.path.join("docs", "tdq", "team", SLUG + ".json")


def git(cwd, *args, check=True):
    proc = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True)
    if check and proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} → {proc.returncode}\n{proc.stderr}")
    return proc.stdout.strip()


class TeamBase(unittest.TestCase):
    """Project TDQ giả lập + repo git tạm. Không bao giờ đụng repo thật."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def _project(self, plan=PLAN_TRON):
        write_state(self.cwd, active_request=SLUG, lane="full", phase="implement",
                    implement_mode="subagent", plan_approved=True, plan_file=PLAN_REL)
        write_file(self.cwd, PLAN_REL, plan)

    def _git_repo(self):
        """Repo git thật trong thư mục tạm, đã có 1 commit gốc."""
        git(self.cwd, "init", "-q", "-b", "chinh")
        git(self.cwd, "config", "user.email", "test@example.com")
        git(self.cwd, "config", "user.name", "test")
        write_file(self.cwd, "goc.txt", "goc\n")
        git(self.cwd, "add", "-A")
        git(self.cwd, "commit", "-q", "-m", "goc")

    def _ban_do(self):
        with open(os.path.join(self.cwd, BAN_DO_REL), encoding="utf-8") as f:
            return json.load(f)

    def _duong_worktree(self, ma):
        wt = git(self.cwd, "worktree", "list", "--porcelain")
        for dong in wt.splitlines():
            if dong.startswith("worktree ") and dong.lower().rstrip().endswith(ma.lower()):
                return dong.split(" ", 1)[1]
        raise AssertionError(f"khong thay worktree cua {ma}:\n{wt}")

    def _duong_tich_hop(self):
        wt = git(self.cwd, "worktree", "list", "--porcelain")
        for dong in wt.splitlines():
            if dong.startswith("worktree ") and "tich-hop" in dong:
                return dong.split(" ", 1)[1]
        raise AssertionError(f"khong thay worktree tich hop:\n{wt}")


    def chay(self, *args, env=None):
        return run_team_cli(self.cwd, *args, env=env)


class PhuThuocTest(unittest.TestCase):
    """T3.1 — dòng `- Cần:` là lời khai phụ thuộc, đọc được bằng máy."""

    def _tasks(self, plan):
        with tempfile.TemporaryDirectory() as d:
            duong = os.path.join(d, "plan.md")
            with open(duong, "w", encoding="utf-8") as f:
                f.write(plan)
            return tdq_team.doc_plan(duong)

    def test_phu_thuoc_doc_dung_mot_ma(self):
        pt = tdq_team.doc_phu_thuoc(self._tasks(PLAN_CAN))
        self.assertEqual(pt["T1.2"], {"T1.1"})

    def test_phu_thuoc_doc_dung_nhieu_ma(self):
        pt = tdq_team.doc_phu_thuoc(self._tasks(PLAN_CAN))
        self.assertEqual(pt["T1.3"], {"T1.1", "T1.2"})

    def test_phu_thuoc_khong_khai_thi_rong(self):
        pt = tdq_team.doc_phu_thuoc(self._tasks(PLAN_CAN))
        self.assertEqual(pt["T1.1"], set())
        self.assertEqual(pt["T1.4"], set())

    def test_phu_thuoc_du_moi_task(self):
        pt = tdq_team.doc_phu_thuoc(self._tasks(PLAN_CAN))
        self.assertEqual(set(pt), {"T1.1", "T1.2", "T1.3", "T1.4"})

    def test_phu_thuoc_bo_qua_ma_chinh_no(self):
        """Task tự nhắc mã của chính nó không thành vòng lặp."""
        plan = PLAN_CAN.replace("  - Cần: T1.1\n", "  - Cần: T1.1, T1.2\n")
        pt = tdq_team.doc_phu_thuoc(self._tasks(plan))
        self.assertEqual(pt["T1.2"], {"T1.1"})

    def test_phu_thuoc_bo_qua_ma_khong_co_that(self):
        """Khai mã không có trong plan thì bỏ qua — plan sai không làm sập lệnh."""
        plan = PLAN_CAN.replace("  - Cần: T1.1\n", "  - Cần: T1.1, T9.9\n")
        pt = tdq_team.doc_phu_thuoc(self._tasks(plan))
        self.assertEqual(pt["T1.2"], {"T1.1"})


class ChiaDotTest(unittest.TestCase):
    """T3.2 — đợt xếp theo `Cần:` đã khai, không theo tên phase."""

    def _tasks(self, plan):
        with tempfile.TemporaryDirectory() as d:
            duong = os.path.join(d, "plan.md")
            with open(duong, "w", encoding="utf-8") as f:
                f.write(plan)
            return tdq_team.doc_plan(duong)

    def _quyet(self, plan):
        tasks = self._tasks(plan)
        return {t.ma: tdq_team.quyet_dinh_task(t, tasks) for t in tasks}

    def _dot(self, plan):
        tasks = self._tasks(plan)
        return tdq_team.chia_dot(tasks, self._quyet(plan))

    def test_chia_dot_vong_lap_khong_lam_sap(self):
        """`Cần:` khai vòng là plan sai, nhưng lệnh phải cắt vòng chứ không văng."""
        dot = self._dot(PLAN_CAN_VONG)
        self.assertEqual(set(dot), {"T1.1", "T1.2"})
        for ma, d in dot.items():
            with self.subTest(task=ma):
                self.assertGreaterEqual(d, 1)

    def test_chia_dot_vong_lap_van_tach_file(self):
        """Cắt vòng không được kéo theo việc quên luật chung file."""
        plan = PLAN_CAN_VONG.replace("`scripts/b.py`", "`scripts/a.py`")
        dot = self._dot(plan)
        self.assertNotEqual(dot["T1.1"], dot["T1.2"])

    def test_chia_dot_theo_chuoi_can(self):
        dot = self._dot(PLAN_CAN)
        self.assertLess(dot["T1.1"], dot["T1.2"])
        self.assertLess(dot["T1.2"], dot["T1.3"])

    def test_chia_dot_khong_khai_thi_dot_dau(self):
        """Task không khai `Cần:` và không đụng file ai thì được chạy ngay đợt 1."""
        dot = self._dot(PLAN_CAN)
        self.assertEqual(dot["T1.1"], 1)
        self.assertEqual(dot["T1.4"], 1)

    def test_chia_dot_bo_qua_ranh_gioi_phase(self):
        """Đây là chỗ ăn thời gian: P2 không khai `Cần:` thì chạy song song với P1."""
        dot = self._dot(PLAN_CAN_CHEO)
        self.assertEqual(dot["T2.1"], 1)
        self.assertEqual(dot["T1.1"], 1)

    def test_chia_dot_chung_file_van_tach_dot(self):
        dot = self._dot(PLAN_CAN_CHEO)
        self.assertNotEqual(dot["T2.1"], dot["T2.2"])

    def test_chia_dot_khai_can_khong_bi_giu_lai(self):
        """Khai `Cần:` là ràng buộc LỊCH TRÌNH, không phải cớ để leader giữ task.

        Trước luật này, một task nhắc mã task khác chưa xong là tự động `tu_lam` —
        thêm dòng `Cần:` sẽ giết sạch song song, ngược hẳn ý đồ.
        """
        quyet = self._quyet(PLAN_CAN)
        for ma in ("T1.2", "T1.3"):
            with self.subTest(task=ma):
                self.assertEqual(quyet[ma][0], "giao", quyet[ma])

    def test_chia_dot_plan_cu_van_giu_ly_do_phu_thuoc(self):
        """Plan không khai `Cần:` thì luật cũ đọc theo văn xuôi vẫn còn hiệu lực."""
        quyet = self._quyet(PLAN_TRON)
        self.assertEqual(quyet["T1.4"], ("tu_lam", "phu-thuoc"))

    def test_chia_dot_plan_cu_giu_nguyen_luat_phase(self):
        """Plan không khai `Cần:` ở đâu cả → lùi về luật cũ, số đợt y như trước."""
        dot = self._dot(PLAN_8_TASK)
        self.assertLess(max(dot[m] for m in ("T1.1", "T1.2", "T1.3")),
                        min(dot[m] for m in ("T2.1", "T2.2")))
        self.assertEqual(max(dot.values()), 2)


class DuongGangTest(unittest.TestCase):
    """T3.3 — b-level: task nào nằm trên đường găng thì phát trước."""

    def _b(self, plan):
        with tempfile.TemporaryDirectory() as d:
            duong = os.path.join(d, "plan.md")
            with open(duong, "w", encoding="utf-8") as f:
                f.write(plan)
            tasks = tdq_team.doc_plan(duong)
        return tdq_team.b_level(tasks, tdq_team.doc_phu_thuoc(tasks))

    def test_duong_gang_cong_don_theo_chuoi(self):
        b = self._b(PLAN_CAN)
        self.assertEqual(b["T1.3"], 5)
        self.assertEqual(b["T1.2"], 10)
        self.assertEqual(b["T1.1"], 15)

    def test_duong_gang_nhanh_le_ngan_hon(self):
        b = self._b(PLAN_CAN)
        self.assertEqual(b["T1.4"], 5)
        self.assertGreater(b["T1.1"], b["T1.4"])

    def test_duong_gang_khong_khai_phut_thi_tinh_mot(self):
        plan = PLAN_CAN.replace(" e5m", "")
        b = self._b(plan)
        self.assertEqual(b["T1.3"], 1)
        self.assertEqual(b["T1.1"], 3)

    def test_duong_gang_du_moi_task(self):
        b = self._b(PLAN_CAN_CHEO)
        self.assertEqual(set(b), {"T1.1", "T1.2", "T2.1", "T2.2"})


class PhanCongTest(TeamBase):
    """T2.2 + T2.3 — đọc cả plan, dựng bản đồ phân công."""

    def test_ban_do_du_moi_task_va_du_4_truong(self):
        self._project(PLAN_8_TASK)
        rc, out, _err = self.chay("phan-cong")
        self.assertEqual(rc, 0, out)
        ban_do = self._ban_do()
        self.assertEqual(len(ban_do["tasks"]), 8)
        for ma, rec in ban_do["tasks"].items():
            with self.subTest(task=ma):
                for truong in ("quyet_dinh", "ly_do", "vung_file", "dot"):
                    self.assertIn(truong, rec)

    def test_phase_sau_nam_o_dot_sau(self):
        self._project(PLAN_8_TASK)
        self.chay("phan-cong")
        tasks = self._ban_do()["tasks"]
        dot_p1 = max(tasks[m]["dot"] for m in ("T1.1", "T1.2", "T1.3"))
        dot_p2 = min(tasks[m]["dot"] for m in ("T2.1", "T2.2"))
        self.assertLess(dot_p1, dot_p2)

    def test_hai_task_chung_file_khong_cung_dot(self):
        self._project(PLAN_CHUNG_FILE)
        self.chay("phan-cong")
        tasks = self._ban_do()["tasks"]
        self.assertNotEqual(tasks["T1.1"]["dot"], tasks["T1.2"]["dot"])

    def test_mac_dinh_la_giao(self):
        self._project(PLAN_8_TASK)
        self.chay("phan-cong")
        tasks = self._ban_do()["tasks"]
        self.assertTrue(all(r["quyet_dinh"] == "giao" for r in tasks.values()),
                        [(m, r["quyet_dinh"]) for m, r in tasks.items()])

    def test_task_roi_cung_dot_task_phu_thuoc_va_mcp_thi_tu_lam(self):
        """T2.3 — 3 task rời cùng một đợt; task phụ thuộc và task (mcp) bị giữ lại."""
        self._project(PLAN_TRON)
        rc, out, _err = self.chay("phan-cong")
        self.assertEqual(rc, 0, out)
        tasks = self._ban_do()["tasks"]
        roi = [tasks[m] for m in ("T1.1", "T1.2", "T1.3")]
        self.assertEqual({r["quyet_dinh"] for r in roi}, {"giao"})
        self.assertEqual(len({r["dot"] for r in roi}), 1)
        self.assertEqual(tasks["T1.4"]["quyet_dinh"], "tu_lam")
        self.assertEqual(tasks["T1.4"]["ly_do"], "phu-thuoc")
        self.assertEqual(tasks["T1.5"]["quyet_dinh"], "tu_lam")
        self.assertEqual(tasks["T1.5"]["ly_do"], "mcp")

    def test_khong_khai_vung_file_thi_bi_giu_lai(self):
        self._project("""# PLAN — mau

## P1 — nen
- [ ] **T1.1** (n3 e5m) viec khong khai file — Test: `true`
""")
        self.chay("phan-cong")
        rec = self._ban_do()["tasks"]["T1.1"]
        self.assertEqual(rec["quyet_dinh"], "tu_lam")
        self.assertEqual(rec["ly_do"], "vung-khoa")

    def test_sua_file_luat_thi_bi_giu_lai(self):
        self._project("""# PLAN — mau

## P1 — nen
- [ ] **T1.1** (n3 e5m) sua luat build — Test: `true`
  - Chạm: `skills/tdq-build/SKILL.md`
""")
        self.chay("phan-cong")
        rec = self._ban_do()["tasks"]["T1.1"]
        self.assertEqual(rec["quyet_dinh"], "tu_lam")
        self.assertEqual(rec["ly_do"], "file-luat")

    def test_ghi_plan_sha_de_khoa_ban_do(self):
        self._project(PLAN_8_TASK)
        self.chay("phan-cong")
        self.assertTrue(self._ban_do()["plan_sha"])


class KiemKeTest(TeamBase):
    """T2.4 + T2.5 — kiểm kê bản đồ, khoá theo sha."""

    def test_ban_do_sach_thi_exit_0(self):
        self._project(PLAN_8_TASK)
        self.chay("phan-cong")
        rc, out, _err = self.chay("kiem-ke")
        self.assertEqual(rc, 0, out)

    def test_chua_phan_cong_thi_exit_khac_0(self):
        self._project(PLAN_8_TASK)
        rc, _out, err = self.chay("kiem-ke")
        self.assertNotEqual(rc, 0)
        self.assertIn("phan-cong", err)

    def test_tu_lam_thieu_ly_do_thi_exit_khac_0_va_neu_ma_task(self):
        self._project(PLAN_8_TASK)
        self.chay("phan-cong")
        path = os.path.join(self.cwd, BAN_DO_REL)
        ban_do = self._ban_do()
        ban_do["tasks"]["T2.3"] = dict(ban_do["tasks"]["T2.3"],
                                       quyet_dinh="tu_lam", ly_do="")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(ban_do, f)
        rc, _out, err = self.chay("kiem-ke")
        self.assertNotEqual(rc, 0)
        self.assertIn("T2.3", err)
        self.assertIn("Kept:", err)

    def test_ly_do_ngoai_4_nhom_thi_exit_khac_0(self):
        self._project(PLAN_8_TASK)
        self.chay("phan-cong")
        path = os.path.join(self.cwd, BAN_DO_REL)
        ban_do = self._ban_do()
        ban_do["tasks"]["T2.3"] = dict(ban_do["tasks"]["T2.3"],
                                       quyet_dinh="tu_lam", ly_do="tien-hon")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(ban_do, f)
        rc, _out, err = self.chay("kiem-ke")
        self.assertNotEqual(rc, 0)
        self.assertIn("T2.3", err)

    def test_plan_doi_thi_ban_do_het_hieu_luc(self):
        self._project(PLAN_8_TASK)
        self.chay("phan-cong")
        write_file(self.cwd, PLAN_REL, PLAN_8_TASK + "\n<!-- them mot dong -->\n")
        rc, _out, err = self.chay("cum")
        self.assertNotEqual(rc, 0)
        self.assertIn("phan-cong", err)
        rc, _out, err = self.chay("kiem-ke")
        self.assertNotEqual(rc, 0)


class VaQcTest(TeamBase):
    """Vá sau QC độc lập 2026-08-17 — bốn đường lách/kẹt mà bộ test đầu không bắt."""

    def _hong_ban_do(self):
        with open(os.path.join(self.cwd, BAN_DO_REL), "w", encoding="utf-8") as f:
            f.write("{ khong phai json")

    def test_giao_ma_vung_file_rong_thi_kiem_ke_do(self):
        """Cửa lách rẻ nhất: khai `giao` nhưng xoá vùng file → hook hết chỗ so."""
        self._project(PLAN_8_TASK)
        self.chay("phan-cong")
        ban_do = self._ban_do()
        ma = next(m for m, r in ban_do["tasks"].items() if r["quyet_dinh"] == "giao")
        ban_do["tasks"][ma]["vung_file"] = []
        with open(os.path.join(self.cwd, BAN_DO_REL), "w", encoding="utf-8") as f:
            json.dump(ban_do, f)
        rc, _out, err = self.chay("kiem-ke")
        self.assertNotEqual(rc, 0)
        self.assertIn(ma, err)
        self.assertIn("file area is EMPTY", err)

    def test_ban_do_hong_thi_cli_bao_lenh_sua_chu_khong_van_traceback(self):
        self._project(PLAN_8_TASK)
        self.chay("phan-cong")
        self._hong_ban_do()
        rc, _out, err = self.chay("kiem-ke")
        self.assertNotEqual(rc, 0)
        self.assertNotIn("Traceback", err)
        self.assertIn("phan-cong", err)

    def test_ban_do_hong_thi_hook_chan_chu_khong_mo_toang(self):
        """Fail-open ở đây là mở đúng cửa mà bản đồ sinh ra để canh."""
        self._project(PLAN_TRON)
        self.chay("phan-cong")
        self._hong_ban_do()
        canh_bao = tdq_team.canh_bao_lach_luat(self.cwd, "scripts/alpha.py")
        self.assertIsNotNone(canh_bao)
        self.assertEqual(canh_bao["kieu"], "ban-do-hong")

    def test_kiem_neu_dung_ten_file_xung_dot(self):
        self._project(PLAN_TRON)
        self._git_repo()
        self.chay("phan-cong")
        self.chay("mo", "T1.1")
        # hai nhánh cùng sửa một file → xung đột thật, phải gọi đúng tên file
        cay = os.path.join(self.cwd, ".tdq-worktrees", SLUG, "t1.1")
        write_file(cay, "scripts/alpha.py", "AAA\n")
        git(cay, "add", "-A")
        git(cay, "commit", "-q", "-m", "a")
        cay_tich_hop = os.path.join(self.cwd, ".tdq-worktrees", SLUG, "tich-hop")
        write_file(cay_tich_hop, "scripts/alpha.py", "BBB\n")
        git(cay_tich_hop, "add", "-A")
        git(cay_tich_hop, "commit", "-q", "-m", "b")
        rc, out, err = self.chay("kiem", "T1.1")
        self.assertNotEqual(rc, 0, out)
        self.assertIn("scripts/alpha.py", out + err)

    def test_cum_noi_ro_vi_sao_task_chua_duoc_phat(self):
        self._project(PLAN_CHUNG_FILE)
        self.chay("phan-cong")
        _rc, out, _err = self.chay("cum")
        self.assertIn("HELD", out)


class CumTest(TeamBase):
    """T2.6 — đợt kế tiếp, trừ vùng đang khoá."""

    def test_cum_in_dung_task_dot_dau(self):
        self._project(PLAN_8_TASK)
        self.chay("phan-cong")
        rc, out, _err = self.chay("cum")
        self.assertEqual(rc, 0, out)
        for ma in ("T1.1", "T1.2", "T1.3"):
            self.assertIn(ma, out)
        # T2.1 được nêu ở dòng HOÃN, nhưng KHÔNG được nằm trong danh sách phát
        self.assertNotIn("  T2.1  ", out)

    def test_task_cham_vung_dang_khoa_thi_bi_giu(self):
        plan = PLAN_8_TASK.replace("- [ ] **T1.1**", "- [>] **T1.1**")
        plan = plan.replace("  - Chạm: `scripts/b.py`", "  - Chạm: `scripts/a.py`")
        self._project(plan)
        self.chay("phan-cong")
        rc, out, _err = self.chay("cum")
        self.assertEqual(rc, 0, out)
        self.assertIn("scripts/a.py", out)
        self.assertNotIn("\n  T1.2 ", "\n" + out)

    def test_hết_task_giao_thi_bao_het(self):
        self._project(PLAN_8_TASK.replace("- [ ] **", "- [x] **"))
        self.chay("phan-cong")
        rc, out, _err = self.chay("cum")
        self.assertEqual(rc, 0, out)
        self.assertIn("DONE", out.upper())


class CumLienTucTest(TeamBase):
    """T3.4 — phát liên tục: sẵn sàng là phát, không chờ cả đợt trước hợp xong."""

    def test_lien_tuc_phat_task_khong_dinh_nhau(self):
        self._project(PLAN_CAN_CHEO)
        self.chay("phan-cong")
        rc, out, _err = self.chay("cum")
        self.assertEqual(rc, 0, out)
        self.assertIn("\n  T1.1 ", "\n" + out)
        self.assertIn("\n  T2.1 ", "\n" + out)

    def test_lien_tuc_hoan_task_con_cho_task_khac(self):
        self._project(PLAN_CAN_CHEO)
        self.chay("phan-cong")
        _rc, out, _err = self.chay("cum")
        self.assertIn("HELD T1.2", out)
        self.assertIn("T1.1", out.split("HELD T1.2")[1].split("\n")[0])

    def test_lien_tuc_khong_phat_hai_task_chung_file(self):
        self._project(PLAN_CAN_CHEO)
        self.chay("phan-cong")
        _rc, out, _err = self.chay("cum")
        phat = [d.strip().split()[0] for d in out.splitlines()
                if d.startswith("  ") and not d.strip().startswith("HELD")]
        self.assertIn("T2.1", phat)
        self.assertNotIn("T2.2", phat)

    def test_lien_tuc_dot_sau_phat_ngay_khi_vung_file_ranh(self):
        """Điểm ăn thời gian: T1.2 ở đợt 2 được phát ngay khi T1.1 xong."""
        plan = PLAN_CAN_CHEO.replace("- [ ] **T1.1**", "- [x] **T1.1**")
        self._project(plan)
        self.chay("phan-cong")
        _rc, out, _err = self.chay("cum")
        phat = [d.strip().split()[0] for d in out.splitlines()
                if d.startswith("  ") and not d.strip().startswith("HELD")]
        self.assertIn("T1.2", phat)
        self.assertIn("T2.1", phat)

    def test_lien_tuc_sap_theo_duong_gang(self):
        """Task trên đường găng đứng trước trong danh sách phát."""
        self._project(PLAN_CAN_CHEO)
        self.chay("phan-cong")
        _rc, out, _err = self.chay("cum")
        phat = [d.strip().split()[0] for d in out.splitlines()
                if d.startswith("  ") and not d.strip().startswith("HELD")]
        self.assertEqual(phat[0], "T1.1")


class TranSongSongTest(TeamBase):
    """T3.5 — trần 4 nhánh một lượt, và đúng là trần TRÊN chứ không phải hạn ngạch."""

    def _phat(self, plan):
        self._project(plan)
        self.chay("phan-cong")
        _rc, out, _err = self.chay("cum")
        return [d.strip().split()[0] for d in out.splitlines()
                if d.startswith("  ") and not d.strip().startswith(("HELD", "WAITING"))], out

    def test_tran_chin_task_roi_nhau_chi_phat_bon(self):
        phat, out = self._phat(PLAN_N_ROI)
        self.assertEqual(len(phat), tdq_team.TRAN_SONG_SONG, out)

    def test_tran_phan_du_in_cho_slot(self):
        _phat, out = self._phat(PLAN_N_ROI)
        self.assertIn("WAITING FOR A SLOT: 5 task", out)

    def test_tran_it_task_thi_phat_it(self):
        plan = "\n".join(PLAN_N_ROI.splitlines()[:7]) + "\n"
        phat, out = self._phat(plan)
        self.assertEqual(len(phat), 2, out)
        self.assertNotIn("CHỜ SLOT", out)

    def test_tran_dem_ca_task_dang_bay(self):
        """Trần là trần của SỐ NHÁNH ĐANG CHẠY, không phải của một lượt phát.

        Phát liên tục mà chỉ đếm trong lượt thì 3 task `[>]` cộng 4 task mới = 7 nhánh
        cùng lúc — vượt đúng cái trần vừa đặt.
        """
        plan = PLAN_N_ROI
        for i in (1, 2, 3):
            plan = plan.replace(f"- [ ] **T1.{i}**", f"- [>] **T1.{i}**")
        phat, out = self._phat(plan)
        self.assertEqual(len(phat), 1, out)

    def test_tran_day_slot_thi_khong_phat_them(self):
        plan = PLAN_N_ROI
        for i in (1, 2, 3, 4):
            plan = plan.replace(f"- [ ] **T1.{i}**", f"- [>] **T1.{i}**")
        phat, out = self._phat(plan)
        self.assertEqual(phat, [], out)
        self.assertIn("WAITING FOR A SLOT", out)

    def test_tran_la_hang_so_co_chu_thich_nguon(self):
        self.assertEqual(tdq_team.TRAN_SONG_SONG, 4)


class LyDoGiuTest(TeamBase):
    """T3.6 — nhóm lý do thứ năm: task dựng hợp đồng dùng chung."""

    def test_ly_do_co_nhom_hop_dong(self):
        self.assertIn("hop-dong", tdq_team.LY_DO_GIU)
        self.assertEqual(len(tdq_team.LY_DO_GIU), 5)

    def test_ly_do_hop_dong_qua_duoc_kiem_ke(self):
        self._project(PLAN_8_TASK)
        self.chay("phan-cong")
        duong = os.path.join(self.cwd, BAN_DO_REL)
        with open(duong, encoding="utf-8") as f:
            ban_do = json.load(f)
        ban_do["tasks"]["T1.1"].update(quyet_dinh="tu_lam", ly_do="hop-dong")
        with open(duong, "w", encoding="utf-8") as f:
            json.dump(ban_do, f, ensure_ascii=False)
        rc, out, err = self.chay("kiem-ke")
        self.assertEqual(rc, 0, out + err)

    def test_ly_do_ngoai_bang_van_bi_chan(self):
        self._project(PLAN_8_TASK)
        self.chay("phan-cong")
        duong = os.path.join(self.cwd, BAN_DO_REL)
        with open(duong, encoding="utf-8") as f:
            ban_do = json.load(f)
        ban_do["tasks"]["T1.1"].update(quyet_dinh="tu_lam", ly_do="ngai-giao")
        with open(duong, "w", encoding="utf-8") as f:
            json.dump(ban_do, f, ensure_ascii=False)
        rc, _out, err = self.chay("kiem-ke")
        self.assertEqual(rc, 1)
        self.assertIn("5 groups", err)


class GitTest(TeamBase):
    """T2.7 → T2.10 — nhánh, worktree, dò xung đột, hợp, dọn."""

    def setUp(self):
        super().setUp()
        self._git_repo()
        self._project(PLAN_8_TASK)
        self.chay("phan-cong")

    def _nhanh(self):
        return git(self.cwd, "branch", "--format=%(refname:short)").splitlines()

    def test_mo_tao_dung_mot_worktree_va_nhanh_dung_khuon(self):
        rc, out, _err = self.chay("mo", "T1.1")
        self.assertEqual(rc, 0, out)
        wt = git(self.cwd, "worktree", "list")
        self.assertEqual(len([d for d in wt.splitlines() if "t1.1" in d.lower()]), 1, wt)
        nhanh = [b for b in self._nhanh() if "t1.1" in b.lower()]
        self.assertEqual(len(nhanh), 1, self._nhanh())
        for cam in ("claude", "antigravity", "gemini", "codex"):
            self.assertFalse(nhanh[0].startswith(cam), nhanh[0])

    def test_mo_khong_doi_nhanh_dang_dung_cua_user(self):
        truoc = git(self.cwd, "rev-parse", "--abbrev-ref", "HEAD")
        self.chay("mo", "T1.1")
        self.assertEqual(git(self.cwd, "rev-parse", "--abbrev-ref", "HEAD"), truoc)

    def test_kiem_bao_xung_dot_va_khong_dung_repo(self):
        self.chay("mo", "T1.1")
        self.chay("mo", "T1.2")
        for ma in ("T1.1", "T1.2"):
            wt = self._duong_worktree(ma)
            write_file(wt, "chung.txt", f"noi dung cua {ma}\n")
            git(wt, "add", "-A")
            git(wt, "commit", "-q", "-m", f"{ma} sua chung.txt")
        self.chay("hop", "T1.1")
        truoc = git(self.cwd, "status", "--porcelain")
        rc, out, _err = self.chay("kiem", "T1.2")
        self.assertNotEqual(rc, 0, out)
        self.assertIn("CONFLICT", out.upper())
        self.assertEqual(git(self.cwd, "status", "--porcelain"), truoc)

    def test_kiem_khong_chet_khi_git_in_byte_khong_phai_utf8(self):
        # Lỗi thật, lộ ra ở lượt chạy benchmark 2026-08-17: `git merge-tree` in cả nội
        # dung object, gặp byte nhị phân là cả lệnh `kiem` văng UnicodeDecodeError.
        self.chay("mo", "T1.1")
        self.chay("mo", "T1.2")
        # Không có byte NUL: git coi là file VĂN BẢN nên in thẳng nội dung ra stdout,
        # mà nội dung đó lại không giải mã được bằng UTF-8. Đúng ca đã làm chết `kiem`.
        for ma, byte in (("T1.1", b"latin \xcb\xfe nhanh mot\n"),
                         ("T1.2", b"latin \xcb\xff nhanh hai\n")):
            wt = self._duong_worktree(ma)
            with open(os.path.join(wt, "van_ban_latin.txt"), "wb") as f:
                f.write(byte)
            git(wt, "add", "-A")
            git(wt, "commit", "-q", "-m", f"{ma} them file nhi phan")
        self.chay("hop", "T1.1")
        rc, out, err = self.chay("kiem", "T1.2")
        self.assertNotIn("Traceback", out + err)
        self.assertNotIn("UnicodeDecodeError", out + err)
        self.assertIn(rc, (0, 1), out + err)

    def test_kiem_khong_xung_dot_thi_exit_0(self):
        self.chay("mo", "T1.1")
        wt = self._duong_worktree("T1.1")
        write_file(wt, "rieng.txt", "chi mot minh\n")
        git(wt, "add", "-A")
        git(wt, "commit", "-q", "-m", "T1.1")
        rc, out, _err = self.chay("kiem", "T1.1")
        self.assertEqual(rc, 0, out)

    def test_hop_ba_nhanh_roi_nhau_du_ba_commit(self):
        for ma in ("T1.1", "T1.2", "T1.3"):
            self.chay("mo", ma)
            wt = self._duong_worktree(ma)
            write_file(wt, f"{ma}.txt", "x\n")
            git(wt, "add", "-A")
            git(wt, "commit", "-q", "-m", f"{ma} xong")
        for ma in ("T1.1", "T1.2", "T1.3"):
            rc, out, _err = self.chay("hop", ma)
            self.assertEqual(rc, 0, out)
        log = git(self._duong_tich_hop(), "log", "--oneline")
        for ma in ("T1.1", "T1.2", "T1.3"):
            self.assertIn(f"{ma} xong", log)

    def test_hop_khong_dong_nhanh_goc_cua_user(self):
        truoc = git(self.cwd, "rev-parse", "chinh")
        self.chay("mo", "T1.1")
        wt = self._duong_worktree("T1.1")
        write_file(wt, "T1.1.txt", "x\n")
        git(wt, "add", "-A")
        git(wt, "commit", "-q", "-m", "T1.1 xong")
        self.chay("hop", "T1.1")
        self.assertEqual(git(self.cwd, "rev-parse", "chinh"), truoc)

    def test_hop_chan_khi_xung_dot(self):
        for ma in ("T1.1", "T1.2"):
            self.chay("mo", ma)
            wt = self._duong_worktree(ma)
            write_file(wt, "chung.txt", f"{ma}\n")
            git(wt, "add", "-A")
            git(wt, "commit", "-q", "-m", f"{ma}")
        self.chay("hop", "T1.1")
        rc, _out, err = self.chay("hop", "T1.2")
        self.assertNotEqual(rc, 0)
        self.assertIn("kiem", err)

    def test_don_sach_worktree_va_khong_con_rac(self):
        self.chay("mo", "T1.1")
        self.chay("mo", "T1.2")
        rc, out, _err = self.chay("don")
        self.assertEqual(rc, 0, out)
        wt = git(self.cwd, "worktree", "list")
        self.assertEqual(len(wt.splitlines()), 1, wt)
        thu_muc = os.path.join(self.cwd, ".git", "worktrees")
        con_lai = os.listdir(thu_muc) if os.path.isdir(thu_muc) else []
        self.assertEqual(con_lai, [], con_lai)

class HookTest(TeamBase):
    """T3.1 → T3.3 — edit_gate nới cho `[>]` nhưng chặn đúng ca lách luật."""

    def setUp(self):
        super().setUp()
        write_file(self.cwd, os.path.join("docs", "workinglog",
                                          datetime.date.today().strftime("%Y-%m-%d") + ".md"),
                   "# log\n")

    def _payload(self, rel):
        return load_fixture("edit_src.json", cwd=self.cwd, session_id="s-team",
                            tool_input={"file_path": os.path.join(self.cwd, rel)})

    def _sua(self, rel):
        return run_hook("edit_gate.py", self._payload(rel))

    def _plan(self, plan, mode="subagent"):
        write_state(self.cwd, active_request=SLUG, lane="full", phase="implement",
                    implement_mode=mode, spec_approved=True, plan_approved=True,
                    plan_file=PLAN_REL)
        write_file(self.cwd, PLAN_REL, plan)

    # --- T3.1 ---------------------------------------------------------------
    def test_nhieu_dau_giao_khong_bi_chan(self):
        self._plan(PLAN_8_TASK.replace("- [ ] **T1.", "- [>] **T1."), mode="main")
        _rc, out, _err = self._sua("scripts/a.py")
        self.assertNotIn('"deny"', out)

    def test_hai_dau_dang_lam_van_bi_chan(self):
        self._plan(PLAN_8_TASK.replace("- [ ] **T1.1**", "- [~] **T1.1**")
                              .replace("- [ ] **T1.2**", "- [~] **T1.2**"), mode="main")
        _rc, out, _err = self._sua("scripts/a.py")
        self.assertIn('"deny"', out)
        self.assertIn("TDQ:TICK", out)

    def test_khong_dau_nao_van_bi_chan(self):
        self._plan(PLAN_8_TASK, mode="main")
        _rc, out, _err = self._sua("scripts/a.py")
        self.assertIn('"deny"', out)
        self.assertIn("TDQ:TICK", out)

    # --- T3.2 ---------------------------------------------------------------
    def test_main_sua_file_cua_task_giao_thi_bi_chan(self):
        self._plan(PLAN_TRON.replace("- [ ] **T1.1**", "- [~] **T1.1**"))
        self.chay("phan-cong")
        _rc, out, _err = self._sua("scripts/alpha.py")
        self.assertIn('"deny"', out)
        self.assertIn("TDQ:TEAM", out)

    def test_main_sua_file_cua_task_tu_lam_thi_khong_chan(self):
        self._plan(PLAN_TRON.replace("- [ ] **T1.4**", "- [~] **T1.4**"))
        self.chay("phan-cong")
        _rc, out, _err = self._sua("scripts/delta.py")
        self.assertNotIn('"deny"', out)

    def test_mode_main_thi_khong_chan_du_ban_do_ghi_giao(self):
        self._plan(PLAN_TRON.replace("- [ ] **T1.1**", "- [~] **T1.1**"), mode="main")
        self.chay("phan-cong")
        _rc, out, _err = self._sua("scripts/alpha.py")
        self.assertNotIn('"deny"', out)

    def test_chua_phan_cong_ma_sua_code_o_main_thi_bi_chan(self):
        self._plan(PLAN_TRON.replace("- [ ] **T1.1**", "- [~] **T1.1**"))
        _rc, out, _err = self._sua("scripts/alpha.py")
        self.assertIn('"deny"', out)
        self.assertIn("phan-cong", out)

    def test_file_ngoai_moi_vung_thi_khong_chan(self):
        self._plan(PLAN_TRON.replace("- [ ] **T1.4**", "- [~] **T1.4**"))
        self.chay("phan-cong")
        _rc, out, _err = self._sua("scripts/khong-ai-nhan.py")
        self.assertNotIn('"deny"', out)

    # --- T3.3 ---------------------------------------------------------------
    def test_da_giao_ma_khong_co_nhanh_thi_bi_chan(self):
        self._git_repo()
        self._plan(PLAN_TRON.replace("- [ ] **T1.1**", "- [>] **T1.1**"))
        self.chay("phan-cong")
        _rc, out, _err = self._sua("scripts/alpha.py")
        self.assertIn('"deny"', out)
        self.assertIn("mo T1.1", out)

    def test_da_giao_va_co_nhanh_that_thi_khong_chan(self):
        self._git_repo()
        self._plan(PLAN_TRON.replace("- [ ] **T1.1**", "- [>] **T1.1**"))
        self.chay("phan-cong")
        self.chay("mo", "T1.1")
        _rc, out, _err = self._sua("scripts/alpha.py")
        self.assertNotIn('"deny"', out)


class CheckStatusTest(TeamBase):
    """T3.4 — chẩn đoán hiểu mode đội: nhiều `[>]` không phải lỗi, còn ca D12 mới."""

    def _state_day_du(self, plan):
        write_state(self.cwd, active_request=SLUG, lane="full", phase="implement",
                    implement_mode="subagent", spec_approved=True, plan_approved=True,
                    plan_file=PLAN_REL,
                    spec_file=os.path.join("docs", "tdq", "spec", SLUG + ".md"))
        write_file(self.cwd, PLAN_REL, plan)
        write_file(self.cwd, os.path.join("docs", "tdq", "spec", SLUG + ".md"), "# spec\n")

    def _ma_ca(self):
        rc, out, err = run_checkstatus_cli(self.cwd, "report", "--json")
        self.assertEqual(rc, 0, err)
        return json.loads(out)

    def test_nhieu_dau_giao_khong_dinh_D4(self):
        self._state_day_du(PLAN_8_TASK.replace("- [ ] **T1.", "- [>] **T1."))
        ma = {c["ma"] for c in self._ma_ca()["ca_lech"]}
        self.assertNotIn("D4", ma)

    def test_hai_dau_dang_lam_van_dinh_D4(self):
        self._state_day_du(PLAN_8_TASK.replace("- [ ] **T1.1**", "- [~] **T1.1**")
                                      .replace("- [ ] **T1.2**", "- [~] **T1.2**"))
        ma = {c["ma"] for c in self._ma_ca()["ca_lech"]}
        self.assertIn("D4", ma)

    def test_da_giao_ma_chua_merge_thi_dinh_D12(self):
        self._state_day_du(PLAN_8_TASK.replace("- [ ] **T1.1**", "- [>] **T1.1**")
                                      .replace("- [ ] **T1.2**", "- [>] **T1.2**"))
        ca = [c for c in self._ma_ca()["ca_lech"] if c["ma"] == "D12"]
        self.assertTrue(ca, "thiếu ca D12")
        self.assertIn("T1.1", ca[0]["chi_tiet"])
        self.assertIn("T1.2", ca[0]["chi_tiet"])

    def test_khong_co_dau_giao_thi_khong_dinh_D12(self):
        self._state_day_du(PLAN_8_TASK.replace("- [ ] **T1.1**", "- [~] **T1.1**"))
        ma = {c["ma"] for c in self._ma_ca()["ca_lech"]}
        self.assertNotIn("D12", ma)

    def test_D12_neu_hanh_dong_tiep_theo(self):
        self._state_day_du(PLAN_8_TASK.replace("- [ ] **T1.1**", "- [>] **T1.1**"))
        du_lieu = self._ma_ca()
        self.assertIn("tdq_team.py", du_lieu["viec_ke_tiep"])

    def test_bang_lech_va_hang_so_van_khop(self):
        import tdq_checkstatus
        bang = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 "skills", "tdq-check-status", "references",
                                 "bang-lech.md"), encoding="utf-8").read()
        self.assertIn("D12", tdq_checkstatus.CA_LECH)
        self.assertIn("| D12 ", bang)


REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEAM_MODE_MD = os.path.join(REPO, "skills", "tdq-build", "references", "team-mode.md")
BUILD_SKILL = os.path.join(REPO, "skills", "tdq-build", "SKILL.md")
PLAN_SKILL = os.path.join(REPO, "skills", "tdq-plan", "SKILL.md")
PLAN_TEMPLATE = os.path.join(REPO, "skills", "tdq-plan", "references", "plan-template.md")
MODE_GATE = os.path.join(REPO, "skills", "tdq-plan", "references", "mode-gate.md")
CONVENTIONS = os.path.join(REPO, "skills", "tdq-conventions", "SKILL.md")
IMPLEMENTER = os.path.join(REPO, "agents", "tdq-implementer.md")

# 7 trường của khuôn prompt giao việc cho agent con. Thiếu một trường là agent con
# phải đoán — đúng thứ soul cấm ở nguyên tắc "viết cho model yếu nhất".
TRUONG_PROMPT = ["TASK:", "CỤM:", "BASE:", "WORKTREE:", "VÙNG FILE:", "TEST:", "TRẢ VỀ:"]


def _doc(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


class KhuonTest(unittest.TestCase):
    """T4.1 → T4.6 — file luật phải đủ chi tiết cho MỌI model đọc là làm được."""

    def test_khuon_team_mode_du_ba_muc(self):
        # Từ 2026-08-22 file luật viết tiếng Anh; nhận cả hai cách viết tên mục.
        noi_dung = _doc(TEAM_MODE_MD).lower()
        for muc in (("## when it applies", "## khi nào áp dụng"),
                    ("## what to do", "## làm gì"),
                    ("## self-check", "## tự kiểm")):
            self.assertTrue(any(m in noi_dung for m in muc),
                            f"team-mode.md thiếu mục {muc[0]}")

    def test_khuon_bang_tra_du_nhom_giu_va_dong_giao(self):
        noi_dung = _doc(TEAM_MODE_MD)
        for ma in tdq_team.LY_DO_GIU:
            self.assertIn(f"`{ma}`", noi_dung, f"bảng tra thiếu nhóm {ma}")
        self.assertIn("GIAO", noi_dung)
        dong_nhom = [d for d in noi_dung.splitlines() if d.strip().startswith("| `")]
        self.assertEqual(len(dong_nhom), len(tdq_team.LY_DO_GIU),
                         "bảng tra phải liệt kê đủ mọi nhóm giữ")
        dong_giao = [d for d in noi_dung.splitlines()
                     if d.strip().startswith("|") and "GIAO" in d]
        self.assertTrue(dong_giao, "bảng tra thiếu dòng mặc định GIAO")

    def test_khuon_bang_tra_co_cot_dau_hieu_va_cot_lenh_kiem(self):
        noi_dung = _doc(TEAM_MODE_MD)
        tieu_de = [d for d in noi_dung.splitlines()
                   if d.strip().startswith("| Nhóm") or d.strip().startswith("| Group")]
        self.assertTrue(tieu_de, "bảng tra thiếu dòng tiêu đề")
        for cot in (("How to recognise it", "Dấu hiệu"), ("Checked by", "Kiểm bằng")):
            self.assertTrue(any(c in tieu_de[0] for c in cot),
                            f"bảng tra thiếu cột {cot[0]}")

    def test_khuon_co_it_nhat_4_cap_dung_sai(self):
        noi_dung = _doc(TEAM_MODE_MD)
        self.assertGreaterEqual(noi_dung.count("ĐÚNG:") + noi_dung.count("RIGHT:"), 4)
        self.assertGreaterEqual(noi_dung.count("SAI:") + noi_dung.count("WRONG:"), 4)

    def test_khuon_prompt_giao_viec_du_7_truong(self):
        noi_dung = _doc(TEAM_MODE_MD)
        for truong in TRUONG_PROMPT:
            self.assertIn(truong, noi_dung, f"khuôn prompt thiếu trường {truong}")

    def test_khuon_implementer_du_7_truong(self):
        noi_dung = _doc(IMPLEMENTER)
        for truong in TRUONG_PROMPT:
            self.assertIn(truong, noi_dung, f"agent thiếu trường {truong}")

    def test_moi_lenh_neu_trong_file_luat_deu_co_that(self):
        """Luật viết lệnh không tồn tại là bẫy chết người với model yếu."""
        import tdq_team
        mau = re.compile(r"tdq_team\.py ([a-z-]+)")
        for path in (TEAM_MODE_MD, BUILD_SKILL, CONVENTIONS, IMPLEMENTER, MODE_GATE):
            for lenh in set(mau.findall(_doc(path))):
                with self.subTest(file=os.path.basename(path), lenh=lenh):
                    self.assertIn(lenh, tdq_team.LENH)


class LuatTest(unittest.TestCase):
    """T4.2 → T4.5 — các file luật khác đã khớp mô hình đội."""

    def test_build_skill_bo_luat_giao_dung_1_task(self):
        noi_dung = _doc(BUILD_SKILL)
        self.assertNotIn("giao ĐÚNG 1 task", noi_dung)
        self.assertIn("team-mode.md", noi_dung)
        self.assertIn("phan-cong", noi_dung)

    def test_plan_skill_bat_khai_vung_file(self):
        self.assertIn("Chạm:", _doc(PLAN_SKILL))
        self.assertIn("Chạm:", _doc(PLAN_TEMPLATE))
        self.assertIn("## Cụm song song", _doc(PLAN_TEMPLATE))

    def test_mode_gate_ta_dung_mo_hinh_lai(self):
        noi_dung = _doc(MODE_GATE)
        self.assertIn("tự làm", noi_dung)
        self.assertNotIn("mỗi agent một task, một git worktree", noi_dung)

    def test_conventions_co_luat_chong_ngung_va_dung_3_ngoai_le(self):
        noi_dung = _doc(CONVENTIONS)
        # Thân skill viết tiếng Anh từ 2026-08-19; luật và số ngoại lệ không đổi.
        self.assertIn("never end a turn while the plan still has tasks", noi_dung.lower())
        moc = noi_dung.lower().find("three exceptions")
        self.assertGreater(moc, -1, "thiếu khối 3 ngoại lệ")
        khoi = noi_dung[moc:moc + 1200]
        self.assertEqual(len(re.findall(r"^\s*\d\.", khoi, re.M)), 3,
                         "phải đúng 3 ngoại lệ, không hơn không kém")


PLAN_XUONG_DONG = """## P1 — a
- [ ] **T1.1** (e10m) Việc dài nên mô tả phải ngắt sang dòng thứ hai cho dễ đọc,
  phần đuôi nằm ở đây — Test: `pytest -q` xanh
  - Chạm: `scripts/a.py`
  - Cần: T1.0
- [ ] **T1.2** (e5m) Việc một dòng — Test: x
  - Chạm: `scripts/b.py`
"""

PLAN_DUONG_DAN_DONG_NOI = """## P1 — a
- [ ] **T1.1** (e10m) Sửa bộ đọc, mô tả dài nên ngắt dòng và đường dẫn rơi xuống
  dòng sau: `scripts/tdq_team.py` — Test: x
"""

PLAN_HEADING_DONG_TASK = """## P1 — a
- [ ] **T1.1** (e5m) Việc — Test: x
  - Chạm: `scripts/a.py`

## Definition of Done
- Chạm: `scripts/khong-phai-cua-task.py`
"""


class DongNoiTiepTest(unittest.TestCase):
    """Mô tả task ngắt xuống dòng KHÔNG được làm rơi các dòng con phía dưới.

    Trước bản sửa 2026-08-19: dòng nối tiếp thụt lề mà không phải bullet rơi vào
    nhánh đóng task, nên mọi `- Chạm:`/`- Cần:` sau nó bị nuốt im lặng.
    """

    def _tasks(self, plan):
        with tempfile.TemporaryDirectory() as d:
            duong = os.path.join(d, "plan.md")
            with open(duong, "w", encoding="utf-8") as f:
                f.write(plan)
            return tdq_team.doc_plan(duong)

    def test_mo_ta_hai_dong_van_giu_cham_va_can(self):
        t = self._tasks(PLAN_XUONG_DONG)[0]
        self.assertEqual(t.ma, "T1.1")
        self.assertIn("Chạm: `scripts/a.py`", t.text)
        self.assertIn("Cần: T1.0", t.text)
        self.assertEqual(t.vung_file, ["scripts/a.py"])

    def test_duoi_mo_ta_noi_vao_dung_phan_tu_truoc(self):
        t = self._tasks(PLAN_XUONG_DONG)[0]
        self.assertTrue(t.text[0].endswith("`pytest -q` xanh"), t.text[0])
        self.assertIn("phần đuôi nằm ở đây", t.text[0])

    def test_duong_dan_o_dong_noi_tiep_vao_vung_file(self):
        t = self._tasks(PLAN_DUONG_DAN_DONG_NOI)[0]
        self.assertEqual(t.vung_file, ["scripts/tdq_team.py"])

    def test_heading_khong_thut_le_van_dong_task(self):
        t = self._tasks(PLAN_HEADING_DONG_TASK)[0]
        self.assertEqual(t.vung_file, ["scripts/a.py"])


PLAN_MA_CO_CHU = """## P2 — a
### Nhánh A
- [~] **T2A.1** (e5m) Việc nhánh A — Test: x
  - Chạm: `scripts/a.py`
- [ ] **T2A.2** (e5m) Việc kế — Test: x
  - Cần: T2A.1
- [ ] **T2.4b** (e5m) Biến thể b — Test: x
  - Cần: T2A.2
"""


class MaTaskCoChuTest(unittest.TestCase):
    """Mã task có chữ nằm SAU số (`T2A.1`, `T2.4b`) phải đọc được.

    Trước bản sửa 2026-08-19: lớp ký tự `[A-Za-z]+[0-9.]*` chỉ ăn chữ đứng trước số,
    nên sáu task trong plan lịch sử vô hình với cả bộ đọc plan lẫn cổng tick.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def _tasks(self, plan):
        duong = os.path.join(self.cwd, "plan.md")
        with open(duong, "w", encoding="utf-8") as f:
            f.write(plan)
        return tdq_team.doc_plan(duong)

    def test_doc_plan_thay_du_ba_ma_la(self):
        self.assertEqual([t.ma for t in self._tasks(PLAN_MA_CO_CHU)],
                         ["T2A.1", "T2A.2", "T2.4b"])

    def test_phu_thuoc_nhan_ma_la(self):
        pt = tdq_team.doc_phu_thuoc(self._tasks(PLAN_MA_CO_CHU))
        self.assertEqual(pt["T2A.2"], {"T2A.1"})
        self.assertEqual(pt["T2.4b"], {"T2A.2"})

    def test_tick_state_dem_du_va_thay_dang_lam(self):
        write_state(self.cwd, active_request="2026-08-17-1828-x", lane="full",
                    phase="implement", implement_mode="main", plan_file=PLAN_REL)
        write_file(self.cwd, PLAN_REL, PLAN_MA_CO_CHU)
        info = tdq_state.plan_tick_state(self.cwd)
        self.assertEqual(info["total"], 3)
        self.assertTrue(info["has_doing"])
        self.assertFalse(info["all_done"])



class SoWorktreeTest(TeamBase):
    """T2.1 → T2.5 — sổ worktree, dọn sau `hop`, và lệnh `soat`.

    Vì sao khoá bằng test chứ không bằng lời dặn trong skill: `don` đã có sẵn từ lâu và
    vẫn được nhắc ở checklist, nhưng không có gì BẮT ai chạy nó — nên worktree cũ nằm lại
    ăn disk. Luật mới chỉ đáng tin khi hỏng là đỏ.
    """

    def setUp(self):
        super().setUp()
        self._git_repo()
        self._project(PLAN_8_TASK)
        self.chay("phan-cong")

    def _so(self):
        import tdq_worktree_registry as so
        return so.doc(self.cwd)["dong"]

    def _dong_mo(self):
        return [d for d in self._so() if d["trang_thai"] == "mo"]

    def _lam_xong(self, ma, ten_file=None):
        """Mở worktree cho task, commit một file riêng — nhánh sạch, merge được."""
        self.chay("mo", ma)
        wt = self._duong_worktree(ma)
        write_file(wt, ten_file or f"{ma}.txt", "x\n")
        git(wt, "add", "-A")
        git(wt, "commit", "-q", "-m", f"{ma} xong")
        return wt

    # ---------------------------------------------------------------- T2.1
    def test_mo_ghi_so_mot_dong_dung_duong_dan(self):
        self.chay("mo", "T1.1")
        dong = self._dong_mo()
        self.assertEqual(len(dong), 1, dong)
        self.assertEqual(dong[0]["ma_task"], "T1.1")
        self.assertTrue(os.path.isdir(dong[0]["duong_dan"]), dong[0]["duong_dan"])

    def test_mo_khong_ghi_so_khi_git_that_bai(self):
        """Sổ ghi TRƯỚC khi git thành công thì sổ nói dối ngay từ dòng đầu tiên."""
        self.chay("mo", "T1.1")
        rc, _out, _err = self.chay("mo", "T1.1")
        self.assertNotEqual(rc, 0)
        self.assertEqual(len(self._dong_mo()), 1)

    # ---------------------------------------------------------------- T2.2
    def test_hop_don_khi_sach_go_worktree_va_nhanh(self):
        wt = self._lam_xong("T1.1")
        rc, out, _err = self.chay("hop", "T1.1")
        self.assertEqual(rc, 0, out)
        self.assertFalse(os.path.isdir(wt), "worktree sạch mà không được dọn")
        nhanh = git(self.cwd, "branch", "--format=%(refname:short)").splitlines()
        self.assertNotIn(f"tdq/{SLUG}/t1.1", nhanh, nhanh)
        self.assertEqual(self._dong_mo(), [])

    def test_hop_giu_nhanh_tich_hop(self):
        self._lam_xong("T1.1")
        self.chay("hop", "T1.1")
        nhanh = git(self.cwd, "branch", "--format=%(refname:short)").splitlines()
        self.assertIn(f"tdq/{SLUG}/tich-hop", nhanh, nhanh)

    def test_hop_khong_mat_commit_cua_task(self):
        self._lam_xong("T1.1")
        self.chay("hop", "T1.1")
        log = git(self._duong_tich_hop(), "log", "--oneline")
        self.assertIn("T1.1 xong", log)

    # ---------------------------------------------------------------- T2.3
    def test_hop_giu_khi_ban(self):
        wt = self._lam_xong("T1.1")
        write_file(wt, "chua_commit.txt", "dang lam do\n")
        rc, out, err = self.chay("hop", "T1.1")
        self.assertEqual(rc, 0, out + err)
        self.assertTrue(os.path.isdir(wt), "worktree còn việc chưa commit mà bị xoá")
        self.assertEqual(len(self._dong_mo()), 1)
        self.assertIn("NOT CLEANED UP YET", out + err)
        self.assertIn("chua_commit.txt", out + err)

    def test_hop_giu_khi_chua_merge(self):
        """Xung đột thì `hop` chặn từ đầu — không merge, không xoá, có gợi ý."""
        for ma in ("T1.1", "T1.2"):
            self.chay("mo", ma)
            wt = self._duong_worktree(ma)
            write_file(wt, "chung.txt", f"{ma}\n")
            git(wt, "add", "-A")
            git(wt, "commit", "-q", "-m", ma)
        self.chay("hop", "T1.1")
        wt2 = self._duong_worktree("T1.2")
        rc, out, err = self.chay("hop", "T1.2")
        self.assertNotEqual(rc, 0)
        self.assertTrue(os.path.isdir(wt2))
        self.assertIn("NOT CLEANED UP YET", out + err)
        self.assertIn("kiem T1.2", out + err)

    def test_khoi_goi_y_in_o_cuoi(self):
        """Khối gợi ý phải là thứ CUỐI CÙNG in ra — nó là thứ user cần đọc và hành động."""
        wt = self._lam_xong("T1.1")
        write_file(wt, "chua_commit.txt", "x\n")
        _rc, out, _err = self.chay("hop", "T1.1")
        dong = [d for d in out.strip().splitlines() if d.strip()]
        vi_tri = [i for i, d in enumerate(dong) if "NOT CLEANED UP YET" in d]
        self.assertTrue(vi_tri, out)
        self.assertGreater(len(dong) - vi_tri[0], 1, "khối gợi ý không có phương án nào")

    # ---------------------------------------------------------------- T2.4
    def test_soat_liet_ke_du_nam_cot(self):
        self._lam_xong("T1.1")
        rc, out, _err = self.chay("soat")
        self.assertEqual(rc, 0, out)
        for cot in ("age", "size", "clean", "merged"):
            self.assertIn(cot, out.lower(), out)
        self.assertIn("t1.1", out.lower())

    def test_soat_khong_dung_worktree_ngoai_tam(self):
        ngoai = os.path.join(self.cwd, "ngoai-tam")
        git(self.cwd, "worktree", "add", "-q", "-b", "nhanh-ngoai", ngoai)
        rc, out, _err = self.chay("soat", "--don")
        self.assertEqual(rc, 0, out)
        self.assertTrue(os.path.isdir(ngoai), "worktree ngoài .tdq-worktrees bị xoá")
        self.assertIn("out of scope", out.lower())

    def test_soat_tu_dong_dong_dong_tro_vao_thu_muc_bien_mat(self):
        self.chay("mo", "T1.1")
        duong = self._dong_mo()[0]["duong_dan"]
        git(self.cwd, "worktree", "remove", "--force", duong)
        rc, out, _err = self.chay("soat")
        self.assertEqual(rc, 0, out)
        self.assertEqual(self._dong_mo(), [], "dòng sổ mồ côi không được tự đóng")

    def test_soat_canh_bao_khi_qua_tuoi(self):
        import tdq_worktree_registry as so
        self.chay("mo", "T1.1")
        du_lieu = so.doc(self.cwd)
        du_lieu["dong"][0]["tao_luc"] = "2020-01-01T00:00:00"
        with open(so.duong_so(self.cwd), "w", encoding="utf-8") as f:
            json.dump(du_lieu, f)
        _rc, out, _err = self.chay("soat")
        self.assertIn("WARNING", out.upper())
        self.assertIn(str(so.TRAN_TUOI_NGAY), out)

    def test_soat_sinh_ban_md(self):
        self.chay("mo", "T1.1")
        self.chay("soat")
        duong = os.path.join(self.cwd, "docs", "tdq", "worktrees.md")
        self.assertTrue(os.path.exists(duong))
        self.assertIn("T1.1", open(duong, encoding="utf-8").read())

    # ---------------------------------------------------------------- T2.5
    def test_soat_don_dep_cai_sach_giu_cai_ban(self):
        wt1 = self._lam_xong("T1.1")
        wt2 = self._lam_xong("T1.2")
        # T1.1 đã merge và sạch → dọn được. T1.2 bẩn → phải giữ lại kèm gợi ý.
        self.chay("hop", "T1.1")
        write_file(wt2, "chua_commit.txt", "x\n")
        rc, out, err = self.chay("soat", "--don")
        # Spec §2 đầu ra 4: còn worktree bẩn thì lệnh phải thoát khác 0.
        self.assertNotEqual(rc, 0, out + err)
        self.assertFalse(os.path.isdir(wt1))
        self.assertTrue(os.path.isdir(wt2))
        self.assertIn("NOT CLEANED UP YET", out + err)

    def test_soat_don_khong_xoa_khi_chua_merge(self):
        wt = self._lam_xong("T1.1")
        rc, out, _err = self.chay("soat", "--don")
        self.assertEqual(rc, 0, out)
        self.assertTrue(os.path.isdir(wt), "nhánh chưa merge mà worktree đã bị xoá")
        self.assertIn("hop T1.1", out)

    def test_soat_khong_con_gi_thi_khong_in_khoi_goi_y(self):
        rc, out, _err = self.chay("soat")
        self.assertEqual(rc, 0, out)
        self.assertNotIn("NOT CLEANED UP YET", out)


class LogWorktreeTest(TeamBase):
    """T6.1 — mở/đóng/xoá worktree đều để lại một dòng log có timestamp, tắt được."""

    def setUp(self):
        super().setUp()
        self._git_repo()
        self._project(PLAN_8_TASK)
        self.chay("phan-cong")

    def test_log_ghi_moc_mo_va_don(self):
        _rc, _out, err = self.chay("mo", "T1.1")
        self.assertIn("open 2026-08-17-1828-x/T1.1", err)
        wt = self._duong_worktree("T1.1")
        write_file(wt, "T1.1.txt", "x\n")
        git(wt, "add", "-A")
        git(wt, "commit", "-q", "-m", "xong")
        _rc, _out, err = self.chay("hop", "T1.1")
        self.assertIn("cleaned T1.1", err)
        self.assertRegex(err, r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\]")

    def test_log_tat_duoc_qua_config(self):
        _rc, _out, err = self.chay("mo", "T1.1", env={"TDQ_LOG": "0"})
        self.assertNotIn("open ", err)
        self.assertEqual(err.strip(), "")


class VaLuoiWorktreeTest(TeamBase):
    """Vòng fix QC 1 — những ca QC độc lập bắt được, khoá lại bằng test.

    Mỗi test dưới đây ứng với một khiếm khuyết THẬT đã tái hiện được, không phải ca
    giả định: sổ hỏng, dòng sổ thiếu trường, worktree tích hợp bị bỏ quên, file bị
    .gitignore bị xoá âm thầm, và `don` cũ xoá cả worktree còn việc.
    """

    def setUp(self):
        super().setUp()
        self._git_repo()
        self._project(PLAN_8_TASK)
        self.chay("phan-cong")

    def _so_json(self):
        return os.path.join(self.cwd, "docs", "tdq", "worktrees.json")

    def _so_hong(self):
        os.makedirs(os.path.dirname(self._so_json()), exist_ok=True)
        with open(self._so_json(), "w", encoding="utf-8") as f:
            f.write("{ hong")

    def test_so_hong_thi_mo_bao_loi_chu_khong_de_lai_worktree_mo_coi(self):
        """Ghi sổ hỏng thì worktree sinh ra sẽ vô hình với `soat` và với cổng qc."""
        self._so_hong()
        rc, out, err = self.chay("mo", "T1.1")
        self.assertEqual(rc, 1, out + err)
        self.assertNotIn("Traceback", err)
        self.assertIn("ledger", (out + err).lower())
        wt = git(self.cwd, "worktree", "list", "--porcelain")
        self.assertNotIn("t1.1", wt.lower(), "worktree mồ côi vẫn được tạo")

    def test_so_hong_thi_soat_khong_vang_traceback(self):
        self._so_hong()
        rc, _out, err = self.chay("soat")
        self.assertNotIn("Traceback", err)
        self.assertIn(rc, (0, 1))

    def test_dong_so_thieu_duong_dan_khong_lam_soat_no(self):
        """Dòng hỏng mà không đóng được thì cổng qc kẹt vĩnh viễn."""
        self.chay("mo", "T1.1")
        with open(self._so_json(), encoding="utf-8") as f:
            du_lieu = json.load(f)
        du_lieu["dong"][0].pop("duong_dan")
        with open(self._so_json(), "w", encoding="utf-8") as f:
            json.dump(du_lieu, f)
        rc, out, err = self.chay("soat")
        self.assertNotIn("Traceback", err)
        self.assertEqual(rc, 0, out + err)
        with open(self._so_json(), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["dong"][0]["trang_thai"], "dong")

    def test_soat_don_go_ca_worktree_tich_hop_nhung_giu_nhanh(self):
        self.chay("mo", "T1.1")
        wt = self._duong_worktree("T1.1")
        write_file(wt, "a.txt", "x\n")
        git(wt, "add", "-A")
        git(wt, "commit", "-q", "-m", "xong")
        tich_hop = self._duong_tich_hop()
        self.chay("hop", "T1.1")
        rc, out, _err = self.chay("soat", "--don")
        self.assertEqual(rc, 0, out)
        self.assertFalse(os.path.isdir(tich_hop), out)
        nhanh = git(self.cwd, "branch", "--format=%(refname:short)").splitlines()
        self.assertIn(f"tdq/{SLUG}/tich-hop", nhanh, nhanh)

    def test_file_bi_gitignore_khong_bi_xoa_am_tham(self):
        """`git worktree remove` xoá cả file bị ignore — `.env` mất là mất hẳn."""
        self.chay("mo", "T1.1")
        wt = self._duong_worktree("T1.1")
        write_file(wt, ".gitignore", ".env\n")
        git(wt, "add", "-A")
        git(wt, "commit", "-q", "-m", "ignore")
        write_file(wt, ".env", "SECRET=1\n")
        rc, out, err = self.chay("hop", "T1.1")
        self.assertEqual(rc, 0, out + err)
        self.assertTrue(os.path.exists(os.path.join(wt, ".env")), out + err)
        self.assertIn("NOT CLEANED UP YET", out + err)
        self.assertIn(".env", out + err)

    def test_rac_sinh_lai_duoc_van_cho_don(self):
        """Chặn vì `__pycache__` thì không bao giờ dọn được gì — cấm chặn kiểu đó."""
        self.chay("mo", "T1.1")
        wt = self._duong_worktree("T1.1")
        write_file(wt, ".gitignore", "__pycache__/\n")
        git(wt, "add", "-A")
        git(wt, "commit", "-q", "-m", "ignore")
        os.makedirs(os.path.join(wt, "__pycache__"), exist_ok=True)
        write_file(wt, os.path.join("__pycache__", "x.pyc"), "x")
        rc, out, err = self.chay("hop", "T1.1")
        self.assertEqual(rc, 0, out + err)
        self.assertFalse(os.path.isdir(wt), out + err)

    def test_don_khong_xoa_worktree_con_viec_chua_commit(self):
        self.chay("mo", "T1.1")
        wt = self._duong_worktree("T1.1")
        write_file(wt, "dang_lam.txt", "x\n")
        rc, out, err = self.chay("don")
        self.assertEqual(rc, 0, out + err)
        self.assertTrue(os.path.isdir(wt), "don cũ vẫn xoá worktree còn việc")
        self.assertIn("NOT CLEANED UP YET", out + err)

    def test_worktree_bi_khoa_khong_lam_chet_ca_luot_soat(self):
        """Một worktree khoá mà làm văng cả lượt quét thì mọi worktree bẩn khác mất khối gợi ý."""
        self.chay("mo", "T1.1")
        self.chay("mo", "T1.2")
        ban = self._duong_worktree("T1.2")
        write_file(ban, "dang_lam.txt", "x\n")
        khoa = self._duong_tich_hop()
        git(self.cwd, "worktree", "lock", khoa)
        try:
            rc, out, err = self.chay("soat", "--don")
        finally:
            git(self.cwd, "worktree", "unlock", khoa)
        self.assertNotIn("Traceback", err)
        self.assertNotEqual(rc, 0, out)
        self.assertIn("NOT CLEANED UP YET", out, out)
        self.assertIn("T1.2", out, out)
        self.assertTrue(os.path.isdir(khoa), "worktree bị khoá vẫn bị xoá")

    def test_worktree_bi_khoa_khong_lam_chet_don(self):
        self.chay("mo", "T1.1")
        wt = self._duong_worktree("T1.1")
        git(self.cwd, "worktree", "lock", wt)
        try:
            rc, out, err = self.chay("don")
        finally:
            git(self.cwd, "worktree", "unlock", wt)
        self.assertNotIn("Traceback", err)
        self.assertEqual(rc, 0, out + err)
        self.assertTrue(os.path.isdir(wt))
        self.assertIn("NOT CLEANED UP YET", out, out)

    def test_rac_ignored_la_ly_do_rieng_va_phuong_an_go_duoc_that(self):
        """Gọi `build/` là 'uncommitted changes' thì user chạy 2 lệnh vô hiệu rồi kẹt mãi."""
        self.chay("mo", "T1.1")
        wt = self._duong_worktree("T1.1")
        write_file(wt, ".gitignore", "build/\n")
        git(wt, "add", "-A")
        git(wt, "commit", "-q", "-m", "ignore")
        os.makedirs(os.path.join(wt, "build"), exist_ok=True)
        write_file(wt, os.path.join("build", "out.o"), "x")
        rc, out, _err = self.chay("soat", "--don")
        self.assertNotEqual(rc, 0, out)
        self.assertIn("ignored files here do not regenerate", out, out)
        self.assertIn("clean -fdx", out, out)
        # Phương án gợi ý phải thật sự gỡ được, chạy đúng như in ra.
        git(wt, "clean", "-fdx")
        rc2, out2, _err2 = self.chay("soat", "--don")
        # Hết lý do `bo-qua`; còn lại đúng một lý do tiến được là chưa merge.
        self.assertEqual(rc2, 0, out2)
        self.assertNotIn("ignored files here do not regenerate", out2, out2)

    def test_worktree_khong_co_dong_so_van_bi_kiem_du_dieu_kien(self):
        """Thư mục lạ trong tầm cũng phải qua đủ ba điều kiện, không chỉ mỗi 'sạch'."""
        self.chay("mo", "T1.1")
        wt = self._duong_worktree("T1.1")
        write_file(wt, ".gitignore", ".env\n")
        git(wt, "add", "-A")
        git(wt, "commit", "-q", "-m", "ignore")
        write_file(wt, ".env", "SECRET=1\n")
        so = self._so_json()
        with open(so, encoding="utf-8") as f:
            du_lieu = json.load(f)
        du_lieu["dong"] = []
        with open(so, "w", encoding="utf-8") as f:
            json.dump(du_lieu, f)
        rc, out, _err = self.chay("soat", "--don")
        self.assertIn("In scope, no ledger row:", out, out)
        self.assertNotEqual(rc, 0, out)
        self.assertTrue(os.path.exists(os.path.join(wt, ".env")), out)

    def test_git_tu_choi_khong_phai_khoa_thi_khong_dan_nhan_khoa(self):
        """Dán nhãn 'khoa' cho lỗi quyền là gửi user đi chạy `worktree unlock` vô ích."""
        self.chay("mo", "T1.1")
        wt = self._duong_worktree("T1.1")
        cha = os.path.dirname(wt)
        cu = os.stat(cha).st_mode
        os.chmod(cha, 0o500)
        try:
            rc, out, err = self.chay("soat", "--don")
        finally:
            os.chmod(cha, cu)
        self.assertNotIn("Traceback", err)
        self.assertIn("NOT CLEANED UP YET", out, out)
        self.assertIn("git refused to remove", out, out)
        self.assertNotIn("git has this worktree locked", out, out)
        self.assertNotIn("worktree unlock", out, out)
        self.assertEqual(rc, 0, out)

    def test_worktree_khoa_that_van_giu_nhan_khoa(self):
        self.chay("mo", "T1.1")
        wt = self._duong_worktree("T1.1")
        git(self.cwd, "worktree", "lock", wt)
        try:
            _rc, out, _err = self.chay("soat", "--don")
        finally:
            git(self.cwd, "worktree", "unlock", wt)
        self.assertIn("git has this worktree locked", out, out)


if __name__ == "__main__":
    unittest.main()
