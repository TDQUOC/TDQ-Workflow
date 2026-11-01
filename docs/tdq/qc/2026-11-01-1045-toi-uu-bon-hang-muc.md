# QC — Tối ưu bốn hạng mục

Ngày: 2026-11-01 · Lane full · QC ultra · Source 6f03e5bec06c11ed1bc7d9c14609d09ce9f3b55f2fc0b069057c80cce97543bc
Soul: chất lượng > runtime > context cost

| # | Lệnh / chứng cứ | Kết quả |
|---|---|---|
| Q1 | verify_scope.py Q1 · qc-checks.json | PASS |
| Q2 | verify_scope.py Q2 · qc-checks.json | PASS |
| Q3 | verify_scope.py Q3 · qc-checks.json | PASS |
| Q4 | verify_scope.py Q4 · qc-checks.json | PASS |
| Q5 | verify_scope.py Q5 · qc-checks.json | PASS |
| Q6 | verify_scope.py Q6 · qc-checks.json | PASS |
| Q7 | verify_scope.py Q7 · qc-checks.json | PASS |
| Q8 | verify_scope.py Q8 · qc-checks.json | PASS |
| QC-F1 | Full --workers 1 --fresh --reuse off; QC-F1-check.json, test-budget-final.json | PASS: 3657 pass / 8 skip; 1 Full / budget2; 0 radius miss |
| QC-F2 | Guarded parent/radius T1.1, T1.2, T2.1, T3.1-owner, T3.2 và Full cuối | PASS: phủ tất cả Chạm, không chạy lặp cùng suite |
| QC-F3 | architecture-constraints.json, AST + final diff + architectural Full cases | PASS: 4 ràng buộc |
| QC-F4 | clean-code-check.json + independent-qc.md | PASS: 5 câu trả lời có và các owner fix đã kiểm |

## Bằng chứng lệnh Q1–Q8

```json
{"check": "Q1", "status": "PASS", "details": {"regressions": 53, "obligations": 3, "baseline_cases": 3602, "current_cases": 3665, "remapped": 0, "source_sha256": "6f03e5bec06c11ed1bc7d9c14609d09ce9f3b55f2fc0b069057c80cce97543bc"}}
```

```json
{"check": "Q2", "status": "PASS", "details": {"regressions": 57, "obligations": 5, "baseline_cases": 3602, "current_cases": 3665, "remapped": 0, "source_sha256": "6f03e5bec06c11ed1bc7d9c14609d09ce9f3b55f2fc0b069057c80cce97543bc"}}
```

```json
{"check": "Q3", "status": "PASS", "details": {"regressions": 322, "obligations": 2, "baseline_cases": 3602, "current_cases": 3665, "remapped": 0, "changed_tests": 11, "migrations": 11, "source_sha256": "6f03e5bec06c11ed1bc7d9c14609d09ce9f3b55f2fc0b069057c80cce97543bc"}}
```

```json
{"check": "Q4", "status": "PASS", "details": {"regressions": 25, "obligations": 4, "baseline_cases": 3602, "current_cases": 3665, "remapped": 0, "top_cases": 20, "top_modules": 20, "quality": "complete", "source_sha256": "6f03e5bec06c11ed1bc7d9c14609d09ce9f3b55f2fc0b069057c80cce97543bc"}}
```

```json
{"check": "Q5", "status": "PASS", "details": {"regressions": 58, "obligations": 4, "baseline_cases": 3602, "current_cases": 3665, "remapped": 0, "input_sha256": "ec60b7816e0f7efc06f5b4784e3fd3f5c3ea0adf604ddbbeaac8cff700e7d7d2", "source_sha256": "6f03e5bec06c11ed1bc7d9c14609d09ce9f3b55f2fc0b069057c80cce97543bc"}}
```

```json
{"check": "Q6", "status": "PASS", "details": {"regressions": 7, "obligations": 1, "baseline_cases": 3602, "current_cases": 3665, "remapped": 0, "source_sha256": "6f03e5bec06c11ed1bc7d9c14609d09ce9f3b55f2fc0b069057c80cce97543bc"}}
```

```json
{"check": "Q7", "status": "PASS", "details": {"regressions": 9, "obligations": 3, "baseline_cases": 3602, "current_cases": 3665, "remapped": 0, "reviewer": "/root/gpt61sol_high_review_qc13", "source_sha256": "6f03e5bec06c11ed1bc7d9c14609d09ce9f3b55f2fc0b069057c80cce97543bc"}}
```

```json
{"check": "Q8", "status": "PASS", "details": {"regressions": 25, "obligations": 1, "baseline_cases": 3602, "current_cases": 3665, "remapped": 0, "source_sha256": "6f03e5bec06c11ed1bc7d9c14609d09ce9f3b55f2fc0b069057c80cce97543bc"}}
```

## Clean code

- SRP: CÓ — pure summary/render tách khỏi export I/O; OwnedProcessJob sở hữu lifecycle, Codex giữ probe policy; lỗi purity đã sửa tại owner T1.3.
- OCP: CÓ — phase/ranking/format và validation sets dùng dữ liệu, không thêm abstraction một use case; primitive có hai consumer Codex/IsolatedJob thực.
- LSP: CÓ — IsolatedJob giữ hợp đồng OwnedProcessJob và thêm pytest isolation; regression giữ caller env/HOME, stdin và error contracts; summary trả cùng schema quality.
- ISP: CÓ — summary chỉ nhận result, renderer nhận summary/provenance; process chỉ nhận launch/ownership inputs cần dùng.
- DIP: CÓ — Codex/pytest đi qua OwnedProcessJob, summary/export dùng tdq_test_report; state vẫn qua shared tdq_state; không nhân bản backend process.

## Giới hạn và trạng thái

Các 8 skip có ID/reason raw trong final-skips.json và result gốc; không biến thành PASS. D9/D10 SKIPPED_USER; không chứng nhận hiệu năng A/B, POSIX, thiết bị vật lý. Receipt FAIL trung gian được giữ. Ngoại lệ telemetry giới hạn đúng appendix đã duyệt. Browser thực direct CDP khi MCP Transport closed; đủ hai role × hai viewport, không phải MCP/physical device. LSP final check server process exited; trước triển khai đã có references/blast radius, cuối chỉ đọc source và dùng AST/grep; graph freshness được cập nhật ở tdq_finish, không là chứng cứ correctness thay test.

## Lệch spec chờ duyệt

tdq_state.py lech list: 0 item(s), 0 pending. Không nới ngưỡng DoD.

## Kết luận

PASS 12/12 mục chất lượng (Q1–Q8 và QC-F1–F4). Workflow chưa đóng: phase=implement vì guard11worktree cũ dirty; không sửa guard/ledger hoặc xóa source cũ. Chưa commit/push phần mới.
