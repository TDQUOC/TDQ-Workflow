"""P5 — unit test cho scripts/tdq_lsp.py: 7 bậc của thang chẩn đoán (lumen và vòng đời Ollama gỡ ở 0.58.0).

Script này quyết định workflow có được dùng LSP hay không, và nó có một lời hứa cứng:
KHÔNG bao giờ tự cài, KHÔNG bao giờ sửa file plugin khác.
Hai lời hứa đó chỉ là chữ nếu không có test đóng đinh, nên mỗi lời hứa có một ca riêng.

Mọi ca đều vá (`patch`) lớp chạm máy thật — `shutil.which`, socket probe, subprocess —
để suite chạy được trên máy chưa cài gì mà vẫn kiểm đúng nhánh logic.
"""
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_lsp  # noqa: E402


class Args:
    """argparse.Namespace tối giản — chỉ những trường lệnh thật sự đọc."""

    def __init__(self, **kw):
        self.__dict__.update(kw)


class BaseLsp(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def ghi_json(self, ten, data):
        path = os.path.join(self.tmp.name, ten)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh)
        return path

    def vao_json(self, mapping):
        """Vá `_doc_json` theo bảng đường-dẫn → nội dung; đường dẫn lạ trả rỗng."""
        return mock.patch.object(tdq_lsp, "_doc_json", lambda p: mapping.get(p, {}))


class Bac1Binary(BaseLsp):
    def test_thieu_binary_thi_ra_lenh_cai(self):
        with mock.patch.object(tdq_lsp.shutil, "which", return_value=None):
            b = tdq_lsp.bac1_binary()
        self.assertFalse(b.dat)
        self.assertIn("tdq_setup.py", b.lenh_cai)

    def test_co_binary_thi_dat_va_doc_ban(self):
        with mock.patch.object(tdq_lsp.shutil, "which", return_value="/usr/local/bin/agent-lsp"), \
                mock.patch.object(tdq_lsp, "_run", return_value=(0, "0.18.0\n")):
            b = tdq_lsp.bac1_binary()
        self.assertTrue(b.dat)
        self.assertIn("0.18.0", b.chi_tiet)


class Bac2Mcp(BaseLsp):
    def test_chua_dang_ky_thi_thieu(self):
        with self.vao_json({"~/.claude.json": {"mcpServers": {"khac": {}}}}):
            b = tdq_lsp.bac2_mcp()
        self.assertFalse(b.dat)
        self.assertEqual(b.lenh_cai, "agent-lsp init")

    def test_da_dang_ky_thi_dat(self):
        with self.vao_json({"~/.claude.json": {"mcpServers": {"lsp": {}, "khac": {}}}}):
            b = tdq_lsp.bac2_mcp()
        self.assertTrue(b.dat)


class Bac3LanguageServer(BaseLsp):
    def du_file(self, duoi, so_luong):
        for i in range(so_luong):
            with open(os.path.join(self.tmp.name, f"f{i}{duoi}"), "w", encoding="utf-8") as fh:
                fh.write("x")

    def test_duoi_nguong_thi_khong_doi_server(self):
        """2 file Python là nhiễu, không phải một stack — đòi server cho nó là làm phiền user."""
        self.du_file(".py", 2)
        self.assertEqual(tdq_lsp.do_ngon_ngu(self.tmp.name), {})

    def test_yaml_json_khong_bao_gio_bi_doi(self):
        """YAML/JSON có mặt ở gần như mọi repo nên bị loại khỏi phép dò, dù thừa ngưỡng."""
        self.du_file(".yaml", 9)
        self.du_file(".json", 9)
        self.assertEqual(tdq_lsp.do_ngon_ngu(self.tmp.name), {})

    def test_bo_qua_thu_muc_rac(self):
        rac = os.path.join(self.tmp.name, "node_modules")
        os.makedirs(rac)
        for i in range(9):
            with open(os.path.join(rac, f"a{i}.py"), "w", encoding="utf-8") as fh:
                fh.write("x")
        self.assertEqual(tdq_lsp.do_ngon_ngu(self.tmp.name), {})

    def test_thieu_server_thi_ra_dung_lenh_cai(self):
        self.du_file(".py", 5)
        with mock.patch.object(tdq_lsp.shutil, "which", return_value=None):
            b = tdq_lsp.bac3_language_server(self.tmp.name)
        self.assertFalse(b.dat)
        self.assertIn("pyright", b.lenh_cai)

    def test_du_server_thi_dat(self):
        self.du_file(".py", 5)
        with mock.patch.object(tdq_lsp.shutil, "which", return_value="/usr/bin/pyright-langserver"):
            b = tdq_lsp.bac3_language_server(self.tmp.name)
        self.assertTrue(b.dat)

    def test_cong3_ngon_ngu_chua_khai_trong_mcp_thi_truot(self):
        """0.59.0: có server trên PATH mà MCP `lsp` chưa khai → agent không gọi tới được."""
        self.du_file(".py", 5)
        self.du_file(".html", 3)
        cau_hinh = {"~/.claude.json": {"mcpServers": {"lsp": {"args": ["python:pyright-langserver,--stdio"]}}}}
        with mock.patch.object(tdq_lsp.shutil, "which", return_value="/usr/bin/x"), self.vao_json(cau_hinh):
            b = tdq_lsp.bac3_language_server(self.tmp.name)
        self.assertFalse(b.dat)
        self.assertIn("HTML", b.chi_tiet)
        self.assertIn("tdq_setup.py", b.lenh_cai)

    def test_cong3_javascript_duoc_entry_typescript_phuc_vu(self):
        self.du_file(".js", 5)
        cau_hinh = {"~/.claude.json": {"mcpServers": {"lsp": {"args": ["typescript:tsls,--stdio"]}}}}
        with mock.patch.object(tdq_lsp.shutil, "which", return_value="/usr/bin/x"), self.vao_json(cau_hinh), \
                mock.patch.object(tdq_lsp, "_chay_doctor", return_value=(None, "bỏ")):
            b = tdq_lsp.bac3_language_server(self.tmp.name)
        self.assertTrue(b.dat)
        self.assertEqual(tdq_lsp.lang_mcp(["typescript:tsls"], "javascript"), "typescript")

    def test_project_khong_co_ngon_ngu_nao_van_dat(self):
        b = tdq_lsp.bac3_language_server(self.tmp.name)
        self.assertTrue(b.dat)


class Bac4QuyenTool(BaseLsp):
    def test_chua_co_quyen_thi_thieu(self):
        with self.vao_json({"~/.claude/settings.json": {"permissions": {"allow": ["Bash"]}}}):
            b = tdq_lsp.bac4_quyen_tool()
        self.assertFalse(b.dat)
        self.assertIn("mcp__lsp__", b.lenh_cai)

    def test_co_quyen_thi_dat(self):
        with self.vao_json({"~/.claude/settings.json":
                            {"permissions": {"allow": ["mcp__lsp__find_symbol"]}}}):
            b = tdq_lsp.bac4_quyen_tool()
        self.assertTrue(b.dat)


class Bac5HookXungDot(BaseLsp):
    def dung_plugin(self, ten, hooks):
        goc = os.path.join(self.tmp.name, ten)
        os.makedirs(os.path.join(goc, "hooks"), exist_ok=True)
        with open(os.path.join(goc, "hooks", "hooks.json"), "w", encoding="utf-8") as fh:
            json.dump({"hooks": hooks}, fh)
        return goc

    def test_bat_duoc_hook_chen_thu_tu_khac(self):
        goc = self.dung_plugin("plugin-ngoai", {"PreToolUse": [{"matcher": "Grep|Bash"}],
                                         "SessionStart": [{"matcher": "*"}]})
        with mock.patch.object(tdq_lsp, "_plugin_dang_bat", return_value=[("plugin-ngoai", goc)]):
            b = tdq_lsp.bac5_hook_xung_dot(self.tmp.name)
        self.assertFalse(b.dat)
        self.assertTrue(b.chi_canh_bao, "bậc 5 chỉ được cảnh báo, không được chặn")
        self.assertIn("plugin-ngoai", b.chi_tiet)

    def test_hook_khong_lien_quan_tim_kiem_thi_bo_qua(self):
        goc = self.dung_plugin("khac", {"PreToolUse": [{"matcher": "Write"}]})
        with mock.patch.object(tdq_lsp, "_plugin_dang_bat", return_value=[("khac", goc)]):
            b = tdq_lsp.bac5_hook_xung_dot(self.tmp.name)
        self.assertTrue(b.dat)

    def test_khong_soi_plugin_nha(self):
        """Hook của chính tdq-workflow là chuẩn mực, không phải xung đột."""
        goc = self.dung_plugin("tdq-workflow", {"PreToolUse": [{"matcher": "Bash"}]})
        with mock.patch.object(tdq_lsp, "_plugin_dang_bat", return_value=[("tdq-workflow", goc)]):
            b = tdq_lsp.bac5_hook_xung_dot(self.tmp.name)
        self.assertTrue(b.dat)

    def test_khong_ghi_gi_vao_file_plugin(self):
        goc = self.dung_plugin("plugin-ngoai", {"PreToolUse": [{"matcher": "Grep"}]})
        f = os.path.join(goc, "hooks", "hooks.json")
        truoc = open(f, encoding="utf-8").read()
        with mock.patch.object(tdq_lsp, "_plugin_dang_bat", return_value=[("plugin-ngoai", goc)]):
            tdq_lsp.bac5_hook_xung_dot(self.tmp.name)
        self.assertEqual(truoc, open(f, encoding="utf-8").read())


class MaThoat(BaseLsp):
    def bac_gia(self, thieu_bac_hanh_dong, canh_bao):
        return [
            tdq_lsp.Bac(1, "x", not thieu_bac_hanh_dong),
            tdq_lsp.Bac(5, "y", not canh_bao, chi_canh_bao=True),
        ]

    # `check` chạy cả smoke từ 2026-10-03 (T4.3). Không vá smoke thì hai ca dưới đây hỏi thật
    # các công cụ của máy (~12 s) và đỏ ở bất kỳ máy nào có một tầng đang tắt — tức đo máy chứ
    # không đo mã thoát. Smoke giả "ba tầng đều trả lời" giữ đúng điều ca này khoá.
    SMOKE_DAT = [("grep", True, ""), ("LSP", True, ""), ("graphify", True, "")]

    def test_thieu_bac_hanh_dong_thi_ma_3(self):
        with mock.patch.object(tdq_lsp, "chay_kiem", return_value=self.bac_gia(True, False)), \
                mock.patch.object(tdq_lsp, "chay_smoke", return_value=self.SMOKE_DAT):
            self.assertEqual(tdq_lsp.cmd_kiem(Args()), tdq_lsp.EXIT_THIEU)

    def test_chi_canh_bao_thi_van_ma_0(self):
        """Bậc chỉ cảnh báo (5, 7) hỏng không được đổi mã thoát: tìm kiếm vẫn chạy bằng agent-lsp rồi grep."""
        with mock.patch.object(tdq_lsp, "chay_kiem", return_value=self.bac_gia(False, True)), \
                mock.patch.object(tdq_lsp, "chay_smoke", return_value=self.SMOKE_DAT):
            self.assertEqual(tdq_lsp.cmd_kiem(Args()), tdq_lsp.EXIT_OK)


class Bac6CauHinhGocImport(BaseLsp):
    """Bậc 6 — cấu hình gốc import, bậc duy nhất bắt được lỗi 'chỉ mục chết mà thang vẫn ĐẠT'."""

    def du_file(self, duoi, so_luong):
        for i in range(so_luong):
            with open(os.path.join(self.tmp.name, f"f{i}{duoi}"), "w", encoding="utf-8") as fh:
                fh.write("x")

    def test_bang_cau_hinh_phu_dung_bo_khoa_cua_lang_server(self):
        """Thiếu một ngôn ngữ trong LANG_CONFIG là bậc 6 im lặng bỏ qua ngôn ngữ đó."""
        self.assertEqual(set(tdq_lsp.LANG_CONFIG), set(tdq_lsp.LANG_SERVER))

    def test_dockerfile_co_trong_ca_hai_bang(self):
        """Máy đã cài docker-language-server; thiếu khoá thì bậc 3 không bao giờ hỏi tới nó."""
        self.assertIn("dockerfile", tdq_lsp.LANG_SERVER)
        self.assertEqual(tdq_lsp.LANG_SERVER["dockerfile"][1], "docker-language-server")
        self.assertIn("dockerfile", tdq_lsp.LANG_CONFIG)
        self.assertEqual(tdq_lsp.LANG_CONFIG["dockerfile"], ([], "A"))

    def test_lenh_cai_go_dung_duong_brew(self):
        """`go install ...gopls` cần sẵn Go; trên máy này Go tới từ brew nên lệnh phải nêu brew."""
        self.assertIn("brew", tdq_lsp.LANG_SERVER["go"][2])

    def test_csharp_dung_omnisharp(self):
        """csharp-ls sập `abort trap` khi hỏi file .cs mồ côi; OmniSharp sống nên nó là server C# chính thức."""
        self.assertEqual(tdq_lsp.LANG_SERVER["csharp"][1], "omnisharp")

    def test_lenh_cai_omnisharp_neu_dotnet_root(self):
        """OmniSharp là bản framework-dependent: thiếu DOTNET_ROOT là chết ngay lúc khởi động."""
        self.assertIn("DOTNET_ROOT", tdq_lsp.LANG_SERVER["csharp"][2])

    def test_nhom_b_thieu_cau_hinh_thi_CHAN(self):
        """Python không pyrightconfig.json: dự án vẫn chạy, test vẫn xanh, chỉ mục liên file chết."""
        self.du_file(".py", 5)
        b = tdq_lsp.bac6_cau_hinh_goc_import(self.tmp.name)
        self.assertFalse(b.dat)
        self.assertFalse(b.chi_canh_bao, "nhóm B phải chặn, không được chỉ cảnh báo")
        self.assertIn("pyrightconfig.json", b.lenh_cai)

    def test_nhom_a_thieu_cau_hinh_thi_chi_canh_bao(self):
        """Go không go.mod thì dự án đã không build được — tự lộ, không cần chặn thêm."""
        self.du_file(".go", 5)
        b = tdq_lsp.bac6_cau_hinh_goc_import(self.tmp.name)
        self.assertFalse(b.dat)
        self.assertTrue(b.chi_canh_bao, "nhóm A chỉ được cảnh báo")

    def test_thieu_ca_hai_nhom_thi_chi_tiet_liet_ke_ca_hai(self):
        """Lỗi QC bắt được: `thieu_b or thieu_a` che mất nhóm A khi nhóm B cũng thiếu.

        Người đọc chỉ thấy Python thiếu `pyrightconfig.json`, không biết Go cũng thiếu `go.mod`,
        nên sửa xong một cái vẫn tưởng đã xong. Mức nghiêm trọng vẫn do nhóm B quyết định.
        """
        self.du_file(".py", 5)
        self.du_file(".go", 5)
        b = tdq_lsp.bac6_cau_hinh_goc_import(self.tmp.name)
        self.assertFalse(b.dat)
        self.assertFalse(b.chi_canh_bao, "có nhóm B thiếu thì phải CHẶN")
        self.assertIn("pyright", b.chi_tiet)
        self.assertIn("go.mod", b.chi_tiet, "nhóm A bị che khi nhóm B cũng thiếu")

    def test_co_cau_hinh_thi_dat(self):
        self.du_file(".py", 5)
        with open(os.path.join(self.tmp.name, "pyrightconfig.json"), "w", encoding="utf-8") as fh:
            fh.write("{}")
        self.assertTrue(tdq_lsp.bac6_cau_hinh_goc_import(self.tmp.name).dat)

    def test_khong_bao_gio_tu_ghi_file_cau_hinh(self):
        """Luật cứng của skill: script chỉ chẩn đoán và xin phép, không tự tạo file."""
        self.du_file(".py", 5)
        truoc = sorted(os.listdir(self.tmp.name))
        tdq_lsp.bac6_cau_hinh_goc_import(self.tmp.name)
        self.assertEqual(sorted(os.listdir(self.tmp.name)), truoc)

    def test_bac6_nam_trong_thang(self):
        self.du_file(".py", 5)
        with open(os.path.join(self.tmp.name, "pyrightconfig.json"), "w", encoding="utf-8") as fh:
            fh.write("{}")
        so = [b.so for b in tdq_lsp.chay_kiem(self.tmp.name)]
        # 0.58.0: lumen (bậc 5 cũ) gỡ; 0.59.0: thêm bậc 8 LSP theo module — số liền, không lỗ.
        self.assertEqual(so, [1, 2, 3, 4, 5, 6, 7, 8])


class LoiHuaKhongTuCai(BaseLsp):
    def test_khong_co_lenh_cai_dat_nao_duoc_chay(self):
        """Lệnh cài chỉ được nằm trong CHUỖI để in ra, không bao giờ trong lời gọi tiến trình con."""
        src = open(os.path.join(ROOT, "scripts", "tdq_lsp.py"), encoding="utf-8").read()
        for dong in src.splitlines():
            if "subprocess.run" in dong or "subprocess.Popen" in dong:
                for cam in ("npm i", "npm install", "brew install", "dotnet tool install", "curl"):
                    self.assertNotIn(cam, dong, f"script đang định tự cài: {dong.strip()}")


if __name__ == "__main__":
    unittest.main()
