#!/usr/bin/env python3
"""Stop gate: if this turn changed the repo (a file is newer than today's
working log, within a recent window) but the log was not updated afterwards,
block ONCE with a reminder (working log + graphify + plan ticks).
`stop_hook_active` guarantees max one block per turn.
"""
import json
import os
import time
from datetime import datetime

from _common import read_payload, payload_cwd, tdq_state

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
