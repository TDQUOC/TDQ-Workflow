# TDQ Diagram — the algorithm outline every feature is approved against

Load [tdq-conventions](../tdq-conventions/SKILL.md) first. Every output for the user is written
in the user's language (`doc_lang`, default Vietnamese).
This skill owns one phase: `diagram`, which sits between `spec` and `plan`.

The rule this phase exists for: **a feature is not implemented until its outline is approved.**
The diagram is that outline. A spec built from several feature flows produces several diagrams,
and the user approves them ONE BY ONE — approving one never approves the rest.

The unit is the FEATURE, never the request. `docs/tdq/mind-map/<feature>.md` is that feature's
single living copy; many requests edit it in turn. A request that touches three features touches
three diagram files, and none of them is named after the request.

Everything below drives `python3 scripts/tdq_mindmap.py`. This skill names its commands and
never repeats what the script does — read the script when you need the mechanics.

## 1. The file shape

One step per line, readable straight in chat. Line 1 is the title; the `@nhánh` line is <!-- i18n-allow: document syntax name, stays Vietnamese -->
mandatory and appears exactly once; `@phụ-thuộc` lines are optional and repeatable. <!-- i18n-allow: document syntax name, stays Vietnamese -->

<!-- i18n-allow: the diagram file is a user-facing document, written in doc_lang -->
```
# Mua hàng
@nhánh: Thương mại > Mua hàng
@phụ-thuộc: dang-nhap · cần token phiên do đăng nhập phát ra

B1 · Bấm đặt hàng trên giỏ (src/pages/cart.tsx::CartPage.onCheckout)
B2 · Đọc token phiên đang giữ (src/lib/session.ts::readSessionToken)
B2! · không có token thì đẩy sang màn đăng nhập (src/lib/session.ts::redirectToLogin)
B3 · Gửi đơn kèm token (src/api/order.ts::orderApi.create)
B4 · Xác thực token rồi khoá tồn kho (server/controllers/order.py::OrderController.create)
B4! · token hết hạn thì trả lỗi phiên và không khoá tồn kho (server/controllers/order.py::deny_order)
B5 · Ghi đơn và phát sự kiện thanh toán (server/services/order.py::OrderService.place)
B6 · Hiện màn xác nhận đơn (?)
```

Four things the shape guarantees, and why each one is there:

- `@nhánh: <nhánh tổng> > <nhánh con>` — where this feature sits in the project. The index page <!-- i18n-allow: document syntax name, stays Vietnamese -->
  groups by it, which is how the mind map reproduces the whole project rather than a flat pile.
- `@phụ-thuộc: <feature-slug> · <lý do một câu>` — a real business dependency, declared by a <!-- i18n-allow: document syntax name, stays Vietnamese -->
  human. The reason is mandatory: an unlabelled arrow between features says nothing. The machine
  is not allowed to infer these — two features sharing a helper is not a dependency.
- `B<n> · <mô tả> (<file>::<hàm>)` — one step, one line. `B<n>!` is that step's error branch. <!-- i18n-allow: document syntax name, stays Vietnamese -->
- `(?)` where the code is not written yet. Honest beats invented: `doi-chieu` skips a `(?)` and
  flags a `file::hàm` pair that does not exist. <!-- i18n-allow: document syntax name, stays Vietnamese -->

## 2. The steps of phase `diagram`

1. **List the feature flows the approved spec is built from.** One flow, one diagram. Do not
   merge two flows into one file to save work — the user approves them separately, and a merged
   file cannot be half-approved.
2. **For each flow: `python3 scripts/tdq_mindmap.py sinh <feature-slug>`.**
   Exit 0 means a new file was created — fill it in. Exit 3 means **the feature already has a
   diagram**: the command prints the current content and does NOT overwrite it. That is the
   update path, section 4 below.
3. **Write the steps from the spec's approach**, not from the code. This is the outline the code
   will be written against, so it states intent. Where the code already exists, put the real
   `file::hàm` pair in; where it does not, put `(?)`. <!-- i18n-allow: document syntax name, stays Vietnamese -->
4. **Declare the dependencies.** Ask, for each flow: what must already have happened for this to
   work? Buying needs a session token, and only logging in issues one — that is a real edge, and
   it goes in as `@phụ-thuộc: dang-nhap · cần token phiên do đăng nhập phát ra`. <!-- i18n-allow: document syntax name, stays Vietnamese -->
5. **`python3 scripts/tdq_mindmap.py kiem <file>`** until it exits 0.
6. **`python3 scripts/tdq_mindmap.py lien-he`** — the whole dependency mesh, across every
   feature in the folder. It fails on a cycle and on an edge pointing at a feature with no file.
   A cycle is nearly always a modelling mistake: go back and split the feature.
7. **`python3 scripts/tdq_mindmap.py doi-chieu <file>`** where the code already exists. Skip it
   in lane `quick` — there the business layer alone is enough.
8. **`python3 scripts/tdq_mindmap.py xem <file>`** to build the page, and `xem --tong` for the
   index once every diagram of the request is written.
9. **Register each diagram into state, then present them for approval — one at a time.**
   Use section 3 for a new feature, section 4 for one that already existed. Record approval only
   through `scripts/tdq_state.py`, and only on the user's own words. The gate into `plan` stays
   shut while any diagram in the request is unapproved, and the refusal names which one.

## 3. Presenting a NEW feature's diagram

<!-- i18n-allow: chat block written in the user's document language -->
```
Feature `<slug>` chưa có sơ đồ, tôi vẽ mới. Đây là dàn ý sẽ dùng để viết code.

<dán nguyên nội dung file sơ đồ>

**Phụ thuộc:** <liệt kê từng dòng @phụ-thuộc kèm lý do, hoặc "không phụ thuộc feature nào">.
**Chỗ chưa biết:** <liệt kê bước còn `(?)`, hoặc "không còn chỗ nào">.

Xem trang: `docs/tdq/mind-map/<slug>.html`

---

**Bạn duyệt sơ đồ này chứ?** (còn <N> sơ đồ nữa của request này)

➤ Duyệt: nhắn "duyệt sơ đồ <slug>" · Góp ý: nhắn trực tiếp
```

Say how many diagrams remain. The user is approving one item of a list, and a list whose length
is hidden cannot be worked through.

## 4. Presenting an UPDATE to a feature that already has a diagram

Exit code 3 from `sinh` is the trigger. Never silently rewrite a living diagram: say it already
exists, then show what it becomes. Do not paste a line-by-line diff — the user settled that the
new full version is what they want to read.

<!-- i18n-allow: chat block written in the user's document language -->
```
Feature `<slug>` đã có sơ đồ rồi. Sau cập nhật của request này nó sẽ thành như sau:

<dán nguyên nội dung file sơ đồ SAU khi sửa>

**Đổi gì:** <1–3 câu nói thẳng phần nào của luồng bị đổi và vì sao>.
**Phụ thuộc:** <có thêm/bớt dòng @phụ-thuộc nào không>.

---

**Bạn duyệt bản cập nhật này chứ?** (còn <N> sơ đồ nữa của request này)

➤ Duyệt: nhắn "duyệt sơ đồ <slug>" · Góp ý: nhắn trực tiếp
```

## 5. The commands and their exit codes

| Command | What it does | Exit codes |
|---|---|---|
| `python3 scripts/tdq_mindmap.py sinh <feature>` | new file from the template, or open the existing one for update | 0 created · 3 already exists, update mode, nothing written · 2 bad slug |
| `python3 scripts/tdq_mindmap.py kiem <file>` | check the shape, print each violation with its rule code | 0 clean · 1 violations · 2 unreadable file |
| `python3 scripts/tdq_mindmap.py doi-chieu <file>` | check each `file::hàm` pair against the code graph | 0 all match · 1 some pairs drifted · 3 the graph cannot be read | <!-- i18n-allow: document syntax name, stays Vietnamese -->
| `python3 scripts/tdq_mindmap.py lien-he` | build the dependency mesh across the whole folder | 0 valid · 1 an edge points at a missing feature · 3 a dependency cycle |
| `python3 scripts/tdq_mindmap.py xem <file>` | build the two-layer page; `--tong` builds the index | 0 written · 1 the diagram is malformed · 2 the file cannot be written |

`TDQ_LOG=0` turns the log service off; it is on by default.

## Two layers, and why only one of them is approved

The page has a business layer and a detail layer, and they differ in the NATURE of their source,
not merely in depth:

- **Business layer** — the `.md` file above. Written by a human, states intent, gets approved.
- **Detail layer** — read from `graphify-out/graph.json` at build time. Every function the flow
  passes through becomes a step, ordered by call-site line, explained by the first line of its
  docstring. Nobody writes it, nobody approves it, and it is rebuilt on every run, so it cannot
  rot.

The detail layer's order is **write order, not run order** — the line a call sits on, not the
sequence a request actually takes through branches and loops. The page says so at the top of
that layer; repeat it if a user starts reading it as a trace.

Done when: every feature flow of the approved spec has a diagram file, `kiem` and `lien-he` exit
0, and state records an approval for each one.
Next step: `python3 scripts/tdq_state.py set phase=plan` — it refuses while any diagram of the
request is still unapproved, and names the ones that are.
