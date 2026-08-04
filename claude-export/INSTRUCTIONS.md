# INSTRUCTIONS — Dựng bundle export cấu hình Claude Code

Từ bản `0.7.0`, việc sinh bundle do `scripts/claude_export.py` lo. Thư mục
`claude-export/` chỉ còn giữ 3 thứ: hướng dẫn này, template README và template
manifest mà script nạp vào lúc chạy, cộng `EXPORT_LOG.md` ghi lịch sử các lần chạy.

Bundle SINH RA nằm ở đường dẫn đích do người chạy chỉ định — KHÔNG bao giờ đặt bên
trong `claude-export/`.

## Sinh bundle

```bash
python3 scripts/claude_export.py build --dest "$HOME/Documents/claude-code-export" --zip
```

Cờ có sẵn:

| Cờ | Mặc định | Dùng khi |
|---|---|---|
| `--dest` | (bắt buộc) | thư mục đích của bundle |
| `--repo` | repo chứa chính script | export một bản checkout khác của TDQWorkflow |
| `--claude-home` | `~/.claude` | máy có thư mục cấu hình khác |
| `--claude-json` | `<cha của claude-home>/.claude.json` | file chứa khối `mcpServers` nằm chỗ khác |
| `--zip` | tắt | muốn thêm file `<dest>.zip` để mang đi |
| `--quiet` / `--verbose` | log mức info | tắt log, hoặc xem thêm dòng debug |
| `--extra-secret` | rỗng | máy nguồn còn giữ key ở nơi script chưa biết |

Exit code: `0` xong · `2` đích không hợp lệ · `3` phát hiện secret còn sót (bundle đã
bị xoá). Log ra stderr, mỗi dòng có timestamp ISO.

## Script làm gì

1. Từ chối ghi đè đích lạ. Chỉ ghi khi đích chưa tồn tại, đang rỗng, hoặc là bundle
   cũ do chính script sinh (nhận biết bằng khoá `exported_at` trong `manifest.json`).
2. `git clone` repo vào `<dest>/tdqworkflow-repo` — giữ `.git`, chỉ lấy file tracked.
   Đây là chỗ thay cho `rsync --exclude` liệt kê tay của bản cũ: rsync không đọc
   `.gitignore` nên bản cũ mang theo `graphify-out/` 15 MB, `docs/tdq/state.json` của
   request đang dở, `.tdq-turn.jsonl` và cả `.DS_Store`.
3. Copy riêng `.remember/` của repo (thư mục này untracked nên clone không lấy), bỏ
   `tmp/` và `logs/`.
4. Copy file cấu hình `~/.claude` sang `<dest>/config/`, tách khối `mcpServers` của
   `~/.claude.json` ra `<dest>/config/mcp-servers.json`.
5. Rewrite đường dẫn marketplace `tdq-local` trong `settings.json` và
   `known_marketplaces.json` trỏ vào repo NẰM TRONG bundle. Thiếu bước này thì plugin
   `tdq-workflow` không load được trên máy đích.
6. Ghi `manifest.json` theo khung `MANIFEST.template.json` (8 khoá), điền thêm phiên
   bản plugin, commit SHA, thời điểm export, và sha256 từng file nguồn.
7. Điền `README.template.md` thành `<dest>/README.md`.
8. Thay mọi giá trị key thật (lấy từ khối `env` của `settings.json`) bằng placeholder
   `<TÊN_BIẾN — điền lại>`, rồi quét lại toàn bundle. Còn sót thì xoá bundle, exit `3`.
9. Nén `<dest>.zip` qua file tạm rồi mới đổi tên đè — nén hỏng giữa chừng thì bản zip
   cũ vẫn còn.

## Đo độ lệch giữa bundle và máy nguồn

```bash
python3 scripts/claude_export.py check --dest "$HOME/Documents/claude-code-export"
```

In bảng các mục đã lệch rồi tổng kết `<n> mục lệch`. Exit `0` khi sạch, `1` khi có
lệch, `2` khi đích không phải bundle. Ba nhóm được đo: file cấu hình đổi nội dung
(so sha256), repo sang commit khác (kèm số commit vượt), phiên bản plugin đã bump.

## Điều script KHÔNG làm

- Không đọc, không sửa, không copy `~/.claude.json` nguyên file — nó chứa
  `oauthAccount`, `machineID`, `userID`. Chỉ lấy đúng khối `mcpServers`.
- Không đưa giá trị key thật vào bundle. Placeholder trong `settings.json` là chủ đích.
- Không copy `history.jsonl`, `sessions/`, `projects/`, `debug/`, `shell-snapshots/`,
  `file-history/`, `telemetry/`, `image-cache/`, `paste-cache/`, `ide/`, `daemon*`,
  `plugins/cache/`, `plugins/data/` — không nằm trong danh sách mang theo.
- Không cài gì lên máy đích. Việc dựng máy đích theo `README.md` trong bundle.

## Ghi log

Mỗi lần chạy thật, thêm 2 dòng vào `claude-export/EXPORT_LOG.md`: một dòng ghi đích,
một dòng tóm tắt kết quả (số file, số plugin, commit, cảnh báo nếu có). Script không tự
ghi log này — nó là sổ tay của người chạy, viết bằng tay hoặc bằng lệnh sau:

```bash
DEST="$HOME/Documents/claude-code-export"
printf '%s — EXPORT_DEST=%s\n' "$(date '+%Y-%m-%d %H:%M')" "$DEST" >> claude-export/EXPORT_LOG.md
printf '%s — %s\n' "$(date '+%Y-%m-%d %H:%M')" "<tóm tắt: số file, số plugin, commit, cảnh báo>" >> claude-export/EXPORT_LOG.md
```
