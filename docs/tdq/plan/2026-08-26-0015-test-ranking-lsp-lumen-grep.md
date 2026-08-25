# QUICK — Test ranking khả năng find: LSP vs lumen vs grep

**Ngày:** 2026-08-26 · Brief: ../brief/2026-08-26-0015-test-ranking-lsp-lumen-grep.md · Lane: quick
**Trạng thái:** CHỜ DUYỆT
**Ước tính sẽ dùng skill:** không có

## Phạm vi
- Trong: chạy 3 loại truy vấn mẫu (tên symbol chính xác, khái niệm mơ hồ, "ai gọi hàm này")
  qua cả 3 lớp `mcp__lsp__*`, lumen (`semantic_search`), `grep` trên repo TDQWorkflow; so sánh
  và xếp hạng theo: đúng, đủ, tốc độ, độ hữu ích.
- NGOÀI: không sửa code/cấu hình nào; không đổi thứ tự ưu tiên đã set trong
  `uu-tien-tim-kiem.md`. Không có feature flow nào bị đổi → bỏ bước vẽ sơ đồ (1b), lý do:
  request thuần đọc/đo, không có code path sản phẩm mới.

## Task
- [x] **T1** Truy vấn tên symbol chính xác (`bac6_hook_xung_dot` trong `scripts/tdq_lsp.py`)
  qua LSP `find_symbol`, lumen `semantic_search`, `grep -rn` — Test: cả 3 trả kết quả, so đúng
  vị trí thật (ground truth: def dòng 284, gọi dòng 314, test 4 chỗ).
- [x] **T2** Truy vấn khái niệm mơ hồ ("nơi ghi trạng thái duyệt approve vào state.json") qua
  cả 3 lớp — Test: so xem lớp nào trả đúng file/hàm liên quan (ground truth:
  `scripts/tdq_state.py` dòng ~1579, các field `*_approved_at/by`).
- [x] **T3** Truy vấn "ai gọi hàm X" (`load()` trong `scripts/tdq_state.py:304`, hàm được
  import ở 10 file khác) qua LSP `find_callers`, lumen, `grep -rn` — Test: so số lượng & độ
  chính xác caller tìm được (ground truth: 14 caller nội bộ + ≥5 file ngoài import và gọi,
  vd `hooks/scripts/edit_gate.py:68`).

## Definition of Done
- Có bảng ranking 3 lớp theo 3 tiêu chí truy vấn, dựa trên output thật (dán log/kết quả).
- Không file source nào bị sửa (chỉ đọc).

## QC
- Q1 test từng task: PASS — cả 3 task chạy qua `mcp__lsp__find_symbol`/`find_callers`,
  `mcp__plugin_lumen_lumen__semantic_search`, `grep -rn`, output thật đã dán vào phiên làm việc.
- Q2 DoD "bảng ranking 3 lớp": PASS — bảng đầy đủ, trình ở báo cáo cuối cho user.
- Q3 DoD "không file source nào bị sửa": PASS — `git status --porcelain` chỉ hiện
  `docs/tdq/brief/`, `docs/tdq/plan/`, `docs/tdq/state.json`, `docs/workinglog/`; không file
  trong `scripts/`, `hooks/`, `tests/` bị đổi.
