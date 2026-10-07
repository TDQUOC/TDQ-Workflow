"""Luật tìm kiếm phải là luật BA tầng (LSP, grep, graphify — lumen gỡ ở 0.58.0), và mọi số đo
trong đó phải ghi kèm tên repo.

Hai lỗi đã xảy ra thật, nên hai lỗi đó bị khoá ở đây:

1. graphify xuất hiện trong 6 file skill như một bước sổ sách, mà KHÔNG có một dòng nào trong
   luật tìm kiếm — doctrine ba tầng trong khi repo chạy bốn công cụ.
2. Mọi số đo của luật đều đo trên chính repo này, một repo nặng tài liệu. Đo lại trên một repo
   code thật thì kết luận về graphify đảo ngược (12% so với 54% cạnh xuyên file). Số đo không
   kèm tên repo là số đo vô nghĩa với người đọc sau.

Và một câu phải BIẾN MẤT: luật từng khẳng định không cần bước reindex nào — chính câu đó là lý do
không ai cắm reindex vào kết turn suốt nhiều tháng.
"""
import io
import os
import unittest

from helper import ROOT

LUAT = os.path.join(ROOT, "skills", "tdq-setup", "references", "uu-tien-tim-kiem.md")


def _doc():
    with io.open(LUAT, encoding="utf-8") as fh:
        return fh.read()


class LuatBonTang(unittest.TestCase):
    def test_graphify_la_mot_tang_trong_luat(self):
        self.assertIn("graphify", _doc(), "công cụ thứ tư phải có mặt trong chính luật tìm kiếm")

    def test_du_ca_ba_ten_cong_cu(self):
        noi_dung = _doc()
        for ten in ("grep", "graphify", "agent-lsp"):
            self.assertIn(ten, noi_dung, f"thiếu tầng {ten}")

    def test_khong_tang_nao_con_tro_toi_lumen(self):
        """0.58.0: bảng loại câu hỏi và bảng phụ thuộc không được còn hàng nào dẫn tới lumen."""
        for dong in _doc().splitlines():
            if dong.startswith("|"):
                self.assertNotIn("**lumen**", dong, dong)
                self.assertFalse(dong.startswith("| lumen"), dong)

    def test_co_bang_phu_thuoc_runtime(self):
        """Mỗi tầng chết thì rơi xuống đâu — thứ luật cũ không có, và là lý do hỏng âm thầm.

        File này viết TIẾNG ANH theo luật ngôn ngữ 3 tầng (`docs/kien-truc.md`, 2026-08-22): luật
        trong `skills/` là tầng 1. Nên phép kiểm phải hỏi bằng từ tiếng Anh, không phải tiếng Việt.
        """
        noi_dung = _doc().lower()
        self.assertIn("runtime dependency", noi_dung)
        self.assertIn("falls back to", noi_dung)

    def test_moi_so_do_ghi_kem_ten_repo(self):
        """Hai repo đã đo phải được gọi tên, để người đọc sau biết số đo nói về cái gì."""
        noi_dung = _doc()
        self.assertIn("TDQ-Workflow", noi_dung)
        self.assertIn("claudecodeui", noi_dung)

    def test_khong_con_cau_khang_dinh_khoi_reindex(self):
        noi_dung = _doc()
        self.assertNotIn("no separate reindex step", noi_dung,
                         "câu này là lý do không ai dựng lại index suốt nhiều tháng")

    def test_noi_ro_do_thi_dung_lai_o_buoc_ket_turn(self):
        self.assertIn("tdq_finish", _doc(), "luật phải chỉ ra AI dựng lại đồ thị và dựng lúc nào")


if __name__ == "__main__":
    unittest.main()
