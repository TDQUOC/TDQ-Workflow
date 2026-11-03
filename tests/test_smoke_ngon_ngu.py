"""T4.2 — the grep floor smoke must follow the project's real languages, not a hard-coded `*.py`.

Measured 2026-10-02: on excalidraw (TypeScript only) `smoke_grep` reported TRƯỢT "không quét ra
file nào" while `git grep` answered instantly — the floor layer reported a failure that did not
exist. Every case runs in a temp dir; nothing on the real machine is read or written.
"""
import io
import os
import shutil
import sys
import tempfile
import unittest

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_setup  # noqa: E402


class SmokeGrepTheoNgonNgu(unittest.TestCase):

    def setUp(self):
        self.thu_muc = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.thu_muc, True)

    def _ghi(self, duong_tuong_doi, noi_dung):
        duong = os.path.join(self.thu_muc, duong_tuong_doi)
        os.makedirs(os.path.dirname(duong), exist_ok=True)
        with io.open(duong, "w", encoding="utf-8") as fh:
            fh.write(noi_dung)

    def test_project_chi_co_ts_thi_dat(self):
        self._ghi(os.path.join("src", "app.ts"), "export function f() {}\n")
        dat, chi_tiet = tdq_setup.smoke_grep(self.thu_muc)
        self.assertTrue(dat, chi_tiet)
        self.assertIn("app.ts", chi_tiet)

    def test_project_chi_co_py_thi_dat(self):
        self._ghi("a.py", "def f():\n    return 1\n")
        dat, chi_tiet = tdq_setup.smoke_grep(self.thu_muc)
        self.assertTrue(dat, chi_tiet)
        self.assertIn("a.py", chi_tiet)

    def test_project_rong_thi_truot(self):
        dat, _ = tdq_setup.smoke_grep(self.thu_muc)
        self.assertFalse(dat)

    def test_ma_chi_nam_trong_node_modules_thi_truot(self):
        self._ghi(os.path.join("node_modules", "lib", "index.ts"), "export function f() {}\n")
        self._ghi(os.path.join("node_modules", "lib", "x.py"), "def f():\n    pass\n")
        dat, chi_tiet = tdq_setup.smoke_grep(self.thu_muc)
        self.assertFalse(dat, chi_tiet)


if __name__ == "__main__":
    unittest.main()
