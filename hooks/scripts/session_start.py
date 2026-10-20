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
from tdq_state import (_TASK_LINE, default_state, effective_phase, lenh_cho_project, load,  # noqa: E402
                       muc_gat_hieu_luc, phase_row, plan_tick_state, render_next)
import search_rules  # noqa: E402
import tdq_setup  # noqa: E402
import tdq_devtool_mcp  # noqa: E402
from tdq_ten_lenh import can_nhac_ten_lenh, co_shim_python3, la_windows  # noqa: E402 — the interpreter-name safety net

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
# expensive part cannot run here: building the layers of a big repo takes minutes (a semantic
# index of excalidraw took 11m5s before lumen was removed in 0.58.0). So this
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
# A stamp written before 0.58.0 may still carry a `lumen` key; only these three are read, so a
# removed layer can never keep a project "not ready" and re-trigger the build every 6 hours.
TANG = ("grep", "lsp", "graphify")


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
    """-> True when the search layers should be (re)built now.

    Reads files, plus one `git ls-files` when the project has an LSP module table
    (`co_ngon_ngu_moi`, measured 0.05–0.08 s) — never an install, never a server.
    """
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
    if co_ngon_ngu_moi(cwd):
        return True                       # a language the LSP setup has never seen
    tang = moc.get("tang") or {}
    if all((tang.get(t) or {}).get("san_sang") for t in TANG):
        return False
    return tuoi > THU_LAI_GIAY


def co_ngon_ngu_moi(cwd):
    """-> True when the project now holds a language the LSP module table has never seen.

    0.59.0, the user's case: a project starts as Python, later grows JS + HTML. The three layers
    still read "ready", yet the new servers are neither installed nor declared in MCP `lsp`. Only
    projects that already have a table are asked (one walk, measured ≤ 0.31 s on 7,994 files); the
    import is lazy so sessions elsewhere pay nothing. Any failure answers False — a SessionStart
    hook must never break the session.
    """
    if not os.path.isfile(os.path.join(cwd, "docs", "tdq", ".tdq-lsp-module.json")):
        return False
    try:
        import lsp_module
        lsp_module.tdq_lsp._LOG_TAT = True
        return bool(lsp_module.ngon_ngu_moi(cwd))
    except Exception:  # noqa: BLE001
        return False


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


def kiem_can_setup_lan_dau(cwd):
    """-> True nếu project hoặc môi trường cần chạy setup lần đầu sau khi cài đặt plugin."""
    if not la_project_that(cwd):
        return False
    if not tdq_setup.doc_phat_hanh(cwd):
        return True
    if la_windows() and not co_shim_python3():
        return True
    return False


def main():
    payload = read_payload()
    cwd = payload_cwd(payload)
    state = load(cwd, heal=False) or default_state()

    lines = [RULE] + render_next(cwd, state, compact=True).splitlines()
    out = cap("\n".join(lines), MAX_LINES, MAX_CHARS)

    # Both notices go AFTER the head cap, never inside it. The head cuts from the tail at 600
    # characters, and on Windows the project path alone can be long enough to push a line out —
    # measured 2026-09-21: the graphify notice came out as `graphify is n…` on a machine without
    # graphify. A notice that silently vanishes is worse than none. Each is empty on a machine
    # that does not need it, so those sessions pay nothing for it.
    thong_bao_update_plugin = ""
    try:
        _, msg = tdq_setup.tu_dong_cap_nhat_plugin_user(goc_plugin=GOC_PLUGIN)
        if msg:
            thong_bao_update_plugin = msg
    except Exception:  # noqa: BLE001
        pass
    da_cap_nhat_ver = False
    try:
        if la_project_that(cwd) and tdq_setup.can_cap_nhat_phien_ban(cwd, goc_plugin=GOC_PLUGIN):
            da_cap_nhat_ver = tdq_setup.tu_dong_cap_nhat_khi_doi_phien_ban(cwd, goc_plugin=GOC_PLUGIN)
    except Exception:  # noqa: BLE001
        pass
    can_setup = False
    try:
        can_setup = kiem_can_setup_lan_dau(cwd)
    except Exception:  # noqa: BLE001
        pass
    dung_nen = (can_khoi_tao(cwd) or can_setup) and kich_hoat_nen(cwd)
    nhac_devtool = ""
    try:
        nhac_devtool = tdq_devtool_mcp.check_session_start(cwd=cwd)
    except Exception:
        pass
    nhac_setup = (
        f"[TDQ:SETUP] Plugin mới cài đặt hoặc chưa hoàn tất thiết lập: chạy "
        f"`python3 {os.path.join(GOC_PLUGIN, 'scripts', 'tdq_setup.py')}` (hoặc gọi skill tdq-setup)."
        if can_setup else ""
    )
    nhac = [n for n in (
        thong_bao_update_plugin,
        "[TDQ] Đã tự động cập nhật instruction và cấu hình cho phiên bản mới." if da_cap_nhat_ver else "",
        nhac_setup,
        "" if shutil.which("graphify") else
        "[TDQ] graphify is not installed (optional): uv tool install graphifyy",
        nhac_devtool,
        can_nhac_ten_lenh(),
        "[TDQ:SEARCH] Setting up the search layers in the background (dependencies, graphify "
        "graph — minutes on a big repo). Until they answer, the search gate does not block." if dung_nen else "") if n]
    if nhac:
        # Their own paragraph: the head never holds a blank line, so the blank line is what
        # tells a reader (and the 12/600 budget) where the head ends.
        out += "\n\n" + "\n".join(nhac)

    muc = muc_gat_hieu_luc(state)
    than = loc_than_luat(doc_than_luat(GOC_LUAT), muc)
    ghi = bool(than) and not already_reminded(cwd, payload, MA_GON)
    pha = effective_phase(state, warn=False)
    # Lazy load: only load the full law body during phase 'implement' (or when no active request
    # is open yet, preserving standalone usage). In other phases (idle, analyze, spec, plan, qc,
    # report), inject a concise 1-line pointer to save ~2,000 tokens of carry-cost per turn.
    nap_day_du = (pha == "implement") or (not (state or {}).get("active_request"))
    law_text = ""
    if ghi:
        if nap_day_du:
            law_text = (f"[{MA_GON}] The build-less-than-asked law (muc_gat={muc}) — climb this "
                        f"ladder before you create anything:\n{than}")
        else:
            law_text = (f"[{MA_GON}] The build-less-than-asked law (muc_gat={muc}) — full ladder "
                        f"loads during phase implement (see skills/tdq-build/references/rules/chung.md).")

    # Derived recovery anchor block (O10)
    src = str(payload.get("source") or "")
    has_active = bool((state or {}).get("active_request"))
    anchor_block = ""
    if has_active and (src in ("compact", "resume") or payload.get("source") == "compact"):
        req = state.get("active_request")
        plan_f = state.get("plan_file") or f"docs/tdq/plan/{req}.md"
        owner = state.get("implement_mode") or "main"
        pts = plan_tick_state(cwd)
        doing_tasks = []
        if pts.get("path") and os.path.isfile(str(pts["path"])):
            try:
                with open(str(pts["path"]), encoding="utf-8") as f:
                    for line in f:
                        m = _TASK_LINE.match(line)
                        if m and m.group(1) == "~":
                            doing_tasks.append(m.group(2))
            except OSError:
                pass
        doing_str = ",".join(doing_tasks) or "none"
        dispatched_str = ",".join(pts.get("dispatched_ids", [])) or "none"
        row = phase_row(state)
        next_hint = row.get("cmd") or row.get("action") or "none"

        raw_cwd = str(payload.get("cwd") or os.getcwd())
        cwd_str = str(cwd)
        if os.path.normpath(raw_cwd) == os.path.normpath(cwd_str):
            wt_str = "root"
        else:
            try:
                wt_str = os.path.relpath(raw_cwd, cwd_str).replace(os.sep, "/")
            except ValueError:
                wt_str = raw_cwd.replace(os.sep, "/")
            if os.path.isfile(os.path.join(raw_cwd, ".git")):
                wt_str = f"worktree:{wt_str}"

        label = "Compact recovery:" if src == "compact" else f"{src.capitalize()} recovery:"
        anchor_block = (
            f"[TDQ:ANCHOR] {label} request={req} phase={pha} source={src} owner={owner} "
            f"plan={plan_f} doing={doing_str} dispatched={dispatched_str} next={next_hint} worktree={wt_str}\n"
            f"MCP-First: ưu tiên MCP & bộ skill MCP, pre-flight check kết nối trước khi làm, hướng dẫn bật nếu chưa mở.\n"
            f"Core anti-patterns: ANTI-1 (no fake red) · ANTI-2 (no blind assert) · ANTI-3 (clean git state) · "
            f"ANTI-4 (tick before code) · ANTI-5 (cap logs <= 15 lines) · ANTI-6 (explicit files in Cham)."
        )

    sections = [out]
    if law_text:
        sections.append(law_text)
    if anchor_block:
        sections.append(anchor_block)

    full_out = "\n\n".join(sections)
    rewritten = lenh_cho_project(full_out, cwd)

    # Capping AFTER rewrite (O10):
    # Essential information: Head and Anchor block must NEVER be cut!
    if anchor_block and "[TDQ:ANCHOR]" in rewritten:
        anchor_idx = rewritten.rfind("[TDQ:ANCHOR]")
        pre_anchor = rewritten[:anchor_idx].rstrip()
        post_anchor = rewritten[anchor_idx:]

        if len(rewritten) > TOAN_MAX_CHARS:
            needed = TOAN_MAX_CHARS - len(post_anchor) - 2
            if needed > 0:
                pre_anchor = pre_anchor[:needed - 1].rstrip() + "…"
            rewritten = pre_anchor + "\n\n" + post_anchor

        if len(rewritten.splitlines()) > TOAN_MAX_LINES:
            anc_lines = len(post_anchor.splitlines())
            max_pre = TOAN_MAX_LINES - anc_lines - 1
            if max_pre > 0:
                pre_anchor = "\n".join(pre_anchor.splitlines()[:max_pre])
            rewritten = pre_anchor + "\n\n" + post_anchor
    else:
        rewritten = cap(rewritten, TOAN_MAX_LINES, TOAN_MAX_CHARS)

    if ghi:
        turn_log_append(cwd, "remind", session=session_id(payload), code=MA_GON,
                        event="SessionStart", muc_gat=muc,
                        so_dong=len(rewritten.partition(f"[{MA_GON}]")[2].splitlines()[1:]) if nap_day_du else 1,
                        source=str(payload.get("source") or ""))
    print(rewritten)


if __name__ == "__main__":
    main()
