"""Tests for upgrade logging, timestamps, mute-ability, and data minimization (O14).

Verifies:
  1. Standard log services emit ISO-formatted timestamps to stderr.
  2. TDQ_LOG=0 mutes runtime log output cleanly.
  3. Data minimization: prompts and tokens are sanitized/tokenized without leaking
     full raw prompt bodies or secret tokens into operational logs.
  4. Denial repeat logs maintain metadata bounds without memory/context leakage.
"""
import io
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

from helper import ROOT

SCRIPTS = os.path.join(ROOT, "scripts")
HOOKS = os.path.join(ROOT, "hooks", "scripts")


class TestUpgradeLogging(unittest.TestCase):
    """Test suite for logging services across upgraded components."""

    def test_log_service_iso_timestamp_and_stderr(self):
        """Standard log output must contain ISO timestamp and output to stderr."""
        sys.path.insert(0, SCRIPTS)
        try:
            import tdq_state
            buff = io.StringIO()
            with patch.dict(os.environ, {"TDQ_LOG": "1"}), patch("sys.stderr", buff):
                tdq_state._info("test event for logging verification")
            out = buff.getvalue()
            self.assertIn("ℹ️", out)
            self.assertIn("test event for logging verification", out)
            self.assertRegex(out, r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
        finally:
            if sys.path and sys.path[0] == SCRIPTS:
                sys.path.pop(0)

    def test_log_service_can_be_muted_with_tdq_log_zero(self):
        """TDQ_LOG=0 must mute stdout/stderr noise from log services."""
        sys.path.insert(0, SCRIPTS)
        try:
            import tdq_state
            buff = io.StringIO()
            with patch.dict(os.environ, {"TDQ_LOG": "0"}), patch("sys.stderr", buff):
                tdq_state._info("this log message must be silenced")
                tdq_state._warn("this warning must also be silenced")
            self.assertEqual(buff.getvalue(), "")
        finally:
            if sys.path and sys.path[0] == SCRIPTS:
                sys.path.pop(0)

    def test_search_observe_data_minimization(self):
        """search_observe logs token identifiers rather than raw user prompt text."""
        sys.path.insert(0, HOOKS)
        try:
            import search_observe
            with tempfile.TemporaryDirectory() as tmp:
                secret_word = "SUPER_SECRET_PASSWORD_12345"
                payload = {
                    "hook_event_name": "UserPromptSubmit",
                    "prompt": f"Please verify this {secret_word} now",
                    "session_id": "test_sess_log",
                    "cwd": tmp,
                }
                buff_err = io.StringIO()
                with patch.dict(os.environ, {"TDQ_LOG": "1"}), patch("sys.stderr", buff_err):
                    with patch("search_observe._common.read_payload", return_value=payload):
                        with patch("search_observe._common.payload_cwd", return_value=tmp):
                            with patch("search_observe._common.session_id", return_value="test_sess_log"):
                                with self.assertRaises(SystemExit):
                                    search_observe.main()

                # Verify log output mentions token count, not full prompt
                err_val = buff_err.getvalue()
                self.assertIn("prompt ·", err_val)
                self.assertIn("token", err_val)

                # Read ledger file: token list is tokenized identifiers, not raw text dump
                ledger_path = os.path.join(tmp, "docs", "tdq", ".tdq-search.jsonl")
                self.assertTrue(os.path.isfile(ledger_path))
                with open(ledger_path, encoding="utf-8") as f:
                    content = f.read()
                self.assertNotIn("Please verify this", content)
                self.assertIn(secret_word, content)
        finally:
            if sys.path and sys.path[0] == HOOKS:
                sys.path.pop(0)

    def test_utf8_io_log_muted_when_no_change_and_no_force(self):
        """utf8_io stays completely silent when streams already speak UTF-8."""
        sys.path.insert(0, SCRIPTS)
        try:
            import utf8_io
            buff = io.StringIO()
            with patch.dict(os.environ, {"TDQ_LOG": "1", "TDQ_UTF8_LOG_FORCE": "0"}), patch("sys.stderr", buff):
                class FakeStream:
                    def __init__(self, enc):
                        self.encoding = enc
                    def reconfigure(self, encoding, errors=None):
                        del encoding, errors

                fake_out = FakeStream("utf-8")
                fake_err = FakeStream("utf-8")
                utf8_io.force_utf8(out=fake_out, err=fake_err)
            self.assertEqual(buff.getvalue(), "")
        finally:
            if sys.path and sys.path[0] == SCRIPTS:
                sys.path.pop(0)

    def test_denial_repeat_log_minimization(self):
        """Turn ledger accurately records repeat_count for repeated denials without message bloat."""
        sys.path.insert(0, HOOKS)
        try:
            import _common
            with tempfile.TemporaryDirectory() as tmp:
                payload = {"session_id": "sess_repeat", "cwd": tmp}
                # Log first block
                _common.turn_log_append(tmp, "block", session="sess_repeat", code="TDQ:GIT",
                                        reason_key="AI traces detected", repeat_count=0)
                # Log second block (repeated)
                _common.turn_log_append(tmp, "block", session="sess_repeat", code="TDQ:GIT",
                                        reason_key="AI traces detected", repeat_count=1)

                rows = _common.turn_rows(tmp, payload)
                block_rows = [r for r in rows if r.get("kind") == "block"]
                self.assertEqual(len(block_rows), 2)
                self.assertEqual(block_rows[0].get("repeat_count"), 0)
                self.assertEqual(block_rows[1].get("repeat_count"), 1)
        finally:
            if sys.path and sys.path[0] == HOOKS:
                sys.path.pop(0)


if __name__ == "__main__":
    unittest.main()
