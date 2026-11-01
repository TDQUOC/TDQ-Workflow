# Kiểm chứng khi tiếp tục — nguồn gây biến động cấu hình

Ngày: 2026-10-27 · Request: 2026-10-27-1846-kiem-chung-tang-toc

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Kết quả

Request vẫn hoàn tất 15/24 task. Chưa chứng nhận Full sau sửa, benchmark hoặc DoD cuối.

- QC1.3: 57 test và 34 subtest PASS, nhưng harness FAIL126 do `.claude.json` thay đổi.
- QC1.1: 513 test PASS, 2 skip và 215 subtest PASS; harness cũng FAIL126 do cấu hình thay đổi.
- Lỗi thiếu cửa sổ Explorer để chuyển sang quyền thường đã được khắc phục. Không đổi quyền chạy test.

## Nguồn gây nhiễu đã quan sát

Windows ETW provider `Microsoft-Windows-Kernel-File` bắt được `claude.exe`, PID 6196, ghi 121929 byte vào FileObject tương ứng với file tạm của `.claude.json`, sau đó thay thế file đích bằng thao tác rename lúc 22:44:21 +07. Event 16 và event 27 được nối theo FileObject/FileKey và PID. File tạm chứa PID 6196 trong tên.

Tiến trình cha PID 15104 là Node chạy CloudCLI. Claude được tạo lúc 22:37:53.591 +07. Đây là bằng chứng cho lần ghi quan sát được; không quy toàn bộ các lỗi lịch sử cho cùng PID. Trace không đọc nội dung cấu hình. Trace đã dừng; chỉ giữ các event liên quan và digest, loại bỏ ETL thô chứa metadata file không liên quan.

## Điều kiện tiếp tục

Cần dừng tác vụ Claude qua CloudCLI đang ghi chung cấu hình, hoặc được người dùng cho phép dừng riêng tiến trình đã xác định. Trước khi thực hiện phải kiểm lại PID, thời điểm tạo, executable và tiến trình cha để tránh nhầm PID tái sử dụng. Không dừng CloudCLI server hoặc các tiến trình khác.

Chưa thực hiện thao tác dừng phiên khác. Không bỏ guard, không hoàn nguyên cấu hình và không chạy các benchmark dài khi gate tiền đề chưa đạt.

Sau khi nguồn ghi ngừng: chứng nhận QC1.1/QC1.3 → refresh Master → Full fresh → runtime scenarios → ba cặp Full A/B → cache/log thật → QC độc lập → DoD và báo cáo cuối.

## Bằng chứng

- [Tóm tắt và digest](resume-diagnostic.json)
- [Event đường dẫn và rename](config-writer-events.json)
- [Event ghi dữ liệu cùng FileObject](config-writer-writes.json)
- [Thời điểm file thay đổi](config-writer-watch.json)
- [Checkpoint HTML trước lượt tiếp tục](checkpoint.html)

Các receipt test thất bại được giữ nguyên dưới worktree QC1.1 và QC1.3; mã lượt chạy nằm trong nhật ký kết thúc lượt.
