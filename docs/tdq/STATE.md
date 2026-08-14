# TDQ STATE (tự sinh — không sửa tay)
Cập nhật: 2026-08-14T15:02:31+07:00 · Project: /Users/truongdinhquoc/Documents/TDQWorkflow · schema 3

| Trường | Giá trị |
|---|---|
| Request | 2026-08-14-trang-tri-khoi-chat |
| Lane | full |
| Phase | spec |
| Spec | docs/tdq/spec/2026-08-14-trang-tri-khoi-chat.md — ✔ đã duyệt |
| Plan | (chưa có) |
| Duyệt quick | (không áp dụng) |
| Mode thực thi | (chưa chốt) |

## Đang ở đâu
Đã phân tích xong. Cấm: Tự suy diễn là user đã duyệt; bắt user nhắn thêm một turn nữa mới viết plan.

## Việc tiếp theo
Viết spec (kèm mục Lộ trình), đăng ký spec_file, trình tóm tắt rồi DỪNG chờ user duyệt.
```
python3 scripts/tdq_state.py approve spec --by "<nguyên văn câu user>"
```
Xong khi: spec_approved = true

> Ghi state chỉ bằng `python3 scripts/tdq_state.py …`. Không chắc đang ở đâu → chạy `tdq_state.py next`.
