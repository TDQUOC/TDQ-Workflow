#!/usr/bin/env python3
"""PreToolUse on `Read` — remind, never block, when the same unchanged file is read whole again.

Why this gate exists, measured on one real 22.76 MB session: `scripts/tdq_state.py` was read
**12 times** and `scripts/build_portable.py` **19 times**; those two files alone account for
502,816 tokens, 28% of everything that session read in. And because 98.2% of a session's input
is re-reading the context it already holds, every one of those copies is paid for again on every
later API call. The rule against this already existed — `context-budget.md` — but it lived inside
a reference file nobody had to load, and nothing ever measured it.

It REMINDS and never blocks. That is the user's decision (2026-10-02) and it matches
`docs/kien-truc.md` 2026-07-29: a hook reminds and checks by real effect. The agent decides
whether a re-read is worth it; this gate only makes the cost visible at the moment of choosing.

Three cases stay silent, because none of them is waste:
  * the first read of a file;
  * a read whose `offset`/`limit` asks for a range not read yet — that is the behaviour the gate
    wants to encourage, not punish;
  * a file whose size or mtime changed since it was read — the content is genuinely new.

It keeps its OWN ledger instead of the shared turn ledger (`_common.turn_rows`). The turn ledger
is cleared at every user prompt (`prompt_context.py` calls `turn_log_clear`), so a memory built on
it can only see re-reads inside ONE assistant turn — while the waste being measured (the same file
12 times) happens ACROSS turns of one session. A per-turn store cannot hold a session-scope fact.

It is also deliberately cheap: one `os.stat`, one small append, one pass over this gate's own
ledger. No subprocess, and it never opens the file it is asked about — counting that file's tokens
here would double the very cost the gate exists to cut.

Env: TDQ_PROJECT_DIR anchors the project; TDQ_LOG=0 silences the log.
"""
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common  # noqa: E402

MA = "TDQ:DOC"
# This gate's own ledger, next to the turn ledger but never cleared by the prompt hook.
SO_SACH = os.path.join("docs", "tdq", ".tdq-read.jsonl")
# Same staleness window as the turn ledger (`tdq_state.TURN_STALE_SECONDS`): a session older than
# this is over, and its reads say nothing about what is in context now.
HAN_GIAY = 6 * 3600
# Rewrite the ledger once it grows past this. A session of 400 reads is already far beyond what
# this gate is trying to catch, and an unbounded append-only file in `docs/` is a slow leak.
TRAN_DONG = 400
# Below this size a re-read is not worth a line of reminder: the reminder costs about as much as
# what it saves. Measured on this repo: a 2 KB file is roughly 600 tokens, the reminder line ~40.
NGUONG_BYTE = 2048


def _log(message):
    """Log service: ISO timestamp on stderr, on by default, muted by TDQ_LOG=0 like every
    other script of this repo. stdout stays clean — the host parses it as JSON."""
    if os.environ.get("TDQ_LOG", "1") != "0":
        print(f"[{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}] read_gate: {message}",
              file=sys.stderr)


def _duong_so(cwd):
    return os.path.join(cwd or ".", SO_SACH)


def _doc_so(cwd, phien):
    """-> this session's rows, newest last. Any I/O or parse error yields [] — a hook never breaks.

    Rows carry an epoch `ts` rather than an ISO string: this runs before every `Read`, and parsing
    a timestamp format is work the gate does not need.
    """
    bay_gio = time.time()
    rows = []
    try:
        with open(_duong_so(cwd), "r", encoding="utf-8") as fh:
            for dong in fh:
                dong = dong.strip()
                if not dong:
                    continue
                try:
                    row = _common.json.loads(dong)
                except ValueError:
                    continue
                if not isinstance(row, dict) or row.get("session") != phien:
                    continue
                if bay_gio - float(row.get("ts") or 0) > HAN_GIAY:
                    continue
                rows.append(row)
    except (OSError, TypeError, ValueError):
        return []
    return rows


def _ghi_so(cwd, row, rows):
    """Append one row; rewrite the whole ledger when it passes the cap. Errors are swallowed."""
    duong = _duong_so(cwd)
    dong = _common.json.dumps(row, ensure_ascii=False) + "\n"
    try:
        os.makedirs(os.path.dirname(duong), exist_ok=True)
        if len(rows) >= TRAN_DONG:
            giu = [_common.json.dumps(r, ensure_ascii=False) + "\n" for r in rows[-TRAN_DONG // 2:]]
            with open(duong, "w", encoding="utf-8") as fh:
                fh.write("".join(giu) + dong)
            return
        with open(duong, "a", encoding="utf-8") as fh:
            fh.write(dong)
    except OSError:
        pass


def _vung(tool_input):
    """-> (start, end) of the range asked for; (0, 0) means the WHOLE file.

    A `Read` without `offset` or `limit` is a whole-file read, and that is the only case worth a
    reminder: a read that carries a range is an aimed read, even when the range repeats an old one.
    """
    try:
        dau = int(tool_input.get("offset") or 0)
        gioi_han = int(tool_input.get("limit") or 0)
    except (TypeError, ValueError):
        return 0, 0
    if not dau and not gioi_han:
        return 0, 0
    return dau, (dau + gioi_han if gioi_han else 0)


def _da_doc_tron(rows, duong):
    """The latest WHOLE read of `duong` in this session, or None.

    Only whole reads count: if the agent read one range before, it does not hold the whole file in
    context, so reading it whole now is new work rather than a re-read.
    """
    for r in reversed(rows):
        if r.get("path") == duong and not r.get("dau") and not r.get("cuoi"):
            return r
    return None


def _da_nhac(rows, duong):
    return any(r.get("path") == duong and r.get("da_nhac") for r in rows)


def main():
    payload = _common.read_payload()
    cwd = _common.payload_cwd(payload)
    vao = payload.get("tool_input") or {}
    duong_that = vao.get("file_path") or ""
    if not duong_that:
        sys.exit(0)
    duong = duong_that.replace(os.sep, "/")

    try:
        so = os.stat(duong_that)
    except OSError:
        # Nothing to compare against, so nothing to say — and never break the read itself.
        sys.exit(0)

    dau, cuoi = _vung(vao)
    phien = _common.session_id(payload)
    rows = _doc_so(cwd, phien)
    truoc = _da_doc_tron(rows, duong) if not dau and not cuoi else None
    # One chain, in the order of the three silent cases in the module docstring: no earlier whole
    # read · too small to be worth the reminder line · size or mtime changed, so the content is
    # genuinely new. Plus the dedupe: one reminder per file per session.
    dang_nhac = (truoc is not None
                 and so.st_size >= NGUONG_BYTE
                 and truoc.get("byte") == so.st_size
                 and truoc.get("mtime") == int(so.st_mtime)
                 and not _da_nhac(rows, duong))

    _ghi_so(cwd, {"ts": time.time(), "session": phien, "path": duong, "dau": dau, "cuoi": cuoi,
                  "byte": so.st_size, "mtime": int(so.st_mtime), "da_nhac": dang_nhac}, rows)
    _log(f"{os.path.basename(duong)} · {so.st_size}B · vung=({dau},{cuoi}) · "
         f"{'nhac' if dang_nhac else 'im'}")
    if not dang_nhac:
        sys.exit(0)

    ten = os.path.basename(duong)
    kb = so.st_size // 1024
    print(_common.json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "permissionDecisionReason": "TDQ: a reminder, not a block.",
            "additionalContext": _common.trim([
                f"[{MA}] {ten} ({kb} KB) is already in context from an earlier read, unchanged.",
                "Need another part? Read it with offset/limit. Need the same part? Do not re-read.",
            ]),
        }
    }, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
