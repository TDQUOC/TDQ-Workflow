# TDQ Workflow — hướng dẫn cho agent

Soul: chất lượng > runtime > context cost · luật gốc: `workflow/references/tdq-conventions/soul.md`

Bộ này chạy theo pipeline có cổng duyệt: intake → spec → plan → implement → QC → report.
Chỉ NGƯỜI DÙNG được duyệt, và mọi thay đổi state chỉ đi qua `scripts/tdq_state.py`.

## Bước 0 — kiểm tương thích TRƯỚC mọi việc khác

```
python3 scripts/tdq_checkportable.py check
```

Báo thiếu thì chạy `python3 scripts/tdq_checkportable.py setup`: nó dựng lại hai file cấu
hình tái tạo được (`.claude/settings.json`, `.mcp.json`), luôn sao lưu `<file>.tdq-bak-<timestamp>`
trước khi ghi đè, và báo `CÒN …` cho phần chỉ chép lại từ bản gốc mới đúng.

Dòng `LƯU Ý project chưa trusted` là dòng quan trọng nhất của lệnh này: chưa trusted thì
Codex bỏ qua cả `.codex/config.toml` lẫn `.codex/hooks.json`, bundle chạy như thể không có.

## Chạy trên Codex CLI (>= 0.147.0) — dùng lớp native, không cần đọc `workflow/`

- `.agents/skills/` — Codex tự nạp skill theo `description`, không phải tự chọn file.
- `.codex/config.toml` — MCP server; chỉ TÊN biến môi trường, tự đặt biến ở máy mình.
- `.codex/hooks.json` + `hooks/` — cổng duyệt do máy canh (`SessionStart`,
  `UserPromptSubmit`, `PreToolUse` cho `Bash` và `apply_patch`, `Stop`).

## Harness khác — đọc `workflow/` theo đúng số thứ tự

Không có skill system thì số thứ tự trong tên file CHÍNH LÀ cơ chế định tuyến:

- `workflow/01-conventions.md`
- `workflow/02-intake.md`
- `workflow/03-spec.md`
- `workflow/04-plan.md`
- `workflow/05-build.md`
- `workflow/06-checkportable.md`
- `workflow/07-status.md`
- `workflow/08-check-status.md`

Bảng phase đầy đủ: `workflow/phases.md` (tự sinh từ hằng `PHASE_TABLE`, không sửa tay).

## Bốn việc máy KHÔNG tự làm được

1. Cấp quyền cho thư mục project ở lần chạy đầu (`setup --trust` làm thay được bước này).
2. Duyệt hook trong giao diện Codex — hook có cổng tin cậy riêng, `--trust` KHÔNG mở được.
3. Duyệt từng MCP server khai trong `.codex/config.toml`.
4. Khởi động lại phiên sau khi thêm thư mục instruction mới.
