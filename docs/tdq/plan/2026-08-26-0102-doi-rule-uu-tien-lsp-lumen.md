# QUICK — Đổi rule ưu tiên tìm kiếm: LSP + lumen song song, grep cuối

**Ngày:** 2026-08-26 · Brief: ../brief/2026-08-26-0102-doi-rule-uu-tien-lsp-lumen.md · Lane: quick
**Trạng thái:** CHỜ DUYỆT
**Ước tính sẽ dùng skill:** không có

## Phát hiện quan trọng trước khi làm (đổi phạm vi so với brief)
`semantic_search` của lumen **tự động incremental-reindex khi index cũ/rỗng** trước khi trả kết
quả (đã xác nhận qua source `internal/index/index.go`: so root-hash Merkle, chỉ embed file đổi).
Nghĩa là **không cần viết thêm code tự reindex trong `tdq_finish.py`** — tool tự lo phần đó mỗi
lần được gọi. Câu 3A ("ưu tiên index sẵn") vì vậy chỉ cần **đổ 5 chỗ đều gọi lumen ngay** (thay
vì chỉ khi LSP rỗng) — tần suất gọi tăng tự nhiên đã kéo theo index luôn tươi, không cần
subsystem mới. Việc thêm bước reindex riêng vào `tdq_finish.py` bị BỎ khỏi phạm vi vì thừa.

## Phạm vi
- Trong: sửa `uu-tien-tim-kiem.md` (luật gốc: LSP+lumen gọi SONG SONG mọi câu hỏi tìm code,
  gộp kết quả, grep vẫn lớp cuối) + đồng bộ nguyên văn câu luật ở đúng 5 chỗ móc đã có test.
- NGOÀI: không đổi code `tdq_finish.py`/`tdq_lsp.py`; không bật Ollama thường trực (giữ
  đánh thức-rồi-tắt như cũ, chỉ đổi ĐIỀU KIỆN đánh thức).

## Task
- [x] **T1** Sửa `skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md` — Chạm:
  `skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md`. §1 đổi câu luật chuẩn thành gọi song
  song; §2 giữ bảng lý do (không đổi); §3 đổi điều kiện đánh thức Ollama từ "LSP rỗng" thành
  "mọi câu hỏi tìm ký hiệu code", thêm 1 dòng ghi chú lumen tự incremental-reindex, không cần
  script riêng — Test: đọc lại thấy đủ 3 ý. PASS.
- [x] **T2** Đồng bộ nguyên văn câu luật mới vào đúng 5 chỗ móc — Chạm: `skills/tdq-intake/SKILL.md`,
  `skills/tdq-intake/references/analyze-full.md`, `skills/tdq-spec/SKILL.md`,
  `skills/tdq-plan/SKILL.md`, `skills/tdq-build/SKILL.md` — Test:
  `python3 -m pytest tests/test_tdq_lsp_skill.py -q`. PASS — 4 passed, 10 subtests passed.

## QC
- Q1 test từng task: PASS — T1 đọc lại file thấy đủ §1/§2/§3 đã đổi sang song song; T2
  `pytest tests/test_tdq_lsp_skill.py -q` → 4 passed, 10 subtests passed.
- Q2 DoD "pytest PASS": PASS (như trên).
- Q3 DoD "đọc thấy rõ 3 ý, không có bước reindex mới": PASS — `uu-tien-tim-kiem.md` §1/§3 nêu rõ
  gọi song song mọi câu hỏi tìm code, Ollama đánh thức theo điều kiện mới, không có script/bước
  reindex thủ công nào được thêm (chỉ ghi chú lumen tự incremental-reindex sẵn có).

## Definition of Done
- `pytest tests/test_tdq_lsp_skill.py -q` PASS (câu luật đủ 3 lớp đúng thứ tự chữ, khớp cả 5
  chỗ móc, có đường dẫn về luật gốc).
- Đọc `uu-tien-tim-kiem.md` thấy rõ: LSP+lumen song song mọi câu hỏi tìm code, grep cuối,
  Ollama đánh thức theo điều kiện mới, không có bước reindex thủ công/script mới nào được nêu.
