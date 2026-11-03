# REPORT — Chấm toàn bộ workflow theo hướng LLM đọc & chi phí context

Ngày: 2026-08-14 · Lane: full · Mode: main · QC: 12/12 PASS

Đã chấm 28 file `skills/` + 6 hook + 3 agent bằng thang 6 tiêu chí R1–R6 chốt trước khi
đo. Kết quả: trung bình 8,7/10, thấp nhất 6/10. Toàn bộ nằm ở
`docs/tdq/knowledge/2026-08-14-toi-uu-llm-workflow.md`.

Ba điều đáng nhớ nhất:

1. **Hook không phải chỗ phí.** Trung vị cao nhất 56,2 ms, tổng đầu ra ≤ 2.075 byte mỗi
   lượt kể cả khi mọi gate cùng bắn. Không đề xuất nào đụng hook.
2. **Chỗ phí lớn nhất là một lần in.** `skill_inventory.py` đổ 39.722 byte ≈ 9.774 token
   vào context mỗi lần chạy analyze — lớn hơn tổng sáu đề xuất còn lại cộng lại.
3. **Hai `SKILL.md` lớn nhất mất điểm ở tầng nạp, không ở độ rõ.** `tdq-intake` và
   `tdq-build` gói các nhánh loại trừ nhau vào một lần nạp; chuyển chỗ là cắt được
   ≈ 1.170 token mỗi lần gọi mà không mất chữ nào.

Bảy đề xuất Đ1–Đ7, mỗi đề xuất có nội dung nháp và lệnh kiểm. Bảng `## Đối chiếu luật`
đếm mệnh lệnh trước/sau trên từng cụm file: 7 dòng tăng, 3 dòng giữ nguyên, 0 dòng giảm —
tức cắt token mà số luật tăng, đúng ràng buộc "không đổi behavior".

Khuyến nghị: **Gói vừa** (Đ2+Đ3+Đ5+Đ6+Đ7, toàn bộ thuần văn bản), rồi mở request riêng
cho Đ1 vì nó là đề xuất duy nhất sửa mã và cần test riêng cho rủi ro "lọc mất năng lực".

Phạm vi giữ đúng: `skills/`, `hooks/`, `agents/`, `scripts/` sạch tuyệt đối
(`git status --porcelain` rỗng), `563 passed` giữ nguyên. Không commit, không push.

Còn mở: `portable/` (12 file, 13.075 token) chưa chấm — là request riêng, và đáng mở vì
đó là nơi model hạng thấp chạy nhiều nhất.
