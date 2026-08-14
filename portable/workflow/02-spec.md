# Phase `spec`

Spec viết **tiếng Việt**. Yêu cầu spec dựa trên brief đã đủ 3 mục (`## Nguyên văn`,
`## Hiểu & kiến thức` có `### Lộ trình`, `## Hỏi đáp` không còn câu mở).

## Các bước

1. **Viết** `docs/tdq/spec/<slug>.md` từ `docs/tdq/brief/<slug>.md`, theo khuôn:

   ```markdown
   # SPEC — <tên việc>
   **Ngày:** YYYY-MM-DD · Bản: 1.0 · Brief: ../brief/<slug>.md · Lane: full
   **Trạng thái:** CHỜ DUYỆT

   ## 1. Mục tiêu & phạm vi
   - Mục tiêu: <1–3 câu, đo được>
   - Trong phạm vi: <gạch đầu dòng>
   - NGOÀI phạm vi: <gạch đầu dòng>

   ## 1b. Lộ trình
   Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.
   | Bước/phase | Chạy? | Vì sao |
   |---|---|---|

   ## 2. Đầu ra cụ thể
   | # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
   |---|---|---|---|

   ## 3. Cách tiếp cận & lý do
   - Chọn / Vì / Đã loại

   ## 3b. Năng lực & công cụ
   Chép bảng phán quyết từ brief mục `### Năng lực dùng được`. Phân vân → DÙNG.

   ## 4. Yêu cầu bắt buộc
   - Log service bật mặc định (chỉ khi có runtime; không có runtime → `Log: BỎ — <lý do>`)
   - Không placeholder/TODO stub/mock giả làm thật
   - Mỗi thành phần có test riêng, chạy được bằng một lệnh

   ## 5. Ràng buộc & rủi ro
   | Rủi ro | Ảnh hưởng | Cách giảm |
   |---|---|---|

   ## 6. QC & Definition of Done
   | # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
   |---|---|---|---|
   **DoD:** <liệt kê điều kiện đủ để tuyên bố xong>

   ## 7. Câu hỏi còn mở
   (Phải RỖNG. Còn câu hỏi → quay lại phase analyze.)
   ```

   Mục "câu hỏi còn mở" PHẢI rỗng — còn câu hỏi thì quay lại phase `analyze`.

2. **Tự review.** Đọc lại tìm chỗ hổng/mâu thuẫn, sửa. Không có `doc_lint.py` trong
   harness này thì tự kiểm bằng checklist: đủ mục trên, mọi đầu ra §2 có ít nhất một
   hạng mục QC ở §6, §7 rỗng, không câu nào mơ hồ ("phù hợp", "tối ưu", "nếu cần") mà
   thiếu ngưỡng cụ thể.

3. **Đăng ký file vào state:**
   ```
   python3 scripts/tdq_state.py set spec_file=docs/tdq/spec/<slug>.md
   ```

4. **Trình bày & DỪNG.** Trong chat: tóm tắt spec ≤ 50 dòng (mục tiêu, đầu ra, DoD,
   rủi ro chính). Bọc tóm tắt theo
   [references/user-facing-block.md](references/user-facing-block.md) — nhãn trường in
   đậm, đường dẫn bọc nháy ngược, dòng `➤` nằm cuối. Ngay dưới tóm tắt in đúng dòng:
   ```
   ➤ Duyệt: nhắn "duyệt spec" · Góp ý: nhắn trực tiếp
   ```
   Rồi **kết thúc turn**. Không viết plan, không sửa code. User góp ý thay vì duyệt →
   sửa spec, tăng số bản, trình lại, chờ tiếp.

5. **User duyệt → ghi nhận NGAY:**
   ```
   python3 scripts/tdq_state.py approve spec --by "<nguyên văn câu user>"
   ```
   Mơ hồ thì HỎI — luật đầy đủ ở [references/approval.md](references/approval.md).

Xong khi: `spec_approved = true` và `spec_file` trỏ đúng file đã trình.
Bước kế tiếp: `python3 scripts/tdq_state.py set phase=plan` rồi sang
[03-plan.md](03-plan.md) **NGAY trong cùng turn** — không bắt user nhắn thêm câu nào.
