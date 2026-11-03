# REPORT — Ví dụ & hướng dẫn thân thiện cho câu hỏi kiểu A/B/C (`2026-08-13-vi-du-cau-hoi-lane` · lane full · mode main · 5 task tick đủ)

Đã làm: P1 đổi khối hint cuối `interview.md` thành 2 phần (nguyên tắc + ví dụ trung tính) ·
P2 rà 3 dòng `➤ Duyệt:` (tdq-spec, tdq-plan, tdq-intake), cả 3 kết luận SỬA — thêm vế nói
rõ bước tiếp theo (viết plan/build/implement ngay) · P3 doc_lint gộp 4 file.
Kết quả: khối hint `interview.md` 1 dòng chung chung → 2 phần rõ ràng · 3 dòng `➤ Duyệt:`
thiếu vế "dẫn tới gì" → có đủ vế đó ở cả 3 file.
Kiểm: `doc_lint.py` từng file + gộp 4 file đều exit 0 · QC 4/4 mục DoD PASS (bằng chứng ở
`docs/tdq/qc/2026-08-13-vi-du-cau-hoi-lane.md`) · không có unit test code (việc thuần văn bản).
Đầu ra: `skills/tdq-intake/references/interview.md`, `skills/tdq-spec/SKILL.md`,
`skills/tdq-plan/SKILL.md`, `skills/tdq-intake/SKILL.md`.
Giới hạn: `skills/tdq-status/SKILL.md:32` có dòng `➤ Duyệt:` tương tự nhưng ngoài phạm vi
spec (chỉ 3 file được liệt) — cố tình chưa sửa, cần request riêng nếu muốn đồng bộ.
Git: chưa commit.
