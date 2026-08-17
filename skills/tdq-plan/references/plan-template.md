# Khuôn plan

Copy nguyên khối vào `docs/tdq/plan/<slug>.md` rồi điền.

```markdown
# PLAN — <tên việc>

Ngày: YYYY-MM-DD · Spec: ../spec/<slug>.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
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
- [ ] **T1.1** (e6m) <việc cụ thể> — Test: <lệnh hoặc tiêu chí pass>
- [ ] **T1.2** (e12m) <việc cụ thể> — Test: <...>

**Xong P1 khi**: <điều kiện đo được>

## P2 — <tên phase>
- [ ] **T2.1** (e20m) <...> — Test: <...>

## Dòng `Chạm:` (đặt NGAY DƯỚI dòng task sửa file mã nguồn ĐÃ CÓ)
- [ ] **T<x.y>** <việc sửa hàm/file sẵn có> — Test: <...>
  - Chạm: <hàm/file bị sửa> → <node bị ảnh hưởng> (nguồn: `graphify affected "<X>" --depth 2`)

Không node nào phụ thuộc → ghi `Chạm: <X> → không node nào phụ thuộc`. Task tạo file
mới hay chỉ sửa tài liệu thì bỏ dòng này. Node nằm trong mục `## Hub` của
`docs/kien-truc.md` → task phải thêm một dòng DoD kiểm hồi quy riêng cho node ấy.

## Khuôn khối hợp đồng skill (đặt NGAY DƯỚI dòng task dùng skill đó, ≤6 dòng)
- [ ] **T<x.y>** <việc của task> — Test: <...>
  - Dùng: `<tên skill>`
- [ ] **T<x.z>** <task mà skill cần MCP tool> — Test: <...>
  - Dùng: `<tên skill>` (mcp)
  - Để: <việc cụ thể skill lo trong task này>, nạp skill TRƯỚC bước đỏ. Agent ngoài
    không có skill system: đọc `<đường dẫn>/SKILL.md` rồi làm theo.
  - Ra: <artifact phải tồn tại sau task, có đường dẫn>
  - Kiểm: <một lệnh chạy được, PASS đo được>
  - Không dùng cho: <việc kề bên mà skill này KHÔNG được lan sang>

Luật nhãn `(mcp)` — BẮT BUỘC ghi ngay khi lập plan: skill nào cần MCP tool lúc
chạy (gọi server MCP, ví dụ tavily/notion) → dòng `Dùng:` phải kết thúc bằng nhãn
` (mcp)` NGOÀI backtick, cuối dòng, đúng cú pháp spec §1. `split-plan` đọc nhãn
này để biết task nào buộc phải do Claude tự làm, không giao sub-agent thiếu MCP.

## Px — Log & test bắt buộc
Phase này bắt buộc **chỉ khi việc này có runtime** — tức có ít nhất một task tạo hoặc sửa
file mã nguồn chạy được. Không có runtime (chỉ sửa tài liệu, khuôn mẫu, cấu hình) → bỏ
task log, giữ task test, và ghi đúng một dòng `Log: BỎ — <lý do một câu>`.

- [ ] **Tx.1** Log service bật mặc định (timestamp, mức log, tắt được qua config) — Test: <...>
- [ ] **Tx.2** Unit test cho từng thành phần, chạy bằng một lệnh — Test: <lệnh>

## Definition of Done
Trỏ về §6 của spec. Liệt kê lại từng hạng mục QC + lệnh kiểm.
```

## Ước tính phút `(eNm)`

Đặt **ngay sau mã task**, trước phần việc: `- [ ] **T2.1** (e12m) việc — Test: ...`.
`eNm` = số **phút** Claude ước tính mình cần để tự THỰC THI xong task ấy (thời gian agent
chạy, không phải thời gian người chờ). Đơn vị luôn là phút, số nguyên 1–999, không viết
`1h` hay `0.5m`. ETA của cả plan = tổng `eNm` các task chưa xong.

Luật:
- Chấm ngay lúc viết task, không chấm bù sau.
- Ước tính thời gian LÀM, không tính thời gian chờ user duyệt hay interview.
- Phân vân → chấm số mình thật sự tin, đừng đệm thêm cho an toàn.
- `eNm` là **tuỳ chọn**: thiếu thì bỏ qua task đó khi cộng ETA, không chặn plan chạy.
- `eNm` KHÔNG đổi luật tick `[ ] [~] [x]` và không phải cam kết thời gian với user.

## Dòng `Mode thực thi`

- Phải nằm **một dòng riêng**, không ghép vào dòng header khác — công cụ đọc dòng này.
- Giá trị ghi ở đây là **định danh máy**: `main` hoặc `subagent`. Nhãn user đọc thấy ở
  cổng `mode` là "làm trực tiếp (inline implement)" và "giao trợ lý (sub-agent
  implement)" — xem [mode-gate.md](mode-gate.md).
- Đây chỉ là **đề xuất** của Claude. User duyệt plan xong, phase `mode` mới hỏi chọn;
  mode ghi vào state là mode user NÓI, không tự lấy đề xuất làm chốt. Câu duyệt đã kèm
  sẵn mode thì bỏ qua cổng đó, vào thẳng implement.

## Kiểm trước khi trình

- Mỗi đầu ra trong spec §2 ánh xạ tới ≥ 1 task.
- Mỗi task có đúng một việc và một cách kiểm đo được — không có task kiểu "hoàn thiện X".
- Task đầu của mỗi phase dựng được đường đi red → green sớm.
- Không task nào phụ thuộc task nằm sau nó.
