# Rà soát 28 file luật `skills/` theo soul

Ngày: 2026-08-14 · Request: 2026-08-14-set-soul-workflow · Task: T3.1–T3.2
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Đối chiếu 4 nguyên tắc của `soul.md`: mục đích harness · thứ tự ưu tiên + luật phân xử ·
viết cho model yếu nhất · phạm vi áp hồi tố. Phán quyết: **HỢP** (đúng soul) ·
**SỬA** (đá soul, phải sửa) · **KHÔNG SỬA** (có căng với soul nhưng giữ, kèm lý do).

|File|Phán quyết|Lý do|
|---|---|---|
| skills/tdq-build/SKILL.md | HỢP | Red→green, cấm placeholder, tick ngay — chất lượng trên hết; test module lúc build + full suite ở QC là cắt runtime không đổi đầu ra |
| skills/tdq-build/references/qc.md | SỬA | "Số hạng mục QC = số dòng DoD" khoá cứng phạm vi QC, dễ sót lỗi ngoài DoD — nới thành QC-F1..F3 theo M5; sửa tại T6.3, số dòng ghi bổ sung khi task đó xong |
| skills/tdq-build/references/report-template.md | HỢP | "Dài hơn thì nói rõ vì sao thay vì cắt bớt sự thật" — chất lượng thắng độ ngắn, đúng luật phân xử |
| skills/tdq-status/SKILL.md | HỢP | `next --brief` tiết kiệm context nhưng có lối thoát "khi thật sự cần checklist đầy đủ" — không hạ chất lượng |
| skills/tdq-spec/SKILL.md | HỢP | §7 phải rỗng, còn câu hỏi thì quay lại analyze — không đoán, đúng nguyên tắc chất lượng |
| skills/tdq-spec/references/spec-template.md | HỢP | Khuôn đo được, cấm từ mơ hồ không kèm ngưỡng; đã mang dòng Soul; phần Clean code bổ sung ở P6 theo plan, không phải lỗi soul |
| skills/tdq-intake/SKILL.md | HỢP | Tầng nhỏ có 4 điều kiện đóng + luật thoát bắt buộc — cắt thủ tục cho việc 1 dòng mà không cắt chất lượng |
| skills/tdq-conventions/SKILL.md | HỢP | §11 đã trỏ soul làm luật gốc (fix T1.3); §10 tiết kiệm context không ép hạ chất lượng đầu ra |
| skills/tdq-conventions/references/approval.md | HỢP | Mơ hồ → HỎI, cấm suy diễn duyệt — đúng ý user quan trọng hơn tốc độ |
| skills/tdq-conventions/references/context-budget.md | SỬA | Nạp on-demand đứng một mình mà không có luật phân xử nào khi tiết kiệm đá chất lượng (vd "đọc vừa đủ" vs việc phải đọc trọn 28 file để rà soát) — thêm 1 bullet trỏ soul.md |
| skills/tdq-conventions/references/measure-scenario.md | HỢP | Đo bằng transcript thật, cấm ước lượng bằng mắt — bằng chứng thật đúng soul |
| skills/tdq-conventions/references/phases.md | HỢP | File tự sinh từ `PHASE_TABLE`; cột "cấm" chặn báo PASS khi chưa chạy — muốn đổi phải sửa nguồn trong `tdq_state.py`, không sửa tay file này |
| skills/tdq-conventions/references/plugin-routing.md | HỢP | Không khớp bảng thì không lôi plugin vào — plugin không liên quan không nâng chất lượng, chỉ tốn context |
| skills/tdq-conventions/references/reminder-codes.md | HỢP | Hook kiểm bằng hiệu ứng thật, in ✓ suông không thoát — chống khai khống |
| skills/tdq-conventions/references/subagent-tuning.md | HỢP | Hạ model chỉ cho việc thuần cơ học, việc chất lượng dùng inherit + effort high — đúng thứ tự ưu tiên |
| skills/tdq-conventions/references/tavily.md | HỢP | Trần ~6 call nhưng lối thoát là HỎI user chứ không đoán bừa; viết tiếng Anh vẫn đạt — soul không ràng ngôn ngữ file luật nội bộ |
| skills/tdq-conventions/references/user-facing-block.md | HỢP | Trang trí chỉ thêm ký tự đánh dấu, cấm đổi chữ nội dung — nội dung đứng trên hình thức |
| skills/tdq-conventions/references/worklog-images.md | HỢP | Cấm tự phán "ảnh không liên quan" rồi bỏ qua — chống cắt góc âm thầm |
| skills/tdq-intake/references/analyze-full.md | HỢP | ZERO chỗ đoán; research đầy đủ nằm trên đĩa, chỉ digest vào hội thoại — giảm context không mất dữ liệu |
| skills/tdq-intake/references/interview.md | HỢP | Cấm sang spec khi còn chỗ phải đoán; khuôn option 1 dòng cho model yếu theo được |
| skills/tdq-intake/references/issue-triage.md | HỢP | Chưa xem log thì chưa được đề xuất nguyên nhân — bằng chứng trước kết luận |
| skills/tdq-intake/references/lane-decision.md | HỢP | Một ô rơi cột deep là đề xuất deep — phân vân nghiêng về làm kỹ |
| skills/tdq-intake/references/quick-lane.md | KHÔNG SỬA | Bỏ full-suite toàn repo là cắt runtime có chủ đích cho việc 1–3 file: DoD vẫn kiểm từng dòng, vòng fix trần 3, vượt trần phải báo user — mức đầu tư tỷ lệ cỡ việc |
| skills/tdq-intake/references/scope-round.md | HỢP | Mức đầu tư lõi/vừa/đầy đủ suy từ bối cảnh bằng số — chất lượng là đúng nhu cầu thật, không phải max mọi thứ |
| skills/tdq-intake/references/skill-inventory.md | HỢP | Phân vân → DÙNG — nghiêng về tận dụng năng lực cho kết quả tốt hơn |
| skills/tdq-plan/SKILL.md | HỢP | Mỗi task đúng một việc + một phép kiểm đo được; "đừng đệm giờ" — số liệu thật |
| skills/tdq-plan/references/mode-gate.md | HỢP | Cấm lý do chung chung, đủ 4 căn cứ đọc từ chính plan — quyết định có bằng chứng |
| skills/tdq-plan/references/plan-template.md | HỢP | Đã mang dòng Soul; điểm `(nN)`/`(eNm)` là metadata ETA, không đổi luật tick hay chất lượng |

## Kết đếm

- 25 HỢP · 2 SỬA · 1 KHÔNG SỬA — đủ 28 file, không ô phán quyết nào trống.
- KHÔNG SỬA duy nhất (quick-lane) giữ nguyên vì trần đầu tư tỷ lệ với cỡ việc là đúng
  tinh thần "chất lượng hơn số lượng", và mọi lối cắt đều có hàng rào báo user.

## Sửa theo phán quyết SỬA (T3.2)

- `context-budget.md`: cũ 19 dòng nội dung (hết ở bullet "Việc nặng giao subagent",
  dòng 18–19) → thêm bullet "Soul phân xử" ở dòng 20–22, file thành 22 dòng.
- `qc.md`: giao **T6.3** sửa cùng lượt nối M5 để khỏi sửa đúp một file hai lần. Đã xong:
  bản build cũ dòng 32–40 (khối "Chạy cái gì") → mới dòng 33–49 (khối QC-F1..F3 + clean
  code), bước 4 tóm tắt cũ dòng 11–12 → mới dòng 11–13; bản portable cũ dòng 7–15 →
  mới dòng 7–23, khối mới khớp nguyên văn giữa hai bản (test `qc_dong_bo`).

## Sửa đã làm từ P1 (ghi nhận theo ghi chú T1.3)

- `portable/AGENTS.md` mục "Không có ở bản portable này": câu 51 từ SẴN CÓ từ trước
  (dòng 113 bản HEAD, doc_lint R5 bắt khi lint lại) tách thành 4 câu ngắn, giữ nguyên ý.
- `skills/tdq-conventions/SKILL.md` §11: dòng trỏ soul nén còn 1 dòng và gộp bullet
  "Không placeholder…" về 1 dòng để giữ trần 120 dòng (R6) — chữ nghĩa không đổi.
