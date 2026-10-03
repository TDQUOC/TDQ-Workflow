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
# The tokenizer, the concept-call recognizer and the state builder live in
# `scripts/search_rules.py` (pure): the replay tool shares them, so the live ledger and the
# replay can never disagree on what counts (they did, until QC round 1 of 2026-10-03).
from search_rules import TOKEN, la_goi_khai_niem, trang_thai  # noqa: E402,F401


def _log(message):
    """Log service: ISO timestamp on stderr, on by default, muted by TDQ_LOG=0."""
    if os.environ.get("TDQ_LOG", "1") != "0":
        print(f"[{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}] search_observe: {message}",
              file=sys.stderr)


def duong_so(cwd):
    return os.path.join(cwd or ".", SO_SACH)


def khoa_hien_tai(cwd, phien):
    """-> the ledger key: the OPEN request's slug, else `phien:<session>`.

    Reads `state.json` directly instead of `tdq_state.load`, which may heal the file — far too
    much work for something that runs after every tool call.
    """
    try:
        with open(_common.tdq_state.state_path(cwd), "r", encoding="utf-8") as fh:
            st = json.load(fh) or {}
        # The key is `active_request` — `tdq_state` writes it under that name. The first version
        # read `request`, which never exists, so every row fell back to the session key.
        request = st.get("active_request")
        # `active_request` is never cleared when a request closes; at phase `idle` it names a
        # FINISHED request. Keying on it let one lumen call from a closed request keep grep
        # unlocked for every later task (review 2026-10-03).
        if st.get("phase") == "idle":
            request = None
    except (OSError, ValueError, TypeError, AttributeError):
        request = None
    return f"yc:{request}" if request else f"phien:{phien}"


def doc_so(cwd, khoa, phien=None):
    """-> rows of `khoa` (plus this session's `phien:` rows when given), oldest first.

    Why the session rows join a request's scope: the user's prompt and an early lumen call arrive
    BEFORE `tdq_state.py init` opens the request, i.e. under the session key. Reading only the
    request key made the gate forget both the moment the request opened — a name the user typed
    was suddenly denied (review 2026-10-03). Unreadable rows are skipped; a broken file reads []."""
    khoa_phien = f"phien:{phien}" if phien else None
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
                if not isinstance(row, dict) or row.get("khoa") not in (khoa, khoa_phien):
                    continue
                if (str(row.get("khoa")).startswith("phien:")
                        and bay_gio - float(row.get("ts") or 0) > HAN_PHIEN_GIAY):
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
