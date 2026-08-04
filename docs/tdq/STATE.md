# TDQ STATE (tự sinh — không sửa tay)
Cập nhật: 2026-08-05T04:01:29+07:00 · Project: /Users/truongdinhquoc/Documents/TDQWorkflow · schema 3

| Trường | Giá trị |
|---|---|
| Request | 2026-08-05-bump-version-va-export |
| Lane | full |
| Phase | implement |
| Spec | docs/tdq/spec/2026-08-05-bump-version-va-export.md — ✔ đã duyệt |
| Plan | docs/tdq/plan/2026-08-05-bump-version-va-export.md — ✔ đã duyệt |
| Duyệt quick | (không áp dụng) |
| Mode thực thi | main |

## Đang ở đâu
plan_approved = true và implement_mode đã chốt. Cấm: Dừng giữa chừng; gom tick vào cuối turn.

## Việc tiếp theo
Làm hết plan trong 1 turn, mỗi task red→green, tick [x] ngay khi pass.
```
python3 scripts/tdq_state.py set phase=qc
```
Xong khi: Mọi task trong plan đã tick [x]

> Ghi state chỉ bằng `python3 scripts/tdq_state.py …`. Không chắc đang ở đâu → chạy `tdq_state.py next`.
