# QUICK — Nâng Cấp Graphify Xây Bản Đồ Toàn Tập Và Đánh Giá Thay Thế LSP

**Ngày:** 2026-10-19 · Brief: ../brief/2026-10-19-1700-nang-cap-graphify-ban-do-du-an.md · Lane: quick
**Trạng thái:** HOÀN THÀNH (bởi "duyệt plan", muc_qc=full)
**Ước tính sẽ dùng skill:** không có

## Phạm vi
- Trong: Nghiên cứu, phân tích kỹ thuật, smoke test các khả năng của Graphify; trả về báo cáo toàn diện và đề xuất hướng triển khai cho người dùng.
- NGOÀI: Chưa thay đổi hành vi (behavior) hay logic thực thi của TDQ-Workflow ở request này.
- Bỏ B0: Đã có sẵn công cụ Graphify và LSP tích hợp trong dự án.
- Bỏ B2: Cơ chế backend OpenAI của Graphify đã chuẩn hóa qua tài liệu CLI.

## Task
- [x] **T1** Khảo sát chi tiết cơ chế OpenAI-compatible của Graphify và đối chiếu kỹ thuật chuyên sâu Graphify vs LSP — Test: ghi nhận tài liệu so sánh kỹ thuật
  - Chạm: `docs/tdq/brief/2026-10-19-1700-nang-cap-graphify-ban-do-du-an.md`
- [x] **T2** Phân tích và smoke test cơ chế trích xuất toàn diện (full extract code + docs) và cơ chế keep update liên tục của Graphify — Test: chạy smoke test CLI của Graphify
  - Chạm: không sửa mã nguồn dự án
- [x] **T3** Tổng hợp báo cáo nghiên cứu chi tiết, giải đáp các câu hỏi và đề xuất phương án nâng cấp vào plan `## QC` — Test: `python3 scripts/doc_lint.py ...`
  - Chạm: `docs/tdq/plan/2026-10-19-1700-nang-cap-graphify-ban-do-du-an.md`

## Definition of Done
- Q1 Báo cáo rõ ràng câu trả lời: Graphify có thay thế LSP được không (lý do kỹ thuật)
- Q2 Đánh giá cụ thể khả năng tìm kiếm feature/function ngữ nghĩa qua Graphify + LLM
- Q3 Cung cấp mẫu lệnh cấu hình kết nối OpenAI-compatible (endpoint, key, model) sẵn sàng để test thực nghiệm
- Q4 Xác lập giải pháp trích xuất full mọi thứ và giữ cập nhật liên tục (keep update)
- Q5 `doc_lint` trên brief và plan đạt 0 lỗi (exit 0)

## QC
- Q1 DoD "Graphify có thay thế LSP được không": PASS — Kết luận: KHÔNG thay thế mà cộng sinh; LSP giữ micro compiler precision, Graphify giữ macro navigation.
- Q2 DoD "Khả năng tìm kiếm feature/function ngữ nghĩa": PASS — Smoke test `graphify query` BFS ra 94 nodes liên quan theo ý niệm mà grep text không thể làm được.
- Q3 DoD "Mẫu cấu hình kết nối OpenAI-compatible": PASS — Chuẩn hóa qua `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `OPENAI_MODEL` và cờ `--backend openai`.
- Q4 DoD "Giải pháp trích xuất full và keep update": PASS — Đã smoke test sinh thành công `GRAPH_TREE.html` (206KB) và `CALLFLOW.html` (16 diagrams); xác lập lộ trình 2 tầng extract.
- Q5 DoD "doc_lint trên brief và plan đạt 0 lỗi": PASS — `python scripts/doc_lint.py` → 0 violation(s), exit 0.
