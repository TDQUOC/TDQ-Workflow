# Procedure for adding a new language

Soul: chất lượng > runtime > context cost <!-- i18n-allow: canonical Soul line -->. Load on meeting a language with no rules yet.

## Sources

- The 7-section template and the threshold levels are drawn from the existing rule set
  (`chung.md` plus the 7 language files), which was built from the set-soul request's research
  file in `docs/tdq/research/`.
- The approve-before-writing procedure follows TDQ's gate law: only the USER approves.

## When it applies

- A task must write/change a file whose extension is NOT in `index.md`'s table, and user scope
  has no `tdq-rules` skill for that language either.
- Run the procedure only when the request genuinely needs code in that language; a language
  merely mentioned in passing is skipped.

## The Intentionality rule

1. A new rule must be able to answer `chung.md`'s 3 Intentionality questions; do not copy a
   long style guide verbatim.
2. **Sources must be real**: every URL put into a rule must exist in the request's research
   file; where no source was found, write "no source found" — inventing a link is banned.
3. A rule that cannot say "how a violation is measured" is a dead rule — every rule attaches to
   a linter or a numeric threshold.

## Measurable thresholds

- The new rule file: under 150 lines, with the full 7-section template in the same order as
  this file.
- At least 2 official sources with URLs verifiable in the research file.
- Complexity thresholds follow `chung.md` (10/15, C family 25); change them only when the
  language's official source states a different level, and cite that source.

## What to do

1. Search tavily with exactly these 4 fixed queries, saving results + URLs into the running
   request's research file:
   - `<language> official style guide`
   - `<language> linter static analysis tool`
   - `<language> code smells common mistakes`
   - `<language> cyclomatic cognitive complexity threshold`
2. Draft the rule in the 7-section template, plus the linter line for `index.md`'s table.
3. With the draft done, **present the draft in chat** for the user to read — in full, not a clipped
   summary.
4. **STOP and wait for the user to approve.** Until the user approves, the rule file is written nowhere.
5. Only after approval, write it into `~/.claude/skills/tdq-rules/` as a skill with a
   `SKILL.md` (stating when to load it, with the rule file beside it) so every project can
   reuse it; the current request loads that rule as its per-job tier.

## Self-check

- [ ] All 4 fixed queries were run; the results are in the research file
- [ ] Every URL in the draft appears in the research file; missing sources recorded as "no source found"
- [ ] The user's approval sentence is in the chat BEFORE anything is written to `~/.claude`
- [ ] The new skill has a `SKILL.md`; the linter table has its row ready for `index.md`

## RIGHT/WRONG examples

```text
WRONG — meeting Kotlin, writing the rule from memory, saving it straight to user scope
        without asking anyone.
RIGHT — search 4 queries → save the research → draft the 7-section shape → present it in
        chat → the user types the approval word → only then write skill tdq-rules with SKILL.md.
```
