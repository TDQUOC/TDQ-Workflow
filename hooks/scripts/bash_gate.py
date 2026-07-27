#!/usr/bin/env python3
"""PreToolUse gate for Bash.

(a) Enforces git naming rules: branch/worktree names must not start with
    claude|antigravity|gemini|codex; commit messages must not contain
    "generated with <ai>" / "được tạo cùng/với/bởi <ai>" / AI Co-Authored-By.
(b) Protects docs/tdq/state.json from direct Bash writes (redirect, tee,
    sed -i, mv/cp, truncate, inline python). Reads (cat/jq/grep) stay allowed.
"""
import os
import re

from _common import read_payload, deny

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
STATE = r"docs/tdq/state\.json"
STATE_WRITES = [
    re.compile(r">{1,2}\s*['\"]?\S*" + STATE),
    re.compile(r"\btee\b[^|;&]*" + STATE),
    re.compile(r"\bsed\b[^;|&]*\s-i[^;|&]*" + STATE),
    re.compile(r"\b(?:mv|cp)\b[^;|&]*" + STATE),
    re.compile(r"\btruncate\b[^;|&]*" + STATE),
    re.compile(r"\bpython3?\b[^;|&]*" + STATE),
    re.compile(r"\bopen\([^)]*" + STATE),
]


def _clean(raw):
    return raw.strip("'\"")


def main():
    payload = read_payload()
    cmd = (payload.get("tool_input") or {}).get("command") or ""
    if not isinstance(cmd, str) or not cmd:
        return

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
            deny(f"[TDQ GATE] Tên branch/worktree '{name}' vi phạm quy ước — "
                 "không được bắt đầu bằng claude|antigravity|gemini|codex.")

    if re.search(r"git\b.*\bcommit\b", cmd, re.DOTALL):
        for pattern in BAD_MSG:
            if pattern.search(cmd):
                deny("[TDQ GATE] Commit message vi phạm quy ước — không chèn "
                     "'generated with claude/gemini/codex/...', 'được tạo cùng/với AI' hoặc Co-Authored-By AI.")

    if re.search(STATE, cmd):
        for pattern in STATE_WRITES:
            if pattern.search(cmd):
                deny("[TDQ GATE] Không ghi trực tiếp docs/tdq/state.json qua Bash — dùng scripts/tdq_state.py; "
                     "field duyệt chỉ đổi khi user gõ /tdq-workflow:tdq-approve.")


if __name__ == "__main__":
    main()
