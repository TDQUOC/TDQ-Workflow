"""P3 (T3.1, T3.2) — lệnh `check` của tầng CLI Codex.

Hợp đồng: `check` KHÔNG BAO GIỜ làm hỏng cổng chọn mode. Máy thiếu `codex`,
`codex` treo, người dùng chưa đồng ý — cả ba đều là câu trả lời "không chọn
được KÈM LÝ DO", exit 0, chứ không phải traceback.

Bốn nguyên nhân không chọn được phải ra BỐN `ly_do` khác nhau: người đọc cần
biết mình phải làm gì tiếp, "không dùng được" thì không sửa được.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_codex  # noqa: E402

CLI = os.path.join(ROOT, "scripts", "tdq_codex.py")


class RepoTam(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = os.path.realpath(self._tmp.name)
        os.makedirs(os.path.join(self.cwd, "docs", "tdq"), exist_ok=True)

    def tearDown(self):
        self._tmp.cleanup()


class CheckTest(RepoTam):
    def test_thieu_codex_van_exit_0(self):
        with mock.patch("shutil.which", return_value=None):
            kq = tdq_codex.check(self.cwd)
        self.assertFalse(kq["co"])
        self.assertFalse(kq["chay_duoc"])
        self.assertTrue(kq["ly_do"].strip())
        self.assertTrue(kq["goi_y"].strip(), "thiếu thì phải nói cách cài")

    def test_du_bon_truong_hop_dong(self):
        with mock.patch("shutil.which", return_value=None):
            kq = tdq_codex.check(self.cwd)
        self.assertEqual({"co", "chay_duoc", "phien_ban", "ly_do", "goi_y"},
                         set(kq))

    def test_co_codex_va_song_thi_chay_duoc(self):
        with mock.patch("shutil.which", return_value="/usr/bin/codex"), \
             mock.patch.object(tdq_codex, "_kiem_song",
                               return_value=(True, "codex 1.2.3", "")):
            tdq_codex.dat_co_dong_y(self.cwd, True, model="gpt-5")
            kq = tdq_codex.check(self.cwd)
        self.assertTrue(kq["co"])
        self.assertTrue(kq["chay_duoc"])
        self.assertIn("1.2.3", kq["phien_ban"])

    def test_kiem_song_qua_han_thi_khong_chay_duoc(self):
        with mock.patch("shutil.which", return_value="/usr/bin/codex"), \
             mock.patch.object(tdq_codex, "_kiem_song",
                               return_value=(False, "", "quá hạn 30s")):
            tdq_codex.dat_co_dong_y(self.cwd, True, model="gpt-5")
            kq = tdq_codex.check(self.cwd)
        self.assertFalse(kq["chay_duoc"])
        self.assertIn("quá hạn", kq["ly_do"])

    def test_bon_nguyen_nhan_ra_bon_ly_do_khac_nhau(self):
        """Q3 — bốn nguyên nhân, bốn câu khác nhau."""
        ly_do = []

        # 1. Chưa cài codex.
        with mock.patch("shutil.which", return_value=None):
            ly_do.append(tdq_codex.check(self.cwd)["ly_do"])

        # 2. Có codex nhưng người dùng chưa đồng ý.
        with mock.patch("shutil.which", return_value="/usr/bin/codex"), \
             mock.patch.object(tdq_codex, "_kiem_song",
                               return_value=(True, "codex 1", "")):
            ly_do.append(tdq_codex.check(self.cwd)["ly_do"])

        # 3. Đã đồng ý nhưng codex không chạy được.
        tdq_codex.dat_co_dong_y(self.cwd, True, model="gpt-5")
        with mock.patch("shutil.which", return_value="/usr/bin/codex"), \
             mock.patch.object(tdq_codex, "_kiem_song",
                               return_value=(False, "", "quá hạn 30s")):
            ly_do.append(tdq_codex.check(self.cwd)["ly_do"])

        # 4. Đã đồng ý, codex sống, nhưng thiếu tên model.
        tdq_codex.dat_co_dong_y(self.cwd, True, model=None)
        with mock.patch("shutil.which", return_value="/usr/bin/codex"), \
             mock.patch.object(tdq_codex, "_kiem_song",
                               return_value=(True, "codex 1", "")):
            ly_do.append(tdq_codex.check(self.cwd)["ly_do"])

        self.assertEqual(len(ly_do), 4)
        self.assertEqual(len(set(ly_do)), 4, f"lý do trùng nhau: {ly_do}")
        for d in ly_do:
            self.assertTrue(d.strip())

    def test_nguoi_dung_tu_choi_thi_co_ly_do_rieng(self):
        tdq_codex.dat_co_dong_y(self.cwd, False)
        with mock.patch("shutil.which", return_value="/usr/bin/codex"), \
             mock.patch.object(tdq_codex, "_kiem_song",
                               return_value=(True, "codex 1", "")):
            kq = tdq_codex.check(self.cwd)
        self.assertFalse(kq["chay_duoc"])
        self.assertTrue(kq["ly_do"].strip())


class CoDongYTest(RepoTam):
    def test_ghi_va_doc_lai_du_ba_khoa(self):
        tdq_codex.dat_co_dong_y(self.cwd, True, model="gpt-5")
        co = tdq_codex.doc_co_dong_y(self.cwd)
        self.assertTrue(co["nguoi_dung_dong_y"])
        self.assertEqual(co["codex_model"], "gpt-5")
        self.assertTrue(co["quyet_dinh_luc"], "phải ghi mốc thời gian quyết định")

    def test_chua_co_file_thi_tra_mac_dinh_chua_dong_y(self):
        co = tdq_codex.doc_co_dong_y(self.cwd)
        self.assertFalse(co["nguoi_dung_dong_y"])

    def test_file_hong_khong_lam_sap_cong_chon_mode(self):
        duong = os.path.join(self.cwd, tdq_codex.CO_REL)
        os.makedirs(os.path.dirname(duong), exist_ok=True)
        with open(duong, "w", encoding="utf-8") as f:
            f.write("{ hỏng")
        self.assertFalse(tdq_codex.doc_co_dong_y(self.cwd)["nguoi_dung_dong_y"])


class CheckCliTest(RepoTam):
    def test_lenh_check_json_exit_0_ngay_ca_khi_thieu_codex(self):
        proc = subprocess.run(
            [sys.executable, CLI, "check", "--json"], cwd=self.cwd,
            capture_output=True, text=True, encoding="utf-8", timeout=90,
            stdin=subprocess.DEVNULL,
            env=dict(os.environ, PATH="/nonexistent-path-for-test"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertFalse(data["co"])
        self.assertTrue(data["ly_do"])


class GitignoreTest(unittest.TestCase):
    def test_co_dong_y_duoc_gitignore(self):
        """Cờ mức máy là chuyện riêng của máy, không được vào lịch sử repo."""
        proc = subprocess.run(
            ["git", "check-ignore", "-q", tdq_codex.CO_REL], cwd=ROOT,
            capture_output=True, text=True, encoding="utf-8", timeout=30,
            stdin=subprocess.DEVNULL)
        self.assertEqual(proc.returncode, 0,
                         f"{tdq_codex.CO_REL} chưa được gitignore")


if __name__ == "__main__":
    unittest.main()
