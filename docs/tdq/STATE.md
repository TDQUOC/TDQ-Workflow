# TDQ STATE (tự sinh — không sửa tay)
Cập nhật: 2026-07-30T23:46:58+07:00 · Project: /Users/truongdinhquoc/Documents/TDQWorkflow · schema 3

| Trường | Giá trị |
|---|---|
| Request | 2026-07-30-fix-agy-adddir-sync-agent |
| Lane | quick |
| Phase | idle |
| Spec | (chưa có) |
| Plan | (chưa có) |
| Duyệt quick | ✔ đã duyệt |
| Mode thực thi | (chưa chốt) |

## Đang ở đâu
lane = quick. Cấm: Implement trước khi ghi working log.

## Việc tiếp theo
Trình mini-plan ≤10 dòng → chờ duyệt → ghi working log TRƯỚC → rồi mới implement.
```
python3 scripts/tdq_state.py approve quick --by "<nguyên văn câu user>"
```
Xong khi: quick_approved = true, log đã ghi, việc đã validate

> Ghi state chỉ bằng `python3 scripts/tdq_state.py …`. Không chắc đang ở đâu → chạy `tdq_state.py next`.
