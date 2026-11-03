# Request — 2026-08-05-rebuild-sync-export

## Nguyên văn user
"có" (trả lời câu hỏi: "Việc rebuild để đồng bộ lại nằm ngoài phạm vi 'chỉ validate'
đã duyệt — bạn có muốn tôi build lại bundle luôn không?")

## Cách hiểu ban đầu
- Mục tiêu: build lại bundle export tại `~/Documents/claude-code-export` (+ `.zip`)
  để đồng bộ với `~/.claude/plugins/{installed_plugins,known_marketplaces}.json`
  hiện tại (khắc phục 2 mục lệch V1 phát hiện ở request `validate-export`).
- Phạm vi đoán: chạy lại đúng lệnh build đã dùng trước
  (`scripts/claude_export.py build --dest ~/Documents/claude-code-export --zip`),
  không sửa code, không đổi `local-repos.json`. Sau build chạy lại `check`/`unzip -t`
  để xác nhận đồng bộ.
- Chỗ chưa rõ: không có — đây là rerun lệnh có sẵn, không phát sinh thiết kế mới.
