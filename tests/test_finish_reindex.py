"""Bước reindex ở kết turn — `scripts/tdq_finish.py`.

Vì sao bước này tồn tại: auto-reindex của lumen là LAZY, ăn theo lời gọi `semantic_search`. MCP
chết cả phiên thì cả tuần không ai dựng lại — đo được 2026-09-28, index đứng từ 21/09 trong khi
file sửa ngày 27/09 không hề có trong đó. Cộng thêm `defaultFreshnessTTL = 30s` của lumen 0.0.42
khiến một lần "fresh" đã xác nhận che mắt phép đo trong cửa sổ ngắn.

Nên workflow tự dựng lại, mỗi turn, bằng CLI. Hai ràng buộc bị khoá ở đây: nó phải RẺ khi không
có gì đổi (`-k ok`), và nó KHÔNG BAO GIỜ được treo lượt (`-k tran`).
"""
import os
import sys
import unittest
from unittest import mock

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_finish  # noqa: E402
import tdq_lsp  # noqa: E402
import tdq_no  # noqa: E402


class ReindexOk(unittest.TestCase):
    def test_ok_co_file_sua_thi_dung_lai_va_bao_so_file(self):
        with mock.patch.object(tdq_lsp, "_binary_lumen", return_value="lumen"), \
                mock.patch.object(tdq_finish, "_run", return_value=(
                    0, "Done. Indexed 1 files, 12 chunks in 2.567s.")):
            b = tdq_finish.step_reindex(".")
        self.assertEqual(b.status, "ok")
        self.assertIn("1 files", b.detail)

    def test_ok_khong_gi_doi_van_chay_va_van_ok(self):
        """0,2 s khi không có gì đổi — đủ rẻ để chạy mỗi turn, nên không có ngưỡng nào cả."""
        with mock.patch.object(tdq_lsp, "_binary_lumen", return_value="lumen"), \
                mock.patch.object(tdq_finish, "_run", return_value=(0, "Index is already up to date.")):
            b = tdq_finish.step_reindex(".")
        self.assertEqual(b.status, "ok")

    def test_ok_ollama_ngu_thi_skip_chu_khong_fail(self):
        """§3 của luật tìm kiếm bảo NHẢ daemon ngay sau khi hỏi lumen.

        Nên đúng những lượt vừa dùng lumen là những lượt ollama đã ngủ. Không có cổng này thì mỗi
        lượt đó đều `fail` và đẻ thêm một dòng nợ, mà index thì vẫn không bao giờ được dựng lại.
        """
        with mock.patch.object(tdq_lsp, "_binary_lumen", return_value="lumen"), \
                mock.patch.object(tdq_lsp, "_ollama_dang_chay", return_value=False), \
                mock.patch.object(tdq_finish, "_run") as chay:
            b = tdq_finish.step_reindex(".")
        chay.assert_not_called()
        self.assertEqual(b.status, "skip")
        self.assertIn("ollama", b.detail)

    def test_ok_chua_cai_lumen_thi_skip_chu_khong_fail(self):
        with mock.patch.object(tdq_lsp, "_binary_lumen", return_value=""):
            b = tdq_finish.step_reindex(".")
        self.assertEqual(b.status, "skip")


class ReindexTran(unittest.TestCase):
    """Trần thời gian: lượt của user quan trọng hơn độ mới của index."""

    def test_tran_qua_gio_thi_fail_va_ghi_no_chu_khong_treo(self):
        with mock.patch.object(tdq_lsp, "_binary_lumen", return_value="lumen"), \
                mock.patch.object(tdq_finish, "_run", return_value=(1, "quá 120s")), \
                mock.patch.object(tdq_no, "ghi_no") as ghi:
            b = tdq_finish.step_reindex(".")
        self.assertEqual(b.status, "fail")
        ghi.assert_called_once()

    def test_tran_la_mot_hang_so_doc_duoc(self):
        self.assertGreaterEqual(tdq_finish.REINDEX_TIMEOUT, 60)


class BoCoSkipGraphify(unittest.TestCase):
    """Cờ `--skip-graphify` bị gỡ hẳn: chính nó làm đồ thị cũ 8 ngày, 34% node trỏ vào thư mục đã xoá."""

    def test_co_skip_graphify_khong_con_duoc_nhan(self):
        with self.assertRaises(SystemExit):
            tdq_finish.parse_args(["--skip-graphify"])


if __name__ == "__main__":
    unittest.main()
