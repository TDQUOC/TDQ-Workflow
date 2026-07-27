#!/usr/bin/env python3
"""SessionStart: inject a tiny state summary (≤3 lines) + graphify availability.

Silent (no output) when the project has no active TDQ request.
"""
import shutil

from _common import read_payload, payload_cwd, tdq_state, APPROVE_CMD


def _mark(approved, registered):
    if approved:
        return "✔"
    return "⏳ chờ duyệt" if registered else "—"


def main():
    payload = read_payload()
    cwd = payload_cwd(payload)
    state = tdq_state.load(cwd)
    if state is None or not state.get("active_request"):
        return

    lines = []
    lane = state.get("lane")
    if lane == "quick":
        quick = "✔" if state.get("quick_approved") else "⏳ chờ duyệt"
        lines.append(f"[TDQ] Request '{state['active_request']}' · lane quick · duyệt quick: {quick}")
    else:
        lines.append(
            f"[TDQ] Request '{state['active_request']}' · lane {lane or '?'} · phase {state.get('phase')} · "
            f"spec {_mark(state.get('spec_approved'), state.get('spec_file'))} · "
            f"plan {_mark(state.get('plan_approved'), state.get('plan_file'))}"
        )

    pending = None
    if lane == "full" and state.get("spec_file") and not state.get("spec_approved"):
        pending = "spec"
    elif lane == "full" and state.get("spec_approved") and state.get("plan_file") and not state.get("plan_approved"):
        pending = "plan"
    elif lane == "quick" and not state.get("quick_approved"):
        pending = "quick"
    if pending:
        lines.append(f"[TDQ] Đang chờ duyệt {pending} — user gõ: {APPROVE_CMD} {pending}")

    if shutil.which("graphify") is None:
        lines.append("[TDQ] graphify chưa cài (tùy chọn): uv tool install graphifyy")

    print("\n".join(lines[:3]))


if __name__ == "__main__":
    main()
