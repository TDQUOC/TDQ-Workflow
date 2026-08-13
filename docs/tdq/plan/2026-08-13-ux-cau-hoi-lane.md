# PLAN — Rút gọn UX câu hỏi chọn lane

Ngày: 2026-08-13 · Spec: ../spec/2026-08-13-ux-cau-hoi-lane.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — thuần sửa văn bản 2 file skill, không có runtime/test tự động, không
cần chia song song cho sub-agent (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: CHỜ DUYỆT

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Sửa khuôn câu hỏi chọn lane
- [x] **T1.1** (n3 e8m) Sửa `skills/tdq-intake/SKILL.md` bước 2 Phần A: bỏ yêu cầu in dòng
  `Cỡ:/Cần:` ra chat, đổi câu hỏi trực tiếp user sang "Bạn muốn chạy pipeline nào?" —
  Test: đọc lại đoạn, đối chiếu format đã chốt trong spec §3.
- [x] **T1.2** (n3 e10m) Sửa `skills/tdq-intake/references/lane-decision.md`: mục "Dòng tự
  nhận định" đổi thành đánh giá NỘI BỘ (không in ra chat, giữ nguyên bảng quyết định làm
  căn cứ), mục "Khuôn câu hỏi" viết lại theo format mới (bỏ dòng Cỡ/Cần, câu hỏi dùng
  "pipeline", thêm khối giải thích nghĩa 2 pipeline ngay dưới option A/B, giữ khối hint trả
  lời có sẵn) — Test: đọc lại, đối chiếu khối format ở spec §3/brief mục "Chốt kiến thức".

**Xong P1 khi**: cả 2 file đọc lại khớp đúng format mới, chưa chạy doc_lint.

## Px — Log & test bắt buộc
Log: BỎ — thuần sửa tài liệu/khuôn skill, không tạo/sửa file mã nguồn chạy được.

- [x] **Tx.2** `doc_lint.py` pass trên cả 2 file đã sửa — Test:
  `python3 scripts/doc_lint.py skills/tdq-intake/SKILL.md skills/tdq-intake/references/lane-decision.md`
  → exit 0.

## Definition of Done
Theo spec §6:
- Q1: `SKILL.md` bước 2 không còn yêu cầu in `Cỡ:/Cần:`, dùng "pipeline" — PASS khi đọc lại khớp.
- Q2: `lane-decision.md` khuôn câu hỏi khớp format đã chốt — PASS khi đọc lại khớp.
- Q3: `doc_lint.py` exit 0 trên cả 2 file — PASS khi lệnh Tx.2 trả về 0.
