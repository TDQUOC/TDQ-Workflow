# QC — Cắt token thừa trong TDQ workflow

Ngày: 2026-08-09 · Plan: ../plan/2026-08-09-cat-token-thua-workflow.md · Vòng: 1
Kết quả: **11/11 PASS**, không có vòng fix.

| # | Phép kiểm | Mong đợi | Thực tế | Kết |
|---|---|---|---|---|
| D1 | `grep -c "Đã xét" skills/tdq-intake/references/skill-inventory.md` | ≥ 1 | 2 | PASS |
| D2 | `grep -c "có runtime" skills/tdq-spec/references/spec-template.md` | ≥ 1 | 2 | PASS |
| D3 | `grep -c "Năng lực → task" skills/tdq-plan/references/plan-template.md` | 0 | 0 | PASS |
| D4 | `cd scripts && python3 -c "import doc_lint; print('Nạp' in doc_lint.CONTRACT_FIELDS)"` | `False` | `False` | PASS |
| D5 | `python3 scripts/tdq_state.py phases-doc \| grep -c "^## analyze"` | 0 | 0 | PASS |
| D6 | `cd tests && python3 -m unittest test_phase_table` | 0 fail | 8 test OK | PASS |
| D7 | `grep -c "có ít nhất một câu hỏi" skills/tdq-intake/references/interview.md` | ≥ 1 | 1 | PASS |
| D8 | `diff docs/claude-md-mau.md ~/.claude/CLAUDE.md` | exit 0, không in gì | exit 0, rỗng | PASS |
| D9 | `cd tests && python3 -m unittest test_claude_md_core` | 0 fail | 4 test OK | PASS |
| D10 | `python3 scripts/doc_lint.py <6 file skills/ vừa sửa>` | exit 0 | exit 0 | PASS |
| D11 | `cd tests && python3 -m unittest discover -p 'test_*.py'` | 0 fail | 412 test OK, 55s | PASS |

## Ghi chú

- D6 ban đầu ĐỎ đúng như dự kiến: `test_render_no_regex_escape_artifact` bổ mục
  `## analyze` trong output `phases-doc` — mục này chính là thứ T3.1 xoá. Đã sửa test để
  soi khối "Lệnh nguyên văn" (nơi lệnh thật còn nằm) thay vì mục chi tiết đã bỏ. Đây là
  cập nhật hợp đồng test theo thiết kế mới, không phải nới lỏng: test vẫn khẳng định
  không có literal `\1`, không wrap đôi backtick, và mỗi phase vẫn có lệnh `python3` thật.
- Test của T3.2 trong plan phải đổi so với bản duyệt: sau T3.1 chuỗi cần kiểm không còn
  xuất hiện trong `phases-doc`, nên chuyển sang soi thẳng hằng `PHASE_TABLE`. Ghi rõ ngay
  tại dòng task trong plan.
- `docs/claude-md-mau.md`: 3.463 → 3.460 byte NHƯNG đã hút thêm 2 mục mới mà bản cũ chưa
  có (§8 plugin đã bật sẵn, §9 mem0) vốn chỉ tồn tại ở `~/.claude/CLAUDE.md` (4.243 byte).
  Tức nội dung sau khi hợp nhất giảm ~18% so với bản live cũ, và hết lệch hai nguồn.
- `phases.md`: 89 → 33 dòng (−56, vượt ngưỡng −40 của plan).
