# Phần 4: Báo cáo Nghiên cứu, Kiểm toán & Kiểm chứng Thực nghiệm — TDQ-Workflow Antigravity Adapter (`build_portable.py --sinh-agy`) & Bản cài Live (`~/.gemini/config/plugins/tdq-workflow`)

## Tóm tắt Điều hành (Executive Summary)

1. **Giải mã dứt điểm bí ẩn vì sao `tdq-workflow` (11+1 skills, MCP servers, hooks) KHÔNG xuất hiện trong `<skills>` / `<mcp_servers>` của phiên hiện tại**:
   - **Nguyên nhân trực tiếp (Smoking Gun)**: Trong `C:\Users\admin\.gemini\config\config.json`, khóa `plugins["tdq-workflow"]` đang bị đặt tường minh là **`{"enabled": false}`** (trong khi cả 7 plugin đang hoạt động còn lại như `chrome-devtools-plugin`, `gemini-api`, `gdocs`, `gdrive`, `gsheets`, `gslides`, `google-antigravity-sdk` đều không đặt `enabled: false` nên mặc định bật). Đồng thời, `C:\Users\admin\.gemini\config\skills.json` **không tồn tại** trên đĩa nên `skills/` cũng không được nạp theo đường đăng ký lẻ. Theo chuẩn chính thức `agy-customizations/docs/plugins.md` (dòng 90–111), `config.json` có quyền ưu tiên tối cao: khi `"enabled": false`, plugin vẫn nằm trong danh sách quản lý nhưng **0% customization bên trong (skills, MCP, hooks, rules, agents) được nạp**.
   - **Loại trừ các giả thuyết khác bằng bằng chứng thực nghiệm**:
     - `plugin.json` tại `C:\Users\admin\.gemini\config\plugins\tdq-workflow\plugin.json` **KHÔNG** có `"disabled": true` (chỉ có `name`, `version: "0.74.0"`, `description`).
     - `mcp_config.json` **KHÔNG** khai báo mảng `"variables"` (nên không bị cơ chế setup-form của `migrate-agent-settings/SKILL.md` dòng 194 tự tắt lúc khởi tạo).
     - Bản cài trên đĩa thuộc phiên bản cũ **`0.74.0`** (mtime `2026-10-19T15:28:41+07:00`, 122 files trong `manifest.json`), lệch 23 phiên bản so với repo nguồn `TDQ-Workflow` hiện tại (**`0.97.0`**, 147 files khi chạy `--sinh-agy`).

2. **Phát hiện nghiêm trọng hơn: Kể cả khi người dùng BẬT `"enabled": true` và chạy lại `--sinh-agy` từ `v0.97.0`, adapter Antigravity hiện tại bị hỏng nặng ở 6 tầng kiến trúc & runtime trên Windows**:
   - **[P0 — Vỡ cú pháp Python (`SyntaxError` ngay lúc nạp)]**: `build_portable.py` (`copy_loc`, dòng 478) chạy thay thế chuỗi thô `${CLAUDE_PLUGIN_ROOT}` → `C:\Users\admin\...` trên **toàn bộ file `.py` trong `scripts/`**. Chuỗi Windows chứa `\U` (`C:\Users`) bị bơm thẳng vào string literal thường của Python khiến **`scripts/tdq_checkportable.py` (dòng 138)** và **`scripts/tdq_setup.py` (dòng 636 ở v0.74.0 / dòng 1147 ở v0.97.0)** nổ `SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes... truncated \UXXXXXXXX escape` trên **cả bản đang cài lẫn bản sinh mới v0.97.0**! Nguy hiểm hơn, `ghi_manifest()` băm SHA-256 **sau khi** đã làm hỏng file, nên chạy `tdq_checkportable.py` từ repo gốc lại báo `CLEAN` giả tạo! Ngoài ra `scripts/tdq_state.py` (dòng 1446) bị bơm `C:\Users\...` vào `re.sub(r'...')`, gây nổ `re.error: bad escape \U` nếu gọi `plugin_root_cmd()`.
   - **[P0 — Sai hoàn toàn Schema `hooks.json` & Hợp đồng Stdin/Stdout của Antigravity Hooks]**:
     - `hooks.json` sinh theo schema Claude Code (`{"description": "...", "hooks": {"PreToolUse": [...], "Stop": [...]}}`) thay vì schema Antigravity (`{"<hook-name>": {"PreToolUse": [{"matcher": "...", "hooks": [...]}], "Stop": [{"type": "command", "command": "..."}]}}` — đối chiếu `agy-customizations/docs/hooks.md` dòng 15–107 và file live đang chạy `C:\Users\admin\.gemini\config\hooks.json`). Đặc biệt `Stop` trong Antigravity là danh sách **phẳng (Flat)** chứ không bọc `{"hooks": [...]}` như Claude Code.
     - `agy_pretooluse_gate.py` (dòng 57–63) đoán mò 5 đường dẫn JSON (`tool_input.command`, `toolInput.command`, `input.command`, `arguments.command`, `command`) nhưng payload thật của Antigravity (protojson camelCase, `hooks.md` dòng 183–193 & xác nhận từ `auto-compact.ps1` dòng 17) là **`toolCall.args.CommandLine`**! Hệ quả: `_first_command()` luôn trả `""`, cổng chặn cứng `PreToolUse` **vô tác dụng 100%** trước mọi lệnh `run_command` thật. Khi cho qua, script in chuỗi rỗng `""` thay vì JSON `{"decision": "allow"}`, và khi chặn lại bơm thêm field lạ `"allow_tool": false`, `"message": ...` không có trong proto `PreToolUse`.
     - `agy_stop_gate.py` (dòng 55–65) dò `cwd`, `workingDirectory`, `workspace_root`... nhưng Antigravity truyền **`workspacePaths` (mảng chuỗi)** và đặt `os.getcwd()` của hook tại thư mục chứa `hooks.json` (`~/.gemini/config/plugins/tdq-workflow`, `hooks.md` dòng 131, 159). Hệ quả: `agy_stop_gate.py` fallback về thư mục cài plugin, không bao giờ thấy `docs/tdq/state.json` của workspace đang mở!
     - `read_gate.py` đọc `tool_input.file_path` (Claude Code `Read`) và xuất `hookSpecificOutput` của Claude Code — hoàn toàn chết trên Antigravity (tool thật là `read_file` với `toolCall.args.Path`, và `PreToolUse` của Antigravity không có kênh `additionalContext`).
   - **[P1 — Lỗi tiêm biến môi trường MCP `mcp_config.json` & Thiếu hẳn `lsp` / `chrome-devtools`]**:
     - Theo `migrate-agent-settings/SKILL.md` (dòng 110–118), `mcp_config.json` của plugin Antigravity **KHÔNG expand biến môi trường hệ điều hành**: viết `"env": {"TAVILY_API_KEY": "${TAVILY_API_KEY}"}` mà không khai báo mảng `"variables"` sẽ **ghi đè biến môi trường kế thừa từ OS bằng đúng chuỗi ký tự đen `"${TAVILY_API_KEY}"`**, làm hỏng xác thực Tavily kể cả khi user đã set biến môi trường trong Windows!
     - `sinh_mcp()` (`tdq_checkportable.py` dòng 143–155) gán trùng `TAVILY_API_KEY` cho cả `tavily-primary` lẫn `tavily-backup` (bỏ quên `TAVILY_API_KEY_BACKUP`), không prefix tên server bằng tên plugin (`plugin/SKILL.md` dòng 304), và **bỏ rơi hoàn toàn MCP `lsp` (`agent-lsp`) cũng như `chrome-devtools`**. Trong khi đó, `npx` trên máy này nằm trong `fnm_multishells\<pid>_<ts>` (thư mục tạm theo shell session) nên Language Server chạy nền có nguy cơ không tìm thấy `npx` nếu không dùng đường dẫn ổn định.
   - **[P1 — Rơi rớt thành phần của TDQ-Workflow v0.97.0]**:
     - Thiếu **2/11 skills** của repo nguồn: `THU_TU_SKILL` (`build_portable.py` dòng 206–220) đóng cứng 10 tên từ thời cũ, bỏ sót **`tdq-browser-research`** và **`tdq-browser-test`** (trái ngược với `.opencode/plugins/tdq-workflow.js` quét động `fs.readdirSync` lấy đủ 11 skills).
     - Thiếu **6/6 subagents** (`agents/tdq-implementer.md`, `tdq-qc-tester.md`, `tdq-reviewer.md`, `tdq-build-resolver.md`, `tdq-refactor-cleaner.md`, `tdq-security-reviewer.md`) — không được chuyển đổi sang `plugins/tdq-workflow/agents/`.
     - Thiếu **100% `rules/`** (`rules/AGENTS.md`) và không có hook `SessionStart` / `PreInvocation`, nên agent Antigravity không hề biết quy tắc *"Mọi prompt mới phải mở bằng skill `tdq-intake`"* (trên Claude Code có `CLAUDE.md` + `session_start.py` + `prompt_context.py`; trên OpenCode có hook chèn `<TDQ_WORKFLOW>`).
     - Ngược lại, `copy_loc` lại chép nhầm **12 script thuần dev** (trong `RELEASE_EXCLUDE_SCRIPTS` như `canvas_*.py`, `i18n_check.py`, `doc_dup.py`...) và thư mục `scripts/samples/` vào plugin người dùng.
   - **[P2 — Hướng dẫn cài đặt (`README_AGY`) lỗi thời & sai chuẩn Antigravity hiện hành]**:
     - Bảo người dùng sửa tay `~/.gemini/config/config.json` (bị `plugin/SKILL.md` dòng 32, 118–121, 295 **cấm tuyệt đối** vì làm mất live reload và có nguy cơ ghi đè `userSettings`/permissions).
     - Bảo người dùng thêm thêm một mục trùng vào `~/.gemini/config/skills.json` với chuỗi Windows chưa escape backslash (`"path": "C:\Users\admin\..."` — **JSON bất hợp lệ!**), trong khi plugin bật rồi đã tự nạp `skills/` (`plugins.md` dòng 54–55).
   - **[P2 — Bộ đo `tdq_eval_hosts.py` không hỗ trợ Antigravity]**: `SUPPORTED_HOSTS = ("claude", "codex")` (dòng 20), chưa có nhánh preflight, cô lập biến môi trường hay bộ đọc `transcript.jsonl` của Antigravity.

---

## Nhiệm vụ 1: Kiểm toán Chuyên sâu Bộ Dựng Đa Host & Xuất Portable (`TDQ-Workflow`)

### 1.1. Kiến trúc đóng gói đa host hiện tại (`v0.97.0`)
Qua kiểm tra mã nguồn tại `C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow`:
- Từ phiên bản `0.50.0` (`2026-09-21`, ghi nhận trong `docs/tdq/brief/2026-09-21-0029-hoc-superpowers-da-host.md` và đầu file `scripts/build_portable.py` dòng 4–18), TDQ-Workflow bỏ mô hình đóng gói sẵn 3 thư mục (`portable_claude`, `portable_codex`, `antigravity_portable` — được khóa bằng `tests/test_adapter_host.py` dòng 28, 164–181) để chuyển sang mô hình **"một nguồn chung, nhiều manifest mỏng"**:
  1. **Claude Code**: đọc trực tiếp repo qua `.claude-plugin/marketplace.json` & `.claude-plugin/plugin.json` (`v0.97.0`, có `displayName`, `author`, `userConfig` cho `TAVILY_API_KEY`, `TAVILY_API_KEY_BACKUP`, `ENABLE_DEVTOOL_MCP`).
  2. **Codex CLI**: đọc trực tiếp repo qua `.agents/plugins/marketplace.json` (`"url": "./"`) và `.codex-plugin/plugin.json` (`"skills": "./skills/"`), kèm `.codex/hooks.json` ở gốc project do `scripts/tdq_codex_mcp.py` quản lý.
  3. **OpenCode**: nạp qua adapter JS `.opencode/plugins/tdq-workflow.js` (dòng 32, 85–114: quét động `../../skills` bằng `fs.readdirSync`, và dòng 117–164: chèn thẻ `<TDQ_WORKFLOW>` vào message đầu phiên qua `ctx.session.hook('context', ...)`).
  4. **Antigravity (`agy`)**: là **ngoại lệ duy nhất vẫn phải sinh cây thư mục vật lý** thông qua `scripts/build_portable.py --sinh-agy` (mặc định ghi vào `~/.gemini/config/plugins/tdq-workflow`), với giả định của tác giả tại dòng 12–14 & 463–465 rằng *"Antigravity requires a plugin directory at a fixed path under `$HOME`, with no way to point elsewhere"* (thực tế giả định này **không còn đúng hoàn toàn** — xem Mục 3.1 về `plugins.json` và `.agents/plugins/`).

### 1.2. Phân tích chi tiết từng module nguồn

#### A. `scripts/build_portable.py` (814 dòng)
- **Ba chế độ CLI (`_xay_parser`, dòng 739–810)**:
  - `--sinh-agy [--dich DICH]`: gọi `sinh_agy_tai_cho(repo, args.dich, plugin_version(repo))` (dòng 578–592, 794–800). Kiểm tra an toàn qua `la_ban_cua_minh(dich)` (dòng 564–575): chỉ cho phép xóa/ghi đè nếu thư mục đích chưa tồn tại, rỗng, hoặc có `plugin.json` mang `"name": "tdq-workflow"`.
  - `--dest DEST`: dựng vào `<DEST>/antigravity_portable` (khác `--sinh-agy` ở chỗ `goc_cai=None`, nên chuỗi thay thế giữ nguyên `~/.gemini/config/plugins/tdq-workflow` thay vì đường dẫn tuyệt đối đã bung `os.path.abspath(os.path.expanduser(dich))`!).
  - `--sinh-hook-claude [--he-dich ...]`: viết lại tiền tố lệnh Python trong `hooks/hooks.json` (`py -3` trên Windows, `python3` trên POSIX — dòng 376–410).
  - `--sinh-main`: dùng `git ls-tree` + `git update-index` + `git commit-tree` xuất nhánh `main` sạch từ `dev`, lọc qua `RELEASE_EXCLUDE_DIRS` (dòng 62–67), `RELEASE_EXCLUDE_FILES` (dòng 68–71), và `RELEASE_EXCLUDE_SCRIPTS` (dòng 72–77).
- **Quy trình `sinh_ban_antigravity` (dòng 461–523) và 4 lỗ hổng thiết kế**:
  1. **Dòng 477–478 (`copy_loc` trên `scripts/`)**:
     ```python
     moi = goc_cai or GOC_AGY
     copy_loc(os.path.join(repo, "scripts"), os.path.join(goc, "scripts"), True, moi)
     ```
     - Bật `doi_bien=True` trên mọi file text trong `scripts/`, thay thế mù `${CLAUDE_PLUGIN_ROOT}` và `$CLAUDE_PLUGIN_ROOT` bằng `moi` (`C:\Users\admin\.gemini\config\plugins\tdq-workflow` khi chạy `--sinh-agy` trên Windows). `EXCLUDE_FILES` (dòng 51–60) chỉ loại `build_portable.py` và `tdq_eval.py`, bỏ quên `tdq_checkportable.py`, `tdq_setup.py`, `tdq_state.py`, `tdq_codex_mcp.py` — trực tiếp gây nổ `SyntaxError` trong `tdq_checkportable.py` và `tdq_setup.py`!
     - Chỉ lọc theo `EXCLUDE_DIRS`/`EXCLUDE_FILES` mà **không** lọc theo `RELEASE_EXCLUDE_SCRIPTS` hay `scripts/samples`, khiến 12 script nội bộ dev và file mẫu lọt vào plugin.
  2. **Dòng 206–220 & 480–490 (Sao chép `skills/`)**:
     - Duyệt cứng tuple `THU_TU_SKILL` (10 phần tử: `tdq-conventions`, `tdq-setup`, `tdq-intake`, `tdq-spec`, `tdq-plan`, `tdq-build`, `tdq-lean`, `tdq-checkportable` lấy từ `portable_src/skills/`, `tdq-status`, `tdq-check-status`). Hai skill mới trong `skills/` là **`tdq-browser-research`** và **`tdq-browser-test`** bị bỏ rơi hoàn toàn.
     - Gọi `_sua_duong_dan_tuong_doi_agy` (dòng 330–360) thay thế mọi cụm `scripts/` hoặc `hooks/` trong `.md` thành `<goc_cai>/scripts/`. Trên Windows, `goc_cai` dùng dấu `\` (`C:\Users\admin\...`) ghép với `/scripts/...` tạo ra đường dẫn lai `C:\Users\admin\.gemini\config\plugins\tdq-workflow/scripts/...` xuất hiện **172 lần** trong `skills/**/*.md`, đồng thời giữ nguyên tiền tố `python3 ` **125 lần** (dù comment của chính tác giả ở dòng 311 viết rằng Windows mặc định không có `python3`!).
  3. **Dòng 492–505 (Chỉ chép 4 file hook và sinh 3 file JSON cấu hình)**:
     - Chỉ chép `agy_pretooluse_gate.py`, `agy_stop_gate.py`, `read_gate.py`, `_common.py` vào `hooks/scripts/`.
     - Không có bước nào xử lý `agents/*.md` hoặc sinh `rules/AGENTS.md`.
  4. **Dòng 522 (`ghi_manifest`)**: Tính SHA-256 sau khi đã ghi các file `.py` bị lỗi cú pháp, biến lỗi build-time thành trạng thái "chuẩn" trong `manifest.json`.

#### B. `portable_src/`
- Chỉ chứa duy nhất 1 file: `C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow\portable_src\skills\tdq-checkportable\SKILL.md` (64 dòng, 3.388 bytes).
- Nội dung `SKILL.md` này đã **lỗi thời so với kiến trúc hiện tại**: Bước 2 (dòng 21–32) và Bước 2b (dòng 34–46) vẫn hướng dẫn chạy `tdq_checkportable.py setup` để tái tạo `.claude/settings.json`, `.mcp.json` và `setup --trust` cho Codex — trong khi nhánh `--trust` trong `scripts/tdq_checkportable.py` đã bị xóa từ `0.50.0` (xem comment dòng 406–410 của `tdq_checkportable.py` — hiện tại gọi `tdq_checkportable.py setup --trust` sẽ báo lỗi `unrecognized arguments: --trust`, exit code 2!).

#### C. `scripts/tdq_checkportable.py` (630 dòng)
- Cung cấp 2 lệnh CLI: `check` và `setup [--shim]`.
- Chứa hàm `sinh_mcp()` (dòng 143–155) được `build_portable.py` import lại để sinh `mcp_config.json` cho Antigravity.
- Chứa hàm `kiem_layout_agy(goc, manifest)` (dòng 312–355): khi thấy `plugin.json` ở gốc, kiểm tra không còn `config/settings.json`, kiểm tra `hooks.json` hợp lệ JSON và các trường `command` không chứa `~` chưa bung (`con_dau_nga_chua_bung`, dòng 358–373) cũng như chứa `os.path.expanduser("~")` của máy hiện tại. **Tuy nhiên không hề kiểm tra cấu trúc top-level của `hooks.json` theo chuẩn Antigravity hay kiểm tra `ast.parse` các file `.py`!**
- Cung cấp cơ chế vá `python3.cmd` / `python3` shim trên Windows (`cai_shim_python3`, dòng 500–553). Trên máy hiện tại, `shutil.which("python3")` trỏ về `C:/Users/admin/.gemini/antigravity/bin\python3.CMD` (shim do chính Antigravity cung cấp).

#### D. `scripts/tdq_eval_hosts.py` (579 dòng) & `scripts/plugin_tiers.py` (213 dòng)
- **`tdq_eval_hosts.py`**: Bộ chạy đánh giá thực nghiệm cô lập (`OwnedProcessJob`, `_private_environment`) nhưng dòng 20 đóng cứng `SUPPORTED_HOSTS = ("claude", "codex")`. Mọi lời gọi với `host="agy"` hoặc `"antigravity"` sẽ trả về `"status": "UNSUPPORTED", "reason": "unsupported_host"` (dòng 151–158) hoặc ném `ValueError("unsupported_host")` (dòng 86, 499). Parser JSONL chỉ biết `CLAUDE_EVENT_TYPES` và `CODEX_EVENT_TYPES` (dòng 25–36), chưa biết định dạng `transcript.jsonl` (`step_index`, `USER_INPUT`, `PLANNER_RESPONSE`, `tool_calls`) của Antigravity.
- **`plugin_tiers.py`**: Công cụ thuần Claude Code, chỉ đọc/ghi `~/.claude/plugin-tiers.json` và `~/.claude/settings.json` (`enabledPlugins` với hậu tố `@claude-plugins-official`, dòng 19–24, 61–89). Hoàn toàn không tương tác với `~/.gemini/config/config.json` của Antigravity (dù file này vẫn bị chép thừa vào `plugins/tdq-workflow/scripts/plugin_tiers.py`).

### 1.3. Các giả định của tác giả TDQ-Workflow qua bộ Test (`tests/`) và Tài liệu Thiết kế (`docs/tdq/`)
Quét toàn bộ `tests/` (phát hiện matches tại 18 file test, trọng tâm là `test_agy_hooks.py`, `test_build_portable.py`, `test_sinh_agy.py`, `test_tuong_thich_host.py`, `test_sua_da_nen_tang.py`, `test_adapter_host.py`) và `docs/tdq/brief/2026-09-03-1440-kiem-tuong-thich-3-host.md` cho thấy bức tranh lịch sử rất rõ ràng:
1. Ngày `2026-09-03`, tác giả khảo sát một bản cài `agy 1.1.11` và tham khảo một bài viết bên thứ ba trên Medium (`source N5`, dòng 26 của brief `2026-09-03-1440`) cùng một GitHub issue (`cmux#5358`, `source N6`). Lúc đó tác giả ghi nhận: *"Google publishes no official PreToolUse INPUT schema"* (`agy_pretooluse_gate.py` dòng 18) và *"Google publishes no official Stop payload schema"* (`agy_stop_gate.py` dòng 25).
2. Vì thiếu tài liệu chính thức vào thời điểm đó:
   - Trong `test_agy_hooks.py` (dòng 35–41), tác giả chỉ test 4 hình dạng giả định (`tool_input.command`, `toolInput.command`, `input.command`, `command`) — bỏ lọt hình dạng thật `toolCall.args.CommandLine`.
   - Trong `test_agy_hooks.py` (dòng 120–122, 195), tác giả giả định Stop gửi `cwd` hoặc `workingDirectory` — bỏ lọt `workspacePaths`.
   - Trong `test_tuong_thich_host.py` (dòng 78–90), tác giả khóa cứng việc `agy_pretooluse_gate.py` phải in đồng thời `"allow_tool": false` và `"decision": "deny"`.
   - Trong `test_build_portable.py` (dòng 273–288) và `test_sinh_agy.py` (dòng 70–75), tác giả khóa cứng cấu trúc `hooks.json` có top-level `"hooks": {"PreToolUse": [{"hooks": [...]}], "Stop": [{"hooks": [...]}]}` (tức cấu trúc của Claude Code!).
   - Trong `test_build_portable.py` (dòng 213), `TestBanAntigravity` gọi `sinh_ban_antigravity(ROOT, self.dest)` **không truyền `goc_cai`**, nên biến được thay bằng `~/.gemini/...` (dấu `/`) thay vì `C:\Users\...` (dấu `\`). Còn `test_sinh_agy.py` có truyền `--dich` trên Windows nhưng **không chạy hay `import` bất kỳ script nào trong `self.dich/scripts/`**, nên lỗi nổ `SyntaxError: unicodeescape` trong `tdq_checkportable.py` và `tdq_setup.py` đã lọt qua toàn bộ 100% unit tests trên Windows!

---

## Nhiệm vụ 2: Kiểm tra Thực tế Bản Cài tại `C:\Users\admin\.gemini\config\plugins\tdq-workflow\` & Cấu hình Người dùng

### 2.1. Cây thư mục & Nội dung Bản Cài Hiện Tại (`v0.74.0`)
Thư mục `C:\Users\admin\.gemini\config\plugins\tdq-workflow\` (cài ngày `2026-10-19T15:28:41+07:00`, tổng **123 files** = 122 files trong `manifest.json` + chính `manifest.json`):
- **Gốc plugin**:
  - `plugin.json` (157 B): `{"description": "Spec-driven TDQ workflow: intake → spec → plan → build → QC → report.", "name": "tdq-workflow", "version": "0.74.0"}`
  - `hooks.json` (991 B): Khai báo top-level `"description"` + `"hooks"` (`PreToolUse` gọi `py -3 "C:\Users\admin\.gemini\config\plugins\tdq-workflow/hooks/scripts/agy_pretooluse_gate.py"` và `read_gate.py`; `Stop` gọi `agy_stop_gate.py`).
  - `mcp_config.json` (430 B): Khai báo `mcpServers` gồm `tavily-primary` và `tavily-backup`, cả hai đều chạy `npx -y tavily-mcp@latest` với `"env": {"TAVILY_API_KEY": "<PLACEHOLDER:${TAVILY_API_KEY}>"}` (hoàn toàn không chứa giá trị khóa thật).
  - `manifest.json` (13.783 B): `"version": "0.74.0"`, `"python_min": "3.11"`, `"external_commands": ["git", "graphify"]`, `"mcp_servers": ["tavily-primary", "tavily-backup"]`, 122 mục SHA-256.
  - `README.md` (4.100 B).
- **`hooks/scripts/`** (4 files): `_common.py`, `agy_pretooluse_gate.py`, `agy_stop_gate.py`, `read_gate.py`.
- **`scripts/`** (47 files `.py` + `samples/transcript-step-audit.jsonl`): **Trong đó `tdq_checkportable.py` (dòng 138) và `tdq_setup.py` (dòng 636) bị lỗi `SyntaxError` không thể chạy được!**
- **`skills/`** (10 thư mục skill: `tdq-build`, `tdq-check-status`, `tdq-checkportable`, `tdq-conventions`, `tdq-intake`, `tdq-lean`, `tdq-plan`, `tdq-setup`, `tdq-spec`, `tdq-status` cùng đầy đủ `references/`).
- **`rules/`**: **KHÔNG TỒN TẠI**.
- **`agents/`**: **KHÔNG TỒN TẠI**.

### 2.2. Kiểm tra An toàn Cấu hình `~/.gemini/config/` & Workspace `TDQ-Workflow-Antigravity`
Thực thi kiểm tra chỉ đọc cấu trúc (ẩn toàn bộ giá trị nhạy cảm):
1. **`C:\Users\admin\.gemini\config\config.json`** (2.223 B, mtime `2026-11-13T13:06:39+07:00`):
   - Top-level keys: `['plugins', 'sidecars', 'userSettings']`.
   - Các khóa dưới `"plugins"`: `['chrome-devtools-plugin', 'gdocs', 'gdrive', 'gemini-api', 'google-antigravity-sdk', 'gsheets', 'gslides', 'tdq-workflow']`.
   - Giá trị của `plugins["tdq-workflow"]`: **`{'enabled': False}`**!
   - Giá trị của cả 7 plugin còn lại: đều là `{'installedFrom': '<dict>'}` (không có khóa `enabled`, nên mặc định bật — khớp hoàn toàn với danh sách `<skills>` đang nạp trong system prompt của phiên hiện tại!).
2. **Các tệp khác trong `C:\Users\admin\.gemini\config\`**:
   - `hooks.json` (563 B): Đang hoạt động thật, cấu hình hook `"auto-compact"` cho `PreInvocation` và `PreToolUse` (`matcher: "run_command"`) gọi `C:\Users\admin\.gemini\config\hooks\auto-compact.ps1`.
   - `mcp_config.json` (0 B): Tệp rỗng (0 byte) — lưu ý: tệp 0 byte không phải JSON hợp lệ nếu parser không bỏ qua file rỗng.
   - `skills.json`, `plugins.json`, `GEMINI.md`, `AGENTS.md`: **KHÔNG TỒN TẠI** trong `~/.gemini/config/` hay `~/.gemini/`.
3. **Workspace `c:\Users\admin\Documents\Projects\TDQ-Workflow-Antigravity`**: Thư mục hoàn toàn trống (0 file, không có `.agents/`, `GEMINI.md` hay `AGENTS.md`).

### 2.3. Bằng chứng Kết luận cho "Critical Mystery"
| Câu hỏi kiểm chứng | Kết quả thực chứng | Bằng chứng xác thực |
| :--- | :--- | :--- |
| `config.json` có đặt `"tdq-workflow": {"enabled": false}` không? | **CÓ (Nguyên nhân gốc rễ 100%)** | `cfg.get("plugins", {}).get("tdq-workflow") == {'enabled': False}` trong `C:\Users\admin\.gemini\config\config.json`. Theo `agy-customizations/docs/plugins.md` dòng 105–111, `config.json` ghi đè mọi khai báo khác và tắt toàn bộ skills/MCP/hooks của plugin. |
| `skills.json` có đăng ký `tdq-workflow/skills` riêng không? | **KHÔNG** | `~/.gemini/config/skills.json` không tồn tại trên đĩa. |
| `plugin.json` có `"disabled": true` không? | **KHÔNG** | `plugins/tdq-workflow/plugin.json` chỉ có `name`, `version`, `description`. |
| `mcp_config.json` có `"variables"` chưa điền khiến plugin tự tắt lúc đầu không? | **KHÔNG** | `plugins/tdq-workflow/mcp_config.json` không khai báo trường `"variables"`. Tuy nhiên, chính việc dùng `"${TAVILY_API_KEY}"` mà không khai báo `"variables"` sẽ làm hỏng xác thực Tavily khi plugin được bật! |
| Vì sao MCP `lsp` và `chrome-devtools` không xuất hiện kể cả nếu bật plugin? | **KHÔNG ĐƯỢC ĐÓNG GÓI** | `sinh_mcp()` chỉ xuất `tavily-primary` và `tavily-backup`; `lsp` và `chrome-devtools` trong TDQ-Workflow chỉ được `tdq_setup.py` / `tdq_devtool_mcp.py` ghi vào `~/.claude.json` của Claude Code. |
| Vì sao chỉ có 10 skills trong bundle thay vì 11+1 skills? | **`THU_TU_SKILL` ĐÓNG CỨNG** | `build_portable.py` dòng 206–220 bỏ sót `tdq-browser-research` và `tdq-browser-test`, đồng thời bản cài trên đĩa vẫn ở `v0.74.0`. |

---

## Nhiệm vụ 3: Đối chiếu Từng Cổ vật Sinh ra với Đặc tả Chính thức của Antigravity & Thử nghiệm Build `v0.97.0`

### 3.1. Kết quả chạy thử nghiệm `build_portable.py --sinh-agy` (`v0.97.0`) trên Windows
Chạy lệnh an toàn vào thư mục scratch:
```powershell
python C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow\scripts\build_portable.py --sinh-agy --dich C:\Users\admin\.gemini\antigravity\brain\2a408580-dde6-4a41-aeda-5a1f871c0366\scratch\sub4_agy_adapter\out\tdq-workflow
```
- **Exit code**: `0`
- **Stderr log**:
  ```text
  [2026-11-13T13:21:24+07:00] antigravity_portable: 10 skill(s), 3 hook(s), 2 MCP server(s), 0 plugin variable left
  [2026-11-13T13:21:24+07:00] manifest: 147 file(s) in tdq-workflow
  [2026-11-13T13:21:24+07:00] agy: đã sinh C:\Users\admin\.gemini\antigravity\brain\2a408580-dde6-4a41-aeda-5a1f871c0366\scratch\sub4_agy_adapter\out\tdq-workflow
  ```
- **So sánh `v0.97.0` vừa sinh (147 files) với `v0.74.0` đang cài (122 files)**:
  - Thêm mới **25 files**: 17 module Python thuộc bộ Archify & Eval (`archify_artifacts.py`, `archify_delivery.py`, `archify_model.py`, `tdq_archify.py`, `tdq_eval_contract.py`, `tdq_eval_hosts.py`, `tdq_graphify.py`, `tdq_readiness.py`, `tdq_runtime_bench.py`, `tdq_skill_eval.py`, `tdq_test_manifest.py`, `tdq_test_process.py`, `tdq_test_receipt.py`, `tdq_test_report.py`, `tdq_test_result.py`, `tdq_transcript.py`, `tdq_transcript_cache.py`) + 8 tài liệu tham chiếu (`archify-lifecycle.md`, `runtime-speed.md`, `skill-eval.md`, `ultracode.md`, `archify-quick.md`, `quick-lane-mini.md`, `mcp-first-guide.md`, `archify-ba.md`).
  - Thay đổi nội dung **72 files**, xóa **0 files**.
  - **Kiểm tra `ast.parse` trên toàn bộ 69 file `.py` của bản sinh `v0.97.0`**: **67 OK, 2 BROKEN (`SyntaxError`)** — vẫn vỡ y hệt bản `v0.74.0` tại `scripts\tdq_checkportable.py:138` và `scripts\tdq_setup.py:1147`!

### 3.2. Bảng Đối chiếu Chi tiết Từng Artifact với Đặc tả Antigravity Chính thức

#### 1) Kiến trúc khám phá Plugin (`plugins.json` & `.agents/plugins/`)
- **Đặc tả Antigravity (`agy-customizations/SKILL.md` dòng 40–55, `docs/plugins.md` dòng 78–85, `docs/json_configs.md` dòng 12–45)**:
  - Antigravity hỗ trợ **cả hai** mô hình mà tác giả TDQ tưởng là không có:
    1. Workspace-scoped plugin tại `<project>/.agents/plugins/<plugin_name>/plugin.json`.
    2. Đăng ký đường dẫn ngoài qua `~/.gemini/config/plugins.json` hoặc `<project>/.agents/plugins.json` (`{"entries": [{"path": "..."}]}` — quét sâu 1 cấp).
  - Do đó, giả định ở đầu `build_portable.py` (dòng 12–14: *"no way to point elsewhere"*) là **lỗi thời**. Dù vậy, cài đặt thành một thư mục chuẩn ở `~/.gemini/config/plugins/tdq-workflow/` vẫn là cách tốt nhất để quản lý bật/tắt tập trung trên UI `customization://tdq-workflow`.

#### 2) `plugin.json`
- **Đặc tả Antigravity (`builtin/skills/plugin/SKILL.md` dòng 213–267)**:
  - Các trường hợp lệ duy nhất: `name`, `description`, `logo` (trong plugin tự viết chỉ nhận đường dẫn tương đối tới ảnh trong bundle như `assets/logo.svg`; URL/absolute path bị lờ đi ở local authoring), `suggestedPrompts` (tối đa 3 chuỗi), `displayName`, `version`, `author`, `homepage`, `repository`, `disabled`. Trường lạ bị loader lặng lẽ bỏ qua (ví dụ `.claude-plugin/plugin.json` có `userConfig` — nếu chép sang Antigravity sẽ bị bỏ qua).
- **Thực trạng `build_portable.py` (`_sinh_plugin_json_agy`, dòng 446–454)**:
  - Xuất `{"name": "tdq-workflow", "version": "0.97.0", "description": "..."}` — **Hợp lệ về cú pháp & schema**, nhưng thiếu `displayName` (`"TDQ Workflow"`), `author`, `homepage`, `repository`, `suggestedPrompts` (đều đã có sẵn trong `.claude-plugin/plugin.json` và `.codex-plugin/plugin.json`), làm thẻ hiển thị trên giao diện Customizations nghèo thông tin.

#### 3) `mcp_config.json`
- **Đặc tả Antigravity (`migrate-agent-settings/SKILL.md` dòng 87–128, `docs/mcp_servers.md` dòng 26–92)**:
  - Chỉ nhận `Stdio` (`command`, `args`, `env`, `cwd`) hoặc `Streamable HTTP` (`url` / `serverUrl`, `headers`), kèm `disabled`, `variables` (và `tools.<name>.eager` như thấy ở plugin `gemini-api` đang chạy). Không hỗ trợ legacy SSE.
  - **Quy tắc sống còn về biến môi trường (`migrate-agent-settings/SKILL.md` dòng 110–124)**:
    - `mcp_config.json` trong plugin **KHÔNG tự bung biến môi trường của hệ điều hành**. Placeholder `${X}` chỉ được thay thế khi `X` được khai báo trong mảng `variables: [{"name": "X", "title": "...", "description": "..."}]` của server đó (và nếu khai báo `variables`, plugin sẽ khởi đầu ở trạng thái **disabled** chờ người dùng điền form trên UI — dòng 194!).
    - Nếu muốn tiến trình MCP con tự kế thừa biến môi trường từ OS (như `TAVILY_API_KEY`), **PHẢI BỎ HẲN mục `"TAVILY_API_KEY": "${TAVILY_API_KEY}"` khỏi `"env"`**! Giữ nó lại khiến tiến trình `npx` nhận chuỗi literal `"${TAVILY_API_KEY}"` đè lên biến thật của OS!
  - Tên MCP server dùng chung một không gian tên toàn cục (`plugin/SKILL.md` dòng 304–306), nên cần tiền tố hóa hoặc kiểm soát xung đột (ví dụ user đã cài plugin chính thức `chrome-devtools-plugin` của Antigravity!).
- **Thực trạng `tdq-workflow/mcp_config.json`**:
  1. Cả `tavily-primary` và `tavily-backup` đều truyền `"env": {"TAVILY_API_KEY": "${TAVILY_API_KEY}"}` không kèm `"variables"` → **lỗi clobber biến OS bằng chuỗi literal `"${TAVILY_API_KEY}"`**.
  2. `tavily-backup` dùng nhầm `TAVILY_API_KEY` thay vì `TAVILY_API_KEY_BACKUP` (`tdq_checkportable.py` dòng 145–154). Nếu muốn kế thừa OS env var cho backup server vốn vẫn chạy gói `tavily-mcp@latest` (vốn đọc biến tên `TAVILY_API_KEY`), thì không thể bỏ trống `env` mà phải dùng `variables` cho `TAVILY_API_KEY_BACKUP` (`"env": {"TAVILY_API_KEY": "${TAVILY_API_KEY_BACKUP}"}` kèm `variables`), hoặc chỉ khai báo 1 server `tdq-tavily` kế thừa thẳng OS env.
  3. Thiếu hẳn cấu hình MCP cho `agent-lsp` (`C:\Users\admin\.local\bin\agent-lsp.EXE` đã có sẵn trên máy!) và `tdq_setup.py` chỉ biết ghi vào `~/.claude.json` chứ không biết `mcp_config.json` của Antigravity. Với `chrome-devtools`, máy người dùng đã có sẵn `chrome-devtools-plugin` của Antigravity nên cần tránh đụng độ tên.

#### 4) `hooks.json` & Các Script Hook trong `hooks/scripts/`
Đối chiếu trực tiếp giữa `agy-customizations/docs/hooks.md`, file thực tế đang chạy `C:\Users\admin\.gemini\config\hooks.json` + `auto-compact.ps1`, và bản sinh của `build_portable.py`:

| Khía cạnh | Chuẩn Antigravity Chính thức (`docs/hooks.md` & live `hooks.json`) | Bản sinh hiện tại của `build_portable.py` | Hệ quả thực tế khi chạy |
| :--- | :--- | :--- | :--- |
| **Vị trí file** | `<plugin_dir>/hooks.json` (bắt buộc ở gốc với native plugin có `plugin.json` — `plugins.md` dòng 61–70) | `<plugin_dir>/hooks.json` | **ĐÚNG** vị trí file. |
| **Cấu trúc JSON gốc (Top-level)** | Map từ `<tên-hook>` sang cấu hình sự kiện: `{"tdq-workflow": {"PreToolUse": [...], "Stop": [...]}}` (`hooks.md` dòng 15–56) | Dùng schema Claude Code: `{"description": "...", "hooks": {"PreToolUse": [...], "Stop": [...]}}` (`build_portable.py` dòng 438–443) | **SAI SCHEMA**: khóa `"description"` có kiểu `string` thay vì object HookSpec (có nguy cơ làm lỗi bộ giải mã JSON/protojson của toàn file `hooks.json`); khóa `"hooks"` vô tình biến thành tên của 1 hook. |
| **Cấu trúc `PreToolUse`** | Grouped: `[{"matcher": "run_command", "hooks": [{"type": "command", "command": "..."}]}]` (`hooks.md` dòng 92–94, 108–119) | Grouped nhưng **thiếu `"matcher"`**: `[{"hooks": [{"command": "...", "type": "command"}]}]` | Không lọc theo tên tool (`run_command`, `read_file`), gây tốn tiến trình Python vô ích trên mọi tool call nếu nạp được. |
| **Cấu trúc `Stop`** | **Flat**: danh sách trực tiếp các handler `[{"type": "command", "command": "..."}]` (`hooks.md` dòng 104–106) | **Grouped**: `[{"hooks": [{"command": "...", "type": "command"}]}]` (`build_portable.py` dòng 434–437) | **HỎNG HOÀN TOÀN**: phần tử trong mảng `Stop` không có trường `"command"` ở cấp phẳng, handler `agy_stop_gate.py` không thể chạy! |
| **Biến môi trường & CWD của Hook** | Antigravity cấp sẵn env `PLUGIN_ROOT`, `PLUGIN_DATA`, tự bung `~` trong `command`, và đặt **CWD tại thư mục chứa `hooks.json`** (`hooks.md` dòng 129–140) | Tác giả tưởng không có `PLUGIN_ROOT` nên nướng cứng path tuyệt đối; `agy_stop_gate.py` gọi `os.getcwd()` tưởng là thư mục workspace! | `agy_stop_gate.py` đọc nhầm thư mục cài plugin thay vì project của user! |
| **`PreToolUse` Stdin** | Protojson camelCase: `{"toolCall": {"name": "run_command", "args": {"CommandLine": "..."}}, "workspacePaths": [...], "conversationId": "..."}` (`hooks.md` dòng 156–193) | `agy_pretooluse_gate.py` dò `tool_input.command`, `toolInput.command`, `input.command`, `arguments.command`, `command`; `read_gate.py` dò `tool_input.file_path` | **VÔ HIỆU HÓA 100%**: cả `agy_pretooluse_gate.py` lẫn `read_gate.py` không bao giờ đọc được lệnh hay đường dẫn file thật! |
| **`PreToolUse` Stdout** | Luôn xuất JSON hợp lệ trên stdout (`hooks.md` dòng 146, 198–215; `auto-compact.ps1` dòng 22, 68): cho phép → `{"decision": "allow"}`; chặn → `{"decision": "deny", "reason": "..."}` | Cho phép → không in gì (`""`); chặn → in dư `"allow_tool": false` và `"message"`; `read_gate.py` in `{"hookSpecificOutput": ...}` của Claude Code | Trả chuỗi rỗng hoặc field lạ ngoài proto (`allow_tool`, `message`, `hookSpecificOutput`) dễ gây lỗi parse protojson phía Language Server! |
| **`Stop` Stdin & Stdout** | Stdin có `"workspacePaths": ["/path/to/ws"]`, `"terminationReason": "NO_TOOL_CALL"`, `"fullyIdle": true` (`hooks.md` dòng 159, 374–395). Stdout: tiếp tục → `{"decision": "continue", "reason": "..."}`; cho dừng → `{"decision": "allow"}` (bất kỳ giá trị nào khác `"continue"` — dòng 406–408) | `agy_stop_gate.py` dò `_CWD_KEYS` (thiếu `workspacePaths`), không kiểm tra `terminationReason` (như `USER_CANCELED`, `ERROR`), và khi cho dừng thì in chuỗi rỗng `""` thay vì JSON `{}` / `{"decision": "allow"}` | Không tìm thấy workspace state; nếu sửa được đường dẫn mà không kiểm `terminationReason == "USER_CANCELED"` thì user bấm Cancel vẫn bị hook ép `continue`! |

#### 5) `skills/`, `agents/`, và `rules/`
- **`skills/`**:
  - Cả 12 `SKILL.md` của TDQ-Workflow đều có YAML frontmatter hợp lệ (`name` trùng tên thư mục, `description` khác rỗng từ 151–230 ký tự). Lưu ý nhỏ: `tdq-conventions` có thêm khóa `user-invocable` và `tdq-lean` có `argument-hint` (từ Claude Code).
  - Tuy nhiên: (a) thiếu 2 skill `tdq-browser-research` và `tdq-browser-test`; (b) nội dung thân bài chứa các tên tool/lệnh đặc thù của Claude Code (`EnterPlanMode`, `AskUserQuestion`, `mcp__lsp__start_lsp` thay vì tên tool MCP của Antigravity là `mcp_<serverName>_<toolName>` như `mcp_tdq-workflow_lsp_start_lsp`) và gọi các script `tdq_setup.py` / `tdq_checkportable.py` đang bị vỡ `SyntaxError` trên Windows!
- **`agents/`**:
  - Theo `migrate-agent-settings/SKILL.md` (dòng 146–162), Antigravity hỗ trợ `plugins/<name>/agents/<agent>.md` nhưng **bắt buộc chuyển đổi frontmatter**: phải có `subagent: true`, `mainAgent: false`, ánh xạ `tools` sang tên native của Antigravity (`[read_file, edit_file, write_file, run_command, manage_task, search_web]`), và **bỏ `model` (`haiku`/`inherit`), `effort`, `color`**. Hiện tại 6 agent của TDQ (`agents/*.md`) dùng frontmatter Claude Code (`model: haiku`, `effort: medium`, `tools: Bash, Read, Grep, Glob`) và **chưa được `build_portable.py` xuất sang bundle Antigravity**.
- **`rules/`**:
  - Theo `plugin/SKILL.md` (dòng 205, 210–211) và `docs/plugins.md` (dòng 73–75), `plugins/tdq-workflow/rules/AGENTS.md` (plain markdown, không frontmatter, giới hạn ≤ 24 KB) sẽ tự động luôn bật (`always_on`) khi plugin được bật. Đây là nơi lý tưởng nhất để đặt bản rút gọn tương thích Antigravity của `docs/claude-md-mau.md` (quy tắc gọi `tdq-intake`, quy tắc nhánh Git, quy tắc working log), thay vì bỏ trống hoàn toàn như hiện tại.

---

## Tổng hợp Danh sách Khuyến nghị Khắc phục (Actionable Fix Roadmap cho Adapter Antigravity)

1. **Khắc phục lỗi `SyntaxError` & `re.error` trên Windows trong `build_portable.py` (Ưu tiên P0)**:
   - Tắt `doi_bien=True` khi chép `scripts/*.py` (hoặc không bao giờ thay thế chuỗi thô chứa backslash Windows vào mã nguồn `.py`; các script Python nên tự xác định plugin root qua `os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` hoặc env `PLUGIN_ROOT` của Antigravity).
   - Khi viết đường dẫn vào `.md` hoặc `README.md`, chuẩn hóa dấu phân cách sang `/` (`dich.replace("\\", "/")`) hoặc escape JSON chuẩn bằng `json.dumps` để không bao giờ sinh JSON lỗi trong `README.md`.
   - Áp dụng bộ lọc `la_duong_dan_release` khi chép `scripts/` để loại bỏ 12 script dev và `scripts/samples/`.
   - Bổ sung bước kiểm tra `ast.parse` cho toàn bộ `scripts/*.py` và `hooks/scripts/*.py` ngay trong `sinh_ban_antigravity` và trong `tests/test_sinh_agy.py`.

2. **Viết lại `_sinh_hooks_agy` & Các Gate Hook đúng chuẩn Antigravity 2.0 (Ưu tiên P0)**:
   - Sửa `hooks.json` sang top-level named hook:
     ```json
     {
       "tdq-workflow": {
         "SessionStart": [
           { "type": "command", "command": "py -3 \"<abs_path>/hooks/scripts/agy_session_start.py\"", "timeout": 10 }
         ],
         "PreToolUse": [
           {
             "matcher": "run_command",
             "hooks": [{ "type": "command", "command": "py -3 \"<abs_path>/hooks/scripts/agy_pretooluse_gate.py\"", "timeout": 10 }]
           }
         ],
         "Stop": [
           { "type": "command", "command": "py -3 \"<abs_path>/hooks/scripts/agy_stop_gate.py\"", "timeout": 15 }
         ]
       }
     }
     ```
   - Trong `agy_pretooluse_gate.py`: đọc ưu tiên `payload["toolCall"]["args"]["CommandLine"]`; khi allow in `{"decision": "allow"}`; khi deny chỉ in `{"decision": "deny", "reason": reason}` (bỏ các khóa không thuộc proto như `allow_tool`, `message`). Bỏ `read_gate.py` khỏi `HOOK_AGY` (hoặc port sang `PreInvocation` nếu cần tiêm `injectSteps.systemMessage`).
   - Trong `agy_stop_gate.py`: đọc workspace từ `payload.get("workspacePaths", [None])[0]` trước khi fallback; chỉ chặn khi `payload.get("terminationReason") == "NO_TOOL_CALL"` (tuyệt đối không chặn `USER_CANCELED` hay `ERROR`); khi không chặn in `{"decision": "allow"}`.

3. **Sửa `mcp_config.json` & Tích hợp `lsp` cho Antigravity (Ưu tiên P1)**:
   - Bỏ `"env": {"TAVILY_API_KEY": "${TAVILY_API_KEY}"}` kiểu passthrough khỏi server stdio để tiến trình con kế thừa biến môi trường hệ điều hành thật, **hoặc** khai báo tường minh mảng `"variables"` đúng chuẩn Antigravity nếu muốn người dùng nhập key trên UI của plugin (kèm `TAVILY_API_KEY_BACKUP` riêng cho backup server).
   - Tiền tố hóa tên server (`tdq-tavily-primary`, `tdq-lsp`) để tránh đụng độ toàn cục, và bổ sung tùy chọn sinh cấu hình `agent-lsp` vào `mcp_config.json` của plugin khi máy đã cài `agent-lsp`.

4. **Đóng gói đủ 12 Skills + 6 Subagents chuyển đổi + `rules/AGENTS.md` (Ưu tiên P1)**:
   - Quét động thư mục `skills/` (cộng `portable_src/skills/`) thay vì đóng cứng 10 tên trong `THU_TU_SKILL`, để lấy đủ `tdq-browser-research` và `tdq-browser-test`.
   - Thêm bước chuyển đổi 6 file `agents/*.md` sang frontmatter chuẩn Antigravity (`subagent: true`, `mainAgent: false`, ánh xạ `tools: [read_file, edit_file, write_file, run_command, manage_task]`, lược bỏ `model`/`effort`).
   - Sinh `rules/AGENTS.md` (≤ 24 KB, lược bỏ các thuật ngữ riêng của Claude Code như `EnterPlanMode`/`AskUserQuestion`) và làm giàu `plugin.json` (`displayName`, `author`, `repository`, `suggestedPrompts`).
   - Cập nhật `README_AGY`: hướng dẫn người dùng bật plugin qua giao diện Customizations (`customization://tdq-workflow`) hoặc `agy plugin enable tdq-workflow`, **bỏ hoàn toàn** hướng dẫn sửa tay `config.json` và ghi trùng vào `skills.json`.
