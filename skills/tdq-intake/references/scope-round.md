# The scope round — the general tier of the interview

This round runs BEFORE the detail questions in [interview.md](interview.md). Purpose: know
which areas the request spans and what the real context is, so the detail round only asks
inside the part the user needs. That way the spec misses no important area and does not
swell into areas the user never wanted.

## Table of contents

- 1. When it runs
- 2. Question 1 — which areas this request spans
- 3. Question 2 — the context in numbers
- 4. Inferring the investment level
- 5. Recording it

## 1. When it runs

The scope round is **conditional**, and applies to both the express and the deep pipeline.
Run it when the user's request meets **at least one** sign below:

1. The request names a whole system or feature ("build a login system", "add feature X to
   the game") instead of pointing at one behaviour or one file.
2. Sweeping the 9-area frame in section 2 shows **2 or more areas** that could apply while
   the request says nothing about them.
3. The request uses open words about scale or quality with no number attached: "fast",
   "safe", "many users", "professional".
4. The work touches user data, money, or a public API.

No sign at all → SKIP the scope round and go straight to the detail round. When skipping,
the brief must carry exactly one line; silence is not allowed:

<!-- i18n-allow: skip line written in the default language -->
```
Vòng scope: BỎ — <lý do một câu, nói rõ vì sao mọi mặt còn lại suy ra được từ code>
```
That mandatory reason line is the fence: "conditional" means there are criteria, not that
you may drop the round whenever it feels faster.

## 2. Question 1 — which areas this request spans

**Internal sweep frame (never printed to chat).** Walk all 9 quality areas of ISO/IEC
25010:2023 so nothing is missed: functionality · performance · compatibility · user
experience · reliability · security · maintainability · Flexibility — extensibility and
multi-platform · safety. This frame only stops you forgetting an area; the user does not
need to read it.

**The part printed to chat.** Pick **3–5 areas** that genuinely fit the request's field,
then ask using the option template of [interview.md](interview.md) — one area per line,
UPPERCASE label, consequence joined with ` — `. Write the consequence as "picking this area
means the spec will carry <what>", so the user sees the price of each choice:

<!-- i18n-allow: question template written in the default language -->
```
<số>. Request này bạn muốn bao quanh những mặt nào? (chọn nhiều được)
- A (đề xuất): <mặt> — spec sẽ có <mục/đầu ra cụ thể>
- B: <mặt> — spec sẽ có <mục/đầu ra cụ thể>
- C: <mặt> — spec sẽ có <mục/đầu ra cụ thể>
- D: chỉ cần chạy được — bỏ hết các mặt trên, spec chỉ lo đúng luồng chính
```
Rules for this question:

- Allow multiple picks: the user can answer "A, C" or "A C D"; say so inside the block.
- The last option is always "just make it run" — the user needs a way out of every
  secondary area.
- No more than 5 areas. If 6 or more all fit, merge the neighbouring ones instead of
  stretching the list.
- An area the request already settled is NOT offered as an option; write it down as settled.

## 3. Question 2 — the context in numbers

**Asking for an abstract level is BANNED.** Never ask whether the user wants it "minimal,
just enough, or fully professional". That question makes the user convert something they do
not know yet, and the answer anchors to nothing checkable. Replace it with concrete context
questions — easy to answer, and the numbers get reused in spec §5 constraints.

Sample set of 5 groups; pick **at most 4 questions** that fit the field:

| Group | What to ask | Example options |
|---|---|---|
| Environment & target build | where it runs, which version | personal machine · 1-node VPS · multi-node cloud |
| Concurrency scale | max CCU, RPS, number of records | < 100 CCU · 100–10,000 · > 10,000 |
| Stage | R&D experiment or a product really running | prototype · internal beta · product with real users |
| Lifetime & maintenance | how long it lives, who maintains it | one-off · one person keeps it · a team keeps it |
| Platform constraints | device, OS, engine, mandatory library | no constraint · one platform · several platforms |
Rules for this question:

- Each question still follows the A/B/C option template, and the levels are **numbers or
  concrete milestones**.
- Each question adds a final option "I will type the number myself" so the user can fill it
  in directly.
- Merge question 1 and the context questions into **a single chat block**, numbered
  continuously — question 1 is `1.`, the first context question is `2.`, and so on with no
  repeat and no restart. This is rule 8 of
  [user-facing-block.md](../../tdq-conventions/references/user-facing-block.md); breaking it
  is what makes two lists both open at `A` and leaves the user unable to say which question
  their letter belongs to.
- Drop any group the request already answered; never re-ask what the user just said.

## 4. Inferring the investment level

The investment level is **inferred by you** from the context answers, never asked of the
user directly. Mapping table:

| Context | Investment level | Consequence for spec/plan |
|---|---|---|
| Prototype/R&D, small scale, one keeper | core | main flow only, 0 performance items, DoD ≤ 5 lines |
| Internal beta, medium scale, a team keeps it | medium | add edge tests and error paths to the DoD |
| Real product, large scale | full | performance and reliability become QC items of their own, with numeric thresholds |
| Touches money, user data, a public API | full | security enters the DoD even when the user did not pick that area |
Once inferred, print exactly one line, together with the detail round's question block:

<!-- i18n-allow: inference line written in the default language -->
```
Tôi hiểu là: <mức đầu tư> vì <bối cảnh user vừa nói>
```
This line lets the user push back immediately if you inferred wrong. It is **not** a new
approval gate — no separate confirmation, no extra phase.

## 5. Recording it

The brief section `## Hiểu & kiến thức` gains `### Phạm vi đã chốt`, exactly 4 lines: <!-- i18n-allow: canonical section names -->

<!-- i18n-allow: record template written in the default language -->
```
- Mặt CHỌN: <danh sách>
- Mặt LOẠI: <danh sách — chép nguyên sang spec §1 NGOÀI phạm vi>
- Bối cảnh: <các con số user đưa>
- Mức đầu tư suy ra: <lõi|vừa|đầy đủ> — vì <bối cảnh>
```
In the spec phase, the "areas RULED OUT" line is copied verbatim into §1 under the
out-of-scope heading. That is the reference point when the spec starts to swell: an area
absent from the "areas PICKED" line that grows into the spec anyway is the sign you are
building more than was asked.
