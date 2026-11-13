# Rescan 05 — Authoritative Cross-Check: Google Antigravity Host Conventions, Installed Plugins, Environment Binaries & Native Capabilities

- **Ngày thực hiện:** `2026-11-13`
- **Phạm vi kiểm chứng:** Toàn bộ tài liệu nội tại `builtin/skills/*`, toàn bộ 8 plugin đang cài tại `C:\Users\admin\.gemini\config\plugins\*`, trình kiểm tra chính thức `agy.exe plugin validate --strict --json`, môi trường Windows PowerShell / Python / Node / Git thực tế trên máy, và đối chiếu từng dòng với `docs/AUDIT-AND-PORTING-PLAN.md`.
- **Tuân thủ ràng buộc:** `100% READ-ONLY` trên `~/.gemini/config`, `~/.gemini/antigravity`, `ForAgentCode\TDQ-Workflow`, và workspace docs; `0` lời gọi HTTP tới `LanguageServerService`; `0` khóa bí mật/email/token in ra báo cáo; toàn bộ script thử nghiệm đặt trong `scratch\rescan_e\`.

---

## Tóm Tắt Điều Hành: 7 Phát Hiện Mới Quan Trọng Nhất (Zero Blind Spots)

Qua đối chiếu chéo với tài liệu gốc của Antigravity và chạy thực nghiệm trực tiếp bộ nạp plugin thật **`agy.exe plugin validate <path> --strict --json`**, kế hoạch `docs/AUDIT-AND-PORTING-PLAN.md` hiện có hướng đi nền tảng đúng nhưng đang tồn tại **4 điểm mù P0/P1 nguy hiểm** và **3 cơ hội nâng cấp kiến trúc lớn** cần bổ sung ngay trước khi viết code:

1. **`[BLIND SPOT P0 — NGHIÊM TRỌNG NHẤT]` Đụng độ vòng đời Subagent trên `PreInvocation`, `PreToolUse` & `Stop` (Deadlock 100% ở `tdq-build` mode `subagent`):**
   - Trên Claude Code, `Stop` chỉ chạy cho agent chính (subagent chạy sự kiện riêng `SubagentStop`) và mọi hook của subagent đều có trường `payload["agent_id"]`.
   - **Trên Antigravity:** Không có `SubagentStop` và **không có trường `agent_id` trong stdin của hook**! Mọi `invoke_subagent` mở một hội thoại riêng (`conversationId` mới) dùng chung `workspacePaths[0]` và **bắn đầy đủ `SessionStart` → `PreInvocation` → `PreToolUse` → `PostToolUse` → `PostInvocation` → `Stop`**.
   - **Hệ quả nếu giữ nguyên kế hoạch Nhóm 3 hiện tại:**
     1. Khi `tdq-implementer` hoặc `tdq-reviewer` khởi chạy, `PreInvocation` (`prompt_context.py`) gọi `turn_log_clear(cwd)` **xóa sạch sổ cái `.tdq-turn.jsonl` của agent chính**!
     2. `edit_gate.py:125` và `bash_gate.py:136` kiểm tra `payload.get("agent_id")` (luôn `None` trên Antigravity) → mất khóa chặn subagent sửa bậy trước phase `implement`.
     3. Khi `tdq-implementer` làm xong Task `T1.1` và dừng (`Stop`), `stop_gate.py` tưởng đó là agent chính nên **ép `"decision": "continue"` vô hạn** vì `[TDQ:LOG]`, `[TDQ:TICK]` và `[TDQ:UNFINISHED]` (do các task `T1.2`, `T2.1` trên plan gốc vẫn đang `[ ]`) → **Subagent bị nhốt không bao giờ trả kết quả về cho Leader được!**
   - **Cách giải quyết dứt điểm (đã kiểm chứng trên `transcript.jsonl` thật):** Đọc dòng 1 (`step_index: 0`) của `payload["transcriptPath"]`: hội thoại gốc luôn có `"type": "USER_INPUT"`, còn subagent luôn có `"type": "SYSTEM_MESSAGE"` (`[Message] ... sender=<parent_uuid>`). `_common.py` tự gắn `payload["agent_id"] = payload["conversationId"]` cho subagent, tách riêng sổ cái (hoặc không xóa sổ cái chính), và cho `stop_gate.py` trả `{"decision": "allow"}` ngay lập tức khi `is_subagent == True`.

2. **`[BLIND SPOT P0]` Các tên tool `grep_search`, `find_by_name`, `list_dir` KHÔNG TỒN TẠI trên Antigravity 2.0 / `agy` CLI (`Nhóm 2, 3, 4`):**
   - Kiểm tra trực tiếp danh sách `<declaration:default_api:*>` của phiên thực thi hiện tại, quét toàn bộ lịch sử `transcript.jsonl` trong `~/.gemini/antigravity/brain/`, và đối chiếu `builtin/skills/migrate-agent-settings/SKILL.md:157-160` chứng minh: runtime Antigravity 2.0 (`language_server.exe`) chỉ cung cấp các tool tệp/shell cốt lõi: `read_file`, `write_file`, `edit_file`, `run_command`, `manage_task`, `search_web`, `ask_question`, `invoke_subagent`, `manage_subagents`, `define_subagent`, `send_message`, `swarm`, `schedule`, `list_resources`, `read_resource`, `search_marketplace`, `list_plugin_accounts`.
   - **Hệ quả:** Nếu cấp cho `tdq-reviewer` và `tdq-security-reviewer` danh sách `tools: [read_file, grep_search, find_by_name, list_dir, send_message]` như `AUDIT-AND-PORTING-PLAN.md` dòng `259`, hai agent này **mù hoàn toàn khả năng duyệt thư mục, chạy `git diff` hay tìm kiếm mã nguồn**! Cần cấp `tools: [read_file, run_command, send_message]` và khóa quyền ghi qua `bash_gate.py` + `edit_gate.py` (dựa trên `agent_id` tổng hợp ở mục 1).

3. **`[TRAP P1]` Khai báo `"variables"` trong `mcp_config.json` sẽ TỰ ĐỘNG TẮT toàn bộ Plugin `tdq-workflow` (`Nhóm 5` dòng 268):**
   - Chạy `agy plugin validate --strict --json` chứng minh nguyên văn:
     `server "tavily-vars" declares variables, so the plugin is off until the user fills them in; if config.json turns it on first, the server starts with the placeholders as written`.
   - Nếu khai báo `"variables"` cho `tavily-primary` và `tavily-backup` (đặc biệt khi nhiều người dùng không có khóa phụ `TAVILY_API_KEY_BACKUP`), toàn bộ plugin `tdq-workflow` sẽ bị khởi tạo ở trạng thái **OFF**! Thay vào đó: để kế thừa biến môi trường OS thì **bỏ hẳn khóa đó khỏi `"env"`**, hoặc để `tdq_setup.py` / `--sinh-agy` đồng bộ khóa thật cục bộ trên máy người dùng vào `mcp_config.json` (chỉ sinh `tavily-backup` khi thực sự có khóa phụ).

4. **`[BLIND SPOT P1]` Các tool MCP Lazy (56/65 tool của `agent-lsp`) đi qua `call_mcp_tool`, lọt hoàn toàn qua `"matcher": "mcp_.*lsp_.*"` (`Nhóm 3` dòng 208, 221 & `Nhóm 5` dòng 266):**
   - Khi chỉ bật `"eager": true` cho 9 tool cốt lõi của `lsp`, 56 tool còn lại là **lazy tools** và được model gọi bằng công cụ `call_mcp_tool(ServerName="tdq-workflow_lsp", ToolName="...")`. Matcher `"mcp_.*lsp_.*"` sẽ bỏ sót 100% các lời gọi này. Cần sửa matcher thành **`"mcp_.*lsp_.*|call_mcp_tool"`** và chuẩn hóa trong `_common.py`.

5. **`[VERIFIED HARD ERRORS]` Bằng chứng thực nghiệm từ `agy plugin validate` cho `agents/*.md` (`Q3`):**
   - `model: haiku` trong `tdq-implementer.md` (`v0.97.0`) gây **LỖI ĐỎ làm bộ nạp bỏ qua toàn bộ agent**: `Invalid model tier haiku. The loader skips this agent`. Tập giá trị `model:` hợp lệ duy nhất trong `agents/*.md` là **`inherit | flash_lite | flash | pro`** (hoặc lược bỏ).
   - `tools: Bash, Read, Grep, Glob` (chuỗi phân tách dấu phẩy trong `tdq-qc-tester.md`, `tdq-reviewer.md`, `tdq-security-reviewer.md`) gây **LỖI ĐỎ YAML**: `cannot unmarshal !!str 'Read, G...' into []string. The loader skips this agent`.
   - `TypeName` khi gọi `invoke_subagent` cho agent đóng gói trong plugin là **tên trần `name`** (`"tdq-implementer"`), **KHÔNG** có tiền tố `"tdq-workflow:"` hay `"tdq-workflow_"`.

6. **`[UPGRADE KIẾN TRÚC LỚN]` `<plugin>/rules/*.md` hỗ trợ chính thức `trigger: glob` & `trigger: model_decision` + Tích hợp cổng kiểm tra `agy plugin validate --strict --json` (`Q4` & `Nhóm 1, 2`):**
   - Kiểm chứng bằng `agy plugin validate --strict --json` xác nhận `<plugin>/rules/` không chỉ nạp `AGENTS.md` (luôn bật), mà còn nạp **mọi tệp `rules/<name>.md` có frontmatter `trigger: always_on | glob | model_decision | manual`**!
   - Nhờ đó, `tdq-workflow` giữ `rules/AGENTS.md` siêu gọn (`~8–10 KB`, chỉ tốn `~11%` ngân sách `20.000 tokens` `defaultRulesBudget`) đồng thời có thể xuất thêm các tệp luật ngôn ngữ/chuyên đề dạng `trigger: glob` (`**/*.py`, `**/*.ts, **/*.tsx`...) và `trigger: model_decision` mà **không tốn một token always-on nào** khi không chạm tới!
   - Đồng thời, tích hợp lệnh `agy plugin validate <bundle> --strict --json` (kèm `assets/logo.svg`) vào `build_portable.py --sinh-agy` và `tdq_checkportable.py` sẽ khóa chặt 100% lỗi schema JSON/YAML và cảnh báo cắt cụt `24.000 bytes` (áp dụng cho cả `rules/*.md` lẫn `skills/*/SKILL.md`!).

7. **`[VERIFIED ENVIRONMENT & TRANSCRIPT NUANCES]` Môi trường Windows thực tế & Double-JSON trong `transcript.jsonl` (`Q5, Q6, Nhóm 6`):**
   - `git config` trên máy **chưa bật `core.longpaths`** ở cả `--system` lẫn `--global` (mặc định `false`), xác nhận việc truyền `git -c core.longpaths=true` trong `tdq_team.py` là bắt buộc.
   - Trên máy **KHÔNG có `rg` (ripgrep)** ở bất kỳ đâu, **KHÔNG có `grep`, `sh`, `pwsh`, `ruff` trên `PATH` mặc định của PowerShell 5.1**, nhưng **CÓ `python3`** chạy tốt (`Python 3.13.15`) nhờ shim `C:\Users\admin\.gemini\antigravity\bin\python3.cmd` (`@py -3 %*`) do chính Antigravity tiêm vào `PATH`!
   - Trong `transcript.jsonl` của Antigravity, các giá trị bên trong `tool_calls[].args` được **mã hóa JSON hai lớp thành chuỗi** (ví dụ `{"CommandLine": "\"pytest -q\""}`) — `tdq_transcript.py` cần `json.loads()` thêm 1 nhịp khi bóc tham số tool.

---

## Phần 1. Tổng Kiểm Tra Tài Liệu Built-In & Toàn Bộ 8 Plugin Đang Cài Đặt

### 1.1. Danh mục tài liệu Built-In của Antigravity đã đối chiếu (`100%` tệp gốc)
Đã đọc toàn văn các tài liệu chuẩn tại `C:\Users\admin\.gemini\antigravity\builtin\`:
- `skills/agy-customizations/SKILL.md` + trọn bộ 6 tệp trong `docs/`: `plugins.md`, `hooks.md`, `mcp_servers.md`, `json_configs.md`, `rules.md`, `skills.md`.
- `skills/plugin/SKILL.md` (quy chuẩn `plugin.json`, vòng đời `customization://<dir>`, quy tắc không sửa tay `config.json`, quy tắc đặt tên MCP server).
- `skills/migrate-agent-settings/SKILL.md` (quy tắc chuyển đổi chính thức từ Claude Code / Codex / Cursor / Gemini CLI sang plugin Antigravity cho `mcp_config.json`, `skills/`, `agents/*.md`, `rules/*.md`).
- `skills/migrate-workflows/SKILL.md` & `skills/run-workflow/SKILL.md` (hỗ trợ `/<skill-name>` slash command và công cụ `run_workflow`).
- `skills/native_swarm/SKILL.md` (cơ chế `swarm`, `post_message`, `read_board`, `swarm_wait`, `workspace: "inherit" | "share" | "branch"`).
- `skills/antigravity_guide/SKILL.md` + trọn bộ 4 tệp `references/{cli,ide,app,sdk}.md`.

### 1.2. Kết quả kiểm toán & chạy `agy plugin validate --strict --json` trên toàn bộ 8 Plugin đang cài

| # | Thư mục Plugin (`~/.gemini/config/plugins/<dir>`) | Phiên bản & Trạng thái (`agy plugin list`) | Cấu trúc thực tế (`plugin.json`, `mcp`, `hooks`, `agents`, `rules`, `skills`, `auth`) | Kết quả chạy `agy plugin validate --strict --json` | Bài học rút ra cho `tdq-workflow` |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | `chrome-devtools-plugin` | `1.10.1` · **enabled** | `plugin.json` + 6 `skills/*/SKILL.md` (`a11y-debugging`, `chrome-devtools`, `cookie-debugging`, `debug-optimize-lcp`, `memory-leak-debugging`, `troubleshooting`). **Không có `mcp_config.json`!** | `ExitCode=0` (`findings: []`) | Giải thích vì sao dù cài `chrome-devtools-plugin`, phiên chạy vẫn có **`0` MCP tool DevTools**: plugin này chỉ đóng gói hướng dẫn `skills/`, chưa hề cấu hình MCP server! `tdq-workflow` tự khai báo server `chrome-devtools` trong `mcp_config.json` sẽ **không đụng độ** MCP server nào có sẵn. |
| **2** | `gdocs` | `0.0.9` · **enabled** | `plugin.json` + `auth.json` (`oauth2` cho CLI `gdocs`) + 1 skill (`gdocs`, kèm `scripts/gdocs.cmd`). | `ExitCode=1` (`1 warning`: `skills/gdocs/SKILL.md: the body is 26148 bytes; only the first 24000 are loaded`) | **Phát hiện mới:** Không chỉ `rules/*.md`, thân **`SKILL.md` cũng bị cắt cụt ở ngưỡng `24.000 bytes`**! (12 `SKILL.md` của TDQ dài `2.864 – 15.976 B` nên an toàn tuyệt đối). |
| **3** | `gdrive` | `0.0.11` · **enabled** | `plugin.json` (khai báo `$schema` Agent Plugins `1.0.0` + `extensions.com.google.antigravity.contextProviders` dùng `${PLUGIN_ROOT}`) + `auth.json` + 1 skill (`gdrive`). | `ExitCode=0` (`1 note`: chế độ Agent Plugins 1.0.0 vs native plugin) | Biến `${PLUGIN_ROOT}` trong `plugin.json` chỉ thuộc nhánh `contextProviders` của đặc tả Agent Plugins 1.0.0, không áp dụng cho `hooks.json` hay `mcp_config.json.command`. |
| **4** | `gemini-api` | `2.6.0` · **enabled** | `plugin.json` + `mcp_config.json` (`gemini-api-docs` dùng Streamable HTTP `serverUrl` + `"tools": {"gemini_search_docs": {"eager": true}, "gemini_get_doc": {"eager": true}}`) + 4 skills. | `ExitCode=1` (`1 warning`: `gemini-omni-flash-api/SKILL.md` vượt `24000 B`) | **Mẫu chuẩn xác thực tế** cho cấu hình `"tools": { "<tool>": { "eager": true } }` trong `mcp_config.json` và quy tắc đặt tên native tool `mcp_<plugin>_<server>_<tool>` (`mcp_gemini-api_gemini-api-docs_gemini_search_docs`). |
| **5** | `google-antigravity-sdk` | `0.0.9` · **enabled** | `plugin.json` + 1 skill (`google-antigravity-sdk` kèm `examples/` và `references/`). | `ExitCode=0` (`findings: []`) | Xác nhận hợp đồng `StopDecision.CONTINUE` bắt buộc có `reason` khác rỗng (`examples/getting_started/hooks.md:111-113`). |
| **6** | `gsheets` | `0.0.8` · **enabled** | `plugin.json` + `auth.json` + 1 skill (`gsheets`). | `ExitCode=0` (`findings: []`) | Frontmatter `SKILL.md` chuẩn chỉ dùng `name` và `description`. |
| **7** | `gslides` | `0.0.8` · **enabled** | `plugin.json` + `auth.json` + 1 skill (`gslides`). | `ExitCode=1` (`1 warning`: `skills/gslides/SKILL.md` `29294 B > 24000 B`) | Khẳng định lại ngưỡng cứng `24.000 bytes` cho thân `SKILL.md`. |
| **8** | `tdq-workflow` | `0.74.0` · **disabled** | `plugin.json`, `mcp_config.json` (2 server Tavily), `hooks.json` (sai schema), `manifest.json`, `hooks/scripts/` (4 file), `scripts/` (47 file), `skills/` (10 skill), `0 agents`, `0 rules`. | `ExitCode=1` (`1 error`, `2 warnings`, `1 note`) — xem nguyên văn bên dưới! | Xác thực 100% chẩn đoán về lỗi vỡ `hooks.json` và lỗi clobber biến `${TAVILY_API_KEY}` trong `mcp_config.json`, cộng thêm `note` thiếu `"logo": "assets/logo.svg"`. |

**Nguyên văn kết quả `agy plugin validate` trên bản cài `tdq-workflow` hiện tại:**
```json
{
  "components": { "agents": 0, "hooks": 0, "mcpServers": 2, "rules": 0, "sidecars": 0, "skills": 10 },
  "findings": [
    {
      "severity": "error",
      "file": "hooks.json",
      "message": "failed to parse hooks.json: json: cannot unmarshal string into Go struct field .description of type jsonhook.JSONHookSpec. The loader skips this whole file"
    },
    {
      "severity": "warning",
      "file": "mcp_config.json",
      "message": "server \"tavily-backup\": ${TAVILY_API_KEY} isn't declared in \"variables\", so it's passed as is. The server inherits the agent's environment, so leave TAVILY_API_KEY out of \"env\""
    },
    {
      "severity": "warning",
      "file": "mcp_config.json",
      "message": "server \"tavily-primary\": ${TAVILY_API_KEY} isn't declared in \"variables\", so it's passed as is. The server inherits the agent's environment, so leave TAVILY_API_KEY out of \"env\""
    },
    {
      "severity": "note",
      "file": "plugin.json",
      "message": "no logo: the plugin shows a generic icon. Add \"logo\": \"assets/logo.svg\" (a .png, .svg, .jpg, .jpeg or .webp file inside the plugin)"
    }
  ]
}
```

---

## Phần 2. Giải Đáp 7 Câu Hỏi Trọng Tâm (`Q1` – `Q7`) Với Bằng Chứng Thực Nghiệm Cứng

### Q1. Nội suy biến đường dẫn & `cwd` trong `hooks.json` và `mcp_config.json`

| Ngữ cảnh | `cwd` (Thư mục làm việc của tiến trình con) | Biến `${PLUGIN_ROOT}` / `${PLUGIN_DATA}` | Biến `${CLAUDE_PLUGIN_ROOT}` & Biến OS (`${TAVILY_API_KEY}`) | Đường dẫn tương đối (`./hooks/...`, `hooks/...`) & `~` |
| :--- | :--- | :--- | :--- | :--- |
| **`hooks.json`**<br>(`docs/hooks.md:129-140` + `probe-hooks-vars`) | Luôn đặt tại **thư mục chứa `hooks.json`** (tức `<plugin_dir>` = `~/.gemini/config/plugins/tdq-workflow`). **KHÔNG** phải thư mục workspace của dự án! | **KHÔNG nội suy trong chuỗi `command`** (`agy plugin validate` cảnh báo: `${PLUGIN_ROOT} isn't set for hook commands. They run in the plugin folder, so use ./hooks/scripts/...`). Tuy nhiên **CÓ được truyền làm biến môi trường OS** (`os.environ["PLUGIN_ROOT"]`, `os.environ["PLUGIN_DATA"]`) cho tiến trình hook! | **KHÔNG nội suy** bởi Antigravity. Trên Windows hook chạy qua **`cmd /c`** (không phải `sh -c`), nên cú pháp POSIX `$VAR` / `${VAR}` cũng không được `cmd.exe` bung (chỉ `%VAR%` mới được `cmd.exe` bung). | **CHẠY TỐT & SẠCH CẢNH BÁO 100%:** Dùng đường dẫn tương đối tính từ gốc plugin như `"py -3 \"hooks/scripts/session_start.py\""` (hoặc `~` ở đầu lệnh được bung thành `$HOME`). |
| **`mcp_config.json`**<br>(`migrate-agent-settings/SKILL.md:99-128` + `probe-hooks-mcp`) | Nếu khai báo `cwd` tương đối (`"cwd": "./sub"`), nó phân giải tương đối theo **`<plugin_dir>`**. Nếu bỏ trống `cwd`, tiến trình kế thừa `cwd` của Language Server (các server như `agent-lsp` nhận đường dẫn dự án qua tham số tool `workspace_root`). | **CÓ nội suy trong `"args"`, `"env"` và `"cwd"`**, nhưng **KHÔNG nội suy trong `"command"`**! Bằng chứng nguyên văn từ `agy plugin validate`: `server "plugin-root-test": ${PLUGIN_ROOT} and ${PLUGIN_DATA} aren't expanded in "command", only in "args", "env" and "cwd"`. Đồng thời tiến trình MCP cũng nhận `PLUGIN_ROOT` & `PLUGIN_DATA` trong `os.environ`. | **KHÔNG nội suy biến môi trường OS**! `${X}` chỉ được bung nếu `X` nằm trong mảng `"variables"` của server đó; nếu không sẽ bị truyền nguyên chuỗi ký tự đen `"${X}"` đè hỏng biến thật kế thừa từ OS! | Trong `"command"` bắt buộc dùng tên lệnh trên `PATH` hoặc đường dẫn tuyệt đối (không dùng `${PLUGIN_ROOT}` trong `"command"`). |

> **Bẫy cực lớn của `"variables"` trong `mcp_config.json`:** `agy plugin validate` và `migrate-agent-settings/SKILL.md:194` xác nhận: hễ bất kỳ MCP server nào trong plugin khai báo mảng `"variables"`, **toàn bộ plugin sẽ khởi tạo ở trạng thái tắt (`disabled`)** cho tới khi người dùng mở UI điền đủ biến; còn nếu bật cưỡng bức qua `agy plugin enable` / `config.json` trước khi điền, server sẽ chạy với chuỗi placeholder thô `"${...}"`!

---

### Q2. Quy ước Đặt Tên Skill & Cơ Chế Slash Commands Trên Antigravity

1. **Tên Skill nạp vào `<skills>` là tên trần (`tdq-plan`), KHÔNG có dấu hai chấm (`tdq:plan`):**
   - Bằng chứng trực tiếp từ khối `<skills>` của phiên hiện tại: `chrome-devtools-plugin` xuất `a11y-debugging`, `gemini-api` xuất `gemini-api-cli` — không bao giờ ghép `<plugin>:<skill>`.
   - Bằng chứng từ `agy plugin validate` (`probe-skills`): `name` trong `SKILL.md` bắt buộc trùng khớp với tên thư mục chứa nó (`warning: skills/mismatch-dir/SKILL.md: name "tdq:plan" doesn't match its folder "mismatch-dir"`), mà hệ thống tệp Windows cấm ký tự `:` trong tên thư mục.
2. **Hai tầng Slash Commands trên Antigravity:**
   - **Tầng 1 — Slash Commands hệ thống cố định (`<slash_commands>` & `antigravity_guide/references/app.md:25-27`):** `/goal`, `/compact`, `/schedule`, `/browser`, `/plan`, `/grill-me`, `/teamwork`, `/learn`, `/boost`, `/plugin`, `/automation`. *(Cảnh báo: `/plan` là chế độ lập kế hoạch nội tại của Antigravity, KHÔNG phải `tdq-plan`!).*
   - **Tầng 2 — Slash Commands tự động cho mọi Skill đang bật (`migrate-workflows/SKILL.md:14`, `plugin/SKILL.md:250-252`, cờ `--disable-slash-commands` của `agy --help`):**
     Mọi skill `<name>` được nạp đều hỗ trợ **gõ trực tiếp `/<name>` trong ô chat UI hoặc `agy` CLI**, đồng thời hỗ trợ **kích hoạt ngữ nghĩa tự động (semantic discovery)** qua `description`!
     - Như vậy trên Antigravity, người dùng có thể gõ **`/tdq-intake`**, **`/tdq-spec`**, **`/tdq-plan`**, **`/tdq-build`**, **`/tdq-lean`**, **`/tdq-status`**, **`/tdq-check-status`**, **`/tdq-setup`**, **`/tdq-browser-research`**, **`/tdq-browser-test`**, **`/tdq-checkportable`** (gạch ngang `-`, **không** gõ `/tdq:plan`).
     - Rất may mắn: quét toàn bộ `skills/**/*.md` trong repo gốc `TDQ-Workflow v0.97.0` ghi nhận **`0` vị trí dùng `tdq:<lenh>`** và `98` vị trí đã dùng sẵn định dạng `tdq-<lenh>`! Tuy nhiên cần dọn các lệnh slash ngoại lai `/skills`, `/mcp`, `/code-review` trong `README_AGY` và tài liệu hướng dẫn (trên `agy` CLI lệnh thật là `agy plugin list`, `agy mcp list`, `/help`).

---

### Q3. Schema `agents/*.md`, Tập Giá Trị `model:`, Tên Tool & Định Danh `TypeName` Trong `invoke_subagent`

Kết quả chạy thử nghiệm vét cạn các biến thể YAML frontmatter với `agy plugin validate --strict --json` (`probe_agy_validator.py`, `probe_agy_validator_2.py`, `probe_models_and_tools.py`):

1. **Các khóa YAML Frontmatter chuẩn trong `plugins/<plugin>/agents/<agent>.md`:**
   - `name` (`string`): Định danh toàn cục của agent. Tránh trùng các agent dựng sẵn (`self`, `browser`, `research`, `image-generator`, `deepagent`, `review-agent` — `migrate-agent-settings/SKILL.md:149-151`). Cả 6 agent của TDQ đều đã có tiền tố `tdq-*` nên không xung đột.
   - `description` (`string`, **bắt buộc**): Bỏ trống bị bộ nạp báo **ERROR** và loại bỏ agent (`the frontmatter has no description. The loader skips this agent`).
   - `subagent: true` và `mainAgent: false` (`bool`): Giữ agent là subagent thuần túy, không tràn vào danh sách main agent (`migrate-agent-settings/SKILL.md:153`).
   - `tools` (`[]string` — **bắt buộc kiểu mảng YAML**):
     - **Nếu viết chuỗi phân tách dấu phẩy** như `tools: Bash, Read, Grep, Glob` (hiện trạng của `tdq-qc-tester.md`, `tdq-reviewer.md`, `tdq-security-reviewer.md` trong `v0.97.0`): **ERROR ĐỎ** `cannot unmarshal !!str 'Read, G...' into []string. The loader skips this agent`!
     - **Nếu bỏ trống `tools:`** (hiện trạng của `tdq-implementer.md`, `tdq-build-resolver.md`, `tdq-refactor-cleaner.md`): Antigravity chỉ cấp quyền mặc định **chỉ đọc (read-only)** (`migrate-agent-settings/SKILL.md:154-155`), làm tê liệt hoàn toàn khả năng sửa code và chạy test!
   - `model` (`string`, tùy chọn — mặc định `inherit`):
     - **4 giá trị hợp lệ duy nhất (đã kiểm chứng thực nghiệm `rc=0`):** **`inherit`**, **`flash_lite`**, **`flash`**, **`pro`**.
     - **Mọi giá trị khác đều gây ERROR ĐỎ làm bộ nạp bỏ qua agent:**
       - `model: haiku` (vừa thêm vào `agents/tdq-implementer.md:4` ở `v0.97.0`!) → **`ERROR: Invalid model tier haiku. The loader skips this agent`**!
       - `model: sonnet` → **`ERROR: Invalid model tier sonnet. The loader skips this agent`**.
       - `model: opus` → **`ERROR: Invalid model tier opus. The loader skips this agent`**.
       - `model: auto` / `model: gemini-3.8-flash` / `model: claude-sonnet-5-5-medium` → **ERROR ĐỎ** tương tự!
     - Các khóa lạ như `effort: medium` hay `color: cyan` không gây lỗi unmarshal Go YAML nhưng bị lờ đi; theo chuẩn `migrate-agent-settings/SKILL.md:162`, cần **lược bỏ `effort` và `color`**, đồng thời đặt `model: inherit` (hoặc lược bỏ `model`) cho cả 6 agent TDQ.
2. **Định danh `TypeName` khi gọi `invoke_subagent(TypeName=...)`:**
   - Là **tên trần khai báo ở khóa `name`** trong frontmatter: **`"tdq-implementer"`**, **`"tdq-qc-tester"`**, **`"tdq-reviewer"`**, **`"tdq-security-reviewer"`**, **`"tdq-build-resolver"`**, **`"tdq-refactor-cleaner"`** (`plugin/SKILL.md:78`, `migrate-agent-settings/SKILL.md:149-151`, `run-workflow/SKILL.md:73-74`). **Tuyệt đối không dùng** `"tdq-workflow:tdq-implementer"` hay `"tdq-workflow_tdq-implementer"`.
   - Khi gọi `invoke_subagent` ở runtime, tham số `Model` cũng chỉ nhận enum `inherit | flash_lite | flash | pro` — do đó bảng điều phối model trong `team-mode.md:143` và `subagent-tuning.md:35-40` phải được ánh xạ sang: việc cơ học → `flash_lite` / `flash`; viết code / review / QC → `inherit` (mặc định); bài toán khó nhất → `pro`.

---

### Q4. Cơ Chế Nạp `<plugin>/rules/*.md`, Frontmatter `trigger:` & Chiến Lược Tiết Kiệm Ngân Sách `20.000 Tokens`

**Kết quả kiểm chứng thực nghiệm (`probe-rules`, `probe-agents-md-fm`, `probe-rules-detail`, `probe_extra.py`) — Đính chính một ngộ nhận cũ rất quan trọng:**

1. **Trong thư mục `<plugin>/rules/`, Antigravity hỗ trợ ĐỒNG THỜI cả hai định dạng:**
   - **Định dạng A — `rules/AGENTS.md` hoặc `rules/GEMINI.md`:** Có thể viết **Plain Markdown không cần frontmatter** (mặc định `always_on` khi plugin bật) **HOẶC** có frontmatter `trigger: always_on` (cả hai đều đạt `rc=0, findings=[]`).
   - **Định dạng B — Bất kỳ tệp `rules/<name>.md` nào khác trong `<plugin>/rules/`:** **ĐƯỢC NẠP CHÍNH THỨC** nếu và chỉ nếu có YAML frontmatter khai báo `trigger:` thuộc 1 trong 4 giá trị:
     1. `trigger: always_on` — luôn nạp vào system prompt (tính vào ngân sách chung `20.000 tokens` `defaultRulesBudget`).
     2. `trigger: glob` kèm `globs: "<chuỗi phân tách dấu phẩy>"` (ví dụ `globs: "**/*.py"` hoặc `globs: "**/*.ts, **/*.tsx"`; **cấm dùng mảng YAML list** vì gây lỗi `cannot unmarshal !!seq into string`, và bắt buộc bung ngoặc nhọn `{ts,tsx}` — `migrate-agent-settings/SKILL.md:176-179`). Chỉ nạp khi làm việc với tệp khớp đường dẫn!
     3. `trigger: model_decision` kèm `description: "<mô tả khi nào áp dụng>"` — áp dụng **Progressive Disclosure** y hệt Skills (`agy-customizations/SKILL.md:88-89`), chỉ nạp phần thân khi model quyết định kích hoạt dựa trên `description`, **KHÔNG chiếm ngân sách `20.000 tokens` always-on**!
     4. `trigger: manual` — chỉ nạp khi người dùng đính kèm thủ công qua `@` mention trong chat (`antigravity_guide/references/app.md:28-30`).
     - *(Nếu tạo `rules/other.md` không có frontmatter `trigger:`, `agy plugin validate` báo lỗi đỏ: `no valid trigger in the frontmatter, so the rule never applies`.)*
2. **Kiểm chứng cú pháp `@[label](path)` và trần `24.000 bytes`:**
   - Thử nghiệm `probe_extra.py` chứng minh `agy plugin validate` bung trực tiếp liên kết `@[label](../path.md)` trong `rules/AGENTS.md` và cắt cụt ngay nếu tổng dung lượng sau khi bung vượt `24.000 bytes` (`warning: rules/AGENTS.md: the content is cut by 25004 bytes to fit the 24000-byte limit`).
3. **Chiến lược tối ưu cho TDQ-Workflow trên Antigravity (Kết hợp Hybrid):**
   - **Giữ nguyên 100% các tệp gốc trong `skills/tdq-build/references/rules/*.md`:** Để không chạm vào khóa kiểm `R9` / `R13` (`doc_lint.py` + `token-budget.json` đang khóa cứng SHA-256 của 62 tệp `references/`).
   - **Trong `build_portable.py --sinh-agy`, sinh thư mục `plugins/tdq-workflow/rules/` theo cấu trúc 2 tầng:**
     - **Tầng Always-On (`rules/AGENTS.md`, `~8.500 – 10.500 B`, `~2.300 tokens` = ~11.5% ngân sách 20k):** Chứa Hiến pháp `Soul`, luật bắt buộc mở `tdq-intake`, luật cấm `ask_question` (Zero-Popup), quy tắc nhánh Git & cấm sửa tay `state.json`, quy tắc PowerShell 5.1 trên Windows, và bảng ánh xạ tool chuẩn xác của Antigravity.
     - **Tầng Lazy / Contextual (`rules/lang-*.md` với `trigger: glob` & `rules/domain-*.md` với `trigger: model_decision`):** Tự động sinh từ `skills/tdq-build/references/rules/{python,typescript-js,go,rust,csharp,cpp,html}.md` (mỗi tệp chỉ `~3.1 – 3.4 KB`) với `trigger: glob` tương ứng đuôi file, cộng `rules/clean-code-chung.md` / `rules/vision-ui-testing.md` với `trigger: model_decision`! Cách này giúp Antigravity tự động nạp đúng luật ngôn ngữ ngay khi chạm file nguồn mà **chi phí token nền đầu phiên = 0**!

---

### Q5. Đối Chiếu `swarm` (`workspace="share"`) vs `invoke_subagent` + `tdq_team.py` Cho Các Đợt Sóng `tdq-build`

| Tiêu chí kỹ thuật | `swarm(action="add", workspace="share")` (`native_swarm/SKILL.md`) | `invoke_subagent(TypeName="tdq-implementer", Workspace="inherit")` + `tdq_team.py` |
| :--- | :--- | :--- |
| **Đường dẫn Worktree & Tên nhánh Git** | Tạo workspace nội bộ do Antigravity tự quản lý ngoài `.tdq-worktrees/`, nhánh không theo chuẩn `tdq/<slug>/<task>`, và bị **xóa vĩnh viễn** ngay khi gọi `swarm(action="kill")` (`native_swarm/SKILL.md:248`). | Khớp **100%** với `tdq_team.py open <task>`: tạo nhánh `tdq/<slug>/<task>` tại `.tdq-worktrees/<slug>/<task>` kèm NTFS junction `node_modules`/`.venv` (`tdq_team.py:826, 861, 1063`). |
| **Tương thích `tdq_team.py check / merge / resolve / sweep` & `worktrees.json`** | **GÃY 100%:** `tdq_team.py` kiểm tra sổ cái `docs/tdq/worktrees.json` và chạy lại lệnh `Test:` bên trong `.tdq-worktrees/<slug>/<task>`. Dùng `swarm` sẽ làm `check`/`merge` không tìm thấy nhánh/thư mục, còn `_chan_worktree_con_mo` của `tdq_state.py` mất kiểm soát! | **TƯƠNG THÍCH 100%:** Không phải sửa một dòng logic nào của `tdq_team.py` hay `tdq_worktree_registry.py`. |
| **Tương thích khóa vùng chạm `[TDQ:TEAM]` (`edit_gate.py`)** | `ngoai_vung_khai()` (`tdq_team.py:1638-1678`) nhận diện subagent dựa trên đường dẫn tuyệt đối nằm dưới `.tdq-worktrees/<slug>/<task>/...`. Workspace riêng của `swarm` nằm ngoài đường dẫn này nên **vô hiệu hóa hoàn toàn hàng rào `Chạm:`**! | **HOẠT ĐỘNG 100%:** Vì dùng `Workspace="inherit"`, `tdq-implementer` sửa trực tiếp file trong `<project>/.tdq-worktrees/<slug>/<task>/...`, kích hoạt chính xác kiểm tra `ngoai_vung_khai()` và miễn trừ đếm streak của leader (`edit_gate.py:240`)! |
| **Chi phí Token, Độ trễ & Chọn Model** | Đánh dấu `(Preview & Quota Heavy)`; bộ công cụ bảng tin (`post_message`, `read_board`, `swarm_wait`) đến **trễ 1 lượt** sau `swarm add` (`native_swarm/SKILL.md:332`); cấm tự chọn model khác nếu user không yêu cầu (`SKILL.md:226`). | Nhẹ, gọi song song toàn bộ N task của cùng 1 wave ngay trong 1 lượt phản hồi, cho phép chọn `Model` (`inherit`, `flash`, `pro`), subagent báo cáo gọn `< 200 tokens` qua `send_message` rồi tự nghỉ (0 token khi idle). |

> **Kết luận dứt khoát cho Q5:** **BẮT BUỘC dùng `invoke_subagent(TypeName="tdq-implementer", Workspace="inherit", ...)` kết hợp `tdq_team.py`!** Tuyệt đối KHÔNG dùng `swarm` và cũng KHÔNG truyền `Workspace="share"` hay `Workspace="branch"` vào `invoke_subagent` khi chạy task của `tdq_team.py` (vì bản thân `.tdq-worktrees/<slug>/<task>` ĐÃ LÀ git worktree cô lập nằm bên trong thư mục dự án kế thừa!).

---

### Q6. Kiểm Toán Thực Nghiệm Môi Trường Máy Windows (`100%` Dữ Liệu Đo Thật)

| Hạng mục kiểm tra | Kết quả đo thực tế trên máy | Hệ quả kỹ thuật đối với TDQ-Workflow trên Antigravity |
| :--- | :--- | :--- |
| **PowerShell (`$PSVersionTable`)** | `PSVersion 5.1.26100.7705` (`Desktop` edition, `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`). **`pwsh` (PowerShell 7) KHÔNG cài đặt!** | 1) Toán tử `&&` và `\|\|` là **lỗi cú pháp** trên PS 5.1 (phải dùng `;` hoặc `if ($?)`).<br>2) `>` / `Out-File` mặc định ghi UTF-16LE hoặc UTF-8 có BOM.<br>3) Mọi lệnh `run_command` mở một phiên PS 5.1 mới tinh (`cd` không giữ qua lượt sau). |
| **Python (`python`, `py`, `python3`)** | - `python`: `...\Python\Python313\python.exe` (**`Python 3.13.15`**)<br>- `py -0p`: `-V:3.13 *` (`...\Launcher\py.exe`)<br>- **`python3 --version` → `ExitCode=0`, `Python 3.13.15`!** | **Phát hiện thú vị:** Antigravity tự đóng gói sẵn `C:\Users\admin\.gemini\antigravity\bin\python3.cmd` (nội dung `@py -3 %*`) và `AppData\Local\agy\bin\python3.cmd` đứng **trước** `WindowsApps\python3.exe` trên `PATH` (kể cả trong `cmd /c`)! Nhờ vậy `python3` chạy được thật trong phiên Antigravity, nhưng `hooks.json` trên Windows dùng `py -3` vẫn là chuẩn an toàn nhất trên mọi máy. |
| **Python Default Encoding** | `sys.stdout.encoding = utf-8`, `locale.getpreferredencoding() = utf-8`, **`sys.flags.utf8_mode = 1`** | Máy hiện tại bật sẵn UTF-8 mode nên in tiếng Việt không vỡ, song vẫn phải giữ `utf8_io` và `encoding="utf-8"` / `"utf-8-sig"` cho các máy Windows mặc định `cp1252`. |
| **Node / npm / npx (`fnm`)** | `node v24.21.0`. Thứ tự `PATH`:<br>1. `...\AppData\Local\fnm_multishells\<PID>_<TS>\` (thư mục tạm!)<br>2. `C:\Program Files\nodejs\`<br>3. `...\AppData\Roaming\fnm\aliases\default\` | **Cấm tuyệt đối** ghi đường dẫn `fnm_multishells\...` vào `mcp_config.json` (khi đóng shell thư mục này biến mất làm gãy `agent-lsp` / `npx`). Luôn chuẩn hóa về `AppData\Roaming\fnm\aliases\default\` hoặc `C:\Program Files\nodejs\`. |
| **Git (`2.56.0.windows.1`)** | - `--system`: `core.autocrlf=true`, `core.symlinks=true`, `init.defaultbranch=master`<br>- `--global`: `user.name=Truong Dinh Quoc`, `user.email=<REDACTED>`<br>- **`core.longpaths`: CHƯA ĐẶT (`false`) ở cả system lẫn global!** | Xác nhận 100% nguyên nhân gây lỗi đường dẫn dài > 260 ký tự khi tạo `.tdq-worktrees/<slug>/<task>/...`! `tdq_team.py` bắt buộc gọi `git -c core.longpaths=true ...`. |
| **Các binary CLI khác (`rg`, `grep`, `sh`, `ruff`, `pytest`, `graphify`, `agent-lsp`, `codex`)** | - **CÓ MẶT:** `pytest.exe`, `graphify.exe`, `agent-lsp.exe`, `codex.cmd`, `findstr.exe`.<br>- **VẮNG MẶT TRÊN `PATH`:** **`rg` (không tồn tại trên toàn ổ đĩa)**, **`grep`**, **`sh`**, **`ruff`** (`grep.exe` và `bash.exe` nằm khuất trong `C:\Program Files\Git\usr\bin`, không nằm trên `PATH` mặc định). | Các câu lệnh mẫu trong `skills/` dùng `grep -c ...` (`team-mode.md:69,70,173`) hoặc `rg` sẽ **báo lỗi `CommandNotFoundException` trong PowerShell**! Cần dặn rõ trong `rules/AGENTS.md` dùng `Select-String` / `python` trên Windows (lưu ý: `scripts/search_rules.py:38-40` ĐÃ nhận diện đầy đủ `select-string`, `sls`, `findstr`, `get-childitem`, `gci`!). |

---

### Q7. Bảng Đối Chiếu Toàn Diện & Danh Sách Cập Nhật Cho `docs/AUDIT-AND-PORTING-PLAN.md`

Dưới đây là toàn bộ các điểm cần **sửa đổi, bổ sung hoặc nâng cấp** vào `docs/AUDIT-AND-PORTING-PLAN.md` theo từng mục để kế hoạch đạt độ chính xác tuyệt đối 100%:

| Vị trí trong `AUDIT-AND-PORTING-PLAN.md` | Nội dung hiện tại trong Plan | Vấn đề / Điểm mù phát hiện qua kiểm chứng thực nghiệm | Nội dung chính xác cần cập nhật vào Plan |
| :--- | :--- | :--- | :--- |
| **Nhóm 1 `[P0]`**<br>(Dòng `159`) | Chỉ đề xuất kiểm tra `ast.parse` trong `tdq_checkportable.py` & `test_sinh_agy.py`. | Bỏ lỡ công cụ kiểm định chính chủ **`agy plugin validate <dir> --strict --json`** có sẵn trên máy và thiếu `assets/logo.svg` (gây `note` khi validate). | Bổ sung `assets/logo.svg` + metadata `displayName`, `author`, `suggestedPrompts` vào `plugin.json`, và chạy tự động `agy plugin validate <dich> --strict --json` (yêu cầu `rc == 0`, `0 errors`, `0 warnings`) ngay cuối `--sinh-agy` và trong test! |
| **Nhóm 2 `[P0]`**<br>(Dòng `162–173`) | Chỉ tạo duy nhất `rules/AGENTS.md`; dòng `170` ánh xạ `Grep`/`Glob` → `grep_search` / `find_by_name` / `list_dir`. | 1) `grep_search`, `find_by_name`, `list_dir` **không tồn tại** trong Antigravity 2.0 (`language_server.exe`), và `rg`/`grep` cũng không có trên `PATH` PowerShell.<br>2) `<plugin>/rules/*.md` hỗ trợ chính thức `trigger: glob` và `trigger: model_decision` không tốn ngân sách always-on `20.000 tokens`. | 1) Sửa bảng ánh xạ trong `rules/AGENTS.md`: tìm kiếm khái niệm qua `mcp_tdq-workflow_lsp_*` + `tdq_graphify.py`, tìm chuỗi/liệt kê file qua `run_command` (`Select-String` / `Get-ChildItem` / `python`, không gọi `grep`/`rg` trần trên Windows); nhắc rõ `/plan` là lệnh của AGY còn skill TDQ là `/tdq-intake`, `/tdq-plan`, `/tdq-build`.<br>2) Tùy chọn xuất thêm `rules/lang-*.md` (`trigger: glob`) từ `skills/tdq-build/references/rules/*.md` (vẫn giữ nguyên bản gốc trong `skills/` để pass `doc_lint.py` R9/R13). |
| **Nhóm 3 `[P0]`**<br>(Dòng `176–244`) | - Matcher LSP chỉ ghi `"mcp_.*lsp_.*"` (dòng `208, 221`).<br>- Chưa phân biệt hội thoại Subagent vs Main Agent.<br>- `Stop` (dòng `244`) in `{"decision": "stop"}` khi cho dừng và chỉ bỏ qua `("USER_CANCELED", "ERROR")`. | 1) **Đụng độ P0:** Subagent bắn `PreInvocation` (xóa `.tdq-turn.jsonl` của cha!), thiếu `agent_id` trong `PreToolUse`, và bị `Stop` nhốt vô hạn bởi `TDQ:LOG`/`TDQ:TICK`/`TDQ:UNFINISHED`!<br>2) 56 tool LSP lazy đi qua `call_mcp_tool`, lọt khỏi `"mcp_.*lsp_.*"`.<br>3) `Stop` có tới 9 mã `terminationReason` (`MAX_INVOCATIONS`, `MAX_TOKEN_BUDGET_EXCEEDED`...). | 1) Trong `_common.py`: đọc dòng đầu `transcriptPath` (`step_0.type == "SYSTEM_MESSAGE"` → `is_subagent = True`), gán `payload["agent_id"] = payload["conversationId"]`; khi `is_subagent == True`: `PreInvocation` không xóa `.tdq-turn.jsonl` của cha và không bơm `TDQ:INTAKE`, còn `Stop` trả ngay `{"decision": "allow"}`!<br>2) Mở rộng matcher LSP thành `"mcp_.*lsp_.*\|call_mcp_tool"` (chuẩn hóa `call_mcp_tool` khi `ServerName` thuộc `lsp`).<br>3) Ở `Stop` của agent chính: **chỉ xét chặn khi `terminationReason == "NO_TOOL_CALL"`** (mọi lý do kết thúc khác đều trả `{"decision": "allow"}`), và khi chặn `continue` bắt buộc kèm `reason` khác rỗng. |
| **Nhóm 4 `[P0]`**<br>(Dòng `246–263`) | - Chưa nêu lỗi `model: haiku` và lỗi `tools: Bash, Read...` kiểu chuỗi.<br>- Cấp cho `tdq-reviewer` & `tdq-security-reviewer` các tool không tồn tại `[read_file, grep_search, find_by_name, list_dir, send_message]`. | 1) `model: haiku` (`v0.97.0`) và `tools:` dạng chuỗi làm loader Antigravity **báo lỗi đỏ và bỏ qua toàn bộ agent**.<br>2) Thiếu `run_command` khiến `tdq-reviewer` và `tdq-security-reviewer` không thể duyệt cây thư mục hay chạy `git diff` / `doc_lint.py` trên Antigravity 2.0. | 1) Chuẩn hóa YAML frontmatter cả 6 agent: `subagent: true`, `mainAgent: false`, `model: inherit` (hoặc lược bỏ `model`, `effort`, `color`), `tools` bắt buộc là mảng YAML.<br>2) Cấp `[read_file, run_command, send_message]` cho `tdq-reviewer` & `tdq-security-reviewer` (đã có `bash_gate.py` + `edit_gate.py` chặn cứng mọi lệnh ghi file của subagent thông qua `agent_id`!).<br>3) Ánh xạ bảng chọn model trong `team-mode.md` / `subagent-tuning.md` từ `haiku/sonnet/opus` sang `flash_lite/flash/inherit/pro`, và xác nhận `invoke_subagent(TypeName="tdq-implementer", Workspace="inherit")` (không dùng `swarm`). |
| **Nhóm 5 `[P1]`**<br>(Dòng `264–268`) | Đề xuất khai báo mảng `"variables"` cho `tavily-primary` và `tavily-backup`. | Khai báo `"variables"` khiến **toàn bộ plugin `tdq-workflow` bị tắt mặc định** cho đến khi điền đủ tất cả biến trên UI (hoặc nhận chuỗi đen `"${...}"` nếu bật qua CLI). | **Không dùng `"variables"` mặc định** trong `mcp_config.json`: nếu dùng biến môi trường OS thì bỏ hẳn khóa khỏi `"env"` để kế thừa tự nhiên; khi chạy `tdq_setup.py` / `--sinh-agy` trên máy đích thì đồng bộ khóa cục bộ (nếu có) và chỉ sinh `tavily-backup` khi có khóa backup thật. Giữ tên server là `"lsp"`, `"chrome-devtools"`, `"tavily-primary"` (Antigravity tự động prefix thành `tdq-workflow_<server>`, không tự prefix kép). Lưu ý `${PLUGIN_ROOT}` dùng được trong `args`/`env`/`cwd` nhưng cấm dùng trong `command`. |
| **Nhóm 6 `[P2]`**<br>(Dòng `270–279`) | Ánh xạ `tool_calls` từ `transcript.jsonl` của Antigravity. | Chưa ghi nhận đặc điểm thực tế trong `transcript.jsonl`: mọi giá trị bên trong `tool_calls[].args` đều bị **serialize JSON thành chuỗi thêm 1 lần** (`"\"Get-ChildItem ...\""`). | Ghi rõ trong đặc tả parser `tdq_transcript.py`: khi đọc `tool_calls[].args` của Antigravity, nếu giá trị là `str` bắt đầu bằng `"` / `{` / `[` hoặc số chuỗi thì gọi `json.loads()` giải mã lớp trong trước khi trích xuất `CommandLine` / `Path` cho `step_audit.py`! |
