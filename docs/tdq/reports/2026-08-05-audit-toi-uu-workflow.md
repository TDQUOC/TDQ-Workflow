# REPORT — Audit toàn bộ workflow TDQ, đề xuất tối ưu token/thời gian (`2026-08-05-audit-toi-uu-workflow` · lane full · mode main · 14 task tick đủ)

Đã làm: audit toàn bộ `skills/tdq-*`, `scripts/*.py`, hook, đối chiếu vòng 1/2 (5 agent
song song + research 4 truy vấn tavily-primary) · viết 26 đề xuất xếp ưu tiên P0/P1/P2
vào `knowledge` mục 9 (6 P0 · 13 P1 · 7 P2, kèm effort/impact — phủ đủ 24 nguồn audit +
2 mục bổ sung: đã làm + đối chiếu research) · nới trần report `≤10 dòng` → khuyến nghị
10-20 dòng, không giới hạn cứng, đồng bộ ở 9 vị trí.

Kết quả: carry-cost hiện tại 142.493.808 token / 1.310 API call (3 session mới nhất,
sau fix vòng 2) — top nhóm Read file 47,75M · Bash khác 36,98M · tavily search 16,55M.
Số này KHÔNG so sánh trực tiếp được với vòng 1/2 (khác cỡ mẫu session) — xem knowledge
mục 2.

Kiểm: `unittest discover` 0 fail · `test_phase_table.py` + `test_claude_md_core.py`
PASS · `doc_lint.py` exit 0 trên report/knowledge/spec/plan + `skills` + `portable` ·
`grep "≤ *10 dòng"` chỉ còn khớp convention "tóm tắt trong chat" (cố tình giữ) ·
`graphify extract . --code-only` exit 0.

Đầu ra: `docs/tdq/knowledge/2026-08-05-audit-toi-uu-workflow.md` mục 9 (danh sách đầy
đủ) · 9 file sửa cho việc nới trần report (xem plan P2) · backup
`~/.claude/CLAUDE.md.bak-<timestamp>`.

Giới hạn: 2 mâu thuẫn luật (P0-4, P0-5) và rủi ro false-positive `stop_gate.py` (P1-3)
mới NÊU + đề xuất hướng sửa, CHƯA sửa — round này chốt dừng ở report theo yêu cầu user.
Nợ đo lường before/after theo kịch bản chuẩn hoá (P1-12) vẫn treo từ vòng 2.

Git: chưa commit.
