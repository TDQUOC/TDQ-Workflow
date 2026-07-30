# QC — Vá điểm mù verify-by-effect (0.3.1)

Ngày: 2026-07-29 · Plan: ../plan/2026-07-29-turn-effect-blindspot.md · Vòng: 1

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Toàn bộ suite | `python3 -m unittest discover tests` | Ran 187 tests — OK | PASS |
| Q2 | Helper snapshot | `python3 -m unittest test_turn_snapshot` | 11 test OK | PASS |
| Q3 | Ảnh chụp đầu turn | `python3 -m unittest test_turn_ledger` | 8 test OK (3 test `turn_start` mới) | PASS |
| Q4 | Đối chiếu cuối turn | `python3 -m unittest test_stop_gate` | 24 test OK (11 test đĩa mới) | PASS |
| Q5 | Không hồi quy hook cũ | `python3 -m unittest test_compliance_protocol test_context_hooks test_e2e_chain test_hook_resilience` | OK | PASS |
| Q6 | Ngân sách token | `python3 -m unittest test_token_budget` | 8 test OK — snapshot ghi vào file, không in ra context | PASS |
| Q7 | Lint doc | `python3 scripts/doc_lint.py skills portable` | exit 0 | PASS |
| Q8 | Portable đồng bộ | `python3 -m unittest test_portable_sync test_docs_consistency` | OK | PASS |
| Q9 | Cấu hình plugin | `claude plugin validate . --strict` | ✔ Validation passed, version 0.3.1 | PASS |
| Q10 | Smoke bản cài (a)(b)(c) | xem "Bằng chứng" | đúng kỳ vọng cả ba | PASS |
| Q11 | Hiệu năng vân tay repo | đo `repo_status_digest('.')` trên repo này | **32 ms** (trần timeout 2 s) | PASS |
| Q12 | Không đụng `bash_gate` | `grep -n "log_written" hooks/scripts/bash_gate.py` | không kết quả — không thêm regex đoán lệnh nào (diff còn lại là của 0.3.0 chưa commit) | PASS |

## Bằng chứng

### Q1
```
Ran 187 tests in 11.4s
OK
```

### Q10 — smoke trên bản cài user-level 0.3.1 (`TDQ_PROJECT_DIR` đặt riêng từng lệnh)

(a) Sửa code bằng `sed -i`, append log bằng `cat >>` → **không** chặn (bug gốc đã hết):
```
(rỗng)
```

(b) Sửa file **tracked** bằng `sed -i`, không ghi log → chặn:
```
{"decision": "block", "reason": "[TDQ:LOG] Turn này đổi repo (src_a.py) nhưng docs/workinglog/2026-07-29.md chưa được append. …"}
```

(c) Sửa nội dung file **untracked**, không ghi log → chặn (sau khi vá QC1.1):
```
{"decision": "block", "reason": "[TDQ:LOG] Turn này đổi repo (src_a.py) nhưng …"}
```

## Lỗi phát hiện trong QC và đã sửa

- **QC1.1 — bỏ lọt file untracked.** Smoke (b) vòng đầu **không** chặn: `git status
  --porcelain` in `?? path` y hệt dù nội dung đổi, còn `git diff HEAD` không đụng tới
  file untracked (repo chưa commit thì cũng không có `HEAD`). Đã băm thêm
  `size:mtime_ns` của các path `??` (cap 200 file); test
  `test_turn_snapshot::test_digest_catches_edit_of_untracked_file` red → green.

## Ghi chú lệch so với spec

1. Spec chỉ nói vân tay là `git status --porcelain`. Thực tế phải gồm **ba** phần
   (`status --porcelain -uall` + `diff HEAD` + `size:mtime` của file untracked) mới
   không bỏ lọt — porcelain đứng yên khi sửa tiếp một file vốn đã `M` hoặc đã `??`.
2. Spec không nêu vùng loại trừ. Thực tế `stop_gate` **không** tính thay đổi trong
   `docs/tdq/` là "đổi repo" — nếu tính thì mỗi lần ghi state lại tự đòi ghi log.
   Spec/plan viết bằng tool Edit vẫn được sổ turn ghi nhận như cũ.
3. Snapshot lưu thêm `repo_paths` (cap 100) để nêu đúng tên file trong lời chặn.
   Khi trong turn không có file nào **mới** xuất hiện, lời chặn nêu file đang bẩn đầu
   tiên — có thể không phải file vừa sửa (smoke (c) nêu `src_a.py` thay vì
   `untracked.py`). Chấp nhận: đây là chuỗi gợi ý, không phải danh sách đầy đủ.

## Kết luận

PASS 12/12 hạng mục ở vòng 1, sau khi sửa QC1.1.
