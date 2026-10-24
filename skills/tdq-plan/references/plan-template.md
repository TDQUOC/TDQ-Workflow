# The plan shape
<!-- muc-luc-dong:
  The minute estimate `(eNm)`=115
-->

Copy the whole block into `docs/tdq/plan/<slug>.md` and fill it in. File em:
[plan-template-co-che.md](plan-template-co-che.md) (cơ chế ba mục có điều kiện) và
[plan-template-huong-dan.md](plan-template-huong-dan.md) (`eNm`, `Mode thực thi`, tự soát).

<!-- i18n-allow: plan template written in the default document language -->
```markdown
# PLAN — <tên việc>

Ngày: YYYY-MM-DD · Spec: ../spec/<slug>.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: <main|subagent|codex> — <lý do 1–2 câu> (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: CHỜ DUYỆT

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- Thiết kế Trước vs Sau (khi bổ sung hoặc refactor)
- P1 — <tên phase>
- P2 — <tên phase>
- Dòng `Chạm:` (đặt NGAY DƯỚI mọi task TẠO hoặc SỬA file mã nguồn)
- Luật file nóng (một file, nhiều task chạm)
- Dòng `Cần:` (khai phụ thuộc giữa các task)
- Cụm song song
- Khuôn khối hợp đồng skill (đặt NGAY DƯỚI dòng task dùng skill đó, ≤6 dòng)
- Px — Log & test bắt buộc
- Definition of Done
- Ước tính phút `(eNm)`
- Dòng `Mode thực thi`
- Kiểm trước khi trình

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Mỗi bước: `tdq_test.py vung-cham`; trọn bộ chỉ ở QC.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Tuân thủ 6 mã cấm cơ học (ANTI-1 Fake Red, ANTI-2 Blind Assertion, ANTI-3 Dirty State Git, ANTI-4 Late Tick, ANTI-5 Raw Dump, ANTI-6 Broad Area).

## Thiết kế Trước vs Sau (áp dụng khi Refactor hoặc bổ sung tính năng)
| Khía cạnh | Hiện trạng (Trước) | Thiết kế mới (Sau) |
|---|---|---|
| Luồng thực thi | <mô tả luồng cũ> | <mô tả luồng mới tối ưu> |
| Thành phần chạm | <danh sách thành phần cũ> | <thành phần mới / thay thế> |

*Đối chiếu sơ đồ kiến trúc:* Khi spec có sinh sơ đồ Archify preview (`<slug>-preview.html`), WBS các task cần bám sát đúng các node và boundary trên sơ đồ để không bỏ sót thành phần.

## P1 — <tên phase>
- [ ] **T1.1** (e6m) <việc cụ thể> — Test: <lệnh hoặc tiêu chí pass>
- [ ] **T1.2** (e12m) <việc cụ thể> — Test: <...>

**Xong P1 khi**: <điều kiện đo được>

## P2 — <tên phase>
- [ ] **T2.1** (e20m) <...> — Test: <...>

## Dòng `Chạm:` (đặt NGAY DƯỚI mọi task TẠO hoặc SỬA file mã nguồn)
- [ ] **T<x.y>** <việc sửa hàm/file sẵn có> — Test: <...>
  - Chạm: `<đường/dẫn/file.py>`, `<tests/test_file.py>` → <node bị ảnh hưởng> (nguồn: `graphify affected "<X>" --depth 2`)
- [ ] **T<x.z>** <việc tạo file mới> — Test: <...>
  - Chạm: `<đường/dẫn/file-moi.py>` → file mới, chưa node nào phụ thuộc

**Mọi task tạo hoặc sửa file mã nguồn đều phải có dòng `Chạm:`**, đường dẫn trong backtick tính từ gốc repo. Task chỉ sửa tài liệu thì bỏ dòng này. Chi tiết: [plan-template-co-che.md](plan-template-co-che.md).

## Dòng `Cần:` (khai phụ thuộc giữa các task)

Đặt ngay dưới task, sau dòng `Chạm:` nếu có. Một dòng, mã task ngoài backtick:

- [ ] **T3.2** việc đọc đầu ra của task khác — Test: <...>
  - Cần: T3.1, T1.3

Task ĐỌC đầu ra của task khác BẮT BUỘC khai. Cấm khai vòng: A cần B mà B cần A. Chi tiết: [plan-template-co-che.md](plan-template-co-che.md).

## Cụm song song

Mục này BẮT BUỘC có trong mọi plan (kể cả một cụm: ghi rõ lý do). Chi tiết: [plan-template-co-che.md](plan-template-co-che.md).

## Luật file nóng (một file, nhiều task chạm)

Đường dẫn bị từ 2 task trở lên khai ở `Chạm:` là FILE NÓNG. Chọn một trong hai cách: **nâng lên đợt sớm** (mặc định) hoặc **một chủ ghi duy nhất**. Chi tiết: [plan-template-co-che.md](plan-template-co-che.md).

## Khuôn khối hợp đồng skill (đặt NGAY DƯỚI dòng task dùng skill đó, ≤6 dòng)
- [ ] **T<x.y>** <việc của task> — Test: <...>
  - Dùng: `<tên skill>`
  - Để: <việc cụ thể skill lo>, nạp skill TRƯỚC bước đỏ
  - Ra: <artifact phải tồn tại sau task, có đường dẫn>
  - Kiểm: <một lệnh chạy được, PASS đo được>
  - Không dùng cho: <việc kề bên mà skill này KHÔNG được lan sang>

Skill cần MCP tool lúc chạy → dòng `Dùng:` phải kết thúc bằng nhãn ` (mcp)` NGOÀI backtick. Năm
trường và luật nhãn đầy đủ: mục `Khuôn khối hợp đồng skill` của
[plan-template-co-che.md](plan-template-co-che.md).
Quy tắc MCP-First: Với task dùng MCP, phải có bước kiểm tra kết nối (pre-flight probe) trước khi gọi tool, và hướng dẫn user mở server nếu chưa kết nối (xem `skills/tdq-setup/references/mcp-first-guide.md`).
## Px — Log & test bắt buộc
Phase này bắt buộc **chỉ khi việc này có runtime** — tức có ít nhất một task tạo hoặc sửa
file mã nguồn chạy được. Không có runtime (chỉ sửa tài liệu, khuôn mẫu, cấu hình) → bỏ
task log, giữ task test, và ghi đúng một dòng `Log: BỎ — <lý do một câu>`.

- [ ] **Tx.1** Log service bật mặc định (timestamp, mức log, tắt được qua config) — Test: <...>
- [ ] **Tx.2** Unit test cho từng thành phần, chạy bằng một lệnh — Test: <lệnh>

## Definition of Done
Trỏ về §6 của spec. Liệt kê lại từng hạng mục QC + lệnh kiểm, MỖI DÒNG MỘT Ô TICK:

- [ ] Q1 <điều kiện đủ> — <lệnh kiểm>
- [ ] Q2 <điều kiện đủ> — <lệnh kiểm>
```

Mark `[x]` when that item PASSes and evidence sits in the qc file. Hook `Stop` checks these boxes via `[TDQ:DOD]`.

## The minute estimate `(eNm)`

Goes **right after the task code**: `- [ ] **T2.1** (e12m) <work> — Test: ...`. `eNm` = estimated minutes to execute (integer 1–999). Details in [plan-template-huong-dan.md](plan-template-huong-dan.md).
