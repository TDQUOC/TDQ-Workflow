"""P2 — vùng file, vùng khoá, mốc hoàn tác.

Bốn bất biến, mỗi cái là một cái bẫy đã gặp thật:

1. T2.1 `chup_moc` — cây SẠCH thì `git stash create` trả rỗng, phải lùi về HEAD,
   nếu không mọi phép so sau đó so với chuỗi rỗng và im lặng PASS.
2. T2.2 `hau_kiem` — mốc là sha chụp trước CHÍNH task đó, không phải HEAD; nếu
   lấy HEAD thì việc dở của task trước bị tính nhầm thành task này làm lệch.
3. T2.3 vùng khoá — file test của task không được Codex chạm, kể cả khi test xanh.
4. T2.4 `hoan_tac` — dùng `git restore --source --worktree`, KHÔNG `git checkout
   <sha> -- <file>` (lệnh sau ghi cả index, làm mù hậu kiểm của task kế tiếp).
"""
import os
import subprocess
import sys
import tempfile
import unittest

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_vungfile  # noqa: E402


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True,
                          text=True, encoding="utf-8", timeout=30)


def ghi(cwd, ten, noi_dung):
    duong = os.path.join(cwd, ten)
    os.makedirs(os.path.dirname(duong), exist_ok=True)
    with open(duong, "w", encoding="utf-8") as f:
        f.write(noi_dung)
    return duong


class RepoTam(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = os.path.realpath(self._tmp.name)
        git(self.cwd, "init", "-q", "-b", "main")
        git(self.cwd, "config", "user.email", "t@t.t")
        git(self.cwd, "config", "user.name", "t")
        ghi(self.cwd, "a.py", "A0\n")
        ghi(self.cwd, "b.py", "B0\n")
        git(self.cwd, "add", "-A")
        git(self.cwd, "commit", "-qm", "nen")

    def tearDown(self):
        self._tmp.cleanup()


class ChupMocTest(RepoTam):
    def test_cay_ban_ra_sha_stash(self):
        ghi(self.cwd, "a.py", "A1\n")
        moc = tdq_vungfile.chup_moc(self.cwd)
        self.assertTrue(moc.sha)
        head = git(self.cwd, "rev-parse", "HEAD").stdout.strip()
        self.assertNotEqual(moc.sha, head, "cây bẩn phải ra sha stash, không phải HEAD")

    def test_cay_sach_lui_ve_head(self):
        moc = tdq_vungfile.chup_moc(self.cwd)
        head = git(self.cwd, "rev-parse", "HEAD").stdout.strip()
        self.assertEqual(moc.sha, head)

    def test_ghi_lai_file_chua_theo_doi_luc_chup(self):
        ghi(self.cwd, "moi.py", "M\n")
        moc = tdq_vungfile.chup_moc(self.cwd)
        self.assertIn("moi.py", moc.chua_theo_doi)

    def test_chup_moc_khong_lam_ban_them_cay(self):
        ghi(self.cwd, "a.py", "A1\n")
        truoc = git(self.cwd, "status", "--porcelain").stdout
        tdq_vungfile.chup_moc(self.cwd)
        self.assertEqual(truoc, git(self.cwd, "status", "--porcelain").stdout)


class HauKiemTest(RepoTam):
    def test_sua_trong_vung_thi_pass(self):
        moc = tdq_vungfile.chup_moc(self.cwd)
        ghi(self.cwd, "a.py", "A1\n")
        kq = tdq_vungfile.hau_kiem(self.cwd, moc, ["a.py"])
        self.assertTrue(kq.dat, kq.lech)

    def test_sua_ngoai_vung_thi_fail_kem_ten_file(self):
        moc = tdq_vungfile.chup_moc(self.cwd)
        ghi(self.cwd, "b.py", "B1\n")
        kq = tdq_vungfile.hau_kiem(self.cwd, moc, ["a.py"])
        self.assertFalse(kq.dat)
        self.assertIn("b.py", kq.lech)

    def test_file_moi_ngoai_vung_thi_fail(self):
        moc = tdq_vungfile.chup_moc(self.cwd)
        ghi(self.cwd, "c.py", "C\n")
        kq = tdq_vungfile.hau_kiem(self.cwd, moc, ["a.py"])
        self.assertFalse(kq.dat)
        self.assertIn("c.py", kq.lech)

    def test_ca_quyet_dinh_viec_do_cua_task_truoc_van_pass(self):
        """Ca ĐỎ nếu ai đó so với HEAD thay vì so với mốc của chính task.

        Dựng đúng cảnh thật: task TRƯỚC đã sửa b.py và chưa commit. Task SAU
        chụp mốc rồi chỉ sửa a.py. So với mốc → chỉ thấy a.py → PASS.
        So với HEAD → thấy cả b.py → FAIL oan.
        """
        ghi(self.cwd, "b.py", "B-task-truoc\n")          # việc dở của task trước
        moc = tdq_vungfile.chup_moc(self.cwd)            # task sau bắt đầu ở đây
        ghi(self.cwd, "a.py", "A-task-sau\n")
        kq = tdq_vungfile.hau_kiem(self.cwd, moc, ["a.py"])
        self.assertTrue(kq.dat, f"so nhầm với HEAD: {kq.lech}")

    def test_file_moi_cua_task_truoc_khong_bi_tinh_cho_task_sau(self):
        ghi(self.cwd, "cu.py", "CU\n")                   # task trước tạo, chưa add
        moc = tdq_vungfile.chup_moc(self.cwd)
        ghi(self.cwd, "a.py", "A1\n")
        kq = tdq_vungfile.hau_kiem(self.cwd, moc, ["a.py"])
        self.assertTrue(kq.dat, f"hiệu hai tập file chưa theo dõi sai: {kq.lech}")


class VungKhoaTest(RepoTam):
    def test_cham_vung_khoa_thi_fail_du_test_xanh(self):
        moc = tdq_vungfile.chup_moc(self.cwd)
        ghi(self.cwd, "a.py", "A1\n")
        ghi(self.cwd, "test_a.py", "sửa file test\n")
        kq = tdq_vungfile.hau_kiem(self.cwd, moc, ["a.py", "test_a.py"],
                                   vung_khoa=["test_a.py"])
        self.assertFalse(kq.dat, "vùng khoá phải thắng cả khi file nằm trong vùng file")
        self.assertIn("test_a.py", kq.khoa_bi_cham)

    def test_khong_cham_vung_khoa_thi_pass(self):
        moc = tdq_vungfile.chup_moc(self.cwd)
        ghi(self.cwd, "a.py", "A1\n")
        kq = tdq_vungfile.hau_kiem(self.cwd, moc, ["a.py"], vung_khoa=["test_a.py"])
        self.assertTrue(kq.dat, kq.lech)

    def test_vung_khoa_toi_thieu_gom_file_test(self):
        """Hợp đồng: gọi hàm dựng vùng khoá cho một task thì file test của task
        đó luôn có mặt, kể cả khi người gọi quên."""
        khoa = tdq_vungfile.dung_vung_khoa("tests/test_x.py", them=["docs/y.md"])
        self.assertIn("tests/test_x.py", khoa)
        self.assertIn("docs/y.md", khoa)


class HoanTacTest(RepoTam):
    def test_file_ngoai_vung_tro_ve_noi_dung_moc(self):
        moc = tdq_vungfile.chup_moc(self.cwd)
        ghi(self.cwd, "a.py", "A1\n")
        ghi(self.cwd, "b.py", "B1\n")
        tdq_vungfile.hoan_tac(self.cwd, moc, ["b.py"])
        with open(os.path.join(self.cwd, "b.py"), encoding="utf-8") as f:
            self.assertEqual(f.read(), "B0\n")

    def test_file_trong_vung_giu_nguyen(self):
        moc = tdq_vungfile.chup_moc(self.cwd)
        ghi(self.cwd, "a.py", "A1\n")
        ghi(self.cwd, "b.py", "B1\n")
        tdq_vungfile.hoan_tac(self.cwd, moc, ["b.py"])
        with open(os.path.join(self.cwd, "a.py"), encoding="utf-8") as f:
            self.assertEqual(f.read(), "A1\n")

    def test_file_moi_ngoai_vung_bi_xoa(self):
        moc = tdq_vungfile.chup_moc(self.cwd)
        ghi(self.cwd, "rac.py", "R\n")
        tdq_vungfile.hoan_tac(self.cwd, moc, ["rac.py"])
        self.assertFalse(os.path.exists(os.path.join(self.cwd, "rac.py")))

    def test_index_khong_doi_truoc_sau(self):
        """Ca ĐỎ nếu ai đó dùng `git checkout <sha> -- <file>`: lệnh đó ghi cả
        index, làm mù hậu kiểm của task kế tiếp."""
        ghi(self.cwd, "b.py", "B-staged\n")
        git(self.cwd, "add", "b.py")
        truoc = git(self.cwd, "diff", "--cached", "--name-only").stdout
        moc = tdq_vungfile.chup_moc(self.cwd)
        ghi(self.cwd, "b.py", "B-worktree\n")
        tdq_vungfile.hoan_tac(self.cwd, moc, ["b.py"])
        sau = git(self.cwd, "diff", "--cached", "--name-only").stdout
        self.assertEqual(truoc, sau, "hoàn tác không được chạm index")


class LogTest(RepoTam):
    """T10.1 — log service bật mặc định, tắt được bằng TDQ_LOG=0."""

    def _chay(self, env_them):
        return subprocess.run(
            [sys.executable, os.path.join(ROOT, "scripts", "tdq_vungfile.py"),
             "chup-moc"], cwd=self.cwd, capture_output=True, text=True,
            encoding="utf-8", timeout=30, stdin=subprocess.DEVNULL,
            env=dict(os.environ, **env_them))

    def test_log_bat_mac_dinh(self):
        proc = self._chay({})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(proc.stderr.strip(), "log phải bật mặc định")
        self.assertIn("chup-moc", proc.stderr)

    def test_tat_duoc_bang_bien_moi_truong(self):
        proc = self._chay({"TDQ_LOG": "0"})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stderr.strip(), "", "TDQ_LOG=0 phải tắt sạch log")

    def test_dong_log_co_timestamp(self):
        proc = self._chay({})
        self.assertRegex(proc.stderr, r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")


if __name__ == "__main__":
    unittest.main()
