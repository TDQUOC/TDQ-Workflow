"""Khoá khuôn CI ba hệ — yêu cầu 2026-09-21-0029 (T4.1).

Chỉ dùng thư viện chuẩn: suite phải chạy được trên máy chưa cài gì, nên test không kéo PyYAML
vào. File workflow cố ý viết danh sách dạng `[a, b]` trên một dòng để đọc được bằng regex.

Mỗi luật dưới đây là một lần suite từng xanh trên máy dev mà đỏ trên máy sạch:
- `PYTHONUTF8` không được đặt: đặt nó là che mất đúng lỗi cp1252 mà T3.2 vừa vá (273 ca).
- Không `pip install`: suite phải xanh khi thiếu pytest/tokenizer/graphify — phần thiếu thành skip.
- `core.autocrlf` tắt TRƯỚC checkout: runner Windows bật sẵn, và CRLF làm lệch sha256.
"""
import os
import re
import unittest

from helper import ROOT

DUONG_CI = os.path.join(ROOT, ".github", "workflows", "test.yml")
HE = {"ubuntu-latest", "macos-latest", "windows-latest"}
PHIEN_BAN = {"3.10", "3.13"}
LENH_SUITE = "python -m unittest discover tests"


def _doc():
    with open(DUONG_CI, encoding="utf-8") as f:
        return f.read()


def _danh_sach(noi_dung, khoa):
    khop = re.search(rf"^\s*{khoa}:\s*\[([^\]]*)\]", noi_dung, re.MULTILINE)
    if not khop:
        return set()
    return {m.strip().strip("'\"") for m in khop.group(1).split(",") if m.strip()}


class KhuonCi(unittest.TestCase):
    def setUp(self):
        self.assertTrue(os.path.isfile(DUONG_CI), "thiếu .github/workflows/test.yml")
        self.noi_dung = _doc()

    def test_du_sau_to_hop(self):
        he, ban = _danh_sach(self.noi_dung, "os"), _danh_sach(self.noi_dung, "python-version")
        self.assertEqual(he, HE)
        self.assertEqual(ban, PHIEN_BAN)
        self.assertEqual(len(he) * len(ban), 6)

    def test_mot_to_hop_do_khong_huy_cac_to_hop_con_lai(self):
        self.assertRegex(self.noi_dung, r"fail-fast:\s*false")

    def test_chay_dung_lenh_suite_cua_repo(self):
        self.assertIn(LENH_SUITE, self.noi_dung)

    def test_khong_cai_cong_cu_ngoai(self):
        self.assertNotRegex(self.noi_dung, r"pip3? install|npm install|uv tool install")

    def test_khong_che_loi_ma_hoa(self):
        self.assertNotIn("PYTHONUTF8", self.noi_dung)
        self.assertNotIn("PYTHONIOENCODING", self.noi_dung)

    def test_tat_autocrlf_truoc_checkout(self):
        crlf = self.noi_dung.find("core.autocrlf")
        checkout = self.noi_dung.find("actions/checkout")
        self.assertGreaterEqual(crlf, 0, "chưa tắt core.autocrlf")
        self.assertLess(crlf, checkout, "tắt autocrlf SAU checkout thì file đã bị đổi rồi")

    def test_moi_action_ghim_phien_ban(self):
        for action in re.findall(r"uses:\s*(\S+)", self.noi_dung):
            with self.subTest(action=action):
                self.assertRegex(action, r"@v\d+$")


if __name__ == "__main__":
    unittest.main()
