# Quy tắc làm việc cho Claude

## 1. Quy trình chung
- Làm việc như chuyên gia kỹ tính: phân tích kỹ, research trước khi kết luận, không đoán.
- Yêu cầu chưa rõ → interview user trước khi làm tiếp. Mọi câu hỏi có option: mỗi option
  đúng 1 dòng, khuôn `- A (đề xuất): nội dung`, cấm gộp option vào đoạn văn.
- Đủ thông tin → plan → tự review → trình plan → **chờ user duyệt** mới làm. Mọi task.
- Không tự vào plan mode; trình plan trong chat hoặc file rồi chờ duyệt.

## 2. Git & worktree
- Project chưa có git → được khởi tạo git/worktree, nhớ kiểm tra việc merge worktree.
- Tên branch/commit/worktree KHÔNG bắt đầu bằng `claude`, `antigravity`, `gemini`, `codex`.
- Commit message không chứa "generated with…", "được tạo bởi…", Co-Authored-By của AI.
- Chỉ commit/push khi user yêu cầu. Ngoại lệ duy nhất: đang build TDQ gặp chặn kỹ thuật
  → được tự commit để gỡ chặn (message chuẩn, KHÔNG push, liệt kê commit đó trong report).

## 3. Research & độ tin cậy
- Luôn search nhiều hướng trước khi tổng hợp. `tavily-primary` là lớp search mặc định;
  luật failover: `skills/tdq-conventions/references/tavily.md`.
- Không bao giờ đưa API key vào câu trả lời, log, lệnh shell hay prompt gửi model.
- Mọi kết luận phải có nguồn — không được bịa thông tin chưa xác định.

## 4. Trình bày
- Ngắn gọn nhất có thể, đi thẳng vào vấn đề chính.

## 5. Log
- Khi develop: ghi log đầy đủ, có timestamp, phục vụ debug. Sản phẩm build ra luôn có
  log service bật mặc định, tắt được qua config.

## 6. Working log
- Turn nào có thay đổi repo → append tóm tắt vào `docs/workinglog/YYYY-MM-DD.md`: giờ,
  file đã đổi, lý do, kiểm tra đã chạy. Turn chỉ đọc/phân tích thì không ghi.

## 7. TDQ Workflow — mặc định tuyệt đối
- **Mọi prompt mới → skill `tdq-intake`**, kể cả câu hỏi nhỏ. Chỉ message thuộc request
  đang mở mới không tính là prompt mới. Thấy `[TDQ:INTAKE]` → mở intake trước mọi việc.
- Chỉ NGƯỜI DÙNG duyệt, bằng chat thường. Câu chữ mơ hồ → HỎI lại, cấm tự suy diễn duyệt.
- Ghi duyệt/state CHỈ qua `scripts/tdq_state.py`; cấm sửa `docs/tdq/state.json` trực tiếp.
- Gộp gate: duyệt spec → viết plan ngay trong turn đó; duyệt plan kèm mode
  (main | subagent) → build ngay trong turn đó. Duyệt plan không nói mode → HỎI.
- Spec/plan/report viết tiếng Việt; report ngắn gọn (khuyến nghị 10-20 dòng, không giới
  hạn cứng). Tick `[x]` ngay khi task pass test.
- Cuối turn có đổi code → chạy `graphify extract . --code-only`.
- Chi tiết lane, tầng `nhỏ`, QC: trong các skill `tdq-*`.
- Sub-agent: description mở đầu `<model>-<effort>-<việc>`, vd `sonnet-low-research`.

## 8. Việc chuyên biệt → đọc file tương ứng
- User báo lỗi/issue → `skills/tdq-intake/references/issue-triage.md`.
- Lập spec → `skills/tdq-spec/references/spec-template.md`.
- Cần plugin ngoài (Notion, Figma, MongoDB…) →
  `skills/tdq-conventions/references/plugin-routing.md`: đề xuất và HỎI user trước, chưa hỏi
  thì cấm bật.
