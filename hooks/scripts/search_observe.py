#!/usr/bin/env python3
"""The search ledger — what the search gate needs to know, recorded by real effect.

Three kinds of row go into `docs/tdq/.tdq-search.jsonl`, each tagged with the key of the current
request (or `phien:<session>` when no request is open):

  * `khai_niem` — a call to the concept layer actually happened: lumen `semantic_search`, an LSP
    query tool (`mcp__lsp__*` minus pure housekeeping), or `graphify query|explain|path|god-nodes|
    affected` through Bash. Written by THIS hook on `PostToolUse`, i.e. after the tool ran — the
    agent saying "I asked lumen" proves nothing; the tool call does.
  * `prompt` — the identifier-shaped tokens of the user's latest prompt, written on
    `UserPromptSubmit`. NOT the prompt text: the gate only needs to know whether a name the agent
    greps for appeared in what the user typed.
  * `tim` — one code search the gate let through or blocked. Written by `search_gate.py`, which is
    where a command is classified; this module only owns the file format.

Why a ledger of its own instead of the shared turn ledger: `prompt_context.py` calls
`turn_log_clear` at EVERY user prompt, so a memory built on the turn ledger forgets everything one
turn later — the exact failure the read gate shipped with on 2026-10-02 and had to be rebuilt for.
A request spans many turns; so must this ledger.

It is deliberately cheap — it runs after every tool call: one read of `state.json` for the request
key, one small append. No subprocess. Every error is swallowed: a hook never breaks a tool call.

Env: TDQ_PROJECT_DIR anchors the project; TDQ_LOG=0 silences the log.
"""
import json
import os
import re
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common  # noqa: E402

SO_SACH = os.path.join("docs", "tdq", ".tdq-search.jsonl")
# Rewrite the ledger once it passes this many rows, keeping the newest half. A request rarely
# makes more than a few hundred searches; an unbounded append-only file in `docs/` is a slow leak.
TRAN_DONG = 600
# A session-keyed row (no request open) stops counting after this long — same window as the turn
# ledger. Request-keyed rows never expire: the request is the scope.
HAN_PHIEN_GIAY = 6 * 3600
# Same tokenizer the replay fixture used (tests/fixtures/phien_excalidraw_tim.json): ASCII
# identifier shapes of 3+ characters. Vietnamese words and short noise never collide with code.
TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")
LUMEN = re.compile(r"^mcp__.*lumen.*__semantic_search$")
# LSP tools that ANSWER a question about the code. Starting a server or opening a document asks
# nothing — counting those would let `start_lsp` unlock grep without a single real query.
LSP_KHONG_PHAI_HOI = {
    "mcp__lsp__start_lsp", "mcp__lsp__restart_lsp_server", "mcp__lsp__open_document",
    "mcp__lsp__close_document", "mcp__lsp__set_log_level", "mcp__lsp__did_change_watched_files",
    "mcp__lsp__get_server_capabilities", "mcp__lsp__detect_lsp_servers",
    "mcp__lsp__list_workspace_folders", "mcp__lsp__add_workspace_folder",
    "mcp__lsp__remove_workspace_folder", "mcp__lsp__export_cache", "mcp__lsp__import_cache",
    "mcp__lsp__activate_skill", "mcp__lsp__deactivate_skill", "mcp__lsp__get_skill_phase",
}
GRAPHIFY_HOI = re.compile(r"\bgraphify\s+(query|explain|path|god-nodes|affected)\b")


def _log(message):
    """Log service: ISO timestamp on stderr, on by default, muted by TDQ_LOG=0."""
    if os.environ.get("TDQ_LOG", "1") != "0":
        print(f"[{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}] search_observe: {message}",
              file=sys.stderr)


def duong_so(cwd):
    return os.path.join(cwd or ".", SO_SACH)


def khoa_hien_tai(cwd, phien):
    """-> the ledger key: the open request's slug, else `phien:<session>`.

    Reads `state.json` directly instead of `tdq_state.load`, which may heal the file — far too
    much work for something that runs after every tool call.
    """
    try:
        with open(_common.tdq_state.state_path(cwd), "r", encoding="utf-8") as fh:
            # The key is `active_request` — `tdq_state` writes it under that name. The first
            # version read `request`, which never exists, so every row fell back to the session
            # key and a new request inherited the previous one's unlock.
            request = (json.load(fh) or {}).get("active_request")
    except (OSError, ValueError, TypeError, AttributeError):
        request = None
    return f"yc:{request}" if request else f"phien:{phien}"


def doc_so(cwd, khoa):
    """-> rows of `khoa`, oldest first. Unreadable rows are skipped; a broken file reads as []."""
    bay_gio = time.time()
    ra = []
    try:
        with open(duong_so(cwd), "r", encoding="utf-8") as fh:
            for dong in fh:
                dong = dong.strip()
                if not dong:
                    continue
                try:
                    row = json.loads(dong)
                except ValueError:
                    continue
                if not isinstance(row, dict) or row.get("khoa") != khoa:
                    continue
                if khoa.startswith("phien:") and bay_gio - float(row.get("ts") or 0) > HAN_PHIEN_GIAY:
                    continue
                ra.append(row)
    except (OSError, TypeError, ValueError):
        return []
    return ra


def ghi_so(cwd, row):
    """Append one row; past the cap, rewrite keeping the newest half. Errors are swallowed."""
    duong = duong_so(cwd)
    dong = json.dumps(row, ensure_ascii=False) + "\n"
    try:
        os.makedirs(os.path.dirname(duong), exist_ok=True)
        try:
            with open(duong, "r", encoding="utf-8") as fh:
                cu = fh.readlines()
        except OSError:
            cu = []
        if len(cu) >= TRAN_DONG:
            with open(duong, "w", encoding="utf-8") as fh:
                fh.write("".join(cu[-TRAN_DONG // 2:]) + dong)
            return
        with open(duong, "a", encoding="utf-8") as fh:
            fh.write(dong)
    except OSError:
        pass


def trang_thai(rows):
    """-> the state the decision rules need, built from a key's rows.

    `so_lan_tim_tu_lan_goi` counts code searches AFTER the latest concept-layer call — the
    unlock window is measured from the latest call, not the first, so asking lumen again re-opens
    it. `token_prompt` is the token set of the latest prompt only.
    """
    da_goi, dem, token = False, 0, set()
    for row in rows:
        loai = row.get("loai")
        if loai == "khai_niem":
            da_goi, dem = True, 0
        elif loai == "tim" and row.get("tinh_cua_so", True):
            dem += 1
        elif loai == "prompt":
            token = set(row.get("token") or [])
    return {"da_goi_khai_niem": da_goi, "so_lan_tim_tu_lan_goi": dem, "token_prompt": token}


def la_goi_khai_niem(ten_tool, tool_input):
    """-> a short label when this tool call is a concept-layer QUERY, else None."""
    if LUMEN.match(ten_tool or ""):
        return "lumen"
    if (ten_tool or "").startswith("mcp__lsp__") and ten_tool not in LSP_KHONG_PHAI_HOI:
        return ten_tool.replace("mcp__lsp__", "lsp:")
    if ten_tool == "Bash":
        cmd = (tool_input or {}).get("command") or ""
        khop = GRAPHIFY_HOI.search(cmd) if isinstance(cmd, str) else None
        if khop:
            return f"graphify:{khop.group(1)}"
    return None


def main():
    payload = _common.read_payload()
    cwd = _common.payload_cwd(payload)
    phien = _common.session_id(payload)
    su_kien = payload.get("hook_event_name") or ""
    khoa = khoa_hien_tai(cwd, phien)

    if su_kien == "UserPromptSubmit" or ("prompt" in payload and "tool_name" not in payload):
        token = sorted(set(TOKEN.findall(str(payload.get("prompt") or ""))))
        ghi_so(cwd, {"ts": time.time(), "khoa": khoa, "loai": "prompt", "token": token})
        _log(f"prompt · {len(token)} token · {khoa}")
        sys.exit(0)

    nhan = la_goi_khai_niem(payload.get("tool_name"), payload.get("tool_input"))
    if nhan:
        ghi_so(cwd, {"ts": time.time(), "khoa": khoa, "loai": "khai_niem", "cong_cu": nhan})
        _log(f"khai_niem · {nhan} · {khoa}")
    sys.exit(0)


if __name__ == "__main__":
    main()
