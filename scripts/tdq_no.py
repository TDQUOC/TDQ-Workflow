#!/usr/bin/env python3
"""Dependency debt: the one place the workflow writes down what it could not fix by itself.

Why it is its own module. Two very different scripts need it — `tdq_setup.py` when an install is
outside the declared allow-list, and `tdq_finish.py` when the end-of-turn reindex does not
finish. Keeping it in the setup script made the bookkeeping step import the installer, which
points the dependency the wrong way round: bookkeeping is the older, lower layer.

Nothing here talks to the network or to another tool. It appends lines to a markdown file and
touches a stamp file, and both operations are idempotent.
"""
import io
import os
import platform
from datetime import datetime

FILE_NO = os.path.join("docs", "tdq", "no-phu-thuoc.md")

DAU_FILE_NO = """# Nợ phụ thuộc

Sinh bởi `scripts/tdq_setup.py` và bước `reindex` của `scripts/tdq_finish.py`. Mỗi dòng là một
món KHÔNG tự xử lý được — vì lệnh của nó nằm ngoài danh sách đã khai, vì nó cần quyền của người,
hoặc vì nó hỏng theo cách máy không đoán được. Xử xong thì xoá dòng đó đi; file này chỉ có nghĩa
khi nó rỗng dần.

Ghi kèm tên máy vì một món có thể thiếu trên máy này mà đủ trên máy khác.

"""


def ghi_no(danh_sach, project):
    """Ghi các món chưa xử lý được vào `docs/tdq/no-phu-thuoc.md`, không nhân bản dòng cũ.

    File luôn được tạo, kể cả khi không nợ gì: "đã kiểm và không thiếu" là một thông tin, còn
    một file vắng mặt thì không phân biệt được với "chưa ai chạy setup bao giờ".

    -> số dòng MỚI vừa thêm.
    """
    duong = os.path.join(project, FILE_NO)
    os.makedirs(os.path.dirname(duong), exist_ok=True)
    cu = ""
    if os.path.isfile(duong):
        with io.open(duong, encoding="utf-8", errors="replace") as fh:
            cu = fh.read()
    if not cu.strip():
        cu = DAU_FILE_NO
    may = platform.node()
    hom_nay = datetime.now().strftime("%Y-%m-%d")
    them = [f"- {hom_nay} · {may} · {mon}\n" for mon in danh_sach
            if f"· {may} · {mon}" not in cu]
    with io.open(duong, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(cu + "".join(them))
    return len(them)


def cham_dau_moc(duong):
    """Chạm dấu mốc "vừa làm xong việc này" — nội dung là mốc thời gian, thứ đọc được bằng mắt.

    Người đọc thật của file này là `mtime` của nó, nhưng ghi cả chuỗi ISO vào trong để ai mở ra
    cũng hiểu ngay đây là cái gì, thay vì một file rỗng không tên tuổi.
    """
    os.makedirs(os.path.dirname(os.path.abspath(duong)), exist_ok=True)
    with io.open(duong, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + "\n")
