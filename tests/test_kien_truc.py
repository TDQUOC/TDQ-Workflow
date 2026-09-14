"""T1.4 — chiều phụ thuộc giữa các tầng, khẳng định bằng AST chứ không bằng grep.

Một bất biến duy nhất nhưng là bất biến gốc của cả request: `scripts/tdq_state.py`
là NGUỒN CHÂN LÝ của workflow, nên nó không được phụ thuộc tầng CLI Codex.
Chiều đúng là state ← codex, không bao giờ ngược lại.

Vì sao đọc AST chứ không grep: grep bắt hụt `__import__("tdq_codex")`,
`importlib.import_module(...)` và bắt nhầm chuỗi trong comment hay docstring —
mà chuỗi thì được phép (đường dẫn `scripts/tdq_codex.py` phải nằm trong
CODEX_CHECK_REL để gọi bằng subprocess).
"""
import ast
import os
import unittest

from helper import ROOT

CAM = "tdq_codex"


def _cac_node_import(duong_dan):
    """-> danh sách mô tả mọi phép nhập khẩu trong file, kể cả nhập động."""
    with open(duong_dan, encoding="utf-8") as f:
        cay = ast.parse(f.read(), filename=duong_dan)
    ten = []
    for node in ast.walk(cay):
        if isinstance(node, ast.Import):
            ten.extend(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            ten.append(node.module or "")
        elif isinstance(node, ast.Call):
            # Nhập động: __import__("x") và importlib.import_module("x").
            f_ = node.func
            la_dong = (isinstance(f_, ast.Name) and f_.id == "__import__") or (
                isinstance(f_, ast.Attribute) and f_.attr == "import_module")
            if la_dong and node.args and isinstance(node.args[0], ast.Constant):
                ten.append(str(node.args[0].value))
    return ten


class ChieuPhuThuocTest(unittest.TestCase):
    def test_state_khong_import_tang_codex(self):
        duong = os.path.join(ROOT, "scripts", "tdq_state.py")
        nhap = _cac_node_import(duong)
        pham = [n for n in nhap if n.split(".")[0] == CAM]
        self.assertEqual(pham, [],
                         f"tdq_state.py không được import {CAM}: {pham}")

    def test_state_van_goi_duoc_tang_codex_qua_duong_dan(self):
        """Chiều đúng vẫn phải chạy được: state biết ĐƯỜNG DẪN tới tầng Codex
        (để chạy subprocess), chỉ là không nhập khẩu nó."""
        import tdq_state
        self.assertIn("tdq_codex", tdq_state.CODEX_CHECK_REL)

    def test_phep_kiem_nay_bat_duoc_ca_nhap_dong(self):
        """Phép kiểm tự chứng minh nó không phải grep: ba dạng nhập đều bị bắt."""
        import tempfile
        mau = ('import tdq_codex\n'
               'from tdq_codex import x\n'
               '__import__("tdq_codex")\n'
               'importlib.import_module("tdq_codex")\n')
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False,
                                         encoding="utf-8") as f:
            f.write(mau)
            tam = f.name
        try:
            self.assertEqual(_cac_node_import(tam).count(CAM), 4)
        finally:
            os.unlink(tam)

    def test_chuoi_trong_comment_khong_bi_bat_nham(self):
        import tempfile
        mau = ('# import tdq_codex\n'
               '"""nói về tdq_codex trong docstring"""\n'
               'DUONG = "scripts/tdq_codex.py"\n')
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False,
                                         encoding="utf-8") as f:
            f.write(mau)
            tam = f.name
        try:
            self.assertEqual(_cac_node_import(tam), [])
        finally:
            os.unlink(tam)


if __name__ == "__main__":
    unittest.main()
