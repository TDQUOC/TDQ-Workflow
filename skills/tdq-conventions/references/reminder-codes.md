# Hook reminder codes

TDQ hooks **do not block**, except in the few cases listed under `## The blocking points`. They
inject lines shaped `[TDQ:<CODE>] <the job to do>` into the context.

**Rule:** on seeing `[TDQ:<CODE>]` → do what it says **BEFORE** anything else in the turn, then
print `✓ [TDQ:<CODE>] <what was done>`.

The `✓` line is for the user to read. The hook does **not** read it — the hook checks by real
effect (which file changed, which command ran), so printing `✓` without doing the work still
gets you reminded again at the end of the turn.

## The codes (closed list)

| Code | Meaning | What to do | Effect the hook checks |
|---|---|---|---|
| `TDQ:NEXT` | Start of turn / start of session | Run `tdq_state.py next`, follow its output | a `tdq_state.py next` command actually ran |
| `TDQ:APPROVE` | Approval pending, or the user just approved | Record the approval, or ASK if ambiguous — see [approval.md](approval.md) | a `*_approved` field flipped to true |
| `TDQ:LOG` | The repo changed but today's working log has no entry | Append an entry to the end of `docs/workinglog/<today>.md` | that exact log file was modified |
| `TDQ:STATE` | About to hand-edit state | Use `tdq_state.py set\|approve\|init\|reset` | a `tdq_state.py` command actually ran |
| `TDQ:GIT` | Branch/worktree name or commit message breaks convention | Rename / fix the message before running | — (repeated at Stop) |
| `TDQ:DOC` | A file already read whole this session is being read whole again, unchanged | Read the part you need with `offset`/`limit`, or work from what you already hold | — (reminds once per file per session) |
| `TDQ:SEARCH` | **Blocks** a code search that skipped the concept layer: the request has not asked lumen/LSP/graphify yet, or a guess-list grep came after the unlock window | Ask the concept layer first (`semantic_search`, `find_symbol`/`find_references`, or `graphify query`), then grep the exact names it returned | a concept-layer call recorded in `docs/tdq/.tdq-search.jsonl` |
| `TDQ:ASK` | `AskUserQuestion` called in phase `implement`/`qc` with no declared pause | An unmet spec threshold is not a reason to ask: apply the spec §6 fallback, `lech add`, carry on; ask only for a `pause --loai` kind | — (reminds once per turn, never blocks) |

## The blocking points

1. **The working log.** The `Stop` hook blocks the end of a turn when: this turn **modified a
   file outside** `docs/workinglog/` and **has not** appended today's working log. To clear it:
   append the entry, then end the turn again.
2. **The search order (`TDQ:SEARCH`, since 2026-10-03).** The `PreToolUse` gate on `Bash`/`Grep`
   denies a code search when the request has not asked the concept layer yet, or when a
   guess-list grep comes after the unlock window. A name the user typed in the prompt and a
   file-list filter are never blocked, and nothing is blocked while the concept layer is still
   being built. To clear it: run the query the denial names, then search again.
3. **Editing code in team mode (`TDQ:TICK`, `TDQ:TEAM`).** The `PreToolUse` edit gate denies a
   source edit during implement/qc while the plan has no task marked `[~]` (`TDQ:TICK`), or one
   the assignment map does not hand to whoever is editing (`TDQ:TEAM`). To clear it: mark the
   task `[~]`, or delegate it as the map says.

Every other code only reminds, never blocks.

## Appendix

### How the hook sees changes

Two independent sources of evidence; one confirming source is enough:

1. **Turn ledger** `docs/tdq/.tdq-turn.jsonl` — records every file edit that went through the
   Edit/Write tools and every `tdq_state.py` command that ran.
2. **Disk snapshot** — at the start of the turn the hook stores the `sha256` of today's
   working log plus a fingerprint of `git status` + `git diff HEAD`; at the end it compares.

Source 2 makes the writing method irrelevant: appending the log with `cat >>`, `tee`, `sed -i`
or a heredoc all count, and editing the repo purely through the shell still gets the log
demanded.

The repo fingerprint **excludes** `docs/tdq/` and `docs/workinglog/` right at git's pathspec —
workflow bookkeeping changes almost every turn, and counting it would make even a read-only
turn owe a log entry. The exclusion applies to both the decision and the file name quoted in
the blocking message. Untracked files are fingerprinted by **content** (≤256 KB), so a `touch`
or a byte-identical rewrite does not count as a change.

Known limits:

- A project that is **not a git repo** has no repo fingerprint: the "log was written" direction
  still works, the "repo changed" direction falls back to the turn ledger as before.
- Editing a file inside `docs/tdq/` with the Edit tool is still recorded by the turn ledger.
- A file hidden by `.gitignore` is invisible to the repo fingerprint.
- An untracked file over 256 KB is fingerprinted by `size:mtime` only, so false alarms are
  possible.
- The file name in the blocking message is a **hint**: when no new file appeared it names the
  first dirty file, which may not be the file you just edited.
- **Two Claude Code sessions on one main worktree**: the repo fingerprint is a disk snapshot
  shared by the whole worktree and cannot tell which session wrote. Session A, which changed no
  code, can still be wrongly counted as "repo changed" if session B overwrites a file while A
  is running. Avoid this by not running two sessions on the same worktree at once.
