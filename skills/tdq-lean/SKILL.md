---
name: tdq-lean
description: Hunt over-engineering and name what can be deleted - review a diff, audit the whole repo, or harvest `ponytail:` markers into a debt ledger. Use when code feels bigger than the request.
argument-hint: "[review|audit|debt]"
---

# TDQ Lean

One skill, three modes. The argument picks the mode; no argument means `review`.
Every mode reports **over-engineering only, never correctness** — a wrong-but-small function is
a bug report, not a finding here, and mixing the two makes both easier to ignore.
Findings are written in the user's document language `doc_lang` (deliberate repetition — the
original is `skills/tdq-conventions/SKILL.md`); the tags below stay in English so the same
vocabulary reads the same in both.

## The five tags — the whole vocabulary

| Tag | What it means |
| --- | --- |
| `delete` | dead code, or a feature built for a case nobody asked for |
| `stdlib` | the standard library already does this |
| `native` | a dependency doing what the platform does |
| `yagni` | an abstraction with exactly one implementation |
| `shrink` | same logic, fewer lines |

A finding with no tag is not a finding: name the tag, or drop the line.
Nothing to cut → say exactly `Lean already. Ship.` and stop. That sentence is the honest
result, not a failure to find something.

## Mode `review` — the diff only

1. Read the diff: `git diff` for unstaged work, `git diff --staged` when a commit is being
   prepared, `git diff <base>...HEAD` when the request has a branch (`nhanh_goc` in state).
2. One line per finding, in the order the diff reads:
   `L<line>: <tag> <what to cut>. <replacement>.`
3. Close with the net removable line count.

Done when: every finding carries a tag and a replacement, or the output is `Lean already. Ship.`
Next step: hand the list to whoever owns the diff — this skill never edits code.

## Mode `audit` — the whole tree

1. Scan the **whole repo**, not a diff — the whole tree is the point of this mode, so reaching
   for a diff command here is the wrong tool.
2. One line per finding, ranked biggest cut first:
   `<tag> <what to cut>. <replacement>. [<path>]`
3. Close with the net removable lines AND the removable dependencies — a dependency that can
   go is worth more than the lines it takes with it.

Done when: findings are ranked by size, each with a path, or the output is `Lean already. Ship.`
Next step: the ranked list goes into the plan as its own task when the user wants the cuts made.

## Mode `debt` — the `ponytail:` ledger

A `ponytail:` marker records a deliberate simplification. It is honest debt only while it
names both a ceiling and an upgrade path; a marker naming neither rots silently into "later
means never", and this mode exists to make that rot visible.

1. Run the ledger the repo already has — do not grep by hand:
   `python3 scripts/kiem_no_marker.py`
2. Report one row per marker, grouped by file:
   `<file>:<line> — <what was simplified>. ceiling: <the limit named>. upgrade: <the trigger>.`
3. Tag every marker that names no ceiling or no trigger as `no-trigger`. Those are the rotten
   rows, and they are what this mode is for.
4. Close with the marker count and how many lack a trigger. None at all → say exactly
   `No ponytail: debt. Clean ledger.`

Report only: change nothing, delete no marker. Clearing debt is somebody's task in a plan, not
a side effect of reading the ledger.

Done when: every marker has a row, and rows without a trigger are tagged `no-trigger`.
Next step: a `no-trigger` row gets a ceiling and a trigger written into the comment, or the
simplification it defends gets undone — the user decides which.
