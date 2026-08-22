"""_common.approve_hint — lời mời duyệt phải mở CẢ HAI lối: câu chữ và chữ cái.

Chữ cái là lối vào cho user không gõ tiếng Việt: `prompt_context.LETTER` nhận `a`–`d`
đứng riêng, và đề xuất luôn ở option A, nên "A" là câu duyệt ở cả 3 cổng duyệt.
"""
import importlib.util
import os
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


if __name__ == "__main__":
    unittest.main()
