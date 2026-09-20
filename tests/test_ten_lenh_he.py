"""Test for the interpreter name per OS, and for the reminder line that covers a machine
without the shim.

Why it matters, measured on the user's Windows 11 box: `python3` there resolves to
`...\\WindowsApps\\python3.exe`, the Microsoft Store stub, which exits 49 instead of running
Python. Every one of the 96 command lines the rule layer prints is unusable until either a shim
sits earlier on PATH or the reader knows to type `py -3`. This module owns both halves of that
answer, and `build_portable` now reads it instead of keeping a second copy.

Every case passes the platform in as an ARGUMENT. Reading `sys.platform` in secret is what made
the original bug untestable from the author's macOS machine.
"""
import os
import sys
import unittest

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))

import tdq_ten_lenh  # noqa: E402
import build_portable  # noqa: E402


STUB = r"C:\Users\ai\AppData\Local\Microsoft\WindowsApps\python3.exe"
THAT = r"C:\Users\ai\AppData\Local\Programs\Python\Python313\Scripts\python3.cmd"


def tim_lenh_gia(ket_qua):
    """A stand-in for shutil.which that answers with whatever the case needs."""
    return lambda _ten: ket_qua


class TenLenhTheoHeTest(unittest.TestCase):
    def test_windows_ra_py_3(self):
        for nen_tang in ("win32", "windows", "win"):
            with self.subTest(nen_tang=nen_tang):
                self.assertEqual(tdq_ten_lenh.ten_lenh_python(nen_tang), "py -3")

    def test_he_khac_ra_python3(self):
        for nen_tang in ("darwin", "linux", "freebsd"):
            with self.subTest(nen_tang=nen_tang):
                self.assertEqual(tdq_ten_lenh.ten_lenh_python(nen_tang), "python3")

    def test_khong_truyen_thi_lay_may_dang_chay(self):
        self.assertEqual(tdq_ten_lenh.ten_lenh_python(),
                         tdq_ten_lenh.ten_lenh_python(sys.platform))

    def test_build_portable_doc_cung_mot_nguon(self):
        """One answer, two callers. A second copy is exactly what drifts."""
        for nen_tang in ("win32", "darwin", "linux"):
            with self.subTest(nen_tang=nen_tang):
                self.assertEqual(build_portable.tien_to_python(nen_tang),
                                 tdq_ten_lenh.ten_lenh_python(nen_tang))


class CoShimTest(unittest.TestCase):
    """"Does the name exist" is the wrong question on Windows — the stub answers to it."""

    def test_stub_microsoft_store_khong_tinh_la_co(self):
        self.assertFalse(tdq_ten_lenh.co_shim_python3(tim_lenh_gia(STUB)))

    def test_duong_that_thi_tinh_la_co(self):
        self.assertTrue(tdq_ten_lenh.co_shim_python3(tim_lenh_gia(THAT)))

    def test_khong_tim_thay_thi_la_khong_co(self):
        self.assertFalse(tdq_ten_lenh.co_shim_python3(tim_lenh_gia(None)))


class CanNhacTest(unittest.TestCase):
    """The safety net: one line, and only where it is true."""

    def test_windows_chua_co_shim_thi_nhac(self):
        line = tdq_ten_lenh.can_nhac_ten_lenh("win32", tim_lenh_gia(STUB))
        self.assertIn("py -3", line)
        self.assertIn("setup --shim", line)

    def test_windows_da_co_shim_thi_im(self):
        self.assertEqual(tdq_ten_lenh.can_nhac_ten_lenh("win32", tim_lenh_gia(THAT)), "")

    def test_he_khac_thi_im_du_khong_co_python3(self):
        """macOS and Linux never see this line, whatever `which` says."""
        for nen_tang in ("darwin", "linux"):
            with self.subTest(nen_tang=nen_tang):
                self.assertEqual(
                    tdq_ten_lenh.can_nhac_ten_lenh(nen_tang, tim_lenh_gia(None)), "")

    def test_dong_nhac_la_mot_dong_duy_nhat(self):
        """It is appended to a capped hook block — two lines would cost the law body space."""
        line = tdq_ten_lenh.can_nhac_ten_lenh("win32", tim_lenh_gia(STUB))
        self.assertEqual(len(line.splitlines()), 1)


if __name__ == "__main__":
    unittest.main()
