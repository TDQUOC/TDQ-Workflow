# BRIEF — Bản portable_codex dùng đúng cơ chế native của Codex CLI
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> tại sao portable của codex không thấy hook cũng như skill,mcp,....

Sau khi tôi trình bày hiện trạng + 4 phương án, user chọn:

> A

Tức phương án A: mở request mới nâng bản `portable_codex/` lên đúng năng lực Codex CLI —
`.codex/config.toml` (MCP), `.agents/skills/` (skill tự nạp), `hooks.json` cho phần hook
bắt được, giữ `workflow/*.md` làm bản dự phòng cho harness khác.

### Cách hiểu đầu tiên

**Mục tiêu.** Sửa một giả định sai đã đóng băng vào `scripts/build_portable.py` ở request
trước (`2026-08-17-0938-portable-codex`): docstring hiện ghi `portable_codex/ — cho harness
không có skill/hook system (Codex CLI, Antigravity…)`. Giả định đó đúng với Codex CLI đời cũ,
không còn đúng với bản hiện tại. Hệ quả: bản codex chỉ có `AGENTS.md` + `workflow/NN-*.md` +
`scripts/`, thiếu hẳn cấu hình MCP và hook, còn skill thì bị hạ cấp thành markdown đọc tay
thay vì để harness tự nạp.

**Phạm vi đoán.**
- Sửa `sinh_ban_codex()` trong `scripts/build_portable.py` để phát sinh thêm các lớp native.
- Sửa `README_CODEX` / `AGENTS_MD` cho khớp năng lực thật.
- Mở rộng `manifest.json` bản codex (file mới phải nằm trong manifest, nếu không `setup`
  sẽ coi là file lạ — xem `tests/test_checkportable.py::test_setup_khong_them_file_la`).
- Test mới trong `tests/test_build_portable.py`.
- KHÔNG đụng `portable_claude/` (đang đúng và đã QC 3 vòng).

**Chỗ chưa rõ (phải chốt ở phase analyze).**
1. Phiên bản Codex CLI làm mốc tương thích — hook mới có từ `rust-v0.114.0` và còn nằm sau
   feature flag `[features].codex_hooks = true`. Sinh `hooks.json` cho người dùng bản cũ hơn
   thì file đó vô hại hay gây lỗi khởi động?
2. Hook Codex giới hạn nặng: chỉ bắt sự kiện tool shell/Bash, chỉ trả `deny` được. Bộ TDQ có
   5 hook; ánh xạ được bao nhiêu, và phần không ánh xạ được thì nói thật thế nào trong README
   thay vì để người dùng tưởng cổng duyệt vẫn được máy canh.
3. Hook Codex không có biến môi trường tương đương `CLAUDE_PROJECT_DIR`; context tới qua stdin
   JSON có trường `cwd`. `hooks/scripts/_common.py` hiện suy đường dẫn kiểu Claude Code →
   cần lớp chuyển đổi hay phải viết wrapper riêng?
4. Skill Codex nạp từ `.agents/skills/<tên>/SKILL.md` (frontmatter `name`/`description`).
   Chép thẳng `skills/` sang có làm phình context mỗi phiên không, và có nên giữ song song
   `workflow/NN-*.md` (nhân đôi nội dung → nhân đôi chỗ lệch) hay bỏ hẳn?
5. `projects.<path>.trust_level` — project `untrusted` thì Codex bỏ qua lớp `.codex/` cấp
   project. Người dùng phải làm gì thủ công, và `tdq-checkportable` có kiểm được không?
6. Toàn bộ hiểu biết trên đến từ một lượt search; cần xác minh lại bằng nguồn chính thức
   trước khi viết spec (bài học của chính request này: giả định không kiểm chứng lọt qua cả
   3 vòng QC vì QC chỉ kiểm bản sinh có khớp spec, không kiểm spec có khớp thực tế).

## Hiểu & kiến thức

### Năng lực dùng được

| Năng lực | Nguồn | Phán quyết | Vì sao |
|---|---|---|---|
| `tdq-conventions` | plugin:tdq-workflow | DÙNG | luật gốc, mọi skill khác nạp trước |
| `tdq-intake` | plugin:tdq-workflow | ĐANG DÙNG | chính skill của phase này |
| `tdq-spec` / `tdq-plan` / `tdq-build` | plugin:tdq-workflow | DÙNG | lane deep chạy đủ ba cổng |
| `tdq-status` | plugin:tdq-workflow | BỎ | user chưa hỏi trạng thái |
| `tavily-primary` (MCP search) | plugin ngoài | DÙNG | phải xác minh tài liệu Codex CLI |
| `WebFetch` | built-in | DÙNG | đọc thẳng file docs trong repo openai/codex |
| agent `general-purpose` | built-in | DÙNG | gánh research, kết quả tavily thô quá tốn context |
| agent `tdq-qc-tester` | plugin:tdq-workflow | DÙNG | QC độc lập — bài học request trước |
| `graphify` | CLI ngoài | BỎ | thay đổi khu trú trong 1 file `build_portable.py`, không phải câu hỏi liên kết |

### Đọc code — hiện trạng đã xác minh

- `scripts/build_portable.py:353` `sinh_ban_codex()` — docstring ghi thẳng giả định sai:
  *"markdown thuần cho harness không có skill/hook system"* và *"Không mang `hooks/`: hook là
  cơ chế riêng của Claude Code"*. Bản codex hiện chỉ sinh: `scripts/` (copy_loc với
  `moi = "."`), `workflow/NN-<tên>.md` (8 skill theo `THU_TU_SKILL`), `workflow/references/`,
  `workflow/phases.md`, `AGENTS.md`, `README.md`, `manifest.json` — tổng 68 file.
- `hooks/hooks.json` — bộ TDQ có 5 hook: `SessionStart` (session_start.py),
  `UserPromptSubmit` (prompt_context.py), `PreToolUse` matcher `Edit|Write|MultiEdit|NotebookEdit`
  (edit_gate.py), `PreToolUse` matcher `Bash` (bash_gate.py), `Stop` (stop_gate.py).
- `hooks/scripts/_common.py:17` suy `scripts/` bằng `../../scripts` tính từ `__file__` →
  `hooks/` và `scripts/` bắt buộc nằm cạnh nhau. Bản codex hiện đặt `scripts/` ở gốc bundle,
  nên muốn thêm hook thì `hooks/` cũng phải ở gốc bundle (không lồng trong `.codex/`).
- Ràng buộc test đã có: `tests/test_checkportable.py::TestVongFix2::test_setup_khong_them_file_la`
  khoá việc `setup` không được thêm file ngoài manifest → mọi file native mới BẮT BUỘC vào
  `manifest.json` của bản codex.
- `docs/kien-truc.md` §Luật gọi: file code mới phải nằm trong `scripts/` hoặc `hooks/`.
  Hồ sơ này vẫn ở trạng thái **NHÁP — chờ user chốt**; dòng "Luật bản ngoài | `portable/`"
  đã lỗi thời vì `portable/` bị xoá ở request trước, cần sửa thành `portable_claude/` +
  `portable_codex/` (việc phụ, gộp vào request này).

### Sự thật về Codex CLI — đã xác minh

Nguồn đầy đủ + mức chắc chắn: `docs/tdq/research/2026-08-17-1139-codex-native-layers.md`.
Hai vòng: vòng 1 qua docs chính thức (learn.chatgpt.com, redirect 308 từ developers.openai.com),
vòng 2 đọc THẲNG source `openai/codex` nhánh main để chốt phần hook.

- **Hook — CAO, đọc từ source `codex-rs/hooks/src/schema.rs` + `core/src/hook_runtime.rs`.**
  Đã merge vào main từ trước 2026-02-10, có trong bản stable `rust-v0.147.0`.
  **KHÔNG có feature flag** `[features] hooks`/`codex_hooks` (claim cũ bị source bác bỏ);
  bật/tắt theo từng hook qua `[hooks.state].<key>.enabled`.
  10 event: `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PreCompact`, `PostCompact`,
  `SessionStart`, `UserPromptSubmit`, `SubagentStart`, `SubagentStop`, `Stop`.
  Cấu hình: `~/.codex/hooks.json` (user) và `<repo>/.codex/hooks.json` (project, cần trusted);
  cấu trúc `MatcherGroup { matcher, hooks }`, handler `Command { command, timeout_sec, … }`.
  Input: **JSON qua stdin**, có `cwd`, `hook_event_name`, `tool_name`, `tool_input`,
  `transcript_path`, `session_id`, `permission_mode`.
  Output: `hookSpecificOutput.permissionDecision` = `allow|deny|ask`, và `decision` =
  `approve|block`. **Áp cho MỌI tool**, không giới hạn shell/bash.
- **Hệ quả lớn:** giao thức hook của Codex TRÙNG với giao thức Claude Code mà
  `hooks/scripts/_common.py` đang dùng (`hookSpecificOutput`/`permissionDecision`/
  `additionalContext`/`decision: block`), và cả 5 hook TDQ đều có event tương ứng:
  `SessionStart` → SessionStart · `UserPromptSubmit` → UserPromptSubmit ·
  `edit_gate` → PreToolUse (matcher tool sửa file) · `bash_gate` → PreToolUse (matcher shell) ·
  `stop_gate` → Stop. Tức bản codex có thể mang **đủ cổng canh bằng máy**, không phải
  markdown suông như hiện nay.
- **MCP — CAO.** `[mcp_servers.<tên>]`; stdio (`command`/`args`/`env`/`env_vars`/`cwd`),
  HTTP (`url`/`bearer_token_env_var`/`http_headers`/`env_http_headers`).
  `.codex/config.toml` cấp project CÓ được nạp.
- **Skill — CAO.** `.agents/skills/<tên>/SKILL.md`, quét từ cwd lên repo root; frontmatter tối
  thiểu `name` + `description`; progressive disclosure như Claude Code (không phình context).
  Ưu tiên cấp PROJECT: có báo lỗi cộng đồng rằng `~/.agents/skills` không luôn được nạp.
- **AGENTS.md — CAO.** Project root + `~/.codex/AGENTS.md`; `project_doc_max_bytes` mặc định
  32 KiB.
- **TRUST — CAO, và đây là ràng buộc nặng nhất.** `[projects."<path>"].trust_level` trong
  `~/.codex/config.toml`. Project `untrusted` → Codex **bỏ qua toàn bộ lớp `.codex/` cấp
  project: config, hooks, rules**. Nghĩa là MCP và hook của bản portable chỉ sống khi user
  đánh dấu project trusted, và **không tìm thấy lệnh CLI nào làm việc đó** (mức THẤP cho
  việc "chắc chắn không có") → nhiều khả năng phải sửa tay `~/.codex/config.toml`.
- **Mốc tương thích đề xuất: Codex CLI >= 0.147.0** (stable 2026-08-07).

### Rủi ro kỹ thuật còn mở (giải ở phase implement, không phải chỗ đoán)

1. `hooks.json` của Codex có nở biến môi trường trong chuỗi `command` không — chưa xác minh.
   Bản codex không có `CLAUDE_PLUGIN_ROOT`/`CLAUDE_PROJECT_DIR`, nên đường dẫn tới hook script
   phải là tương đối và phụ thuộc Codex chạy hook với cwd nào. Phải kiểm bằng chạy thật.
2. Tên wire cho event `SessionEnd` không có trong enum (runtime lại có `run_session_end_hooks`)
   — bộ TDQ không dùng event này nên không chặn, chỉ ghi lại.
3. Skill `.agents/skills` đặt ở cấp project ổn hơn user-level, nhưng độ ổn định qua các version
   chưa chắc chắn 100%.

_(vòng scope + interview: xem mục `## Hỏi đáp`)_

## Hỏi đáp

### Vòng scope — BỎ, có lý do

Research đã thu hẹp phạm vi đủ chặt: chỉ đụng đúng một hàm `sinh_ban_codex()` + tài liệu đi
kèm, không đụng `portable_claude/`, không đụng `skills/`/`hooks/` nguồn. Bối cảnh bằng số đã
biết: 5 hook, 8 skill, 2 MCP server, 68 file trong bản codex hiện tại. Không còn "mặt" nào để
user phải chọn ở mức tổng quát, nên đi thẳng vòng chi tiết.

### Vòng 1 — câu hỏi chi tiết (hỏi 11:55, user trả lời 11:58: `1a 2a 3b 4a`)

- **Q1. Phạm vi lớp native:** làm cả ba (skill `.agents/skills/` + MCP `.codex/config.toml` +
  hook `.codex/hooks.json`), hay bớt lớp nào?
- **Q2. Hook script:** dùng lại nguyên `hooks/scripts/*.py` (giao thức trùng Claude Code), hay
  viết lớp adapter riêng cho Codex?
- **Q3. Trust level:** `tdq-checkportable` có được tự ghi `[projects."<path>"] trust_level =
  "trusted"` vào `~/.codex/config.toml` của user không? (Đây là ghi ra cấu hình MỨC NGƯỜI DÙNG,
  ngoài bundle — cùng loại quyền với quyết định 3B của request trước, mà request trước đã KHÔNG
  thực hiện.)
- **Q4. `workflow/NN-*.md`:** giữ song song với `.agents/skills/` (an toàn cho harness khác,
  nhưng nhân đôi nội dung → nhân đôi chỗ có thể lệch), hay bỏ hẳn?
- **Q5. Kiểm chứng thật:** ~~máy có cài Codex CLI không?~~ Không phải hỏi — đã kiểm bằng máy:
  `/Applications/ChatGPT.app/Contents/Resources/codex`, `codex-cli 0.147.0-alpha.6.5`.

### Trả lời của user (nguyên văn: `1a 2a 3b 4a`)

- **A1 = A.** Làm cả ba lớp native: skill `.agents/skills/`, MCP `.codex/config.toml`,
  hook `.codex/hooks.json`.
- **A2 = A.** Dùng lại nguyên `hooks/scripts/*.py`, không viết adapter — giao thức đã trùng,
  thêm một lớp nữa chỉ tạo thêm chỗ lệch.
- **A3 = B.** `setup` **được tự ghi** `[projects."<path>"] trust_level = "trusted"` vào
  `~/.codex/config.toml`, bắt buộc sao lưu `<file>.tdq-bak-<timestamp>` trước khi ghi.
  **Ràng buộc rút từ request trước:** lần đó quyền tương tự được duyệt nhưng mã không hề chạm
  tới `~`, và tôi đã đi thu hẹp lời hứa trong tài liệu thay vì viết mã. Lần này việc ghi phải
  là mã CHẠY THẬT, có test khoá, nếu không thì không được viết vào tài liệu.
- **A4 = A.** Giữ song song `workflow/NN-*.md`. Không sợ lệch vì cả hai đều sinh từ `skills/`
  trong cùng một lần chạy `build_portable.py`.

### Kiểm cổng (analyze → spec)

- **Phạm vi cuối đã rõ chưa?** Rõ. Sửa `sinh_ban_codex()` để sinh thêm 4 nhóm hiện vật:
  `.agents/skills/<tên>/SKILL.md` (8 skill), `.codex/config.toml` (MCP + trỏ hook),
  `.codex/hooks.json` (5 hook), và cây `hooks/` + `scripts/` cạnh nhau ở gốc bundle
  (ràng buộc `../../scripts` của `_common.py`). Thêm lệnh `setup --trust`. Cập nhật
  `AGENTS.md`/`README_CODEX`/docstring cho hết giả định sai. Sửa `docs/kien-truc.md`.
- **Cần model/download/cài đặt gì không?** Không. Codex CLI đã có sẵn trên máy (0.147.0-alpha.6.5),
  Python thuần stdlib, không thêm gói.
- **Phạm vi QC/test đã có chưa?** Có. Test cấu trúc trong `tests/test_build_portable.py` +
  `tests/test_checkportable.py`, cộng một mức kiểm mới mà request trước không có: **chạy thật
  `codex` trên bản sinh** để chứng minh Codex nạp được skill/MCP/hook, thay vì chỉ chứng minh
  file đúng khuôn.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Research thêm | BỎ | 2 vòng xong, phần hook đã chốt bằng source; 3 rủi ro còn lại là loại phải chạy thử mới biết, không phải loại đọc thêm tài liệu |
| Spec + plan | CÓ | khung bất biến |
| Implement | CÓ | khung bất biến |
| Chạy thật `codex` trên bản sinh | CÓ | bài học request trước: QC chỉ đối chiếu bản sinh với spec, không bắt được spec sai. Chỉ chạy thật mới bắt được |
| QC độc lập bằng agent `tdq-qc-tester` | CÓ | request trước QC 3 vòng bắt 10 khuyết tật — tỷ lệ quá cao để bỏ |
| Review sâu spec/plan bằng `tdq-reviewer` | BỎ | user chưa yêu cầu; đổi khu trú trong 1 file mã |
| Chia subagent | Chốt ở cổng mode | phần lớn thay đổi dồn vào `build_portable.py` + `tdq_checkportable.py`, nghiêng về `main` |
| Report | CÓ | khung bất biến |
