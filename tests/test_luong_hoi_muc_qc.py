"""Luồng hỏi mức QC — luật nằm trong skill, nên phép kiểm đọc chính file skill.

Vì sao kiểm được bằng máy: câu hỏi mức QC là một BƯỚC BẮT BUỘC của phase `analyze` (lane full)
và của cổng duyệt (lane express). Một bước chỉ sống trong trí nhớ agent là bước sẽ bị bỏ qua vào
lúc bận nhất. Test này khoá đúng ba điều kiện đo được: bước có tồn tại, câu hỏi bày đủ ba mức
`lite|full|ultra` kèm mặc định `full`, và KHÔNG bày `off` ra cho user.

Hai nhóm chạy riêng được bằng `-k`: `deep`, `express`.
"""
import os
import re
import unittest

from helper import ROOT

SKILL_INTAKE = os.path.join(ROOT, "skills", "tdq-intake", "SKILL.md")
ANALYZE = os.path.join(ROOT, "skills", "tdq-intake", "references", "analyze-full.md")
QUICK_LANE = os.path.join(ROOT, "skills", "tdq-intake", "references", "quick-lane.md")
MUC = ("lite", "full", "ultra")


def doc(duong):
    with open(duong, encoding="utf-8") as f:
        return f.read()


def khoi_hoi(van_ban, tu_khoa):
    """Khối ``` chứa câu hỏi in ra cho user — thứ DUY NHẤT user đọc.

    Tách riêng vì luật quanh nó viết tiếng Anh (tầng ngôn ngữ của repo) và có quyền nhắc `off`
    để CẤM bày nó ra; kiểm cả bước thì hai thứ đó lẫn vào nhau.
    """
    for khoi in re.findall(r"```\n(.*?)```", van_ban, re.S):
        if tu_khoa in khoi:
            return khoi
    raise AssertionError(f"không tìm thấy khối câu hỏi chứa {tu_khoa!r}")


def buoc_5c(van_ban):
    """Toàn bộ bước 5c, gồm cả phần luật tiếng Anh."""
    return van_ban.split("5c.", 1)[1].split("\n6. **Gate check", 1)[0]


class LaneDeepTest(unittest.TestCase):
    """Lane full: hỏi ở CUỐI phase analyze, ngay trước khi viết spec."""

    def setUp(self):
        self.analyze = doc(ANALYZE)
        self.skill = doc(SKILL_INTAKE)

    def test_deep_co_buoc_hoi_muc_qc(self):
        self.assertIn("muc_qc", self.analyze, "analyze-full.md chưa có bước hỏi mức QC")
        self.assertRegex(self.analyze, r"5c\.", "bước hỏi mức QC phải là bước 5c, sau lộ trình")

    def test_deep_bay_du_ba_muc(self):
        khoi = khoi_hoi(self.analyze, "QC tới mức nào")
        for muc in MUC:
            with self.subTest(muc=muc):
                self.assertIn(muc, khoi, f"câu hỏi thiếu mức {muc}")

    def test_deep_khong_bay_off(self):
        """Quyết định 2026-09-23: `off` là giá trị hợp lệ nhưng không bao giờ được mời."""
        self.assertNotIn("off", khoi_hoi(self.analyze, "QC tới mức nào"),
                         "danh sách hỏi không được bày mức off")

    def test_deep_co_muc_mac_dinh(self):
        """Luật viết tiếng Anh theo tầng ngôn ngữ của repo, nên dò `default is full`."""
        buoc = buoc_5c(self.analyze)
        self.assertRegex(buoc, r"default is `full`", "phải nói rõ im lặng thì rơi về mức nào")
        self.assertIn("(đề xuất): `full`", buoc, "mức đề xuất phải đứng ở A")

    def test_deep_ghi_vao_state_bang_lenh(self):
        self.assertIn("set muc_qc=", buoc_5c(self.analyze),
                      "mức phải được ghi vào state, không chỉ nói miệng")

    def test_deep_skill_nhac_buoc_nay(self):
        self.assertIn("muc_qc", self.skill, "thân skill phải nhắc bước hỏi mức QC")

    def test_deep_buoc_dung_truoc_cong_spec(self):
        """Hỏi SAU khi spec viết xong thì spec §6 đã đóng rồi — sai chỗ."""
        vi_tri_5c = self.analyze.index("5c.")
        vi_tri_gate = self.analyze.index("6. **Gate check")
        self.assertLess(vi_tri_5c, vi_tri_gate)


class LaneExpressTest(unittest.TestCase):
    """Lane express: hỏi tại cổng duyệt SẴN CÓ, không thêm lượt dừng."""

    def setUp(self):
        self.quick = doc(QUICK_LANE)

    def test_express_hoi_muc_qc(self):
        self.assertIn("muc_qc", self.quick, "quick-lane.md chưa có mức QC")

    def test_express_khong_con_co_cu(self):
        self.assertNotIn("--no-qc", self.quick, "cờ --no-qc đã gỡ ngày 2026-09-23")

    def test_express_khong_them_cong_dung(self):
        """Express chỉ có MỘT cổng duyệt. Thêm cổng thứ hai là phá đúng thứ làm nó nhanh."""
        so_cong = len(re.findall(r"STOP", self.quick))
        self.assertLessEqual(so_cong, 3, f"quick-lane có {so_cong} chỗ STOP — kiểm lại")
        self.assertRegex(self.quick, r"(?i)(cùng|same)\s+(khối|block)",
                         "phải nói rõ hỏi mức trong cùng khối với lời mời duyệt")

    def test_express_khong_bay_off(self):
        self.assertNotIn("off", khoi_hoi(self.quick, "QC tới mức nào"),
                         "express cũng không được mời user tắt QC")


if __name__ == "__main__":
    unittest.main()
