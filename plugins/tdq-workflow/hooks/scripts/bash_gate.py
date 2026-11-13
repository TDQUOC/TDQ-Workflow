#!/usr/bin/env python3
"""PreToolUse (Bash) — observe/remind; deny sub-agent mutation before implement.

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
import os as _tdq_os, sys as _tdq_sys
_tdq_here = _tdq_os.path.dirname(_tdq_os.path.abspath(__file__))
_tdq_scripts = _tdq_os.path.normpath(_tdq_os.path.join(_tdq_here, '..', '..', 'scripts'))
for _p in (_tdq_scripts, _tdq_here):
    if _tdq_os.path.isdir(_p) and _p not in _tdq_sys.path:
        _tdq_sys.path.insert(0, _p)
import utf8_io  # noqa: E402,F401
import os
import re

from _common import (
    block,
    detect_subagent,
    echo_line,
    is_agy,
    observe,
    payload_cwd,
    read_payload,
    remind,
    remind_force,
    turn_rows,
)
# Keep this AFTER `from _common`: `_common` is what injects `scripts/` into sys.path.
from tdq_state import _info  # noqa: E402

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
# CLI aliases → the gate name prompt_context writes into `signal` rows. `approve plan --mode`
# is also the answer to the mode gate, so a matched `mode` signal opens it too.
SIGNAL_TARGETS = {"nhanh": ("quick",), "express": ("quick",), "plan": ("plan", "mode")}  # i18n-allow
SHELL_MUTATOR = re.compile(
    r"^\s*(?:rm\b|sed\b.*(?:^|\s)-i(?:\s|$)|(?:cp|mv|tee)\b|"
    r"(?:Set-Content|Add-Content|Out-File|Copy-Item|Move-Item|Remove-Item|New-Item|Set-Item)\b|"
    r"python3?\b.*\bopen\([^)]*['\"](?:w|a)['\"])", re.IGNORECASE)
STDOUT_WRITE = re.compile(r"(?<!\d)>{1,2}\s*(?!&)(\S+)")
DOCS_ARTIFACT = re.compile(r"docs[\\/]tdq[\\/]artifacts[\\/]", re.IGNORECASE)


def _latest_signal(rows, targets):
    """The LATEST kind="signal" row matching one of targets (walking the turn ledger backwards)."""
    for row in reversed(rows):
        if row.get("kind") == "signal" and row.get("target") in targets:
            return row
    return None


def _check_signal_mismatch(cwd, payload, target, rows):
    """Deny an approval the user's own prompt this turn did not give.

    One user prompt opens one gate: prompt_context classifies the prompt and writes a `signal`
    row. A `turn_start` row proves that hook ran this turn, so a missing or unmatched signal
    means the approval came from the agent, not the user (play3clone 2026-11-08: "1a", then
    `approve spec` + `approve plan` in the same turn). No `turn_start` → a host without the
    prompt hook: keep the old reminder rather than deadlock every approval.
    """
    targets = SIGNAL_TARGETS.get(target, (target,))
    row = _latest_signal(rows, targets)
    if row is not None and row.get("matched") is True and not row.get("mode_conflict"):
        return
    lines = [
        (f"The user's prompt this turn did not approve {target} (or the mode differs) "
         "— STOP, do not run this command."),
        f"How: present {target}, END the turn, wait for the user's own approval message.",
        echo_line("TDQ:APPROVE", "asked again and got a clear confirmation"),
    ]
    if any(r.get("kind") == "turn_start" for r in rows):
        _info(f"bash_gate: block TDQ:APPROVE · target={target} · "
              f"signal={'none' if row is None else 'unmatched'}")
        block(cwd, payload, "TDQ:APPROVE", lines, day_du=True)
    if row is not None:
        remind_force(cwd, payload, "TDQ:APPROVE", lines)


def _clean(raw):
    return raw.strip("'\"")


_PS_WRITE_PATTERN = re.compile(
    r"(?:Set-Content|Add-Content|Out-File|Copy-Item|Move-Item|Remove-Item|New-Item)\b",
    re.IGNORECASE,
)


def _enforce_agy_bash_guards(payload, cwd):
    info = detect_subagent(payload, cwd)
    agy = is_agy()
    if not agy and not info.get("is_subagent"):
        return False
    cmd = str((payload.get("tool_input") or {}).get("command") or "")
    role = (info.get("role") or "").lower()
    if any(r in role for r in ("reviewer", "browser")) and (
        ">" in cmd or _PS_WRITE_PATTERN.search(cmd) or any(w in cmd for w in ("tee ", "sed -i", "rm ", "mv "))
    ):
        block(cwd, payload, "READONLY", [f"Read-only subagent `{role}` cannot mutate files via shell."])
        return True
    norm_cmd = cmd.replace("\\", "/")
    if agy and _PS_WRITE_PATTERN.search(cmd) and ("docs/tdq/state.json" in norm_cmd or "docs/tdq/STATE.md" in norm_cmd):
        block(cwd, payload, "GATE", ["Do not mutate TDQ state via PowerShell; use tdq_state.py CLI."])
        return True
    if agy and re.search(r"git\s+(?:checkout\s+-[bB]|switch\s+-[cC]|branch)\s+['\"]?(?:claude|antigravity|gemini|codex)[-_]", cmd, re.IGNORECASE):
        block(cwd, payload, "TDQ:GIT", ["AI-prefixed branch names are banned; name the branch after the work."])
        return True
    return False


def main():
    payload = read_payload()
    cmd = (payload.get("tool_input") or {}).get("command") or ""
    if not isinstance(cmd, str) or not cmd:
        return
    cwd = payload_cwd(payload)
    if _enforce_agy_bash_guards(payload, cwd):
        return
    rows = turn_rows(cwd, payload)  # P0-3: read once, reused by every check below
    state = __import__("tdq_state").load(cwd) or {}
    parts = [part.strip() for part in re.split(r"[;&]", cmd) if part.strip()]
    mutates_outside_docs = any(
        (SHELL_MUTATOR.search(part) and not DOCS_ARTIFACT.search(part))
        or any(not DOCS_ARTIFACT.search(target) and target.lower() not in ("/dev/null", "$null")
               for target in STDOUT_WRITE.findall(part))
        for part in parts)
    if payload.get("agent_id") and state.get("active_request") \
            and state.get("phase") not in ("implement", "qc") and mutates_outside_docs:
        block(cwd, payload, "TDQ:TEAM", [
            "A sub-agent may not mutate the project through Bash/PowerShell before implement.",
            "Return structured output, or write only the assigned report under docs/tdq/artifacts/.",
            "The TDQ leader remains the state and source writer.",
        ])

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
        # A gate already approved needs no fresh consent to move on: the QC fix round goes
        # back with `set phase=implement` long after the plan was approved, no signal written.
        if target and not state.get(f"{target}_approved"):
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
            ("This command dumps its whole content into context — every output is re-read on "
             "every API call after it."),
            ("How: limit it inside the command (`head`/`tail`/`sed -n`/`-n`/`--stat`/"
             "`--oneline`), or use Read with `offset`/`limit`. Genuinely need the whole file? "
             "Then run it — quality outranks context cost."),
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
