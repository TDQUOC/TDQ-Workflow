"""Unit test cho scripts/setup_status.py — bộ thu số liệu của trang trạng thái setup.

Trang này chỉ có giá trị khi nó nói THẬT, nên mỗi ca ở đây đóng đinh đúng một lời hứa:
KHÔNG rò bí mật ra file, KHÔNG chết khi máy thiếu công cụ, KHÔNG bịa giá trị khi
không đọc được nguồn. Mọi ca đều vá lớp chạm máy thật (`shutil.which`, `subprocess`)
để suite chạy được trên máy trắng.
"""
import io
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import setup_status  # noqa: E402


class CheBiMat(unittest.TestCase):
    """mask_secrets() — hàng rào cuối trước khi bất cứ chuỗi nào chạm file HTML."""

    def test_che_khoa_trong_query_string(self):
        goc = "tavily-primary: https://mcp.tavily.com/mcp/?tavilyApiKey=tvly-dev-ABC123XYZ (HTTP)"
        ra = setup_status.mask_secrets(goc)
        self.assertNotIn("tvly-dev-ABC123XYZ", ra)
        self.assertIn("tavilyApiKey=", ra)
        self.assertIn("tavily-primary", ra)

    def test_che_nhieu_ten_tham_so_khac_nhau(self):
        for tham_so in ("apiKey", "api_key", "token", "access_token", "secret", "password"):
            ra = setup_status.mask_secrets(f"https://x.dev/?{tham_so}=SIEU-MAT-1234&safe=yes")
            self.assertNotIn("SIEU-MAT-1234", ra, tham_so)
            self.assertIn("safe=yes", ra, tham_so)

    def test_che_header_authorization(self):
        ra = setup_status.mask_secrets("Authorization: Bearer sk-live-9f8e7d")
        self.assertNotIn("sk-live-9f8e7d", ra)

    def test_khong_dung_den_chuoi_khong_co_bi_mat(self):
        goc = "lsp: /Users/tdq/.local/bin/agent-lsp python:pyright-langserver,--stdio - ✔ Connected"
        self.assertEqual(setup_status.mask_secrets(goc), goc)

    def test_che_co_dong_lenh(self):
        """Khoá không chỉ nằm trong URL: MCP kiểu stdio truyền khoá qua cờ dòng lệnh."""
        goc = "/usr/bin/mcpx --api-key=BIMAT-1111 --port=8080"
        ra = setup_status.mask_secrets(goc)
        self.assertNotIn("BIMAT-1111", ra)
        self.assertIn("--api-key=", ra)
        self.assertIn("--port=8080", ra)

    def test_che_co_dong_lenh_cach_bang_dau_cach(self):
        ra = setup_status.mask_secrets("mcpx --token BIMAT-2222 --verbose")
        self.assertNotIn("BIMAT-2222", ra)
        self.assertIn("--verbose", ra)

    def test_che_bien_moi_truong(self):
        """Khối `env` của server MCP là nguồn rò thứ ba, ngang hàng URL và cờ."""
        ra = setup_status.mask_secrets("TAVILY_API_KEY=BIMAT-3333 DOTNET_ROOT=/usr/local/share")
        self.assertNotIn("BIMAT-3333", ra)
        self.assertIn("TAVILY_API_KEY=", ra)
        self.assertIn("DOTNET_ROOT=/usr/local/share", ra)

    def test_chuoi_rong_va_none_khong_lam_vo(self):
        self.assertEqual(setup_status.mask_secrets(""), "")
        self.assertEqual(setup_status.mask_secrets(None), "")


class ChayLenhNgoai(unittest.TestCase):
    """_run_tool() — thiếu binary là chuyện bình thường, không phải sự cố."""

    def test_thieu_binary_tra_o_chua_cai_kem_lenh_goi_y(self):
        with mock.patch.object(setup_status.shutil, "which", return_value=None):
            ra = setup_status._run_tool("graphify", ["--version"], goi_y="cài graphify")
        self.assertFalse(ra["co"])
        self.assertEqual(ra["goi_y"], "cài graphify")
        self.assertIn("chưa cài", ra["chi_tiet"])
        self.assertEqual(ra["ra"], "")

    def test_lenh_chay_duoc_thi_tra_stdout_da_che(self):
        ket_qua = mock.Mock(returncode=0, stdout="url?apiKey=BI-MAT-9\n", stderr="")
        with mock.patch.object(setup_status.shutil, "which", return_value="/usr/bin/x"), \
             mock.patch.object(setup_status.subprocess, "run", return_value=ket_qua):
            ra = setup_status._run_tool("x", ["--version"])
        self.assertTrue(ra["co"])
        self.assertNotIn("BI-MAT-9", ra["ra"])

    def test_lenh_loi_khong_nem_exception(self):
        with mock.patch.object(setup_status.shutil, "which", return_value="/usr/bin/x"), \
             mock.patch.object(setup_status.subprocess, "run",
                               side_effect=OSError("hỏng")):
            ra = setup_status._run_tool("x", ["--version"])
        self.assertTrue(ra["co"])
        self.assertFalse(ra["chay_duoc"])
        self.assertIn("hỏng", ra["chi_tiet"])

    def test_lenh_qua_han_tra_o_khong_doc_duoc(self):
        with mock.patch.object(setup_status.shutil, "which", return_value="/usr/bin/x"), \
             mock.patch.object(setup_status.subprocess, "run",
                               side_effect=setup_status.subprocess.TimeoutExpired("x", 5)):
            ra = setup_status._run_tool("x", ["--version"])
        self.assertFalse(ra["chay_duoc"])
        self.assertIn("quá hạn", ra["chi_tiet"])


class DichVuLog(unittest.TestCase):
    """Log service bật mặc định, tắt bằng TDQ_LOG=0 — đúng khuôn của repo."""

    def test_mac_dinh_bat(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertTrue(setup_status._log_enabled())

    def test_tdq_log_0_thi_tat(self):
        with mock.patch.dict(os.environ, {"TDQ_LOG": "0"}):
            self.assertFalse(setup_status._log_enabled())


class ThuDependency(unittest.TestCase):
    """thu_dependency() — 4 công cụ, mỗi công cụ một hàng, thiếu cũng phải có hàng."""

    def _gia_lap(self, ban_ra):
        def chay(binary, args, goi_y="", timeout=None):
            if binary not in ban_ra:
                return {"co": False, "chay_duoc": False, "duong_dan": "", "ma": None,
                        "ra": "", "loi": "", "chi_tiet": "chưa cài", "goi_y": goi_y}
            return {"co": True, "chay_duoc": True, "duong_dan": f"/bin/{binary}", "ma": 0,
                    "ra": ban_ra[binary], "loi": "", "chi_tiet": "", "goi_y": goi_y}
        return chay

    def test_du_bon_cong_cu_du_ca_khi_thieu(self):
        with mock.patch.object(setup_status, "_run_tool", self._gia_lap({})):
            hang = setup_status.thu_dependency()
        self.assertEqual([h["ten"] for h in hang],
                         ["graphify", "lumen", "agent-lsp", "ollama"])
        for h in hang:
            self.assertFalse(h["co"])
            self.assertEqual(h["ban"], "chưa cài")
            self.assertTrue(h["goi_y"], h["ten"])

    def test_goi_y_cai_agent_lsp_lay_tu_tdq_lsp(self):
        """Gợi ý cài phải là lệnh THẬT: chép tay sẽ lệch khi tdq_lsp đổi cách cài."""
        import tdq_lsp
        goi_y = {ten: y for ten, _args, y in setup_status.CONG_CU}
        self.assertEqual(goi_y["agent-lsp"], tdq_lsp.INSTALL_AGENT_LSP)
        self.assertNotIn("npm install -g @agent-lsp/cli", goi_y["agent-lsp"])

    def test_lay_dong_dau_lam_so_ban(self):
        ra = {"graphify": "graphify 0.9.55\nextra line\n", "lumen": "lumen 0.0.42\n"}
        with mock.patch.object(setup_status, "_run_tool", self._gia_lap(ra)):
            hang = {h["ten"]: h for h in setup_status.thu_dependency()}
        self.assertEqual(hang["graphify"]["ban"], "graphify 0.9.55")
        self.assertEqual(hang["lumen"]["ban"], "lumen 0.0.42")
        self.assertEqual(hang["graphify"]["duong_dan"], "/bin/graphify")

    def test_lumen_dung_lenh_version_khong_phai_co_hai_gach(self):
        goi = []

        def chay(binary, args, goi_y="", timeout=None):
            goi.append((binary, tuple(args)))
            return {"co": False, "chay_duoc": False, "duong_dan": "", "ma": None,
                    "ra": "", "loi": "", "chi_tiet": "chưa cài", "goi_y": goi_y}

        with mock.patch.object(setup_status, "_run_tool", chay):
            setup_status.thu_dependency()
        self.assertIn(("lumen", ("version",)), goi)

    def test_chay_duoc_nhung_ra_rong_thi_ghi_khong_doc_duoc(self):
        with mock.patch.object(setup_status, "_run_tool", self._gia_lap({"ollama": "  \n"})):
            hang = {h["ten"]: h for h in setup_status.thu_dependency()}
        self.assertTrue(hang["ollama"]["co"])
        self.assertEqual(hang["ollama"]["ban"], "không đọc được")


class ThuLumen(unittest.TestCase):
    """thu_lumen() — model thật và các endpoint, đọc từ chính config lumen."""

    def ghi_config(self, noi_dung):
        duong = os.path.join(self.tmp, "config.yaml")
        with open(duong, "w", encoding="utf-8") as f:
            f.write(noi_dung)
        return duong

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_doc_du_hai_endpoint_va_model(self):
        duong = self.ghi_config(
            "servers:\n"
            "  - backend: ollama\n"
            "    host: http://100.122.225.62:11434\n"
            "    model: qwen3-embedding:0.6b\n"
            "  - backend: ollama\n"
            "    host: http://localhost:11434\n"
            "    model: qwen3-embedding:0.6b\n")
        with mock.patch.object(setup_status, "CONFIG_LUMEN", duong):
            ra = setup_status.thu_lumen()
        self.assertEqual(ra["model"], "qwen3-embedding:0.6b")
        self.assertEqual(ra["endpoint"],
                         ["http://100.122.225.62:11434", "http://localhost:11434"])
        self.assertEqual(ra["config"], duong)

    def test_khong_co_config_thi_noi_thang_va_van_co_model_mac_dinh(self):
        with mock.patch.object(setup_status, "CONFIG_LUMEN",
                               os.path.join(self.tmp, "khong-ton-tai.yaml")):
            ra = setup_status.thu_lumen()
        self.assertEqual(ra["endpoint"], [])
        self.assertIn("không đọc được", ra["chi_tiet"])
        self.assertTrue(ra["model"])

    def test_config_rac_khong_lam_vo(self):
        duong = self.ghi_config(":::: khong phai yaml\n\x00\n")
        with mock.patch.object(setup_status, "CONFIG_LUMEN", duong):
            ra = setup_status.thu_lumen()
        self.assertEqual(ra["endpoint"], [])
        self.assertTrue(ra["model"])


class ThuWorkflow(unittest.TestCase):
    """thu_workflow() — skill trên đĩa, hook, state, 7 bậc; nguồn hỏng thì ghi lý do."""

    def vao_nguon(self, **kw):
        """Vá 4 nguồn của thu_workflow(); nguồn nào không truyền thì trả về rỗng."""
        mac_dinh = {
            "skill": lambda project: [],
            "hook": lambda: [],
            "do_hook": lambda runs=3: [],
            "state": lambda: {},
            "bac": lambda project: [],
        }
        mac_dinh.update(kw)
        return [
            mock.patch.object(setup_status, "_nguon_skill", mac_dinh["skill"]),
            mock.patch.object(setup_status, "_nguon_hook", mac_dinh["hook"]),
            mock.patch.object(setup_status, "_nguon_do_hook", mac_dinh["do_hook"]),
            mock.patch.object(setup_status, "_nguon_state", mac_dinh["state"]),
            mock.patch.object(setup_status, "_nguon_bac", mac_dinh["bac"]),
        ]

    def chay(self, **kw):
        va = self.vao_nguon(**kw)
        for p in va:
            p.start()
            self.addCleanup(p.stop)
        return setup_status.thu_workflow()

    def test_nguon_rong_van_du_khoa(self):
        ra = self.chay()
        for khoa in ("skill", "hook", "do_hook", "state", "bac", "loi"):
            self.assertIn(khoa, ra)

    def test_gom_skill_theo_nguon(self):
        ra = self.chay(skill=lambda project: [
            ("tdq-intake", "mở request", "plugin:tdq-workflow"),
            ("graphify", "đồ thị", "user"),
        ])
        self.assertEqual(len(ra["skill"]), 2)
        self.assertEqual(ra["skill"][0]["nguon"], "plugin:tdq-workflow")
        self.assertEqual(ra["skill"][1]["ten"], "graphify")

    def test_bac_chuyen_thanh_hang_doc_duoc(self):
        class BacGia:
            def __init__(self, so, ten, dat, chi_tiet="", chi_canh_bao=False):
                self.so, self.ten, self.dat = so, ten, dat
                self.chi_tiet, self.chi_canh_bao = chi_tiet, chi_canh_bao
                self.lenh_cai = ""

        ra = self.chay(bac=lambda project: [
            BacGia(1, "binary agent-lsp", True, "0.19.2"),
            BacGia(5, "lumen", False, "thiếu model", chi_canh_bao=True),
        ])
        self.assertEqual(ra["bac"][0]["nhan"], "ĐẠT")
        self.assertEqual(ra["bac"][1]["nhan"], "CẢNH BÁO")
        self.assertEqual(ra["bac"][1]["so"], 5)

    def test_mot_nguon_no_thi_ghi_ly_do_chu_khong_vo(self):
        def no(project):
            raise RuntimeError("agent-lsp biến mất")

        ra = self.chay(bac=no)
        self.assertEqual(ra["bac"], [])
        self.assertIn("agent-lsp biến mất", ra["loi"]["bac"])
        self.assertIn("skill", ra)


MCP_THAT = """Checking MCP server health…

claude.ai Figma: https://mcp.figma.com/mcp - ✔ Connected
tavily-primary: https://mcp.tavily.com/mcp/?tavilyApiKey=tvly-dev-BIMAT99 (HTTP) - ✔ Connected
lsp: /Users/tdq/.local/bin/agent-lsp c:clangd python:pyright-langserver,--stdio - ✔ Connected
hong: https://x.dev/mcp - ✘ Failed to connect
"""

DOCTOR_THAT = """[info] LSP server started: clangd (PID 1)
● c (clangd)
  Status:  ok
  Capabilities (3):
    hoverProvider                       → inspect_symbol

● python (pyright-langserver)
  Status:  ok
  Capabilities (9):

● csharp (omnisharp)
  Status:  failed
  Error:   did not answer initialize

Summary: 2 ok, 1 failed
"""


class ThuThucNhan(unittest.TestCase):
    """thu_thuc_nhan() — cột 'Claude Code thực sự nhận được gì', đo bằng chạy thật."""

    def vao(self, mcp_ra, doctor_ra, khai_bao=None, ma=0):
        cau_hinh = {"args": khai_bao if khai_bao is not None else
                    ["c:clangd", "python:pyright-langserver,--stdio", "csharp:omnisharp,-lsp"],
                    "env": {"DOTNET_ROOT": "/opt/dotnet"}}

        def chay(binary, args, goi_y="", timeout=None, env=None):
            ra = mcp_ra if binary == "claude" else doctor_ra
            if ra is None:
                return {"co": False, "chay_duoc": False, "duong_dan": "", "ma": None,
                        "ra": "", "loi": "", "chi_tiet": "chưa cài", "goi_y": goi_y}
            self.env_da_dung = env
            return {"co": True, "chay_duoc": True, "duong_dan": f"/bin/{binary}", "ma": ma,
                    "ra": setup_status.mask_secrets(ra), "loi": "", "chi_tiet": "",
                    "goi_y": goi_y}

        return [mock.patch.object(setup_status, "_run_tool", chay),
                mock.patch.object(setup_status, "_cau_hinh_lsp", lambda: cau_hinh)]

    def chay(self, mcp_ra=MCP_THAT, doctor_ra=DOCTOR_THAT, **kw):
        self.env_da_dung = None
        for p in self.vao(mcp_ra, doctor_ra, **kw):
            p.start()
            self.addCleanup(p.stop)
        return setup_status.thu_thuc_nhan()

    def test_doc_du_server_mcp_kem_trang_thai(self):
        ra = self.chay()
        ten = [s["ten"] for s in ra["mcp"]["server"]]
        self.assertEqual(ten, ["claude.ai Figma", "tavily-primary", "lsp", "hong"])
        self.assertTrue(ra["mcp"]["server"][0]["noi_duoc"])
        self.assertFalse(ra["mcp"]["server"][3]["noi_duoc"])

    def test_khoa_khong_bao_gio_lot_ra_khoi_mcp(self):
        ra = self.chay()
        self.assertNotIn("tvly-dev-BIMAT99", repr(ra))

    def test_khai_bao_va_thuc_nhan_lech_thi_chi_dung_ten_server_chet(self):
        ra = self.chay()
        self.assertEqual(ra["lsp"]["so_khai_bao"], 3)
        self.assertEqual(ra["lsp"]["so_song"], 2)
        self.assertEqual([m["lang"] for m in ra["lsp"]["chet"]], ["csharp"])
        self.assertEqual(ra["lsp"]["chet"][0]["binary"], "omnisharp")

    def test_khai_bao_khong_duoc_doctor_nhac_den_van_hien_la_khong_ro(self):
        ra = self.chay(khai_bao=["c:clangd", "go:gopls"])
        theo_lang = {m["lang"]: m for m in ra["lsp"]["may"]}
        self.assertEqual(theo_lang["c"]["trang_thai"], "ok")
        self.assertEqual(theo_lang["go"]["trang_thai"], "không rõ")

    def test_truyen_dung_env_cua_cau_hinh_vao_doctor(self):
        self.chay()
        self.assertEqual(self.env_da_dung, {"DOTNET_ROOT": "/opt/dotnet"})

    def test_dinh_dang_la_thi_ghi_khong_phan_tich_duoc_kem_nguyen_van(self):
        ra = self.chay(mcp_ra="mot dong khong theo khuon nao ca\n", doctor_ra="???\n")
        self.assertEqual(ra["mcp"]["server"], [])
        self.assertIn("không phân tích được", ra["mcp"]["chi_tiet"])
        self.assertIn("mot dong khong theo khuon nao ca", ra["mcp"]["chi_tiet"])
        self.assertIn("không phân tích được", ra["lsp"]["chi_tiet"])

    def test_thieu_binary_thi_noi_thang_khong_vo(self):
        ra = self.chay(mcp_ra=None, doctor_ra=None)
        self.assertEqual(ra["mcp"]["server"], [])
        self.assertIn("chưa cài", ra["mcp"]["chi_tiet"])
        self.assertIn("chưa cài", ra["lsp"]["chi_tiet"])


class DoiChieuDoctor(unittest.TestCase):
    """_doi_chieu_doctor() — doctor tự tổng kết một đằng, đếm theo server một nẻo thì phải nói.

    Dòng `[error] ... exited with error after 0s` trên stderr KHÔNG vào đây: đo 3 lần liên
    tiếp cho 3 tập server khác nhau (4 → 7 → 5 dòng) trong khi `Summary` và returncode đứng
    yên, nên đó là nhiễu lúc đóng tiến trình, không phải server chết.
    """

    def _ket_qua(self, ra, ma=0):
        return {"co": True, "chay_duoc": True, "duong_dan": "/bin/agent-lsp", "ma": ma,
                "ra": ra, "loi": "", "chi_tiet": "", "goi_y": ""}

    def test_khop_thi_khong_canh_bao(self):
        canh = setup_status._doi_chieu_doctor(
            self._ket_qua("Summary: 2 ok, 0 failed"), {"python": "ok", "go": "ok"})
        self.assertEqual(canh, "")

    def test_summary_nam_cuoi_output_van_doc_duoc(self):
        """Ca thật: dòng Summary nằm sau 14 khối server, không ở đầu chuỗi."""
        ra = "● python (pyright)\n  Status:  ok\n\nSummary: 1 ok, 0 failed\n"
        self.assertEqual(setup_status._doi_chieu_doctor(self._ket_qua(ra), {"python": "ok"}), "")

    def test_summary_lech_so_dem_thi_canh_bao(self):
        canh = setup_status._doi_chieu_doctor(
            self._ket_qua("Summary: 14 ok, 0 failed"), {"python": "ok"})
        self.assertIn("14", canh)
        self.assertIn("1", canh)

    def test_returncode_khac_0_thi_canh_bao(self):
        canh = setup_status._doi_chieu_doctor(
            self._ket_qua("Summary: 1 ok, 0 failed", ma=2), {"python": "ok"})
        self.assertIn("2", canh)

    def test_thieu_dong_summary_thi_canh_bao(self):
        canh = setup_status._doi_chieu_doctor(self._ket_qua("● python (pyright)"),
                                              {"python": "ok"})
        self.assertIn("Summary", canh)

    def test_dong_error_luc_dong_tien_trinh_khong_thanh_canh_bao(self):
        ket_qua = self._ket_qua("Summary: 1 ok, 0 failed")
        ket_qua["loi"] = "[error] LSP server pyright (PID 1) exited with error after 0s."
        self.assertEqual(setup_status._doi_chieu_doctor(ket_qua, {"python": "ok"}), "")


class ThuTatCa(unittest.TestCase):
    """thu_tat_ca() — dán 4 khối vào đúng khung mà bộ kết xuất chờ."""

    def test_du_bon_khoi_va_dung_khoa(self):
        va = [
            mock.patch.object(setup_status, "thu_workflow", lambda project=None: {"skill": []}),
            mock.patch.object(setup_status, "thu_dependency", lambda: [{"ten": "graphify"}]),
            mock.patch.object(setup_status, "thu_lumen", lambda: {"model": "m"}),
            mock.patch.object(setup_status, "thu_thuc_nhan",
                              lambda: {"mcp": {"server": [], "chi_tiet": ""},
                                       "lsp": {"so_khai_bao": 0}}),
        ]
        for p in va:
            p.start()
            self.addCleanup(p.stop)
        ra = setup_status.thu_tat_ca(project="/du/an")
        self.assertEqual(sorted(ra), ["chi_tiet", "dependency", "mcp", "meta", "workflow"])
        self.assertEqual(ra["meta"]["project"], "/du/an")
        self.assertEqual(ra["chi_tiet"]["lumen"]["model"], "m")
        self.assertEqual(ra["chi_tiet"]["lsp"]["so_khai_bao"], 0)
        self.assertTrue(ra["meta"]["sinh_luc"])


class DongLenh(unittest.TestCase):
    """main() — thu, kết xuất, ghi file; nguồn lỗi cũng không được làm hỏng cả trang."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.ra = os.path.join(self.tmp, "setup_status.html")
        p = mock.patch.object(setup_status, "DUONG_DAN_RA", self.ra)
        p.start()
        self.addCleanup(p.stop)

    def test_ghi_duoc_file_va_thoat_0(self):
        with mock.patch.object(setup_status, "thu_tat_ca", lambda project=None: {"x": 1}), \
             mock.patch.object(setup_status, "setup_status_render") as render:
            render.render.return_value = "<!doctype html>\n<html>ok</html>"
            ma = setup_status.main([])
        self.assertEqual(ma, 0)
        with open(self.ra, encoding="utf-8") as f:
            self.assertIn("<html>ok</html>", f.read())

    def test_in_duong_dan_ra_stdout(self):
        with mock.patch.object(setup_status, "thu_tat_ca", lambda project=None: {}), \
             mock.patch.object(setup_status, "setup_status_render") as render, \
             mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            render.render.return_value = "<html></html>"
            setup_status.main([])
        self.assertIn(self.ra, out.getvalue())

    def test_mot_nguon_no_van_ra_trang(self):
        def thu_co_loi(project=None):
            du_lieu = setup_status.khung_du_lieu()
            du_lieu["workflow"]["loi"] = {"bac": "RuntimeError: hỏng"}
            return du_lieu

        with mock.patch.object(setup_status, "thu_tat_ca", thu_co_loi):
            ma = setup_status.main([])
        self.assertEqual(ma, 0)
        with open(self.ra, encoding="utf-8") as f:
            self.assertIn("hỏng", f.read())


class TatLogLanNhau(unittest.TestCase):
    """TDQ_LOG=0 phải làm im CẢ những module được mượn — context_surface có biến riêng."""

    def test_tat_log_thi_tat_luon_log_cua_context_surface(self):
        with mock.patch.dict(os.environ, {"TDQ_LOG": "0"}, clear=False):
            os.environ.pop("TDQ_SURFACE_LOG", None)
            with mock.patch.object(setup_status.context_surface, "scan", lambda: []):
                setup_status._nguon_hook()
            self.assertEqual(os.environ.get("TDQ_SURFACE_LOG"), "0")

    def test_bat_log_thi_khong_dung_den_bien_cua_module_khac(self):
        with mock.patch.dict(os.environ, {"TDQ_LOG": "1"}, clear=False):
            os.environ.pop("TDQ_SURFACE_LOG", None)
            with mock.patch.object(setup_status.context_surface, "scan", lambda: []):
                setup_status._nguon_hook()
            self.assertIsNone(os.environ.get("TDQ_SURFACE_LOG"))


if __name__ == "__main__":
    unittest.main()
