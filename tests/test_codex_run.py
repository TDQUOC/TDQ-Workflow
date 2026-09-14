"""P3 (T3.3–T3.7) — dựng lệnh, chọn model, phán quyết, CODEX_HOME, log.

Bốn cái bẫy mà phép kiểm ở đây dựng riêng để bắt:

1. T3.3 — tên cờ của `codex exec` chỉ được viết ở MỘT chỗ (`CO_EXEC`). Phép
   kiểm ĐỌC hằng số đó rồi đối chiếu, không liệt kê lại tên cờ; liệt kê lại thì
   phép kiểm chỉ chứng minh hai bản sao giống nhau, không chứng minh gì hết.
2. T3.4 — cấm rơi về model mặc định của máy. Thiếu tên model là FAIL kèm câu sửa.
3. T3.5 — exit code KHÔNG được tự mình quyết trạng thái: ba ca cùng `exit=0`
   phải ra ba trạng thái khác nhau.
4. T3.6/T3.7 — không đầu ra nào chứa `Bearer`; log ghi sha256 prompt chứ không
   ghi nguyên văn vào chỗ git theo dõi.
"""
import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_codex  # noqa: E402


class RepoTam(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = os.path.realpath(self._tmp.name)
        os.makedirs(os.path.join(self.cwd, "docs", "tdq"), exist_ok=True)
        tdq_codex.dat_co_dong_y(self.cwd, True, model="gpt-5-codex")

    def tearDown(self):
        self._tmp.cleanup()


class DungLenhTest(RepoTam):
    """T3.3 — lệnh dựng ra phải mang đủ mục trong bảng CO_EXEC."""

    def _lenh(self, **kw):
        kw.setdefault("goc_repo", self.cwd)
        kw.setdefault("model", "gpt-5-codex")
        kw.setdefault("file_schema", os.path.join(self.cwd, "s.json"))
        kw.setdefault("file_ket_qua", os.path.join(self.cwd, "o.json"))
        return tdq_codex.dung_lenh(**kw)

    def test_mang_du_moi_muc_trong_bang(self):
        lenh = self._lenh()
        for khoa, co in tdq_codex.CO_EXEC.items():
            with self.subTest(khoa=khoa):
                self.assertIn(co, lenh, f"lệnh thiếu mục `{khoa}` của bảng CO_EXEC")

    def test_bang_la_cho_duy_nhat_viet_ten_co(self):
        """Đọc mã nguồn: ngoài CO_EXEC ra không chỗ nào viết chuỗi cờ."""
        with open(os.path.join(ROOT, "scripts", "tdq_codex.py"),
                  encoding="utf-8") as f:
            nguon = f.read()
        than = nguon.split("CO_EXEC = {", 1)[1].split("}", 1)[1]
        for khoa, co in tdq_codex.CO_EXEC.items():
            if co.startswith("--"):
                with self.subTest(khoa=khoa):
                    self.assertNotIn(f'"{co}"', than,
                                     f"cờ {co} bị viết lại ngoài bảng CO_EXEC")

    def test_goc_repo_di_theo_lenh(self):
        self.assertIn(self.cwd, self._lenh())

    def test_model_di_theo_lenh(self):
        self.assertIn("gpt-5-codex", self._lenh())

    def test_ba_tinh_chat_roi_stdin_timeout_goc(self):
        """Ba tính chất bắt buộc của MỌI lượt gọi codex, kiểm ở tầng hợp đồng."""
        hd = tdq_codex.hop_dong_chay()
        self.assertIs(hd["stdin"], subprocess.DEVNULL)
        self.assertEqual(hd["timeout"], tdq_codex.TIMEOUT_RUN)
        self.assertIn(tdq_codex.CO_EXEC["goc_repo"], self._lenh())


class NguonModelTest(RepoTam):
    """T3.4 — thứ tự: cờ --model → khoá codex_model → FAIL kèm câu sửa."""

    def test_co_dong_lenh_thang(self):
        self.assertEqual(tdq_codex.chon_model(self.cwd, "tu-co"), "tu-co")

    def test_khong_co_co_thi_lay_khoa_cai_dat(self):
        self.assertEqual(tdq_codex.chon_model(self.cwd, None), "gpt-5-codex")

    def test_khong_co_ca_hai_thi_fail_kem_cau_sua(self):
        tdq_codex.dat_co_dong_y(self.cwd, True, model=None)
        with self.assertRaises(tdq_codex.LoiThieuModel) as ctx:
            tdq_codex.chon_model(self.cwd, None)
        self.assertTrue(str(ctx.exception).strip())
        self.assertIn("setup-model", str(ctx.exception), "phải nói cách sửa")

    def test_cam_roi_ve_model_mac_dinh_cua_may(self):
        """Không có nhánh nào trả về chuỗi rỗng hay None — đó chính là cách
        `codex` âm thầm dùng model mặc định."""
        tdq_codex.dat_co_dong_y(self.cwd, True, model="")
        with self.assertRaises(tdq_codex.LoiThieuModel):
            tdq_codex.chon_model(self.cwd, None)


class PhanQuyetTest(unittest.TestCase):
    """T3.5 — bảng phán quyết bốn trạng thái; exit code không quyết một mình."""

    def test_ba_ca_cung_exit_0_ra_ba_trang_thai(self):
        xong = tdq_codex.phan_quyet(exit_code=0, ket_qua={"xong": True},
                                    stdout="ok", qua_han=False)
        deny = tdq_codex.phan_quyet(exit_code=0, ket_qua={"xong": True},
                                    stdout='{"permissionDecision":"deny"}',
                                    qua_han=False)
        chan = tdq_codex.phan_quyet(exit_code=0, ket_qua={"xong": True},
                                    stdout="BLOCKED by sandbox", qua_han=False)
        self.assertEqual(xong, "xong")
        self.assertEqual(deny, "deny")
        self.assertEqual(chan, "deny")
        self.assertEqual(len({xong, deny, chan}), 2)
        self.assertNotEqual(xong, deny)

    def test_qua_han_thang_moi_dau_hieu_khac(self):
        self.assertEqual(
            tdq_codex.phan_quyet(exit_code=0, ket_qua={"xong": True},
                                 stdout="ok", qua_han=True), "timeout")

    def test_file_ket_qua_thieu_rong_lech_schema_deu_fail(self):
        for ket_qua in (None, {}, {"sai_khoa": 1}):
            with self.subTest(ket_qua=ket_qua):
                self.assertEqual(
                    tdq_codex.phan_quyet(exit_code=0, ket_qua=ket_qua,
                                         stdout="ok", qua_han=False), "fail")

    def test_exit_khac_0_la_fail(self):
        self.assertEqual(
            tdq_codex.phan_quyet(exit_code=1, ket_qua={"xong": True},
                                 stdout="", qua_han=False), "fail")

    def test_doc_ket_qua_bat_ba_dang_hong(self):
        with tempfile.TemporaryDirectory() as d:
            thieu = os.path.join(d, "khong-co.json")
            self.assertIsNone(tdq_codex.doc_ket_qua(thieu))
            rong = os.path.join(d, "rong.json")
            open(rong, "w", encoding="utf-8").close()
            self.assertIsNone(tdq_codex.doc_ket_qua(rong))
            lech = os.path.join(d, "lech.json")
            with open(lech, "w", encoding="utf-8") as f:
                f.write("{ không phải json")
            self.assertIsNone(tdq_codex.doc_ket_qua(lech))


class CodexHomeTest(RepoTam):
    """T3.6 — vòng đời CODEX_HOME: quyền 700, không rò `Bearer`, cleanup sạch."""

    def test_thu_muc_tam_quyen_700(self):
        home = tdq_codex.dung_codex_home(self.cwd, model="gpt-5-codex")
        try:
            che_do = stat.S_IMODE(os.stat(home).st_mode)
            self.assertEqual(che_do, 0o700, oct(che_do))
        finally:
            tdq_codex.cleanup(self.cwd)

    def test_config_toml_duoc_dung_toi_thieu(self):
        home = tdq_codex.dung_codex_home(self.cwd, model="gpt-5-codex")
        try:
            self.assertTrue(os.path.exists(os.path.join(home, "config.toml")))
        finally:
            tdq_codex.cleanup(self.cwd)

    def test_cleanup_xoa_het(self):
        home = tdq_codex.dung_codex_home(self.cwd, model="gpt-5-codex")
        tdq_codex.cleanup(self.cwd)
        self.assertFalse(os.path.exists(home))

    def test_cleanup_hai_lan_van_exit_0(self):
        tdq_codex.dung_codex_home(self.cwd, model="gpt-5-codex")
        self.assertEqual(tdq_codex.cleanup(self.cwd), 0)
        self.assertEqual(tdq_codex.cleanup(self.cwd), 0)

    def test_cleanup_khi_khong_co_gi_van_exit_0(self):
        self.assertEqual(tdq_codex.cleanup(self.cwd), 0)

    def test_khong_dau_ra_nao_chua_bearer(self):
        ban = 'Authorization: Bearer sk-abc123secret'
        self.assertNotIn("sk-abc123secret", tdq_codex.mask_secrets(ban))


class BienMocTest(RepoTam):
    """T3.3/Q21b — biến môi trường mốc của mode, tên KHÔNG chứa KEY/TOKEN/SECRET."""

    def test_ten_bien_khong_cham_tu_cam(self):
        ten = tdq_codex.BIEN_MOC
        for cam in ("KEY", "TOKEN", "SECRET"):
            with self.subTest(cam=cam):
                self.assertNotIn(cam, ten.upper())

    def test_bien_moc_di_vao_moi_truong_cua_lenh(self):
        env = tdq_codex.dung_env(self.cwd, home="/tmp/x", ma_task="T9.9")
        self.assertEqual(env[tdq_codex.BIEN_MOC], "T9.9")
        self.assertEqual(env["CODEX_HOME"], "/tmp/x")

    def test_vung_va_vung_khoa_di_theo_moi_truong(self):
        """Hook chặn sớm đọc vùng từ môi trường — không truyền thì hook mù.

        Dạng JSON chứ không phải chuỗi ngăn bởi dấu hai chấm: đường dẫn có thể mang
        khoảng trắng, và một danh sách rỗng phải phân biệt được với "chưa khai".
        """
        env = tdq_codex.dung_env(self.cwd, home="/tmp/x", ma_task="T9.9",
                                 vung=["scripts/a.py"], khoa=["tests/test_a.py"])
        self.assertEqual(json.loads(env[tdq_codex.BIEN_VUNG]), ["scripts/a.py"])
        self.assertEqual(json.loads(env[tdq_codex.BIEN_KHOA]), ["tests/test_a.py"])

    def test_ten_bien_vung_cung_khong_cham_tu_cam(self):
        for ten in (tdq_codex.BIEN_VUNG, tdq_codex.BIEN_KHOA):
            for cam in ("KEY", "TOKEN", "SECRET"):
                with self.subTest(ten=ten, cam=cam):
                    self.assertNotIn(cam, ten.upper())

    def test_ten_bien_khop_ten_hook_doc(self):
        """Hai đầu phải gọi biến bằng CÙNG một tên, nếu không thì im lặng mù."""
        import importlib.util
        duong = os.path.join(ROOT, "hooks", "scripts", "codex_edit_gate.py")
        spec = importlib.util.spec_from_file_location("codex_edit_gate_ten", duong)
        mo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mo)
        self.assertEqual(mo.BIEN_MOC, tdq_codex.BIEN_MOC)
        self.assertEqual(mo.BIEN_VUNG, tdq_codex.BIEN_VUNG)
        self.assertEqual(mo.BIEN_KHOA, tdq_codex.BIEN_KHOA)


class LogTest(RepoTam):
    """T3.7 — log đủ 7 mảnh, ghi sha256 prompt, nguyên văn chỉ vào file gitignore."""

    def test_dong_log_du_bay_manh(self):
        dong = tdq_codex.dong_log_luot(
            ma_task="T1.1", model="gpt-5-codex", home="/tmp/h",
            giay=12.5, trang_thai="xong", prompt="viết hàm x")
        for manh in ("T1.1", "gpt-5-codex", "/tmp/h", "12.5", "xong"):
            with self.subTest(manh=manh):
                self.assertIn(manh, dong)
        self.assertRegex(dong, r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
        self.assertIn(hashlib.sha256("viết hàm x".encode()).hexdigest()[:16], dong)

    def test_dong_log_chi_mang_phan_dau_prompt_khong_mang_than(self):
        """Hợp đồng: dòng log mang sha256 CỘNG một phần đầu ngắn đã che — đủ để
        người đọc nhận ra lượt nào, không đủ để lộ thân prompt.

        Phép kiểm chốt đúng cái ranh giới đó: chữ nằm SAU phần đầu không bao giờ
        được xuất hiện, dù prompt dài bao nhiêu."""
        than = "CHUOI-O-THAN-PROMPT-KHONG-DUOC-LO"
        prompt = "x" * 200 + than
        dong = tdq_codex.dong_log_luot(
            ma_task="T1.1", model="m", home="/tmp/h", giay=1.0,
            trang_thai="xong", prompt=prompt)
        self.assertNotIn(than, dong)
        self.assertLess(len(dong), 300, "dòng log phình ra là dấu hiệu chép cả prompt")

    def test_nguyen_van_prompt_chi_vao_file_da_gitignore(self):
        duong = tdq_codex.ghi_log_prompt(self.cwd, "T1.1", "nguyên văn đầy đủ")
        self.assertTrue(duong.endswith(tdq_codex.LOG_PROMPT_REL))
        with open(duong, encoding="utf-8") as f:
            self.assertIn("nguyên văn đầy đủ", f.read())

    def test_file_log_nguyen_van_duoc_gitignore(self):
        proc = subprocess.run(
            ["git", "check-ignore", "-q", tdq_codex.LOG_PROMPT_REL], cwd=ROOT,
            capture_output=True, text=True, encoding="utf-8", timeout=30,
            stdin=subprocess.DEVNULL)
        self.assertEqual(proc.returncode, 0,
                         f"{tdq_codex.LOG_PROMPT_REL} chưa được gitignore")

    def _chay_check(self, env_them):
        return subprocess.run(
            [sys.executable, os.path.join(ROOT, "scripts", "tdq_codex.py"),
             "check"], cwd=self.cwd, capture_output=True, text=True,
            encoding="utf-8", timeout=90, stdin=subprocess.DEVNULL,
            env=dict(os.environ, PATH="/nonexistent", **env_them))

    def test_log_bat_mac_dinh(self):
        """T10.1 — mặc định là BẬT. Một lệnh chỉ nói khi được hỏi thì lúc hỏng
        không để lại dấu vết nào, và đó đúng là lúc cần dấu vết nhất."""
        proc = self._chay_check({})
        self.assertTrue(proc.stderr.strip(), "log phải bật mặc định")
        self.assertIn("tdq_codex:", proc.stderr)
        self.assertRegex(proc.stderr, r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")

    def test_tat_duoc_bang_bien_moi_truong(self):
        proc = self._chay_check({"TDQ_LOG": "0"})
        self.assertEqual(proc.stderr.strip(), "")


class NhipChiaDoiTest(RepoTam):
    """T3.7/Q14c — nhịp đỏ trước, xanh sau; log ghi CẢ HAI mốc."""

    def test_log_ghi_ca_moc_do_va_moc_xanh(self):
        dong = tdq_codex.dong_log_nhip(ma_task="T1.1", do=True, xanh=False)
        dong2 = tdq_codex.dong_log_nhip(ma_task="T1.1", do=True, xanh=True)
        self.assertIn("red=", dong)
        self.assertIn("red=", dong2)
        self.assertIn("green=yes", dong2)

    def test_chua_thay_do_thi_tu_choi_goi_codex(self):
        """Gọi Codex khi test chưa đỏ là phá nhịp — phải chặn ngay."""
        with self.assertRaises(tdq_codex.LoiChuaDo):
            tdq_codex.kiem_nhip(da_thay_do=False)
        self.assertTrue(tdq_codex.kiem_nhip(da_thay_do=True))


if __name__ == "__main__":
    unittest.main()
