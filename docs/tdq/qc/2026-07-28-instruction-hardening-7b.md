# QC — Instruction hardening cho model yếu (0.3.0)

Ngày: 2026-07-29 · Plan: ../plan/2026-07-28-instruction-hardening-7b.md · Vòng: 1

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Toàn bộ suite | `python3 -m unittest discover tests` | Ran 162 tests — OK | PASS |
| Q2 | Giao thức tuân thủ | `python3 -m unittest test_compliance_protocol test_turn_ledger` | OK | PASS |
| Q3 | `next` / `--brief` / `get` | `python3 -m unittest test_next` | 7 test OK (gồm QC1.1) | PASS |
| Q4 | Lint R1–R7 | `python3 -m unittest test_doc_lint` | 10 test OK; `doc_lint.py skills portable` exit 0 | PASS |
| Q5 | Portable đồng bộ | `python3 -m unittest test_portable_sync` | 4 test OK; bước khớp 16/5/6/10 | PASS |
| Q6 | Không deny, không transcript | `grep -rn '"deny"\|transcript_path' hooks/ scripts/` | không kết quả | PASS |
| Q7 | Cấu hình plugin | `claude plugin validate . --strict` | ✔ Validation passed; version 0.3.0 | PASS |
| Q8 | Bản cài thật | uninstall → install `--scope user`, rồi `ls` cache | cache 0.3.0: 6 skill mới, có `portable/`, không có `tdq-approve` | PASS |
| Q9 | Smoke bản cài (a–d) | xem "Bằng chứng" | a/b/c/d đúng kỳ vọng | PASS |
| Q10 | Dọn dẹp | `ls docs/archive/v0.1`, `find . -name .DS_Store`, `test_docs_consistency` | 7 mục lưu trữ; 0 `.DS_Store`; có `CHANGELOG.md`; 5 test OK | PASS |
| Q11 | State file S1–S8 | `python3 -m unittest test_state_file` | OK | PASS |
| Q12 | Bảng phase không lệch | `python3 -m unittest test_phase_table` | OK — `phases.md` sinh từ `PHASE_TABLE` | PASS |
| Q13 | Ngân sách token | `python3 -m unittest test_token_budget` | 8 test OK, đo trên cả 6 phase | PASS |
| Q14 | Hook không làm hỏng tool call | `python3 -m unittest test_hook_resilience` | 4 test OK | PASS |
| Q15 | Skill đứng độc lập | `test_skill_shape` + đọc thủ công | 6 skill đủ bước đánh số, `Xong khi:`, `Bước kế tiếp:` | PASS |

## Bằng chứng

### Q1
```
Ran 162 tests in 8.024s
OK
```

### Q9 — smoke trên bản cài user-level (mọi lệnh đặt TDQ_PROJECT_DIR riêng)
(a) `next --brief` sau `init … quick`:
```
[TDQ:NEXT] 2026-07-29-smoke · lane quick · phase quick · Project: …/scratchpad/smoke
```
(b) Edit file ngoài `docs/` khi chưa duyệt → `allow` kèm lời nhắc:
```
{"permissionDecision": "allow", "additionalContext": "[TDQ:APPROVE] Đang sửa file ngoài docs/ mà quick chưa được ghi nhận duyệt. …"}
```
(c) Repo đổi mà chưa ghi working log → Stop chặn:
```
{"decision": "block", "reason": "[TDQ:LOG] Turn này đổi repo (src/a.py) nhưng docs/workinglog/2026-07-29.md chưa được append. …"}
```
(d) `approve quick` chạy 2 lần → `lần 1 rc=0`, `lần 2 rc=0` (duyệt lại không phải lỗi).

### Q12 — ghi chú lệch nhẹ so với spec
Spec ghi bảng phase nằm trong `portable/AGENTS.md`. Thực tế bảng được **sinh** ra
`portable/workflow/phases.md` và `AGENTS.md` trỏ tới đó — cùng một nguồn `PHASE_TABLE`,
test `test_phase_table::test_docs_match_constant` khoá cả hai file. Đạt đúng mục đích
(không có bảng viết tay), chỉ khác chỗ đặt.

## Kết luận

PASS toàn bộ 15 hạng mục ở vòng 1, sau khi sửa 1 lỗi phát hiện lúc smoke:

- **QC1.1** — dòng tiêu đề của `next` in `phase idle` cho lane quick trong khi thân bài
  dùng row `quick`; model dễ hiểu là hết việc. Đã sửa `next_headline` dùng `phase_key`,
  có test `test_next::test_headline_shows_quick_for_quick_lane` (red → green).
