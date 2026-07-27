"""Shared helpers for TDQ hook scripts (stdlib only)."""
import json
import os
import sys

_SCRIPTS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts")
)
sys.path.insert(0, _SCRIPTS_DIR)
import tdq_state  # noqa: E402

APPROVE_CMD = "/tdq-workflow:tdq-approve"


def read_payload():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def payload_cwd(payload):
    return payload.get("cwd") or os.getcwd()


def deny(reason):
    """Emit a PreToolUse deny decision and exit 0."""
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }, ensure_ascii=False))
    sys.exit(0)


def approve_hint(target):
    return f"➤ Để duyệt: gõ `{APPROVE_CMD} {target}` · Góp ý: nhắn trực tiếp"
