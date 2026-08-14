# Vòng scope — tầng tổng quát của interview

Vòng này chạy TRƯỚC vòng câu hỏi chi tiết ở [interview.md](interview.md). Mục đích: biết
request bao quanh những mặt nào và bối cảnh thật ra sao, để vòng chi tiết chỉ hỏi trong
đúng phần user cần. Spec nhờ đó không thiếu mặt quan trọng, cũng không phình ra mặt user
không cần.

## 1. Khi nào chạy

Vòng scope **có điều kiện**, áp cho cả chế độ nhanh (express) lẫn chế độ chuyên sâu (deep).
Chạy khi yêu cầu của user thoả **ít nhất một** dấu hiệu dưới đây:

1. Yêu cầu gọi tên cả một hệ thống hay tính năng ("làm hệ thống login", "thêm tính năng
   X cho game"), không trỏ vào một hành vi hay một file cụ thể.
2. Soát khung 9 mặt ở mục 2 thấy từ **2 mặt trở lên** có thể áp dụng mà yêu cầu không nói
   gì về chúng.
3. Yêu cầu có từ mở về quy mô hay chất lượng mà không kèm số: "nhanh", "an toàn",
   "nhiều người dùng", "chuyên nghiệp".
4. Việc chạm tới dữ liệu người dùng, tiền, hoặc API công khai.

Không dấu hiệu nào → BỎ vòng scope, đi thẳng vòng chi tiết. Khi BỎ, brief phải có đúng
một dòng, không được im lặng:

```
Vòng scope: BỎ — <lý do một câu, nói rõ vì sao mọi mặt còn lại suy ra được từ code>
```

Dòng lý do bắt buộc này là hàng rào: "có điều kiện" nghĩa là có tiêu chí, không phải tuỳ
hứng bỏ cho nhanh.

## 2. Câu 1 — request này bao quanh những mặt nào

**Khung soát nội bộ (không in ra chat).** Đi hết 9 mặt chất lượng của ISO/IEC 25010:2023
để không sót: chức năng · hiệu năng · tương thích · trải nghiệm người dùng · độ tin cậy ·
bảo mật · bảo trì · Flexibility — mở rộng, đa nền tảng · an toàn. Khung này chỉ để bạn
không bỏ quên mặt nào; user không cần đọc nó.

**Phần in ra chat.** Chọn **3–5 mặt** thật sự hợp lĩnh vực của request rồi hỏi theo đúng
khuôn option của [interview.md](interview.md) — mỗi mặt một dòng, nhãn chữ HOA, hệ quả
nối bằng ` — `. Hệ quả viết theo dạng "chọn mặt này thì spec sẽ có <mục gì>", để user
thấy được cái giá của từng lựa chọn:

```
<số>. Request này bạn muốn bao quanh những mặt nào? (chọn nhiều được)
- A (đề xuất): <mặt> — spec sẽ có <mục/đầu ra cụ thể>
- B: <mặt> — spec sẽ có <mục/đầu ra cụ thể>
- C: <mặt> — spec sẽ có <mục/đầu ra cụ thể>
- D: chỉ cần chạy được — bỏ hết các mặt trên, spec chỉ lo đúng luồng chính
```

Luật của câu này:

- Cho chọn nhiều: user trả lời được kiểu "A, C" hoặc "A C D"; nói rõ điều đó trong khối.
- Option cuối luôn là "chỉ cần chạy được" — user cần lối thoát khỏi mọi mặt phụ.
- Không quá 5 mặt. Thấy 6 mặt trở lên đều hợp thì gộp mặt gần nhau, đừng kéo dài danh sách.
- Mặt nào yêu cầu đã nói rõ rồi thì KHÔNG đưa vào option, ghi thẳng là đã chốt.

## 3. Câu 2 — bối cảnh bằng số

**CẤM hỏi mức độ trừu tượng.** Không hỏi "bạn muốn gọn nhất, vừa đủ, hay đầy đủ chuyên
nghiệp". Câu đó bắt user tự quy đổi thứ họ chưa biết, và câu trả lời không neo vào gì
kiểm được. Thay bằng câu bối cảnh cụ thể — user trả lời dễ, và con số đó dùng lại được ở
spec §5 ràng buộc.

Bộ mẫu 5 nhóm, chọn ra **tối đa 4 câu** hợp lĩnh vực:

| Nhóm | Hỏi cái gì | Ví dụ option |
|---|---|---|
| Môi trường & bản target | chạy ở đâu, phiên bản nào | máy cá nhân · VPS 1 node · cloud nhiều node |
| Quy mô đồng thời | max CCU, RPS, số bản ghi | < 100 CCU · 100–10.000 · > 10.000 |
| Giai đoạn | R&D thử nghiệm hay product chạy thật | prototype · beta nội bộ · product có người dùng thật |
| Vòng đời & bảo trì | sống bao lâu, ai sửa sau này | dùng một lần · một người giữ · cả nhóm giữ |
| Ràng buộc nền tảng | thiết bị, OS, engine, thư viện bắt buộc | không ràng buộc · một nền tảng · nhiều nền tảng |

Luật của câu này:

- Mỗi câu vẫn theo khuôn option A/B/C, các mức là **con số hoặc mốc cụ thể**.
- Mỗi câu thêm một option cuối "tôi tự gõ số" cho user điền thẳng.
- Gộp câu 1 và các câu bối cảnh vào **một khối chat duy nhất**, đánh số liên tục.
- Nhóm nào yêu cầu đã trả lời sẵn thì bỏ, đừng hỏi lại thứ user vừa nói.

## 4. Suy ra mức đầu tư

Mức đầu tư do **bạn suy ra** từ câu trả lời bối cảnh, không hỏi thẳng user. Bảng ánh xạ:

| Bối cảnh | Mức đầu tư | Hệ quả lên spec/plan |
|---|---|---|
| Prototype/R&D, quy mô nhỏ, một người giữ | lõi | chỉ luồng chính, 0 hạng mục hiệu năng, DoD ≤ 5 dòng |
| Beta nội bộ, quy mô vừa, cả nhóm giữ | vừa | thêm test biên và đường lỗi vào DoD |
| Product thật, quy mô lớn | đầy đủ | hiệu năng và độ tin cậy thành hạng mục QC riêng, có ngưỡng số |
| Chạm tiền, dữ liệu người dùng, API công khai | đầy đủ | bảo mật vào DoD kể cả khi user không chọn mặt đó |

Suy xong phải in đúng một dòng, đặt kèm khối câu hỏi của vòng chi tiết:

```
Tôi hiểu là: <mức đầu tư> vì <bối cảnh user vừa nói>
```

Dòng này để user cãi được ngay nếu bạn suy sai. Nó **không** phải một cổng duyệt mới —
không chờ user xác nhận riêng, không thêm phase.

## 5. Ghi lại

Brief mục `## Hiểu & kiến thức` thêm `### Phạm vi đã chốt`, đúng 4 dòng:

```
- Mặt CHỌN: <danh sách>
- Mặt LOẠI: <danh sách — chép nguyên sang spec §1 NGOÀI phạm vi>
- Bối cảnh: <các con số user đưa>
- Mức đầu tư suy ra: <lõi|vừa|đầy đủ> — vì <bối cảnh>
```

Sang phase spec, dòng "Mặt LOẠI" chép nguyên vào §1 mục `NGOÀI phạm vi`. Đó là chỗ đối
chiếu khi spec bắt đầu phình: mặt nào không có trong "Mặt CHỌN" mà tự mọc ra trong spec
là dấu hiệu đang làm dư.
