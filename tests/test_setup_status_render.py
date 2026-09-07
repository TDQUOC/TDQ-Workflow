"""Unit test cho scripts/setup_status_render.py — bộ kết xuất HTML của trang trạng thái.

Bộ kết xuất là hàm thuần: vào một dict, ra một chuỗi. Nhờ vậy mọi ca ở đây chạy được
trên máy trắng — không cần agent-lsp, lumen, ollama hay graphify — và đó chính là điều
ca `test_khong_can_cong_cu_ngoai` đóng đinh.
"""
import os
import re
import sys
import unittest
from unittest import mock

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import setup_status_render  # noqa: E402


def du_lieu_toi_thieu(**ghi_de):
    """Khung dữ liệu đủ 4 khối, giá trị tối thiểu — mỗi ca chỉ ghi đè phần nó quan tâm."""
    goc = {
        "meta": {"sinh_luc": "2026-09-07T10:00:00+07:00", "project": "/du/an",
                 "python": "3.13.0"},
        "workflow": {"skill": [], "hook": [], "do_hook": [], "state": {}, "bac": [],
                     "ghi_chu_builtin": "Skill built-in của Claude Code nằm trong binary.",
                     "loi": {}},
        "dependency": [],
        "chi_tiet": {"lumen": {"model": "", "endpoint": [], "config": "", "chi_tiet": ""},
                     "lsp": {"may": [], "so_khai_bao": 0, "so_song": 0, "chet": [],
                             "chi_tiet": ""}},
        "mcp": {"server": [], "chi_tiet": ""},
    }
    goc.update(ghi_de)
    return goc


class TuChua(unittest.TestCase):
    """Trang phải mở được khi rút mạng: không tài nguyên ngoài nào."""

    def test_khong_tai_nguyen_ngoai(self):
        html = setup_status_render.render(du_lieu_toi_thieu())
        ngoai = re.findall(r'(?:src|href)\s*=\s*["\']https?://', html)
        self.assertEqual(ngoai, [], f"còn {len(ngoai)} tài nguyên ngoài")

    def test_co_khung_html_va_css_noi_tuyen(self):
        html = setup_status_render.render(du_lieu_toi_thieu())
        self.assertTrue(html.lstrip().lower().startswith("<!doctype html>"))
        self.assertIn("<style>", html)
        self.assertNotIn("<script src=", html)

    def test_du_bon_khoi(self):
        html = setup_status_render.render(du_lieu_toi_thieu())
        khoi = re.findall(r'data-khoi="([a-z-]+)"', html)
        self.assertEqual(sorted(khoi), ["chi-tiet", "dependency", "mcp", "workflow"])

    def test_khong_can_cong_cu_ngoai(self):
        """Gọi render với PATH rỗng: không hàm nào được đụng tới binary bên ngoài."""
        goc = os.environ.get("PATH", "")
        os.environ["PATH"] = ""
        try:
            html = setup_status_render.render(du_lieu_toi_thieu())
        finally:
            os.environ["PATH"] = goc
        self.assertIn("<html", html)


class SaiKieu(unittest.TestCase):
    """Nguồn hỏng thì trả về kiểu lạ; trang phải ghi \"không đọc được\", không được ném."""

    def test_khoi_sai_kieu_van_ra_trang(self):
        html = setup_status_render.render(
            {"meta": {}, "workflow": 123, "dependency": "hỏng", "chi_tiet": [], "mcp": 7})
        self.assertIn("không đọc được", html)
        self.assertEqual(html.count('data-khoi='), len(setup_status_render.KHOI))

    def test_du_lieu_khong_phai_dict(self):
        for xau in (None, [], "x", 5):
            self.assertIn("<!doctype html>", setup_status_render.render(xau))


class ThemKhoiLaMotDong(unittest.TestCase):
    """OCP: thêm một khối cho trang phải là thêm ĐÚNG một dòng dữ liệu, không mở thân render()."""

    def test_moi_muc_khoi_co_ham_dung(self):
        for muc in setup_status_render.KHOI:
            self.assertEqual(len(muc), 4, muc)
            self.assertTrue(callable(muc[3]), muc[0])

    def test_them_mot_dong_la_them_mot_section(self):
        them = ("thu-nghiem", "5 · Khối thử", "khong_co", lambda _: "<p>xin chào</p>")
        with mock.patch.object(setup_status_render, "KHOI",
                               setup_status_render.KHOI + (them,)):
            html = setup_status_render.render(du_lieu_toi_thieu())
        self.assertIn('data-khoi="thu-nghiem"', html)
        self.assertIn("xin chào", html)
        self.assertEqual(html.count("data-khoi="), 5)


class ThoatKyTu(unittest.TestCase):
    """Dữ liệu đến từ output của lệnh ngoài — không bao giờ được chèn thẳng làm thẻ."""

    def test_thoat_dau_ngoac_nhon(self):
        du_lieu = du_lieu_toi_thieu()
        du_lieu["mcp"]["server"] = [
            {"ten": "<script>alert(1)</script>", "dich": "a & b",
             "trang_thai": "✔ Connected", "noi_duoc": True}]
        html = setup_status_render.render(du_lieu)
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("a &amp; b", html)


class OTrong(unittest.TestCase):
    """Nguồn không đọc được thì nói thẳng, tuyệt đối không điền giá trị đoán."""

    def test_lumen_thieu_config_hien_ly_do(self):
        du_lieu = du_lieu_toi_thieu()
        du_lieu["chi_tiet"]["lumen"] = {"model": "qwen3-embedding:0.6b", "endpoint": [],
                                        "config": "/x.yaml",
                                        "chi_tiet": "không đọc được /x.yaml: thiếu file"}
        html = setup_status_render.render(du_lieu)
        self.assertIn("không đọc được /x.yaml", html)
        self.assertIn("qwen3-embedding:0.6b", html)

    def test_khoi_rong_van_hien_khong_doc_duoc(self):
        html = setup_status_render.render(du_lieu_toi_thieu())
        self.assertIn("không đọc được", html)

    def test_loi_cua_nguon_workflow_duoc_hien_nguyen_van(self):
        du_lieu = du_lieu_toi_thieu()
        du_lieu["workflow"]["loi"] = {"bac": "RuntimeError: agent-lsp biến mất"}
        html = setup_status_render.render(du_lieu)
        self.assertIn("agent-lsp biến mất", html)


class NoiDungThat(unittest.TestCase):
    """Số liệu đưa vào phải xuất hiện đúng trên trang."""

    def test_bang_dependency(self):
        du_lieu = du_lieu_toi_thieu(dependency=[
            {"ten": "graphify", "co": True, "ban": "graphify 0.9.55",
             "duong_dan": "/bin/graphify", "chi_tiet": "", "goi_y": ""},
            {"ten": "lumen", "co": False, "ban": "chưa cài", "duong_dan": "",
             "chi_tiet": "chưa cài", "goi_y": "cài lumen"},
        ])
        html = setup_status_render.render(du_lieu)
        self.assertIn("graphify 0.9.55", html)
        self.assertIn("cài lumen", html)

    def test_bay_bac_va_state(self):
        du_lieu = du_lieu_toi_thieu()
        du_lieu["workflow"]["bac"] = [
            {"so": 1, "ten": "binary agent-lsp", "nhan": "ĐẠT", "chi_tiet": "0.19.2",
             "lenh_cai": ""}]
        du_lieu["workflow"]["state"] = {"active_request": "abc", "lane": "full",
                                        "phase": "implement"}
        html = setup_status_render.render(du_lieu)
        self.assertIn("binary agent-lsp", html)
        self.assertIn("abc", html)
        self.assertIn("implement", html)

    def test_do_toc_do_hook(self):
        du_lieu = du_lieu_toi_thieu()
        du_lieu["workflow"]["do_hook"] = [
            ["hooks/scripts/stop_gate.py", "kết thúc turn", "24.9ms", "23.0ms", "26.1ms"]]
        html = setup_status_render.render(du_lieu)
        self.assertIn("stop_gate.py", html)
        self.assertIn("24.9ms", html)


class KhaiBaoVaThucNhan(unittest.TestCase):
    """Trang phải chỉ đúng cái chết, không gộp thành một con số cho xong."""

    def du_lieu_14_khai(self, so_chet=1):
        lang = ["c", "cpp", "json", "python", "csharp", "dockerfile", "go", "javascript",
                "typescript", "yaml", "html", "css", "markdown", "eslint"]
        may = [{"lang": t, "binary": f"{t}-server", "trang_thai": "ok"} for t in lang]
        for muc in may[-so_chet:] if so_chet else []:
            muc["trang_thai"] = "failed"
        chet = [m for m in may if m["trang_thai"] != "ok"]
        du_lieu = du_lieu_toi_thieu()
        du_lieu["chi_tiet"]["lsp"] = {"may": may, "so_khai_bao": len(may),
                                      "so_song": len(may) - len(chet), "chet": chet,
                                      "chi_tiet": ""}
        return du_lieu

    def test_khai_14_song_13_thi_noi_ro_ca_hai_so(self):
        html = setup_status_render.render(self.du_lieu_14_khai(1))
        self.assertIn("<b>14</b>", html)
        self.assertRegex(html, r'class="thieu">13<')

    def test_chi_dung_ten_server_chet(self):
        html = setup_status_render.render(self.du_lieu_14_khai(1))
        self.assertIn("Không nhận được", html)
        self.assertIn("eslint", html)
        khuc = html.split("Không nhận được", 1)[1].split("</p>", 1)[0]
        self.assertNotIn("python", khuc)
        self.assertNotIn("clangd", khuc)

    def test_song_du_thi_khong_co_dong_bao_chet(self):
        html = setup_status_render.render(self.du_lieu_14_khai(0))
        self.assertNotIn("Không nhận được", html)
        self.assertRegex(html, r'class="dat">14<')

    def test_noi_ro_dong_error_luc_dong_khong_tinh_la_chet(self):
        """Người đọc tự chạy doctor sẽ thấy dòng [error] — trang phải giải thích trước."""
        html = setup_status_render.render(self.du_lieu_14_khai(0))
        self.assertEqual(html.count("exited with error"), 1)
        self.assertIn("không tính là chết", html)

    def test_khong_khai_bao_server_nao_thi_khong_co_ghi_chu(self):
        html = setup_status_render.render(du_lieu_toi_thieu())
        self.assertNotIn("exited with error", html)

    def test_dung_mot_dong_ve_skill_builtin(self):
        du_lieu = du_lieu_toi_thieu()
        du_lieu["workflow"]["ghi_chu_builtin"] = (
            "Bảng này chỉ liệt kê skill có trên đĩa. Các skill built-in của Claude Code "
            "nằm trong chính binary nên script không đọc được.")
        html = setup_status_render.render(du_lieu)
        self.assertEqual(html.count("skill built-in"), 1)


if __name__ == "__main__":
    unittest.main()
