# TDQ STATE (tự sinh — không sửa tay)
Cập nhật: 2026-08-05T10:38:35+07:00 · Project: /Users/truongdinhquoc/Documents/TDQWorkflow · schema 3

| Trường | Giá trị |
|---|---|
| Request | 2026-08-05-format-cau-hoi-interview |
| Lane | quick |
| Phase | implement |
| Spec | (chưa có) |
| Plan | (chưa có) |
| Duyệt quick | ✔ đã duyệt |
| Mode thực thi | (chưa chốt) |

## Đang ở đâu
lane = quick. Cấm: Implement trước khi ghi working log.

## Việc tiếp theo
Phân tích → mini-spec/plan gộp 1 file → chờ duyệt → ghi working log TRƯỚC → rồi mới implement.
```
python3 scripts/tdq_state.py approve quick [--mode external] --by "<nguyên văn câu user>"
```
Xong khi: quick_approved = true, log đã ghi, việc đã validate, phase đã về idle

> Ghi state chỉ bằng `python3 scripts/tdq_state.py …`. Không chắc đang ở đâu → chạy `tdq_state.py next`.
