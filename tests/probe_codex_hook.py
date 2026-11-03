#!/usr/bin/env python3
"""Hook thăm dò — ghi lại NGUYÊN payload Codex gửi cho hook, để chốt hai ẩn số của R2.

Vì sao cần: `.codex/hooks.json` phải ghi một chuỗi `command`, mà chuỗi đó chỉ đúng nếu biết
Codex chạy tiến trình hook với thư mục làm việc nào. Và `matcher` chỉ đúng nếu biết tên tool
THẬT mà Codex đặt cho tool sửa file / tool chạy lệnh. Cả hai không có trong tài liệu — đoán
rồi sửa sau chính là lỗi đã sinh ra request này.

File này KHÔNG đi theo bản portable: nó sống trong `tests/` và chỉ chạy ở phase trinh sát.

Ghi ra: `$TDQ_PROBE_OUT` (mặc định `probe-codex-hook.jsonl`) — mỗi lần gọi một dòng JSON:
    {"cwd_process": <os.getcwd()>, "argv": [...], "payload": <nguyên payload stdin>}

Luôn in ra stdout một JSON rỗng hợp lệ và exit 0 để không chặn phiên codex đang thăm dò.
"""
import json
import os
import sys


def doc_payload():
    """Payload stdin, hoặc dict báo lỗi — tuyệt đối không ném để khỏi làm hỏng phiên thăm dò."""
    try:
        raw = sys.stdin.read()
    except OSError as loi:
        return {"_loi_doc_stdin": str(loi)}
    if not raw.strip():
        return {"_stdin_rong": True}
    try:
        return json.loads(raw)
    except ValueError:
        # Không phải JSON cũng là dữ liệu đáng giá: nó bác bỏ giả định "input là JSON".
        return {"_stdin_khong_phai_json": raw[:2000]}


def main(argv=None):
    argv = list(sys.argv if argv is None else argv)
    ban_ghi = {
        "cwd_process": os.getcwd(),
        "argv": argv,
        "payload": doc_payload(),
    }
    duong = os.environ.get("TDQ_PROBE_OUT") or "probe-codex-hook.jsonl"
    try:
        with open(duong, "a", encoding="utf-8") as f:
            f.write(json.dumps(ban_ghi, ensure_ascii=False) + "\n")
    except OSError as loi:
        # Mất chỗ ghi thì báo ra stderr, vẫn không chặn phiên.
        print(f"probe: không ghi được {duong}: {loi}", file=sys.stderr)
    print("{}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
