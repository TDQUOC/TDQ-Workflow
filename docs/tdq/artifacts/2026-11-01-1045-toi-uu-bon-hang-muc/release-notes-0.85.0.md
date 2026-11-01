> **CI đa nền tảng chưa đạt:** [run 41301102960](https://github.com/TDQUOC/TDQ-Workflow/actions/runs/41301102960) đã có bốn job Linux/macOS FAIL; hai job Windows còn chạy tại lần kiểm cuối. Log Ubuntu 3.13 có 87 failure, 23 error, gồm lỗi thiếu dependency `PIL`, `pytest`. Không tuyên bố release đã qua CI đa nền tảng.

## Thay đổi chính

- Validation calibration chạy trước vòng đo; input sai không tạo output mới.
- Codex dùng process ownership chung, timeout riêng cho từng probe và dọn đúng descendants/HOME.
- 11 ca kiểm thuần bỏ công việc subprocess/calibration/Git lặp; giữ các integration thực.
- Tự động tổng hợp Top20 case/module và export JSON, Markdown, HTML từ result có sẵn, không chạy lại test. Giữ verdict, quality và provenance.
- Bao gồm các cải thiện runner/timing đã tích hợp trên dev: structured outcomes, inventory/receipt, giữ lỗi gốc và phân biệt thời gian wall/API/tool.

## Kiểm chứng và giới hạn

- Full trước bước bump metadata: **3.657 PASS, 8 SKIP**; giữ đủ 3.602 case baseline, thêm 63 case. QC **12/12**; review độc lập và HTML desktop/mobile đạt.
- Đối chiếu 313 file runtime/test/hook trước commit: không đổi byte so với lượt Full đã kiểm. Release chỉ bổ sung version, changelog và quy tắc giữ byte evidence.
- Lượt bổ sung metadata/đóng gói: **60 test và 28 subtest qua**, nhưng receipt là **FAIL126** do `.claude.json` thay đổi trong lúc chạy. Đây **không phải** một lượt chứng nhận guard PASS mới. Receipt FAIL được giữ, không sửa cấu hình hoặc retry để tìm khoảng yên tĩnh.
- Benchmark A/B D9/D10 giữ `SKIPPED_USER`; chưa có kết luận % tăng tốc hoặc chứng nhận POSIX từ lượt Windows. Giữ worker1, cache/reuse off.
- Metadata workflow vẫn bị chặn bởi 11 worktree cũ có source chưa commit; dữ liệu được giữ nguyên. Điều này không được ghi thành workflow đã đóng.

## Gói phát hành

`TDQ-Workflow-0.85.0.zip` được tạo bằng `git archive` từ nhánh `main` tinh gọn: 169 file, không có tests/docs/cache/worktree. Hai manifest cùng version `0.85.0`; kèm báo cáo HTML tóm tắt và `SHA256SUMS.txt`.

Mã nguồn phát triển và hồ sơ QC nằm trên nhánh [dev](https://github.com/TDQUOC/TDQ-Workflow/tree/dev). Bản plugin phát hành nằm trên nhánh [main](https://github.com/TDQUOC/TDQ-Workflow/tree/main).
