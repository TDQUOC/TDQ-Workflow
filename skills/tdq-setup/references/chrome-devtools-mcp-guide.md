# Hướng Dẫn: Cài Đặt & Cấu Hình Chrome DevTools MCP Cho Claude Code

Tài liệu tóm lược cách tích hợp **Google Chrome** với **Claude Code** qua **Chrome DevTools MCP**, cấu hình bypass quyền 2 tầng và cơ chế auto-launch. Chi tiết script nâng cao xem tại [chrome-devtools-mcp-scripts.md](chrome-devtools-mcp-scripts.md).

## 1. Tổng Quan Kiến Trúc
```
Claude Code CLI <--(stdio)--> chrome-devtools-mcp <--(CDP WebSocket:9222)--> Google Chrome (ChromeDevProfile)
```

## 2. Cài Đặt MCP Server
Đăng ký server vào `~/.claude.json`:
```json
{
  "mcpServers": {
    "chrome-devtools": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest", "--browserUrl=http://127.0.0.1:9222"]
    }
  }
}
```

## 3. Bypass Quyền 2 Tầng (Zero-Prompt Setup)

### Tầng 1: Phía Claude Code CLI
Thêm quyền vào `~/.claude/settings.json`:
```json
{
  "permissions": {
    "allow": ["mcp__chrome-devtools__*", "mcp__chrome_devtools__*"]
  }
}
```

### Tầng 2: Phía Google Chrome
Khởi chạy Chrome với profile cách ly và mở origin:
```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%USERPROFILE%\ChromeDevProfile" --remote-allow-origins=*
```

## 4. Khắc Phục Sự Cố Thường Gặp

| Hiện tượng | Nguyên nhân | Cách xử lý |
|---|---|---|
| `ECONNREFUSED 127.0.0.1:9222` | Chrome chưa bật cờ debug | Chạy lệnh `python3 scripts/tdq_devtool_mcp.py launch` |
| Cảnh báo bảo mật màu cam | Thiếu cờ origin | Thêm cờ `--remote-allow-origins=*` vào lệnh Chrome |
| Hỏi Allow/Deny liên tục | Chưa cấu hình wildcard | Thêm `"mcp__chrome-devtools__*"` vào `settings.json` |
| Profile bị lock | Tiến trình Chrome cũ chưa tắt | Tắt tiến trình Chrome trong Task Manager |
