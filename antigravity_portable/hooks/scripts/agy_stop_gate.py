#!/usr/bin/env python3
"""Stop (Antigravity/agy) — force the loop to keep going while real work is unfinished.

Unlike Claude Code's Stop (`hooks/scripts/stop_gate.py`), which returns `decision: "block"`
consumed by a harness that already tracks a per-turn ledger written by 2 PreToolUse hooks plus
a `turn_start` disk snapshot from a THIRD hook (`prompt_context.py`, UserPromptSubmit) — agy's
`decision: "continue"` forces the loop onward, and this bundle declares only 2 agy hook events
(PreToolUse, Stop), no UserPromptSubmit. So there is no turn-ledger and no turn-start snapshot
to compare against here. Instead this hook keeps its OWN "since the previous Stop" snapshot on
disk (`docs/tdq/.agy-stop-snapshot.json`) and compares the current call against it — the same
disk-fingerprint idea as `stop_gate.py`'s `_snapshot`/`_log_changed`/`_repo_changed`, just with
the baseline written by this hook itself instead of a separate turn-start hook.

Ports exactly 3 conditions from `stop_gate.py`, in the same priority order:
  1. TDQ:LOG    — the repo changed since the last Stop, but today's working log did not.
  2. TDQ:TICK   — the repo changed since the last Stop, but the plan's checkboxes did not.
  3. TDQ:UNFINISHED — phase is still `implement` and the plan has an open task (independent of
     whether the repo changed this cycle — ported verbatim from `unfinished_reason`, pure).
A block prints `{"decision": "continue", "reason": "[TDQ:<code>] ..."}`. `MAX_STREAK` (=3,
ported from `_streak_bump`/`_chan_chua_xong`) steps a run down to silence once the SAME plan
content has blocked that many times in a row with no checkbox movement — otherwise a session
that is genuinely stuck has no way to ever end its turn. Nothing open, or no active request →
silent (no `decision` key at all).

Google publishes no official Stop payload schema (checked 2026-09-03; the event list in
docs/tdq/brief/2026-09-03-1440-kiem-tuong-thich-3-host.md source N5 is third-party) — `_cwd_of`
tries several plausible field names for the working directory and falls back to `os.getcwd()`;
this hook never raises on an unexpected payload shape.
"""
import json
import os
import sys

_SCRIPTS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts")
)
sys.path.insert(0, _SCRIPTS_DIR)

from tdq_state import (  # noqa: E402
    effective_phase, load, log_enabled, now_iso, plan_tick_state, repo_status_digest,
    repo_status_paths, sha256_file, today_log_rel,
)

MAX_STREAK = 3
SNAPSHOT_REL = os.path.join("docs", "tdq", ".agy-stop-snapshot.json")
STREAK_REL = os.path.join("docs", "tdq", ".agy-stop-streak.json")
MAX_PATH_CHARS = 60

# `repo_status_digest`/`repo_status_paths` already exclude this zone via a git pathspec, so a
# write to the snapshot/streak files above never counts as "the repo changed" and can never
# feed back into its own next comparison.
BOOKKEEPING = ("docs/tdq/", "docs/workinglog/", "graphify-out/")

_CWD_KEYS = ("cwd", "workingDirectory", "working_directory", "workspace_root",
             "project_root", "root")


def _cwd_of(payload):
    if isinstance(payload, dict):
        for key in _CWD_KEYS:
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value
    return os.getcwd()


def _sha(path):
    try:
        return sha256_file(path)
    except OSError:
        return None


def _read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _write_json(path, data):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except OSError:
        pass  # losing the baseline degrades to "no prior snapshot", never a crash


def _current_snapshot(cwd):
    log_rel = today_log_rel()
    return {
        "log_rel": log_rel,
        "log_sha": _sha(os.path.join(cwd, log_rel)),
        "repo_sha": repo_status_digest(cwd),
        "repo_paths": repo_status_paths(cwd),
        "plan_sha": plan_tick_state(cwd).get("sha", ""),
    }


def _log_changed(now, snap):
    if now["log_rel"] != snap.get("log_rel"):
        return True  # straddling midnight: a new day's file exists that snap never saw
    before = snap.get("log_sha")
    if before is None:
        return now["log_sha"] is not None
    return now["log_sha"] != before


def _shell_changed_path(snap):
    """The path to quote — a path new since the baseline wins over one already known."""
    before = set(snap.get("repo_paths") or [])
    fresh, known = "", ""
    for path in snap.get("_now_paths") or []:
        if not isinstance(path, str) or path.startswith(BOOKKEEPING):
            continue
        if path not in before:
            fresh = fresh or path
        else:
            known = known or path
    return (fresh or known)[:MAX_PATH_CHARS]


def _repo_changed(now, snap):
    before = snap.get("repo_sha")
    if not isinstance(before, str) or not isinstance(now["repo_sha"], str):
        return False  # not a git repo, or unreadable — no evidence either way
    return now["repo_sha"] != before


def unfinished_reason(state, tick):
    """Ported verbatim (pure) from `hooks/scripts/stop_gate.py::unfinished_reason`."""
    if not isinstance(state, dict) or effective_phase(state, warn=False) != "implement":
        return None
    if not tick.get("exists") or tick.get("total", 0) <= 0 or tick.get("all_done"):
        return None
    if tick.get("dispatched_count", 0) > 0:
        return None
    if state.get("implement_pause"):
        return None
    con_ho = tick.get("total", 0)
    return (f"[TDQ:UNFINISHED] The plan still has {con_ho} open task(s) and the phase is still "
            "implement. Keep going to the end of the plan in this turn: mark [~], do the task, "
            "mark [x]. Genuinely blocked → run `tdq_state.py pause --ly-do \"<why>\"` and "
            "tell the user why.")


def _streak_bump(cwd, sha):
    path = os.path.join(cwd, STREAK_REL)
    saved = _read_json(path) or {}
    count = int(saved.get("count", 0)) if saved.get("sha") == sha else 0
    count += 1
    _write_json(path, {"sha": sha, "count": count})
    return count


def _continue(reason):
    """Force the loop onward, and say on stderr which of the 3 cases matched (TDQ_LOG=0 mutes)."""
    if log_enabled():
        print(f"[{now_iso()}] ℹ️ agy Stop continue — {reason}", file=sys.stderr)
    print(json.dumps({"decision": "continue", "reason": reason}, ensure_ascii=False))


def main():
    try:
        payload = json.load(sys.stdin)
    except (ValueError, UnicodeDecodeError):
        payload = {}
    cwd = _cwd_of(payload)
    state = load(cwd)
    if not isinstance(state, dict) or not state.get("active_request"):
        return

    now = _current_snapshot(cwd)
    now["_now_paths"] = repo_status_paths(cwd)
    snap_path = os.path.join(cwd, SNAPSHOT_REL)
    snap = _read_json(snap_path)
    tick = plan_tick_state(cwd)

    reason = None
    if snap is not None:
        changed = _repo_changed(now, snap)
        culprit = _shell_changed_path(snap) if changed else ""
        if culprit and not _log_changed(now, snap):
            log_rel = now["log_rel"]
            reason = (f"[TDQ:LOG] Repo changed ({culprit}), {log_rel} not appended. "
                      "Run `tdq_finish.py --files <file> --log \"<summary>\"`, no hand edit.")
        elif culprit and effective_phase(state, warn=False) in ("implement", "qc") \
                and tick.get("exists") and tick.get("total", 0) > 0 and not tick.get("all_done") \
                and tick.get("sha") == snap.get("plan_sha"):
            reason = ("[TDQ:TICK] This turn edited code but the plan checkboxes did not change. "
                      "Open the plan, mark [~] the task in progress and [x] the ones done.")

    if reason is None:
        reason = unfinished_reason(state, tick)

    _write_json(snap_path, {k: v for k, v in now.items() if k != "_now_paths"})

    if reason is None:
        return

    streak = _streak_bump(cwd, tick.get("sha", ""))
    if streak > MAX_STREAK:
        return  # stuck for MAX_STREAK stops straight — stepping down beats trapping the run
    _continue(reason)


if __name__ == "__main__":
    main()
