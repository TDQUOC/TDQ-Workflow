# PLAN — Bump 0.7.0 + bộ export Claude Code chạy bằng một lệnh

Ngày: 2026-08-05 · Spec: ../spec/2026-08-05-bump-version-va-export.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — P2→P4 cùng sửa một file `scripts/claude_export.py` nên không chia song song được, còn P6 phải chạy trên chính máy nguồn (đọc `~/.claude`, ghi `~/Documents`) mà worktree của subagent sẽ clone sai bản. (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: ĐÃ DUYỆT (2026-08-05T04:01:29+07:00, mode main)

## Năng lực → task

| Skill | Task | Đầu ra bắt buộc |
|---|---|---|
| tdq-spec | T7.4 | mục §7 spec được đóng hoặc ghi câu hỏi mới, `doc_lint.py` exit 0 |
| tdq-plan | T7.5 | mọi task trong file này có `[x]`, task fix của QC nằm ở mục QC |
| tdq-build | QC-1 | `docs/tdq/reports/2026-08-05-bump-version-va-export.md` ≤10 dòng |
| tavily-search | T5.2 | mục nguồn mới trong `docs/tdq/research/2026-08-05-bump-version-va-export.md` |
| graphify | T7.3 | `graphify-out/graph.json` có mtime sau lần sửa code cuối |

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: viết test trước (đỏ) → code → test xanh → tick `[x]` NGAY vào file này.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Test của P2–P4 chỉ được đọc/ghi trong thư mục tạm; cấm trỏ vào `~/.claude` hay `~/Documents` thật.
8. Không in giá trị API key ra bất kỳ đâu — chỉ so khớp qua biến, chỉ in tên khoá.

## P1 — Bump 0.7.0

- [x] **T1.1** Đổi `version` trong `.claude-plugin/plugin.json` từ `0.6.2` sang `0.7.0` — Test (đỏ trước): `cd tests && python3 -m unittest test_docs_consistency` phải FAIL đúng `test_changelog_documents_current_version`
- [x] **T1.2** Thêm mục `## 0.7.0 — 2026-08-05` lên đầu `CHANGELOG.md`, tóm tắt 5 commit sau `0.6.2` cộng bộ export mới — Test: `cd tests && python3 -m unittest test_docs_consistency` xanh

**Xong P1 khi**: `test_docs_consistency` xanh và dòng `## 0.7.0` là mục đầu của `CHANGELOG.md`.

## P2 — Khung `claude_export.py` + lớp thu thập nguồn

- [x] **T2.1** Tạo `tests/test_claude_export.py` với ca đỏ đầu tiên: import được module và `parse_args` nhận 2 lệnh con `build`, `check` — Test: `cd tests && python3 -m unittest test_claude_export` FAIL vì thiếu module
- [x] **T2.2** Viết `scripts/claude_export.py`: `parse_args`, khung 2 lệnh con, hàm `log(msg, level)` in `<ISO timestamp> <mức> <msg>` ra stderr, cờ `--quiet` tắt hẳn và `--verbose` mở mức debug — Test: ca kiểm `--quiet` cho stderr rỗng, mặc định có ≥1 dòng chứa `2026-`
- [x] **T2.3** Hàm `read_mcp_servers(path)` đọc khoá `mcpServers` của một file kiểu `~/.claude.json` (mở chế độ chỉ đọc, không ghi) và trả về dict — Test: file tạm 2 server giả trả đúng 2 tên, file thiếu khoá trả dict rỗng
- [x] **T2.4** Hàm `scan_secrets(root, values)` duyệt mọi file văn bản dưới `root` · trả danh sách đường dẫn chứa bất kỳ chuỗi nào trong `values` — Test: thư mục tạm có 1 file chứa chuỗi bí mật giả → trả đúng 1 đường dẫn; không có → trả rỗng
- [x] **T2.5** Hàm `sha256_of(path)` và `collect_config_files(claude_home)` liệt kê file cấu hình cần mang theo kèm sha256 — Test: cây tạm 3 file cho ra 3 mục, đổi 1 byte thì sha256 đổi

**Xong P2 khi**: 5 hàm trên có test riêng và `cd tests && python3 -m unittest test_claude_export` xanh.

## P3 — Lệnh `build`

- [x] **T3.1** `build --dest <dir>`: chỉ ghi đè khi đích trống, chưa tồn tại, hoặc chứa `manifest.json` có khoá `exported_at` do chính script sinh; đích lạ → log lỗi và exit `2` — Test: 3 ca (đích trống, đích có manifest hợp lệ, đích lạ có file rác) cho 3 exit code đúng
- [x] **T3.2** Bản copy repo: `git clone <repo> <dest>/tdqworkflow-repo` rồi copy thêm `.remember/` có lọc bỏ `tmp/` và `logs/` — Test: bundle tạm có `tdqworkflow-repo/.git`, có `.remember/core-memories.md`, KHÔNG có `.remember/tmp`
- [x] **T3.3** Copy cấu hình `~/.claude` (đường dẫn tiêm qua tham số `--claude-home`) sang `<dest>/config/`, và ghi `<dest>/config/mcp-servers.json` từ `read_mcp_servers` — Test: cây `~/.claude` giả cho ra `config/settings.json` + `config/mcp-servers.json` đúng 2 tên server
- [x] **T3.4** Ghi `<dest>/manifest.json` đúng 8 khoá: `plugin_version`, `repo_commit`, `exported_at`, `source_files`, `plugins`, `marketplaces`, `mcp_servers`, `cli_dependencies` (bỏ `excluded` vì `git clone` đã thi hành loại trừ) — Test: `sorted(json.load(...))` bằng đúng 8 tên trên; `repo_commit` khớp `git rev-parse HEAD`
- [x] **T3.5** Sau khi sinh xong, `build` chạy `scan_secrets` với giá trị thật của `TAVILY_API_KEY_PRIMARY`/`TAVILY_API_KEY_BACKUP` lấy từ môi trường; dính thì xoá cả `<dest>` và exit `3` — Test: tiêm secret giả qua tham số, bundle bị xoá sạch và exit `3`
- [x] **T3.6** Cờ `--zip` nén bundle ra `<dest>.zip.tmp` rồi mới `os.replace` đè lên `<dest>.zip` — Test: zip cũ vẫn nguyên khi nén lỗi giữa chừng; chạy thành công thì `zipfile.ZipFile(...).testzip()` trả `None`

**Xong P3 khi**: `build` sinh được bundle vào thư mục tạm, 6 ca trên xanh, không ca nào chạm `~/.claude` thật.

## P4 — Lệnh `check` (đo drift)

- [x] **T4.1** `check --dest <dir>` đọc `manifest.json`, tính lại sha256 từng mục `source_files` ở nguồn, in bảng `file · trạng thái` cho các mục lệch — Test: bundle tạm chưa đổi gì thì bảng rỗng
- [x] **T4.2** `check` in `0 mục lệch` và exit `0` khi sạch; có lệch thì in số mục và exit `1` — Test: 2 ca exit code, ca lệch phải nêu đúng tên file đã sửa
- [x] **T4.3** `check` so `repo_commit` trong manifest với `git rev-parse HEAD` hiện tại, lệch thì tính là một mục drift kèm 2 SHA rút gọn — Test: manifest tiêm SHA giả → exit `1` và output chứa cả 2 SHA

**Xong P4 khi**: 3 ca xanh và `check` chạy ngay sau `build` trên thư mục tạm cho exit `0`.

## P5 — Tài liệu bộ export

- [x] **T5.1** Viết lại `claude-export/INSTRUCTIONS.md`: thay 7 bước tay bằng một lệnh `build`, giữ mục "kiểm sau khi sinh" và mục ghi `EXPORT_LOG.md` — Test: `python3 scripts/doc_lint.py claude-export` exit 0
- [x] **T5.2** Viết lại `claude-export/README.template.md`: thêm mục khôi phục MCP bằng `claude mcp add-json <name> '<json>' --scope user`, thêm `claude doctor` vào mục verify, nêu rõ cấm copy đè `~/.claude.json` — Test: `grep -c "claude mcp add-json" claude-export/README.template.md` ≥ 1 và `doc_lint.py` exit 0
  - Dùng: `tavily-search` (mcp)
  - Nạp: gọi skill `tavily-search` TRƯỚC bước đỏ của task này. Agent ngoài không có skill system: đọc `~/.claude/plugins/cache/claude-plugins-official/tavily/1.0.0/skills/tavily-search/SKILL.md` rồi làm theo.
  - Để: xác minh lại cú pháp `claude mcp add-json --scope user` và `claude doctor` còn đúng ở bản CLI hiện hành trước khi ghi vào README template.
  - Ra: mục "Truy vấn 4" trong `docs/tdq/research/2026-08-05-bump-version-va-export.md` có nguồn và kết luận.
  - Kiểm: `grep -c "Truy vấn 4" docs/tdq/research/2026-08-05-bump-version-va-export.md` trả 1.
  - Không dùng cho: tra cứu nội dung file trong repo — việc đó đọc thẳng bằng Read.
- [x] **T5.3** Viết lại `claude-export/MANIFEST.template.json` thành đúng 8 khoá của T3.4, mỗi khoá có giá trị mẫu rỗng đúng kiểu — Test: `python3 -m json.tool claude-export/MANIFEST.template.json` exit 0 và số khoá bằng 8

**Xong P5 khi**: 3 file trong `claude-export/` khớp hành vi thật của script, `doc_lint.py` trên thư mục đó exit 0.

## P6 — Sinh bundle thật + zip

- [x] **T6.1** Chạy `build` ghi đè `~/Documents/claude-code-export` kèm `--zip`; trước đó đổi tên zip cũ thành `claude-code-export.zip.bak-20260805` để có bản lùi — Test: lệnh exit 0, thư mục có `manifest.json` mới
- [x] **T6.2** Kiểm bundle theo Q4–Q6: không có `.DS_Store`/`state.json`/`graphify-out/20*`, có `tdqworkflow-repo/.git` log được, có `config/mcp-servers.json` đúng 2 server — Test: đúng 3 lệnh của spec §6 Q4, Q5, Q6
- [x] **T6.3** Kiểm Q7 (không lộ secret) và Q8 (manifest 8 khoá) — Test: `grep -rF` với giá trị lấy từ biến môi trường trả 0 kết quả; danh sách khoá manifest in ra đủ 8 tên
- [x] **T6.4** Kiểm Q9 và Q10: `check` ngay sau `build` cho exit 0; nhân bản bundle sang thư mục tạm, sửa 1 file rồi `check` lại phải exit 1 và nêu đúng tên file — Test: 2 exit code như trên
- [x] **T6.5** Kiểm Q11 rồi ghi 2 dòng mốc `2026-08-05` vào `claude-export/EXPORT_LOG.md` (kích thước bundle, số file, commit SHA, đường dẫn zip) — Test: `unzip -t ~/Documents/claude-code-export.zip` in `No errors detected` và `tail -2 claude-export/EXPORT_LOG.md` ra 2 dòng mốc mới

**Xong P6 khi**: Q4–Q12 trừ Q1–Q3 đều có bằng chứng chạy thật, zip mới hợp lệ, bản lùi `.bak` còn giữ.

## P7 — Log & test bắt buộc

- [x] **T7.1** Log service bật mặc định: mọi bước của `build`/`check` có dòng log ISO timestamp ra stderr, tắt bằng `--quiet` — Test: ca `test_log_default_on` và `test_quiet_silences_log` trong `tests/test_claude_export.py`
- [x] **T7.2** Chạy toàn bộ suite bằng một lệnh — Test: `cd tests && python3 -m unittest discover -s . -p "test_*.py"` 0 fail, tổng số test ≥ 521
- [x] **T7.3** Lint tài liệu và rebuild code graph — Test: `python3 scripts/doc_lint.py claude-export skills portable docs/tdq` exit 0, rồi `graphify extract . --code-only` chạy xong
  - Dùng: `graphify`
  - Nạp: gọi skill `graphify` TRƯỚC bước đỏ của task này. Agent ngoài không có skill system: đọc `~/.claude/skills/graphify/SKILL.md` rồi làm theo.
  - Để: dựng lại code graph sau khi thêm `scripts/claude_export.py` và test đi kèm.
  - Ra: `graphify-out/graph.json` và `graphify-out/GRAPH_REPORT.md` cập nhật.
  - Kiểm: `python3 -c "import json;print(len(json.load(open('graphify-out/graph.json'))['nodes']))"` in số node lớn hơn lần trước.
  - Không dùng cho: sinh tài liệu cho user — báo cáo do `tdq-build` viết.
- [x] **T7.4** Đối chiếu bundle vừa sinh với spec §6, cập nhật §7 của spec (đóng lại hoặc ghi câu hỏi mới phát sinh) — Test: `python3 scripts/doc_lint.py docs/tdq/spec` exit 0
  - Dùng: `tdq-spec`
  - Nạp: gọi skill `tdq-spec` TRƯỚC bước đỏ của task này. Agent ngoài không có skill system: đọc `skills/tdq-spec/SKILL.md` rồi làm theo.
  - Để: giữ spec là nguồn chuẩn duy nhất của DoD, ghi lại chênh lệch giữa spec và thứ thật sự sinh ra.
  - Ra: `docs/tdq/spec/2026-08-05-bump-version-va-export.md` mục §7 có nội dung dứt khoát.
  - Kiểm: `grep -n "## 7" docs/tdq/spec/2026-08-05-bump-version-va-export.md` ra đúng 1 dòng.
  - Không dùng cho: đổi §2 hay §6 của spec đã duyệt — muốn đổi phải hỏi user.
- [x] **T7.5** Tick `[x]` cho mọi task đã pass, thêm task fix vào mục QC nếu QC báo FAIL — Test: `grep -c "^- \[ \]" docs/tdq/plan/2026-08-05-bump-version-va-export.md` trả 0
  - Dùng: `tdq-plan`
  - Nạp: gọi skill `tdq-plan` TRƯỚC bước đỏ của task này. Agent ngoài không có skill system: đọc `skills/tdq-plan/SKILL.md` rồi làm theo.
  - Để: giữ file plan phản ánh đúng trạng thái thật, thêm task fix theo quy tắc thi hành số 5.
  - Ra: `docs/tdq/plan/2026-08-05-bump-version-va-export.md` không còn ô chưa tick.
  - Kiểm: `python3 scripts/doc_lint.py --pair docs/tdq/spec/2026-08-05-bump-version-va-export.md docs/tdq/plan/2026-08-05-bump-version-va-export.md` exit 0.
  - Không dùng cho: viết plan cho request khác — mỗi request một file plan riêng.

**Xong P7 khi**: suite xanh, lint exit 0, graph rebuild xong, plan không còn ô trống.

## QC

- [x] **QC-1** Giao `tdq-qc-tester` kiểm độc lập Q1–Q12 của spec §6, rồi viết report ≤10 dòng — Test: agent trả PASS 12/12 và `docs/tdq/reports/2026-08-05-bump-version-va-export.md` ≤10 dòng
  - Dùng: `tdq-build`
  - Nạp: gọi skill `tdq-build` TRƯỚC bước đỏ của task này. Agent ngoài không có skill system: đọc `skills/tdq-build/SKILL.md` rồi làm theo.
  - Để: điều phối thực thi plan, giao QC cho agent độc lập, viết report cuối theo khuôn.
  - Ra: `docs/tdq/reports/2026-08-05-bump-version-va-export.md`.
  - Kiểm: `wc -l < docs/tdq/reports/2026-08-05-bump-version-va-export.md` trả số ≤ 10.
  - Không dùng cho: tự chấm PASS cho chính mình — QC do agent khác chạy.
- [x] **QC-2** Vá 2 khiếm khuyết QC báo: manifest hỏng phải exit `2` kèm thông điệp tiếng Việt thay vì traceback exit `1`; `check` không in `(+?)` khi SHA cũ không có trong repo — Test: `cd tests && python3 -m unittest test_claude_export.CheckTest` xanh với 2 ca mới
- [x] **QC-3** Sinh lại bundle + zip sau khi vá để bản export mang đúng script đã sửa — Test: `git -C ~/Documents/claude-code-export/tdqworkflow-repo log --oneline -1` khớp HEAD mới và `check` ra `0 mục lệch`

(Task fix phát sinh từ QC thêm vào ngay dưới dòng này.)

## Definition of Done

Trỏ về §6 của spec. Cả 12 hạng mục phải PASS:

| # | Hạng mục | Lệnh kiểm | Task phụ trách |
|---|---|---|---|
| Q1 | Version + changelog | `cd tests && python3 -m unittest test_docs_consistency` | T1.1, T1.2 |
| Q2 | Suite đầy đủ | `cd tests && python3 -m unittest discover -s . -p "test_*.py"` | T7.2 |
| Q3 | Lint tài liệu | `python3 scripts/doc_lint.py claude-export skills portable docs/tdq` | T7.3 |
| Q4 | Bundle không rác | `find <dest> -name '.DS_Store' -o -name 'state.json' -o -path '*graphify-out/20*'` | T6.2 |
| Q5 | Bundle có `.git` | `git -C <dest>/tdqworkflow-repo log --oneline -1` | T6.2 |
| Q6 | Bundle có MCP | đọc `<dest>/config/mcp-servers.json`, in danh sách tên server | T6.2 |
| Q7 | Không lộ secret | `grep -rF "$TAVILY_API_KEY_PRIMARY" <dest>` trả rỗng | T3.5, T6.3 |
| Q8 | manifest đủ khoá | in `sorted(json.load(open('<dest>/manifest.json')))` | T3.4, T6.3 |
| Q9 | `check` sạch sau `build` | `python3 scripts/claude_export.py check --dest <dest>` | T6.4 |
| Q10 | `check` bắt được drift | sửa 1 file trong bản nhân bản tạm rồi `check` lại | T4.2, T6.4 |
| Q11 | Zip hợp lệ | `unzip -t ~/Documents/claude-code-export.zip` | T6.5 |
| Q12 | Log export | `tail -2 claude-export/EXPORT_LOG.md` | T6.5 |

Thêm: 8 lỗ hổng của bundle cũ mỗi lỗ có ít nhất một hạng mục QC chứng minh đã vá · report ≤10 dòng nêu số đo trước/sau · không có key thật trong bundle, log hay report.
