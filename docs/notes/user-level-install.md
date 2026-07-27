# Hướng dẫn tự cài tdq-workflow ở user-level (thủ công)

Plugin này mặc định chỉ chạy trong repo (`claude --plugin-dir …`) và **không bao giờ tự cài user-level**. Nếu bạn muốn mọi project đều có, tự làm các bước sau.

## 1. Cài qua local marketplace

```bash
# thêm repo này làm marketplace (chạy 1 lần)
claude plugin marketplace add /Users/truongdinhquoc/Documents/TDQWorkflow
# cài plugin ở scope user
claude plugin install tdq-workflow --scope user
```
Kiểm tra: mở session mới bất kỳ → gõ `/tdq-workflow:tdq-status` → phải trả "Chưa có request TDQ nào đang chạy…".

Lưu ý: repo chưa có file `.claude-plugin/marketplace.json` thì lệnh add sẽ báo thiếu — tạo tối thiểu:
```json
{
  "name": "tdq-local",
  "owner": { "name": "TDQ" },
  "plugins": [{ "name": "tdq-workflow", "source": "./" }]
}
```

## 2. Đồng bộ rule working log ở `~/.claude/CLAUDE.md`

Rule user-level hiện ghi log vào `docs/superpowers/workinglog/YYYY-MM-DD.md`, còn plugin dùng `docs/workinglog/YYYY-MM-DD.md`. Nếu giữ nguyên sẽ có 2 chỗ log lệch nhau. Sửa mục 7 trong `~/.claude/CLAUDE.md`:

- Đổi mọi `docs/superpowers/workinglog/` → `docs/workinglog/`.

(Hook `stop_gate`/`edit_gate` của plugin chỉ nhìn `docs/workinglog/`.)

## 3. Gỡ

```bash
claude plugin uninstall tdq-workflow --scope user
claude plugin marketplace remove tdq-local
```

## Lưu ý an toàn
- Hook chặn ghi trực tiếp `docs/tdq/state.json` áp dụng ở mọi project đã bật plugin — duyệt gate chỉ bằng `/tdq-workflow:tdq-approve …`.
- Cập nhật plugin: sửa trong repo này rồi `claude plugin marketplace update tdq-local` (hoặc gỡ/cài lại).
