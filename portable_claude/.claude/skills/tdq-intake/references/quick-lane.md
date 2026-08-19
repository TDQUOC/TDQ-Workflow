# Chế độ nhanh (express) — chi tiết

Chế độ nhanh differs from chế độ chuyên sâu by **merging the documents and merging the
gates**, not by dropping thought. Analysis, a web search whenever there is an external
unknown, and an interview whenever a question can still change the outcome are all KEPT.
Drop them only when the work is purely internal or already fully clear — and say why.

| Bước | Full | Quick |
|---|---|---|
| Phân tích + đọc code | có | có |
| Web search | có (2–4 truy vấn) | có khi có ẩn số bên ngoài |
| Vòng scope | có điều kiện, theo dấu hiệu kích hoạt | y hệt — cùng một bộ dấu hiệu |
| Interview | lặp đến hết mơ hồ | khi còn câu làm đổi kết quả |
| Tài liệu | brief + spec + plan | **1 file** `docs/tdq/plan/<slug>.md` |
| Gate duyệt | 2 (spec, plan) + 1 câu chọn cách chạy | **1** ("duyệt nhanh") |
| QC | file `qc/<slug>.md` | mỗi dòng DoD một phép kiểm, ghi vào mục ## QC của plan (mặc định BẬT) |
| Vòng fix khi FAIL | trần 3 vòng, ghi file qc/ | trần 3 vòng, ghi trong plan |
Vòng scope in chế độ nhanh shares the rule in [scope-round.md](scope-round.md): one trigger
sign met → ask about areas + context first; none met → write one SKIP reason line into the
mini-plan under `## Phạm vi` and move on.

## Mục lục

- Chín bước thi hành
- Luật ĐỌC đồ thị ở bước 1 (phân tích)
- Khuôn mini-spec/plan (≤ 40 dòng)
- Phạm vi
- Task
- Definition of Done
- Khối trình mini-plan cho user
- Luật tick — `[ ]` · `[~]` · `[x]`
- QC ở chế độ nhanh (express)
- QC
- QC
- Vòng fix
## Chín bước thi hành

This is the whole of Part C of [SKILL.md](../SKILL.md) — moved here so the skill body does
not load this branch on every call. Entering chế độ nhanh you **MUST** read all nine steps
below before doing step 1; working from memory is banned.

1. **Analyse.** Read exactly the code involved. External unknown (library, API, version) →
   web search through `tavily-primary` BEFORE writing anything; purely internal → skip it
   and say why. A question that can still CHANGE the outcome → interview per
   [interview.md](interview.md), with the **scope round** ahead of the detail round exactly
   as in lane deep ([scope-round.md](scope-round.md)).
2. **Write the mini spec/plan MERGED into 1 file** `docs/tdq/plan/<slug>.md`, ≤ 40 lines:
   scope in/out, one checkbox task per test, DoD with every line checkable by a command.
   **Every task that edits source must carry a `Chạm:` line** listing the paths in
   backticks — short does not mean the file map is optional. The checkbox has 4 states:
   `[ ]` chưa làm · `[~]` đang làm · `[>]` đã giao agent con · `[x]` xong. At implement time
   (step 7) mark `[~]` when the task starts and switch to `[x]` the moment the test is green.
3. **Present a ≤ 10-line summary** in chat: what will be done, which files it touches, how
   it is validated, plus exactly 1 line `Ước tính sẽ dùng skill: <các skill sẽ DÙNG, hoặc
   "không có">` (in doubt → USE).
4. In đúng dòng: `➤ Duyệt: nhắn "duyệt nhanh" (bỏ QC: "duyệt nhanh không QC"; "duyệt quick" vẫn chạy — duyệt xong implement ngay) · Góp ý: nhắn trực tiếp` rồi **DỪNG**.
5. User approves → run `python3 "${CLAUDE_PROJECT_DIR}/.claude/tdq/scripts/tdq_state.py" approve quick [--no-qc] --by "<nguyên văn>"` (`--no-qc` ONLY when the user says so explicitly — silence about QC means QC stays ON).
6. Append the mini-plan summary to `docs/workinglog/<hôm nay>.md` **BEFORE** touching code.
7. Implement end-to-end in 1 turn. **Before typing the first line of code, count the tasks
   whose `Chạm:` sets are disjoint** (no task sharing a path with another):
   - **3 or more** → hand them to sub-agent `tdq-implementer`, one agent per task, issued in
     the same response so they run in parallel; the cap is **4 branches** at a time — the
     same cap `python3 scripts/tdq_team.py cum` applies in chế độ chuyên sâu (task 5 prints
     `CHỜ SLOT`). Build a worktree only for an agent that ACTUALLY writes files; a read-only
     agent gets none. Mark `[>]` when handing over, and switch to `[x]` as the report lands.
   - **fewer than 3** → run inline as before; standing up an agent for 1–2 disjoint tasks
     costs more briefing than it saves.
   Each task: mark `[~]` BEFORE editing code (hook `edit_gate` BLOCKS when the plan has no
   `[~]`; `tests/**` is exempt), red→green, switch to
   `[x]` the moment the test is green — batching ticks at the end of the turn is banned.
   Then run **QC** (ON by default): one check per DoD line, evidence written into the plan's
   `## QC` section. `quick_qc_skipped = true` → section `## QC` holds a single line
   `BỎ theo yêu cầu user: "<nguyên văn>"`.
   (The full tick rule is in `## Luật tick` and the full QC rule in `## QC ở chế độ nhanh
   (express)`, both in this file.)
8. **Fix round when QC FAILs or a bug shows up**: add tasks to the plan under
   `## QC vòng N — fix`, fix red→green, then re-run the failed items plus the items the fix
   could have broken. There is a 3-round cap — over the cap, STOP, tell the user, propose
   moving to lane full, and leave the phase as it is. (Full version in `## Vòng fix` in this
   file.)
9. Append the result to the working log; ask the user about the commit.

Xong khi: `quick_approved = true`, the log is written, section `## QC` exists, no red test.
Bước kế tiếp: hỏi user về commit; hết request thì `... set phase=idle`.

## Luật ĐỌC đồ thị ở bước 1 (phân tích)

A question about **links** or the **overall map** ("who calls X", "what does changing X
affect") → open the graph with `graphify query|path|explain|affected`. Finding a string or
reading a specific file → grep/read. The graph holds only `scripts/` and `hooks/`; tests and
docs are excluded by `.graphifyignore`.

## Khuôn mini-spec/plan (≤ 40 dòng)

```markdown
# QUICK — <tên việc>

**Ngày:** YYYY-MM-DD · Brief: ../brief/<slug>.md · Lane: quick
**Trạng thái:** CHỜ DUYỆT
**Ước tính sẽ dùng skill:** <skill sẽ DÙNG, hoặc "không có">

## Phạm vi
- Trong: <gạch đầu dòng>
- NGOÀI: <gạch đầu dòng>

## Task
- [ ] **T1** <việc cụ thể> — Test: <lệnh hoặc tiêu chí pass>
- [ ] **T2** <việc cụ thể> — Test: <lệnh>

## Definition of Done
- <điều kiện đo được, có lệnh kiểm>
```
Going past 40 lines means this work is no longer quick — say so to the user and propose
moving to chế độ chuyên sâu (deep).

## Khối trình mini-plan cho user

Per [user-facing-block.md](../../tdq-conventions/references/user-facing-block.md) — all 5
components, the approval block at the end of the message, no emoji:

```
Tôi đã lên kế hoạch gọn cho yêu cầu của bạn.

**Sẽ làm:** <gạch đầu dòng ngắn>.
**Đụng tới:** <file/khu vực>.
**Kiểm thế nào:** <lệnh hoặc tiêu chí>.
**Ước tính sẽ dùng skill:** <skill sẽ DÙNG, hoặc "không có">.

Xem đầy đủ tại: `docs/tdq/plan/<slug>.md`

---

**Bạn duyệt để tôi làm luôn chứ?**

➤ Duyệt: nhắn "duyệt nhanh" (bỏ QC: "duyệt nhanh không QC"; "duyệt quick" vẫn chạy — duyệt xong tôi làm ngay) · Góp ý: nhắn trực tiếp
```
## Luật tick — `[ ]` · `[~]` · `[x]`

(nhắc lại có chủ ý — bản gốc ở mục `## Luật cứng` của `skills/tdq-build/SKILL.md`.)

The checkbox has four states: `[ ]` chưa làm · `[~]` đang làm · `[>]` đã giao agent con ·
`[x]` xong. At implement time:

1. Mark `[~]` on the task you are about to do **BEFORE** editing the first line of code.
   Handed to a sub-agent → mark `[>]` instead of `[~]`, so the plan shows who holds it.
2. Write the test (red) → code → test green.
3. Switch `[~]`/`[>]` → `[x]` **IMMEDIATELY**, never after the next task.

Only one task carries `[~]` at a time; `[>]` may be several, at most the 4-branch cap.
**Batching ticks at the end of the turn is banned** — chế độ nhanh (express) does the whole
job in one turn, so batched ticks mean the plan reflected nothing while the work happened.

Fence: `hooks/scripts/edit_gate.py` **BLOCKS** (deny) every edit outside `docs/` and
`tests/` while the phase is `implement`/`qc` and no task in the plan carries `[~]`.
`tests/**` is exempt so a red test can still be written first. Blocked while the request is
in fact closed → run `python3 scripts/tdq_state.py set phase=idle`.

## QC ở chế độ nhanh (express)

ON by default. Run it right after implement finishes, **số hạng mục bằng số dòng DoD** of
the mini-plan: one command-run check per DoD line, with the real output pasted in.
Plus one fixed item: run the exact `Test:` command of every task in the plan.

Add no item beyond the DoD. Edges, error paths, logging and placeholders are checked only
when a DoD line calls for them. Chế độ nhanh differs from chế độ chuyên sâu here: no
full-suite run over the repo, only each task's own test.

Evidence is appended to the plan file ITSELF, with no `qc/` file created:

```markdown
## QC
- Q1 test từng task: PASS — `<lệnh>` → `<output thật>`
- Q2 DoD "<nguyên văn dòng DoD 1>": PASS — `<lệnh>` → `<output thật>`
- Q3 DoD "<nguyên văn dòng DoD 2>": PASS — `<lệnh>` → `<output thật>`
```

Opt-out ONLY when the user says so, e.g. `"duyệt nhanh không QC"` → run approve with
`--no-qc`. Silence about QC means QC HAPPENS. Section `## QC` must still exist, with exactly
1 line:

```markdown
## QC
**BỎ theo yêu cầu user:** "<nguyên văn câu user>"
```

## Vòng fix

- Runs when QC FAILs, or when a bug / red test shows up.
- Fix tasks go into the plan under the heading `## QC vòng N — fix`, in the shape
  `- [ ] **QCn.1** <việc> — Test: <check>`. Do it red→green: `[~]` at the start, switch to
  `[x]` as soon as it is green.
- After the fix, re-run the failed items (hạng mục đã FAIL) plus the items the fix could
  have broken.
- **Trần 3 vòng.** Over the cap → STOP, tell the user, propose moving to chế độ chuyên sâu
  (deep). Keep `phase=implement`, do NOT run `set phase=idle`.
