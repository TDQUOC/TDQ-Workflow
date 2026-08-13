# Phase `no_state` / `analyze` / chế độ nhanh — Intake

## Tầng nhỏ — trả lời/sửa luôn, không mở request

Vào tầng `nhỏ` khi **cả 4** điều kiện đúng:

1. Không đổi hành vi sản phẩm, hoặc chỉ đổi đúng một chỗ hiển nhiên (typo, hằng số,
   chuỗi hiển thị, số phiên bản).
2. Không thêm và không xoá file mã nguồn.
3. Không đụng hook (nếu harness có), state, gate duyệt.
4. Xong trong một turn, không có chỗ nào cần user chốt.

Ở tầng này: trả lời hoặc sửa luôn. Không mở request, không `init` state, không plan,
không QC. Có đổi repo thì vẫn append working log như mọi turn khác.

**Luật thoát (bắt buộc).** Giữa chừng vi phạm bất kỳ điều kiện nào → DỪNG tay, nói rõ
điều kiện nào vỡ, rồi mở request bình thường từ Phần A. Cấm làm tiếp ở tầng `nhỏ`.

## Phần A — Mở request (phase `no_state`)

Định nghĩa "yêu cầu mới": MỌI prompt của user khi KHÔNG có request mở — request mở
= có `active_request` VÀ `phase != idle`. Khi phase ≠ idle, message của user thuộc
request đang chạy (duyệt, góp ý, trả lời interview), không mở request lồng.

1. **Ghi lại yêu cầu.** Tạo `docs/tdq/brief/<slug>.md` với slug
   `YYYY-MM-DD-<kebab ≤5 từ, không dấu>`. Brief là file DUY NHẤT của phase intake +
   analyze, đúng 3 mục: `## Nguyên văn` (nguyên văn yêu cầu user + cách hiểu đầu tiên
   của bạn: mục tiêu, phạm vi đoán, chỗ chưa rõ), `## Hiểu & kiến thức`, `## Hỏi đáp`.
   Ở bước này chỉ viết mục đầu; hai mục sau để trống, Phần B điền.

2. **Đề xuất lane rồi HỎI.** Trong chat: 2–3 dòng tóm tắt việc user muốn. Rồi đúng 1
   dòng tự nhận định cỡ, dạng
   `Cỡ: <nhỏ|quick|full> · Cần: <research | interview | subagent | QC độc lập | skill ngoài | không>`
   — cột `Cần` chỉ liệt kê thứ CÓ THỂ bỏ, thứ luôn chạy thì không liệt kê. Rồi 1 dòng đề
   xuất lane kèm lý do cho CHÍNH việc này. Rồi câu hỏi "Bạn muốn chạy lane nào?" theo
   đúng khuôn hỏi ở mục "Vòng interview — cách hỏi" bên dưới, phương án đề xuất luôn
   đứng ở A: `- A (đề xuất): chế độ nhanh (express) — <lý do>` xuống dòng
   `- B: chế độ chuyên sâu (deep) — <lý do>`.
   **DỪNG chờ user trả lời.** Không tự chọn lane.

3. **Init state** ngay khi user chốt lane:
   ```
   python3 scripts/tdq_state.py init <slug> <quick|full>
   ```
   Lệnh này **xoá sạch** state cũ. Nếu đang có request khác còn dở → nói rõ slug và
   phase sẽ mất, **hỏi user trước** rồi mới chạy.

4. **Rẽ nhánh:**
   - `full` → `... set phase=analyze`, làm tiếp Phần B ngay trong turn này.
   - `quick` → làm Phần C, không qua Phần B.

Xong khi: `state.json` có `active_request` và `lane` đúng thứ user chọn.
Bước kế tiếp: Phần B (chế độ chuyên sâu (deep)) hoặc Phần C (chế độ nhanh (express)).

## Phần B — Phân tích (phase `analyze`, chỉ chế độ chuyên sâu (deep))

Chỉ nạp khi chế độ chuyên sâu (deep) — chế độ nhanh không cần mục này. Đóng vai chuyên gia đúng lĩnh vực,
mục tiêu rời phase này với ZERO chỗ đoán. Làm đủ 6 bước:

1. **Kiểm kê năng lực (B0).** Harness không có skill system riêng thì bỏ qua bước này;
   có công cụ/tài liệu tương đương skill (ví dụ AGENTS.md phụ, tool riêng) thì liệt kê 1
   dòng mỗi thứ vào brief mục `## Hiểu & kiến thức` → `### Năng lực dùng được`. Phân
   vân → DÙNG.

2. **Đọc code.** Tìm hết chỗ yêu cầu này chạm tới: entry point, luồng dữ liệu, config,
   test. Ghi lại phiên bản/framework đang dùng.

3. **Research nhiều hướng.** 2–4 truy vấn khác góc nhìn qua công cụ search của harness
   (nguồn chính trước, dự phòng chỉ khi nguồn chính lỗi). Ghi vào
   `docs/tdq/research/<slug>.md` (truy vấn → nguồn → điều rút ra). Bỏ qua chỉ khi việc
   thuần nội bộ, không có ẩn số bên ngoài.

4. **Vòng interview.** Liệt kê MỌI câu hỏi làm thay đổi kết quả (phạm vi, UX, dữ liệu,
   lỗi, hiệu năng, tương thích). Cách hỏi ở mục "Vòng interview — cách hỏi" ngay dưới.
   Ghi hỏi–đáp vào brief mục `## Hỏi đáp`. **Lặp** đến khi không còn câu hỏi
   nào làm đổi kết quả — nhiều vòng là bình thường. Không lấp chỗ trống bằng phỏng đoán.

5. **Chốt kiến thức.** Viết vào brief mục `## Hiểu & kiến thức`: quyết định đã chốt,
   ràng buộc, cách tiếp cận đã chọn + lý do, phương án đã loại + lý do, nguồn.

5b. **Quyết lộ trình.** Thêm `### Lộ trình` vào mục đó: bảng `Bước/phase | CÓ-BỎ |
    Vì sao` cho từng bước còn lại (research thêm, QC độc lập, review sâu, chia
    sub-agent…). Khung bất biến không được bỏ: phân tích → spec/plan → implement →
    report. Chỉ cắt bước THỪA cho chính việc này, nêu lý do; phân vân → GIỮ. Lộ trình
    này chép nguyên sang spec §1b và user duyệt spec là duyệt luôn nó.

6. **Kiểm cổng** trước khi đi tiếp:
   - Phạm vi cuối đã rõ chưa: làm ra gì, có gì mới, output cụ thể là gì?
   - Có cần model / download / cài đặt gì không?
   - Phạm vi QC/test/validate đã có chưa?
   Thiếu bất kỳ mục nào → quay lại bước 4.

Xong khi: `brief/<slug>.md` đủ 3 mục (có `### Lộ trình`) và cả 3 câu hỏi kiểm cổng đều
trả lời được.
Bước kế tiếp: `python3 scripts/tdq_state.py set phase=spec` rồi sang
[02-spec.md](02-spec.md) — cùng turn nếu interview đã xong, còn phải hỏi user thì
trình câu hỏi và dừng.

## Vòng interview — cách hỏi

Mục tiêu: không còn câu hỏi nào mà câu trả lời khác nhau sẽ dẫn tới sản phẩm khác nhau.
Chỉ hỏi câu **làm đổi kết quả** — phạm vi, đầu ra, dữ liệu, lỗi & biên, hiệu năng & quy
mô, tương thích, vận hành. Không hỏi thứ đọc code là biết, thứ đã có trong `## Nguyên
văn`, hay thuần sở thích trình bày.

Mỗi câu hỏi kèm **2–4 phương án cụ thể**. **Luôn hỏi bằng danh sách trong chat** — không
dùng công cụ hỏi trắc nghiệm rời (nếu harness có), để user đọc được toàn bộ phương án
cùng lúc và trả lời mở. Khuôn bắt buộc, dán đúng dạng này:

```
<số>. <Câu hỏi>
- A (đề xuất): <phương án> — <hệ quả 1 dòng>
- B: <phương án> — <hệ quả 1 dòng>
- C: <phương án> — <hệ quả 1 dòng>
```

Luật khuôn: mỗi option đúng **1 dòng riêng**, mở đầu bằng `- ` rồi nhãn chữ HOA
`A`/`B`/`C`/`D`; **cấm gộp** nhiều option vào một dòng hay nhét vào đoạn văn dạng
`(a) … · (b) …`; phương án bạn khuyên luôn là **A** mang nhãn `(đề xuất)`, các option
khác không có nhãn; sau nhãn là dấu `:` rồi nội dung, hệ quả nối bằng ` — ` cùng dòng;
nhiều câu hỏi trong một vòng → đánh số câu `1.`, `2.` mỗi câu một bảng option riêng.
Câu hỏi chốt lane, chốt mode, hỏi commit cũng theo đúng khuôn này.

Câu chốt vòng có điều kiện — chỉ ghi khi vòng đó có ít nhất một câu hỏi:
```
<số>. Bạn muốn bổ sung thêm gì không?
- A (đề xuất): Không, đủ rồi — làm tiếp đi.
- B: Có — tôi nói thêm.
```
Vòng không có câu hỏi nào thì không dựng vòng interview rỗng chỉ để hỏi câu này.

Ghi mọi hỏi–đáp vào brief mục `## Hỏi đáp`: câu hỏi, các phương án, user chọn gì
(nguyên văn), ngày giờ. Dừng khi đọc lại danh sách câu hỏi mà mọi câu còn lại đều
**không** làm đổi sản phẩm; còn một câu làm đổi → hỏi tiếp vòng nữa. Cấm chuyển sang
viết spec khi còn chỗ phải đoán.

## Phần C — Chế độ nhanh (express)

Chế độ nhanh = rút gọn, KHÔNG cắt bước tư duy: [references/quick-lane.md](references/quick-lane.md).
