# DRAFT — The build-less-than-asked law

Soul: chất lượng > runtime > context cost <!-- i18n-allow: canonical Soul line --> · root law: skills/tdq-conventions/references/soul.md

**Status: DRAFT.** Nothing here is in force yet. This file is output 2 of the request
`2026-09-16-1447-hop-ponytail-vao-tdq`; the plan for putting it in force is output 1.

**Where each part goes when it is put in force** (reason: the split section of output 1):

| Part | Destination | Tier |
|---|---|---|
| `## What to do` step 1 and step 2, compressed to 4 lines | body of `skills/tdq-build/SKILL.md:1`, section `## Hard rules` | 1 |
| everything else in this file | `skills/tdq-build/references/rules/chung.md:19` | 3 |

## When it applies

- Every time you are about to CREATE something that does not exist yet: a file, a class, a
  function, a constant, a config key, a dependency, an abstraction layer, a wrapper.
- Every time a task could be finished by editing something that already exists instead.
- Every time you are about to write code the user did not ask for, because it "will be
  needed later", "makes it extensible", or "is the proper way".
- It does NOT apply to the shape of code that has already earned the right to exist. That is
  SOLID's job, and SOLID runs after this law, never against it.
- It is on at `muc_gat` = `lite`, `full` (the default), `ultra` and `review`. It is off only
  at `muc_gat` = `off`, which no rule and no reasoning of yours can select: only an explicit
  user request sets it, and every new request starts back at `full`.

## What to do

### Step 1 — climb the ladder, stop at the first rung that holds

<!-- doc-lint: allow R12 — law body stays English by the language tier at docs/kien-truc.md:51 -->
1. **Does this need to exist at all?** A need you inferred rather than read is speculative:
   skip it and say so in one line. The wording is "exist", not "be built": a thing that
   already exists somewhere in the repo also fails this rung.
2. **Is it already in this codebase?** Run `mcp__lsp__find_symbol` on the name plus two
   synonyms BEFORE writing it; the compiler index answers "does this exist" exactly. Empty
   answer, then one round of lumen or grep. Found something close and creating anyway → write
   `Tạo mới thay vì dùng <path> vì <reason>` <!-- i18n-allow: canonical note written into the plan --> into the plan task.
<!-- doc-lint: allow R12 — law body stays English by the language tier at docs/kien-truc.md:51 -->
3. **Does the standard library do it?** Use it.
4. **Does a native platform feature cover it?** A DB constraint over application code, CSS
   over JS, a shell builtin over a helper script.
5. **Does an already-installed dependency solve it?** Use it. Never add a new dependency for
   what a few lines can do.
6. **Can it be one line?** Then it is one line.
7. **Only then:** write the smallest code that works.

<!-- doc-lint: allow R12 — law body stays English by the language tier at docs/kien-truc.md:51 -->
The ladder runs AFTER you understand the problem, never instead of understanding it. Read the
task, read the code it touches, trace the real flow end to end, and only then climb. The
smallest change in the wrong place is not laziness, it is a second bug.

### Step 2 — the ladder only chooses among options that already pass the thresholds

The ladder picks between candidates that are ALL already correct. It never picks a candidate
because that candidate is smaller, when the smaller one breaks a measurable threshold.

<!-- doc-lint: allow R12 — law body stays English by the language tier at docs/kien-truc.md:51 -->
The thresholds are the floor, already fixed in
`skills/tdq-build/references/rules/chung.md:37` (cyclomatic at most 10, every language) and
`skills/tdq-build/references/rules/chung.md:38` (cognitive at most 15, at most 25 for the C
family). A rung that can only be reached by crossing that floor is not a rung; climb to the
next one.

<!-- doc-lint: allow R12 — law body stays English by the language tier at docs/kien-truc.md:51 -->
There is deliberately NO escape hatch. No comment, no annotation and no declared "known
ceiling" buys an exception to the floor, because the ladder never needed one: an option that
fails the floor was never one of the options.

### Step 3 — two ordered passes, never one merged judgement

| Pass | Question it answers | Law that owns it |
|---|---|---|
| 1 | Should this thing exist at all? | this file |
| 2 | What shape should the surviving thing have? | `skills/tdq-conventions/references/clean-code.md:55` (SRP) and the rest of SOLID |

<!-- doc-lint: allow R12 — law body stays English by the language tier at docs/kien-truc.md:51 -->
Pass 1 can delete a whole file. Pass 2 can split one function into two. They never argue,
because they answer different questions in a fixed order. A single function that both fetches
data and judges it still gets split by SRP in pass 2 — the ladder has no opinion on that,
because the function already earned the right to exist in pass 1.

### Step 4 — say out loud what you climbed past

<!-- doc-lint: allow R12 — law body stays English by the language tier at docs/kien-truc.md:51 -->
Whenever you stop above rung 2, one line in chat and in the working log: the rung you stopped
at, and why the rung below it failed. At `muc_gat` = `ultra` this line is mandatory. At
`lite` and `full` it is mandatory only when you created a new file.

### Step 5 — never simplify these away

This law cuts code that should not exist. It never cuts:

- Input validation at a trust boundary.
- Error handling that prevents data loss.
- Security measures, including every item of the short OWASP walk already required at
  `skills/tdq-build/references/rules/chung.md:50`.
- Accessibility basics.
- **The log service.** Every product this workflow builds ships with logging on by default,
<!-- doc-lint: allow R12 — law body stays English by the language tier at docs/kien-truc.md:51 -->
  timestamped, detailed enough to debug the event and its data, switchable off through config.
  It is a standing requirement of the workflow, so by definition it is "explicitly requested"
  and the ladder can never reach it.
- The one runnable check that non-trivial logic leaves behind. Code without its check is
  unfinished, not lazy. Trivial one-liners need no test.
- Anything the user explicitly asked for, including an explanation they asked for.

## Self-check

- Yes/no: "Can I name the rung I stopped at, and say why the rung below it failed?" — No →
  you did not climb the ladder, you guessed.
- Yes/no: "Did I pick the smaller option even though it crosses the complexity floor?" — Yes →
  undo it; step 2 says that option was never a candidate.
- Yes/no: "Is anything in this diff here because it will be needed later?" — Yes → delete it
  and say so in one line.
- Command: the language's own complexity check, from the check-command column named at
  `skills/tdq-build/references/rules/index.md:17`, must report no function over the floor.

## RIGHT / WRONG — the ladder against the thresholds

This is the single easiest thing in this law to read wrong, so it gets the example.

**The task:** parse a config file that may declare a value as a plain number, as a string with
a unit suffix, or as a nested object with an explicit unit key.

WRONG — the ladder used to justify crossing the floor:

```python
# "Rung 6: can it be one line?" -> made it one line.
def parse(v):
    return (v if isinstance(v, (int, float)) else int(v[:-1]) * {"s": 1, "m": 60, "h": 3600}[v[-1]] if isinstance(v, str) and v[-1] in "smh" else int(v["value"]) * {"s": 1, "m": 60, "h": 3600}[v["unit"]] if isinstance(v, dict) and "unit" in v else int(v))
```

<!-- doc-lint: allow R12 — law body stays English by the language tier at docs/kien-truc.md:51 -->
Why it is wrong: this is one line and it is smaller, but its cognitive complexity is over the
floor and nobody can change it safely. Step 2 says a candidate that breaks the floor was never
a candidate — so rung 6 did not hold here, and the honest answer was to climb on to rung 7.

RIGHT — the ladder stops at the lowest rung that holds AND passes the floor:

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

<!-- doc-lint: allow R12 — law body stays English by the language tier at docs/kien-truc.md:51 -->
Why it is right: rung 7, the smallest code that works, with four flat branches — under both
thresholds, and the ladder still did its job. No parser class was created (rung 1 held against
that), no dependency was added (rung 5), and no "strategy" abstraction appeared for three
cases that will never be extended by a stranger.

WRONG — the other direction, the ladder ignored entirely:

```python
class DurationParser(AbstractConfigParser):
    def __init__(self, registry: UnitRegistry, strategy: ParseStrategy = DefaultStrategy()):
        ...
```

Why it is wrong: nobody asked for a registry, a strategy or an abstract base. Rung 1 alone
removes all three. This is the failure mode the law exists for, and it is the one a model
reaches for most often.
