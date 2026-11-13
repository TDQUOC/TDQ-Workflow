# Báo Cáo Kiểm Toán & Thực Nghiệm Phần 3: TDQ-Workflow Lifecycle Hooks & Gates trên Antigravity (Windows)

> **Phạm vi kiểm toán**:
> - Repo gốc: `C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow` (`v0.97.0`)
> - Bản cài plugin Antigravity: `C:\Users\admin\.gemini\config\plugins\tdq-workflow` (`v0.74.0`, hiện đang `"enabled": false` trong `~/.gemini/config/config.json`)
> - Tài liệu chuẩn (Ground Truth) của Antigravity:
>   - `C:\Users\admin\.gemini\antigravity\builtin\skills\agy-customizations\docs\hooks.md` (lines 1–416)
>   - `C:\Users\admin\.gemini\antigravity\builtin\skills\agy-customizations\docs\plugins.md` (lines 58–112)
> - Bộ test mô phỏng thực nghiệm trên Windows (`cmd /c`):
>   - Script harness: `C:\Users\admin\.gemini\antigravity\brain\2a408580-dde6-4a41-aeda-5a1f871c0366\scratch\sub3_hooks_sim\run_sim.py`
>   - Log kết quả thô: `C:\Users\admin\.gemini\antigravity\brain\2a408580-dde6-4a41-aeda-5a1f871c0366\scratch\sub3_hooks_sim\sim_results.json`

---

## Tóm Tắt Điều Hành (Executive Summary)

Qua đối chiếu từng dòng code với tài liệu chuẩn `docs/hooks.md` & `docs/plugins.md` của Antigravity và chạy thực nghiệm `cmd /c` trực tiếp trên Windows 11 với đúng payload `protojson` (`camelCase`), kết quả kiểm toán khẳng định:

1. **0 / 17 script hook của TDQ-Workflow hoạt động đúng trên Antigravity hiện tại** — kể cả 3 script được thiết kế riêng cho Antigravity trong bundle `tdq-workflow` (`agy_pretooluse_gate.py`, `read_gate.py`, `agy_stop_gate.py`).
2. **Nguyên nhân gốc rễ lịch sử** (`docs/tdq/brief/2026-09-03-1440-kiem-tuong-thich-3-host.md`, lines 18–28): Tác giả TDQ-Workflow xây dựng adapter Antigravity dựa trên bài viết bên thứ ba (nguồn N5/N6 ngày `2026-09-03`) khi chưa tiếp cận tài liệu chính thức `agy-customizations/docs/hooks.md`, đồng thời viết unit test `tests/test_tuong_thich_host.py` (lines 82–83) bằng payload `snake_case` của Claude Code (`{"tool_name": ..., "tool_input": {"command": ...}}`) thay vì `camelCase` (`{"toolCall": {"name": ..., "args": {"CommandLine": ...}}}`) của Antigravity.
3. **Đứt gãy toàn diện ở cả 6 chiều hợp đồng (Contract Dimensions)**:
   - **Cấu trúc `hooks.json`**: Đặt `"description"` (kiểu `string`) ngang hàng `"hooks"` ở top-level vi phạm cấu trúc `map[hookName]HookSpec` của Antigravity; thiếu trường `"matcher"` trong các nhóm `PreToolUse`.
   - **Stdin Payload (`camelCase` protojson)**: `agy_pretooluse_gate.py` tìm lệnh trong `_CMD_PATHS` nhưng thiếu `("toolCall", "args", "CommandLine")` → **mọi lệnh nguy hiểm (`git checkout -b antigravity-test`, ghi đè `docs/tdq/state.json`) đều lọt qua im lặng 100%**. `_common.py` đọc `cwd`, `session_id`, `prompt`, `tool_name`, `tool_input` nên mù hoàn toàn trước `workspacePaths`, `conversationId`, `lastUserInput`, `toolCall`.
   - **Lỗi `cwd = plugin_dir` trên Antigravity**: Antigravity chạy hook với thư mục làm việc (`cwd`) là thư mục chứa `hooks.json` (`~/.gemini/config/plugins/tdq-workflow`), và truyền đường dẫn project qua mảng `workspacePaths`. Cả `_common.payload_cwd()` lẫn `agy_stop_gate._cwd_of()` đều không đọc `workspacePaths` mà fallback về `os.getcwd()` = thư mục cài đặt plugin → không bao giờ tìm thấy `docs/tdq/state.json` của workspace, và nếu ghi sổ cái (`.tdq-read.jsonl`) sẽ **ghi bẩn thẳng vào thư mục plugin toàn cục**!
   - **Bug Dead-Code 100% trong `agy_stop_gate.py` (lines 177 & 185)**: Gán `now["_now_paths"] = repo_status_paths(cwd)` vào biến `now` nhưng lại gọi `_shell_changed_path(snap)` trên biến `snap` (vốn đã bị lọc bỏ `"_now_paths"` khi lưu xuống đĩa ở line 199) → `culprit` luôn bằng `""` → **2/3 cổng chặn của `agy_stop_gate.py` (`[TDQ:LOG]` và `[TDQ:TICK]`) là dead code tuyệt đối 100% ngay cả khi sửa đúng `cwd`**!
   - **Stdout Payload**: Mọi hook ở trạng thái cho phép ("allow") đều in rỗng `""` thay vì JSON hợp lệ (`{"decision": "allow"}`, `{}`); các hook Claude Code in plain text (cho `SessionStart`/`UserPromptSubmit`) hoặc `{"hookSpecificOutput": ...}` (cho `PreToolUse`/`Stop`) hoặc `{"decision": "block"}` (ngược nghĩa hoàn toàn với `{"decision": "continue"}` của Antigravity `Stop`!).
4. **Giải mã dứt điểm lỗi `tool call denied by pre-tool hook: ` ở phiên cha (Step 4 → Step 6)**: Không phải do `tdq-workflow` (đang tắt `enabled: false`, và test thực tế trả stdout rỗng) và cũng không phải do user hook `~/.gemini/config/hooks/auto-compact.ps1` (test thực nghiệm với đúng payload Step 4 trả `{"decision":"allow"}`, exit `0`), mà do **cơ chế bảo vệ nội bộ (built-in internal pre-tool security guard) của host Antigravity** chặn hành vi dùng `run_command` gọi trực tiếp endpoint nội bộ `LanguageServerService` kèm CSRF token.

---

## Phần 1: Kiểm Kê Toàn Bộ Hooks, Gates & Cơ Chế `Verify-by-Effect` của TDQ-Workflow

### 1.1. Danh mục đầy đủ 19 file Python trong `TDQ-Workflow/hooks/scripts/` vs Bản cài Antigravity (`tdq-workflow` v0.74.0)

Trong repo gốc `C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow\hooks\` có `hooks.json` (12 binding cho 6 event của Claude Code) và **19 file `.py`** trong `hooks/scripts/` (gồm **2 module dùng chung**, **11 script hook chính cho Claude Code**, **3 adapter cho Codex/Antigravity**, và **3 utility CLI độc lập** — tổng cộng **14 gate/observer thực thi** + **3 CLI helper** + **2 thư viện**):

| # | File (`hooks/scripts/`) | Dòng | Vai trò & Sự kiện đăng ký | Có trong Plugin AGY (`v0.74.0`)? | Mã `[TDQ:*]` phát ra | Chặn (Block) hay Nhắc (Remind)? |
|---|---|---|---|---|---|---|
| 1 | `_common.py` | 311 | Thư viện chung: đọc/lọc stdin (`read_payload`), ghi/đọc sổ cái lượt `.tdq-turn.jsonl`, hàm xuất `remind()` / `block()` / `remind_force()` | **Có** (SHA khớp 100%) | Định nghĩa tuple 10 mã gốc `CODES` | Thư viện nền |
| 2 | `luat_gon.py` | 76 | Thư viện đọc & lọc "luật gọt" từ `skills/tdq-build/references/rules/chung.md` theo `muc_gat` (`off\|lite\|full\|ultra`) | Không | *(Phục vụ `TDQ:GON`)* | Thư viện nền |
| 3 | `session_start.py` | 390 | `SessionStart` (Claude): nạp Rule, `tdq_state.py next`, kiểm update plugin/project, gọi ngầm `tdq_setup.py --nen` (detached), nạp `TDQ:GON` & `TDQ:ANCHOR` | Không | `[TDQ]`, `TDQ:NEXT`, `TDQ:SETUP`, `TDQ:SEARCH`, `TDQ:GON`, `TDQ:ANCHOR` | Chỉ bơm ngữ cảnh (Plain text stdout) |
| 4 | `subagent_start.py` | 55 | `SubagentStart` (Claude): bơm toàn văn thân luật `TDQ:GON` cho sub-agent khi `muc_gat != "off"` | Không | `TDQ:GON` | Chỉ bơm ngữ cảnh (Plain text stdout) |
| 5 | `prompt_context.py` | 437 | `UserPromptSubmit` (Claude): xóa sổ cái lượt cũ (`turn_log_clear`), chụp snapshot đĩa đầu lượt (`turn_snapshot`), kiểm worktree mở, phát hiện câu duyệt (`looks_like_approval` → ghi `signal`), kiểm lệch `spec_sha256` | Không | `TDQ:WORKTREE`, `TDQ:INTAKE`, `TDQ:APPROVE`, `TDQ:NEXT`, `TDQ:GON`, `TDQ:QC` | Chỉ bơm ngữ cảnh (Plain text stdout) + ghi `turn_start` & `signal` |
| 6 | `edit_gate.py` | 291 | `PreToolUse` (`Edit\|Write\|MultiEdit\|NotebookEdit`): ghi `observe(edit)` & `observe(log_written)` vào `.tdq-turn.jsonl`; gác cổng duyệt, tick `[~]`, phân công team & vùng file `Chạm:` | Không | `TDQ:STATE`, `TDQ:TEAM`, `TDQ:APPROVE`, `TDQ:LOG`, `TDQ:TICK`, `TDQ:RULE:PY\|TS\|JS` | **Block**: `TDQ:STATE` (subagent), `TDQ:TEAM`, `TDQ:APPROVE` (file trong project), `TDQ:TICK` (`0 [~]`, `>1 [~]`, hoặc `>=3` edit liên tiếp không đổi `plan_sha`). **Remind**: còn lại |
| 7 | `read_gate.py` | 233 *(repo)* / 195 *(AGY)* | `PreToolUse` (`Read`): ghi sổ cái phiên `docs/tdq/.tdq-read.jsonl`; nhắc khi đọc lại nguyên file `>= 2KB` chưa đổi mtime/size, hoặc *(bản v0.97.0)* đọc lặp đoạn dòng trùng `>= 70%` từ 2 lần trở lên | **Có** *(bản cũ v0.74.0, thiếu kiểm overlap 70%)* | `TDQ:DOC` | **Remind** (`permissionDecision: "allow"`, không bao giờ block) |
| 8 | `bash_gate.py` | 208 | `PreToolUse` (`Bash\|PowerShell`): ghi `observe(state_cli)` & `observe(next_run)`; chặn subagent sửa ngoài `docs/tdq/artifacts/` trước `implement`; chặn tự ý chạy `tdq_state.py approve` không khớp `signal` của user | Không | `TDQ:TEAM`, `TDQ:APPROVE`, `TDQ:GIT`, `TDQ:OUTPUT`, `TDQ:STATE` | **Block**: `TDQ:TEAM`, `TDQ:APPROVE` (khi có `turn_start` mà thiếu `signal`). **Remind**: `TDQ:GIT`, `TDQ:OUTPUT`, `TDQ:STATE` |
| 9 | `search_gate.py` | 201 | `PreToolUse` (`Bash\|Grep\|PowerShell`): kiểm tra thứ tự tìm kiếm qua `scripts/search_rules.py` và `.tdq-search.jsonl` + mốc `.tdq-san-sang.json`; có cầu dao tự ngắt (`BREAKER_CHAN = 3`) | Không | `TDQ:SEARCH` | **Block** tìm code khi bỏ qua tầng khái niệm (`lsp`, `graphify`); **Remind** khi stand-down |
| 10 | `lsp_gate.py` | 163 | `PreToolUse` (`mcp__lsp__start_lsp\|blast_radius`): chặn gọi `start_lsp` thiếu `language_id` hoặc sai cặp `(root_dir, language_id)` trong `.tdq-lsp-module.json`; chặn `blast_radius` quá 3 file / `scope != 'exported'` / `include_transitive=true` / mở circuit breaker | Không | `TDQ:LSP` | **Block** (`permissionDecision: "deny"`) |
| 11 | `search_observe.py` | 222 | `UserPromptSubmit`, `PreToolUse` (`mcp__lsp__*`), `PostToolUse` (`mcp__lsp__*\|Bash\|PowerShell`), `PostToolUseFailure` (`mcp__lsp__*`): ghi nhận token prompt, cuộc gọi khái niệm (`khai_niem`) và kết quả/độ trễ LSP (`lsp_ket_qua`) vào `docs/tdq/.tdq-search.jsonl` | Không | *(Không phát mã)* | Thuần quan sát (in rỗng `""`, exit `0`) |
| 12 | `ask_gate.py` | 63 | `PreToolUse` (`AskUserQuestion`): nhắc trong pha `implement`/`qc` (khi chưa khai `implement_pause`) không được dừng hỏi vì lệch ngưỡng spec mà phải ghi `lech add` | Không | `TDQ:ASK` | **Remind** với `decide=False` (bỏ trống `permissionDecision`) |
| 13 | `stop_gate.py` | 367 | `Stop` (Claude): đối chiếu `remind` vs `observe` trong `.tdq-turn.jsonl` + so khớp snapshot đĩa `turn_start`; sau `MAX_STREAK = 3` lần chặn cùng `plan_sha` thì hạ xuống nhắc `TDQ:STUCK` | Không | `TDQ:LOG`, `TDQ:TICK`, `TDQ:UNFINISHED`, `TDQ:STUCK`, `TDQ:DOD`, `TDQ:NEXT`, `TDQ:STATE`, `TDQ:APPROVE`, `TDQ:GIT` | **Block** (`decision: "block"`): `TDQ:LOG`, `TDQ:TICK`, `TDQ:UNFINISHED`. **Remind**: các mã còn lại |
| 14 | `codex_edit_gate.py` | 223 | `.codex/hooks.json` `PreToolUse` (`apply_patch`, `Bash`): kiểm tra vùng file được phép (`TDQ_CODEX_VUNG`) và vùng khóa test (`TDQ_CODEX_KHOA`), trích đường dẫn từ patch body rồi gọi tiếp `edit_gate.py` | Không | `TDQ:VUNG` *(+ các mã của `edit_gate.py`)* | **Block** (`TDQ:VUNG`) khi chạm vùng khóa hoặc ngoài vùng khai |
| 15 | `agy_pretooluse_gate.py` | 157 | `hooks.json` (AGY) `PreToolUse`: bản rút gọn cho Antigravity, chỉ chặn cứng 2 luật tĩnh trên chuỗi lệnh shell | **Có** *(khác 1 dòng docstring so với v0.97.0)* | `TDQ:GIT`, `TDQ:STATE` | **Block** (`allow_tool: false`, `decision: "deny"`); im lặng `""` khi allow |
| 16 | `agy_stop_gate.py` | 211 | `hooks.json` (AGY) `Stop`: bản độc lập cho Antigravity, tự lưu snapshot tại `docs/tdq/.agy-stop-snapshot.json` và streak tại `.agy-stop-streak.json` (`MAX_STREAK = 3`) | **Có** (SHA khớp 100%) | `TDQ:LOG`, `TDQ:TICK`, `TDQ:UNFINISHED` | **Block** (`decision: "continue"`); im lặng `""` khi allow |
| 17 | `doc_file_gate.py` | 80 | CLI helper độc lập (`doc_file_gate.py <path>`), không gắn trong `hooks.json`: chặn tạo file `.md` ngoài thư mục quy hoạch (`docs/tdq/`, `docs/workinglog/`, ...) | Không | `[TDQ DOC-GATE REJECTION]` | CLI trả exit code `1` + stderr |
| 18 | `stop_batch_checker.py` | 78 | CLI/helper độc lập đọc `.claude/tmp/edited_files.txt` để chạy gom `scripts/doc_lint.py` và `py_compile` cuối lượt (được gọi trong `scripts/tdq_team.py` / `tests/test_stop_batching.py`, không khai trong `hooks.json`) | Không | `[TDQ Stop-Batch: ...]` | CLI trả exit code `1` + stderr khi lỗi cú pháp/lint |
| 19 | `strategic_compact_gate.py` | 106 | CLI helper độc lập (`record <tool>` / `check <phase>`) chấm điểm gánh nặng ngữ cảnh vào `.claude/tmp/tool_weights_tracker.json`, khuyên compact khi `>= 60` điểm ở ranh giới pha | Không | `[TDQ Strategic Compaction Advisory]` | CLI in cảnh báo ra stderr, exit `0` |

### 1.2. Bảng tổng hợp toàn bộ 23 mã `[TDQ:*]` trong hệ sinh thái Hook

Ngoài 10 mã đóng trong `_common.py` (lines 89–90: `TDQ:NEXT`, `TDQ:APPROVE`, `TDQ:LOG`, `TDQ:STATE`, `TDQ:GIT`, `TDQ:GON`, `TDQ:DOC`, `TDQ:SEARCH`, `TDQ:ASK`, `TDQ:LSP`), mã nguồn thực tế trong `hooks/scripts/` phát ra thêm **13 mã mở rộng**:
- Nhóm tiến độ & thực thi: `TDQ:TICK`, `TDQ:UNFINISHED`, `TDQ:STUCK`, `TDQ:DOD`, `TDQ:QC`, `TDQ:INTAKE`, `TDQ:ANCHOR`, `TDQ:SETUP`.
- Nhóm điều phối đội ngũ & vùng file: `TDQ:TEAM`, `TDQ:WORKTREE`, `TDQ:VUNG`.
- Nhóm quy tắc code & ngữ cảnh: `TDQ:OUTPUT`, `TDQ:RULE:PY`, `TDQ:RULE:TS`, `TDQ:RULE:JS`.

Trong bản cài Antigravity (`C:\Users\admin\.gemini\config\plugins\tdq-workflow`), `build_portable.py` (lines 243–251) chỉ đóng gói **3 hook** chứa **6 mã** (`TDQ:GIT`, `TDQ:STATE`, `TDQ:DOC`, `TDQ:LOG`, `TDQ:TICK`, `TDQ:UNFINISHED`), bỏ lại hoàn toàn 17 mã và toàn bộ hệ thống kiểm soát `TDQ:APPROVE`, `TDQ:SEARCH`, `TDQ:LSP`, `TDQ:TEAM`, `TDQ:GON`, `TDQ:NEXT`.

### 1.3. Giải phẫu cơ chế `Verify-by-Effect` & Snapshot đĩa SHA-256

TDQ-Workflow không đọc transcript và không tin dòng `✓ [TDQ:...]` do model tự in ra, mà xác minh bằng **2 nguồn bằng chứng độc lập** (`scripts/tdq_state.py`, lines 574–824 & 1069–1081; `hooks/scripts/stop_gate.py`, lines 54–119 & 270–334):

1. **Nguồn 1 — Sổ cái lượt (`docs/tdq/.tdq-turn.jsonl`)**:
   - Đầu lượt (`prompt_context.py` line 253): gọi `turn_log_clear(cwd, sid)` xóa sổ cái cũ của phiên, sau đó ghi dòng `kind="turn_start"` chứa kết quả `turn_snapshot(cwd)`. Nếu có cổng đang chờ duyệt, phân tích prompt của user để ghi dòng `kind="signal"` (`matched: true/false`).
   - Giữa lượt: `edit_gate.py` ghi `kind="observe", event="edit"` và `event="log_written"`; `bash_gate.py` ghi `event="state_cli"` và `event="next_run"`; các hàm `remind()`/`block()` ghi `kind="remind"` và `kind="block"`.
2. **Nguồn 2 — Snapshot vân tay đĩa SHA-256 (`turn_snapshot(cwd)` trong `scripts/tdq_state.py`, lines 1069–1081)**:
   - **`log_sha`**: Băm `sha256_file` của file `docs/workinglog/YYYY-MM-DD.md` (hoặc `None` nếu chưa tạo). Cho phép phát hiện cập nhật working log bằng lệnh shell (`cat >>`, `tee`, Python script) dù không đi qua tool `Edit`/`Write`.
   - **`repo_sha` (`repo_status_digest`, lines 686–725)**:
     - Chạy `git -C <cwd> status --porcelain --untracked-files=all -- :(top) :(top,exclude)docs/tdq :(top,exclude)docs/workinglog :(top,exclude)graphify-out` (timeout 2s) **kết hợp** `git diff HEAD -- :(top) ...` rồi băm `sha256(status + b"\0" + diff)`.
     - **Điểm tinh vi cho file untracked (`?? `)**: Vì `git status --porcelain` không đổi chuỗi `?? path` khi sửa nội dung file mới và `git diff HEAD` bỏ qua file untracked, hàm `_untracked_mark` (lines 668–683) băm trực tiếp nội dung `sha256_file(path)` cho tối đa `200` file untracked có kích thước `<= 256 KB` (tổng ngân sách đọc `4 MB`/lần chụp); file `> 256 KB` mới fallback về `size:mtime_ns`. Nhờ đó lệnh `touch` hoặc ghi đè nội dung y hệt không gây báo động giả.
     - Loại trừ cứng 3 thư mục kế toán (`BOOKKEEPING_PATHS = ("docs/tdq", "docs/workinglog", "graphify-out")`) ngay từ pathspec của Git để việc hook tự ghi `.tdq-turn.jsonl` / `state.json` không tự gây block vòng lặp.
   - **`plan_sha` (`plan_tick_state`, lines 782–823)**: Băm `sha256_file` toàn bộ file plan hiện hành để phát hiện xem bất kỳ checkbox `- [ ]` / `- [~]` / `- [x]` / `- [>]` nào có dịch chuyển trong lượt hay không.
   - *(Ngoài ra đối với `spec_sha256` khi kiểm tra sửa spec sau khi duyệt tại `prompt_context.py` line 369, `sha256_noi_dung` tại `tdq_state.py` lines 582–602 chỉ băm từ tiêu đề `## ` đầu tiên trở đi để bỏ qua phần header metadata).*
3. **Biến thể trên Antigravity (`agy_stop_gate.py`, lines 92–207)**:
   - Do bundle Antigravity không có hook đầu lượt (`PreInvocation`/`UserPromptSubmit`), `agy_stop_gate.py` tự lưu snapshot của lần `Stop` trước vào `docs/tdq/.agy-stop-snapshot.json`.
   - **2 lỗi thiết kế chí mạng trong biến thể này**:
     1. **Mất dấu lượt đầu tiên**: Ở lần `Stop` đầu tiên của phiên (`snap is None`), nó chưa có baseline nên bỏ qua hoàn toàn kiểm tra `TDQ:LOG` và `TDQ:TICK`!
     2. **Bug Dead-Code 100% (`_now_paths`)**: Tại line 177, code gán `now["_now_paths"] = repo_status_paths(cwd)`, nhưng tại line 185 lại gọi `culprit = _shell_changed_path(snap)` (đọc `snap.get("_now_paths")` luôn là `None` vì line 199 xóa `"_now_paths"` trước khi lưu `snap`!). Kết quả là `culprit` luôn trả về `""`, vô hiệu hóa vĩnh viễn cả `[TDQ:LOG]` lẫn `[TDQ:TICK]`.

---

## Phần 2: Kiểm Toán Từng Dòng Schema & Hợp Đồng với Antigravity Ground Truth

Đối chiếu trực tiếp với `C:\Users\admin\.gemini\antigravity\builtin\skills\agy-customizations\docs\hooks.md` và `docs\plugins.md`:

### 2a. Vị trí file & Cấu trúc JSON cấp cao nhất (`hooks.json`)

- **Chuẩn Antigravity** (`docs/plugins.md` lines 59–70; `docs/hooks.md` lines 15–56):
  - Native plugin (có `plugin.json` ở gốc) **bắt buộc** đặt `hooks.json` ngay tại gốc `<plugin_dir>/hooks.json`. *(Điểm này `tdq-workflow` làm đúng: có `C:\Users\admin\.gemini\config\plugins\tdq-workflow\hooks.json`)*.
  - Cấu trúc JSON cấp cao nhất **phải là map từ `<tên-hook>` sang cấu hình sự kiện (`HookSpec`)**:
    ```json
    {
      "tdq-gates": {
        "enabled": true,
        "PreToolUse": [ { "matcher": "run_command", "hooks": [ ... ] } ],
        "Stop": [ { "type": "command", "command": "..." } ]
      }
    }
    ```
- **Thực tế trong `C:\Users\admin\.gemini\config\plugins\tdq-workflow\hooks.json` (lines 1–33)**:
  ```json
  {
    "description": "TDQ workflow for Antigravity CLI (agy) — auto-generated...",
    "hooks": {
      "PreToolUse": [ { "hooks": [ ... ] }, { "hooks": [ ... ] } ],
      "Stop": [ { "hooks": [ ... ] } ]
    }
  }
  ```
- **Phát hiện vi phạm (3 lỗi cấu trúc trong cùng 1 file 33 dòng!)**:
  1. **Khóa `"description"` kiểu `string` ở top-level (line 2)**: Trong Antigravity, mỗi top-level key được unmarshal thành một object `HookSpec`. Giá trị chuỗi `"TDQ workflow..."` không phải object JSON, gây lỗi parse `cannot unmarshal string into Go value of type HookSpec` làm hỏng toàn bộ file `hooks.json`!
  2. **Khóa `"hooks"` ở top-level (line 3)**: Đây là cú pháp của Claude Code/Codex. Kể cả khi xóa `"description"`, Antigravity sẽ hiểu `"hooks"` chỉ là **tên của một hook duy nhất có tên `"hooks"`** chứ không phải wrapper gốc.
  3. **Sai cấu trúc mảng `Stop` (lines 22–31)**: Theo `docs/hooks.md` lines 104–106, `Stop`, `SessionStart`, `PreInvocation`, `PostInvocation` có cấu trúc **Flat (danh sách trực tiếp các handler object `{"type": "command", "command": "..."}`)**, KHÔNG bọc trong `{"hooks": [...]}` như `PreToolUse`/`PostToolUse`! Bọc `{"hooks": [...]}` bên trong `Stop` khiến handler `command` ở cấp trong bị trống (`command == ""`) dưới bộ đọc của Antigravity!

### 2b. Tên Sự Kiện Hỗ Trợ (Supported Event Names)

| Sự kiện trong TDQ-Workflow (`hooks/hooks.json`) | Có được Antigravity hỗ trợ không? (`docs/hooks.md` lines 87–107) | Sự kiện tương đương trên Antigravity & Khác biệt hợp đồng |
|---|---|---|
| `SessionStart` | **Có** (`SessionStart`) | Cấu trúc Flat; stdout phải là `{"injectSteps": [{"systemMessage": {"systemMessage": "..."}}]}` thay vì plain text. |
| `SubagentStart` | **KHÔNG TỒN TẠI** | Antigravity không có sự kiện `SubagentStart`. Có thể bắt gián tiếp qua `PreToolUse` với `"matcher": "invoke_subagent"` hoặc `SessionStart` của subagent. |
| `UserPromptSubmit` | **KHÔNG TỒN TẠI** | Tương đương gần nhất là **`PreInvocation`** (chạy trước khi gọi model, đọc prompt user qua trường `lastUserInput` thay vì `prompt`, và xuất `injectSteps` thay vì plain text). Lưu ý: `PreInvocation` chạy trước **mỗi lần gọi model** trong vòng lặp agent (kể cả sau khi chạy tool, xem `invocationNum`), không chỉ 1 lần đầu lượt như `UserPromptSubmit`! Nếu gọi `turn_log_clear` vô điều kiện ở mọi `PreInvocation`, sổ cái lượt sẽ bị xóa sạch sau mỗi tool call! |
| `PreToolUse` | **Có** (`PreToolUse`) | Cấu trúc Grouped (`matcher` + `hooks`); hỗ trợ chặn (`deny`), hỏi (`ask`/`force_ask`), cho phép (`allow`), và ghi đè tham số (`overwrite`), **nhưng KHÔNG có kênh bơm `additionalContext` vào ngữ cảnh như Claude Code**! |
| `PostToolUse` | **Có** (`PostToolUse`) | Cấu trúc Grouped; input có `error` nếu tool lỗi; stdout chỉ nhận `{}` (không bơm được ngữ cảnh). |
| `PostToolUseFailure` | **KHÔNG TỒN TẠI** | Trên Antigravity, lỗi thực thi tool vẫn đi vào chính `PostToolUse` kèm trường `"error": "exit status 1"` (`docs/hooks.md` line 252). |
| *(Không dùng trong TDQ)* | **Có** (`PostInvocation`) | Cho phép kiểm tra đầu ra model và ép chạy tiếp bằng `"terminationBehavior": "force_continue"` kèm `injectSteps`. |
| `Stop` | **Có** (`Stop`) | Cấu trúc Flat; input có `terminationReason` (`"NO_TOOL_CALL"`, `"ERROR"`, `"USER_CANCELED"`, ...); chặn dừng bằng **`"decision": "continue"`** (ngược hẳn `"decision": "block"` của Claude Code!). |

### 2c. Tên Tool trong `matcher` (`PreToolUse` / `PostToolUse`)

- **Chuẩn Antigravity** (`docs/hooks.md` lines 108–120): Tên tool là tên `CORTEX_STEP_TYPE_*` viết thường bỏ tiền tố: `run_command`, `read_file`, `edit_file`, `write_file`, `grep_search`, `find_by_name`, `list_dir`, `ask_question`, `invoke_subagent`, `mcp_<server>_<tool>` (lưu ý: **một dấu gạch dưới `_`**, ví dụ `mcp_lsp_start_lsp`, KHÔNG phải hai dấu gạch dưới `mcp__lsp__start_lsp` của Claude Code!).
- **Thực tế trong TDQ**:
  - Trong `C:\Users\admin\.gemini\config\plugins\tdq-workflow\hooks.json` (lines 5–20): **Hoàn toàn KHÔNG khai báo trường `"matcher"`** ở cả 2 nhóm `PreToolUse`! Hệ quả: nếu hook chạy, cả `agy_pretooluse_gate.py` (chỉ kiểm lệnh shell) lẫn `read_gate.py` (chỉ kiểm đọc file) đều bị kích hoạt lãng phí trên **mọi tool call** (`edit_file`, `grep_search`, `list_dir`, MCP...).
  - Trong `TDQ-Workflow/hooks/hooks.json` (lines 40–117): Toàn bộ matcher viết theo tên tool của Claude Code (`Edit|Write|MultiEdit|NotebookEdit`, `Read`, `Bash|PowerShell`, `Bash|Grep|PowerShell`, `mcp__(plugin_tdq-workflow_)?lsp__.*`, `AskUserQuestion`) — **không khớp bất kỳ tên tool nào của Antigravity**!

### 2d. Thực thi Shell trên Windows (`cmd /c`, `cwd`, `PLUGIN_ROOT`)

- **Chuẩn Antigravity** (`docs/hooks.md` lines 129–141):
  - Chạy qua `cmd /c` trên Windows với **`cwd` = thư mục chứa `hooks.json`**.
  - Cấp biến môi trường `PLUGIN_ROOT` và `PLUGIN_DATA` (KHÔNG tự thay thế chuỗi vào `command`; muốn mở rộng trong `cmd.exe` phải viết `%PLUGIN_ROOT%` hoặc dùng đường dẫn tương đối `./hooks/scripts/...` vì `cwd` đã là thư mục plugin!).
- **Thực tế kiểm chứng**:
  1. Trong `C:\Users\admin\.gemini\config\plugins\tdq-workflow\hooks.json` (lines 8, 16, 26):
     `py -3 "C:\Users\admin\.gemini\config\plugins\tdq-workflow/hooks/scripts/agy_pretooluse_gate.py"`
     - `py -3` có sẵn trên máy Windows này và chạy được dưới `cmd /c`, **nhưng** nướng cứng đường dẫn tuyệt đối của máy build (`C:\Users\admin\...`) vào `hooks.json` một cách không cần thiết (vì Antigravity đã đặt `cwd = <plugin_dir>`, chỉ cần viết `py -3 "hooks/scripts/..."` là chạy portable trên mọi máy Windows!).
  2. Trong `TDQ-Workflow/hooks/hooks.json` (lines 9, 19, 29...):
     `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/session_start.py" || py -3 "${CLAUDE_PLUGIN_ROOT}/..."`
     - Khi chạy qua `cmd /c` (Test `B0`), `cmd.exe` **không mở rộng cú pháp bash `${CLAUDE_PLUGIN_ROOT}`** (và Antigravity cũng không đặt biến `CLAUDE_PLUGIN_ROOT`). Cả 3 nhánh `||` đều sập với **exit code `2`**:
       `can't open file '...mock_plugin\${CLAUDE_PLUGIN_ROOT}\hooks\scripts\session_start.py': [Errno 2] No such file or directory`.

### 2e. Định dạng Stdin JSON (`camelCase` protojson)

Bảng đối chiếu trường dữ liệu thực tế Antigravity truyền vào `stdin` so với code đọc payload của TDQ-Workflow:

| Ý nghĩa trường | Antigravity Stdin (`docs/hooks.md` lines 149–194) | `_common.py` (`read_payload`, lines 97–145) | `agy_pretooluse_gate.py` (lines 57–79) | `agy_stop_gate.py` (lines 55–65) | Hệ quả thực tế |
|---|---|---|---|---|---|
| ID phiên hội thoại | `"conversationId": "..."` | Đọc `payload.get("session_id")` → trả `""` | Không đọc | Không đọc | Mất định danh phiên trong sổ cái |
| Thư mục project | `"workspacePaths": ["C:\\..."]` *(mảng)* | Đọc `payload.get("cwd")` → `None` → fallback `os.getcwd()` (**= `plugin_dir`!**) | Không đọc | Thử `cwd`, `workingDirectory`, `workspace_root`, `project_root`, `root` → **thiếu `workspacePaths`** → fallback `os.getcwd()` (**= `plugin_dir`!**) | **Mù hoàn toàn thư mục project!** Tìm `state.json` nhầm vào thư mục cài plugin và ghi bẩn sổ cái vào `plugin_dir`! |
| Prompt của user | `"lastUserInput": "..."` | Đọc `payload.get("prompt")` → `""` | Không đọc | Không đọc | Không nhận diện được câu duyệt spec/plan hay `_tdq_direct` |
| Tên tool gọi | `"toolCall": {"name": "run_command"}` | Đọc `payload.get("tool_name")` → `None` | Không đọc tên tool | N/A | `search_gate.py`, `lsp_gate.py`, `search_observe.py` thoát ngay lập tức |
| Lệnh shell | `"toolCall": {"args": {"CommandLine": "..."}}` | Đọc `tool_input.command` / `cmd` → `""` | Thử 5 đường dẫn `_CMD_PATHS`, **thiếu `("toolCall", "args", "CommandLine")`** → trả `""`! | N/A | **`agy_pretooluse_gate.py` thoát im lặng, bỏ lọt 100% lệnh cấm!** |
| Đường dẫn file đọc/sửa | `"toolCall": {"args": {"Path": "..."}}` | Đọc `tool_input.file_path` / `notebook_path` → `""` | Không đọc | N/A | `read_gate.py` và `edit_gate.py` thoát ngay tại kiểm tra rỗng |
| Mẫu tìm kiếm Grep | `"toolCall": {"args": {"Query": "...", "SearchPath": "..."}}` | Đọc `tool_input.pattern` / `path` → `""` | Không đọc | N/A | `search_gate.py` không đọc được mẫu tìm kiếm |

### 2f. Định dạng Stdout JSON theo từng Sự Kiện

| Sự kiện | Hợp đồng Stdout của Antigravity (`docs/hooks.md`) | Thực tế TDQ-Workflow xuất ra | Tương thích? |
|---|---|---|---|
| `SessionStart` | JSON object: `{"injectSteps": [{"systemMessage": {"systemMessage": "..."}}]}` | `session_start.py` in **văn bản thuần (plain text)** `[TDQ] Rule: ...` (không phải JSON!) | **Hỏng 100%** (lỗi parse JSON trên stdout) |
| `PreInvocation` | JSON object: `{"injectSteps": [{"systemMessage": {"systemMessage": "..."}}], "terminationBehavior": ""}` | `prompt_context.py` in **văn bản thuần (plain text)** `[TDQ:NEXT] ...` | **Hỏng 100%** (lỗi parse JSON trên stdout) |
| `PreToolUse` (Allow) | JSON object bắt buộc có `decision`: `{"decision": "allow"}` | Mọi gate TDQ (`agy_pretooluse_gate.py`, `read_gate.py`, `edit_gate.py`, `bash_gate.py`...) đều **không in gì cả (`""` - empty stdout)** khi cho phép! | **Vi phạm hợp đồng** (`docs/hooks.md` line 147 & 206 yêu cầu xuất JSON object với `decision` required) |
| `PreToolUse` (Remind) | Antigravity **KHÔNG có trường bơm context cho model** trong `PreToolUse` (`reason` chỉ giải thích cho permission/block; chỉ `SessionStart`/`PreInvocation`/`PostInvocation`/`Stop` mới bơm message cho model) | `_common.remind()` và `read_gate.py` xuất `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow", "additionalContext": "..."}}` | **Hỏng 100%** (sai toàn bộ schema JSON, thiếu trường `decision`, dư `hookSpecificOutput` làm `protojson` báo lỗi unknown field) |
| `PreToolUse` (Deny) | `{"decision": "deny", "reason": "..."}` | - Claude gates (`_common.block`): `{"hookSpecificOutput": {"permissionDecision": "deny", ...}}` → **Sai schema hoàn toàn**.<br>- `agy_pretooluse_gate.py`: `{"allow_tool": false, "decision": "deny", "reason": "...", "message": "..."}` → Có `"decision": "deny"` và `"reason"`, **nhưng dư 2 khóa lạ `"allow_tool"` và `"message"`** (nếu `protojson.UnmarshalOptions` của Antigravity không bật `DiscardUnknown`, 2 khóa lạ này sẽ gây lỗi unmarshal!). | **Claude gates: Hỏng 100%**.<br>**AGY gate: Rủi ro lỗi `protojson` do dư khóa lạ** (và thực tế không bao giờ chạm tới hàm `_deny` vì lỗi đọc stdin ở mục 2e!). |
| `PostToolUse` | JSON object rỗng: `{}` | `search_observe.py` in rỗng `""` (empty stdout, không phải `{}`) | **Sai chuẩn** (`""` thay vì `{}`) |
| `Stop` (Block dừng) | `{"decision": "continue", "reason": "..."}` *(dòng 406: "Set to `continue` to block the stop and re-enter the loop. Any other value allows the agent to stop.")* | - `stop_gate.py` (Claude): xuất `{"decision": "block", "reason": "...", "stop_hook_active": false}` → **Ngược nghĩa 100%!** Giá trị `"block"` khác `"continue"` nên Antigravity hiểu là **CHO PHÉP DỪNG NGAY LẬP TỨC** (đồng thời dư khóa `stop_hook_active`)!<br>- `agy_stop_gate.py`: xuất `{"decision": "continue", "reason": "..."}` → **Đúng schema khi block**, nhưng không bao giờ kích hoạt được trên thực tế vì lỗi `cwd` (mục 2e) và bug `_now_paths` (mục 1.3), và khi cho phép dừng lại in rỗng `""` thay vì JSON hợp lệ! | **`stop_gate.py`: Ngược nghĩa hoàn toàn**.<br>**`agy_stop_gate.py`: Đúng JSON khi block nhưng tê liệt thực tế**. |

---

## Phần 3: Kết Quả Chạy Thực Nghiệm Mô Phỏng Trên Windows (`cmd /c`)

Toàn bộ các ca kiểm thử dưới đây được chạy thật bằng `C:\Users\admin\.gemini\antigravity\brain\2a408580-dde6-4a41-aeda-5a1f871c0366\scratch\sub3_hooks_sim\run_sim.py` gọi trực tiếp Win32 `cmd /c <command>` với `cwd = mock_plugin` (bản sao nguyên trạng của `C:\Users\admin\.gemini\config\plugins\tdq-workflow`), `env` có `PLUGIN_ROOT` & `PLUGIN_DATA` (không có `CLAUDE_PLUGIN_ROOT`), cùng một repo Git thật tại `mock_ws` đang mở request `phase = "implement"` có 2 task `- [ ]` chưa tick.

### 3.1. Bảng Kết Quả Suite A — Bản Cài Plugin Antigravity (`tdq-workflow` v0.74.0)

| Mã Test | Hook Script | Payload Stdin đưa vào | Exit | Stdout thực tế | Kết luận theo Hợp đồng Antigravity |
|---|---|---|---|---|---|
| **A1** | `agy_pretooluse_gate.py` | AGY `PreToolUse`: `{"toolCall": {"name": "run_command", "args": {"CommandLine": "pytest -q"}}, ...}` | `0` | `""` *(0 byte)* | **SAI HỢP ĐỒNG**: Trả chuỗi rỗng thay vì `{"decision": "allow"}`. |
| **A2** | `agy_pretooluse_gate.py` | AGY `PreToolUse`: `{"toolCall": {"name": "run_command", "args": {"CommandLine": "git checkout -b antigravity-test"}}, ...}` | `0` | `""` *(0 byte)* | **LỌT CỔNG NGHIÊM TRỌNG (BYPASS 100%)**: Lệnh tạo nhánh cấm `antigravity-test` (chính là bài smoke-test ghi trong `README.md` line 35 của bundle!) **KHÔNG HỀ BỊ CHẶN** vì `_first_command` không biết đọc `toolCall.args.CommandLine`! |
| **A3** | `agy_pretooluse_gate.py` | AGY `PreToolUse`: `{"toolCall": {"name": "run_command", "args": {"CommandLine": "echo {} > docs/tdq/state.json"}}, ...}` | `0` | `""` *(0 byte)* | **LỌT CỔNG NGHIÊM TRỌNG (BYPASS 100%)**: Ghi đè trực tiếp `docs/tdq/state.json` qua shell lọt qua hoàn toàn không một lời cảnh báo! |
| **A4** *(Đối chứng)* | `agy_pretooluse_gate.py` | Claude `snake_case`: `{"tool_name": "run_command", "tool_input": {"command": "git checkout -b antigravity-test"}}` | `0` | `{"allow_tool": false, "decision": "deny", "reason": "[TDQ:GIT] branch/worktree name 'antigravity-test'...", "message": "..."}` | Chứng minh logic regex bên trong vẫn sống nhưng chỉ chạy khi nhận schema `tool_input.command` của Claude Code; đầu ra dư 2 khóa lạ `allow_tool`, `message`. |
| **A5** | `agy_pretooluse_gate.py` | AGY `PreToolUse`: `{"toolCall": {"name": "edit_file", "args": {"Path": ".../app.py", ...}}}` | `0` | `""` *(0 byte)* | Do thiếu `"matcher"` trong `hooks.json`, Python bị spawn vô ích trên cả mọi lệnh `edit_file`. |
| **A6 & A7** | `read_gate.py` | AGY `PreToolUse` (gọi 2 lần liên tiếp trên cùng file `app.py` 4.5 KB): `{"toolCall": {"name": "read_file", "args": {"Path": ".../app.py"}}, ...}` | `0` | Lần 1: `""`<br>Lần 2: `""` | **VÔ HIỆU HÓA 100%**: `build_portable.py` (line 247) thậm chí đã ghi chú thừa nhận `read_gate.py` là no-op vì tìm `tool_input.file_path`, không đọc `toolCall.args.Path`. |
| **A8 & A9** *(Đối chứng)* | `read_gate.py` | Payload có `tool_input.file_path` nhưng không có `cwd` (như AGY) gọi 2 lần liên tiếp | `0` | Lần 1: `""`<br>Lần 2: `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow", ..., "additionalContext": "[TDQ:DOC] app.py (4 KB)..."}}` | **2 LỖI CÙNG LÚC**:<br>1. **Ghi bẩn thư mục cài plugin** (`A8b` xác nhận file `mock_plugin\docs\tdq\.tdq-read.jsonl` bị tạo ra ngay trong thư mục plugin do thiếu `cwd`!).<br>2. Output `hookSpecificOutput` sai hoàn toàn schema `PreToolUse` của Antigravity! |
| **A10** | `agy_stop_gate.py` | AGY `Stop`: `{"executionNum": 1, "terminationReason": "NO_TOOL_CALL", "fullyIdle": true, "workspacePaths": [".../mock_ws"], ...}` với `cwd = mock_plugin` | `0` | `""` *(0 byte)* | **LỌT CỔNG 100%**: Dù `mock_ws` đang ở pha `implement` còn 2 task mở, `_cwd_of(payload)` bỏ qua `workspacePaths`, đọc `mock_plugin/docs/tdq/state.json` (không tồn tại) rồi thoát im lặng! |
| **A11 → A13b** *(Đối chứng sửa `cwd`)* | `agy_stop_gate.py` | Truyền cưỡng bức `"cwd": ".../mock_ws"`:<br>- `A11`: Lần Stop 1 (2 task mở)<br>- `A12`: Sửa `src/app.py`, KHÔNG ghi working log<br>- `A13b`: Sửa tiếp `src/app.py` + ĐÃ ghi working log, KHÔNG tick plan | `0` | Cả 3 ca đều in y hệt:<br>`{"decision": "continue", "reason": "[TDQ:UNFINISHED] The plan still has 2 open task(s)..."}` | **CHỨNG MINH THỰC NGHIỆM BUG `_now_paths`**: Ở `A12` lẽ ra phải báo `[TDQ:LOG]`, ở `A13b` lẽ ra phải báo `[TDQ:TICK]`, nhưng cả hai đều rơi thẳng xuống `[TDQ:UNFINISHED]` vì `snap.get("_now_paths")` luôn bằng `None` (lines 177 & 185)! Nếu pha là `qc` (không thỏa `unfinished_reason`), sửa code không ghi log / không tick plan sẽ **lọt hoàn toàn**! |

### 3.2. Bảng Kết Quả Suite B — Bộ Hook Chính của Repo `TDQ-Workflow` (`v0.97.0`) dưới Runner Antigravity

| Mã Test | Sự kiện & Script | Định dạng Payload | Exit | Stdout / Stderr thực tế (rút gọn) | Kết luận tương thích Antigravity |
|---|---|---|---|---|---|
| **B0** | `hooks/hooks.json` raw command (`session_start.py`) | AGY `SessionStart` chạy nguyên chuỗi lệnh có `${CLAUDE_PLUGIN_ROOT}` qua `cmd /c` | **`2`** | Stdout: `""`<br>Stderr: `python.exe: can't open file '...mock_plugin\${CLAUDE_PLUGIN_ROOT}\hooks\scripts\session_start.py': [Errno 2]` (lặp 3 lần) | **CHẾT NGAY TỪ SHELL (`rc=2`)**: `cmd /c` không bung biến `${CLAUDE_PLUGIN_ROOT}` và biến này cũng không tồn tại trên Antigravity. |
| **B1a / B1b** | `SessionStart` → `session_start.py` | `B1a`: AGY camelCase<br>`B1b`: Claude snake_case (`source="compact"`) | `0` | Plain text (655B ở `B1a` vì nhầm `cwd=mock_plugin` tưởng `no request`; 6,435B ở `B1b` gồm `[TDQ] Rule...`, `[TDQ:GON]`, `[TDQ:ANCHOR]`) | **HỎNG SCHEMA STDOUT (`INVALID_JSON`)**: Xuất plain text thay vì `{"injectSteps": [{"systemMessage": {"systemMessage": "..."}}]}`. Ngoài ra `B1a` đọc nhầm thư mục plugin thay vì `workspacePaths[0]`, và `B1b` tự động chạy đồng bộ tạo `.claude/CLAUDE.md` & `.codex/hooks.json`! |
| **B2a / B2b** | `PreInvocation` → `prompt_context.py` | `B2a`: AGY (`lastUserInput="approve spec"`)<br>`B2b`: Claude (`prompt="implement T1.1"`) | `0` | `B2a`: `[TDQ:INTAKE] (same as last turn — unchanged)\n`<br>`B2b`: `[TDQ:NEXT] 2026-11-13-sim...` | **HỎNG CẢ STDIN LẪN STDOUT**: `B2a` không đọc `workspacePaths` và `lastUserInput` nên báo nhầm `TDQ:INTAKE` và tạo rác `docs/tdq/` trong `mock_plugin`; stdout là plain text thay vì `injectSteps`. |
| **B3a / B3b** | `PreToolUse` → `edit_gate.py` | `B3a`: AGY `edit_file`<br>`B3b`: Claude `Edit` | `0` | `B3a`: `""`<br>`B3b`: `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow", ..., "additionalContext": "[TDQ:LOG]..."}}` | `B3a` câm hoàn toàn vì không có `tool_input.file_path`; `B3b` xuất `hookSpecificOutput` không tương thích `PreToolUse` của Antigravity. |
| **B4a / B4b** | `PreToolUse` → `bash_gate.py` | `B4a`: AGY `run_command` (`antigravity-bad`)<br>`B4b`: Claude `Bash` | `0` | `B4a`: `""`<br>`B4b`: `{"hookSpecificOutput": {..., "additionalContext": "[TDQ:GIT]..."}}` | `B4a` câm hoàn toàn; `B4b` sai schema stdout Antigravity. |
| **B5a / B5b** | `PreToolUse` → `search_gate.py` | `B5a`: AGY `grep_search`<br>`B5b`: Claude `Grep` | `0` | `B5a`: `""`<br>`B5b`: `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "[TDQ:SEARCH] Code search before any concept query..."}}` | `B5a` câm hoàn toàn (không nhận ra `grep_search` hay `run_command`); kể cả khi chặn ở `B5b`, Antigravity không hiểu `hookSpecificOutput.permissionDecision: "deny"` nên sẽ không chặn đúng hợp đồng! |
| **B6a / B6b** | `PreToolUse` → `lsp_gate.py` | `B6a`: AGY `mcp_lsp_start_lsp`<br>`B6b`: Claude `mcp__lsp__start_lsp` | `0` | `B6a`: `""` *(stderr: `payload without tool_input — silent`)*<br>`B6b`: `{"hookSpecificOutput": {..., "permissionDecision": "deny", "permissionDecisionReason": "[TDQ:LSP]..."}}` | `B6a` thoát sớm ở line 139 vì thiếu `tool_input`; `B6b` sai schema stdout Antigravity. |
| **B7a / B7b** | `PreToolUse` → `ask_gate.py` | `B7a`: AGY `ask_question`<br>`B7b`: Claude `AskUserQuestion` | `0` | `B7a`: `""` *(stderr: `phase=None · silent`)*<br>`B7b`: `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": "[TDQ:ASK]..."}}` | `B7a` không tìm thấy `state.json` do thiếu `cwd`; `B7b` thiếu `decision` và bọc trong `hookSpecificOutput`. |
| **B8a / B8b** | `PostToolUse` → `search_observe.py` | `B8a`: AGY `run_command` (`graphify query`)<br>`B8b`: Claude `Bash` | `0` | Cả hai đều in `""` *(nhưng chỉ `B8b` ghi được dòng `khai_niem · graphify:query` vào `.tdq-search.jsonl`, còn `B8a` không ghi được gì!)* | `B8a` không ghi nhận được truy vấn khái niệm vì thiếu `tool_name` / `tool_input` / `cwd`; cả hai đều xuất `""` thay vì `{}` theo hợp đồng `PostToolUse`. |
| **B9a / B9b** | `Stop` → `stop_gate.py` | `B9a`: AGY `Stop`<br>`B9b`: Claude `Stop` | `0` | `B9a`: `""`<br>`B9b`: `{"decision": "block", "reason": "[TDQ:LOG] Repo changed (src/app.py)..."}` | **`B9b` ĐẢO NGƯỢC NGỮ NGHĨA NGUY HIỂM**: `stop_gate.py` trả `"decision": "block"`, nhưng trong Antigravity `Stop` (`docs/hooks.md` line 406), mọi giá trị `decision != "continue"` đều có nghĩa là **CHO PHÉP DỪNG**! |

---

## Phần 4: Điều Tra Nguyên Nhân Lỗi `tool call denied by pre-tool hook: ` ở Phiên Cha (Step 4 → Step 6)

### 4.1. Bằng chứng đối chiếu dòng thời gian & cấu hình thực tế

Trích xuất metadata từ `transcript.jsonl` của phiên cha (`2a408580-dde6-4a41-aeda-5a1f871c0366`, ghi trong `sim_results.json` lines 55–169) và kiểm tra toàn bộ các file `hooks.json` trên máy:

1. **Toàn bộ các `hooks.json` tồn tại trên hệ thống**:
   - Workspace `c:\Users\admin\Documents\Projects\TDQ-Workflow-Antigravity`: **Không có** `.agents/hooks.json`.
   - Các plugin đang bật (`chrome-devtools-plugin`, `gdocs`, `gdrive`, `gemini-api`, `google-antigravity-sdk`, `gsheets`, `gslides`): **Không có** bất kỳ file `hooks.json` nào.
   - Plugin `C:\Users\admin\.gemini\config\plugins\tdq-workflow\hooks.json`: Đang bị tắt (`"tdq-workflow": {"enabled": false}`) trong `C:\Users\admin\.gemini\config\config.json` (mtime `2026-11-13T13:06:39`, tức `06:06:39Z`).
   - Cấu hình toàn cục của user `C:\Users\admin\.gemini\config\hooks.json` (lines 1–23): **Đang hoạt động**, khai báo hook `"auto-compact"` cho `PreInvocation` và `PreToolUse` (`"matcher": "run_command"`) chạy `powershell -NoProfile -NonInteractive -File C:\Users\admin\.gemini\config\hooks\auto-compact.ps1`.
2. **Dòng thời gian chính xác ở phiên cha**:
   - **Step 1 (`13:04:34+07:00`)**: Gọi 2 lệnh `read_file` → **Thành công (`DONE`)**.
   - **Step 4 (`13:04:40+07:00`)**: Gọi đồng thời 1 lệnh `read_file` và 1 lệnh `run_command` (bên trong `CommandLine` có gọi tới `LanguageServerService` kèm header `csrf`).
   - **Step 5 (`13:04:54+07:00`)**: Lệnh `read_file` của Step 4 → **Thành công (`DONE`)**.
   - **Step 6 (`13:04:54+07:00`)**: Lệnh `run_command` gọi `LanguageServerService` của Step 4 → **Bị từ chối (`ERROR`)**:
     `Encountered error in step execution: tool call denied by pre-tool hook: ` *(lý do sau dấu `: ` hoàn toàn rỗng `""`)*.
   - **Step 22 & 24 (`13:11:38+07:00` & `13:11:55+07:00`)**: Các lệnh `run_command` PowerShell bình thường (`Get-ChildItem`) → **Thành công (`DONE`)**.

### 4.2. Thực nghiệm loại trừ từng nghi phạm

Trong `run_sim.py` (`exact_step4_in_memory_hook_test`, lines 182–199 của `sim_results.json`), chúng tôi đã nạp **chính xác object `toolCall` của Step 4 trong bộ nhớ** (không thực thi lệnh mạng, không in token) vào cả 3 hook để kiểm chứng:

1. **Loại trừ `tdq-workflow` (`agy_pretooluse_gate.py` và `bash_gate.py`)**:
   - Cả hai script đều trả `exit_code = 0`, `stdout = ""` (không có bất kỳ regex nào kiểm tra `LanguageServerService`, HTTP hay port nội bộ).
   - Hơn nữa, kể cả giả thuyết `tdq-workflow` từng bật lúc `13:04:54` (trước khi `config.json` được lưu lúc `13:06:39`), `hooks.json` của `tdq-workflow` không có `"matcher"` cho `PreToolUse` — nếu stdout rỗng `""` của `tdq-workflow` là nguyên nhân gây chặn thì lệnh `read_file` ở **Step 1 (`13:04:34`)** và **Step 5 (`13:04:54`, cùng batch với Step 6)** cũng bắt buộc phải bị chặn! Thực tế cả hai lệnh `read_file` đều `DONE`.
2. **Loại trừ `auto-compact.ps1` (`C:\Users\admin\.gemini\config\hooks\auto-compact.ps1`)**:
   - Chạy thật `cmd /c powershell -NoProfile -NonInteractive -File ...\auto-compact.ps1` với đúng payload Step 4 (cả khi trỏ tới `transcript.jsonl` thật lẫn file giả lập chưa tồn tại) đều trả về **`exit_code = 0`, `stdout = '{"decision":"allow"}'`** hợp lệ 100%.
   - *(Lưu ý phụ đáng giá khi audit `auto-compact.ps1` lines 12–15: khối `catch { @{} | ConvertTo-Json -Compress; exit 0 }` có lỗi tiềm ẩn — nếu stdin không parse được JSON trong `PreToolUse`, nó in `{}` thiếu `"decision": "allow"`, nhưng với payload Step 4 thực tế thì `ConvertFrom-Json` thành công hoàn toàn).*
3. **Kết luận xác thực**:
   - Thông báo `tool call denied by pre-tool hook: ` (với chuỗi `reason` rỗng) tại Step 6 **đến từ chốt chặn bảo mật nội bộ (built-in internal pre-tool security hook) bên trong binary executor của Antigravity**, được thiết kế để chặn các lệnh `run_command` cố tình dò quét/gọi trực tiếp dịch vụ nội bộ `LanguageServerService` / trích xuất CSRF token của host — hoàn toàn độc lập với `tdq-workflow` và `auto-compact.ps1`.

---

## Phần 5: Ma Trận Khuyến Nghị Chuyển Đổi (Porting Blueprint) Cho Antigravity Trên Windows

Để hệ thống Lifecycle Hooks & Gates của TDQ-Workflow thực sự vận hành chuẩn xác 100% trên Antigravity (Windows & macOS/Linux):

1. **Sửa cấu trúc `hooks.json` ở gốc plugin (`<plugin_dir>/hooks.json`)**:
   - Bỏ khóa `"description"` ở top-level; đổi khóa bọc `"hooks"` thành tên hook định danh `"tdq-workflow"`.
   - Với `SessionStart`, `PreInvocation`, `PostInvocation`, `Stop`: dùng mảng **Flat** `[{"type": "command", "command": "..."}]` (bỏ lớp bọc `{"hooks": [...]}`).
   - Với `PreToolUse`, `PostToolUse`: khai báo rõ `"matcher"` theo tên tool của Antigravity:
     - Gate sửa file: `"matcher": "edit_file|write_file"`
     - Gate đọc file: `"matcher": "read_file"`
     - Gate lệnh shell: `"matcher": "run_command"`
     - Gate tìm kiếm: `"matcher": "run_command|grep_search|find_by_name"`
     - Gate LSP MCP: `"matcher": "mcp_.*lsp_.*"`
     - Gate hỏi user: `"matcher": "ask_question"`
   - Dùng lệnh tương đối từ `cwd = <plugin_dir>` thay vì nướng cứng `$HOME` của máy build: `py -3 "hooks/scripts/<ten_gate>.py"` trên Windows (hoặc adapter đa nền tảng).
2. **Viết bộ chuẩn hóa Payload hai chiều trong `_common.py` (Dual-Protocol Adapter: Claude Code ↔ Antigravity)**:
   - **Chiều đọc Stdin (`read_payload` / `payload_cwd` / `session_id`)**:
     - Tự động nhận diện payload Antigravity khi có `"toolCall"`, `"workspacePaths"`, hoặc `"conversationId"`.
     - Ánh xạ `cwd`: lấy `payload["workspacePaths"][0]` (nếu là mảng không rỗng) trước khi fallback về `os.getcwd()`, triệt tiêu hoàn toàn lỗi tìm nhầm `state.json` và lỗi ghi bẩn `.tdq-read.jsonl` vào thư mục cài đặt plugin!
     - Ánh xạ `session_id` ← `payload.get("conversationId")`; `prompt` ← `payload.get("lastUserInput")`.
     - Ánh xạ `toolCall`:
       - `run_command`: `args.CommandLine` → `tool_input.command`, `tool_name = "Bash"`
       - `read_file`: `args.Path`, `args.StartLine`, `args.EndLine` → `tool_input.file_path`, `offset`, `limit`, `tool_name = "Read"`
       - `edit_file` / `write_file`: `args.Path` → `tool_input.file_path`, `tool_name = "Edit"` / `"Write"`
       - `grep_search`: `args.Query`, `args.SearchPath` → `tool_input.pattern`, `path`, `tool_name = "Grep"`
       - `ask_question`: `tool_name = "AskUserQuestion"`
       - `mcp_<server>_<tool>`: chuẩn hóa cho `lsp_gate.py` và `search_observe.py`.
   - **Chiều xuất Stdout**:
     - **`SessionStart` & `PreInvocation`**: Bọc chuỗi nhắc vào `{"injectSteps": [{"systemMessage": {"systemMessage": text}}]}`; nếu rỗng in `{}`. Lưu ý ở `PreInvocation`: kiểm tra `invocationNum == 1` (hoặc lưu `lastUserInput` hash) để **không xóa sổ cái `.tdq-turn.jsonl` ở các lần gọi model giữa lượt**!
     - **`PreToolUse`**:
       - Khi cho phép (mặc định khi thoát `0`): **luôn in `{"decision": "allow"}`** thay vì chuỗi rỗng `""`.
       - Khi chặn (`block()`): in đúng `{"decision": "deny", "reason": ...}` (bỏ `allow_tool`, `message`, và `hookSpecificOutput`).
       - Với các mã chỉ nhắc (`remind()` như `TDQ:DOC`, `TDQ:LOG`, `TDQ:GIT`, `TDQ:ASK`): Do `PreToolUse` của Antigravity không có `additionalContext`, ghi nhận `remind` vào `.tdq-turn.jsonl` (hoặc queue file theo phiên), trả `{"decision": "allow"}` ở `PreToolUse`, và **bơm nhắc nhở qua `PostInvocation` (`injectSteps`) ngay sau khi tool hoàn tất**!
     - **`PostToolUse`**: Luôn in `{}` ở cuối `search_observe.py` (và đọc trường `"error"` để thay thế cho sự kiện `PostToolUseFailure`).
     - **`Stop`**: Xuất `{"decision": "continue", "reason": ...}` khi cần chặn dừng (`TDQ:LOG`, `TDQ:TICK`, `TDQ:UNFINISHED`) và `{"decision": "stop"}` khi cho phép dừng; đồng thời sửa ngay bug `_shell_changed_path(now)` thay vì `_shell_changed_path(snap)` tại `agy_stop_gate.py:185` (hoặc dùng chung luôn `stop_gate.py` sau khi đã có `PreInvocation` ghi `turn_start` snapshot!).
