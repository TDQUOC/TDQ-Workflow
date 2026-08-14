"""Test scripts/code_rule_scan.py — T5.1 viết đỏ trước, T5.2 làm xanh.

Hợp đồng CLI: `python3 scripts/code_rule_scan.py [đường dẫn...] [--tat-ca|--im|--chi-tiet]`
- Không đường dẫn, không --tat-ca → chỉ quét file đã đổi theo git.
- Bảng kết quả in ra stdout, mỗi file một dòng kèm ngôn ngữ + trạng thái;
  chốt bằng dòng tổng `PASS: n · LỖI: n · CHƯA KIỂM ĐƯỢC: n`.
- Log service in ra stderr (mặc định bật, có timestamp); `--im` tắt hẳn.
- Exit 1 CHỈ khi có LỖI; linter thiếu → CHƯA KIỂM ĐƯỢC, exit 0.
"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helper import ROOT

SCRIPT = Path(ROOT) / "scripts" / "code_rule_scan.py"


def chay(args, path_rong=False, cwd=None):
    """Chạy script; path_rong=True → PATH không có linter nào (shutil.which trượt hết)."""
    env = dict(os.environ)
    if path_rong:
        env["PATH"] = "/khong-ton-tai-bin"
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, env=env, cwd=cwd or ROOT)


class CodeRuleScan(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        goc = Path(self.tmp.name)
        (goc / "a.py").write_text("x = 1\n", encoding="utf-8")
        (goc / "b.go").write_text("package main\n", encoding="utf-8")
        (goc / "c.txt").write_text("ngoai bang linter\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_scan_do_ngon_ngu(self):
        """Dò đúng ngôn ngữ theo đuôi file trên thư mục mẫu; đuôi lạ thì bỏ qua."""
        kq = chay([self.tmp.name], path_rong=True)
        self.assertIn("a.py", kq.stdout)
        self.assertIn("Python", kq.stdout)
        self.assertIn("b.go", kq.stdout)
        self.assertIn("Go", kq.stdout)
        self.assertNotIn("c.txt", kq.stdout)

    def test_scan_linter_thieu(self):
        """Linter thiếu → CHƯA KIỂM ĐƯỢC chứ không PASS; không phải LỖI nên exit 0."""
        kq = chay([self.tmp.name], path_rong=True)
        self.assertIn("CHƯA KIỂM ĐƯỢC", kq.stdout)
        self.assertIn("PASS: 0", kq.stdout)
        self.assertIn("LỖI: 0", kq.stdout)
        self.assertEqual(kq.returncode, 0, kq.stderr)

    def test_scan_im_tat_log(self):
        """--im tắt hẳn log stderr; mặc định log bật và có ít nhất một dòng."""
        co_log = chay([self.tmp.name], path_rong=True)
        self.assertNotEqual(co_log.stderr.strip(), "", "mặc định phải có log stderr")
        im = chay([self.tmp.name, "--im"], path_rong=True)
        self.assertEqual(im.stderr, "", "--im phải tắt log hoàn toàn")
        self.assertIn("CHƯA KIỂM ĐƯỢC", im.stdout, "--im vẫn phải in bảng kết quả")

    def test_scan_mac_dinh_chi_file_da_doi(self):
        """Không tham số → chỉ quét file git báo đổi, bỏ qua file sạch đã commit."""
        goc = Path(self.tmp.name)
        lenh_git = ["git", "-c", "user.email=t@t", "-c", "user.name=t"]
        subprocess.run(["git", "init", "-q"], cwd=goc, check=True)
        subprocess.run([*lenh_git, "add", "a.py"], cwd=goc, check=True)
        subprocess.run([*lenh_git, "commit", "-qm", "mau"], cwd=goc, check=True)
        # path_rong=False vì chính script cần gọi được git; trạng thái linter không
        # ảnh hưởng assertion — chỉ soi file nào có mặt trong bảng.
        kq = chay([], cwd=str(goc))
        self.assertIn("b.go", kq.stdout, "file chưa commit phải được quét")
        self.assertNotIn("a.py", kq.stdout, "file sạch đã commit phải được bỏ qua")


if __name__ == "__main__":
    unittest.main()
