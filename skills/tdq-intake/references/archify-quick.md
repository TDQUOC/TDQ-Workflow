# Archify BA preview for the quick pipeline

Load whenever the request changes something that already exists (extended feature, bugfix, refactor, update), before presenting the merged mini-plan. The current agent writes the candidate; no external AI endpoint is required. There is no extra approval gate: the preview belongs to the existing quick approval.

Keep the BA focused on the actor, trigger, input, rules, main flow, exception paths, output and acceptance criteria of this change. Do not remove required behavior to fit a node cap. A larger graph may use several views with explicit scope.

Same page shape as the deep pipeline — section `Before and after on one page` of [archify-ba.md](../../tdq-spec/references/archify-ba.md): one explainer with the current flow before the flow after the update, diagrams first, text supporting only. Brand-new feature: `Hiện trạng: chưa có`, after diagrams only. Store candidate sources outside the plan Markdown namespace, for example `docs/tdq/artifacts/<slug>/truoc-sau.archify.md`. Label existing code with verifiable evidence, proposed changes planned, unknowns explicitly.

From the target project root:

```sh
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_archify.py" check
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_archify.py" render --type explainer --candidate "docs/tdq/artifacts/<slug>/truoc-sau.archify.md" --out "docs/tdq/plan/<slug>-flow.html" --document "docs/tdq/plan/<slug>.md" --request "<slug>" --lane quick --evidence-kind planned
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_archify.py" verify --document "docs/tdq/plan/<slug>.md" --manifest "docs/tdq/plan/<slug>-flow.manifest.json"
```

Always render Archify preview for express pipeline; for a brand-new feature with nothing before, write `Hiện trạng: chưa có` after diagrams only.
`approve quick` enforces that `docs/tdq/plan/<slug>-flow.manifest.json` is `current` for requests opened after mốc `2026-11-09-0143`. If the flow manifest is missing or stale, `approve quick` refuses approval. Bypass via `--bo-qua-archify "<reason>"` is available only with user agreement.
