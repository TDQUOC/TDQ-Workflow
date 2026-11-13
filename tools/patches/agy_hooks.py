"""Upgrade dual-protocol lifecycle hooks for Antigravity 2.0 + Claude backward compat."""
import re
from pathlib import Path

from .common_utils import ensure_utf8_import, read_utf8, replace_exact, write_utf8


COMMON_PY = r'''#!/usr/bin/env python3
"""Dual-protocol shared runtime helpers for TDQ lifecycle hooks (Claude Code + Antigravity 2.0)."""
import atexit
import json
import os
import re
import sys
import time

SCRIPTS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts")
)
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import utf8_io  # noqa: E402,F401
from tdq_state import (  # noqa: E402
    PHASE_TABLE, effective_lane, load, render_next, resolve_project_dir,
    turn_log_append, turn_log_path, turn_log_read as _state_turn_log_read,
)

CODES = (
    "EDIT", "TEST", "TICK", "DIRTY", "LOG", "READ", "SEARCH", "NO-PLAN-MODE",
    "LSP", "LSP-WAIT", "COMPACT", "GON", "UNFINISHED", "PAUSE", "LECH",
    "SETUP", "SUBAGENT", "VUNG", "GATE", "ANCHOR", "ZERO-POPUP", "READONLY",
    "SCOPE", "FEEDBACK",
)
MAX_REMIND_CHARS = 200
MAX_REMIND_LINES = 3
APPROVE_HINTS = {
    "spec": 'Wait for the user to approve the spec in chat, then run `py -3 scripts/tdq_state.py approve spec --by "..."`.',
    "plan": 'Wait for the user to approve the plan in chat, then run `py -3 scripts/tdq_state.py approve plan --by "..."`.',
    "quick": 'Wait for the user to confirm in chat, then run `py -3 scripts/tdq_state.py approve quick --by "..."`.',
    "mode": 'Ask the user for main | subagent | codex implement mode in chat, then run `py -3 scripts/tdq_state.py set implement_mode=<val>`.',
}

_AGY_TOOLS = {
    "run_command", "edit_file", "write_file", "write_to_file", "replace_file_content",
    "multi_replace_file_content", "read_file", "view_file", "grep_search",
    "find_by_name", "list_dir", "search_directory", "find_file", "list_directory",
    "invoke_subagent", "swarm", "define_subagent", "ask_question", "ask_user_question",
    "call_mcp_tool", "manage_task", "send_message", "enter_plan_mode", "exit_plan_mode",
}

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


def _is_antigravity_payload(raw):
    if _RUNTIME_STATE["event"]:
        return True
    if os.environ.get("TDQ_HOST") == "antigravity" or os.environ.get("ANTIGRAVITY_AGENT"):
        return True
    if not isinstance(raw, dict):
        return False
    if any(k in raw for k in ("conversation_id", "conversationId", "trajectory_id", "transcriptPath", "agent_step_idx")):
        return True
    tname = str(raw.get("tool_name") or raw.get("toolName") or "")
    return tname in _AGY_TOOLS or (tname.startswith("mcp_") and not tname.startswith("mcp__"))


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


def normalize_payload(raw):
    """Normalize Antigravity 2.0 and Claude Code hook payloads into one canonical dict."""
    if not isinstance(raw, dict):
        return {}
    out = dict(raw)
    event = _parse_event_flag()
    if event:
        _RUNTIME_STATE["event"] = event
    _RUNTIME_STATE["is_agy"] = _is_antigravity_payload(raw)

    tname = str(out.get("tool_name") or out.get("toolName") or "")
    tinput = out.get("tool_input") or out.get("toolInput") or out.get("arguments") or out.get("input") or {}
    if isinstance(tinput, str):
        try:
            tinput = json.loads(tinput)
        except ValueError:
            tinput = {}
    if not isinstance(tinput, dict):
        tinput = {}
    tinput = dict(tinput)

    tname, tinput = _unwrap_call_mcp(tname, tinput)

    # Normalize Antigravity tool aliases cleanly while keeping original field names available
    if tname.startswith("mcp_") and not tname.startswith("mcp__") and "_lsp_" in tname:
        op = tname.split("_lsp_", 1)[1]
        out["original_tool_name"] = tname
        tname = f"mcp__lsp__{op}"

    # File path normalization (TargetFile / Path / AbsolutePath / TargetDir -> file_path)
    if "file_path" not in tinput:
        for alias in ("TargetFile", "Path", "AbsolutePath", "path", "target_file"):
            if isinstance(tinput.get(alias), str) and tinput[alias].strip():
                tinput["file_path"] = tinput[alias]
                break

    # Shell command normalization (CommandLine -> command)
    if "command" not in tinput:
        for alias in ("CommandLine", "cmd"):
            if isinstance(tinput.get(alias), str) and tinput[alias].strip():
                tinput["command"] = tinput[alias]
                break

    # read_file StartLine/EndLine/ByteOffset -> offset/limit
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

    out["tool_name"] = tname
    out["tool_input"] = tinput
    return out


def _flush_agy_stdout():
    """Single-JSON stdout emitter called via atexit for Antigravity hook protocol."""
    if not _RUNTIME_STATE["is_agy"]:
        return
    if _RUNTIME_STATE["deny_reason"]:
        reason = _RUNTIME_STATE["deny_reason"]
        payload = {
            "decision": "deny",
            "reason": reason,
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            },
        }
        sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
        return
    if _RUNTIME_STATE["stop_reason"]:
        payload = {"decision": "continue", "reason": _RUNTIME_STATE["stop_reason"]}
        sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
        return
    if _RUNTIME_STATE["context_lines"] and _RUNTIME_STATE["event"] in (
        "SessionStart", "PreInvocation", "PostInvocation", None
    ):
        text = "\n".join(line for line in _RUNTIME_STATE["context_lines"] if line)
        if text:
            sys.stdout.write(json.dumps({"additionalContext": text}, ensure_ascii=False) + "\n")


def _ensure_atexit():
    if not _RUNTIME_STATE["registered"]:
        atexit.register(_flush_agy_stdout)
        _RUNTIME_STATE["registered"] = True


def read_payload():
    """Parse stdin JSON payload fail-open; return normalized dict."""
    _ensure_atexit()
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw and raw.strip() else {}
        return normalize_payload(data if isinstance(data, dict) else {})
    except Exception:
        return normalize_payload({})


def payload_cwd(payload):
    """Resolve canonical project root from payload cwd keys or os.getcwd()."""
    if isinstance(payload, dict):
        for key in ("cwd", "workingDirectory", "working_directory", "workspace_root", "project_root", "root"):
            val = payload.get(key)
            if isinstance(val, str) and val.strip():
                return resolve_project_dir(val)
    return resolve_project_dir(os.getcwd())


def session_id(payload):
    """Return canonical conversation/session identifier."""
    if isinstance(payload, dict):
        for key in ("conversation_id", "conversationId", "session_id", "sessionId", "trajectory_id"):
            val = payload.get(key)
            if isinstance(val, str) and val.strip():
                return re.sub(r"[^A-Za-z0-9._-]", "_", val.strip())[:64]
    return "default"


def _runtime_dir(cwd):
    return os.path.join(cwd, "docs", "tdq", ".tdq-runtime")


def _shard_turn_path(cwd, conv_id):
    return os.path.join(_runtime_dir(cwd), f"turns-{conv_id}.jsonl")


def _lock_and_append_jsonl(path, row):
    """Append one JSONL record using a dedicated NTFS lockfile for 0% contention drop."""
    parent = os.path.dirname(path)
    os.makedirs(parent, exist_ok=True)
    line = json.dumps(row, ensure_ascii=False) + "\n"
    raw = line.encode("utf-8")
    lock_path = path + ".lock"
    for attempt in range(200):
        lf = None
        locked = False
        try:
            if os.name == "nt":
                import msvcrt
                lf = open(lock_path, "a+b")
                lf.seek(0)
                msvcrt.locking(lf.fileno(), msvcrt.LK_NBLCK, 1)
                locked = True
            with open(path, "ab") as fh:
                fh.write(raw)
                fh.flush()
            return True
        except OSError:
            if attempt == 199:
                return False
            time.sleep(min(0.02, 0.002 * (attempt % 10 + 1)))
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
    return False


def _read_jsonl(path):
    rows = []
    if not os.path.isfile(path):
        return rows
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                s = line.strip()
                if s:
                    try:
                        rows.append(json.loads(s))
                    except ValueError:
                        continue
    except OSError:
        pass
    return rows


def observe(cwd, payload, event, **fields):
    """Record hook telemetry row cleanly in sharded + canonical turn ledgers."""
    sid = session_id(payload)
    kind = fields.pop("kind", "observe")
    row = {"kind": kind, "event": event, "session": sid, **fields}
    _lock_and_append_jsonl(_shard_turn_path(cwd, sid), row)
    try:
        turn_log_append(cwd, kind, session=sid, event=event, **fields)
    except Exception:
        pass


def turn_rows(cwd, payload=None):
    """Read current conversation turn rows combining canonical ledger + per-convId NTFS shard."""
    sid = session_id(payload) if payload is not None else None
    merged = []
    try:
        merged.extend(_state_turn_log_read(cwd, session=sid))
    except Exception:
        pass
    if sid:
        shard = _read_jsonl(_shard_turn_path(cwd, sid))
        if shard:
            merged.extend(shard)
    return merged


def already_reminded(cwd, payload, code, rows=None):
    """True when reminder code was already emitted in this session."""
    sid = session_id(payload)
    items = rows if rows is not None else turn_rows(cwd, payload)
    return any(
        (r.get("kind") == "remind" or r.get("event") == "remind")
        and r.get("code") == code
        and (r.get("session", sid) == sid)
        for r in items
    )


def trim(lines, max_lines=MAX_REMIND_LINES, max_chars=MAX_REMIND_CHARS):
    """Enforce TDQ reminder cap."""
    out = [str(l).strip() for l in (lines or []) if str(l).strip()][:max_lines]
    joined = "\n".join(out)
    if len(joined) > max_chars:
        joined = joined[:max_chars - 1].rstrip() + "…"
    return joined


def emit_context(lines):
    """Queue additionalContext lines for Antigravity or print on stdout for Claude."""
    text = "\n".join(str(l) for l in lines if l) if isinstance(lines, (list, tuple)) else str(lines or "")
    if not text:
        return
    if _RUNTIME_STATE["is_agy"]:
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
    rows = _read_jsonl(qpath)
    if rows:
        try:
            os.remove(qpath)
        except OSError:
            pass
    return [r.get("text", "") for r in rows if r.get("text")]


def _fmt_tag(code):
    c = str(code)
    return f"[{c}]" if c.startswith("TDQ:") else f"[TDQ:{c}]"


def remind(cwd, payload, code, lines, event="PreToolUse", rows=None, decide=True):
    """Emit (or queue under AGY PreToolUse) a non-blocking TDQ reminder once per session."""
    if already_reminded(cwd, payload, code, rows=rows):
        return False
    body = trim(lines) if isinstance(lines, (list, tuple)) else trim(str(lines).splitlines())
    tag = _fmt_tag(code)
    msg = f"{tag} {body}" if not str(body).startswith(("[TDQ:", f"[{code}]")) else body
    observe(cwd, payload, "remind", code=code, source_event=event)
    if _RUNTIME_STATE["is_agy"]:
        if (_RUNTIME_STATE["event"] or event) == "PreToolUse":
            queue_remind(cwd, payload, code, msg)
        else:
            emit_context([msg])
    else:
        print(msg)
    return True


def remind_force(cwd, payload, code, lines, event="PreToolUse"):
    """Always emit/queue reminder regardless of prior session emission."""
    body = trim(lines) if isinstance(lines, (list, tuple)) else trim(str(lines).splitlines())
    tag = _fmt_tag(code)
    msg = f"{tag} {body}" if not str(body).startswith(("[TDQ:", f"[{code}]")) else body
    observe(cwd, payload, "remind", code=code, source_event=event, force=True)
    if _RUNTIME_STATE["is_agy"] and (_RUNTIME_STATE["event"] or event) == "PreToolUse":
        queue_remind(cwd, payload, code, msg)
    elif _RUNTIME_STATE["is_agy"]:
        emit_context([msg])
    else:
        print(msg)


def block(cwd, payload, code, lines, event="PreToolUse", day_du=False):
    """Block a PreToolUse call cleanly across both Claude Code and Antigravity 2.0."""
    body = "\n".join(str(l) for l in lines) if isinstance(lines, (list, tuple)) else str(lines)
    if not day_du:
        body = trim(body.splitlines(), max_lines=5, max_chars=400)
    tag = _fmt_tag(code)
    msg = f"{tag} {body}" if not body.startswith(("[TDQ:", f"[{code}]")) else body
    observe(cwd, payload, "block", code=code, source_event=event)
    if _RUNTIME_STATE["is_agy"]:
        _RUNTIME_STATE["deny_reason"] = msg
        return
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": msg,
        }
    }, ensure_ascii=False))


def stop_block(cwd, payload, reason, code="STOP"):
    """Emit Stop block decision: decision='continue' for Antigravity, decision='block' for Claude."""
    observe(cwd, payload, "stop_block", code=code)
    if _RUNTIME_STATE["is_agy"]:
        _RUNTIME_STATE["stop_reason"] = reason
    else:
        print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))


def echo_line(code, what):
    return f"{_fmt_tag(code)} {what}"


def approve_hint(target, mode=None):
    return APPROVE_HINTS.get(target, "")


def plan_mode(cwd, state):
    """Detect active TDQ plan vs main mode cleanly."""
    st = state or load(cwd, heal=False) or {}
    return st.get("implement_mode") or "main"


def register_subagent_role(cwd, conv_id, role, target_task=""):
    """Persist dispatched subagent role under .tdq-runtime/sessions.json for role-aware gates."""
    path = os.path.join(_runtime_dir(cwd), "sessions.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
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
    tpath = (payload or {}).get("transcriptPath") or (payload or {}).get("transcript_path")
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
'''

POST_INVOCATION_PY = r'''#!/usr/bin/env python3
"""PostInvocation hook — flush queued PreToolUse reminders and update lightweight turn state."""
import sys
from _common import (
    emit_context, flush_pending_reminders, observe, payload_cwd, read_payload, session_id
)


def main():
    payload = read_payload()
    cwd = payload_cwd(payload)
    sid = session_id(payload)
    queued = flush_pending_reminders(cwd, sid)
    observe(cwd, payload, "PostInvocation", flushed=len(queued))
    if queued:
        emit_context(queued)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
'''

SUBAGENT_DISPATCH_GATE_PY = r'''#!/usr/bin/env python3
"""PreToolUse gate for invoke_subagent / swarm / define_subagent (AGY 2.0)."""
import re
import sys
from _common import block, payload_cwd, read_payload, remind, session_id
from tdq_state import effective_phase, load


REQUIRED_IMPL_FIELDS = ("TASK:", "WORKTREE:", "VÙNG FILE:", "TEST:", "TRẢ VỀ:")  # i18n-allow


def main():
    payload = read_payload()
    cwd = payload_cwd(payload)
    tname = payload.get("tool_name") or ""
    if tname not in ("invoke_subagent", "swarm", "define_subagent", "Task", "Agent"):
        return
    tinput = payload.get("tool_input") or {}
    state = load(cwd, heal=False) or {}
    phase = effective_phase(state, warn=False)
    mode = state.get("implement_mode") or ""
    prompt = str(tinput.get("Prompt") or tinput.get("prompt") or tinput.get("brief") or "")
    role = str(tinput.get("Role") or tinput.get("subagent_type") or "")

    # Block swarm outside approved subagent mode
    if tname == "swarm" and tinput.get("action") == "add" and phase == "implement" and mode != "subagent":
        block(cwd, payload, "SUBAGENT", [
            f"Swarm add blocked while implement_mode={mode or 'unset'}.",
            "Set implement_mode=subagent after user plan approval first.",
        ])
        return

    # Enforce Workspace="inherit" when an implementer explicitly carries WORKTREE:
    if "WORKTREE:" in prompt and str(tinput.get("Workspace") or "").lower() in ("branch", "share"):
        block(cwd, payload, "SUBAGENT", [
            "TDQ already isolated a git worktree (WORKTREE:); pass Workspace='inherit' to invoke_subagent.",
        ])
        return

    # Validate 7-field assignment block on tdq-implementer dispatches during implement
    if phase == "implement" and ("tdq-implementer" in role.lower() or "TASK:" in prompt):
        missing = [f for f in REQUIRED_IMPL_FIELDS if f not in prompt]
        if missing:
            remind(cwd, payload, "SUBAGENT", [
                f"Implementer assignment missing fields: {', '.join(missing)}. Check team-mode.md.",
            ])


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
'''


def apply_all(hooks_scripts_dir: Path) -> None:
    """Write dual-protocol _common.py, new AGY hooks, and upgrade all existing hook gates."""
    write_utf8(hooks_scripts_dir / "_common.py", COMMON_PY)
    write_utf8(hooks_scripts_dir / "post_invocation.py", POST_INVOCATION_PY)
    write_utf8(hooks_scripts_dir / "subagent_dispatch_gate.py", SUBAGENT_DISPATCH_GATE_PY)

    # Ensure every hook script (except stdlib-only codex_edit_gate) imports utf8_io
    for py_file in sorted(hooks_scripts_dir.glob("*.py")):
        if py_file.name in ("_common.py", "post_invocation.py", "subagent_dispatch_gate.py", "codex_edit_gate.py"):
            continue
        ensure_utf8_import(py_file)

    # Patch ask_gate.py -> support ask_question & emit ZERO-POPUP block during active request
    ask_path = hooks_scripts_dir / "ask_gate.py"
    ask_text = read_utf8(ask_path)
    if "ZERO-POPUP" not in ask_text:
        ask_text = ask_text.replace(
            'def main():',
            'from _common import block, payload_cwd, read_payload\n'
            'from tdq_state import load\n\n\n'
            'def _agy_zero_popup_main():\n'
            '    payload = read_payload()\n'
            '    tname = payload.get("tool_name") or ""\n'
            '    if tname not in ("ask_question", "ask_user_question", "AskUserQuestion"):\n'
            '        return\n'
            '    cwd = payload_cwd(payload)\n'
            '    st = load(cwd, heal=False) or {}\n'
            '    if st.get("active_request"):\n'
            '        block(cwd, payload, "ZERO-POPUP", [\n'
            '            "Popup question UI is banned during an active TDQ request.",\n'
            '            "Ask numbered options (1a 2b 3c) directly in chat instead.",\n'
            '        ])\n\n\n'
            'def main():\n'
            '    _agy_zero_popup_main()',
            1,
        )
        write_utf8(ask_path, ask_text)

    # Patch edit_gate.py -> enforce read-only subagent roles + [TDQ:FEEDBACK] awareness
    edit_path = hooks_scripts_dir / "edit_gate.py"
    edit_text = read_utf8(edit_path)
    if "detect_subagent" not in edit_text:
        guard = '''
def _enforce_agy_readonly_subagent(payload, cwd):
    from _common import block, detect_subagent
    info = detect_subagent(payload, cwd)
    role = (info.get("role") or "").lower()
    if any(r in role for r in ("reviewer", "qc-tester", "browser")):
        block(cwd, payload, "READONLY", [
            f"Subagent role `{role}` is strictly read-only and cannot modify files.",
        ])
        return True
    return False
'''
        edit_text = edit_text.replace("def main():", guard + "\n\ndef main():", 1)
        write_utf8(edit_path, edit_text)
        replace_exact(
            edit_path,
            '    payload = read_payload()\n    tool_input = payload.get("tool_input") or {}\n'
            '    target = tool_input.get("file_path") or tool_input.get("notebook_path") or ""\n'
            '    if not target or not isinstance(target, str):\n        return\n    cwd = payload_cwd(payload)',
            '    payload = read_payload()\n    cwd = payload_cwd(payload)\n'
            '    if _enforce_agy_readonly_subagent(payload, cwd):\n        return\n'
            '    tool_input = payload.get("tool_input") or {}\n'
            '    target = tool_input.get("file_path") or tool_input.get("notebook_path") or ""\n'
            '    if not target or not isinstance(target, str):\n        return',
            label="edit_gate_readonly_guard",
        )

    # Patch bash_gate.py -> enforce read-only subagent shell mutation blocks + AGY PS cmdlets
    bash_path = hooks_scripts_dir / "bash_gate.py"
    bash_text = read_utf8(bash_path)
    if "_PS_WRITE_PATTERN" not in bash_text:
        ps_guard = '''
import re as _re_ps
_PS_WRITE_PATTERN = _re_ps.compile(
    r"(?:Set-Content|Add-Content|Out-File|Copy-Item|Move-Item|Remove-Item|New-Item)\\b",
    _re_ps.IGNORECASE,
)


def _enforce_agy_bash_guards(payload, cwd):
    from _common import block, detect_subagent
    cmd = str((payload.get("tool_input") or {}).get("command") or "")
    info = detect_subagent(payload, cwd)
    role = (info.get("role") or "").lower()
    if any(r in role for r in ("reviewer", "browser")) and (
        ">" in cmd or _PS_WRITE_PATTERN.search(cmd) or any(w in cmd for w in ("tee ", "sed -i", "rm ", "mv "))
    ):
        block(cwd, payload, "READONLY", [f"Read-only subagent `{role}` cannot mutate files via shell."])
        return True
    if _PS_WRITE_PATTERN.search(cmd) and ("docs/tdq/state.json" in cmd.replace("\\\\", "/") or "docs/tdq/STATE.md" in cmd.replace("\\\\", "/")):
        block(cwd, payload, "GATE", ["Do not mutate TDQ state via PowerShell; use tdq_state.py CLI."])
        return True
    if _re_ps.search(r"git\\s+(?:checkout\\s+-[bB]|switch\\s+-[cC]|branch)\\s+['\\x22]?(?:claude|antigravity|gemini|codex)[-_]", cmd, _re_ps.IGNORECASE):
        block(cwd, payload, "TDQ:GIT", ["AI-prefixed branch names are banned; name the branch after the work."])
        return True
    return False
'''
        bash_text = bash_text.replace("def main():", ps_guard + "\n\ndef main():", 1)
        write_utf8(bash_path, bash_text)
        replace_exact(
            bash_path,
            '    cwd = payload_cwd(payload)\n    rows = turn_rows(cwd, payload)',
            '    cwd = payload_cwd(payload)\n    if _enforce_agy_bash_guards(payload, cwd):\n        return\n    rows = turn_rows(cwd, payload)',
            label="bash_gate_agy_guards",
        )

    # Patch prompt_context.py -> route context output through emit_context + detect bug/feedback + subagent skip
    pc_path = hooks_scripts_dir / "prompt_context.py"
    pc_text = read_utf8(pc_path)
    if "flush_pending_reminders" not in pc_text:
        pc_addon = '''
def _agy_pre_invocation_hook(payload, cwd):
    from _common import detect_subagent, emit_context, flush_pending_reminders, session_id
    sid = session_id(payload)
    queued = flush_pending_reminders(cwd, sid)
    if queued:
        emit_context(queued)
    sub = detect_subagent(payload, cwd)
    if sub.get("is_subagent"):
        return True
    prompt = str(payload.get("prompt") or payload.get("user_message") or "")
    low = prompt.lower()
    if any(k in low for k in ("lỗi", "bug", "sửa lại", "broken", "fail", "không chạy", "sai rồi")):  # i18n-allow
        emit_context(["[TDQ:FEEDBACK] User reported bug/feedback: run `py -3 scripts/tdq_state.py hotfix <slug>` or open express fix cycle before editing."])
    return False
'''
        pc_text = pc_text.replace("def main():", pc_addon + "\n\ndef main():", 1)
        write_utf8(pc_path, pc_text)
        replace_exact(
            pc_path,
            "from _common import (already_reminded, approve_hint, payload_cwd, plan_mode,",
            "from _common import (already_reminded, approve_hint, emit_context, payload_cwd, plan_mode,",
            label="prompt_context_import_emit",
        )
        replace_exact(
            pc_path,
            "    payload = read_payload()\n    cwd = payload_cwd(payload)\n",
            "    payload = read_payload()\n    cwd = payload_cwd(payload)\n    if _agy_pre_invocation_hook(payload, cwd):\n        return\n",
            label="prompt_context_pre_hook",
        )
        replace_exact(
            pc_path,
            '    if mo:\n        print(lenh_cho_project(f"[TDQ:WORKTREE] {len(mo)} worktree(s) still open — run: "\n'
            '                                         "python3 scripts/tdq_team.py sweep", cwd))',
            '    if mo:\n        emit_context([lenh_cho_project(f"[TDQ:WORKTREE] {len(mo)} worktree(s) still open — run: "\n'
            '                                                "python3 scripts/tdq_team.py sweep", cwd)])',
            label="prompt_context_worktree_emit",
        )
        replace_exact(
            pc_path,
            "                    so_dong=len(dong.splitlines()))\n    print(dong)",
            "                    so_dong=len(dong.splitlines()))\n    emit_context([dong])",
            label="prompt_context_gon_emit",
        )
        replace_exact(
            pc_path,
            "    if critical:\n        print(text)\n        return",
            "    if critical:\n        emit_context([text])\n        return",
            label="prompt_context_emit_critical",
        )
        replace_exact(
            pc_path,
            "    else:\n        prompt_context_save(cwd, session, digest)\n    print(text)",
            "    else:\n        prompt_context_save(cwd, session, digest)\n    emit_context([text])",
            label="prompt_context_emit_normal",
        )

    # Patch stop_gate.py -> support AGY stop_block JSON {"decision": "continue", "reason": ...}
    stop_path = hooks_scripts_dir / "stop_gate.py"
    stop_text = read_utf8(stop_path)
    if "stop_block(" not in stop_text:
        replace_exact(
            stop_path,
            "from _common import payload_cwd, read_payload, turn_rows",
            "from _common import emit_context, payload_cwd, read_payload, stop_block, turn_rows",
            label="stop_gate_import",
        )
        replace_exact(
            stop_path,
            "def _chan_chua_xong(cwd, state):",
            "def _chan_chua_xong(cwd, state, payload=None):",
            label="stop_gate_chan_sig",
        )
        replace_exact(
            stop_path,
            '    print(json.dumps({"decision": "block", "reason": reason, "stop_hook_active": False},\n'
            '                     ensure_ascii=False))',
            '    stop_block(cwd, payload or {}, reason, code="TDQ:UNFINISHED")',
            label="stop_gate_unfinished_block",
        )
        replace_exact(
            stop_path,
            "    if lap_lai and _chan_chua_xong(cwd, state):",
            "    if lap_lai and _chan_chua_xong(cwd, state, payload):",
            label="stop_gate_call_1",
        )
        replace_exact(
            stop_path,
            '    if culprit and not logged:\n'
            '        # §6: a block decision has to be traceable — a wrong block must name its source at once.\n'
            '        _info(f"stop_gate: block TDQ:LOG · source={source} · path={culprit}")\n'
            '        print(json.dumps({\n'
            '            "decision": "block",\n'
            '            # The wording must fit 300 chars even when the path hits MAX_PATH_CHARS.\n'
            '            "reason": (f"[TDQ:LOG] Repo changed ({culprit}), {log_rel} not appended. "\n'
            '                       "Run `tdq_finish.py --files <file> --log \\"<summary>\\"`, no hand Edit. "\n'
            '                       "Then reprint the last chat block VERBATIM (question + options + "\n'
            '                       "the ➤ line), no summarising."),\n'
            '        }, ensure_ascii=False))\n'
            '        return',
            '    if culprit and not logged:\n'
            '        # §6: a block decision has to be traceable — a wrong block must name its source at once.\n'
            '        _info(f"stop_gate: block TDQ:LOG · source={source} · path={culprit}")\n'
            '        reason = (f"[TDQ:LOG] Repo changed ({culprit}), {log_rel} not appended. "\n'
            '                  "Run `tdq_finish.py --files <file> --log \\"<summary>\\"`, no hand Edit. "\n'
            '                  "Then reprint the last chat block VERBATIM (question + options + "\n'
            '                  "the ➤ line), no summarising.")\n'
            '        stop_block(cwd, payload, reason, code="TDQ:LOG")\n'
            '        return',
            label="stop_gate_log_block",
        )
        replace_exact(
            stop_path,
            '            print(json.dumps({\n'
            '                "decision": "block",\n'
            '                "reason": ("[TDQ:TICK] This turn edited code but the plan checkboxes did not change. "\n'
            '                           "Open the plan, mark [~] the task in progress and [x] the ones done (task by task). "\n'
            '                           "Then reprint the last chat block VERBATIM — no summarising."),\n'
            '            }, ensure_ascii=False))',
            '            stop_block(cwd, payload, ("[TDQ:TICK] This turn edited code but the plan checkboxes did not change. "\n'
            '                                      "Open the plan, mark [~] the task in progress and [x] the ones done (task by task). "\n'
            '                                      "Then reprint the last chat block VERBATIM — no summarising."), code="TDQ:TICK")',
            label="stop_gate_tick_block",
        )
        replace_exact(
            stop_path,
            "    if _chan_chua_xong(cwd, state):",
            "    if _chan_chua_xong(cwd, state, payload):",
            label="stop_gate_call_2",
        )

    # Patch session_start.py -> emit via emit_context on Antigravity instead of raw stdout
    ss_path = hooks_scripts_dir / "session_start.py"
    ss_text = read_utf8(ss_path)
    if "emit_context(" not in ss_text:
        ss_text = ss_text.replace(
            "from _common import (",
            "from _common import (\n    emit_context,",
            1,
        )
        ss_text = ss_text.replace("    print(rewritten)", "    emit_context([rewritten])", 1)
        write_utf8(ss_path, ss_text)

    # Patch read_gate.py -> queue reminder via _common.remind_force on AGY instead of raw hookSpecificOutput
    rg_path = hooks_scripts_dir / "read_gate.py"
    rg_text = read_utf8(rg_path)
    if "_RUNTIME_STATE" not in rg_text:
        old_rg_tail = (
            '    print(_common.json.dumps({\n'
            '        "hookSpecificOutput": {\n'
            '            "hookEventName": "PreToolUse",\n'
            '            "permissionDecision": "allow",\n'
            '            "permissionDecisionReason": "TDQ: a reminder, not a block.",\n'
            '            "additionalContext": _common.trim(_tao_thong_diep(ten, kb, dau, cuoi, lap_count)),\n'
            '        }\n'
            '    }, ensure_ascii=False))'
        )
        new_rg_tail = (
            '    if _common._RUNTIME_STATE.get("is_agy"):\n'
            '        _common.remind_force(cwd, payload, "READ", _tao_thong_diep(ten, kb, dau, cuoi, lap_count))\n'
            '    else:\n'
            '        print(_common.json.dumps({\n'
            '            "hookSpecificOutput": {\n'
            '                "hookEventName": "PreToolUse",\n'
            '                "permissionDecision": "allow",\n'
            '                "permissionDecisionReason": "TDQ: a reminder, not a block.",\n'
            '                "additionalContext": _common.trim(_tao_thong_diep(ten, kb, dau, cuoi, lap_count)),\n'
            '            }\n'
            '        }, ensure_ascii=False))'
        )
        replace_exact(rg_path, old_rg_tail, new_rg_tail, label="read_gate_agy_remind")
