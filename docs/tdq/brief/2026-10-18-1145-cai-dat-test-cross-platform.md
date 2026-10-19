# Brief: Cài đặt/cập nhật Agy, Codex, TDQ Plugin trên macOS và Linux, setup và chạy full smoke test

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> "okay hãy giúp tôi update/ install agy, codex và tdq plugin vào và setup và cho phép tạo smoke test project để fully test tdq workflow và thống kê, báo cáo kết quả cho tôi"

### Đọc hiểu ban đầu:
- **Mục tiêu**: SSH vào cả 2 máy từ xa (macOS `100.105.75.71` và Linux `100.102.92.43`), kiểm tra/cài đặt/cập nhật các thành phần cốt lõi:
  1. **Agy** (Antigravity portable / CLI).
  2. **Codex** (Codex CLI, config và MCP).
  3. **TDQ Workflow Plugin** (phiên bản mới nhất v0.73.1).
  4. Chạy `tdq_setup.py` để cấu hình môi trường đầy đủ (3 tầng tìm kiếm, hooks, CLAUDE.md).
  5. Tạo smoke test project trên từng máy để kiểm thử thực tế toàn diện toàn bộ quy trình TDQ Workflow (intake -> plan -> implement -> qc -> report).
  6. Thống kê số liệu, đo đạc thời gian/hiệu năng và lập báo cáo kết quả chi tiết.
- **Phạm vi**:
  - Máy macOS Apple Silicon (`tdq@100.105.75.71`).
  - Máy Linux Ubuntu (`admin@100.102.92.43` / `tdq`).
  - Dự án test độc lập trên môi trường remote.
- **Điểm chốt**: Tiến hành theo quy trình kiểm thử hệ thống chuẩn mực.

## Hiểu & kiến thức
(Sẽ được bổ sung trong phase analyze/quick_analyze)

## Hỏi đáp
(Trao đổi lựa chọn pipeline)
