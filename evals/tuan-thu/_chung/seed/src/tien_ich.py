"""Mô-đun tiện ích của dự án giả lập, dùng làm sân cho phiên đo."""


def gop_ten(ho, ten):
    return f"{ho} {ten}".strip()


def dem_tu(cau):
    return len([t for t in cau.split() if t])
