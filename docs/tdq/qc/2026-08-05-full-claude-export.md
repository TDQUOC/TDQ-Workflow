# QC — Full claude export (multi-repo local dependency)

Ngày: 2026-08-05 · Plan: ../plan/2026-08-05-full-claude-export.md · Spec: ../spec/2026-08-05-full-claude-export.md

| # | Hạng mục | Verdict | Bằng chứng |
|---|---|---|---|
| Q1 | Test suite `claude_export` | PASS | `cd tests && python3 -m unittest test_claude_export -v` → `Ran 64 tests in 8.546s / OK` (46 test cũ + 18 test mới, 0 fail) |
| Q2 | Build bundle thật | PASS | `python3 scripts/claude_export.py build --dest ~/Documents/claude-code-export --zip` → exit 0; log có dòng `quét secret: sạch`, không có dòng cảnh báo secret sót; kết thúc bằng `xong · 2121 file · 2 repo · commit 453e3702 · plugin 0.8.0` |
| Q3 | Drift check ngay sau build | PASS | `python3 scripts/claude_export.py check --dest ~/Documents/claude-code-export` → exit 0, in `0 mục lệch` |
| Q4 | Cấu trúc bundle | PASS | Agent `tdq-qc-tester` (chạy độc lập trên bundle thật, không phải test giả lập): `ls` top-level đủ `README.md`/`config/`/`manifest.json`/`mem0-repo/`/`tdqworkflow-repo/`; `manifest.json["repos"]` có 2 entry (`tdqworkflow-repo`@453e3702, `mem0-repo`@bb3ad38a) khớp `git log -1` từng repo trong bundle; xác nhận tồn tại `tdqworkflow-repo/.git`, `mem0-repo/.git`, `config/skills-graphify/`, `config/skills-mem0-memory/`, `config/launch-agents/com.mem0.gateway.plist` |
| Q5 | Zip toàn vẹn | PASS | `unzip -t ~/Documents/claude-code-export.zip` → kết thúc bằng `No errors detected in compressed data of ...claude-code-export.zip.` |
| Q6 | Secret scan sạch | PASS | Log build có dòng `quét secret: sạch`; agent `tdq-qc-tester` đọc TAVILY key thật từ `~/.claude/settings.json` (không in ra) rồi `grep -rl` toàn bộ bundle → 0 match cho cả `TAVILY_API_KEY_PRIMARY` và `TAVILY_API_KEY_BACKUP`; `config/settings.json` trong bundle chỉ chứa placeholder `<TAVILY_API_KEY_PRIMARY — điền lại>`/`<TAVILY_API_KEY_BACKUP — điền lại>` |

## Cộng thêm (ngoài bảng Q1–Q6)

- `claude-export/EXPORT_LOG.md`: đã thêm mốc `2026-08-05 18:54` (EXPORT_DEST + tóm tắt build).
- `docs/workinglog/2026-08-05.md`: đã append mục `18:48–19:00` (file đổi, lý do, kiểm tra đã chạy).
- Bundle cũ tại `~/Documents/claude-code-export` (+ `.zip`) đã bị đè bởi bundle mới cùng vị trí — không tạo thư mục mới.

## Kết luận

6/6 hạng mục PASS, không có defect. Không cần thêm task fix vào mục "QC bổ sung" của plan.
