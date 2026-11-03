# Bối cảnh kiểm Archify trên Windows

Lượt Full đầu và preview gốc chạy từ tiến trình elevated; native browser gate lỗi `Chrome DevTools read pipe failed: stream ended`. Hai probe độc lập với Chrome/Edge đều đọc 0 byte rồi pipe đóng. Đây là bằng chứng phù hợp với giới hạn elevated-shell mà Archify mô tả, chưa phải chứng minh đầy đủ cơ chế Windows relaunch.

Đã khởi chạy Python qua `Document.Application.ShellExecute(..., 'open', 0)` của cửa sổ Explorer hiện có. Cách gọi dùng cửa sổ ẩn, không đổi UAC, không tạo tài khoản, không thay engine, dependency hoặc test. Probe `ctypes.windll.shell32.IsUserAnAdmin()` trả false. Gọi `New-Object -ComObject Shell.Application` trực tiếp trước đó vẫn trả true, vì vậy không dùng đường đó để chứng nhận.

Đường xử lý dựa trên hướng dẫn [Microsoft: thực thi qua Explorer để chạy quyền thường](https://devblogs.microsoft.com/oldnewthing/20131118-00/?p=2643). Chỉ dùng ý tưởng gọi ứng dụng qua Explorer; không sao chép mã hoặc thay chính sách bảo mật.

Lệnh con thực tế: `C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe -m unittest discover -s tests -p test_archify_e2e.py`.

Biên nhận `QC1.2-normal.json`: 2 test, gồm subtest lane full và quick, 12.788 giây test / 12.869 giây tiến trình, exit 0. Đây là native gate thật, không lấy ảnh CDP thay kết quả test. Các lượt Full quyền thường dùng cùng cách khởi chạy; `QC-F1-final.context.json` (lượt 2, sau đó còn lỗi fixture updater) và `QC-F1-after-QC2.context.json` (lượt 3) ghi elevated=false, không có PYTHONUTF8/PYTHONIOENCODING và hash 342 file scripts/tests/skills ngay trước chạy.

`archify_delivery.py` đã có logic đặt `ARCHIFY_CHROME_NO_SANDBOX=1` khi elevated từ trước request; file không được sửa trong đợt 1. Probe độc lập không dùng biến đó vẫn tái hiện lỗi. Lượt chứng nhận quyền thường không đi nhánh elevated này. Không kết luận môi trường elevated đã được hỗ trợ sau đợt 1.

Tái lập: mở PowerShell thường trong repo, xác nhận không elevated rồi chạy `python -m unittest discover -s tests -p test_archify_e2e.py` hoặc `python scripts/tdq_test.py tron-bo`. Không cần dùng helper trong TEMP nếu chỉ cần kết quả test; helper chỉ lưu output và biên nhận.
