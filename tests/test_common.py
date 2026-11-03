"""_common.approve_hint — lời mời duyệt phải mở CẢ HAI lối: câu chữ và chữ cái.

Chữ cái là lối vào cho user không gõ tiếng Việt: `prompt_context.LETTER` nhận `a`–`d`
đứng riêng, và đề xuất luôn ở option A, nên "A" là câu duyệt ở cả 3 cổng duyệt.
"""
import importlib.util
import io
import json
from unittest import mock
import os
import re
import sys
import unittest

from helper import tdq_state

HOOKS = os.path.normpath(os.path.join(tdq_state.__file__, "..", "..", "hooks", "scripts"))
if HOOKS not in sys.path:
    sys.path.insert(0, HOOKS)
common = importlib.import_module("_common")

_spec = importlib.util.spec_from_file_location(
    "pc_for_common", os.path.join(HOOKS, "prompt_context.py"))
pc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pc)

MAX_CHARS = 240


class PayloadBoundaryTest(unittest.TestCase):
    def test_non_object_json_is_not_a_payload(self):
        for value in (None, [], [1], 42, True, "approval"):
            with self.subTest(value=value):
                with mock.patch.object(sys, "stdin", io.StringIO(json.dumps(value))):
                    self.assertEqual(common.read_payload(), {})

    def test_nested_fields_are_type_checked(self):
        payload = {"cwd": 42, "session_id": [], "tool_input": [1],
                   "tool_name": {}, "prompt": False, "stop_hook_active": "false"}
        with mock.patch.object(sys, "stdin", io.StringIO(json.dumps(payload))):
            parsed = common.read_payload()
        self.assertNotIn("cwd", parsed)
        self.assertNotIn("session_id", parsed)
        self.assertEqual(parsed["tool_input"], {})
        self.assertNotIn("tool_name", parsed)
        self.assertNotIn("prompt", parsed)
        self.assertNotIn("stop_hook_active", parsed)

    def test_invalid_tool_input_cannot_credit_a_concept_call(self):
        payload = {"tool_name": "mcp__lsp__find_symbol", "tool_input": []}
        with mock.patch.object(sys, "stdin", io.StringIO(json.dumps(payload))):
            parsed = common.read_payload()
        self.assertNotIn("tool_name", parsed)

    def test_command_argv_is_preserved(self):
        payload = {"tool_name": "shell", "tool_input": {
            "command": ["bash", "-lc", "rg symbol"]}}
        with mock.patch.object(sys, "stdin", io.StringIO(json.dumps(payload))):
            self.assertEqual(common.read_payload(), payload)

    def test_invalid_nested_values_cannot_credit_a_concept_call(self):
        for field, value in (("command", ["rg", 42]), ("command", {}),
                             ("pattern", []), ("root_dir", 42)):
            with self.subTest(field=field, value=value):
                payload = {"tool_name": "mcp__lsp__find_symbol",
                           "tool_input": {field: value}}
                with mock.patch.object(sys, "stdin", io.StringIO(json.dumps(payload))):
                    parsed = common.read_payload()
                self.assertNotIn(field, parsed["tool_input"])
                self.assertNotIn("tool_name", parsed)

    def test_valid_payload_is_preserved(self):
        payload = {"cwd": "C:/project", "session_id": "s", "tool_name": "Bash",
                   "tool_input": {"command": "rg symbol"}, "stop_hook_active": False}
        with mock.patch.object(sys, "stdin", io.StringIO(json.dumps(payload))):
            self.assertEqual(common.read_payload(), payload)


class ApproveHintTest(unittest.TestCase):
    def test_moi_cong_duyet_moi_ca_hai_loi(self):
        for target in ("spec", "plan", "quick"):
            with self.subTest(target=target):
                hint = common.approve_hint(target, None)
                self.assertIn("say", hint)
                self.assertIn('type "A"', hint)

    def test_cong_mode_moi_ca_hai_loi(self):
        hint = common.approve_hint("mode", "main")
        self.assertIn("inline", hint)
        self.assertIn('type "A"/"B"', hint)

    def test_chu_cai_da_moi_thi_hook_phai_nhan(self):
        """Lời mời gõ "A" mà hook không nhận "A" là mời user vào ngõ cụt."""
        for target in ("spec", "plan", "quick", "mode"):
            with self.subTest(target=target):
                self.assertTrue(pc.looks_like_approval("A", target), target)

    def test_moi_hint_van_duoi_tran_ky_tu(self):
        for target in ("spec", "plan", "quick", "mode"):
            with self.subTest(target=target):
                self.assertLessEqual(len(common.approve_hint(target, "subagent")), MAX_CHARS)


class PlanModeRegexTest(unittest.TestCase):
    """`_PLAN_MODE` phải sinh từ `VALID_MODES`, không viết cứng cặp nhị phân.

    Viết cứng `(main|subagent)` nghĩa là thêm mode thứ ba thì plan khai mode đó vẫn bị
    hook đọc ra None — cổng mode im lặng đề xuất sai. Nên bất biến ở đây là: MỌI mode
    trong `VALID_MODES` đều đọc được, và regex không chứa mã nào ngoài bảng đó.
    """

    def _viet_plan(self, mode):
        import tempfile
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        rel = os.path.join("docs", "tdq", "plan", "x.md")
        path = os.path.join(tmp.name, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write("# Plan\nMode thực thi: %s — lý do nào đó\n" % mode)
        return tmp.name, rel

    def test_doc_duoc_moi_mode_trong_bang(self):
        for mode in tdq_state.VALID_MODES:
            with self.subTest(mode=mode):
                cwd, rel = self._viet_plan(mode)
                self.assertEqual(common.plan_mode(cwd, {"plan_file": rel}), mode)

    def test_regex_sinh_tu_valid_modes(self):
        """Tập nhánh trong regex phải BẰNG `VALID_MODES` — không thiếu, không thừa.

        So bằng tập chứ không so bằng chuỗi nối: thứ tự nhánh là chuyện của regex
        (mã dài xếp trước để không bị mã ngắn là tiền tố nuốt mất), còn cái phải
        khoá lại là "đúng những mode đang có, không hơn không kém".
        """
        nhanh = re.search(r"\(([^)]*)\)", common._PLAN_MODE.pattern)
        self.assertIsNotNone(nhanh, "regex phải có đúng một nhóm bắt mode")
        self.assertEqual(set(nhanh.group(1).split("|")), set(tdq_state.VALID_MODES),
                         "nhánh mode phải sinh từ `VALID_MODES`, không gõ tay")

    def test_mode_ngoai_bang_khong_khop(self):
        cwd, rel = self._viet_plan("xyz")
        self.assertIsNone(common.plan_mode(cwd, {"plan_file": rel}))


class MaDongTest(unittest.TestCase):
    """`CODES` là danh sách ĐÓNG (spec §2.1) — thêm mã phải khai ở đây, không rải rác.

    Mã thứ sáu `TDQ:GON` (2026-09-17, T3.2) là mã của ba kênh bơm luật gọn. Test khoá
    luôn việc mã đó là mã hook thật: `session_start.py` in chính chuỗi này.
    """

    def test_gon_nam_trong_danh_sach_dong(self):
        self.assertIn("TDQ:GON", common.CODES)

    def test_moi_ma_dung_khuon_tdq(self):
        for ma in common.CODES:
            with self.subTest(ma=ma):
                self.assertRegex(ma, r"^TDQ:[A-Z]+$")

    def test_khong_ma_trung(self):
        self.assertEqual(len(common.CODES), len(set(common.CODES)))


class FormatDenialTest(unittest.TestCase):
    """O07 — format_denial sinh đúng định dạng cho lần đầu và lần lặp."""

    def test_lan_dau_full_remediation(self):
        lines = ["Chặn code.", "Dòng 1", "Dòng 2"]
        res = common.format_denial("TDQ:TEST", lines, repeat_count=0, day_du=True)
        self.assertIn("[TDQ:TEST] Chặn code.", res)
        self.assertIn("Dòng 1", res)
        self.assertIn("Dòng 2", res)
        self.assertNotIn("(lặp)", res)

    def test_lan_lap_shortened_co_tag_va_action(self):
        lines = ["Chặn code.", "Dòng 1: hướng dẫn", "Dòng 2: chi tiết"]
        res1 = common.format_denial("TDQ:TEST", lines, repeat_count=0, day_du=True)
        res2 = common.format_denial("TDQ:TEST", lines, repeat_count=1, day_du=True)
        res3 = common.format_denial("TDQ:TEST", lines, repeat_count=2, day_du=True)

        self.assertIn("(lặp)", res2)
        self.assertIn("(lặp x3)", res3)
        self.assertLess(len(res2), len(res1))
        self.assertIn("Gỡ nhanh:", res2)


if __name__ == "__main__":
    unittest.main()
