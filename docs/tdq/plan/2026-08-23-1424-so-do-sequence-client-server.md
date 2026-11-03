# QUICK — sơ đồ dạng sequence, đóng khung tầng và tách làn theo module

**Ngày:** 2026-08-23 · Brief: ../brief/2026-08-23-1424-so-do-sequence-client-server.md · Lane: quick
**Trạng thái:** ĐÃ LÀM XONG RỒI HOÀN NGUYÊN — user xem thử thấy sequence diagram khó nhìn hơn
dự kiến, chốt quay lại khuôn cũ. Cả 4 task từng xanh và QC 8/8 PASS, nhưng hai file kết quả đã
`git checkout` về trạng thái trước request. Giữ file này làm hồ sơ, không xoá.
**Ước tính sẽ dùng skill:** không có

## Phạm vi

Vòng hỏi phạm vi: BỎ — việc chỉ đụng hai file tài liệu đã biết tên, user đã chốt cả hai câu.

- Trong: sửa mục 1 và mục 2 của tài liệu thiết kế v2; viết lại file mẫu theo khuôn mới.
- NGOÀI: sửa `scripts/`, `hooks/`, `skills/` — vẫn là đề xuất chưa apply, y như request trước.

## Chốt thiết kế

- Mỗi bước mang một nhãn tầng: `B3 @server · mô tả (file::hàm)`.
- Đầu file khai một dòng `@tầng: client, server, db` — thứ tự khai là thứ tự khung trái sang phải.
- Participant là MODULE, suy ra từ tên file trong cặp `file::hàm`, không phải khai tay.
- Khung `box` bao quanh các participant cùng tầng, đúng ý user muốn nhìn ra client hay server.
- Lệnh `sinh` chèn khối mermaid vào cuối chính file sơ đồ, đánh dấu sinh tự động, cấm sửa tay.

## Task

- [x] **T1** Sửa mục 2 tài liệu thiết kế: thêm luật `L8` dòng khai tầng, `L9` nhãn tầng trên mọi
  bước kể cả dòng `(?)`, `L10` khối mermaid là vùng sinh tự động — Test:
  `grep -cE '^\| L[0-9]+ ' docs/tdq/knowledge/2026-08-23-thiet-ke-mind-map-v2.md` trả về 10
- [x] **T2** Sửa mục 1 tài liệu thiết kế: lệnh `sinh` thêm việc dựng khối mermaid, kèm bốn quy
  tắc dựng (participant từ tên file, khung từ nhãn tầng, mũi tên khi đổi participant, nhánh lỗi
  vẽ mũi tên đứt) — Test: mục 1 có tiểu mục quy tắc dựng với đúng 4 quy tắc đánh số
- [x] **T3** Viết lại `docs/tdq/mind-map/vi-du-login.md` theo khuôn mới, kèm khối mermaid mẫu —
  Test: file có dòng `@tầng:`, mọi dòng bước có nhãn `@`, và có khối ```mermaid``` chứa `box`
- [x] **T4** Lint và kiểm trần dòng — Test:
  `python3 scripts/doc_lint.py docs/tdq/knowledge/2026-08-23-thiet-ke-mind-map-v2.md docs/tdq/mind-map/vi-du-login.md`
  exit 0 và `wc -l` tài liệu thiết kế ≤ 320

## Definition of Done

- Tài liệu thiết kế có đúng 10 luật khuôn — `grep -cE '^\| L[0-9]+ ' <tài liệu>`
- Mục 1 có 4 quy tắc dựng sơ đồ — `grep -cE '^[0-9]\. ' <tiểu mục quy tắc dựng>`
- File mẫu khai tầng và mọi bước có nhãn — `grep -c '^@tầng:' <file mẫu>` bằng 1, và số dòng `B`
  bằng số dòng `B` có ký tự `@`
- File mẫu có khối mermaid đóng khung — `grep -c 'box ' <file mẫu>` ≥ 2
- Lint sạch trên cả hai file — `python3 scripts/doc_lint.py <hai file>` exit 0
- Tài liệu thiết kế vẫn ≤ 320 dòng — `wc -l <tài liệu>`
- Không file nào ngoài `docs/` bị đụng — `git status --porcelain | grep -v '^.. docs/'`

## QC

Kết quả: 8/8 PASS, không defect, không vòng sửa. Ký hiệu `<TK>` là tài liệu thiết kế,
`<VD>` là `docs/tdq/mind-map/vi-du-login.md`.

| # | Hạng mục | Lệnh | Kết quả | Phán quyết |
|---|---|---|---|---|
| Q1 | 10 luật khuôn | `grep -cE '^\| L[0-9]+ ' <TK>` | 10 | PASS |
| Q2 | 4 quy tắc dựng | đếm `^[0-9]\. ` trong tiểu mục quy tắc dựng | 4 | PASS |
| Q3 | File mẫu khai tầng | `grep -c '^@tầng:' <VD>` | 1 | PASS |
| Q4 | Mọi bước có nhãn tầng | số dòng `B` so với số dòng `B` có `@` | 8 và 8 | PASS |
| Q5 | Khối mermaid có đóng khung | `grep -c 'box ' <VD>` | 2 | PASS |
| Q6 | Lint sạch hai file | `doc_lint.py <TK> <VD>` | 0 vi phạm, exit 0 | PASS |
| Q7 | Trần 320 dòng | `wc -l <TK>` | 305 | PASS |
| Q8 | Không đụng ngoài `docs/` | `git status --porcelain \| grep -v '^.. docs/' \| grep -v graphify-out` | 0 dòng | PASS |

Chạy lại lệnh `Test:` của cả 4 task: T1 trả 10 · T2 trả 4 · T3 đủ ba điều kiện · T4 exit 0 và
305 dòng. Không lệnh nào đỏ.

## Kết cục và thứ đáng giữ lại

Hoàn nguyên `docs/tdq/knowledge/2026-08-23-thiet-ke-mind-map-v2.md` và
`docs/tdq/mind-map/vi-du-login.md` về commit `7c69a8d`. Không commit đợt sửa này.

Ba thứ học được, để request build sau khỏi đi lại:

1. Sequence diagram ĐẮT hơn tưởng với người đọc. Nó diễn đạt được ranh giới client/server, nhưng
   đổi lại phải mở trình duyệt và phải đọc theo hai chiều cùng lúc. Khuôn danh sách một-bước-một-dòng
   đọc thẳng trong chat được, và đó là chỗ người ta thực sự đọc nó.
2. Khuôn viết tay một-dòng-một-bước dựng ra được nhiều dạng đầu ra từ một nguồn. Cây ASCII cho
   chat đã thử và đọc tốt. Nếu sau này vẫn muốn tầng client/server, hướng rẻ hơn là thêm cờ dạng
   đầu ra cho lệnh `xem`, chứ không đổi khuôn viết tay.
3. Nếu có ngày dựng mermaid thật: mã participant của mermaid là namespace phẳng toàn sơ đồ, trùng
   tên phải xét cả file chứ không riêng từng `box`; và mũi tên nhánh lỗi phải trỏ tới module xử lý
   lỗi, không quay về bước liền trước, nếu không module đó biến mất khỏi sơ đồ.

## Ghi chú lúc làm

Viết file mẫu mới lòi ra hai chỗ sai trong quy tắc dựng vừa viết ở T2, đã sửa ngay:

- Quy tắc 1 ban đầu nói chỉ đổi tên khi trùng **trong cùng một tầng**. Sai: mã participant của
  mermaid là duy nhất toàn sơ đồ, nên `src/api/auth.ts` và `server/controllers/auth.py` — hai
  tầng khác nhau — vẫn đâm nhau. Sửa thành trùng ở bất kỳ đâu trong file thì lấy thêm thư mục cha.
- Quy tắc 4 ban đầu vẽ mũi tên lỗi **quay về bước liền trước**. Làm vậy thì module xử lý lỗi
  (`src/lib/form-ui.ts`) biến mất khỏi sơ đồ, đúng cái người đi dò sự cố cần tìm. Sửa thành vẽ
  tới participant của chính dòng nhánh lỗi.
