# Picking the size of a request: tier `nhỏ`, express or deep <!-- i18n-allow: canonical name in the default language -->

You **propose**, the user **decides**. Always ask, even when the answer looks obvious.
The only exception is tier `nhỏ`: all 4 conditions in [SKILL.md](../SKILL.md) hold → do it <!-- i18n-allow: canonical name in the default language -->
right away, no request opened, no lane question.

## The self-rating line

Every new request rates itself INTERNALLY in the shape below before the lane question —
this is what picks recommendation A/B, and it is **never printed to chat**:

<!-- i18n-allow: rating line written in the default language -->
```
**Cỡ:** <nhỏ|quick|full> · Cần: <research | interview | subagent | QC độc lập | skill ngoài | không>
```

Column `Cần` lists only what CAN be dropped. Whatever always runs is left out, so the <!-- i18n-allow: canonical name in the default language -->
rating stays short. Nothing optional at all → treat it as "nothing needed".

## The decision table

| Sign | Express | Deep |
|---|---|---|
| Estimated duration | < ~1 hour | > ~1 hour |
| Files touched | 1–3 | many, or unknown |
| Is the request clear | clear, nothing to ask | vague spots / research needed |
| Risk if it goes wrong | low, easy to undo | high: data, security, public API, money |
| Any new design | no, a small edit or addition | yes, new architecture or flow |
| New model or infrastructure needed | no | yes |

**Any** cell landing in the deep column → propose the **deep pipeline**.

## The flow of each lane

- **Express**: analysis (+ search/interview when needed) → mini spec/plan
  merged into 1 file, a ≤10-line summary in chat → user approves (1 gate) → working log →
  implement → validate → short report. Details: [quick-lane.md](quick-lane.md).
- **Deep**: analysis + interview → spec (wait for approval, then write
  the plan in that same turn) → plan (wait for approval). Then: pick the execution mode
  (main or subagent) → implement → QC → report.

## The question template (copy it)

Follows [user-facing-block.md](../../tdq-conventions/references/user-facing-block.md) and
the option template of [interview.md](interview.md) — one option per line, the recommendation
always at `A`. Never print the `Cỡ:/Cần:` line; call the "lane" a "pipeline" when asking <!-- i18n-allow: canonical name in the default language -->
the user; right under the 2 options there is always the short block explaining what the 2
pipelines mean (fixed wording, it does not change per task):

<!-- i18n-allow: question block written in the default language -->
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
