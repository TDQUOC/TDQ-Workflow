# QUICK — Thử Nghiệm Semantic Extraction Của Graphify Với Cấu Hình Claude Code

**Ngày:** 2026-10-19 · Brief: ../brief/2026-10-19-1750-test-graphify-semantic-backend.md · Lane: quick
**Trạng thái:** HOÀN THÀNH (bởi "duyệt nhanh", muc_qc=full)
**Ước tính sẽ dùng skill:** không có

## Phạm vi
- Trong: Thiết lập biến môi trường backend `claude` (Anthropic endpoint, token, model `custom-combo-no2`); chạy thử nghiệm trích xuất ngữ nghĩa và gán nhãn cụm trên thư mục mẫu cách ly; đo đạc số liên kết ngữ nghĩa, thời gian và báo cáo kết quả.
- NGOÀI: Không ghi đè trực tiếp lên `graphify-out/` chính của dự án, không lưu cứng API key vào tệp tin.
- Bỏ B0: Đã có sẵn công cụ Graphify và cấu hình kết nối trong môi trường.
- Bỏ B2: Cơ chế gọi Anthropic API của Graphify đã chuẩn hóa qua tài liệu CLI.

## Task
- [x] **T1** Thiết lập môi trường cách ly và script cấu hình gọi Graphify qua backend `claude` — Test: kiểm tra kết nối API tới endpoint
  - Chạm: thư mục tạm cách ly
- [x] **T2** Thực thi trích xuất ngữ nghĩa (`graphify extract --backend claude`) và gán nhãn cụm trên tập mẫu — Test: xác nhận file `graph.json` sinh các cạnh và nhãn ngữ nghĩa
  - Chạm: thư mục tạm cách ly
- [x] **T3** Tổng hợp báo cáo đo đạc thực nghiệm (số nodes/edges, thời gian, chất lượng nhãn) vào plan `## QC` — Test: `python3 scripts/doc_lint.py ...`
  - Chạm: `docs/tdq/plan/2026-10-19-1750-test-graphify-semantic-backend.md`

## Definition of Done
- Q1 Graphify kết nối thành công tới endpoint `http://36.50.55.22:20228/v1` qua backend `claude`
- Q2 Tiến trình trích xuất hoàn tất và sinh ra các liên kết ngữ nghĩa và nhãn cụm tính năng
- Q3 Đo đạc chi tiết thời gian thực thi và số lượng node/edge
- Q4 Thư mục chính của dự án không bị ảnh hưởng (môi trường cách ly sạch)
- Q5 `doc_lint` trên brief và plan đạt 0 lỗi (exit 0)

## QC
- Q1 DoD "Kết nối thành công tới endpoint": PASS — Endpoint trả về HTTP 200 qua OpenAI-compatible `/chat/completions` với model `custom-combo-no2`.
- Q2 DoD "Sinh ra các liên kết ngữ nghĩa và nhãn cụm": PASS — Tạo ra các cạnh `rationale_for` và 4 cụm tính năng có tên rõ ràng (`User Session Management`, `API and Authentication Modules`...).
- Q3 DoD "Đo đạc chi tiết thời gian và số lượng node/edge": PASS — 19 nodes, 20 edges, thời gian trích xuất ~4s, token: 3,573 in / 190 out.
- Q4 DoD "Thư mục chính không bị ảnh hưởng": PASS — Chạy hoàn toàn trong thư mục cách ly `evals/graphify_semantic_test/` và đã dọn dẹp sạch sẽ sau test.
- Q5 DoD "doc_lint trên brief và plan đạt 0 lỗi": PASS — `python scripts/doc_lint.py` → 0 violation(s), exit 0.
