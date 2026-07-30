#!/usr/bin/env python3
"""SessionStart — nạp ngữ cảnh đầu session.

Dòng luật tuân thủ đứng TRƯỚC, rồi tới nguyên khối `tdq_state.py next` (nguồn
sự thật duy nhất về "đang ở đâu, làm gì tiếp") và tình trạng graphify. Thứ tự
này quan trọng: trần 600 ký tự cắt phần đuôi, luật không được nằm ở đuôi.
Chưa có request cũng vẫn in — phase `no_state` chỉ đường mở request mới.
Trần ngân sách: ≤12 dòng / 600 ký tự (spec §2.7).
"""
import shutil

from _common import payload_cwd, read_payload, tdq_state

MAX_LINES = 12
MAX_CHARS = 600

RULE = ("[TDQ] Luật: thấy dòng [TDQ:<MÃ>] → làm đúng việc trong đó TRƯỚC, "
        "xong in ✓ [TDQ:<MÃ>]. Ghi state chỉ bằng scripts/tdq_state.py.")


def main():
    payload = read_payload()
    cwd = payload_cwd(payload)
    state = tdq_state.load(cwd) or tdq_state.default_state()

    lines = [RULE] + tdq_state.render_next(cwd, state, compact=True).splitlines()
    if shutil.which("graphify") is None:
        lines.append("[TDQ] graphify chưa cài (tùy chọn): uv tool install graphifyy")

    text = "\n".join(lines[:MAX_LINES])
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS - 1].rstrip() + "…"
    print(text)


if __name__ == "__main__":
    main()
