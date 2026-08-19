# Procedure for adding a new language

Soul: chất lượng > runtime > context cost. Load on meeting a language with no rules yet.

## Nguồn

- The 7-section template and the threshold levels are drawn from the existing rule set
  (`chung.md` plus the 7 language files), which was built from the set-soul request's research
  file in `docs/tdq/research/`.
- The approve-before-writing procedure follows TDQ's gate law: only the USER approves.

## Khi nào áp dụng

- A task must write/change a file whose extension is NOT in `index.md`'s table, and user scope
  has no `tdq-rules` skill for that language either.
- Run the procedure only when the request genuinely needs code in that language; a language
  merely mentioned in passing is skipped.

## Luật Intentionality

1. A new rule must be able to answer `chung.md`'s 3 Intentionality questions; do not copy a
   long style guide verbatim.
2. **Sources must be real**: every URL put into a rule must exist in the request's research
   file; where no source was found, write "chưa có nguồn" — inventing a link is banned.
3. A rule that cannot say "how a violation is measured" is a dead rule — every rule attaches to
   a linter or a numeric threshold.

## Ngưỡng đo được

- The new rule file: under 150 lines, with the full 7-section template in the same order as
  this file.
- At least 2 official sources with URLs verifiable in the research file.
- Complexity thresholds follow `chung.md` (10/15, C family 25); change them only when the
  language's official source states a different level, and cite that source.

## Làm gì

1. Search tavily with exactly these 4 fixed queries, saving results + URLs into the running
   request's research file:
   - `<ngôn ngữ> official style guide`
   - `<ngôn ngữ> linter static analysis tool`
   - `<ngôn ngữ> code smells common mistakes`
   - `<ngôn ngữ> cyclomatic cognitive complexity threshold`
2. Draft the rule in the 7-section template, plus the linter line for `index.md`'s table.
3. With the draft done, **trình nháp trong chat** for the user to read — in full, not a clipped
   summary.
4. **DỪNG chờ user duyệt.** Until the user approves, the rule file is written nowhere.
5. Only after approval, write it into `~/.claude/skills/tdq-rules/` as a skill with a
   `SKILL.md` (stating when to load it, with the rule file beside it) so every project can
   reuse it; the current request loads that rule as its per-job tier.

## Tự kiểm

- [ ] All 4 fixed queries were run; the results are in the research file
- [ ] Every URL in the draft appears in the research file; missing sources recorded as "chưa có nguồn"
- [ ] The user's approval sentence is in the chat BEFORE anything is written to `~/.claude`
- [ ] The new skill has a `SKILL.md`; the linter table has its row ready for `index.md`

## Ví dụ ĐÚNG/SAI

```text
SAI  — gặp Kotlin, viết rule từ trí nhớ, ghi thẳng ra user scope không hỏi ai.
ĐÚNG — search 4 truy vấn → lưu research → nháp khuôn 7 mục → trình trong chat
       → user gõ "duyệt" → mới ghi skill tdq-rules kèm SKILL.md.
```
