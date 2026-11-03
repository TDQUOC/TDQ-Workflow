# QC — Token budget idle (E2) — 2026-07-27

Cách đo: tổng chars metadata luôn nạp (name + description của 10 skill, frontmatter 3 agent) + injection hook, quy đổi ~4 chars/token.

| Thành phần | Chars |
|---|---|
| 10 skill (name+description) | 1.532 |
| 3 agent (frontmatter) | 547 |
| **Tổng metadata luôn nạp** | **2.079 ≈ 520 tokens** |
| Inject SessionStart (worst-case, có request) | +144 chars |
| Inject UserPromptSubmit (đang chờ duyệt) | +72 chars |

- **Idle thật (không có request TDQ)**: hooks im lặng (đã test B4) → chỉ metadata ≈ **520 tokens** < ~800 → **PASS**.
- Active đang chờ duyệt: ≈ 574 tokens — vẫn dưới ngưỡng.
- Thân skill (tối đa 54 dòng) và `references/tavily.md` chỉ nạp khi skill được gọi (lazy load).

Kết luận: **PASS** (spec mục 3.1 & DoD mục 4).
