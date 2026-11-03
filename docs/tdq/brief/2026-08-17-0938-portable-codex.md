Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

User: "mở request mới phân tích xem nếu tôi muốn tạo một portable codex có thể có đầy đủ
mcp, hook, skill, rule ví dụ ra folder portable_codex"

Cách hiểu đầu tiên: user muốn PHÂN TÍCH tính khả thi (feasibility) của việc đóng gói một bộ
"codex" di động (portable) — gồm MCP server config, hook, skill, rule (giống bộ máy TDQ hiện
có) — xuất ra một thư mục tên `portable_codex`, để mang dùng ở project/máy khác không phụ
thuộc cấu trúc `${CLAUDE_PLUGIN_ROOT}` hiện tại.

Phạm vi đoán ban đầu (CHƯA CHỐT — cần hỏi):
- "Codex" ở đây là danh từ chung ("bộ luật/kiến thức đóng gói") hay ám chỉ cụ thể sản phẩm
  OpenAI Codex CLI? Cần làm rõ vì ảnh hưởng toàn bộ kiến trúc target.
- Portable cho ai dùng: Claude Code ở project khác, hay cross-tool (Codex CLI, Cursor, Gemini
  CLI...)? TDQWorkflow hiện chỉ target Claude Code.
- Đây là output PHÂN TÍCH (feasibility report/plan) hay bao gồm cả BUILD luôn folder
  portable_codex trong request này?

Chỗ chưa rõ: định nghĩa "codex", đối tượng target chạy portable này, ranh giới phân tích vs
triển khai — tất cả cần hỏi ở vòng scope/interview trước khi viết `### Lộ trình`.

## Bổ sung sau khi user làm rõ (turn 2)

User: "...và người dùng chỉ cần move nó qua một project ở máy khác là có thể có đủ script
hook, skill, mcp, instruction của bộ workflow này."

→ Chốt: "codex" = danh từ chung, chỉ CHÍNH bộ TDQWorkflow hiện tại (không phải OpenAI Codex
CLI). Mục tiêu: đóng gói toàn bộ script, hook, skill, MCP config, instruction (rule) của
TDQWorkflow vào một thư mục `portable_codex`, sao cho user chỉ cần COPY/MOVE thư mục đó sang
một project khác trên máy khác là dùng được ngay — không phụ thuộc đường dẫn tuyệt đối hiện
tại (`${CLAUDE_PLUGIN_ROOT}`, `/Users/truongdinhquoc/Documents/TDQWorkflow/...` hard-code
trong nhiều skill/script), không phụ thuộc cấu trúc plugin-registered hiện có.

Vẫn cần hỏi thêm (vòng scope): đây là plugin Claude Code chuẩn (dùng `${CLAUDE_PLUGIN_ROOT}`)
hay một bộ file rời copy-paste? Có cần giữ nguyên khả năng chạy độc lập (self-contained,
không cần cài lại MCP server) hay chỉ cần config trỏ đúng? Phạm vi: chỉ PHÂN TÍCH khả thi +
đề xuất kiến trúc, hay làm luôn (build) `portable_codex/`?

## Hiểu & kiến thức

### Khảo sát hiện trạng (2 nhánh sub-agent, 2026-08-17 09:46-09:47)

**Cơ chế đóng gói đã có (KHÔNG cái nào đáp ứng yêu cầu):**
- `portable/` — bản dịch TAY của `skills/tdq-*` sang markdown thuần, cho harness không có
  hook/skill system (Codex, Antigravity). Chỉ instruction; KHÔNG hook, KHÔNG sub-agent,
  KHÔNG `tdq_finish.py`, KHÔNG MCP config. **Không tự sinh** (README ghi rõ "sửa `skills/`
  xong nhớ đồng bộ tay"); test khoá đồng bộ `test_portable_sync.py` đã bị xoá từ 0.10.0 →
  nhiều khả năng đang lệch với bản thật. Ngoại lệ: `portable/workflow/phases.md` tự sinh từ
  `PHASE_TABLE` bằng `tdq_state.py phases-doc`.
- `scripts/claude_export.py` — bundle MÁY sang MÁY (git clone repo + copy `~/.claude` đã lọc
  secret + xuất `config/mcp-servers.json` + `manifest.json` có sha256 từng file). Có sẵn
  `build`/`check` subcommand. Đây là thứ gần nhất về kỹ thuật (đã xử lý MCP + placeholder
  secret + manifest), nhưng đích đến là dựng lại môi trường trên máy mới, không phải thả
  folder vào project.
- Cách dùng ở project khác hiện tại (`docs/notes/user-level-install.md`): phải
  `claude plugin marketplace add /Users/truongdinhquoc/Documents/TDQWorkflow` — trỏ ngược
  về đường dẫn tuyệt đối máy nguồn — cộng dán tay block instruction vào `~/.claude/CLAUDE.md`.

**Phụ thuộc đường dẫn/môi trường — ĐÃ portable sẵn:**
- KHÔNG có dòng hard-code `/Users/truongdinhquoc` nào trong `skills/`, `hooks/`, `scripts/`,
  `agents/` (grep sạch).
- `resolve_project_dir()` (`tdq_state.py:193-215`) ưu tiên `TDQ_PROJECT_DIR` > git root >
  thư mục có state sẵn > cwd; được import dùng chung bởi `tdq_timing`, `token_audit`,
  `tdq_checkstatus`, `tdq_finish`, `skill_inventory`, `hooks/scripts/_common.py`.
  → **state luôn nằm ở project của user, không dính chỗ cài đặt** (đúng thứ portable cần).
- Toàn bộ script **pure stdlib**, không cần `.venv`. `graphify` optional (có
  `shutil.which` + skip graceful); `git` là phụ thuộc ngầm phổ biến.
- Cross-link giữa skill đều tương đối (`../tdq-conventions/SKILL.md`) → copy nguyên cây
  `skills/` vẫn đúng link.
- `hooks/scripts/_common.py:16-19` tự suy `_SCRIPTS_DIR` từ `__file__`, độc lập env var.

**Hai rào cản thật:**
1. `${CLAUDE_PLUGIN_ROOT}` — 17 file dùng (`skills/*/SKILL.md`, `skills/*/references/*.md`,
   `hooks/hooks.json`). Chỉ được set khi thư mục đăng ký làm plugin. Copy folder trần →
   biến rỗng → `python3 "/hooks/scripts/session_start.py"` → **toàn bộ hook gãy**, không có
   fallback trong code. Mã Python KHÔNG đọc biến này (chỉ 1 chỗ ở `tdq_state.py:808` là
   chuỗi in gợi ý lệnh) → sửa thuần cơ học, không phải viết lại logic.
2. MCP `tavily-primary` — `tdq-conventions` (mọi skill đều nạp) quy định bắt buộc cho search
   web. Phụ thuộc môi trường máy đích, không phải phụ thuộc file.

### Xác minh cơ chế project-level của Claude Code (docs chính thức, 2026-08-17 09:49)

| Thành phần | Cách portable | Tự động? |
|---|---|---|
| Hook | `.claude/settings.json` dùng `${CLAUDE_PROJECT_DIR}` | Có — SAU KHI user bấm trust |
| Skill | `.claude/skills/<tên>/SKILL.md` | Có, live-reload khi sửa |
| Sub-agent | `.claude/agents/*.md` | Có (restart nếu thư mục mới tinh) |
| MCP | `.mcp.json` root project | Đọc tự động, **approve từng server** |

- `${CLAUDE_PROJECT_DIR}` là biến thay thế đúng cho `${CLAUDE_PLUGIN_ROOT}` ở project-level;
  có ví dụ chính thức trong docs hooks (`"command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/..."`).
- Ba giới hạn KHÔNG tự động hoá được: (a) trust dialog lần đầu, bắt buộc, không bypass;
  (b) MCP approve từng server — `enableAllProjectMcpServers` **bị bỏ qua khi chưa trust**;
  (c) restart nếu `.claude/skills/` hoặc `.claude/agents/` là thư mục hoàn toàn mới.
- `.mcp.json` project-scope: biến `${VAR}` cần default kiểu `${CLAUDE_PROJECT_DIR:-.}`, khác
  plugin (Claude Code tự thay `${CLAUDE_PLUGIN_ROOT}` không cần default).
- `extraKnownMarketplaces`/`enabledPlugins` trong settings chỉ ENABLE plugin đã cài, không
  tự tải/cài → không dùng được cho kịch bản "chỉ copy folder".

## Hỏi đáp

- Q: "codex" là OpenAI Codex CLI hay danh từ chung? → A: danh từ chung, chỉ chính bộ
  TDQWorkflow này.
- Q: Phạm vi phân tích hay build? → A (turn 4): **C** — phân tích + build `portable_codex/`
  + script tự sinh `build_portable.py` để không lặp vết xe đổ của `portable/`.
- Q (turn 4, user thêm): muốn có skill `tdq-checkportable` trong bản portable; instruction
  mặc định sẽ chạy skill đó để check manifest + tương thích của script; thiếu lib hay thiếu
  bất cứ thứ gì thì agent **được quyền tự setup**.

### Vòng chốt scope (turn 5) — user trả lời 1A 2C 3B 4A

- **1A — Lane:** chuyển chế độ chuyên sâu (deep). Đã `init ... full` + `set phase=analyze`.
- **2C — Target: CẢ HAI harness, hai thư mục riêng ở root repo:**
  - `portable_claude/` — bản Claude Code đầy đủ: `.claude/skills/`, `.claude/agents/`,
    `.claude/settings.json` (hook dùng `${CLAUDE_PROJECT_DIR}`), `.mcp.json`, `scripts/`.
  - `portable_codex/` — bản cho harness không có skill/hook system (Codex CLI,
    Antigravity…): markdown thuần kiểu `portable/` hiện tại + `scripts/` mang theo.
  - Cả hai sinh từ CÙNG một nguồn (`skills/`, `hooks/`, `agents/`, `scripts/`) bằng
    `scripts/build_portable.py` → hết cảnh đồng bộ tay như `portable/` cũ.
- **3B — Quyền tự setup: TỐI ĐA.** `tdq-checkportable` được tự cài package, tự sửa cả config
  user-level (`~/.claude`), tự tạo thứ còn thiếu; làm xong BÁO LẠI đầy đủ, không hỏi trước.
  Ghi chú kỹ thuật (không trái ý user, chỉ là cách làm an toàn của cùng quyết định đó):
  mọi hành vi ghi ra ngoài project phải (a) log đủ chi tiết theo luật log service, (b) backup
  file user-level trước khi sửa, (c) không bao giờ in/copy giá trị secret ra log hay report.
- **4A — Manifest đầy đủ:** danh sách file + sha256 · version bộ · phiên bản Python tối thiểu ·
  lệnh ngoài cần có (`git`, `graphify`) · danh sách MCP server cần có.

### Ba giới hạn cứng vẫn còn (không code nào vượt được — phải nêu trong README bản portable)

1. Trust dialog lần đầu — user phải bấm, không bypass được.
2. MCP approve từng server — `enableAllProjectMcpServers` bị bỏ qua khi chưa trust.
3. Restart Claude Code nếu `.claude/skills/` hay `.claude/agents/` là thư mục hoàn toàn mới.

→ `tdq-checkportable` không vượt được 3 thứ này, nhưng PHẢI phát hiện và in hướng dẫn chính
xác cho user (đây là lý do skill này tồn tại).

### Lộ trình

1. `scripts/build_portable.py` — sinh cả hai thư mục từ nguồn duy nhất; gồm bước rewrite
   `${CLAUDE_PLUGIN_ROOT}` → `${CLAUDE_PROJECT_DIR}` cho bản claude, và bước sinh
   `manifest.json` (sha256 + version + yêu cầu môi trường) cho cả hai.
2. `portable_claude/` — cấu trúc `.claude/` đầy đủ + `.mcp.json` + `scripts/` + README nêu
   3 giới hạn cứng.
3. `portable_codex/` — markdown thuần (kế thừa cách làm `portable/` cũ nhưng TỰ SINH) +
   `scripts/` + `AGENTS.md` + README.
4. Skill `tdq-checkportable` (có trong cả hai bản, dạng phù hợp từng harness) — đọc
   `manifest.json`, kiểm toàn vẹn file + tương thích môi trường, tự vá thứ vá được, in báo
   cáo thứ không vá được.
5. Instruction mặc định của cả hai bản portable → chạy `tdq-checkportable` đầu tiên.
6. Test: unit test cho `build_portable.py` (sinh đúng cấu trúc, rewrite đúng biến, manifest
   khớp sha256) + test cho bộ kiểm của `tdq-checkportable` (phát hiện file thiếu/sai hash,
   phát hiện thiếu lệnh ngoài).
7. Quyết định số phận `portable/` cũ: thay bằng `portable_codex/` tự sinh (xoá thư mục viết
   tay) — cần chốt trong spec.

### Kiểm cổng

- Biết đủ để viết spec? CÓ — đã rõ target, kiến trúc, ranh giới quyền, nội dung manifest.
- Còn chỗ nào phải đoán? Một chỗ: có xoá `portable/` cũ không → đưa thành mục quyết định
  trong spec để user chốt lúc duyệt.
- Rủi ro lớn nhất? Bản sinh ra gãy im lặng ở máy người khác → DoD phải có phép kiểm chạy
  thật trên thư mục tạm, không chỉ kiểm bằng mắt.
