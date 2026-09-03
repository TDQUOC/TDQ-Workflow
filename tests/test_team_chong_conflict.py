#!/usr/bin/env python3
"""Tests for the anti-conflict work on team mode (request 2026-09-03-1527).

Covers: the English command names + hidden aliases (P0), verifying a sub-agent's
result before merge (P1), enforcing the declared file area (P2), rebase and the
conflict-resolution command (P3), the hot-file warning (P4), and the log lines (P6).
"""
import contextlib
import io
import os
import re
import subprocess
import sys

import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(GOC, "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

import tdq_ten_lenh  # noqa: E402


# ------------------------------------------------------------------ P0 doi_ten
def test_doi_ten_bang_du_5_script():
    """Every CLI script that had Vietnamese sub-commands is in the table."""
    assert set(tdq_ten_lenh.BANG_DOI_TEN) == {
        "tdq_team.py", "tdq_bench.py", "tdq_eval.py", "tdq_lsp.py", "tdq_state.py",
    }


def test_doi_ten_ten_moi_giu_nguyen():
    """An official English name resolves to itself."""
    bang = tdq_ten_lenh.BANG_DOI_TEN["tdq_team.py"]
    assert tdq_ten_lenh.giai_ten("merge", bang) == "merge"
    assert tdq_ten_lenh.giai_ten("assign", bang) == "assign"


def test_doi_ten_ten_cu_thanh_ten_moi():
    """An old Vietnamese name resolves to its English replacement."""
    bang = tdq_ten_lenh.BANG_DOI_TEN["tdq_team.py"]
    assert tdq_ten_lenh.giai_ten("hop", bang) == "merge"
    assert tdq_ten_lenh.giai_ten("phan-cong", bang) == "assign"
    assert tdq_ten_lenh.giai_ten("kiem", bang) == "check"


def test_doi_ten_ten_la_tra_none():
    """A name in neither column resolves to None, so the CLI can report it."""
    bang = tdq_ten_lenh.BANG_DOI_TEN["tdq_team.py"]
    assert tdq_ten_lenh.giai_ten("khong-co-lenh-nay", bang) is None


def test_doi_ten_khong_lan_giua_cac_script():
    """`kiem` means `check` in both tdq_team and tdq_lsp, but the tables stay separate."""
    assert tdq_ten_lenh.giai_ten("kiem", tdq_ten_lenh.BANG_DOI_TEN["tdq_lsp.py"]) == "check"
    assert tdq_ten_lenh.giai_ten("hop", tdq_ten_lenh.BANG_DOI_TEN["tdq_lsp.py"]) is None


def test_doi_ten_moi_ten_moi_la_ascii_tieng_anh():
    """No new name may carry a Vietnamese diacritic — that is the whole point."""
    for bang in tdq_ten_lenh.BANG_DOI_TEN.values():
        for ten_moi in set(bang.values()):
            assert ten_moi.isascii(), ten_moi


def test_doi_ten_bi_danh_khong_dam_len_ten_moi():
    """An old name must never collide with a different command's new name."""
    for ten_script, bang in tdq_ten_lenh.BANG_DOI_TEN.items():
        ten_moi = set(bang.values())
        for cu, moi in bang.items():
            if cu != moi:
                assert cu not in ten_moi, f"{ten_script}: {cu} clashes"


def _chay(script, *args):
    return subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, script), *args],
        capture_output=True, text=True, cwd=GOC, timeout=120)


@pytest.mark.parametrize("script", sorted(tdq_ten_lenh.BANG_DOI_TEN))
def test_doi_ten_help_chi_in_ten_moi(script):
    """`--help` advertises the English names only; the aliases stay hidden."""
    if script == "tdq_state.py":
        pytest.skip("tdq_state.py dispatches by hand, it has no argparse --help")
    proc = _chay(script, "--help")
    assert proc.returncode == 0, proc.stderr
    bang = tdq_ten_lenh.BANG_DOI_TEN[script]
    for cu, moi in bang.items():
        if cu != moi:
            # Whole word only: `mo` also lives inside "remove", `don` inside "conditions".
            assert not re.search(rf"(?<![\w-]){re.escape(cu)}(?![\w-])", proc.stdout), \
                f"{script} --help still shows {cu}"
        assert moi in proc.stdout, f"{script} --help is missing {moi}"


def test_doi_ten_team_chay_duoc_ca_hai_ten():
    """tdq_team accepts the new name and the alias for the same sub-command."""
    moi = _chay("tdq_team.py", "check", "--help")
    cu = _chay("tdq_team.py", "kiem", "--help")
    assert moi.returncode == 0 and cu.returncode == 0


# ------------------------------------------------------- P1 lay_lenh_test / kiem_chay_test
import tdq_team  # noqa: E402


def _task_gia(dong_task, *phu):
    """Build one Task the way doc_plan would, without touching the disk."""
    t = tdq_team.Task("T1.1", " ", "P1")
    t.text.append(dong_task)
    t.text.extend(phu)
    return t


def test_lay_lenh_test_lay_dung_lenh_sau_test():
    """The command taken is the first backticked one after `Test:`, not an earlier quote."""
    t = _task_gia("(e6m) Sửa `scripts/a.py` — Test: `python3 -m pytest tests/test_a.py -q` xanh")
    assert tdq_team.lay_lenh_test(t) == "python3 -m pytest tests/test_a.py -q"


def test_lay_lenh_test_khong_co_test_tra_none():
    """A task with no `Test:` at all — nothing to run, so None."""
    assert tdq_team.lay_lenh_test(_task_gia("(e6m) Chỉ sửa tài liệu, không có tiêu chí")) is None


def test_lay_lenh_test_tieu_chi_chu_khong_phai_lenh_tra_none():
    """`Test:` holding a prose pass criterion carries no command to run."""
    t = _task_gia("(e6m) Sửa gì đó — Test: đọc lại thấy đủ 3 mục")
    assert tdq_team.lay_lenh_test(t) is None


# ------------------------------------------------------- P1 `check` really runs the test
import unittest  # noqa: E402

from test_team_mode import SLUG, TeamBase, git  # noqa: E402
from helper import write_file  # noqa: E402
import datetime  # noqa: E402


def _hom_nay():
    return datetime.date.today().strftime("%Y-%m-%d")

PLAN_KIEM = """# PLAN — mau

## P1 — nen
- [ ] **T1.1** (e5m) viec xanh — Test: `true`
  - Chạm: `scripts/a.py`
- [ ] **T1.2** (e5m) viec do — Test: `false`
  - Chạm: `scripts/b.py`
- [ ] **T1.3** (e5m) viec khong co lenh — Test: đọc lại thấy đủ
  - Chạm: `scripts/c.py`
"""


class KiemChayTestTest(TeamBase):
    """T1.2 — `check` runs the task's own `Test:` after the conflict probe."""

    def setUp(self):
        super().setUp()
        self._git_repo()
        self._project(PLAN_KIEM)
        self.chay("assign")

    def _lam(self, ma):
        self.chay("open", ma)
        wt = self._duong_worktree(ma)
        write_file(wt, f"{ma}.txt", "x\n")
        git(wt, "add", "-A")
        git(wt, "commit", "-q", "-m", ma)
        return wt

    def test_kiem_chay_test_xanh_thi_thoat_0(self):
        self._lam("T1.1")
        rc, out, err = self.chay("check", "T1.1")
        self.assertEqual(rc, 0, out + err)
        self.assertIn("true", out + err)

    def test_kiem_chay_test_do_thi_chan_va_noi_loi_CODE(self):
        self._lam("T1.2")
        rc, out, err = self.chay("check", "T1.2")
        self.assertNotEqual(rc, 0)
        self.assertIn("CODE", out + err)
        self.assertIn("T1.2", out + err)

    def test_kiem_khong_co_lenh_thi_bao_loi_PLAN(self):
        self._lam("T1.3")
        rc, out, err = self.chay("check", "T1.3")
        self.assertNotEqual(rc, 0)
        self.assertIn("PLAN", out + err)
        self.assertIn("T1.3", out + err)


class HopChanTestDoTest(TeamBase):
    """T1.3 — `merge` refuses a branch whose own test is red; nothing lands."""

    def setUp(self):
        super().setUp()
        self._git_repo()
        self._project(PLAN_KIEM)
        self.chay("assign")

    def _lam(self, ma):
        self.chay("open", ma)
        wt = self._duong_worktree(ma)
        write_file(wt, f"{ma}.txt", "x\n")
        git(wt, "add", "-A")
        git(wt, "commit", "-q", "-m", ma)
        return wt

    def _so_commit(self):
        return len(git(self._duong_tich_hop(), "log", "--oneline").splitlines())

    def test_hop_chan_test_do(self):
        self._lam("T1.2")
        truoc = self._so_commit()
        rc, out, err = self.chay("merge", "T1.2")
        self.assertNotEqual(rc, 0, out)
        self.assertIn("CODE", out + err)
        self.assertEqual(self._so_commit(), truoc, "nhánh tích hợp nhận commit dù test đỏ")

    def test_hop_chan_khi_plan_khong_co_lenh(self):
        self._lam("T1.3")
        truoc = self._so_commit()
        rc, out, err = self.chay("merge", "T1.3")
        self.assertNotEqual(rc, 0, out)
        self.assertIn("PLAN", out + err)
        self.assertEqual(self._so_commit(), truoc)

    def test_hop_van_qua_khi_test_xanh(self):
        self._lam("T1.1")
        truoc = self._so_commit()
        rc, out, err = self.chay("merge", "T1.1")
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(self._so_commit(), truoc + 2)



class NgoaiVungTest(TeamBase):
    """T2.1 — a write from inside a task's worktree, aimed outside its declared `Chạm:`."""

    def setUp(self):
        super().setUp()
        self._git_repo()
        self._project(PLAN_KIEM)
        self.chay("assign")
        self.chay("open", "T1.1")
        self.wt = self._duong_worktree("T1.1")

    def test_ngoai_vung_trong_vung_thi_khong_canh_bao(self):
        muc = os.path.join(self.wt, "scripts", "a.py")
        self.assertIsNone(tdq_team.ngoai_vung_khai(self.cwd, muc))

    def test_ngoai_vung_ngoai_vung_thi_bao_du_thong_tin(self):
        muc = os.path.join(self.wt, "scripts", "z.py")
        canh = tdq_team.ngoai_vung_khai(self.cwd, muc)
        self.assertIsNotNone(canh)
        self.assertEqual(canh["ma"], "T1.1")
        self.assertEqual(canh["vung_file"], ["scripts/a.py"])
        self.assertEqual(canh["duong"], "scripts/z.py")

    def test_ngoai_vung_ngoai_worktree_tra_none(self):
        """Mode `main` writes in the project itself — the fence must not see it at all."""
        muc = os.path.join(self.cwd, "scripts", "z.py")
        self.assertIsNone(tdq_team.ngoai_vung_khai(self.cwd, muc))

    def test_ngoai_vung_file_test_duoc_mien(self):
        """Red→green means writing the failing test first; tests/ is never someone's zone."""
        muc = os.path.join(self.wt, "tests", "test_z.py")
        self.assertIsNone(tdq_team.ngoai_vung_khai(self.cwd, muc))



class GateChanNgoaiVungTest(TeamBase):
    """T2.2 — the hook blocks a write that leaves the task's declared area."""

    def setUp(self):
        super().setUp()
        self._git_repo()
        self._project(PLAN_KIEM)
        from helper import write_state
        write_state(self.cwd, active_request="2026-08-17-1828-x", lane="full",
                    phase="implement", implement_mode="subagent", spec_approved=True,
                    plan_approved=True,
                    plan_file=os.path.join("docs", "tdq", "plan", "2026-08-17-1828-x.md"))
        self.chay("assign")
        self.chay("open", "T1.1")
        self.wt = self._duong_worktree("T1.1")

    def _sua(self, duong_tuyet_doi):
        from helper import run_hook, load_fixture
        write_file(self.cwd, os.path.join("docs", "workinglog",
                                          _hom_nay() + ".md"), "# log\n")
        payload = load_fixture("edit_src.json", cwd=self.cwd, session_id="s-vung",
                               tool_input={"file_path": duong_tuyet_doi})
        return run_hook("edit_gate.py", payload)

    def test_gate_chan_ngoai_vung_chan_va_noi_du_ba_thu(self):
        _rc, out, _err = self._sua(os.path.join(self.wt, "scripts", "z.py"))
        self.assertIn('"deny"', out)
        self.assertIn("T1.1", out)              # the task code
        self.assertIn("scripts/a.py", out)      # the area it may write in
        self.assertIn("Chạm", out)              # the way out: ask the leader to widen it

    def test_gate_chan_ngoai_vung_cho_qua_trong_vung(self):
        _rc, out, _err = self._sua(os.path.join(self.wt, "scripts", "a.py"))
        self.assertNotIn("outside the file area", out)



class ModeMainKhongDoiTest(TeamBase):
    """T2.3 — the new fence is invisible to mode `main`: no worktree, no verdict."""

    def setUp(self):
        super().setUp()
        self._git_repo()
        from helper import write_state
        write_state(self.cwd, active_request="2026-08-17-1828-x", lane="full",
                    phase="implement", implement_mode="main", spec_approved=True,
                    plan_approved=True,
                    plan_file=os.path.join("docs", "tdq", "plan", "2026-08-17-1828-x.md"))
        write_file(self.cwd, os.path.join("docs", "tdq", "plan",
                                          "2026-08-17-1828-x.md"), PLAN_KIEM)

    def test_mode_main_ghi_ngoai_vung_van_khong_bi_ham_chan(self):
        muc = os.path.join(self.cwd, "scripts", "z.py")
        self.assertIsNone(tdq_team.ngoai_vung_khai(self.cwd, muc))

    def test_mode_main_ghi_trong_vung_cung_khong_bi_ham_chan(self):
        muc = os.path.join(self.cwd, "scripts", "a.py")
        self.assertIsNone(tdq_team.ngoai_vung_khai(self.cwd, muc))



PLAN_REBASE = """# PLAN — mau

## P1 — nen
- [ ] **T1.1** (e5m) viec a — Test: `true`
  - Chạm: `scripts/a.py`
- [ ] **T1.2** (e5m) viec b — Test: `true`
  - Chạm: `scripts/b.py`
- [ ] **T1.3** (e5m) viec c — Test: `true`
  - Chạm: `scripts/c.py`
"""


class RebaseTest(TeamBase):
    """T3.1 — `merge` rebases onto the newest integration branch before probing."""

    def setUp(self):
        super().setUp()
        self._git_repo()
        self._project(PLAN_REBASE)
        self.chay("assign")

    def _lam(self, ma, ten_file, noi_dung):
        self.chay("open", ma)
        wt = self._duong_worktree(ma)
        write_file(wt, ten_file, noi_dung)
        git(wt, "add", "-A")
        git(wt, "commit", "-q", "-m", ma)
        return wt

    def test_rebase_hai_nhanh_noi_tiep_merge_lien_tiep(self):
        """Both branches opened off the same base; the second must still merge untouched."""
        self._lam("T1.1", "a.txt", "a\n")
        self._lam("T1.2", "b.txt", "b\n")
        rc1, o1, e1 = self.chay("merge", "T1.1")
        self.assertEqual(rc1, 0, o1 + e1)
        rc2, o2, e2 = self.chay("merge", "T1.2")
        self.assertEqual(rc2, 0, o2 + e2)
        log = git(self._duong_tich_hop(), "log", "--oneline")
        self.assertIn("T1.1", log)
        self.assertIn("T1.2", log)

    def test_rebase_nhanh_task_dung_tren_ban_tich_hop_moi_nhat(self):
        """The merged branch must sit ON TOP of the integration tip — proof it was rebased.

        Without the rebase, T1.2 still hangs off the base of its wave, so the integration tip
        at merge time is NOT an ancestor of what gets merged. That is gap H2.
        """
        self._lam("T1.1", "a.txt", "a\n")
        self._lam("T1.2", "b.txt", "b\n")
        self.chay("merge", "T1.1")
        truoc = git(self.cwd, "rev-parse", f"tdq/{SLUG}/tich-hop")
        self.chay("merge", "T1.2")
        cha2 = git(self.cwd, "rev-parse", f"tdq/{SLUG}/tich-hop^2")
        rc = subprocess.run(["git", "-C", self.cwd, "merge-base", "--is-ancestor", truoc, cha2],
                            capture_output=True, text=True).returncode
        self.assertEqual(rc, 0, "nhánh task chưa được rebase lên bản tích hợp mới nhất")

    def test_rebase_hong_thi_worktree_khong_ket_giua_chung(self):
        """A conflicting rebase is aborted at once — no worktree left mid-rebase."""
        self._lam("T1.1", "chung.txt", "mot\n")
        wt2 = self._lam("T1.2", "chung.txt", "hai\n")
        self.chay("merge", "T1.1")
        rc, out, err = self.chay("merge", "T1.2")
        self.assertNotEqual(rc, 0, out)
        trang_thai = git(wt2, "status", "--porcelain=v1", "-b")
        self.assertNotIn("REBASE", git(wt2, "status"))
        self.assertNotIn("UU ", trang_thai)



class LenhResolveTest(TeamBase):
    """T3.2 — `resolve` shows what is stuck, and changes nothing on its own."""

    def setUp(self):
        super().setUp()
        self._git_repo()
        self._project(PLAN_REBASE)
        self.chay("assign")
        for ma, noi_dung in (("T1.1", "mot"), ("T1.2", "hai")):
            self.chay("open", ma)
            wt = self._duong_worktree(ma)
            write_file(wt, "chung.txt", noi_dung + "\n")
            git(wt, "add", "-A")
            git(wt, "commit", "-q", "-m", ma)
        self.chay("merge", "T1.1")

    def test_lenh_resolve_neu_dung_file_ket_va_ca_hai_phia(self):
        rc, out, err = self.chay("resolve", "T1.2")
        self.assertNotEqual(rc, 0, "còn conflict mà resolve báo sạch")
        self.assertIn("chung.txt", out + err)
        self.assertIn("mot", out + err)
        self.assertIn("hai", out + err)

    def test_lenh_resolve_khong_tu_sua_file_nao(self):
        truoc = git(self._duong_worktree("T1.2"), "status", "--porcelain")
        sha_truoc = git(self.cwd, "rev-parse", f"tdq/{SLUG}/t1.2")
        self.chay("resolve", "T1.2")
        self.assertEqual(git(self._duong_worktree("T1.2"), "status", "--porcelain"), truoc)
        self.assertEqual(git(self.cwd, "rev-parse", f"tdq/{SLUG}/t1.2"), sha_truoc)

    def test_lenh_resolve_sach_thi_thoat_0(self):
        self.chay("open", "T1.3")
        wt = self._duong_worktree("T1.3")
        write_file(wt, "c.txt", "c\n")
        git(wt, "add", "-A")
        git(wt, "commit", "-q", "-m", "T1.3")
        rc, out, err = self.chay("resolve", "T1.3")
        self.assertEqual(rc, 0, out + err)



PLAN_FILE_NONG = """# PLAN — mau

## P1 — nen
- [ ] **T1.1** (e5m) viec a — Test: `true`
  - Chạm: `scripts/nong.py`
- [ ] **T1.2** (e5m) viec b — Test: `true`
  - Chạm: `scripts/nong.py`, `scripts/b.py`
- [ ] **T1.3** (e5m) viec c — Test: `true`
  - Chạm: `scripts/c.py`
"""


class FileNongTest(TeamBase):
    """T4.1 — `assign` names the files several tasks touch, before any branch is opened."""

    def setUp(self):
        super().setUp()
        self._git_repo()

    def test_file_nong_duoc_neu_ten_va_so_task(self):
        self._project(PLAN_FILE_NONG)
        rc, out, err = self.chay("assign")
        self.assertEqual(rc, 0, out + err)
        self.assertIn("scripts/nong.py", out + err)
        self.assertIn("2", out + err)

    def test_file_nong_khong_co_thi_khong_canh_bao(self):
        self._project(PLAN_REBASE)
        _rc, out, err = self.chay("assign")
        self.assertNotIn("HOT FILE", out + err)



class LogNhanhQuyetDinhTest(TeamBase):
    """T6.1 — every new decision branch logs one line, and `TDQ_LOG=0` mutes all of them."""

    def setUp(self):
        super().setUp()
        self._git_repo()

    def _log_file_nong(self, env):
        self._project(PLAN_FILE_NONG)
        _rc, _out, err = self.chay("assign", env=env)
        return err

    def test_log_file_nong_bat_thi_co_tat_thi_khong(self):
        self.assertIn("HOT FILE", self._log_file_nong({"TDQ_LOG": "1"}))
        self.assertNotIn("HOT FILE", self._log_file_nong({"TDQ_LOG": "0"}))

    def test_log_ngoai_vung_ghi_mot_dong(self):
        self._project(PLAN_KIEM)
        self.chay("assign")
        self.chay("open", "T1.1")
        muc = os.path.join(self._duong_worktree("T1.1"), "scripts", "z.py")
        loi = io.StringIO()
        with contextlib.redirect_stderr(loi):
            tdq_team.ngoai_vung_khai(self.cwd, muc)
        self.assertIn("outside its declared area", loi.getvalue())

    def test_log_ngoai_vung_tat_duoc(self):
        self._project(PLAN_KIEM)
        self.chay("assign")
        self.chay("open", "T1.1")
        muc = os.path.join(self._duong_worktree("T1.1"), "scripts", "z.py")
        loi = io.StringIO()
        cu = os.environ.get("TDQ_LOG")
        os.environ["TDQ_LOG"] = "0"
        try:
            with contextlib.redirect_stderr(loi):
                tdq_team.ngoai_vung_khai(self.cwd, muc)
        finally:
            if cu is None:
                del os.environ["TDQ_LOG"]
            else:
                os.environ["TDQ_LOG"] = cu
        self.assertEqual(loi.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
