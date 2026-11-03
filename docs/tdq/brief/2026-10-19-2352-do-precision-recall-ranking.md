# BRIEF — Đo false positives, false negatives và ranking Graphify
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> Đo lun false positives, false negatives hay thứ hạng kết quả.

Đọc hiểu lần đầu:
- Bổ sung phép đo thực cho Graphify trên Photoboth360 thay vì chỉ tỷ lệ PASS smoke test.
- Tạo ground truth từ mã nguồn độc lập với graph/output, đóng băng trước khi chạy; không đổi oracle để làm kết quả đẹp.
- Đếm TP/FP/FN, precision/recall/F1; đánh giá thứ hạng bằng Precision@k, Recall@k, Hit@k và MRR@k trên các truy vấn có tập đích xác minh.
- Ghi raw stdout/stderr, kết quả được parse, expected/actual, nguồn/dòng chứng cứ, latency và lỗi; bổ sung kết quả vào HTML hiện có.

## Hiểu & kiến thức

- Audit cũ có 50 PASS nhưng dùng substring rộng và không có gold set đầy đủ; không tái sử dụng PASS đó làm nhãn relevance.
- Phải phân biệt đánh giá cạnh exact với tìm kiếm ở cấp file/symbol; chốt đơn vị đánh giá, k, phạm vi và cách loại trùng trước khi chạy.
- Recall/FN chỉ hợp lệ trong phạm vi gold set đã xét đủ; kết quả ngoài phạm vi chưa gán nhãn phải ghi unjudged, không tự tính là FP.
- Kiểm tra CLI có trả thứ tự xếp hạng thực không; nếu không thì không biến thứ tự dòng context thành ranking search.
- Không rebuild graph/call API trong bước intake; cần fingerprint source/graph và ghi độ mới để kết quả tái lập.
- Repo còn các tệp audit, HTML và cấu hình chưa commit; quyền giữ dirty/bỏ qua LSP ở request HTML trước không tự mở rộng sang benchmark mới.

## Hỏi đáp

- Người dùng chọn “A” (express), sau đó “đồng ý” giữ dirty và bỏ qua kiểm chứng LSP cross-file riêng request này; đã ghi lý do bằng init CLI.
- Nhánh `chore/graphify-precision-recall-ranking` mở từ `docs/html-danh-gia-graphify`; không tự commit các thay đổi cũ.
- B1: LSP list_symbols đã đọc cấu trúc harness cũ; xác minh trực tiếp package Graphify: `serve.py:1349–1408` query dùng scorer → chọn seeds → BFS/DFS → context budget. Thứ tự NODE của CLI không phải danh sách ranking thuần.
- `serve.py:531–539` có `_score_nodes`, trả `(score, node_id)` theo ranking nội bộ. Có thể đo scorer offline cùng graph; phải gọi rõ là ranking nội bộ, không đồng nhất output CLI. Không sửa package.
- Phạm vi dự kiến: 11 file JS nghiệp vụ nodeserver (app.js, config.js và 9 file app/), 12 truy vấn tính năng; gán nhãn file liên quan bằng đọc source, đóng băng trước output. Ngoài 11 file ghi unjudged; báo coverage và không ép chúng thành FP.
- Đánh giá cạnh imports_from và contains/functions tách khỏi retrieval. Khớp path/symbol chính xác, có chứng cứ dòng; giữ trường hợp require socket.io gọi lồng để đo thiếu sót thay vì đổi test.
- Chưa chạy truy vấn Photoboth360. Lệnh `graphify query --help` ở intake bị CLI hiểu là câu hỏi literal trên graph TDQ; không dùng output đó làm kết quả benchmark.
- Bỏ nghiên cứu ngoài: đủ mã nguồn package cài đặt để xác định semantics, không cần API/web. Chưa chạy benchmark trước duyệt mini-plan.
