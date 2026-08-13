# BRIEF — Interview đi từ tổng quát đến chi tiết, có bước hỏi scope

Ngày: 2026-08-14 · Slug: 2026-08-14-interview-hoi-scope

## Nguyên văn

> okay tôi muốn mở request cho việc là khi mà nhận yêu cầu thì các bước interview á thì
> sẽ đi từ tổng quát đến chi tiết, và nếu cần sẽ có hỏi người dùng về phạm vi scope để có
> thể đưa interview question hoặc làm rõ scope phù hợp. ví dụ: người dùng đưa yêu cầu làm
> một hệ thống login thì sẽ hỏi là bạn cần hẹ thống login cho request này touch những phạm
> vi nào: design, security, performance, nhiều người dùng,... hoặc bạn muốn đơn giản hay
> đầy đủ chức năng chuyên nghiệp, hoặc ví dụ người dùng làm một tính năng cho game thì ví
> dụ sẽ hỏi người dùng muốn chú trọng điều gì. nghĩa là sẽ hỏi người dùng muốn scope bao
> quanh những gì để có thể lập spec bao quát, đáp ứng đúng nhu cầu người dùng, hạn chế
> tình trạng spec bao quá thiếu hoặc dư những gì người dùng cần

### Cách hiểu đầu tiên

**Mục tiêu.** Vòng interview hiện tại nhảy thẳng vào 7 hạng mục chi tiết (phạm vi, đầu
ra, dữ liệu, lỗi & biên, hiệu năng, tương thích, vận hành). User muốn thêm một **vòng
tổng quát đứng trước**: hỏi request này bao quanh những mặt nào (design, bảo mật, hiệu
năng, đa người dùng…) và mức độ mong muốn (đơn giản hay đầy đủ chuyên nghiệp). Câu trả
lời vòng này quyết định vòng chi tiết hỏi gì — hỏi đúng mặt user quan tâm, bỏ mặt user
không cần. Kết quả: spec không thiếu, không dư.

**Phạm vi đoán.** Sửa tài liệu quy trình, không sửa code sản phẩm:
`skills/tdq-intake/references/interview.md` (khuôn vòng hỏi),
`skills/tdq-intake/references/analyze-full.md` (bước interview của lane deep),
có thể cả `skills/tdq-intake/references/quick-lane.md` và `skills/tdq-spec/`.

**Chỗ chưa rõ.**

- Vòng scope là **bắt buộc mọi request** hay chỉ khi yêu cầu đủ mơ hồ?
- Danh sách mặt scope là **cố định** (một bộ dùng chung) hay **sinh theo lĩnh vực** của
  từng request (login → bảo mật/đa người dùng; game → cảm giác chơi/hiệu năng)?
- Áp cho cả lane express hay chỉ lane deep?
- Câu trả lời scope ghi lại ở đâu, và spec có phải trích lại thành mục "ngoài phạm vi"
  để chống spec phình không?
- Hỏi mặt scope và hỏi mức độ (đơn giản ↔ đầy đủ) là **một câu** hay **hai câu** riêng?

## Hiểu & kiến thức

### Năng lực dùng được

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake / tdq-spec / tdq-plan / tdq-build | project | NỀN | khung workflow đang chạy, cũng là đối tượng bị sửa |
| mem0-memory | user | DÙNG | ghi 1 fact quy ước "vòng scope trước vòng chi tiết" |
| graphify | user | DÙNG | chạy cuối turn vì có sửa `scripts/tdq_state.py` |
| Đã xét 62 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

### Hiện trạng đọc được từ code

- `skills/tdq-intake/references/interview.md` (80 dòng) chỉ có MỘT tầng câu hỏi: 7 hạng
  mục chi tiết (phạm vi, đầu ra, dữ liệu, lỗi & biên, hiệu năng, tương thích, vận hành),
  kèm luật "tự trả lời được thì thôi". Tức agent tự quyết mặt nào đáng hỏi — đúng chỗ
  sinh ra spec thiếu hoặc dư.
- `analyze-full.md` bước 4 gọi thẳng vào interview.md, không có bước tổng quát trước.
- `quick-lane.md` bước 1 cũng gọi interview.md khi còn câu làm đổi kết quả.
- `scripts/tdq_state.py` `PHASE_GUIDE["analyze"]` có dòng checklist "Hỏi user mọi điểm
  chưa rõ" — chưa nói tới scope.
- `spec-template.md` §1 đã có dòng `NGOÀI phạm vi` nhưng không ràng buộc phải khớp với
  câu trả lời scope của user.
- Khuôn hỏi (option mỗi dòng, A là đề xuất) đã có sẵn ở interview.md và bị 3 test khoá:
  `test_gate_merge.py`, `test_user_facing_block.py`, `test_skill_shape.py`.

### Kiến thức ngoài

- ISO/IEC 25010:2023 định nghĩa 9 đặc tính chất lượng sản phẩm phần mềm: functional
  suitability, performance efficiency, compatibility, interaction capability,
  reliability, security, maintainability, flexibility, safety. Nguồn:
  <https://blog.pacificcert.com/iso-25010-software-product-quality-model>.
  Dùng làm **khung nội bộ để không sót mặt**, không phải danh sách in ra chat.

### Quyết định đã chốt

1. Vòng scope chạy **có điều kiện**, áp cho cả hai lane (user chọn 1c). Để "có điều
   kiện" không thành tuỳ hứng, phải viết ra dấu hiệu kích hoạt và bắt buộc ghi lý do khi
   BỎ vòng scope.
2. Danh sách mặt scope **sinh theo lĩnh vực** của từng request nhưng soát qua khung 9 mặt
   ISO 25010; chỉ trình ra 3–5 mặt hợp việc (user chọn 2a).
3. Vòng scope gồm **hai câu**: câu 1 chọn nhiều mặt, câu 2 hỏi **bối cảnh cụ thể** —
   không hỏi "gọn hay đầy đủ". Ví dụ user đưa: target phiên bản nào, chạy ở đâu, max CCU
   bao nhiêu, R&D hay product. Mức độ đầu tư do agent **suy ra** từ các câu bối cảnh đó
   rồi nói lại cho user biết mình suy ra gì (user chọn 3a + sửa).
4. Câu trả lời scope neo ở hai chỗ: brief thêm `### Phạm vi đã chốt`, và spec §1 phải
   liệt kê các mặt user KHÔNG chọn vào `NGOÀI phạm vi` (user chọn 4a). Không thêm luật
   `doc_lint` mới ở bản này.

### Phương án đã loại

- Bắt buộc vòng scope mọi request (1a/1b) — user không muốn hỏi thừa với việc đã rõ.
- Danh sách mặt cố định (2b) — hỏi thừa với request hẹp.
- Hỏi thẳng "gọn nhất / vừa đủ / đầy đủ chuyên nghiệp" — user thấy câu đó trừu tượng,
  trả lời không neo vào gì kiểm được; câu bối cảnh (CCU, môi trường, R&D hay product)
  vừa dễ trả lời vừa dùng lại được ở spec §5 ràng buộc.
- Thêm rule `doc_lint` kiểm "NGOÀI phạm vi" (4c) — để dành, chưa cần ngay.

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ (đã xong) | 1 truy vấn lấy khung ISO 25010, không cần thêm |
| Interview | CÓ (đã xong) | 4 câu, user đã chốt 1c 2a 3a-sửa 4a |
| Spec + plan | CÓ | khung bất biến |
| Chia subagent | BỎ | 1 nhóm file tài liệu liên quan chặt, chia ra dễ lệch giọng văn |
| QC độc lập (agent) | BỎ | DoD kiểm được bằng lệnh (`pytest`, `doc_lint`, `grep`) |
| Report | CÓ | khung bất biến |

## Hỏi đáp

**Vòng 1 — 2026-08-14 01:22**

1. Vòng scope chạy khi nào? A: bắt buộc ở deep · B: bắt buộc cả hai lane · C: có điều
   kiện ở cả hai lane → user chọn **C**.
2. Danh sách mặt scope lấy từ đâu? A: sinh theo lĩnh vực trên khung ISO 25010 cố định ·
   B: cố định hoàn toàn · C: sinh tự do → user chọn **A**.
3. Hỏi mặt và hỏi mức độ là một câu hay hai? A: hai câu · B: gộp · C: chỉ hỏi mặt →
   user chọn **A nhưng sửa câu 2**: nguyên văn *"thay vì hỏi như mức độ gọn nhất vừa đủ
   chuyên nghiệp thì sẽ hỏi ví dụ bạn làm server này target ver này chạy ở đâu, max ccu
   là bao nhiêu, r&d hay product, và những câu tương tự để từ đó suy ra nên tổ chức theo
   mức độ nào"*.
4. Neo câu trả lời scope ở đâu? A: brief + spec §1 · B: chỉ `## Hỏi đáp` · C: A + rule
   doc_lint → user chọn **A**.
5. Bổ sung gì không? → **A: không, đủ rồi**.
