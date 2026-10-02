# The user-facing block: the symbol table and a BEFORE/AFTER example

Split out of `user-facing-block.md` on 2026-10-02 (965 tokens). Both parts are lookup material: the
symbol table is opened when you are unsure whether a mark is allowed; the example when you want to
compare the block you just wrote against a correct one. The rules themselves — the six components,
the eight laws, the hard rules — stay in the parent file.

## The symbols allowed

A block printed for the user may use exactly six non-ASCII symbols:

| Character | Codepoint | Used for |
|---|---|---|
| `➤` | U+27A4 | opens the answer-guidance line, always the last line |
| `·` | U+00B7 | separates two equal halves on one line |
| `—` | U+2014 | separates an explanation from the thing explained |
| `→` | U+2192 | points from one state to the next |
| `–` | U+2013 | joins the two ends of a range |
| `…` | U+2026 | cuts short a repeated part in an example |

A character outside the table must not be added, however harmless it looks. `▸` is excluded for
exactly that reason. It has never appeared in any string of this codebase, so there is no evidence
it renders correctly on all three surfaces. Box-drawing characters
(`─` `│` `├` `└` `┌` `┬` `┐`) are banned too: they demand column alignment, and terminal width
varies. The machine checks this with `python3 scripts/scan_block_symbols.py --chi-khoi`.

## Examples

The same content, differing only in decoration. The `Sau` version changes not one word of the
`Truoc` version — it only adds bold markers, backticks and line breaks. Both samples are written
in the default language (`doc_lang = vi`).

### Before (`Trước`) <!-- i18n-allow -->

<!-- i18n-allow — the "Trước" block is deliberately off-shape: it is the counter-example, not a template to copy. -->

```
Tôi đã viết xong spec cho yêu cầu của bạn.

Mục tiêu: <1–2 câu>.
Đầu ra chính: <gạch đầu dòng ngắn>.
Rủi ro đáng chú ý: <gạch đầu dòng ngắn>.

Xem đầy đủ tại: docs/tdq/spec/<slug>.md

---

**Bạn duyệt spec này chứ?**

➤ Duyệt: nhắn "duyệt spec" (duyệt xong tôi viết plan ngay) · Góp ý: nhắn trực tiếp
```

### After (`Sau`) <!-- i18n-allow -->

<!-- i18n-allow: khuôn mẫu viết bằng ngôn ngữ mặc định, chép nguyên văn khi doc_lang = vi -->

```
Tôi đã viết xong spec cho yêu cầu của bạn.

**Mục tiêu:** <1–2 câu>.
**Đầu ra chính:** <gạch đầu dòng ngắn>.
**Rủi ro đáng chú ý:** <gạch đầu dòng ngắn>.

Xem đầy đủ tại: `docs/tdq/spec/<slug>.md`

---

**Bạn duyệt spec này chứ?**

➤ Duyệt: nhắn "duyệt spec" (duyệt xong tôi viết plan ngay) · Góp ý: nhắn trực tiếp

---
```

The second `---` is component 6, the closing rule of the turn. The `Trước` version has only the
first one, which is part of what makes it the counter-example.
