# Cấu hình Graphify custom LLM provider

`docs/tdq/config.json` chỉ chứa endpoint, model và **tên biến môi trường** giữ API key. Không ghi API key vào file này hoặc commit nó.

```json
{
  "GRAPHIFY_CUSTOM_PROVIDER": {
    "enabled": true,
    "endpoint": "https://your-openai-compatible-endpoint/v1",
    "model": "your-model-name",
    "api_key_env": "GRAPHIFY_CUSTOM_API_KEY"
  }
}
```

## Bật full extraction + wiki

1. Đặt `enabled` thành `true`.
2. Điền endpoint và model của provider OpenAI-compatible.
3. Đặt biến môi trường có tên trong `api_key_env` trước khi chạy TDQ. Trên PowerShell:

```powershell
$env:GRAPHIFY_CUSTOM_API_KEY = "<api-key>"
```

Sau đó, khi code hoặc tài liệu thay đổi, TDQ chạy full extraction và export wiki. Key không được đưa vào manifest hoặc log.

## Chế độ degraded

Khi provider bị tắt, config thiếu/sai hoặc biến key chưa có, TDQ chỉ chạy `graphify extract . --code-only`. Terminal sẽ nêu trường config hoặc tên biến môi trường còn thiếu. Graph/wiki ở trạng thái `degraded`, nên agent phải dùng LSP + grep cho câu hỏi semantic cho tới khi full extraction chạy thành công.
