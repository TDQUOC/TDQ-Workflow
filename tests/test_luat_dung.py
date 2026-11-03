"""Luật dừng, khuôn spec, QC và report — yêu cầu 2026-10-03-0732 (đo trước, chạy hết plan).

Ca gốc: một phiên excalidraw dừng giữa implement để hỏi đổi ngưỡng installer 200 → 250 MB, vì
luật cũ cho dừng khi "spec/plan scope change". Luật mới: chỉ dừng ở 4 loại bất khả kháng khai bằng
`pause --loai`; ngưỡng trượt thì áp dự phòng, `lech add`, làm tiếp.

Chạy riêng từng nhóm bằng `-k`: `dung`, `khuon`, `qc_report`.
"""
import io
import os
import sys
import unittest

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import doc_lint  # noqa: E402

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


class Khuon(unittest.TestCase):
    """Khuôn §6 chép ra một spec mới phải qua được R14 khi điền đủ — khuôn và luật không lệch nhau."""

    TEN = "2026-10-04-0000-thu-khuon.md"

    def _bang_khuon(self):
        noi_dung = _doc(os.path.join(ROOT, "skills", "tdq-spec", "references", "spec-template.md"))
        dau = noi_dung.index("## 6. QC & Definition of Done")
        return noi_dung[dau:].splitlines()[1:3]  # header + separator, verbatim

    def _spec(self, hang):
        return "\n".join(["# SPEC — thử", "", "## 6. QC & Definition of Done",
                          *self._bang_khuon(), hang, "", "## 7. Câu hỏi còn mở", ""])

    def test_khuon_co_hai_cot_moi(self):
        dau = self._bang_khuon()[0]
        self.assertIn("Đo trước", dau)
        self.assertIn("Dự phòng nếu trượt", dau)

    def test_khuon_dien_du_thi_qua_r14(self):
        hang = ("| Q1 | Installer | bộ cài ≤ 200 MB | WebView2 offline 212 MB + app ~20 MB = 232 MB "
                "(trang tải của Microsoft) | dùng bootstrapper 2 MB, tải runtime lúc cài |")
        self.assertEqual(doc_lint.r14_loi(self._spec(hang), self.TEN), [])

    def test_khuon_thieu_do_thi_r14_bat(self):
        hang = "| Q1 | Installer | bộ cài ≤ 200 MB | — | — |"
        self.assertNotEqual(doc_lint.r14_loi(self._spec(hang), self.TEN), [])


class QcReport(unittest.TestCase):
    """Lệch spec phải hiện ở QC (không thành FAIL) và được hỏi duyệt ở report."""

    REPORT = os.path.join(ROOT, "skills", "tdq-build", "references", "report-template.md")

    def test_qc_report_qc_ghi_lech_khong_fail(self):
        noi_dung = _doc(QC)
        self.assertIn("## Lệch spec chờ duyệt", noi_dung)
        self.assertIn("lech list", noi_dung)
        self.assertIn("not FAIL", noi_dung)

    def test_qc_report_report_hoi_duyet_tung_lech(self):
        noi_dung = _doc(self.REPORT)
        self.assertIn("**Lệch spec chờ duyệt:**", noi_dung)
        for lenh in ("lech duyet", "lech bac", "set phase=implement"):
            self.assertIn(lenh, noi_dung, lenh)


if __name__ == "__main__":
    unittest.main()
