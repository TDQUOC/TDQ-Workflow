#!/usr/bin/env python3
"""Stop gate, two checks, blocking ONCE per turn (`stop_hook_active`):

1. Invitation check: the approve line must never reach the user unless state can
   actually honour it (open request, right lane, detail file registered, not
   already approved). Otherwise the user types the command and gets refused.
2. Working log check: if this turn changed the repo (a file is newer than
   today's working log, within a recent window) but the log was not updated
   afterwards, remind (working log + graphify + plan ticks).
"""
import json
import os
import re
import time
from datetime import datetime

from _common import read_payload, payload_cwd, tdq_state

INVITE_RE = re.compile(r"/tdq-workflow:tdq-approve\s+(spec|plan|quick)\b")
FIX = ("Sửa trước khi kết thúc turn: mở/chỉnh request bằng "
       "`python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py\" init <slug> <quick|full>` "
       "(và đăng ký spec_file/plan_file nếu là lane full), rồi trình lại và mời duyệt.")


def last_assistant_text(path):
    """Text of the most recent assistant message in the transcript (or '')."""
    if not path or not os.path.isfile(path):
        return ""
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return ""
    for line in reversed(lines):
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        message = entry.get("message") or {}
        if entry.get("type") != "assistant" and message.get("role") != "assistant":
            continue
        content = message.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = [c.get("text", "") for c in content
                     if isinstance(c, dict) and c.get("type") == "text"]
            text = "\n".join(p for p in parts if p)
            if text.strip():
                return text
    return ""


def invite_problem(state, target, cwd):
    """Vietnamese reason why this approve invitation cannot be honoured, or None."""
    if state is None or not state.get("active_request"):
        return ("Chưa có request TDQ nào đang mở nên lệnh duyệt sẽ bị gate từ chối — "
                "user gõ đúng lệnh vẫn không duyệt được.")
    lane = state.get("lane")
    if target == "quick" and lane != "quick":
        return f"Mời duyệt quick nhưng request đang ở lane {lane} — gate chỉ nhận quick khi lane quick."
    if target in ("spec", "plan") and lane != "full":
        return f"Mời duyệt {target} nhưng request đang ở lane {lane} — gate chỉ nhận {target} khi lane full."
    if state.get(f"{target}_approved"):
        return f"{target} đã được duyệt rồi — đừng mời duyệt lại, đi tiếp bước sau."
    if target == "plan" and not state.get("spec_approved"):
        return "Mời duyệt plan khi spec chưa được duyệt — gate bắt đúng thứ tự spec trước."
    if target in ("spec", "plan"):
        rel = state.get(f"{target}_file")
        if not rel:
            return f"Chưa đăng ký {target}_file trong state — gate không biết duyệt file nào."
        path = rel if os.path.isabs(rel) else os.path.join(cwd, rel)
        if not os.path.isfile(path) or os.path.getsize(path) == 0:
            return f"File {target} đã đăng ký ({rel}) không tồn tại hoặc rỗng."
    return None


def check_invite(payload, cwd, state):
    text = last_assistant_text(payload.get("transcript_path"))
    match = INVITE_RE.search(text)
    if not match:
        return None
    problem = invite_problem(state, match.group(1), cwd)
    if not problem:
        return None
    return f"[TDQ] Dòng mời duyệt không hợp lệ: {problem} {FIX}"

PRUNE = {".git", "node_modules", "__pycache__", ".venv", "venv", ".pytest_cache",
         ".claude", ".idea", "dist", "build", ".next", "target"}
RECENT_WINDOW = 6 * 3600  # only changes in the last 6h count as "this session"
MAX_ENTRIES = 20000


def main():
    payload = read_payload()
    if payload.get("stop_hook_active"):
        return
    cwd = payload_cwd(payload)
    state = tdq_state.load(cwd)

    reason = check_invite(payload, cwd, state)
    if reason:
        print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
        return

    if state is None or not state.get("active_request"):
        return

    today = datetime.now().strftime("%Y-%m-%d")
    log_rel = os.path.join("docs", "workinglog", today + ".md")
    log_path = os.path.join(cwd, log_rel)
    try:
        log_mtime = os.path.getmtime(log_path)
    except OSError:
        log_mtime = 0.0
    floor = max(log_mtime, time.time() - RECENT_WINDOW)

    state_file = os.path.realpath(tdq_state.state_path(cwd))
    log_dir = os.path.realpath(os.path.join(cwd, "docs", "workinglog"))

    newer = None
    seen = 0
    for root, dirs, files in os.walk(cwd):
        dirs[:] = [d for d in dirs if d not in PRUNE]
        for name in files:
            seen += 1
            if seen > MAX_ENTRIES:
                break
            if name == ".DS_Store":
                continue
            path = os.path.join(root, name)
            real = os.path.realpath(path)
            if real == state_file or real.startswith(log_dir + os.sep):
                continue
            try:
                if os.path.getmtime(path) > floor:
                    newer = os.path.relpath(path, cwd)
                    break
            except OSError:
                continue
        if newer or seen > MAX_ENTRIES:
            break

    if not newer:
        return
    print(json.dumps({
        "decision": "block",
        "reason": (f"[TDQ] Turn này có thay đổi repo (vd: {newer}) nhưng {log_rel} chưa được cập nhật sau đó — "
                   "append entry working log (ngữ cảnh, file đổi, lý do, test đã chạy), chạy graphify update nếu có cài, "
                   "và tick [x] các task plan đã xong. Làm xong rồi mới kết thúc turn."),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
