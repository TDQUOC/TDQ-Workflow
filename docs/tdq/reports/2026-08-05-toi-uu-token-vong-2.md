# REPORT — Tối ưu token/time vòng 2 (`2026-08-05-toi-uu-token-vong-2` · lane full · mode main · 21+2 task tick đủ)

Đã làm: P1 sửa lỗi đếm `token_audit.py` ±62% + cột chi phí quy đổi · P2 CLAUDE.md lõi 8 mục, luật chi tiết dời sang `skills/*/references/`, 10 LSP sang tier `on_demand` · P3 `scripts/tdq_finish.py` gộp 4 việc cuối turn · P4 8 luật tiết kiệm context vào 3 SKILL.md + 2 file `portable/workflow/` · P5 ngưỡng digest cho 7 agent.
Kết quả: `~/.claude/CLAUDE.md` 12.245 → 3.233 byte (−73,6%) · plugin bật 27 → 17 · bookkeeping cuối turn 4 lệnh → 1 · `tdq_state.py next` 1.350 → 130 ký tự · `set` 581 → 70 · `doc_lint` đúng file 8.092 → 0 · digest sub-agent nay có trần 1.500 ký tự.
Đo session (`token_audit.py --sessions 2` trên `0f97200f-81a3-4bbb-8d86-8df8e95afb65` + `ff4b7d6f-adf6-4a11-814e-8d2c10b80013`): BEFORE 01:14 = 14.730.000 → AFTER 01:57 = 20.294.187 quy đổi input-token. Số này KHÔNG chứng minh cải thiện vì đo bên trong chính session đang dài thêm; tối ưu context nền chỉ có hiệu lực từ session sau — kiểm lại bằng session mới.
Kiểm: `cd tests && python3 -m unittest discover` 521 test xanh · `doc_lint.py skills portable` exit 0 · graphify 2915 node / 4072 edge · QC `tdq-qc-tester` PASS 10/10 mục DoD, 2 defect nhẹ (Q1 report dài, Q2 thiếu working log) đã sửa.
Đầu ra: `scripts/tdq_finish.py`, `scripts/token_audit.py`, `portable/claude-md/CLAUDE.md`, 7 `agents/*.md` · Backup: `~/.claude/CLAUDE.md.bak-20260805-0142`, `~/.claude/plugin-tiers.json.bak-20260805-0142`, `~/.claude/CLAUDE.md.bak-20260805-0219`.
Giới hạn: chưa có số đo trên session sạch nên mức giảm thực tế chưa xác nhận · mọi đề xuất làm giảm độ tin cậy đã bị loại từ spec, chỉ cắt phần dán lại dữ liệu đã có trên đĩa.
Git: chưa commit — cây làm việc giữ cả thay đổi vòng 1 (P0) lẫn vòng 2.
