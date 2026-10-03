"""Cổng tìm kiếm cho Codex — T3.1, yêu cầu 2026-10-03-0015.

Trinh sát T1.1 bằng chạy thật `codex-cli 0.155.1`: Codex đã BỎ hook đi theo plugin
(`plugin_hooks  removed  false`), nên cổng phải được ghi vào `.codex/hooks.json` của từng project,
với đường dẫn tuyệt đối (Codex không có `${CLAUDE_PLUGIN_ROOT}`). Và `PreToolUse` của Codex chỉ
nhận `deny` — đúng khuôn cổng in ra.

Một lượt `codex exec` THẬT bị chặn chưa đo được trên máy dev (Codex chưa đăng nhập, 401) — ca đó
nằm ở Q9 của file QC, không giả lập ở đây.

Chạy riêng bằng `-k`: `ghi_hook`, `ten_tool`.
"""
import io
import json
import os
import sys
import tempfile
import unittest

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "hooks", "scripts"))
import search_observe  # noqa: E402
import tdq_codex_mcp  # noqa: E402


class GhiHook(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.duong = os.path.join(self.tmp.name, ".codex", "hooks.json")

    def doc(self):
        with io.open(self.duong, encoding="utf-8") as fh:
            return json.load(fh)

    def lenh(self, cfg, event):
        return [h["command"] for m in cfg["hooks"].get(event, []) for h in m.get("hooks", [])]

    def test_ghi_hook_project_moi_co_du_bon_entry(self):
        tdq_codex_mcp.khai_hook_codex(self.tmp.name)
        cfg = self.doc()
        self.assertTrue(any("search_gate.py" in c for c in self.lenh(cfg, "PreToolUse")))
        self.assertTrue(any("search_observe.py" in c for c in self.lenh(cfg, "PostToolUse")))
        self.assertTrue(any("search_observe.py" in c for c in self.lenh(cfg, "UserPromptSubmit")))

    def test_ghi_hook_duong_dan_tuyet_doi_co_that(self):
        """Codex không mở rộng `${CLAUDE_PLUGIN_ROOT}` — lệnh phải trỏ tới file có thật."""
        tdq_codex_mcp.khai_hook_codex(self.tmp.name)
        for c in self.lenh(self.doc(), "PreToolUse"):
            self.assertNotIn("CLAUDE_PLUGIN_ROOT", c)
            duong = c.split('"')[1]
            self.assertTrue(os.path.isfile(duong), duong)

    def test_ghi_hook_giu_cong_cu_cua_user_va_sao_luu(self):
        os.makedirs(os.path.dirname(self.duong))
        cu = {"hooks": {"PreToolUse": [{"matcher": "apply_patch", "hooks": [
            {"type": "command", "command": "python3 \"hooks/scripts/codex_edit_gate.py\""}]}]}}
        with io.open(self.duong, "w", encoding="utf-8") as fh:
            json.dump(cu, fh)
        tdq_codex_mcp.khai_hook_codex(self.tmp.name)
        self.assertIn("python3 \"hooks/scripts/codex_edit_gate.py\"",
                      self.lenh(self.doc(), "PreToolUse"), "hook sẵn có của user phải còn nguyên")
        bak = [f for f in os.listdir(os.path.dirname(self.duong)) if f.endswith(".bak")]
        self.assertEqual(len(bak), 1)

    def test_ghi_hook_chay_hai_lan_khong_doi(self):
        tdq_codex_mcp.khai_hook_codex(self.tmp.name)
        mot = io.open(self.duong, encoding="utf-8").read()
        dong = tdq_codex_mcp.khai_hook_codex(self.tmp.name)
        self.assertEqual(io.open(self.duong, encoding="utf-8").read(), mot)
        self.assertTrue(any("left unchanged" in d for d in dong))
        bak = [f for f in os.listdir(os.path.dirname(self.duong)) if f.endswith(".bak")]
        self.assertEqual(bak, [], "lần đầu không có file cũ thì không có gì để sao lưu")

    def test_ghi_hook_file_hong_thi_de_nguyen(self):
        os.makedirs(os.path.dirname(self.duong))
        with io.open(self.duong, "w", encoding="utf-8") as fh:
            fh.write("{khong phai json")
        dong = tdq_codex_mcp.khai_hook_codex(self.tmp.name)
        self.assertEqual(io.open(self.duong, encoding="utf-8").read(), "{khong phai json")
        self.assertIn("left untouched", dong[0])

    def _ghi(self, cfg):
        os.makedirs(os.path.dirname(self.duong), exist_ok=True)
        with io.open(self.duong, "w", encoding="utf-8") as fh:
            json.dump(cfg, fh)

    def _bak(self):
        return [f for f in os.listdir(os.path.dirname(self.duong)) if f.endswith(".bak")]

    def test_ghi_hook_cap_nhat_plugin_thi_sua_duong_cu_khong_nhan_doi(self):
        """Đường cache plugin mang số phiên bản: sau một lần cập nhật plugin, entry cũ trỏ vào
        file đã xoá phải được sửa tại chỗ — không thêm bộ thứ hai, không đụng entry của người khác."""
        cu = "C:/Users/x/.claude/plugins/cache/tdq/tdq-workflow/0.54.0/hooks/scripts"
        la = {"type": "command", "command": "python3 \"hooks/scripts/codex_edit_gate.py\""}
        self._ghi({"hooks": {
            "PreToolUse": [
                {"matcher": "apply_patch", "hooks": [dict(la)]},
                {"matcher": "Bash", "hooks": [
                    {"type": "command", "command": f'python3 "{cu}/search_gate.py"'}]},
                {"matcher": tdq_codex_mcp.MATCHER_KHAI_NIEM, "hooks": [
                    {"type": "command", "command": f'python3 "{cu}/search_observe.py"'}]}],
            "PostToolUse": [{"matcher": tdq_codex_mcp.MATCHER_KHAI_NIEM, "hooks": [
                {"type": "command", "command": f'python3 "{cu}/search_observe.py"'}]}],
            "UserPromptSubmit": [{"hooks": [
                {"type": "command", "command": f'python3 "{cu}/search_observe.py"'}]}]}})
        dong = tdq_codex_mcp.khai_hook_codex(self.tmp.name)
        cfg = self.doc()
        tat_ca = [c for ev in cfg["hooks"] for c in self.lenh(cfg, ev)]
        self.assertFalse([c for c in tat_ca if "0.54.0" in c], "đường cũ phải được sửa hết")
        for ev, ten in (("PreToolUse", "search_gate.py"), ("PreToolUse", "search_observe.py"),
                        ("PostToolUse", "search_observe.py"),
                        ("UserPromptSubmit", "search_observe.py")):
            moi = tdq_codex_mcp._lenh_hook(ten)
            self.assertIn(moi, self.lenh(cfg, ev), (ev, ten))
        # không nhân đôi: mỗi (event, matcher, script) đúng một lệnh
        for ev, muc_list in cfg["hooks"].items():
            khoa = [(m.get("matcher"), h["command"]) for m in muc_list for h in m["hooks"]]
            self.assertEqual(len(khoa), len(set(khoa)), ev)
        self.assertEqual(cfg["hooks"]["PreToolUse"][0], {"matcher": "apply_patch", "hooks": [la]})
        self.assertTrue(any("updated" in d for d in dong), dong)
        self.assertEqual(len(self._bak()), 1)

        truoc = io.open(self.duong, encoding="utf-8").read()
        dong2 = tdq_codex_mcp.khai_hook_codex(self.tmp.name)
        self.assertEqual(io.open(self.duong, encoding="utf-8").read(), truoc)
        self.assertEqual(len(self._bak()), 1, "chạy lại không được sao lưu thêm")
        self.assertTrue(any("left unchanged" in d for d in dong2))

    def test_ghi_hook_event_khong_phai_list_thi_de_nguyen(self):
        self._ghi({"hooks": {"PreToolUse": "not-a-list"}})
        truoc = io.open(self.duong, encoding="utf-8").read()
        dong = tdq_codex_mcp.khai_hook_codex(self.tmp.name)
        self.assertEqual(io.open(self.duong, encoding="utf-8").read(), truoc)
        self.assertIn("left untouched", dong[0])
        self.assertEqual(self._bak(), [])

    def test_ghi_hook_entry_thieu_hooks_thi_de_nguyen(self):
        self._ghi({"hooks": {"PostToolUse": [{"matcher": "x"}]}})
        truoc = io.open(self.duong, encoding="utf-8").read()
        dong = tdq_codex_mcp.khai_hook_codex(self.tmp.name)
        self.assertEqual(io.open(self.duong, encoding="utf-8").read(), truoc)
        self.assertIn("left untouched", dong[0])

    def test_ghi_hook_matcher_bash_co_ca_cong_va_ghi_nhan(self):
        """V4: `graphify query` chạy qua Bash phải được ghi nhận dưới Codex."""
        tdq_codex_mcp.khai_hook_codex(self.tmp.name)
        bash = [h["command"] for m in self.doc()["hooks"]["PreToolUse"]
                if m.get("matcher") == "Bash" for h in m["hooks"]]
        self.assertTrue(any(c.endswith('search_gate.py"') for c in bash), bash)
        self.assertTrue(any(c.endswith('search_observe.py"') for c in bash), bash)


class TenTool(unittest.TestCase):
    def test_ten_tool_claude_van_nhan(self):
        self.assertEqual(search_observe.la_goi_khai_niem(
            "mcp__plugin_lumen_lumen__semantic_search", {}), "lumen")
        self.assertEqual(search_observe.la_goi_khai_niem("mcp__lsp__find_references", {}),
                         "lsp:find_references")

    def test_ten_tool_kieu_codex_nhan_duoc(self):
        for ten in ("mcp__lumen__semantic_search", "lumen.semantic_search"):
            self.assertEqual(search_observe.la_goi_khai_niem(ten, {}), "lumen", ten)
        for ten in ("mcp__lsp__find_symbol", "lsp.find_symbol"):
            self.assertEqual(search_observe.la_goi_khai_niem(ten, {}), "lsp:find_symbol", ten)

    def test_ten_tool_don_dep_lsp_khong_tinh(self):
        for ten in ("mcp__lsp__start_lsp", "lsp.open_document"):
            self.assertIsNone(search_observe.la_goi_khai_niem(ten, {}), ten)

    def test_ten_tool_khong_lien_quan(self):
        for ten in ("mcp__claude_ai_Figma__whoami", "Read", "mcp__lumen__health_check"):
            self.assertIsNone(search_observe.la_goi_khai_niem(ten, {}), ten)


if __name__ == "__main__":
    unittest.main()
