# Hỏi–đáp — 2026-08-03-skill-vao-goi-external

## Vòng 1
1. **Nguồn trích đoạn skill nhúng vào gói (nhánh 2)?**
   → User chọn: **chép nguyên SKILL.md vào gói** (không dùng mục chuẩn "External notes", không chắt lọc ad-hoc).
2. **Nhận diện task dùng skill MCP-tool để loại khỏi gói?**
   → User chọn: **đánh dấu trong plan** — khối `Dùng:` ghi nhãn loại, ví dụ `Dùng: notion (mcp)`; split-plan đọc nhãn bằng máy và loại task, Claude tự làm.
3. **AGENTS.md trong worktree (nhánh 1)?**
   → User chọn: **chỉ AGENTS.md** ≤60 dòng ở root worktree, sinh lúc chuẩn bị, **xóa trước diff-check/merge**; KHÔNG làm `.agents/skills/` cho agy.
4. **Enforcement khi plan có `Dùng:` mà gói thiếu skill?**
   → User chọn ban đầu: chỉ quy ước trong skill docs.

## Vòng 2 (follow-up vì va chạm ràng buộc "model cấp thấp")
5. **Giới hạn khi chép nguyên SKILL.md?** (cảnh báo: model thấp suy giảm từ ~3k token)
   → User chốt: **chép nguyên SKILL.md + TOÀN BỘ references** — chấp nhận rủi ro context phình, ưu tiên không sót thông tin. Đã được cảnh báo rõ trong option.
6. **Lưới máy-kiểm tối thiểu thay vì chỉ quy ước?**
   → User đổi sang: **warning trong script** — `run-plan` in CẢNH BÁO + ghi log khi gói thiếu mục skill so với khối `Dùng:` của plan, vẫn chạy tiếp (không chặn cứng); kèm unit test.

Không còn câu hỏi làm thay đổi kết quả.
