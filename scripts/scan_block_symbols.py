#!/usr/bin/env python3
"""Quét ký hiệu ngoài ASCII trong các file giữ khuôn khối nói với user.

Lý do tồn tại: trước khi siết `tests/test_user_facing_block.py` thành whitelist ký hiệu,
phải biết 12 file trong phạm vi kiểm đang thật sự dùng những ký tự nào. Siết mù sẽ làm
test đỏ oan vì một ký tự hợp lệ có sẵn (spec §5, rủi ro 2).

Chỉ đếm ký tự thuộc Unicode category P* (dấu câu) và S* (ký hiệu) và nằm ngoài ASCII.
Chữ tiếng Việt thuộc category L* nên không bị đụng — đó là điều làm whitelist khả thi.

Dùng:
    python3 scripts/scan_block_symbols.py              # bảng markdown, exit 0
    python3 scripts/scan_block_symbols.py --lieu-ke    # thêm cột số lần theo từng file
    python3 scripts/scan_block_symbols.py --chi-khoi   # chỉ phần in ra cho user
"""
import argparse
import os
import sys
import unicodedata
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Whitelist chốt ở T0.2 (xem `docs/tdq/qc/2026-08-14-trang-tri-khoi-chat.md`): sáu ký tự,
# tất cả đều có bằng chứng đang chạy thật trong khối mẫu in ra cho user. Ba ký tự đầu do
# user chọn ở vòng interview 2; ba ký tự sau được nhận vào theo đúng luật 2A (có bằng
# chứng chạy thật). Ký tự `▸` bị loại vì grep toàn repo ra 0 kết quả.
WHITELIST = ("➤", "·", "—", "→", "–", "…")

# 12 file giữ khuôn hoặc chép khối mẫu — phạm vi mà whitelist sẽ áp.
SCOPE = (
    "skills/tdq-conventions/references/user-facing-block.md",
    "skills/tdq-spec/SKILL.md",
    "skills/tdq-plan/SKILL.md",
    "skills/tdq-plan/references/mode-gate.md",
    "skills/tdq-intake/references/lane-decision.md",
    "skills/tdq-intake/references/quick-lane.md",
    "skills/tdq-intake/references/interview.md",
    "skills/tdq-build/references/report-template.md",
    "skills/tdq-status/SKILL.md",
    "portable/workflow/02-spec.md",
    "portable/workflow/03-plan.md",
    "portable/workflow/references/user-facing-block.md",
)


def la_ky_hieu(ch):
    """True khi ch là dấu câu/ký hiệu ngoài ASCII — thứ whitelist phải quản."""
    if ord(ch) < 128:
        return False
    return unicodedata.category(ch)[0] in ("P", "S")


def khoi_mau(text):
    """Nội dung các khối ``` trong file — đây mới là phần THẬT SỰ in ra cho user.

    Văn xuôi hướng dẫn quanh khối không bao giờ tới mắt user, nên whitelist không quản.
    """
    ra, trong_khoi = [], False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            trong_khoi = not trong_khoi
            continue
        if trong_khoi:
            ra.append(line)
    return "\n".join(ra)


def quet(paths, chi_khoi=False):
    """{ký tự: (tổng số lần, {file: số lần})} cho mọi ký hiệu ngoài ASCII."""
    tong = Counter()
    theo_file = defaultdict(Counter)
    for rel in paths:
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            print(f"CẢNH BÁO: thiếu file {rel}", file=sys.stderr)
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        if chi_khoi:
            text = khoi_mau(text)
        for ch in text:
            if la_ky_hieu(ch):
                tong[ch] += 1
                theo_file[ch][rel] += 1
    return tong, theo_file


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lieu-ke", action="store_true",
                    help="in thêm cột liệt kê file dùng ký tự đó")
    ap.add_argument("--chi-khoi", action="store_true",
                    help="chỉ quét nội dung các khối ``` (phần thật sự in ra cho user)")
    args = ap.parse_args(argv)

    tong, theo_file = quet(SCOPE, chi_khoi=args.chi_khoi)
    print(f"| Ký tự | Codepoint | Tên Unicode | Số lần | Trong whitelist? |"
          + (" File |" if args.lieu_ke else ""))
    print("|---|---|---|---|---|" + ("---|" if args.lieu_ke else ""))
    for ch, n in sorted(tong.items(), key=lambda kv: (-kv[1], ord(kv[0]))):
        ten = unicodedata.name(ch, "?")
        trong = "CÓ" if ch in WHITELIST else "**KHÔNG**"
        dong = f"| `{ch}` | U+{ord(ch):04X} | {ten} | {n} | {trong} |"
        if args.lieu_ke:
            dong += " " + ", ".join(sorted(theo_file[ch])) + " |"
        print(dong)

    la = [ch for ch in tong if ch not in WHITELIST]
    print()
    print(f"Tổng: {len(tong)} ký hiệu khác nhau trên {len(SCOPE)} file · "
          f"{len(la)} ký tự NGOÀI whitelist cần quyết định.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
