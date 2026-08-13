# Brief — Lưu & nhúng ảnh đính kèm vào working log

## Nguyên văn

Nguyên văn user:
> "tôi muốn update là trong workinglog là nếu người dùng có gửi kèm ảnh thì lưu ảnh và
> embeding đến ảnh vào working log thì có khả thi không?"
> (sau khi nghe phân tích khả thi) "okay mở request đi"

Cách hiểu đầu tiên:
- **Mục tiêu:** khi user gửi ảnh đính kèm trong một turn có ghi working log, ảnh đó
  được lưu lại vào repo (không chỉ nằm ở cache tạm session) và được nhúng
  (markdown `![...](...)`) ngay trong mục log tương ứng của
  `docs/workinglog/<ngày>.md`.
- **Phạm vi đoán:** sửa quy ước ở `skills/tdq-conventions/` (định nghĩa cách ghi
  working log) — có thể cần thêm bước: copy ảnh từ
  `~/.claude/image-cache/<session-id>/<n>.png` sang một thư mục trong repo
  (vd `docs/workinglog/assets/<ngày>/`) rồi chèn link markdown.
- **Chỗ chưa rõ:**
  1. Ảnh có nên vào git repo (commit cùng code) hay chỉ lưu cục bộ (gitignore)?
     — liên quan rủi ro riêng tư (screenshot có thể chứa email/token/thông tin nhạy cảm).
  2. Áp dụng cho MỌI ảnh user gửi, hay chỉ khi ảnh thực sự liên quan tới nội dung
     turn đó (vd ảnh lỗi, ảnh minh hoạ yêu cầu) — có cần hỏi user mỗi lần trước khi lưu không?
  3. Đặt tên/thư mục file ảnh theo quy ước nào.

## Hiểu & kiến thức

### Năng lực dùng được
Chạy `scripts/skill_inventory.py` — danh sách chỉ có skill dự án Unity/Adobe/Canva…,
không có skill nào lo việc copy-file/nhúng-ảnh-markdown. Việc này thuần thao tác file +
sửa văn bản quy ước, không cần MCP hay skill ngoài.

### Đọc code
- `scripts/tdq_finish.py::step_worklog` — chỉ nhận `--log <summary>` rồi
  `fh.write(f"\n## {now:%H:%M}\n\n{summary.strip()}\n")` append vào cuối
  `docs/workinglog/<ngày>.md`. Ghi **verbatim** chuỗi truyền vào — nghĩa là nếu chuỗi đó
  đã chứa cú pháp markdown ảnh `![mô tả](assets/...)`, nó được ghi y nguyên. **Không cần
  sửa script này** để hỗ trợ nhúng ảnh — chỉ cần: (a) copy file ảnh vào repo trước khi gọi
  `tdq_finish.py`, (b) đưa đường dẫn ảnh vào chuỗi `--log` dưới dạng markdown.
- `skills/tdq-conventions/SKILL.md` §6 "Working log" — nơi đúng để thêm quy ước mới (bước
  copy ảnh + cú pháp nhúng), vì mọi skill `tdq-*` đều nạp file này.
- Xác nhận thực nghiệm: ảnh user gửi kèm được Claude Code cache tại
  `~/.claude/image-cache/<session-id>/<n>.png` (quyền `600`, chỉ user hiện tại đọc được).
  Thư mục này **theo session**, không có bằng chứng tồn tại vĩnh viễn — phải `cp` sang vị
  trí trong repo NGAY trong turn nhận ảnh, không trì hoãn sang turn sau.
- `.gitignore` hiện KHÔNG loại trừ `docs/workinglog/` — mọi file trong đó (kể cả ảnh nếu
  thêm) mặc định được git track trừ khi chủ động thêm pattern ignore.

## Hỏi đáp

1. Ảnh có nên commit vào git cùng working log không?
   - A (đề xuất): Track trong git — ảnh đi theo log khi clone/chia sẻ, tăng size repo dần,
     rủi ro riêng tư nếu screenshot chứa thông tin nhạy cảm.
   - B: Gitignore, chỉ lưu cục bộ.
   - C: Hỏi user xác nhận mỗi lần.
   → User chọn **A** ("1A 2B 3B", 2026-08-13 16:36). Ảnh track trong git, không gitignore.

2. Áp dụng cho ảnh nào?
   - A (đề xuất): Chỉ khi liên quan tới nội dung turn.
   - B: Mọi ảnh user gửi kèm trong turn có đổi repo.
   → User chọn **B**. Không cần Claude tự đánh giá "liên quan" — mọi ảnh gửi kèm trong
   turn có ghi working log đều được lưu + nhúng (turn không đổi repo thì vốn không ghi
   log — theo đúng §6 quy ước hiện có, không phát sinh case thừa).

3. Đặt tên/thư mục ảnh theo quy ước nào?
   - A (đề xuất): `assets/<ngày>/<HHmm>-<n>.<ext>`.
   - B: `assets/<slug-request>/<n>.<ext>`.
   → User chọn **B**. Nhóm ảnh theo slug request đang mở; `n` = số thứ tự kế tiếp trong
   thư mục đó (đếm file hiện có + 1), không phụ thuộc số thứ tự trong cache gốc.
   Không có `active_request` (vd tầng nhỏ, ngoài request) → dùng `misc` làm tên thư mục
   thay slug.

## Chốt kiến thức

- Cơ chế: khi turn có ảnh user gửi kèm VÀ turn đó phải ghi working log (đổi repo) →
  TRƯỚC khi gọi `tdq_finish.py --log`, copy từng ảnh từ đường dẫn cache
  (`~/.claude/image-cache/<session>/<n>.png`, đọc được ngay vì đã hiện trong context turn
  đó) sang `docs/workinglog/assets/<slug-request|misc>/<n>.<ext>` (`n` = đếm file đã có
  trong thư mục + 1), rồi chèn `![<mô tả ngắn>](assets/<slug>/<n>.<ext>)` vào đúng vị trí
  liên quan trong chuỗi truyền cho `--log` (không phải lúc nào cũng ở đầu — chèn cạnh câu
  mô tả ảnh đó).
- Không cần sửa `tdq_finish.py` (đã ghi verbatim chuỗi `--log`). Chỉ thêm quy ước + hướng
  dẫn thao tác vào `skills/tdq-conventions/SKILL.md` §6.
- Rủi ro riêng tư: user đã chọn A (track git) — chấp nhận rủi ro; không thêm bước hỏi xác
  nhận mỗi lần (đã loại ở câu 1).
- Định dạng ảnh: giữ nguyên đuôi gốc từ cache (`.png` — quan sát thực tế mọi ảnh cache đều
  `.png`); không transcode.

### Lộ trình

| Bước | CÓ/BỎ | Vì sao |
|---|---|---|
| Phân tích (đã xong) | CÓ | Đã đọc code + chốt 3 câu hỏi |
| Spec | CÓ | Bắt buộc, khung bất biến |
| Plan | CÓ | Bắt buộc, khung bất biến |
| Research thêm (tavily) | BỎ | Thuần nội bộ (quy ước + `cp` file), không có ẩn số bên ngoài cần search |
| QC độc lập bằng agent | BỎ | Việc nhỏ (sửa 1 file quy ước), QC tự làm đủ (giả lập 1 turn có ảnh, kiểm file + link) |
| Chia sub-agent | BỎ | 1-2 task, không đụng file rời nhau — mode `main` |
| Implement → report | CÓ | Khung bất biến |


