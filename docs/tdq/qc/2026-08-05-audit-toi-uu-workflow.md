# QC — Audit toàn bộ workflow TDQ, đề xuất tối ưu token/thời gian (vòng 3)

Đối chiếu spec §6 (`docs/tdq/spec/2026-08-05-audit-toi-uu-workflow.md` bản 1.1).

| # | Hạng mục | Lệnh/cách kiểm | Bằng chứng | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Report ngắn gọn, đúng khuôn TDQ | đọc lại bằng mắt | `docs/tdq/reports/2026-08-05-audit-toi-uu-workflow.md` — 26 dòng (`wc -l`), đúng khuôn `report-template.md` mới (Đã làm/Kết quả/Kiểm/Đầu ra/Giới hạn/Git), không placeholder | PASS |
| Q2 | Report + knowledge + spec qua lint | `python3 scripts/doc_lint.py docs/tdq/reports/... docs/tdq/knowledge/... docs/tdq/spec/...` | exit 0 (chạy chung với plan + `skills` + `portable`, cũng exit 0) | PASS |
| Q3 | Mọi finding ở knowledge mục 2-4 xuất hiện trong bảng ưu tiên | đối chiếu tay: 10 (mục 3) + 4 (mục 4) + 9 deferred + 1 nợ đo lường = 24 nguồn | knowledge mục 9: 6 dòng P0 + 13 dòng P1 (P1-1..P1-13) + 7 dòng P2 (P2-1..P2-7) = 26 dòng đề xuất, phủ đủ 24 nguồn (S2 gộp 4 loại trùng lặp thành 1 dòng P1-2, có ghi chú "Ghi chú đối chiếu Q3" giải thích) — không thiếu mục nào | PASS |
| Q4 | Số liệu report khớp số đã đo | đối chiếu report với knowledge mục 1 | report: "142.493.808 token / 1.310 API call ... Read file 47,75M · Bash khác 36,98M · tavily search 16,55M" khớp nguyên văn knowledge mục 1 | PASS |
| Q5 | Convention report đã nới đồng bộ, không vỡ test | `cd tests && python3 -m unittest test_phase_table test_claude_md_core -v` + `grep -rn "≤ *10 dòng" skills/ portable/ scripts/tdq_state.py` | 2 test suite: 8/8 + 5/5 PASS. grep còn 8 dòng khớp — toàn bộ là convention "tóm tắt/status trong chat" (tdq-spec, tdq-plan, tdq-intake, tdq-status, lane-decision.md, 2 bản portable song song) — không còn khớp ở report-file `docs/tdq/reports/<slug>.md` | PASS |

## Kiểm bổ sung (không nằm trong Q1-Q5 nhưng thuộc DoD)
- Full suite: `cd tests && python3 -m unittest discover -v` → 575 test, 0 fail.
- `graphify extract . --code-only` → exit 0, `graphify-out/graph.json` mtime mới hơn lúc bắt đầu P2 (3315 node, 4550 edge).
- Byte budget `portable/claude-md/CLAUDE.md`: 3405/3500 byte (còn 95 byte) — không vỡ trần `MAX_BYTES` của `test_claude_md_core.py`.
- `diff` bản repo và bản đã cài `~/.claude/CLAUDE.md` → rỗng. Backup: `~/.claude/CLAUDE.md.bak-20260805-1159`.

## Kết luận
5/5 mục Q1-Q5 PASS. Không có defect cần vòng fix. Chuyển phase `report`.
