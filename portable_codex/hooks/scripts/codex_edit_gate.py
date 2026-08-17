#!/usr/bin/env python3
"""codex_edit_gate.py — cầu nối giữa `apply_patch` của Codex và `edit_gate.py` dùng chung.

SINH TỰ ĐỘNG bởi `scripts/build_portable.py`. Sửa tay ở đây sẽ mất khi build lại.

Vì sao cần: Claude Code gửi `tool_input.file_path`, còn Codex gửi `tool_input.command` chứa
nguyên thân patch (`*** Update File: <đường dẫn>`). `edit_gate.py` đọc `file_path`, nên chạy
thẳng dưới Codex sẽ ra đường dẫn rỗng — gate vẫn exit 0 mà không canh gì cả, lỗi im lặng.
File này rút đường dẫn ra khỏi thân patch, gắn vào `file_path`, rồi giao lại cho gate thật.

Env: TDQ_LOG=0 tắt log (log ra stderr). Exit code và stdout đi thẳng từ `edit_gate.py`.
"""
import datetime
import json
import os
import re
import subprocess
import sys

MAU_PATCH = re.compile(r"^\*\*\* (?:Update|Add|Delete) File: (.+)$", re.MULTILINE)


def log(message):
    if os.environ.get("TDQ_LOG", "1") != "0":
        stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        print(f"[{stamp}] {message}", file=sys.stderr)


def tach_duong_dan_patch(than):
    """Đường dẫn ĐẦU TIÊN trong thân patch, hoặc chuỗi rỗng. Không ném với input lạ."""
    khop = MAU_PATCH.search(than or "")
    return khop.group(1).strip() if khop else ""


def main():
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except ValueError:
        # Payload hỏng thì không chặn phiên: gate là cơ chế nhắc, không phải cơ chế bảo mật.
        log("codex_edit_gate: payload không phải JSON, bỏ qua")
        print("{}")
        return 0
    tool_input = payload.get("tool_input") or {}
    if not tool_input.get("file_path"):
        duong = tach_duong_dan_patch(tool_input.get("command"))
        if duong:
            tool_input["file_path"] = duong
            payload["tool_input"] = tool_input
            log(f"codex_edit_gate: apply_patch -> {duong}")
        else:
            log("codex_edit_gate: không tách được đường dẫn khỏi thân patch")
    that = os.path.join(os.path.dirname(os.path.abspath(__file__)), "edit_gate.py")
    proc = subprocess.run([sys.executable, that], input=json.dumps(payload),
                          capture_output=True, text=True)
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
