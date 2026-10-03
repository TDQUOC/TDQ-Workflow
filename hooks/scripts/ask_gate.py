#!/usr/bin/env python3
"""PreToolUse on `AskUserQuestion` — remind, never block, when the run asks the user mid-way.

Why this hook exists (request 2026-10-03-0732): an excalidraw run stopped in the middle of phase
`implement` to ask whether the installer threshold could go from 200 to 250 MB. It stopped with
`AskUserQuestion` INSIDE the turn — not by ending the turn — so the Stop gate
(`stop_gate.py`, `[TDQ:UNFINISHED]`) never saw it. The rule it broke: an unreachable spec
threshold is not a stop; apply the fallback, `lech add`, carry on, and ask in the report.

It REMINDS and never blocks — the user's choice (2026-10-03). The agent may still ask, e.g. for
one of the four force-majeure kinds, which it should declare with `pause --loai` first. Silent
when: the phase is not `implement`/`qc`, or a pause is already declared.

Env: TDQ_PROJECT_DIR anchors the project; TDQ_LOG=0 silences the log.
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common  # noqa: E402 — also puts `scripts/` on sys.path for tdq_state
from tdq_state import LOAI_DUNG, effective_phase, load, log_enabled  # noqa: E402

MA = "TDQ:ASK"
PHASE_NHAC = ("implement", "qc")


def _log(message):
    """Log service: ISO timestamp on stderr, on by default, muted by TDQ_LOG=0."""
    if log_enabled():
        print(f"[{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}] ask_gate: {message}",
              file=sys.stderr)


def can_nhac(state, phase):
    """True when a mid-run question deserves the reminder. Pure, for the tests."""
    return phase in PHASE_NHAC and not state.get("implement_pause")


def main():
    try:
        payload = _common.read_payload()
        cwd = _common.payload_cwd(payload)
        state = load(cwd)
    except Exception as loi:  # noqa: BLE001 — a reminder hook must never break the question
        _log(f"cannot read state ({loi}) — silent")
        sys.exit(0)
    phase = effective_phase(state, warn=False) if isinstance(state, dict) else None
    nhac = phase is not None and can_nhac(state, phase)
    _log(f"phase={phase} · {'remind' if nhac else 'silent'}")
    if not nhac:
        sys.exit(0)
    # `decide=False`: an "allow" from a hook may answer the permission question for the tool,
    # and for AskUserQuestion the tool IS the question to the user — add context, decide nothing.
    # Kept under the 200-character reminder cap so `trim` never cuts the second line.
    _common.remind(cwd, payload, MA, [
        "An unmet spec threshold is no reason to ask: apply the §6 fallback, `lech add`, carry on.",
        f"Ask only for {' · '.join(LOAI_DUNG)}, after `pause --loai`.",
    ], decide=False)


if __name__ == "__main__":
    main()
