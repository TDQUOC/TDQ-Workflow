"""Khoá ba luật của yêu cầu 2026-09-03-1220: hỏi bằng chat, `Next step:` nêu pha kế,
đường kẻ cuối lượt.

Vì sao phải khoá bằng test chứ không chỉ viết luật ra: cả ba luật này đều là luật HÀNH VI,
không có mã nào chạy để ép. Luật đánh số câu hỏi từng bị vi phạm ngay khi văn bản đã có sẵn.
Test là thứ duy nhất đỏ lên khi ai đó (người hay agent) sửa skill làm mất luật.

Ba luật, ba test, mỗi test một tên `-k` chạy riêng được: `popup`, `next_step`, `duong_ke`.
"""
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")
KHOI = os.path.join(SKILLS, "tdq-conventions", "references", "user-facing-block.md")

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_state  # noqa: E402

TEN_TOOL = "AskUserQuestion"

# Hai file được phép nhắc tên tool, vì chính chúng là nơi viết câu CẤM. Khai bằng đường dẫn
# thật chứ không bằng regex "câu nào có chữ cấm thì tha": một regex lỏng như thế tha luôn
# câu "cấm dùng grep, hãy dùng AskUserQuestion", tức là tha đúng thứ cần bắt.
DUOC_NHAC = {
    os.path.join("tdq-conventions", "references", "user-facing-block.md"),
    os.path.join("tdq-intake", "references", "interview.md"),
}

# Câu "Next step:" có thể xuống dòng. Đọc tiếp cho tới dòng trống hoặc heading.
NEXT_RE = re.compile(r"^Next step:")
KHONG_DOI_PHA = ("phase does not change", "pha không đổi")


def moi_file_md(goc):
    for thu_muc, _, ten_file in os.walk(goc):
        for ten in sorted(ten_file):
            if ten.endswith(".md"):
                yield os.path.join(thu_muc, ten)


def doc(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def cau_next_step(noi_dung):
    """Trả về từng câu `Next step:` đã nối hết phần xuống dòng."""
    dong = noi_dung.splitlines()
    ra = []
    for i, d in enumerate(dong):
        if not NEXT_RE.match(d):
            continue
        cau = [d]
        for tiep in dong[i + 1:]:
            if not tiep.strip() or tiep.startswith("#"):
                break
            cau.append(tiep)
        ra.append(" ".join(cau))
    return ra


class CamPopupTest(unittest.TestCase):
    """Luật 1 — mọi câu hỏi cho user hỏi bằng chat, không dùng tool popup."""

    def test_popup_khong_xuat_hien_ngoai_hai_file_viet_luat(self):
        pham = []
        for path in moi_file_md(SKILLS):
            if TEN_TOOL not in doc(path):
                continue
            tuong_doi = os.path.relpath(path, SKILLS)
            if tuong_doi not in DUOC_NHAC:
                pham.append(tuong_doi)
        self.assertEqual(pham, [], f"{TEN_TOOL} xuất hiện ngoài hai file viết luật: {pham}")

    def test_popup_luat_cam_nam_o_tang_conventions_va_phu_moi_cau_hoi(self):
        noi_dung = doc(KHOI)
        self.assertIn(TEN_TOOL, noi_dung, "mất câu cấm ở user-facing-block.md")
        self.assertIn("is banned", noi_dung)
        # Phạm vi phải là MỌI câu hỏi, không riêng bảy cổng — đây là điểm user chốt (1a).
        self.assertIn("EVERY question", noi_dung,
                      "câu cấm phải nói rõ áp cho mọi câu hỏi, không chỉ ở cổng")


class NextStepTest(unittest.TestCase):
    """Luật 2 — mỗi dòng `Next step:` nêu pha kế tiếp, hoặc nói rõ pha không đổi."""

    def test_next_step_moi_dong_neu_duoc_pha_ke(self):
        thieu = []
        for path in sorted(moi_file_md(SKILLS)):
            if os.path.basename(path) != "SKILL.md":
                continue
            for cau in cau_next_step(doc(path)):
                co_pha = any(f"`{pha}`" in cau for pha in tdq_state.PHASE_TABLE)
                co_khong_doi = any(chu in cau for chu in KHONG_DOI_PHA)
                if not (co_pha or co_khong_doi):
                    thieu.append((os.path.relpath(path, ROOT), cau[:80]))
        self.assertEqual(thieu, [],
                         "dòng Next step không nêu pha kế cũng không nói pha không đổi: "
                         f"{thieu}")

    def test_next_step_co_luat_va_ghi_ro_la_lop_du_phong(self):
        than = doc(os.path.join(SKILLS, "tdq-conventions", "SKILL.md"))
        self.assertIn("`Next step:`", than, "mất luật Next step ở tdq-conventions")
        self.assertIn("FALLBACK", than,
                      "luật phải nói rõ đây là lớp dự phòng, hook vẫn là đường chính")
        self.assertIn("[TDQ:NEXT]", than)


class DuongKeTest(unittest.TestCase):
    """Luật 3 — mọi lượt chat kết thúc bằng một đường kẻ `---`."""

    def test_duong_ke_la_thanh_phan_sau_khoi_tra_loi(self):
        noi_dung = doc(KHOI)
        self.assertIn("Closing rule of the turn", noi_dung, "mất thành phần 6")
        self.assertIn("six components", noi_dung,
                      "bảng thành phần vẫn ghi năm, chưa cộng thành phần 6")

    def test_duong_ke_khai_dung_ky_tu(self):
        noi_dung = doc(KHOI)
        self.assertIn("three hyphens `---`", noi_dung, "luật phải khai đúng ký tự ---")
        self.assertIn("———", noi_dung, "luật phải nói rõ ba gạch dài KHÔNG phải đường kẻ")

    def test_duong_ke_khong_con_cau_mau_thuan(self):
        noi_dung = doc(KHOI)
        self.assertNotIn("Printing anything after it", noi_dung,
                         "câu cũ nói không được viết gì dưới khối trả lời — đá với thành phần 6")


if __name__ == "__main__":
    unittest.main()
