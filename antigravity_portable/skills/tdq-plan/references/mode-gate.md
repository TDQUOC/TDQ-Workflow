# The mode gate — a question block built from the mode table, not typed by hand

Used at step 6 of [tdq-plan](../SKILL.md), when the plan is approved but the user has not named
a mode. The block follows
[user-facing-block.md](../../tdq-conventions/references/user-facing-block.md).

## Table of contents

- Where the options come from
- The question block — 3 options
- The question block — 2 options
- The proposal always sits at A
- Why `codex` may be unofferable — the 4 causes
- Rule for writing the "Vì sao đề xuất" paragraph <!-- i18n-allow: canonical name of the block -->
- What each option does NOT mean
- The names

## Where the options come from

**Never type the option list from memory.** How many options exist depends on the machine, so
ask the machine:

```
python3 ~/.gemini/config/plugins/tdq-workflow/scripts/tdq_state.py modes --json
```

It prints one row per mode with four keys: `ma` (the machine identifier), `nhan` (the display
label), `chon_duoc` (offerable on this machine), and `ly_do` (why not, when `chon_duoc` is
false). Offer exactly the rows with `chon_duoc` true, in the order printed. A row that is not
offerable becomes one grey line under the options — never a hidden option and never a lie.

Two modes are always offerable: `main` and `subagent`. The third, `codex`, needs the Codex CLI
plus the user's consent on this machine, so the block has two shapes.

## The question block — 3 options

<!-- i18n-allow: chat block written in the default document language -->
```
Plan đã được duyệt. Còn một câu cuối: bạn muốn tôi chạy theo cách nào?

1. Bạn chọn cách chạy nào?
- A (đề xuất): làm trực tiếp (inline implement) — tôi làm tuần tự ngay trong cuộc trò chuyện này, bạn theo dõi được từng bước.
- B: giao trợ lý (sub-agent implement) — tôi làm leader: chia cả plan thành từng đợt, mỗi đợt phát cho nhiều trợ lý chạy song song ở worktree riêng, phần không tách được thì tôi tự làm, xong đợt nào tôi kiểm và gộp đợt đó.
- C: giao Codex (codex implement) — tôi viết test đỏ cho từng task rồi để Codex viết code cho xanh trong đúng vùng file đã khai, tôi chạy lại test và soi vùng file trước khi tick.

**Vì sao đề xuất A cho plan này:** <1–3 dòng, theo luật dưới>

---

**Bạn chọn cách nào?**

➤ Trả lời: nhắn "1a" / "inline", "1b" / "sub-agent" hoặc "1c" / "codex" (chọn xong tôi bắt tay làm ngay) · Góp ý: nhắn trực tiếp
```

## The question block — 2 options

This is the shape when `modes --json` reports `codex` as not offerable. The grey line under
the options carries the reason verbatim from the `ly_do` key.

<!-- i18n-allow: chat block written in the default document language -->
```
Plan đã được duyệt. Còn một câu cuối: bạn muốn tôi chạy theo cách nào?

1. Bạn chọn cách chạy nào?
- A (đề xuất): làm trực tiếp (inline implement) — tôi làm tuần tự ngay trong cuộc trò chuyện này, bạn theo dõi được từng bước.
- B: giao trợ lý (sub-agent implement) — tôi làm leader: chia cả plan thành từng đợt, mỗi đợt phát cho nhiều trợ lý chạy song song ở worktree riêng, phần không tách được thì tôi tự làm, xong đợt nào tôi kiểm và gộp đợt đó.

_(Cách thứ ba — giao Codex — máy này chưa dùng được: <ly_do>. Mở bằng: <goi_y>.)_

**Vì sao đề xuất A cho plan này:** <1–3 dòng, theo luật dưới>

---

**Bạn chọn cách nào?**

➤ Trả lời: nhắn "1a" / "inline" hoặc "1b" / "sub-agent" (chọn xong tôi bắt tay làm ngay) · Góp ý: nhắn trực tiếp
```

## The proposal always sits at A

Whichever mode you propose, it is written on line A. Change the TEXT of line A, never its
position. The hook that reads the user's reply maps the letters onto the list you offered, in
the order you offered them, so a proposal parked at B silently turns "1a" into the wrong mode.

Matching consequence: a letter is only valid while the option exists. In the 2-option block,
"1c" means nothing, and you ask again rather than guessing which mode was meant.

## Why `codex` may be unofferable — the 4 causes

`ly_do` carries one of four sentences, and each has its own fix. Print the reason and the fix;
never merge them into "Codex is unavailable".

| # | Cause | What `ly_do` says | Fix printed to the user |
|---|---|---|---|
| 1 | CLI not installed | chưa cài `codex` trên máy này | `npm i -g @openai/codex`, then `codex login` | <!-- i18n-allow: reason sentence printed verbatim by the check command -->
| 2 | Installed, not approved | có `codex` nhưng bạn chưa duyệt cho workflow gọi nó | `python3 ~/.gemini/config/plugins/tdq-workflow/scripts/tdq_codex.py dong-y --model <ten-model>` — only after the user says yes | <!-- i18n-allow: reason sentence printed verbatim by the check command -->
| 3 | Approved, model does not answer the say hi | `codex` có nhưng không chạy được — <chi tiết> | check the provider/router in `~/.codex/config.toml` or run `codex login`, then rerun `python3 ~/.gemini/config/plugins/tdq-workflow/scripts/tdq_codex.py check` | <!-- i18n-allow: reason sentence printed verbatim by the check command -->
| 4 | No model name | thiếu tên model — mode này cấm rơi về model mặc định của máy | `python3 ~/.gemini/config/plugins/tdq-workflow/scripts/tdq_codex.py setup-model <ten-model>` | <!-- i18n-allow: reason sentence printed verbatim by the check command -->

Never install anything and never flip the consent flag yourself. Cause 2 exists precisely
because calling an outside CLI is the user's decision, not yours.

## Rule for writing the "Vì sao đề xuất" paragraph <!-- i18n-allow: canonical name of the block -->

1–3 lines long, sitting right under the options. Vague wording is banned.

**Which mode gets proposed is decided by a COMMAND, not by eye.** Run it on the plan you have
just written: `tdq_bench.py simulate --plan <plan> --thuc-do <constants file> --he-so-agent 1.5`,
then take the `Winner:` line as the proposal and the minute gap as the evidence. The four grounds
below only serve to WRITE the reason so a reader follows it; they never overturn what the command
returned:

1. Task count.
2. Whether any task depends on the one before it.
3. How many files several tasks touch at once.
4. Whether any task carries the `(mcp)` label — that label forces Claude to do it itself.

Close with exactly one sentence saying why NOT the other options.

An example carrying every ground:

> `simulate` cho main 40,7 phút so với đội 32,6 phút (hệ số agent 1,5) nên đề xuất B; <!-- i18n-allow: example written in the default document language -->
> 12 task, 4 task cùng sửa `tdq_state.py`, T4.3 mang nhãn `(mcp)` nên leader vẫn giữ 3 task. <!-- i18n-allow: example written in the default document language -->

## What each option does NOT mean

**B is not "hand everything out".** Mode B is a hybrid. The leader still keeps for itself
(`tu_lam`) the tasks matching exactly one group of the closed keep-set: `phu-thuoc`, `vung-khoa`,
`mcp`, `file-luat`, `hop-dong`. Everything else MUST be handed out — and
`~/.gemini/config/plugins/tdq-workflow/scripts/tdq_team.py audit` exits non-zero when the leader invents a group outside that set to
keep work. The set is the constant `LY_DO_GIU` in `~/.gemini/config/plugins/tdq-workflow/scripts/tdq_team.py`; the full lookup table
lives in `tdq-build/references/team-mode.md`.

So the "Vì sao đề xuất" paragraph must never describe B as "handing everything to assistants". <!-- i18n-allow: canonical name of the block -->
The right way to size B is: **how many tasks are separable out of the total**. That number, not
the total task count, decides whether B beats A. Full rule of the team mode:
[team-mode.md](../../tdq-build/references/team-mode.md).

<!-- luat-mode-allow: so hai mode với nhau, không phải liệt kê danh sách lựa chọn -->
**C is not the fast mode.** Measured, mode `codex` lands roughly level with mode `main` when run
sequentially: about 5 seconds of fixed startup per task, and 105.8s on a real task against the
leader's 122.16s. What it changes is who writes the code, not the wall clock. Describing C as
"faster" in the proposal paragraph is banned. Full rule:
[codex-mode.md](../../tdq-build/references/codex-mode.md).

## The names

(deliberate repetition — the original is step 6 of `skills/tdq-plan/SKILL.md`.)

The names above are **display labels**. What state records is the machine identifier
(`MODE_LABELS`/`MODE_ALIASES` in `~/.gemini/config/plugins/tdq-workflow/scripts/tdq_state.py`). The user typing "inline",
"sub-agent implement", "codex" or an old machine name all resolve to the right identifier.
