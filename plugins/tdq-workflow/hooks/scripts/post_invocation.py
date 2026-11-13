#!/usr/bin/env python3
"""PostInvocation hook — flush queued PreToolUse reminders and update lightweight turn state."""
import sys
from _common import (
    emit_context, flush_pending_reminders, observe, payload_cwd, read_payload, session_id
)


def main():
    payload = read_payload()
    cwd = payload_cwd(payload)
    sid = session_id(payload)
    queued = flush_pending_reminders(cwd, sid)
    observe(cwd, payload, "PostInvocation", flushed=len(queued))
    if queued:
        emit_context(queued)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
