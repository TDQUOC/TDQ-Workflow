"""Bộ tự kiểm & tự vá chạy ở MÁY ĐÍCH — nơi không ai sửa được nếu nó sai.

Vì `setup` được trao quyền tối đa (cài gói, sửa cả config mức người dùng, báo lại sau), ba
hàng rào phải được khoá bằng test chứ không bằng lời hứa trong tài liệu:
  - phát hiện file lệch dù chỉ 1 byte;
  - thiếu lệnh ngoài thì báo tên, tuyệt đối không crash (crash ở máy lạ = mất luôn đường vá);
  - ghi đè thì phải có bản sao lưu, và không đường in nào lộ GIÁ TRỊ khoá.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

import helper  # noqa: F401  — nạp sys.path cho scripts/
import build_portable
import tdq_checkportable

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "tdq_checkportable.py")


def chay(*args, env=None):
    proc = subprocess.run(
        [sys.executable, SCRIPT, *args],
        capture_output=True, text=True, timeout=120,
        env=dict(os.environ, **(env or {})),
    )
    return proc.returncode, proc.stdout, proc.stderr


class CoBanSinh(unittest.TestCase):
    """Mỗi test chạy trên một bản portable_claude sinh thật, không phải cây giả."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.goc = build_portable.sinh_ban_claude(ROOT, self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()


class TestCheck(CoBanSinh):
    def test_ban_sinh_sach_thi_exit_0(self):
        ma, out, _ = chay("check", "--root", self.goc)
        self.assertEqual(ma, 0, out)

    def test_phat_hien_file_sua_1_byte(self):
        duong = os.path.join(self.goc, "README.md")
        with open(duong, "a", encoding="utf-8") as f:
            f.write(".")
        ma, out, _ = chay("check", "--root", self.goc)
        self.assertNotEqual(ma, 0)
        self.assertIn("README.md", out)

    def test_phat_hien_file_thieu(self):
        os.remove(os.path.join(self.goc, "README.md"))
        ma, out, _ = chay("check", "--root", self.goc)
        self.assertNotEqual(ma, 0)
        self.assertIn("README.md", out)


class TestMoiTruong(CoBanSinh):
    def test_bao_thieu_git_khong_crash(self):
        """Lệnh ngoài vắng mặt là chuyện thường ở máy lạ — phải báo, không được ném exception."""
        ket_qua = tdq_checkportable.kiem_moi_truong(
            {"python_min": "3.8", "external_commands": ["khong-ton-tai-abc"],
             "mcp_servers": []},
            tim_lenh=lambda ten: None,
        )
        self.assertTrue(any("khong-ton-tai-abc" in d for d in ket_qua["thieu"]))

    def test_python_qua_cu_thi_bao(self):
        ket_qua = tdq_checkportable.kiem_moi_truong(
            {"python_min": "99.0", "external_commands": [], "mcp_servers": []})
        self.assertTrue(any("python" in d.lower() for d in ket_qua["thieu"]))


class TestSetup(CoBanSinh):
    def test_setup_backup_truoc_khi_ghi_de(self):
        duong = os.path.join(self.goc, "README.md")
        with open(duong, "a", encoding="utf-8") as f:
            f.write("nội dung lệch")
        tdq_checkportable.ghi_de_co_backup(duong, "nội dung mới")
        sao_luu = [t for t in os.listdir(self.goc) if t.startswith("README.md.tdq-bak-")]
        self.assertEqual(len(sao_luu), 1, "phải có đúng một bản sao lưu")
        with open(os.path.join(self.goc, sao_luu[0]), encoding="utf-8") as f:
            self.assertIn("nội dung lệch", f.read())

    def test_setup_khong_dung_thi_bao_da_lam_gi(self):
        ma, out, _ = chay("setup", "--root", self.goc)
        self.assertEqual(ma, 0, out)
        self.assertTrue(out.strip(), "setup phải báo lại việc đã làm, kể cả khi không sửa gì")


class TestVongFix1(CoBanSinh):
    """Năm khuyết tật QC độc lập bắt được — mỗi cái một test khoá lại."""

    def test_chay_khong_can_root(self):
        """Chính tài liệu bảo chạy `python3 .claude/tdq/scripts/… check` từ gốc bundle.

        Script nằm sâu hai tầng dưới gốc, nên mặc định `../..` trỏ vào `.claude/tdq` —
        nơi không có `manifest.json`. Lệnh đầu tiên người dùng gõ mà lỗi thì bundle coi
        như hỏng ngay từ bước 0.
        """
        ma, out, _ = chay("check")
        # chạy với cwd bất kỳ: gốc phải suy từ vị trí script, không phải từ cwd
        ma, out, _ = chay("check", env={})
        duong = os.path.join(self.goc, ".claude", "tdq", "scripts", "tdq_checkportable.py")
        proc = subprocess.run([sys.executable, duong, "check"],
                              capture_output=True, text=True, cwd=self.goc, timeout=120)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("SẠCH", proc.stdout)

    def test_setup_va_that_va_bao_dung(self):
        """`setup` không được báo thành công khi bundle vẫn hỏng."""
        os.remove(os.path.join(self.goc, ".mcp.json"))
        ma, out, _ = chay("setup", "--root", self.goc)
        self.assertIn(".mcp.json", out)
        self.assertEqual(ma, 0, "sinh lại được thì phải xong sạch")
        self.assertTrue(os.path.isfile(os.path.join(self.goc, ".mcp.json")))

        # File không tự vá được thì phải nói thẳng bằng exit code, không im lặng exit 0.
        os.remove(os.path.join(self.goc, ".claude", "tdq", "scripts", "tdq_state.py"))
        ma, out, _ = chay("setup", "--root", self.goc)
        self.assertNotEqual(ma, 0, "còn thiếu file mà vẫn exit 0 là báo láo")
        self.assertIn("tdq_state.py", out)

    def test_setup_ghi_de_settings_thi_co_backup(self):
        duong = os.path.join(self.goc, ".claude", "settings.json")
        with open(duong, "w", encoding="utf-8") as f:
            f.write('{"hooks": {}}')
        chay("setup", "--root", self.goc)
        sao_luu = [t for t in os.listdir(os.path.dirname(duong))
                   if t.startswith("settings.json.tdq-bak-")]
        self.assertEqual(len(sao_luu), 1, "ghi đè cấu hình mà không sao lưu")

    def test_manifest_rong_la_loi(self):
        with open(os.path.join(self.goc, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump({"files": {}, "version": "x", "python_min": "3.8",
                       "external_commands": [], "mcp_servers": []}, f)
        ma, out, _ = chay("check", "--root", self.goc)
        self.assertNotEqual(ma, 0, "manifest rỗng là hỏng, không phải sạch")


class TestVongFix2(CoBanSinh):
    """Năm điểm nhỏ QC vòng 2 bắt được."""

    def test_check_bao_trang_thai_bien_mcp(self):
        """`to_ten_khoa` phải có caller thật, và chỉ in TÊN biến kèm có/chưa đặt."""
        ma, out, _ = chay("check", "--root", self.goc,
                          env={"TAVILY_" + "API" + "_KEY": "gia-tri-khong-duoc-lo"})
        self.assertIn("TAVILY", out)
        self.assertNotIn("gia-tri-khong-duoc-lo", out)

    def test_setup_bundle_chi_doc(self):
        """Bundle chép qua mạng hay giải nén sai quyền là chuyện thường — báo, đừng traceback."""
        os.chmod(self.goc, 0o555)
        try:
            os.remove(os.path.join(self.goc, ".mcp.json"))
        except PermissionError:
            pass
        try:
            ma, out, bat = chay("setup", "--root", self.goc)
            self.assertNotIn("Traceback", bat)
        finally:
            os.chmod(self.goc, 0o755)

    def test_docstring_khong_hua_qua(self):
        noi_dung = tdq_checkportable.__doc__ or ""
        for cum in ("cài gói", "mức người dùng"):
            self.assertNotIn(cum, noi_dung, f"docstring hứa quá năng lực: {cum!r}")

    def test_settings_mat_trang_bao_ro(self):
        """Sinh lại được phần hook nhưng khối `env` thì không — nói rõ, đừng nói nước đôi."""
        duong = os.path.join(self.goc, ".claude", "settings.json")
        os.remove(duong)
        ma, out, _ = chay("setup", "--root", self.goc)
        self.assertIn("env", out, "phải nói rõ khối env không tái tạo được")
        self.assertTrue(os.path.isfile(duong), "phần hook vẫn phải được dựng lại")

    def test_setup_khong_them_file_la(self):
        """Bản codex không có `.mcp.json` trong manifest — `setup` không được tự thêm vào."""
        with tempfile.TemporaryDirectory() as d:
            codex = build_portable.sinh_ban_codex(ROOT, d)
            chay("setup", "--root", codex)
            self.assertFalse(os.path.isfile(os.path.join(codex, ".mcp.json")),
                             "setup thêm file không có trong manifest")
            ma, _, _ = chay("check", "--root", codex)
            self.assertEqual(ma, 0, "setup làm bẩn bundle codex")


class TestKhongLoSecret(unittest.TestCase):
    def test_khong_in_gia_tri_secret(self):
        """Chỉ được in TÊN biến. In giá trị là rò khoá vào log của người khác."""
        moi_truong = {"TAVILY_" + "API" + "_KEY": "gia-tri-that-khong-duoc-lo"}
        dong = tdq_checkportable.to_ten_khoa(moi_truong)
        self.assertNotIn("gia-tri-that-khong-duoc-lo", "\n".join(dong))
        self.assertTrue(any("TAVILY" in d for d in dong))

    def test_mcp_json_cua_ban_sinh_khong_lot_gia_tri(self):
        with tempfile.TemporaryDirectory() as d:
            goc = build_portable.sinh_ban_claude(ROOT, d)
            with open(os.path.join(goc, ".mcp.json"), encoding="utf-8") as f:
                cau_hinh = json.load(f)
            for may_chu in cau_hinh["mcpServers"].values():
                for gia_tri in may_chu.get("env", {}).values():
                    self.assertTrue(gia_tri.startswith("${"),
                                    "env của MCP chỉ được trỏ biến, không ghi giá trị")


class TestTrustCodex(unittest.TestCase):
    """`setup --trust` — đường DUY NHẤT được phép ghi ra ngoài bundle.

    Vì sao khoá kỹ: mọi test khác trong file này chỉ động tới cây bundle tạm, còn đường này
    ghi vào thư mục cấu hình mức người dùng. Ba chốt phải đúng, không được chỉ nằm trong
    tài liệu: không có cờ thì tuyệt đối không chạm; có cờ thì luôn để lại bản sao lưu; chạy
    hai lần không sinh block trùng.

    Mọi test ở đây trỏ `CODEX_HOME` vào thư mục tạm, nên `~/.codex` thật không bao giờ bị đụng.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.bundle = build_portable.sinh_ban_codex(ROOT, self._tmp.name)
        self.codex_home = os.path.join(self._tmp.name, "codexhome")
        os.makedirs(self.codex_home)
        self.config = os.path.join(self.codex_home, "config.toml")

    def tearDown(self):
        self._tmp.cleanup()

    def _ghi_config(self, noi_dung):
        with open(self.config, "w", encoding="utf-8") as f:
            f.write(noi_dung)

    def _sao_luu_co_duoc(self):
        return [t for t in os.listdir(self.codex_home) if ".tdq-bak-" in t]

    def test_setup_tran_khong_cham_config_nguoi_dung(self):
        self._ghi_config('[mcp_servers.x]\ncommand = "npx"\n')
        truoc = open(self.config, encoding="utf-8").read()
        ma, out, _ = chay("setup", "--root", self.bundle, env={"CODEX_HOME": self.codex_home})
        self.assertEqual(open(self.config, encoding="utf-8").read(), truoc,
                         "setup không cờ mà vẫn ghi vào config mức người dùng")
        self.assertEqual(self._sao_luu_co_duoc(), [])
        self.assertEqual(ma, 0, out)

    def test_trust_ghi_block_va_giu_nguyen_phan_con_lai(self):
        self._ghi_config('[mcp_servers.x]\ncommand = "npx"\n')
        ma, out, _ = chay("setup", "--trust", "--root", self.bundle,
                          env={"CODEX_HOME": self.codex_home})
        self.assertEqual(ma, 0, out)
        moi = open(self.config, encoding="utf-8").read()
        self.assertIn("[mcp_servers.x]", moi, "phần cũ của file bị mất")
        self.assertIn(f'[projects."{os.path.realpath(self.bundle)}"]', moi)
        self.assertIn('trust_level = "trusted"', moi)

    def test_trust_luon_de_lai_ban_sao_luu(self):
        self._ghi_config("# cu\n")
        chay("setup", "--trust", "--root", self.bundle, env={"CODEX_HOME": self.codex_home})
        sao_luu = self._sao_luu_co_duoc()
        self.assertEqual(len(sao_luu), 1, sao_luu)
        with open(os.path.join(self.codex_home, sao_luu[0]), encoding="utf-8") as f:
            self.assertEqual(f.read(), "# cu\n", "bản sao lưu không giữ đúng nội dung cũ")

    def test_chay_hai_lan_khong_sinh_block_trung(self):
        for _ in range(2):
            chay("setup", "--trust", "--root", self.bundle,
                 env={"CODEX_HOME": self.codex_home})
        noi_dung = open(self.config, encoding="utf-8").read()
        self.assertEqual(noi_dung.count('trust_level = "trusted"'), 1, noi_dung)

    def test_trust_tao_duoc_file_khi_chua_co(self):
        ma, out, _ = chay("setup", "--trust", "--root", self.bundle,
                          env={"CODEX_HOME": self.codex_home})
        self.assertEqual(ma, 0, out)
        self.assertTrue(os.path.isfile(self.config))
        self.assertEqual(self._sao_luu_co_duoc(), [], "file mới thì không có gì để sao lưu")

    def test_check_bao_trang_thai_trusted(self):
        _, truoc, _ = chay("check", "--root", self.bundle,
                           env={"CODEX_HOME": self.codex_home})
        self.assertIn("chưa trusted", truoc.lower())
        chay("setup", "--trust", "--root", self.bundle, env={"CODEX_HOME": self.codex_home})
        _, sau, _ = chay("check", "--root", self.bundle, env={"CODEX_HOME": self.codex_home})
        self.assertIn("trusted", sau.lower())
        self.assertNotIn("chưa trusted", sau.lower())

    def test_check_khong_crash_khi_thieu_thu_muc_cau_hinh(self):
        trong = os.path.join(self._tmp.name, "khong-ton-tai")
        ma, out, _ = chay("check", "--root", self.bundle, env={"CODEX_HOME": trong})
        self.assertEqual(ma, 0, out)
        self.assertIn("chưa trusted", out.lower())

    def test_log_tat_duoc_va_neu_ten_file_da_ghi(self):
        _, _, bat = chay("setup", "--trust", "--root", self.bundle,
                         env={"CODEX_HOME": self.codex_home})
        self.assertIn("config.toml", bat, "log phải nêu file đã ghi ra ngoài bundle")
        with tempfile.TemporaryDirectory() as d2:
            _, _, tat = chay("setup", "--trust", "--root", self.bundle,
                             env={"CODEX_HOME": d2, "TDQ_LOG": "0"})
        self.assertEqual(tat.strip(), "", "TDQ_LOG=0 phải im hoàn toàn")

    def test_trust_khong_cham_bundle(self):
        chay("setup", "--trust", "--root", self.bundle, env={"CODEX_HOME": self.codex_home})
        ma, out, _ = chay("check", "--root", self.bundle, env={"CODEX_HOME": self.codex_home})
        self.assertEqual(ma, 0, out)


if __name__ == "__main__":
    unittest.main()
