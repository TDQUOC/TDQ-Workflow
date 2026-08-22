"""Shared helpers for the TDQ hooks (stdlib only).

Compliance protocol 0.3.0 (spec §2.1): a hook emits a reminder carrying a CODE, and writes
both kinds of event into the turn ledger:
  - remind : which code the hook reminded about
  - observe: what REALLY happened (which file was edited, which state command ran)
At the end of the turn `stop_gate` pairs the two sides up. The evidence of compliance is the
observable EFFECT, never the model's own claim — which is why no hook reads the transcript
and none of them trusts a `✓ [TDQ:...]` line the model printed itself.
"""
import json
import os
import re
import sys

_SCRIPTS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts")
)
sys.path.insert(0, _SCRIPTS_DIR)
# The import MUST be `from tdq_state import <name>` and then call `f()` directly, NEVER
# through the module attribute: graphify (0.9.28 and 0.9.42) only emits a cross-file `calls`
# edge for the from-import shape. Call through the attribute and the graph goes blind to the
# whole hook → state chain.
import tdq_state  # noqa: E402 — kept so other modules can `from _common import tdq_state`
from tdq_state import (mode_label, resolve_project_dir,  # noqa: E402
                       turn_log_append, turn_log_read)

# 0.2.0 dropped the hard gate; 0.3.0 dropped the approval slash command too — the user
# approves in plain chat.
# Every invite offers TWO ways to answer: type a sentence, or type a single letter. The letter
# is the way in for a user who does not write English either (`prompt_context.LETTER` accepts a
# bare `a`–`d`), and the recommendation always sits at A, so "A" always means approved.
APPROVE_HINTS = {
    "spec": 'say "approve spec" or type "A"',
    # The plan gate no longer asks about the mode — that is phase `mode`, right after it.
    # Making the user approve and pick a mode in one sentence is what made the block unreadable.
    "plan": 'say "approve plan" or type "A"',
    # {mode} = the mode the plan PROPOSES (its "Mode thực thi:" line), falling back to main.  # i18n-allow
    # Explained on the spot: an end user has no duty to know what "subagent" means.
    # The "the plan proposes {mode}" part comes FIRST: the reminder is cut from the tail at the
    # character cap, and cutting the proposal away leaves the user guessing what to pick.
    "mode": 'the plan proposes {mode} — say "inline" (I do it step by step right here) '
            'or "sub-agent" (several assistants in parallel), or type "A"/"B"; '
            'the old names main/subagent still work',
    # The skip-QC variant has to show up in the hint, or the user never learns the opt-out.
    "quick": 'say "approve quick" or type "A" (skip QC: "approve quick no QC")',
}

_PLAN_MODE = re.compile(r"Mode thực thi:\s*(main|subagent)", re.IGNORECASE)  # i18n-allow


def plan_mode(cwd, state):
    """The mode settled in plan_file (its 'Mode thực thi:' line), None when not written yet."""  # i18n-allow
    rel = (state or {}).get("plan_file")
    if not rel:
        return None
    path = rel if os.path.isabs(rel) else os.path.join(cwd, rel)
    try:
        with open(path, encoding="utf-8") as f:
            match = _PLAN_MODE.search(f.read())
    except OSError:
        return None
    return match.group(1).lower() if match else None

# The CLOSED list of codes (spec §2.1). Adding a new code means editing the spec first.
CODES = ("TDQ:NEXT", "TDQ:APPROVE", "TDQ:LOG", "TDQ:STATE", "TDQ:GIT")

# The token budget cap (spec §2.7) — measured on the reminder content.
MAX_REMIND_CHARS = 200
MAX_REMIND_LINES = 3


def read_payload():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def payload_cwd(payload):
    """The project root for state — the payload cwd may be a subdirectory or a worktree."""
    return resolve_project_dir(payload.get("cwd") or os.getcwd())


def session_id(payload):
    return str(payload.get("session_id") or "")


# ------------------------------------------------------------------ turn ledger

def observe(cwd, payload, event, **fields):
    """Record one real, observed action."""
    turn_log_append(cwd, "observe", session=session_id(payload),
                    event=event, **fields)


def turn_rows(cwd, payload):
    return turn_log_read(cwd, session=session_id(payload))


def already_reminded(cwd, payload, code, rows=None):
    """Has this code already been reminded in the current turn (dedupe: once per code/turn)?

    `rows`: an already-read turn ledger (P0-3 — avoids re-reading `.tdq-turn.jsonl` when the
    caller got rows from another read inside the same invoke). None → read it here.
    """
    if rows is None:
        rows = turn_rows(cwd, payload)
    return any(r.get("kind") == "remind" and r.get("code") == code for r in rows)


def trim(lines):
    """Force it under the cap: <= 3 lines, <= 200 characters."""
    lines = [l for l in lines if l][:MAX_REMIND_LINES]
    text = "\n".join(lines)
    if len(text) > MAX_REMIND_CHARS:
        text = text[:MAX_REMIND_CHARS - 1].rstrip() + "…"
    return text


def remind(cwd, payload, code, lines, event="PreToolUse", rows=None):
    """Remind Claude with a CODE WITHOUT blocking the tool, then exit.

    The 3-line shape (spec §2.1): the job to do · how to do it · the echo line to print.
    A code already reminded this turn stays silent (dedupe) so no tokens are burnt.
    `rows`: an already-read turn ledger — see `already_reminded` (P0-3).
    """
    if already_reminded(cwd, payload, code, rows=rows):
        sys.exit(0)
    turn_log_append(cwd, "remind", session=session_id(payload), code=code)
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event,
            "permissionDecision": "allow",
            "permissionDecisionReason": "TDQ: a reminder, not a block.",
            "additionalContext": trim([f"[{code}] {lines[0]}"] + list(lines[1:])),
        }
    }, ensure_ascii=False))
    sys.exit(0)


def block(cwd, payload, code, lines, event="PreToolUse"):
    """BLOCK the tool with a CODE, then exit.

    Two deliberate differences from `remind()`:
    - `permissionDecision: "deny"` — the tool does not run.
    - NO dedupe by code. The blocking condition dissolves by itself once Claude does what was
      asked (e.g. ticks `[~]` into the plan); dedupe would let the second edit slip through
      while that job is still undone, i.e. the fence would only ever work once.
    Written to the turn ledger under kind `block` so it never mixes with `remind`'s dedupe.
    """
    turn_log_append(cwd, "block", session=session_id(payload), code=code)
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event,
            "permissionDecision": "deny",
            "permissionDecisionReason": trim([f"[{code}] {lines[0]}"] + list(lines[1:])),
        }
    }, ensure_ascii=False))
    sys.exit(0)


def remind_force(cwd, payload, code, lines, event="PreToolUse"):
    """Like `remind()` but WITHOUT dedupe by code — for when another hook (e.g. edit_gate.py)
    already claimed that code this turn and this reminder still has to get out."""
    turn_log_append(cwd, "remind", session=session_id(payload), code=code)
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event,
            "permissionDecision": "allow",
            "permissionDecisionReason": "TDQ: a reminder, not a block.",
            "additionalContext": trim([f"[{code}] {lines[0]}"] + list(lines[1:])),
        }
    }, ensure_ascii=False))
    sys.exit(0)


def echo_line(code, what):
    return f"When done, print: ✓ [{code}] {what}"


def approve_hint(target, mode=None):
    hint = APPROVE_HINTS.get(target, "say approve")
    if target == "mode":
        # Print the READER label, not the machine identifier: a user has no duty to know what
        # "subagent" means when the mode gate already calls it "sub-agent implement".
        return (f"➤ Pick how to run it: {hint.format(mode=mode_label(mode or 'main'))}"
                " · Feedback: just say it")
    return f"➤ Approve: {hint} · Feedback: just say it"
