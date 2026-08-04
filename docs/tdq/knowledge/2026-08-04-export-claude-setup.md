# Knowledge: 2026-08-04-export-claude-setup

## Năng lực dùng được

Phân vân → DÙNG. Không xoá bảng này kể cả khi mọi dòng là KHÔNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-build, tdq-conventions, tdq-intake, tdq-plan, tdq-spec, tdq-status | plugin:tdq-workflow | NỀN | chính workflow đang chạy request này |
| update-config | built-in | DÙNG | tham chiếu cấu trúc `settings.json` (global/project/local), permissions, hooks khi liệt kê manifest export |
| keybindings-help | built-in | DÙNG | tham chiếu cấu trúc `keybindings.json` cần đưa vào export |
| remember (remember, remember:doctor) | plugin:remember / built-in | DÙNG | tham chiếu cấu trúc `.remember/` (memory) cần export; doctor để kiểm tra tình trạng memory trước khi đóng gói |
| plugin-dev:plugin-structure | plugin:plugin-dev | DÙNG | tham chiếu chuẩn `plugin.json`/`marketplace.json` khi lập manifest plugin đã cài |
| tavily-search | plugin:tavily | DÙNG | dùng ở bước research nhiều hướng (bước 3 phase analyze) qua `tavily-primary` |
| graphify, frontend-design, hookify:writing-rules, hookify:configure, hookify:help, hookify:hookify, hookify:list, mcp-server-dev:build-mcp-app, mcp-server-dev:build-mcp-server, mcp-server-dev:build-mcpb, plugin-dev:agent-development, plugin-dev:command-development, plugin-dev:hook-development, plugin-dev:mcp-integration, plugin-dev:plugin-settings, plugin-dev:skill-development, plugin-dev:create-plugin, skill-creator, tavily-best-practices, tavily-cli, tavily-crawl, tavily-dynamic-search, tavily-extract, tavily-map, tavily-research, feature-dev:feature-dev, code-review:code-review, claude-md-management:revise-claude-md, claude-md-management:claude-md-improver, agent-sdk-dev:new-sdk-app, dataviz, artifact-design, artifact-diagramming, artifact-capabilities, simplify, fewer-permission-prompts, loop, schedule, claude-api, run, init, review, security-review | built-in/plugin (nhiều nguồn) | KHÔNG | khác lĩnh vực |

## Khảo sát máy nguồn (đọc code/cấu hình thực tế)

Chi tiết đầy đủ đã thu thập qua Explore agent (2026-08-04). Tóm tắt các điểm quyết định:

- **Global `~/.claude/`**: `settings.json` (3873B, có 2 secret Tavily hard-code trong `env`,
  `permissions.defaultMode=bypassPermissions`, hook SessionStart/SessionEnd gọi
  `scripts/plugin_tiers.py reset`, statusLine trỏ `statusline.sh`, `enabledPlugins` map 51
  plugin, `extraKnownMarketplaces.tdq-local` trỏ path TDQWorkflow), `CLAUDE.md` (89 dòng),
  `plugin-tiers.json` (always_off 6 + on_demand 16), `plugins/installed_plugins.json` (51
  plugin, hầu hết marketplace `claude-plugins-official` scope `user`, riêng `superpowers`
  scope `project` gắn Project01 — NGOÀI phạm vi export), `plugins/known_marketplaces.json`
  (2 marketplace: `claude-plugins-official` GitHub `anthropics/claude-plugins-official`,
  `tdq-local` directory-source = chính repo TDQWorkflow), `skills/graphify` (skill user-level
  duy nhất), `.remember/now.md` (memory, 559B), `statusline.sh` (256 dòng, chỉ gọi `jq`),
  `scripts/plugin_tiers.py` (script hook), không có `keybindings.json` (dùng default).
- **`~/.claude.json`** (65KB, không phải trong `.claude/`): có `mcpServers` (2 server HTTP:
  `tavily-primary`, `tavily-backup`, cùng URL `https://mcp.tavily.com/mcp/`, auth qua header
  `Authorization: Bearer ${TAVILY_API_KEY_PRIMARY|BACKUP}` — chỉ tham chiếu biến, giá trị
  thật nằm ở `settings.json`), `projects` (5 project từng mở, chỉ TDQWorkflow trong phạm
  vi), `oauthAccount` (metadata tài khoản, không export — máy đích tự đăng nhập lại),
  `machineID`/`userID` (không export).
- **Project `.claude/` trong TDQWorkflow**: chỉ 1 file `settings.json` (184B, chứa 5 env var
  `TDQ_SEARCH_*`, không phải secret). Repo TDQWorkflow tự nó **không có git remote** (local-
  only) → "clone" nghĩa là copy vật lý thư mục, không phải `git clone <url>`.
- **CLI dependency đã cài trên máy nguồn** (cần ghi rõ version tối thiểu + hướng dẫn cài
  trong README, đa nền theo câu hỏi 3):
  - `claude` (Claude Code) 2.1.221
  - `node` v24.18.0, `npm` 11.16.0
  - `python3` 3.12.13, `pip3` 26.1.2
  - `git` 2.50.1
  - `uv`/`uvx` 0.11.32 (dùng để cài `graphify` qua `uv tool install`)
  - `graphify` 0.9.28 — cài qua uv tool, symlink tại `~/.local/bin/graphify` +
    `graphify-mcp`, cần hướng dẫn cài (repo: github.com/Graphify-Labs/graphify, theo
    CLAUDE.md mục 9).
  - `codex` (Codex CLI) 0.146.0-alpha.9.2 — trên máy này chạy từ
    `/Applications/ChatGPT.app/Contents/Resources/codex` (kèm theo app ChatGPT desktop,
    **macOS-only path này**); trên Linux/Windows phải cài Codex CLI riêng (không qua app
    ChatGPT desktop) — cần research thêm cách cài chuẩn đa nền ở bước spec/plan nếu cần.
  - `agy` (Google Antigravity CLI) 1.1.10 — binary độc lập 165MB tại `~/.local/bin/agy`,
    không qua package manager chuẩn — cần hướng dẫn tải/cài riêng.
  - `gh` (GitHub CLI): **không cài** trên máy này — KHÔNG phải dependency bắt buộc của
    workflow hiện tại, không cần đưa vào manifest bắt buộc (ghi optional nếu user cần).
  - `docker`: không cài, không dùng trong workflow hiện tại.

## Quyết định đã chốt (từ vòng interview)

1. **Phạm vi**: global `~/.claude` (đã lọc runtime/cache/secret) + toàn bộ repo
   TDQWorkflow (copy vật lý). KHÔNG gồm Project01_LiveCaptionTranslate,
   insightfaceserverv2, plugin `superpowers`.
2. **Secret**: giữ cấu trúc `env`, thay giá trị 2 Tavily key bằng placeholder tường minh
   (không bao giờ ghi giá trị thật ra export/README/log).
3. **OS đích**: đa nền — README có 3 nhánh cài dependency: macOS (brew), Linux (apt/dnf
   tuỳ distro, ghi rõ Debian/Ubuntu family là ví dụ chính), Windows (qua WSL2 + Linux
   instructions bên trong WSL — Claude Code không hỗ trợ Windows native ngoài WSL, cần xác
   nhận qua research thêm ở bước spec nếu cần).
4. **Hình thức**: KHÔNG có script shell tự động (`setup.sh`) thực thi việc cài đặt trên
   máy đích. Có 3 loại tài liệu, đều là Markdown/JSON tĩnh:
   - **File instruction** (quy trình dựng export — Claude/user làm theo để (tái) tạo bản
     export mới khi cấu hình máy nguồn thay đổi): liệt kê từng bước thu thập dữ liệu, lọc
     secret/runtime, copy file, sinh manifest, sinh README.
   - **Manifest** (JSON máy-đọc-được: danh sách plugin/marketplace/mcp/CLI-dependency kèm
     version — snapshot tại thời điểm export).
   - **README** (đi kèm trong bundle xuất ra, hướng dẫn con người setup máy đích từng bước
     lệnh thủ công, đa nền).
5. **Vị trí — 2 nơi khác nhau, không được nhầm lẫn**:
   - **Bộ công cụ export** (file instruction + template README + template manifest) lưu
     **cố định trong repo TDQWorkflow**, tại thư mục `claude-export/` ở root repo → theo
     dõi bằng git, tái sử dụng được cho các lần export sau (mỗi khi cấu hình máy nguồn đổi
     — thêm plugin, đổi skill... — chạy lại instruction để sinh bản export mới, không phải
     viết lại từ đầu).
   - **Bundle export thực tế** (bản copy config đã lọc secret, bản copy repo TDQWorkflow,
     manifest đã điền dữ liệu thật, README hoàn chỉnh) **KHÔNG nằm trong `claude-export/`
     của repo** — sinh ra tại một đường dẫn đích do user chỉ định lúc chạy instruction
     (path là tham số/placeholder trong file instruction, ví dụ mặc định gợi ý
     `~/Documents/claude-code-export/`, user có thể đổi). Giữ nguyên lý do đã chốt: tránh
     lồng bản copy repo TDQWorkflow vào bên trong chính repo TDQWorkflow.

## Loại trừ khỏi export (đã có căn cứ từ research + khảo sát)

Runtime/cache/machine-specific, không mang ý nghĩa "cấu hình" — không export:
`history.jsonl`, `sessions/`, `projects/*/*.jsonl` (session transcript), `debug/`, `logs/`,
`cache/`, `shell-snapshots/`, `file-history/`, `telemetry/`, `image-cache/`, `paste-cache/`,
`ide/`, `daemon*`, `plugins/cache/`, `plugins/plugin-catalog-cache.json`,
`plugins/data/` (dữ liệu runtime riêng từng plugin), `machineID`, `userID`, `projects` (nhánh
thống kê trong `~/.claude.json`), `oauthAccount`, `.DS_Store`, các file `.bak*`.

## Kiểm cổng (3 câu hỏi bắt buộc trước khi sang spec)

- **Phạm vi cuối đã rõ**: Có — 2 sản phẩm tách biệt:
  (1) thư mục `claude-export/` trong repo TDQWorkflow chứa **bộ công cụ export tái dùng
  được** (file instruction quy trình dựng export + template manifest + template README),
  version theo git;
  (2) khi chạy instruction, sinh ra **bundle export thực tế** tại đường dẫn đích do user
  chọn (ngoài repo, mặc định gợi ý `~/Documents/claude-code-export/`) gồm: manifest JSON đã
  điền dữ liệu thật (plugin/marketplace/mcp/CLI-deps kèm version), bản copy các file cấu
  hình global đã lọc secret+runtime, bản copy repo TDQWorkflow, và README.md hoàn chỉnh
  hướng dẫn từng bước setup lại trên máy khác (đa nền).
- **Cần model/download/cài đặt gì**: Có — README phải hướng dẫn cài Claude Code CLI, Node,
  Python, git, uv/uvx (cho graphify), tuỳ chọn Codex CLI + Antigravity CLI (agy) nếu muốn
  dùng mode external — tất cả đều là hướng dẫn cài ONLINE (không đóng gói binary vào export
  vì license/kích thước, riêng `agy` 165MB cần cân nhắc thêm ở spec).
- **Phạm vi QC/test/validate**: Có sơ bộ — QC sẽ đối chiếu manifest export với trạng thái
  thực tế máy nguồn (`installed_plugins.json`, `known_marketplaces.json`,
  `settings.json.enabledPlugins`) khớp 100% số lượng/tên/trạng thái enable; kiểm README
  không thiếu bước nào trong chuỗi cài (marketplace add → plugin install → set env → verify
  bằng `claude --version` + `claude plugin list`). KHÔNG chạy thử end-to-end trên một máy
  thứ hai thật (ngoài phạm vi phiên làm việc này) — sẽ ghi rõ giới hạn này trong spec.
