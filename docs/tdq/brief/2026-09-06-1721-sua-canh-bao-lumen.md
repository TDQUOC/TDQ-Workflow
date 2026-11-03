# BRIEF — Sửa cảnh báo lumen sai ở bậc 5
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay tôi muón sửa cái 1 đi còn những cái khác thấy có vẻ ko quan trọng lắm

"Cái 1" trỏ tới issue số 1 trong bản rà soát setup vừa trình: bậc 5 của `scripts/tdq_lsp.py`
báo CẢNH BÁO "thiếu model ordis/jina-embeddings-v2-base-code" trong khi máy đã cố ý chuyển
lumen sang `qwen3-embedding:0.6b`. Bốn issue còn lại (drift plugin cache, marker i18n,
hooks.json antigravity, connector Google Drive) người dùng chốt là **không làm**.

- **Mục tiêu**: bậc 5 phản ánh đúng model lumen thật sự đang dùng, hết cảnh báo oan mỗi lần intake.
- **Phạm vi đoán**: `scripts/tdq_lsp.py` (hằng `MODEL_LUMEN:42`, `_model_da_pull:308`,
  `bac5_lumen:314`) + test tương ứng trong `tests/test_tdq_lsp.py` (class `Bac5Lumen`).
- **Chỗ chưa rõ**: lấy model từ đâu (config lumen / biến môi trường / cả hai) và ưu tiên thế nào.

## Hiểu & kiến thức

### Bằng chứng đã thu (trước khi mở request)

- `~/.config/lumen/config.yaml` khai 2 server (primary Tailscale `100.122.225.62`, backup
  `localhost`), cả hai `model: qwen3-embedding:0.6b`. Quyết định nằm ở plan
  `docs/tdq/plan/2026-09-06-1151-cai-setup-lumen.md`.
- `ollama list` chỉ có `qwen3-embedding:0.6b` (639 MB). `lumen search "kiểm tra 7 bậc lsp"`
  trả 8 kết quả đúng ⇒ lumen KHOẺ, chỉ checker sai.
- `lumen index --help`: model mặc định = `$LUMEN_EMBED_MODEL` hoặc
  `ordis/jina-embeddings-v2-base-code` ⇒ thứ tự đúng là config → env → mặc định.
- Bẫy đường dẫn manifest: hiện `_model_da_pull` ghép thẳng `MODEL_LUMEN.split("/")`. Với
  `qwen3-embedding:0.6b` (không có "/") đường dẫn thật là
  `registry.ollama.ai/library/qwen3-embedding/0.6b` ⇒ phải tách namespace + tag, nếu không
  sửa hằng số thôi vẫn báo thiếu.
- `tdq_lsp.py` chỉ dùng stdlib, KHÔNG có PyYAML ⇒ phải đọc config bằng parser tối giản.

### Kiểm lớp tìm kiếm (bước 1b)

7 bậc: 6/7 ĐẠT, riêng bậc 5 CẢNH BÁO — chính là lỗi cần sửa, không chặn.
Kiểm hiệu ứng: `find_references` trên `tdq_state.load` (`scripts/tdq_state.py:313`) trả 49
tham chiếu trải `scripts/`, `hooks/`, `tests/`; grep đếm 11 file ⇒ LSP ≥ grep, PASS.

## Hỏi đáp
