# REQUEST — Fix chặn oan `[TDQ:LOG]` khi log ghi qua shell

Ngày: 2026-07-29 · Lane đề xuất: **full** · Nguồn: user ("hãy phân tích để làm spec/plan để fix nốt issue đó đi")

## Nguyên văn triệu chứng
Cuối turn implement 0.3.0, Stop hook chặn `[TDQ:LOG] … chưa được append` dù working log
đã được append thật (bằng `cat >>` trong Bash). Phải append lại bằng công cụ Edit mới qua.

## Vì sao là lane full
Chạm vào hook Stop — thành phần duy nhất còn quyền chặn — và cả hai chiều sai (chặn oan +
bỏ lọt). Cần spec + plan + QC có bằng chứng, không phải sửa nhanh.

## Liên quan
- Spec: `../spec/2026-07-29-turn-effect-blindspot.md`
- Request trước: `2026-07-28-instruction-hardening-7b` (bản 0.3.0 sinh ra điểm mù này)
