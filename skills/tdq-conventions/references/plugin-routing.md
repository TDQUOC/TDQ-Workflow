# Định tuyến việc → plugin (lazy-load)

Nguồn sự thật duy nhất về tier: `~/.claude/plugin-tiers.json`.
`always_off` = cấm bật. `on_demand` = tắt mặc định cho nhẹ context; hook SessionStart/SessionEnd
chạy `plugin_tiers.py reset` để tắt lại nhóm này.

## Giao thức bật — đúng 2 bước, không thêm bước nào

1. **ĐỀ XUẤT rồi HỎI user** (đưa vào vòng interview hoặc bảng option). Chưa hỏi thì CẤM bật.
2. User đồng ý → chạy `python3 ~/.claude/scripts/plugin_tiers.py enable <tên>` rồi in đúng
   1 dòng: `➤ Gõ /reload-plugins để nạp plugin vào phiên.`

Cấm bật bằng đường khác: `claude plugin enable`, sửa `settings.json` bằng tay.
Review code → dùng built-in `/code-review`, không bật plugin review khác.
User muốn một plugin luôn bật/luôn tắt lâu dài → sửa danh sách trong `~/.claude/plugin-tiers.json`
(xoá khỏi `on_demand` thì hook không tắt nó nữa), chỉ khi user yêu cầu rõ.

## Bảng định tuyến

Chỉ dùng đúng tên ở cột phải.

| Việc chạm tới | Bật plugin |
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

Việc không khớp dòng nào → không bật gì, làm bằng công cụ sẵn có.
