# REQUEST — Tối ưu thời gian + token cho TDQ workflow

Ngày: 2026-08-04 · Slug: 2026-08-04-toi-uu-token-workflow

## Nguyên văn yêu cầu

> Phân tích và check issue và những dự kiến có thẻ gây tốn time, token không cần thiết
> cho workflow đồngg thời resreach phương thức giải quyết lâu dài hiệu quả và đề xuất lại.
> vì hiện tại tôi cảm giac tốn quá nhièu time + token, hãy check xem có thể tối ưu hơn không?

## Cách hiểu đầu tiên

- **Mục tiêu:** tìm ra các điểm trong TDQ workflow đang đốt time/token không cần thiết,
  research cách giải quyết bền vững, và đề xuất phương án chỉnh sửa (chưa implement ngay).
- **Phạm vi đoán:** context injection mỗi prompt (hook `prompt_context.py`, `session_start.py`),
  kích thước skill/reference được nạp, số file doc sinh ra mỗi request, số vòng interview,
  số lần chạy full test suite, mode subagent/external, agent model/effort.
- **Chưa rõ:**
  - Đầu ra mong muốn: chỉ báo cáo phân tích + đề xuất, hay làm luôn cả phần sửa?
  - Ngưỡng chấp nhận: giảm bao nhiêu % token là đạt?
  - Được phép hy sinh gì (bớt doc, bớt gate, bớt test) hay giữ nguyên chất lượng?

## Số liệu thô ban đầu (đo tại thời điểm mở request)

- 6 SKILL.md = 542 dòng; 16 file references = 928 dòng; portable = 630 dòng.
- 7 agent frontmatter = 181 dòng; 5 hook script = 716 dòng.
- `~/.claude/CLAUDE.md` = 93 dòng, nạp mọi turn ở mọi project.
- Mỗi request lane full sinh 8 file doc (requests, questions, research, knowledge,
  spec, plan, qc, reports) + working log.
