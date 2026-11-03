# REQUEST — Thực thi 5 task P0 của đề xuất tối ưu token

Ngày: 2026-08-04 · Nguồn: ../knowledge/2026-08-04-de-xuat-toi-uu-token.md

## Nguyên văn yêu cầu

Người dùng trả lời `1` cho câu hỏi cuối report `2026-08-04-toi-uu-token-workflow`:

> 1. Mở request mới để **thực thi** đề xuất? Khuyên bắt đầu đúng 5 task P0.
> 2. Commit đợt này không? …

→ Chọn (1): mở request mới thực thi đề xuất, bắt đầu bằng 5 task P0.

## Cách hiểu đầu tiên

**Mục tiêu:** hiện thực hoá đúng 5 task hạng P0, cắt ~51% carry-cost với ~4–5 giờ công.

| Task | Nội dung | File dự kiến chạm |
|---|---|---|
| A4 | `tdq_state.py` mặc định in 1 dòng; `--json` mới in đầy đủ | `scripts/tdq_state.py`, `tests/test_tdq_state.py`, chỗ gọi trong skill |
| A5 | `doc_lint.py` im khi PASS | `scripts/doc_lint.py`, `tests/test_doc_lint.py` |
| D1 | Luật gộp lệnh Bash độc lập vào 1 call | `skills/tdq-conventions/`, `~/.claude/CLAUDE.md`(?) |
| D2 | Test theo module lúc implement, full suite 1 lần ở QC | `skills/tdq-build/SKILL.md`, `skills/tdq-plan/` |
| B1 | Research LUÔN chạy trong subagent, trả digest ≤1.500 ký tự | `skills/tdq-intake/SKILL.md`, `skills/tdq-conventions/references/` |

**Đo lại sau khi làm:** `python3 scripts/token_audit.py --sessions 2 --top 8`.

## Chỗ chưa rõ (cần hỏi)

1. Lane: quick hay full? (đề xuất đã có sẵn task + test + ước lượng → phân tích gần như xong)
2. A4/A5 đổi output CLI — có chỗ nào khác đang parse output đó không (hook, portable, test)?
3. D1/D2 là **luật prose**: viết vào skill của plugin hay vào `~/.claude/CLAUDE.md`?
   (Đề xuất C1 nói CLAUDE.md phải gầy đi → nghiêng về skill.)
4. B1 dùng agent nào làm mặc định: `search-scout` hay `Explore`?
5. Có làm luôn C1 (CLAUDE.md bản lõi, hạng P1) trong đợt này không, hay để đợt sau?
6. Câu hỏi số 2 của report cũ vẫn chưa trả lời: commit đợt trước hay chưa?
