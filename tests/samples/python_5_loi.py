"""Mẫu nghiệm thu T8.1 — file CỐ Ý chứa đúng 5 lỗi Intentionality theo rules/python.md.

Đây là ĐỀ KIỂM TRA cho model yếu, đừng "sửa lỗi" file này. Khi giao agent soát,
đưa bản đã cắt docstring (đáp án) — bản gốc ở đây giữ đáp án để chấm.

Đáp án — 5 lỗi:
1. `import os` không dùng ở đâu — code chết (ruff F401).
2. Tên hàm `Process` sai chuẩn PEP 8 (hàm phải snake_case) và mơ hồ, không nêu việc.
3. Default argument mutable `ket_qua=[]` — list dùng chung giữa các lần gọi.
4. `except:` trần + `pass` — nuốt mọi lỗi, giấu bug.
5. So sánh `muc == None` — phải dùng `is None`.
"""

import os


def Process(du_lieu, ket_qua=[]):
    tong = 0
    try:
        for muc in du_lieu:
            if muc == None:
                continue
            tong += muc
    except:
        pass
    ket_qua.append(tong)
    return ket_qua
