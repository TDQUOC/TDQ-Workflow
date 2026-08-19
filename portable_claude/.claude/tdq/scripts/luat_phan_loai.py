#!/usr/bin/env python3
"""Gợi ý nhãn cho từng điểm neo luật: `ly-luan` hay `user-facing`.

Điều kiện tiền đề (a) của hướng A. Bộ workflow chỉ được viết bằng tiếng Anh ở phần LUẬT
LÝ LUẬN; phần KHUÔN USER-FACING (câu in ra chat, khuôn báo cáo, ví dụ few-shot) phải giữ
tiếng Việt. Script này KHÔNG quyết — nó gợi ý để người soát nhanh hơn, và lời khai cuối
cùng nằm ở `docs/tdq/audit/ranh-gioi-luat.md` do người chốt.

Cách dùng:
    python3 scripts/luat_phan_loai.py --bang docs/tdq/audit/luat-hien-co.md

In bảng markdown ra stdout: `| mã | nguồn | nhãn gợi ý | vì sao |`.
Env: TDQ_LOG=0 tắt log service (mặc định bật, ISO-timestamp ra stderr).
"""
import argparse
import collections
import os
import re
import sys
from datetime import datetime

Goi = collections.namedtuple("Goi", "nhan ly_do")
Dong = collections.namedtuple("Dong", "nhan chu")

LY_LUAN = "ly-luan"
USER_FACING = "user-facing"

# Bảng điểm neo: `| L001 | `file:dòng` | chữ neo |`. Cùng khuôn mà tests/test_luat_skill.py
# đọc — sửa khuôn ở một chỗ là phải sửa cả hai, nên giữ nguyên.
DONG_BANG = re.compile(r"^\| (L\d+) \| `([^`:]+):(\d+)` \|")
# Ô ngăn bằng dấu `|` KHÔNG bị escape — nội dung luật có thể mang `\|` của markdown.
# Bảng có cột thứ tư `neo bản mới` (để trống cho tới khi luật được viết lại); bộ phân
# loại chỉ cần cột nội dung, nhưng phải tách ô cho đúng thay vì bắt tới `|` cuối dòng.
O_BANG = re.compile(r"(?<!\\)\|")
DONG_RANH_GIOI = re.compile(r"^\| (L\d+) \| ([\w-]+) \| (.*?) \|$")

# File mà TOÀN BỘ nội dung là khuôn cho user đọc: đổi chữ trong đó là đổi thứ user thấy.
FILE_KHUON = ("-template.md", "user-facing-block.md", "interview.md",
              "lane-decision.md", "scope-round.md")

# Dấu hiệu trong chính câu luật. Mỗi dấu hiệu kèm lý do để bảng gợi ý đọc được, không
# phải một nhãn trần trụi bắt người soát tự đoán vì sao máy nghĩ vậy.
DAU_HIEU = (
    (re.compile(r"➤"), "chứa ký hiệu của khối duyệt user thấy"),
    (re.compile(r"\bin ra chat\b", re.I), "nói thẳng là in ra chat"),
    (re.compile(r"\bin đúng dòng\b", re.I), "ra lệnh in nguyên văn một dòng"),
    (re.compile(r"\bnhắn\b", re.I), "mô tả câu user nhắn lại"),
    (re.compile(r"\bkhuôn\b", re.I), "nói về khuôn văn bản"),
    (re.compile(r"\boption\b", re.I), "nói về option của câu hỏi"),
    (re.compile(r"\bcâu hỏi\b", re.I), "nói về câu hỏi cho user"),
    (re.compile(r"\btrình bày\b", re.I), "nói về cách trình bày cho user"),
    (re.compile(r"\bnguyên văn\b", re.I), "đòi giữ nguyên văn chữ"),
    (re.compile(r"\buser thấy\b", re.I), "nói về thứ user nhìn thấy"),
    (re.compile(r"\btiếng Việt\b", re.I), "khai báo ngôn ngữ đầu ra"),
)


def _log(message):
    """Log service: 1 dòng ISO-timestamp ra stderr. Tắt bằng TDQ_LOG=0.

    Ra stderr vì stdout là bảng máy đọc — lẫn log vào đó là hỏng hợp đồng.
    """
    if os.environ.get("TDQ_LOG", "1") != "0":
        print(f"[{datetime.now().isoformat(timespec='seconds')}] luat_phan_loai: {message}",
              file=sys.stderr)


def doc_bang(path):
    """Bảng điểm neo → [(mã, đường dẫn, số dòng, chữ neo)] theo đúng thứ tự trong file."""
    ban = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = DONG_BANG.match(line.rstrip("\n"))
            if m:
                o = O_BANG.split(line.rstrip("\n").strip())[1:-1]
                ban.append((m.group(1), m.group(2), int(m.group(3)), o[2].strip()))
    return ban


def doc_ranh_gioi(path):
    """Bảng người soát đã chốt → {mã: Dong(nhãn, chữ)}."""
    ban = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = DONG_RANH_GIOI.match(line.rstrip("\n"))
            if m and m.group(2) in (LY_LUAN, USER_FACING):
                ban[m.group(1)] = Dong(m.group(2), m.group(3).strip())
    return ban


def liet_ke_ma(path):
    """Danh sách mã theo đúng thứ tự file, GIỮ cả mã trùng.

    `doc_ranh_gioi` trả dict nên dòng trùng bị đè lặng lẽ; muốn bắt trùng thì phải
    đếm trên danh sách thô này.
    """
    thu = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = DONG_RANH_GIOI.match(line.rstrip("\n"))
            if m and m.group(2) in (LY_LUAN, USER_FACING):
                thu.append(m.group(1))
    return thu


def goi_y_nhan(duong_dan, chu, trong_khoi_ma=False):
    """Nhãn gợi ý cho một điểm neo, kèm lý do.

    Thứ tự xét đi từ dấu hiệu CHẮC nhất tới dấu hiệu mềm nhất: nằm trong khối mã của
    skill → là khuôn copy được; nằm trong file khuôn → cả file là khuôn; còn lại thì
    soi chính câu chữ. Không dấu hiệu nào khớp thì mặc định là luật lý luận, vì đó là
    loại chiếm đa số — nhưng vẫn ghi lý do để người soát biết máy dựa vào đâu.
    """
    if trong_khoi_ma:
        return Goi(USER_FACING, "nằm trong khối mã — khuôn copy được")
    ten = os.path.basename(duong_dan)
    for duoi in FILE_KHUON:
        if ten.endswith(duoi):
            return Goi(USER_FACING, f"cả file `{ten}` là khuôn cho user")
    for mau, ly_do in DAU_HIEU:
        if mau.search(chu):
            return Goi(USER_FACING, ly_do)
    return Goi(LY_LUAN, "không thấy dấu hiệu user-facing trong câu")


def bang_nhap(ban):
    """[(mã, đường dẫn, dòng, chữ)] → các dòng markdown của bảng nháp."""
    ra = ["| Mã | Nguồn | Nhãn gợi ý | Vì sao |", "|---|---|---|---|"]
    for ma, duong_dan, dong, chu in ban:
        goi = goi_y_nhan(duong_dan, chu)
        ra.append(f"| {ma} | `{duong_dan}:{dong}` | {goi.nhan} | {goi.ly_do} |")
    return ra


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bang", required=True, help="đường dẫn bảng điểm neo")
    args = parser.parse_args(argv)
    _log(f"đọc bảng điểm neo: {args.bang}")
    ban = doc_bang(args.bang)
    _log(f"đọc được {len(ban)} điểm neo")
    dong = bang_nhap(ban)
    print("\n".join(dong))
    so_uf = sum(1 for d in dong if f"| {USER_FACING} |" in d)
    _log(f"gợi ý: {so_uf} user-facing, {len(ban) - so_uf} ly-luan")
    return 0


if __name__ == "__main__":
    sys.exit(main())
