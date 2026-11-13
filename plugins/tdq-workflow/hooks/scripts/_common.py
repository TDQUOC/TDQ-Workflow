"""Shared helpers for the TDQ hooks (stdlib only).

Compliance protocol 0.3.0 (spec §2.1): a hook emits a reminder carrying a CODE, and writes
both kinds of event into the turn ledger:
  - remind : which code the hook reminded about
  - observe: what REALLY happened (which file was edited, which state command ran)
At the end of the turn `stop_gate` pairs the two sides up. The evidence of compliance is the
observable EFFECT, never the model's own claim — which is why no hook reads the transcript
and none of them trusts a `✓ [TDQ:...]` line the model printed itself.
"""
import atexit
import contextlib
import json
import os
import re
import sys
import time
import urllib.parse

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
AGY_CODES = (
    "EDIT", "TEST", "TICK", "DIRTY", "LOG", "READ", "SEARCH", "NO-PLAN-MODE",
    "LSP", "LSP-WAIT", "COMPACT", "GON", "UNFINISHED", "PAUSE", "LECH",
    "SETUP", "SUBAGENT", "VUNG", "GATE", "ANCHOR", "ZERO-POPUP", "READONLY",
    "SCOPE", "FEEDBACK",
)
CODES = AGY_CODES

# The token budget cap (spec §2.7) — measured on the reminder content.
MAX_REMIND_CHARS = 200
MAX_REMIND_LINES = 3

_AGY_TOOLS = frozenset({
    "run_command", "edit_file", "write_file", "write_to_file", "replace_file_content",
    "multi_replace_file_content", "read_file", "view_file", "grep_search",
    "find_by_name", "list_dir", "search_directory", "find_file", "list_directory",
    "invoke_subagent", "swarm", "define_subagent", "ask_question", "ask_user_question",
    "call_mcp_tool", "manage_task", "send_message", "enter_plan_mode", "exit_plan_mode",
})
_AGY_PAYLOAD_KEYS = (
    "conversation_id", "conversationId", "trajectory_id", "transcriptPath",
    "workingDirectory", "user_message", "agent_step_idx", "toolName", "toolInput",
    "workspacePaths", "toolCall", "stepIdx", "invocationNum", "executionNum",
    "terminationReason", "lastUserInput",
)
TERMINAL_STOP_REASONS = frozenset({
    "USER_CANCELED", "ERROR", "MAX_INVOCATIONS", "MAX_FORCED_INVOCATIONS",
    "MAX_TOKEN_BUDGET_EXCEEDED", "TERMINAL_CUSTOM_HOOK",
})
_RUNTIME_STATE = {
    "event": None,
    "is_agy": False,
    "deny_reason": None,
    "stop_reason": None,
    "context_lines": [],
    "registered": False,
}


def _parse_event_flag(argv=None):
    args = list(argv if argv is not None else sys.argv[1:])
    for idx, tok in enumerate(args):
        if tok == "--event" and idx + 1 < len(args):
            return args[idx + 1]
    return None


def _is_antigravity_payload(raw, event=None):
    """Detect Antigravity protocol strictly from flag/host/payload markers, never bare env."""
    if event:
        return True
    if os.environ.get("TDQ_HOST") == "antigravity":
        return True
    if not isinstance(raw, dict):
        return False
    if any(k in raw for k in _AGY_PAYLOAD_KEYS):
        return True
    tname = str(raw.get("tool_name") or raw.get("toolName") or "")
    return tname in _AGY_TOOLS or (tname.startswith("mcp_") and not tname.startswith("mcp__"))


def is_agy():
    """Return True when the active hook invocation is running under Antigravity protocol."""
    return bool(_RUNTIME_STATE["is_agy"])


def _agy_active(payload=None):
    return bool(_RUNTIME_STATE["is_agy"] or (payload is not None and _is_antigravity_payload(payload)))


def _unwrap_call_mcp(tool_name, tool_input):
    if tool_name != "call_mcp_tool" or not isinstance(tool_input, dict):
        return tool_name, tool_input
    srv = str(tool_input.get("ServerName") or tool_input.get("server") or "").strip()
    tname = str(tool_input.get("ToolName") or tool_input.get("tool") or "").strip()
    args = tool_input.get("Arguments") or tool_input.get("arguments") or {}
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except ValueError:
            args = {}
    if srv and tname:
        norm_srv = "lsp" if "lsp" in srv.lower() else srv
        return f"mcp__{norm_srv}__{tname}", args if isinstance(args, dict) else {}
    return tool_name, tool_input


def extract_workspace_path(payload):
    """Return first local workspace path from Antigravity `workspacePaths`, decoding file:// URIs."""
    if not isinstance(payload, dict):
        return None
    wpaths = payload.get("workspacePaths")
    if not isinstance(wpaths, list):
        return None
    for entry in wpaths:
        if not isinstance(entry, str) or not entry.strip():
            continue
        raw = entry.strip()
        if raw.lower().startswith("file://"):
            parsed = urllib.parse.unquote(urllib.parse.urlparse(raw).path or "")
            if os.name == "nt" and len(parsed) >= 3 and parsed[0] == "/" and parsed[2] == ":":
                parsed = parsed[1:]
            raw = parsed or raw
        if raw:
            return raw
    return None


def _flush_agy_stdout():
    """Single-JSON stdout emitter called via atexit for Antigravity hook protocol."""
    if not _RUNTIME_STATE["is_agy"]:
        return
    if _RUNTIME_STATE["deny_reason"]:
        reason = _RUNTIME_STATE["deny_reason"]
        payload = {
            "allow_tool": False,
            "decision": "deny",
            "reason": reason,
            "message": reason,
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            },
        }
        sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
        sys.stdout.flush()
        return
    if _RUNTIME_STATE["stop_reason"]:
        payload = {"decision": "continue", "reason": _RUNTIME_STATE["stop_reason"]}
        sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
        sys.stdout.flush()
        return
    if _RUNTIME_STATE["context_lines"] and _RUNTIME_STATE["event"] in (
        "SessionStart", "PreInvocation", "PostInvocation", None
    ):
        text = "\n".join(line for line in _RUNTIME_STATE["context_lines"] if line)
        if text:
            sys.stdout.write(json.dumps({
                "additionalContext": text,
                "injectSteps": [{"systemMessage": {"systemMessage": text}}],
            }, ensure_ascii=False) + "\n")
            sys.stdout.flush()


def _ensure_atexit():
    if not _RUNTIME_STATE["registered"]:
        atexit.register(_flush_agy_stdout)
        _RUNTIME_STATE["registered"] = True


def normalize_payload(raw):
    """Normalize Antigravity 2.0 and Claude Code hook payloads into one canonical dict."""
    event = _parse_event_flag()
    agy = _is_antigravity_payload(raw, event=event)
    _RUNTIME_STATE.update({
        "event": event,
        "is_agy": agy,
        "deny_reason": None,
        "stop_reason": None,
        "context_lines": [],
    })
    if not isinstance(raw, dict):
        return {}
    payload = dict(raw)
    if agy:
        tool_call = payload.get("toolCall") if isinstance(payload.get("toolCall"), dict) else {}
        tname = str(payload.get("tool_name") or payload.get("toolName") or tool_call.get("name") or "")
        if tname.startswith("CORTEX_STEP_TYPE_"):
            tname = tname[len("CORTEX_STEP_TYPE_"):].lower()
        tinput = (payload.get("tool_input") or payload.get("toolInput") or tool_call.get("args")
                  or payload.get("arguments") or payload.get("input") or {})
        if isinstance(tinput, str):
            try:
                tinput = json.loads(tinput)
            except ValueError:
                tinput = {}
        tinput = dict(tinput) if isinstance(tinput, dict) else {}
        tname, tinput = _unwrap_call_mcp(tname, tinput)
        if tname.startswith("mcp_") and not tname.startswith("mcp__") and "_lsp_" in tname:
            op = tname.split("_lsp_", 1)[1]
            payload["original_tool_name"] = tname
            tname = f"mcp__lsp__{op}"
        if "file_path" not in tinput:
            for alias in ("TargetFile", "Path", "AbsolutePath", "path", "target_file"):
                if isinstance(tinput.get(alias), str) and tinput[alias].strip():
                    tinput["file_path"] = tinput[alias]
                    break
        if "command" not in tinput:
            for alias in ("CommandLine", "cmd"):
                if isinstance(tinput.get(alias), str) and tinput[alias].strip():
                    tinput["command"] = tinput[alias]
                    break
        if tname in ("read_file", "view_file", "Read"):
            if "offset" not in tinput and "StartLine" in tinput:
                tinput["offset"] = tinput.get("StartLine")
            if "limit" not in tinput and "StartLine" in tinput and "EndLine" in tinput:
                try:
                    sl = int(tinput["StartLine"])
                    el = int(tinput["EndLine"])
                    if el >= sl:
                        tinput["limit"] = (el - sl) + 1
                except (TypeError, ValueError):
                    pass
            if "limit" not in tinput and "ByteOffset" in tinput and "EndLine" not in tinput:
                tinput["limit"] = 150
        if "tool_name" in payload or "toolName" in payload or tname:
            payload["tool_name"] = tname
        if any(k in payload for k in ("tool_input", "toolInput", "toolCall", "arguments", "input")) or tinput:
            payload["tool_input"] = tinput
        if not payload.get("prompt") and isinstance(payload.get("lastUserInput"), str) and payload["lastUserInput"].strip():
            payload["prompt"] = payload["lastUserInput"]

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


def read_payload():
    """Read an object payload and discard ill-typed protocol fields."""
    _ensure_atexit()
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError, UnicodeError):
        tdq_state._warn("Hook payload rejected: invalid JSON or unreadable stdin")
        return normalize_payload({})
    if not isinstance(payload, dict):
        tdq_state._warn("Hook payload rejected: expected an object")
        return normalize_payload({})
    return normalize_payload(payload)


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
    if isinstance(payload, dict):
        for key in ("cwd", "workingDirectory", "working_directory", "workspace_root", "project_root", "root"):
            val = payload.get(key)
            if isinstance(val, str) and val.strip():
                return resolve_project_dir(val)
        ws_path = extract_workspace_path(payload)
        if ws_path:
            return resolve_project_dir(ws_path)
    return resolve_project_dir(os.getcwd())


def session_id(payload):
    if not isinstance(payload, dict):
        return "default" if _RUNTIME_STATE["is_agy"] else ""
    if _agy_active(payload):
        for key in ("conversation_id", "conversationId", "session_id", "sessionId", "trajectory_id"):
            val = payload.get(key)
            if isinstance(val, str) and val.strip():
                return re.sub(r"[^A-Za-z0-9._-]", "_", val.strip())[:64]
        return "default"
    return str(payload.get("session_id") or "")


# ------------------------------------------------------------------ NTFS locks & shards

def _runtime_dir(cwd):
    return os.path.join(cwd, "docs", "tdq", ".tdq-runtime")


def _shard_turn_path(cwd, conv_id):
    return os.path.join(_runtime_dir(cwd), f"turns-{conv_id}.jsonl")


@contextlib.contextmanager
def with_ntfs_lock(lock_path, attempts=200):
    """Acquire a non-blocking Windows NTFS byte lock with exponential backoff."""
    parent = os.path.dirname(lock_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    lf = None
    locked = False
    for attempt in range(attempts):
        try:
            if os.name == "nt":
                import msvcrt
                lf = open(lock_path, "a+b")
                lf.seek(0)
                msvcrt.locking(lf.fileno(), msvcrt.LK_NBLCK, 1)
                locked = True
            break
        except OSError:
            if lf is not None:
                try:
                    lf.close()
                except OSError:
                    pass
                lf = None
            if attempt == attempts - 1:
                yield False
                return
            time.sleep(min(0.02, 0.002 * (attempt % 10 + 1)))
    try:
        yield True
    finally:
        if lf is not None:
            if locked and os.name == "nt":
                import msvcrt
                try:
                    lf.seek(0)
                    msvcrt.locking(lf.fileno(), msvcrt.LK_UNLCK, 1)
                except OSError:
                    pass
            try:
                lf.close()
            except OSError:
                pass


def _lock_and_append_jsonl(path, row):
    """Append one JSONL record under a dedicated NTFS lockfile for zero contention drops."""
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    raw = (json.dumps(row, ensure_ascii=False) + "\n").encode("utf-8")
    with with_ntfs_lock(path + ".lock") as ok:
        if not ok:
            return False
        try:
            with open(path, "ab") as fh:
                fh.write(raw)
                fh.flush()
            return True
        except OSError:
            return False


def _read_jsonl(path):
    rows = []
    if not os.path.isfile(path):
        return rows
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                s = line.strip()
                if not s:
                    continue
                try:
                    rows.append(json.loads(s))
                except ValueError:
                    continue
    except OSError:
        pass
    return rows


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
    sid = session_id(payload)
    if _agy_active(payload):
        kind = fields.pop("kind", "observe")
        row = {"ts": tdq_state.now_iso(), "kind": kind, "event": event, "session": sid, **fields}
        _lock_and_append_jsonl(_shard_turn_path(cwd, sid), row)
        return
    turn_log_append(cwd, "observe", session=sid, event=event, **fields)


def turn_rows(cwd, payload=None):
    sid = session_id(payload) if payload is not None else None
    rows = turn_log_read(cwd, session=sid)
    if payload is not None and _agy_active(payload) and sid:
        shard = _read_jsonl(_shard_turn_path(cwd, sid))
        if shard:
            return list(rows) + shard
    return rows


def already_reminded(cwd, payload, code, rows=None):
    """Has this code already been reminded in the current turn (dedupe: once per code/turn)?

    `rows`: an already-read turn ledger (P0-3 — avoids re-reading `.tdq-turn.jsonl` when the
    caller got rows from another read inside the same invoke). None → read it here.
    """
    if rows is None:
        rows = turn_rows(cwd, payload)
    return any(
        (r.get("kind") == "remind" or r.get("event") == "remind")
        and r.get("code") == code
        for r in rows
    )


def _fmt_tag(code):
    c = str(code)
    return f"[{c}]" if c.startswith("TDQ:") else f"[TDQ:{c}]"


def emit_context(lines):
    """Queue additionalContext lines for Antigravity or print on stdout for Claude."""
    text = "\n".join(str(l) for l in lines if l) if isinstance(lines, (list, tuple)) else str(lines or "")
    if not text:
        return
    if _RUNTIME_STATE["is_agy"]:
        _ensure_atexit()
        _RUNTIME_STATE["context_lines"].append(text)
    else:
        print(text)


def queue_remind(cwd, payload, code, text):
    """Queue a PreToolUse reminder to flush cleanly at PostInvocation / PreInvocation."""
    sid = session_id(payload)
    qpath = os.path.join(_runtime_dir(cwd), f"pending-reminders-{sid}.jsonl")
    _lock_and_append_jsonl(qpath, {"code": code, "text": text})


def flush_pending_reminders(cwd, conv_id):
    """Pop queued PreToolUse reminders for conv_id so next invocation sees them."""
    qpath = os.path.join(_runtime_dir(cwd), f"pending-reminders-{conv_id}.jsonl")
    with with_ntfs_lock(qpath + ".lock"):
        rows = _read_jsonl(qpath)
        if rows:
            try:
                os.remove(qpath)
            except OSError:
                pass
    return [r.get("text", "") for r in rows if r.get("text")]


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


def _as_lines(lines):
    if isinstance(lines, str):
        return lines.splitlines() or [lines]
    return [str(l) for l in (lines or [])]


def remind(cwd, payload, code, lines, event="PreToolUse", rows=None, decide=True):
    """Remind Claude with a CODE WITHOUT blocking the tool, then exit.

    The 3-line shape (spec §2.1): the job to do · how to do it · the echo line to print.
    A code already reminded this turn stays silent (dedupe) so no tokens are burnt.
    `rows`: an already-read turn ledger — see `already_reminded` (P0-3).
    `decide=False` leaves out `permissionDecision`: for AskUserQuestion the tool IS the question
    to the user, and an "allow" from a hook may answer it (`ask_gate.py`, 2026-10-03).
    """
    if already_reminded(cwd, payload, code, rows=rows):
        if _agy_active(payload):
            return False
        sys.exit(0)
    line_list = _as_lines(lines)
    tag = _fmt_tag(code)
    head = line_list[0] if line_list else ""
    prefixed = head if head.startswith(("[TDQ:", f"[{code}]")) else f"{tag} {head}"
    body = _tuyet_doi(trim([prefixed] + line_list[1:]), cwd)
    sid = session_id(payload)
    if _agy_active(payload):
        _ensure_atexit()
        row = {"ts": tdq_state.now_iso(), "kind": "remind", "event": "remind",
               "session": sid, "code": code, "source_event": event}
        _lock_and_append_jsonl(_shard_turn_path(cwd, sid), row)
        if (_RUNTIME_STATE["event"] or event) == "PreToolUse":
            queue_remind(cwd, payload, code, body)
        else:
            emit_context([body])
        return True
    turn_log_append(cwd, "remind", session=sid, code=code)
    out = {"hookEventName": event}
    if decide:
        out["permissionDecision"] = "allow"
        out["permissionDecisionReason"] = "TDQ: a reminder, not a block."
    out["additionalContext"] = body
    print(json.dumps({"hookSpecificOutput": out}, ensure_ascii=False))
    sys.exit(0)


def format_denial(code, lines, repeat_count=0, day_du=False):
    """Format denial lines according to first vs repeat occurrence in the turn (O07).

    - First occurrence (repeat_count == 0): full remediation instructions.
    - Repeat occurrence (repeat_count > 0): concise message saving context tokens
      while preserving the actionable recovery path.
    """
    line_list = _as_lines(lines)
    tag_full = _fmt_tag(code)
    head = line_list[0] if line_list else ""
    first_line = head if head.startswith(("[TDQ:", f"[{code}]")) else f"{tag_full} {head}"
    dong = [first_line] + list(line_list[1:])
    if repeat_count <= 0:
        return "\n".join(l for l in dong if l) if day_du else trim(dong)

    tag = f"{tag_full} (lặp x{repeat_count + 1})" if repeat_count > 1 else f"{tag_full} (lặp)"  # i18n-allow
    first_summary = head.strip()

    action_summary = []
    for l in line_list[1:]:
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
        repeat_body.append(f"Gỡ nhanh: {primary_action}")  # i18n-allow

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
    line_list = _as_lines(lines)
    reason_key = line_list[0].strip() if line_list else ""
    prev_blocks = [r for r in rows if r.get("kind") == "block" and r.get("code") == code and r.get("reason_key") == reason_key]
    repeat_count = len(prev_blocks)
    sid = session_id(payload)
    ly_do = _tuyet_doi(format_denial(code, line_list, repeat_count=repeat_count, day_du=day_du), cwd)

    if _agy_active(payload):
        _ensure_atexit()
        row = {"ts": tdq_state.now_iso(), "kind": "block", "event": "block",
               "session": sid, "code": code, "reason_key": reason_key,
               "repeat_count": repeat_count, "source_event": event}
        _lock_and_append_jsonl(_shard_turn_path(cwd, sid), row)
        _RUNTIME_STATE["deny_reason"] = ly_do
        sys.exit(0)

    turn_log_append(cwd, "block", session=sid, code=code,
                    reason_key=reason_key, repeat_count=repeat_count)
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event,
            "permissionDecision": "deny",
            "permissionDecisionReason": ly_do,
        }
    }, ensure_ascii=False))
    sys.exit(0)


def remind_force(cwd, payload, code, lines, event="PreToolUse"):
    """Like `remind()` but WITHOUT dedupe by code — for when another hook (e.g. edit_gate.py)
    already claimed that code this turn and this reminder still has to get out."""
    line_list = _as_lines(lines)
    tag = _fmt_tag(code)
    head = line_list[0] if line_list else ""
    prefixed = head if head.startswith(("[TDQ:", f"[{code}]")) else f"{tag} {head}"
    body = _tuyet_doi(trim([prefixed] + line_list[1:]), cwd)
    sid = session_id(payload)
    if _agy_active(payload):
        _ensure_atexit()
        row = {"ts": tdq_state.now_iso(), "kind": "remind", "event": "remind",
               "session": sid, "code": code, "source_event": event, "force": True}
        _lock_and_append_jsonl(_shard_turn_path(cwd, sid), row)
        if (_RUNTIME_STATE["event"] or event) == "PreToolUse":
            queue_remind(cwd, payload, code, body)
        else:
            emit_context([body])
        return True
    turn_log_append(cwd, "remind", session=sid, code=code)
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event,
            "permissionDecision": "allow",
            "permissionDecisionReason": "TDQ: a reminder, not a block.",
            "additionalContext": body,
        }
    }, ensure_ascii=False))
    sys.exit(0)


def stop_block(cwd, payload, reason, code="STOP", stop_hook_active=None):
    """Emit Stop block decision: decision='continue' for Antigravity, decision='block' for Claude."""
    sid = session_id(payload)
    if _agy_active(payload):
        _ensure_atexit()
        row = {"ts": tdq_state.now_iso(), "kind": "stop_block", "event": "stop_block",
               "session": sid, "code": code}
        _lock_and_append_jsonl(_shard_turn_path(cwd, sid), row)
        _RUNTIME_STATE["stop_reason"] = reason
        return
    out = {"decision": "block", "reason": reason}
    if stop_hook_active is not None:
        out["stop_hook_active"] = stop_hook_active
    print(json.dumps(out, ensure_ascii=False))


def register_subagent_role(cwd, conv_id, role, target_task=""):
    """Persist dispatched subagent role under .tdq-runtime/sessions.json for role-aware gates."""
    path = os.path.join(_runtime_dir(cwd), "sessions.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with with_ntfs_lock(path + ".lock"):
        data = {}
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
            except (OSError, ValueError):
                data = {}
        if not isinstance(data, dict):
            data = {}
        data[str(conv_id)] = {"role": role, "task": target_task, "at": time.time()}
        try:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
        except OSError:
            pass


def detect_subagent(payload, cwd):
    """Detect subagent invocation and resolve role via sessions.json or step-0 transcriptPath."""
    sid = session_id(payload)
    spath = os.path.join(_runtime_dir(cwd), "sessions.json")
    if os.path.isfile(spath):
        try:
            with open(spath, "r", encoding="utf-8") as fh:
                reg = json.load(fh)
            if isinstance(reg, dict) and sid in reg:
                rec = reg[sid]
                return {"is_subagent": True, "role": rec.get("role"), "task": rec.get("task")}
        except (OSError, ValueError):
            pass
    if isinstance(payload, dict) and payload.get("agent_type"):
        return {"is_subagent": True, "role": str(payload.get("agent_type")), "task": ""}
    tpath = (payload or {}).get("transcriptPath") if isinstance(payload, dict) else None
    if isinstance(tpath, str) and os.path.isfile(tpath):
        try:
            with open(tpath, "r", encoding="utf-8", errors="replace") as fh:
                first_line = fh.readline()
            if first_line:
                rec = json.loads(first_line)
                txt = str(rec.get("content") or rec)
                for role_name in (
                    "tdq-security-reviewer", "tdq-reviewer", "tdq-qc-tester",
                    "tdq-implementer", "tdq-build-resolver", "tdq-refactor-cleaner",
                ):
                    if role_name in txt:
                        register_subagent_role(cwd, sid, role_name)
                        return {"is_subagent": True, "role": role_name, "task": ""}
        except (OSError, ValueError):
            pass
    return {"is_subagent": False, "role": None, "task": ""}


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
