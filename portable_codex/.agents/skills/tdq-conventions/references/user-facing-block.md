# Shape of a block spoken to the user

Applies to **every** place where TDQ asks a question or presents a result to the user. The reader
is an end user, not a colleague from the trade: they need to know what they are looking at, where
the details are, and how to answer.

Language: every word of the block is written in the language of state field `doc_lang` (default
`vi`). The rules below shape it; they never dictate the wording. Every Vietnamese string quoted
here is a SAMPLE of the shape in the default language, not a string to copy when `doc_lang`
is something else.

## Table of contents

- The seven places this shape is mandatory
- The six components (all six, in order)
- The eight decoration rules
- Hard rules
- The symbols allowed
- Examples

## The seven places this shape is mandatory

The pipeline question · every interview round · the spec approval gate · the plan approval gate ·
the mode gate · the express-lane approval gate · the commit question closing a request.

## The six components (all six, in order)

| # | Component | Presentation used |
|---|---|---|
| 1 | Opening line | plain prose, no bold, no bullet |
| 2 | Body | bold field label `**Label:**` + a `- ` bullet per item once there are 2 or more |
| 3 | File path | the lead-in `Xem đầy đủ tại: ` stays bare, the path goes in backticks | <!-- i18n-allow: sample string of the default language -->
| 4 | Separator rule | exactly one `---` line, one blank line above and below |
| 5 | Answer block | bold heading, one blank line, then the `➤` line as its last line |
| 6 | Closing rule of the turn | one `---` line under the `➤` line, the last line of the message |

1. **Opening line** — 1–2 sentences saying what was just finished and what the user is invited to
   do. Address the user directly, neutral tone. No internal jargon unless explained on the spot.
2. **Body** — a real summary, enough to decide without opening the file. Short sentences, bullets.
3. **Full file path** — a line of its own, shaped `Xem đầy đủ tại: <path>`. Drop this line when <!-- i18n-allow: sample string of the default language -->
   the block is not tied to a file.
4. **Separator rule** — one `---` line separating the answer block from everything above.
5. **Answer block** — a bold heading, then the `➤` line. Nothing is written below it except
   component 6, and no other text ever comes between the two.
6. **Closing rule of the turn** — one `---` line, one blank line above it, sitting under the `➤`
   line as the very last line of the message. It is what tells the reader the turn is over and
   the block rendered whole. The character is three hyphens `---`, the only form a terminal, the
   app and the extension all draw as a rule running the full width. Three em dashes `———`, three
   underscores, or any box-drawing character are NOT that line: they render as three letters of
   fixed length that do not reach the edge, so they are banned here.

**Component 6 closes EVERY turn, not only a turn holding a block.** An answer with no gate, no
options and no file path still ends on that rule. It is a property of the turn, not of the block.

## The eight decoration rules

Use only markdown that renders on all three surfaces (terminal, app, extension). Decoration means
**adding markup characters**, never rewriting words: the eight rules below allow no word of the
content to be changed, removed or added.

1. Bold field labels, **with the colon INSIDE the pair of stars**: `**Mục tiêu:** nội dung`. <!-- i18n-allow: sample string of the default language -->
   Putting the colon outside breaks every running string search for `Mục tiêu:`. <!-- i18n-allow: sample string of the default language -->
2. A field with 2 or more items → one item per line, opening with `- `. Below 2 items it stays on
   the label line; never break a single item out into a bullet.
3. Paths go in backticks, the lead-in `Xem đầy đủ tại: ` stays bare — that way the line still <!-- i18n-allow: sample string of the default language -->
   matches every old search.
4. File names, command names and numbers inside the body go in backticks.
5. Keep the `---` rule with exactly one blank line above and below. Never swap it for another
   drawing character.
6. An option list keeps the shape `- A (đề xuất): nội dung`, one option per line; bold is allowed <!-- i18n-allow: sample string of the default language -->
   only inside the content part, never on the `- A (đề xuất): ` part itself. <!-- i18n-allow: sample string of the default language -->
7. The `➤` line keeps every byte as it is and is always the last line of the block.
8. **Every question carrying an option list is numbered.** The question line opens with
   `<số>. ` — `1.`, `2.`, `3.` — counting continuously across the whole block, and the numbering
   applies even when the block holds exactly ONE question. No exception for the single-question
   case: the user answers by pairing the number with the letter (`1a`, `2b`), and a letter with
   no number in front of it is ambiguous the moment a second question appears. Sample shape,
   written in the default language:

   <!-- i18n-allow: sample of the shape in the default language -->
   ```
   1. <Câu hỏi thứ nhất>
   - A (đề xuất): <phương án> — <hệ quả>
   - B: <phương án> — <hệ quả>

   2. <Câu hỏi thứ hai>
   - A (đề xuất): <phương án> — <hệ quả>
   - B: <phương án> — <hệ quả>
   ```

   The number never restarts inside one block: two question lists in one message are `1.` and
   `2.`, never `1.` twice. Merging two questions into one numbered item is banned too — one
   number per question the user has to answer separately.

## Hard rules

- **Every question to the user is asked in chat, never through a popup tool.** The tool
  `AskUserQuestion` is banned — not only at the seven gates above, but at EVERY question TDQ puts
  to the user, gate or not. Two reasons. First, the user reads all the options at once and can
  answer with anything, including a sentence no option covers. Second, the hosts this workflow has
  to run on (Gemini CLI, GitHub Copilot CLI, Aider) have no such tool at all, so a question shaped
  around one is a question they cannot ask. Print the block, then **end the turn** and wait for the
  reply in chat. Recording the answer: [approval.md](approval.md).
- **No emoji** in any component. The `➤` character stays; it is not an emoji.
- Several options → **exactly one line per option**, shaped `- A (đề xuất): nội dung`. <!-- i18n-allow: sample string of the default language -->
  Merging options into a paragraph is banned.
- Terms only a professional understands (`mode`, `subagent`, `lane`, `phase`) → explain them on
  the spot in a short clause; never make the user go and look them up.
- The answer block comes last of the block. The only thing under it is the closing rule of
  component 6; anything else printed there breaks the shape.
- The turn keeps running after this block was printed → reprint it **word for word, 100%** in the
  last message (rule §1 item 5 of [SKILL.md](../SKILL.md)).
- **Self-check before sending — mandatory, never skipped.** The block holds at least one option
  list → read your own draft back and answer these three before the message goes out:
  1. Does every question line open with its number (`1.`, `2.`, …)? A single question counts too.
  2. Do the numbers run continuously across the whole block, with no repeat and no gap?
  3. Does every option sit on its own line, opening with `- ` and an UPPERCASE letter?
  Any answer is "no" → fix the draft, do not send it. This check exists because the numbering
  rule got broken in practice while the rule itself was already written down: it lived only in
  the skill files that ask questions, and nobody re-read the draft before sending.

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
