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


class DocKetQuaRaoTest(unittest.TestCase):
    """T1.1 — ket-qua.json: JSON trần hoặc ĐÚNG MỘT rào code bao trọn cả file; còn lại là None.

    Nguyên văn của ba lượt thật (Q13, Q21b, R1) nằm trong nhóm bị từ chối: văn thường không
    bao giờ được đọc thành kết quả."""

    NHAN = {
        "tran": '{"xong": true}',
        "rao_json": '```json\n{\n  "xong": true\n}\n```',
        "rao_khong_nhan": '```\n{"xong": true}\n```',
        "rao_nhan_hoa": '```JSON\n{"xong": true}\n```',
        "khoang_trang_quanh_rao": '\n\n  ```json\n{"xong": true}\n```\n  \n',
    }
    TU_CHOI = {
        "van_q13": 'The write was denied with an "operation not permitted" error.',
        "van_q21b_r1": "Yes, 2 + 2 is equal to 4.",
        "van_truoc_rao": 'Done:\n```json\n{"xong": true}\n```',
        "van_sau_rao": '```json\n{"xong": true}\n```\nAll good.',
        "hai_rao": '```json\n{"xong": true}\n```\n```json\n{"xong": true}\n```',
        "rao_khong_dong": '```json\n{"xong": true}\n',
        "rao_nhan_khac": '```python\n{"xong": true}\n```',
        "mang_json": '```json\n[{"xong": true}]\n```',
        "rong": "",
    }

    def _doc(self, noi_dung):
        with tempfile.TemporaryDirectory() as d:
            duong = os.path.join(d, "ket-qua.json")
            with open(duong, "w", encoding="utf-8") as f:
                f.write(noi_dung)
            return tdq_codex.doc_ket_qua(duong)

    def test_dang_duoc_nhan_ra_dict(self):
        for ten, noi_dung in self.NHAN.items():
            with self.subTest(ten=ten):
                self.assertEqual(self._doc(noi_dung), {"xong": True})

    def test_dang_bi_tu_choi_ra_none(self):
        for ten, noi_dung in self.TU_CHOI.items():
            with self.subTest(ten=ten):
                self.assertIsNone(self._doc(noi_dung))

    def test_file_khong_co_ra_none(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(tdq_codex.doc_ket_qua(os.path.join(d, "khong-co.json")))


class PhanQuyetLyDoTest(unittest.TestCase):
    """T1.2 — mỗi lượt không xong mang đúng một mã lý do trong tập ĐÓNG; chỉ `xong is True` là xong."""

    DUNG = {"xong": True}

    def test_tap_ma_dong_du_sau_ma(self):
        self.assertEqual(set(tdq_codex.MA_LY_DO), {
            "qua-han", "bi-chan", "exit-khac-0", "khong-co-ket-qua",
            "ket-qua-sai-khuon", "model-bao-chua-xong"})

    def test_thu_tu_timeout_deny_exit(self):
        pq = tdq_codex.phan_quyet_ly_do
        self.assertEqual(pq(1, None, "BLOCKED", True), ("timeout", "qua-han"))
        self.assertEqual(pq(1, None, "BLOCKED", False), ("deny", "bi-chan"))
        self.assertEqual(pq(1, self.DUNG, "", False), ("fail", "exit-khac-0"))

    def test_ket_qua_vang_hoac_sai_khuon(self):
        pq = tdq_codex.phan_quyet_ly_do
        self.assertEqual(pq(0, None, "", False), ("fail", "khong-co-ket-qua"))
        self.assertEqual(pq(0, None, "", False, "ket-qua-sai-khuon"), ("fail", "ket-qua-sai-khuon"))
        for ket_qua in ({}, {"sai_khoa": True}, {"xong": "true"}, {"xong": 1}, {"xong": None}):
            with self.subTest(ket_qua=ket_qua):
                self.assertEqual(pq(0, ket_qua, "", False), ("fail", "ket-qua-sai-khuon"))

    def test_chi_xong_is_true_moi_la_xong(self):
        pq = tdq_codex.phan_quyet_ly_do
        self.assertEqual(pq(0, {"xong": False}, "", False), ("fail", "model-bao-chua-xong"))
        self.assertEqual(pq(0, {"xong": True, "ghi_chu": "x"}, "", False), ("xong", None))
        self.assertEqual(tdq_codex.phan_quyet(0, {"xong": False}, "", False), "fail")

    def test_doc_ket_qua_ly_do_tach_vang_va_sai_khuon(self):
        with tempfile.TemporaryDirectory() as d:
            def doc(noi_dung):
                duong = os.path.join(d, "ket-qua.json")
                with open(duong, "w", encoding="utf-8") as f:
                    f.write(noi_dung)
                return tdq_codex.doc_ket_qua_ly_do(duong)
            self.assertEqual(tdq_codex.doc_ket_qua_ly_do(os.path.join(d, "khong-co.json")),
                             (None, "khong-co-ket-qua"))
            self.assertEqual(doc("  \n"), (None, "khong-co-ket-qua"))
            self.assertEqual(doc("Yes, 2 + 2 is equal to 4."), (None, "ket-qua-sai-khuon"))
            self.assertEqual(doc('[{"xong": true}]'), (None, "ket-qua-sai-khuon"))
            self.assertEqual(doc('```json\n{"xong": true}\n```'), ({"xong": True}, None))


class ChayLaiTestTest(unittest.TestCase):
    """Sai khuôn thì lấy test làm chuẩn — chỉ lượt hỏng ở khâu đọc câu trả lời, vùng file đạt, mới đáng chạy lại test."""

    CUU_DUOC = ("khong-co-ket-qua", "ket-qua-sai-khuon")

    def test_tap_cuu_duoc_dung_hai_ma_va_nam_trong_tap_dong(self):
        self.assertEqual(set(tdq_codex.MA_LY_DO_CHAY_LAI_TEST), set(self.CUU_DUOC))
        self.assertTrue(set(tdq_codex.MA_LY_DO_CHAY_LAI_TEST) <= set(tdq_codex.MA_LY_DO))

    def test_fail_ma_cuu_duoc_vung_dat_thi_chay_lai(self):
        for ly_do in self.CUU_DUOC:
            with self.subTest(ly_do=ly_do):
                self.assertIs(tdq_codex.can_chay_lai_test("fail", ly_do, True), True)

    def test_moi_ca_con_lai_khong_chay_lai(self):
        ca = [
            ("xong", None, True),
            ("timeout", "qua-han", True),
            ("deny", "bi-chan", True),
            ("fail", "exit-khac-0", True),
            ("fail", "model-bao-chua-xong", True),
            ("fail", None, True),                   # xong nhưng bị hạ vì vùng file
            ("fail", "ket-qua-sai-khuon", False),   # sai khuôn mà ghi ra ngoài vùng
            ("fail", "khong-co-ket-qua", False),
            ("fail", "ket-qua-sai-khuon", 1),       # chỉ đúng `True` mới là đạt
        ]
        for trang_thai, ly_do, dat in ca:
            with self.subTest(trang_thai=trang_thai, ly_do=ly_do, dat=dat):
                self.assertIs(tdq_codex.can_chay_lai_test(trang_thai, ly_do, dat), False)


class _VungGia:
    """Stand-in for the zone audit result: only `dat` and `as_dict()` are read."""

    def __init__(self, dat):
        self.dat = dat

    def as_dict(self):
        return {"dat": self.dat, "lech": [] if self.dat else ["ngoai.txt"], "khoa_bi_cham": []}


class PhanQuyetJsonTest(unittest.TestCase):
    """Dòng JSON của `run`: 5 khoá đúng thứ tự, leader đọc được lý do và biết có nên chạy lại test."""

    KHOA = ["trang_thai", "giay", "vung_file", "ly_do", "can_chay_lai_test"]

    def test_du_nam_khoa_dung_thu_tu(self):
        pq = tdq_codex.dung_phan_quyet("fail", 12.34, "ket-qua-sai-khuon", _VungGia(True))
        self.assertEqual(list(pq), self.KHOA)
        self.assertEqual(list(json.loads(json.dumps(pq))), self.KHOA)
        self.assertEqual(pq["giay"], 12.3)
        self.assertEqual(pq["vung_file"]["dat"], True)

    def test_xong_thi_ly_do_null_va_khong_chay_lai(self):
        pq = tdq_codex.dung_phan_quyet("xong", 1.0, None, _VungGia(True))
        self.assertEqual((pq["trang_thai"], pq["ly_do"], pq["can_chay_lai_test"]),
                         ("xong", None, False))

    def test_sai_khuon_vung_dat_thi_chay_lai(self):
        for ly_do in tdq_codex.MA_LY_DO_CHAY_LAI_TEST:
            with self.subTest(ly_do=ly_do):
                pq = tdq_codex.dung_phan_quyet("fail", 1.0, ly_do, _VungGia(True))
                self.assertEqual((pq["trang_thai"], pq["ly_do"]), ("fail", ly_do))
                self.assertIs(pq["can_chay_lai_test"], True)

    def test_can_chay_lai_luon_la_bool(self):
        for trang_thai, ly_do, dat in (("xong", None, True), ("fail", "ket-qua-sai-khuon", True),
                                       ("fail", "ket-qua-sai-khuon", False),
                                       ("timeout", "qua-han", True)):
            with self.subTest(trang_thai=trang_thai, ly_do=ly_do, dat=dat):
                pq = tdq_codex.dung_phan_quyet(trang_thai, 1.0, ly_do, _VungGia(dat))
                self.assertIsInstance(pq["can_chay_lai_test"], bool)

    def test_xong_ma_lech_vung_thi_ha_fail_khong_ly_do_khong_chay_lai(self):
        pq = tdq_codex.dung_phan_quyet("xong", 1.0, None, _VungGia(False))
        self.assertEqual((pq["trang_thai"], pq["ly_do"], pq["can_chay_lai_test"]),
                         ("fail", None, False))
        self.assertFalse(pq["vung_file"]["dat"])

    def test_sai_khuon_ma_lech_vung_thi_khong_chay_lai(self):
        pq = tdq_codex.dung_phan_quyet("fail", 1.0, "ket-qua-sai-khuon", _VungGia(False))
        self.assertEqual((pq["ly_do"], pq["can_chay_lai_test"]), ("ket-qua-sai-khuon", False))


class KhuonSchemaTest(unittest.TestCase):
    """T1.3 — schema khai cho Codex đạt điều kiện strict: có additionalProperties false."""

    def test_schema_du_dieu_kien_strict(self):
        self.assertEqual(tdq_codex.khuon_schema(), {
            "type": "object",
            "properties": {"xong": {"type": "boolean"}},
            "required": ["xong"],
            "additionalProperties": False,
        })

    def test_schema_ghi_ra_json_duoc(self):
        self.assertEqual(json.loads(json.dumps(tdq_codex.khuon_schema())), tdq_codex.khuon_schema())


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


class CodexHomeProviderTest(RepoTam):
    """Bugfix 2026-09-14 — CODEX_HOME tạm phải mang provider của máy.

    Thiếu `model_provider`, Codex rơi về `openai` và trả 400 "model not supported when using
    Codex with a ChatGPT account" — đo thật trên máy dùng router `9router`.
    """

    CONFIG_MAY = (
        'model = "model-cua-may"\n'
        'model_provider = "9router"\n'
        'approval_policy = "never"\n\n'
        '[model_providers.9router]\n'
        'name = "9Router"\n'
        'base_url = "http://127.0.0.1:20128/v1"\n'
        'wire_api = "responses"\n\n'
        '[model_providers.9router.http_headers]\n'
        'Authorization = "Bearer sk-gia-cho-test"\n\n'
        '[model_providers.khac]\n'
        'base_url = "http://khac.invalid/v1"\n\n'
        '[agents]\n'
        'default_subagent_model = "x"\n\n'
        '[projects."/Users/ai-do"]\n'
        'trust_level = "trusted"\n\n'
        '[mcp_servers.foo]\n'
        'command = "foo"\n'
    )

    def setUp(self):
        super().setUp()
        self.nguon = os.path.join(self.cwd, "codex-may")
        os.makedirs(self.nguon)

    def tearDown(self):
        tdq_codex.cleanup(self.cwd)
        super().tearDown()

    def _ghi_nguon(self, noi_dung):
        with open(os.path.join(self.nguon, "config.toml"), "w", encoding="utf-8") as f:
            f.write(noi_dung)

    def _doc_config(self, home):
        import tomllib
        with open(os.path.join(home, "config.toml"), "rb") as f:
            return tomllib.load(f)

    def test_chep_dung_provider_dang_chon_kem_bang_con(self):
        self._ghi_nguon(self.CONFIG_MAY)
        home = tdq_codex.dung_codex_home(self.cwd, model="gpt-5-codex", nguon=self.nguon)
        cfg = self._doc_config(home)
        self.assertEqual(cfg["model_provider"], "9router")
        bang = cfg["model_providers"]["9router"]
        self.assertEqual(bang["base_url"], "http://127.0.0.1:20128/v1")
        self.assertEqual(bang["wire_api"], "responses")
        self.assertEqual(bang["http_headers"]["Authorization"], "Bearer sk-gia-cho-test")

    def test_model_la_model_workflow_chon_khong_phai_model_may(self):
        self._ghi_nguon(self.CONFIG_MAY)
        home = tdq_codex.dung_codex_home(self.cwd, model="gpt-5-codex", nguon=self.nguon)
        self.assertEqual(self._doc_config(home)["model"], "gpt-5-codex")

    def test_khong_chep_bang_ngoai_provider(self):
        self._ghi_nguon(self.CONFIG_MAY)
        home = tdq_codex.dung_codex_home(self.cwd, model="gpt-5-codex", nguon=self.nguon)
        cfg = self._doc_config(home)
        self.assertEqual(set(cfg), {"model", "model_provider", "model_providers"})
        self.assertEqual(set(cfg["model_providers"]), {"9router"},
                         "chỉ chép provider đang chọn")

    def test_may_khong_khai_provider_thi_chi_co_model(self):
        self._ghi_nguon('model = "o3"\n')
        home = tdq_codex.dung_codex_home(self.cwd, model="gpt-5-codex", nguon=self.nguon)
        self.assertEqual(self._doc_config(home), {"model": "gpt-5-codex"})

    def test_config_may_thieu_hoac_hong_van_dung_duoc_home(self):
        home = tdq_codex.dung_codex_home(self.cwd, model="gpt-5-codex", nguon=self.nguon)
        self.assertEqual(self._doc_config(home), {"model": "gpt-5-codex"})
        self._ghi_nguon("[hỏng\n")
        home = tdq_codex.dung_codex_home(self.cwd, model="gpt-5-codex", nguon=self.nguon)
        self.assertEqual(self._doc_config(home), {"model": "gpt-5-codex"})

    def test_auth_json_lay_tu_nguon_quyen_600(self):
        with open(os.path.join(self.nguon, "auth.json"), "w", encoding="utf-8") as f:
            f.write("{}")
        home = tdq_codex.dung_codex_home(self.cwd, model="gpt-5-codex", nguon=self.nguon)
        duong = os.path.join(home, "auth.json")
        self.assertTrue(os.path.exists(duong))
        self.assertEqual(stat.S_IMODE(os.stat(duong).st_mode), 0o600)

    def test_nguon_mac_dinh_theo_bien_codex_home(self):
        with mock.patch.dict(os.environ, {"CODEX_HOME": self.nguon}):
            self.assertEqual(tdq_codex.thu_muc_codex_may(), self.nguon)
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("CODEX_HOME", None)
            self.assertEqual(tdq_codex.thu_muc_codex_may(),
                             os.path.join(os.path.expanduser("~"), ".codex"))

    def test_thu_muc_home_tam_duoc_gitignore(self):
        """`auth.json` và khoá provider nằm trong đây; repo công khai thì không được lọt."""
        mau = os.path.join("docs", "tdq", ".tdq-codex-home", "tdq-codex-home-x", "auth.json")
        proc = subprocess.run(["git", "check-ignore", "-q", mau], cwd=ROOT,
                              capture_output=True, text=True, timeout=30,
                              stdin=subprocess.DEVNULL)
        self.assertEqual(proc.returncode, 0, f"{mau} chưa được gitignore")


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

    def test_luot_khong_xong_ket_thuc_bang_ly_do(self):
        """T1.4/Q6 — lượt không xong nói lý do ở CUỐI dòng; 7 mảnh cũ còn đủ, dòng vẫn ngắn."""
        prompt = "y" * 220
        dong = tdq_codex.dong_log_luot(
            ma_task="T1.1", model="gpt-5-codex", home="/tmp/h", giay=3.25,
            trang_thai="fail", prompt=prompt, ly_do="ket-qua-sai-khuon")
        self.assertTrue(dong.endswith(" · ly_do=ket-qua-sai-khuon"), dong)
        for manh in ("T1.1", "gpt-5-codex", "/tmp/h", "3.2", "fail", "sha256=", 'dau="'):
            with self.subTest(manh=manh):
                self.assertIn(manh, dong)
        self.assertRegex(dong, r"^\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
        self.assertLess(len(dong), 300)

    def test_luot_xong_khong_mang_ly_do(self):
        dong = tdq_codex.dong_log_luot(
            ma_task="T1.1", model="m", home="/tmp/h", giay=1.0,
            trang_thai="xong", prompt="p", ly_do=None)
        self.assertNotIn("ly_do=", dong)
        self.assertTrue(dong.endswith('dau="p"'), dong)

    def _in_log_luot(self, env):
        import contextlib
        import io
        dong = tdq_codex.dong_log_luot("T1.1", "m", "/tmp/h", 1.0, "fail", "p", "bi-chan")
        buf = io.StringIO()
        with mock.patch.dict(os.environ, env, clear=False), contextlib.redirect_stderr(buf):
            tdq_codex.in_log_luot(dong)
        return buf.getvalue()

    def test_dong_log_luot_bat_mac_dinh_tat_duoc(self):
        """T4.1 — dòng log lượt đi qua cùng công tắc TDQ_LOG với mọi log khác."""
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("TDQ_LOG", None)
            ra = self._in_log_luot({})
        self.assertRegex(ra, r"^\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
        self.assertIn("· ly_do=bi-chan", ra)
        self.assertEqual(self._in_log_luot({"TDQ_LOG": "0"}), "")

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
