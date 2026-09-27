"""Test for `tdq_checkportable.py setup --shim` — the two files that make `python3` typeable.

Why the shim exists, measured on the user's Windows 11 box: `python3` resolves to the Microsoft
Store stub (`...\\WindowsApps\\python3.exe`, exit 49), so all 96 command lines the rule layer
prints are dead as written. Two one-line files placed EARLIER on PATH than that stub fix every
one of them without touching a rule file.

Order is the whole invariant. A shim written into a directory that sits AFTER the stub never
runs, and the failure is silent — the user types the command, gets the store, and blames the
workflow. So the picker is tested harder than the writer.
"""
import os
import sys
import unittest

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))

import tdq_checkportable as cp  # noqa: E402


# Fixture phải viết theo hệ ĐANG CHẠY, không theo hệ mà tính năng này phục vụ.
# 2026-09-27: bản cũ dùng đường dẫn Windows cho mọi hệ, và `path_of` nối bằng `os.pathsep` —
# trên POSIX `os.pathsep` là dấu hai chấm, nên `C:\...` bị xé thành `C` và `\...`, làm 9 ca đỏ
# trên Ubuntu/macOS (CI run 35957834415). Sản phẩm KHÔNG sai: `chon_thu_muc_shim` quy cả hai dấu
# chéo về `/` rồi so theo TỪNG THÀNH PHẦN, nên nó đúng ở cả ba hệ. Thứ phải đổi là fixture.
# Ý nghĩa từng đường dẫn giữ nguyên: một chỗ ghi được, một chỗ là stub của Store, một chỗ sống
# theo shell, một chỗ là thư mục tạm của hệ.
if os.name == "nt":
    SCRIPTS = r"C:\Users\ai\AppData\Local\Programs\Python\Python313\Scripts"
    STUB = r"C:\Users\ai\AppData\Local\Microsoft\WindowsApps"
    LOCAL = r"C:\Users\ai\.local\bin"
    KHONG_GHI = r"C:\Windows\system32"
    THEO_SHELL = r"C:\Users\ai\AppData\Local\fnm_multishells\16552_1789904142495"
    THU_MUC_TAM = (r"C:\Windows\Temp", r"C:\Users\ai\AppData\Local\Temp\x")
else:
    SCRIPTS = "/home/ai/.local/python313/Scripts"
    STUB = "/home/ai/.local/microsoft/WindowsApps"
    LOCAL = "/home/ai/.local/bin"
    KHONG_GHI = "/usr/bin"
    THEO_SHELL = "/home/ai/.local/fnm_multishells/16552_1789904142495"
    THU_MUC_TAM = ("/var/tmp", "/home/ai/.cache/temp/x")


def path_of(*muc):
    return os.pathsep.join(muc)


class FixtureTest(unittest.TestCase):
    """Canh đúng cái bẫy vừa sập: fixture không được chứa dấu phân cách PATH của hệ đang chạy.

    Thiếu ca này thì lần sau ai đó lại viết đường dẫn Windows cho mọi hệ, và test chỉ đỏ ở CI —
    nơi đắt nhất để phát hiện.
    """

    def test_fixture_khong_chua_dau_phan_cach_path(self):
        for ten, duong in (("SCRIPTS", SCRIPTS), ("STUB", STUB), ("LOCAL", LOCAL),
                           ("KHONG_GHI", KHONG_GHI), ("THEO_SHELL", THEO_SHELL)):
            with self.subTest(fixture=ten):
                self.assertNotIn(os.pathsep, duong,
                                 f"{ten} chứa {os.pathsep!r} nên sẽ bị split() xé làm hai")
        for duong in THU_MUC_TAM:
            with self.subTest(fixture=duong):
                self.assertNotIn(os.pathsep, duong)

    def test_path_of_giu_dung_so_muc(self):
        self.assertEqual(len(path_of(SCRIPTS, STUB, LOCAL).split(os.pathsep)), 3)


class ChonThuMucTest(unittest.TestCase):
    """The picker: on PATH, writable, and before the stub."""

    def test_lay_thu_muc_ghi_duoc_dau_tien(self):
        duong, ly_do = cp.chon_thu_muc_shim(path_of(SCRIPTS, STUB, LOCAL),
                                            ghi_duoc=lambda d: True)
        self.assertEqual(duong, SCRIPTS)
        self.assertEqual(ly_do, "")

    def test_bo_qua_thu_muc_khong_ghi_duoc(self):
        duong, _ = cp.chon_thu_muc_shim(path_of(KHONG_GHI, SCRIPTS, STUB),
                                        ghi_duoc=lambda d: d == SCRIPTS)
        self.assertEqual(duong, SCRIPTS)

    def test_moi_thu_muc_ghi_duoc_deu_sau_stub_thi_tu_choi(self):
        """The silent-failure case: writable, on PATH, but the stub answers first."""
        duong, ly_do = cp.chon_thu_muc_shim(path_of(STUB, LOCAL), ghi_duoc=lambda d: True)
        self.assertIsNone(duong)
        self.assertIn("after the Microsoft Store stub", ly_do)

    def test_bo_qua_thu_muc_song_theo_shell(self):
        """Measured: fnm prepends a per-shell dir to PATH, and the first version of this code
        put the shim there — litter that dies with the shell and never runs again."""
        duong, _ = cp.chon_thu_muc_shim(path_of(THEO_SHELL, SCRIPTS, STUB),
                                        ghi_duoc=lambda d: True)
        self.assertEqual(duong, SCRIPTS)

    def test_bo_qua_thu_muc_tam_cua_he(self):
        for tam in THU_MUC_TAM:
            with self.subTest(tam=tam):
                duong, _ = cp.chon_thu_muc_shim(path_of(tam, SCRIPTS), ghi_duoc=lambda d: True)
                self.assertEqual(duong, SCRIPTS)

    def test_path_rong_thi_tu_choi_kem_ly_do(self):
        duong, ly_do = cp.chon_thu_muc_shim("", ghi_duoc=lambda d: True)
        self.assertIsNone(duong)
        self.assertIn("no writable directory", ly_do)


class CaiShimTest(unittest.TestCase):
    """The writer: two files, idempotent, and a no-op away from Windows."""

    def setUp(self):
        self.viet = {}

    def _ghi(self, duong, noi_dung):
        self.viet[duong] = noi_dung

    def _cai(self, nen_tang="win32", chuoi_path=None):
        return cp.cai_shim_python3(nen_tang=nen_tang,
                                   chuoi_path=chuoi_path or path_of(SCRIPTS, STUB),
                                   ghi_duoc=lambda d: d == SCRIPTS,
                                   ghi_file=self._ghi)

    def test_ghi_dung_hai_file(self):
        da_lam, _ = self._cai()
        self.assertEqual(len(da_lam), 2)
        self.assertEqual(sorted(os.path.basename(d) for d in self.viet),
                         ["python3", "python3.cmd"])

    def test_ban_cmd_goi_py_3(self):
        self._cai()
        noi_dung = self.viet[os.path.join(SCRIPTS, "python3.cmd")]
        self.assertIn("py -3", noi_dung)
        self.assertIn("%*", noi_dung)

    def test_ban_sh_giu_nguyen_tham_so(self):
        """Git Bash reads the extension-less one; losing the arguments breaks every command."""
        self._cai()
        noi_dung = self.viet[os.path.join(SCRIPTS, "python3")]
        self.assertIn("py -3", noi_dung)
        self.assertIn('"$@"', noi_dung)

    def test_ngoai_windows_thi_khong_ghi_gi(self):
        for nen_tang in ("darwin", "linux"):
            with self.subTest(nen_tang=nen_tang):
                self.viet.clear()
                da_lam, ghi_chu = self._cai(nen_tang=nen_tang)
                self.assertEqual(da_lam, [])
                self.assertEqual(self.viet, {})
                self.assertIn("already runs Python", ghi_chu[0])

    def test_khong_chon_duoc_thu_muc_thi_bao_ly_do_chu_khong_no(self):
        da_lam, ghi_chu = cp.cai_shim_python3(nen_tang="win32",
                                              chuoi_path=path_of(STUB, LOCAL),
                                              ghi_duoc=lambda d: True,
                                              ghi_file=self._ghi)
        self.assertEqual(da_lam, [])
        self.assertEqual(self.viet, {})
        self.assertIn("skipped --shim", ghi_chu[0])


class CliTest(unittest.TestCase):
    """`--shim` must work from a plain repo checkout, where there is no manifest at all."""

    def test_shim_khong_doi_manifest(self):
        """The old `setup` path dies with `no manifest.json found`; --shim must not reach it."""
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ma = cp.main(["setup", "--shim"])
        ra = buf.getvalue()
        self.assertEqual(ma, 0, ra)
        self.assertNotIn("no manifest.json", ra)

    def test_shim_voi_check_thi_tu_choi(self):
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ma = cp.main(["check", "--shim"])
        self.assertEqual(ma, 2)
        self.assertIn("only works with `setup`", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
