"""Unit test cho `scripts/tdq_setup.py` — cửa cài đặt của cả workflow.

Script này được phép LÀM chứ không chỉ chẩn đoán, nên mỗi quyền nó có phải có một ca khoá lại:
cài gì (`cai`), đọc cấu hình thế nào (`cauhinh`), chứng minh từng tầng ra sao (`smoke`), vá hook
của plugin khác thế nào (`hook`), ghi nợ ra sao (`no`), và log bật/tắt thế nào (`log`).

Mọi ca đều vá lớp chạm máy thật, và mọi ca chạm file đều chạy trong thư mục tạm — không ca nào
được đọc hay ghi file thật của máy.
"""
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_lsp  # noqa: E402
import tdq_no  # noqa: E402
import tdq_setup  # noqa: E402


def _bac(so, ten, dat, lenh_cai="", chi_canh_bao=False):
    return tdq_lsp.Bac(so, ten, dat, "chi tiết", lenh_cai, chi_canh_bao)


class CaiThieu(unittest.TestCase):
    """`setup` được user gõ nên nó ĐƯỢC cài — nhưng chỉ đúng danh sách đã khai."""

    def test_cai_chay_lenh_cua_bac_thieu(self):
        bac = [_bac(1, "binary agent-lsp", False, "uv tool install graphifyy")]
        with mock.patch.object(tdq_setup, "_chay_lenh", return_value=(0, "")) as chay:
            da_cai, no = tdq_setup.cai_thieu(bac)
        self.assertEqual(len(da_cai), 1)
        self.assertEqual(no, [])
        chay.assert_called_once()

    def test_cai_tu_choi_lenh_ngoai_danh_sach_va_ghi_no(self):
        """Lệnh lạ không được chạy — nó thành NỢ, đúng luật 'ngoài danh sách thì chỉ ghi nợ'."""
        bac = [_bac(5, "sức khoẻ lumen", False, "rm -rf /nha/cua/toi")]
        with mock.patch.object(tdq_setup, "_chay_lenh") as chay:
            da_cai, no = tdq_setup.cai_thieu(bac)
        chay.assert_not_called()
        self.assertEqual(da_cai, [])
        self.assertEqual(len(no), 1)

    def test_cai_tu_choi_lenh_noi_nhieu_ve_bang_dau_cham_phay(self):
        """Bậc 3 nối lệnh nhiều ngôn ngữ bằng ` ; `, và `_chay_lenh` chạy qua shell.

        Một project C + Ruby sinh ra `brew install llvm ; gem install solargraph`: vế đầu hợp lệ,
        vế sau thì không. Kiểm mỗi tiền tố đầu chuỗi là để lọt nguyên vế sau chạy theo.
        """
        bac = [_bac(3, "language server", False, "brew install llvm ; gem install solargraph")]
        with mock.patch.object(tdq_setup, "_chay_lenh") as chay:
            da_cai, no = tdq_setup.cai_thieu(bac)
        chay.assert_not_called()
        self.assertEqual(da_cai, [])
        self.assertIn("shell", no[0])

    def test_cai_tu_choi_ca_chuoi_ghep_du_MOI_ve_deu_hop_le(self):
        """Chuỗi ghép bị từ chối cả cụm, không phải duyệt từng vế.

        Tự tách chuỗi để duyệt từng vế là viết lại bộ tách lệnh của shell — thứ không bao giờ
        đúng (nó không thấy `$(...)`, nháy, xuống dòng). Nên `_chay_lenh` bỏ hẳn shell, và ai
        khai lệnh thì khai từng lệnh một.
        """
        bac = [_bac(3, "language server", False, "brew install llvm ; brew install gopls")]
        with mock.patch.object(tdq_setup, "_chay_lenh") as chay:
            da_cai, no = tdq_setup.cai_thieu(bac)
        chay.assert_not_called()
        self.assertEqual(da_cai, [])
        self.assertIn("shell", no[0])

    def test_cai_khong_dung_python_he_thong_cua_apple(self):
        """Ràng buộc đứng của user: không bao giờ chạm python hệ thống của Apple."""
        bac = [_bac(3, "language server", False,
                    "/usr/bin/python3 -m pip install python-lsp-server")]
        with mock.patch.object(tdq_setup, "_chay_lenh") as chay:
            da_cai, no = tdq_setup.cai_thieu(bac)
        chay.assert_not_called()
        self.assertEqual(len(no), 1)
        self.assertIn("python", no[0].lower())

    def test_cai_bac_da_dat_thi_khong_dung_toi(self):
        bac = [_bac(1, "binary agent-lsp", True, "uv tool install graphifyy")]
        with mock.patch.object(tdq_setup, "_chay_lenh") as chay:
            da_cai, no = tdq_setup.cai_thieu(bac)
        chay.assert_not_called()
        self.assertEqual((da_cai, no), ([], []))

    def test_cai_lenh_that_bai_thi_thanh_no_chu_khong_im_lang(self):
        bac = [_bac(8, "đồ thị graphify", False, "uv tool install graphifyy")]
        with mock.patch.object(tdq_setup, "_chay_lenh", return_value=(1, "mạng hỏng")):
            da_cai, no = tdq_setup.cai_thieu(bac)
        self.assertEqual(da_cai, [])
        self.assertEqual(len(no), 1)


class KiemCauHinh(unittest.TestCase):
    """"Config đúng" là một trong bốn thứ user đòi, nên nó có phép kiểm riêng."""

    def setUp(self):
        self.thu_muc = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.thu_muc, True)

    def _ghi(self, noi_dung):
        duong = os.path.join(self.thu_muc, "config.yaml")
        with io.open(duong, "w", encoding="utf-8") as fh:
            fh.write(noi_dung)
        return duong

    def test_cauhinh_thieu_backend_bi_bat(self):
        """`backend` thiếu là lỗi lumen báo thẳng: `config: servers[0]: backend is required`."""
        cfg = self._ghi("servers:\n  - model: qwen3-embedding:0.6b\n")
        loi = tdq_setup.kiem_cau_hinh_lumen(cfg)
        self.assertTrue(loi)
        self.assertIn("backend", loi[0])

    def test_cauhinh_du_thi_khong_loi(self):
        cfg = self._ghi("servers:\n  - backend: ollama\n    model: qwen3-embedding:0.6b\n")
        self.assertEqual(tdq_setup.kiem_cau_hinh_lumen(cfg), [])

    def test_cauhinh_chua_co_file_thi_bao_thieu(self):
        loi = tdq_setup.kiem_cau_hinh_lumen(os.path.join(self.thu_muc, "chua-co.yaml"))
        self.assertTrue(loi)




class SmokeTungTang(unittest.TestCase):
    """"Smoke test đảm bảo hoạt động ổn" là yêu cầu thứ ba của user — mỗi tầng một câu hỏi thật."""

    def setUp(self):
        self.thu_muc = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.thu_muc, True)

    def test_smoke_grep_tim_duoc_chuoi_co_that(self):
        with io.open(os.path.join(self.thu_muc, "a.py"), "w", encoding="utf-8") as fh:
            fh.write("def main():\n    return 1\n")
        dat, chi_tiet = tdq_setup.smoke_grep(self.thu_muc)
        self.assertTrue(dat, chi_tiet)

    def test_smoke_grep_thu_muc_rong_thi_truot(self):
        dat, _ = tdq_setup.smoke_grep(self.thu_muc)
        self.assertFalse(dat, "không file nào mà vẫn báo đạt thì phép thử vô nghĩa")

    def test_smoke_lsp_doc_ma_thoat_cua_doctor(self):
        with mock.patch.object(tdq_lsp, "_run", return_value=(0, "all servers ok")):
            dat, _ = tdq_setup.smoke_lsp(self.thu_muc)
        self.assertTrue(dat)
        with mock.patch.object(tdq_lsp, "_run", return_value=(1, "gopls missing")):
            dat, chi_tiet = tdq_setup.smoke_lsp(self.thu_muc)
        self.assertFalse(dat)
        self.assertIn("gopls", chi_tiet)

    def test_smoke_graphify_can_co_ket_qua_chu_khong_chi_ma_thoat(self):
        with mock.patch.object(tdq_lsp, "_run", return_value=(0, "")):
            dat, _ = tdq_setup.smoke_graphify(self.thu_muc)
        self.assertFalse(dat, "thoát 0 mà rỗng vẫn là không trả lời được")
        with mock.patch.object(tdq_lsp, "_run", return_value=(0, "main() 20")):
            dat, _ = tdq_setup.smoke_graphify(self.thu_muc)
        self.assertTrue(dat)

    def test_smoke_bang_du_bon_tang(self):
        with mock.patch.object(tdq_setup, "smoke_grep", return_value=(True, "")), \
                mock.patch.object(tdq_setup, "smoke_lsp", return_value=(True, "")), \
                mock.patch.object(tdq_setup, "smoke_graphify", return_value=(False, "chưa cài")), \
                mock.patch.object(tdq_lsp, "_lumen_tra_loi_duoc", return_value=(True, "")):
            bang = tdq_setup.smoke_bon_tang(self.thu_muc)
        self.assertEqual([h[0] for h in bang], ["grep", "LSP", "graphify", "lumen"])
        self.assertEqual([h[1] for h in bang], [True, True, False, True])


class VaHookPlugin(unittest.TestCase):
    """Vá hook của plugin KHÁC là quyền mạnh nhất script này có, nên nó bị khoá chặt nhất.

    Nền pháp lý: tài liệu Claude Code nói thẳng không có cách tắt một hook riêng lẻ mà giữ nó
    trong cấu hình — chỉ có công tắc tổng `disableAllHooks`. Nên sửa file của plugin là đường
    duy nhất, và vì phiên bản nằm trong đường dẫn cache, plugin lên bản mới là hook cũ sống lại.
    """

    def setUp(self):
        self.thu_muc = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.thu_muc, True)

    def _dung_plugin(self, hooks):
        goc = os.path.join(self.thu_muc, "plugin", "hooks")
        os.makedirs(goc, exist_ok=True)
        tep = os.path.join(goc, "hooks.json")
        with io.open(tep, "w", encoding="utf-8") as fh:
            json.dump({"hooks": hooks}, fh, ensure_ascii=False)
        return tep

    def test_hook_go_khoi_chan_giu_khoi_phien(self):
        tep = self._dung_plugin({
            "SessionStart": [{"matcher": "startup", "hooks": [{"type": "command", "command": "x"}]}],
            "PreToolUse": [{"matcher": "Grep|Bash", "hooks": [{"type": "command", "command": "y"}]}]})
        with mock.patch.object(tdq_lsp, "hook_xung_dot", return_value=[("lumen", tep, "Grep|Bash")]):
            da_va, no = tdq_setup.va_hook_xung_dot()
        self.assertEqual(len(da_va), 1)
        self.assertEqual(no, [])
        with io.open(tep, encoding="utf-8") as fh:
            con_lai = json.load(fh)["hooks"]
        self.assertNotIn("PreToolUse", con_lai, "khối chặn công cụ phải biến mất")
        self.assertIn("SessionStart", con_lai, "khối phiên phải còn nguyên")

    def test_hook_luu_ban_cu_truoc_khi_sua(self):
        tep = self._dung_plugin({"PreToolUse": [{"matcher": "Grep"}]})
        with mock.patch.object(tdq_lsp, "hook_xung_dot", return_value=[("lumen", tep, "Grep")]):
            tdq_setup.va_hook_xung_dot()
        self.assertTrue(os.path.isfile(tep + tdq_setup.DUOI_SAO_LUU),
                        "không có bản sao lưu thì không lùi lại được")

    def test_hook_chi_go_khoi_dung_toi_cong_cu_tim_kiem(self):
        """Một khối PreToolUse nhắm việc KHÁC không phải việc của lệnh này."""
        tep = self._dung_plugin({"PreToolUse": [
            {"matcher": "Grep", "hooks": [{"command": "a"}]},
            {"matcher": "WebFetch", "hooks": [{"command": "b"}]}]})
        with mock.patch.object(tdq_lsp, "hook_xung_dot", return_value=[("lumen", tep, "Grep")]):
            tdq_setup.va_hook_xung_dot()
        with io.open(tep, encoding="utf-8") as fh:
            con_lai = json.load(fh)["hooks"]["PreToolUse"]
        self.assertEqual([m["matcher"] for m in con_lai], ["WebFetch"])

    def test_hook_khong_co_xung_dot_thi_khong_dung_vao_file_nao(self):
        with mock.patch.object(tdq_lsp, "hook_xung_dot", return_value=[]):
            da_va, no = tdq_setup.va_hook_xung_dot()
        self.assertEqual((da_va, no), ([], []))


class GhiNo(unittest.TestCase):
    """Nợ phải ghi ra FILE, vì thứ chỉ in ra màn hình thì hết phiên là mất."""

    def setUp(self):
        self.thu_muc = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.thu_muc, True)

    def _doc(self):
        with io.open(os.path.join(self.thu_muc, tdq_no.FILE_NO), encoding="utf-8") as fh:
            return fh.read()

    def test_no_moi_mon_mot_dong_co_ngay_va_ten_may(self):
        tdq_no.ghi_no(["thiếu graphify"], self.thu_muc)
        noi_dung = self._doc()
        self.assertIn("thiếu graphify", noi_dung)
        self.assertIn(tdq_no.platform.node(), noi_dung)
        self.assertRegex(noi_dung, r"\d{4}-\d{2}-\d{2}")

    def test_no_chay_lai_khong_nhan_ban_dong_cu(self):
        tdq_no.ghi_no(["thiếu graphify"], self.thu_muc)
        tdq_no.ghi_no(["thiếu graphify"], self.thu_muc)
        self.assertEqual(self._doc().count("thiếu graphify"), 1)

    def test_no_them_mon_moi_van_giu_mon_cu(self):
        tdq_no.ghi_no(["thiếu graphify"], self.thu_muc)
        tdq_no.ghi_no(["thiếu ollama"], self.thu_muc)
        noi_dung = self._doc()
        self.assertIn("thiếu graphify", noi_dung)
        self.assertIn("thiếu ollama", noi_dung)

    def test_no_rong_thi_van_tao_file_de_biet_la_da_kiem(self):
        tdq_no.ghi_no([], self.thu_muc)
        self.assertTrue(os.path.isfile(os.path.join(self.thu_muc, tdq_no.FILE_NO)))


class LogService(unittest.TestCase):
    """Yêu cầu bắt buộc của spec §4: log bật mặc định, có timestamp, tắt được qua config.

    Một công tắc duy nhất — biến môi trường `TDQ_LOG`. Bản đầu có thêm cờ global `_LOG_TAT` của
    riêng file này, nên `--khong-log` chỉ tắt được một nửa tiếng ồn: thang bậc là module khác và
    vẫn in. Hai công tắc cho một cái đèn là thứ ca này khoá lại.
    """

    def test_log_bat_mac_dinh_va_co_timestamp(self):
        with mock.patch.dict(os.environ, {"TDQ_LOG": "1"}),                 mock.patch("sys.stderr", new_callable=io.StringIO) as err:
            tdq_setup._log("thử một dòng")
        ra = err.getvalue()
        self.assertIn("thử một dòng", ra)
        self.assertRegex(ra, r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\]")

    def test_log_tat_duoc_bang_bien_moi_truong(self):
        with mock.patch.dict(os.environ, {"TDQ_LOG": "0"}),                 mock.patch("sys.stderr", new_callable=io.StringIO) as err:
            tdq_setup._log("không được in")
        self.assertEqual(err.getvalue(), "")

    def test_log_co_dong_lenh_tat_ca_log_cua_thang_bac(self):
        """`--khong-log` phải tắt được cả module kia, không thì im lặng một nửa."""
        with mock.patch.dict(os.environ, {"TDQ_LOG": "1"}),                 mock.patch.object(tdq_setup.tdq_lsp, "chay_kiem", return_value=[]),                 mock.patch.object(tdq_setup, "va_hook_xung_dot", return_value=([], [])),                 mock.patch.object(tdq_setup, "kiem_cau_hinh_lumen", return_value=[]),                 mock.patch.object(tdq_setup, "no_skill_khong_ton_tai", return_value=[]),                 mock.patch.object(tdq_setup, "ghim_huong_dan_tool", return_value=False),                 mock.patch.object(tdq_setup, "smoke_bon_tang", return_value=[]),                 mock.patch.object(tdq_no, "ghi_no", return_value=0),                 mock.patch("sys.stdout", new_callable=io.StringIO):
            tdq_setup.main(["--khong-log"])
            self.assertEqual(os.environ["TDQ_LOG"], "0")


if __name__ == "__main__":
    unittest.main()
