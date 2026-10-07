"""T3.2 — declare the lsp MCP server for Codex without touching existing entries (lumen left in 0.58.0).

Never calls the real `codex` and never touches the real ~/.codex: every test uses a temp
CODEX_HOME, a temp claude.json and a fake command runner that writes what the real CLI would.
"""
import glob
import json
import os
import shutil
import sys
import tempfile
import tomllib
import unittest
from unittest import mock

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_codex_mcp  # noqa: E402

KHOI_CO_SAN = (
    '[mcp_servers.cloudcli-browser]\n'
    'command = "node"\n'
    'args = ["C:/x/browser.js", "--port", "9222"]\n'
)
LSP_ARGS = ["typescript:C:/t/tsserver.cmd,--stdio", "python:C:/p/pyright-langserver.cmd,--stdio"]


def _toml_str(s):
    return json.dumps(s, ensure_ascii=False)


class GiaCodex:
    """Fake runner: `codex mcp add NAME -- CMD ARGS...` appends the table the CLI would write."""

    def __init__(self):
        self.goi = []

    def __call__(self, argv, env=None):
        self.goi.append(list(argv))
        assert env and env.get("CODEX_HOME"), "CODEX_HOME must be set for the temp home"
        if argv[1:3] == ["mcp", "add"]:
            ten = argv[3]
            tach = argv.index("--")
            lenh, args = argv[tach + 1], argv[tach + 2:]
            with open(os.path.join(env["CODEX_HOME"], "config.toml"), "a", encoding="utf-8") as f:
                f.write(f"\n[mcp_servers.{ten}]\ncommand = {_toml_str(lenh)}\n"
                        f"args = [{', '.join(_toml_str(a) for a in args)}]\n")
        return 0, "", ""

    def so_lan_add(self):
        return sum(1 for g in self.goi if g[1:3] == ["mcp", "add"])


class TestKhaiMcpCodex(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.home = os.path.join(self.tmp, "codex")
        os.makedirs(self.home)
        self.cfg = os.path.join(self.home, "config.toml")
        with open(self.cfg, "w", encoding="utf-8", newline="") as f:
            f.write(KHOI_CO_SAN)
        self.claude_json = os.path.join(self.tmp, "claude.json")
        with open(self.claude_json, "w", encoding="utf-8") as f:
            json.dump({"mcpServers": {"lsp": {"type": "stdio", "command": "C:/a/agent-lsp.exe",
                                              "args": LSP_ARGS}}}, f)
        p1 = mock.patch.object(tdq_codex_mcp, "_tim_codex", return_value="C:/fake/codex.exe")
        p3 = mock.patch.dict(os.environ, {"TDQ_LOG": "0"})
        for p in (p1, p3):
            p.start()
        self.addCleanup(mock.patch.stopall)

    def _chay(self, gia):
        return tdq_codex_mcp.khai_mcp_codex(codex_home=self.home, claude_json=self.claude_json,
                                            chay=gia)

    def _doc(self):
        with open(self.cfg, "rb") as f:
            return tomllib.load(f)

    def _bak(self):
        return glob.glob(self.cfg + ".truoc-tdq-*.bak")

    def test_them_lsp_giu_nguyen_muc_san_co(self):
        gia = GiaCodex()
        dong = self._chay(gia)
        cfg = self._doc()["mcp_servers"]
        self.assertIn("lsp", cfg)
        self.assertNotIn("lumen", cfg, "0.58.0: không còn khai lumen cho Codex")
        with open(self.cfg, encoding="utf-8", newline="") as f:
            self.assertTrue(f.read().startswith(KHOI_CO_SAN))
        baks = self._bak()
        self.assertEqual(len(baks), 1)
        with open(baks[0], encoding="utf-8", newline="") as f:
            self.assertEqual(f.read(), KHOI_CO_SAN)
        self.assertEqual(gia.so_lan_add(), 1)
        self.assertTrue(dong)

    def test_lsp_args_chep_nguyen_van(self):
        self._chay(GiaCodex())
        lsp = self._doc()["mcp_servers"]["lsp"]
        self.assertEqual(lsp["command"], "C:/a/agent-lsp.exe")
        self.assertEqual(lsp["args"], LSP_ARGS)

    def test_chay_hai_lan_mot_ket_qua(self):
        self._chay(GiaCodex())
        with open(self.cfg, "rb") as f:
            lan1 = f.read()
        gia2 = GiaCodex()
        dong = self._chay(gia2)
        with open(self.cfg, "rb") as f:
            self.assertEqual(f.read(), lan1)
        self.assertEqual(gia2.so_lan_add(), 0)
        self.assertEqual(len(self._bak()), 1)
        self.assertTrue(any("already present, left unchanged" in d for d in dong))

    def test_ten_da_co_thi_khong_add(self):
        with open(self.cfg, "a", encoding="utf-8") as f:
            f.write('\n[mcp_servers.lsp]\ncommand = "khac"\nargs = []\n')
        gia = GiaCodex()
        self._chay(gia)
        ten_add = [g[3] for g in gia.goi if g[1:3] == ["mcp", "add"]]
        self.assertEqual(ten_add, [])
        self.assertEqual(self._doc()["mcp_servers"]["lsp"]["command"], "khac")

    def test_khong_co_codex_thi_khong_ghi(self):
        with open(self.cfg, "rb") as f:
            truoc = f.read()
        gia = GiaCodex()
        with mock.patch.object(tdq_codex_mcp, "_tim_codex", return_value=None):
            dong = self._chay(gia)
        self.assertEqual(gia.goi, [])
        with open(self.cfg, "rb") as f:
            self.assertEqual(f.read(), truoc)
        self.assertEqual(self._bak(), [])
        self.assertTrue(any("Codex" in d for d in dong))

    def test_thieu_nguon_thi_bo_qua_khong_raise(self):
        os.remove(self.claude_json)
        gia = GiaCodex()
        dong = self._chay(gia)
        self.assertEqual(gia.so_lan_add(), 0)
        self.assertEqual(self._bak(), [])
        self.assertEqual(len(dong), 1)

    def test_khong_co_config_thi_khong_backup(self):
        os.remove(self.cfg)
        self._chay(GiaCodex())
        self.assertEqual(self._bak(), [])
        self.assertIn("lsp", self._doc()["mcp_servers"])

    def test_config_hong_thi_doc_ten_qua_mcp_list(self):
        with open(self.cfg, "a", encoding="utf-8") as f:
            f.write("\nthis is = = not toml\n")
        gia = GiaCodex()
        bang = ("Name              Command  Args  Env  Cwd  Status   Auth\n"
                "cloudcli-browser  node     x     -    -    enabled  Unsupported\n"
                "lsp               l        x     -    -    enabled  Unsupported\n")

        def chay(argv, env=None):
            if argv[1:3] == ["mcp", "list"]:
                gia.goi.append(list(argv))
                return 0, bang, ""
            return gia(argv, env)

        tdq_codex_mcp.khai_mcp_codex(codex_home=self.home, claude_json=self.claude_json,
                                     chay=chay)
        ten_add = [g[3] for g in gia.goi if g[1:3] == ["mcp", "add"]]
        self.assertEqual(ten_add, [], "lsp đã có trong `codex mcp list` -> không add")


class LogService(unittest.TestCase):
    """Log service của tdq_codex_mcp: timestamp ISO ra stderr, bật mặc định, tắt bằng TDQ_LOG=0."""

    def _bat(self, gia_tri):
        import contextlib
        import io as _io
        buf = _io.StringIO()
        with mock.patch.dict(os.environ, {"TDQ_LOG": gia_tri}), contextlib.redirect_stderr(buf):
            tdq_codex_mcp._log("thu log")
        return buf.getvalue()

    def test_log_bat_mac_dinh_co_timestamp(self):
        self.assertRegex(self._bat("1"), r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\] tdq_codex_mcp")

    def test_log_tat_duoc_bang_bien_moi_truong(self):
        self.assertEqual(self._bat("0"), "")


if __name__ == "__main__":
    unittest.main()
