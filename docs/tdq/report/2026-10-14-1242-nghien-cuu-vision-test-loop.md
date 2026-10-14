# REPORT — Nghiên cứu mở rộng mindset test và vòng lặp so sánh vision UI/UX Figma cho TDQ Workflow (`2026-10-14-1242-nghien-cuu-vision-test-loop` · lane full · QC ultra)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:**
- **Khung Quy chuẩn Mindset Kiểm thử Thực tế cho AI (§3.1)**: Xóa bỏ lối tư duy test máy móc, hình thức; thiết lập chuẩn kiểm thử theo kịch bản người dùng thực tế (User-Scenario-Driven Testing) với định dạng `Given - When - Then`, 3 tầng kịch bản (Realistic Happy Path, Boundary/Edge Cases, Visual & UX Verification), và danh mục 6 Test Anti-Patterns cấm kỵ (tautology assertions, over-mocking, circular logic, happy-path-only, invisible visual tests, silent catches).
- **Kiến trúc Vòng lặp Kiểm thử Thị giác — Vision Test Loop (§3.2)**: Thiết kế chu trình khép kín 6 bước: (1) Thu thập Source (Local/Figma/MCP); (2) Chụp Dist (MCP Browser viewport chuẩn); (3) Hybrid Diff Engine (Pixel Diff Pillow + Canvas padding chống méo tỷ lệ + Masking vùng động); (4) Multimodal AI Vision (Claude phân tích ngữ nghĩa các hộp Bounding Box đỏ `[1]`, `[2]`); (5) Vòng lặp Auto-fix tự sửa CSS/HTML; (6) Cơ chế dừng an toàn với trần tối đa 3 vòng lặp, dừng sớm khi không hội tụ và báo cáo người dùng.
- **Bộ đôi Báo cáo Thị giác Song song (§3.3)**: Định dạng Markdown Report (`docs/tdq/visual-reports/<slug>.md`) cho AI/Git và Interactive HTML Report (`docs/tdq/visual-reports/<slug>.html`) với Slider so sánh chia đôi màn hình (Before/After comparison slider), chế độ nhấp nháy/chồng mờ (Overlay Onion-skin & Blink 2Hz), và Trình duyệt Bounding Box tương tác click-to-zoom có gợi ý code CSS fix sinh tự động từ template (chống cháy token LLM).
- **Quy trình Reviewer Sub-agent Độc lập & Human-in-the-loop (§3.3 & §3.4)**: Khởi chạy Reviewer Sub-agent hậu kiểm trực quan (second-pair-of-eyes) với trần an toàn tối đa 1 lượt feedback để tránh lặp vô hạn; kích hoạt cơ chế dừng hỏi người dùng khi thiếu asset/font/Figma token hoặc quá trần 3 vòng.
- **Thẩm định QC mức Ultra (§6)**: Khởi chạy sub-agent reviewer độc lập (`a7c6e78cc70098542`) thẩm định và phản biện kiến trúc; tiếp thu và cập nhật 100% 4 cải tiến kỹ thuật sắc bén vào spec.

**Kết quả:**
- Definition of Done Q1–Q6: 6/6 PASS (100%).
- Ràng buộc kiến trúc và tính khả thi QC-F1 đến QC-F4: PASS.
- Môi trường kiểm chứng thực tế: Python Pillow 12.3.0, Node v24.19.0, cloudcli-browser MCP kết nối hoàn hảo.
- Hợp đồng tài liệu: `doc_lint.py` 0 vi phạm trên toàn bộ brief, spec và qc.

**Giới hạn & Khuyến nghị tiếp theo:**
- Request này hoàn thành trọn vẹn nhiệm vụ nghiên cứu, phân tích và đề xuất giải pháp kiến trúc khả thi, chưa sinh mã nguồn triển khai thực tế theo đúng yêu cầu đề bài.
- Khuyến nghị bước tiếp theo: Mở một request triển khai (implementation request) để code script tiện ích `scripts/tdq_vision_diff.py` và tích hợp quy tắc `QC-F5 (Visual Regression Check)` vào `skills/tdq-build/references/qc.md`.

**Lệch spec:** 0 mục lệch spec.

**Git:** Hiện nằm trên branch `feature/nghien-cuu-vision-test-loop`.
