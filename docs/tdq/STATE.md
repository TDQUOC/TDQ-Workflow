# TDQ STATE (tự sinh — không sửa tay)
Cập nhật: 2026-08-05T16:01:24+07:00 · Project: /Users/truongdinhquoc/Documents/TDQWorkflow · schema 3

| Trường | Giá trị |
|---|---|
| Request | 2026-08-05-bump-sync-user |
| Lane | quick |
| Phase | idle |
| Spec | (chưa có) |
| Plan | (chưa có) |
| Duyệt quick | ✔ đã duyệt |
| Mode thực thi | (chưa chốt) |

## Đang ở đâu
Đã xong hoặc chưa mở request. Cấm: Đè request cũ còn dở mà chưa hỏi user.

## Việc tiếp theo
Chờ yêu cầu mới từ user.
```
python3 scripts/tdq_state.py init <YYYY-MM-DD-slug> <quick|full>
```
Xong khi: Có request mới được mở

> Ghi state chỉ bằng `python3 scripts/tdq_state.py …`. Không chắc đang ở đâu → chạy `tdq_state.py next`.
