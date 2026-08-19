# Phần B — Phân tích (phase `analyze`, chỉ chế độ chuyên sâu (deep))

Play the expert of the exact field the request belongs to. Goal: leave this phase with
**ZERO guesswork**. Everything written in this phase lives in ONE file
`docs/tdq/brief/<slug>.md`, with exactly 3 sections: `## Nguyên văn` (the user's request,
already written in Part A), `## Hiểu & kiến thức`, `## Hỏi đáp`.

1. **Capability inventory (B0).** Run
   `python3 "${CLAUDE_PROJECT_DIR}/.claude/tdq/scripts/skill_inventory.py" --loc "<từ khoá của yêu cầu>"`;
   the filtered view always keeps every skill from source `project` and
   `plugin:tdq-workflow`. Suspect something is missing → re-run with `--tat-ca` for the
   full table. Add the built-in skills you can see in context, then fill the verdict table
   per the khuôn in [skill-inventory.md](skill-inventory.md) into the brief under
   `## Hiểu & kiến thức` → `### Năng lực dùng được`. In doubt → USE it.

2. **Read the code.** Find everything this request touches: entry point, data flow,
   config, tests. Write down the versions and frameworks in use.

   **Architecture profile — generated once per project.** Open `docs/kien-truc.md`.
   Already there → read it fully before writing a single line of analysis. Not there →
   generate a draft in this phase, then have the user settle it; until settled every line
   in it is a suggestion, not a rule. The draft has exactly 4 sections. `## Tầng`: one
   line per layer with its responsibility. `## Luật gọi`: the "layer X must not call layer
   Y" lines with reasons. `## Hub`: the 5 most connected nodes with their degree, taken
   from `graphify god-nodes`; editing one of them is high risk and must be declared on the
   plan's `Chạm:` line. `## Đã chốt`: closed decisions with their date; changing one needs
   its own request. Sources: the directory tree + `graphify god-nodes` + build config.

   **When to READ the graphify graph** (conditional advice, NOT mandatory every analyze):
   - OPEN the graph when the question is about **links** or about the **overall map**.
     That means: "who calls X", "what breaks if I change X", "how are these two connected",
     "which clusters does the project have". Commands: `graphify query|path|explain|affected`.
   - USE grep/read when the question is finding a string, reading a file, or looking at
     specific content — faster, and it does not depend on how fresh the graph is.
   - The graph holds product source only (`scripts/`, `hooks/`); `tests/` and docs are
     excluded by `.graphifyignore`. Need a test or a doc → grep, don't wait for the graph.

3. **Research from several angles — hand it to a subagent.** 2–4 queries from different
   angles through `tavily-primary` (failover rule in
   [tavily.md](../../tdq-conventions/references/tavily.md)). By default hand it to one
   `general-purpose` sub-agent: the agent runs the queries itself, writes
   `docs/tdq/research/<slug>.md` itself (query → source → what follows), and returns a
   **digest ≤ 1.500 ký tự** to the main conversation.
   Raw tavily results left sitting in context cost ~14M tokens per 2 sessions — that is
   why this is mandatory.
   Exception, do it yourself: a single query, or a URL you already know (use `WebFetch`).
   Skip the step only when the work is purely internal, with no external unknown.

4. **Interview rounds — general first, detail after.** Run the **scope round** first per
   [scope-round.md](scope-round.md): which areas the request spans, what the context looks
   like in numbers, and from that infer the investment level. The scope round is
   conditional; skip it and the reason goes into the brief. Only then the detail round:
   list EVERY question that changes the outcome (scope, UX, data, errors, performance,
   compatibility) but only inside the areas the user chose. How to ask:
   [interview.md](interview.md).
   Write question–answer pairs into the brief under `## Hỏi đáp`. **Repeat** until no
   question left can change the outcome — several rounds is normal. Never fill a gap with
   a guess.

5. **Settle the knowledge.** Write into the brief under `## Hiểu & kiến thức`: settled
   decisions, constraints, the chosen approach + why, the rejected options + why, sources.

5b. **Decide the route.** Add `### Lộ trình` to that section: a table `Bước/phase | CÓ-BỎ |
   Vì sao` for each remaining step (extra research, independent QC by an agent, deep
   review, splitting across subagents…). The invariant frame that can never be dropped:
   analysis → spec/plan → implement → report. Cut only the steps that are REDUNDANT for
   this particular task, and say why; in doubt → KEEP. This route is copied verbatim into
   spec §1b, and approving the spec approves it too.

6. **Gate check** before moving on:
   - Is the final scope clear: what gets built, what is new, what exactly is the output?
   - Is any model / download / installation needed?
   - Is the QC/test/validate scope defined?
   Any item missing → back to step 4.

Xong khi: `brief/<slug>.md` has all 3 sections (including `### Lộ trình`) and all 3 gate
questions can be answered.
Bước kế tiếp: `python3 "${CLAUDE_PROJECT_DIR}/.claude/tdq/scripts/tdq_state.py" set phase=spec`
then on to [tdq-spec](../../tdq-spec/SKILL.md) — same turn if the interview is finished;
if questions remain, present them and stop.
