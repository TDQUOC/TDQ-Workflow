# KNOWLEDGE — Bump version + export đầy đủ hơn

Request: `../requests/2026-08-05-bump-version-va-export.md` · Lane full · 2026-08-05

## Năng lực dùng được

Kiểm kê bằng `skill_inventory.py` + skill built-in đang thấy trong context.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | skill khung đang chạy phase analyze |
| tdq-spec | plugin:tdq-workflow | DÙNG | viết spec request này |
| tdq-plan | plugin:tdq-workflow | DÙNG | viết plan sau khi duyệt spec |
| tdq-build | plugin:tdq-workflow | DÙNG | thực thi plan, QC, report |
| tdq-conventions | plugin:tdq-workflow | NỀN | quy ước chung mọi phase |
| tdq-status | plugin:tdq-workflow | KHÔNG | khác lĩnh vực |
| graphify | user | DÙNG | rebuild code graph cuối turn có đổi code |
| claude-md-improver | plugin:claude-md-management | KHÔNG | khác lĩnh vực |
| frontend-design | plugin:frontend-design | KHÔNG | khác lĩnh vực |
| writing-hookify-rules | plugin:hookify | KHÔNG | khác lĩnh vực |
| build-mcp-app | plugin:mcp-server-dev | KHÔNG | khác lĩnh vực |
| build-mcp-server | plugin:mcp-server-dev | KHÔNG | khác lĩnh vực |
| build-mcpb | plugin:mcp-server-dev | KHÔNG | khác lĩnh vực |
| playground | plugin:playground | KHÔNG | khác lĩnh vực |
| agent-development | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| command-development | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| hook-development | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| mcp-integration | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| plugin-settings | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| plugin-structure | plugin:plugin-dev | KHÔNG | đã có manifest, không tạo plugin mới |
| skill-development | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| remember | plugin:remember | NỀN | hook tự chạy cuối phiên |
| skill-creator | plugin:skill-creator | KHÔNG | không tạo skill mới |
| tavily-best-practices | plugin:tavily | KHÔNG | không viết tích hợp Tavily |
| tavily-cli | plugin:tavily | KHÔNG | đã dùng MCP, không cần CLI |
| tavily-crawl | plugin:tavily | KHÔNG | không crawl site |
| tavily-dynamic-search | plugin:tavily | KHÔNG | search tĩnh là đủ |
| tavily-extract | plugin:tavily | KHÔNG | snippet đã đủ |
| tavily-map | plugin:tavily | KHÔNG | không map site |
| tavily-research | plugin:tavily | KHÔNG | không đủ 2 dấu hiệu deep search |
| tavily-search | plugin:tavily | DÙNG | 3 truy vấn phase analyze (đã chạy) |
| update-config | built-in | KHÔNG | không đổi settings máy nguồn |
| Explore | built-in (agent) | KHÔNG | phạm vi file đã xác định |
| Plan | built-in (agent) | KHÔNG | plan viết bằng tdq-plan |

## Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ | đã chạy 3 truy vấn, cần luật MCP scope + marketplace local |
| Interview | CÓ | đã chạy 1 vòng, 5 câu, user trả lời đủ |
| Spec | CÓ | lane full |
| Plan | CÓ | lane full |
| Implement | CÓ | mode do user chốt khi duyệt plan |
| QC độc lập (agent) | CÓ | bundle đụng file ngoài repo, cần người thứ hai kiểm |
| Report | CÓ | lane full, ≤10 dòng |

## Quyết định đã chốt (user trả lời vòng 1)

1. **Bump `0.6.2` → `0.7.0`** (minor). Lý do: 5 commit tính năng sau 0.6.2.
2. **Phạm vi = phương án (c)**: vá 8 lỗ hổng + viết `scripts/claude_export.py` có 2 lệnh
   `build` và `check`, kèm unit test.
3. **Ghi đè** bundle `~/Documents/claude-code-export` và **sinh lại** `claude-code-export.zip`.
4. **Giữ `.git`** trong bản copy repo.
5. **Giữ `.remember`** trong bundle.

## 8 lỗ hổng đã đo của bundle 2026-08-04

| # | Lỗ hổng | Bằng chứng đo được |
|---|---|---|
| 1 | Máy đích không có MCP server nào | README mục 5 không có bước add; manifest strip `headers` |
| 2 | Mất `.git` → không phải git repo | `--exclude='.git'` ở Bước 3 |
| 3 | Bundle 17 MB, repo tracked chỉ 6,0 MB / 382 file | 15 MB là `graphify-out/20*/` gitignored |
| 4 | `docs/tdq/state.json` lọt vào bundle | state request cũ, phase `implement`, đã duyệt |
| 5 | `.tdq-turn.jsonl` + `.remember/tmp/` runtime lọt vào | pid, lock, session-slug máy nguồn |
| 6 | 3 file `.DS_Store` dù đã nằm trong danh sách loại trừ | loại trừ chỉ là văn bản, không thi hành |
| 7 | manifest thiếu version plugin + commit SHA | `MANIFEST.template.json` chỉ 5 khoá |
| 8 | Không có cách đo drift | phải đo tay như turn này |

## Ràng buộc kỹ thuật

- Header MCP là `Bearer ${TAVILY_API_KEY_PRIMARY}` — **biến môi trường**, không phải key
  thật, nên khối `mcpServers` copy được mà không lộ secret. Đã xác minh bằng cách đếm
  độ dài và kiểm ký tự `$`, không in giá trị.
- **Cấm** copy đè `~/.claude.json` sang máy đích (chứa `oauthAccount`, `machineID`) —
  nguồn: anthropics/claude-code#15797. Khôi phục bằng `claude mcp add-json <name> --scope user`.
- MCP scope `user` nằm ở `~/.claude.json` key top-level `mcpServers` — nguồn docs chính thức.
- `git clone <path> <dest>` chạy được vì repo không có remote nhưng có `.git` đầy đủ (8,0 MB).
- Loại trừ nên bám `.gitignore` (rsync không tự đọc) — dùng `git clone` là hết sạch vấn đề
  #3/#4/#5/#6 cùng lúc, vì clone chỉ lấy file tracked.
- `.remember/` của repo là **untracked** → `git clone` KHÔNG mang theo, phải copy riêng
  (có lọc `tmp/` và `logs/`).

## Cách tiếp cận đã chọn

Viết `scripts/claude_export.py`:

- `build --dest <dir> [--zip]`: sinh bundle từ máy nguồn, ghi đè an toàn, log có timestamp.
- `check --dest <dir>`: so bundle với nguồn, in bảng drift + exit code khác 0 khi lệch.

Bản copy repo dùng `git clone` (giữ `.git`, chỉ file tracked), rồi copy thêm `.remember/`
đã lọc. Bundle thêm `config/mcp-servers.json` + lệnh `claude mcp add-json` sẵn trong README.
`manifest.json` thêm `plugin_version`, `repo_commit`, `exported_at`, `source_files` (đường
dẫn + sha256 để `check` so lại).

## Phương án đã loại

- **Giữ 7 bước thủ công** — user chốt (c); thủ công là nguyên nhân gốc của lỗi #3–#6
  (danh sách loại trừ chỉ là văn bản, không ai thi hành).
- **Copy đè `~/.claude.json`** — issue 15797, mất oauth/machineID máy đích.
- **Nhúng key thật vào bundle** — vi phạm luật bảo mật; giữ nguyên placeholder.
- **Bỏ `graphify-out` bằng exclude tay** — `git clone` đã loại sạch untracked, không cần.

## Nguồn

- `code.claude.com/docs/en/mcp-quickstart` — bảng scope MCP.
- `code.claude.com/docs/en/plugin-marketplaces` — `claude plugin marketplace add <local dir>`.
- `github.com/anthropics/claude-code/issues/15797` — cấm ghi đè `~/.claude.json`.
- `github.com/anthropics/claude-code/issues/11278` — marketplace phải trỏ thư mục, không trỏ file.
- Chi tiết: `../research/2026-08-05-bump-version-va-export.md`.
