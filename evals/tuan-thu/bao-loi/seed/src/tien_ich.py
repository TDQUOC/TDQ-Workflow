"""Mô-đun tiện ích của dự án giả lập, dùng làm sân cho phiên đo.

Bản riêng của ca `bao-loi`: `dem_tu` cắt theo đúng một dấu cách nên chuỗi rỗng ra 1 thay
vì 0. Bộ test sẵn có không phủ ca rỗng nên repo vẫn xanh — đúng cảnh user báo lỗi thật.
"""


def gop_ten(ho, ten):
    return f"{ho} {ten}".strip()


def dem_tu(cau):
    return len(cau.split(" "))
