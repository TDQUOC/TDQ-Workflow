#!/usr/bin/env python3
"""PreToolUse on `Bash` and `Grep` — DENY a code search that skips the concept layer.

Why this gate blocks while every other TDQ hook only reminds (`docs/kien-truc.md` 2026-10-03):
measured on a real session (2026-10-02, excalidraw), an agent made ~20 code searches across four
requests — almost all through Bash `grep`, not the `Grep` tool — with 0 lumen and 0 LSP calls,
until the user asked about the search rule. The rule lived in text only; nothing held it at the
moment the agent picked a tool. The user asked for it to be FORCED, and Codex's `PreToolUse`
accepts nothing but `deny` — a reminder is not available there at all.

What is decided here is decided by `scripts/search_rules.py` (pure, no I/O), so the replay tool
(`scripts/search_replay.py`) runs the very same rules on recorded sessions. This hook only:
  1. reads the command or the Grep pattern, and lets everything that is not a search through;
  2. reads the request's state from the search ledger (`search_observe.py` owns the format);
  3. asks `search_rules.quyet_dinh`, records the search, and prints `deny` + reason when refused.

It never breaks a tool call because of its own fault: any exception lets the call through. It is
cheap — no subprocess, and it never opens the files the agent is searching.

Env: TDQ_PROJECT_DIR anchors the project; TDQ_LOG=0 silences the log.
"""
import json
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common  # noqa: E402 — also puts `scripts/` on sys.path for search_rules
import search_observe  # noqa: E402
import search_rules  # noqa: E402

MA = "TDQ:SEARCH"
# The readiness stamp `tdq_setup.py --nen` writes, and how long a "still building" claim is
# believed: the builder's own overall cap (`tdq_setup.TRAN_GIAY`, 1800 s — sized from an 11-minute
# lumen index of excalidraw). Past that the build is dead, not slow.
MOC_SAN_SANG = os.path.join("docs", "tdq", ".tdq-san-sang.json")
HAN_DUNG_NEN_GIAY = 1800
TANG_KHAI_NIEM = ("lumen", "lsp", "graphify")
# Denials in one scope, with no concept query ever recorded, after which a machine with NO
# readiness stamp is treated as having no concept layer (see `ly_do_dung_xuong`).
BREAKER_CHAN = 3
# Tool names of a shell across hosts: Claude Code says `Bash`; Codex has used `shell`,
# `local_shell` and `exec_command`. The rules module accepts the same aliases.
CONG_CU_SHELL = {"Bash", "PowerShell", "shell", "local_shell", "exec_command"}


def _log(message):
    """Log service: ISO timestamp on stderr, on by default, muted by TDQ_LOG=0."""
    if os.environ.get("TDQ_LOG", "1") != "0":
        print(f"[{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}] search_gate: {message}",
              file=sys.stderr)


def _lenh(ten_tool, vao):
    """-> what to classify: the shell command (str or argv list) or the whole Grep input.

    Grep's `glob`/`path`/`type` decide whether it searches code or documents, so they travel too.
    """
    if ten_tool == "Grep":
        return vao
    return vao.get("command") or vao.get("cmd") or ""


def _doc_moc(cwd):
    """-> the readiness stamp `tdq_setup.py --nen` writes, or None. Read directly: importing
    `tdq_setup` would drag the whole setup module in before every Bash call."""
    try:
        with open(os.path.join(cwd or ".", MOC_SAN_SANG), "r", encoding="utf-8") as fh:
            moc = json.load(fh)
    except (OSError, ValueError):
        return None
    return moc if isinstance(moc, dict) else None


def ly_do_dung_xuong(moc, tt):
    """-> why the gate must stand down (the agent has no right way to go), else None.

    1. The stamp says NONE of lumen, LSP, graphify can answer — whether it is still building or
       finished that way (ollama off, no language server). Denying then sends the agent to tools
       that cannot answer; the first version did exactly that once a build had finished (review
       2026-10-03).
    2. No stamp at all (never built here: Codex, a host without SessionStart, auto-init off) AND
       the gate has already denied BREAKER_CHAN times in this scope with no concept query ever
       recorded. That is a machine without a concept layer, or a host whose tool names the ledger
       cannot see. It is deliberately NOT applied when a stamp says a layer is alive: there,
       "retry three times" must not become a way around the rule.
    """
    if moc is not None:
        tang = moc.get("tang") or {}
        song = [t for t in TANG_KHAI_NIEM if (tang.get(t) or {}).get("san_sang")]
        if not song:
            trang = "being built" if moc.get("dang_dung") else "not available here"
            return (f"no concept layer can answer yet (lumen, LSP, graphify: {trang}) — "
                    "searching freely until one does; run tdq-setup to fix it")
        return None
    if not tt.get("da_goi_khai_niem") and tt.get("so_lan_bi_chan", 0) >= BREAKER_CHAN:
        return (f"{BREAKER_CHAN} searches denied and no concept query was ever recorded here — "
                "the concept layer looks unavailable; searching freely. Run tdq-setup to install it")
    return None


def quyet(cwd, phien, ten_tool, vao):
    """-> (allowed, reason, classification, stand_down). Testable without a subprocess."""
    cong_cu = "Grep" if ten_tool == "Grep" else "Bash"
    pl = search_rules.phan_loai(cong_cu, _lenh(ten_tool, vao))
    if pl.get("loai") not in (search_rules.TIM_CODE, search_rules.LOC_FILE):
        return True, "not a search", pl, False
    khoa = search_observe.khoa_hien_tai(cwd, phien)
    tt = search_rules.trang_thai(search_observe.doc_so(cwd, khoa, phien))
    tt["cua_so"] = search_rules.CUA_SO
    ok, ly_do = search_rules.quyet_dinh(pl, tt)
    dung_xuong = None
    if not ok:
        dung_xuong = ly_do_dung_xuong(_doc_moc(cwd), tt)
        if dung_xuong:
            ok, ly_do = True, dung_xuong
    if pl.get("loai") == search_rules.TIM_CODE:
        # Only a search that RAN counts toward the unlock window: a denied one never executed.
        search_observe.ghi_so(cwd, {"ts": time.time(), "khoa": khoa, "loai": "tim",
                                    "cho_phep": ok, "tinh_cua_so": ok,
                                    "doan_mo": bool(pl.get("doan_mo"))})
    return ok, ly_do, pl, bool(dung_xuong)


def main():
    try:
        payload = _common.read_payload()
        ten_tool = payload.get("tool_name") or ""
        if ten_tool != "Grep" and ten_tool not in CONG_CU_SHELL:
            sys.exit(0)
        cwd = _common.payload_cwd(payload)
        vao = payload.get("tool_input") or {}
        ok, ly_do, pl, dung_xuong = quyet(cwd, _common.session_id(payload), ten_tool, vao)
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 — a gate must never break the agent's tool call
        _log(f"error, letting the call through: {type(exc).__name__}: {exc}")
        sys.exit(0)

    _log(f"{ten_tool} · {pl.get('loai')} · doan_mo={pl.get('doan_mo')} · "
         f"{'cho' if ok else 'CHAN'} · {ly_do.splitlines()[0][:80]}")
    if dung_xuong:
        # Say it — once per turn (`remind` dedupes by code): a gate that silently stops gating
        # leaves the agent believing the rule holds (review 2026-10-03, spec §2 row 3).
        _common.remind(cwd, payload, MA, [ly_do, "Concept layer: lumen semantic_search, LSP "
                                      "find_symbol/find_references, graphify query."])
    if ok:
        sys.exit(0)
    # Every Claude Code deny goes through `_common.block()` (pinned by test_compliance_protocol).
    # `day_du=True`: the 200-character reminder cap would cut the one thing the agent needs here —
    # which query to run instead. The rules already start the reason with the code; drop it so
    # `block()` does not print it twice.
    dong = [str(x) for x in ly_do.splitlines()] or [str(ly_do)]
    dong[0] = dong[0].replace(f"[{MA}] ", "", 1)
    _common.block(cwd, payload, MA, dong, day_du=True)


if __name__ == "__main__":
    main()
