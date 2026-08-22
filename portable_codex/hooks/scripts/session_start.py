#!/usr/bin/env python3
"""SessionStart — load the context at the start of a session.

The compliance rule line comes FIRST, then the whole `tdq_state.py next` block (the single
source of truth on "where we are, what comes next") and the graphify status. That order
matters: the 600-character cap cuts from the tail, and the rule must not sit in the tail.
It prints even with no request open — phase `no_state` shows the way to open one.
Budget cap: <= 12 lines / 600 characters (spec §2.7).
"""
import shutil

from _common import payload_cwd, read_payload
# Placed AFTER `from _common`: `_common` itself injects `scripts/` into sys.path. The
# from-import shape (not a module attribute call) is what lets graphify emit a cross-file
# `calls` edge.
from tdq_state import default_state, load, render_next  # noqa: E402

MAX_LINES = 12
MAX_CHARS = 600

RULE = ("[TDQ] Rule: a [TDQ:<CODE>] line means do exactly that job FIRST, "
        "then print ✓ [TDQ:<CODE>]. Write state only via scripts/tdq_state.py.")


def main():
    payload = read_payload()
    cwd = payload_cwd(payload)
    state = load(cwd) or default_state()

    lines = [RULE] + render_next(cwd, state, compact=True).splitlines()
    if shutil.which("graphify") is None:
        lines.append("[TDQ] graphify is not installed (optional): uv tool install graphifyy")

    text = "\n".join(lines[:MAX_LINES])
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS - 1].rstrip() + "…"
    print(text)


if __name__ == "__main__":
    main()
