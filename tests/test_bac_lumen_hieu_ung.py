"""Bậc 5 và bậc 8 phải kiểm bằng HIỆU ỨNG, không kiểm sự tồn tại.

Vì sao file này tồn tại: 2026-09-28, MCP `lumen` chết cả phiên (`CONNECTION_CLOSED`) mà bậc 5
vẫn báo ĐẠT, vì nó chỉ hỏi "ollama có chạy không". Cùng lỗ hổng mà phép kiểm hiệu ứng ở intake
bước 1b đã vá cho LSP: một bậc chỉ kiểm CÓ TỒN TẠI thì mù với chuyện "tồn tại mà trả lời sai".

Ba lớp hỏng, ba ca riêng, chạy riêng được bằng `-k`: `path`, `vong`, `noidung`, `graphify`.
Mọi ca đều vá lớp chạm máy thật để suite chạy được trên máy chưa cài gì.
"""
import contextlib
import os
import shutil
import sys
import tempfile
import time
import unittest
from unittest import mock

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_lsp  # noqa: E402


class Bac5KhongPhuThuocPath(unittest.TestCase):
    """Ca `path` — daemon sống thì bậc 5 ĐẠT, dù binary không nằm trong PATH của tiến trình.

    Đo được trên máy macOS của user 2026-09-28: `/opt/homebrew/bin/ollama` có thật, login shell
    tìm ra, nhưng `shutil.which("ollama")` từ một tiến trình không-login trả None. Thứ tự cũ hỏi
    `which` TRƯỚC nên bậc 5 báo "thiếu ollama" và in `brew install ollama` — sai hai lần: kết
    luận sai, và xúi cài lại thứ đã có.
    """

    def test_path_thieu_binary_nhung_daemon_song_van_dat(self):
        with mock.patch.object(tdq_lsp.shutil, "which", return_value=None), \
                mock.patch.object(tdq_lsp, "_ollama_dang_chay", return_value=True), \
                mock.patch.object(tdq_lsp, "_model_da_pull", return_value=True), \
                mock.patch.object(tdq_lsp, "_lumen_thieu_binary_windows", return_value=("", "")), \
                mock.patch.object(tdq_lsp, "_index_cu_hon_code", return_value=(False, "")), \
                mock.patch.object(tdq_lsp, "_lumen_tra_loi_duoc", return_value=(True, "")):
            b = tdq_lsp.bac5_lumen()
        self.assertTrue(b.dat, f"daemon sống mà vẫn trượt: {b.chi_tiet}")
        self.assertEqual(b.lenh_cai, "", "không được xúi cài thứ đang chạy")

    def test_path_khong_binary_va_daemon_chet_thi_moi_bao_thieu(self):
        """Mặt còn lại: chỉ khi CẢ HAI cùng vắng mới được kết luận là chưa cài."""
        with mock.patch.object(tdq_lsp.shutil, "which", return_value=None), \
                mock.patch.object(tdq_lsp, "_ollama_dang_chay", return_value=False):
            b = tdq_lsp.bac5_lumen()
        self.assertFalse(b.dat)
        self.assertTrue(b.chi_canh_bao, "lumen là lớp dự phòng, hỏng thì cảnh báo chứ không chặn")
        self.assertIn("ollama", b.lenh_cai)


class Bac5VongDiVe(unittest.TestCase):
    """Ca `vong` — hỏi lumen một câu thật và đọc câu trả lời.

    2026-09-28: ollama chạy suốt phiên, MCP `lumen` chết cả phiên (`CONNECTION_CLOSED`), bậc 5
    báo ĐẠT. Một bậc chỉ kiểm daemon thì mù với chuyện "daemon sống mà đường tìm kiếm đứt".
    """

    def _va_phan_con_lai(self):
        """Mọi phép dò KHÁC đều xanh, để ca chỉ đo đúng một biến."""
        return [mock.patch.object(tdq_lsp, "_ollama_dang_chay", return_value=True),
                mock.patch.object(tdq_lsp, "_model_da_pull", return_value=True),
                mock.patch.object(tdq_lsp, "_lumen_thieu_binary_windows", return_value=("", ""))]

    def test_vong_lumen_khong_tra_ket_qua_thi_khong_dat(self):
        va = self._va_phan_con_lai()
        va.append(mock.patch.object(tdq_lsp, "_lumen_tra_loi_duoc",
                                    return_value=(False, "không kết quả nào")))
        va.append(mock.patch.object(tdq_lsp, "_index_cu_hon_code", return_value=(False, "")))
        with contextlib.ExitStack() as ngan:
            for p in va:
                ngan.enter_context(p)
            b = tdq_lsp.bac5_lumen()
        self.assertFalse(b.dat, "lumen câm mà bậc 5 vẫn ĐẠT là đúng lỗi 2026-09-28")
        self.assertIn("vòng đi-về", b.chi_tiet)

    def test_vong_lumen_tra_loi_duoc_thi_dat(self):
        va = self._va_phan_con_lai()
        va.append(mock.patch.object(tdq_lsp, "_lumen_tra_loi_duoc", return_value=(True, "1 kết quả")))
        va.append(mock.patch.object(tdq_lsp, "_index_cu_hon_code", return_value=(False, "")))
        with contextlib.ExitStack() as ngan:
            for p in va:
                ngan.enter_context(p)
            b = tdq_lsp.bac5_lumen()
        self.assertTrue(b.dat, b.chi_tiet)

    def test_vong_doc_dung_ket_qua_rong_va_ket_qua_that(self):
        """Phép đo phải đọc NỘI DUNG câu trả lời, không chỉ đọc mã thoát."""
        with mock.patch.object(tdq_lsp, "_binary_lumen", return_value="lumen"), \
                mock.patch.object(tdq_lsp, "_run", return_value=(0, "")):
            dat, _ = tdq_lsp._lumen_tra_loi_duoc(".")
        self.assertFalse(dat, "thoát 0 mà không kết quả nào vẫn là hỏng")
        with mock.patch.object(tdq_lsp, "_binary_lumen", return_value="lumen"), \
                mock.patch.object(tdq_lsp, "_run",
                                  return_value=(0, '<result:file filename="a.py">')):
            dat, _ = tdq_lsp._lumen_tra_loi_duoc(".")
        self.assertTrue(dat)


class Bac5NoiDungIndex(unittest.TestCase):
    """Ca `noidung` — index có nội dung mới nhất của cây làm việc hay không.

    Bằng chứng 2026-09-28: `index_status` báo `Stale: no` trong khi index thiếu hẳn phần sửa
    ngày 27/09 của một file đã từng index. Nguyên nhân là `defaultFreshnessTTL = 30s` của lumen
    0.0.42, cộng chuyện auto-reindex chỉ chạy khi có ai gọi `semantic_search`.

    Phép đo phải THUẦN ĐỌC. Bản đầu chạy `lumen index` ngay trong lúc chẩn đoán, và đó là sai
    tầng: `chay_kiem` chạy ở bước 1b của MỌI request và cả trong trang trạng thái, còn
    `tdq_finish` thì đã dựng lại ở cuối lượt trước — nên cùng một việc chạy hai lần mỗi lượt.
    """

    def setUp(self):
        self.thu_muc = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.thu_muc, True)

    def _ghi_dau_moc(self, tuoi_giay):
        dau_moc = os.path.join(self.thu_muc, tdq_lsp.DAU_MOC_INDEX)
        os.makedirs(os.path.dirname(dau_moc), exist_ok=True)
        with open(dau_moc, "w", encoding="utf-8") as fh:
            fh.write("2026-09-28T00:00:00\n")
        moc = time.time() - tuoi_giay
        os.utime(dau_moc, (moc, moc))
        return dau_moc

    def test_noidung_index_cu_hon_code_thi_canh_bao(self):
        with mock.patch.object(tdq_lsp, "_ollama_dang_chay", return_value=True), \
                mock.patch.object(tdq_lsp, "_model_da_pull", return_value=True), \
                mock.patch.object(tdq_lsp, "_lumen_thieu_binary_windows", return_value=("", "")), \
                mock.patch.object(tdq_lsp, "_lumen_tra_loi_duoc", return_value=(True, "")), \
                mock.patch.object(tdq_lsp, "_index_cu_hon_code",
                                  return_value=(True, "code mới hơn lần dựng index gần nhất 9 phút")):
            b = tdq_lsp.bac5_lumen()
        self.assertFalse(b.dat)
        self.assertIn("9 phút", b.chi_tiet)
        self.assertIn("index", b.lenh_cai)

    def test_noidung_phep_do_khong_chay_lenh_nao(self):
        """Phép chẩn đoán không được ghi, và cũng không được spawn tiến trình nào."""
        with mock.patch.object(tdq_lsp, "_run") as chay, \
                mock.patch.object(tdq_lsp, "_moc_code_moi_nhat", return_value=time.time()):
            cu, mo_ta = tdq_lsp._index_cu_hon_code(self.thu_muc)
        chay.assert_not_called()
        self.assertTrue(cu, "chưa có dấu mốc nào thì phải coi là chưa dựng lần nào")
        self.assertIn("chưa có", mo_ta)

    def test_noidung_dau_moc_moi_hon_code_thi_khong_canh_bao(self):
        self._ghi_dau_moc(tuoi_giay=0)
        with mock.patch.object(tdq_lsp, "_moc_code_moi_nhat", return_value=time.time() - 3600):
            cu, _ = tdq_lsp._index_cu_hon_code(self.thu_muc)
        self.assertFalse(cu)

    def test_noidung_dau_moc_cu_hon_code_thi_canh_bao(self):
        self._ghi_dau_moc(tuoi_giay=7200)
        with mock.patch.object(tdq_lsp, "_moc_code_moi_nhat", return_value=time.time()):
            cu, mo_ta = tdq_lsp._index_cu_hon_code(self.thu_muc)
        self.assertTrue(cu)
        self.assertIn("phút", mo_ta)


class Bac8Graphify(unittest.TestCase):
    """Ca `graphify` — công cụ thứ tư của bộ tìm kiếm, trước nay không có bậc nào.

    Đo được 2026-09-28: đồ thị của repo này cũ 8 ngày, 34% node (845/2415) trỏ vào một thư mục
    đã bị xoá. Không ai dựng lại, và không ai bị chặn vì không dựng lại — nên thang bậc phải nói.
    """

    def setUp(self):
        self.thu_muc = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.thu_muc, True)

    def _ghi_do_thi(self, tuoi_giay):
        duong = os.path.join(self.thu_muc, "graphify-out")
        os.makedirs(duong, exist_ok=True)
        tep = os.path.join(duong, "graph.json")
        with open(tep, "w", encoding="utf-8") as fh:
            fh.write("{}")
        moc = time.time() - tuoi_giay
        os.utime(tep, (moc, moc))
        return tep

    def test_graphify_thieu_binary_thi_canh_bao_kem_lenh_cai(self):
        with mock.patch.object(tdq_lsp.shutil, "which", return_value=None):
            b = tdq_lsp.bac8_graphify(self.thu_muc)
        self.assertFalse(b.dat)
        self.assertTrue(b.chi_canh_bao, "graphify là lớp bổ trợ — thiếu thì cảnh báo, không chặn")
        self.assertIn("graphify", b.lenh_cai)

    def test_graphify_chua_co_do_thi_thi_canh_bao(self):
        with mock.patch.object(tdq_lsp.shutil, "which", return_value="/usr/bin/graphify"), \
                mock.patch.object(tdq_lsp, "_moc_code_moi_nhat", return_value=time.time()):
            b = tdq_lsp.bac8_graphify(self.thu_muc)
        self.assertFalse(b.dat)
        self.assertIn("extract", b.lenh_cai)

    def test_graphify_do_thi_cu_hon_ma_nguon_thi_canh_bao(self):
        self._ghi_do_thi(tuoi_giay=7200)
        with mock.patch.object(tdq_lsp.shutil, "which", return_value="/usr/bin/graphify"), \
                mock.patch.object(tdq_lsp, "_moc_code_moi_nhat", return_value=time.time()):
            b = tdq_lsp.bac8_graphify(self.thu_muc)
        self.assertFalse(b.dat)
        self.assertIn("cũ hơn", b.chi_tiet)

    def test_graphify_do_thi_moi_hon_ma_nguon_thi_dat(self):
        self._ghi_do_thi(tuoi_giay=0)
        with mock.patch.object(tdq_lsp.shutil, "which", return_value="/usr/bin/graphify"), \
                mock.patch.object(tdq_lsp, "_moc_code_moi_nhat", return_value=time.time() - 3600):
            b = tdq_lsp.bac8_graphify(self.thu_muc)
        self.assertTrue(b.dat, b.chi_tiet)

    def test_graphify_khong_co_file_ma_nguon_thi_khong_ket_luan_cu(self):
        """Không có file mã nguồn nào để so thì bậc không được bịa ra một phán quyết."""
        self._ghi_do_thi(tuoi_giay=7200)
        with mock.patch.object(tdq_lsp.shutil, "which", return_value="/usr/bin/graphify"), \
                mock.patch.object(tdq_lsp, "_moc_code_moi_nhat", return_value=None):
            b = tdq_lsp.bac8_graphify(self.thu_muc)
        self.assertTrue(b.dat)

    def test_graphify_nam_trong_thang_bac(self):
        """Vá cả hai phép đo của bậc 5: không vá thì `chay_kiem` chạy `lumen index` THẬT trên
        repo của người đang chạy test — một lệnh GHI, mất tới cả phút, và trái đúng câu đầu file
        này ("mọi ca đều vá lớp chạm máy thật")."""
        with mock.patch.object(tdq_lsp, "_index_cu_hon_code", return_value=(False, "")), \
                mock.patch.object(tdq_lsp, "_lumen_tra_loi_duoc", return_value=(True, "")):
            b = tdq_lsp.chay_kiem(ROOT)
        self.assertEqual([x.so for x in b], [1, 2, 3, 4, 5, 6, 7, 8])


if __name__ == "__main__":
    unittest.main()
