# REPORT — Vòng scope: interview đi từ tổng quát đến chi tiết

Ngày: 2026-08-14 · Lane: full · Mode: main (inline) · Spec 1.0 · 15/15 task `[x]`

## Đã làm

- Thêm file luật `skills/tdq-intake/references/scope-round.md` (115 dòng, 5 mục): khi nào
  chạy · câu 1 chọn mặt · câu 2 bối cảnh bằng số · suy mức đầu tư · ghi lại.
- Vòng scope chạy **có điều kiện** theo danh sách đóng 4 dấu hiệu; bỏ thì buộc ghi một dòng
  `Vòng scope: BỎ — <lý do>` vào brief. Áp cho cả lane express lẫn deep.
- Câu 1: chỉ trình 3–5 mặt hợp lĩnh vực, soát nội bộ theo khung 9 mặt ISO/IEC 25010.
- Câu 2: hỏi môi trường/bản target, CCU/RPS, R&D hay product, người bảo trì — **cấm** hỏi
  "gọn hay đầy đủ chuyên nghiệp"; agent tự suy mức đầu tư rồi in `Tôi hiểu là: …`.
- Nối vào 4 chỗ gọi: `interview.md` (hai tầng, tầng 2 chỉ hỏi trong mặt user chọn),
  `analyze-full.md` bước 4, `quick-lane.md`, `tdq-intake/SKILL.md` (109 dòng ≤ 120).
- Neo kết quả: `spec-template.md` §1 buộc chép mặt bị loại vào NGOÀI phạm vi + 1 dòng
  checklist; `tdq_state.py` `PHASE_GUIDE["analyze"]` thêm dòng nhắc vòng scope.
- Test mới `tests/test_scope_round.py` (8 test nội dung + 2 test "đã nối dây") và
  `test_next_analyze_asks_for_the_scope_round` trong `tests/test_next.py`.

## QC

11/11 PASS vòng 1 — chi tiết ở `docs/tdq/qc/2026-08-14-interview-hoi-scope.md`.
`pytest tests/ -q` → 563 passed, 244 subtests. `doc_lint.py` 10 file → exit 0.
Log service giữ nguyên: `_warn` in 1 dòng có timestamp, `TDQ_LOG=0` in 0 dòng.

## Còn lại

Chưa commit — chờ user quyết.
