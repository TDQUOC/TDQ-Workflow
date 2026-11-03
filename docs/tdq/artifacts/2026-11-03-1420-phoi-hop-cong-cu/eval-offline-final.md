# BÁO CÁO ĐÁNH GIÁ CHẤT LƯỢNG SKILL VÀ PLUGIN TDQ
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Tổng quan theo từng Cell (Host / Model)

| Cell | Mẫu | Khuyến nghị | Lý do | Guardrail | Base Điểm | Cand Điểm | Delta | Trigger Base | Trigger Cand | Chi phí (USD) |
|---|---|---|---|---|---|---|---|---|---|---|
| `claude:cc4` | 16 | **INCONCLUSIVE** | `unavailable_metrics` | TRƯỢT | null | null | null | 0% | 0% | unavailable |

## Chi tiết khuyến nghị và quy tắc Guardrail

- **KEEP**: Chất lượng cải thiện vượt ngưỡng biên độ đăng ký trước và không vi phạm guardrail.
- **TRIM**: Chất lượng không đổi nhưng hiệu quả token/chi phí cải thiện vượt ngưỡng.
- **DROP**: Hồi quy chất lượng hoặc tỷ lệ trigger trượt quá biên độ cho phép.
- **INCONCLUSIVE**: Chưa đủ mẫu, thiếu chỉ số đo bắt buộc, hoặc baseline đã chạm trần.

Nguồn gốc bản ghi: live. Tổng hợp ngoại tuyến; không tự chứng nhận hiệu quả mô hình sống.