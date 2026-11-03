# PLAN — Lưu & nhúng ảnh đính kèm vào working log

Ngày: 2026-08-13 · Spec: ../spec/2026-08-13-luu-anh-workinglog.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — 2 task tuần tự, cùng đụng 1 file quy ước, không cần chia sub-agent (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Thêm quy ước vào tdq-conventions
- [x] **T1.1** (n3 e8m) Thêm vào `skills/tdq-conventions/SKILL.md` §6 (Working log) đoạn
  quy ước mới: turn có ảnh user gửi kèm + phải ghi working log → TRƯỚC khi gọi
  `tdq_finish.py --log`, copy từng ảnh từ `~/.claude/image-cache/<session>/<n>.<ext>`
  sang `docs/workinglog/assets/<slug-request|misc>/<n>.<ext>` (`n` = đếm file đã có
  trong thư mục đích + 1), rồi chèn `![<mô tả ngắn>](assets/<slug>/<n>.<ext>)` vào đúng
  vị trí liên quan trong chuỗi `--log`. Nêu rõ: track git (không gitignore), áp dụng cho
  MỌI ảnh trong turn đổi repo, copy lỗi → báo user thay vì im lặng bỏ qua — Test: đọc lại,
  đủ 3 chốt (git/phạm vi/tên-thư mục) đúng tinh thần spec §1b + §3
- [x] **T1.2** (n1 e3m) `doc_lint.py` cho file vừa sửa — Test:
  `python3 scripts/doc_lint.py skills/tdq-conventions/SKILL.md` exit 0

**Xong P1 khi**: quy ước đã ghi đủ, `doc_lint.py` exit 0.

## P2 — Log: BỎ — chỉ sửa tài liệu quy ước, không tạo/sửa file mã nguồn chạy được.

- [x] **T2.1** (n2 e5m) Test bằng chứng cơ chế: giả lập 1 ảnh (tạo file PNG mẫu tối
  giản), copy theo đúng quy ước T1.1 vào `docs/workinglog/assets/2026-08-13-luu-anh-workinglog/1.png`,
  ghi 1 dòng vào working log hôm nay có `![test](assets/2026-08-13-luu-anh-workinglog/1.png)`
  — Test: `test -f docs/workinglog/assets/2026-08-13-luu-anh-workinglog/1.png` và
  `grep -q '!\[test\]' docs/workinglog/<hôm nay>.md`

## Definition of Done
Trỏ về spec §6.
| # | Hạng mục kiểm | Lệnh/cách kiểm | Kết quả |
|---|---|---|---|
| Q1 | Quy ước đủ 3 chốt | Đọc lại `tdq-conventions/SKILL.md` §6 | |
| Q2 | `doc_lint.py` pass | `python3 scripts/doc_lint.py skills/tdq-conventions/SKILL.md` | |
| Q3 | Cơ chế hoạt động đúng thực nghiệm | `test -f .../1.png` + `grep` link trong working log | |
