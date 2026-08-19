# HTML rules

Soul: chất lượng > runtime > context cost. Load after `chung.md`; applies to `.html .htm`.

## Nguồn

- W3C Markup Validation Service — https://validator.w3.org/ — W3C's official validator; the Nu
  version is not DTD-based for HTML5: https://validator.w3.org/nu (use it for new pages).
- HTMLHint — the official rule catalogue https://htmlhint.com/rules/ — rules with concrete IDs:
  `doctype-first`, `doctype-html5`, `head-script-disabled`, `alt-require`, `id-unique`,
  `input-requires-label`, `attr-no-duplication`, `title-require`, `src-not-empty`.

## Khi nào áp dụng

- Writing or changing an `.html`/`.htm` file, templates and static docs pages included.
- JS inside a page's `<script>` tag is reviewed under `typescript-js.md`, not under this file.

## Luật Intentionality

1. **A tag must state its role**: use the semantic element for the job instead of stacking
   `div`s; off-standard tags and attributes are markup that cannot express intent to a machine
   reader.
2. **Missing alt/label hides intent from users**: every `img` has an `alt` (`alt-require`) and
   every `input` has a `label` (`input-requires-label`) — missing them blocks both
   accessibility and machine understanding of the page.
3. **Duplication is contradictory intent**: `id` must be unique (`id-unique`), attributes must
   not repeat within a tag (`attr-no-duplication`), `src` must not be empty (`src-not-empty`).

## Ngưỡng đo được

- HTML has no cyclomatic/cognitive measure — this file's threshold is **0 validator errors**
  and **0 HTMLHint errors** on the rule set listed under Nguồn.
- A new page must use the HTML5 doctype (`doctype-html5`) with the doctype first in the file
  (`doctype-first`).

## Làm gì

1. Open the file with `<!DOCTYPE html>`; the page has a `<title>` (`title-require`).
2. Do not put `<script>` in `<head>` unless required (`head-script-disabled`) — render-blocking
   scripts go at the end of `<body>`.
3. Write attribute pairs fully, in double quotes; every `img` has an `alt`, every `input` has a
   `label`, and no `id` repeats.
4. Public pages get validated through https://validator.w3.org/nu before delivery.
5. Run `htmlhint <đường dẫn>` with the rule set under Nguồn; if the machine lacks htmlhint,
   write "chưa kiểm được".

## Tự kiểm

- [ ] `htmlhint` clean on the chosen rule set, or "chưa kiểm được" recorded
- [ ] HTML5 doctype first in the file; a `title` is present
- [ ] Every `img` has `alt`; every `input` has a `label`; every `id` is unique
- [ ] The 3 Intentionality questions in `chung.md` are answerable

## Ví dụ ĐÚNG/SAI

```html
<!-- SAI — thiếu doctype, img không alt, id trùng: -->
<div id="a"><img src="logo.png"></div>
<div id="a"><input type="text"></div>
<!-- ĐÚNG — doctype đầu file, alt và label đầy đủ, id duy nhất: -->
<!DOCTYPE html>
<img src="logo.png" alt="Logo TDQ">
<label for="ten">Tên</label><input id="ten" type="text">
```
