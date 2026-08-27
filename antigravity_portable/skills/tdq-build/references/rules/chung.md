# Shared rules for every language

Soul: chất lượng > runtime > context cost <!-- i18n-allow: canonical Soul line --> · luật gốc: skills/tdq-conventions/references/soul.md
Load this file FIRST, then the language rule file from the table in `index.md`.

## Sources

- SonarSource Clean Code — https://community.sonarsource.com/t/introducing-clean-code-in-our-products/98431 —
  4 measurable attributes: Consistent, Intentional, Adaptable, Responsible.
- arXiv 2411.10656 — https://arxiv.org/html/2411.10656v2 — measured 1,848 code issues in
  LLM-generated code: 59,6% fall in the Intentionality group.
- Complexity thresholds — https://dev.to/optiklab/writing-self-documented-code-with-low-cognitive-complexity-3k2l
  and https://www.augmentcode.com/learn/how-to-reduce-cyclomatic-complexity — SonarQube
  defaults to 10/15(25); ESLint uses 20 and Microsoft CA1502 uses 25, so one level must be
  fixed here.
- Security — https://www.kiuwan.com/blog/secure-coding-guidelines — OWASP Secure Coding
  Practices is the language-neutral checklist; CERT exists only for C/C++/Java/Perl.

## When it applies

- Every time you write or change code, in any language — small scripts and tests included.
- This rule is always on; there is no toggle. The SOLID principles and the 5-question
  checklist in `skills/tdq-conventions/references/clean-code.md` apply at the same time.

## The Intentionality rule

LLM-generated code breaks most often in the Intentional group (59,6%), so review that group
BEFORE the other three. Three mandatory questions before submitting code:

1. **Does the name say what it does?** A function/variable name must read as the work it does.
2. **Is the logic complete?** No dangling TODO, no empty conditional branch, no silently
   swallowed error.
3. **Is there dead code?** Unused variables, extra imports, functions nobody calls → delete.

## Measurable thresholds

- Cyclomatic complexity ≤ 10 per function (every language).
- Cognitive complexity ≤ 15 per function; the C family (C, C++, Objective-C) ≤ 25.
- A function over the threshold → split it, NEVER widen the threshold in place.
- How to override a threshold: only by one line in the request's spec (with the new number and
  the reason), because every tool's default differs; overriding by a spoken agreement in chat
  is banned.

## What to do

1. Open `index.md`, look up the extension of the file you are editing → load that language's
   rule file.
2. Write the code per that language file's "What to do" section; name things per the language's
   standard.
3. Walk the short OWASP checklist: validate input at the boundary, hardcode no secret/API key,
   errors must be handled or logged and rethrown — an empty `catch` is banned.
4. Run the linter command from the `index.md` table; if the machine lacks the
   linter, write "not checked yet" and never write PASS.

## Self-check

- [ ] No function exceeds cyclomatic ≤ 10, cognitive ≤ 15 (C family ≤ 25)
- [ ] All 3 Intentionality questions above are answerable for the file just changed
- [ ] No secrets, no dead code, no dangling TODO
- [ ] The linter ran (or "not checked yet" was recorded because the machine lacks it)

## RIGHT/WRONG examples

```python
# WRONG — vague name, swallowed error, empty branch (all 3 Intentionality faults):
def process(d):
    try:
        r = do(d)
    except Exception:
        pass  # TODO
# RIGHT — the name states the work, the error is logged and rethrown:
def extract_error_lines(log_text):
    try:
        return [d for d in log_text.splitlines() if "ERROR" in d]
    except UnicodeDecodeError as err:
        logging.error("log_text has a broken encoding: %s", err)
        raise
```
