# Phần B — Phân tích (phase `analyze`, chỉ chế độ chuyên sâu (deep))

Đóng vai chuyên gia đúng lĩnh vực của yêu cầu. Mục tiêu: rời phase này với **ZERO chỗ đoán**.
Mọi thứ ghi ra ở phase này nằm trong MỘT file `docs/tdq/brief/<slug>.md`, đúng 3 mục:
`## Nguyên văn` (yêu cầu user, đã ghi ở Phần A), `## Hiểu & kiến thức`, `## Hỏi đáp`.

1. **Kiểm kê năng lực (B0).** Chạy
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/skill_inventory.py" --loc "<từ khoá của yêu cầu>"`,
   bản lọc luôn giữ đủ skill nguồn `project` và `plugin:tdq-workflow`; nghi còn sót thì
   chạy lại với `--tat-ca` để xem đủ bảng,
   chép thêm skill built-in đang thấy trong context, điền bảng phán quyết theo khuôn
   [skill-inventory.md](skill-inventory.md) vào
   brief mục `## Hiểu & kiến thức` → `### Năng lực dùng được`. Phân vân → DÙNG.

2. **Đọc code.** Tìm hết chỗ yêu cầu này chạm tới: entry point, luồng dữ liệu, config,
   test. Ghi lại phiên bản/framework đang dùng.

   **Luật ĐỌC đồ thị graphify** (gợi ý có điều kiện, KHÔNG bắt buộc mỗi lần analyze):
   - MỞ đồ thị khi câu hỏi thuộc dạng **liên kết** hoặc **bản đồ tổng thể**.
     Dạng đó là: "ai gọi X", "sửa X thì ảnh hưởng tới đâu", "hai chỗ này nối nhau đường
     nào", "project có những cụm nào". Lệnh: `graphify query|path|explain|affected`.
   - DÙNG grep/read khi câu hỏi là tìm một chuỗi, đọc một file, hay xem nội dung cụ thể —
     nhanh hơn và không phụ thuộc đồ thị có mới hay không.
   - Đồ thị chỉ chứa mã nguồn sản phẩm (`scripts/`, `hooks/`); `tests/` và tài liệu bị
     `.graphifyignore` loại. Cần tra test hay doc thì grep, đừng chờ đồ thị.

3. **Research nhiều hướng — giao subagent.** 2–4 truy vấn khác góc nhìn qua `tavily-primary`
   (luật failover ở [tavily.md](../../tdq-conventions/references/tavily.md)). Mặc định giao
   một sub-agent `general-purpose`: agent tự chạy truy vấn, tự ghi `docs/tdq/research/<slug>.md`
   (truy vấn → nguồn → điều rút ra), trả về hội thoại chính **digest ≤ 1.500 ký tự**.
   Kết quả tavily thô nằm lại context tốn ~14M token/2 session — đó là lý do bắt buộc.
   Ngoại lệ tự làm: chỉ 1 truy vấn, hoặc đã biết sẵn URL (dùng `WebFetch`).
   Bỏ qua chỉ khi việc thuần nội bộ, không có ẩn số bên ngoài.

4. **Vòng interview — tổng quát trước, chi tiết sau.** Chạy **vòng scope** trước theo
   [scope-round.md](scope-round.md): request bao quanh mặt nào, bối cảnh bằng số ra sao,
   từ đó suy ra mức đầu tư. Vòng scope có điều kiện; bỏ thì ghi lý do vào brief. Rồi mới
   tới vòng chi tiết: liệt kê MỌI câu hỏi làm thay đổi kết quả (phạm vi, UX, dữ liệu,
   lỗi, hiệu năng, tương thích) nhưng chỉ trong các mặt user đã chọn. Cách hỏi:
   [interview.md](interview.md).
   Ghi hỏi–đáp vào brief mục `## Hỏi đáp`. **Lặp** đến khi không còn câu hỏi
   nào làm đổi kết quả — nhiều vòng là bình thường. Không lấp chỗ trống bằng phỏng đoán.

5. **Chốt kiến thức.** Viết vào brief mục `## Hiểu & kiến thức`: quyết định đã chốt,
   ràng buộc, cách tiếp cận đã chọn + lý do, phương án đã loại + lý do, nguồn.

5b. **Quyết lộ trình.** Thêm `### Lộ trình` vào mục đó: bảng `Bước/phase | CÓ-BỎ |
   Vì sao` cho từng bước còn lại (research thêm, QC độc lập bằng agent, review sâu,
   chia subagent…). Khung bất biến không được bỏ: phân tích → spec/plan → implement →
   report. Chỉ cắt bước THỪA cho chính việc này, nêu lý do; phân vân → GIỮ. Lộ trình
   này chép nguyên sang spec §1b và user duyệt spec là duyệt luôn nó.

6. **Kiểm cổng** trước khi đi tiếp:
   - Phạm vi cuối đã rõ chưa: làm ra gì, có gì mới, output cụ thể là gì?
   - Có cần model / download / cài đặt gì không?
   - Phạm vi QC/test/validate đã có chưa?
   Thiếu bất kỳ mục nào → quay lại bước 4.

Xong khi: `brief/<slug>.md` đủ 3 mục (có `### Lộ trình`) và cả 3 câu hỏi kiểm cổng đều
trả lời được.
Bước kế tiếp: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=spec`
rồi sang [tdq-spec](../../tdq-spec/SKILL.md) — cùng turn nếu interview đã xong, còn phải
hỏi user thì trình câu hỏi và dừng.
