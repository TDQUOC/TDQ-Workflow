"""Đội sub-agent gộp vào NHÁNH REQUEST, không đẻ thêm tầng nhánh tích hợp (chốt C5).

Trước việc này có ba tầng: nhánh task → nhánh tích hợp `tdq/<slug>/tich-hop` → nhánh user.
Tầng giữa là thứ đẻ ra nhánh mồ côi khi request kết thúc mà không ai dọn. Nay nhánh request
do intake mở đóng luôn vai đó, còn hai tầng.

Mọi ca ở đây dựng repo git trong thư mục tạm — không ca nào được đụng repo thật.
"""
import json
import os
import subprocess
import tempfile
import unittest

from helper import write_state, write_file, run_team_cli  # noqa: F401 — bơm scripts/ vào sys.path

SLUG = "2026-09-05-0833-thu-doi"
PLAN_REL = os.path.join("docs", "tdq", "plan", SLUG + ".md")
NHANH_REQUEST = "feature/thu-doi"
NHANH_GOC = "chinh"

PLAN = """# PLAN — mau

## P1 — nen
- [ ] **T1.1** (e5m) sua alpha — Test: `true`
  - Chạm: `scripts/alpha.py`
- [ ] **T1.2** (e5m) sua beta — Test: `true`
  - Chạm: `scripts/beta.py`
"""


def git(cwd, *args, check=True):
    proc = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True)
    if check and proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} → {proc.returncode}\n{proc.stderr}")
    return proc.stdout.strip()


class DoiBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)
        git(self.cwd, "init", "-q", "-b", NHANH_GOC)
        git(self.cwd, "config", "user.email", "test@example.com")
        git(self.cwd, "config", "user.name", "test")
        write_file(self.cwd, "goc.txt", "goc\n")
        git(self.cwd, "add", "-A")
        git(self.cwd, "commit", "-q", "-m", "goc")
        # Đúng thứ intake làm ở bước 3b: mở nhánh request rồi ghi ba khoá vào state.
        git(self.cwd, "switch", "-q", "-c", NHANH_REQUEST)
        write_state(self.cwd, active_request=SLUG, lane="full", phase="implement",
                    implement_mode="subagent", plan_approved=True, plan_file=PLAN_REL,
                    loai_request="feature", nhanh_goc=NHANH_GOC,
                    nhanh_request=NHANH_REQUEST)
        write_file(self.cwd, PLAN_REL, PLAN)
        self.chay("assign")

    def chay(self, *args):
        return run_team_cli(self.cwd, *args)

    def _nhanh(self):
        return git(self.cwd, "branch", "--format=%(refname:short)").splitlines()

    def _duong_worktree(self, ma):
        wt = git(self.cwd, "worktree", "list", "--porcelain")
        for dong in wt.splitlines():
            if dong.startswith("worktree ") and dong.lower().rstrip().endswith(ma.lower()):
                return dong.split(" ", 1)[1]
        raise AssertionError(f"không thấy worktree của {ma}:\n{wt}")

    def _lam_xong(self, ma):
        """Mở task, commit một file riêng trong worktree của nó."""
        rc, out, err = self.chay("open", ma)
        self.assertEqual(rc, 0, out + err)
        wt = self._duong_worktree(ma)
        write_file(wt, f"{ma}.txt", "x\n")
        git(wt, "add", "-A")
        git(wt, "commit", "-q", "-m", f"{ma} xong")
        return wt


class KhongNhanhTichHopTest(DoiBase):
    def test_khong_nhanh_tich_hop_nao_duoc_tao(self):
        """Không nhánh nào mang đuôi `tich-hop` được sinh ra nữa."""
        self._lam_xong("T1.1")
        rc, out, err = self.chay("merge", "T1.1")
        self.assertEqual(rc, 0, out + err)
        con_lai = [n for n in self._nhanh() if n.endswith("tich-hop")]
        self.assertEqual(con_lai, [], f"vẫn còn nhánh tích hợp: {con_lai}")

    def test_nhanh_task_base_tu_nhanh_request(self):
        """Nhánh task mọc ra từ nhánh request, không từ một nhánh trung gian nào khác."""
        moc = git(self.cwd, "rev-parse", NHANH_REQUEST)
        self.chay("open", "T1.1")
        nhanh_task = [n for n in self._nhanh() if n.lower().endswith("t1.1")]
        self.assertEqual(len(nhanh_task), 1, self._nhanh())
        self.assertEqual(git(self.cwd, "rev-parse", nhanh_task[0]), moc,
                         "nhánh task không base từ đúng nhánh request")


class VongDoiTest(DoiBase):
    def test_vong_doi_day_du_mo_hop_don(self):
        """`open` → `merge` → chỉ còn nhánh gốc và nhánh request, không sót worktree nào."""
        for ma in ("T1.1", "T1.2"):
            self._lam_xong(ma)
        for ma in ("T1.1", "T1.2"):
            rc, out, err = self.chay("merge", ma)
            self.assertEqual(rc, 0, out + err)
        self.assertEqual(sorted(self._nhanh()), sorted([NHANH_GOC, NHANH_REQUEST]),
                         "còn sót nhánh sau khi gộp")
        wt = git(self.cwd, "worktree", "list")
        self.assertEqual(len(wt.splitlines()), 1, wt)
        log = git(self.cwd, "log", "--oneline", NHANH_REQUEST)
        for ma in ("T1.1", "T1.2"):
            self.assertIn(f"{ma} xong", log, f"commit của {ma} không nằm trên nhánh request")

    def test_hop_khong_dong_nhanh_goc_cua_user(self):
        """Nhánh gốc chỉ được động tới ở bước 10 của báo cáo, không phải lúc gộp task."""
        truoc = git(self.cwd, "rev-parse", NHANH_GOC)
        self._lam_xong("T1.1")
        self.chay("merge", "T1.1")
        self.assertEqual(git(self.cwd, "rev-parse", NHANH_GOC), truoc)


if __name__ == "__main__":
    unittest.main()
