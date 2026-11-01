# Kiểm chứng tiếp tục plan — chặn cấu hình còn tồn tại
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-10-27 · Request: 2026-10-27-1846-kiem-chung-tang-toc

## Công việc đã thực hiện

- Đọc lại spec, plan, state và sổ phân công; giữ request, nhánh và chế độ subagent hiện có.
- Xóa đúng 10 bản STATE.md orphan dưới worktree của request, sau khi xác minh đường dẫn và không có state.json cùng thư mục. Không xóa worktree hoặc thay đổi mã nguồn.
- Chạy lại detector: TIẾP TỤC ĐƯỢC, không còn D11. Audit phân công: 15/24 task giao agent, 0 vấn đề.
- Khởi động LSP Python; kiểm môi trường đạt 8/8 bậc, smoke 3/3 tầng. Không cài hoặc cập nhật plugin.
- Hai agent review độc lập xác nhận candidate QC1.1 và QC1.3 đã tích hợp vào root, trùng byte với worktree và không có finding chặn trong phạm vi sửa. Đây là review, chưa phải chứng nhận chạy test thành công.

## Lần kiểm thử mới

Lệnh: `python -X utf8 docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/safe_run.py --label QC1.3-codex-resume -- python -m pytest -q tests/test_tdq_runtime_bench.py tests/test_utf8_io.py tests/test_bao_cao_da_nen_tang.py tests/test_dem_da_nen_tang.py`

- Quyền thường; 57 test và 34 subtest PASS trong 60.60 giây; child exit 0.
- Harness FAIL126: `.claude.json` đổi digest trước/sau. Source/dependency guard không ghi nhận lỗi, sandbox cleanup hoàn tất.
- Receipt nguyên vẹn: [receipt.json](runs/QC1.3-codex-resume-5183d26c3e824ad98257aa2633a596ed/receipt.json); [stdout](runs/QC1.3-codex-resume-5183d26c3e824ad98257aa2633a596ed/stdout.txt).
- Không tick QC1.3; không tiếp tục Full, runtime hoặc benchmark khi tiền đề chưa đạt. Không chạy lại nhiều lần để tìm khoảng yên tĩnh.

## Nguồn gây nhiễu và giới hạn kết luận

PID 6196 vẫn tồn tại, thời điểm tạo 2026-10-27 22:37:53.591 +07, cha Node PID 15104. [ETW của phiên trước](config-writer-events.json) đã quan sát PID này ghi/rename cấu hình lúc 22:44:21. Lượt mới chưa có ETW quy tác giả; không kết luận mọi thay đổi mới đều do PID này.

Quan sát filename events 22 giây không thấy event trong chính cửa sổ đó: [metadata](codex-resume-config-events.json). Sau cửa sổ quan sát, `.claude.json` có LastWriteTime 23:21:10 +07. Một khoảng yên tĩnh ngắn không chứng minh nguồn ghi đã dừng. Ngoài CloudCLI còn có các tiến trình Claude do Code.exe mở; không dừng bất kỳ phiên nào.

Host hiện không elevated. Cần người dùng tạm dừng các phiên Claude ghi chung cấu hình trước khi chứng nhận lại. Không khóa file, sửa/hoàn nguyên cấu hình hoặc nới guard để vượt điều kiện của spec.

## Việc kế tiếp

Khi nguồn ghi đã dừng: resume state; chứng nhận QC1.1/QC1.3; refresh Master; Full fresh; runtime; ba cặp Full A/B; cache/log thật; QC độc lập; DoD và báo cáo MD/HTML desktop/mobile. Tiến độ vẫn 15/24; T5.1 đang làm. Các kết quả lịch sử được giữ nguyên.
