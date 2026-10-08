"""One check command: `tdq_lsp.py check` runs the 7 rungs AND the 3-layer smoke test.

Observed 2026-10-02: an agent ran only `tdq_lsp.py check`, read "8/8 bậc ĐẠT" (8 rungs back then) and skipped the
smoke test that lived only in `tdq_setup.py` — while two layers could not answer. Two
commands made "check only the ladder" possible; these cases lock in the single total line that
is ĐẠT only when both halves pass, and that `tdq_setup.py` reuses the same function.

Every rung and every smoke layer is patched: no case touches the real machine.
"""
import io
import os
import sys
import tempfile
import unittest
from unittest import mock

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_lsp  # noqa: E402
import tdq_no  # noqa: E402
import tdq_setup  # noqa: E402

TEN_BAC = ["bac1_binary", "bac2_mcp", "bac3_language_server", "bac4_quyen_tool",
           "bac5_hook_xung_dot", "bac6_cau_hinh_goc_import", "bac7_graphify", "bac8_module"]


class Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


class MotLenhKiem(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        p = mock.patch.dict(os.environ, {"TDQ_PROJECT_DIR": self.tmp.name, "TDQ_LOG": "0"})
        p.start()
        self.addCleanup(p.stop)

    def va_gia(self, bac_hong=(), tang_hong=()):
        """Patch the 8 rungs and the 3 smoke layers; numbers in `bac_hong` / names in `tang_hong` fail."""
        vas = []
        for i, ten in enumerate(TEN_BAC, start=1):
            bac = tdq_lsp.Bac(i, ten, i not in bac_hong, "giả", "lệnh giả" if i in bac_hong else "")
            vas.append(mock.patch.object(tdq_lsp, ten, return_value=bac))
        for ten, ham in (("grep", "smoke_grep"), ("LSP", "smoke_lsp"), ("graphify", "smoke_graphify")):
            vas.append(mock.patch.object(tdq_setup, ham, return_value=(ten not in tang_hong, "giả")))
        for v in vas:
            v.start()
            self.addCleanup(v.stop)

    def chay_check(self):
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            rc = tdq_lsp.cmd_kiem(Args())
        return rc, out.getvalue()

    @staticmethod
    def dong_tong(ra):
        dong = [d for d in ra.splitlines() if d.startswith("Tổng:")]
        assert len(dong) == 1, f"phải có đúng MỘT dòng tổng, thấy {dong!r}"
        return dong[0]

    def test_tat_ca_dat_thi_tong_dat_va_ma_0(self):
        self.va_gia()
        rc, ra = self.chay_check()
        self.assertEqual(rc, tdq_lsp.EXIT_OK)
        self.assertIn("Smoke test ba tầng:", ra)
        self.assertEqual(ra.count("Bậc "), 8)
        tong = self.dong_tong(ra)
        self.assertIn("ĐẠT", tong)
        self.assertNotIn("CHƯA", tong)

    def test_mot_tang_smoke_truot_thi_tong_khong_dat(self):
        self.va_gia(tang_hong=("graphify",))
        rc, ra = self.chay_check()
        self.assertNotEqual(rc, tdq_lsp.EXIT_OK)
        tong = self.dong_tong(ra)
        self.assertIn("CHƯA ĐẠT", tong)
        self.assertIn("graphify", tong)

    def test_mot_bac_thieu_thi_tong_khong_dat(self):
        self.va_gia(bac_hong=(3,))
        rc, ra = self.chay_check()
        self.assertNotEqual(rc, tdq_lsp.EXIT_OK)
        self.assertIn("Smoke test ba tầng:", ra, "bậc thiếu vẫn phải chạy smoke")
        self.assertIn("CHƯA ĐẠT", self.dong_tong(ra))

    def test_setup_dung_lai_dung_ham_chung(self):
        with mock.patch.object(tdq_lsp, "chay_kiem", return_value=[]), \
                mock.patch.object(tdq_setup, "va_hook_xung_dot", return_value=([], [])), \
                mock.patch.object(tdq_setup, "no_skill_khong_ton_tai", return_value=[]), \
                mock.patch.object(tdq_setup, "ghim_huong_dan_tool", return_value=False), \
                mock.patch.object(tdq_setup, "smoke_ba_tang") as smoke_rieng, \
                mock.patch.object(tdq_lsp, "kiem_mot_lenh",
                                  return_value=(tdq_lsp.EXIT_OK, [], [("graphify", False, "hỏng")])) as chung, \
                mock.patch.object(tdq_no, "ghi_no", return_value=0) as ghi_no, \
                mock.patch("sys.stdout", new_callable=io.StringIO):
            tdq_setup.main(["--khong-log"])
        self.assertEqual(chung.call_count, 1)
        smoke_rieng.assert_not_called()
        no = ghi_no.call_args[0][0]
        self.assertTrue(any("graphify" in d for d in no), "tầng trượt vẫn phải thành nợ")


if __name__ == "__main__":
    unittest.main()
