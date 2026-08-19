# Vòng scope — tầng tổng quát của interview

This round runs BEFORE the detail questions in [interview.md](interview.md). Purpose: know
which areas the request spans and what the real context is, so the detail round only asks
inside the part the user needs. That way the spec misses no important area and does not
swell into areas the user never wanted.

## Mục lục

- 1. Khi nào chạy
- 2. Câu 1 — request này bao quanh những mặt nào
- 3. Câu 2 — bối cảnh bằng số
- 4. Suy ra mức đầu tư
- 5. Ghi lại

## 1. Khi nào chạy

The scope round is **conditional**, and applies to both chế độ nhanh (express) and chế độ
chuyên sâu (deep). Run it when the user's request meets **at least one** sign below:

1. The request names a whole system or feature ("làm hệ thống login", "thêm tính năng X
   cho game") instead of pointing at one behaviour or one file.
2. Sweeping the 9-area frame in section 2 shows **2 or more areas** that could apply while
   the request says nothing about them.
3. The request uses open words about scale or quality with no number attached: "nhanh",
   "an toàn", "nhiều người dùng", "chuyên nghiệp".
4. The work touches user data, money, or a public API.

No sign at all → SKIP the scope round and go straight to the detail round. When skipping,
the brief must carry exactly one line; silence is not allowed:

```
Vòng scope: BỎ — <lý do một câu, nói rõ vì sao mọi mặt còn lại suy ra được từ code>
```
That mandatory reason line is the fence: "conditional" means there are criteria, not that
you may drop the round whenever it feels faster.

## 2. Câu 1 — request này bao quanh những mặt nào

**Internal sweep frame (never printed to chat).** Walk all 9 quality areas of ISO/IEC
25010:2023 so nothing is missed: functionality · performance · compatibility · user
experience · reliability · security · maintainability · Flexibility — extensibility and
multi-platform · safety. This frame only stops you forgetting an area; the user does not
need to read it.

**The part printed to chat.** Pick **3–5 areas** that genuinely fit the request's field,
then ask using the option khuôn of [interview.md](interview.md) — one area per line,
UPPERCASE label, consequence joined with ` — `. Write the consequence as "picking this area
means the spec will carry <what>", so the user sees the price of each choice:

```
<số>. Request này bạn muốn bao quanh những mặt nào? (chọn nhiều được)
- A (đề xuất): <mặt> — spec sẽ có <mục/đầu ra cụ thể>
- B: <mặt> — spec sẽ có <mục/đầu ra cụ thể>
- C: <mặt> — spec sẽ có <mục/đầu ra cụ thể>
- D: chỉ cần chạy được — bỏ hết các mặt trên, spec chỉ lo đúng luồng chính
```
Luật của câu này:

- Allow multiple picks: the user can answer "A, C" or "A C D"; say so inside the block.
- The last option is always "chỉ cần chạy được" — the user needs a way out of every
  secondary area.
- No more than 5 areas. If 6 or more all fit, merge the neighbouring ones instead of
  stretching the list.
- An area the request already settled is NOT offered as an option; write it down as settled.

## 3. Câu 2 — bối cảnh bằng số

**CẤM hỏi mức độ trừu tượng.** Never ask "bạn muốn gọn nhất, vừa đủ, hay đầy đủ chuyên
nghiệp". That question makes the user convert something they do not know yet, and the
answer anchors to nothing checkable. Replace it with concrete context questions — easy to
answer, and the numbers get reused in spec §5 constraints.

Sample set of 5 groups; pick **at most 4 questions** that fit the field:

| Nhóm | Hỏi cái gì | Ví dụ option |
|---|---|---|
| Môi trường & bản target | chạy ở đâu, phiên bản nào | máy cá nhân · VPS 1 node · cloud nhiều node |
| Quy mô đồng thời | max CCU, RPS, số bản ghi | < 100 CCU · 100–10.000 · > 10.000 |
| Giai đoạn | R&D thử nghiệm hay product chạy thật | prototype · beta nội bộ · product có người dùng thật |
| Vòng đời & bảo trì | sống bao lâu, ai sửa sau này | dùng một lần · một người giữ · cả nhóm giữ |
| Ràng buộc nền tảng | thiết bị, OS, engine, thư viện bắt buộc | không ràng buộc · một nền tảng · nhiều nền tảng |
Luật của câu này:

- Each question still follows the A/B/C option khuôn, and the levels are **numbers or
  concrete milestones**.
- Each question adds a final option "tôi tự gõ số" so the user can fill it in directly.
- Merge question 1 and the context questions into **a single chat block**, numbered
  continuously.
- Drop any group the request already answered; never re-ask what the user just said.

## 4. Suy ra mức đầu tư

The investment level is **inferred by you** from the context answers, never asked of the
user directly. Mapping table:

| Bối cảnh | Mức đầu tư | Hệ quả lên spec/plan |
|---|---|---|
| Prototype/R&D, quy mô nhỏ, một người giữ | lõi | chỉ luồng chính, 0 hạng mục hiệu năng, DoD ≤ 5 dòng |
| Beta nội bộ, quy mô vừa, cả nhóm giữ | vừa | thêm test biên và đường lỗi vào DoD |
| Product thật, quy mô lớn | đầy đủ | hiệu năng và độ tin cậy thành hạng mục QC riêng, có ngưỡng số |
| Chạm tiền, dữ liệu người dùng, API công khai | đầy đủ | bảo mật vào DoD kể cả khi user không chọn mặt đó |
Suy xong phải in đúng một dòng, đặt kèm khối câu hỏi của vòng chi tiết:

```
Tôi hiểu là: <mức đầu tư> vì <bối cảnh user vừa nói>
```
This line lets the user push back immediately if you inferred wrong. It is **not** a new
approval gate — no separate confirmation, no extra phase.

## 5. Ghi lại

The brief section `## Hiểu & kiến thức` gains `### Phạm vi đã chốt`, exactly 4 lines:

```
- Mặt CHỌN: <danh sách>
- Mặt LOẠI: <danh sách — chép nguyên sang spec §1 NGOÀI phạm vi>
- Bối cảnh: <các con số user đưa>
- Mức đầu tư suy ra: <lõi|vừa|đầy đủ> — vì <bối cảnh>
```
In the spec phase, the "Mặt LOẠI" line is copied verbatim into §1 under `NGOÀI phạm vi`.
That is the reference point when the spec starts to swell: an area absent from "Mặt CHỌN"
that grows into the spec anyway is the sign you are building more than was asked.
