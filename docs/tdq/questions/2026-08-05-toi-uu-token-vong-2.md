# Hỏi–đáp — tối ưu token vòng 2

## Vòng 1 (00:52)

**H1. Phạm vi có mở khoá `~/.claude/CLAUDE.md` và `~/.claude/settings.json` không?**
(vòng 1 loại trừ cả hai; đo lại thấy context nền chiếm 24% hóa đơn)
→ **Đ: Mở cả hai.** Được sửa CLAUDE.md (12.245 byte → mục tiêu ~4.000 byte, đẩy phần
dài sang skill nạp lười) và settings.json (chuyển plugin ít dùng sang tier on_demand).

**H2. 26% tool call là bookkeeping (state 82 + doc_lint 48 + test 48 + graphify 13).
Gộp thế nào?**
→ **Đ: Một lệnh `tdq_finish.py`.** Cuối turn chạy 1 lệnh làm cả 4 việc (set phase +
lint đúng file vừa sửa + append working log + graphify), in 1 dòng tổng kết.
4–6 call → 1 call mỗi turn.

**H3. Đang bật 27 plugin, 11 trong đó là LSP cho ngôn ngữ repo không dùng. Xử lý sao?**
→ **Đ: Tắt LSP trừ pyright.** Chuyển 10 LSP còn lại sang on_demand, bật lại bằng 1 lệnh
khi cần.

**H4. Bổ sung thêm gì không?**
→ **Đ: Có — user nói thêm.** (chờ nội dung, ghi tiếp ở vòng 2)

## Vòng 2 (01:10)

**User bổ sung (nguyên văn):** "tên của sub-agent sẽ mở đầu = model name + think level của nó
trước. ví dụ `sonnet-low_ resreach doc`" và "tối ưu nhưng ko được đánh đổi quality làm việc và output".
→ Quy ước chốt: `description` của mọi lần gọi Agent theo dạng `<model>-<effort>_ <mô tả>`.
Vì `effort` chỉ đọc được từ frontmatter nên phải khai báo tường minh cho cả 7 agent (task D2).
Ràng buộc chất lượng thành điều kiện chặn: task tối ưu nào làm giảm độ tin cậy thì loại
khỏi spec, không "cân nhắc" (đã loại 3 phương án, xem knowledge mục 5).

**H5. CLAUDE.md rút gọn thế nào cho an toàn?**
→ **Đ: Duyệt từng mục trong spec.** Spec §2 đưa bảng 11 mục kèm phán quyết GIỮ/CẮT/CHUYỂN,
nơi đến và cơ chế chống bỏ sót (bản repo + backup + test đối chiếu).

**H6. Context dài thì xử lý thế nào?**
→ **Đ: Giao phase cho subagent khi plan > 6 task.** Không dùng luật tự compact vì compact
làm mất chi tiết. Thành task D4 và là lý do plan này đề xuất mode `subagent`.

**H7. Bổ sung thêm gì không?**
→ **Đ: Không, đủ rồi — làm tiếp đi.** Chốt interview, sang viết spec.
