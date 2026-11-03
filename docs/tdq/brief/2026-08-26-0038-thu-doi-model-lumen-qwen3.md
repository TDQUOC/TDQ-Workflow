# Thử tạm đổi model lumen sang qwen3-embedding:0.6b, test lại

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> hãy thử tạm chuyển lumen qua qwen3-embedding:0.6b xem và test lại giúp tôi thử

Nối tiếp phần research trước: xác nhận `ordis/jina-embeddings-v2-base-code` (model lumen đang
dùng) chỉ đa ngữ ở PHẦN NGÔN NGỮ LẬP TRÌNH, không train tiếng Việt; `qwen3-embedding:0.6b` đã có
sẵn trên máy và lumen đã biết model này trong `KnownModels`. User muốn: đổi TẠM config lumen
sang qwen3-embedding:0.6b, reindex, chạy lại truy vấn T2 (khái niệm mơ hồ tiếng Việt) để so
sánh trước/sau.

## Hiểu & kiến thức

- Config lumen nằm NGOÀI repo: `~/.config/lumen/config.yaml` (2 server entries, cùng model
  `ordis/jina-embeddings-v2-base-code`, khác host). Đây là config machine-wide, không phải
  config của riêng project TDQWorkflow — đổi ảnh hưởng mọi project dùng lumen trên máy này.
- "Thử tạm" → bắt buộc backup file gốc trước khi sửa, có đường lùi rõ ràng (revert lại y hệt).
- Đổi model xong cần `lumen reindex` (chạy lại embedding toàn bộ index bằng model mới) trước
  khi test lại, nếu không so sánh sẽ dùng nhầm index cũ.
- Việc so sánh: lặp lại đúng câu hỏi T2 của request trước ("nơi ghi trạng thái duyệt approve
  vào state.json") qua `semantic_search`, đối chiếu với kết quả jina cũ đã ghi trong
  `docs/tdq/plan/2026-08-26-0015-test-ranking-lsp-lumen-grep.md`.
- Không sửa file source của TDQWorkflow — chỉ sửa config lumen (ngoài repo) + chạy lệnh reindex.

## Hỏi đáp

(không có câu hỏi cần hỏi lại — phạm vi rõ, user đã tự nêu "thử tạm" nghĩa là có backup/rollback)
