# Team mode: the worktree ledger

Split out of `team-mode.md` on 2026-10-02: this part is LOOKUP material — opened only when the
worktree ledger has to be inspected, never while splitting waves or handing out tasks. 575 tokens
inside a 3,652-token file.

## The worktree ledger

Every worktree `open` opens is written into `docs/tdq/worktrees.json` (machine) and rendered
into `docs/tdq/worktrees.md` (human). The ledger outlives the request: a row stays open until
the worktree is really gone, so a worktree of a request finished weeks ago is still findable.
Write it ONLY through `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_team.py"` — the same rule as `state.json`.

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_team.py" sweep        # report: task · request · path · age · size · clean · merged
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_team.py" sweep --clean  # the same sweep, and remove everything that is safe
```

**Removing needs all THREE conditions**, checked per worktree, never by feel: the working
tree is clean · the branch is already in the request branch · git does not hold it
locked. Any one missing and NOTHING is deleted — the row stays open and the reason is
printed. The task branch is deleted after the merge; the request branch is kept — step 11
of the report merges it back into `nhanh_goc` and deletes it there.

"Clean" counts ignored files too, unless they regenerate by themselves (`__pycache__`,
`node_modules`, …): `git worktree remove` deletes a `.env` or a local key without a word,
and those exist nowhere else. Such a worktree is kept with its own reason and its own way
out, never lumped in with uncommitted changes.

`sweep` only ever deletes inside `.tdq-worktrees/`. A worktree living elsewhere is listed
under "out of scope" and is never touched: it may well be the user's own working copy.

**Rule — the suggestion block goes at the END of the turn.** A worktree that cannot be
cleaned up prints a `NOT CLEANED UP YET` block with one option per line. Put that block at the
end of your reply to the user, as the last thing they read, TRANSLATED into their `doc_lang`
— the commands stay verbatim, character for character, because the user pastes them. Reason:
the user is the only one who can decide whether uncommitted work is thrown away or kept, and
a block buried in the middle of a long turn is a block nobody acts on.

Gate `qc` refuses to open while the ledger still holds an open row, and every turn the hook
prints one `[TDQ:WORKTREE]` line for as long as that is true.

## RIGHT/WRONG examples

1. Splitting the work
   - RIGHT: `assign` done, 9/12 tasks `giao`, 3 tasks `tu_lam` with reason codes; `audit` exit 0.
   - WRONG: read the plan, think "faster if I just do it", work on main, never generate the map.
2. Delegation rhythm
   - RIGHT: one response calling the agent 4 times for 4 tasks of the same wave — they run concurrently.
   - WRONG: call 1 agent, wait for it, then call the next — that is mode `main` wearing a team costume.
3. Merging
   - RIGHT: `kiem T1.2` clean → `hop T1.2` → tick `[x]` right away.
   - WRONG: merge straight through with no `check`, hit a conflict midway, patch it up in the main repo.
4. Tick marks
   - RIGHT: 4 tasks `[>]` at once plus 1 `[~]` task of the leader.
   - WRONG: 4 tasks `[~]` at once — the hook blocks it, and nobody can tell where the leader really is.
5. File regions
   - RIGHT: two tasks both touch `scripts/a.py` → `assign` puts them in two different waves.
   - WRONG: delegate both in one wave because "it'll probably be fine" — git says nothing until the merge breaks.
6. Shared contracts
   - RIGHT: the task creating the `TRAN_SONG_SONG` constant and the message template is kept and
     finished FIRST, only then is the wave that reads both dispatched.
   - WRONG: delegate all three tasks needing that constant in parallel — each sub-agent invents its
     own name, and only the merge reveals three mismatched versions.

