#!/usr/bin/env python3
"""Unit test suite for Chrome DevTools MCP integration in TDQ Workflow."""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
import tdq_devtool_mcp


class TestDevtoolMcpIntegration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.claude_json = os.path.join(self.temp_dir, ".claude.json")
        self.settings_json = os.path.join(self.temp_dir, "settings.json")

    def tearDown(self):
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_plugin_manifest_has_config(self):
        manifest_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".claude-plugin", "plugin.json"))
        with open(manifest_path, encoding="utf-8") as f:
            data = json.load(f)
        user_config = data.get("userConfig", {})
        self.assertIn("ENABLE_DEVTOOL_MCP", user_config)
        self.assertEqual(user_config["ENABLE_DEVTOOL_MCP"]["type"], "boolean")

    def test_is_enabled_logic(self):
        # 1. Default disabled
        os.environ.pop("TDQ_ENABLE_DEVTOOL_MCP", None)
        self.assertFalse(tdq_devtool_mcp.is_enabled())

        # 2. Env enabled
        os.environ["TDQ_ENABLE_DEVTOOL_MCP"] = "1"
        self.assertTrue(tdq_devtool_mcp.is_enabled())
        os.environ.pop("TDQ_ENABLE_DEVTOOL_MCP", None)

    def test_setup_devtool_mcp_mock(self):
        # Initial status incomplete
        st = tdq_devtool_mcp.check_devtool_setup(
            claude_json_path=self.claude_json,
            settings_json_path=self.settings_json
        )
        self.assertFalse(st["mcp_registered"])
        self.assertFalse(st["permission_allowed"])

        # Run setup
        ok = tdq_devtool_mcp.setup_devtool_mcp(
            claude_json_path=self.claude_json,
            settings_json_path=self.settings_json
        )
        self.assertTrue(ok)

        # Re-check status
        st2 = tdq_devtool_mcp.check_devtool_setup(
            claude_json_path=self.claude_json,
            settings_json_path=self.settings_json
        )
        self.assertTrue(st2["mcp_registered"])
        self.assertTrue(st2["permission_allowed"])

    def test_skills_exist_and_valid(self):
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        test_skill = os.path.join(root, "skills", "tdq-browser-test", "SKILL.md")
        research_skill = os.path.join(root, "skills", "tdq-browser-research", "SKILL.md")
        guide_doc = os.path.join(root, "skills", "tdq-setup", "references", "chrome-devtools-mcp-guide.md")

        self.assertTrue(os.path.isfile(test_skill), "tdq-browser-test SKILL.md missing")
        self.assertTrue(os.path.isfile(research_skill), "tdq-browser-research SKILL.md missing")
        self.assertTrue(os.path.isfile(guide_doc), "chrome-devtools-mcp-guide.md missing")

        with open(test_skill, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Layer 1: Structural Tree", content)
        self.assertIn("Layer 2: Viewport Responsiveness", content)
        self.assertIn("Layer 3: Interactive Element States", content)
        self.assertIn("Layer 4: Silent Fault Detection", content)
        self.assertIn("Layer 5: CSS Cascade", content)

        with open(research_skill, encoding="utf-8") as f:
            r_content = f.read()
        self.assertIn("Adaptive Polling Engine", r_content)
        self.assertIn("Exponential Backoff", r_content)


if __name__ == "__main__":
    unittest.main()
