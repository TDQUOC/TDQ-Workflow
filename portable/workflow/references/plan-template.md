# Khuôn plan

Copy nguyên khối vào `docs/tdq/plan/<slug>.md` rồi điền.

```markdown
# PLAN — <tên việc>

Ngày: YYYY-MM-DD · Spec: ../spec/<slug>.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — <lý do 1–2 câu> (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: CHỜ DUYỆT

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — <tên phase>
- [ ] **T1.1** (n3) <việc cụ thể> — Test: <lệnh hoặc tiêu chí pass>
- [ ] **T1.2** (n5) <việc cụ thể> — Test: <...>

**Xong P1 khi**: <điều kiện đo được>

## P2 — <tên phase>
- [ ] **T2.1** (n8) <...> — Test: <...>

## Khuôn khối hợp đồng skill/năng lực (đặt NGAY DƯỚI dòng task dùng năng lực đó, ≤6 dòng)
- [ ] **T<x.y>** <việc của task> — Test: <...>
  - Dùng: `<tên skill/năng lực>`
- [ ] **T<x.z>** <task mà năng lực cần công cụ ngoài (search/API) lúc chạy> — Test: <...>
  - Dùng: `<tên skill/năng lực>` (mcp)
  - Để: <việc cụ thể lo trong task này>, nạp/đọc năng lực đó TRƯỚC bước đỏ.
  - Ra: <artifact phải tồn tại sau task, có đường dẫn>
  - Kiểm: <một lệnh chạy được, PASS đo được>
  - Không dùng cho: <việc kề bên mà năng lực này KHÔNG được lan sang>

Luật nhãn `(mcp)` — BẮT BUỘC ghi ngay khi lập plan: năng lực nào cần công cụ ngoài lúc
chạy (gọi search/API, ví dụ tavily/notion) → dòng `Dùng:` phải kết thúc bằng nhãn
` (mcp)` NGOÀI backtick, cuối dòng. Nhãn này đánh dấu task buộc bạn tự làm, không
giao agent phụ thiếu công cụ đó.

## Px — Log & test bắt buộc
Phase này bắt buộc **chỉ khi việc này có runtime** — tức có ít nhất một task tạo hoặc sửa
file mã nguồn chạy được. Không có runtime (chỉ sửa tài liệu, khuôn mẫu, cấu hình) → bỏ
task log, giữ task test, và ghi đúng một dòng `Log: BỎ — <lý do một câu>`.

- [ ] **Tx.1** Log service bật mặc định (timestamp, mức log, tắt được qua config) — Test: <...>
- [ ] **Tx.2** Unit test cho từng thành phần, chạy bằng một lệnh — Test: <lệnh>

## Definition of Done
Trỏ về §6 của spec. Liệt kê lại từng hạng mục QC + lệnh kiểm.
```

## Điểm độ phức tạp `(nN)`

Đặt **ngay sau mã task**, trước phần việc: `- [ ] **T2.1** (n5) việc — Test: ...`.
Đây là độ phức tạp **tương đối** 1–10, không phải số phút.

Thang neo mốc:

| Điểm | Mốc tham chiếu |
|---|---|
| 1 | sửa một dòng văn bản, đổi một hằng số |
| 3 | thêm một mục tài liệu, sửa một nhánh nhỏ có sẵn test |
| 5 | một hàm mới kèm test (mốc giữa — phân vân thì chấm 5) |
| 8 | đổi hành vi một module, kéo theo sửa nhiều test |
| 10 | đổi công thức/hợp đồng dữ liệu lõi, lan sang nhiều hàm |

Luật:
- Chấm ngay lúc viết task, không chấm bù sau.
- Phân vân giữa hai mốc → lấy mốc thấp hơn; hoàn toàn không biết → 5.
- Điểm là **tuỳ chọn**: thiếu `(nN)` thì bộ đọc coi như 5, plan cũ vẫn chạy y nguyên.
- Điểm KHÔNG đổi luật tick `[ ] [~] [x]` và không phải cam kết thời gian.

## Dòng `Mode thực thi`

- Phải nằm **một dòng riêng**, không ghép vào dòng header khác.
- Đây chỉ là **đề xuất**. User duyệt plan xong, phase `mode` mới hỏi chọn `main` hay
  `subagent`; mode ghi vào state là mode user NÓI, không tự lấy đề xuất làm chốt.
  Câu duyệt đã kèm sẵn mode thì bỏ qua cổng đó, vào thẳng implement.

## Kiểm trước khi trình

- Mỗi đầu ra trong spec §2 ánh xạ tới ≥ 1 task.
- Mỗi task có đúng một việc và một cách kiểm đo được — không có task kiểu "hoàn thiện X".
- Task đầu của mỗi phase dựng được đường đi red → green sớm.
- Không task nào phụ thuộc task nằm sau nó.
