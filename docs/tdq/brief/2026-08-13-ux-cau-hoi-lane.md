# Brief — Rút gọn UX câu hỏi chọn lane

## Nguyên văn

Nguyên văn user (kèm ảnh chụp màn hình một session khác, cho thấy dạng in hiện tại của
câu hỏi chọn lane trong `tdq-intake`):
> "chỉnh lại ux của chỗ này chỉ hiện lí do tại sao và đề xuất pipeline phù hợp, cuối chốt
> lại là mời bạn chọn pipeline và hướng dẫn chi tiết cho người dùng dễ hiểu mở request
> mới cho cái này"

Nội dung ảnh (transcript) — dạng in HIỆN TẠI của bước "Đề xuất lane rồi HỎI"
(`tdq-intake/SKILL.md` Phần A bước 2):
```
Tóm lại việc cần bạn quyết:

Cỡ: full · Cần: research (Figma design context), interview, QC độc lập

- A (đề xuất): chế độ chuyên sâu (deep) — mode mới đụng đường đi chính của app đang
  chạy được, còn 7 điểm mờ (định nghĩa "lost ≥2 pack", chọn epc nào khi gói có nhiều
  người, CMS lỗi mạng khác 404, thời lượng màn 3 / màn lỗi, khuôn file config, dựng màn
  trong SampleScene hay scene riêng), và cần đọc design context Figma trước khi dựng 3
  màn mới
- B: chế độ nhanh (express) — tôi tự chốt các điểm mờ bằng mặc định hợp lý, làm gọn
  trong ít vòng
```

Cách hiểu đầu tiên:
- **Mục tiêu:** đổi cách trình bày câu hỏi chọn lane ở `tdq-intake/SKILL.md` Phần A bước 2
  (và có thể `references/interview.md` nếu dùng chung khuôn) — bớt thông tin kỹ thuật thô
  (dòng `Cỡ:`/`Cần:`), chỉ giữ LÝ DO cho mỗi lựa chọn + đề xuất rõ ràng, kết thúc bằng lời
  mời chọn kèm hướng dẫn thân thiện hơn cho người mới.
- **Phạm vi đoán:** sửa văn bản/khuôn trong `skills/tdq-intake/SKILL.md` bước 2 của Phần A
  (có thể cả `references/lane-decision.md`, `references/interview.md` nếu liên quan).
- **Chỗ chưa rõ:**
  1. Dòng `Cỡ: <nhỏ|quick|full> · Cần: <...>` hiện tại — bỏ hẳn, hay giữ nhưng rút gọn?
  2. "Pipeline" user dùng ở đây có phải đồng nghĩa với "lane" (nhanh/chuyên sâu) trong hệ
     thống hiện tại không, hay là khái niệm khác cần thêm?
  3. "Hướng dẫn chi tiết cho người dùng dễ hiểu" cụ thể là gì — mở rộng khối hint có sẵn
     cuối câu hỏi (`_Trả lời bằng chữ cái...`), hay thêm hẳn 1-2 câu giải thích mỗi lane
     nghĩa là gì (không chỉ lý do riêng cho việc hiện tại)?

## Hỏi đáp

1. Dòng `Cỡ:`/`Cần:` xử lý thế nào?
   - A (đề xuất): Bỏ hẳn khỏi phần hiện cho user — chỉ giữ lý do bằng lời văn tự nhiên.
   - B: Giữ nguyên, chỉ thêm lý do/hướng dẫn phía sau.
   → User chọn **A** ("1A 2A 3A", 2026-08-13 17:20). Bỏ dòng `Cỡ:`/`Cần:` khỏi phần hiện
   cho user trong chat.

2. "Pipeline" có phải là "lane" hiện có không?
   - A (đề xuất): Đúng — đổi CÁCH GỌI khi trình bày với user từ "lane" sang "pipeline",
     code/state vẫn dùng `lane` nội bộ.
   - B: Không, giữ nguyên gọi "lane".
   → User chọn **A**. Lời văn hiện cho user dùng "pipeline"; code/state/tài liệu nội bộ
   (`tdq_state.py`, khoá `lane` trong `state.json`, tên biến trong skill khác) giữ nguyên
   "lane" — chỉ đổi từ hiển thị trực tiếp với user trong câu hỏi này.

3. "Hướng dẫn chi tiết cho người dùng dễ hiểu" là gì?
   - A (đề xuất): Thêm 1-2 câu giải thích ngắn NGHĨA của mỗi lane, áp dụng chung mọi lần hỏi.
   - B: Chỉ giữ/nâng cấp khối hint có sẵn.
   → User chọn **A**. Thêm câu giải thích nghĩa 2 pipeline (không riêng cho việc đang mở)
   vào khuôn dùng chung.

4. Chọn lane cho chính request này?
   - A (đề xuất): chế độ nhanh (express).
   - B: chế độ chuyên sâu (deep).
   → User chọn **B** (2026-08-13 17:21).

## Hiểu & kiến thức

### Năng lực dùng được
`skill_inventory.py` — không có skill nào lo trình bày UX/copywriting; việc này thuần sửa
văn bản 2 file skill (`tdq-intake/SKILL.md`, `references/lane-decision.md`).

### Đọc code
- Chuỗi user-facing `"Bạn muốn chạy lane nào?"` chỉ xuất hiện đúng 2 chỗ:
  `skills/tdq-intake/SKILL.md` dòng 43 và `skills/tdq-intake/references/lane-decision.md`
  dòng 48 — đây là 2 file cần sửa. Các chỗ khác dùng chữ "lane" (`phases.md`, description
  frontmatter của `tdq-intake/SKILL.md`, khoá `lane` trong `state.json`/`tdq_state.py`) là
  thuật ngữ NỘI BỘ, không hiện trực tiếp cho user trong câu hỏi — theo đúng câu 2 (2A),
  KHÔNG đổi các chỗ này, chỉ đổi lời văn hiển thị với user.
- `lane-decision.md` mục "Dòng tự nhận định" hiện quy định IN dòng `Cỡ:/Cần:` ra chat
  (dòng 7-16) — đây là chỗ cần sửa theo câu 1 (1A): đổi thành tự đánh giá NỘI BỘ, không in.
- `interview.md` có khối hint chung (`_Trả lời bằng chữ cái...`) dùng cho MỌI câu hỏi
  A/B/C, không riêng câu chọn lane — theo brief gốc, câu 3 (3A) yêu cầu giải thích nghĩa
  2 pipeline "áp dụng chung mọi lần hỏi [lane]", nghĩa là mọi lần hỏi CHỌN LANE (không
  phải mọi câu hỏi A/B/C nói chung) → đặt câu giải thích trong khuôn riêng của
  `lane-decision.md` (nơi duy nhất định nghĩa khuôn câu hỏi lane), không sửa `interview.md`
  dùng chung cho toàn bộ interview khác.

## Chốt kiến thức

- Sửa đúng 2 file: `skills/tdq-intake/SKILL.md` (bước 2, Phần A) và
  `skills/tdq-intake/references/lane-decision.md` (mục "Dòng tự nhận định" + "Khuôn câu hỏi").
- Bỏ dòng `Cỡ:/Cần:` khỏi phần in ra chat; vẫn giữ bảng quyết + tiêu chí ở
  `lane-decision.md` làm căn cứ NỘI BỘ để Claude tự chọn đề xuất A/B (không đổi cách quyết
  định, chỉ đổi cái gì được IN ra).
- Đổi chữ hiển thị "lane" → "pipeline" CHỈ trong câu hỏi trực tiếp với user
  (`"Bạn muốn chạy pipeline nào?"`); giữ nguyên "lane" trong code/state/tài liệu nội bộ.
- Thêm 1 khối giải thích ngắn, cố định, đặt ngay dưới 2 option A/B trong khuôn câu hỏi ở
  `lane-decision.md`: 1 câu nêu ý nghĩa mỗi pipeline (nhanh = làm gọn ít hỏi, hợp việc
  nhỏ/rõ; chuyên sâu = phân tích + hỏi kỹ trước, hợp việc phức tạp/rủi ro), rồi mời user
  chọn, rồi tới khối hint có sẵn (chữ cái hoặc câu tự nhiên) — không sửa `interview.md`.
- Format cụ thể (áp trong plan/spec):
  ```
  Tóm tắt: <2–3 dòng việc user muốn>
  1. Bạn muốn chạy pipeline nào?
  - A (đề xuất): chế độ nhanh (express) — <lý do gắn với chính việc này>
  - B: chế độ chuyên sâu (deep) — <lý do gắn với chính việc này>

  _chế độ nhanh (express): làm gọn, ít vòng hỏi, hợp việc nhỏ/đã rõ. chế độ chuyên sâu
  (deep): phân tích + hỏi kỹ trước khi làm, hợp việc phức tạp hoặc rủi ro cao._

  _Trả lời bằng chữ cái (vd: "A"), hoặc gõ thẳng câu tự nhiên khớp ý bạn chọn — cả hai
  đều được hiểu như nhau._
  ```

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Phân tích (đã xong) | CÓ | Xác định đúng 2 file cần sửa, chốt format mới |
| Spec | CÓ | Bắt buộc, khung bất biến |
| Plan | CÓ | Bắt buộc, khung bất biến |
| Research web | BỎ | Thuần nội bộ (copywriting UX của chính skill) |
| QC độc lập (agent) | BỎ | Việc nhỏ (đổi văn bản 2 file), tự QC đủ bằng cách đọc lại + doc_lint |

