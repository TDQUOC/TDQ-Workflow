# Knowledge — 2026-08-05-clone-setting-codex

## Năng lực dùng được

| Năng lực | Có sẵn | Dùng? | Vì sao |
|---|---|---|---|
| `graphify` | Có | Có | Bắt buộc cuối turn có đổi code (§quy tắc chung). |
| `skill-creator` | Có | Có | Việc chính của request là tạo 1 skill Claude Code mới — đúng mục đích skill này. |
| `mem0-memory` | Có | Có | Cấu trúc thật của Codex CLI (AGENTS.md, chuẩn Agent Skills, `config.toml`, plugin manifest) là fact kỹ thuật cross-project, đáng nhớ dài hạn — khác `full-claude-export` (thuần nội bộ 1 repo). |
| `tavily-primary` (qua agent `search-scout`/`search-runner`) | Có | Đã dùng (research) | Nền tảng search đã chạy 2 phase, 4 agent, 12 finding có nguồn — xem mục Nguồn. |
| `tdq-workflow:*` (spec/plan/build/qc) | Có | NỀN | Khung bắt buộc của toàn bộ request, không phải công cụ dùng trong 1 task con. |
| `plugin-dev:skill-development` | Có | Không | Trùng chức năng với `skill-creator` đã chọn làm công cụ chính. |
| Skill built-in khác (dataviz, artifact-*, claude-md-improver...) | Có | Không | Không tạo artifact/chart; không sửa `CLAUDE.md` trong request này (chỉ ĐỌC để hiểu, không sửa). |

## Đã đọc / khảo sát thực địa

- `codex --help`, `codex doctor` trên máy user: Codex CLI đã cài (`0.147.0-alpha.1.2`,
  bundle theo ChatGPT.app), `CODEX_HOME=~/.codex`, thư mục hiện gần như trống (chỉ có
  `tmp/`) — chưa từng cấu hình `config.toml`/`AGENTS.md`/`.agents/skills`.
- `~/Documents/SimplifyWorkflow/PluginOutput` — precedent THAM KHẢO (không phải nguồn
  chính thức): một project khác đã tự chế layout `.codex/config.toml` +
  `.codex/hooks.json` + `.codex/rules/*.rules` + `AGENTS.md` root + `.agents/skills/`.
  Research vòng 2 xác nhận: `.agents/skills/` và `AGENTS.md` khớp tài liệu chính thức;
  `hooks.json` khớp một phần (đúng tên file, khác vị trí mặc định `.codex/` chỉ là quy
  ước riêng của project đó — Codex thật tìm ở `~/.codex/` hoặc `.codex/` dự án);
  `.codex/rules/*.rules` KHÔNG tìm thấy nguồn chính thức xác nhận (khả năng là quy ước
  riêng của công cụ `rulesync`, không phải Codex CLI gốc).
- `scripts/claude_export.py` (bản đã có sẵn trong repo) — dùng làm khuôn kiến trúc tham
  khảo cho `codex_clone.py` mới: pattern `CONFIG_FILES`/`CONFIG_DIRS`, secret-scan,
  `write_manifest`, subcommand `build`/`check`.

## Research (2 phase, 4 agent, 12 finding sau dedup — nguồn chính thức OpenAI trừ khi
ghi chú khác)

Chi tiết đầy đủ: `docs/tdq/research/2026-08-05-clone-setting-codex.md` +
`docs/tdq/research/search/2026-08-05-clone-setting-codex/{merged.json,report.md}`.

1. **AGENTS.md** ≈ `CLAUDE.md`. Global: `~/.codex/AGENTS.override.md` nếu có, không thì
   `~/.codex/AGENTS.md` (chỉ 1 file cấp này). Project: quét từ git root xuống cwd, file
   gần cwd hơn ưu tiên cao hơn. Cap mặc định 32 KiB (`project_doc_max_bytes`). Nguồn:
   developers.openai.com/codex (qua scout) + verdent.ai (đối chiếu, độc lập).
2. **Skills — CÓ chuẩn chính thức, gần như giống hệt Claude Code Skills.** Codex CLI
   dùng chuẩn mở **Agent Skills** (agentskills.io) — SKILL.md bắt buộc YAML frontmatter
   `name`+`description` + phần hướng dẫn markdown, portable qua nhiều CLI (Claude Code,
   Codex, Cursor, Gemini CLI). Discovery: quét `.agents/skills/` từ cwd lên tới repo
   root, cộng thêm user/admin/system location. Nguồn: agentskills.io/home,
   agentskills.io/specification (2 trang chính thức của chuẩn) + axiomstudio.ai (đối
   chiếu độc lập, khớp).
3. **config.toml** — khối hợp lệ chính thức: `model`, `approval_policy`, `sandbox_mode`
   (cũ), `default_permissions`+`[permissions]` (mới, permission profiles), `mcp_servers.*`,
   `features.*`, `plugins.*`, `[hooks]` (inline). Field lỗi thời gây bug tương thích nếu
   copy nguyên văn: `ask_for_approval`, `sandbox`, `experimental_use_rmcp_client`,
   top-level `[env]`. Nguồn: GitHub `openai/codex` issue #17012 (schema thật) +
   learn.chatgpt.com/docs/config-file/config-reference.
4. **Permission profiles thay `sandbox_mode`** từ Codex ≥0.138.0 — 2 hệ **không hợp
   nhất** (compose) được: hoặc dùng `default_permissions`+`[permissions]`, hoặc dùng
   `sandbox_mode`/`sandbox_workspace_write`, không dùng cả hai cùng lúc; nếu
   `sandbox_mode` xuất hiện ở bất kỳ đâu (file/flag/profile), Codex ưu tiên nhánh cũ.
   Máy user (0.147.0-alpha) đủ mới cho nhánh permission profiles. Nguồn:
   developers.openai.com/codex/permissions,
   developers.openai.com/codex/enterprise/managed-configuration.
5. **MCP server format khác hẳn Claude Code**: TOML `[mcp_servers.<tên>]` (snake_case),
   không phải JSON `mcpServers` (camelCase) như `settings.json`/`.mcp.json` của Claude
   Code — cần đổi tên khối + convert JSON→TOML khi migrate, không copy thẳng được.
   Nguồn: commit chính thức `openai/codex`.
6. **Hooks — chính thức, ổn định** (không còn experimental). Khai qua `hooks.json`
   HOẶC khối inline `[hooks]` trong `config.toml`, đặt ở `~/.codex/` (global) hoặc
   `.codex/` (project) — **khác với** precedent `SimplifyWorkflow` (đặt cứng ở
   `.codex/hooks.json` — trùng ngẫu nhiên với vị trí project thật, nhưng KHÔNG có
   global). Field xác nhận: `matcher`, `command`, `additionalContext`, `statusMessage`,
   `additionalContextLimit`; dùng chung schema event giữa 2 cách khai. Danh sách event
   cụ thể (SessionStart/PreToolUse/PostToolUse/Stop...) — có tài liệu nhưng CHƯA đối
   chiếu 1-1 với tên event Claude Code trong research này (để làm ở bước implement khi
   đọc kỹ `hooks.json` thật của TDQWorkflow). Nguồn: developers.openai.com/codex,
   learn.chatgpt.com/docs/config-file/config-reference.
7. **Plugin — schema RIÊNG, không map 1:1 với Claude Code.** Plugin Codex bắt buộc
   manifest `.codex-plugin/plugin.json`, có thể kèm `skills/`, `hooks/hooks.json`,
   `.app.json` (map MCP server đã đăng ký), `.mcp.json` (MCP server đóng gói theo
   plugin). Claude Code dùng `.claude-plugin/plugin.json` + `marketplace.json` +
   `agents/`/`commands/`/`hooks/`/`skills/` — cấu trúc khác tên field và cách khai MCP.
   → xác nhận quyết định 4.A (bỏ qua, không best-effort convert). Nguồn:
   developers.openai.com/plugins/build/plugins.
8. Không tìm thấy tài liệu chính thức cho: Codex có khái niệm "subagent" định nghĩa
   bằng file `.md` + frontmatter (`agents/*.md` của Claude Code) hay không — route rỗng
   trong research. Coi là KHÔNG map được (không suy đoán).

## Quyết định đã chốt

1. **Phạm vi nguồn: chỉ `~/.claude/*` global** (không đụng `.claude/` project-level).
2. **Đích: hỗ trợ cả apply trực tiếp máy hiện tại (`~/.codex/*`) lẫn build bundle
   cross-machine** — kiến trúc soi theo `claude_export.py` (subcommand tách bạch, ví dụ
   `apply` ghi thẳng `~/.codex/`, `build` sinh bundle thư mục/zip để mang máy khác).
3. **Script Python xác định** `scripts/codex_clone.py`, có test — không phải skill
   thuần hướng dẫn.
4. **Phần không map 1:1 → bỏ qua, liệt kê rõ trong report/manifest**, không best-effort
   convert. Danh sách xác nhận không map: `agents/*.md` (subagent), plugin manifest
   (`.claude-plugin` → `.codex-plugin`, field khác hẳn), field `[env]` top-level cũ.
5. **Ghi đè toàn bộ đích**, không merge, không backup tự động (khác `full-claude-export`
   trước đó) — user chọn rõ ràng ở câu 5.
6. **Copy secret thật nguyên văn** (Tavily key, MCP token...) sang `config.toml`/bundle
   — **KHÔNG** bật bước "quét secret: sạch" chặn build cho riêng `codex_clone.py`
   (khác hẳn `claude_export.py`). User đã được cảnh báo xung đột với quy ước sẵn có ở
   câu hỏi 8 và xác nhận chấp nhận rủi ro rõ ràng (chọn B, không phải phương án đề
   xuất). **Ghi rõ cảnh báo này trong SKILL.md và output của tool** (banner rủi ro khi
   chạy `build` để mang bundle sang máy khác) để user tương lai không quên.
7. **Mapping cụ thể** (chốt theo research, không đoán):
   - `~/.claude/CLAUDE.md` → `~/.codex/AGENTS.md` (copy, không merge — theo quyết
     định 5).
   - `~/.claude/skills/<tên>/SKILL.md` + tài nguyên kèm → `~/.codex/skills/<tên>/`
     (copy gần như nguyên trạng — cùng chuẩn Agent Skills; **cảnh báo not_found**: vị
     trí global user-level chính xác của Codex — `~/.codex/skills/` hay biến thể khác —
     KHÔNG có trong 12 finding đã research, chỉ có vị trí "user/admin/system location"
     nói chung và vị trí project (`.agents/skills/` từ cwd lên root) là rõ. Việc xác
     định đường dẫn user-level đúng chữ phải làm ở bước implement bằng cách đọc
     `codex --help`/`codex doctor -v` hoặc test thật trên máy, KHÔNG suy đoán tiếp ở
     đây).
   - MCP server trong `settings.json`/`~/.claude.json` (`mcpServers`, JSON camelCase)
     → khối `[mcp_servers.<tên>]` trong `config.toml` (TOML snake_case) — convert field
     `command`/`args`/`env` (field phổ biến của mọi client MCP, có xác nhận tên khối
     top-level chính thức, mức tin cậy đủ cho auto-convert).
   - `agents/*.md`, `commands/*.md`, plugin (`.claude-plugin/*`) → KHÔNG convert, liệt
     kê trong report theo quyết định 4.
   - **`hooks` (settings.json) và `permissions` (allow/deny/ask theo tool-pattern) →
     KHÔNG convert, thêm vào danh sách "không map"** — 2 lý do: (a) `permissions` của
     Claude Code là ACL theo pattern lệnh/tool (vd `Bash(git *)`), khác hẳn về bản chất
     với `approval_policy`/`sandbox_mode`/permission profiles của Codex (kiểm soát
     sandbox hệ điều hành, không phải ACL theo tool) — không có ánh xạ 1:1 hợp lý; (b)
     dù field `matcher`/`command`/`additionalContext`/`statusMessage` của Codex hooks
     khớp tên với Claude Code, **danh sách event** (SessionStart/PreToolUse/...) CHƯA
     được đối chiếu 1-1 trong research này — convert mù event có thể tạo hook không
     bao giờ chạy hoặc chạy sai lúc. Copy tay có kiểm tra là việc của user, không phải
     tool tự động ở v1 này.
8. Tool `apply` ghi thẳng, không cần gate dry-run riêng — nhất quán với hành vi sẵn có
   của `claude_export.py build` (ghi trực tiếp, không hỏi lại mỗi lần).

## Phương án đã loại

- Merge có backup khi đích đã có config (5.A) — loại, user chọn ghi đè toàn bộ.
- Placeholder cho secret (6.A) — loại, user xác nhận muốn copy giá trị thật kể cả
  trong bundle cross-machine, dù đã được cảnh báo rủi ro.
- Best-effort convert phần không map được (4.B) — loại, rủi ro suy đoán sai vì Codex
  không có khái niệm tương đương đã xác nhận (agents/, plugin manifest).
- Bao gồm cả `.claude/` project-level (1.B) — loại, user chọn chỉ global.
- Dùng `.codex/rules/*.rules` hay `.codex/hooks.json` đặt cứng theo precedent
  `SimplifyWorkflow` — loại làm căn cứ kỹ thuật, vì không xác nhận được là quy ước
  chính thức Codex (chỉ dùng project đó làm tham khảo bố cục, không phải nguồn).

## Nguồn

- `docs/tdq/research/2026-08-05-clone-setting-codex.md` (search-scout, 6 câu hỏi, 11
  finding phase 1).
- `docs/tdq/research/search/2026-08-05-clone-setting-codex/merged.json` +`report.md`
  (deep-search phase 2, 3 route đào sâu, 12 finding sau dedup, đa số nguồn chính thức
  developers.openai.com/codex, agentskills.io, learn.chatgpt.com, GitHub openai/codex).
- Khảo sát thực địa `codex --help`/`codex doctor` trên máy user + đọc
  `~/Documents/SimplifyWorkflow/PluginOutput` (tham khảo bố cục, không phải nguồn kỹ
  thuật — xem mục Phương án đã loại).

## Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Phân tích (đã xong) | CÓ | Bắt buộc — đã tránh được 2 lỗi giả định sai (hooks.json vị trí, .rules không chính thức) nhờ research thật. |
| Spec | CÓ | Khung bất biến — chốt 8 quyết định + mapping cụ thể thành spec chính thức. |
| Plan | CÓ | Khung bất biến — chia task theo mapping từng loại artifact + test tương ứng. |
| Research thêm | BỎ | Đã đủ nguồn cho mọi quyết định thiết kế; 1 câu còn "not_found" (vị trí skills user-level chính xác) xử lý bằng đọc code/CLI thật ở bước implement, không cần thêm vòng Tavily. |
| Chia nhiều subagent song song | BỎ | Khối lượng vừa (1 script chính + test + skill scaffold), 1 luồng main làm liền mạch, tránh overhead điều phối cho công việc phụ thuộc chặt vào cùng 1 file mapping. |
| QC độc lập bằng agent riêng | CÓ | Rủi ro cao hơn `full-claude-export`: ghi đè trực tiếp `~/.codex/*` thật trên máy + cố ý copy secret thật vào bundle — bắt buộc agent QC độc lập xác minh hành vi ghi đè đúng phạm vi, không lem sang chỗ khác, và banner cảnh báo secret có xuất hiện. |
| Review sâu code (tdq-reviewer) | CÓ | Script mới hoàn toàn (không phải sửa trên nền 46 test có sẵn như `claude_export.py`) — thiết kế mới rủi ro cao hơn, cần review trước khi build hoặc trong QC. |
| Implement | CÓ | Khung bất biến. |
| Report | CÓ | Khung bất biến. |

## Kiểm cổng

- **Phạm vi cuối rõ chưa?** Rõ: tạo skill Claude Code mới `clone-setting-to-codex`
  (SKILL.md + references, dùng `skill-creator`) bọc script mới `scripts/codex_clone.py`
  với 2 subcommand chính `apply` (ghi thẳng `~/.codex/*` máy hiện tại) và `build` (sinh
  bundle cross-machine, banner cảnh báo secret), map 4 loại artifact (AGENTS.md, skills,
  MCP servers, hooks/permissions) theo bảng chốt ở trên, bỏ qua + báo cáo phần không
  map (agents/, commands/, plugin).
- **Cần model/download/cài đặt gì không?** Không — Codex CLI đã có sẵn trên máy
  (0.147.0-alpha), script chỉ đọc/ghi file, không cần gọi lệnh `codex` để hoạt động.
- **Phạm vi QC/test/validate đã có chưa?** Có: test cho từng loại mapping (AGENTS.md,
  skills copy, MCP JSON→TOML, hooks/permissions field lọc field lỗi thời, danh sách
  not-convert), test hành vi ghi đè + secret verbatim đúng quyết định, QC agent độc lập
  chạy thử `apply` + `build` thật rồi xác minh cấu trúc/nội dung.
