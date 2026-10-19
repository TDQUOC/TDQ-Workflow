"""Test ẩn cửa sổ Console Command Prompt trên Windows khi chạy subprocess.

Đảm bảo:
1. Helper `tham_so_subprocess_an_cua_so` trả về cờ `CREATE_NO_WINDOW` (0x08000000) trên Windows và rỗng trên POSIX.
2. `chay_subprocess` tự động tiêm cờ `CREATE_NO_WINDOW` khi chạy trên Windows.
3. `tdq_finish._run` áp dụng cờ ẩn cửa sổ trên Windows.
4. `tdq_lsp._run` áp dụng cờ ẩn cửa sổ trên Windows.
5. `tdq_setup.kiem_dryrun_hook` và `kiem_va_cai_shim_python3` gọi subprocess kèm cờ ẩn cửa sổ.
6. `setup_status._kiem_tra_binary` gọi subprocess có cờ ẩn cửa sổ.
7. `stop_batch_checker` gọi batch checks kèm cờ ẩn cửa sổ trên Windows.
"""
import os
import subprocess
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "hooks", "scripts"))

import tdq_ten_lenh as tl  # noqa: E402
import tdq_finish  # noqa: E402
import tdq_lsp  # noqa: E402
import tdq_setup  # noqa: E402
import setup_status  # noqa: E402
import stop_batch_checker  # noqa: E402


class HelperAnCuaSoTest(unittest.TestCase):
    """Kiểm tra logic helper tham_so_subprocess_an_cua_so trong tdq_ten_lenh."""

    def test_windows_tra_ve_creationflags_create_no_window(self):
        tham_so = tl.tham_so_subprocess_an_cua_so(nen_tang="win32")
        self.assertIn("creationflags", tham_so)
        cflag_mong_doi = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
        self.assertEqual(tham_so["creationflags"], cflag_mong_doi)

    def test_posix_tra_ve_dict_rong(self):
        for he in ("linux", "darwin", "openbsd"):
            with self.subTest(he=he):
                tham_so = tl.tham_so_subprocess_an_cua_so(nen_tang=he)
                self.assertEqual(tham_so, {})

    @patch("subprocess.run")
    def test_chay_subprocess_tu_dong_them_creationflags_tren_windows(self, mock_run):
        mock_p = MagicMock()
        mock_p.returncode = 0
        mock_run.return_value = mock_p

        with patch("tdq_ten_lenh.la_windows", return_value=True):
            tl.chay_subprocess(["git", "status"], nen_tang="win32")
            self.assertTrue(mock_run.called)
            _, kwargs = mock_run.call_args
            self.assertIn("creationflags", kwargs)
            self.assertEqual(kwargs["creationflags"], 0x08000000)

    @patch("subprocess.run")
    def test_chay_subprocess_khong_them_creationflags_tren_posix(self, mock_run):
        mock_p = MagicMock()
        mock_p.returncode = 0
        mock_run.return_value = mock_p

        with patch("tdq_ten_lenh.la_windows", return_value=False):
            tl.chay_subprocess(["git", "status"], nen_tang="linux")
            self.assertTrue(mock_run.called)
            _, kwargs = mock_run.call_args
            self.assertNotIn("creationflags", kwargs)


class SubprocessRunWrappersTest(unittest.TestCase):
    """Kiểm tra các hàm wrapper subprocess trong tdq_finish, tdq_lsp, tdq_setup, setup_status."""

    @patch("subprocess.run")
    def test_tdq_finish_run_co_an_cua_so_tren_windows(self, mock_run):
        mock_p = MagicMock()
        mock_p.returncode = 0
        mock_p.stdout = "ok"
        mock_p.stderr = ""
        mock_run.return_value = mock_p

        with patch("tdq_ten_lenh.la_windows", return_value=True):
            tdq_finish._run(["graphify", "extract"], cwd=ROOT)
            self.assertTrue(mock_run.called)
            _, kwargs = mock_run.call_args
            self.assertIn("creationflags", kwargs)
            self.assertEqual(kwargs["creationflags"], 0x08000000)

    @patch("subprocess.run")
    def test_tdq_lsp_run_co_an_cua_so_tren_windows(self, mock_run):
        mock_p = MagicMock()
        mock_p.returncode = 0
        mock_p.stdout = "ok"
        mock_p.stderr = ""
        mock_run.return_value = mock_p

        with patch("tdq_ten_lenh.la_windows", return_value=True):
            tdq_lsp._run(["graphify", "god-nodes"], cwd=ROOT)
            self.assertTrue(mock_run.called)
            _, kwargs = mock_run.call_args
            self.assertIn("creationflags", kwargs)
            self.assertEqual(kwargs["creationflags"], 0x08000000)

    @patch("subprocess.run")
    def test_tdq_setup_kiem_dryrun_hook_co_an_cua_so_tren_windows(self, mock_run):
        mock_p = MagicMock()
        mock_p.returncode = 0
        mock_p.stdout = b"usage: prompt_context.py"
        mock_p.stderr = b""
        mock_run.return_value = mock_p

        with patch("tdq_ten_lenh.la_windows", return_value=True):
            dat, chi_tiet = tdq_setup.kiem_dryrun_hook(ROOT)
            self.assertTrue(dat)
            self.assertTrue(mock_run.called)
            _, kwargs = mock_run.call_args
            self.assertIn("creationflags", kwargs)
            self.assertEqual(kwargs["creationflags"], 0x08000000)

    @patch("subprocess.run")
    def test_setup_status_kiem_tra_binary_co_an_cua_so_tren_windows(self, mock_run):
        mock_p = MagicMock()
        mock_p.returncode = 0
        mock_p.stdout = "graphify 0.5.0"
        mock_p.stderr = ""
        mock_run.return_value = mock_p

        with patch("tdq_ten_lenh.la_windows", return_value=True), \
             patch("shutil.which", return_value="C:\\dummy\\graphify.exe"):
            kq = setup_status._run_tool("graphify", ["--version"], "hint")
            self.assertTrue(kq["chay_duoc"])
            self.assertTrue(mock_run.called)
            _, kwargs = mock_run.call_args
            self.assertIn("creationflags", kwargs)
            self.assertEqual(kwargs["creationflags"], 0x08000000)

    @patch("subprocess.run")
    def test_stop_batch_checker_co_an_cua_so_tren_windows(self, mock_run):
        mock_p = MagicMock()
        mock_p.returncode = 0
        mock_p.stdout = ""
        mock_p.stderr = ""
        mock_run.return_value = mock_p

        from pathlib import Path
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            buf = Path(td) / "buf.txt"
            sample_file = Path(td) / "test.py"
            sample_file.write_text("print('hello')", encoding="utf-8")
            buf.write_text(str(sample_file) + "\n", encoding="utf-8")

            with patch("sys.platform", "win32"):
                stop_batch_checker.run_batch_checks(buf)
                self.assertTrue(mock_run.called)
                _, kwargs = mock_run.call_args
                self.assertIn("creationflags", kwargs)
                self.assertEqual(kwargs["creationflags"], 0x08000000)


if __name__ == "__main__":
    unittest.main()
