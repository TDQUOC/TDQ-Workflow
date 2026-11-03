"""Sinh layout Antigravity theo yêu cầu, thay cho thư mục bundle đã bỏ.

Vì sao đổi cách làm: bản cũ chép sẵn 95 file vào `antigravity_portable/` rồi commit. Cách đó
nướng cứng thư mục nhà của MÁY DỰNG vào mọi đường dẫn trong config — bản dựng trên Windows ra
`C:\\Users\\admin/.gemini/...`, nên không commit được, và bản dựng trên macOS thì sai với mọi
người dùng Windows. Sinh tại chỗ trên chính máy cài thì `~` bung ra đúng của máy đó.

Ba bất biến khoá ở đây:
  1. Sinh ra đủ bốn thành phần agy cần: `plugin.json`, `skills/`, `hooks.json`, `mcp_config.json`.
  2. Chạy lần hai không đổi thêm gì — người ta chạy lại sau mỗi `git pull`.
  3. Từ chối ghi đè một thư mục không phải của mình. Đích mặc định nằm trong thư mục cấu hình
     của người dùng; xoá nhầm ở đó là mất dữ liệu thật.
"""
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_checkportable  # noqa: E402 — chủ của phép kiểm dấu ~

CLI = os.path.join(ROOT, "scripts", "build_portable.py")
THANH_PHAN = ("plugin.json", "hooks.json", "mcp_config.json", "skills")


def chay(*args, **kwargs):
    proc = subprocess.run([sys.executable, CLI, *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=300, **kwargs)
    return proc.returncode, proc.stdout, proc.stderr


def cay_file(goc):
    """{đường dẫn tương đối: nội dung bytes} — để so hai lần sinh."""
    ra = {}
    for thu_muc, _, ten_file in os.walk(goc):
        for ten in ten_file:
            duong = os.path.join(thu_muc, ten)
            with open(duong, "rb") as f:
                ra[os.path.relpath(duong, goc).replace(os.sep, "/")] = f.read()
    return ra


class SinhAgyTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dich = os.path.join(self.tmp.name, "tdq-workflow")

    def test_sinh_du_bon_thanh_phan(self):
        ma, out, err = chay("--sinh-agy", "--dich", self.dich)
        self.assertEqual(ma, 0, out + err)
        for ten in THANH_PHAN:
            with self.subTest(thanh_phan=ten):
                self.assertTrue(os.path.exists(os.path.join(self.dich, ten)),
                                f"thiếu {ten}\n{out}{err}")

    def test_plugin_json_dung_ten(self):
        chay("--sinh-agy", "--dich", self.dich)
        with io.open(os.path.join(self.dich, "plugin.json"), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["name"], "tdq-workflow")

    def test_duong_dan_tro_vao_dich_that(self):
        """Đường dẫn trong config phải là đích ĐANG cài, không phải một hằng nướng sẵn."""
        chay("--sinh-agy", "--dich", self.dich)
        with io.open(os.path.join(self.dich, "hooks.json"), encoding="utf-8") as f:
            du_lieu = json.load(f)
        lenh = [h["command"]
                for muc in du_lieu["hooks"].values()
                for nhom in muc for h in nhom["hooks"]]
        self.assertTrue(lenh, "hooks.json không khai lệnh nào")
        for c in lenh:
            with self.subTest(lenh=c[:40]):
                self.assertIn(os.path.basename(self.dich), c)
                # Chỉ soi `command`, không soi cả file: phần `description` có nhắc
                # `~/.gemini/config/config.json` cho NGƯỜI đọc, và dấu ~ ở đó là đúng chỗ.
                # Dấu ~ trong một `command` mới là lỗi — shell không bung nó trong nháy kép,
                # hook chết với exit 127.
                # Dùng chung phép kiểm với sản phẩm: `~` giữa tên 8.3 (`RUNNER~1`) là hợp lệ,
                # chỉ `~` đứng đầu token mới là chưa bung (2026-09-27).
                self.assertFalse(tdq_checkportable.con_dau_nga_chua_bung(c))

    def test_chay_hai_lan_khong_doi_gi(self):
        chay("--sinh-agy", "--dich", self.dich)
        truoc = cay_file(self.dich)
        chay("--sinh-agy", "--dich", self.dich)
        self.assertEqual(cay_file(self.dich), truoc)

    def test_tu_choi_thu_muc_khong_phai_cua_minh(self):
        """Đích mặc định nằm trong thư mục cấu hình người dùng — xoá nhầm là mất dữ liệu thật."""
        os.makedirs(self.dich)
        with io.open(os.path.join(self.dich, "tai-lieu-cua-toi.txt"), "w",
                     encoding="utf-8") as f:
            f.write("đừng xoá\n")
        ma, out, err = chay("--sinh-agy", "--dich", self.dich)
        self.assertNotEqual(ma, 0, out)
        self.assertTrue(os.path.exists(os.path.join(self.dich, "tai-lieu-cua-toi.txt")))

    def test_ghi_de_duoc_ban_cua_chinh_minh(self):
        """Cài lại sau `git pull` là việc thường, không được bắt người ta xoá tay."""
        chay("--sinh-agy", "--dich", self.dich)
        ma, out, err = chay("--sinh-agy", "--dich", self.dich)
        self.assertEqual(ma, 0, out + err)


class KhongLoSecretTest(unittest.TestCase):
    """Chuyển từ `test_checkportable.TestKhongLoSecret` (2026-09-21): bản claude bị gỡ, nhưng agy
    vẫn SINH `mcp_config.json` — và sinh ngay trên máy có khoá thật trong môi trường."""

    GIA_TRI = "gia-tri-that-khong-duoc-lo-" + "x" * 12

    def test_mcp_config_chi_tro_bien_khong_ghi_gia_tri(self):
        with tempfile.TemporaryDirectory() as tmp:
            dich = os.path.join(tmp, "tdq-workflow")
            moi_truong = dict(os.environ, TDQ_LOG="0", TAVILY_API_KEY=self.GIA_TRI,
                              TAVILY_API_KEY_BACKUP=self.GIA_TRI)
            ma, _, err = chay("--sinh-agy", "--dich", dich, env=moi_truong)
            self.assertEqual(ma, 0, err[-600:])
            with open(os.path.join(dich, "mcp_config.json"), encoding="utf-8") as f:
                may_chu = json.load(f)["mcpServers"]
            self.assertTrue(may_chu, "mcp_config.json không khai máy chủ nào")
            for ten, cau_hinh in may_chu.items():
                for bien, gia_tri in cau_hinh.get("env", {}).items():
                    with self.subTest(may_chu=ten, bien=bien):
                        self.assertTrue(gia_tri.startswith("${"),
                                        "env của MCP chỉ được trỏ biến, không ghi giá trị")
            for duong, noi_dung in cay_file(dich).items():
                with self.subTest(file=duong):
                    self.assertNotIn(self.GIA_TRI.encode(), noi_dung, "khoá thật lọt vào bản sinh")


class LogTest(unittest.TestCase):
    """Log service bật mặc định, tắt bằng TDQ_LOG=0 — yêu cầu bắt buộc của spec §4."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dich = os.path.join(self.tmp.name, "tdq-workflow")

    def test_log_bat_mac_dinh_co_timestamp(self):
        env = dict(os.environ)
        env.pop("TDQ_LOG", None)
        proc = subprocess.run([sys.executable, CLI, "--sinh-agy", "--dich", self.dich],
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", env=env, timeout=300)
        self.assertRegex(proc.stderr, r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")

    def test_log_tat_duoc(self):
        proc = subprocess.run([sys.executable, CLI, "--sinh-agy", "--dich", self.dich],
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", env=dict(os.environ, TDQ_LOG="0"), timeout=300)
        self.assertEqual(proc.stderr.strip(), "")


if __name__ == "__main__":
    unittest.main()
