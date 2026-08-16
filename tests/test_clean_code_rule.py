"""Test luật clean code + SOLID ở skills/tdq-conventions/references/clean-code.md.

Luật này thay cho cổng hỏi BẬT/TẮT và script `code_rule_scan.py` đã xoá. Vì phần tự
kiểm không còn chạy được bằng linter, bộ test này gánh phần kiểm bằng lệnh: hình dạng
file, đủ 5 mã SOLID, đủ hai cột đọc, ví dụ trỏ file có thật, checklist đúng 5 câu.

- khuon: đủ 3 mục bắt buộc của một file luật (soul nguyên tắc 3).
- bang_solid / nguon: bảng 5 luật hai cột và URL truy được về file research.
- vi_du: mọi đường dẫn nêu trong ví dụ ĐÚNG/SAI phải tồn tại trên đĩa.
- lsp_gioi_han: LSP có nhãn giới hạn và đánh dấu bản đọc cho hàm là suy diễn.
- checklist / khi_nao: 5 câu có/không, và dấu hiệu nhận ra bằng mắt.
- conventions_nap: thân skill conventions có trỏ tới file luật.
- qc_khop_portable: hai bản qc.md đổi sang checklist, không bản nào còn nhắc script cũ.
"""
import re
import unittest
from pathlib import Path

from helper import ROOT

SKILLS = Path(ROOT) / "skills"
LUAT = SKILLS / "tdq-conventions" / "references" / "clean-code.md"
CONVENTIONS = SKILLS / "tdq-conventions" / "SKILL.md"
QC_BUILD = SKILLS / "tdq-build" / "references" / "qc.md"
QC_PORTABLE = Path(ROOT) / "portable" / "workflow" / "references" / "qc.md"
RESEARCH = Path(ROOT) / "docs" / "tdq" / "research" / "2026-08-16-bo-cong-clean-code.md"

MA_SOLID = ("SRP", "OCP", "LSP", "ISP", "DIP")
MUC_BAT_BUOC = ("## Khi nào áp dụng", "## Làm gì", "## Tự kiểm")

# Đường dẫn repo nhắc trong ví dụ: `scripts/x.py` hoặc `scripts/x.py::ham`.
DUONG_DAN = re.compile(r"`((?:scripts|hooks|skills|tests)/[\w./-]+?\.(?:py|md))(?:::[\w.]+)?`")
URL = re.compile(r"https?://[^\s)`|]+")


def doc(path):
    return path.read_text(encoding="utf-8")


def dong_bang(noi_dung, ma):
    """Dòng bảng bắt đầu bằng `| <ma> |` — trả list ô đã tách, rỗng nếu không có."""
    for dong in noi_dung.splitlines():
        if dong.strip().startswith(f"| {ma} "):
            return [o.strip() for o in dong.strip().strip("|").split("|")]
    return []


class KhuonFileLuat(unittest.TestCase):
    """T1.1 — hình dạng bắt buộc của một file luật theo soul nguyên tắc 3."""

    def test_khuon_du_ba_muc(self):
        self.assertTrue(LUAT.is_file(), f"chưa có file luật {LUAT}")
        noi_dung = doc(LUAT)
        for muc in MUC_BAT_BUOC:
            self.assertIn(muc, noi_dung, f"file luật thiếu mục `{muc}`")

    def test_khuon_co_dong_soul(self):
        self.assertIn("Soul: chất lượng > runtime > context cost", doc(LUAT),
                      "file luật thiếu dòng Soul ở đầu file")


class BangSolid(unittest.TestCase):
    """T1.2 — bảng 5 luật, mỗi luật đủ hai cột đọc."""

    def test_bang_solid_du_nam_ma(self):
        noi_dung = doc(LUAT)
        for ma in MA_SOLID:
            with self.subTest(ma=ma):
                self.assertTrue(dong_bang(noi_dung, ma), f"bảng thiếu dòng của {ma}")

    def test_bang_solid_du_hai_cot_doc(self):
        """Cột 'khi có class' và cột 'khi chỉ có hàm/module' đều phải có chữ."""
        noi_dung = doc(LUAT)
        for ma in MA_SOLID:
            with self.subTest(ma=ma):
                o = dong_bang(noi_dung, ma)
                self.assertGreaterEqual(len(o), 3, f"{ma}: bảng phải có ít nhất 3 cột")
                self.assertTrue(o[1], f"{ma}: cột 'khi có class' rỗng")
                self.assertTrue(o[2], f"{ma}: cột 'khi chỉ có hàm/module' rỗng")

    def test_bang_solid_co_tieu_de_hai_cot(self):
        noi_dung = doc(LUAT).lower()
        self.assertIn("class", noi_dung, "bảng thiếu tiêu đề cột cho ca có class")
        self.assertIn("hàm", noi_dung, "bảng thiếu tiêu đề cột cho ca chỉ có hàm/module")

    def test_nguon_truy_duoc_ve_research(self):
        """Cấm bịa nguồn: mọi URL trong luật phải có mặt trong file research."""
        self.assertTrue(RESEARCH.is_file(), "thiếu file research của request")
        goc = doc(RESEARCH)
        la = [u for u in URL.findall(doc(LUAT)) if u not in goc]
        self.assertEqual(la, [], f"URL không truy được về research: {la}")

    def test_nguon_co_it_nhat_ba_url(self):
        self.assertGreaterEqual(len(set(URL.findall(doc(LUAT)))), 3,
                                "luật phải dẫn ít nhất 3 nguồn")


class ViDu(unittest.TestCase):
    """T1.3 — ví dụ ĐÚNG/SAI phải trỏ vào file có thật, không bịa đường dẫn."""

    def test_vi_du_co_ca_dung_va_sai(self):
        noi_dung = doc(LUAT)
        self.assertIn("ĐÚNG", noi_dung, "luật thiếu ví dụ ĐÚNG")
        self.assertIn("SAI", noi_dung, "luật thiếu ví dụ SAI")

    def test_vi_du_duong_dan_co_that(self):
        thieu = [d for d in set(DUONG_DAN.findall(doc(LUAT)))
                 if not (Path(ROOT) / d).is_file()]
        self.assertEqual(thieu, [], f"ví dụ trỏ vào file không tồn tại: {thieu}")

    def test_vi_du_du_nam_luat(self):
        """Mỗi mã SOLID phải có ít nhất một ví dụ riêng, không gộp chung một ví dụ."""
        noi_dung = doc(LUAT)
        for ma in MA_SOLID:
            with self.subTest(ma=ma):
                khoi = noi_dung.split(f"### {ma}")
                self.assertGreater(len(khoi), 1, f"thiếu khối ví dụ `### {ma}`")
                self.assertIn("ĐÚNG", khoi[1].split("### ")[0], f"{ma}: thiếu ví dụ ĐÚNG")
                self.assertIn("SAI", khoi[1].split("### ")[0], f"{ma}: thiếu ví dụ SAI")


class LspGioiHan(unittest.TestCase):
    """T1.4 — LSP là luật duy nhất cần kế thừa; cấm trình bày bản đọc hàm như trích Liskov."""

    def test_lsp_gioi_han_neu_dieu_kien_ke_thua(self):
        o = dong_bang(doc(LUAT), "LSP")
        self.assertTrue(o, "bảng thiếu dòng LSP")
        self.assertIn("kế thừa", " ".join(o).lower(),
                      "LSP phải nói rõ chỉ áp nguyên văn khi có kế thừa")

    def test_lsp_gioi_han_danh_dau_suy_dien(self):
        noi_dung = doc(LUAT)
        khoi = noi_dung.split("### LSP")
        self.assertGreater(len(khoi), 1, "thiếu khối `### LSP`")
        than = khoi[1].split("### ")[0].lower()
        self.assertIn("suy diễn", than,
                      "bản đọc cho hàm của LSP phải đánh dấu là suy diễn, không phải trích Liskov")


class TuKiem(unittest.TestCase):
    """T1.5 — checklist thay cho lệnh scan đã xoá."""

    def _cau_hoi(self):
        than = doc(LUAT).split("## Tự kiểm")[-1]
        return [d.strip() for d in than.splitlines()
                if d.strip().startswith("-") and d.strip().endswith("?")]

    def test_checklist_dung_nam_cau(self):
        cau = self._cau_hoi()
        self.assertEqual(len(cau), 5, f"checklist phải đúng 5 câu, đang có {len(cau)}: {cau}")

    def test_checklist_moi_cau_mot_dong(self):
        for c in self._cau_hoi():
            with self.subTest(cau=c[:40]):
                self.assertNotIn("\n", c, "mỗi câu hỏi phải nằm gọn một dòng")

    def test_checklist_phu_ca_hai_ban_doc(self):
        """QC1.1 — bảng có hai cột thì checklist cũng phải hỏi cả hai, không chỉ bản đọc hàm.

        LSP và OCP là hai luật đổi nghĩa nhiều nhất giữa ca có class và ca chỉ có hàm.
        Câu hỏi chỉ nhắc vế hàm sẽ dẫn model sửa cây class đi sai luật gốc.
        """
        can = {"LSP": "kế thừa", "OCP": "class"}
        cau = {c.split(":", 1)[0].lstrip("- ").strip(): c for c in self._cau_hoi()}
        for ma, tu in can.items():
            with self.subTest(ma=ma):
                self.assertIn(ma, cau, f"checklist thiếu câu của {ma}")
                self.assertIn(tu, cau[ma].lower(),
                              f"câu {ma} chưa phủ ca có class — thiếu chữ `{tu}`")

    def test_khi_nao_co_dau_hieu_nhan_ra(self):
        than = doc(LUAT).split("## Khi nào áp dụng")[-1].split("## ")[0]
        dong = [d for d in than.splitlines() if d.strip().startswith("-")]
        self.assertGreaterEqual(len(dong), 2,
                                "mục `Khi nào áp dụng` phải có ít nhất 2 dấu hiệu")


class ConventionsNap(unittest.TestCase):
    """T2.1 — luật vô hình nếu thân skill không trỏ tới nó."""

    def test_conventions_nap_luat_moi(self):
        self.assertIn("clean-code.md", doc(CONVENTIONS),
                      "tdq-conventions/SKILL.md chưa trỏ tới references/clean-code.md")

    def test_conventions_nap_neu_ro_solid(self):
        self.assertIn("SOLID", doc(CONVENTIONS),
                      "thân skill phải nêu chữ SOLID để model biết luật nói về gì")


class QcKhopPortable(unittest.TestCase):
    """T4.1 + T4.2 — hạng mục DoD đổi dạng, hai bản phải khớp nhau."""

    def test_qc_khop_portable_khong_con_script_cu(self):
        for path in (QC_BUILD, QC_PORTABLE):
            with self.subTest(file=path.name):
                self.assertNotIn("code_rule_scan", doc(path),
                                 f"{path} còn nhắc script đã xoá")

    def test_qc_khop_portable_deu_nhac_checklist(self):
        for path in (QC_BUILD, QC_PORTABLE):
            with self.subTest(file=path.name):
                self.assertIn("clean-code.md", doc(path),
                              f"{path} phải trỏ tới luật clean code mới")

    def test_qc_khop_portable_khong_con_cong_bat_tat(self):
        for path in (QC_BUILD, QC_PORTABLE):
            with self.subTest(file=path.name):
                self.assertNotIn("Clean code: BẬT", doc(path),
                                 f"{path} còn dựa vào cổng BẬT/TẮT đã gỡ")


if __name__ == "__main__":
    unittest.main()
