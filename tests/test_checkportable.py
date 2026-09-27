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
        capture_output=True, encoding="utf-8", text=True, timeout=120,
        env=dict(os.environ, **(env or {})),
    )
    return proc.returncode, proc.stdout, proc.stderr


class CoBanSinh(unittest.TestCase):
    """Mỗi test chạy trên một layout agy sinh thật, không phải cây giả.

    2026-09-21: trước đây fixture này dựng `portable_claude`. Bundle đó đã bỏ — Claude Code đọc
    thẳng repo qua `.claude-plugin/marketplace.json`, không còn bản sao nào để kiểm. Layout agy
    là thứ DUY NHẤT còn sinh ra file thật kèm manifest, nên mọi hành vi check/setup/backup mà
    file này khoá vẫn còn nguyên ý nghĩa, chỉ đổi chỗ chạy.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.goc = build_portable.sinh_agy_tai_cho(
            ROOT, os.path.join(self._tmp.name, "tdq-workflow"))

    def tearDown(self):
        self._tmp.cleanup()


class TestCheck(CoBanSinh):
    @unittest.skipUnless(helper.co_lenh("graphify"), "chưa cài graphify — check báo MISSING, thoát 1")
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

    @unittest.skipUnless(helper.co_lenh("graphify"), "chưa cài graphify — check báo MISSING, thoát 1")
    def test_setup_khong_dung_thi_bao_da_lam_gi(self):
        ma, out, _ = chay("setup", "--root", self.goc)
        self.assertEqual(ma, 0, out)
        self.assertTrue(out.strip(), "setup phải báo lại việc đã làm, kể cả khi không sửa gì")


class TestVongFix1(CoBanSinh):
    """Năm khuyết tật QC độc lập bắt được — mỗi cái một test khoá lại."""


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


    def test_docstring_khong_hua_qua(self):
        noi_dung = tdq_checkportable.__doc__ or ""
        for cum in ("cài gói", "mức người dùng"):
            self.assertNotIn(cum, noi_dung, f"docstring hứa quá năng lực: {cum!r}")


class TestKhongLoSecret(unittest.TestCase):
    def test_khong_in_gia_tri_secret(self):
        """Chỉ được in TÊN biến. In giá trị là rò khoá vào log của người khác."""
        moi_truong = {"TAVILY_" + "API" + "_KEY": "gia-tri-that-khong-duoc-lo"}
        dong = tdq_checkportable.to_ten_khoa(moi_truong)
        self.assertNotIn("gia-tri-that-khong-duoc-lo", "\n".join(dong))
        self.assertTrue(any("TAVILY" in d for d in dong))


class DauNgaTest(unittest.TestCase):
    r"""`con_dau_nga_chua_bung` — phép kiểm dùng chung giữa sản phẩm và 3 file test.

    Bản cũ hỏi "có ký tự `~` không", nên trên runner Windows của GitHub (thư mục nhà dạng 8.3,
    `C:\Users\RUNNER~1\...`) nó báo đỏ oan, VÀ nuốt luôn nhánh `elif` phía sau — tức phép kiểm
    thật (bundle dựng dưới thư mục nhà máy khác) không bao giờ chạy ở đó.
    """

    def test_nga_dau_token_la_chua_bung(self):
        for lenh in ('py -3 "~/x/y.py"', "py -3 ~/x.py", "sh -c ~", 'py -3 "~someone/x.py"',
                     r'py -3 "~\x\y.py"'):
            with self.subTest(lenh=lenh):
                self.assertTrue(tdq_checkportable.con_dau_nga_chua_bung(lenh),
                                "dạng này shell phải bung mà trong nháy thì không bung")

    def test_nga_giua_ten_83_la_hop_le(self):
        """Đây là ca CI 35957834415 từng đỏ oan."""
        for lenh in (r"py -3 C:\Users\RUNNER~1\AppData\Local\Temp\t\hooks\a.py",
                     r"py -3 C:\Users\ADMINI~1\x.py"):
            with self.subTest(lenh=lenh):
                self.assertFalse(tdq_checkportable.con_dau_nga_chua_bung(lenh))

    def test_nga_lenh_rong_hay_none(self):
        for lenh in ("", None, "   "):
            with self.subTest(lenh=repr(lenh)):
                self.assertFalse(tdq_checkportable.con_dau_nga_chua_bung(lenh))


class TrustDaGoTest(unittest.TestCase):
    """Lớp trust/codex gỡ ở 0.50.0 — nhưng `_in_ket_qua` vẫn GỌI hai hàm đã xoá tới 2026-09-27.

    Nhánh đó chỉ chạy khi manifest khai `.codex/config.toml`, mà không bundle nào còn khai, nên
    nó là `NameError` ngồi chờ chứ không phải lỗi đã nổ. Hai ca dưới canh đúng chỗ đó.
    """

    def test_trust_khong_con_goi_api_da_xoa(self):
        """Đọc AST nên nhắc tên trong CHÚ THÍCH không tính — chỉ lời gọi thật mới tính."""
        import ast
        with open(os.path.join(ROOT, "scripts", "tdq_checkportable.py"), encoding="utf-8") as f:
            cay = ast.parse(f.read())
        ten_dung = {n.id for n in ast.walk(cay) if isinstance(n, ast.Name)}
        for ten in ("da_trusted", "duong_config_codex", "bat_trusted", "cai_tang_codex"):
            with self.subTest(ten=ten):
                self.assertNotIn(ten, ten_dung, f"{ten} đã xoá mà code còn gọi")

    def test_trust_manifest_co_codex_van_khong_no(self):
        """Ca hồi quy thật: manifest khai `.codex/config.toml` thì lệnh in kết quả KHÔNG được nổ."""
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as goc:
            manifest = {"files": {".codex/config.toml": "a" * 64}, "version": "0.0.0",
                        "python_min": "3.11", "external_commands": [], "mcp_servers": []}
            # Bọc stdout: lệnh này in báo cáo cho user, và để nó xả vào đầu ra của suite thì
            # lần sau ai đọc log test cũng phải đoán dòng `MISSING` đó từ đâu ra.
            with contextlib.redirect_stdout(io.StringIO()):
                tdq_checkportable._in_ket_qua(goc, manifest)


if __name__ == "__main__":
    unittest.main()
