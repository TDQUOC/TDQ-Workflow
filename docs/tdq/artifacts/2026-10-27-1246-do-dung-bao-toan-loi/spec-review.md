# Kiểm tra spec đợt 1

Ngày: 2026-10-27. Phạm vi: tài liệu thiết kế và preview, chưa phải QC mã triển khai.

## Tự soát nội dung

- Phạm vi đợt 1, các mục loại trừ và mức QC Full khớp brief; lựa chọn `1a` được ghi riêng với lựa chọn pipeline.
- O1–O6 đều có D1–D7 kiểm chứng. Điều kiện PASS trong spec; tên file/lệnh test cụ thể dành cho plan.
- Ranh giới dựa trên LSP/caller/Graphify đã khảo sát; các module runtime không khai trùng file. Không mở rộng quyền state hoặc thay gate duyệt.
- Có Mermaid, đối chiếu trước/sau, các bước giải thuật, độ phức tạp, ca biên, ví dụ hợp khoảng và bảng thuật ngữ cho người mới.
- Tách dữ liệu quan sát khỏi suy đoán; model chưa đo được giữ null; project_window không được gọi là quy thuộc độc quyền cho request.
- Giữ FAIL/ERROR dù thiếu chi tiết; no-op là SKIP; source chưa có test là INCOMPLETE. Có tình huống direct xanh nhưng indirect đỏ ở QC.
- Tương thích lịch sử có version và nhãn nghĩa cũ; không viết lại sổ. Init/close-once/JSON stdout và CI unittest có tiêu chí hồi quy.
- Mục câu hỏi mở rỗng. Chưa duyệt spec, chưa viết plan và chưa sửa runtime.

## Kiểm tài liệu và liên kết

`doc_lint.py` cho brief và spec: exit 0, 0 vi phạm, R14 không có finding. Đã đưa đường dẫn file test khỏi spec theo R11 và giữ việc chọn tên/lệnh ở plan.

`tdq_archify.py verify`: manifest và document binding đều `current`, `valid=true`. Binding áp dụng thiết kế `planned`, không gán source dự kiến cho một commit đã tồn tại.

## Preview và giới hạn

- Archify validate/deliver/check: PASS. Browser-check gốc: FAIL do Chrome DevTools pipe trên Windows. Wrapper xuất HTML bằng fallback; không đổi kết quả gate gốc trong bằng chứng.
- Kiểm bổ sung dùng Chrome headless qua CDP localhost, profile tạm riêng; không cài package, không tắt sandbox. Kiểm nhãn nội dung, lỗi JavaScript và tràn ngang trang; lưu `preview-review.json` cùng SHA-256 của HTML.
- Đã xem trực tiếp ảnh `preview-1440.png`: luồng chính, nhánh thiếu bằng chứng, nhánh test rỗng, chú giải và thẻ diễn giải đọc được, không thấy chồng chữ hoặc mất nhãn.
- Đã xem `preview-390.png`: phần diễn giải đọc được; canvas rộng cần kéo/thu phóng, không hiển thị toàn bộ sơ đồ ở mức zoom hiện tại. Ưu tiên mở preview trên desktop. Một số nút của viewer vẫn dùng tiếng Anh.
- Kiểm CDP và xem ảnh là bằng chứng bổ sung, không được ghi đè browser-check gốc thành PASS. Chưa kiểm mọi tính năng export/theme của viewer; không coi là QC sản phẩm TDQ.

## Bằng chứng baseline

`baseline.json` sao lại kết quả tái hiện E1–E5 trước sửa. Các đường dẫn Temp trong đó ghi vị trí chạy thực lúc khảo sát, không phải file runtime mới của workflow. Spec và brief giữ dẫn chiếu tới báo cáo audit gốc; regression có thể tái lập trong repo sẽ được viết theo plan sau khi được duyệt.
