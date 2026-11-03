# PLAN — Fix: câu hỏi TDQ bị ẩn khi bật focus mode

Ngày: 2026-08-13 · Spec: ../spec/2026-08-13-fix-cau-hoi-focus-mode.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — 1 task sửa văn bản 1 file, không có gì chia được cho subagent (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
5. Không commit/push cho đến khi user yêu cầu.

## P1 — Sửa quy tắc §1 bước 4
- [x] **T1.1** (n3 e10m) Sửa `skills/tdq-conventions/SKILL.md` §1 bước 4: thêm (a) câu bắt
  buộc gọi `tdq_finish.py`, cấm Edit tay working log; (b) câu bắt buộc lệnh đó chạy TRƯỚC
  đoạn chat cuối cùng kết thúc turn (tóm tắt/câu hỏi/dòng ➤ Duyệt/báo lỗi vượt trần),
  không gọi thêm tool sau khi đã in đoạn đó — Test: `python3 scripts/doc_lint.py
  skills/tdq-conventions/SKILL.md` → exit 0; đọc lại có đủ 2 ý.

**Xong P1 khi**: §1 bước 4 có đủ 2 ý, `doc_lint.py` exit 0.

## Px — Log & test bắt buộc
Log: BỎ — việc thuần sửa văn bản skill, không có file mã nguồn chạy được nào được tạo/sửa
(script `tdq_finish.py` đã có sẵn, không sửa).

- [x] **Tx.2** `doc_lint.py` chạy trên file đã sửa (đã gộp vào T1.1, tick khi T1.1 xanh) —
  Test: `python3 scripts/doc_lint.py skills/tdq-conventions/SKILL.md`

## Definition of Done
Trỏ về §6 spec:
- Q1: đọc lại `tdq-conventions/SKILL.md` §1 bước 4 có đủ 2 ý (bắt buộc lệnh + thứ tự trước).
- Q2: `python3 scripts/doc_lint.py skills/tdq-conventions/SKILL.md` → exit 0.
- Q3: bằng chứng sống — turn build/QC/report còn lại của CHÍNH request này đều dùng
  `tdq_finish.py` (đã có 1 entry từ turn viết spec; cần tiếp tục ở các turn implement/QC/report).
