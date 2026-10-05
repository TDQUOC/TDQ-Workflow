# The plan shape
<!-- muc-luc-dong:
  The minute estimate `(eNm)`=124
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

**Mọi task tạo hoặc sửa file mã nguồn đều phải có dòng `Chạm:`**, kể cả task tạo file mới; đường
dẫn trong backtick, tính từ gốc repo. Task chỉ sửa tài liệu thì bỏ dòng này. Node nằm trong mục
`## Hub` của `docs/kien-truc.md` thì task phải thêm một dòng DoD kiểm hồi quy riêng cho node ấy.
Hai người đọc dòng này, và cái giá của việc thiếu nó: mục `Dòng Chạm` của
[plan-template-co-che.md](plan-template-co-che.md).

## Dòng `Cần:` (khai phụ thuộc giữa các task)

Đặt ngay dưới task, sau dòng `Chạm:` nếu có. Một dòng, mã task ngoài backtick, phân cách
bằng dấu phẩy:

- [ ] **T3.2** việc đọc đầu ra của task khác — Test: <...>
  - Cần: T3.1, T1.3

Task nào ĐỌC đầu ra của task khác thì BẮT BUỘC khai. Cấm khai vòng: A cần B mà B cần A thì máy
báo lỗi và dừng. Cách máy dùng dòng này để xếp đợt, và luật lùi khi plan không khai `Cần:` ở đâu
cả: mục `Dòng Cần` của [plan-template-co-che.md](plan-template-co-che.md).

## Cụm song song

Mục này BẮT BUỘC có trong mọi plan, mọi lane, mọi mode — kể cả khi kết luận là chỉ một cụm. Lý
do: tính modular là thuộc tính của TÀI LIỆU, không phải của mode thi hành. Viết "một cụm vì
<lý do>" vẫn hợp lệ; bỏ trắng mục thì `doc_lint --pair` báo lỗi. Cách chia cho đúng (4 luật, kèm
cách ước lượng trần tốc độ): mục `Cụm song song` của
[plan-template-co-che.md](plan-template-co-che.md).

## Luật file nóng (một file, nhiều task chạm)

Đường dẫn bị từ 2 task trở lên khai ở `Chạm:` là FILE NÓNG, và worktree không cứu được: mọi nhánh
đều phải sửa nó. Hai cách xử, chọn một, không có cách thứ ba — **nâng lên đợt sớm** (mặc định) hoặc
**một chủ ghi duy nhất**. Cách nhận diện và chi tiết hai cách: mục `Luật file nóng` của
[plan-template-co-che.md](plan-template-co-che.md).

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

These boxes are **the close-out evidence**, not decoration: mark `[x]` when that item PASSes
and its evidence already sits in the qc file. The machine counts them — `dod_tick_state()`
reads this section on its own, and hook `Stop` fires `[TDQ:DOD]` when the books close on an
open box while QC has passed everything. A DoD written without boxes still runs, it just
loses that net.

## The minute estimate `(eNm)`

Goes **right after the task code**, before the work itself:
`- [ ] **T2.1** (e12m) <work> — Test: ...`. `eNm` = minutes
Claude estimates it needs to EXECUTE that task, an integer 1–999, scored as the task is written
and never padded. Plan ETA = the sum over unfinished tasks. The six rules in full, including what
`eNm` deliberately does NOT promise: section `The minute estimate (eNm)` of
[plan-template-huong-dan.md](plan-template-huong-dan.md).
