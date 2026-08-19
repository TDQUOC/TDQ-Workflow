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
   TDQ:OUTPUT— lệnh đổ nguyên file/lịch sử vào context mà không giới hạn dòng.
"""
import os
import re

from _common import (echo_line, observe, payload_cwd, read_payload, remind,
                     remind_force, turn_rows)

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
# Lệnh có xu hướng đổ trọn nội dung vào context. Mỗi output bị model đọc lại ở MỌI
# API call còn lại của phiên, nên một lần đổ thừa nhân lên hàng trăm lần chính nó.
DUMP = re.compile(
    r"(?:^|[|;&]|\bthen\b|\bdo\b)\s*(cat|git\s+log|git\s+diff|git\s+show|ls\s+-R)\b")
# Dấu hiệu lệnh ĐÃ tự giới hạn — có một dấu là đủ im.
GIOI_HAN = re.compile(
    r"\|\s*(?:head|tail|wc|jq|sed\s+-n)\b"      # nối sang lệnh cắt
    r"|\b(?:head|tail)\b"
    r"|(?:^|\s)-[a-zA-Z]*[nc]\s*\d"              # -n 20 · -c 500 · -n20
    r"|--stat\b|--name-only\b|--oneline\b|--shortstat\b|--numstat\b"
    r"|\|\s*grep\b[^|]*\s-[a-zA-Z]*[clq]\b")
# `cat > f <<EOF` là GHI file, không phải đọc — nhắc ở đây chỉ tạo nhiễu.
CAT_GHI = re.compile(r"\bcat\b[^|;&]*(?:<<|>)")

STATE_CLI = re.compile(r"tdq_state\.py\s+(\w[\w-]*)")
# nhanh|express là bí danh CLI của quick (xem LANE_ALIASES trong tdq_state).
APPROVE_CLI = re.compile(r"tdq_state\.py\s+approve\s+(spec|plan|quick|nhanh|express)\b")
SETPHASE_CLI = re.compile(r"tdq_state\.py\s+set\b.*?\bphase=(\w+)")
NEXT_PHASE_TARGET = {"plan": "spec", "implement": "plan"}


def _latest_signal(rows, target):
    """Dòng kind="signal" GẦN NHẤT khớp target (duyệt ngược sổ turn)."""
    for row in reversed(rows):
        if row.get("kind") == "signal" and row.get("target") == target:
            return row
    return None


def _check_signal_mismatch(cwd, payload, target, rows):
    row = _latest_signal(rows, target)
    if row is None:
        return
    if row.get("matched") is False or row.get("mode_conflict") is True:
        remind_force(cwd, payload, "TDQ:APPROVE", [
            f"Prompt gần nhất KHÔNG rõ là câu duyệt {target} (hoặc mode lệch) — DỪNG, "
            "đừng chạy lệnh này.",
            "Cách làm: HỎI lại user xác nhận duyệt trước khi gọi approve/set phase.",
            echo_line("TDQ:APPROVE", "đã hỏi lại và có xác nhận rõ ràng"),
        ])


def _clean(raw):
    return raw.strip("'\"")


def main():
    payload = read_payload()
    cmd = (payload.get("tool_input") or {}).get("command") or ""
    if not isinstance(cmd, str) or not cmd:
        return
    cwd = payload_cwd(payload)
    rows = turn_rows(cwd, payload)  # P0-3: đọc 1 lần, dùng lại cho mọi kiểm tra dưới đây

    # (1) quan sát
    for sub in STATE_CLI.findall(cmd):
        observe(cwd, payload, "state_cli", cmd=sub)
        if sub == "next":
            observe(cwd, payload, "next_run")

    # (2) nhắc — chặn-tiến-phase (approve/set phase=) ưu tiên hơn GIT/STATE
    approve_match = APPROVE_CLI.search(cmd)
    if approve_match:
        _check_signal_mismatch(cwd, payload, approve_match.group(1), rows)
    setphase_match = SETPHASE_CLI.search(cmd)
    if setphase_match:
        target = NEXT_PHASE_TARGET.get(setphase_match.group(1))
        if target:
            _check_signal_mismatch(cwd, payload, target, rows)

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
            ], rows=rows)

    if re.search(r"git\b.*\bcommit\b", cmd, re.DOTALL):
        for pattern in BAD_MSG:
            if pattern.search(cmd):
                remind(cwd, payload, "TDQ:GIT", [
                    "Commit message mang dấu vết AI — phạm quy ước.",
                    "Cách làm: bỏ 'generated with …', 'được tạo cùng/với AI' và Co-Authored-By AI.",
                    echo_line("TDQ:GIT", "đã sửa commit message"),
                ], rows=rows)

    if DUMP.search(cmd) and not GIOI_HAN.search(cmd) and not CAT_GHI.search(cmd):
        remind(cwd, payload, "TDQ:OUTPUT", [
            "Lệnh này đổ trọn nội dung vào context — mỗi output còn bị đọc lại ở mọi "
            "API call sau nó.",
            "Cách làm: giới hạn ngay trong lệnh (`head`/`tail`/`sed -n`/`-n`/`--stat`/"
            "`--oneline`), hoặc dùng Read với `offset`/`limit`. Cần trọn file thì cứ "
            "chạy — chất lượng đứng trên context cost.",
            echo_line("TDQ:OUTPUT", "đã giới hạn output hoặc xác nhận cần trọn"),
        ], rows=rows)

    if re.search(STATE, cmd):
        for pattern in STATE_WRITES:
            if pattern.search(cmd):
                remind(cwd, payload, "TDQ:STATE", [
                    "Đừng ghi thẳng file trạng thái qua shell.",
                    "Cách làm: python3 scripts/tdq_state.py set|approve|init|reset.",
                    echo_line("TDQ:STATE", "đã ghi state bằng CLI"),
                ], rows=rows)


if __name__ == "__main__":
    main()
