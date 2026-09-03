#!/usr/bin/env python3
"""PreToolUse (Edit|Write|MultiEdit|NotebookEdit) — observe + remind; blocks exactly 1 case.

Only `TDQ:TICK` denies: editing source code during implement/qc while the plan carries no
task marked `[~]`. Every other code only reminds.

Two jobs, in this order:
1. Write `observe` rows into the turn ledger: `edit:<path>` for every file edit,
   `log_written` when that file is today's working log. This is the evidence `stop_gate`
   uses at end of turn — no transcript, no self-reporting by the model.
2. Emit a reminder code when needed: TDQ:STATE (about to hand-edit state), TDQ:APPROVE
   (editing code while the lane gate is unapproved), TDQ:LOG (repo changed but today's
   log is missing).
"""
import os

from _common import (block, echo_line, observe, payload_cwd, read_payload, remind,
                     turn_rows)
# Keep this AFTER `from _common`: `_common` is what injects `scripts/` into sys.path. Use a
# from-import (not module attribute access) so graphify can emit the cross-file `calls` edge.
# `today_log_rel` comes straight from tdq_state — one single source, shared with stop_gate.
from tdq_state import (cong_dang_cho, effective_phase, load,  # noqa: E402
                       plan_tick_state, state_md_path, state_path,
                       today_log_rel)

# Streak threshold (spec 2026-08-13-ra-soat-tick-che-do-sau §3): more than THRESHOLD source
# edits in a row without the plan (checksum) changing since → block the next one. Matches the
# "fix round" ceiling (3 rounds) already used across the system.
STREAK_NGUONG = 3


def within(child, parent):
    return child == parent or child.startswith(parent + os.sep)


def main():
    payload = read_payload()
    tool_input = payload.get("tool_input") or {}
    target = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not target or not isinstance(target, str):
        return
    cwd = payload_cwd(payload)
    abs_target = os.path.realpath(target if os.path.isabs(target) else os.path.join(cwd, target))
    try:
        rel_target = os.path.relpath(abs_target, os.path.realpath(cwd))
    except ValueError:
        rel_target = abs_target

    log_rel = today_log_rel()
    log_dir = os.path.realpath(os.path.join(cwd, "docs", "workinglog"))
    is_log = within(abs_target, log_dir)

    # (1) observe — always written, even when no request is open
    observe(cwd, payload, "edit", path=rel_target)
    if is_log:
        observe(cwd, payload, "log_written", path=rel_target)

    # (2) remind
    state_file = os.path.realpath(state_path(cwd))
    state_md = os.path.realpath(state_md_path(cwd))
    if abs_target in (state_file, state_md):
        remind(cwd, payload, "TDQ:STATE", [
            "Do not hand-edit the state file — write it through the CLI.",
            "How: python3 scripts/tdq_state.py set <key>=<value> (or approve/init/reset).",
            echo_line("TDQ:STATE", "wrote state through the CLI"),
        ])

    state = load(cwd)
    if state is None or not state.get("active_request"):
        return
    if within(abs_target, os.path.realpath(os.path.join(cwd, "docs"))):
        return  # docs/** needs no reminder: brief/spec/plan/research/log

    # The gate-picking rule lives in `tdq_state.cong_dang_cho` — shared with `stop_gate`.
    # Copying the rule into both hooks is an open invitation for the two to drift: that exact
    # drift is what made stop_gate nag lane quick wrongly for quite a while.
    pending = cong_dang_cho(state)
    if pending:
        # Name both the machine value and the label the user sees at the mode gate — both accepted.
        mode = " --mode <main|inline | subagent|sub-agent>" if pending == "plan" else ""
        # Command before advice: the 200-char ceiling must cut the least needed part.
        remind(cwd, payload, "TDQ:APPROVE", [
            f"Editing a file outside docs/ while {pending} has no recorded approval.",
            f"User approved → python3 scripts/tdq_state.py approve {pending}{mode} "
            f"--by \"<the user's words>\".",
            f"Not approved yet → present the {pending} and ask for approval.",
        ])

    # repo changed → remind about the working log now, do not save it up for Stop
    if not os.path.isfile(os.path.join(cwd, log_rel)):
        remind(cwd, payload, "TDQ:LOG", [
            f"This turn changed the repo — append an entry to {log_rel} before the turn ends.",
            "How: open the file, add a \"## HH:MM — <what>\" item at the END of the file.",
            echo_line("TDQ:LOG", f"appended {log_rel}"),
        ])

    # File OUTSIDE the state's project (a sub-agent building a scratch repo, a sandbox, an
    # outside tool) → the plan in state says nothing about that file, so blocking on the tick
    # mark blocks the wrong thing. Measured in the team-mode smoke test: the sub-agent had to
    # sneak through the shell to write at all.
    # This only drops the BLOCK (both TDQ:TEAM and TDQ:TICK) — observing and reminding still run.
    trong_project = within(abs_target, os.path.realpath(cwd))
    if not trong_project:
        # Written to the turn ledger instead of printed: this is a fact for later debugging,
        # not a reminder for the model.
        observe(cwd, payload, "bo_qua_chan_ngoai_project", path=abs_target)

    # (2b) team mode: the user picked "hand it to assistants" and the leader types the code of
    # a task it promised to delegate → BLOCK. Without this fence the promise to split the work
    # is only words: the model still does everything on main and nobody can prove otherwise.
    from tdq_team import canh_bao_lach_luat  # noqa: E402 — imported only when truly needed
    # Same reason as `trong_project` above: the assignment map only speaks about file areas
    # INSIDE the project, so a file outside it is not under its authority.
    canh_bao = canh_bao_lach_luat(cwd, rel_target) if trong_project else None
    if canh_bao:
        if canh_bao["kieu"] == "ban-do-hong":  # i18n-allow
            block(cwd, payload, "TDQ:TEAM", [
                "The assignment map is unreadable — nobody can prove this task was delegated "
                "or done by the leader.",
                "Run: python3 scripts/tdq_team.py assign (regenerate), then audit.",
                "Editing code with a broken map is banned: that is exactly the loophole the map guards.",
            ])
        elif canh_bao["kieu"] == "chua-phan-cong":  # i18n-allow
            block(cwd, payload, "TDQ:TEAM", [
                "Team mode with no assignment map — you may not edit code on main first.",
                "Run: python3 scripts/tdq_team.py assign (then audit, then wave).",
                "A task the leader must do itself is recorded as tu_lam with one closed reason.",
            ])
        elif canh_bao["kieu"] == "da-giao-thieu-nhanh":  # i18n-allow
            block(cwd, payload, "TDQ:TEAM", [
                f"{canh_bao['ma']} carries the [>] mark but branch "
                f"{canh_bao['nhanh']} is missing — the sub-agent died midway or never ran.",
                f"Run: python3 scripts/tdq_team.py open {canh_bao['ma']}",
                "Or put the task back to [ ] and assign it again.",
            ])
        else:
            block(cwd, payload, "TDQ:TEAM", [
                f"This file belongs to the area of {canh_bao['ma']} — the map says GIAO to a "
                f"sub-agent, the leader does not edit it.",
                f"Run: python3 scripts/tdq_team.py open {canh_bao['ma']} then hand it to "
                f"agent tdq-implementer.",
                "Really have to do it yourself → change the map to tu_lam with one closed "
                "reason, then run audit.",
            ])

    # (2c) H1: `Chạm:` used to be a declaration nobody checked. A sub-agent writing from its
    # own worktree to a file outside its declared area is exactly how two agents of one wave
    # end up on the same file and only find out at merge time.
    from tdq_team import ngoai_vung_khai  # noqa: E402 — imported only when truly needed
    ngoai_vung = ngoai_vung_khai(cwd, abs_target)
    if ngoai_vung:
        block(cwd, payload, "TDQ:TEAM", [
            f"{ngoai_vung['duong']} is outside the file area {ngoai_vung['ma']} declared.",
            f"Task {ngoai_vung['ma']} may write in: {', '.join(ngoai_vung['vung_file'])}.",
            "Really need this file → report it to the leader so the task's `Chạm:` is widened "
            "and the waves are cut again; do not write it from here.",
        ])

    # in implement/qc while the plan marks no task as in progress → BLOCK.
    # stop_gate only compares the plan fingerprint at start/end of turn, so it cannot catch a
    # bulk-tick inside a single turn (lane quick does the whole thing in 1 turn) — the real
    # fence has to be here. `tests/**` is exempt: red→green means writing a red test before
    # there is anything to tick.
    # Placed LAST because `remind()` exits right after the first reminder: TDQ:LOG leads to a
    # hard block at Stop, so it must come first.
    in_tests = within(rel_target, "tests") or rel_target.startswith("tests" + os.sep)
    # Team mode: each sub-agent works in its own worktree under `.tdq-worktrees/`, but the turn
    # ledger is shared by the session — N agents running in parallel eat each other's streak
    # budget and the whole team freezes after exactly 3 edits. Tick discipline is the LEADER's
    # discipline in the main worktree; the red→green loop inside a sub-agent's worktree is not
    # the place to enforce it. Exempted by path, not by agent identity.
    in_worktree_doi = (os.sep + ".tdq-worktrees" + os.sep) in (abs_target + os.sep)
    if not in_tests and not in_worktree_doi and trong_project \
            and effective_phase(state, warn=False) in ("implement", "qc"):
        tick = plan_tick_state(cwd)
        if tick["exists"] and tick["total"] > 0 \
                and not tick["has_doing"] and not tick["all_done"]:
            block(cwd, payload, "TDQ:TICK", [
                "The plan carries no task marked [~] — mark the task in progress BEFORE editing code.",
                "Open the plan, switch the next task to [~]; flip it to [x] the moment it is green.",
                "Request already finished → tdq_state.py set phase=idle.",
            ])
        # several tasks marked [~] at once is equally a checkbox that no longer reflects what is
        # being done — close the old task ([x]) before opening a new one.
        if tick["exists"] and tick["doing_count"] > 1:
            block(cwd, payload, "TDQ:TICK", [
                "The plan has several tasks marked [~] — close the old one ([x]) before opening a new one.",
                "Open the plan, tick [x] the finished task, keep exactly 1 task [~] at a time.",
                "Request already finished → tdq_state.py set phase=idle.",
            ])
        # exactly 1 task [~] left standing forever dodges both blocks above: the agent ticks T1
        # once, keeps it while quietly editing many files, then bulk-ticks at end of turn.
        # Count the source edits in a row since the plan last changed (checksum) — past the
        # THRESHOLD it blocks, forcing the task closed before editing further.
        if tick["exists"] and tick["doing_count"] == 1:
            rows = turn_rows(cwd, payload)
            streak = sum(
                1 for r in rows
                if r.get("kind") == "observe" and r.get("event") == "code_edit"
                and r.get("plan_sha") == tick["sha"]
            )
            if streak >= STREAK_NGUONG:
                block(cwd, payload, "TDQ:TICK", [
                    f"{streak} edits in a row with no tick in the plan — close the task before editing on.",
                    "Test green → flip to [x] now; a different task → tick it before coding.",
                    "Request already finished → tdq_state.py set phase=idle.",
                ])
            observe(cwd, payload, "code_edit", path=rel_target, plan_sha=tick["sha"])


if __name__ == "__main__":
    main()
