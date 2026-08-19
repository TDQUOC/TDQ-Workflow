# Chọn cỡ request: nhỏ, chế độ nhanh (express) hay chế độ chuyên sâu (deep)

You **propose**, the user **decides**. Always ask, even when the answer looks obvious.
The only exception is tier `nhỏ`: all 4 conditions in [SKILL.md](../SKILL.md) hold → do it
right away, no request opened, no lane question.

## Dòng tự nhận định

Every new request rates itself INTERNALLY in the shape below before the lane question —
this is what picks recommendation A/B, and it is **never printed to chat**:

```
**Cỡ:** <nhỏ|quick|full> · Cần: <research | interview | subagent | QC độc lập | skill ngoài | không>
```

Column `Cần` lists only what CAN be dropped. Whatever always runs is left out, so the
rating stays short. Nothing optional at all → treat it as `Cần: không`.

## Bảng quyết

| Dấu hiệu | chế độ nhanh (express) | chế độ chuyên sâu (deep) |
|---|---|---|
| Thời lượng ước tính | < ~1 giờ | > ~1 giờ |
| Số file đụng tới | 1–3 | nhiều, hoặc chưa biết |
| Yêu cầu đã rõ chưa | rõ, không phải hỏi gì | còn chỗ mơ hồ / cần research |
| Rủi ro nếu sai | thấp, dễ hoàn tác | cao: dữ liệu, bảo mật, API công khai, tiền |
| Có thiết kế mới không | không, chỉ sửa/thêm nhỏ | có kiến trúc/luồng mới |
| Cần model/hạ tầng mới | không | có |

Có **bất kỳ** ô nào rơi vào cột chế độ chuyên sâu (deep) → đề xuất **chế độ chuyên sâu (deep)**.

## Luồng mỗi lane

- **chế độ nhanh (express)**: analysis (+ search/interview when needed) → mini spec/plan
  merged into 1 file, a ≤10-line summary in chat → user approves (1 gate) → working log →
  implement → validate → short report. Details: [quick-lane.md](quick-lane.md).
- **chế độ chuyên sâu (deep)**: analysis + interview → spec (wait for approval, then write
  the plan in that same turn) → plan (wait for approval). Then: pick the execution mode
  (main or subagent) → implement → QC → report.

## Khuôn câu hỏi (copy được)

Follows [user-facing-block.md](../../tdq-conventions/references/user-facing-block.md) and
the option khuôn of [interview.md](interview.md) — one option per line, the recommendation
always at `A`. Never print the `Cỡ:/Cần:` line; call the "lane" a "pipeline" when asking
the user; right under the 2 options there is always the short block explaining what the 2
pipelines mean (fixed wording, it does not change per task):

```
Tôi đã ghi lại yêu cầu của bạn.

**Tóm tắt:** <2–3 dòng việc user muốn>

- A (đề xuất): chế độ nhanh (express) — <lý do gắn với chính việc này>
- B: chế độ chuyên sâu (deep) — <lý do gắn với chính việc này>

_chế độ nhanh (express): làm gọn, ít vòng hỏi, hợp việc nhỏ/đã rõ. chế độ chuyên sâu
(deep): phân tích + hỏi kỹ trước khi làm, hợp việc phức tạp hoặc rủi ro cao._

Xem đầy đủ tại: `docs/tdq/brief/<slug>.md`

---

**Bạn muốn chạy pipeline nào?**

➤ Trả lời: nhắn "A" hoặc "B", hoặc gõ câu tự nhiên khớp ý bạn chọn · Góp ý: nhắn trực tiếp
```

Halfway through and the lane looks wrong? Say why, propose the change, **ask the user**,
and only then re-run `init` with the new lane.
