#!/usr/bin/env python3
"""Quét file code theo thư viện rule `skills/tdq-build/references/rules/`.

Dò ngôn ngữ theo đuôi file, tra bảng linter trong `rules/index.md`, chạy linter đã cài
(kiểm bằng shutil.which — KHÔNG tự cài gì); in bảng ba trạng thái
PASS · LỖI · CHƯA KIỂM ĐƯỢC ra stdout. Exit 1 CHỈ khi có LỖI.

Mặc định chỉ quét file git báo đổi (diff HEAD + untracked); `--tat-ca` quét mọi file
git quản lý; truyền đường dẫn thì quét đúng chỗ đó. Log service ra stderr, bật mặc
định kèm timestamp; `--im` tắt hẳn; `--chi-tiet` in thêm bước dò ngôn ngữ.
"""
import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
INDEX = GOC / "skills" / "tdq-build" / "references" / "rules" / "index.md"
TRANG_THAI = ("PASS", "LỖI", "CHƯA KIỂM ĐƯỢC")

TUY_CHON = None  # argparse.Namespace, gán trong main()


def log(msg, chi_tiet=False):
    """Log service ra stderr, timestamp ISO; --im tắt hẳn, dòng chi_tiet cần --chi-tiet."""
    if TUY_CHON.im or (chi_tiet and not TUY_CHON.chi_tiet):
        return
    moc = datetime.now().isoformat(timespec="seconds")
    print(f"[{moc}] {msg}", file=sys.stderr)


def doc_bang_linter():
    """Đọc bảng `| Ngôn ngữ | đuôi | file rule | lệnh |` trong rules/index.md."""
    bang = {}
    for dong in INDEX.read_text(encoding="utf-8").splitlines():
        o = [c.strip() for c in dong.strip().strip("|").split("|")]
        if len(o) != 4 or not o[1].startswith("`."):
            continue
        lenh = o[3].strip("`")
        for duoi in o[1].strip("`").split():
            bang[duoi] = (o[0], lenh)
    return bang


def _git(lenh):
    try:
        kq = subprocess.run(["git", *lenh], capture_output=True, text=True)
    except FileNotFoundError:
        log("không tìm thấy git trong PATH — coi như không có file đổi")
        return []
    return kq.stdout.splitlines() if kq.returncode == 0 else []


def gom_file(duong_dan, tat_ca):
    """Chọn file cần quét: đường dẫn chỉ định > --tat-ca > mặc định file đã đổi."""
    if duong_dan:
        for p in map(Path, duong_dan):
            if p.is_dir():
                yield from sorted(x for x in p.rglob("*") if x.is_file())
            elif p.is_file():
                yield p
        return
    if tat_ca:
        ten = _git(["ls-files"])
    else:
        ten = _git(["diff", "--name-only", "HEAD"]) + _git(
            ["ls-files", "--others", "--exclude-standard"])
    for t in dict.fromkeys(ten):
        p = Path(t)
        if p.is_file():
            yield p


def chay_linter(lenh, f, bo_nho):
    """Chạy lệnh linter cho file f; lệnh không có placeholder thì chạy 1 lần dùng chung."""
    if "<đường dẫn>" in lenh:
        tokens = lenh.replace("<đường dẫn>", "\x00").split()
        cmd = [str(f) if t == "\x00" else t for t in tokens]
    else:
        if lenh in bo_nho:
            return bo_nho[lenh]
        cmd = lenh.split()
    kq = subprocess.run(cmd, capture_output=True, text=True)
    dong_dau = (kq.stdout or kq.stderr).strip().splitlines()
    ghi_chu = dong_dau[0][:120] if dong_dau else ""
    ket = ("PASS", "") if kq.returncode == 0 else ("LỖI", ghi_chu)
    if "<đường dẫn>" not in lenh:
        bo_nho[lenh] = ket
    return ket


def quet(files, bang):
    ket_qua, bo_nho = [], {}
    for f in files:
        if f.suffix not in bang:
            log(f"bỏ qua {f} — đuôi '{f.suffix}' ngoài bảng rule", chi_tiet=True)
            continue
        ngon_ngu, lenh = bang[f.suffix]
        log(f"dò {f} → {ngon_ngu} (linter: {lenh.split()[0]})", chi_tiet=True)
        if shutil.which(lenh.split()[0]) is None:
            ket_qua.append((f, ngon_ngu, "CHƯA KIỂM ĐƯỢC", f"thiếu {lenh.split()[0]}"))
            continue
        trang_thai, ghi_chu = chay_linter(lenh, f, bo_nho)
        ket_qua.append((f, ngon_ngu, trang_thai, ghi_chu))
    return ket_qua


def in_bang(ket_qua):
    print("KẾT QUẢ QUÉT RULE")
    for f, ngon_ngu, trang_thai, ghi_chu in ket_qua:
        duoi = f" — {ghi_chu}" if ghi_chu else ""
        print(f"{f} · {ngon_ngu} · {trang_thai}{duoi}")
    dem = {t: sum(1 for k in ket_qua if k[2] == t) for t in TRANG_THAI}
    print(f"PASS: {dem['PASS']} · LỖI: {dem['LỖI']} · CHƯA KIỂM ĐƯỢC: {dem['CHƯA KIỂM ĐƯỢC']}")
    return dem["LỖI"]


def main():
    global TUY_CHON
    p = argparse.ArgumentParser(description="Quét code theo thư viện rule TDQ")
    p.add_argument("duong_dan", nargs="*", help="file/thư mục cần quét (bỏ trống = file đã đổi)")
    p.add_argument("--tat-ca", action="store_true", help="quét mọi file git quản lý")
    p.add_argument("--im", action="store_true", help="tắt hẳn log stderr")
    p.add_argument("--chi-tiet", action="store_true", help="in thêm bước dò ngôn ngữ")
    TUY_CHON = p.parse_args()
    bang = doc_bang_linter()
    files = list(gom_file(TUY_CHON.duong_dan, TUY_CHON.tat_ca))
    log(f"bắt đầu quét {len(files)} file (bảng rule: {len(bang)} đuôi)")
    ket_qua = quet(files, bang)
    so_loi = in_bang(ket_qua)
    log(f"xong — {len(ket_qua)} file có rule, {so_loi} lỗi")
    return 1 if so_loi else 0


if __name__ == "__main__":
    sys.exit(main())
