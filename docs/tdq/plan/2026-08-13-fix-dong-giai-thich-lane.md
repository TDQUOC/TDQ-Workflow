# PLAN — Fix dòng giải thích pipeline gây rối khi đọc lại tóm tắt

Ngày: 2026-08-13 · Spec: ../spec/2026-08-13-fix-dong-giai-thich-lane.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — thuần thêm 1 câu quy ước vào mỗi trong 2 file skill, không có
runtime/test tự động, không cần chia song song (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: CHỜ DUYỆT

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Thêm quy ước gắn nhãn khuôn mẫu
- [x] **T1.1** (n3 e6m) Thêm câu quy ước vào `skills/tdq-spec/SKILL.md` bước 4 ("Trình
  bày & DỪNG"): khi tóm tắt cần trích nguyên khối mẫu/khuôn có sẵn, gắn nhãn rõ trước
  đoạn trích — Test: đọc lại, đối chiếu format ở spec §3/brief.
- [x] **T1.2** (n3 e6m) Thêm câu quy ước tương tự vào `skills/tdq-plan/SKILL.md` bước 5
  ("Trình bày & DỪNG") — Test: đọc lại, đối chiếu nhất quán với T1.1.

**Xong P1 khi**: cả 2 file đọc lại có câu quy ước đúng nội dung đã chốt, chưa chạy doc_lint.

## Px — Log & test bắt buộc
Log: BỎ — thuần sửa tài liệu/khuôn skill, không tạo/sửa file mã nguồn chạy được.

- [x] **Tx.2** `doc_lint.py` pass trên cả 2 file đã sửa — Test:
  `python3 scripts/doc_lint.py skills/tdq-spec/SKILL.md skills/tdq-plan/SKILL.md` → exit 0.

## Definition of Done
Theo spec §6:
- Q1: `tdq-spec/SKILL.md` bước 4 có câu quy ước gắn nhãn khuôn mẫu — PASS khi đọc lại khớp.
- Q2: `tdq-plan/SKILL.md` bước 5 có câu quy ước tương tự — PASS khi đọc lại khớp.
- Q3: `doc_lint.py` exit 0 trên cả 2 file — PASS khi lệnh Tx.2 trả về 0.
