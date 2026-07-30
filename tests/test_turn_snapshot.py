"""P1 — ảnh chụp trạng thái đầu turn (spec 0.3.1 §4 S3).

Hai helper này là nền của việc vá điểm mù verify-by-effect: chúng nhìn HIỆU ỨNG
trên đĩa, không nhìn tên tool được gọi.
"""
import os
import subprocess
import tempfile
import unittest

from helper import tdq_state, write_file


def git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=30)


class RepoDigestTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def test_digest_changes_on_new_file(self):
        git(self.cwd, "init", "-q")
        before = tdq_state.repo_status_digest(self.cwd)
        self.assertIsInstance(before, str)
        write_file(self.cwd, os.path.join("src", "a.py"), "print(1)\n")
        after = tdq_state.repo_status_digest(self.cwd)
        self.assertIsInstance(after, str)
        self.assertNotEqual(before, after)

    def test_digest_stable_without_change(self):
        git(self.cwd, "init", "-q")
        self.assertEqual(tdq_state.repo_status_digest(self.cwd),
                         tdq_state.repo_status_digest(self.cwd))

    def test_digest_catches_edit_of_already_dirty_file(self):
        """`status --porcelain` không đổi khi sửa tiếp file vốn đã `M` — dễ bỏ lọt."""
        git(self.cwd, "init", "-q")
        write_file(self.cwd, "a.py", "one\n")
        git(self.cwd, "add", "-A")
        git(self.cwd, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "init")
        write_file(self.cwd, "a.py", "two\n")
        before = tdq_state.repo_status_digest(self.cwd)
        write_file(self.cwd, "a.py", "three\n")
        self.assertNotEqual(before, tdq_state.repo_status_digest(self.cwd))

    def test_digest_catches_edit_of_untracked_file(self):
        """QC1.1 — file untracked bị sửa nội dung: porcelain in `?? path` y hệt."""
        git(self.cwd, "init", "-q")
        write_file(self.cwd, "a.py", "hello\n")
        before = tdq_state.repo_status_digest(self.cwd)
        write_file(self.cwd, "a.py", "world!!\n")
        self.assertNotEqual(before, tdq_state.repo_status_digest(self.cwd))

    def test_paths_list_files_not_directories(self):
        git(self.cwd, "init", "-q")
        write_file(self.cwd, os.path.join("src", "a.py"), "print(1)\n")
        self.assertIn("src/a.py", tdq_state.repo_status_paths(self.cwd))

    def test_paths_empty_outside_git(self):
        self.assertEqual(tdq_state.repo_status_paths(self.cwd), [])

    def test_digest_none_outside_git(self):
        self.assertIsNone(tdq_state.repo_status_digest(self.cwd))

    def test_digest_none_when_git_missing(self):
        """PATH không có `git` → None chứ không raise."""
        git(self.cwd, "init", "-q")
        old = os.environ.get("PATH")
        os.environ["PATH"] = os.path.join(self.cwd, "khong-ton-tai")
        try:
            self.assertIsNone(tdq_state.repo_status_digest(self.cwd))
        finally:
            os.environ["PATH"] = old if old is not None else ""


class BookkeepingExclusionTest(unittest.TestCase):
    """0.3.2 — sổ sách của workflow tự đổi gần như mỗi turn (hook append sổ turn NGAY
    sau khi chụp baseline). Tính chúng vào vân tay thì turn read-only cũng bị chặn oan."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)
        git(self.cwd, "init", "-q")

    def commit_all(self):
        git(self.cwd, "add", "-A")
        git(self.cwd, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "x")

    def test_bookkeeping_prefixes_use_forward_slash(self):
        """git luôn in path bằng `/` — dùng os.path.join là tự tắt bộ lọc trên Windows."""
        for prefix in tdq_state.BOOKKEEPING_PATHS:
            self.assertNotIn("\\", prefix)

    def test_digest_ignores_bookkeeping_writes(self):
        before = tdq_state.repo_status_digest(self.cwd)
        write_file(self.cwd, "docs/tdq/state.json", '{"a": 1}\n')
        write_file(self.cwd, "docs/tdq/.tdq-turn.jsonl", '{"kind": "observe"}\n')
        self.assertEqual(before, tdq_state.repo_status_digest(self.cwd))

    def test_digest_ignores_tracked_bookkeeping_change(self):
        """Sổ sách đã commit rồi sửa tiếp → phải lọt qua cả pathspec của `diff HEAD`."""
        write_file(self.cwd, "docs/tdq/state.json", '{"a": 1}\n')
        self.commit_all()
        before = tdq_state.repo_status_digest(self.cwd)
        write_file(self.cwd, "docs/tdq/state.json", '{"a": 2}\n')
        self.assertEqual(before, tdq_state.repo_status_digest(self.cwd))

    def test_digest_ignores_worklog_append(self):
        before = tdq_state.repo_status_digest(self.cwd)
        write_file(self.cwd, "docs/workinglog/2026-07-29.md", "# log\n- x\n")
        self.assertEqual(before, tdq_state.repo_status_digest(self.cwd))

    def test_digest_still_sees_real_file_next_to_bookkeeping(self):
        before = tdq_state.repo_status_digest(self.cwd)
        write_file(self.cwd, "docs/tdq/state.json", '{"a": 1}\n')
        write_file(self.cwd, "src/a.py", "print(1)\n")
        self.assertNotEqual(before, tdq_state.repo_status_digest(self.cwd))

    def test_paths_exclude_bookkeeping(self):
        write_file(self.cwd, "docs/tdq/state.json", "{}\n")
        write_file(self.cwd, "src/a.py", "print(1)\n")
        paths = tdq_state.repo_status_paths(self.cwd)
        self.assertIn("src/a.py", paths)
        self.assertEqual([p for p in paths if p.startswith("docs/")], [])


class UntrackedFingerprintTest(unittest.TestCase):
    """0.3.2 — dấu của file untracked phải theo NỘI DUNG, không theo mtime."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)
        git(self.cwd, "init", "-q")

    def test_digest_stable_when_untracked_only_touched(self):
        """`touch`/ghi đè y hệt byte (formatter, build tool) không phải là thay đổi."""
        path = write_file(self.cwd, "scratch.txt", "same\n")
        before = tdq_state.repo_status_digest(self.cwd)
        st = os.stat(path)
        os.utime(path, ns=(st.st_atime_ns + 10**9, st.st_mtime_ns + 10**9))
        self.assertEqual(before, tdq_state.repo_status_digest(self.cwd))

    def test_digest_catches_untracked_change_same_size_and_mtime(self):
        path = write_file(self.cwd, "scratch.txt", "aaaa\n")
        st = os.stat(path)
        before = tdq_state.repo_status_digest(self.cwd)
        write_file(self.cwd, "scratch.txt", "bbbb\n")
        os.utime(path, ns=(st.st_atime_ns, st.st_mtime_ns))
        self.assertNotEqual(before, tdq_state.repo_status_digest(self.cwd))

    def test_digest_falls_back_to_stat_for_big_untracked_file(self):
        """Quá trần đọc thì vẫn phải có dấu (size), không được bỏ trắng."""
        old = tdq_state.UNTRACKED_HASH_MAX_BYTES
        tdq_state.UNTRACKED_HASH_MAX_BYTES = 4
        try:
            write_file(self.cwd, "big.bin", "x" * 100)
            before = tdq_state.repo_status_digest(self.cwd)
            write_file(self.cwd, "big.bin", "x" * 200)
            self.assertNotEqual(before, tdq_state.repo_status_digest(self.cwd))
        finally:
            tdq_state.UNTRACKED_HASH_MAX_BYTES = old

    def test_untracked_cap_counts_files_not_lines(self):
        """Cap phải đếm FILE untracked; cắt theo dòng status thì 1 dòng `M` là đủ nuốt hết."""
        write_file(self.cwd, "a.py", "one\n")
        git(self.cwd, "add", "-A")
        git(self.cwd, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "init")
        write_file(self.cwd, "a.py", "two\n")             # dòng status đầu tiên: ` M a.py`
        path = write_file(self.cwd, "b.txt", "aaaa\n")    # dòng thứ hai: `?? b.txt`
        st = os.stat(path)
        old = tdq_state.UNTRACKED_STAT_CAP
        tdq_state.UNTRACKED_STAT_CAP = 1
        try:
            before = tdq_state.repo_status_digest(self.cwd)
            write_file(self.cwd, "b.txt", "bbbb\n")
            os.utime(path, ns=(st.st_atime_ns, st.st_mtime_ns))
            self.assertNotEqual(before, tdq_state.repo_status_digest(self.cwd))
        finally:
            tdq_state.UNTRACKED_STAT_CAP = old

    def test_digest_from_subdirectory(self):
        """porcelain in path theo repo root — stat theo cwd là trật khi chạy từ thư mục con."""
        sub = os.path.join(self.cwd, "sub")
        path = write_file(self.cwd, "sub/x.txt", "aaaa\n")
        st = os.stat(path)
        before = tdq_state.repo_status_digest(sub)
        self.assertIsInstance(before, str)
        write_file(self.cwd, "sub/x.txt", "bbbb\n")
        os.utime(path, ns=(st.st_atime_ns, st.st_mtime_ns))
        self.assertNotEqual(before, tdq_state.repo_status_digest(sub))


class SnapshotTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def test_snapshot_without_log_file(self):
        snap = tdq_state.turn_snapshot(self.cwd)
        self.assertEqual(set(snap), {"log_rel", "log_sha", "repo_sha", "repo_paths"})
        self.assertTrue(snap["log_rel"].startswith(os.path.join("docs", "workinglog")))
        self.assertIsNone(snap["log_sha"])
        self.assertIsNone(snap["repo_sha"])

    def test_snapshot_with_log_file(self):
        snap0 = tdq_state.turn_snapshot(self.cwd)
        path = write_file(self.cwd, snap0["log_rel"], "# log\n")
        snap = tdq_state.turn_snapshot(self.cwd)
        self.assertEqual(snap["log_sha"], tdq_state.sha256_file(path))

    def test_today_log_rel_matches_snapshot(self):
        self.assertEqual(tdq_state.turn_snapshot(self.cwd)["log_rel"],
                         tdq_state.today_log_rel())


if __name__ == "__main__":
    unittest.main()
