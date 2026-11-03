# Research: Codex CLI — các lớp nạp cấu hình gốc (MCP, hooks, skills, AGENTS.md, trust)

Ngày: 2026-08-17

## Truy vấn đã chạy
1. tavily: `openai codex config.toml mcp_servers stdio bearer_token_env_var http_headers`
2. tavily: `openai codex CLI hooks feature codex_hooks PreToolUse PostToolUse`
3. tavily: `openai codex CLI skills .agents/skills SKILL.md discovery`
4. tavily: `openai codex AGENTS.md project_doc_max_bytes project_doc_fallback_filenames config.toml`
5. tavily: `openai codex trust_level trusted untrusted projects config.toml`
6. tavily: `openai/codex latest release version 2026`
7. tavily: `"learn.chatgpt.com" codex config.toml project_doc_max_bytes trust_level`
8. WebFetch raw.githubusercontent.com/openai/codex/main/docs/config.md, docs/skills.md, docs/hooks.md (docs/hooks.md không tồn tại — 404)
9. WebFetch developers.openai.com/codex/{skills,mcp,config,hooks} → tất cả 308-redirect sang learn.chatgpt.com/docs/...
10. WebFetch learn.chatgpt.com/docs/{build-skills, extend/mcp?surface=cli, config, config-file/config-reference}
11. WebFetch github.com/openai/codex/releases

## Nguồn
| URL | Loại nguồn |
|---|---|
| https://learn.chatgpt.com/docs/config-file/config-reference | Chính thức (OpenAI Codex Learn docs — sau redirect từ developers.openai.com/codex/config) |
| https://learn.chatgpt.com/docs/config-file/config-advanced | Chính thức |
| https://learn.chatgpt.com/docs/config-file/config-sample | Chính thức |
| https://learn.chatgpt.com/docs/extend/mcp?surface=cli | Chính thức (redirect từ developers.openai.com/codex/mcp) |
| https://learn.chatgpt.com/docs/build-skills | Chính thức (redirect từ developers.openai.com/codex/skills) |
| https://learn.chatgpt.com/docs/hooks | Chính thức (không đi qua redirect có ghi log rõ, nhưng cùng domain học chính thức; xem cảnh báo bên dưới) |
| https://learn.chatgpt.com/docs/agent-configuration/agents-md | Chính thức |
| https://github.com/openai/codex (raw docs/config.md, docs/skills.md) | Chính thức nhưng nội dung trong 2 file này chỉ trỏ link ra ngoài, không có chi tiết |
| https://github.com/openai/codex/releases | Chính thức (release tags) |
| https://github.com/openai/codex/issues/7138, /issues/3120, /issues/14599, /issues/9932, /issues/14882 | Chính thức (issue tracker của repo, nhưng là thảo luận/bug report — không phải spec đã merge, dùng làm chứng cứ phụ) |
| policylayer.com, ofox.ai, agenticcontrolplane.com, hookstack.app, byteiota.com, axiomstudio.ai, blog.fsck.com, thepromptindex.com, releasebot.io, codesignal.com | Bên thứ ba — dùng để tham chiếu chéo, KHÔNG dùng làm căn cứ chính khi mâu thuẫn với nguồn chính thức |
| https://github.com/openai/codex/blob/main/codex-rs/hooks/src/schema.rs | Chính thức — SOURCE CODE gốc, đọc trực tiếp raw content (1197 dòng), dùng làm căn cứ chính cho toàn bộ schema/event name/decision enum |
| https://github.com/openai/codex/blob/main/codex-rs/hooks/src/engine/discovery.rs | Chính thức — SOURCE CODE gốc (1588 dòng), căn cứ cho vị trí file cấu hình + xác nhận KHÔNG có feature flag |
| https://github.com/openai/codex/blob/main/codex-rs/hooks/src/config_rules.rs | Chính thức — SOURCE CODE gốc, căn cứ cho cơ chế bật/tắt hook theo từng key (`[hooks.state]`) |
| https://github.com/openai/codex/blob/main/codex-rs/hooks/src/declarations.rs | Chính thức — SOURCE CODE gốc, căn cứ cho `HookHandlerConfig` variants và cấu trúc `MatcherGroup` |
| https://github.com/openai/codex/blob/main/codex-rs/core/src/hook_runtime.rs | Chính thức — SOURCE CODE gốc (1069 dòng), căn cứ cho luồng gọi hook theo từng tool/event, xác nhận áp dụng cho mọi tool (không chỉ shell) |
| https://api.github.com/repos/openai/codex/commits?path=codex-rs/hooks | Chính thức — GitHub Commits API, căn cứ cho lịch sử phát triển hooks (từ 2026-02-10 đến 2026-08-17) |
| https://api.github.com/repos/openai/codex/releases?per_page=100 | Chính thức — GitHub Releases API, căn cứ xác định bản stable mới nhất `rust-v0.147.0` (2026-08-07) so với alpha `0.148.0-alpha.20` |

CẢNH BÁO ĐỘ TIN CẬY: `developers.openai.com/codex/*` tất cả redirect 308 sang `learn.chatgpt.com/docs/*`. Đây có vẻ là domain docs chính thức mới của OpenAI cho Codex (ChatGPT Learn), nhưng KHÔNG xác minh được bằng cách độc lập rằng learn.chatgpt.com thuộc sở hữu OpenAI chính thức (không có WHOIS/khẳng định trong nội dung fetch). Vì developers.openai.com (domain openai.com xác nhận chính chủ) chủ động redirect 308 (permanent) sang đó, đánh giá đây LÀ tài liệu chính thức, mức tin cậy CAO cho việc "đây là docs chính thức", nhưng nội dung cụ thể vẫn có thể trôi theo version — không có timestamp version rõ trong trang.

## Điều rút ra

### 1. MCP
- Tên bảng: `[mcp_servers.<name>]` — CAO. Nguồn: learn.chatgpt.com/docs/extend/mcp?surface=cli.
- Stdio: `command` (bắt buộc), `args`, `env`, `env_vars` (forward biến môi trường cha), `cwd`, `experimental_environment` — CAO.
- HTTP: `url` (bắt buộc), `bearer_token_env_var`, `http_headers` (static), `env_http_headers` (đọc từ env var), `auth` (default `oauth`) — CAO.
- **Project-level `.codex/config.toml` CÓ được nạp**, nhưng CHỈ khi project được đánh dấu `trusted`. Trích nguyên văn: "you can also scope MCP servers to a project with `.codex/config.toml` (trusted projects only)." và ở trang config-reference: "Codex loads project-scoped config files only when you trust the project." — CAO. Nguồn: learn.chatgpt.com/docs/extend/mcp, learn.chatgpt.com/docs/config-file/config-reference.
- Project-scoped config.toml KHÔNG được override một số khoá machine-local: `openai_base_url`, `chatgpt_base_url`, `apps_mcp_product_sku`, `model_provider`, `model_providers`, `notify`, `profile`, `profiles`, `experimental_realtime_ws_base_url`, `otel` — CAO.
- **Hệ quả cho bản portable**: MCP config theo folder KHẢ THI qua `.codex/config.toml`, nhưng project phải được user đánh dấu `trusted` trong `~/.codex/config.toml` (`[projects."<path>"] trust_level = "trusted"`) — nếu không Codex bỏ qua toàn bộ lớp `.codex/` của project, bao gồm MCP servers khai báo ở đó.

### 2. HOOKS — CHOT DUT DIEM (doc truc tiep source code openai/codex nhanh main, 2026-08-17)

**1. Co tinh nang hook khong, tu version nao, da merge vao main chua?**
CO — CAO. Khong phai PR/de xuat, ma la code da merge vao `main`, co crate rieng `codex-rs/hooks` (extracted tu core ngay 2026-02-10, commit `d735df1f` "Extract hooks into dedicated crate (#11311)" — nghia la hooks ton tai trong core TRUOC moc do nua, chi la moc tach crate). Dang phat trien tich cuc, commit gan nhat lien quan hooks la hom nay 2026-08-17 (`89e29772`, "Prevent Noise auth tokens from reaching child processes") va 2026-08-15 (`85fc4def`, "Add MCP tool handler support to the hooks engine"). Ban release stable moi nhat la `rust-v0.147.0` (2026-08-07); ban `0.148.0-alpha.*` dang alpha. Vi code hooks da co on dinh tu nhieu thang truoc 0.147.0, **hooks CO trong ban stable hien hanh >= 0.147.0**. Nguon: `codex-rs/hooks/src/*`, `codex-rs/core/src/hook_runtime.rs`, https://api.github.com/repos/openai/codex/commits?path=codex-rs/hooks, https://github.com/openai/codex/releases.

**2. Feature flag** — KHONG XAC MINH DUOC co flag `[features] hooks` hay `codex_hooks` nao gac tinh nang nay. Doc truc tiep `codex-rs/hooks/src/engine/discovery.rs` (1588 dong, toan bo logic discover handlers) — khong co bat ky check `[features].hooks` hay ten tuong tu nao; cung khong thay trong `codex-rs/core/src/config/managed_features.rs`. Viec bat/tat hook nam o muc **tung hook rieng le** qua `[hooks.state].<key>.enabled` trong config.toml (xem `codex-rs/hooks/src/config_rules.rs`), khong phai mot flag toan cuc bat/tat ca he thong hooks. → SUA LAI muc cu: KHONG co `[features] hooks = true/false`, KHONG co `codex_hooks` — day la claim SAI tu nguon tom tat truoc do, da bac bo bang source code truc tiep.

**3. File cau hinh dat o dau** — CAO, doc truc tiep `codex-rs/hooks/src/engine/discovery.rs` ham `load_hooks_json`: moi config layer (user, project, managed...) co mot `hooks_config_folder()`, va file duoc nap la `<config_folder>/hooks.json`. Cu the 2 lop ap dung cho ban portable:
  - User: `~/.codex/hooks.json`
  - Project (chi khi project `trusted`, theo cung co che trust da xac nhan o muc TRUST): `<repo>/.codex/hooks.json`
  Dong thoi hooks con khai duoc truc tiep trong `config.toml` o muc `[hooks]` (bang TOML dang `HookEventsToml`, vi du `[[hooks.pre_tool_use]]` — xem `codex-rs/hooks/src/declarations.rs` test fixture dung `codex_config::HookEventsToml`). Ca hai nguon (`hooks.json` va `config.toml [hooks]`) duoc nap cho cung mot layer va co canh bao neu trung — ham `discover_handlers` gop ca `json_hooks` va `toml_hooks`.

**4. Schema chinh xac** — CAO, doc truc tiep `codex-rs/hooks/src/schema.rs` (1197 dong).
  - Event name (enum `HookEventNameWire`, dung 10 gia tri, PascalCase, dung nguyen van trong JSON): `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PreCompact`, `PostCompact`, `SessionStart`, `UserPromptSubmit`, `SubagentStart`, `SubagentStop`, `Stop`. (Runtime co ham `run_session_end_hooks` cho SessionEnd nhung ten nay KHONG xuat hien trong enum `HookEventNameWire` — can luu y khi build, co the la ten wire khac hoac dang phat trien.)
  - Loai handler: `HookHandlerConfig` co it nhat cac bien the `Prompt {}`, `Command { command, command_windows, timeout_sec, r#async, status_message, additional_context_limit }`, `Agent {}` (thay trong `declarations.rs` test fixture).
  - Cau truc: moi event trong `hooks.json`/`config.toml` la mang `MatcherGroup { matcher: Option<String>, hooks: Vec<HookHandlerConfig> }` — cho phep nhieu handler khop theo `matcher` (vi du khop `tool_name`).

**5. Input qua stdin hay env? Truong nao?** — CAO. Input la JSON qua stdin (struct `PreToolUseCommandInput` derive `Serialize`, dung lam input cho hook process command). Cac truong trong `PreToolUseCommandInput`:
  `session_id`, `turn_id` (Codex-specific), `agent_id` (optional), `agent_type` (optional), `transcript_path`, **`cwd`** (CO truong cwd — xac nhan thu muc project/hien hanh), `hook_event_name`, `model`, `permission_mode`, `tool_name`, `tool_input` (JSON Value tu do), `tool_use_id`. Cac event khac (`SessionStart`, `Stop`, `PreCompact`...) dung struct tuong tu rut gon, deu co `cwd`, `transcript_path`, `permission_mode`.

**6. Tra gi de chan? allow/ask co ton tai khong? Gioi han tool nao?** — CAO, doc truc tiep struct output trong `schema.rs`.
  - **CO du `allow`/`deny`/`ask`** cho `PreToolUse`: enum `PreToolUsePermissionDecisionWire` = `Allow | Deny | Ask` (field `hookSpecificOutput.permissionDecision`, camelCase tren wire). Ngoai ra con field top-level `decision: PreToolUseDecisionWire` = `Approve | Block` (mot co che chan thu hai/song song, don gian hon).
  - `PermissionRequest` hook: enum `PermissionRequestBehaviorWire` = `Allow | Deny` (KHONG co `ask` cho event nay — dung theo ten "da dang xin permission roi" nen khong co "hoi lai").
  - `PostToolUse` hook: dung `BlockDecisionWire` (chan sau khi tool da chay — dung de feedback/additional_context, khong phai "ngan hanh dong" theo nghia pre-check).
  - **Khong gioi han chi shell/bash**: `PreToolUseCommandInput.tool_name: String` va `tool_input: Value` la generic — ap dung cho **moi tool** (ke ca MCP tools — xac nhan them boi commit `85fc4def` "Add MCP tool handler support to the hooks engine", 2026-08-15) va ca file-edit tools (`apply_patch` v.v., vi deu di qua `run_pre_tool_use_hooks` voi `tool_name` bat ky trong `codex-rs/core/src/hook_runtime.rs`). Claim cu "chi ap cho shell" da bi BAC BO bang source code.

Tom lai: muc hooks trong ban nghien cuu truoc day SAI o phan feature-flag (`[features] hooks`/`codex_hooks` khong ton tai trong source) va bi nghi ngo dung o phan allow/ask/deny + pham vi ap dung moi tool (nay xac nhan CAO bang source code truc tiep).


### 3. SKILLS
- Đường dẫn khám phá theo thứ tự: repo `.agents/skills` (quét từ cwd lên tới repo root), user `$HOME/.agents/skills`, admin `/etc/codex/skills`, system (skill built-in của OpenAI) — CAO. Nguồn: learn.chatgpt.com/docs/build-skills, trích: "Codex reads skills from repository, user, admin, and system locations."
- Frontmatter SKILL.md bắt buộc: `name`, `description` — CAO.
- Nạp vào context: progressive disclosure — ban đầu chỉ nạp tên + mô tả (danh sách này giới hạn ~2% context / fallback 8000 ký tự), full SKILL.md chỉ đọc khi skill được chọn dùng — CAO, giống cơ chế Claude Code.
- Lưu ý khác từ bên thứ ba (blog.fsck.com, TRUNG BÌNH): có bản build cũ dùng đường dẫn `~/.codex/skills/` (không phải `~/.agents/skills/`) và cờ `codex --enable skills`; cũng có báo lỗi GitHub cộng đồng (community.openai.com) rằng `~/.agents/skills` "không còn được discover" trong một số bản VS Code extension gần đây — cho thấy đường dẫn/hành vi CÓ THỂ đã đổi qua các version, không ổn định 100%. Khuyến nghị bản portable nên sinh skill ở CẢ `.agents/skills/<name>/SKILL.md` (project-level, ưu tiên chính) và kiểm tra thực tế trên máy user bằng cách chạy thử.
- Version giới thiệu: KHÔNG XÁC MINH ĐƯỢC chính xác (docs không ghi ngày; blog bên thứ ba nói skills "gated behind feature flag `codex --enable skills`" ở một thời điểm, nhưng không rõ mốc version cụ thể).

### 4. AGENTS.md
- Vị trí: project root (tự động), và `~/.codex/AGENTS.md` cho global guidance — CAO. Nguồn: learn.chatgpt.com/docs/agent-configuration/agents-md.
- `project_doc_max_bytes`: mặc định **32 KiB (32768 bytes)** — CAO, xác nhận kép: learn.chatgpt.com ("Codex skips empty files and stops adding files once the combined size reaches the limit... 32 KiB by default") VÀ source code GitHub issue #7138 trích `PROJECT_DOC_MAX_BYTES: usize = 32 * 1024` trong `src/config/mod.rs`.
- `project_doc_fallback_filenames`: mặc định là mảng rỗng `[]` theo ví dụ codesignal.com (bên thứ ba, TRUNG BÌNH); learn.chatgpt.com xác nhận field tồn tại và có thể set (ví dụ `["TEAM_GUIDE.md", ".agents.md"]`) nhưng KHÔNG nêu rõ giá trị mặc định trong đoạn fetch được — MỨC TRUNG BÌNH cho giá trị mặc định `[]`, CAO cho việc field này tồn tại và dùng được.

### 5. TRUST
- `[projects."<path>"].trust_level = "trusted" | "untrusted"` — CAO.
- Ý nghĩa: "Untrusted projects skip project-scoped `.codex/` layers, including project-local config, hooks, and rules." — CAO, trích nguyên văn từ learn.chatgpt.com/docs/config-file/config-reference, xác nhận chéo bởi learn.chatgpt.com/docs/config-file/config-advanced: "For security, Codex loads project-scoped config files only when the project is trusted... User and system layers remain separate and still load."
- Cách bật trusted: user tự thêm block `[projects."/đường/dẫn"] trust_level = "trusted"` vào `~/.codex/config.toml` (thủ công) — CAO, thấy trong nhiều ví dụ (ofox.ai, github issue #9932 workaround). KHÔNG xác minh được có UI/lệnh `codex trust` tự động ghi hộ hay không — THẤP, không tìm thấy tài liệu chính thức mô tả lệnh CLI dành riêng cho việc này trong lần search này.

### 6. Version hiện tại
- Bản mới nhất theo GitHub Releases (fetch trực tiếp github.com/openai/codex/releases): **0.148.0-alpha.20** (pre-release, 16/08/2026) — CAO cho việc đây là tag mới nhất trên trang releases tại thời điểm fetch.
- Bản ổn định gần nhất được nêu trong tin tức bên thứ ba (releasebot.io, TRUNG BÌNH): **0.147.0** (6/8/2026), có "MCP 2026-07-28 support", "Amazon Bedrock caching", "portable Agent Plugins".
- Nên dùng mốc tương thích: **>= 0.147.0** cho toàn bộ field đã xác minh CAO, bao gồm cả hooks (mcp_servers, project_doc_max_bytes, trust_level, hooks.json/config.toml [hooks], PreToolUse allow/deny/ask) — mục hooks đã chốt dứt điểm bằng source code, không còn cần re-verify.

## Chỗ chưa xác minh được
- **Hooks đã CHỐT DỨT ĐIỂM bằng source code (xem mục 2)** — không còn nằm trong danh sách chưa xác minh, TRỪ một điểm nhỏ: tên wire chính xác cho event `SessionEnd` (runtime có hàm `run_session_end_hooks` nhưng không thấy giá trị `SessionEnd` trong enum `HookEventNameWire` — có thể dùng tên khác hoặc chưa hoàn thiện, cần kiểm tra lại `codex-rs/protocol` hoặc bản build cụ thể nếu portable cần dùng đúng event này).
- **Skills — mốc version giới thiệu chính xác**: không tìm thấy ngày/số version chính thức.
- **Skills — độ ổn định discovery ở `~/.agents/skills`**: có báo lỗi cộng đồng gần đây (community.openai.com) nói skill ở `~/.agents/skills` không được nạp trong một số bản IDE extension — rủi ro cho bản portable nếu chỉ đặt skill ở user-level; nên ưu tiên đặt ở `.agents/skills` cấp project.
- **Trust — có lệnh CLI (`codex trust <path>` hoặc tương đương) để bật trusted không, hay chỉ có thể sửa tay `config.toml`**: chưa tìm thấy tài liệu chính thức xác nhận.
- **`project_doc_fallback_filenames` giá trị mặc định chính xác**: suy luận là `[]` từ ví dụ bên thứ ba, chưa thấy dòng "default: []" trực tiếp trong đoạn trích chính thức.
