# REPORT — Dựng lại `portable/` cho Codex + cập nhật tài liệu project-level (`2026-08-11-cai-tdq-project-level` · lane full · mode main · 20/20 task tick đủ)

Đã làm: P1 core `AGENTS.md`/`README.md` · P2 4 file phase workflow (`01-intake`…`04-build`, spec-template + report-template gộp thẳng vào file phase để giữ đủ 11 file) · P3 4 file reference + `phases.md` tự sinh (khuôn interview inline vào `01-intake.md`) · P4 sửa `docs/notes/user-level-install.md` (mở phạm vi user+project-level), `README.md` không cần sửa (chưa từng mô tả sai `portable/`) · Px đếm đủ 11 file
Kết quả: `portable/` 0 file → 11 file (đúng bảng §2 spec) · `docs/notes/user-level-install.md` mục 1+4 cập nhật, không còn trỏ chết
Kiểm: `doc_lint.py` trên spec exit 0 · QC 7/7 hạng mục PASS (Q1 phases.md khớp PHASE_TABLE, Q2 chỉ 1 ghi chú lịch sử gắn nhãn đã bỏ, Q3 AGENTS.md đủ mục, Q4 mọi path còn sống, Q5 README không sai, Q6 doc_lint spec exit 0, Q7 đủ 11 file) — chi tiết trong plan mục `## QC`
Đầu ra: `portable/{AGENTS,README}.md`, `portable/workflow/{01-04}.md`, `portable/workflow/phases.md`, `portable/workflow/references/{approval,plan-template,qc,quick-lane}.md`, `docs/notes/user-level-install.md`
Giới hạn: không có script tự động cài đặt (theo yêu cầu, docs-only) · chưa test thật với Codex trên project mẫu (QC bằng self-review/đối chiếu `scripts/tdq_state.py` + `skills/`, không có `test_portable_sync.py`) · đồng bộ `portable/` với `skills/` về sau vẫn là việc thủ công, đã cảnh báo rõ trong `portable/README.md`
Git: chưa commit
