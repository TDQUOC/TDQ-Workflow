#!/usr/bin/env python3
"""UserPromptSubmit — open a new turn.

Three jobs:
1. Wipe this session's turn ledger (the compliance-matching scope is one turn).
2. Emit TDQ:APPROVE when something waits for approval AND the prompt matches an approval
   sign (spec §2.9.2). Ambiguous → do not emit, and tell the agent to ASK rather than guess.
3. Emit TDQ:NEXT — exactly 1 line of `next --brief`.
4. Emit TDQ:WORKTREE while the worktree ledger still holds an open row.

Budget ceiling: ≤3 lines / 240 chars (spec §2.7). Silent when idle.
"""
import hashlib
import os
import re
import sys

from _common import (approve_hint, payload_cwd, plan_mode, read_payload,
                     session_id)
# Keep this AFTER `from _common`: `_common` is what injects `scripts/` into sys.path. Use a
# from-import (not module attribute access) so graphify can emit the cross-file `calls` edge.
from tdq_state import (effective_lane, effective_mode,  # noqa: E402
                       effective_phase, load, normalize_mode, phase_key,
                       prompt_context_last, prompt_context_save, render_next,
                       sha256_noi_dung, turn_log_append, turn_log_clear,
                       turn_snapshot)

MAX_LINES = 3
MAX_CHARS = 240

# An approval sign = (a) a word of agreement AND (b) the object waiting for approval.
AGREE = re.compile(r"\b(duyệt|duyet|ok|oke|okay|đồng\s*ý|dong\s*y|chốt|chot|"  # i18n-allow
                   r"approve[sd]?|approved|accept(?:ed)?|confirm(?:ed)?|agree[d]?|yes|yep|"
                   r"lgtm|go\s*ahead|proceed|ship\s*it|sounds\s*good|looks\s*good|"
                   r"làm\s*đi|lam\s*di|tiến\s*hành|tien\s*hanh)\b", re.IGNORECASE)  # i18n-allow
OBJECT = re.compile(r"\b(spec|plan|quick|mini-?plan)\b", re.IGNORECASE)
# Vietnamese/English aliases of lane quick. "nhanh" is a very common adjective in ordinary
# Vietnamese requests ("do it quickly for me"), so it only counts as an approval when it
# stands RIGHT AFTER the word of agreement — it does not share the path of OBJECT above, which only needs to appear anywhere
# in the sentence.
APPROVE_FAST = re.compile(
    r"\b(duyệt|duyet|chốt|chot|approve[sd]?|confirm|pick|choose)\s+"  # i18n-allow
    r"(chế\s*độ\s*nhanh|che\s*do\s*nhanh|nhanh|express|quick|fast)\b",  # i18n-allow
    re.IGNORECASE)
PRONOUN = re.compile(r"(cái\s*này|cai\s*nay|cái\s*đó|cai\s*do|cái\s*trên|cai\s*tren|"  # i18n-allow
                     r"\bthis\b|\bthat\b|\bthe\s+above\b)", re.IGNORECASE)
# A question — or a hedge — is not an approval, even when both components are present.
# The English half matters as much as the Vietnamese one: "ok but not yet" carries the word
# of agreement AND the object, so without this blocker it would read as a clean approval.
QUESTION = re.compile(
    r"(\?|\bchưa\b|\bchua\b|\bkhông\b\s*$|\bko\b\s*$"  # i18n-allow
    r"|\bnot\s+yet\b|\bnot\s+sure\b|\bnot\b|\bdon'?t\b|\bnope\b|\bno\b\s*$"
    r"|\bhold\s+on\b|\bwait\b|\bmaybe\b|\breject(?:ed)?\b|\bcancel\b)",
    re.IGNORECASE)
# Accepts both the old machine identifiers (main|subagent) and the labels the user reads at
# the mode gate (inline | sub-agent | sub agent), with an optional "implement" tail. The \b
# word boundaries stay so "mainline" and "inlineable" are not read as a mode answer.
MODE = re.compile(r"\b(main|inline|subagent|sub[\s-]?agent)\b(\s+implement)?",
                  re.IGNORECASE)
# Every gate template invites the user to answer with a letter, so a bare letter is a valid
# answer at all 4 gates. Accepted ONLY when it STANDS ALONE (an optional choose-prefix and a
# short tail are allowed): a full sentence such as "Approve? not sure" must miss.
# a-d, not just a-b: the option lists of the interview template run up to D.
LETTER = re.compile(
    r"^\s*(?:chọn\s+|chon\s+|choose\s+|option\s+|pick\s+|answer\s+)?"  # i18n-allow
    r"([a-d])\b\s*(?:nhé|nhe|đi|di|please|thanks|!|\.)?\s*$",  # i18n-allow
    re.IGNORECASE)
# At the 3 approval gates the recommendation always sits at option A (interview.md), so A —
# and only A — is the approving letter. b/c/d there answer some other question: they are not
# read as an approval, so the agent has to ASK instead of guessing.
APPROVE_LETTER = "a"


def looks_like_approval(prompt, target):
    if not prompt:
        return False
    if QUESTION.search(prompt):
        return False
    letter = LETTER.match(prompt)
    if target == "mode":
        # An answer at the mode gate is usually bare: "main", "subagent", "choose A".
        # No word of agreement is required — the plan is already approved, this only
        # picks how to run it. The mode gate offers exactly 2 options, so only a/b count.
        return bool(MODE.search(prompt)
                    or (letter and letter.group(1).lower() in ("a", "b")))
    if letter:
        return letter.group(1).lower() == APPROVE_LETTER
    if target == "quick" and APPROVE_FAST.search(prompt):
        return True
    if not AGREE.search(prompt):
        return False
    match = OBJECT.search(prompt)
    if match:
        said = match.group(1).lower().replace("-", "")
        return said == target or (target == "quick" and said in ("quick", "miniplan"))
    # With no object named, only an explicit pointing pronoun is accepted ("approve this").
    # "ok", "ok I get it" are NOT approvals — when it is ambiguous, let the agent ASK.
    return bool(PRONOUN.search(prompt))


def mode_from_answer(prompt, planned):
    """An answer at the mode gate -> the machine identifier, or None if unreadable.

    The mode name typed out beats the letter. A letter reads by the template: A is the mode the
    plan PROPOSED (always sitting at option A), B is the other one.
    """
    found = MODE.search(prompt or "")
    if found:
        said = normalize_mode(found.group(0))
        if said:
            return said
    letter = LETTER.match(prompt or "")
    if not letter or letter.group(1).lower() not in ("a", "b"):
        return None
    suggested = planned or "main"
    if letter.group(1).lower() == "a":
        return suggested
    return "subagent" if suggested == "main" else "main"


def _nhac_worktree(cwd):
    """One line, only while the ledger holds an open row — silent the rest of the time.

    Outside the 3-line/240-char budget on purpose: it is not part of the standing context,
    it appears only while disk is being wasted, and it disappears the moment `sweep --clean`
    runs. A ledger that is missing or corrupt says nothing, so it prints nothing: a nudge
    that cries wolf gets ignored, and this one has to still be believed weeks from now.
    """
    try:
        import tdq_worktree_registry as so_wt
        mo = so_wt.dong_mo(cwd)
    except Exception:
        return
    if mo:
        print(f"[TDQ:WORKTREE] {len(mo)} worktree(s) still open — run: "
              "python3 scripts/tdq_team.py sweep")


def main():
    payload = read_payload()
    cwd = payload_cwd(payload)
    sid = session_id(payload)
    turn_log_clear(cwd, sid)
    # Start-of-turn disk snapshot — so stop_gate can tell at end of turn what REALLY changed,
    # even when the change went through the shell (the turn ledger only sees Edit/Write).
    # Written to the ledger, NOT printed into context → costs the model no tokens.
    turn_log_append(cwd, "turn_start", session=sid, **turn_snapshot(cwd))
    _nhac_worktree(cwd)

    # No OPEN request (open = active_request exists AND phase != idle) → point at intake.
    # The INTAKE line comes FIRST so _truncate (which cuts from the tail) never clips it.
    intake = ("[TDQ:INTAKE] No request is open — unless this prompt belongs to an intake round "
              "already running, open tdq-intake before doing anything else.")
    state = load(cwd)
    if state is None or not state.get("active_request"):
        _emit(cwd, sid, [intake])
        return
    # phase_key, not the raw phase: a running lane quick keeps the raw phase=idle — comparing
    # raw would fire INTAKE wrongly and swallow the APPROVE line of quick.
    if phase_key(state) == "idle":
        _emit(cwd, sid, [intake, render_next(cwd, state, brief=True)])
        return

    lane = effective_lane(state, warn=False)
    pending = None
    if lane == "quick" and not state.get("quick_approved"):
        pending = "quick"
    elif lane == "full" and state.get("spec_file") and not state.get("spec_approved"):
        pending = "spec"
    elif lane == "full" and state.get("spec_approved") and state.get("plan_file") \
            and not state.get("plan_approved"):
        pending = "plan"
    elif lane == "full" and state.get("plan_approved") \
            and effective_phase(state, warn=False) == "mode" \
            and not effective_mode(state, warn=False):
        # The mode gate: the plan is approved but the user has not picked how to run it. The
        # answer here is usually a bare "main"/"subagent", so it is detected separately.
        pending = "mode"

    lines = [render_next(cwd, state, brief=True)]

    if pending:
        # The APPROVE line comes BEFORE NEXT: _truncate cuts from the tail — better to clip
        # the project path than to clip the hint / approve command (the clipped-hint bug of
        # 2026-08-02).
        lines = []
        prompt = payload.get("prompt") or ""
        planned = plan_mode(cwd, state) if pending in ("plan", "mode") else None
        matched = looks_like_approval(prompt, pending)
        turn_log_append(cwd, "signal", session=sid, event="approve_pending",
                        target=pending, matched=matched, mode_conflict=False)
        if matched:
            mode = ""
            if pending == "mode":
                # The mode gate: the answer IS the mode. Picking a different mode than the
                # plan proposed is no conflict — a proposal is only a proposal, the user
                # settles it. Normalised to the machine identifier: the user typing "inline"
                # must still run --mode main, else state holds a string outside VALID_MODES.
                said = mode_from_answer(prompt, planned) or planned or "main"
                lines.append("[TDQ:APPROVE] The user just picked a mode → run NOW: "
                             f"python3 scripts/tdq_state.py approve plan --mode {said} "
                             f"--by \"{prompt[:60]}\"")
                lines.append(render_next(cwd, state, brief=True))
                _emit(cwd, sid, lines, critical=True)
                return
            if pending == "plan":
                found = MODE.search(prompt)
                said = normalize_mode(found.group(0)) if found else None
                if said and planned and said != planned:
                    # The mode in the approval sentence differs from the mode SETTLED in the
                    # plan — it must not be recorded by guessing, the agent has to ASK the
                    # user to confirm.
                    turn_log_append(cwd, "signal", session=sid, event="approve_pending",
                                    target=pending, matched=matched, mode_conflict=True)
                    lines.append(f"[TDQ:APPROVE] ⚠️ The approval says mode {said} but the plan "
                                 f"settled {planned} — ASK the user to confirm the mode first, "
                                 f"do not run approve yet.")
                    _emit(cwd, sid, lines, critical=True)
                    return
                # No mode named → do NOT insert a placeholder: a missing mode is valid now,
                # phase `mode` right after will ask. A placeholder makes the agent ask a beat early.
                mode = f" --mode {said}" if said else ""
            lines.append(f"[TDQ:APPROVE] The user just approved {pending} → run NOW: "
                         f"python3 scripts/tdq_state.py approve {pending}{mode} "
                         f"--by \"{prompt[:60]}\"")
        else:
            waiting = ("the user to pick a mode" if pending == "mode"
                       else f"{pending} approval")
            lines.append(f"[TDQ:APPROVE] Waiting for {waiting}. This prompt is NOT clearly an "
                         f"approval → do not guess: ASK again, or print "
                         f"\"{approve_hint(pending, planned)}\".")
        lines.append(render_next(cwd, state, brief=True))
        # No dedupe: every turn must see the "do not guess an approval" warning again —
        # compacting it to "(same as last turn)" here would swallow that very safety warning.
        _emit(cwd, sid, lines, critical=True)
        return

    # spec approved but the file changed afterwards → warn (the approval trace no longer matches)
    rel, sha = state.get("spec_file"), state.get("spec_sha256")
    drifted = False
    if state.get("spec_approved") and rel and sha:
        path = rel if os.path.isabs(rel) else os.path.join(cwd, rel)
        try:
            # The same hash function used when the approval was recorded
            # (`tdq_state._cli_approve`) — copying the hashing rule out here would let the two
            # sides drift apart and then disagree.
            drifted = sha256_noi_dung(path) != sha
        except OSError:
            drifted = True
        if drifted:
            lines.append("[TDQ:APPROVE] ⚠️ The spec changed after approval (sha256 mismatch) — "
                         "present it to the user for re-approval.")
    _emit(cwd, sid, lines, critical=drifted)


def _truncate(text, limit=MAX_CHARS):
    if len(text) <= limit:
        return text
    cut = limit - 1
    # A22: a cut landing inside inline code leaves half a command looking like a real one —
    # an odd backtick count means we are inside a span, so step back before the opening one.
    if text[:cut].count("`") % 2 == 1:
        cut = text.rfind("`", 0, cut)
    return text[:cut].rstrip() + "…"


def _compact(text):
    """The previous turn printed exactly this — replace it with a short line, same code."""
    match = re.match(r"^\[(TDQ:[A-Z]+)\]", text)
    code = match.group(1) if match else "TDQ"
    return f"[{code}] (same as last turn — unchanged)"


def _emit(cwd, session, lines, critical=False):
    """critical=True: a warning/action specific to this turn (ambiguous approval, mode
    mismatch, spec drift) — never compacted, even when it repeats last turn word for word."""
    text = _truncate("\n".join(lines[:MAX_LINES]))
    if critical:
        print(text)
        return
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if prompt_context_last(cwd, session) == digest:
        text = _compact(text)
    else:
        prompt_context_save(cwd, session, digest)
    print(text)


if __name__ == "__main__":
    main()
