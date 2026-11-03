# REPORT — Sửa lỗi approval-gate (nhắc nhở khi duyệt sai)

Ngày: 2026-08-04 · Spec: ../spec/2026-08-04-approval-gate-bug.md · Plan: ../plan/2026-08-04-approval-gate-bug.md · QC: ../qc/2026-08-04-approval-gate-bug.md

## Đã làm gì
- `prompt_context.py`: lưu kết quả `looks_like_approval()` vào turn ledger (dòng
  `kind="signal"`) mỗi lần đang chờ duyệt spec/plan/quick, kể cả nhánh lệch mode
  (`mode_conflict=True`).
- `_common.py`: thêm `remind_force()` — bản không dedupe theo mã, tránh bị nuốt
  bởi lời nhắc `TDQ:APPROVE` mà `edit_gate.py` đã in trước trong cùng turn.
- `bash_gate.py`: thêm đối chiếu tín hiệu cho cả lệnh `approve <target>` lẫn
  đường vòng `set phase=<kế tiếp>` — tra dòng signal GẦN NHẤT theo target, bắn
  nhắc `TDQ:APPROVE` nếu prompt gần nhất không phải câu duyệt (hoặc mode lệch),
  im lặng khi khớp thật, fail-open khi ledger rỗng.
- 16 test mới/sửa (2 file `test_prompt_context.py`, `test_bash_gate.py`), sửa 1
  assertion cũ khớp hành vi mới có chủ đích (`test_compliance_protocol.py`).

## Đầu ra
| Đầu ra | Đường dẫn |
|---|---|
| Ghi tín hiệu duyệt vào ledger | `hooks/scripts/prompt_context.py` |
| Nhắc không dedupe theo mã | `hooks/scripts/_common.py` (`remind_force`) |
| Đối chiếu tín hiệu, nhắc khi lệch | `hooks/scripts/bash_gate.py` |
| Test | `tests/test_prompt_context.py`, `tests/test_bash_gate.py` |

## Cách chạy / cách kiểm
```
python3 -m unittest discover -s tests -p "test_*.py"   # 448 passed
python3 scripts/doc_lint.py docs/tdq/spec/2026-08-04-approval-gate-bug.md   # exit 0
```

## Kết quả QC
7/7 hạng mục (Q1–Q7) PASS, 1 vòng, không cần vòng fix. Chi tiết:
`docs/tdq/qc/2026-08-04-approval-gate-bug.md`.

## Quyết định đáng chú ý
- Chỉ siết soft-reminder (không thêm gate cứng/deny) — theo lựa chọn user, tránh
  lặp lỗi đọc transcript của gate cứng cũ (bỏ ở v0.3.0).
- Dùng `remind_force()` thay vì mã nhắc mới — né việc phải sửa danh sách `CODES`
  đóng (spec §2.1), vẫn giải quyết trọn vẹn bẫy dedupe với `edit_gate.py`.

## Giới hạn còn lại
- Không có gate cứng — Claude về lý thuyết vẫn có thể bỏ qua nhắc nhở đã siết
  (rủi ro R1, user đã chấp nhận có ý thức).
- Không audit lịch sử các lần lỗi đã xảy ra trước đây (theo phạm vi đã chốt).

## Đề xuất tiếp theo
- Không có.
