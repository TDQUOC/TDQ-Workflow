# QC — Câu hỏi TDQ bị ẩn khi bật focus mode

Ngày: 2026-08-13 · Spec: ../spec/2026-08-13-focus-mode-an-cau-hoi.md · Lane: full
QC độc lập: BỎ (đã chốt trong spec §1b — không có code để test). Tự QC bằng đọc lại +
`doc_lint.py`.

## Kết quả

| # | Hạng mục | Bằng chứng | Kết quả |
|---|---|---|---|
| Q1 | Report có trích đường dẫn:dòng thật của `stop_gate.py` | §2 report trích `hooks/scripts/stop_gate.py:9`, dòng 107-188, 139-144 — đối chiếu file thật khớp | PASS |
| Q2 | Report có trích nguồn research chính thức | §2 report trích `code.claude.com/docs/en/commands.md`, release v2.1.221, GitHub Issue #50894 — đúng kết quả agent `claude-code-guide` trả về | PASS |
| Q3 | `doc_lint.py` PASS trên report | `python3 scripts/doc_lint.py docs/tdq/reports/2026-08-13-focus-mode-an-cau-hoi.md` → exit 0 | PASS |

## Kết luận
3/3 PASS. DoD đạt — không còn mục QC nào FAIL, không cần thêm task fix.
