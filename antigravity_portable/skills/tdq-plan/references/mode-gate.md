# The mode gate — the question block and the rule for writing the reason

Used at step 6 of [tdq-plan](../SKILL.md), when the plan is approved but the user has not named
a mode. The block follows
[user-facing-block.md](../../tdq-conventions/references/user-facing-block.md).

## The question block

<!-- i18n-allow: chat block written in the default document language -->
```
Plan đã được duyệt. Còn một câu cuối: bạn muốn tôi chạy theo cách nào?

1. Bạn chọn cách chạy nào?
- A (đề xuất): làm trực tiếp (inline implement) — tôi làm tuần tự ngay trong cuộc trò chuyện này, bạn theo dõi được từng bước.
- B: giao trợ lý (sub-agent implement) — tôi làm leader: chia cả plan thành từng đợt, mỗi đợt phát cho nhiều trợ lý chạy song song ở worktree riêng, phần không tách được thì tôi tự làm, xong đợt nào tôi kiểm và gộp đợt đó.

**Vì sao đề xuất A cho plan này:** <1–3 dòng, theo luật dưới>

---

**Bạn chọn cách nào?**

➤ Trả lời: nhắn "1a" / "inline" hoặc "1b" / "sub-agent" (chọn xong tôi bắt tay làm ngay) · Góp ý: nhắn trực tiếp
```

The proposal sits at A whichever mode it is — change the text of line A, never its position.

## Rule for writing the "Vì sao đề xuất" paragraph <!-- i18n-allow: canonical name of the block -->

1–3 lines long, sitting right under the two options. Vague wording is banned.

**Which mode gets proposed is decided by a COMMAND, not by eye.** Run it on the plan you have
just written: `tdq_bench.py mo-phong --plan <plan> --thuc-do <constants file> --he-so-agent 1.5`,
then take the `Winner:` line as the proposal and the minute gap as the evidence. The four grounds
below only serve to WRITE the reason so a reader follows it; they never overturn what the command
returned:

1. Task count.
2. Whether any task depends on the one before it.
3. How many files several tasks touch at once.
4. Whether any task carries the `(mcp)` label — that label forces Claude to do it itself.

Close with exactly one sentence saying why NOT the other option.

An example carrying every ground:

> `mo-phong` cho main 40,7 phút so với đội 32,6 phút (hệ số agent 1,5) nên đề xuất B; <!-- i18n-allow: example written in the default document language -->
> 12 task, 4 task cùng sửa `tdq_state.py`, T4.3 mang nhãn `(mcp)` nên leader vẫn giữ 3 task. <!-- i18n-allow: example written in the default document language -->

## B does NOT mean handing everything out

Mode B is a hybrid, not "every task pushed to a sub-agent". The leader still keeps for itself
(`tu_lam`) the tasks matching exactly one group of the closed keep-set: `phu-thuoc`, `vung-khoa`, `mcp`,
`file-luat`, `hop-dong`. Everything else MUST be handed out — and `~/.gemini/antigravity-cli/tdq/scripts/tdq_team.py kiem-ke`
exits non-zero when the leader invents a group outside that set to keep work. The set is the
constant `LY_DO_GIU` in `~/.gemini/antigravity-cli/tdq/scripts/tdq_team.py`; the full lookup table lives in
`tdq-build/references/team-mode.md`.

So the "Vì sao đề xuất" paragraph must never describe B as "handing everything to assistants". <!-- i18n-allow: canonical name of the block -->
The right way to size B is: **how many tasks are separable out of the total**. That number, not
the total task count, decides whether B beats A. Full rule of the team mode:
[team-mode.md](../../tdq-build/references/team-mode.md).

## The names

(deliberate repetition — the original is step 6 of `skills/tdq-plan/SKILL.md`.)

The two names above are **display labels**. What state records is still `main`/`subagent`
(`MODE_LABELS`/`MODE_ALIASES` in `~/.gemini/antigravity-cli/tdq/scripts/tdq_state.py`). The user typing "inline",
"sub-agent implement" or an old machine name all resolve to the right machine identifier.
