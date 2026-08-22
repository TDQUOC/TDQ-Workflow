#!/usr/bin/env python3
"""Stop — match reminders against the REAL effects, at end of turn.

The single data source is the turn ledger docs/tdq/.tdq-turn.jsonl (written by the 2
PreToolUse hooks). This hook does NOT read the transcript and does NOT trust an echo
line the model printed — 0.1.8 read the transcript and blocked valid turns because the
transcript lagged, and a weak model can print a fake echo anyway.

The single BLOCK point: the repo changed while today's working log was never updated.
Every other code is only repeated through additionalContext.
Ceiling: ≤4 lines / 300 chars (spec §2.7). `stop_hook_active` → absolute silence.

0.3.1 — the turn ledger only sees actions going through the Edit/Write tools, so changes
made through the shell are invisible to it: it both blocked wrongly (a log appended with
`cat >>`) and let things through (a repo edited with `sed -i`). So the hook also checks
the DISK: the `turn_start` snapshot written by prompt_context at the start of the turn,
against the current state. No snapshot (the turn did not open with a user prompt, the
project is not a git repo) → it falls back to exactly the old behaviour.
"""
import json
import os

from _common import payload_cwd, read_payload, turn_rows
# Keep this AFTER `from _common`: `_common` is what injects `scripts/` into sys.path. Use a
# from-import (not module attribute access) so graphify can emit the cross-file `calls` edge.
from tdq_state import (BOOKKEEPING_PATHS, _info, _warn,  # noqa: E402
                       cong_dang_cho, dod_tick_state, effective_phase, load,
                       plan_tick_state, qc_result_state, task_open_count,
                       repo_status_digest, repo_status_paths, sha256_file,
                       today_log_rel)

MAX_LINES = 4
MAX_CHARS = 300
MAX_PATH_CHARS = 60

# Second safety net for the bookkeeping area: `repo_status_paths` already excludes it with a
# git pathspec, this is only the backstop for a git old enough not to understand
# `:(top,exclude)`. It uses tdq_state's own list so the decision and the naming can never
# drift apart (that drift is exactly the wrong block of 0.3.1), and matches on `/` because
# git prints paths with `/`.
BOOKKEEPING = tuple(p + "/" for p in BOOKKEEPING_PATHS)

# code → (the event proving it was done, the line to repeat if missing)
EFFECTS = {
    "TDQ:NEXT": ("next_run", "`tdq_state.py next` not run yet — run it to see the next step."),
    "TDQ:STATE": ("state_cli", "state not written through the CLI — use `tdq_state.py set|approve`."),
}


def _snapshot(rows):
    """The start-of-turn snapshot — take the NEWEST row.

    Normally there is one row per turn (turn_log_clear wipes the ledger at turn start). If
    that wipe was missed, the leftover row belongs to the previous turn: taking it as the
    baseline means comparing against a state up to 6 hours old → the previous turn's changes
    get blamed on this one.
    """
    found = None
    for row in rows:
        if row.get("kind") == "turn_start":
            found = row
    return found


def _sha(path):
    try:
        return sha256_file(path)
    except OSError:
        return None


def _log_changed(cwd, snap):
    """Did today's log change since the start of the turn (however it was written)?"""
    log_rel = today_log_rel()
    now = _sha(os.path.join(cwd, log_rel))
    if now is None:
        return False
    before = snap.get("log_sha")
    if snap.get("log_rel") != log_rel:
        return True                      # turn straddling midnight: the new day's file exists
    if before is None:
        return True                      # no file at turn start, there is one now
    return isinstance(before, str) and now != before


def _repo_changed(cwd, snap):
    before = snap.get("repo_sha")
    if not isinstance(before, str):
        return False                     # not a git repo / could not be read
    now = repo_status_digest(cwd)
    if not isinstance(now, str):
        # The fingerprint was readable at turn start but not at turn end → something is truly broken.
        _warn("stop_gate: could not read the repo fingerprint at turn end — "
              "dropping the disk evidence, falling back to the turn ledger alone")
        return False
    return now != before


def _shell_changed_path(cwd, snap):
    """The file name to quote in the block message — a file new in this turn wins.

    Empty string = the changes are workflow bookkeeping only → not counted as a repo change.
    """
    before = snap.get("repo_paths")
    before = set(before) if isinstance(before, list) else set()
    fresh, known = "", ""
    for path in repo_status_paths(cwd):
        if not isinstance(path, str) or path.startswith(BOOKKEEPING):
            continue
        if path not in before:
            fresh = fresh or path
        else:
            known = known or path
    return (fresh or known)[:MAX_PATH_CHARS]


def _dod_hint(cwd, state):
    """[TDQ:DOD] — a REMINDER, never a block: the books are being closed while checkboxes
    are still open.

    QC signing off on every item while the Definition of Done boxes stay `[ ]` is pure
    bookkeeping slippage, so a reminder is the right strength — the work IS done, only the
    record is not. Four conditions must all hold, and each one exists to keep a hook that
    runs at user scope from nagging a project it knows nothing about:

    1. phase `report` or `idle` — that is close-out; earlier, open boxes are normal.
    2. the DoD section actually uses checkboxes — a plan written the older way (plain
       bullets) counts 0 and must never be nagged.
    3. a box is still open.
    4. the qc file exists, holds at least one PASS and no FAIL — proof QC really ran and
       really passed, which is what makes an open box a slip rather than honest state.
    """
    if effective_phase(state, warn=False) not in ("report", "idle"):
        return []
    dod = dod_tick_state(cwd)
    if not dod["exists"] or dod["total"] == 0 or dod["all_done"]:
        return []
    qc = qc_result_state(cwd)
    if not qc["exists"] or not qc["all_pass"]:
        return []
    task_con = task_open_count(cwd)
    dod_con = dod["total"] - dod["done"]
    _info(f"stop_gate: hint TDQ:DOD · dod={dod['done']}/{dod['total']} "
          f"· task open={task_con} · qc={qc['passed']} PASS/{qc['failed']} FAIL "
          f"· plan={dod['path']}")
    return [f"[TDQ:DOD] Closing the books with boxes still open: {task_con} task(s), "
            f"{dod_con} DoD line(s). QC passed — tick them in the plan."]


def main():
    payload = read_payload()
    if payload.get("stop_hook_active"):
        return
    cwd = payload_cwd(payload)
    state = load(cwd)
    if state is None or not state.get("active_request"):
        return

    rows = turn_rows(cwd, payload)
    log_rel = today_log_rel()
    log_dir = os.path.join("docs", "workinglog")
    snap = _snapshot(rows)

    edited = [r.get("path", "") for r in rows
              if r.get("kind") == "observe" and r.get("event") == "edit"
              and not str(r.get("path", "")).startswith(log_dir)]
    logged = any(r.get("kind") == "observe" and r.get("event") == "log_written" for r in rows)

    # Second piece of evidence, independent of the tool name: the real effect on disk.
    # Truncate the path here, not only in _shell_changed_path: a path read off the turn ledger
    # also goes straight into `reason`, and a long path pushes the block past 300 chars.
    culprit = edited[0][:MAX_PATH_CHARS] if edited else ""
    source = "turn ledger" if culprit else "—"
    if snap:
        if not logged:
            logged = _log_changed(cwd, snap)
        if not culprit and _repo_changed(cwd, snap):
            culprit = _shell_changed_path(cwd, snap)
            source = "repo fingerprint"

    if culprit and not logged:
        # §6: a block decision has to be traceable — a wrong block must name its source at once.
        _info(f"stop_gate: block TDQ:LOG · source={source} · path={culprit}")
        print(json.dumps({
            "decision": "block",
            # The wording must fit 300 chars even when the path hits MAX_PATH_CHARS.
            "reason": (f"[TDQ:LOG] Repo changed ({culprit}), {log_rel} not appended. "
                       "Run `tdq_finish.py --files <file> --log \"<summary>\"`, no hand Edit. "
                       "Then reprint the last chat block VERBATIM (question + options + "
                       "the ➤ line), no summarising."),
        }, ensure_ascii=False))
        return

    # Second block point: code changed during the turn while the plan checkboxes stood still.
    # A bulk tick at end of turn makes progress jump 0/N → N/N, and worse: the ETA loses its
    # whole per-task rhythm sample, because a mark is only recorded when progress CHANGES.
    # Blocked here, not at PreToolUse — editing code freely inside the turn is fine, only
    # ending the turn is not. Every silent branch here exists to avoid a wrong block: this
    # hook runs at user scope.
    if culprit and snap and isinstance(snap.get("plan_sha"), str) \
            and effective_phase(state, warn=False) in ("implement", "qc"):
        tick = plan_tick_state(cwd)
        if tick["exists"] and tick["total"] > 0 and not tick["all_done"] \
                and tick["sha"] == snap["plan_sha"]:
            _info(f"stop_gate: block TDQ:TICK · source={source} · path={culprit} "
                  f"· plan={tick['path']} · checkboxes unchanged during the turn")
            print(json.dumps({
                "decision": "block",
                "reason": ("[TDQ:TICK] This turn edited code but the plan checkboxes did not change. "
                           "Open the plan, mark [~] the task in progress and [x] the ones done (task by task). "
                           "Then reprint the last chat block VERBATIM — no summarising."),
            }, ensure_ascii=False))
            return

    reminded = {r.get("code") for r in rows if r.get("kind") == "remind"}
    done = {r.get("event") for r in rows if r.get("kind") == "observe"}
    hints = []
    for code, (event, message) in EFFECTS.items():
        if code in reminded and event not in done:
            hints.append(f"[{code}] {message}")
    if "TDQ:APPROVE" in reminded:
        # The same function `edit_gate` uses: the gate must be computed per LANE. A hard-coded
        # list here made lane quick permanently nagged with "spec not approved" — that gate
        # does not even exist in that lane.
        target = cong_dang_cho(state)
        if target:
            hints.append(f"[TDQ:APPROVE] {target} still has no recorded approval — "
                         "if the user approved, run `tdq_state.py approve`; if unclear, ASK.")
    if "TDQ:GIT" in reminded:
        hints.append("[TDQ:GIT] Re-check the branch name / commit message against the convention before moving on.")
    # Front of the queue, not the back: `hints` is cut to MAX_LINES, and with four other
    # reminders already standing the close-out warning would be the one silently dropped —
    # exactly the turn it is needed, since closing the books IS the last turn.
    hints[:0] = _dod_hint(cwd, state)

    if not hints:
        return
    text = "\n".join(hints[:MAX_LINES])
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS - 1].rstrip() + "…"
    print(json.dumps({
        "hookSpecificOutput": {"hookEventName": "Stop", "additionalContext": text}
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
