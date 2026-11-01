## Ponytail mặc định `ultra`

- State mới và fallback khi state thiếu khoá, giá trị sai hoặc rỗng đều dùng `muc_gat=ultra`.
- Bộ lọc luật và bảng cường độ được cập nhật cùng mặc định.
- Giữ nguyên các lựa chọn rõ ràng `lite/full/ultra/off`; không tự nâng các project đã lưu lựa chọn riêng.
- Mức QC `muc_qc` vẫn mặc định `full`, độc lập với Ponytail. Request hiện tại đã được set `ultra` theo yêu cầu.

## Kiểm chứng

Đã kiểm hồi quy state/CLI, bộ lọc luật, các hook SessionStart/SubagentStart/prompt, dedupe/log và metadata của hai host: **194 test PASS, 296 subtest PASS**. Receipt `ponytail-ultra-regression-e057325240a44a49bcfaa915d3bc634d` có child exit 0 và guard **PASS**. Có RED trước sửa, chứng minh các expectation mặc định mới phát hiện hành vi cũ.

Đây là kiểm tra phạm vi thay đổi, không phải một lượt Full mới. CI đa nền tảng của nền `0.85.0` chưa đạt; bản vá này không tuyên bố đã sửa các lỗi CI đó. Không chạy lại benchmark hoặc đổi mức QC mặc định.

ZIP được tạo từ `main` tinh gọn; có cả hai manifest `0.85.1` và đủ hai mặc định `ultra` trong state/hook. Kèm `SHA256SUMS.txt`.
