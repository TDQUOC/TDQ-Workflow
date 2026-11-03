# QUICK — HTML đánh giá nhanh Graphify
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Ngày:** 2026-10-19 · Brief: ../brief/2026-10-19-2327-html-danh-gia-graphify.md · Lane: quick
**Trạng thái:** HOÀN THÀNH — “Duyệt nhanh”, QC full; T1–T2 và Q1–Q4 đạt kiểm tra tĩnh
**Ước tính sẽ dùng skill:** dataviz

## Phạm vi
- Trong: một HTML tiếng Việt, offline, responsive, ngắn gọn; bốn phần accuracy/performance, LSP/Lumen, tìm code, token/tool calls; nguồn và giới hạn phép đo.
- NGOÀI: không sửa harness/log audit, không đo mới hoặc gọi API; không thay behavior TDQ, không tự commit/merge.
- Bỏ B0: đã có báo cáo audit và dữ liệu cùng chủ đề; tái sử dụng, không xây ứng dụng/dashboard mới.
- Bỏ B2: chỉ kết luận trong phạm vi tài liệu và dữ liệu sẵn có; không khẳng định chất lượng Lumen hiện tại hoặc kết quả đối chứng chưa đo.
- Bỏ scope round: đầu ra một file, bốn câu hỏi đã rõ; không cần lựa chọn thiết kế từ người dùng.
- Đã cho phép giữ thay đổi audit chưa commit và bỏ qua kiểm chứng LSP cho HTML tĩnh; CLI ghi lý do.

## Task
- [x] **T1** Tạo HTML độc lập, giải thích rõ bằng số đo, bảng so sánh và một ví dụ luồng tra cứu — Test: kiểm tra cấu trúc HTML, nội dung bốn câu hỏi, đường dẫn nguồn và không có tài nguyên mạng.
  - Chạm: `docs/tdq/reports/graphify-danh-gia-nhanh.html`
- [x] **T2** Đối chiếu số liệu và kiểm chất lượng tài liệu, ghi bằng chứng QC — Test: so số liệu với JSONL/summary; kiểm HTML bằng HTMLParser, kiểm responsive bằng cấu trúc CSS; doc_lint brief/plan.
  - Chạm: `docs/tdq/reports/graphify-danh-gia-nhanh.html`, `docs/tdq/plan/2026-10-19-2327-html-danh-gia-graphify.md`

## Definition of Done
- Q1 File HTML mở offline, UTF-8, có viewport, bố cục mobile và bảng đọc được; không CDN, font ngoài hoặc request API — kiểm HTMLParser và thuộc tính tài nguyên.
- Q2 Trả lời đủ bốn nhóm câu hỏi, ghi 50/50 là PASS bộ smoke test chứ không phải accuracy tuyệt đối; không gọi 535 nhãn là bằng chứng full semantic coverage — kiểm nội dung và đối chiếu harness.
- Q3 Số đo Photoboth360 đúng summary/JSONL; tách latency RAM với CLI, không suy ra thời gian extract; token/tool calls ghi chưa có A/B — kiểm số liệu bằng Python.
- Q4 Có nguồn tương đối tới summary, JSONL, harness và quy tắc tìm kiếm; ghi hạn chế query/affected/explain và thiếu raw stdout; doc_lint brief/plan exit 0.

## QC
- T1 red→green: trước khi tạo file, `Path.exists` FAIL; sau tạo, Python HTMLParser → `T1 PASS: balanced HTML, unique IDs, 4 answers, offline resources, source links, responsive CSS`.
- Q1 PASS — HTMLParser kiểm doctype, UTF-8, viewport, thẻ đóng/mở, ID duy nhất, CSS mobile/overflow, không script/src/CDN/@import/url; các liên kết tồn tại. Chỉ kiểm tĩnh, chưa kiểm hiển thị thực.
- Q2 PASS — đối chiếu harness: query/affected khớp một keyword, explain kiểm độ dài; HTML nêu 50/50 không phải precision/recall, T14 đổi oracle, 535 nhãn không chứng minh full coverage.
- Q3 PASS — Python JSONL → `50 unique results; all 5 averages match JSONL/summary`; số node/link và 535 communities khớp summary; tách RAM/CLI, không bịa thời gian extract hoặc tỷ lệ tiết kiệm.
- Q4 PASS — nguồn local tồn tại; thiếu raw stdout/stderr được công khai; `doc_lint` brief/plan → `0 violation(s) total, exit 0`.
- T2 red→green: kiểm bằng chứng QC ban đầu FAIL; sau đối chiếu đã ghi Q1–Q4, chạy lại kiểm bằng chứng PASS.
- Giới hạn: HTMLHint không được cài → chưa kiểm; không gửi HTML lên validator công khai; không chạy runtime trình duyệt theo QC full, không tuyên bố đã nghiệm thu hình ảnh.
- Luật gọn: dừng bậc 4 HTML/CSS native, tái dùng số liệu; không có HTML Graphify sẵn nên tạo một file được yêu cầu, không thêm dashboard/JS/dependency.
