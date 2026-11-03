# REQUEST — 2026-08-05-bump-sync-user

## Nguyên văn user

> okay hãy pump version và sync với claude user-level và commit

## Cách hiểu đầu tiên

- Mục tiêu: (1) bump version plugin `tdq-workflow` (đang `0.7.0` từ request
  `bump-version-va-export`, chưa bump từ 2 request sau: audit token vòng 3 +
  16 đề xuất P0/P1 workflow, và luật đặt tên sub-agent global) — đề xuất `0.8.0` vì
  đổi cấu trúc nhiều skill + thêm luật global mới, không chỉ vá lỗi (khác kiểu patch
  0.6.1/0.6.2). (2) "sync với claude user-level" = quy trình đã ghi sẵn ở
  `docs/notes/user-level-install.md` mục "Cập nhật plugin": chạy
  `claude plugin marketplace update tdq-local` rồi
  `claude plugin update tdq-workflow@tdq-local` (cache hiện đang kẹt ở bản `0.6.2`,
  lệch xa `plugin.json` — xác nhận bằng `installed_plugins.json`). (3) commit sau khi
  bump.
- Phạm vi đoán: thêm mục CHANGELOG.md cho bản mới, tóm tắt 2 batch việc kể từ 0.7.0.
  Không đổi nội dung tính năng nào khác trong turn này.
- Chỗ chưa rõ: số version chính xác (đề xuất 0.8.0, xin xác nhận) — không phải điều
  chỉnh hồi tố được nếu đã commit + tag, nhưng sửa lại vẫn rẻ.
