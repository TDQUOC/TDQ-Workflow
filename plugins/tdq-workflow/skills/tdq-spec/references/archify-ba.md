# Archify BA preview for the full pipeline

Load while authoring a full spec, before presenting its approval gate. The current agent authors the candidate; Archify validates and renders it locally. No separate AI endpoint or credential is required. There is no extra approval gate.

## Author the BA

Record the actor, trigger, inputs, business rules, happy path, exceptions/fallbacks, outputs and acceptance criteria. Derive existing responsibilities from evidence; label proposed behavior as planned and unresolved claims as unknown. Choose architecture for components, workflow for business steps, sequence for ordered messages, lifecycle for states and ERD for data. Do not drop behavior to meet an arbitrary node count; split views instead.

Read the installed Archify SKILL.md and the selected schema/example. Keep candidates and receipts outside the spec Markdown namespace, for example under `docs/tdq/artifacts/<slug>/`. Always customize `meta.legend.entries` and `meta.translations` (`viewer.kind.*`, `legend.architecture.*`, `legend.workflow.*`) to match the domain roles of the system (e.g., `Host Adapters`, `Skills & Agents`, `Lifecycle Hooks`, `CLI Runtime`) instead of leaving Web-App defaults (`Frontend`, `Backend`, `Database`). Use committed citations only against their actual revision; sources use `path`, `line`, `end_line`. Never invent a repository URL or source for planned code.

## Before and after on one page

A request that changes something that already exists (extended feature, bugfix, refactor, update) renders ONE explainer page, `docs/tdq/artifacts/<slug>/truoc-sau.archify.md`, where the diagrams carry the explanation and the text is supporting only:

- One panel per view, before then after: the current architecture/flow (from code you read; its supporting text names the files) next to the same view after the update. Keep node names stable across the pair so the reader sees what moved. The page is a design proposal, so `--evidence-kind planned` applies to the whole page.
- Up to four native diagrams per page (`@workflow`, `@architecture`, `@sequence`…, syntax in Archify `references/explainer-authoring.md`). Diagram ids must differ from panel ids.
- Text under a diagram only says what the diagram cannot: why it changed, an exception.
- A brand-new feature with nothing before: one line `Hiện trạng: chưa có`, after diagrams only.
- Put `@meta locale=en` right under the title (the engine defaults to `zh-CN` chrome). Skip `lane` rows: measured 2026-11-02, a lane workflow inside an explainer rendered 0×0.

Validate before rendering: `node <archify>/bin/archify.mjs validate explainer <candidate>`.

## Render and bind before approval

Run from the target project's root, using the plugin's absolute CLI path. Check Node and Archify first. Replace placeholders with actual paths; the command is a template, not evidence that it ran.

```sh
python3 "${PLUGIN_ROOT}/scripts/tdq_archify.py" check
python3 "${PLUGIN_ROOT}/scripts/tdq_archify.py" render --type explainer --candidate "docs/tdq/artifacts/<slug>/truoc-sau.archify.md" --out "docs/tdq/spec/<slug>-preview.html" --document "docs/tdq/spec/<slug>.md" --request "<slug>" --lane full --evidence-kind planned
```

A request with nothing before and a single view may still render `--type workflow` from `candidate.json`.

Finish the spec's content before rendering/binding. The CLI writes a manifest beside the HTML and binds its hash to the document. Any later content edit requires rerender/rebinding before presentation. After approval, do not rewrite the binding silently: a design change needs the existing spec approval again.

Only show a preview link when the command succeeded and the output exists. A failed gate, missing engine or unavailable browser must be disclosed; keep the textual BA/Mermaid as a labelled fallback, never present an old HTML as newly verified. Native browser checks and explainer checks differ; distinguish static validation from actual visual inspection.

```sh
python3 "${PLUGIN_ROOT}/scripts/tdq_archify.py" verify --document "docs/tdq/spec/<slug>.md" --manifest "docs/tdq/spec/<slug>-preview.manifest.json"
python3 "${PLUGIN_ROOT}/scripts/tdq_archify.py" open "docs/tdq/spec/<slug>-preview.html"
```

Plan references the approved preview and manifest rather than creating another design. No HTML asset replaces the spec's measurable requirements. A standalone HTML is a snapshot, not a live project scanner.

## Approval Gate

`approve spec` enforces that `docs/tdq/spec/<slug>-preview.manifest.json` is `current` (bound and hash-matched) for requests opened after mốc `2026-11-09-0143`. If the preview manifest is missing or stale, `approve spec` exits non-zero and refuses to approve.
Emergency bypass (requires user consent in chat): pass `--bo-qua-archify "<reason>"` to record the bypass in state.
