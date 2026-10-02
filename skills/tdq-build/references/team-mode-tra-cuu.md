# Team mode: the worktree ledger

Split out of `team-mode.md` on 2026-10-02: this part is LOOKUP material — opened only when the
worktree ledger has to be inspected, never while splitting waves or handing out tasks. 575 tokens
inside a 3,652-token file.

## The worktree ledger

Every worktree `open` opens is written into `docs/tdq/worktrees.json` (machine) and rendered
into `docs/tdq/worktrees.md` (human). The ledger outlives the request: a row stays open until
the worktree is really gone, so a worktree of a request finished weeks ago is still findable.
Write it ONLY through `scripts/tdq_team.py` — the same rule as `state.json`.

```
python3 scripts/tdq_team.py sweep        # report: task · request · path · age · size · clean · merged
python3 scripts/tdq_team.py sweep --clean  # the same sweep, and remove everything that is safe
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
