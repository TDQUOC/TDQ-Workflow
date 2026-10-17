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
# `utf8_io` first: a hook that dies on a cp1252 console takes the whole turn with it, and every
# reminder below carries `✓` plus Vietnamese. Imported for the side effect, not for a name.
import utf8_io  # noqa: E402,F401 — stdout/stderr become UTF-8 the moment this lands
# The import MUST be `from tdq_state import <name>` and then call `f()` directly, NEVER
# through the module attribute: graphify (0.9.28 and 0.9.42) only emits a cross-file `calls`
# edge for the from-import shape. Call through the attribute and the graph goes blind to the
# whole hook → state chain.
import tdq_state  # noqa: E402 — kept so other modules can `from _common import tdq_state`
from tdq_state import (VALID_MODES, mode_label, resolve_project_dir,  # noqa: E402
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
    # No skip-QC variant here on purpose (2026-09-23): `muc_qc=off` exists but is never
    # OFFERED — putting the opt-out in the most-read line is offering it.
    "quick": 'say "approve quick" or type "A"',
}

# Built from VALID_MODES, never typed by hand: a binary pair hardcoded here means a plan
# naming the third mode reads back as None, and the mode gate silently proposes the wrong
# one. Longest code first, because the regex takes the FIRST matching branch: a short code
# that is the prefix of a longer one would swallow the tail if it came first.
_MODE_NHANH = "|".join(re.escape(m) for m in sorted(VALID_MODES, key=len, reverse=True))
_PLAN_MODE = re.compile(r"Mode thực thi:\s*(%s)" % _MODE_NHANH, re.IGNORECASE)  # i18n-allow


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
# 2026-09-17: the sixth code, TDQ:GON — the lean-law channels (SessionStart, SubagentStart
# carry the law body; UserPromptSubmit carries one pointer line). Declared in spec §5 first.
# 2026-10-02: the seventh, TDQ:DOC — `read_gate.py` on a whole-file re-read. Declared in spec
# 2026-09-28-2324 §2 first, and documented in `reminder-codes.md` with the other six.
# 2026-10-03: the eighth, TDQ:SEARCH — `search_gate.py` DENIES a code search that skips the
# concept layer. The second blocking point of the workflow; why, in `docs/kien-truc.md` 2026-10-03
# and spec 2026-10-03-0015 §3.
# 2026-10-03: the ninth, TDQ:ASK — `ask_gate.py` REMINDS (never blocks) when AskUserQuestion is
# called in implement/qc: an unmet spec threshold is recorded with `lech add`, not asked about.
# Why, in `docs/kien-truc.md` 2026-10-03 and spec 2026-10-03-0732 §3.
# 2026-10-08: the tenth, TDQ:LSP — `lsp_gate.py` DENIES `mcp__lsp__start_lsp` sent without a
# `language_id` or with a (root, language) pair no LSP module of the project has. The reason is a
# wrong call, not a missing approval; why, in `docs/kien-truc.md` 2026-10-08 and spec
# 2026-10-07-2225 §3.
CODES = ("TDQ:NEXT", "TDQ:APPROVE", "TDQ:LOG", "TDQ:STATE", "TDQ:GIT", "TDQ:GON",
         "TDQ:DOC", "TDQ:SEARCH", "TDQ:ASK", "TDQ:LSP")

# The token budget cap (spec §2.7) — measured on the reminder content.
MAX_REMIND_CHARS = 200
MAX_REMIND_LINES = 3


def read_payload():
    """Read an object payload and discard ill-typed protocol fields."""
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError, UnicodeError):
        tdq_state._warn("Hook payload rejected: invalid JSON or unreadable stdin")
        return {}
    if not isinstance(payload, dict):
        tdq_state._warn("Hook payload rejected: expected an object")
        return {}
    expected = {"cwd": str, "session_id": str, "tool_name": str,
                "hook_event_name": str, "prompt": str, "source": str,
                "agent_type": str, "stop_hook_active": bool, "tool_input": dict}
    for field, kind in expected.items():
        if field in payload and not isinstance(payload[field], kind):
            tdq_state._warn(f"Hook payload field rejected: {field}")
            payload.pop(field)
            if field == "tool_input":
                payload["tool_input"] = {}
                payload.pop("tool_name", None)
    _sanitize_tool_input(payload)
    return payload


def _sanitize_tool_input(payload):
    tool_input = payload.get("tool_input", {})
    expected = {"command": (str, list), "cmd": str, "file_path": str,
                "notebook_path": str, "path": str, "pattern": str,
                "root_dir": str, "language_id": str}
    for field in tool_input.keys() & expected.keys():
        value = tool_input[field]
        valid = isinstance(value, expected[field])
        if isinstance(value, list):
            valid = isinstance(value, expected[field]) and all(
                isinstance(arg, str) for arg in value)
        if not valid:
            tdq_state._warn(f"Hook payload field rejected: tool_input.{field}")
            tool_input.pop(field)
            payload.pop("tool_name", None)


def payload_cwd(payload):
    """The project root for state — the payload cwd may be a subdirectory or a worktree."""
    return resolve_project_dir(payload.get("cwd") or os.getcwd())


def session_id(payload):
    return str(payload.get("session_id") or "")


# ------------------------------------------------------------------ turn ledger

def observe(cwd, payload, event, **fields):
    """Record one real, observed action.

    Any `path` is written with forward slashes, whatever the host. The ledger is compared
    against git output (which always prints `/`) and against prefixes like `docs/workinglog`,
    so letting a Windows `\\` through would make the same file look like two different ones to
    every reader downstream.
    """
    if isinstance(fields.get("path"), str):
        fields["path"] = fields["path"].replace(os.sep, "/")
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


def _tuyet_doi(text, cwd):
    """Make every `python3 scripts/X.py` in a reminder runnable from THIS project.

    Applied AFTER `trim`: the 200-character cap measures what the reminder says, while the path
    prefix is mechanical. Rewriting before the cap would cut a command in half, and a command cut
    in half is one the agent cannot run.
    """
    return tdq_state.lenh_cho_project(text, cwd)


def trim(lines):
    """Force it under the cap: <= 3 lines, <= 200 characters."""
    lines = [l for l in lines if l][:MAX_REMIND_LINES]
    text = "\n".join(lines)
    if len(text) > MAX_REMIND_CHARS:
        text = text[:MAX_REMIND_CHARS - 1].rstrip() + "…"
    return text


def remind(cwd, payload, code, lines, event="PreToolUse", rows=None, decide=True):
    """Remind Claude with a CODE WITHOUT blocking the tool, then exit.

    The 3-line shape (spec §2.1): the job to do · how to do it · the echo line to print.
    A code already reminded this turn stays silent (dedupe) so no tokens are burnt.
    `rows`: an already-read turn ledger — see `already_reminded` (P0-3).
    `decide=False` leaves out `permissionDecision`: for AskUserQuestion the tool IS the question
    to the user, and an "allow" from a hook may answer it (`ask_gate.py`, 2026-10-03).
    """
    if already_reminded(cwd, payload, code, rows=rows):
        sys.exit(0)
    turn_log_append(cwd, "remind", session=session_id(payload), code=code)
    out = {"hookEventName": event}
    if decide:
        out["permissionDecision"] = "allow"
        out["permissionDecisionReason"] = "TDQ: a reminder, not a block."
    out["additionalContext"] = _tuyet_doi(trim([f"[{code}] {lines[0]}"] + list(lines[1:])), cwd)
    print(json.dumps({"hookSpecificOutput": out}, ensure_ascii=False))
    sys.exit(0)


def format_denial(code, lines, repeat_count=0, day_du=False):
    """Format denial lines according to first vs repeat occurrence in the turn (O07).

    - First occurrence (repeat_count == 0): full remediation instructions.
    - Repeat occurrence (repeat_count > 0): concise message saving context tokens
      while preserving the actionable recovery path.
    """
    dong = [f"[{code}] {lines[0]}"] + list(lines[1:])
    if repeat_count <= 0:
        return "\n".join(l for l in dong if l) if day_du else trim(dong)

    tag = f"[{code}] (lặp x{repeat_count + 1})" if repeat_count > 1 else f"[{code}] (lặp)"
    first_summary = lines[0].strip() if lines else ""

    action_summary = []
    for l in lines[1:]:
        l_s = l.strip()
        if not l_s:
            continue
        action_summary.append(l_s)

    repeat_body = [f"{tag} {first_summary}"]
    if action_summary:
        # Keep only the primary actionable remediation line on repeat
        primary_action = action_summary[0]
        if primary_action.endswith(":") and len(action_summary) > 1:
            primary_action = f"{primary_action} {action_summary[1]}"
        repeat_body.append(f"Gỡ nhanh: {primary_action}")

    res = "\n".join(repeat_body)
    return res if day_du else trim(repeat_body)


def block(cwd, payload, code, lines, event="PreToolUse", day_du=False):
    """BLOCK the tool with a CODE, then exit.

    Two deliberate differences from `remind()`:
    - `permissionDecision: "deny"` — the tool does not run.
    - NO dedupe by code: does not turn deny into allow. The blocking condition
      remains active while the job is undone.
    - O07: Repeated denials in the same turn with the same reason/evidence are
      formatted concisely to minimize token consumption while preserving the
      actionable remediation. New reasons or first occurrences emit full remediation.
    Written to the turn ledger under kind `block` with repeat metadata.

    `day_du=True` keeps the whole reason instead of `trim`ming it to 200 characters. Use it only
    when the reason IS the way out — the search gate's denial names the exact query to run
    instead, and a reason cut in half leaves the agent blocked with no instruction.
    """
    rows = turn_rows(cwd, payload)
    reason_key = lines[0].strip() if lines else ""
    prev_blocks = [r for r in rows if r.get("kind") == "block" and r.get("code") == code and r.get("reason_key") == reason_key]
    repeat_count = len(prev_blocks)

    turn_log_append(cwd, "block", session=session_id(payload), code=code,
                    reason_key=reason_key, repeat_count=repeat_count)
    ly_do = format_denial(code, lines, repeat_count=repeat_count, day_du=day_du)
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event,
            "permissionDecision": "deny",
            "permissionDecisionReason": _tuyet_doi(ly_do, cwd),
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
            "additionalContext": _tuyet_doi(trim([f"[{code}] {lines[0]}"] + list(lines[1:])), cwd),
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
