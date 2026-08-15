"""Nhãn lane cho người đọc + bí danh cho người gõ.

Định danh máy vẫn là `quick`/`full` (không migrate state). Chỉ hai thứ đổi:
  - NHÃN người ĐỌC: lane_label() -> "chế độ nhanh (express)" / "chế độ chuyên sâu (deep)"
  - BÍ DANH người GÕ: normalize_lane() nhận nhanh|express|quick, chuyên sâu|deep|full
Spec: docs/tdq/spec/2026-08-12-0900-doi-ten-lane.md
"""
import sys
import tempfile
import unittest

from helper import HOOKS, read_state, run_state_cli, tdq_state

sys.path.insert(0, HOOKS)
import _common  # noqa: E402
import bash_gate  # noqa: E402
import prompt_context  # noqa: E402

LABEL_QUICK = "chế độ nhanh (express)"
LABEL_FULL = "chế độ chuyên sâu (deep)"


class LaneLabelTest(unittest.TestCase):
    def test_nhan_hai_lane(self):
        self.assertEqual(tdq_state.lane_label("quick"), LABEL_QUICK)
        self.assertEqual(tdq_state.lane_label("full"), LABEL_FULL)

    def test_lane_la_tra_lai_nguyen_chuoi(self):
        """Nhãn là lớp hiển thị, không phải lớp kiểm tra — lane lạ không được nổ."""
        self.assertEqual(tdq_state.lane_label("xyz"), "xyz")
        self.assertEqual(tdq_state.lane_label(None), "")

    def test_bang_nhan_phu_dung_hai_lane_hop_le(self):
        self.assertEqual(set(tdq_state.LANE_LABELS), {"quick", "full"})


class NormalizeLaneTest(unittest.TestCase):
    CASES = [
        ("quick", "quick"), ("nhanh", "quick"), ("express", "quick"),
        ("QUICK", "quick"), ("Express", "quick"), ("  nhanh  ", "quick"),
        ("full", "full"), ("deep", "full"), ("chuyen-sau", "full"),
        ("chuyensau", "full"), ("chuyên sâu", "full"), ("DEEP", "full"),
        ("xyz", None), ("", None), (None, None), ("quicky", None),
    ]

    def test_bang_bi_danh(self):
        for raw, want in self.CASES:
            with self.subTest(raw=raw):
                self.assertEqual(tdq_state.normalize_lane(raw), want)


class LaneCliAliasTest(unittest.TestCase):
    def test_init_bang_bi_danh_ghi_dinh_danh_cu(self):
        """`init t express` phải ghi lane=quick — bí danh chỉ ở cửa vào, state không đổi."""
        for alias, want in (("express", "quick"), ("chuyen-sau", "full"), ("nhanh", "quick")):
            with self.subTest(alias=alias), tempfile.TemporaryDirectory() as tmp:
                code, _, err = run_state_cli(tmp, "init", "2026-08-12-0900-t", alias)
                self.assertEqual(code, 0, err)
                self.assertEqual(read_state(tmp)["lane"], want)

    def test_init_lane_rac_van_bao_loi(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, _, err = run_state_cli(tmp, "init", "2026-08-12-0900-t", "xyz")
            self.assertNotEqual(code, 0)
            self.assertIn("nhanh", err.lower())

    def test_approve_bi_danh_ghi_khoa_quick(self):
        for alias in ("nhanh", "express", "quick"):
            with self.subTest(alias=alias), tempfile.TemporaryDirectory() as tmp:
                run_state_cli(tmp, "init", "2026-08-12-0900-t", "nhanh")
                code, _, err = run_state_cli(tmp, "approve", alias, "--by", "duyệt " + alias)
                self.assertEqual(code, 0, err)
                self.assertTrue(read_state(tmp)["quick_approved"])


class ApprovalPhraseTest(unittest.TestCase):
    """Câu duyệt bằng từ mới. Rủi ro nặng nhất của việc đổi nhãn là duyệt OAN:
    `nhanh` là tính từ rất thường gặp trong chat, nên chỉ nhận khi nó đứng NGAY
    SAU một từ đồng ý (duyệt/chốt/approve)."""

    DUONG = ["duyệt quick", "duyệt nhanh", "duyệt express", "duyet nhanh",
             "chốt nhanh", "approve express", "Duyệt Chế Độ Nhanh"]
    AM = ["làm nhanh giúp tôi", "ok làm nhanh nhé", "nhanh lên", "ok tôi hiểu rồi",
          "duyệt nhanh chưa?", "chạy nhanh hơn được không"]

    def test_cau_duyet_duong(self):
        for prompt in self.DUONG:
            with self.subTest(prompt=prompt):
                self.assertTrue(prompt_context.looks_like_approval(prompt, "quick"))

    def test_cau_khong_phai_duyet(self):
        for prompt in self.AM:
            with self.subTest(prompt=prompt):
                self.assertFalse(prompt_context.looks_like_approval(prompt, "quick"))

    def test_bi_danh_khong_duyet_lam_cho_spec_plan(self):
        self.assertFalse(prompt_context.looks_like_approval("duyệt nhanh", "spec"))
        self.assertFalse(prompt_context.looks_like_approval("duyệt nhanh", "plan"))


class BashGateAliasTest(unittest.TestCase):
    def test_approve_cli_nhan_bi_danh(self):
        for cmd in ("python3 scripts/tdq_state.py approve quick",
                    "python3 scripts/tdq_state.py approve nhanh",
                    "python3 scripts/tdq_state.py approve express"):
            with self.subTest(cmd=cmd):
                self.assertTrue(bash_gate.APPROVE_CLI.search(cmd))

    def test_khong_nhan_tu_la(self):
        self.assertIsNone(bash_gate.APPROVE_CLI.search(
            "python3 scripts/tdq_state.py approve xyz"))


class ApproveHintTest(unittest.TestCase):
    def test_hint_quick_neu_tu_moi_va_khong_qua_dai(self):
        hint = _common.APPROVE_HINTS["quick"]
        self.assertIn("duyệt nhanh", hint)
        trimmed = _common.trim([hint])
        self.assertLessEqual(len(trimmed), _common.MAX_REMIND_CHARS)
        self.assertLessEqual(len(trimmed.splitlines()), _common.MAX_REMIND_LINES)


class UsageLabelTest(unittest.TestCase):
    def test_usage_neu_nhan_moi(self):
        self.assertIn("nhanh", tdq_state.USAGE)
        self.assertIn("express", tdq_state.USAGE)


if __name__ == "__main__":
    unittest.main()
