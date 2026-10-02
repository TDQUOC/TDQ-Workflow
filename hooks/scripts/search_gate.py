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
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common  # noqa: E402 — also puts `scripts/` on sys.path for search_rules
import search_observe  # noqa: E402
import search_rules  # noqa: E402

MA = "TDQ:SEARCH"
# Tool names of a shell across hosts: Claude Code says `Bash`; Codex has used `shell`,
# `local_shell` and `exec_command`. The rules module accepts the same aliases.
CONG_CU_SHELL = {"Bash", "shell", "local_shell", "exec_command"}


def _log(message):
    """Log service: ISO timestamp on stderr, on by default, muted by TDQ_LOG=0."""
    if os.environ.get("TDQ_LOG", "1") != "0":
        print(f"[{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}] search_gate: {message}",
              file=sys.stderr)


def _lenh(ten_tool, vao):
    """-> what to classify: the shell command (str or argv list) or the Grep pattern."""
    if ten_tool == "Grep":
        return vao.get("pattern") or ""
    return vao.get("command") or vao.get("cmd") or ""


def quyet(cwd, phien, ten_tool, vao):
    """-> (allowed, reason, classification). Pure enough to test without a subprocess."""
    cong_cu = "Grep" if ten_tool == "Grep" else "Bash"
    pl = search_rules.phan_loai(cong_cu, _lenh(ten_tool, vao))
    if pl.get("loai") not in (search_rules.TIM_CODE, search_rules.LOC_FILE):
        return True, "not a search", pl
    khoa = search_observe.khoa_hien_tai(cwd, phien)
    tt = search_observe.trang_thai(search_observe.doc_so(cwd, khoa))
    tt["cua_so"] = search_rules.CUA_SO
    ok, ly_do = search_rules.quyet_dinh(pl, tt)
    if pl.get("loai") == search_rules.TIM_CODE:
        # Only a search that RAN counts toward the unlock window: a denied one never executed.
        search_observe.ghi_so(cwd, {"ts": time.time(), "khoa": khoa, "loai": "tim",
                                    "cho_phep": ok, "tinh_cua_so": ok,
                                    "doan_mo": bool(pl.get("doan_mo"))})
    return ok, ly_do, pl


def main():
    try:
        payload = _common.read_payload()
        ten_tool = payload.get("tool_name") or ""
        if ten_tool != "Grep" and ten_tool not in CONG_CU_SHELL:
            sys.exit(0)
        cwd = _common.payload_cwd(payload)
        vao = payload.get("tool_input") or {}
        ok, ly_do, pl = quyet(cwd, _common.session_id(payload), ten_tool, vao)
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 — a gate must never break the agent's tool call
        _log(f"error, letting the call through: {type(exc).__name__}: {exc}")
        sys.exit(0)

    _log(f"{ten_tool} · {pl.get('loai')} · doan_mo={pl.get('doan_mo')} · "
         f"{'cho' if ok else 'CHAN'} · {ly_do.splitlines()[0][:80]}")
    if ok:
        sys.exit(0)
    # Every Claude Code deny goes through `_common.block()` (pinned by test_compliance_protocol).
    # `day_du=True`: the 200-character reminder cap would cut the one thing the agent needs here —
    # which query to run instead. The rules already start the reason with the code; drop it so
    # `block()` does not print it twice.
    dong = ly_do.splitlines() or [ly_do]
    dong[0] = dong[0].replace(f"[{MA}] ", "", 1)
    _common.block(cwd, payload, MA, dong, day_du=True)


if __name__ == "__main__":
    main()
