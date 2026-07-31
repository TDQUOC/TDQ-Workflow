# TDQ STATE (tự sinh — không sửa tay)
Cập nhật: 2026-07-31T17:22:34+07:00 · Project: /Users/truongdinhquoc/Documents/TDQWorkflow · schema 3

| Trường | Giá trị |
|---|---|
| Request | 2026-07-31-hybrid-deep-search |
| Lane | full |
| Phase | report |
| Spec | docs/tdq/spec/2026-07-31-hybrid-deep-search.md — ✔ đã duyệt |
| Plan | docs/tdq/plan/2026-07-31-hybrid-deep-search.md — ✔ đã duyệt |
| Duyệt quick | (không áp dụng) |
| Mode thực thi | main |

## Đang ở đâu
QC đã PASS. Cấm: Tự commit hoặc push khi user chưa yêu cầu.

## Việc tiếp theo
Viết report ≤50 dòng rồi hỏi user có commit không.
```
python3 scripts/tdq_state.py set phase=idle
```
Xong khi: Report đã ghi và user đã được hỏi về commit

> Ghi state chỉ bằng `python3 scripts/tdq_state.py …`. Không chắc đang ở đâu → chạy `tdq_state.py next`.
