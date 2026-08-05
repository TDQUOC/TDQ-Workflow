# Phần B — Phân tích (phase `analyze`, chỉ lane full)

Đóng vai chuyên gia đúng lĩnh vực của yêu cầu. Mục tiêu: rời phase này với **ZERO chỗ đoán**.

1. **Kiểm kê năng lực (B0).** Chạy `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/skill_inventory.py"`,
   chép thêm skill built-in đang thấy trong context, điền bảng phán quyết theo khuôn
   [skill-inventory.md](skill-inventory.md) vào
   `docs/tdq/knowledge/<slug>.md` mục `## Năng lực dùng được`. Phân vân → DÙNG.

2. **Đọc code.** Tìm hết chỗ yêu cầu này chạm tới: entry point, luồng dữ liệu, config,
   test. Ghi lại phiên bản/framework đang dùng.

3. **Research nhiều hướng — giao subagent.** 2–4 truy vấn khác góc nhìn qua `tavily-primary`
   (luật failover ở [tavily.md](../../tdq-conventions/references/tavily.md)). Mặc định giao
   agent `search-scout`: agent tự chạy truy vấn, tự ghi `docs/tdq/research/<slug>.md`
   (truy vấn → nguồn → điều rút ra), trả về hội thoại chính **digest ≤ 1.500 ký tự**.
   Kết quả tavily thô nằm lại context tốn ~14M token/2 session — đó là lý do bắt buộc.
   Ngoại lệ tự làm: chỉ 1 truy vấn, hoặc đã biết sẵn URL (dùng `WebFetch`).
   Bỏ qua chỉ khi việc thuần nội bộ, không có ẩn số bên ngoài. Đủ tiêu chí deep
   search (≥2 dấu hiệu) → theo [deep-search.md](../../tdq-conventions/references/deep-search.md).

4. **Vòng interview.** Liệt kê MỌI câu hỏi làm thay đổi kết quả (phạm vi, UX, dữ liệu,
   lỗi, hiệu năng, tương thích). Cách hỏi: [interview.md](interview.md).
   Ghi hỏi–đáp vào `docs/tdq/questions/<slug>.md`. **Lặp** đến khi không còn câu hỏi
   nào làm đổi kết quả — nhiều vòng là bình thường. Không lấp chỗ trống bằng phỏng đoán.

5. **Chốt kiến thức.** Viết `docs/tdq/knowledge/<slug>.md`: quyết định đã chốt, ràng buộc,
   cách tiếp cận đã chọn + lý do, phương án đã loại + lý do, nguồn.

5b. **Quyết lộ trình.** Thêm mục `## Lộ trình` vào knowledge: bảng `Bước/phase | CÓ-BỎ |
   Vì sao` cho từng bước còn lại (research thêm, QC độc lập bằng agent, review sâu,
   chia subagent…). Khung bất biến không được bỏ: phân tích → spec/plan → implement →
   report. Chỉ cắt bước THỪA cho chính việc này, nêu lý do; phân vân → GIỮ. Lộ trình
   này chép nguyên sang spec §1b và user duyệt spec là duyệt luôn nó.

6. **Kiểm cổng** trước khi đi tiếp:
   - Phạm vi cuối đã rõ chưa: làm ra gì, có gì mới, output cụ thể là gì?
   - Có cần model / download / cài đặt gì không?
   - Phạm vi QC/test/validate đã có chưa?
   Thiếu bất kỳ mục nào → quay lại bước 4.

Xong khi: `knowledge/<slug>.md` (có mục Lộ trình) đã viết và cả 3 câu hỏi kiểm cổng đều
trả lời được.
Bước kế tiếp: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=spec`
rồi sang [tdq-spec](../../tdq-spec/SKILL.md) — cùng turn nếu interview đã xong, còn phải
hỏi user thì trình câu hỏi và dừng.
