"""Luật dừng, khuôn spec, QC và report — yêu cầu 2026-10-03-0732 (đo trước, chạy hết plan).

Ca gốc: một phiên excalidraw dừng giữa implement để hỏi đổi ngưỡng installer 200 → 250 MB, vì
luật cũ cho dừng khi "spec/plan scope change". Luật mới: chỉ dừng ở 4 loại bất khả kháng khai bằng
`pause --loai`; ngưỡng trượt thì áp dự phòng, `lech add`, làm tiếp.

Chạy riêng từng nhóm bằng `-k`: `dung`, `khuon`, `qc_report`.
"""
import io
import os
import unittest

from helper import ROOT

BUILD = os.path.join(ROOT, "skills", "tdq-build", "SKILL.md")
CONV = os.path.join(ROOT, "skills", "tdq-conventions", "SKILL.md")
QC = os.path.join(ROOT, "skills", "tdq-build", "references", "qc.md")
LOAI = ("mat-truy-cap", "pha-huy", "dau-vao-user", "tran-qc")


def _doc(duong):
    with io.open(duong, encoding="utf-8") as fh:
        return fh.read()


class LuatDung(unittest.TestCase):
    def test_dung_khong_con_cho_dung_vi_doi_pham_vi(self):
        """Không file luật nào còn cho dừng vì "scope change" — đó là đường agent đã đi trong ảnh."""
        for goc, _, ten in os.walk(os.path.join(ROOT, "skills")):
            for t in ten:
                if t.endswith(".md"):
                    duong = os.path.join(goc, t)
                    self.assertNotIn("scope change", _doc(duong), duong)

    def test_dung_bon_loai_co_mat_o_ca_hai_file(self):
        for duong in (BUILD, CONV):
            noi_dung = _doc(duong)
            for loai in LOAI:
                self.assertIn(loai, noi_dung, (duong, loai))
            self.assertIn("pause --loai", noi_dung, duong)

    def test_dung_nguong_truot_thi_ghi_lech_lam_tiep(self):
        for duong in (BUILD, CONV, QC):
            self.assertIn("lech add", _doc(duong), duong)

    def test_dung_qc_khong_keo_user_vao_giua(self):
        noi_dung = _doc(QC)
        self.assertIn("PASS (lệch, chờ duyệt)", noi_dung)
        self.assertIn("pause --loai tran-qc", noi_dung)


if __name__ == "__main__":
    unittest.main()
