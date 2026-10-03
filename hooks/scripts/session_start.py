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
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime

from _common import (already_reminded, payload_cwd, read_payload, session_id,
                     turn_log_append)
# Placed AFTER `from _common`: `_common` itself injects `scripts/` into sys.path. The
# from-import shape (not a module attribute call) is what lets graphify emit a cross-file
# `calls` edge.
from luat_gon import doc_than_luat, loc_than_luat  # noqa: E402
from tdq_state import (default_state, lenh_cho_project, load,  # noqa: E402
                       muc_gat_hieu_luc, render_next)
import search_rules  # noqa: E402
from tdq_ten_lenh import can_nhac_ten_lenh  # noqa: E402 — the interpreter-name safety net

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


# ------------------------------------------------- auto-init of the search layers (2026-10-03)
# The user asked that a project come up with its search layers READY before work starts. The
# expensive part cannot run here: a lumen index of excalidraw took 11m5s (843 files). So this
# hook only PROBES the readiness stamp and, when needed, starts `tdq_setup.py --nen` DETACHED
# and returns at once; the search gate stands down while that build runs.
# Written by THIS hook when it starts a build. Two sessions opened back to back would otherwise
# both start one before the first build has taken its pid lock. The builder's lock is still the
# real guard; this only closes the start-up window.
DAU_DA_GOI = os.path.join("docs", "tdq", ".tdq-khoi-tao.da-goi")
CUA_SO_DA_GOI_GIAY = 120
# A finished build that left a layer down (no ollama, say) is retried only after this long — not
# at every session, which would re-run the same failing install each time.
THU_LAI_GIAY = 6 * 3600
# A stamp claiming "still building" for longer than the builder's own cap is a dead build.
HAN_DUNG_GIAY = 1800
GOC_PLUGIN = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TANG = ("grep", "lsp", "graphify", "lumen")


def _tuoi_giay(iso):
    try:
        return time.time() - datetime.fromisoformat(str(iso)).timestamp()
    except (TypeError, ValueError):
        return float("inf")


def la_project_that(cwd):
    """-> True only for a real project: it has a `.git`, and it is neither the home folder nor a
    drive/filesystem root. Opening a session in `~` or `C:\\` must not start a 25-minute index of
    the whole disk, nor drop `docs/tdq/` and `.codex/hooks.json` there."""
    try:
        cwd = os.path.abspath(cwd)
    except (TypeError, ValueError):
        return False
    if cwd == os.path.abspath(os.path.expanduser("~")):
        return False
    if os.path.dirname(cwd) == cwd:            # a drive or filesystem root
        return False
    return os.path.exists(os.path.join(cwd, ".git"))


def can_khoi_tao(cwd):
    """-> True when the search layers should be (re)built now. Reads files only, never runs."""
    if os.environ.get("TDQ_KHOI_TAO_NEN", "1") == "0":
        return False
    if not la_project_that(cwd):
        return False
    try:
        if time.time() - os.path.getmtime(os.path.join(cwd, DAU_DA_GOI)) < CUA_SO_DA_GOI_GIAY:
            return False
    except OSError:
        pass
    try:
        with open(os.path.join(cwd, search_rules.MOC_SAN_SANG), "r", encoding="utf-8") as fh:
            moc = json.load(fh)
    except (OSError, ValueError):
        return True                       # never built by us
    if not isinstance(moc, dict):
        return True
    tuoi = _tuoi_giay(moc.get("cap_nhat"))
    if moc.get("dang_dung"):
        return tuoi > HAN_DUNG_GIAY       # building → leave it, unless it died
    tang = moc.get("tang") or {}
    if all((tang.get(t) or {}).get("san_sang") for t in TANG):
        return False
    return tuoi > THU_LAI_GIAY


def kich_hoat_nen(cwd):
    """Start `tdq_setup.py --nen` detached from this hook. -> True when a process was started.

    `TDQ_LENH_NEN` (a JSON argv) replaces the command — tests use it so no real install or index
    ever runs from a test.
    """
    lenh = [sys.executable, os.path.join(GOC_PLUGIN, "scripts", "tdq_setup.py"), "--nen"]
    if os.environ.get("TDQ_LENH_NEN"):
        try:
            lenh = json.loads(os.environ["TDQ_LENH_NEN"])
        except ValueError:
            return False
    kw = {"cwd": cwd, "stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL,
          "stderr": subprocess.DEVNULL, "close_fds": True,
          "env": dict(os.environ, TDQ_PROJECT_DIR=cwd)}
    if os.name == "nt":
        # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP: the build must outlive this hook and the
        # host's console; without them Windows kills it when the hook process exits.
        kw["creationflags"] = 0x00000008 | 0x00000200
    else:
        kw["start_new_session"] = True
    try:
        os.makedirs(os.path.join(cwd, "docs", "tdq"), exist_ok=True)
        with open(os.path.join(cwd, DAU_DA_GOI), "w", encoding="utf-8") as fh:
            fh.write(datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
        subprocess.Popen(lenh, **kw)
    except OSError:
        return False
    return True


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
    out = cap("\n".join(lines), MAX_LINES, MAX_CHARS)

    # Both notices go AFTER the head cap, never inside it. The head cuts from the tail at 600
    # characters, and on Windows the project path alone can be long enough to push a line out —
    # measured 2026-09-21: the graphify notice came out as `graphify is n…` on a machine without
    # graphify. A notice that silently vanishes is worse than none. Each is empty on a machine
    # that does not need it, so those sessions pay nothing for it.
    dung_nen = can_khoi_tao(cwd) and kich_hoat_nen(cwd)
    nhac = [n for n in (
        "" if shutil.which("graphify") else
        "[TDQ] graphify is not installed (optional): uv tool install graphifyy",
        can_nhac_ten_lenh(),
        "[TDQ:SEARCH] Setting up the search layers in the background (dependencies, graphify "
        "graph, lumen index — minutes on a big repo). Until they answer, the search gate does "
        "not block." if dung_nen else "") if n]
    if nhac:
        # Their own paragraph: the head never holds a blank line, so the blank line is what
        # tells a reader (and the 12/600 budget) where the head ends.
        out += "\n\n" + "\n".join(nhac)

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
    # Absolute paths AFTER both caps: the caps measure what the block says; rewriting first
    # pushed the block over 600 characters and cut its tail off (measured 2026-10-03).
    print(lenh_cho_project(out, cwd))


if __name__ == "__main__":
    main()
