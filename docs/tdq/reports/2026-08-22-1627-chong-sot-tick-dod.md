# REPORT — Chống sót tick dòng Definition of Done lúc đóng sổ

Ngày: 2026-08-22 · Lane: full · Mode: main
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Đã làm

Gốc rễ: `plan_tick_state()` chỉ đếm ô tick có mã task in đậm, nên 19 dòng DoD hoàn toàn vô
hình — `all_done` vẫn True dù mọi ô DoD còn trống. Chốt chặn `[TDQ:TICK]` lại chỉ bắn ở
phase `implement`/`qc`, đúng lúc đóng sổ ở `report` thì không ai canh. Bảo hiểm duy nhất
trước đây là một câu văn xuôi trong khuôn report, dựa vào trí nhớ của model.

Thêm ba bộ đọc mới trong `scripts/tdq_state.py` — `dod_tick_state()`, `qc_result_state()`,
`task_open_count()` — và một nhánh nhắc `[TDQ:DOD]` trong `hooks/scripts/stop_gate.py`.
Nhắc bắn ở phase `report` và `idle` khi QC đã PASS sạch mà ô tick còn trống, nêu cả số task
lẫn số dòng DoD còn lại. Nó **chỉ nhắc, không chặn** — đúng phương án B bạn chọn. Khuôn
`plan-template.md` giờ bắt DoD viết dạng ô tick, khuôn `report-template.md` bước 8 nói rõ
phải tick CẢ HAI loại ô.

`_TASK_LINE` và giá trị trả về của `plan_tick_state()` giữ nguyên tuyệt đối: bốn nơi phụ
thuộc hợp đồng đó, một test khoá đúng bộ khoá của nó.

## Kiểm chứng

19 hạng mục DoD + 4 hạng mục cố định đều PASS. QC độc lập bằng agent chạy song song, xác
nhận 18/19 và nêu 8 defect — 2 mức trung bình (nhắc bị cắt khi đã có 4 nhắc khác; file
không phải UTF-8 làm hook rc=1), 6 mức thấp. Đã sửa hết trong đúng một vòng fix, trần 3
vòng chưa chạm. Chi tiết ở [qc/2026-08-22-1627-chong-sot-tick-dod.md](../qc/2026-08-22-1627-chong-sot-tick-dod.md).

Test: `tests/test_plan_tick.py` 32 xanh, `tests/test_stop_gate.py` 61 xanh, full suite giữ
đúng 37 đỏ mốc nền, toàn bộ trong `tests/test_skill_router.py`.

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 0s | 0s | 1 |
| analyze | 12 min | 11 min | 1 |
| spec | 3 min | 3 min | 1 |
| plan | 4 min | 4 min | 1 |
| implement | 8 min | 8 min | 1 |
| qc | 19 min | 11 min | 1 |
| report | 1s | 0s | 1 |
| **Total** | **45 min** | **36 min** | |

Nguồn: `python3 scripts/tdq_timing.py show`

## Nợ lại

`plan_tick_state()` vẫn ném lỗi khi plan không phải UTF-8. Lỗi có sẵn từ trước, không phải
hồi quy của request này, và hàm đó nằm trong luật cấm chạm của plan nên tôi không sửa lén.
