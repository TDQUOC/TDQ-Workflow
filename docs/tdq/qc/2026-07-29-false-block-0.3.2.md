# QC — Vá chặn oan do vân tay repo (0.3.2)

Ngày: 2026-07-29 · Plan: ../plan/2026-07-29-false-block-0.3.2.md · Vòng: 1

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Toàn bộ suite | `python3 -m unittest discover tests` | Ran 204 tests — OK (0.3.1: 187) | PASS |
| Q2 | Helper vân tay | `python3 -m unittest test_turn_snapshot` | 22 test OK (11 test mới) | PASS |
| Q3 | Stop gate | `python3 -m unittest test_stop_gate` | 31 test OK (6 test mới) | PASS |
| Q4 | Không hồi quy hook | `python3 -m unittest test_context_hooks test_e2e_chain test_hook_resilience test_compliance_protocol test_token_budget` | OK | PASS |
| Q5 | Lint + portable | `python3 scripts/doc_lint.py skills portable` · `test_portable_sync test_docs_consistency` | exit 0 · OK | PASS |
| Q6 | Cấu hình plugin | `claude plugin validate . --strict` | ✔ Validation passed, version 0.3.2 | PASS |
| Q7 | Hết chặn oan (A, B) | smoke A1/A2/B trên bản cài user-level | **không** chặn cả ba | PASS |
| Q8 | Không hồi quy 0.3.1 | smoke (a)(b)(c) | (a) không chặn · (b)(c) chặn | PASS |
| Q9 | Log service (D) | shim `git` treo 5 s → chạy `stop_gate` | 2 dòng ⚠️ kèm timestamp, rc=0, không crash | PASS |
| Q10 | Hiệu năng | đo `repo_status_digest('.')` trên repo này | **53 ms** (0.3.1: 32 ms; trần timeout 2 s) | PASS |

## Bằng chứng

### Q7 — ba kịch bản audit, dựng lại nguyên trạng (bản cài 0.3.2)
```
### A1 — turn read-only (không sửa gì), repo có file bẩn sẵn:      (rỗng)
### A2 — turn chỉ ghi state:                                       (rỗng)
### B — touch file untracked (nội dung y nguyên):                  (rỗng)
```
0.3.1 chặn cả ba với `[TDQ:LOG] Turn này đổi repo (a.py)` / `(scratch.txt)`.

### Q8 — hồi quy 0.3.1
```
### 0.3.1-a — sửa code + append log bằng `cat >>`:  (rỗng — đúng, không chặn)
### 0.3.1-b — sed -i file tracked, không ghi log:
[…] ℹ️ stop_gate: chặn TDQ:LOG · nguồn=vân tay repo · path=a.py
{"decision": "block", "reason": "[TDQ:LOG] Turn này đổi repo (a.py) …"}
### 0.3.1-c — sửa nội dung file untracked, không ghi log:  → block
```

### Q9 — git treo quá 2 s
```
[…] ⚠️ git status quá 2s tại /var/folders/…/tmp.WYEX3Lgu9O — bỏ qua bằng chứng đĩa
[…] ⚠️ stop_gate: cuối turn không lấy được vân tay repo — bỏ qua bằng chứng đĩa, chỉ còn dựa vào sổ turn
rc=0
```

## Không sửa (có chủ ý)

- **E — hook `SubagentStop`**: subagent không phải nơi ghi working log; gắn gate ở đó là
  tạo thêm một kiểu chặn oan. Vân tay git ở Stop của phiên cha đã bắt được file subagent ghi.
- **H — `stop_hook_active`**: sau lần chặn đầu, Stop kế im lặng. Đây là ràng buộc của
  Claude Code, không phải bug: gate là *nhắc một lần*, không phải cưỡng chế. Đã ghi vào doc.
- Tên file trong lời chặn vẫn có thể trỏ nhầm khi không có file **mới** xuất hiện
  (smoke (c) nêu `a.py` thay vì `untracked.py`) — là chuỗi gợi ý, đã ghi rõ giới hạn.

## Kết luận

PASS 10/10 ở vòng 1. Chi phí vân tay tăng 32 → 53 ms do băm nội dung file untracked;
đổi lấy việc hết báo động giả theo `mtime`, vẫn cách trần timeout 2 s rất xa.
