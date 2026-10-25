"""Unit tests for MCP-First instruction, anchor recovery, and auto-setup / update features."""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "hooks", "scripts"))
import session_start  # noqa: E402
import tdq_setup  # noqa: E402


class MCPFirstAndAutoSetupTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.project = self.temp_dir.name
        os.makedirs(os.path.join(self.project, "docs", "tdq"), exist_ok=True)

    def test_khoi_huong_dan_chua_mcp_first(self):
        huong_dan = tdq_setup.khoi_huong_dan(goc=self.project)
        self.assertIn("## Nguyên tắc Ưu tiên MCP & Bộ kỹ năng MCP (MCP-First)", huong_dan)
        self.assertIn("Pre-flight check", huong_dan)
        self.assertIn("Roblox hoặc Unity", huong_dan)
        self.assertIn("mcp-first-guide.md", huong_dan)

    def test_mcp_first_guide_exists_and_has_platforms(self):
        guide_path = os.path.join(ROOT, "skills", "tdq-setup", "references", "mcp-first-guide.md")
        self.assertTrue(os.path.isfile(guide_path))
        with open(guide_path, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Chrome DevTools MCP", content)
        self.assertIn("Unity Engine", content)
        self.assertIn("Roblox Studio", content)
        self.assertIn("Pre-flight Check", content)

    def test_thuc_hien_setup_bu(self):
        ket_qua = tdq_setup.thuc_hien_setup_bu(self.project, "0.73.0", "0.75.0", goc_plugin=ROOT)
        self.assertIsInstance(ket_qua, list)
        self.assertTrue(any("ghim instruction" in k for k in ket_qua))

    def test_can_cap_nhat_phien_ban_detects_mismatch(self):
        # Khi chưa có file phát hành
        self.assertTrue(tdq_setup.can_cap_nhat_phien_ban(self.project, goc_plugin=ROOT))
        # Khi có file phát hành với version cũ
        phat_hanh = os.path.join(self.project, "docs", "tdq", ".tdq-phat-hanh.json")
        with open(phat_hanh, "w", encoding="utf-8") as f:
            json.dump({"phien_ban": "0.70.0", "cap_nhat": "2026-10-15"}, f)
        self.assertTrue(tdq_setup.can_cap_nhat_phien_ban(self.project, goc_plugin=ROOT))

        # Khi đã ghi nhận version hiện hành
        hien_tai = tdq_setup.doc_phien_ban_plugin(ROOT)
        with open(phat_hanh, "w", encoding="utf-8") as f:
            json.dump({"phien_ban": hien_tai, "cap_nhat": "2026-10-20"}, f)
        self.assertFalse(tdq_setup.can_cap_nhat_phien_ban(self.project, goc_plugin=ROOT))

    def test_tu_dong_cap_nhat_plugin_user_with_cli_runner(self):
        fake_home = os.path.join(self.temp_dir.name, "home")
        plugins_dir = os.path.join(fake_home, ".claude", "plugins")
        os.makedirs(plugins_dir, exist_ok=True)
        installed = {
            "plugins": {
                "tdq-workflow@tdq-local": [
                    {
                        "scope": "user",
                        "installPath": os.path.join(plugins_dir, "cache", "tdq-local", "tdq-workflow", "0.70.0"),
                        "version": "0.70.0",
                    }
                ]
            }
        }
        installed_file = os.path.join(plugins_dir, "installed_plugins.json")
        with open(installed_file, "w", encoding="utf-8") as f:
            json.dump(installed, f)

        calls = []

        def fake_runner(cmd):
            calls.append(cmd)
            return 0, "updated successfully"

        # Tắt _khong_cham_may trong phạm vi test để runner được gọi
        old_val = os.environ.get("TDQ_KHONG_CHAM_MAY")
        try:
            os.environ["TDQ_KHONG_CHAM_MAY"] = "0"
            cap_nhat, msg = tdq_setup.tu_dong_cap_nhat_plugin_user(home=fake_home, goc_plugin=ROOT, chay_lenh=fake_runner)
            v_hien_tai = tdq_setup.doc_phien_ban_plugin(ROOT)
            self.assertTrue(cap_nhat)
            self.assertIn(v_hien_tai, msg)
        finally:
            if old_val is None:
                os.environ.pop("TDQ_KHONG_CHAM_MAY", None)
            else:
                os.environ["TDQ_KHONG_CHAM_MAY"] = old_val

    def test_session_start_script_contains_mcp_first_in_anchor(self):
        script_path = os.path.join(ROOT, "hooks", "scripts", "session_start.py")
        with open(script_path, encoding="utf-8") as f:
            code = f.read()
        self.assertIn("MCP-First: ưu tiên MCP & bộ skill MCP", code)
        self.assertIn("LSP-Autonomy: toàn quyền tự quyết gate LSP", code)
        self.assertTrue(callable(session_start.main))


if __name__ == "__main__":
    unittest.main()
