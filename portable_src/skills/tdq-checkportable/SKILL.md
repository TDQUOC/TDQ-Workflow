---
name: tdq-checkportable
description: Use when a TDQ portable bundle has just been copied into a project, before running any other TDQ skill - verifies manifest.json checksums, Python/command/MCP requirements, and self-heals what is missing.
---

# TDQ Checkportable — kiểm bản portable & tự vá

Chạy skill này **trước mọi skill TDQ khác** ở một project vừa được chép bản portable vào.
Bản portable đi qua tay người: file rơi rớt, bị sửa dọc đường, Python quá cũ, lệnh ngoài
chưa cài — cả bốn đều biểu hiện muộn dưới dạng lỗi khó hiểu giữa một request đang chạy dở.

## Bước 1 — kiểm

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_checkportable.py" check
```

Đọc kết quả theo tiền tố: `SẠCH` xong việc · `THIẾU` chưa có · `LỆCH` nội dung khác manifest ·
`LƯU Ý` việc chỉ người dùng làm được.

## Bước 2 — vá khi có `THIẾU`/`LỆCH`

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_checkportable.py" setup
```

Lệnh này dựng lại được đúng hai file mà bundle có đủ dữ liệu để tái tạo: `.claude/settings.json`
(từ `hooks.json` đi kèm, giữ nguyên khối `env` bạn đã thêm) và `.mcp.json`. Ghi đè thì luôn
để lại `<file>.tdq-bak-<timestamp>`, và việc đã làm được in ra cuối lệnh.

File khác `THIẾU`/`LỆCH` thì nó in `CÒN …` rồi exit khác 0 — **chép lại từ bản gốc**, đừng sửa
tay và đừng bịa nội dung: manifest là bản án cuối, còn nội dung đúng chỉ có ở nguồn.

## Bước 2b — chỉ với bundle Codex: `LƯU Ý project chưa trusted`

Codex bỏ qua TOÀN BỘ tầng `.codex/` của project chưa được tin cậy — MCP không nạp, hook
không đọc, bundle trông như rỗng. Hỏi người dùng rồi mới chạy:

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_checkportable.py" setup --trust
```

Đây là lệnh DUY NHẤT của bộ này ghi ra ngoài bundle (`config.toml` của Codex ở `~/.codex`
hoặc `$CODEX_HOME`). Nó luôn để lại `<file>.tdq-bak-<timestamp>` và không ghi chồng block đã
có. Không có cờ `--trust` thì `setup` không đụng tới file đó.

## Bước 3 — báo những việc máy không làm thay được

Các thứ sau chỉ người dùng bấm được, `setup` không vượt qua được:

1. Cấp quyền tin cậy thư mục project ở lần mở đầu tiên (`setup --trust` thay được bước này).
2. **Chỉ với Codex:** duyệt hook trong giao diện — hook có cổng tin cậy RIÊNG, `--trust`
   không mở được, và mỗi lần `hooks.json` đổi là phải duyệt lại.
3. Duyệt từng MCP server (`LƯU Ý` liệt kê đúng tên).
4. Khởi động lại phiên để skill/agent trong thư mục mới được nạp.

Nói thẳng những việc này cho người dùng thay vì im lặng chờ — im lặng thì họ tưởng đã xong.

## Luật khoá bí mật

Chỉ nhắc **TÊN** biến môi trường, không bao giờ in giá trị khoá ra chat, log hay lệnh shell.

Xong khi: `check` exit 0, và ba việc thủ công đã được báo cho người dùng.
Bước kế tiếp: chạy skill `tdq-intake` như bình thường.
