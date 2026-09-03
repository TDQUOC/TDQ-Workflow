"""Giữ luật UI/UX trong `plugin-routing.md` và bản vá kiểm kê năng lực khỏi mục.

Request 2026-09-03-1949: thêm một dòng routing + một khối luật ba tầng nói rõ
`ui-ux-pro-max` là BỘ ĐỀ XUẤT ĐỂ TRA (không phải bước bắt buộc chạy), ghép được với
`frontend-design`/`figma`/`chrome-devtools-mcp`, loại trừ Unity/game; và vá
`skill_inventory.py` để nó nhìn thấy plugin để skill ở `.claude/skills/`.

Test ĐỎ ở đây nghĩa là văn bản luật hoặc bản vá đã bị sửa lệch, không nhất thiết là mã hỏng.
"""
import json
import os
import re
import sys
import tempfile
import unittest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "scripts"))

DUONG_LUAT = os.path.join(GOC, "skills", "tdq-conventions", "references", "plugin-routing.md")
TIEU_DE_KHOI = "## UI/UX — three layers"
# Từ ra lệnh tuyệt đối: khối này là sổ tra cứu, không được viết như một bước bắt buộc.
TU_MENH_LENH = ("MUST", "BẮT BUỘC", "mandatory", "always load", "never skip")


def doc_luat():
    with open(DUONG_LUAT, encoding="utf-8") as f:
        return f.read()


def lay_khoi(van_ban):
    """Cắt đúng khối luật UI/UX: từ tiêu đề của nó đến tiêu đề `##` kế tiếp."""
    vi_tri = van_ban.find(TIEU_DE_KHOI)
    if vi_tri < 0:
        return ""
    con_lai = van_ban[vi_tri + len(TIEU_DE_KHOI):]
    ke_tiep = re.search(r"^## ", con_lai, re.MULTILINE)
    return con_lai[: ke_tiep.start()] if ke_tiep else con_lai


def lay_bang_routing(van_ban):
    """Các dòng của bảng routing — chỉ dòng bắt đầu bằng `|`."""
    khuc = van_ban.split("## Routing table", 1)
    if len(khuc) < 2:
        return []
    sau = khuc[1].split("\n## ", 1)[0]
    return [d for d in sau.splitlines() if d.startswith("|")]


class LuatUiUx(unittest.TestCase):
    """Bảy điều kiện của DoD 1–7."""

    def setUp(self):
        self.van_ban = doc_luat()
        self.khoi = lay_khoi(self.van_ban)

    def test_routing_co_dong_uiux(self):
        dong = [d for d in lay_bang_routing(self.van_ban) if "ui-ux-pro-max" in d]
        self.assertEqual(len(dong), 1, "bảng routing phải có đúng một dòng cho ui-ux-pro-max")
        self.assertNotIn("ui-ux-pro-max", lay_bang_routing(self.van_ban)[0],
                         "dòng tiêu đề bảng không được chứa tên plugin")

    def test_ba_tang(self):
        self.assertTrue(self.khoi, "phải có khối luật " + TIEU_DE_KHOI)
        so_muc = re.findall(r"^\d\. ", self.khoi, re.MULTILINE)
        self.assertGreaterEqual(len(so_muc), 3, "khối luật phải nêu đủ ba tầng, đánh số")
        self.assertIn("chrome-devtools-mcp", self.khoi,
                      "tầng kiểm chứng phải trỏ sang chrome-devtools-mcp")

    def test_tang_giua(self):
        self.assertIn("ONLY layer", self.khoi,
                      "phải nói rõ tầng quyết định thiết kế là tầng DUY NHẤT ui-ux-pro-max phủ")

    def test_khong_menh_lenh(self):
        thay = [t for t in TU_MENH_LENH if t in self.khoi]
        self.assertEqual(thay, [], f"khối luật là sổ tra cứu, không được ra lệnh: {thay}")
        self.assertIn("CATALOGUE TO CONSULT", self.khoi, "phải mang nghĩa tra cứu/đối chiếu")

    def test_muc_rang_buoc(self):
        self.assertIn("may be skipped", self.khoi)
        self.assertIn("one line saying why", self.khoi)

    def test_ghep_duoc(self):
        for ten in ("frontend-design", "figma", "chrome-devtools-mcp"):
            self.assertIn(ten, self.khoi, f"thiếu plugin ghép được: {ten}")
        self.assertIn("Combines with, never exclusive", self.khoi,
                      "phải nói rõ là ghép được, không loại trừ nhau")

    def test_loai_tru_unity(self):
        self.assertIn("Not for Unity", self.khoi)


class KiemKeThayPluginDatSkillTrongClaude(unittest.TestCase):
    """Bản vá `skill_inventory.py`: thấy cả `skills/` lẫn `.claude/skills/`."""

    def dung_plugin(self, goc, ten, duong_con):
        """Tạo một plugin giả; `duong_con` rỗng nghĩa là plugin không có thư mục skill nào."""
        thu_muc = os.path.join(goc, ten)
        os.makedirs(thu_muc, exist_ok=True)
        if duong_con:
            skills = os.path.join(thu_muc, *duong_con.split("/"))
            os.makedirs(os.path.join(skills, "mot-skill"))
            with open(os.path.join(skills, "mot-skill", "SKILL.md"), "w", encoding="utf-8") as f:
                f.write("---\nname: mot-skill\ndescription: thu\n---\n")
        return thu_muc

    def dung_may(self, tam, plugin):
        """Dựng cây `home` + `project` giả đúng khuôn mà `_plugin_skill_dirs` đọc."""
        home = os.path.join(tam, "home")
        project = os.path.join(tam, "project")
        os.makedirs(os.path.join(home, ".claude", "plugins"))
        os.makedirs(os.path.join(project, ".claude"))
        bat = {f"{ten}@cho": True for ten in plugin}
        with open(os.path.join(home, ".claude", "settings.json"), "w", encoding="utf-8") as f:
            json.dump({"enabledPlugins": bat}, f)
        da_cai = {f"{ten}@cho": [{"installPath": duong}] for ten, duong in plugin.items()}
        duong_cai = os.path.join(home, ".claude", "plugins", "installed_plugins.json")
        with open(duong_cai, "w", encoding="utf-8") as f:
            json.dump({"plugins": da_cai}, f)
        return home, project

    def quet(self, home, project):
        import skill_inventory
        return skill_inventory._plugin_skill_dirs(home, project)

    def test_thay_ca_hai_kieu_bo_tri(self):
        with tempfile.TemporaryDirectory() as tam:
            goc = os.path.join(tam, "cai")
            os.makedirs(goc)
            plugin = {
                "kieu-cu": self.dung_plugin(goc, "kieu-cu", "skills"),
                "kieu-claude": self.dung_plugin(goc, "kieu-claude", ".claude/skills"),
            }
            home, project = self.dung_may(tam, plugin)
            ten = {t for t, _ in self.quet(home, project)}
            self.assertEqual(ten, {"kieu-cu", "kieu-claude"})

    def test_khong_phinh_bang(self):
        """Plugin không có thư mục skill nào thì không được sinh dòng rác."""
        with tempfile.TemporaryDirectory() as tam:
            goc = os.path.join(tam, "cai")
            os.makedirs(goc)
            plugin = {"rong": self.dung_plugin(goc, "rong", "")}
            home, project = self.dung_may(tam, plugin)
            self.assertEqual(self.quet(home, project), [])

    def test_uu_tien_thu_muc_skills_truoc(self):
        """Có cả hai thì lấy `skills/` — giữ nguyên hành vi cũ."""
        with tempfile.TemporaryDirectory() as tam:
            goc = os.path.join(tam, "cai")
            os.makedirs(goc)
            ca_hai = self.dung_plugin(goc, "ca-hai", "skills")
            os.makedirs(os.path.join(ca_hai, ".claude", "skills", "khac"))
            home, project = self.dung_may(tam, {"ca-hai": ca_hai})
            duong = [d for _, d in self.quet(home, project)]
            self.assertEqual(duong, [os.path.join(ca_hai, "skills")])


class LuatXuongBundle(unittest.TestCase):
    """Ai quên dựng lại bundle thì test này đỏ."""

    def test_bundle_mang_luat_uiux(self):
        duong = os.path.join(GOC, "portable_claude", ".claude", "skills", "tdq-conventions",
                             "references", "plugin-routing.md")
        self.assertTrue(os.path.isfile(duong), "bundle portable_claude thiếu file luật")
        with open(duong, encoding="utf-8") as f:
            khoi = lay_khoi(f.read())
        self.assertIn("ui-ux-pro-max", khoi, "bundle chưa có luật mới — dựng lại đi")


if __name__ == "__main__":
    unittest.main()
