#!/usr/bin/env python3
"""PreToolUse (Bash) — observe + remind, NEVER block.

1. Observe into the turn ledger: `state_cli` when the command calls scripts/tdq_state.py,
   `next_run` when that command is `next`. This is the evidence letting stop_gate know the
   agent really ran the command, instead of trusting an echo line the model printed itself.
2. Remind:
   TDQ:GIT   — a branch/worktree name starting with claude|antigravity|gemini|codex; a commit
               message carrying AI traces ("generated with…", Co-Authored-By).
   TDQ:STATE — writing docs/tdq/state.json | STATE.md straight through the shell (redirect,
               tee, sed -i, mv/cp, truncate, inline python).
   TDQ:OUTPUT— a command dumping a whole file/history into context with no line limit.
"""
import os
import re

from _common import (echo_line, observe, payload_cwd, read_payload, remind,
                     remind_force, turn_rows)

BAN = re.compile(r"^(claude|antigravity|gemini|codex)", re.IGNORECASE)
BRANCH_PATTERNS = [
    re.compile(r"git\s+checkout\s+-b\s+(\S+)"),
    re.compile(r"git\s+switch\s+(?:-c|--create)\s+(\S+)"),
    re.compile(r"git\s+branch\s+(?!-)(\S+)"),
]
WORKTREE = re.compile(r"git\s+worktree\s+add\s+(?:-b\s+(\S+)\s+)?(\S+)")
BAD_MSG = [
    re.compile(r"generated\s+with.{0,40}?(claude|gemini|codex|antigravity)", re.IGNORECASE | re.DOTALL),
    re.compile(r"được\s+tạo\s+(?:cùng|với|bởi).{0,40}?(claude|gemini|codex|antigravity)", re.IGNORECASE | re.DOTALL),  # i18n-allow
    re.compile(r"co-authored-by:.{0,60}?(claude|gemini|codex|antigravity)", re.IGNORECASE),
]
STATE = r"docs/tdq/(?:state\.json|STATE\.md)"
STATE_WRITES = [
    re.compile(r">{1,2}\s*['\"]?\S*" + STATE),
    re.compile(r"\btee\b[^|;&]*" + STATE),
    re.compile(r"\bsed\b[^;|&]*\s-i[^;|&]*" + STATE),
    re.compile(r"\b(?:mv|cp)\b[^;|&]*" + STATE),
    re.compile(r"\btruncate\b[^;|&]*" + STATE),
    re.compile(r"\bpython3?\b[^;|&]*" + STATE),
    re.compile(r"\bopen\([^)]*" + STATE),
]
# Commands that tend to dump their whole content into context. Every output is re-read by the
# model on EVERY remaining API call of the session, so one needless dump multiplies itself
# hundreds of times over.
DUMP = re.compile(
    r"(?:^|[|;&]|\bthen\b|\bdo\b)\s*(cat|git\s+log|git\s+diff|git\s+show|ls\s+-R)\b")
# Signs the command ALREADY limits itself — one sign is enough to stay silent.
GIOI_HAN = re.compile(
    r"\|\s*(?:head|tail|wc|jq|sed\s+-n)\b"      # piped into a trimming command
    r"|\b(?:head|tail)\b"
    r"|(?:^|\s)-[a-zA-Z]*[nc]\s*\d"              # -n 20 · -c 500 · -n20
    r"|--stat\b|--name-only\b|--oneline\b|--shortstat\b|--numstat\b"
    r"|\|\s*grep\b[^|]*\s-[a-zA-Z]*[clq]\b")
# `cat > f <<EOF` WRITES a file rather than reading one — a reminder here is just noise.
CAT_GHI = re.compile(r"\bcat\b[^|;&]*(?:<<|>)")

STATE_CLI = re.compile(r"tdq_state\.py\s+(\w[\w-]*)")
# nhanh|express are the CLI aliases of quick (see LANE_ALIASES in tdq_state).  # i18n-allow
APPROVE_CLI = re.compile(r"tdq_state\.py\s+approve\s+(spec|plan|quick|nhanh|express)\b")
SETPHASE_CLI = re.compile(r"tdq_state\.py\s+set\b.*?\bphase=(\w+)")
NEXT_PHASE_TARGET = {"plan": "spec", "implement": "plan"}


def _latest_signal(rows, target):
    """The LATEST kind="signal" row matching target (walking the turn ledger backwards)."""
    for row in reversed(rows):
        if row.get("kind") == "signal" and row.get("target") == target:
            return row
    return None


def _check_signal_mismatch(cwd, payload, target, rows):
    row = _latest_signal(rows, target)
    if row is None:
        return
    if row.get("matched") is False or row.get("mode_conflict") is True:
        remind_force(cwd, payload, "TDQ:APPROVE", [
            f"The latest prompt is NOT clearly an approval of {target} (or the mode differs) "
            "— STOP, do not run this command.",
            "How: ASK the user to confirm the approval before calling approve/set phase.",
            echo_line("TDQ:APPROVE", "asked again and got a clear confirmation"),
        ])


def _clean(raw):
    return raw.strip("'\"")


def main():
    payload = read_payload()
    cmd = (payload.get("tool_input") or {}).get("command") or ""
    if not isinstance(cmd, str) or not cmd:
        return
    cwd = payload_cwd(payload)
    rows = turn_rows(cwd, payload)  # P0-3: read once, reused by every check below

    # (1) observe
    for sub in STATE_CLI.findall(cmd):
        observe(cwd, payload, "state_cli", cmd=sub)
        if sub == "next":
            observe(cwd, payload, "next_run")

    # (2) remind — the phase-advance guard (approve/set phase=) outranks GIT/STATE
    approve_match = APPROVE_CLI.search(cmd)
    if approve_match:
        _check_signal_mismatch(cwd, payload, approve_match.group(1), rows)
    setphase_match = SETPHASE_CLI.search(cmd)
    if setphase_match:
        target = NEXT_PHASE_TARGET.get(setphase_match.group(1))
        if target:
            _check_signal_mismatch(cwd, payload, target, rows)

    branch_names = []
    for pattern in BRANCH_PATTERNS:
        branch_names += [_clean(m) for m in pattern.findall(cmd)]
    for b_name, path in WORKTREE.findall(cmd):
        if b_name:
            branch_names.append(_clean(b_name))
        if path:
            branch_names.append(os.path.basename(_clean(path).rstrip("/")))
    for name in branch_names:
        if BAN.match(name):
            remind(cwd, payload, "TDQ:GIT", [
                f"The branch/worktree name '{name}' breaks the convention — rename it first.",
                "How: drop the claude|antigravity|gemini|codex prefix, name it after the work.",
                echo_line("TDQ:GIT", "renamed it to match the convention"),
            ], rows=rows)

    if re.search(r"git\b.*\bcommit\b", cmd, re.DOTALL):
        for pattern in BAD_MSG:
            if pattern.search(cmd):
                remind(cwd, payload, "TDQ:GIT", [
                    "The commit message carries AI traces — that breaks the convention.",
                    "How: drop 'generated with …', 'được tạo cùng/với AI' and any AI Co-Authored-By.",  # i18n-allow
                    echo_line("TDQ:GIT", "fixed the commit message"),
                ], rows=rows)

    if DUMP.search(cmd) and not GIOI_HAN.search(cmd) and not CAT_GHI.search(cmd):
        remind(cwd, payload, "TDQ:OUTPUT", [
            "This command dumps its whole content into context — every output is re-read on "
            "every API call after it.",
            "How: limit it inside the command (`head`/`tail`/`sed -n`/`-n`/`--stat`/"
            "`--oneline`), or use Read with `offset`/`limit`. Genuinely need the whole file? "
            "Then run it — quality outranks context cost.",
            echo_line("TDQ:OUTPUT", "limited the output, or confirmed the whole is needed"),
        ], rows=rows)

    if re.search(STATE, cmd):
        for pattern in STATE_WRITES:
            if pattern.search(cmd):
                remind(cwd, payload, "TDQ:STATE", [
                    "Do not write the state file straight through the shell.",
                    "How: python3 scripts/tdq_state.py set|approve|init|reset.",
                    echo_line("TDQ:STATE", "wrote state through the CLI"),
                ], rows=rows)


if __name__ == "__main__":
    main()
