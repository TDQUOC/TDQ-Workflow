# Team mode — the leader assigns the whole plan, sub-agents run in parallel

Soul: chất lượng > runtime > context cost · luật gốc: ../../tdq-conventions/references/soul.md <!-- i18n-allow: canonical Soul line -->

You are the LEADER. Sub-agents are your TEAM. The default is DELEGATE; keeping a task for
yourself needs a reason from the lookup table below, and that reason is machine-checked.

## Table of contents

- When it applies
- What to do
- The worktree ledger
- Self-check

## When it applies

In phase `implement`, **every mode**. The leader doctrine is a way of ORGANISING the work, not
a run mode: the plan is always split into waves, and every task always carries a
delegate-or-keep decision with a checkable reason.

The mode the user picked only changes who types:
- `subagent` — `giao` tasks are done by sub-agents, one worktree per task, one wave in parallel.
- `main` — the leader does EVERYTHING, but in the plan's wave order and still recording the
  keep reason for each task. Jumping the wave order in mode `main` breaks exactly the thing
  that was measured: wave order is dependency order, not a suggestion.

Team mode does NOT mean every task must be delegated. It means: **whatever can be split must
be split**, and the leader does the rest — like a real team lead, neither someone who hoards
all the work nor someone who scatters it blindly.

## What to do

### Step 0 — assign the WHOLE plan before typing the first line of code

```
python3 scripts/tdq_team.py phan-cong
python3 scripts/tdq_team.py kiem-ke
```

`phan-cong` reads the ENTIRE plan (not one task at a time), builds each task's file region from
its `Chạm:` line, then writes `docs/tdq/team/<slug>.json`. Each task has exactly 4 fields: <!-- i18n-allow: canonical field names of the plan -->
`quyet_dinh` (giao | tu_lam) · `ly_do` · `vung_file` · `dot`.

`kiem-ke` exits non-zero when a `tu_lam` task has an empty reason or one outside the closed
reason set (the lookup table just below is that set, exactly the `LY_DO_GIU` constant the
command reads).
This is the anti-loophole fence. You cannot quietly do everything on main and claim the work
was split: the map is on disk. The `[TDQ:TEAM]` hook stops your hand the moment you edit a file
in the region of a task recorded as `giao` without having opened its branch.

### Decision table — default GIAO, keeping a task must match exactly one row

| Group | How to recognise it | Checked by |
|---|---|---|
| `phu-thuoc` | the task description names another task code (`T1.1`) that is not yet `[x]` | read the task line; the named task is still `[ ]`/`[~]`/`[>]` |
| `vung-khoa` | the task has no `Chạm:` line → no file region can be declared for it | `grep -A2 'T1.1' <plan>` shows no `Chạm:` <!-- i18n-allow: canonical field names of the plan --> |
| `mcp` | the task's `Dùng:` line ends with the `(mcp)` label | `grep '(mcp)' <plan>` <!-- i18n-allow: canonical field names of the plan --> |
| `file-luat` | the file region touches `skills/`, `hooks/`, `agents/`, `.claude/`, `.codex/`, `CLAUDE.md`, `AGENTS.md` | look at `vung_file` in the map |
| `hop-dong` | the task builds a shared contract (data type, constant, message template, registry) that later tasks read | several other tasks declare `Cần:` pointing at it <!-- i18n-allow: canonical field names of the plan --> |
| **mặc định: GIAO** | **matches none of the 5 rows above** | `python3 scripts/tdq_team.py kiem-ke` exit 0 <!-- i18n-allow: canonical field names of the plan --> |

These five groups are a CLOSED set. Inventing a sixth reason ("this is faster if I do it",
"this task is too small", "explaining it to a sub-agent takes longer than doing it") is working
around the rule, and `kiem-ke` will go red.

### The wave loop

```
python3 scripts/tdq_team.py cum            # next wave: delegatable tasks with no locked region
python3 scripts/tdq_team.py mo T1.1        # branch + its own worktree for the task
# → call the tdq-implementer agent with the prompt template below, EVERY task of the wave in ONE response
# → mark every task you just handed out [>] in the plan (several [>] is valid)
python3 scripts/tdq_team.py kiem T1.1      # probe for conflicts, does NOT touch the repo
python3 scripts/tdq_team.py hop T1.1       # merge, then clean up the worktree right away
# → turn [>] into [x] IMMEDIATELY once the merge lands
python3 scripts/tdq_team.py soat --don     # end of wave: sweep EVERY request, then back to `cum`
```

While a wave runs, the leader works the `tu_lam` tasks of that same wave — that is why this
mode beats `main`, not because sub-agents type faster than you.

Tick marks: `[ ]` not started · `[~]` the LEADER is doing it (at most ONE) · `[>]` handed to a
sub-agent (several allowed) · `[x]` done and merged back.

### The delegation prompt template — all 9 fields, none left out

<!-- i18n-allow: field names of the prompt template, pinned by the tests -->
```
TASK: T1.1 — <chép nguyên văn dòng task trong plan, kể cả phần Test:>
CỤM: đợt 2/5 · chạy song song với T1.2, T1.4
BASE: tdq/<slug>/tich-hop
WORKTREE: /đường/dẫn/tuyệt/đối/.tdq-worktrees/<slug>/t1.1
VÙNG FILE: scripts/alpha.py, tests/test_alpha.py — CẤM sửa file ngoài danh sách này
TEST: <lệnh kiểm của task> — phải đỏ trước, xanh sau
RANH GIỚI: luôn được làm — sửa file trong VÙNG FILE, thêm test của chính task này.
  phải hỏi trước — đổi API/khuôn dữ liệu dùng chung, thêm phụ thuộc mới, sửa file ngoài vùng.
  cấm — sửa plan/spec/state, commit lên nhánh khác, chạy full suite, đụng worktree của task khác.
TỰ KIỂM: <đúng MỘT lệnh agent con chạy được trước khi báo xong, thường là lệnh ở TEST>
TRẢ VỀ: đúng khuôn TASK/STATUS/FILES/TEST/BRANCH/TICK-READY/NOTES ở agents/tdq-implementer.md
```

Include the spec and plan paths in the prompt body. A sub-agent CANNOT read this conversation —
a missing field means it has to guess, and a wrong guess is paid for at merge time.

### RIGHT/WRONG examples

1. Splitting the work
   - RIGHT: `phan-cong` done, 9/12 tasks `giao`, 3 tasks `tu_lam` with reason codes; `kiem-ke` exit 0.
   - WRONG: read the plan, think "faster if I just do it", work on main, never generate the map.
2. Delegation rhythm
   - RIGHT: one response calling the agent 4 times for 4 tasks of the same wave — they run concurrently.
   - WRONG: call 1 agent, wait for it, then call the next — that is mode `main` wearing a team costume.
3. Merging
   - RIGHT: `kiem T1.2` clean → `hop T1.2` → tick `[x]` right away.
   - WRONG: merge straight through with no `kiem`, hit a conflict midway, patch it up in the main repo.
4. Tick marks
   - RIGHT: 4 tasks `[>]` at once plus 1 `[~]` task of the leader.
   - WRONG: 4 tasks `[~]` at once — the hook blocks it, and nobody can tell where the leader really is.
5. File regions
   - RIGHT: two tasks both touch `scripts/a.py` → `phan-cong` puts them in two different waves.
   - WRONG: delegate both in one wave because "it'll probably be fine" — git says nothing until the merge breaks.
6. Shared contracts
   - RIGHT: the task creating the `TRAN_SONG_SONG` constant and the message template is kept and
     finished FIRST, only then is the wave that reads both dispatched.
   - WRONG: delegate all three tasks needing that constant in parallel — each sub-agent invents its
     own name, and only the merge reveals three mismatched versions.

## The worktree ledger

Every worktree `mo` opens is written into `docs/tdq/worktrees.json` (machine) and rendered
into `docs/tdq/worktrees.md` (human). The ledger outlives the request: a row stays open until
the worktree is really gone, so a worktree of a request finished weeks ago is still findable.
Write it ONLY through `scripts/tdq_team.py` — the same rule as `state.json`.

```
python3 scripts/tdq_team.py soat        # report: task · request · path · age · size · clean · merged
python3 scripts/tdq_team.py soat --don  # the same sweep, and remove everything that is safe
```

**Removing needs all THREE conditions**, checked per worktree, never by feel: the working
tree is clean · the branch is already in the integration branch · git does not hold it
locked. Any one missing and NOTHING is deleted — the row stays open and the reason is
printed. The task branch is deleted after the merge; the integration branch is kept.

"Clean" counts ignored files too, unless they regenerate by themselves (`__pycache__`,
`node_modules`, …): `git worktree remove` deletes a `.env` or a local key without a word,
and those exist nowhere else. Such a worktree is kept with its own reason and its own way
out, never lumped in with uncommitted changes.

`soat` only ever deletes inside `.tdq-worktrees/`. A worktree living elsewhere is listed
under "out of scope" and is never touched: it may well be the user's own working copy.

**Rule — the suggestion block goes at the END of the turn.** A worktree that cannot be
cleaned up prints a `NOT CLEANED UP YET` block with one option per line. Put that block at the
end of your reply to the user, as the last thing they read, TRANSLATED into their `doc_lang`
— the commands stay verbatim, character for character, because the user pastes them. Reason:
the user is the only one who can decide whether uncommitted work is thrown away or kept, and
a block buried in the middle of a long turn is a block nobody acts on.

Gate `qc` refuses to open while the ledger still holds an open row, and every turn the hook
prints one `[TDQ:WORKTREE]` line for as long as that is true.

## Self-check

Before ending phase implement, all of these must hold:

```
python3 scripts/tdq_team.py kiem-ke          # exit 0
python3 scripts/tdq_team.py cum              # prints "HẾT: không còn task nào để giao" <!-- i18n-allow: quoted machine output -->
python3 scripts/tdq_team.py soat --don       # every worktree cleaned up, across all requests
python3 scripts/tdq_team.py soat             # the ledger holds no open row left
git worktree list                            # only the root worktree left
grep -c '^- \[x\]' docs/tdq/plan/<slug>.md   # equals the total task count
```

And one question to ask yourself, answerable with a number: **how many delegated / how many in
total?** That number must appear in the report. A low delegation ratio with no reason from the
lookup table means you worked around the user's rule — the user picked team mode to get a team,
not a promise.
