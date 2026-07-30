#!/usr/bin/env python3
"""PreToolUse (Bash) — quan sát + nhắc, KHÔNG chặn.

1. Quan sát vào sổ turn: `state_cli` khi lệnh gọi scripts/tdq_state.py,
   `next_run` khi lệnh đó là `next`. Đây là bằng chứng để stop_gate biết agent
   đã thật sự chạy lệnh, thay vì tin dòng echo model tự in.
2. Nhắc:
   TDQ:GIT   — tên branch/worktree bắt đầu bằng claude|antigravity|gemini|codex;
               commit message mang dấu vết AI ("generated with…", Co-Authored-By).
   TDQ:STATE — ghi thẳng docs/tdq/state.json | STATE.md qua shell (redirect, tee,
               sed -i, mv/cp, truncate, python inline).
"""
import os
import re

from _common import echo_line, observe, payload_cwd, read_payload, remind

BAN = re.compile(r"^(claude|antigravity|gemini|codex)", re.IGNORECASE)
BRANCH_PATTERNS = [
    re.compile(r"git\s+checkout\s+-b\s+(\S+)"),
    re.compile(r"git\s+switch\s+(?:-c|--create)\s+(\S+)"),
    re.compile(r"git\s+branch\s+(?!-)(\S+)"),
]
WORKTREE = re.compile(r"git\s+worktree\s+add\s+(?:-b\s+(\S+)\s+)?(\S+)")
BAD_MSG = [
    re.compile(r"generated\s+with.{0,40}?(claude|gemini|codex|antigravity)", re.IGNORECASE | re.DOTALL),
    re.compile(r"được\s+tạo\s+(?:cùng|với|bởi).{0,40}?(claude|gemini|codex|antigravity)", re.IGNORECASE | re.DOTALL),
    re.compile(r"co-authored-by:.{0,60}?(claude|gemini|codex|antigravity)", re.IGNORECASE),
]
STATE = r"docs/tdq/(?:state\.json|STATE\.md)"
STATE_WRITES = [
    re.compile(r">{1,2}\s*['\"]?\S*" + STATE),
    re.compile(r"\btee\b[^|;&]*" + STATE),
    re.compile(r"\bsed\b[^;|&]*\s-i[^;|&]*" + STATE),
    re.compile(r"\b(?:mv|cp)\b[^;|&]*" + STATE),
    re.compile(r"\btruncate\b[^;|&]*" + STATE),
    re.compile(r"\bpython3?\b[^;|&]*" + STATE),
    re.compile(r"\bopen\([^)]*" + STATE),
]
STATE_CLI = re.compile(r"tdq_state\.py\s+(\w[\w-]*)")


def _clean(raw):
    return raw.strip("'\"")


def main():
    payload = read_payload()
    cmd = (payload.get("tool_input") or {}).get("command") or ""
    if not isinstance(cmd, str) or not cmd:
        return
    cwd = payload_cwd(payload)

    # (1) quan sát
    for sub in STATE_CLI.findall(cmd):
        observe(cwd, payload, "state_cli", cmd=sub)
        if sub == "next":
            observe(cwd, payload, "next_run")

    # (2) nhắc
    branch_names = []
    for pattern in BRANCH_PATTERNS:
        branch_names += [_clean(m) for m in pattern.findall(cmd)]
    for b_name, path in WORKTREE.findall(cmd):
        if b_name:
            branch_names.append(_clean(b_name))
        if path:
            branch_names.append(os.path.basename(_clean(path).rstrip("/")))
    for name in branch_names:
        if BAN.match(name):
            remind(cwd, payload, "TDQ:GIT", [
                f"Tên branch/worktree '{name}' phạm quy ước — đổi tên trước khi chạy.",
                "Cách làm: bỏ tiền tố claude|antigravity|gemini|codex, đặt tên theo nội dung việc.",
                echo_line("TDQ:GIT", "đã đổi tên đúng quy ước"),
            ])

    if re.search(r"git\b.*\bcommit\b", cmd, re.DOTALL):
        for pattern in BAD_MSG:
            if pattern.search(cmd):
                remind(cwd, payload, "TDQ:GIT", [
                    "Commit message mang dấu vết AI — phạm quy ước.",
                    "Cách làm: bỏ 'generated with …', 'được tạo cùng/với AI' và Co-Authored-By AI.",
                    echo_line("TDQ:GIT", "đã sửa commit message"),
                ])

    if re.search(STATE, cmd):
        for pattern in STATE_WRITES:
            if pattern.search(cmd):
                remind(cwd, payload, "TDQ:STATE", [
                    "Đừng ghi thẳng file trạng thái qua shell.",
                    "Cách làm: python3 scripts/tdq_state.py set|approve|init|reset.",
                    echo_line("TDQ:STATE", "đã ghi state bằng CLI"),
                ])


if __name__ == "__main__":
    main()
