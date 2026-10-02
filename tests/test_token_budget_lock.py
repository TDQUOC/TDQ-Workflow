"""Tệp khoá token — `scripts/token_budget.py` và rule trần của `doc_lint`.

Vì sao phải có tệp khoá, và vì sao không dùng đại lượng thay thế: `doc_lint` chạy ở CI, nơi repo
cố ý không cài công cụ ngoài, nên nó KHÔNG có tokenizer. Đo trên cả 43 file reference
(2026-10-02): token/dòng dao động 11,6-47,2 (lệch 4,1 lần) và byte/token 2,20-3,98 (lệch 1,81
lần) — không đại lượng nào đủ tin để cưỡng chế một trần chính xác.

Nên một script CÓ tokenizer ghi `{đường dẫn: {token, sha256}}`, và `doc_lint` chỉ so `sha256`:
khớp thì con số token còn đúng và đem so trần được; không khớp thì báo số đo đã cũ. Cùng cơ chế
lockfile của npm/pip — con số đã đo được khoá bằng hash của thứ đã đo.

Nhóm chạy riêng bằng `-k`: `sinh`, `tran_token`, `khoa_cu`, `log`.
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from helper import ROOT, co_bo_dem_token

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import doc_lint  # noqa: E402
import token_budget  # noqa: E402

CAN_TOKENIZER = unittest.skipUnless(co_bo_dem_token(), "máy này không có bộ đếm token")


class BaseKhoa(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.vung = os.path.join(self.tmp, "skills", "tdq-thu", "references")
        os.makedirs(self.vung, exist_ok=True)
        os.makedirs(os.path.join(self.tmp, "docs", "tdq"), exist_ok=True)

    def ghi_md(self, ten, so_dong=20):
        duong = os.path.join(self.vung, ten)
        with io.open(duong, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("# Thử\n\n## Mục\n\n" + "một dòng nội dung thật\n" * so_dong)
        return duong

    def khoa(self):
        with io.open(os.path.join(self.tmp, token_budget.FILE_KHOA), encoding="utf-8") as fh:
            return json.load(fh)

    def _ghi_khoa(self, ban_ghi):
        """Viết tệp khoá bằng tay, ĐÚNG khuôn `sinh_khoa` ghi ra — nhờ vậy nhóm `tran_token` và
        `khoa_cu` kiểm được mà không cần tokenizer trên máy."""
        duong = os.path.join(self.tmp, token_budget.FILE_KHOA)
        os.makedirs(os.path.dirname(duong), exist_ok=True)
        with io.open(duong, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(ban_ghi, fh, ensure_ascii=False, indent=2, sort_keys=True)
            fh.write("\n")


@CAN_TOKENIZER
class SinhKhoa(BaseKhoa):
    def test_sinh_moi_file_mot_ban_ghi_co_token_va_sha(self):
        self.ghi_md("a.md")
        self.ghi_md("b.md")
        token_budget.sinh_khoa(self.tmp)
        khoa = self.khoa()
        self.assertEqual(sorted(khoa), ["skills/tdq-thu/references/a.md",
                                        "skills/tdq-thu/references/b.md"])
        for ban in khoa.values():
            self.assertGreater(ban["token"], 0)
            self.assertEqual(len(ban["sha256"]), 64)

    def test_sinh_hai_lan_ra_cung_noi_dung(self):
        self.ghi_md("a.md")
        token_budget.sinh_khoa(self.tmp)
        mot = io.open(os.path.join(self.tmp, token_budget.FILE_KHOA), encoding="utf-8").read()
        token_budget.sinh_khoa(self.tmp)
        hai = io.open(os.path.join(self.tmp, token_budget.FILE_KHOA), encoding="utf-8").read()
        self.assertEqual(mot, hai)

    def test_sinh_bo_ban_ghi_cua_file_da_xoa(self):
        duong = self.ghi_md("a.md")
        self.ghi_md("b.md")
        token_budget.sinh_khoa(self.tmp)
        os.remove(duong)
        token_budget.sinh_khoa(self.tmp)
        self.assertEqual(sorted(self.khoa()), ["skills/tdq-thu/references/b.md"])


class TranToken(BaseKhoa):
    """Trần cưỡng chế được KHÔNG CẦN tokenizer — đó là toàn bộ lý do tệp khoá tồn tại."""

    def test_tran_token_file_vuot_thi_bao_loi(self):
        duong = self.ghi_md("to.md")
        rel = "skills/tdq-thu/references/to.md"
        self._ghi_khoa({rel: {"token": token_budget.TRAN_TOKEN + 1,
                              "sha256": token_budget.sha_file(duong)}})
        loi = token_budget.kiem_khoa(self.tmp)
        self.assertTrue(loi)
        self.assertIn("to.md", loi[0])
        self.assertIn(str(token_budget.TRAN_TOKEN), loi[0])

    def test_tran_token_file_duoi_tran_thi_im(self):
        duong = self.ghi_md("nho.md")
        rel = "skills/tdq-thu/references/nho.md"
        self._ghi_khoa({rel: {"token": 100, "sha256": token_budget.sha_file(duong)}})
        self.assertEqual(token_budget.kiem_khoa(self.tmp), [])

    def test_tran_token_khong_can_tokenizer(self):
        """Phép kiểm không được gọi bộ đếm token — CI không có nó."""
        nguon = io.open(os.path.join(ROOT, "scripts", "token_budget.py"), encoding="utf-8").read()
        than = nguon.split("def kiem_khoa", 1)[1].split("\ndef ", 1)[0]
        self.assertNotIn("count_tokens", than)
        self.assertNotIn("nap_bo_dem", than)


class KhoaCu(BaseKhoa):
    def test_khoa_cu_sha_lech_thi_bao_so_do_da_cu(self):
        self.ghi_md("a.md")
        rel = "skills/tdq-thu/references/a.md"
        self._ghi_khoa({rel: {"token": 100, "sha256": "0" * 64}})
        loi = token_budget.kiem_khoa(self.tmp)
        self.assertTrue(loi)
        self.assertIn("stale", loi[0].lower())

    def test_khoa_cu_file_moi_chua_co_ban_ghi(self):
        self.ghi_md("a.md")
        self._ghi_khoa({})
        loi = token_budget.kiem_khoa(self.tmp)
        self.assertTrue(loi)
        self.assertIn("a.md", loi[0])

    def test_khoa_cu_khong_co_tep_khoa_thi_im(self):
        """Repo chưa sinh khoá lần nào thì không phải lỗi — việc 'phải có khoá' do CI lo."""
        self.ghi_md("a.md")
        self.assertEqual(token_budget.kiem_khoa(self.tmp), [])


class LogService(BaseKhoa):
    @CAN_TOKENIZER
    def test_log_tat_duoc_bang_bien_moi_truong(self):
        self.ghi_md("a.md")
        ra = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "token_budget.py"),
                             "--goc", self.tmp],
                            capture_output=True, encoding="utf-8", text=True,
                            env=dict(os.environ, TDQ_LOG="0"))
        self.assertEqual(ra.stderr.strip(), "")

    @CAN_TOKENIZER
    def test_log_bat_mac_dinh_co_timestamp(self):
        self.ghi_md("a.md")
        ra = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "token_budget.py"),
                             "--goc", self.tmp],
                            capture_output=True, encoding="utf-8", text=True,
                            env=dict(os.environ, TDQ_LOG="1"))
        self.assertRegex(ra.stderr, r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")


class DocLintCamChe(unittest.TestCase):
    """`doc_lint` phải mang rule này, nếu không trần chỉ là một con số trong tài liệu."""

    def test_tran_token_doc_lint_co_rule(self):
        self.assertTrue(hasattr(doc_lint, "kiem_tran_token"),
                        "doc_lint thiếu phép kiểm trần token")

    def test_khoa_cu_repo_nay_dang_khop(self):
        """Khoá của chính repo này phải đang đúng — nếu không, mọi con số trần đều vô nghĩa."""
        self.assertEqual(token_budget.kiem_khoa(ROOT), [])


if __name__ == "__main__":
    unittest.main()
