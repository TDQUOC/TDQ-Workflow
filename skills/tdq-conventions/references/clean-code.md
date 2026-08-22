# Clean code — the 5 SOLID principles

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md  <!-- i18n-allow: soul line, doc_lang wording -->

In this workflow clean code is NOT a gate you ask about and NOT one linter run at the end of a
request. It is standing behaviour: every time you write or change code, organise the project,
the script, the function and the class as cleanly as possible, following the 5 SOLID principles.

## Table of contents

- Sources
- When it applies
- What to do
- Self-check

## Sources

- Wikipedia SOLID — https://en.wikipedia.org/wiki/SOLID — Robert C. Martin stated the
  principles in *Design Principles and Design Patterns* (2000); the acronym was coined by
  Michael Feathers around 2004.
- CSCE 315 slides, Texas A&M —
  https://people.engr.tamu.edu/choe/choe/courses/12summer/315/lectures/slide23.pdf —
  SOLID is "a set of principles for object-oriented design (with focus on designing the
  classes)".
- Real Python — https://realpython.com/solid-principles-python — the scope the author states
  is "when you're writing object-oriented code".
- DEV, *Do the SOLID principles apply to Functional Programming?* —
  https://dev.to/patferraggi/do-the-solid-principles-apply-to-functional-programming-56lm
  — the function-and-module reading of SRP, OCP, ISP, DIP.
- DEV, *A Pythonic Guide to SOLID* —
  https://dev.to/ezzy1337/a-pythonic-guide-to-solid-design-principles-4c8i — Barbara Liskov's
  original statement is about objects and subtypes.

## When it applies

Signs — hitting any one of these means this rule is present:

- About to create a new source file, a new class, or a new function.
- About to change an existing function whose body runs past one screen, or that has more than
  three `if` branches.
- About to add an `if`/`elif` branch to handle a new case of something that already exists.
- About to copy a block of code into a second place.
- In phase `implement`, or fixing a QC item.

This rule applies to EVERY language. Numeric thresholds and per-language rules live in
`skills/tdq-build/references/rules/` — load `chung.md` first, then exactly one language file.

## What to do

This repo has 4 `class` declarations against 280 `def` declarations, i.e. it is nearly purely
functional. So each principle has two readings. Read the column matching what you are writing.

| Principle | With classes | Functions/modules only |
|---|---|---|
| SRP | One class has exactly one reason to change. Several responsibilities → split the class. | One function does exactly one thing; one module gathers functions serving one purpose. A function that both fetches data and judges it gets split in two. |
| OCP | Add new behaviour with a subclass or a new implementation, never by editing the old class. | Add a new case as one line of DATA in a table or constant, never as a new branch in a function body. |
| LSP | A subtype substitutes for its parent without breaking the contract. Applies literally only where there is inheritance, or several implementations of one interface. | With no inheritance, read it broadly: every `return` branch of a function returns the same type and the same error contract. This is an INFERENCE made by this repo. |
| ISP | Force nobody to depend on methods they never call. A fat interface gets cut up. | A function's parameters take exactly what it uses. Need a path → take a path, not the whole state object. |
| DIP | High and low layers both depend on one abstraction, never on each other. | Call through one shared entry point (a CLI, a shared function); do not re-implement the details at each call site. |

### SRP

RIGHT — `scripts/tdq_checkstatus.py`: `gom_bang_chung()` only READS the disk, `cham_ca_lech()`
only JUDGES data already read. Changing how it reads is not changing how it scores.

WRONG — one `kiem_tra()` that opens the file, compares the sha, writes the diagnosis and prints
the table. Changing the printed table shape forces editing the file-reading function.

### OCP

RIGHT — `scripts/doc_lint.py`, the `SKILL_LINE_LIMITS` constant: adding a new skill needs one
new data line and `rule_r6()` does not change by a single character.

WRONG — writing `rule_r6()` as a chain of `if skill == "tdq-intake": ... elif skill == "tdq-spec":`
Every new skill forces the function body open again.

### LSP

RIGHT — `scripts/tdq_checkstatus.py`: `doc_state_tho()` returns a 2-element tuple on EVERY
branch, including the missing-file branch and the broken-JSON branch. Callers write exactly one
unpacking.

WRONG — one branch does `return None`, another `return {...}`, a third `raise`. The caller has to
guess, and a wrong guess blows up somewhere else.

Restating the limit: LSP as originally stated is about objects and subtypes. The function
reading above is an INFERENCE by this repo, not a quotation of Liskov — do not cite it as her
words.

### ISP

RIGHT — `scripts/tdq_checkstatus.py`: `_dem_tick(cwd, rel)` takes exactly the plan file's path.
It has no need to know what is in the state, so it does not take the state.

WRONG — `_dem_tick(cwd, state)` digging out `state["plan_file"]` inside. Counting the ticks of any
other plan file then means building a fake state, even in a test.

### DIP

RIGHT — `scripts/tdq_state.py` is the single entry point that writes `docs/tdq/state.json`. Hooks,
skills and every other script go through that CLI; nowhere opens the file itself.

WRONG — a hook that `json.dump`s straight into `docs/tdq/state.json`. Changing the state format
then means editing every site, and missing one leaves two writers silently out of step.

## Self-check

Answer these 5 questions before closing a task that touched source code. Any "no" → fix the
code, not the answer. In phase QC, the answers go into the qc file together with what was fixed.

- SRP: does every function and class I just wrote have exactly one reason to change?
- OCP: could I add one more case with a single data line or a subclass, without opening a function body and without editing the old class?
- LSP: with inheritance, does the subtype substitute for its parent without breaking the contract, and without inheritance, does every `return` branch return the same type and the same error contract?
- ISP: is every parameter I pass in actually used inside?
- DIP: does this go through the existing shared entry point instead of re-implementing the details?
