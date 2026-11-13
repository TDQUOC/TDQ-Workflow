#!/usr/bin/env python3
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
