"""T4.1 — bậc 3 phải khởi động language server thật, không chỉ thấy binary.

Đo 2026-10-02 trên excalidraw: bậc 3 báo ĐẠT trong khi `agent-lsp doctor` in 2 ok / 2 failed
(typescript@7 toàn cục không có tsserver). Các ca dưới đây đóng đinh: server `failed` → bậc 3
không đạt kèm lỗi; doctor không chạy được → giữ phán quyết binary, không đánh trượt oan.

Mọi ca đều vá `_run` và `shutil.which` — không bao giờ gọi agent-lsp thật.
"""
import os
import sys
import tempfile
import unittest
from unittest import mock

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_lsp  # noqa: E402

MAU_DOCTOR = """agent-lsp doctor
● javascript (C:\npm\typescript-language-server.cmd)
  Status:  failed
  Error:   initialize request: lsp error -32603: Request initialize failed with message: Could not find a valid TypeScript installation. Please ensure that the "typescript" dependency is installed.

● json (C:\npm\vscode-json-language-server.cmd)
  Status:  ok
  Capabilities: hover, completion

● python (C:\npm\pyright-langserver.cmd)
  Status:  ok

● typescript (C:\npm\typescript-language-server.cmd)
  Status:  failed
  Error:   initialize request: lsp error -32603: Could not find a valid TypeScript installation.

Summary: 2 ok, 2 failed
"""

MAU_DOCTOR_OK = MAU_DOCTOR.replace("Status:  failed", "Status:  ok").replace(
    "Summary: 2 ok, 2 failed", "Summary: 4 ok, 0 failed")


class DocDoctor(unittest.TestCase):
    def test_doc_mau_that(self):
        kq = tdq_lsp.doc_doctor(MAU_DOCTOR)
        self.assertEqual(set(kq), {"javascript", "json", "python", "typescript"})
        self.assertEqual(kq["json"], ("ok", ""))
        self.assertEqual(kq["python"][0], "ok")
        self.assertEqual(kq["typescript"][0], "failed")
        self.assertIn("valid TypeScript installation", kq["javascript"][1])

    def test_rac_thi_rong(self):
        self.assertEqual(tdq_lsp.doc_doctor(""), {})
        self.assertEqual(tdq_lsp.doc_doctor(None), {})
        self.assertEqual(tdq_lsp.doc_doctor("quá 90s"), {})


class Bac3KhoiDong(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        for i in range(5):
            with open(os.path.join(self.tmp.name, f"f{i}.ts"), "w", encoding="utf-8") as fh:
                fh.write("x")
        self.goi = []

    def _bac3(self, ket_qua_run, co_agent_lsp=True):
        def which(ten):
            if ten == "agent-lsp" and not co_agent_lsp:
                return None
            return f"/gia/{ten}"

        def run(cmd, cwd=None, timeout=tdq_lsp.CHECK_TIMEOUT):
            self.goi.append((cmd, cwd, timeout))
            return ket_qua_run

        with mock.patch.object(tdq_lsp.shutil, "which", side_effect=which), \
                mock.patch.object(tdq_lsp, "_run", side_effect=run), \
                mock.patch.object(tdq_lsp, "_doc_json", return_value={}):
            return tdq_lsp.bac3_language_server(self.tmp.name)

    def test_hai_failed_thi_khong_dat(self):
        b = self._bac3((1, MAU_DOCTOR))
        self.assertFalse(b.dat)
        self.assertIn("typescript", b.chi_tiet)
        self.assertIn("valid TypeScript installation", b.chi_tiet)
        self.assertIn("typescript-language-server", b.lenh_cai)
        cmd, cwd, timeout = self.goi[0]
        self.assertEqual(cmd[1], "doctor")
        self.assertEqual(cwd, self.tmp.name)
        self.assertEqual(timeout, tdq_lsp.TIMEOUT_DOCTOR)

    def test_tat_ca_ok_thi_dat(self):
        b = self._bac3((0, MAU_DOCTOR_OK))
        self.assertTrue(b.dat)
        self.assertIn("TypeScript", b.chi_tiet)

    def test_ngon_ngu_doctor_khong_bao_thi_xet_binary(self):
        """CSS không có trong output doctor → chỉ xét binary, vẫn đạt."""
        for i in range(5):
            with open(os.path.join(self.tmp.name, f"s{i}.css"), "w", encoding="utf-8") as fh:
                fh.write("x")
        b = self._bac3((0, MAU_DOCTOR_OK))
        self.assertTrue(b.dat)
        self.assertIn("CSS", b.chi_tiet)

    def test_doctor_qua_gio_thi_giu_phan_quyet_binary(self):
        b = self._bac3((1, "quá 90s"))
        self.assertTrue(b.dat)
        self.assertIn("chưa khởi động thử được", b.chi_tiet)
        self.assertIn("quá 90s", b.chi_tiet)

    def test_thieu_agent_lsp_thi_giu_phan_quyet_binary(self):
        b = self._bac3((0, ""), co_agent_lsp=False)
        self.assertTrue(b.dat)
        self.assertIn("chưa khởi động thử được", b.chi_tiet)
        self.assertEqual(self.goi, [])

    def test_thieu_binary_thi_khong_goi_doctor(self):
        with mock.patch.object(tdq_lsp.shutil, "which", return_value=None), \
                mock.patch.object(tdq_lsp, "_run", side_effect=AssertionError("không được gọi")):
            b = tdq_lsp.bac3_language_server(self.tmp.name)
        self.assertFalse(b.dat)
        self.assertIn("typescript-language-server", b.lenh_cai)


if __name__ == "__main__":
    unittest.main()
