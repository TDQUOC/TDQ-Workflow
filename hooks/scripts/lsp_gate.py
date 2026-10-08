#!/usr/bin/env python3
"""PreToolUse on `mcp__lsp__start_lsp` — DENY a start that picks no language or the wrong root.

Why (request 2026-10-07-2225): without `language_id`, agent-lsp does not detect the language — it
starts EVERY configured server and makes the first one (`typescript`) current. On a Python repo
that crashed tsserver (`0xc0000409`) or answered "No Project" (bench 2026-10-07, runs 1–2). And
`find_symbol` only ever asks the current server, so a start on the wrong (root, language) makes it
answer empty with no error at all (upstream issue #55).

Rules, in order:
1. `language_id` missing → deny.
2. The root is inside this project AND the module table `docs/tdq/.tdq-lsp-module.json` exists AND
   no row has that (root, language) pair → deny, listing the valid calls. JavaScript and TypeScript
   are one family (one server), so either id is accepted for a module of that family.
3. Anything else → silent: a root outside the project, or no table yet, is not ours to judge.

It blocks for a WRONG CALL, never for a missing approval — `docs/kien-truc.md` 2026-07-29 stands.
The table is read as plain JSON; `lsp_module` (the tree scan) is never imported, so the hook stays
cheap (82–85 ms measured 2026-10-08, `_common` included).

Env: TDQ_PROJECT_DIR anchors the project; TDQ_LOG=0 silences the log.
"""
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common  # noqa: E402

MA = "TDQ:LSP"
FILE_BANG = os.path.join("docs", "tdq", ".tdq-lsp-module.json")
HO_TS = ("typescript", "javascript")


def _log(message):
    """Log service: ISO timestamp on stderr, on by default, muted by TDQ_LOG=0."""
    if os.environ.get("TDQ_LOG", "1") != "0":
        print(f"[{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}] lsp_gate: {message}", file=sys.stderr)


def _chuan(duong):
    return os.path.normcase(os.path.normpath(os.path.abspath(duong)))


def _cung_ho(a, b):
    return a == b or (a in HO_TS and b in HO_TS)


def doc_cap_hop_le(cwd):
    """-> [(absolute root, language)] from the module table, or None when there is no table."""
    try:
        with open(os.path.join(cwd, FILE_BANG), encoding="utf-8") as fh:
            module = (json.load(fh) or {}).get("module") or {}
    except (OSError, ValueError, AttributeError):
        return None
    return [(os.path.normpath(os.path.join(cwd, m.get("goc", "."))), m.get("lang", ""))
            for m in module.values() if isinstance(m, dict)]


def phan_xu(cwd, tool_input):
    """-> [] to allow, or the deny lines. Pure, for the tests."""
    lang = str(tool_input.get("language_id") or "").strip()
    goc = str(tool_input.get("root_dir") or "").strip()
    cap = doc_cap_hop_le(cwd) or []
    goi_y = [f'start_lsp {{"root_dir": {json.dumps(g)}, "language_id": "{l}"}}' for g, l in cap]
    if not lang:
        return ["start_lsp without language_id: agent-lsp starts every server and makes "
                "TypeScript current (crash 0xc0000409 / No Project on 2026-10-07).",
                *(["Use one of: " + " · ".join(goi_y)] if goi_y else
                  ["Pass the language of the code you work on, e.g. \"language_id\": \"python\"."])]
    if not goc or not cap:
        return []
    goc_c, cwd_c = _chuan(goc), _chuan(cwd)
    if not (goc_c == cwd_c or goc_c.startswith(cwd_c + os.sep)):
        return []
    if any(_chuan(g) == goc_c and _cung_ho(l, lang) for g, l in cap):
        return []
    return [f"No LSP module of this project is ({goc}, {lang}) — find_symbol would answer empty.",
            "Use one of: " + " · ".join(goi_y),
            "New module? python3 scripts/tdq_lsp.py kich-ban refreshes the table."]


def main():
    try:
        payload = _common.read_payload()
        cwd = _common.payload_cwd(payload)
        tool_input = payload.get("tool_input")
    except Exception as loi:  # noqa: BLE001 — a broken payload must never block the tool
        _log(f"cannot read payload ({loi}) — silent")
        sys.exit(0)
    if not isinstance(tool_input, dict) or not tool_input:
        # Unreadable or empty payload: nothing to judge. Denying here would block a correct call
        # because of a transport fault (measured 2026-10-08 with a shell-mangled JSON payload).
        _log("payload without tool_input — silent")
        sys.exit(0)
    dong = phan_xu(cwd, tool_input)
    _log(f"language_id={tool_input.get('language_id')!r} root={tool_input.get('root_dir')!r} · "
         f"{'deny' if dong else 'allow'}")
    if dong:
        _common.block(cwd, payload, MA, dong, day_du=True)
    sys.exit(0)


if __name__ == "__main__":
    main()
