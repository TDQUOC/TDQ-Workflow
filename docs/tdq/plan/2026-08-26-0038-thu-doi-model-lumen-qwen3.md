# QUICK — Thử tạm đổi model lumen sang qwen3-embedding:0.6b, test lại

**Ngày:** 2026-08-26 · Brief: ../brief/2026-08-26-0038-thu-doi-model-lumen-qwen3.md · Lane: quick
**Trạng thái:** CHỜ DUYỆT
**Ước tính sẽ dùng skill:** không có

## Phạm vi
- Trong: backup `~/.config/lumen/config.yaml`, đổi tạm cả 2 server entry sang model
  `qwen3-embedding:0.6b`, reindex, chạy lại truy vấn T2 cũ để so sánh, rồi hỏi user giữ hay
  revert.
- NGOÀI: không đổi thứ tự ưu tiên LSP→lumen→grep; không sửa code TDQWorkflow; không đổi
  model cho project khác ngoài scope test.

## Task
- [x] **T1** Backup `~/.config/lumen/config.yaml` → `config.yaml.bak-20260826` — Test: file
  backup tồn tại, nội dung giống bản gốc (`diff` rỗng). PASS.
- [x] **T2** Sửa cả 2 entry `model:` thành `qwen3-embedding:0.6b`, reindex project
  TDQWorkflow — Test: `lumen index` chạy xong không lỗi. PASS (lần 1 lỗi socket tạm ở 87%,
  retry incremental xong: 143 file, 3903 chunk, root hash b448e4f7bede86de).
- [x] **T3** Chạy lại đúng câu T2 cũ ("nơi ghi trạng thái duyệt approve vào state.json") qua
  `semantic_search`, so kết quả với bản jina cũ đã ghi trong
  `docs/tdq/plan/2026-08-26-0015-test-ranking-lsp-lumen-grep.md` — Test: có bảng so sánh
  trước/sau bằng output thật. PASS — xem `## So sánh trước/sau` bên dưới.

## So sánh trước/sau (cùng 1 câu hỏi, top-5)

| Hạng | jina-embeddings-v2-base-code (cũ) | qwen3-embedding:0.6b (mới) |
|---|---|---|
| 1 | docs/archive/CHANGELOG (score 0.76) — SAI, không phải code | **scripts/tdq_state.py `_cli_approve` (score 0.84) — ĐÚNG, đúng hàm ghi approve** |
| 2 | docs/workinglog (0.67) — SAI | portable_claude bản sao `_cli_approve` (0.83) — ĐÚNG (file trùng nội dung) |
| 3 | docs/tdq/spec (0.63) — SAI | portable_codex bản sao `_cli_approve` (0.83) — ĐÚNG (file trùng nội dung) |
| 4 | docs/tdq/spec khác (0.63) — SAI | docs/archive/CHANGELOG (0.77) — docs, đúng ngữ cảnh nhưng không phải code |
| 5 | docs/tdq/reports (0.63) — SAI | docs/workinglog (0.72) — docs, đúng ngữ cảnh nhưng không phải code |

**Kết quả:** jina cũ 0/5 trúng code thật; qwen3 mới 3/5 trúng code thật (top-1 chính xác đúng
hàm `_cli_approve` — nơi ghi `*_approved_at`/`*_approved_by` vào state.json). Cải thiện rõ rệt
cho truy vấn khái niệm bằng tiếng Việt.

## Definition of Done
- Có bảng so sánh top-5 kết quả jina vs qwen3 cho cùng 1 câu hỏi, dựa trên output thật.
- Backup config gốc còn nguyên, revert được ngay nếu user yêu cầu.

## QC
- Q1 test từng task: PASS — T1 backup diff rỗng; T2 reindex xong (143 file, 3903 chunk, root
  hash `b448e4f7bede86de`); T3 `semantic_search` chạy thật, output dán ở trên.
- Q2 DoD "bảng so sánh top-5": PASS — bảng ở mục `## So sánh trước/sau`.
- Q3 DoD "backup còn nguyên, revert được": PASS — `diff ~/.config/lumen/config.yaml.bak-20260826 <(...)` xác nhận file backup còn y hệt bản gốc; revert = `cp config.yaml.bak-20260826 config.yaml` rồi `lumen index . --force -m ordis/jina-embeddings-v2-base-code`.
