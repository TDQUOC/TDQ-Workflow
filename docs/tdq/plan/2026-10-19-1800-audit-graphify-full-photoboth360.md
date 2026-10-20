# QUICK — Benchmark Và Audit Toàn Diện Graphify Full Trên Dự Án Photoboth360

**Ngày:** 2026-10-19 · Brief: ../brief/2026-10-19-1800-audit-graphify-full-photoboth360.md · Lane: quick
**Trạng thái:** CHỜ DUYỆT
**Ước tính sẽ dùng skill:** không có

## Phạm vi
- Trong: Chạy `graphify extract` full AST + Semantic cho `Photoboth360` bằng endpoint/model `custom-combo-no2`; xây dựng harness 50 bài test tự động; đo đạc hiệu năng (thời gian, token) và độ chính xác (accuracy); xuất log đầy đủ 50 bài test và báo cáo tổng hợp.
- NGOÀI: Không sửa đổi mã nguồn gốc của dự án `Photoboth360`.
- Bỏ B0: Dự án Photoboth360 và Graphify đã có sẵn trên máy.
- Bỏ B2: Cơ chế trích xuất OpenAI-compatible đã được xác minh thành công ở request trước.

## Task
- [x] **T1** Chạy `graphify extract` full (AST + Semantic) và `graphify label` cho dự án `Photoboth360` — Test: kiểm tra file `graph.json` và `GRAPH_REPORT.md` sinh ra
  - Chạm: `C:\Users\admin\Documents\Photoboth360\graphify-out\`
- [x] **T2** Xây dựng và thực thi harness bộ 50 bài test kiểm toán (accuracy + performance + query) kèm ghi log chi tiết từng bài — Test: chạy suite 50 tests ra file log
  - Chạm: `evals/audit_photoboth360_50_tests.py`
- [x] **T3** Tổng hợp số liệu đo đạc, tính toán tỷ lệ chính xác, hiệu năng và hoàn tất plan `## QC` — Test: xác nhận log 50 bài và `python3 scripts/doc_lint.py ...`
  - Chạm: `docs/tdq/plan/2026-10-19-1800-audit-graphify-full-photoboth360.md`

## Definition of Done
- Q1 Graphify hoàn tất trích xuất full cho `Photoboth360`, sinh `graph.json` và `GRAPH_REPORT.md`
- Q2 Bộ 50 bài test chạy hoàn chỉnh 100%, mỗi bài test có log chi tiết (input, output, latency, status)
- Q3 Tỷ lệ chính xác (accuracy rate) của các bài test đạt ≥ 90%
- Q4 Có bảng thống kê đầy đủ về hiệu năng (thời gian, token, số node/edge, độ phủ)
- Q5 `doc_lint` trên brief và plan đạt 0 lỗi (exit 0)

## QC
- Q1 DoD "Graphify hoàn tất trích xuất full": PASS — Đồ thị sinh ra tại `graphify-out/graph.json` gồm 21,585 nodes, 52,741 edges và `GRAPH_REPORT.md` với 535 communities được gán nhãn bằng LLM `custom-combo-no2`.
- Q2 DoD "Bộ 50 bài test chạy hoàn chỉnh 100%, mỗi bài test có log": PASS — Toàn bộ 50 bài test chạy xong, xuất log định dạng JSONL đầy đủ thời gian, latency, đầu vào, đầu ra tại `evals/photoboth360_audit_logs.jsonl`.
- Q3 DoD "Tỷ lệ chính xác (accuracy rate) đạt ≥ 90%": PASS — Đạt 50/50 PASS (100.0%).
- Q4 DoD "Bảng thống kê đầy đủ về hiệu năng": PASS — Báo cáo tổng kết chi tiết tại `evals/photoboth360_audit_summary.md` phân rã theo 5 nhóm: Entity Coverage (2.19 ms), Dependency Accuracy (29.53 ms), Structural & Call Flow (19.00 ms), Semantic Query (2698.47 ms), Architectural Impact (706.49 ms).
- Q5 DoD "doc_lint trên brief và plan đạt 0 lỗi": PASS — Kiểm tra `scripts/doc_lint.py` đạt 0 vi phạm (exit 0).
