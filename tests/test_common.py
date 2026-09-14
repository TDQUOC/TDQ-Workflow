"""_common.approve_hint — lời mời duyệt phải mở CẢ HAI lối: câu chữ và chữ cái.

Chữ cái là lối vào cho user không gõ tiếng Việt: `prompt_context.LETTER` nhận `a`–`d`
đứng riêng, và đề xuất luôn ở option A, nên "A" là câu duyệt ở cả 3 cổng duyệt.
"""
import importlib.util
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


if __name__ == "__main__":
    unittest.main()
