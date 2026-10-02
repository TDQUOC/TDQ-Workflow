# Shared rules for every language
<!-- muc-luc-dong:
  Table of contents=16-26 · Sources=27-39 · When it applies=40-45 · The Intentionality rule=46-55 ·
  Measurable thresholds=56-66 · The build-less-than-asked law=67-75 ·
  The ladder — stop at the first rung that holds=76-93 · Make it run first, refactor after=94-101 ·
  The ladder only chooses among options that already pass the floor=102-109 ·
  Two ordered passes, never one merged judgement=110-121 · Never simplify these away=122-133 ·
  Say out loud what you climbed past=134-139 · Intensity table=140-150 ·
  Extra at level ultra=151-156 · RIGHT / WRONG for this law=157-208 · What to do=209-219 ·
  Self-check=220-226 · RIGHT/WRONG examples=227
-->

Soul: chất lượng > runtime > context cost <!-- i18n-allow: canonical Soul line --> · luật gốc: skills/tdq-conventions/references/soul.md
Load this file FIRST, then the language rule file from the table in `index.md`.

## Table of contents

- [Sources](#Sources)
- [When it applies](#When it applies)
- [The Intentionality rule](#The Intentionality rule)
- [Measurable thresholds](#Measurable thresholds)
- [The build-less-than-asked law](#The build-less-than-asked law)
- [What to do](#What to do)
- [Self-check](#Self-check)
- [RIGHT/WRONG examples](#RIGHT/WRONG examples)

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

<!-- luat-gon:bat-dau -->

## The build-less-than-asked law

It applies every time you are about to CREATE something that does not exist yet: a file, a
class, a function, a constant, a config key, a dependency, an abstraction layer, a wrapper.
It applies again every time a task could be finished by editing something that already exists
instead. It does
NOT apply to the shape of code that has already earned the right to exist: that is SOLID's job,
and SOLID runs after this law, never against it.

### The ladder — stop at the first rung that holds

| Rung | Question | When it holds |
|---|---|---|
| 1 | Does this need to exist at all? | Skip it and say so in one line. A need you inferred rather than read is speculative, and a thing that already EXISTS anywhere in the repo fails this rung too |
| 2 | Is it already in this codebase? | Use it. Search before writing: `mcp__lsp__find_symbol` on the name plus two synonyms, then one round of lumen or grep |
| 3 | Does the standard library do it? | Use it |
| 4 | Does a native platform feature cover it? | Use it — a DB constraint over application code, CSS over JS, a shell builtin over a helper script |
| 5 | Does an already-installed dependency solve it? | Use it. Never add a new dependency for what a few lines can do |
| 6 | Can it be one line? | Then it is one line |
| 7 | Only then | Write the smallest code that works |

Found something close at rung 2 and creating anyway → write
`Tạo mới thay vì dùng <đường dẫn> vì <lý do>` <!-- i18n-allow: canonical note written into the plan --> into the plan task.
The ladder runs AFTER you understand the problem, never instead of understanding it: read the
task, read the code it touches, trace the real flow end to end, and only then climb. The
smallest change in the wrong place is not laziness, it is a second bug.

### Make it run first, refactor after

Step 1 is code that runs. Tidying the project up comes after the feature is done and behaving.
Write the simplest, most direct code you can — minimal, with no namespace, no class and no
function the feature does not need, so the path of one feature never reads like a spider's web.
Refactor only once the feature works; refactoring first is the same mistake as building what
nobody asked for, wearing a cleaner shirt.

### The ladder only chooses among options that already pass the floor

The rungs pick between candidates that are ALL already correct. A candidate that crosses the
thresholds above (cyclomatic ≤ 10, cognitive ≤ 15, C family ≤ 25) was never a candidate, so a
rung reachable only by crossing them is not a rung: climb to the next one. There is deliberately
no escape hatch — no comment, no annotation and no declared "known ceiling" buys an exception to
the floor, because an option that fails the floor was never one of the options.

### Two ordered passes, never one merged judgement

| Pass | Question it answers | Law that owns it |
|---|---|---|
| 1 | Should this thing exist at all? | this law |
| 2 | What shape should the surviving thing have? | SRP and the rest of SOLID, in `skills/tdq-conventions/references/clean-code.md` |

Pass 1 can delete a whole file; pass 2 can split one function into two. They never argue,
because they answer different questions in a fixed order. A function that both fetches data and
judges it still gets split by SRP in pass 2 — the ladder has no opinion there, because that
function already earned the right to exist in pass 1.

### Never simplify these away

Input validation at a trust boundary · error handling that prevents data loss · the OWASP walk
in this file · accessibility basics · anything the user explicitly asked for, an explanation they
asked for included. Two more are settled by user ruling on 2026-09-16:

- **The log service.** Every product this workflow builds ships with logging on by default,
  timestamped, detailed enough to debug the event and its data, switchable off through config.
  It is a standing requirement of the workflow, so it counts as explicitly requested and no rung
  can ever reach it.
- **The unit test of every task, red → green. No exemption, not even for a one-line change.**

### Say out loud what you climbed past

Stopping above rung 2 → one line in chat and in the working log: the rung you stopped at, and
why the rung below it failed. That line is mandatory at `muc_gat` = `ultra`; at `lite` and
`full` it is mandatory only when you created a new file.

### Intensity table

| `muc_gat` | The ladder | This table and the examples | The say-out-loud line |
|---|---|---|---|
| `off` | off — only an explicit user request selects it, and every new request starts back at `full` | not loaded | not required |
| `lite` | on | not loaded | new file only |
| `full` (the default) | on | loaded | new file only |
| `ultra` | on | loaded | always |

An unreadable or unknown value behaves as `full`. No reasoning of yours can select `off`.

### Extra at level ultra

Name the rung on EVERY creation, not only for a new file, and list in the working log what you
decided not to build. At this level a diff that adds a file with no rung line recorded is a QC
defect on its own.

### RIGHT / WRONG for this law

The ladder against the floor is the single easiest thing here to read wrong, so it gets the
example. The task: parse a config value that may be a plain number, a string with a unit
suffix, or a nested object with an explicit unit key.

WRONG — the ladder used to justify crossing the floor:

```python
# "Rung 6: can it be one line?" -> made it one line.
def parse(v):
    return (v if isinstance(v, (int, float)) else int(v[:-1]) * {"s": 1, "m": 60, "h": 3600}[v[-1]] if isinstance(v, str) and v[-1] in "smh" else int(v["value"]) * {"s": 1, "m": 60, "h": 3600}[v["unit"]] if isinstance(v, dict) and "unit" in v else int(v))
```

It is one line and it is smaller, but its cognitive complexity is over the floor and nobody can
change it safely. A candidate that breaks the floor was never a candidate, so rung 6 did not
hold here and the honest answer was to climb on to rung 7.

RIGHT — the lowest rung that holds AND passes the floor:

```python
UNITS = {"s": 1, "m": 60, "h": 3600}


def parse(value):
    """Config duration -> seconds. Number, "30m", or {"value": 30, "unit": "m"}."""
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, dict):
        return int(value["value"]) * UNITS[value["unit"]]
    if value[-1] in UNITS:
        return int(value[:-1]) * UNITS[value[-1]]
    return int(value)
```

Rung 7, the smallest code that works, four flat branches, under both thresholds. No parser class
(rung 1 held against it), no new dependency (rung 5), and no "strategy" abstraction for three
cases nobody will extend.

WRONG — the other direction, the ladder ignored entirely:

```python
class DurationParser(AbstractConfigParser):
    def __init__(self, registry: UnitRegistry, strategy: ParseStrategy = DefaultStrategy()):
        ...
```

Nobody asked for a registry, a strategy or an abstract base. Rung 1 alone removes all three.
This is the failure mode the law exists for, and the one a model reaches for most often.

<!-- luat-gon:ket-thuc -->

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
