"""Mọi lệnh con đọc ở chế độ văn bản phải khai `encoding=` — yêu cầu 2026-09-21-0029 (T3.2).

Vì sao: từ 0.49.0 mọi script của repo ép stdout sang UTF-8 (`scripts/utf8_io.py`). Bên đọc thì
khác: `text=True` mà không khai `encoding=` sẽ giải mã bằng code page của máy — trên Windows mặc
định là cp1252. Chữ Việt có byte 0x8f, 0x90, 0x9d mà cp1252 không có mã, luồng đọc chết, và
`proc.stdout` thành `None`. Lỗi này nấp được cả một request vì máy chạy suite có `PYTHONUTF8=1`.

Test đọc AST chứ không grep dòng: lời gọi `subprocess.run(...)` hay trải nhiều dòng, và
`encoding=` có thể nằm ở dòng khác với `text=True`.
"""
import ast
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THU_MUC = ("scripts", "hooks", "tests")
HAM = {"run", "Popen", "check_output", "check_call", "call"}


def _cac_file():
    for goc in THU_MUC:
        for thu_muc, _, ten_file in os.walk(os.path.join(ROOT, goc)):
            for ten in ten_file:
                if ten.endswith(".py"):
                    yield os.path.join(thu_muc, ten)


def _goi_thieu_ma_hoa(duong):
    with open(duong, encoding="utf-8") as f:
        cay = ast.parse(f.read(), duong)
    for nut in ast.walk(cay):
        if not (isinstance(nut, ast.Call) and isinstance(nut.func, ast.Attribute)
                and nut.func.attr in HAM):
            continue
        khoa = {k.arg: k.value for k in nut.keywords if k.arg}
        van_ban = any(getattr(khoa.get(k), "value", None) is True
                      for k in ("text", "universal_newlines"))
        if van_ban and "encoding" not in khoa:
            yield nut.lineno


def _open_thieu_ma_hoa(duong):
    """`open()` chế độ văn bản không khai `encoding=` — cùng một lỗi, ở phía file."""
    with open(duong, encoding="utf-8") as f:
        cay = ast.parse(f.read(), duong)
    for nut in ast.walk(cay):
        if not (isinstance(nut, ast.Call) and isinstance(nut.func, ast.Name)
                and nut.func.id == "open"):
            continue
        khoa = {k.arg: k.value for k in nut.keywords if k.arg}
        che_do = khoa.get("mode") or (nut.args[1] if len(nut.args) > 1 else None)
        chuoi = getattr(che_do, "value", "r") if che_do is not None else "r"
        if isinstance(chuoi, str) and "b" not in chuoi and "encoding" not in khoa:
            yield nut.lineno


class MaHoaLenhCon(unittest.TestCase):
    def test_moi_open_van_ban_deu_khai_encoding(self):
        thieu = [f"{os.path.relpath(d, ROOT)}:{dong}"
                 for d in _cac_file() for dong in _open_thieu_ma_hoa(d)]
        self.assertEqual(thieu, [], "open() văn bản thiếu encoding= — Windows sẽ ghi/đọc "
                                    "bằng cp1252:\n" + "\n".join(thieu))

    def test_moi_loi_goi_van_ban_deu_khai_encoding(self):
        thieu = [f"{os.path.relpath(d, ROOT)}:{dong}"
                 for d in _cac_file() for dong in _goi_thieu_ma_hoa(d)]
        self.assertEqual(thieu, [], "text=True mà thiếu encoding= — Windows sẽ giải mã "
                                    "bằng cp1252:\n" + "\n".join(thieu))

    def test_bat_duoc_ca_loi_goi_nhieu_dong(self):
        """Tự kiểm bộ dò: một lời gọi trải ba dòng vẫn phải bị bắt."""
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False,
                                         encoding="utf-8") as f:
            f.write("import subprocess\nsubprocess.run(\n    ['x'],\n    text=True)\n"
                    "subprocess.run(['y'], text=True, encoding='utf-8')\n")
        self.addCleanup(os.unlink, f.name)
        self.assertEqual(list(_goi_thieu_ma_hoa(f.name)), [2])


if __name__ == "__main__":
    unittest.main()
