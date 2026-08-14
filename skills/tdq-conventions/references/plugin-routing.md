# Định tuyến việc → plugin

**Trạng thái từ 2026-08-06: TẤT CẢ plugin đã bật sẵn ở user scope.**

## Giao thức dùng

1. Plugin đã bật → **dùng thẳng, không cần xin phép**. Bảng dưới chỉ để chọn đúng plugin
   cho đúng việc, không còn là cổng duyệt.
2. Vẫn phải **HỎI user trước** khi: cài plugin/marketplace MỚI; chạy OAuth hoặc nhập
   credential cho một service; gọi tool **ghi/xoá ra dịch vụ ngoài** (tạo page Notion, ghi
   DB, deploy, upload asset…). Đọc thì tự do.
3. Review code → dùng built-in `/code-review`, không dùng plugin review khác.

## Bảng định tuyến

Chỉ dùng đúng tên ở cột phải.

| Việc chạm tới | Dùng plugin |
|---|---|
| Airflow / DAG / pipeline dữ liệu | data-engineering |
| Hugging Face / train model / dataset ML | huggingface-skills |
| Làm video / motion graphics | hyperframes |
| DataRobot | datarobot-agent-skills |
| Figma / design-to-code | figma |
| Qt / QML | qt-development-skills |
| Cloudflare Workers / Pages / Zero Trust | cloudflare |
| Canva | canva |
| Adobe / Photoshop / sửa ảnh hàng loạt | adobe-for-creativity |
| MongoDB | mongodb |
| Postman / test API collection | postman |
| Thao tác máy ngoài repo (app, file hệ thống) | desktop-commander |
| Base44 | base44 |
| Unreal Engine | unreal-engine-skills-for-claude-code |
| Notion | notion |
| Redis | redis-development |
| Crawl web quy mô lớn | firecrawl |
| Debug trình duyệt qua CDP | chrome-devtools-mcp |
| Review/phân tích repo bằng index ngoài | greptile |
| Quét chất lượng/bảo mật tĩnh | sonarqube |
| Quan sát log / trace | lumen |
| LSP theo ngôn ngữ | `<lang>-lsp` (clangd, gopls, jdtls, kotlin, lua, php, ruby, rust-analyzer, swift, csharp) |

Việc không khớp dòng nào → làm bằng công cụ sẵn có, đừng lôi plugin vào cho nặng context.

## Phụ lục

`~/.claude/plugin-tiers.json` có `always_off` và `on_demand` đều RỖNG → hook
SessionStart/SessionEnd chạy `plugin_tiers.py reset` là no-op, không tắt lại plugin nào.
Bản tier cũ (chế độ lazy-load): `~/.claude/plugin-tiers.json.bak-2026-08-06`.

Muốn quay lại lazy-load cho nhẹ context: thêm tên plugin vào `on_demand` (tắt mặc định,
bật lại bằng `python3 ~/.claude/scripts/plugin_tiers.py enable <tên>`) hoặc `always_off`
(cấm bật) trong `~/.claude/plugin-tiers.json` — chỉ khi user yêu cầu rõ.
