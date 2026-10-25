# Archify BA preview for the quick pipeline

Load when the request affects at least two modules or refactors architecture, before presenting the merged mini-plan. The current agent writes the candidate; no external AI endpoint is required. There is no extra approval gate: the preview belongs to the existing quick approval.

Keep the BA focused on the actor, trigger, input, rules, main flow, exception paths, output and acceptance criteria of this change. A tiny single-module edit may use text/Mermaid instead; record why. Do not remove required behavior to fit a node cap. A larger graph may use several views with explicit scope.

Read the installed Archify authoring reference and selected schema. Store candidate sources outside the plan Markdown namespace, for example `docs/tdq/artifacts/<slug>/candidate.json`. Label proposed changes planned, existing code with verifiable evidence, and unknowns explicitly.

From the target project root:

```sh
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_archify.py" check
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_archify.py" render --type workflow --candidate "docs/tdq/artifacts/<slug>/candidate.json" --out "docs/tdq/plan/<slug>-flow.html" --document "docs/tdq/plan/<slug>.md" --request "<slug>" --lane quick --evidence-kind planned
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_archify.py" verify --document "docs/tdq/plan/<slug>.md" --manifest "docs/tdq/plan/<slug>-flow.manifest.json"
```

Show the HTML link in the existing short summary only after successful delivery. If Node/Archify/browser is unavailable, disclose the missing verification and keep the textual BA; do not output a nonexistent or stale preview link. Binding uses the finished mini-plan before approval. Verify again before code; changing approved design requires the existing quick approval, not a new diagram gate. Progress tick edits may invalidate the binding: preserve the approval snapshot and distinguish progress-only updates from a changed design rather than silently rebinding.
