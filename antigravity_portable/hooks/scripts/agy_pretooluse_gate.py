#!/usr/bin/env python3
"""PreToolUse (Antigravity/agy) — hard deny on 2 fixed, pre-existing rules.

Unlike Claude Code's PreToolUse (`hooks/scripts/bash_gate.py`), which only ever REMINDS,
agy's PreToolUse `decision: "deny"` is a genuine hard block (see
docs/tdq/research/2026-08-27-1112-antigravity-portable-skill.md, Truy vấn 2). This hook
enforces exactly 2 cases that are already-locked project rules, not "not yet approved"
gates (locked decision docs/kien-truc.md § Đã chốt 2026-07-29 forbids a `deny` used to gate
on approval state — the 2 cases below are unconditional naming/write rules instead):

  (a) a branch/worktree name starting with claude|antigravity|gemini|codex
      — ported from BAN/BRANCH_PATTERNS/WORKTREE in `hooks/scripts/bash_gate.py`.
  (b) writing docs/tdq/state.json or STATE.md straight through the shell — ported from
      STATE_WRITES in the same file, tightened here: a `python3`/`open(...)` command is only
      counted as a WRITE when it names an actual write mode ("w"/"a"/"x"); a read
      (`cat`, `head`/`tail`, `sed -n`, or `open()` with no mode / mode "r") is never denied.

agy's exact PreToolUse input JSON schema is not confirmed by public docs as of 2026-08 —
so `_first_command` tries several plausible field paths for the shell command text, and this
hook never raises: an unparsable payload, or a command it cannot find, is silently allowed.
"""
import datetime
import json
import os
import re
import sys

BAN = re.compile(r"^(claude|antigravity|gemini|codex)", re.IGNORECASE)
BRANCH_PATTERNS = [
    re.compile(r"git\s+checkout\s+-b\s+(\S+)"),
    re.compile(r"git\s+switch\s+(?:-c|--create)\s+(\S+)"),
    re.compile(r"git\s+branch\s+(?!-)(\S+)"),
]
WORKTREE = re.compile(r"git\s+worktree\s+add\s+(?:-b\s+(\S+)\s+)?(\S+)")

STATE = r"docs/tdq/(?:state\.json|STATE\.md)"
STATE_WRITES = [
    re.compile(r">{1,2}\s*['\"]?\S*" + STATE),
    re.compile(r"\btee\b[^|;&]*" + STATE),
    re.compile(r"\bsed\b[^;|&]*\s-i[^;|&]*" + STATE),
    re.compile(r"\b(?:mv|cp)\b[^;|&]*" + STATE),
    re.compile(r"\btruncate\b[^;|&]*" + STATE),
    # `open(...)` only counts as a write when a write-capable mode is named in the same call —
    # a bare `open(path)` or an explicit mode "r" is a read and must never be denied.
    re.compile(r"\bopen\([^)]*" + STATE + r"[^)]*['\"](?:w|a|x)[a-z+]*['\"]"),
]

# The command field, tried across several plausible agy PreToolUse payload shapes.
_CMD_PATHS = (
    ("tool_input", "command"),
    ("toolInput", "command"),
    ("input", "command"),
    ("arguments", "command"),
    ("command",),
)


def _first_command(payload):
    """The shell command text off the payload, or "" when no known shape carries one."""
    if not isinstance(payload, dict):
        return ""
    for path in _CMD_PATHS:
        node = payload
        for key in path:
            if not isinstance(node, dict):
                node = None
                break
            node = node.get(key)
        if isinstance(node, str) and node.strip():
            return node
    return ""


def _clean(raw):
    return raw.strip("'\"")


def _branch_names(cmd):
    names = []
    for pattern in BRANCH_PATTERNS:
        names += [_clean(m) for m in pattern.findall(cmd)]
    for b_name, path in WORKTREE.findall(cmd):
        if b_name:
            names.append(_clean(b_name))
        if path:
            names.append(_clean(path).rstrip("/").rsplit("/", 1)[-1])
    return names


def _writes_state(cmd):
    if not re.search(STATE, cmd):
        return False
    return any(pattern.search(cmd) for pattern in STATE_WRITES)


def _log(msg):
    """One timestamped stderr line naming the matched case. Off with TDQ_LOG=0.

    Deliberately self-contained rather than importing `scripts/tdq_state.py` like
    `agy_stop_gate.py` does: this hook runs on EVERY tool call, so the hot path stays a
    stdlib-only import. Same shape as `tdq_state._info`.
    """
    if os.environ.get("TDQ_LOG", "1") == "0":
        return
    dau_thoi_gian = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    print(f"[{dau_thoi_gian}] ℹ️ {msg}", file=sys.stderr)


def _deny(reason):
    _log(f"agy PreToolUse deny — {reason}")
    print(json.dumps({"decision": "deny", "reason": reason}, ensure_ascii=False))


def main():
    try:
        payload = json.load(sys.stdin)
    except (ValueError, UnicodeDecodeError):
        return
    cmd = _first_command(payload)
    if not cmd:
        return

    banned = [name for name in _branch_names(cmd) if BAN.match(name)]
    if banned:
        _deny(f"[TDQ:GIT] branch/worktree name '{banned[0]}' breaks the fixed naming rule — "
              "drop the claude|antigravity|gemini|codex prefix, name it after the work.")
        return

    if _writes_state(cmd):
        _deny("[TDQ:STATE] writing docs/tdq/state.json or STATE.md straight through the shell "
              "is not allowed — use python3 scripts/tdq_state.py set|approve|init|reset.")
        return


if __name__ == "__main__":
    main()
