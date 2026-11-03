"""Policy coverage, not a claim of measured agent effectiveness."""
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import tdq_setup


class ToolCompositionPolicy(unittest.TestCase):
    def text(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_soul_and_standing_steps(self):
        for relative in ("skills/tdq-conventions/SKILL.md",
                         "skills/tdq-conventions/references/soul.md"):
            with self.subTest(path=relative):
                text = self.text(relative)
                for term in ("internal steps", "verify", "permission"):
                    self.assertIn(term, text)

    def test_routing_uses_actual_inventory_and_direct_path(self):
        text = self.text("skills/tdq-conventions/references/plugin-routing.md")
        for term in ("current inventory", "Chrome MCP", "agent-desktop",
                     "upload_file", "window", "one tool"):
            self.assertIn(term, text)
        self.assertNotIn("EVERY plugin is already enabled", text)

    def test_missing_tools_require_proposal_not_install(self):
        text = self.text("skills/tdq-setup/references/mcp-first-guide.md")
        for term in ("official sources", "user-level", "approval", "uninstall"):
            self.assertIn(term, text)
        instruction = tdq_setup.khoi_huong_dan("/fixture")
        self.assertIn("chờ user duyệt", instruction)
        self.assertNotIn("Agent tự tìm kiếm và cài đặt dependency", instruction)

    def test_delivery_observe_before_repeat(self):
        text = self.text("skills/tdq-conventions/references/plugin-routing.md")
        self.assertIn("delivery is uncertain", text)
        self.assertIn("observe before retry", text)
        self.assertIn("denied action", text)

    def test_download_verifies_real_file(self):
        text = self.text("skills/tdq-conventions/references/plugin-routing.md")
        for term in ("final file", "content", "click", "Save As"):
            self.assertIn(term, text)

    def test_retry_requires_progress(self):
        text = self.text("skills/tdq-conventions/SKILL.md")
        self.assertIn("changed conditions", text)
        self.assertIn("completion events", text)

    def test_managed_instruction_has_full_loop(self):
        instruction = tdq_setup.khoi_huong_dan("/fixture")
        for term in ("bước nội bộ", "Chrome MCP", "agent-desktop", "upload_file",
                     "đích", "kiểm chứng", "không lặp", "quyền"):
            self.assertIn(term, instruction)


def verify_runtime_receipt(receipt):
    """Verify an explicit local-fixture receipt, never discover private user files."""
    assert receipt["origin"] == "local-fixture"
    assert receipt["upload_tool"] == "chrome-devtools.upload_file"
    assert receipt["attachment_verified"] is True
    assert receipt["console_errors"] == 0
    target = Path(receipt["download_path"])
    assert target.is_file() and not target.name.endswith((".crdownload", ".part"))
    assert hashlib.sha256(target.read_bytes()).hexdigest() == receipt["sha256"]


class RuntimeReceiptTests(unittest.TestCase):
    def test_runtime_rejects_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt = {"origin": "local-fixture", "upload_tool": "chrome-devtools.upload_file",
                       "attachment_verified": True, "console_errors": 0,
                       "download_path": str(Path(tmp) / "missing.txt"), "sha256": "0" * 64}
            with self.assertRaises(AssertionError):
                verify_runtime_receipt(receipt)

    def test_runtime_rejects_partial_or_wrong_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "result.txt"
            target.write_bytes(b"fixture")
            receipt = {"origin": "local-fixture", "upload_tool": "chrome-devtools.upload_file",
                       "attachment_verified": True, "console_errors": 0,
                       "download_path": str(target), "sha256": "0" * 64}
            with self.assertRaises(AssertionError):
                verify_runtime_receipt(receipt)
            receipt["sha256"] = hashlib.sha256(b"fixture").hexdigest()
            verify_runtime_receipt(receipt)
            partial = target.with_suffix(".crdownload")
            target.rename(partial)
            receipt["download_path"] = str(partial)
            with self.assertRaises(AssertionError):
                verify_runtime_receipt(receipt)

    @unittest.skipUnless(os.environ.get("TDQ_TOOL_RUNTIME_RECEIPT"), "explicit live receipt required")
    def test_runtime_live_receipt(self):
        receipt = json.loads(Path(os.environ["TDQ_TOOL_RUNTIME_RECEIPT"]).read_text(encoding="utf-8"))
        verify_runtime_receipt(receipt)

    @unittest.skipUnless(os.environ.get("TDQ_INSTRUCTION_RECEIPT"), "explicit user-level receipt required")
    def test_user_instruction_receipt(self):
        receipt = json.loads(Path(os.environ["TDQ_INSTRUCTION_RECEIPT"]).read_text(encoding="utf-8"))
        self.assertEqual(receipt["outside_before_sha256"], receipt["outside_after_sha256"])
        self.assertTrue(receipt["backup_verified"])
        self.assertTrue(receipt["second_run_noop"])
        self.assertTrue(receipt["permissions_unchanged"])
        self.assertTrue(receipt["settings_unchanged"])


if __name__ == "__main__":
    unittest.main()
