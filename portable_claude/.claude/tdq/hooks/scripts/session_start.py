#!/usr/bin/env python3
"""SessionStart — load the context at the start of a session.

Two blocks, in this order. The HEAD block: the compliance rule line, then the whole
`tdq_state.py next` block (the single source of truth on "where we are, what comes next")
and the graphify status. That order matters: the head cap cuts from the tail, and the rule
must not sit in the tail. It prints even with no request open — phase `no_state` shows the
way to open one.
The LAW block (2026-09-17): the lean "build less than asked" law, read off disk from
`skills/tdq-build/references/rules/chung.md` and filtered by `muc_gat`. It sits AFTER the
head so nothing can push the rule line out, and it is skipped entirely at `muc_gat=off`.
Budget caps: head <= 12 lines / 600 characters (spec §2.7, unchanged); whole output
<= 160 lines / 8200 characters (measured, see the note on TOAN_MAX_LINES).
Injected once per turn: bug #10871 runs a plugin hook twice with two PIDs, so the turn
ledger (`already_reminded`) is what keeps the law from landing twice.
"""
import os
import shutil

from _common import (already_reminded, payload_cwd, read_payload, session_id,
                     turn_log_append)
# Placed AFTER `from _common`: `_common` itself injects `scripts/` into sys.path. The
# from-import shape (not a module attribute call) is what lets graphify emit a cross-file
# `calls` edge.
from luat_gon import doc_than_luat, loc_than_luat  # noqa: E402
from tdq_state import default_state, load, muc_gat_hieu_luc, render_next  # noqa: E402

MAX_LINES = 12
MAX_CHARS = 600
# 2026-09-17: measured, not guessed. The filtered law body is 72 lines/4404 chars at `lite`,
# 133/6887 at `full` and 139/7123 at `ultra`; plus the head block that is ~150 lines / ~7800
# characters at the widest. The plan had declared 140/7000 BEFORE the law body existed, and at
# that number `full` and `ultra` both came back truncated — and a truncated law is a law
# missing its last rungs. soul.md:101 settles which side gives: a cap is a tier-3 constraint,
# so the cap is raised and the law is never squeezed to fit.
TOAN_MAX_LINES = 160
TOAN_MAX_CHARS = 8200

RULE = ("[TDQ] Rule: a [TDQ:<CODE>] line means do exactly that job FIRST, "
        "then print ✓ [TDQ:<CODE>]. Write state only via scripts/tdq_state.py.")

MA_GON = "TDQ:GON"
# The law lives in the PLUGIN, not in the user's project: read it relative to this file so a
# session opened in any other repo still gets the law.
GOC_LUAT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def cap(text, max_lines, max_chars):
    """Cut to the declared budget, from the tail."""
    text = "\n".join(text.splitlines()[:max_lines])
    if len(text) > max_chars:
        text = text[:max_chars - 1].rstrip() + "…"
    return text


def main():
    payload = read_payload()
    cwd = payload_cwd(payload)
    state = load(cwd) or default_state()

    lines = [RULE] + render_next(cwd, state, compact=True).splitlines()
    if shutil.which("graphify") is None:
        lines.append("[TDQ] graphify is not installed (optional): uv tool install graphifyy")
    out = cap("\n".join(lines), MAX_LINES, MAX_CHARS)

    muc = muc_gat_hieu_luc(state)
    than = loc_than_luat(doc_than_luat(GOC_LUAT), muc)
    ghi = bool(than) and not already_reminded(cwd, payload, MA_GON)
    if ghi:
        out += (f"\n\n[{MA_GON}] The build-less-than-asked law (muc_gat={muc}) — climb this "
                f"ladder before you create anything:\n{than}")
    out = cap(out, TOAN_MAX_LINES, TOAN_MAX_CHARS)
    if ghi:
        # Logged AFTER the cap on purpose: `so_dong` must be the law lines that actually
        # survived into the context, not the ones we meant to print. A row claiming 133 while
        # the cap let 90 through is worse than no row at all.
        turn_log_append(cwd, "remind", session=session_id(payload), code=MA_GON,
                        event="SessionStart", muc_gat=muc,
                        so_dong=len(out.partition(f"[{MA_GON}]")[2].splitlines()[1:]),
                        source=str(payload.get("source") or ""))
    print(out)


if __name__ == "__main__":
    main()
