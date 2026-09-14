# Codex mode — the leader writes the failing test, Codex makes it pass

Soul: chất lượng > runtime > context cost · luật gốc: ../../tdq-conventions/references/soul.md <!-- i18n-allow: canonical Soul line -->

You stay the LEADER. Codex is a hired hand with a keyboard, not a teammate you hand the plan
to. You own the test, the file zone and the verdict; Codex owns only the production code of
one task at a time.

## Table of contents

- When it applies
- What to do
- The role contract
- Self-check

## When it applies

In phase `implement`, only when the user picked mode `codex` at the mode gate. The mode is
not available on a machine without the Codex CLI or without the user's consent flag; the gate
already says so, with the reason.

This mode is NOT the fast mode, and you must never present it as one. Measured: `codex exec`
costs about 5 seconds of fixed startup per task, and one real task ran 105.8s against the
leader's own 122.16s. Sequential, it lands roughly level with mode `main`. What it buys is a
different hand writing the code, not a shorter wall clock.

## What to do

### The four beats of ONE task

Every task in the plan runs these four beats, in this order, with nothing skipped:

1. **The leader writes the failing test.** You write it yourself. Codex never writes the test
   it is measured by — a hand that can edit the ruler is not being measured.
2. **The leader runs it and SEES red.** Not "expects red": runs it and reads the failure. A
   green-from-the-start test proves nothing about what comes next.
3. **Codex makes it green**, writing only inside `VÙNG FILE` and never inside `VÙNG KHOÁ`. <!-- i18n-allow: canonical zone names -->
   The zone travels to Codex as declared file paths; the test file of the task is always in
   the locked zone.
4. **The leader runs the test again and audits the zone.** Green alone is not `xong`. A task <!-- i18n-allow: canonical status name -->
   that touched a file outside its zone is a FAIL, whatever Codex reported.

### Step 1 — check the machine once per request

```
python3 ~/.gemini/config/plugins/tdq-workflow/scripts/tdq_codex.py check
```

Not runnable → say the printed reason to the user and go back to the mode gate. Never install
the CLI and never set the consent flag on the user's behalf.

### Step 2 — declare the zone from the plan

The task's `Chạm:` line IS the file zone; do not invent a wider one. The locked zone is the <!-- i18n-allow: canonical plan field name -->
task's own test file plus anything the plan names as untouchable.

### Step 3 — run the task

```
python3 ~/.gemini/config/plugins/tdq-workflow/scripts/tdq_codex.py run <ma-task> --prompt "<prompt>" --vung <file...> --khoa <file...> --da-thay-do
```

`--da-thay-do` is your signature on beat 2. Passing it without having seen red is lying to
your own audit trail. The command owns the snapshot, the sandbox, the timeout and the
post-audit; you do not rebuild any of that by hand.

### Step 4 — read the verdict, not the transcript

The command prints one JSON line with five keys, in this order: `trang_thai`, `giay`,
`vung_file`, `ly_do`, `can_chay_lai_test`. Read four of them: the status, the file-zone
result, the reason code (`null` when the status is `xong`), and `can_chay_lai_test`, which <!-- i18n-allow: canonical status name -->
says whether the test gets the last word on a `fail`. Read that. The raw Codex transcript
stays out of your context — see the digest threshold below.

### Step 5 — on a zone breach, roll back before anything else

```
python3 ~/.gemini/config/plugins/tdq-workflow/scripts/tdq_vungfile.py hoan-tac --moc <json> --file <file...>
```

Roll back the stray files first, then decide: retry the task with a tighter prompt, or take
the task back and write the code yourself. Never leave a stray file in the tree "to clean up
later"; the next task's audit compares against a mark taken now, so the mess would be charged
to whoever comes next.

### Step 6 — close the books on the task

Test green plus zone audit `dat` → tick `[x]` in the plan immediately. <!-- i18n-allow: canonical field name of the audit result -->

`can_chay_lai_test` is `true` → the verdict is `fail` only because the REPLY was missing or
unreadable (`ly_do` is `khong-co-ket-qua` or `ket-qua-sai-khuon`) while the zone audit passed.
Codex may well have done the work, so the test decides: rerun the task's test yourself.

- Green → tick `[x]` and end the task line with the note `(cứu bằng test · ly_do=<mã>)`, so QC <!-- i18n-allow: canonical note written into the plan -->
  and the report can count the rescued turns.
- Red → the task failed, exactly as if the key were `false`.

`run` never turns that `fail` into `xong` itself. A `fail` with `can_chay_lai_test: false` is <!-- i18n-allow: canonical status name -->
never rescued this way: not a timeout, a deny, a non-zero exit, a model that answered
`xong: false`, or a turn that strayed outside its zone. <!-- i18n-allow: canonical result key -->

Anything else → the task is not done, and you say which of the two failed.

## The role contract

### The fixed prompt template

Every task uses this shape. Fill the four slots, change nothing else — a prompt that drifts
from task to task makes two runs incomparable.

<!-- i18n-allow: template copied verbatim -->
```
Nhiệm vụ: làm cho test sau chuyển từ ĐỎ sang XANH.
Lệnh chạy test: <lệnh>
Được sửa (VÙNG FILE): <danh sách file>
CẤM sửa (VÙNG KHOÁ): <danh sách file, luôn gồm file test>
Không sửa test, không nới điều kiện test, không thêm phụ thuộc mới.
Xong thì trả JSON đúng khuôn đã khai, khoá `xong` là true/false.
Chỉ trả object JSON trần, không bọc trong rào code, không kèm câu chữ nào khác.
```

### The result shape Codex must return

One JSON object, with the key `xong` as a boolean. The schema is handed to the CLI on every
run, but a router may drop it and the CLI does not check the reply against it, so the wrapper
reads the reply itself and never guesses:

- Accepted: bare JSON, or JSON inside exactly one code fence that wraps the WHOLE reply (label
  empty or `json`). Text before or after a fence, two fences, or plain prose is not a result.
- Only `xong` equal to the boolean `true` is `xong`. `false`, the string `"true"`, `1`, `null`
  or a missing key are all `fail`. Not knowing what happened is not permission to assume it
  went well.
- A turn that is not `xong` ends its log line with `· ly_do=<code>`, one code from the closed
  set `MA_LY_DO` in `~/.gemini/config/plugins/tdq-workflow/scripts/tdq_codex.py`. The same code rides in the verdict's `ly_do` key —
  read that code before rereading the raw reply.

### The digest threshold

Codex output is long, and the leader's context is the scarce resource. Read the shaped result
file and the one-line verdict. Pull at most **1,500 characters** of raw transcript into the
conversation, and only when a `fail` needs diagnosing. The full prompt and the full transcript
already live in the run log on disk; point at them instead of pasting them.

### What stays with the leader, always

| Belongs to the leader | Belongs to Codex |
|---|---|
| The test, its command, its assertions | The production code of one task |
| The file zone and the locked zone | Nothing outside that zone |
| The `[x]` tick in the plan | Nothing in the plan |
| The working log and the state | Nothing in `docs/tdq/` |

## Self-check

Before moving to the next task, all six must hold:

1. The test was seen red before Codex was called, and green after.
2. The zone audit returned `dat`, or the stray files were rolled back. <!-- i18n-allow: canonical field name of the audit result -->
3. Codex wrote nothing in the locked zone, so the test still measures what it measured.
4. No raw transcript above 1,500 characters went into the conversation.
5. The plan carries `[x]` for this task, written the moment it passed.
6. A `fail` with `can_chay_lai_test: true` had its test rerun, and a tick it earned carries the
   note `(cứu bằng test · ly_do=<mã>)`. <!-- i18n-allow: canonical note written into the plan -->
