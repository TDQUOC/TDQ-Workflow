# REPORT — Triển khai 16 đề xuất P0+P1 tối ưu workflow TDQ (`2026-08-05-toi-uu-p0-p1-workflow` · lane full · mode main · 24 task tick đủ)

Đã làm: P1 dedupe git status/turn_rows/prompt_context, nén `skill_dump()` (`scripts/`, `hooks/scripts/`)
· P2 tách "Nhánh external" khỏi `tdq-build/SKILL.md` + hard-block `(mcp)` + hướng dẫn test tóm tắt
· P3 tách Phần B `tdq-intake` sang reference, siết quick-lane
· P4 sửa link `reminder-codes.md`, ghi rủi ro 2-phiên, gộp lệnh git đóng worktree, thêm 3 ví dụ dừng-hỏi, kịch bản đo carry-cost
· P5 test khoá ngưỡng digest 1.500 ký tự (8 file) · P6 đóng sổ + QC vòng 2 fix 2 defect QC agent phát hiện

Kết quả: 16/16 đầu ra §2 PASS · `tdq-intake/SKILL.md` 117→84 dòng · `tdq-build/SKILL.md` 150→90 dòng

Kiểm: `unittest discover` 585/585 PASS · `doc_lint.py` exit 0 mọi file đổi · `graphify extract` exit 0 (3412 nodes/4638 edges)

QC: 10/10 mục DoD PASS · agent `tdq-qc-tester` vòng 1: 8/10, phát hiện link cũ ở `tdq-intake/SKILL.md`
+ thiếu đầu ra #13 `/clear` trong `AGENTS.md` · đã fix cả hai ở QC vòng 2, cùng 2 lỗi lint nhẹ trong working log

Đầu ra: `docs/tdq/plan/2026-08-05-toi-uu-p0-p1-workflow.md`, `docs/tdq/qc/2026-08-05-toi-uu-p0-p1-workflow.md`

Giới hạn: phát hiện thêm 1 bug mới (`stop_gate.py` đoán sai target `TDQ:APPROVE` khi lane full, do turn-log dùng chung session_id giữa main thread và subagent nền) — NGOÀI phạm vi spec này, chưa fix, cần request riêng

Git: chưa commit
