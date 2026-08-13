# PLAN — Điều tra & báo cáo: câu hỏi TDQ bị ẩn khi bật focus mode

Ngày: 2026-08-13 · Spec: ../spec/2026-08-13-focus-mode-an-cau-hoi.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — 1 task viết văn bản, không có gì chia được cho subagent (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
5. Không commit/push cho đến khi user yêu cầu.

## P1 — Viết báo cáo nguyên nhân
- [x] **T1.1** (n3 e10m) Viết `docs/tdq/reports/2026-08-13-focus-mode-an-cau-hoi.md` — 3
  phần: hiện tượng quan sát (trích ảnh chụp user báo), cơ chế gây ra (trích
  `hooks/scripts/stop_gate.py` đường dẫn:dòng + nguồn research chính thức/GitHub Issue
  #50894), 1 gợi ý hướng khắc phục khả dĩ (không triển khai) — Test:
  `python3 scripts/doc_lint.py docs/tdq/reports/2026-08-13-focus-mode-an-cau-hoi.md` → exit 0

**Xong P1 khi**: report tồn tại, đủ 3 phần, `doc_lint.py` exit 0.

## Px — Log & test bắt buộc
Log: BỎ — việc thuần viết báo cáo, không có file mã nguồn chạy được nào được tạo/sửa.

- [x] **Tx.2** `doc_lint.py` chạy trên report (đã gộp vào T1.1, tick khi T1.1 xanh) — Test:
  `python3 scripts/doc_lint.py docs/tdq/reports/2026-08-13-focus-mode-an-cau-hoi.md`

## Definition of Done
Trỏ về §6 spec:
- Q1: report có trích đường dẫn:dòng thật của `stop_gate.py` — đọc lại đối chiếu.
- Q2: report có trích nguồn research chính thức (docs.claude.com hoặc GitHub Issue) —
  đọc lại đối chiếu.
- Q3: `python3 scripts/doc_lint.py docs/tdq/reports/2026-08-13-focus-mode-an-cau-hoi.md` → exit 0.
