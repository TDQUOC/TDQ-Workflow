# SPEC — Skill clone-setting-to-codex

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-08-05 · Bản: 1.0 · Request: ../requests/2026-08-05-clone-setting-codex.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi
- Mục tiêu: tạo skill Claude Code mới `clone-setting-to-codex` bọc script
  `scripts/codex_clone.py`, chuyển các phần **map được có căn cứ** từ `~/.claude/*`
  (global) sang cấu hình Codex CLI thật — hoặc ghi thẳng máy hiện tại (`apply`), hoặc
  đóng gói bundle mang sang máy khác (`build`) — và báo cáo rõ phần KHÔNG map được.
- Trong phạm vi:
  - Skill `skills/clone-setting-to-codex/SKILL.md` + `references/mapping.md` (bảng
    mapping làm nguồn sự thật, dùng `skill-creator` để scaffold đúng khuôn).
  - `scripts/codex_clone.py` với 2 subcommand: `apply` (ghi thẳng `~/.codex/*` máy
    hiện tại) và `build --dest <path> [--zip]` (sinh bundle thư mục/zip cross-machine).
  - Convert tự động 3 loại: `CLAUDE.md` → `AGENTS.md`; `skills/<tên>/` →
    `skills/<tên>/` bên Codex (copy nguyên trạng, cùng chuẩn Agent Skills); MCP server
    (`mcpServers` JSON) → `[mcp_servers.<tên>]` trong `config.toml` (TOML).
  - Báo cáo (`CODEX_CLONE_REPORT.md` trong đích) liệt kê phần KHÔNG convert: hooks,
    permissions, `agents/*.md`, `commands/*.md`, plugin — kèm lý do từng mục.
  - Banner cảnh báo secret khi chạy `build` (bundle mang secret thật sang máy khác).
- NGOÀI phạm vi:
  - `.claude/` project-level (chỉ global `~/.claude/*`).
  - Convert `hooks`, `permissions` (allow/deny/ask), `agents/*.md` (subagent),
    `commands/*.md`, plugin (`.claude-plugin/*`) — lý do kỹ thuật ở §3.
  - Merge/backup khi đích đã có config Codex — luôn ghi đè toàn bộ.
  - Che/redact secret — luôn copy giá trị thật (mọi đích, kể cả bundle).
  - Subcommand `check` (drift detection) — không được yêu cầu, `apply`/`build` tự đủ
    tái chạy an toàn vì luôn ghi đè.
  - Cài đặt/khởi động `codex` CLI — chỉ ghi file cấu hình, không gọi lệnh `codex`.

## 1b. Lộ trình
| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ (đã xong ở phase analyze) | 2 phase, 4 agent, 12 finding — bắt buộc vì cấu trúc Codex CLI là ẩn số ngoài, đã tránh 2 giả định sai (vị trí hooks.json, `.rules` không chính thức). |
| Interview | CÓ (đã xong, 2 vòng, 8 câu) | Nhiều quyết định thay đổi kết quả: phạm vi nguồn, đích, cơ chế, xử lý phần không map, overwrite/merge, secret. |
| QC độc lập (agent) | CÓ | Ghi đè trực tiếp `~/.codex/*` thật + cố ý copy secret thật vào bundle — rủi ro cao hơn mức thường, cần agent QC độc lập xác minh phạm vi ghi đè và banner cảnh báo. |
| Chia nhiều subagent song song | BỎ | Khối lượng vừa (1 script chính + skill scaffold + test), phụ thuộc chặt cùng 1 bảng mapping — 1 luồng main nhanh hơn điều phối song song. |
| Review sâu (tdq-reviewer) | CÓ | Script hoàn toàn mới (không có 46-test baseline như `claude_export.py`) — thiết kế mới, cần review trước/trong QC. |

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Skill mới | `skills/clone-setting-to-codex/SKILL.md` + `references/mapping.md` | `skill_inventory.py` liệt kê được skill; `doc_lint.py` exit 0 |
| 2 | Script convert | `scripts/codex_clone.py` (`apply`, `build`) | Test PASS cho từng loại mapping (AGENTS.md, skills, MCP JSON→TOML) |
| 3 | Report phần không map | `<đích>/CODEX_CLONE_REPORT.md` | Test PASS: report liệt kê đủ 5 mục (hooks/permissions/agents/commands/plugin) kèm lý do |
| 4 | Banner cảnh báo secret khi `build` | stdout của `codex_clone.py build` | Test PASS: chuỗi cảnh báo xuất hiện trong output khi chạy `build`, KHÔNG xuất hiện khi chạy `apply` (local không cần banner cross-machine) |
| 5 | Test suite mới | `tests/test_codex_clone.py` | `python3 -m unittest test_codex_clone -v` (trong `tests/`) toàn bộ PASS |
| 6 | Chạy thật 1 lần trên máy user | `~/.codex/AGENTS.md`, `~/.codex/config.toml`, `~/.codex/skills/*` | `apply` chạy thật exit 0; đọc lại file xác nhận nội dung khớp nguồn |

## 3. Cách tiếp cận & lý do
- Chọn: script Python độc lập (`codex_clone.py`), kiến trúc soi theo
  `scripts/claude_export.py` đã có (subcommand tách bạch, log timestamp, secret-scan
  làm nền nhưng tắt bước CHẶN cho tool này — xem §5).
- Vì: user chọn 3.A (script xác định, có test) thay vì skill thuần hướng dẫn — đảm bảo
  tái chạy được, review được, không lệch giữa các lần chạy (quyết định knowledge #3).
- Chỉ auto-convert 3 loại có căn cứ nguồn chính thức vững (AGENTS.md, skills,
  mcp_servers) — **hooks và permissions bị loại khỏi auto-convert** dù ban đầu có ý
  định best-effort, vì rà lại thấy 2 lý do chặn: (a) `permissions` Claude Code là ACL
  theo tool-pattern, khác bản chất với `approval_policy`/sandbox/permission-profile
  của Codex (kiểm soát sandbox OS) — không có ánh xạ hợp lý; (b) danh sách event hooks
  (SessionStart/PreToolUse/...) của Codex CHƯA được đối chiếu 1-1 với Claude Code
  trong research đã có — convert mù event có thể tạo hook chạy sai lúc hoặc không chạy,
  vi phạm nguyên tắc "không suy đoán".
- Đã loại: convert `agents/*.md` (subagent) — Codex không có khái niệm tương đương xác
  nhận được (route rỗng trong research); plugin (`.claude-plugin` → `.codex-plugin`) —
  2 schema khác hẳn field, tự convert rủi ro tạo plugin hỏng.
- Đã loại: merge có backup khi đích đã có config — user chọn ghi đè toàn bộ (5.B).
- Đã loại: placeholder cho secret — user xác nhận muốn copy giá trị thật kể cả trong
  bundle cross-machine, đã được cảnh báo xung đột với quy ước `claude_export.py` và
  chấp nhận rủi ro rõ ràng (câu hỏi 8, chọn B không phải phương án đề xuất).

## 3b. Năng lực & công cụ
| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `graphify` | user | DÙNG | Chạy `graphify extract . --code-only` cuối turn có đổi code (bắt buộc). |
| `skill-creator` | plugin:skill-creator | DÙNG | Scaffold `skills/clone-setting-to-codex/SKILL.md` đúng khuôn frontmatter/description. |
| `mem0-memory` | user | DÙNG | Đã `remember` fact cấu trúc Codex CLI (durable, cross-project) ở phase analyze. |
| `tavily-*` | plugin:tavily | DÙNG | Đã dùng qua agent `search-scout`/`search-runner` ở phase analyze (2 phase, 12 finding). |
| `tdq-workflow:tdq-spec` | plugin:tdq-workflow | NỀN | Skill khung đang chạy — viết spec này. |
| `tdq-workflow:tdq-plan` | plugin:tdq-workflow | NỀN | Skill khung — viết plan ngay sau duyệt spec. |
| `tdq-workflow:tdq-build` | plugin:tdq-workflow | NỀN | Skill khung — thực thi plan sau khi duyệt. |
| `plugin-dev:skill-development` | plugin:plugin-dev | KHÔNG | spec §3 đã chọn cách khác tốt hơn — trùng chức năng với `skill-creator` đã chọn |
| `claude-md-improver` | plugin:claude-md-management | KHÔNG | khác lĩnh vực — không sửa `CLAUDE.md`, chỉ ĐỌC để convert sang `AGENTS.md` |
| `frontend-design` | plugin:frontend-design | KHÔNG | khác lĩnh vực — không có UI |
| `plugin-dev:*` (agent/command/hook/mcp/settings/plugin-structure) | plugin:plugin-dev | KHÔNG | khác lĩnh vực — không tạo plugin Claude Code mới, không tạo MCP server mới |
| `mcp-server-dev:*` | plugin:mcp-server-dev | KHÔNG | khác lĩnh vực — không xây MCP server mới, chỉ convert config MCP đã có |
| `playground`, `remember`, `hookify:*` | plugin tương ứng | KHÔNG | khác lĩnh vực |
| `dataviz`, `artifact-design`, `artifact-diagramming`, `artifact-capabilities` | built-in | KHÔNG | khác lĩnh vực — không tạo artifact/chart |
| `claude-api` | built-in | KHÔNG | khác lĩnh vực — không gọi Claude API trực tiếp trong code sửa |
| `update-config`, `keybindings-help` | built-in | KHÔNG | khác lĩnh vực — không đổi `settings.json`/keybindings của Claude Code, chỉ ĐỌC để convert |
| `run` | built-in | KHÔNG | khác lĩnh vực — không có app để chạy/screenshot |
| `simplify` | built-in | KHÔNG | spec §3 đã chọn cách khác tốt hơn — mã mới viết theo test ngay từ đầu |
| `security-review`, `review`, `init` | built-in | KHÔNG | khác lĩnh vực — không phải yêu cầu review bảo mật tổng quan hay khởi tạo project mới |
| `code-review:code-review` | plugin:code-review | KHÔNG | spec §3 đã chọn cách khác tốt hơn — đã có QC riêng bằng agent `tdq-qc-tester` + `tdq-reviewer` (§1b) |
| `agent-sdk-dev:*` | plugin:agent-sdk-dev | KHÔNG | khác lĩnh vực — không xây Agent SDK app |

## 4. Yêu cầu bắt buộc
- Log service bật mặc định: `codex_clone.py` in log timestamp ISO ra stderr cho mỗi
  bước convert (theo đúng pattern `log()` của `claude_export.py`), tắt được qua
  `--quiet`.
- Không placeholder/TODO/mock: mọi giá trị ghi vào `config.toml`/`AGENTS.md` là nội
  dung thật đọc từ `~/.claude/*`, không có chuỗi giả lập.
- Mỗi loại mapping (AGENTS.md, skills, mcp_servers, report phần-không-map, banner
  secret) có unit test riêng trong `tests/test_codex_clone.py`, chạy bằng
  `python3 -m unittest test_codex_clone`.

## 5. Ràng buộc & rủi ro
| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| `apply` ghi đè trực tiếp `~/.codex/config.toml`/`AGENTS.md`/`skills/*` thật trên máy, không backup | Nếu user đã tự cấu hình Codex trước đó (hiện `~/.codex` đang trống, chưa xảy ra), lần chạy đầu sẽ mất cấu hình cũ | Chấp nhận theo quyết định 5.B của user; SKILL.md ghi rõ cảnh báo "ghi đè, không backup" ngay đầu mục Cách dùng |
| `build` nhúng secret thật (Tavily key, MCP token) vào bundle cross-machine | Bundle rò rỉ nếu bị chia sẻ/upload nhầm chỗ khác | Chấp nhận theo quyết định 6.B của user (đã cảnh báo rõ ở câu hỏi 8); banner cảnh báo in ra mỗi lần `build` + ghi trong `CODEX_CLONE_REPORT.md` |
| Vị trí thư mục skills user-level thật của Codex CHƯA xác nhận 100% qua research (chỉ có "user/admin/system location" chung chung, không có đường dẫn cụ thể) | Convert sai chỗ → Codex không discover được skills đã copy | Ở bước implement: xác minh bằng cách đọc `codex --help`/thử nghiệm thật (tạo 1 skill test, chạy `codex`, xem có discover); dùng suy luận có căn cứ `$CODEX_HOME/skills/` (= `~/.codex/skills/`, theo pattern `CODEX_HOME` đã xác nhận qua `codex doctor`) làm mặc định NHƯNG gắn cờ `unverified` rõ ràng trong log + report nếu không tìm được nguồn xác nhận trực tiếp |
| Field `command`/`args`/`env` của Codex `mcp_servers` TOML chưa được research xác nhận chi tiết từng field (chỉ xác nhận tên khối top-level `mcp_servers`) | Convert MCP server có thể sai field nhỏ | Test riêng cho conversion; nếu implement phát hiện field khác — cập nhật lại, không chặn scope các phần khác |
| Field lỗi thời (`ask_for_approval`/`sandbox`/`experimental_use_rmcp_client`/top-level `[env]`) nếu lỡ copy nguyên settings.json | Codex báo lỗi schema hoặc bỏ qua âm thầm | Không copy nguyên `settings.json` — chỉ trích xuất đúng 3 loại đã chốt (AGENTS.md nguồn, skills, mcpServers), test khoá danh sách field cấm |

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Test suite mới | `python3 -m unittest test_codex_clone -v` (trong `tests/`) | Toàn bộ test PASS |
| Q2 | `apply` chạy thật trên máy user | `python3 scripts/codex_clone.py apply` | Exit 0; `~/.codex/AGENTS.md`, `~/.codex/config.toml` tồn tại, nội dung không rỗng |
| Q3 | Nội dung AGENTS.md khớp nguồn | So `~/.codex/AGENTS.md` với `~/.claude/CLAUDE.md` | Giống nội dung (copy nguyên văn) |
| Q4 | MCP servers convert đúng cấu trúc | Đọc `~/.codex/config.toml` khối `[mcp_servers.*]` | Có TOML hợp lệ (parse được bằng `tomllib`), tên khối đúng snake_case, đủ số server so với nguồn |
| Q5 | Report liệt kê đủ phần không map | Đọc `~/.codex/CODEX_CLONE_REPORT.md` | Có đủ 5 mục: hooks, permissions, agents/*.md, commands/*.md, plugin — kèm lý do |
| Q6 | Banner cảnh báo secret khi `build` | `python3 scripts/codex_clone.py build --dest <tmp> --zip` rồi đọc stdout | Có dòng cảnh báo secret thật trong bundle; bundle chứa giá trị secret thật (đúng theo quyết định — KHÔNG được redact) |
| Q7 | Review độc lập (`tdq-reviewer`) | Agent đọc `codex_clone.py` + spec | Không còn lỗ hổng thiết kế nghiêm trọng chưa được nêu ở §5 |
| Q8 | QC hành vi ghi đè đúng phạm vi (agent `tdq-qc-tester`) | Chạy `apply` trên thư mục `~/.codex` giả lập (temp `CODEX_HOME` qua biến môi trường/tham số `--codex-home`), xác nhận không ghi ra ngoài phạm vi khai báo | Chỉ đúng các file trong §2 bị ghi, không đụng file khác trong `$CODEX_HOME` |

DoD: Q1–Q8 PASS; skill `clone-setting-to-codex` xuất hiện trong `skill_inventory.py`;
`doc_lint.py` trên `SKILL.md`/`references/mapping.md` exit 0; `graphify extract .
--code-only` đã chạy sau khi có code mới; working log đã ghi.

## 7. Câu hỏi còn mở
(Không có — 2 vòng interview (8 câu) đã trả lời đủ ở
`docs/tdq/questions/2026-08-05-clone-setting-codex.md`; 1 chi tiết kỹ thuật nhỏ chưa
100% xác nhận (đường dẫn skills user-level) đã có phương án xử lý cụ thể ở §5, không
phải câu hỏi cần user quyết định.)
