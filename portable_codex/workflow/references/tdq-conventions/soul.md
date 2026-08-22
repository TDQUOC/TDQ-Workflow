# Soul — the root law of TDQ Workflow

Soul stands above every other law in the workflow. A law that contradicts soul — old or new —
is the law that gets fixed; soul does not. Changing soul requires the user's approval.

## Table of contents

- The four principles
- When it applies
- What to do
- Which tier a law belongs to
- Self-check

## The four principles

### 1. What the harness is for

The harness exists to help a dev use AI to produce better, more finished results. Quality over
quantity: one product that runs correctly, reads well and survives is worth more than many
half-done ones.

### 2. Priority order: chất lượng > runtime > context cost <!-- i18n-allow: canonical wording -->

Read in English: quality first, then runtime, then context cost. The Vietnamese wording above is
the canonical string — it is the one copied into the `Soul:` line of every request document.

- **Tier 1 — quality**: the code the agent produces must be a real MVP — it runs, it has
  tests, and no foreseeable technical debt is left undeclared.
- **Tier 2 — runtime**: how long the workflow and the product take to run. Optimise only when
  it does not lower tier 1.
- **Tier 3 — context cost**: tokens fed to the model. Cut only when it lowers neither tier
  above.

**Tie-break law** when two laws collide:
1. The law serving the higher tier wins.
2. Same tier → pick the law whose check can be run as a command.
3. Still tied → ask the user, and record the ruling in the open request's documents.

### 3. Write for the weakest model

Every rule and behaviour must be detailed enough that a low model like Haiku reads it and does
the right thing — not only a high model like Opus. A rule meets the bar when it has all three
sections: `## When it applies` (signs recognisable by eye or by command),
`## What to do` (numbered steps, one action per step, imperative sentences),
`## Self-check` (one command, or one yes/no question). Anywhere easy to misread must carry a
RIGHT/WRONG example.

### 4. Scope

Soul applies to every skill, every script, every template, and to every document of a request:
brief, spec, plan, qc, report — including the documents of the request that created soul itself.
It applies retroactively to existing laws and to every later addition. Each request document
opens with the line:

<!-- i18n-allow: khuôn dòng Soul chép nguyên văn vào tài liệu -->
```
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
```

## When it applies

Signs — hitting any one of these means soul is present:

- About to write or change a law, a skill, a document template, or a workflow script.
- Two laws point in different directions on the same piece of work.
- About to cut a step (test, QC, log, research) to run faster or to save tokens.
- About to open a new request document (brief, spec, plan, qc, report).

## What to do

1. Place the work in its tier: quality, runtime, or context cost.
2. Check: does this change lower a higher tier? Yes → stop, follow the higher tier.
3. Write the new rule in the three-section shape from principle 3; add a RIGHT/WRONG example
   wherever it is easy to misread.
4. Opening a new request document → put the `Soul:` line at the top of the file, right under
   the title.
5. Two laws collide → run the tie-break law in principle 2 and record the ruling.

RIGHT example: dropping a duplicate research round because the result is already in the brief —
saves tokens without losing information (tier 3 serving tier 1).
WRONG example: dropping the write-the-test-first step to build faster — runtime overriding
quality.

## Which tier a law belongs to

Filing a law in the wrong tier is how a correct law gets legitimately ignored: a law that cuts
time but is labelled "saves tokens" drops to tier 3 — the lowest tier, the one you may skip when
busy. So before writing or changing any law, ask: **which number does this law change?**

| Which number the law changes | Tier | Example |
|---|---|---|
| The correctness of the output | 1 — quality | test before fixing, no fake mock passed off as real data |
| The NUMBER OF STEPS (tool calls, waiting rounds) | 2 — runtime | batch independent tool calls, no `sleep` polling loop |
| The NUMBER OF TOKENS loaded into the model | 3 — context cost | lint the exact file instead of the whole tree, terse CLI output |

A law that changes several numbers is filed in the **highest** tier it touches. The batch-the-
tool-calls law cuts both steps and tokens → tier 2, not tier 3.

Consequence for placement: tier 1 and tier 2 laws must live in the body of a skill loaded every
turn; only tier 3 laws and detailed tables get pushed into a reference file. A skill's line cap
is a tier 3 constraint — hitting the cap means raising the cap, never compressing a tier 2 law
to fit.

## Self-check

- Yes/no question: "Does the change I am about to make lower quality in exchange for speed or
  tokens?" — Yes → do not make it.
- Yes/no question: "The rule I just wrote — hand it to Haiku with no spoken explanation, would
  it do the right thing?" — No → rewrite it in the three-section shape.
- Command: `python3 -m pytest tests/test_soul_rules.py -q` must be green.
