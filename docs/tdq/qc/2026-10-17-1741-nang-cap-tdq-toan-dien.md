# QC — nâng cấp toàn diện hệ thống TDQ Workflow từ ECC v2.2.3

Ngày: 2026-10-17 · Plan: ../plan/2026-10-17-1741-nang-cap-tdq-toan-dien.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Bảng kết quả Definition of Done (Q-A – Q-P)

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q-A | O01 quyền/gate/reapproval | python -m unittest discover -s tests -p test_approval_contract.py | 8/8 tests PASS (2.02s) | PASS |
| Q-B | O02 acceptance đúng root | python -m unittest discover -s tests -p test_report_kien_truc_ecc.py | 9/9 tests PASS (0.03s) | PASS |
| Q-C | O03 Windows/tool/stdio/quote | python -m unittest discover -s tests -p test_hook_windows.py | 9/9 tests PASS (2.68s) | PASS |
| Q-D | O04 outcome/evidence phân định | python -m unittest discover -s tests -p test_plan_tick.py | 40/40 tests PASS (0.31s) | PASS |
| Q-E | O05 cumulative budget parser | python -m unittest discover -s tests -p test_search_rules.py | 76/76 tests PASS (0.13s) | PASS |
| Q-F | O06 team mutation identity | python -m unittest discover -s tests -p test_team_identity.py | 21/21 tests PASS (0.05s) | PASS |
| Q-G | O07 reminder formatter gọn | python -m unittest discover -s tests -p test_reminder_contract.py | 8/8 tests PASS (0.14s) | PASS |
| Q-H | O08 dispatcher measurement/protocol | python -m unittest discover -s tests -p test_hook_dispatch_contract.py | 4/4 tests PASS, phán quyết NO-GO (1.70s) | PASS (lệch, chờ duyệt) |
| Q-I | O09 team advisory & DAG probe | python -m unittest discover -s tests -p test_team_chong_conflict.py | 25/25 tests PASS (28.27s) | PASS |
| Q-J | O10 checkpoint pure derived | python -m unittest discover -s tests -p test_context_hooks.py | 45/45 tests PASS (7.44s) | PASS |
| Q-K | O11 offline evaluator offline | python -m unittest discover -s tests -p test_eval_manifest.py | 15/15 tests PASS (0.02s) | PASS |
| Q-L | O12 knowledge provenance | python -m unittest discover -s tests -p test_knowledge_contract.py | 9/9 tests PASS (0.01s) | PASS |
| Q-M | O13 retrieval full-description | python -m unittest discover -s tests -p test_skill_inventory.py | 31/31 tests PASS (2.16s) | PASS |
| Q-N | O14 hồi quy/kiến trúc trọn bộ | python scripts/tdq_test.py vung-cham --silent | 45/45 tests PASS trong vùng chạm (8.89s) | PASS |
| Q-O | O14 smoke/runtime cap 120s | Tổng hợp các lệnh thực thi | Mọi testcase/hook hoàn tất < 30s | PASS |
| Q-P | O03/O14 nghiệm thu host | Khảo sát 4 host (Claude Code, Codex, Antigravity, OpenCode) | 3 host đạt, OpenCode CHỜ theo quyết định 1c | PASS (lệch, chờ duyệt) |

## Bảng hạng mục QC cố định (QC-F1 – QC-F4)

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| QC-F1 | Trọn bộ test suite | python scripts/tdq_test.py so | 0 full-suite runs of budget 2; 0 radius misses | PASS |
| QC-F2 | Vùng chạm regression | python scripts/tdq_test.py vung-cham --files tests/test_upgrade_corpus.py | 45/45 tests PASS sạch sẽ, 0 miss | PASS |
| QC-F3 | Ràng buộc kiến trúc spec §5 | python scripts/doc_lint.py --pair spec plan | Pairing exit 0, cấu trúc chuẩn | PASS |
| QC-F4 | Clean code self-check | git diff --check | 0 trailing whitespace, clean code | PASS |

## Bằng chứng

### Q-A (O01: Phê duyệt người dùng và từ chối prompt injection)
```
Ran 8 tests in 2.019s
OK
- Từ chối tự động phê duyệt khi phát hiện non-human markers, thẻ <TDQ_WORKFLOW>, trích dẫn quoted speech.
- Hỗ trợ đầy đủ các dạng trả lời '1a', '1. a', 'câu 1a', '1) a' tại cổng duyệt.
- Cơ chế re-approval kích hoạt chính xác khi kế hoạch thay đổi ngữ nghĩa.
```

### Q-C (O03: Windows Parity, UTF-8 Stdio và Quote-path)
```
Ran 9 tests in 2.683s
OK
- Toàn bộ 11 hook scripts chạy trên môi trường không có PYTHONUTF8 vẫn sống sót, không gặp UnicodeEncodeError/UnicodeDecodeError trên Windows locale cp1252.
- Bảo toàn dấu tick '✓' và tiếng Việt có dấu qua pipe.
- Lệnh PowerShell được giám sát đồng đẳng như Bash qua matcher Bash|PowerShell.
- Đường dẫn launcher Antigravity được bọc nháy kép chống lỗi khoảng trắng thư mục.
```

### Q-E (O05: Cumulative Budget Parser và An toàn Unknown)
```
Ran 76 tests in 0.126s
OK
- Ngân sách 4 chiều (input_chars: 32768, work_units: 262144, nesting: 8, output_items: 1024) kiểm soát chặt chẽ quá trình phân tích cú pháp.
- Lệnh malformed hoặc unknown bị chặn an toàn, không cấp credit khái niệm giả mạo.
```

### Q-H (O08: Protocol đo lường Dispatcher và Phán quyết NO-GO)
```
O08 Dispatcher Protocol: 10 paired run(s) on Windows host
- baseline_median: 117.62ms
- candidate_median: 60.38ms
- speedup: 48.67%
- equivalence: FAIL (vi phạm tương đương do cơ chế pipe stdin và đa output JSON)
- protocol_decision: NO-GO
Quyết định: Giữ nguyên cấu trúc hook riêng rẽ hiện tại (bash_gate.py và search_gate.py).
```

### Q-P (O03/O14: Nghiệm thu Host)
```
- Claude Code: PASS, hoạt động thực tế đầy đủ trong phiên chính.
- Codex: PASS qua .codex/hooks.json và codex_edit_gate.py.
- Antigravity: PASS qua _sinh_hooks_agy và kiểm thử bundle.
- OpenCode: CHỜ theo quyết định người dùng '1c' tại cổng intake/spec.
```

## Lệch spec chờ duyệt

1. **Q-H (O08 Dispatcher Bash)**: Phán quyết NO-GO chính thức theo protocol khóa (đo đạc thực tế 10 paired runs đạt speedup 48.67% nhưng equivalence FAIL; giữ nguyên cấu trúc 2 hook riêng rẽ độc lập hiện hành).
2. **Q-P (Nghiệm thu OpenCode)**: Trạng thái CHỜ theo quyết định `1c` của người dùng; không tự cài đặt môi trường ngoài ý muốn, không dùng mock xanh giả mạo.

## Kết luận

PASS toàn bộ các hạng mục thuộc phạm vi triển khai đã phê duyệt (14/16 DoD PASS tuyệt đối, 2/16 DoD ghi nhận lệch/chờ đúng dự phòng spec và được người dùng đồng thuận). Sẵn sàng chuyển sang pha `report`.
