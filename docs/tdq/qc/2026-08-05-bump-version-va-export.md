# QC — Bump 0.7.0 + bộ export Claude Code

Ngày: 2026-08-05 · Plan: ../plan/2026-08-05-bump-version-va-export.md · Vòng: 1 (agent `tdq-qc-tester` chạy độc lập, chỉ đọc repo)

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Version + changelog | `cd tests && python3 -m unittest test_docs_consistency` | `Ran 5 tests OK`, `plugin.json` = `0.7.0`, mục đầu CHANGELOG là `## 0.7.0 — 2026-08-05` | PASS |
| Q2 | Suite đầy đủ | `cd tests && python3 -m unittest discover -s . -p "test_*.py"` | `Ran 565 tests OK` lúc QC, `567` sau 2 ca vá | PASS |
| Q3 | Lint tài liệu | `python3 scripts/doc_lint.py claude-export skills portable docs/tdq` | exit 1, 101 vi phạm — **0/101 thuộc request này**; bản thu hẹp theo file của request exit 0 | FAIL (câu chữ) / PASS (phạm vi) |
| Q4 | Bundle không rác | `find <dest> -name '.DS_Store' -o -name 'state.json' -o -path '*graphify-out/20*'` | 0 dòng; dò thêm `.tdq-turn.jsonl`, `*.pyc`, `__pycache__` cũng rỗng | PASS |
| Q5 | Bundle có `.git` | `git -C <dest>/tdqworkflow-repo log --oneline -1` | trùng HEAD máy nguồn, `git status` trong clone rỗng | PASS |
| Q6 | Bundle có MCP | đọc `<dest>/config/mcp-servers.json` | `['tavily-backup', 'tavily-primary']` | PASS |
| Q7 | Không lộ secret | script nạp key vào biến rồi quét 1642 file + 1642 entry zip | 0 file trùng; gieo secret vào file tạm thì bộ quét bắt được 1 → chứng minh phép quét hoạt động | PASS |
| Q8 | manifest đủ khoá | đọc `sorted(<dest>/manifest.json)` | đúng 8 khoá, có đủ `plugin_version`/`repo_commit`/`exported_at`/`source_files` | PASS |
| Q9 | `check` sạch sau `build` | `python3 scripts/claude_export.py check --dest <dest>` | `0 mục lệch`, exit 0 | PASS |
| Q10 | `check` bắt drift | bundle nhân bản trong scratchpad: sửa 1 file nguồn, xoá 1 file nguồn, tiêm SHA giả | `nội dung đã đổi` + `thiếu ở nguồn` + drift commit, exit 1 | PASS |
| Q11 | Zip hợp lệ | `unzip -t ~/Documents/claude-code-export.zip` | `No errors detected`, 1642 entry | PASS |
| Q12 | Log export | `tail -2 claude-export/EXPORT_LOG.md` | 2 dòng mốc `2026-08-05`, số liệu khớp `find`/`du` thật | PASS |

Spec §4 (log mặc định có timestamp, `--quiet` tắt hẳn, `--verbose` thêm debug, test riêng từng thành phần, không TODO/stub, exit code đúng cho đích lạ `2` / secret sót `3`): 6/6 PASS.

Hợp đồng skill trong plan: `tdq-spec` (doc_lint spec exit 0) · `tdq-plan` (0 ô trống) · `tdq-build` (report 8 dòng ≤ 10) · `tavily-search` (`Truy vấn 4` có trong research) · `graphify` (graph rebuild cuối turn) — cả 5 đều có artifact thật.

## Defect QC phát hiện

1. **Đã sửa** — `manifest.json` hỏng JSON làm `check` văng traceback và trả `1` (nghĩa "có drift") trong khi hợp đồng script ghi `2` = bundle không hợp lệ. Vá ở `cmd_check`, thêm ca `test_broken_manifest_exits_2_without_traceback`.
2. **Đã sửa** — `check` in `(+?)` khi SHA cũ không còn trong repo. Nay in `(không so được khoảng cách — SHA cũ không có trong repo)`, thêm ca `test_unknown_old_commit_says_so_instead_of_question_mark`.
3. **Chưa sửa, đã ghi spec §7** — `check` chỉ đo drift phía NGUỒN. Xoá `tdqworkflow-repo/` hay sửa file ngay trong bundle thì vẫn báo `0 mục lệch`. Đúng câu chữ Q10 nhưng là lỗ hổng khi bundle rơi file lúc truyền sang máy khác. Cần lệnh `verify --dest` ở request sau.
4. **Chưa sửa, đã ghi spec §7** — DoD Q3 tự mâu thuẫn: bảng §6 đòi exit 0 trên toàn `docs/tdq` trong khi nợ cũ 101 vi phạm nằm ngoài phạm vi request.

## Kết luận

11/12 PASS theo đúng câu chữ spec §6 (Q3 FAIL vì nợ cũ), 12/12 theo phạm vi file của request này. 2 defect chức năng đã vá và có test, 2 khoảng trống còn lại đã ghi vào spec §7. Không có giá trị API key thật xuất hiện ở bundle, zip, log hay tài liệu QC.
