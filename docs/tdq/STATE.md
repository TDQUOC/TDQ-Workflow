# TDQ STATE (tự sinh — không sửa tay)
Cập nhật: 2026-08-04T21:32:22+07:00 · Project: /Users/truongdinhquoc/Documents/TDQWorkflow · schema 3

| Trường | Giá trị |
|---|---|
| Request | 2026-08-04-workflow-linh-hoat |
| Lane | full |
| Phase | idle |
| Spec | docs/tdq/spec/2026-08-04-workflow-linh-hoat.md — ✔ đã duyệt |
| Plan | docs/tdq/plan/2026-08-04-workflow-linh-hoat.md — ✔ đã duyệt |
| Duyệt quick | (không áp dụng) |
| Mode thực thi | main |

## Đang ở đâu
Đã xong hoặc chưa mở request. Cấm: Đè request cũ còn dở mà chưa hỏi user.

## Việc tiếp theo
Chờ yêu cầu mới từ user.
```
python3 scripts/tdq_state.py init <YYYY-MM-DD-slug> <quick|full>
```
Xong khi: Có request mới được mở

> Ghi state chỉ bằng `python3 scripts/tdq_state.py …`. Không chắc đang ở đâu → chạy `tdq_state.py next`.
