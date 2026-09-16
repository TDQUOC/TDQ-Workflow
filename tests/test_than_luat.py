"""Test khoá hình dạng thân luật "build less than asked" (T1.2).

Khoá 5 điều, sửa hỏng điều nào là đỏ điều đó:
1. `rules/chung.md` có đúng một cặp marker `luat-gon`, mở trước đóng.
2. Khối giữa cặp marker chứa bảng thang đúng 7 bậc, theo thứ tự 1..7 (rớt bậc hay
   trùng bậc đều đỏ) — `BayBacTuChoiBangSai` chứng minh phép so này có cắn.
3. Khối đó chứa món 8 "make it run first, refactor after", so theo lời luật.
4. Câu luật tầng 1–2 nằm trong THÂN `skills/tdq-build/SKILL.md`, kèm sàn phức tạp
   (cyclomatic ≤ 10 / cognitive ≤ 15) ngay trong gạch đầu dòng đó — sàn là phán
   quyết của user, cấm trôi hết vào reference.
5. Mục "Never simplify these away" còn đủ hai phán quyết: log service bật mặc định
   tắt được qua config, và unit test mỗi task red → green không miễn trừ.
"""
import re
import unittest
from pathlib import Path

from helper import ROOT

CHUNG = Path(ROOT) / "skills" / "tdq-build" / "references" / "rules" / "chung.md"
SKILL = Path(ROOT) / "skills" / "tdq-build" / "SKILL.md"

MO = "<!-- luat-gon:bat-dau -->"
DONG = "<!-- luat-gon:ket-thuc -->"


def _than_luat(text):
    """Trả về khối giữa cặp marker luat-gon; chuỗi rỗng nếu thiếu marker."""
    if text.count(MO) != 1 or text.count(DONG) != 1:
        return ""
    dau = text.index(MO) + len(MO)
    cuoi = text.index(DONG)
    return text[dau:cuoi] if cuoi > dau else ""


TIEU_DE_THANG = "### The ladder — stop at the first rung that holds"


def _bac_thang(khoi):
    """Số bậc ở cột đầu mỗi dòng bảng thang, theo đúng thứ tự xuất hiện.

    Chỉ soi trong mục bảng thang: thân luật còn bảng "Two ordered passes" cũng
    mở đầu dòng bằng `| 1 |`, đếm lẫn vào là đếm sai.
    """
    if TIEU_DE_THANG not in khoi:
        return []
    muc = khoi[khoi.index(TIEU_DE_THANG) + len(TIEU_DE_THANG):]
    ke_tiep = muc.find("\n### ")
    if ke_tiep != -1:
        muc = muc[:ke_tiep]
    return re.findall(r"^\|\s*(\d+)\s*\|", muc, re.MULTILINE)


class ThanLuat(unittest.TestCase):
    def test_cap_marker(self):
        self.assertTrue(CHUNG.is_file(), f"Chưa có {CHUNG}")
        text = CHUNG.read_text(encoding="utf-8")
        self.assertEqual(text.count(MO), 1, f"{MO} phải có đúng 1 lần trong chung.md")
        self.assertEqual(text.count(DONG), 1, f"{DONG} phải có đúng 1 lần trong chung.md")
        self.assertLess(text.index(MO), text.index(DONG), "marker mở phải đứng trước marker đóng")
        self.assertTrue(_than_luat(text).strip(), "khối giữa cặp marker không được rỗng")

    def test_bay_bac(self):
        khoi = _than_luat(CHUNG.read_text(encoding="utf-8"))
        self.assertIn(TIEU_DE_THANG, khoi,
                      f"thân luật thiếu mục bảng thang '{TIEU_DE_THANG}'")
        bac = _bac_thang(khoi)
        self.assertEqual(len(bac), 7, f"bảng thang phải có đúng 7 bậc, đang có {len(bac)}")
        self.assertEqual(bac, [str(i) for i in range(1, 8)],
                         "7 bậc phải đứng đúng thứ tự 1..7, không rớt không trùng")

    def test_mon_8(self):
        """Món 8 phải nằm TRONG thân luật, so theo lời luật chứ không theo số dòng."""
        khoi = _than_luat(CHUNG.read_text(encoding="utf-8")).lower()
        for loi in (
            "make it run first, refactor after",
            "step 1 is code that runs",
            "refactor only once the feature works",
        ):
            with self.subTest(loi=loi):
                self.assertIn(loi, khoi, f"thân luật thiếu lời món 8: '{loi}'")

    def test_khong_the_xoa_bot(self):
        """Mục 'Never simplify these away' giữ đủ 2 phán quyết của user."""
        khoi = _than_luat(CHUNG.read_text(encoding="utf-8"))
        self.assertIn("Never simplify these away", khoi,
                      "thân luật thiếu mục 'Never simplify these away'")
        thap = " ".join(khoi.lower().split())
        for loi in (
            "logging on by default",
            "switchable off through config",
            "red → green. no exemption",
        ):
            with self.subTest(loi=loi):
                self.assertIn(loi, thap, f"mục không-được-xoá thiếu phán quyết: '{loi}'")


class BayBacTuChoiBangSai(unittest.TestCase):
    """Chứng minh phép so 7 bậc có cắn: bảng thiếu bậc / trùng bậc phải khác 1..7."""

    DU = [str(i) for i in range(1, 8)]

    def test_bang_sai_bi_tu_choi(self):
        khung = (
            f"{MO}\n\n{TIEU_DE_THANG}\n\n"
            "| Rung | Question | When it holds |\n|---|---|---|\n"
            "%s\n" f"{DONG}\n"
        )
        cac_ca = {
            "thieu_bac_5": [1, 2, 3, 4, 6, 7],
            "trung_bac_2": [1, 2, 2, 3, 4, 5, 6],
            "sai_thu_tu": [1, 2, 3, 4, 5, 7, 6],
        }
        for ten, bac in cac_ca.items():
            with self.subTest(ca=ten):
                gia = khung % "\n".join(f"| {i} | q | w |" for i in bac)
                self.assertNotEqual(_bac_thang(_than_luat(gia)), self.DU,
                                    f"bảng thang sai ({ten}) mà vẫn lọt qua phép so 1..7")

    def test_thieu_marker_thi_khoi_rong(self):
        self.assertEqual(_than_luat("### The ladder\n| 1 | q | w |\n"), "",
                         "không có cặp marker thì phải coi như chưa có thân luật")
        self.assertEqual(_than_luat(f"{MO}\na\n{DONG}\nb\n{MO}\nc\n{DONG}\n"), "",
                         "marker lặp 2 lần thì phải đỏ, không được đoán khối nào là thật")


class CauLuatTangMot(unittest.TestCase):
    def test_o_than_skill_khong_o_reference(self):
        """Hai câu luật tầng 1–2 + sàn phức tạp phải nằm trong thân SKILL.md."""
        self.assertTrue(SKILL.is_file(), f"Chưa có {SKILL}")
        text = SKILL.read_text(encoding="utf-8")
        for dau_dong in (
            "- **Build less than asked: climb the ladder.**",
            "- **Make it run first, refactor after.**",
        ):
            with self.subTest(cau=dau_dong):
                self.assertIn(dau_dong, text,
                              f"SKILL.md thiếu câu luật tầng 1-2: '{dau_dong}'")
        # Sàn phức tạp phải nằm ngay trong gạch đầu dòng "Build less than asked",
        # không chỉ ở đâu đó trong file: cắt đúng bullet đó rồi mới soi.
        dau = text.index("- **Build less than asked: climb the ladder.**")
        ke_tiep = text.index("\n- **", dau + 1)
        bullet = " ".join(text[dau:ke_tiep].split())
        for nguong in ("cyclomatic ≤ 10", "cognitive ≤ 15"):
            with self.subTest(nguong=nguong):
                self.assertIn(nguong, bullet,
                              f"sàn '{nguong}' phải ở trong bullet luật của SKILL.md")


if __name__ == "__main__":
    unittest.main()
