# Archify BA preview for the full pipeline

Load while authoring a full spec, before presenting its approval gate. The current agent authors the candidate; Archify validates and renders it locally. No separate AI endpoint or credential is required. There is no extra approval gate.

## Author the BA

Record the actor, trigger, inputs, business rules, happy path, exceptions/fallbacks, outputs and acceptance criteria. Derive existing responsibilities from evidence; label proposed behavior as planned and unresolved claims as unknown. Choose architecture for components, workflow for business steps, sequence for ordered messages, lifecycle for states and ERD for data. Do not drop behavior to meet an arbitrary node count; split views instead.

Read the installed Archify SKILL.md and the selected schema/example. Keep candidates and receipts outside the spec Markdown namespace, for example under `docs/tdq/artifacts/<slug>/`. Use committed citations only against their actual revision; sources use `path`, `line`, `end_line`. Never invent a repository URL or source for planned code.

## Render and bind before approval

Run from the target project's root, using the plugin's absolute CLI path. Check Node and Archify first. Replace placeholders with actual paths; the command is a template, not evidence that it ran.

```sh
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_archify.py" check
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_archify.py" render --type workflow --candidate "docs/tdq/artifacts/<slug>/candidate.json" --out "docs/tdq/spec/<slug>-preview.html" --document "docs/tdq/spec/<slug>.md" --request "<slug>" --lane full --evidence-kind planned
```

Finish the spec's content before rendering/binding. The CLI writes a manifest beside the HTML and binds its hash to the document. Any later content edit requires rerender/rebinding before presentation. After approval, do not rewrite the binding silently: a design change needs the existing spec approval again.

Only show a preview link when the command succeeded and the output exists. A failed gate, missing engine or unavailable browser must be disclosed; keep the textual BA/Mermaid as a labelled fallback, never present an old HTML as newly verified. Native browser checks and explainer checks differ; distinguish static validation from actual visual inspection.

```sh
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_archify.py" verify --document "docs/tdq/spec/<slug>.md" --manifest "docs/tdq/spec/<slug>-preview.manifest.json"
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_archify.py" open "docs/tdq/spec/<slug>-preview.html"
```

Plan references the approved preview and manifest rather than creating another design. No HTML asset replaces the spec's measurable requirements. A standalone HTML is a snapshot, not a live project scanner.
