# BRIEF — Đổi tên mode ở cổng chọn cách chạy + phân tích lý do đề xuất

Ngày: 2026-08-14 · Slug: 2026-08-14-doi-ten-mode-implement

## Nguyên văn

> tôi muốn ở phase chọn mode sẽ đổi main thành inline implement và sub-agent implement cho
> nghe cho chuyên nghiệp và bổ sung thêm là sẽ có phân tích lí do tại sao đề xuất mode
> implement đó cho spec/plan đó

Kèm ảnh chụp khối hỏi hiện tại:

```
Plan đã được duyệt. Còn một câu cuối: bạn muốn tôi chạy theo cách nào?
- A (đề xuất): main — tôi làm tuần tự ngay trong cuộc trò chuyện này, bạn theo dõi được từng bước.
- B: subagent — tôi chia việc cho nhiều trợ lý chạy song song, nhanh hơn nhưng bạn chỉ thấy báo cáo từng chặng.
➤ Trả lời: nhắn "main" hoặc "subagent" (chọn xong tôi bắt tay làm ngay) · Góp ý: nhắn trực tiếp
```

### Cách hiểu đầu tiên

**Mục tiêu.** Cổng `mode` đang gọi hai lựa chọn bằng từ kỹ thuật nội bộ (`main`,
`subagent`). User muốn tên hiển thị nghe chuyên nghiệp hơn — "inline implement" và
"sub-agent implement" — và muốn khối hỏi kèm một đoạn phân tích vì sao đề xuất đúng mode
đó cho chính spec/plan đang chờ, thay vì mô tả chung chung như hiện nay.

**Phạm vi đoán.**
- Sửa khuôn khối hỏi mode ở `skills/tdq-plan/SKILL.md` (bước 6).
- Bổ sung luật viết phần "vì sao đề xuất mode này" — dựa vào số task, mức phụ thuộc, có
  đụng chung file không, có nhãn `(mcp)` không.
- Các chỗ khác nhắc tên mode: `scripts/tdq_state.py` (`VALID_MODES`, checklist `next`),
  `hooks/scripts/_common.py` (gợi ý duyệt), `hooks/scripts/prompt_context.py` (regex nhận
  câu trả lời), `skills/tdq-build/SKILL.md`, `skills/tdq-plan/references/plan-template.md`,
  và test tương ứng.
- NGOÀI phạm vi (theo quyết định đã chốt trước đó): thư mục `portable/`.

**Chỗ chưa rõ.**
1. Giá trị lưu trong state và tham số CLI (`--mode main|subagent`) có đổi theo không, hay
   chỉ đổi chữ hiển thị cho user?
2. User gõ "main"/"subagent" như cũ có còn được chấp nhận không (tương thích ngược)?
3. Đoạn phân tích lý do dài bao nhiêu, đặt ở đâu trong khối hỏi, và có bắt buộc nêu cả lý
   do KHÔNG chọn phương án còn lại không?

## Hiểu & kiến thức

### Năng lực dùng được

| Năng lực | Phán quyết | Vì sao |
|---|---|---|
| `graphify` | BỎ | Việc nằm ở chuỗi hiển thị và tài liệu skill, không phải câu hỏi liên kết mã. |
| `tavily-primary` (web search) | BỎ | Thuần nội bộ: quy ước của chính repo này, không có ẩn số bên ngoài. |
| `mem0-memory` | DÙNG | Chốt xong ghi 1 fact ngắn về quy ước đặt tên mode. |
| Agent `tdq-reviewer` / `tdq-qc-tester` | BỎ | Thay đổi nhỏ, rủi ro thấp, QC bằng lệnh là đủ. |

### Bản đồ chỗ nhắc tên mode (đã đọc code)

| Chỗ | Nội dung | Vai trò |
|---|---|---|
| `scripts/tdq_state.py:29` | `VALID_MODES = ("main", "subagent")` | Giá trị hợp lệ của `--mode`, lưu vào `implement_mode`. |
| `scripts/tdq_state.py:499-504` | `effective_mode` cảnh báo khi mode lạ | Lớp kiểm tra. |
| `scripts/tdq_state.py:573-585` | Checklist phase `mode` | Văn bản hướng dẫn Claude ở cổng mode. |
| `scripts/tdq_state.py:991,999` | Parse `--mode`, và dạng gõ tắt `approve plan main` | Nhập liệu. |
| `hooks/scripts/_common.py:36-40` | `APPROVE_HINTS["mode"]` | Lời nhắc một dòng in mỗi prompt. |
| `hooks/scripts/_common.py:43` | `_PLAN_MODE` regex đọc dòng `Mode thực thi:` | Đọc mode ĐỀ XUẤT trong plan. |
| `hooks/scripts/prompt_context.py:42` | `MODE` regex nhận câu trả lời của user | Nhận diện user đã chọn mode. |
| `hooks/scripts/edit_gate.py:82` | Chuỗi `--mode <main\|subagent>` trong lời nhắc | Hiển thị. |
| `skills/tdq-plan/SKILL.md` bước 1 & 6 | Khuôn khối hỏi mode | Chỗ chính user muốn đổi. |
| `skills/tdq-plan/references/plan-template.md:9,94-99` | Dòng `Mode thực thi:` | Nơi ghi đề xuất. |
| `skills/tdq-build/SKILL.md` Phần A | Xử lý `implement_mode` | Hành vi lúc build. |

### Tiền lệ có sẵn trong repo

Lane đã tách sẵn hai lớp: giá trị chuẩn là `quick`/`full`, còn `LANE_LABELS` cho chữ
hiển thị ("chế độ nhanh (express)") và `LANE_ALIASES` nhận nhiều cách gõ
(`nhanh`, `express`, `chuyen-sau`…). Mode hiện chưa có lớp nhãn nào — `VALID_MODES` vừa
là giá trị lưu vừa là chữ in ra. Cách rẻ và an toàn nhất là bê nguyên mẫu hình của lane
sang mode: thêm `MODE_LABELS` + `MODE_ALIASES`, giữ `main|subagent` làm giá trị chuẩn.

## Hỏi đáp

### Vòng 1 — đã trả lời (user: "1a 2a 3a 4b")

1. **Đổi lớp nào → 1A.** Chỉ đổi chữ hiển thị: thêm `MODE_LABELS`/`MODE_ALIASES`, giữ
   `main|subagent` làm giá trị lưu trong state và tham số `--mode`. Không migrate state,
   không đụng `_PLAN_MODE`.
2. **Tương thích ngược → 2A.** Vẫn nhận "main"/"subagent", cộng thêm "inline",
   "sub-agent" và các biến thể có chữ "implement".
3. **Phân tích lý do → 3A.** 1–3 dòng ngay dưới hai option, căn cứ lấy từ chính plan (số
   task, mức phụ thuộc, có đụng chung file không, có nhãn `(mcp)` không), kèm đúng một
   câu vì sao không chọn phương án còn lại.
4. **Nhãn → 4B.** Việt hoá theo kiểu nhãn lane: `main` → "làm trực tiếp (inline
   implement)", `subagent` → "giao trợ lý (sub-agent implement)".

Không còn câu hỏi nào làm đổi kết quả → kết thúc interview.

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | Thuần nội bộ, quy ước của chính repo, không có ẩn số bên ngoài. |
| Interview | CÓ (đã xong) | 4 câu đã hỏi và đã có đáp án ở trên. |
| Spec + plan | CÓ | Khung bất biến. |
| Implement | CÓ | Sửa `tdq_state.py`, 3 hook, 2 skill, plan-template, test. |
| QC độc lập bằng agent | BỎ | Thay đổi lớp hiển thị, rủi ro thấp; QC bằng lệnh là đủ. |
| Chia subagent | Để cổng `mode` quyết | Task ít, đụng file rời nhau nhưng phụ thuộc chuỗi nhãn. |
| Report | CÓ | Khung bất biến. |

