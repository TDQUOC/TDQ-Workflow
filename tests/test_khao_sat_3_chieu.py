"""Unit tests for Triangulation Code Exploration and Refactor Intent Preservation (T5.1).

Covers:
1. Free Grep in exploration phases (analyze, quick_analyze, spec, no_state, idle).
2. Strict 3-tier discipline maintained during implement phase.
3. Triangulation search observer (tam_giac_khao_sat helper).
4. Refactor / Clean Architecture invariant exception in chung.md.
5. Before vs After design intent blocks in spec-template.md and plan-template.md.
6. Sync of 3-dimensional search and refactor exception in tdq_setup.py instruction block.
"""
import io
import os
import sys
import unittest

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import search_rules  # noqa: E402
import tdq_setup  # noqa: E402


class TestKhaoSat3Chieu(unittest.TestCase):
    def test_grep_tu_do_trong_cac_pha_khao_sat(self):
        """Trong các phase analyze, quick_analyze, spec: Grep được phép tự do không bị chặn."""
        cac_pha_khao_sat = ["analyze", "quick_analyze", "spec"]
        for pha in cac_pha_khao_sat:
            trang_thai = {
                "phase": pha,
                "so_grep": 15,  # Vượt quá quota 10
                "da_goi_lsp": False,
                "da_khoi_dong_lsp": False,
            }
            pl = search_rules.phan_loai("Grep", {"pattern": "tam_giac_khao_sat"})
            ok, ly_do = search_rules.quyet_dinh(pl, trang_thai)
            self.assertTrue(ok, f"Pha {pha} phải cho phép grep tự do, nhưng nhận: {ly_do}")
            self.assertIn("exploration phase", ly_do.lower())

    def test_grep_kiem_soat_trong_pha_implement(self):
        """Trong phase implement (hoặc khi không ở phase khảo sát): quy tắc 3 tầng chuẩn tiếp tục có hiệu lực."""
        for pha in ["implement", None]:
            # Chưa gọi LSP/Graphify trước mà đã grep symbol lạ -> bị từ chối
            trang_thai_chua_goi = {
                "phase": pha,
                "da_goi_khai_niem": False,
            }
            pl = search_rules.phan_loai("Grep", {"pattern": "some_symbol"})
            ok, ly_do = search_rules.quyet_dinh(pl, trang_thai_chua_goi)
            self.assertFalse(ok, f"Pha {pha} chưa gọi concept phải từ chối: {ly_do}")
            self.assertIn("before any concept query", ly_do.lower())

            # Đã hết cửa sổ và tìm đoán mò -> bị từ chối
            trang_thai_het_cua_so = {
                "phase": pha,
                "da_goi_khai_niem": True,
                "so_lan_tim_tu_lan_goi": 12,
                "cua_so": 10,
            }
            # Regex đoán mò có nhánh hoặc dấu |
            pl_mo = search_rules.phan_loai("Grep", {"pattern": "alpha|beta|gamma"})
            ok_mo, ly_do_mo = search_rules.quyet_dinh(pl_mo, trang_thai_het_cua_so)
            self.assertFalse(ok_mo, f"Pha {pha} hết quota đoán mò phải từ chối: {ly_do_mo}")
            self.assertIn("guess-list search", ly_do_mo.lower())

    def test_tam_giac_khao_sat_phan_loai(self):
        """tam_giac_khao_sat nhận diện đúng đủ 3 chiều Grep, LSP, Graphify."""
        # Trường hợp rỗng
        kq_rong = search_rules.tam_giac_khao_sat([])
        self.assertFalse(kq_rong["du_3_chieu"])
        self.assertEqual(kq_rong["so_grep"], 0)

        # Trường hợp chỉ có grep
        rows_grep = [{"loai": "tim", "nhan": "Grep: some_query"}]
        kq_grep = search_rules.tam_giac_khao_sat(rows_grep)
        self.assertFalse(kq_grep["du_3_chieu"])
        self.assertEqual(kq_grep["so_grep"], 1)

        # Trường hợp đủ cả 3 chiều
        rows_du = [
            {"loai": "tim", "nhan": "Grep: pattern"},
            {"loai": "khai_niem", "nhan": "lsp:find_references"},
            {"loai": "khai_niem", "nhan": "graphify:affected"},
        ]
        kq_du = search_rules.tam_giac_khao_sat(rows_du)
        self.assertTrue(kq_du["du_3_chieu"])
        self.assertTrue(kq_du["co_lsp"])
        self.assertTrue(kq_du["co_graphify"])
        self.assertEqual(kq_du["so_grep"], 1)

    def test_ngoai_le_refactor_trong_chung_md(self):
        """chung.md phải chứa ngoại lệ bảo toàn kiến trúc sạch cho Rung 1 khi người dùng yêu cầu refactor."""
        duong_chung = os.path.join(ROOT, "skills", "tdq-build", "references", "rules", "chung.md")
        with io.open(duong_chung, encoding="utf-8") as f:
            noi_dung = f.read()
        self.assertIn("Chủ đích Refactor & Mở rộng Kiến trúc", noi_dung)
        self.assertIn("Clean Architecture/SOLID", noi_dung)
        self.assertIn("hàm phẳng", noi_dung)

    def test_khoi_truoc_vs_sau_trong_spec_va_plan(self):
        """Cả spec-template.md và plan-template.md phải có bảng so sánh Hiện trạng (Trước) vs Thiết kế mới (Sau)."""
        duong_spec = os.path.join(ROOT, "skills", "tdq-spec", "references", "spec-template.md")
        with io.open(duong_spec, encoding="utf-8") as f:
            spec_nd = f.read()
        self.assertIn("Hiện trạng (Trước)", spec_nd)
        self.assertIn("Thiết kế mới (Sau)", spec_nd)

        duong_plan = os.path.join(ROOT, "skills", "tdq-plan", "references", "plan-template.md")
        with io.open(duong_plan, encoding="utf-8") as f:
            plan_nd = f.read()
        self.assertIn("Hiện trạng (Trước)", plan_nd)
        self.assertIn("Thiết kế mới (Sau)", plan_nd)

    def test_dong_bo_instruction_tdq_setup(self):
        """KHOI_HUONG_DAN trong scripts/tdq_setup.py phải có khảo sát 3 chiều và ngoại lệ refactor."""
        khoi = tdq_setup.khoi_huong_dan()
        self.assertIn("Khảo sát code 3 chiều", khoi)
        self.assertIn("Grep tự do", khoi)
        self.assertIn("Ngoại lệ Refactor & Kiến trúc sạch", khoi)


if __name__ == "__main__":
    unittest.main()
