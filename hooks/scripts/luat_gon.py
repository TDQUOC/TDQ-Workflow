#!/usr/bin/env python3
"""Bộ đọc–lọc thân luật tinh gọn cho ba kênh nạp luật (T2.1).

Luật được viết MỘT chỗ duy nhất — `skills/tdq-build/references/rules/chung.md`, khối giữa
cặp marker `luat-gon` — rồi hook đọc từ đĩa và lọc theo mức gắt. Ở đây không chép lại một
chữ nào của luật: chép là có hai bản luật, và bản trong code sẽ lệch trước.

Hai hàm thuần, không class, không state:
    doc_than_luat(goc)            -> khối luật thô, hoặc "" kèm một dòng cảnh báo ra stderr
    loc_than_luat(than, muc_gat)  -> khối đã lọc theo `lite|full|ultra|off`

Fail-closed: mức lạ, rỗng hay None đều xử như `full` — không suy luận nào của agent chọn
được `off`, chỉ user đặt `muc_gat=off` mới tắt được (bảng cường độ trong chung.md).
"""
import os
import sys

MARKER_MO = "<!-- luat-gon:bat-dau -->"
MARKER_DONG = "<!-- luat-gon:ket-thuc -->"
DUONG_DAN_LUAT = ("skills", "tdq-build", "references", "rules", "chung.md")

# Tiêu đề `###` bị cắt ở từng mức; chép nguyên văn tiêu đề trong chung.md, không phải luật.
MUC_BANG_CUONG_DO = "### Intensity table"
MUC_VI_DU = "### RIGHT / WRONG for this law"
MUC_ULTRA = "### Extra at level ultra"

CAT_THEO_MUC = {
    "off": (),  # trả rỗng ngay, không cần danh sách cắt
    "lite": (MUC_BANG_CUONG_DO, MUC_VI_DU, MUC_ULTRA),
    "full": (MUC_ULTRA,),
    "ultra": (),
}
MUC_MAC_DINH = "full"


def doc_than_luat(goc):
    """Khối luật giữa cặp marker trong chung.md của project `goc`.

    Thiếu file, thiếu marker hay marker đảo thứ tự → trả "" và in MỘT dòng cảnh báo ra
    stderr. Hook nạp luật không được chết vì một file luật bị sửa tay.
    """
    duong_dan = os.path.join(goc, *DUONG_DAN_LUAT)
    try:
        with open(duong_dan, encoding="utf-8") as f:
            text = f.read()
    except OSError as err:
        print(f"luat_gon: không đọc được thân luật ({err})", file=sys.stderr)
        return ""
    mo = text.find(MARKER_MO)
    dong = text.find(MARKER_DONG)
    if mo < 0 or dong <= mo:
        print(f"luat_gon: thiếu cặp marker luat-gon trong {duong_dan}", file=sys.stderr)
        return ""
    return text[mo + len(MARKER_MO):dong].strip()


def loc_than_luat(than, muc_gat):
    """Khối luật đã lọc theo mức gắt. Thân rỗng hoặc mức `off` → "".

    Lọc theo tiêu đề `###`: gặp tiêu đề nằm trong danh sách cắt thì bỏ cả mục đó cho tới
    tiêu đề kế tiếp. Bậc thang và hai phán quyết của user (log service, test mỗi task
    red → green) không nằm trong danh sách cắt của mức nào, nên mọi mức khác `off` đều giữ.
    """
    if not than:
        return ""
    muc = muc_gat if muc_gat in ("lite", "full", "ultra", "off") else MUC_MAC_DINH
    if muc == "off":
        return ""
    bo = CAT_THEO_MUC[muc]
    giu, dang_bo = [], False
    for dong in than.splitlines():
        if dong.startswith("### "):
            dang_bo = dong.strip() in bo
        if not dang_bo:
            giu.append(dong)
    return "\n".join(giu).strip()
