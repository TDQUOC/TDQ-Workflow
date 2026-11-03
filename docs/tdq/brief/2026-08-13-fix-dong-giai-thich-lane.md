# Brief — Fix dòng giải thích pipeline gây rối khi đọc lại

## Nguyên văn

Nguyên văn user (kèm ảnh chụp màn hình chính transcript turn trước, khoanh đỏ khối giải
thích 2 pipeline trong "Tóm tắt spec" vừa trình):
> "mở request fix issue sau. rõ ràng đã chọn pipeline rồi mà ở spec vẫn thấy dòng '_chế độ
> nhanh (express): làm gọn, ít vòng hỏi, hợp việc nhỏ/đã rõ. chế độ chuyên sâu (deep): phân
> tích + hỏi kỹ trước khi làm, hợp việc phức tạp hoặc rủi ro cao._' nó khiến cho việc đọc
> dễ bị rối"

Cách hiểu đầu tiên:
- **Mục tiêu:** việc vừa làm ở request `2026-08-13-ux-cau-hoi-lane` (thêm khối giải thích
  ngắn nghĩa 2 pipeline ngay dưới option A/B) đang gây tác dụng phụ — khối giải thích đó
  vẫn còn "đứng" trong nội dung khi đọc lại transcript SAU khi user đã chọn xong, làm
  người đọc khó phân biệt "đây là câu hỏi đang chờ" hay "đã xong rồi, đây chỉ là tài
  liệu". User muốn sửa cho gọn/rõ hơn.
- **Phạm vi đoán:** có thể liên quan đến 1 trong 2 hướng — (a) chỉnh lại chính khuôn câu
  hỏi ở `lane-decision.md` (rút gọn/đổi vị trí khối giải thích), hoặc (b) vấn đề chỉ nằm ở
  cách Claude trình bày "Tóm tắt spec" trong chat (lặp lại nguyên khối format mẫu như một
  đoạn code block, khiến nó trông giống câu hỏi sống) — không phải lỗi của khuôn skill.
- **Chỗ chưa rõ:**
  1. Vấn đề nằm ở khuôn câu hỏi thật (`lane-decision.md`) hay ở cách trình bày "Tóm tắt
     spec" (khi Claude dẫn lại format mới làm ví dụ trong phần tóm tắt duyệt)?
  2. Nếu là khuôn câu hỏi thật: sửa thế nào — bỏ hẳn khối giải thích, rút ngắn còn 1 dòng,
     hay chỉ hiện khi cần (ví dụ chỉ hiện cho user mới)?
  3. Việc này có tính là "issue" của chính feature vừa build (tức mở request fix nối tiếp
     `2026-08-13-ux-cau-hoi-lane`) hay là một góp ý riêng về cách Claude trình bày tóm tắt
     (nằm ngoài phạm vi sửa code/skill)?

## Hỏi đáp

1. Cách sửa tóm tắt khi đầu ra là 1 khuôn văn bản?
   - A (đề xuất): Gắn nhãn rõ "(khuôn mẫu — áp dụng cho các lần hỏi sau, không phải câu
     hỏi của turn này)" ngay trước đoạn trích, để không lẫn với câu hỏi sống.
   - B: Không trích nguyên khối — chỉ mô tả bằng lời.
   - C: Rút gọn phần giải thích ngay trong khuôn thật ở `lane-decision.md`.
   → User chọn **A** ("1A 2A", 2026-08-13 17:40). Khi tóm tắt spec/plan cần trích khuôn
   mẫu có sẵn (như A/B kèm giải thích), gắn nhãn rõ đây là mẫu/khuôn — không phải câu hỏi
   sống của turn hiện tại.

2. Ghi quy ước sửa ở đâu?
   - A (đề xuất): `skills/tdq-spec/SKILL.md` bước 4 (và `tdq-plan/SKILL.md` bước tương
     ứng nếu có bước tóm tắt tương tự).
   - B: `tdq-conventions/SKILL.md` làm quy ước chung mọi tóm tắt.
   → User chọn **A**. Sửa cả 2 file: `tdq-spec/SKILL.md` bước 4 và `tdq-plan/SKILL.md`
   bước 5 (đã đọc code, xác nhận cả 2 đều có bước "Trình bày & DỪNG" tóm tắt tương tự —
   `tdq-plan/SKILL.md` dòng 61 "tóm tắt plan ≤ 10 dòng").

## Hiểu & kiến thức

### Năng lực dùng được
`skill_inventory.py` — không có skill nào lo trình bày UX/copywriting; việc này thuần sửa
khuôn văn bản trong `skills/tdq-intake/references/lane-decision.md`.

### Đọc code
- **Sửa lại kết luận trước (SAI):** đã đoán vấn đề nằm ở khuôn câu hỏi lane thật
  (`lane-decision.md`) vì thấy khối giải thích xuất hiện y hệt ở câu hỏi lane turn trước.
  User sửa lại: vấn đề KHÔNG phải ở đó — mà ở chỗ, khi request đã QUA khỏi bước chọn lane,
  sang tới spec, "Tóm tắt spec" Claude trình trong chat vẫn dẫn lại NGUYÊN khối format có
  cả giải thích 2 lane (express lẫn deep) — dù lane của request này đã chốt xong từ lâu.
  Đọc lại chat turn viết spec cho `ux-cau-hoi-lane` xác nhận: mục "Format mới (đã chốt
  trong brief)" trong tóm tắt spec có chép nguyên khối mẫu (gồm cả 2 dòng giải thích
  express/deep) làm ví dụ minh hoạ đầu ra — đây là nội dung Claude TỰ chọn đưa vào tóm tắt
  (không có skill nào bắt buộc chép nguyên văn thế này), và nó gây cảm giác "lại hỏi chọn
  lane lần nữa" dù không phải.
- `skills/tdq-spec/SKILL.md` bước 4 chỉ nói "tóm tắt spec ≤ 50 dòng (mục tiêu, đầu ra,
  DoD, rủi ro chính)" — không có hướng dẫn cụ thể về cách trích dẫn khuôn/mẫu UI có sẵn
  trong nội dung đầu ra (trường hợp đầu ra CHÍNH LÀ một khuôn văn bản, như request
  `ux-cau-hoi-lane`). Đây là khoảng trống cần bổ sung.
- `skills/tdq-plan/SKILL.md` bước 5 (dòng 61) có cùng dạng bước "Trình bày & DỪNG" — tóm
  tắt plan ≤10 dòng — cùng khoảng trống, cần bổ sung tương tự cho nhất quán.

## Chốt kiến thức

- Sửa đúng 2 file: `skills/tdq-spec/SKILL.md` bước 4 và `skills/tdq-plan/SKILL.md` bước 5
  — thêm 1 câu quy ước: khi tóm tắt (spec/plan) cần trích nguyên khối mẫu/khuôn có sẵn
  (ví dụ khuôn câu hỏi A/B kèm giải thích), phải gắn nhãn rõ ngay trước đoạn trích, dạng
  "(khuôn mẫu — áp dụng cho các lần hỏi sau, không phải câu hỏi của turn này)", để người
  đọc lại transcript không nhầm là đang hỏi lại.
- Không sửa `lane-decision.md` hay bất kỳ khuôn câu hỏi thật nào khác — vấn đề nằm ở cách
  Claude tóm tắt, không phải ở nội dung khuôn.
- Không sửa `tdq-conventions/SKILL.md` — user chọn 2A, giới hạn phạm vi đúng 2 file spec
  + plan, không mở rộng thành quy ước chung cho report/mọi tóm tắt khác.

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Phân tích (đã xong) | CÓ | Sửa lại nhận định sai ban đầu, xác định đúng 2 file cần sửa |
| Spec | CÓ | Bắt buộc, khung bất biến |
| Plan | CÓ | Bắt buộc, khung bất biến |
| Research web | BỎ | Thuần nội bộ (quy ước trình bày của chính skill) |
| QC độc lập (agent) | BỎ | Việc nhỏ (thêm 1 câu quy ước vào 2 file), tự QC đủ bằng đọc lại + doc_lint |
