# Archify artifact lifecycle
<!-- muc-luc-dong:
  Before code=8-17 · Refresh Master=18-30 · Evidence for report=31
-->

Load before implementation when the approved spec or mini-plan includes an Archify manifest, and again after source changes or merge. Do not create another approval gate.

## Before code

Use the approved document, not a regenerated design. From the target project root:

```sh
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_archify.py" verify --document "<approved-document.md>" --manifest "<preview.manifest.json>"
```

On stale or invalid binding, identify whether the document, candidate, artifact or source changed. Do not treat stale output as current or rewrite approved binding silently. A design change follows the existing spec/quick approval. Preserve the original approval snapshot when adding progress-only ticks. No manifest means the request used text fallback; record that rather than claiming visual verification.

## Refresh Master

Finish checks freshness and writes a separate status file; it does not call an AI endpoint or automatically turn planned task diagrams into committed architecture. The agent must read the relevant source changes and author a new model.

```sh
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_archify.py" status
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_archify.py" sync-master --model "docs/tdq/artifacts/master/model.json" --project "." --out "docs/architecture"
```

The model inventories modules and coverage, identifies unknown/excluded areas and lists views with relative candidate paths. Use `committed` only for a verified clean source snapshot at the declared Git revision. Use `working-tree` for uncommitted bytes and `planned` for proposed behavior. Do not invent committed citations for either. Recheck the destination revision after merge; source changes outside workflow are detected only on the next status/finish/refresh invocation.

Retain last-good output if any required view fails. An existing lock is not permission to delete it: establish ownership before recovery. A diagram's motion is illustrative, not a runtime trace. `compare` visualizes differences, never merges the model.

## Evidence for report

Author `docs/tdq/reports/<slug>.html` from actual task, DoD, QC, outputs and limits. Render it with `tdq_archify.py render --type explainer --candidate docs/tdq/artifacts/<slug>/bao-cao.archify.md --out docs/tdq/reports/<slug>.html --document docs/tdq/reports/<slug>.md --request <slug> --lane <quick|full> --evidence-kind working-tree`; use `committed` only with a verified clean revision. The CLI accepts only `planned`, `working-tree`, `committed`, `partial` — never pass `actual`. In prose, describe verified outcomes as actual, not proposed; the manifest's evidence kind describes source provenance. Verify manifest binding before linking. Keep candidate, manifest, engine receipt, command exit and test evidence together. A missing, failed or stale Archify artifact is a disclosed fallback; never link it as current. Report static gates, native browser gates and visual review separately. Finish every background check before concluding PASS. Missing engine, native browser pipe failure or timeout is not success; give recovery instructions and preserve unresolved status. Never disable browser sandbox just to obtain a green receipt.
