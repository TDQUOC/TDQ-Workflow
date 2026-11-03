# Mini plan — Phân tích repo Ponytail
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Trạng thái: ĐÃ DUYỆT (nguyên văn: "duyệt nhanh") · lane quick · nguồn: `docs/tdq/brief/2026-09-16-1129-phan-tich-repo-ponytail.md`

## Mục tiêu
Một tài liệu phân tích Ponytail v4.10.0 tự đứng được, cho bạn + đồng đội chưa biết Ponytail: phủ
cả 4 mặt A+B+C+D và so rộng với TDQ-Workflow trên cả vòng đời request.

## Phạm vi
- Đầu ra duy nhất: `docs/tdq/research/2026-09-16-1129-phan-tich-repo-ponytail.md`.
- KHÔNG sửa repo Ponytail (bên thứ ba, đã trả về sạch) và KHÔNG đề xuất bản vá cho nó.
- B0/B2 đã chạy xong ở bước phân tích, không lặp lại; B1 chỉ đọc bổ sung khi một khẳng định
  thiếu `đường-dẫn:dòng`.

## Việc
- [x] **T1** (e12m) Phần 1–2: Ponytail là gì + bộ luật & 5 mode (mặt A), viết cho người chưa biết
      — Kiểm: có mục "Ponytail là gì trong 5 dòng"; nêu đủ 7 bậc thang và 5 mode
- [x] **T2** (e15m) Phần 3: kiến trúc đa host (mặt B) — một nguồn chân lý, 3 hook vòng đời
      — Kiểm: có bảng host → file → cách bơm; nêu đúng 5 nhánh của `writeHookOutput()`
- [x] **T3** (e15m) Phần 4: chất lượng & rủi ro (mặt C) — 3 phát hiện + số đo test thật
      — Kiểm: đủ phát hiện 9/10/11, mỗi cái kèm `đường-dẫn:dòng`; ghi 94/95 và lý do test đỏ
- [x] **T4** (e12m) Phần 5: repo tự khai vs nhà cung cấp xác nhận (mặt D)
      — Kiểm: ≥10 nền tảng, mỗi dòng gắn nhãn "đã xác thực (URL)" hoặc "repo tự khai"
- [x] **T5** (e15m) Phần 6: so rộng với TDQ-Workflow trên cả vòng đời request
      — Kiểm: bảng đối chiếu ≥6 chặng; nêu rõ chặng nào hai bên KHÔNG so được và vì sao
- [x] **T6** (e6m) Tóm tắt điều hành ≤15 dòng đặt đầu tài liệu + báo cáo chat ≤50 dòng
      — Kiểm: đọc 20 dòng đầu là nắm được kết luận, không cần đọc tiếp

Chạm: `docs/tdq/research/2026-09-16-1129-phan-tich-repo-ponytail.md`

Mode thực thi: **main (inline)** — cả 6 task ghi vào CÙNG một file nên không tách rời được;
giao sub-agent sẽ đâm nhau khi ghi, không phải vì việc nhỏ.

## Định nghĩa hoàn thành (DoD)
- Tài liệu tồn tại và có đủ 6 phần đánh số.
- Mọi khẳng định về code Ponytail đều kèm `đường-dẫn:dòng` tồn tại thật.
- Mọi khẳng định về nền tảng ngoài đều gắn nhãn "đã xác thực (URL)" hoặc "repo tự khai".
- `git status` trong `/Users/tdq/Documents/ponytail` vẫn sạch sau khi xong.

## QC

QC bật (người dùng duyệt "duyệt nhanh", không nói bỏ QC). 4 dòng DoD → 4 mục kiểm, mỗi mục một
lệnh chạy được, không mục nào chấm bằng mắt.

| # | Dòng DoD | Lệnh kiểm | Kết quả | Kết luận |
|---|---|---|---|---|
| 1 | Tài liệu có đủ 6 phần đánh số | `check_citations.py` (regex `^## (\d)\. `) | `['1','2','3','4','5','6']` | **PASS** |
| 2 | Mọi khẳng định về code kèm `đường-dẫn:dòng` tồn tại thật | `check_citations.py` — mở từng file, so số dòng trích với số dòng thật | `38 trích dẫn · hợp lệ 38 · sai 0` | **PASS** (sau 1 vòng fix) |
| 3 | Mọi khẳng định về nền tảng ngoài có nhãn xác thực | script đếm dòng bảng phần 5 thiếu nhãn | `17 dòng nền tảng · thiếu nhãn 0` | **PASS** |
| 4 | `git status` trong repo Ponytail vẫn sạch | `git -C /Users/tdq/Documents/ponytail status --porcelain` | rỗng; `docs/` còn đủ 3 file tracked | **PASS** (sau 1 vòng fix) |

### QC vòng 1 — fix

Hai lỗi thật, trình kiểm bắt được chứ không phải tự nhận ra:

1. **13/37 trích dẫn thiếu thư mục** (`ponytail-activate.js:75-80` thay vì
   `hooks/ponytail-activate.js:75-80`) → không tự kiểm được. Đã thêm tiền tố thư mục cho toàn bộ,
   chạy lại: 38/38 hợp lệ.
2. **Lỗi thao tác của tôi, mức nghiêm trọng:** khi dọn thư mục `docs/tdq/` bị ghi nhầm vào repo
   Ponytail, lệnh `mv` của tôi đã chuyển **cả thư mục `docs/` của repo**, xoá mất 3 file đang
   được git theo dõi (`agent-portability.md`, `cursor-hooks.md`, `platform-native.md`). Đã phục
   hồi bằng `git checkout -- docs` (lấy từ git, không dùng bản copy của tôi) và xoá lớp bọc thừa.
   `git status` nay rỗng.
   **Nguyên nhân gốc, đã xử lý:** mỗi lệnh `cd` sang repo Ponytail làm đổi thư mục làm việc chính,
   khiến hook telemetry TDQ ghi `.tdq-turn.jsonl` vào đó. Đã chuyển sang dùng `git -C` để không
   đổi cwd nữa.

### Số đo test repo Ponytail (chỉ để báo cáo, không sửa gì trong repo đó)

- `node --test tests/*.test.js`: 94 pass / 95 · 1 fail
- `npm test --prefix pi-extension`: 23/23 · `npm test --prefix ponytail-mcp`: 3/3
- Test đỏ = `tests/correctness.test.js:77`, do máy thiếu `pandas`, không phải khiếm khuyết repo.
