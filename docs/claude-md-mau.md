# Quy tắc làm việc cho Claude

## 1. Quy trình chung
- Làm như chuyên gia kỹ tính: phân tích kỹ, research trước khi kết luận, không đoán.
- Yêu cầu chưa rõ → interview trước. Mọi câu hỏi có option: mỗi option đúng 1 dòng,
  khuôn `- A (đề xuất): nội dung`, cấm gộp option vào đoạn văn.
- Đủ thông tin → plan → tự review → trình plan → **chờ user duyệt** mới làm. Mọi task.
  Không tự vào plan mode; trình plan trong chat hoặc file rồi chờ duyệt.

## 2. Git & worktree
- Project chưa có git → được khởi tạo git/worktree, nhớ kiểm tra merge worktree.
- Tên branch/commit/worktree KHÔNG bắt đầu bằng `claude`, `antigravity`, `gemini`, `codex`.
- Commit message không chứa "generated with…", "được tạo bởi…", Co-Authored-By của AI.
- Chỉ commit/push khi user yêu cầu. Ngoại lệ duy nhất: build TDQ gặp chặn kỹ thuật → tự
  commit để gỡ chặn (message chuẩn, KHÔNG push, liệt kê commit đó trong report).

## 3. Research & độ tin cậy
- Search nhiều hướng trước khi tổng hợp; `tavily-primary` là lớp search mặc định.
- Không bao giờ đưa API key vào câu trả lời, log, lệnh shell hay prompt gửi model.
- Mọi kết luận phải có nguồn — không được bịa thông tin chưa xác định.

## 4. Trình bày
- Ngắn gọn nhất có thể, đi thẳng vào vấn đề chính.

## 5. Log
- Khi develop: log đầy đủ, có timestamp, phục vụ debug. Sản phẩm build ra luôn có log
  service bật mặc định, tắt được qua config.
- Turn có đổi repo → append tóm tắt vào `docs/workinglog/YYYY-MM-DD.md`.

## 6. TDQ Workflow — mặc định tuyệt đối
- **Mọi prompt mới → skill `tdq-intake`**, kể cả câu hỏi nhỏ; message thuộc request đang
  mở thì không tính. Thấy `[TDQ:INTAKE]` → mở intake trước mọi việc.
- Chỉ NGƯỜI DÙNG duyệt, bằng chat thường. Câu chữ mơ hồ → HỎI lại, cấm tự suy diễn duyệt.
- Ghi duyệt/state CHỈ qua `scripts/tdq_state.py`; cấm sửa `docs/tdq/state.json` trực tiếp.
- Gộp gate: duyệt spec → viết plan ngay turn đó; duyệt plan → hỏi cách chạy
  (main | subagent), chọn xong build luôn. Duyệt đã nói sẵn mode → build thẳng.
- Spec/plan/report viết tiếng Việt; report ngắn gọn (10-20 dòng). Tick `[x]` khi task pass.
- Cuối turn có đổi code → `graphify extract . --code-only`.
- Sub-agent: description mở đầu `<model>-<effort>-<việc>`, vd `sonnet-low-research`.

## 7. Chi tiết ở đâu — đọc khi cần, KHÔNG chép lại vào đây
Quy ước chung (working log, failover tavily, định tuyến plugin, QC): `skills/tdq-conventions/`.
Lane, tầng `nhỏ`, khuôn spec/plan, mode thực thi: các skill `tdq-*`.

## 8. Plugin ngoài
Mọi plugin đã bật sẵn ở user scope → không phải xin phép để dùng tool. Vẫn HỎI trước khi:
cài plugin/marketplace MỚI; chạy OAuth hay nhập credential; gọi tool GHI/XOÁ ra dịch vụ
ngoài (tạo page Notion, ghi DB, deploy, upload…).

## 9. Bộ nhớ dài hạn
Việc quan trọng (kiến trúc, sở thích user, lỗi tái diễn) → search mem0
(project = tên repo) trước khi kết luận, chốt xong thì `remember` một fact ngắn.
Chi tiết: skill `mem0-memory`.
