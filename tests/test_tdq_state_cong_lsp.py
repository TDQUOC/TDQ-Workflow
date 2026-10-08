"""Cổng LSP của `tdq_state.py init` (0.59.0): request chỉ mở khi mọi module LSP đã ĐẠT qua MCP.

User chọn chặn cứng (1A) kèm lối thoát `--bo-qua-lsp "<lý do>"` có ghi lại. Cổng nằm ở LỆNH,
không ở hook — giống cổng R14 của `approve spec` — nên test đi qua CLI thật trên thư mục tạm.
"""
import os
import shutil
import sys
import tempfile
import unittest

from helper import ROOT, read_state, run_state_cli

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import lsp_module  # noqa: E402

SLUG = "2026-10-08-0900-demo-cong-lsp"


def _ghi(goc, rel, noi_dung=""):
    duong = os.path.join(goc, *rel.split("/"))
    os.makedirs(os.path.dirname(duong), exist_ok=True)
    with open(duong, "w", encoding="utf-8") as fh:
        fh.write(noi_dung)


class CongLspInit(unittest.TestCase):
    def setUp(self):
        self.goc = tempfile.mkdtemp(prefix="tdq-cong-lsp-")
        self.addCleanup(shutil.rmtree, self.goc, True)

    def cay_python(self):
        _ghi(self.goc, "pyproject.toml", "")
        _ghi(self.goc, "lib.py", "def tinh_tong_hop(a, b):\n    return a + b\n")
        _ghi(self.goc, "app.py", "from lib import tinh_tong_hop\nprint(tinh_tong_hop(1, 2))\n")
        _ghi(self.goc, "khac.py", "x = 1\n")

    def test_repo_khong_co_ma_nguon_init_qua(self):
        rc, _out, _err = run_state_cli(self.goc, "init", SLUG, "full")
        self.assertEqual(rc, 0)
        self.assertIsNone((read_state(self.goc) or {})["lsp_bo_qua"])

    def test_module_chua_kiem_thi_init_bi_tu_choi(self):
        self.cay_python()
        rc, out, err = run_state_cli(self.goc, "init", SLUG, "full")
        self.assertNotEqual(rc, 0)
        self.assertIn("python:. → CHUA_KIEM", out + err)
        # The temp project has no `scripts/`: the command is rewritten to the plugin's quoted path.
        self.assertRegex(out + err, r'tdq_lsp\.py"? kich-ban')
        self.assertFalse(os.path.exists(os.path.join(self.goc, "docs", "tdq", "state.json")))

    def test_bo_qua_lsp_cho_qua_va_ghi_ly_do(self):
        self.cay_python()
        rc, _out, _err = run_state_cli(self.goc, "init", SLUG, "full", "--bo-qua-lsp", "máy đang thiếu RAM")
        self.assertEqual(rc, 0)
        bq = (read_state(self.goc) or {})["lsp_bo_qua"]
        self.assertEqual(bq["ly_do"], "máy đang thiếu RAM")
        self.assertIn("python:. → CHUA_KIEM", bq["module"][0])

    def test_bo_qua_lsp_thieu_ly_do_bi_tu_choi(self):
        self.cay_python()
        rc, _out, _err = run_state_cli(self.goc, "init", SLUG, "full", "--bo-qua-lsp")
        self.assertNotEqual(rc, 0)

    def test_module_da_dat_thi_init_qua(self):
        self.cay_python()
        args = lsp_module.doc_mcp_args()
        [(m, _kb)] = lsp_module.lap_kich_ban(self.goc, args=args)
        lsp_module.ghi_ket_qua(self.goc, m["id"], 3, args=args)
        rc, _out, err = run_state_cli(self.goc, "init", SLUG, "full")
        self.assertEqual(rc, 0, err)
        self.assertIsNone((read_state(self.goc) or {})["lsp_bo_qua"])


if __name__ == "__main__":
    unittest.main()
