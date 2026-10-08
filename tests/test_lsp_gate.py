"""Hook chặn `[TDQ:LSP]` — `hooks/scripts/lsp_gate.py` (request 2026-10-07-2225, T4.1).

Ca gốc: `start_lsp` không `language_id` trên repo Python → agent-lsp bật hết server, TypeScript
thành server hiện hành → crash `0xc0000409` / "No Project". User chọn chặn (4A).
"""
import json
import os
import shutil
import sys
import tempfile
import time
import unittest

from helper import ROOT, run_hook

sys.path.insert(0, os.path.join(ROOT, "hooks", "scripts"))
import _common  # noqa: E402

HOOK = "lsp_gate.py"


class LspGate(unittest.TestCase):
    def setUp(self):
        self.cwd = tempfile.mkdtemp(prefix="tdq-lsp-gate-")
        self.addCleanup(shutil.rmtree, self.cwd, True)
        os.makedirs(os.path.join(self.cwd, "docs", "tdq"))
        with open(os.path.join(self.cwd, "docs", "tdq", ".tdq-lsp-module.json"), "w", encoding="utf-8") as fh:
            json.dump({"module": {"python:.": {"lang": "python", "goc": "."},
                                  "javascript:web": {"lang": "javascript", "goc": "web"}}}, fh)

    def goi(self, tool_input):
        payload = {"tool_name": "mcp__lsp__start_lsp", "tool_input": tool_input, "cwd": self.cwd,
                   "session_id": "phien-lsp-gate"}
        rc, out, _err = run_hook(HOOK, payload, env={"TDQ_LOG": "0", "TDQ_PROJECT_DIR": self.cwd})
        self.assertEqual(rc, 0)
        return json.loads(out)["hookSpecificOutput"] if out else None

    def test_deny_khi_thieu_language_id(self):
        ra = self.goi({"root_dir": self.cwd}) or {}
        self.assertEqual(ra["permissionDecision"], "deny")
        self.assertIn("[TDQ:LSP]", ra["permissionDecisionReason"])
        self.assertIn('"language_id": "python"', ra["permissionDecisionReason"])

    def test_deny_khi_cap_goc_ngon_ngu_khong_co_trong_bang(self):
        ra = self.goi({"root_dir": self.cwd, "language_id": "html"}) or {}
        self.assertEqual(ra["permissionDecision"], "deny")
        ra = self.goi({"root_dir": os.path.join(self.cwd, "web"), "language_id": "python"}) or {}
        self.assertEqual(ra["permissionDecision"], "deny")

    def test_allow_khi_dung_cap_va_ho_ts_dung_chung(self):
        self.assertIsNone(self.goi({"root_dir": self.cwd, "language_id": "python"}))
        self.assertIsNone(self.goi({"root_dir": os.path.join(self.cwd, "web"), "language_id": "typescript"}))

    def test_allow_khi_goc_ngoai_project_hoac_chua_co_bang(self):
        ngoai = tempfile.mkdtemp(prefix="tdq-ngoai-")
        self.addCleanup(shutil.rmtree, ngoai, True)
        self.assertIsNone(self.goi({"root_dir": ngoai, "language_id": "go"}))
        os.remove(os.path.join(self.cwd, "docs", "tdq", ".tdq-lsp-module.json"))
        self.assertIsNone(self.goi({"root_dir": self.cwd, "language_id": "go"}))

    def test_payload_hong_hoac_rong_khong_bao_gio_chan(self):
        rc, out, _err = run_hook(HOOK, {"tool_name": "mcp__lsp__start_lsp", "cwd": self.cwd},
                                 env={"TDQ_LOG": "0"})
        self.assertEqual((rc, out), (0, ""))
        import subprocess
        p = subprocess.run([sys.executable, os.path.join(ROOT, "hooks", "scripts", HOOK)],
                           input="{không phải json", capture_output=True, text=True, encoding="utf-8",
                           env={**os.environ, "TDQ_LOG": "0"})
        self.assertEqual((p.returncode, p.stdout.strip()), (0, ""))

    def test_ma_lsp_nam_trong_danh_sach_dong(self):
        self.assertIn("TDQ:LSP", _common.CODES)

    def test_thoi_gian_chay_duoi_200ms(self):
        payload = {"tool_name": "mcp__lsp__start_lsp", "cwd": self.cwd,
                   "tool_input": {"root_dir": self.cwd, "language_id": "python"}}
        do = []
        for _ in range(5):
            bat_dau = time.perf_counter()
            run_hook(HOOK, payload, env={"TDQ_LOG": "0"})
            do.append(time.perf_counter() - bat_dau)
        self.assertLess(min(do), 0.2, f"thời gian chạy: {do}")


if __name__ == "__main__":
    unittest.main()
