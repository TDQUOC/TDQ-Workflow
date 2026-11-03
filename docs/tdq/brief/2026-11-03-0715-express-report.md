# BRIEF — Thêm phase report cho Express
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> tôi muốn nó có phase report nữa để báo cáo trực quan

Mục tiêu: Express không chuyển thẳng từ `implement` sang `idle`; thêm phase `report` để tổng hợp kết quả trực quan sau QC. Phạm vi có thể chạm state transition, luật Express, tài liệu phase và regression tests. Đây là thay đổi hành vi skill/state nên cần eval plan và kiểm thử hồi quy.

Điểm chưa rõ: định dạng báo cáo trực quan cụ thể (Markdown có bảng/Before-After hay HTML Archify), nội dung bắt buộc và việc báo cáo có thêm cổng duyệt hay không.

## Hiểu & kiến thức

- Hiện trạng Express: `quick_analyze` → `implement` (gồm mini-plan, code, QC và fix loop) → `idle`; bước cuối tự hỏi commit, không tạo report chuẩn.
- Phase `report` đã tồn tại trong `VALID_PHASES`, `PHASE_TABLE` và `skills/tdq-build/references/report-template.md`; Deep đang dùng để tạo `docs/tdq/reports/<slug>.md`. Không cần thêm phase/state key mới.
- `phase_key()` hiện gom mọi phase Quick ngoài `analyze` và terminal `idle` về hàng `quick`, nên `phase=report` của Express chưa hiển thị đúng. Luật Quick cũng đang yêu cầu chuyển thẳng `phase=idle`.
- Thiết kế tối thiểu: sau QC xanh, Express chuyển `phase=report`; `phase_key()` trả hàng `report`; tái dùng report template, rồi report mới chuyển `idle`. Vẫn đúng một cổng `quick`, không thêm cổng duyệt hoặc file state mới.
- Báo cáo chuẩn áp dụng cho cả hai lane: Markdown nghiệm thu + một HTML Archify độc lập. HTML thể hiện kết quả thực tế gồm Before/After, task/DoD, QC, đầu ra và giới hạn; không sửa hoặc trộn với preview thiết kế đã duyệt.
- Deep giữ phase `report` hiện có nhưng bổ sung HTML chuẩn; Express chuyển vào cùng phase và dùng đúng report contract đó. Đầu ra dự kiến: `docs/tdq/reports/<slug>.md` và `docs/tdq/reports/<slug>.html`.
- Vùng chạm dự kiến: `scripts/tdq_state.py`, luật Quick/Report/Archify lifecycle, `phases.md` sinh lại và tests phase/context/Quick/report. B0 bỏ vì state/report có tiền lệ; B2 bỏ vì không có phụ thuộc ngoài repo.

### Lộ trình

- Luồng Express: analyze → implement/QC → report trực quan → idle.
- Luồng report: tổng hợp thay đổi thật, QC/DoD, đầu ra, giới hạn và hỏi commit; không thêm approval gate.

## Hỏi đáp

- Vòng 1: đã chọn pipeline Express (`1a`).
- Vòng 2: chọn Markdown chuẩn + HTML Archify độc lập (`1a`); xác nhận đây là report chuẩn cho cả hai lane.
