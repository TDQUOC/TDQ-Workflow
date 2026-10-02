"""Unit tests for the background bootstrap `tdq_setup.py --nen` (T6.1).

Why it exists: a lumen index of excalidraw took 11m5s, so a SessionStart hook cannot build the
search layers itself. It spawns `tdq_setup.py --nen` detached; this file locks that side: the
readiness stamp, the pid lock that prevents two builders, and the build that never raises.

Nothing real runs here: every command goes through a fake `chay`, and every tool lookup
(codex, graphify, lumen, ollama, the ladder, the smoke) is patched. Each case works in its own
temp project directory.

Selectors: `-k kich_hoat` (a build runs end to end), `-k chong` (no two builders at once).
"""
import io
import json
import os
import shutil
import sys
import tempfile
import time
import unittest
from unittest import mock

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_codex_mcp  # noqa: E402
import tdq_lsp  # noqa: E402
import tdq_no  # noqa: E402
import tdq_setup  # noqa: E402

TANG = ("grep", "lsp", "graphify", "lumen")
# A pid far above any real pid table, so it is never alive on the test machine.
PID_CHET = 2_000_000_000


class ChayGia:
    """Fake command runner: records (argv, cwd) and answers from a table of argv[0]/argv[1]."""

    def __init__(self, project, loi=(), qua_gio=(), moi_lenh=None):
        self.project = project
        self.lenh = []
        self.loi = set(loi)          # tool names whose command fails
        self.qua_gio = set(qua_gio)  # tool names whose command times out (raises)
        self.moi_lenh = moi_lenh     # callback run inside every command

    def __call__(self, argv, cwd=None, timeout=None):
        self.lenh.append((list(argv), cwd))
        if self.moi_lenh:
            self.moi_lenh(argv)
        ten = os.path.basename(str(argv[0]))
        if ten in self.qua_gio:
            import subprocess
            raise subprocess.TimeoutExpired(argv, timeout or 1)
        if ten in self.loi:
            return 1, "hỏng giả"
        return 0, "Done. giả"

    def lenh_cua(self, ten):
        return [(a, c) for a, c in self.lenh if os.path.basename(str(a[0])) == ten]


class CoSo(unittest.TestCase):
    """Temp project + every machine-touching lookup patched to a fake."""

    def setUp(self):
        self.project = tempfile.mkdtemp(prefix="tdq-tu-khoi-tao-")
        self.addCleanup(shutil.rmtree, self.project, ignore_errors=True)
        with open(os.path.join(self.project, "a.py"), "w", encoding="utf-8") as fh:
            fh.write("def a():\n    return 1\n")
        self.codex_goi = []
        vas = [
            mock.patch.dict(os.environ, {"TDQ_LOG": "0"}),
            mock.patch.object(tdq_setup, "_tim_cong_cu",
                              side_effect=lambda ten: f"/gia/{ten}"),
            mock.patch.object(tdq_lsp, "_binary_lumen", return_value="/gia/lumen"),
            mock.patch.object(tdq_lsp, "_ollama_dang_chay", return_value=True),
            mock.patch.object(tdq_lsp, "chay_kiem", return_value=[]),
            mock.patch.object(tdq_lsp, "chay_smoke", return_value=[
                ("grep", True, "g"), ("LSP", True, "l"),
                ("graphify", True, "gr"), ("lumen", True, "lu")]),
            mock.patch.object(tdq_codex_mcp, "khai_mcp_codex",
                              side_effect=lambda *a, **k: self.codex_goi.append(1) or ["lsp: giả"]),
            # T3.1 thêm bước ghi `.codex/hooks.json` vào cùng đường này. Không vá nó thì test ghi
            # THẬT vào `.codex/hooks.json` của repo (đã xảy ra 2026-10-03, có file .bak làm chứng).
            mock.patch.object(tdq_codex_mcp, "khai_hook_codex", return_value=["hook: giả"]),
            mock.patch.object(tdq_no, "ghi_no", return_value=0),
        ]
        for va in vas:
            va.start()
            self.addCleanup(va.stop)

    def duong(self, ten):
        return os.path.join(self.project, "docs", "tdq", ten)

    def dat_khoa(self, pid, tuoi_giay=0):
        os.makedirs(os.path.dirname(self.duong(".tdq-khoi-tao.lock")), exist_ok=True)
        tep = self.duong(".tdq-khoi-tao.lock")
        with open(tep, "w", encoding="utf-8") as fh:
            fh.write(str(pid))
        if tuoi_giay:
            moc = time.time() - tuoi_giay
            os.utime(tep, (moc, moc))
        return tep


class KichHoat(CoSo):
    """A build runs end to end and leaves a readable stamp behind."""

    def test_kich_hoat_ghi_moc_dang_dung_roi_xong(self):
        thay = []

        def trong_lenh(_argv):
            thay.append(tdq_setup.doc_san_sang(self.project))

        chay = ChayGia(self.project, moi_lenh=trong_lenh)
        rc = tdq_setup.khoi_tao_nen(self.project, chay=chay)
        self.assertEqual(rc, 0)
        self.assertTrue(thay, "no command ran at all")
        for moc in thay:
            self.assertIsNotNone(moc)
            self.assertTrue(moc["dang_dung"])
            self.assertEqual(moc["pid"], os.getpid())
        cuoi = tdq_setup.doc_san_sang(self.project)
        self.assertFalse(cuoi["dang_dung"])
        self.assertIsNone(cuoi["pid"])
        self.assertIn("cap_nhat", cuoi)
        self.assertEqual(set(cuoi["tang"]), set(TANG))
        for ten in TANG:
            self.assertTrue(cuoi["tang"][ten]["san_sang"], ten)
            self.assertIsInstance(cuoi["tang"][ten]["chi_tiet"], str)

    def test_kich_hoat_graphify_lumen_chay_o_project(self):
        chay = ChayGia(self.project)
        tdq_setup.khoi_tao_nen(self.project, chay=chay)
        gr = chay.lenh_cua("graphify")
        lu = chay.lenh_cua("lumen")
        self.assertEqual(len(gr), 1)
        self.assertEqual(gr[0][0][1:], ["extract", ".", "--code-only"])
        self.assertEqual(gr[0][1], self.project)
        self.assertEqual(len(lu), 1)
        self.assertEqual(lu[0][0][1:], ["index", self.project])
        self.assertEqual(lu[0][1], self.project)
        self.assertTrue(os.path.isfile(os.path.join(self.project, tdq_lsp.DAU_MOC_INDEX)),
                        "a successful lumen index must touch the index stamp")
        self.assertEqual(self.codex_goi, [1])

    def test_kich_hoat_nha_khoa_sau_khi_xong(self):
        tdq_setup.khoi_tao_nen(self.project, chay=ChayGia(self.project))
        self.assertFalse(os.path.exists(self.duong(".tdq-khoi-tao.lock")))

    def test_kich_hoat_cai_qua_duong_da_khai(self):
        """The install step reuses `cai_thieu`: allowed commands run, others become debt."""
        bac = [tdq_lsp.Bac(8, "graphify", False, "thiếu", "uv tool install graphifyy", True),
               tdq_lsp.Bac(1, "agent-lsp", False, "thiếu", "curl x | sh")]
        chay = ChayGia(self.project)
        with mock.patch.object(tdq_lsp, "chay_kiem", return_value=bac):
            tdq_setup.khoi_tao_nen(self.project, chay=chay)
        self.assertIn(["uv", "tool", "install", "graphifyy"], [a for a, _ in chay.lenh])
        self.assertFalse(any(a[0] == "curl" for a, _ in chay.lenh))

    def test_kich_hoat_bo_qua_cong_cu_vang_mat(self):
        chay = ChayGia(self.project)
        with mock.patch.object(tdq_setup, "_tim_cong_cu", return_value=None), \
                mock.patch.object(tdq_lsp, "_binary_lumen", return_value=""):
            tdq_setup.khoi_tao_nen(self.project, chay=chay)
        self.assertEqual(chay.lenh_cua("graphify"), [])
        self.assertEqual(chay.lenh_cua("lumen"), [])
        self.assertEqual(self.codex_goi, [], "no codex on PATH -> no MCP declaration")

    def test_kich_hoat_lumen_can_ollama(self):
        chay = ChayGia(self.project)
        with mock.patch.object(tdq_lsp, "_ollama_dang_chay", return_value=False):
            tdq_setup.khoi_tao_nen(self.project, chay=chay)
        self.assertEqual(chay.lenh_cua("lumen"), [])


class ChongChayChong(CoSo):
    """Two triggers in a row -> one builder (spec Q16)."""

    def test_chong_khoa_pid_song_thi_ve_ngay(self):
        self.dat_khoa(os.getpid())
        chay = ChayGia(self.project)
        rc = tdq_setup.khoi_tao_nen(self.project, chay=chay)
        self.assertEqual(rc, 0)
        self.assertEqual(chay.lenh, [])
        self.assertEqual(self.codex_goi, [])
        self.assertIsNone(tdq_setup.doc_san_sang(self.project), "must not touch the stamp")
        self.assertTrue(os.path.exists(self.duong(".tdq-khoi-tao.lock")),
                        "someone else's lock must survive")

    def test_chong_khoa_pid_chet_thi_lay_lai(self):
        self.dat_khoa(PID_CHET)
        chay = ChayGia(self.project)
        tdq_setup.khoi_tao_nen(self.project, chay=chay)
        self.assertTrue(chay.lenh, "a stale lock must be taken over")
        self.assertFalse(os.path.exists(self.duong(".tdq-khoi-tao.lock")))

    def test_chong_khoa_qua_tran_thi_lay_lai(self):
        self.dat_khoa(os.getpid(), tuoi_giay=tdq_setup.TRAN_GIAY + 60)
        chay = ChayGia(self.project)
        tdq_setup.khoi_tao_nen(self.project, chay=chay)
        self.assertTrue(chay.lenh, "a lock older than TRAN_GIAY must be taken over")

    def test_chong_khoa_rac_thi_lay_lai(self):
        tep = self.dat_khoa("không phải số")
        self.assertTrue(tdq_setup.giu_khoa(self.project))
        with open(tep, encoding="utf-8") as fh:
            self.assertEqual(fh.read().strip(), str(os.getpid()))
        tdq_setup.nha_khoa(self.project)
        self.assertFalse(os.path.exists(tep))

    def test_chong_giu_khoa_lan_hai_that_bai(self):
        self.assertTrue(tdq_setup.giu_khoa(self.project))
        self.assertFalse(tdq_setup.giu_khoa(self.project))
        tdq_setup.nha_khoa(self.project)
        self.assertTrue(tdq_setup.giu_khoa(self.project))
        tdq_setup.nha_khoa(self.project)

    def test_chong_pid_song_khong_nem(self):
        self.assertTrue(tdq_setup._pid_con_song(os.getpid()))
        self.assertFalse(tdq_setup._pid_con_song(PID_CHET))
        self.assertFalse(tdq_setup._pid_con_song(0))


class KhongNem(CoSo):
    """One failing step never stops the others, and nothing escapes."""

    def test_lenh_hong_khong_chan_lenh_khac(self):
        chay = ChayGia(self.project, loi={"graphify"})
        rc = tdq_setup.khoi_tao_nen(self.project, chay=chay)
        self.assertEqual(rc, 0)
        self.assertEqual(len(chay.lenh_cua("lumen")), 1, "lumen must still run")
        self.assertFalse(tdq_setup.doc_san_sang(self.project)["dang_dung"])
        self.assertFalse(os.path.exists(self.duong(".tdq-khoi-tao.lock")))

    def test_lenh_qua_gio_khong_nem(self):
        chay = ChayGia(self.project, qua_gio={"graphify", "lumen"})
        rc = tdq_setup.khoi_tao_nen(self.project, chay=chay)
        self.assertEqual(rc, 0)
        self.assertFalse(os.path.isfile(os.path.join(self.project, tdq_lsp.DAU_MOC_INDEX)),
                         "a failed index must not claim to be fresh")
        self.assertFalse(tdq_setup.doc_san_sang(self.project)["dang_dung"])

    def test_smoke_va_codex_nem_van_xong(self):
        with mock.patch.object(tdq_lsp, "chay_smoke", side_effect=RuntimeError("smoke vỡ")), \
                mock.patch.object(tdq_codex_mcp, "khai_mcp_codex", side_effect=OSError("vỡ")), \
                mock.patch.object(tdq_lsp, "chay_kiem", side_effect=RuntimeError("thang vỡ")):
            rc = tdq_setup.khoi_tao_nen(self.project, chay=ChayGia(self.project))
        self.assertEqual(rc, 0)
        moc = tdq_setup.doc_san_sang(self.project)
        self.assertFalse(moc["dang_dung"])
        self.assertEqual(set(moc["tang"]), set(TANG))
        self.assertFalse(os.path.exists(self.duong(".tdq-khoi-tao.lock")))

    def test_het_tran_bo_qua_buoc_con_lai(self):
        chay = ChayGia(self.project)
        with mock.patch.object(tdq_setup, "TRAN_GIAY", 0):
            rc = tdq_setup.khoi_tao_nen(self.project, chay=chay)
        self.assertEqual(rc, 0)
        self.assertEqual(chay.lenh_cua("lumen"), [])
        self.assertFalse(tdq_setup.doc_san_sang(self.project)["dang_dung"])


class MocSanSang(CoSo):
    """The stamp T6.2 and the search gate read."""

    def test_doc_moc_vang_mat_la_none(self):
        self.assertIsNone(tdq_setup.doc_san_sang(self.project))

    def test_doc_moc_hong_la_none(self):
        os.makedirs(os.path.dirname(self.duong(".tdq-san-sang.json")), exist_ok=True)
        with open(self.duong(".tdq-san-sang.json"), "w", encoding="utf-8") as fh:
            fh.write("{không phải json")
        self.assertIsNone(tdq_setup.doc_san_sang(self.project))

    def test_ghi_roi_doc_lai(self):
        du_lieu = {"cap_nhat": "x", "dang_dung": False, "pid": None,
                   "tang": {t: {"san_sang": True, "chi_tiet": ""} for t in TANG}}
        tdq_setup.ghi_san_sang(self.project, du_lieu)
        self.assertEqual(tdq_setup.doc_san_sang(self.project), du_lieu)
        con_lai = os.listdir(os.path.dirname(self.duong(".tdq-san-sang.json")))
        self.assertEqual(con_lai, [".tdq-san-sang.json"], "no temp file may be left behind")


class LuongSetupThuong(CoSo):
    """The normal setup flow also declares lumen + LSP for Codex."""

    def _va_main(self):
        return [mock.patch.object(tdq_setup, "va_hook_xung_dot", return_value=([], [])),
                mock.patch.object(tdq_setup, "kiem_cau_hinh_lumen", return_value=[]),
                mock.patch.object(tdq_setup, "no_skill_khong_ton_tai", return_value=[]),
                mock.patch.object(tdq_setup, "ghim_huong_dan_tool", return_value=False),
                mock.patch.object(tdq_lsp, "kiem_mot_lenh", return_value=(0, [], [])),
                mock.patch("sys.stdout", new_callable=io.StringIO)]

    def test_setup_thuong_goi_khai_mcp_codex(self):
        vas = self._va_main()
        for va in vas:
            va.start()
        try:
            rc = tdq_setup.chay_cli(["--khong-log"])
            ra = sys.stdout.getvalue()
        finally:
            for va in reversed(vas):
                va.stop()
        self.assertEqual(rc, 0)
        self.assertEqual(self.codex_goi, [1])
        self.assertIn("lsp: giả", ra)

    def test_cli_nen_chay_khoi_tao_nen(self):
        with mock.patch.object(tdq_setup, "khoi_tao_nen", return_value=0) as nen, \
                mock.patch.dict(os.environ, {"TDQ_PROJECT_DIR": self.project}):
            rc = tdq_setup.chay_cli(["--nen"])
        self.assertEqual(rc, 0)
        nen.assert_called_once_with(self.project)
        self.assertEqual(self.codex_goi, [], "--nen must not run the normal flow too")


class SessionStartKichHoat(unittest.TestCase):
    """T6.2 — `SessionStart` chỉ DÒ mốc rồi bật dựng nền tách rời; nó không bao giờ tự chờ.

    Lệnh nền thật (`tdq_setup.py --nen`) được thay bằng `TDQ_LENH_NEN`: một python ghi đúng một
    file dấu. Nhờ đó ca này đo được "có bật hay không" bằng hiệu ứng mà không cài/index gì thật.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cwd = self.tmp.name
        os.makedirs(os.path.join(self.cwd, "docs", "tdq"), exist_ok=True)
        self.dau = os.path.join(self.cwd, "da-chay.txt")

    def env(self, bat=True):
        lenh = [sys.executable, "-c",
                f"open(r'{self.dau}', 'a', encoding='utf-8').write('x')"]
        return {"TDQ_PROJECT_DIR": self.cwd, "TDQ_LOG": "0",
                "TDQ_KHOI_TAO_NEN": "1" if bat else "0", "TDQ_LENH_NEN": json.dumps(lenh)}

    def goi(self, bat=True):
        from helper import run_hook
        t0 = time.time()
        rc, out, err = run_hook("session_start.py",
                                {"session_id": "thu-nen", "cwd": self.cwd,
                                 "hook_event_name": "SessionStart"}, env=self.env(bat))
        self.assertEqual(rc, 0, err)
        return out, time.time() - t0

    def cho_dau(self, giay=10):
        het = time.time() + giay
        while time.time() < het:
            if os.path.isfile(self.dau):
                return True
            time.sleep(0.2)
        return False

    def ghi_moc(self, dang_dung=False, tuoi_giay=0, het_san_sang=True):
        from datetime import datetime, timedelta
        moc = {"cap_nhat": (datetime.now() - timedelta(seconds=tuoi_giay)).strftime(
                   "%Y-%m-%dT%H:%M:%S"),
               "dang_dung": dang_dung, "pid": None,
               "tang": {t: {"san_sang": het_san_sang, "chi_tiet": ""}
                        for t in ("grep", "lsp", "graphify", "lumen")}}
        with io.open(os.path.join(self.cwd, "docs", "tdq", ".tdq-san-sang.json"), "w",
                     encoding="utf-8") as fh:
            json.dump(moc, fh)

    def test_kich_hoat_project_chua_dung_thi_bat_nen_va_tra_ve_ngay(self):
        out, giay = self.goi()
        self.assertIn("[TDQ:SEARCH]", out)
        self.assertTrue(self.cho_dau(), "tiến trình nền phải thật sự chạy")
        self.assertLess(giay, 15, "hook không được chờ tiến trình nền")

    def test_kich_hoat_da_san_sang_thi_khong_bat(self):
        self.ghi_moc(het_san_sang=True)
        out, _ = self.goi()
        self.assertNotIn("[TDQ:SEARCH]", out)
        self.assertFalse(self.cho_dau(1.5))

    def test_kich_hoat_tat_bang_bien_moi_truong(self):
        out, _ = self.goi(bat=False)
        self.assertNotIn("[TDQ:SEARCH]", out)
        self.assertFalse(self.cho_dau(1.5))

    def test_kich_hoat_tang_hong_chi_thu_lai_sau_6_gio(self):
        """Không có ollama thì lumen hỏng mãi — bật lại mỗi phiên là chạy lại cùng một lỗi."""
        self.ghi_moc(het_san_sang=False, tuoi_giay=60)
        self.goi()
        self.assertFalse(self.cho_dau(1.5), "mốc còn mới → chưa được thử lại")
        self.ghi_moc(het_san_sang=False, tuoi_giay=7 * 3600)
        self.goi()
        self.assertTrue(self.cho_dau(), "quá 6 giờ → thử lại")

    def test_chong_dang_dung_thi_khong_bat_them(self):
        self.ghi_moc(dang_dung=True, het_san_sang=False)
        self.goi()
        self.assertFalse(self.cho_dau(1.5))

    def test_chong_dang_dung_nhung_da_chet_thi_bat_lai(self):
        self.ghi_moc(dang_dung=True, het_san_sang=False, tuoi_giay=3 * 3600)
        self.goi()
        self.assertTrue(self.cho_dau())

    def test_chong_hai_phien_mo_lien_nhau_chi_bat_mot_lan(self):
        self.goi()
        self.assertTrue(self.cho_dau())
        os.remove(self.dau)
        out, _ = self.goi()                    # phiên thứ hai, mốc vẫn chưa có
        self.assertNotIn("[TDQ:SEARCH]", out)
        self.assertFalse(self.cho_dau(1.5), "dấu `da-goi` còn mới → không bật lần hai")


if __name__ == "__main__":
    unittest.main()
