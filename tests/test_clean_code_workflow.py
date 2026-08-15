"""Test P6 — nối thư viện rule vào workflow (T6.1 viết đỏ, T6.2–T6.4 làm xanh).

- clean_code_gate: cổng bật/tắt clean code ở tdq-spec (câu hỏi + dòng `Clean code:` §4).
- qc_dong_bo: khối QC-F1→F3 cố định phải KHỚP nguyên văn giữa qc.md bản skill và portable.
- co_che_m: 5 cơ chế chống nợ kỹ thuật M1–M5 nằm đúng file neo theo
  docs/tdq/knowledge/2026-08-14-0900-chong-no-ky-thuat.md.
"""
import re
import unittest
from pathlib import Path

from helper import ROOT

SKILLS = Path(ROOT) / "skills"
SPEC_SKILL = SKILLS / "tdq-spec" / "SKILL.md"
SPEC_TEMPLATE = SKILLS / "tdq-spec" / "references" / "spec-template.md"
QC_BUILD = SKILLS / "tdq-build" / "references" / "qc.md"
QC_PORTABLE = Path(ROOT) / "portable" / "workflow" / "references" / "qc.md"
BUILD_SKILL = SKILLS / "tdq-build" / "SKILL.md"
PLAN_TEMPLATE = SKILLS / "tdq-plan" / "references" / "plan-template.md"
ANALYZE = SKILLS / "tdq-intake" / "references" / "analyze-full.md"

BAT_DAU_KHOI = ("**Số hạng mục QC = số dòng Definition of Done của plan, "
                "cộng ba hạng mục cố định.**")


class CleanCodeGate(unittest.TestCase):
    def test_clean_code_gate(self):
        skill = SPEC_SKILL.read_text(encoding="utf-8")
        self.assertIn("clean code", skill.lower(), "tdq-spec/SKILL.md thiếu cổng clean code")
        self.assertIn("Clean code:", skill, "SKILL.md phải trỏ tới dòng `Clean code:` của §4")
        khuon = SPEC_TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("A (đề xuất): BẬT", khuon, "khuôn A/B thiếu option BẬT")
        self.assertIn("B: TẮT", khuon, "khuôn A/B thiếu option TẮT")
        self.assertIn("Clean code: BẬT|TẮT", khuon, "§4 thiếu dòng Clean code: BẬT|TẮT")
        self.assertIn("tổ chức code theo rule", khuon,
                      "phải ghi rõ TẮT vẫn tổ chức code theo rule ngôn ngữ")


class QcDongBo(unittest.TestCase):
    def _khoi(self, path):
        text = path.read_text(encoding="utf-8")
        m = re.search(re.escape(BAT_DAU_KHOI) + r".*?ngoài DoD\.", text, re.DOTALL)
        self.assertIsNotNone(m, f"{path.name} ({path.parent}) thiếu khối QC-F cố định")
        return m.group(0)

    def test_qc_dong_bo(self):
        khoi_skill = self._khoi(QC_BUILD)
        khoi_portable = self._khoi(QC_PORTABLE)
        for ten in ("QC-F1", "QC-F2", "QC-F3"):
            self.assertIn(ten, khoi_skill, f"khối cố định thiếu {ten}")
        self.assertIn("code_rule_scan.py", khoi_skill,
                      "thiếu hạng mục scan khi Clean code: BẬT")
        self.assertIn("Clean code: BẬT", khoi_skill, "hạng mục scan phải gắn điều kiện BẬT")
        self.assertEqual(khoi_skill, khoi_portable,
                         "khối QC-F ở bản skill và bản portable phải khớp nguyên văn")


class CoCheM(unittest.TestCase):
    def test_co_che_m(self):
        cac_muc = [
            ("M1", ANALYZE, ["Hồ sơ kiến trúc", "docs/kien-truc.md", "sinh một lần"]),
            ("M2", SPEC_TEMPLATE, ["Ràng buộc kiến trúc phải giữ"]),
            ("M3", BUILD_SKILL, ["Tìm rồi mới tạo", "Tạo mới thay vì dùng"]),
            ("M4", PLAN_TEMPLATE, ["Chạm:", "graphify affected"]),
            ("M5", QC_BUILD, ["QC-F1", "QC-F2", "QC-F3"]),
        ]
        for ma, path, chuoi_can in cac_muc:
            with self.subTest(ten=ma):
                text = path.read_text(encoding="utf-8")
                for chuoi in chuoi_can:
                    self.assertIn(chuoi, text, f"{ma}: {path.name} thiếu '{chuoi}'")


if __name__ == "__main__":
    unittest.main()
