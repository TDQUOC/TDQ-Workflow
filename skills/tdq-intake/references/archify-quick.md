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

Show the HTML link in the existing short summary only after successful delivery. If Node/Archify/browser is unavailable, disclose the missing verification and keep a textual before/after (two Mermaid blocks); do not output a nonexistent or stale preview link. Binding uses the finished mini-plan before approval. Verify again before code; changing approved design requires the existing quick approval, not a new diagram gate. Progress tick edits may invalidate the binding: preserve the approval snapshot and distinguish progress-only updates from a changed design rather than silently rebinding.
