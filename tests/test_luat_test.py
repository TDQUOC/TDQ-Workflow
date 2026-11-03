"""Luật chạy test một nguồn — yêu cầu 2026-10-03-1907 (H5: test vùng chạm, trọn bộ ở 2 cổng).

Trước đó ba file luật nói ba điều khác nhau: `tdq-build` "chạy trọn bộ EXACTLY ONCE", khuôn plan
"sau mỗi phase chạy toàn bộ", `qc.md` "mỗi vòng sửa cộng full suite". Đo trên 8 request: trung bình
7,4 lần trọn bộ mỗi request. Luật mới: bước trung gian = `tdq_test.py vung-cham` (vùng chạm + bán
kính ảnh hưởng); trọn bộ = QC-F1 + một lần sau vòng sửa QC cuối.
"""
import io
import os
import unittest

from helper import ROOT

BUILD = os.path.join(ROOT, "skills", "tdq-build", "SKILL.md")
PLAN = os.path.join(ROOT, "skills", "tdq-plan", "references", "plan-template.md")
QC = os.path.join(ROOT, "skills", "tdq-build", "references", "qc.md")
CAU_CU = ("EXACTLY ONCE", "Sau mỗi phase: chạy toàn bộ", "plus the full suite",
          "plus the test suite", "running only **the module's tests**")


def _doc(duong):
    with io.open(duong, encoding="utf-8") as fh:
        return fh.read()


class LuatMotNguon(unittest.TestCase):
    def test_ba_file_cung_noi_vung_cham(self):
        for duong in (BUILD, PLAN, QC):
            self.assertIn("vung-cham", _doc(duong), duong)

    def test_khong_con_cau_cu_o_dau_ca(self):
        """Không file luật nào còn câu dẫn tới 7,4 lần trọn bộ mỗi request."""
        for goc, _, ten in os.walk(os.path.join(ROOT, "skills")):
            for t in ten:
                if t.endswith(".md"):
                    noi_dung = _doc(os.path.join(goc, t))
                    for cau in CAU_CU:
                        self.assertNotIn(cau, noi_dung, (t, cau))

    def test_xong_implement_khong_chay_tron_bo_rieng(self):
        self.assertIn("do NOT run the full suite here", _doc(BUILD))
        self.assertIn("tron-bo", _doc(BUILD))

    def test_qc_hai_cong_va_so_bo_sot(self):
        noi_dung = _doc(QC)
        self.assertIn("tdq_test.py\" tron-bo", noi_dung.replace("${CLAUDE_PLUGIN_ROOT}/scripts/", ""))
        self.assertIn("only after the LAST fix round", noi_dung)
        self.assertIn("tdq_test.py so", noi_dung)
        self.assertIn("radius miss", noi_dung.lower())


if __name__ == "__main__":
    unittest.main()
