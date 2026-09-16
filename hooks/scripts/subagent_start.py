#!/usr/bin/env python3
"""SubagentStart — put the lean law in front of a sub-agent before it writes anything.

This channel is a REMINDER, NOT A FENCE, and the difference matters when reading its output:
issue #23885 measured `additionalContext` on a sub-agent being pruned, with 40–60%
non-compliance. So the law landing here buys a better chance, never a guarantee — the things
that actually hold the line are the `edit_gate` PreToolUse gate and the leader's own audit.
Fail-open by construction: any missing payload key, unreadable state or unreadable law file
prints nothing and still exits 0. A hook that blocks a sub-agent's turn costs the whole run;
a silent skip costs one reminder.
Skipped entirely at `muc_gat=off`. Injected once per turn through the shared turn ledger
(bug #10871 runs a plugin hook twice with two PIDs).
"""
import os

from _common import (already_reminded, payload_cwd, read_payload, session_id,
                     turn_log_append)
# Placed AFTER `from _common`: `_common` itself injects `scripts/` into sys.path. The
# from-import shape (not a module attribute call) is what lets graphify emit a cross-file
# `calls` edge.
from luat_gon import doc_than_luat, loc_than_luat  # noqa: E402
from tdq_state import load, muc_gat_hieu_luc  # noqa: E402

MA_GON = "TDQ:GON"
# The law lives in the PLUGIN, not in the project the sub-agent runs in.
GOC_LUAT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    payload = read_payload()
    cwd = payload_cwd(payload)
    state = load(cwd) or {}
    muc = muc_gat_hieu_luc(state)
    if muc == "off":
        return
    than = loc_than_luat(doc_than_luat(GOC_LUAT), muc)
    if not than or already_reminded(cwd, payload, MA_GON):
        return
    turn_log_append(cwd, "remind", session=session_id(payload), code=MA_GON,
                    event="SubagentStart", muc_gat=muc,
                    agent=str(payload.get("agent_type") or ""))
    print(f"[{MA_GON}] The build-less-than-asked law (muc_gat={muc}) — climb this ladder "
          f"before you create anything:\n{than}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Fail-open, deliberately swallowing everything: see the module docstring. A traceback
        # on stderr would still exit 0, but it would land in the sub-agent's log as noise.
        pass
