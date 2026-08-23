"""P5 — unit test cho scripts/tdq_lsp.py: 6 bậc của thang chẩn đoán + vòng đời Ollama.

Script này quyết định workflow có được dùng LSP hay không, và nó có một lời hứa cứng:
KHÔNG bao giờ tự cài, KHÔNG bao giờ sửa file plugin khác, KHÔNG tắt daemon của user.
Ba lời hứa đó chỉ là chữ nếu không có test đóng đinh, nên mỗi lời hứa có một ca riêng.

Mọi ca đều vá (`patch`) lớp chạm máy thật — `shutil.which`, socket probe, subprocess —
để suite chạy được trên máy chưa cài gì mà vẫn kiểm đúng nhánh logic.
"""
import json
import os
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
        # Dấu sở hữu phải nằm trong tmp, nếu không test sẽ giẫm lên phiên làm việc thật.
        self.dau = os.path.join(self.tmp.name, "owner.json")
        p = mock.patch.object(tdq_lsp, "_dau_so_huu", lambda: self.dau)
        p.start()
        self.addCleanup(p.stop)

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
        self.assertIn("install.sh", b.lenh_cai)

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


class Bac5Lumen(BaseLsp):
    def test_thieu_ollama_chi_canh_bao(self):
        """lumen là lớp dự phòng: hỏng thì cảnh báo, tuyệt đối không chặn phiên làm việc."""
        with mock.patch.object(tdq_lsp.shutil, "which", return_value=None):
            b = tdq_lsp.bac5_lumen()
        self.assertFalse(b.dat)
        self.assertTrue(b.chi_canh_bao)

    def test_thieu_model_chi_canh_bao(self):
        with mock.patch.object(tdq_lsp.shutil, "which", return_value="/usr/local/bin/ollama"), \
                mock.patch.object(tdq_lsp, "_model_da_pull", return_value=False):
            b = tdq_lsp.bac5_lumen()
        self.assertFalse(b.dat)
        self.assertTrue(b.chi_canh_bao)
        self.assertIn("ollama pull", b.lenh_cai)

    def test_du_do_nhung_daemon_ngu_van_chi_canh_bao(self):
        with mock.patch.object(tdq_lsp.shutil, "which", return_value="/usr/local/bin/ollama"), \
                mock.patch.object(tdq_lsp, "_model_da_pull", return_value=True), \
                mock.patch.object(tdq_lsp, "_ollama_dang_chay", return_value=False):
            b = tdq_lsp.bac5_lumen()
        self.assertFalse(b.dat)
        self.assertTrue(b.chi_canh_bao)

    def test_du_ca_ba_thi_dat(self):
        with mock.patch.object(tdq_lsp.shutil, "which", return_value="/usr/local/bin/ollama"), \
                mock.patch.object(tdq_lsp, "_model_da_pull", return_value=True), \
                mock.patch.object(tdq_lsp, "_ollama_dang_chay", return_value=True):
            b = tdq_lsp.bac5_lumen()
        self.assertTrue(b.dat)


class Bac6HookXungDot(BaseLsp):
    def dung_plugin(self, ten, hooks):
        goc = os.path.join(self.tmp.name, ten)
        os.makedirs(os.path.join(goc, "hooks"), exist_ok=True)
        with open(os.path.join(goc, "hooks", "hooks.json"), "w", encoding="utf-8") as fh:
            json.dump({"hooks": hooks}, fh)
        return goc

    def test_bat_duoc_hook_chen_thu_tu_khac(self):
        goc = self.dung_plugin("lumen", {"PreToolUse": [{"matcher": "Grep|Bash"}],
                                         "SessionStart": [{"matcher": "*"}]})
        with mock.patch.object(tdq_lsp, "_plugin_dang_bat", return_value=[("lumen", goc)]):
            b = tdq_lsp.bac6_hook_xung_dot(self.tmp.name)
        self.assertFalse(b.dat)
        self.assertTrue(b.chi_canh_bao, "bậc 6 chỉ được cảnh báo, không được chặn")
        self.assertIn("lumen", b.chi_tiet)

    def test_hook_khong_lien_quan_tim_kiem_thi_bo_qua(self):
        goc = self.dung_plugin("khac", {"PreToolUse": [{"matcher": "Write"}]})
        with mock.patch.object(tdq_lsp, "_plugin_dang_bat", return_value=[("khac", goc)]):
            b = tdq_lsp.bac6_hook_xung_dot(self.tmp.name)
        self.assertTrue(b.dat)

    def test_khong_soi_plugin_nha(self):
        """Hook của chính tdq-workflow là chuẩn mực, không phải xung đột."""
        goc = self.dung_plugin("tdq-workflow", {"PreToolUse": [{"matcher": "Bash"}]})
        with mock.patch.object(tdq_lsp, "_plugin_dang_bat", return_value=[("tdq-workflow", goc)]):
            b = tdq_lsp.bac6_hook_xung_dot(self.tmp.name)
        self.assertTrue(b.dat)

    def test_khong_ghi_gi_vao_file_plugin(self):
        goc = self.dung_plugin("lumen", {"PreToolUse": [{"matcher": "Grep"}]})
        f = os.path.join(goc, "hooks", "hooks.json")
        truoc = open(f, encoding="utf-8").read()
        with mock.patch.object(tdq_lsp, "_plugin_dang_bat", return_value=[("lumen", goc)]):
            tdq_lsp.bac6_hook_xung_dot(self.tmp.name)
        self.assertEqual(truoc, open(f, encoding="utf-8").read())


class MaThoat(BaseLsp):
    def bac_gia(self, thieu_bac_hanh_dong, canh_bao):
        return [
            tdq_lsp.Bac(1, "x", not thieu_bac_hanh_dong),
            tdq_lsp.Bac(5, "y", not canh_bao, chi_canh_bao=True),
        ]

    def test_thieu_bac_hanh_dong_thi_ma_3(self):
        with mock.patch.object(tdq_lsp, "chay_kiem", return_value=self.bac_gia(True, False)):
            self.assertEqual(tdq_lsp.cmd_kiem(Args()), tdq_lsp.EXIT_THIEU)

    def test_chi_canh_bao_thi_van_ma_0(self):
        """Bậc 5-6 hỏng không được đổi mã thoát: tìm kiếm vẫn chạy bằng agent-lsp rồi grep."""
        with mock.patch.object(tdq_lsp, "chay_kiem", return_value=self.bac_gia(False, True)):
            self.assertEqual(tdq_lsp.cmd_kiem(Args()), tdq_lsp.EXIT_OK)


class VongDoiOllama(BaseLsp):
    def test_da_chay_san_thi_khong_nhan_so_huu(self):
        with mock.patch.object(tdq_lsp, "_ollama_dang_chay", return_value=True), \
                mock.patch.object(tdq_lsp.subprocess, "Popen") as popen:
            rc = tdq_lsp.cmd_danh_thuc(Args(han_cho=1.0))
        self.assertEqual(rc, tdq_lsp.EXIT_OK)
        popen.assert_not_called()
        self.assertFalse(os.path.exists(self.dau), "daemon của user mà nhận sở hữu là sai")

    def test_khong_co_binary_thi_bo_qua_khong_chan(self):
        with mock.patch.object(tdq_lsp, "_ollama_dang_chay", return_value=False), \
                mock.patch.object(tdq_lsp.shutil, "which", return_value=None), \
                mock.patch.object(tdq_lsp.subprocess, "Popen") as popen:
            rc = tdq_lsp.cmd_danh_thuc(Args(han_cho=1.0))
        self.assertEqual(rc, tdq_lsp.EXIT_OK, "thiếu Ollama không được chặn lượt làm việc")
        popen.assert_not_called()

    def test_danh_thuc_lanh_thi_nhan_so_huu(self):
        trang_thai = {"len": False}

        def dang_chay():
            return trang_thai["len"]

        def popen(*a, **kw):
            trang_thai["len"] = True
            return mock.Mock(pid=4242)

        with mock.patch.object(tdq_lsp, "_ollama_dang_chay", side_effect=dang_chay), \
                mock.patch.object(tdq_lsp.shutil, "which", return_value="/usr/local/bin/ollama"), \
                mock.patch.object(tdq_lsp.subprocess, "Popen", side_effect=popen):
            rc = tdq_lsp.cmd_danh_thuc(Args(han_cho=5.0))
        self.assertEqual(rc, tdq_lsp.EXIT_OK)
        self.assertEqual(tdq_lsp._doc_dau(), 4242)

    def test_qua_han_thi_don_tien_trinh_va_khong_chan(self):
        p = mock.Mock(pid=777)
        with mock.patch.object(tdq_lsp, "_ollama_dang_chay", return_value=False), \
                mock.patch.object(tdq_lsp.shutil, "which", return_value="/usr/local/bin/ollama"), \
                mock.patch.object(tdq_lsp.subprocess, "Popen", return_value=p):
            rc = tdq_lsp.cmd_danh_thuc(Args(han_cho=0.01))
        self.assertEqual(rc, tdq_lsp.EXIT_OK, "quá hạn là rơi xuống grep, không phải hỏng lượt")
        p.terminate.assert_called_once()
        self.assertFalse(os.path.exists(self.dau))

    def test_nha_khong_giet_daemon_cua_user(self):
        """Ca user tự bật: không có dấu sở hữu → nhả model nhưng để daemon sống."""
        with mock.patch.object(tdq_lsp, "_ollama_dang_chay", return_value=True), \
                mock.patch.object(tdq_lsp.shutil, "which", return_value="/usr/local/bin/ollama"), \
                mock.patch.object(tdq_lsp, "_run", return_value=(0, "")) as run, \
                mock.patch.object(tdq_lsp.os, "kill") as kill:
            rc = tdq_lsp.cmd_nha(Args())
        self.assertEqual(rc, tdq_lsp.EXIT_OK)
        self.assertIn("stop", run.call_args[0][0])
        kill.assert_not_called()

    def test_nha_giet_dung_daemon_do_script_bat(self):
        tdq_lsp._ghi_dau(99999)
        with mock.patch.object(tdq_lsp, "_ollama_dang_chay", return_value=True), \
                mock.patch.object(tdq_lsp.shutil, "which", return_value="/usr/local/bin/ollama"), \
                mock.patch.object(tdq_lsp, "_run", return_value=(0, "")), \
                mock.patch.object(tdq_lsp.os, "kill") as kill:
            tdq_lsp.cmd_nha(Args())
        kill.assert_called_once_with(99999, 15)
        self.assertFalse(os.path.exists(self.dau), "tắt xong phải xoá dấu, nếu không lần sau tắt nhầm")

    def test_daemon_ngu_thi_khong_goi_ollama_stop(self):
        """macOS: gọi `ollama stop` lúc daemon ngủ sẽ đánh thức đúng thứ đang muốn để yên."""
        with mock.patch.object(tdq_lsp, "_ollama_dang_chay", return_value=False), \
                mock.patch.object(tdq_lsp.shutil, "which", return_value="/usr/local/bin/ollama"), \
                mock.patch.object(tdq_lsp, "_run") as run:
            rc = tdq_lsp.cmd_nha(Args())
        self.assertEqual(rc, tdq_lsp.EXIT_OK)
        run.assert_not_called()


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
