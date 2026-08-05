# Phần B — Phân tích (phase `analyze`, chỉ lane full)

Đóng vai chuyên gia đúng lĩnh vực của yêu cầu. Mục tiêu: rời phase này với **ZERO chỗ đoán**.

1. **Kiểm kê năng lực (B0).** Chạy `python3 scripts/skill_inventory.py`,
   chép thêm skill built-in đang thấy trong context, điền bảng phán quyết theo khuôn
   [skill-inventory.md](skill-inventory.md) vào
   `docs/tdq/knowledge/<slug>.md` mục `## Năng lực dùng được`. Phân vân → DÙNG.
   Agent không có skill system → liệt kê công cụ/lệnh tương đương mình có, xét như skill.

2. **Đọc code.** Tìm hết chỗ yêu cầu này chạm tới: entry point, luồng dữ liệu, config,
   test. Ghi lại phiên bản/framework đang dùng.

3. **Research nhiều hướng — giao subagent.** 2–4 truy vấn khác góc nhìn qua `tavily-primary`
   (harness không có tavily → dùng công cụ search sẵn có của nó; lỗi mới đổi nguồn, không
   gọi song song). Harness có subagent → giao hẳn (bản Claude Code dùng agent `search-scout`):
   agent tự ghi file research, chỉ trả về digest **≤ 1.500 ký tự**, vì kết quả search thô
   nằm lại context rất tốn token. Lưu `docs/tdq/research/<slug>.md` dạng: truy vấn → nguồn → điều rút ra.
   Bỏ qua chỉ khi việc thuần nội bộ, không có ẩn số bên ngoài. Đủ tiêu chí deep
   search (≥2 dấu hiệu) → theo [06-deep-search.md](../06-deep-search.md).

4. **Vòng interview.** Liệt kê MỌI câu hỏi làm thay đổi kết quả (phạm vi, UX, dữ liệu,
   lỗi, hiệu năng, tương thích). Hỏi theo cụm 2–4 câu, mỗi câu kèm 2–4 phương án.
   **Luôn hỏi bằng danh sách trong chat**, khuôn bắt buộc:

   ```
   <số>. <Câu hỏi>
   - A (đề xuất): <phương án> — <hệ quả 1 dòng>
   - B: <phương án> — <hệ quả 1 dòng>
   ```

   Mỗi option đúng 1 dòng riêng, nhãn chữ HOA rồi dấu `:`. **Cấm gộp** nhiều option vào
   một dòng hay nhét vào đoạn văn dạng `(a) … · (b) …`. Phương án bạn khuyên luôn là `A`
   và mang nhãn `(đề xuất)`. Ghi hỏi–đáp vào `docs/tdq/questions/<slug>.md`.
   **Lặp** đến khi không còn câu hỏi nào làm đổi kết quả — nhiều vòng là bình thường.
   Không lấp chỗ trống bằng phỏng đoán. **Câu cuối mỗi vòng là bắt buộc**, kể cả khi chỉ
   có 1 câu hỏi: hỏi thêm đúng câu "Bạn muốn bổ sung thêm gì không?" với hai option
   `- A (đề xuất): Không, đủ rồi — làm tiếp đi.` và `- B: Có — tôi nói thêm.`

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
Bước kế tiếp: `python3 scripts/tdq_state.py set phase=spec` rồi sang
[02-spec.md](../02-spec.md) — cùng turn nếu interview đã xong, còn phải
hỏi user thì trình câu hỏi và dừng.
