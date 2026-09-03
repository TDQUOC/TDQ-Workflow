#!/usr/bin/env python3
"""Đếm các mẫu mã nguồn quyết định việc chạy được trên Linux/Windows.

Đếm bằng `ast` chứ không bằng grep: một chuỗi văn bản có chữ `encoding=` không phải là một
tham số `encoding=`, và grep không phân biệt được. Mọi con số trong báo cáo tương thích của
request 2026-09-03-1648 lấy từ đây, và bộ test đọc lại chính hàm này để báo cáo không mục.

Năm khoá đầu ra:
  subprocess_thieu_encoding — gọi subprocess có text=True (hoặc universal_newlines=True)
                              mà không khai encoding=; trên Windows sẽ giải mã theo code page.
  open_thieu_encoding       — open() chế độ văn bản không khai encoding=; cùng hậu quả.
  import_chi_posix          — import stdlib chỉ tồn tại trên POSIX; mỗi cái là một lỗi cứng.
  goi_chmod                 — os.chmod: bit quyền POSIX, trên Windows gần như vô nghĩa.
  hook_goi_python3          — hook khai `command` gọi thẳng tên lệnh `python3`, tên mà
                              PowerShell thuần không phân giải được.
"""
import argparse
import ast
import json
import os
import sys

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VUNG_QUET = ("scripts", "hooks")
MODULE_CHI_POSIX = {"fcntl", "pwd", "grp", "termios", "tty", "posix", "resource"}
# Ba nguồn hook, một cho mỗi host.
NGUON_HOOK = {
    "claude": "hooks/hooks.json",
    "codex": "portable_codex/.codex/hooks.json",
    "agy": "antigravity_portable/hooks.json",
}


def _file_python(goc):
    for vung in VUNG_QUET:
        for thu_muc, _, ten_files in os.walk(os.path.join(goc, vung)):
            for ten in sorted(ten_files):
                if ten.endswith(".py"):
                    yield os.path.join(thu_muc, ten)


def _co_tham_so(node, ten):
    return any(kw.arg == ten for kw in node.keywords)


def _gia_tri_that(node, ten):
    """True khi tham số `ten` được truyền và giá trị hằng của nó là thật."""
    for kw in node.keywords:
        if kw.arg == ten and isinstance(kw.value, ast.Constant):
            return bool(kw.value.value)
    return False


def _ten_ham(node):
    """`subprocess.run` → "subprocess.run"; `open` → "open"."""
    dich = node.func
    phan = []
    while isinstance(dich, ast.Attribute):
        phan.append(dich.attr)
        dich = dich.value
    if isinstance(dich, ast.Name):
        phan.append(dich.id)
    return ".".join(reversed(phan))


def _che_do_van_ban(node):
    """open() ở chế độ văn bản? Không khai mode → mặc định 'r', là văn bản."""
    mode = None
    if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
        mode = node.args[1].value
    for kw in node.keywords:
        if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
            mode = kw.value.value
    if mode is None:
        return True
    return "b" not in str(mode)


def dem_ma_nguon(goc=GOC):
    """Bốn khoá đếm từ mã Python, mỗi khoá kèm danh sách `file:dòng` để tra lại."""
    ket = {k: [] for k in
           ("subprocess_thieu_encoding", "open_thieu_encoding", "import_chi_posix", "goi_chmod")}
    for duong in _file_python(goc):
        with open(duong, encoding="utf-8") as f:
            try:
                cay = ast.parse(f.read(), filename=duong)
            except SyntaxError:
                continue
        tuong_doi = os.path.relpath(duong, goc)
        for node in ast.walk(cay):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                ten_mods = ([a.name for a in node.names] if isinstance(node, ast.Import)
                            else [node.module or ""])
                for ten in ten_mods:
                    if ten.split(".")[0] in MODULE_CHI_POSIX:
                        ket["import_chi_posix"].append(f"{tuong_doi}:{node.lineno}")
                continue
            if not isinstance(node, ast.Call):
                continue
            ten = _ten_ham(node)
            if ten in ("os.chmod", "chmod", "Path.chmod"):
                ket["goi_chmod"].append(f"{tuong_doi}:{node.lineno}")
            elif ten.startswith("subprocess.") or ten in ("run", "Popen", "check_output"):
                van_ban = _gia_tri_that(node, "text") or _gia_tri_that(node, "universal_newlines")
                if van_ban and not _co_tham_so(node, "encoding"):
                    ket["subprocess_thieu_encoding"].append(f"{tuong_doi}:{node.lineno}")
            elif ten == "open" and _che_do_van_ban(node) and not _co_tham_so(node, "encoding"):
                ket["open_thieu_encoding"].append(f"{tuong_doi}:{node.lineno}")
    return ket


def dem_hook_python3(goc=GOC):
    """Mỗi nguồn hook: bao nhiêu `command` gọi thẳng tên lệnh `python3`, trên tổng bao nhiêu."""
    ket = {}
    for ten, tuong_doi in NGUON_HOOK.items():
        duong = os.path.join(goc, tuong_doi)
        if not os.path.exists(duong):
            ket[ten] = {"duong_dan": tuong_doi, "co_file": False, "python3": 0, "tong": 0}
            continue
        with open(duong, encoding="utf-8") as f:
            du_lieu = json.load(f)
        lenh = []

        def _gom(nut):
            if isinstance(nut, dict):
                if isinstance(nut.get("command"), str):
                    lenh.append(nut["command"])
                for v in nut.values():
                    _gom(v)
            elif isinstance(nut, list):
                for v in nut:
                    _gom(v)

        _gom(du_lieu)
        ket[ten] = {
            "duong_dan": tuong_doi,
            "co_file": True,
            "python3": sum(1 for c in lenh if c.split()[:1] == ["python3"]),
            "tong": len(lenh),
        }
    return ket


def dem_tat_ca(goc=GOC):
    ket = dem_ma_nguon(goc)
    ket["hook_goi_python3"] = dem_hook_python3(goc)
    return ket


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true", help="in JSON đầy đủ kèm vị trí")
    parser.add_argument("--goc", default=GOC, help="thư mục gốc repo cần quét")
    tham_so = parser.parse_args(argv)
    ket = dem_tat_ca(tham_so.goc)
    if tham_so.json:
        print(json.dumps(ket, ensure_ascii=False, indent=2))
        return 0
    for khoa in ("subprocess_thieu_encoding", "open_thieu_encoding", "import_chi_posix", "goi_chmod"):
        print(f"{khoa}: {len(ket[khoa])}")
    for ten, so in ket["hook_goi_python3"].items():
        print(f"hook_goi_python3.{ten}: {so['python3']}/{so['tong']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
