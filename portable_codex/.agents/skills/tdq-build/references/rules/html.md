# HTML rules

Soul: chất lượng > runtime > context cost <!-- i18n-allow: canonical Soul line -->. Load after `chung.md`; applies to `.html .htm`.

## Sources

- W3C Markup Validation Service — https://validator.w3.org/ — W3C's official validator; the Nu
  version is not DTD-based for HTML5: https://validator.w3.org/nu (use it for new pages).
- HTMLHint — the official rule catalogue https://htmlhint.com/rules/ — rules with concrete IDs:
  `doctype-first`, `doctype-html5`, `head-script-disabled`, `alt-require`, `id-unique`,
  `input-requires-label`, `attr-no-duplication`, `title-require`, `src-not-empty`.

## When it applies

- Writing or changing an `.html`/`.htm` file, templates and static docs pages included.
- JS inside a page's `<script>` tag is reviewed under `typescript-js.md`, not under this file.

## The Intentionality rule

1. **A tag must state its role**: use the semantic element for the job instead of stacking
   `div`s; off-standard tags and attributes are markup that cannot express intent to a machine
   reader.
2. **Missing alt/label hides intent from users**: every `img` has an `alt` (`alt-require`) and
   every `input` has a `label` (`input-requires-label`) — missing them blocks both
   accessibility and machine understanding of the page.
3. **Duplication is contradictory intent**: `id` must be unique (`id-unique`), attributes must
   not repeat within a tag (`attr-no-duplication`), `src` must not be empty (`src-not-empty`).

## Measurable thresholds

- HTML has no cyclomatic/cognitive measure — this file's threshold is **0 validator errors**
  and **0 HTMLHint errors** on the rule set listed under Sources.
- A new page must use the HTML5 doctype (`doctype-html5`) with the doctype first in the file
  (`doctype-first`).

## What to do

1. Open the file with `<!DOCTYPE html>`; the page has a `<title>` (`title-require`).
2. Do not put `<script>` in `<head>` unless required (`head-script-disabled`) — render-blocking
   scripts go at the end of `<body>`.
3. Write attribute pairs fully, in double quotes; every `img` has an `alt`, every `input` has a
   `label`, and no `id` repeats.
4. Public pages get validated through https://validator.w3.org/nu before delivery.
5. Run `htmlhint <path>` with the rule set under Sources; if the machine lacks htmlhint,
   write "not checked yet".

## Self-check

- [ ] `htmlhint` clean on the chosen rule set, or "not checked yet" recorded
- [ ] HTML5 doctype first in the file; a `title` is present
- [ ] Every `img` has `alt`; every `input` has a `label`; every `id` is unique
- [ ] The 3 Intentionality questions in `chung.md` are answerable

## RIGHT/WRONG examples

```html
<!-- WRONG — no doctype, img without alt, duplicated id: -->
<div id="a"><img src="logo.png"></div>
<div id="a"><input type="text"></div>
<!-- RIGHT — doctype first in the file, alt and label present, id unique: -->
<!DOCTYPE html>
<img src="logo.png" alt="TDQ logo">
<label for="name">Name</label><input id="name" type="text">
```
