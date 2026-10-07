"""P3 — khoá luật ưu tiên tìm kiếm: MỘT bản gốc, 5 chỗ móc chỉ mang CON TRỎ.

Luật viết 1 chỗ (`skills/tdq-setup/references/uu-tien-tim-kiem.md`), 5 phase trỏ về đó.

2026-10-02 — đổi cách khoá, và lý do là số đo. Bản cũ bắt 5 chỗ móc chép NGUYÊN VĂN câu luật rồi
so từng chữ; `doc_dup.py` đo ra 6 bản của cùng một câu tốn **1.125 token**, và 5 trong 6 bản đó
không mang thêm thông tin nào. Nay mỗi chỗ móc mang một con trỏ ba dòng, còn chính câu luật chỉ
tồn tại một lần. Bất biến cần giữ KHÔNG đổi: mọi phase phải chỉ về cùng một nguồn, và nguồn đó
phải thực sự có câu luật. Mất một trong hai thì mỗi phase lại đọc một thứ tự tìm kiếm khác nhau.
"""
import os
import re
import unittest

from helper import ROOT

GOC = os.path.join(ROOT, "skills", "tdq-setup", "references", "uu-tien-tim-kiem.md")
GOC_REL = "skills/tdq-setup/references/uu-tien-tim-kiem.md"
# File em giữ phần CHI TIẾT, trong đó có §6. Luật không rời skill khi nó sang file em — nên lưới
# phải đi theo nó, không được tháo. Bản 2026-10-02 đầu tiên đã TÁO: bốn phép kiểm của §6 bị xoá
# thay vì trỏ lại, và §6 là nơi duy nhất soul.md nguyên tắc 3 (đủ ba mục) được kiểm bằng máy.
EM = os.path.join(ROOT, "skills", "tdq-setup", "references", "uu-tien-tim-kiem-chi-tiet.md")

# 5 chỗ móc — đúng bảng §5 của file luật gốc.
CHO_MOC = [
    os.path.join(ROOT, "skills", "tdq-intake", "SKILL.md"),
    os.path.join(ROOT, "skills", "tdq-intake", "references", "analyze-full.md"),
    os.path.join(ROOT, "skills", "tdq-spec", "SKILL.md"),
    os.path.join(ROOT, "skills", "tdq-plan", "SKILL.md"),
    os.path.join(ROOT, "skills", "tdq-build", "SKILL.md"),
]

CAU_LUAT = "Đối tượng tìm là ký hiệu code"


def doc(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def gon(text):
    text = re.sub(r"(?m)^\s*>\s?", " ", text)
    return re.sub(r"\s+", " ", text).strip()


class NguonDuyNhat(unittest.TestCase):
    def test_cau_luat_chi_ton_tai_mot_lan_trong_skills(self):
        dem = sum(doc(os.path.join(goc, f)).count(CAU_LUAT)
                  for goc, _, tep in os.walk(os.path.join(ROOT, "skills"))
                  for f in tep if f.endswith(".md"))
        self.assertEqual(dem, 1, "câu luật phải tồn tại ĐÚNG một lần trong skills/")

    def test_ban_goc_mang_cau_luat(self):
        than = gon(doc(GOC))
        self.assertIn(gon(CAU_LUAT), than)
        for tang in ("mcp__lsp__*", "grep", "graphify"):
            self.assertIn(tang, than, f"câu luật gốc thiếu tầng {tang}")


class MoiChoMocDeuTroVeNguon(unittest.TestCase):
    def test_du_nam_cho_moc_deu_tro_ve_dung_file_goc(self):
        for duong in CHO_MOC:
            with self.subTest(cho=os.path.relpath(duong, ROOT)):
                self.assertIn(GOC_REL, doc(duong),
                              "chỗ móc phải trỏ về file luật gốc bằng đường dẫn đầy đủ")

    def test_cho_moc_noi_ro_day_la_luat_bat_buoc(self):
        """Một con trỏ suông thì agent coi là tài liệu tham khảo rồi bỏ qua."""
        for duong in CHO_MOC:
            with self.subTest(cho=os.path.relpath(duong, ROOT)):
                self.assertIn("BẮT BUỘC", doc(duong))

    def test_cho_moc_khong_chep_lai_cau_luat(self):
        for duong in CHO_MOC:
            with self.subTest(cho=os.path.relpath(duong, ROOT)):
                self.assertNotIn(CAU_LUAT, doc(duong),
                                 "chỗ móc chỉ được TRỎ, không được chép lại câu luật")


class BonTangVanDuMatTrongLuat(unittest.TestCase):
    def test_luat_goc_co_bang_phan_tuyen_theo_loai_truy_van(self):
        than = doc(GOC)
        self.assertIn("## 1.", than)
        self.assertIn("## 2.", than)


class LuatKhongMoFileTruoc(unittest.TestCase):
    """§6 — màn khởi động làm `find_references` TỆ đi, không phải tốt lên.

    Đo trên repo này: hỏi thẳng ra 6 file; sau khi mở 3 caller còn 4 file; sau khi mở cả 8 file
    grep nêu tên thì còn 1. Câu trả lời đã tệ đi mà không kèm lỗi, cũng không kèm cảnh báo — nên
    luật phải được viết ra chứ không để tuỳ cảm nhận. Từ 2026-10-02 luật này ở file em.
    """

    def setUp(self):
        self.text = doc(EM)
        self.muc6 = self.text.split("## 6.", 1)[1]

    def test_co_muc_luat(self):
        self.assertIn("Never open documents before asking `find_references`", self.text)

    def test_du_ba_muc_theo_soul_nguyen_tac_3(self):
        """Một luật mà model yếu theo được thì cần đủ ba phần, không chỉ phán quyết."""
        for phan in ("### When it applies", "### What to do", "### Self-check"):
            with self.subTest(phan=phan):
                self.assertIn(phan, self.muc6)

    def test_mang_so_do_chu_khong_chi_lenh(self):
        """Luật không có số đo đứng sau là luật đầu tiên bị ai đó nói cho qua."""
        for so in ("6", "4", "1"):
            self.assertIn(f"| {so} |", self.muc6.replace("**", ""))

    def test_cam_open_document_lam_buoc_chuan_bi(self):
        self.assertIn("Never call `open_document` as preparation", self.muc6)

    def test_em_duoc_tro_tu_skill_md_cua_chinh_no(self):
        """Một tầng: file em phải được trỏ từ `SKILL.md`, nếu không nó là tầng 2."""
        skill = doc(os.path.join(ROOT, "skills", "tdq-setup", "SKILL.md"))
        self.assertIn("uu-tien-tim-kiem-chi-tiet.md", skill)


class BaLopGanDungLoaiTruyVan(unittest.TestCase):
    """Ánh xạ lớp ↔ loại truy vấn, thứ KHÔNG được trôi khi câu luật được viết lại.

    Số đo ở `docs/tdq/report/2026-09-03-0017-them-pyrightconfig-do-lai.md`: quan hệ thì LSP phủ
    15/15 còn grep đúng 67%; tên chính xác thì grep nhanh gấp bội mà vẫn đủ; khái niệm mơ hồ thì
    LSP xếp đích hạng 13/62.
    """

    def setUp(self):
        self.cau = gon(doc(GOC))

    def test_du_ba_lop_moi_lop_gan_mot_loai_truy_van(self):
        for lop in ("mcp__lsp__", "graphify", "grep"):
            self.assertIn(lop, self.cau, f"câu luật gốc thiếu lớp {lop}")
        for loai, lop in (("quan hệ", "mcp__lsp__"), ("tên chính xác", "grep"),
                          ("khái niệm mơ hồ", "graphify")):
            i = self.cau.index(loai)
            self.assertIn(lop, self.cau[i:i + 80],
                          f"loại truy vấn '{loai}' không gắn với lớp {lop}")

    def test_khong_con_bat_buoc_goi_song_song(self):
        """Ràng buộc cũ "BẮT BUỘC gọi song song ở mọi truy vấn ký hiệu" đã bị bãi bỏ."""
        self.assertNotIn("BẮT BUỘC gọi song song", self.cau)


if __name__ == "__main__":
    unittest.main()
