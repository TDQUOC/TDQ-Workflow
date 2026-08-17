# Cổng chọn mode — khuôn hỏi & luật viết đoạn lý do

Dùng ở bước 6 của [tdq-plan](../SKILL.md), khi plan đã duyệt mà user chưa nói mode.
Khối này theo [user-facing-block.md](../../tdq-conventions/references/user-facing-block.md).

## Khuôn hỏi

```
Plan đã được duyệt. Còn một câu cuối: bạn muốn tôi chạy theo cách nào?

- A (đề xuất): làm trực tiếp (inline implement) — tôi làm tuần tự ngay trong cuộc trò chuyện này, bạn theo dõi được từng bước.
- B: giao trợ lý (sub-agent implement) — tôi làm leader: chia cả plan thành từng đợt, mỗi đợt phát cho nhiều trợ lý chạy song song ở worktree riêng, phần không tách được thì tôi tự làm, xong đợt nào tôi kiểm và gộp đợt đó.

**Vì sao đề xuất A cho plan này:** <1–3 dòng, theo luật dưới>

---

**Bạn chọn cách nào?**

➤ Trả lời: nhắn "A" / "inline" hoặc "B" / "sub-agent" (chọn xong tôi bắt tay làm ngay) · Góp ý: nhắn trực tiếp
```

Đề xuất nằm ở A dù đề xuất là mode nào — đổi nội dung dòng A, không đổi vị trí.

## Luật viết đoạn "Vì sao đề xuất"

Dài 1–3 dòng, đặt ngay dưới hai option. Cấm nói chung chung. Mọi câu phải dựa trên
**căn cứ đọc được từ chính plan này**. Lấy đủ 4 căn cứ:

1. Số task.
2. Có task nào phụ thuộc nối tiếp task trước không.
3. Số file bị nhiều task cùng đụng.
4. Có task nào mang nhãn `(mcp)` không — nhãn đó buộc Claude tự làm.

Kết bằng đúng một câu nói vì sao KHÔNG chọn phương án còn lại.

Ví dụ đủ căn cứ:

> 12 task nhưng dính chuỗi, 4 task cùng sửa `tdq_state.py`, T4.3 mang nhãn `(mcp)`;
> không chọn B vì lợi ích song song gần bằng 0 mà thêm rủi ro merge worktree.

## B KHÔNG có nghĩa là giao hết

Mode B là mô hình lai, không phải "mọi task đều đẩy cho agent con". Leader vẫn tự làm
những task khớp đúng một trong bốn nhóm lý do đóng: `phu-thuoc`, `vung-khoa`, `mcp`,
`file-luat`. Phần còn lại bắt buộc phải giao — và `scripts/tdq_team.py kiem-ke` exit
khác 0 nếu leader bịa ra lý do thứ năm để ôm việc.

Vì vậy đoạn "Vì sao đề xuất" đừng bao giờ mô tả B là "giao toàn bộ cho trợ lý". Cách
đo đúng của B là: **bao nhiêu task tách được trên tổng số task**. Con số đó, chứ không
phải tổng số task, mới quyết định B có nhanh hơn A hay không. Luật đầy đủ của mode đội:
[team-mode.md](../../tdq-build/references/team-mode.md).

## Tên gọi

(nhắc lại có chủ ý — bản gốc ở bước 6 của `skills/tdq-plan/SKILL.md`.)

Hai tên trên là **nhãn hiển thị**. Giá trị ghi vào state vẫn là `main`/`subagent`
(`MODE_LABELS`/`MODE_ALIASES` trong `scripts/tdq_state.py`). User gõ "inline",
"sub-agent implement" hay tên máy cũ đều được nhận về đúng định danh máy.
