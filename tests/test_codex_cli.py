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


def _codex_gia(thu_muc, kieu):
    """-> path of a fake `codex`. kieu: song | chet | treo | rong.

    Every `exec` call records its argv, its CODEX_HOME and that home's config.toml into
    `ghi-lai.json`, so a test can prove WHICH home the say hi went through.
    """
    duong = os.path.join(thu_muc, "codex")
    ghi = os.path.join(thu_muc, "ghi-lai.json")
    co_ket_qua = tdq_codex.CO_EXEC["ket_qua"]
    with open(duong, "w", encoding="utf-8") as f:
        f.write(f"""#!{sys.executable}
import json, os, sys, time
args = sys.argv[1:]
if args == ["--version"]:
    print("codex-cli 9.9.9")
    sys.exit(0)
home = os.environ.get("CODEX_HOME", "")
try:
    cfg = open(os.path.join(home, "config.toml"), encoding="utf-8").read()
except OSError:
    cfg = ""
with open({ghi!r}, "w", encoding="utf-8") as f:
    json.dump({{"args": args, "home": home, "config": cfg}}, f)
kieu = {kieu!r}
if kieu == "treo":
    time.sleep(30)
if kieu == "chet":
    print('ERROR: {{"status":400,"message":"model not supported"}}', file=sys.stderr)
    sys.exit(1)
if kieu == "song":
    with open(args[args.index({co_ket_qua!r}) + 1], "w", encoding="utf-8") as f:
        f.write("hi\\n")
sys.exit(0)
""")
    os.chmod(duong, 0o755)
    return duong, ghi


class KiemSongThatTest(RepoTam):
    """Bugfix 2026-09-14 — `check` phải gửi say hi thật, không chỉ `codex --version`.

    Đo thật: router chết mà `codex --version` vẫn exit 0, `check` báo chạy được, còn lượt thật
    quá hạn 60s.
    """

    def setUp(self):
        super().setUp()
        self.bin = os.path.join(self.cwd, "bin")
        os.makedirs(self.bin)
        may = os.path.join(self.cwd, "codex-may")
        os.makedirs(may)
        with open(os.path.join(may, "config.toml"), "w", encoding="utf-8") as f:
            f.write('model_provider = "r"\n\n[model_providers.r]\nbase_url = "http://r.invalid"\n')
        vao = mock.patch.dict(os.environ, {"CODEX_HOME": may})
        vao.start()
        self.addCleanup(vao.stop)
        tdq_codex.dat_co_dong_y(self.cwd, True, model="m-test")

    def _check(self, kieu):
        duong, ghi = _codex_gia(self.bin, kieu)
        with mock.patch("shutil.which", return_value=duong):
            kq = tdq_codex.check(self.cwd)
        return kq, ghi

    def _ghi_lai(self, ghi):
        with open(ghi, encoding="utf-8") as f:
            return json.load(f)

    def test_model_tra_loi_thi_chay_duoc(self):
        kq, ghi = self._check("song")
        self.assertTrue(kq["chay_duoc"], kq)
        self.assertIn("9.9.9", kq["phien_ban"])
        args = self._ghi_lai(ghi)["args"]
        self.assertEqual(args[0], tdq_codex.CO_EXEC["lenh"])
        self.assertIn("m-test", args, "say hi phải gọi đúng model đã cài")
        i = args.index(tdq_codex.CO_EXEC["sandbox"])
        self.assertEqual(args[i + 1], "read-only")

    def test_say_hi_di_qua_home_tam_mang_provider(self):
        _, ghi = self._check("song")
        ban_ghi = self._ghi_lai(ghi)
        self.assertTrue(ban_ghi["home"].startswith(tdq_codex._duong_home(self.cwd)),
                        "say hi phải đi qua CODEX_HOME tạm y như `run`")
        self.assertIn('model_provider = "r"', ban_ghi["config"])

    def test_home_tam_bi_don_sau_khi_kiem(self):
        self._check("song")
        goc = tdq_codex._duong_home(self.cwd)
        con = [t for t in os.listdir(goc)] if os.path.isdir(goc) else []
        self.assertEqual([t for t in con if t.startswith(tdq_codex.HOME_PREFIX)], [])

    def test_model_chet_thi_khong_chay_duoc_kem_loi(self):
        kq, _ = self._check("chet")
        self.assertFalse(kq["chay_duoc"])
        self.assertIn("say hi", kq["ly_do"])
        self.assertIn("400", kq["ly_do"], "lý do phải mang dòng lỗi thật của Codex")

    def test_tra_loi_rong_thi_khong_chay_duoc(self):
        kq, _ = self._check("rong")
        self.assertFalse(kq["chay_duoc"])
        self.assertIn("say hi", kq["ly_do"])

    def test_treo_thi_qua_han_va_van_don_home(self):
        duong, _ = _codex_gia(self.bin, "treo")
        song, _, ly_do = tdq_codex._kiem_song(duong, self.cwd, "m-test", timeout=2)
        self.assertFalse(song)
        self.assertIn("quá hạn", ly_do)
        goc = tdq_codex._duong_home(self.cwd)
        con = os.listdir(goc) if os.path.isdir(goc) else []
        self.assertEqual([t for t in con if t.startswith(tdq_codex.HOME_PREFIX)], [])

    def test_thieu_model_thi_khong_goi_say_hi(self):
        tdq_codex.dat_co_dong_y(self.cwd, True, model=None)
        kq, ghi = self._check("song")
        self.assertFalse(kq["chay_duoc"])
        self.assertIn("thiếu tên model", kq["ly_do"])
        self.assertFalse(os.path.exists(ghi), "không có model thì không được gọi `exec`")


class DongYCliTest(RepoTam):
    """Bugfix 2026-09-14 — lệnh bật cờ đồng ý phải chạy được ở gốc repo nguồn.

    Đo thật: `tdq_checkportable.py setup --codex` ở gốc repo → `ERROR no manifest.json`, exit 1,
    không ghi cờ — trong khi đó chính là lệnh `check` gợi ý.
    """

    def _chay(self, *args, path=None):
        env = dict(os.environ, TDQ_LOG="0")
        if path is not None:
            env["PATH"] = path
        return subprocess.run(
            [sys.executable, CLI, "-C", self.cwd, *args], capture_output=True, text=True,
            encoding="utf-8", timeout=60, stdin=subprocess.DEVNULL, env=env)

    def _path_co_codex(self):
        bin_ = os.path.join(self.cwd, "bin")
        os.makedirs(bin_, exist_ok=True)
        _codex_gia(bin_, "song")
        return bin_ + os.pathsep + os.environ.get("PATH", "")

    def test_dong_y_chay_duoc_khi_khong_co_manifest(self):
        proc = self._chay("dong-y", "--model", "m1", path=self._path_co_codex())
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.cwd, "manifest.json")))
        co = tdq_codex.doc_co_dong_y(self.cwd)
        self.assertTrue(co["nguoi_dung_dong_y"])
        self.assertEqual(co["codex_model"], "m1")

    def test_dong_y_khong_kem_model_thi_giu_model_cu(self):
        tdq_codex.dat_co_dong_y(self.cwd, False, model="model-cu")
        proc = self._chay("dong-y", path=self._path_co_codex())
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        co = tdq_codex.doc_co_dong_y(self.cwd)
        self.assertTrue(co["nguoi_dung_dong_y"])
        self.assertEqual(co["codex_model"], "model-cu")

    def test_thieu_codex_thi_khong_ghi_co(self):
        proc = self._chay("dong-y", "--model", "m1", path="/nonexistent-path-for-test")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("npm i -g @openai/codex", proc.stdout)
        self.assertFalse(os.path.exists(os.path.join(self.cwd, tdq_codex.CO_REL)))

    def test_goi_y_nguyen_nhan_2_chi_lenh_dong_y(self):
        with mock.patch("shutil.which", return_value="/usr/bin/codex"):
            kq = tdq_codex.check(self.cwd)
        self.assertIn("tdq_codex.py dong-y", kq["goi_y"])

    def test_goi_y_nguyen_nhan_3_khong_con_bao_thu_codex_version(self):
        tdq_codex.dat_co_dong_y(self.cwd, True, model="m1")
        with mock.patch("shutil.which", return_value="/usr/bin/codex"), \
             mock.patch.object(tdq_codex, "_kiem_song",
                               return_value=(False, "", "say hi quá hạn 30s")):
            kq = tdq_codex.check(self.cwd)
        self.assertNotIn("codex --version", kq["goi_y"],
                         "`--version` chạy được không chứng minh model trả lời")
        self.assertIn("tdq_codex.py check", kq["goi_y"])

    def test_ba_cho_goi_y_cung_mot_lenh(self):
        import tdq_checkportable
        lenh = "python3 scripts/tdq_codex.py dong-y"
        self.assertIn(lenh, " ".join(tdq_checkportable.CAU_HOI_CODEX))
        with open(os.path.join(ROOT, "skills", "tdq-plan", "references", "mode-gate.md"),
                  encoding="utf-8") as f:
            dong_2 = [d for d in f if d.startswith("| 2 |")]
        self.assertEqual(len(dong_2), 1)
        self.assertIn(lenh, dong_2[0])


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
