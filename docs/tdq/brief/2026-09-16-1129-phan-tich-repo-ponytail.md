# Brief — Phân tích repo Ponytail
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-09-16 · Slug: `2026-09-16-1129-phan-tich-repo-ponytail` · Lane: (chờ người dùng chọn)

## Nguyên văn

> hi hãy check xem bạn có thấy repo ponytail ở document folder không?

> yup tôi muốn mở reqeust phân tích tính năng cảu repo ponytail đó và cách thức nó hoạt động
> và report lại cho tôi

**Đọc lần đầu**

- **Mục tiêu:** hiểu repo `/Users/tdq/Documents/ponytail` làm được gì (tính năng) và hoạt động
  bằng cơ chế nào (luồng chạy, điểm móc vào agent), rồi trả về một report cho người dùng đọc.
- **Đầu ra dự kiến:** tài liệu phân tích + report trong chat. KHÔNG sửa code của Ponytail.
- **Phạm vi đoán:** đọc hiểu repo bên thứ ba, 166 file tracked (57 `.md`, 45 `.js`, 20 `.json`,
  6 `.py`, 6 `.toml`), `package.json` là `@dietrichgebert/ponytail` v4.10.0, entry
  `./.opencode/plugins/ponytail.mjs`. Repo mang cấu hình cho rất nhiều agent khác nhau
  (`.claude-plugin`, `.codex-plugin`, `.cursor`, `.windsurf`, `.opencode`, `.kiro`, `.grok-plugin`,
  `.devin-plugin`, `.qoder`, `.clinerules`, `.openclaw`, `gemini-extension.json`) cộng `hooks/`,
  `commands/`, `benchmarks/`, `examples/`, `ponytail-mcp`.
**Lớp tìm kiếm (bước 1b)**

- `tdq_lsp.py check`: 6/7 bậc ĐẠT · bậc 7 (cấu hình gốc import theo ngôn ngữ) THIẾU — Python
  không có `pyrightconfig.json`/`pyproject.toml`/`setup.py`/`setup.cfg`. Repo này là của bên thứ
  ba và gần như toàn bộ là JS, nên tôi KHÔNG tạo file cấu hình nào ở đây.
- **Kiểm hiệu ứng LSP: FAIL.** Ký hiệu `getPonytailInstructions`
  (định nghĩa `hooks/ponytail-instructions.js:77`, được gọi từ nhiều file):
  `mcp__lsp__find_references` = **0 file** (lỗi `file path … is outside workspace root
  "/Users/tdq/Documents/ForAgentCode/TDQ-Workflow"`, vẫn lỗi sau khi
  `add_workspace_folder /Users/tdq/Documents/ponytail` báo thêm thành công) ·
  `grep -rln --include="*.js" --include="*.mjs"` = **7 file** (`.opencode/plugins/ponytail.mjs`,
  `hooks/ponytail-activate.js`, `hooks/ponytail-instructions.js`,
  `hooks/ponytail-mode-tracker.js`, `hooks/ponytail-subagent.js`, `pi-extension/index.js`,
  `ponytail-mcp/instructions.js`). 0 < 7 → **dùng grep cho toàn bộ request này**; LSP index chỉ
  neo ở repo TDQ-Workflow nên không trả lời được repo Ponytail.

- **Chỗ chưa rõ (chờ hỏi người dùng):**
  1. Report sâu tới đâu: tổng quan tính năng, hay soi từng hook/luồng chạy kèm sơ đồ?
  2. Người đọc report là ai (chỉ bạn, hay chia sẻ cho người khác)?
  3. Có cần so sánh Ponytail với TDQ-Workflow của bạn, hay chỉ mô tả Ponytail?
  4. Nơi lưu tài liệu TDQ: hiện đang ghi vào `docs/tdq/` NGAY TRONG repo Ponytail (repo bên thứ
     ba, nhánh `main` sạch). Tôi không commit vào repo của người khác; nếu bạn muốn, chuyển sang
     chỗ khác.

## Hiểu & kiến thức

### Vòng scope

Dấu hiệu 1 khớp (yêu cầu trỏ vào cả một hệ thống, không phải một hành vi) → vòng scope đã chạy.
Người dùng trả lời: `1abcd 2b 3b 4a`.

### Phạm vi đã chốt

- **Mặt CHỌN:** A bộ luật & 5 mode · B kiến trúc đa host · C chất lượng & rủi ro kỹ thuật ·
  D repo tự khai vs nhà cung cấp xác nhận — cả bốn, cộng phần so rộng với TDQ-Workflow trên cả
  vòng đời request (câu 3 = B).
- **Mặt LOẠI:** không viết lại tài liệu hướng dẫn cài đặt từng host (repo đã có
  `docs/agent-portability.md`); không đề xuất bản vá cho Ponytail; không đụng một dòng code nào
  của repo bên thứ ba.
- **Bối cảnh:** người đọc là bạn + đồng đội **chưa biết Ponytail là gì** (câu 2 = B) → tài liệu
  phải tự đứng được, mở đầu bằng phần giới thiệu, không giả định người đọc đã đọc repo. Tài liệu
  TDQ của request này đã chuyển về TDQ-Workflow (câu 4 = A), repo Ponytail trả về sạch.
- **Mức đầu tư suy ra:** vừa-cao — 4 mặt + phần nhập môn + phần so sánh rộng, ước tính một tài
  liệu ~6 phần đọc trong 20–25 phút; không phải sách trắng, cũng không phải ghi chú vắn tắt.

### B0 — kiểm kê năng lực (CHẠY, vì repo này không có report tiền lệ)

| Năng lực | Phán quyết | Vì sao |
|---|---|---|
| `mcp__lsp__*` | KHÔNG DÙNG ĐƯỢC | workspace root chốt ở TDQ-Workflow; `add_workspace_folder` báo thêm thành công nhưng mọi request vẫn bị chặn (kiểm hiệu ứng ở mục 1) |
| Read + grep | DÙNG — lớp chính | hệ quả trực tiếp của dòng trên |
| tavily qua sub-agent | ĐÃ DÙNG cho B2 | cơ chế móc của ~20 host là kiến thức ngoài repo |
| graphify | KHÔNG DÙNG | graph chỉ chứa `scripts/` + `hooks/` của TDQ-Workflow, không có Ponytail |
| lumen | ĐÃ THỬ, GIÁ TRỊ THẤP cho request này | `index_status` trước khi gọi: `Files: 0 · Chunks: 0 · Last indexed: never · Stale: yes`. `semantic_search` tự index nền và trả 8 kết quả kèm cảnh báo "index đang cập nhật, dùng grep/glob cho tới khi xong"; kết quả trỏ vào `README.md`, `__init__.py`, `benchmarks/`, KHÔNG trỏ vào `hooks/*.js` là đúng chỗ cần. Vậy lớp mơ hồ không thay thế được Read/grep ở đây. Một kết quả vẫn có ích: `__init__.py:105 build_injected_context` — plugin Hermes |

### B1 — đọc code (LUÔN chạy)

Kiến trúc: **một nguồn chân lý + nhiều adapter mỏng** (repo tự gọi tên trong
`docs/agent-portability.md`: "Keep adapters thin").

1. **Nguồn chân lý:** `skills/ponytail/SKILL.md` — bộ luật "lazy senior dev": thang 7 bậc
   (YAGNI → đã có trong repo → stdlib → tính năng nền tảng → dependency đã cài → một dòng →
   tối thiểu chạy được), mục `Rules`, `Output`, bảng `Intensity` 3 mức, mục `When NOT to be lazy`.
2. **Bộ dựng chỉ dẫn:** `hooks/ponytail-instructions.js` — `filterSkillBodyForMode()` lọc chính
   file SKILL.md theo level: chỉ bỏ dòng bảng `| **lite** |` và dòng ví dụ `- lite: "..."` không
   khớp mode; dòng luật thường có nhãn trùng tên mode được giữ nguyên (có chú thích giải thích
   đúng cái bẫy này). Đọc file lỗi → `getFallbackInstructions()` trả bản luật cứng nhúng trong JS.
   Mode `review` nằm trong `INDEPENDENT_MODES`: không bơm luật, chỉ trả một dòng trỏ sang skill.
3. **Phân giải mode:** `hooks/ponytail-config.js` — thứ tự env `PONYTAIL_DEFAULT_MODE` →
   `config.json` (XDG / `~/.config/ponytail` / `%APPDATA%`) → `'full'`. `VALID_MODES` 5 mức
   (`off/lite/full/ultra/review`) nhưng `RUNTIME_MODES` 4 mức: `review` không được làm default
   (ghi rõ #377). Có `isDeactivationCommand()` khớp NGUYÊN câu "stop ponytail"/"normal mode"
   (từng khớp giữa câu nên tắt oan) và `isShellSafe()` allowlist đường dẫn trước khi nhúng vào
   lệnh statusline.
4. **Nhận dạng host + khuôn output:** `hooks/ponytail-runtime.js` — dò host bằng biến môi trường
   (`COPILOT_PLUGIN_DATA`/`CLAUDE_PLUGIN_ROOT` chứa `.vscode`+`agent-plugins`, `PLUGIN_DATA`,
   `QODER_SESSION_ID`, `CURSOR_VERSION`), đổi cả **thư mục state** (`~/.claude`, `PLUGIN_DATA`,
   `~/.qoder`, `~/.cursor`) và **khuôn JSON stdout** trong `writeHookOutput()`: Copilot
   `{additionalContext}`, Codex `{systemMessage, hookSpecificOutput}`, Qoder `{hookSpecificOutput}`,
   Cursor `{additional_context, continue}`, Claude gốc in stdout thô trừ `SubagentStart` phải bọc JSON.
5. **Ba hook vòng đời** — cùng đọc một bộ luật, khác điểm móc:
   - `ponytail-activate.js` (SessionStart): ghi cờ `.ponytail-active`, bơm luật, và nhắc cài
     statusline đúng MỘT lần (cờ `.ponytail-statusline-nudged`).
   - `ponytail-mode-tracker.js` (UserPromptSubmit): bắt `/ponytail <level>`, `/ponytail default
     <level>` (ghi xuống config), `/ponytail-review`, và câu tắt; với Qoder thì kiêm luôn việc
     SessionStart vì Qoder không có event đó.
   - `ponytail-subagent.js` (SubagentStart): context SessionStart không tới sub-agent (#252) nên
     bơm lại; `PONYTAIL_SUBAGENT_MATCHER` lọc theo `agent_type`, mọi trường hợp mơ hồ đều
     **fail open** (vẫn bơm).
6. **Bề mặt người dùng:** 6 skill (`ponytail`, `-review`, `-audit`, `-debt`, `-gain`, `-help`) và
   6 lệnh `commands/*.toml` cùng tên. `ponytail-debt` thu hoạch các chú thích `ponytail:` — chính
   quy ước mà bộ luật bắt buộc khi cắt góc — thành một sổ nợ.
7. **Hợp đồng chung của mọi hook: không bao giờ được treo hay làm hỏng session.** Mọi `try/catch`
   đều fail im lặng, và hook nào đọc stdin cũng có `setTimeout(...,1000).unref()` + handler
   `error` vì trên Windows lớp bọc PowerShell có thể ăn mất JSON khiến `end` không bao giờ nổ (#443).
8. **Kiểm thử — đã CHẠY THẬT trên máy này (2026-09-16), không phải đọc suông:**
   `npm test` → **95 test, 94 pass, 1 fail**. Test đỏ duy nhất là
   `tests/correctness.test.js:77 "csv: correct pandas one-liner passes"`. **Nguyên nhân là
   khoảng trống môi trường, KHÔNG phải lỗi repo:** test này *thực thi thật* đoạn
   `import pandas as pd` rồi so kết quả, mà máy này `ModuleNotFoundError: No module named
   'pandas'`. Đây là loại test phụ thuộc runtime ngoài, sẽ đỏ trên mọi máy không có pandas.
   `npm test` nối bằng `&&` nên lần fail đó **ngắt luôn** hai bộ con; chạy riêng thì
   `pi-extension` **23/23 pass**, `ponytail-mcp` **3/3 pass**.
   16 file trong `tests/` phần lớn là test *đóng gói* (mỗi nền tảng một file: `cursor-hooks`,
   `qoder-plugin`, `gemini-extension`, `grok-plugin`, `copilot-plugin`, `hermes-plugin`,
   `openclaw-skills`, `opencode-plugin`, `package*`), cộng `behavior`/`correctness`/`hooks`/
   `hooks-windows`. `scripts/check-rule-copies.js` canh **7 bản sao rule** (`.cursor/rules/
   ponytail.mdc`, `.windsurf/`, `.clinerules/`, `.agents/`, `.qoder/`, `.github/copilot-
   instructions.md`, `.kiro/steering/`) so byte với `AGENTS.md`, cộng **9 "invariant"** phải có
   mặt verbatim trong cả SKILL.md và AGENTS.md — tự nhận là "canary, not full equality".

9. **Phát hiện đáng giá nhất: adapter Hermes KHÔNG mỏng — nó phá chính luật của repo.**
   `docs/agent-portability.md` có "Adapter Rule: Keep adapters thin", và mọi adapter JS đều giữ
   đúng: `pi-extension/index.js`, `ponytail-mcp/instructions.js`,
   `.opencode/plugins/ponytail.mjs` đều `require('../hooks/ponytail-instructions.js')` — một
   nguồn duy nhất (bản mjs/ESM phải bắc cầu qua `createRequire`). Nhưng `__init__.py` (218 dòng,
   plugin Hermes, cặp với `plugin.yaml`) **viết lại toàn bộ builder bằng Python**: `DEFAULT_MODE`,
   `RUNTIME_MODES`, `_config_dir()`, `_default_mode()`, `_strip_frontmatter()`,
   `_filter_skill_body_for_mode()`, `_fallback_instructions()` — bản sao thứ hai của logic.
   Lý do kỹ thuật thì chính đáng (Python không `require` được CJS), nhưng cái giá là hai bản
   phải tự đồng bộ bằng tay.

10. **Và bản sao đó ĐÃ lệch — hiện còn TIỀM ẨN, không có hàng rào nào chặn:**
    - *Regex ví dụ:* JS dùng `^-\s*([^:]+):\s*"` — **bắt buộc dấu ngoặc kép**, kèm comment dài
      giải thích vì sao, và `pi-extension` có hẳn một test tên *"filterSkillBodyForMode does not
      drop a rule bullet whose label matches a mode name"*. Python dùng `^-\s*([^:]+):\s*`,
      **bỏ yêu cầu ngoặc kép**, và không có test tương ứng. Hiện `SKILL.md:86-88` đều có ngoặc
      kép nên hai bản lọc ra kết quả giống nhau → lệch chưa bật. Nhưng thêm một bullet thường
      dạng `- Full: ...` là Python âm thầm xoá nó ở mọi mode khác, JS thì giữ — đúng cái tình
      huống comment bên JS dựng ra để chặn.
    - *Mode `review`:* JS coi `review` là `INDEPENDENT_MODES` và chỉ trả **một dòng** trỏ sang
      skill; Python đọc thẳng `skills/ponytail-review/SKILL.md` rồi bơm **cả thân**. Cùng tên
      mode, hai hành vi khác nhau. Có test bên Python (`hermes-plugin.test.js:152`) nên đây là
      **cố ý**, nhưng không tài liệu nào ghi sự khác biệt này.
    - *Không có hàng rào:* `check-rule-copies.js` **không canh `__init__.py`**, và
      `tests/hermes-plugin.test.js` kiểm Python **độc lập** — không hề so kết quả với bản JS.
      Nghĩa là không tồn tại test tương đương Python↔JS nào.

11. **Mode được lưu ở ba tầng với ba PHẠM VI khác nhau — dễ gây ngộ nhận:**
    - Hermes: `_current_mode` là **biến toàn cục của process**, còn `_pre_llm_call` nhận
      `session_id` rồi **bỏ qua** → trong một gateway nhiều phiên, `/ponytail ultra` của một
      người đổi mode của tất cả.
    - Hook JS: ghi ra **file** `.ponytail-active` trong stateDir → phạm vi *máy*, không phải
      phiên; đây là lý do `readMode()` vắng file nghĩa là "tắt".
    - `pi-extension`: tầng duy nhất thật sự **theo phiên** — `pi.appendEntry('ponytail-mode')`
      rồi `resolveSessionMode()` quét ngược danh sách entry để lấy mode mới nhất.
    Tức câu "Level persists until changed or session end" trong SKILL.md chỉ đúng nghĩa với
    `pi`; ở hook JS và Hermes nó dai hơn thế.

### B2 — nghiên cứu ngoài repo (CHẠY, vì cơ chế móc của ~20 host là hành vi bên thứ ba)

Digest sub-agent trả về (xác thực từ file trong repo; phần phía nhà cung cấp còn treo ghi rõ):

- **opencode:** plugin server nạp từ khoá `plugin` · `opencode.json` + `.opencode/plugins/ponytail.mjs` ·
  hook `config`, `experimental.chat.system.transform` (append luật mỗi lượt), `command.execute.before`.
- **Claude Code:** plugin + hooks JSON · `.claude-plugin/plugin.json` trỏ `hooks/claude-codex-hooks.json` ·
  `SessionStart` (matcher `startup|resume|clear|compact`), `SubagentStart`, `UserPromptSubmit`.
- **Codex:** dùng CHUNG file hook với Claude Code · `.codex-plugin/plugin.json` · nhận qua env `PLUGIN_DATA`.
- **pi:** `pi: {extensions, skills}` trong package.json · `before_agent_start` trả `{systemPrompt}`.
- **MCP:** server stdio · `ponytail-mcp/index.js` · phơi prompt `ponytail` + tool `ponytail_instructions`;
  **không có đường always-on**, người dùng phải gọi tay.
- **Cursor:** `hooks/cursor-hooks.json` merge vào `~/.cursor/hooks.json`, hoặc rule luôn bật
  `.cursor/rules/ponytail.mdc` · `sessionStart` + `beforeSubmitPrompt`; `subagentStart` không nhận
  context nên sub-agent không có luật.
- **Qoder:** `.qoder-plugin/plugin.json` + `hooks/qoder-hooks.json` · `UserPromptSubmit` + `PreToolUse`
  matcher `task|Task`.
- **Copilot:** `.github/plugin/plugin.json` + `hooks/copilot-hooks.json` · chỉ `sessionStart` đọc context.
- **Gemini CLI:** `gemini-extension.json` với `contextFileName: AGENTS.md` · chủ ý KHÔNG dùng hook.
- **Windsurf / Cline / Kiro:** file rule hoặc steering thuần, không hook.
- **Grok / Devin:** manifest plugin, không dùng lifecycle hook (Grok vì output hook không chèn được luật).

- **Hermes:** `plugin.yaml` + `__init__.py` · bơm mode qua `pre_llm_call`; hàm
  `build_injected_context` (`__init__.py:105`) là chỗ dựng khối context.

**Xác thực phía nhà cung cấp (agent web, có URL nguồn) — nhóm rules-file:**

- **Cursor:** rule `.cursor/rules/*.mdc` (file `.md` trong thư mục đó bị BỎ QUA), frontmatter
  `description`/`globs`/`alwaysApply`, 4 chế độ kích hoạt. Hooks có thật nhưng **beta** (changelog
  1.7), schema `{"version":1,"hooks":{…}}`, thứ tự nạp enterprise → team → project → user, và có
  ~21 event. Ponytail chỉ dùng `sessionStart` + `beforeSubmitPrompt`; `subagentStart` tồn tại
  nhưng chỉ nhận `permission`/`user_message` nên đúng như repo tự khai: sub-agent không có luật.
- **Windsurf:** nay là Devin Desktop; rule `.devin/rules/*.md` ưu tiên, `.windsurf/rules/*.md` là
  fallback — tức file Ponytail đang ship nằm ở đường fallback. Có `trigger:
  always_on|model_decision|glob|manual`, **giới hạn 12.000 ký tự/file** (6.000 cho global). Có
  Cascade Hooks 12 event, Ponytail không dùng.
- **Kiro:** steering `.kiro/steering/*.md`, frontmatter `inclusion: always|fileMatch|manual|auto`
  (+ `fileMatchPattern`) — khớp đúng cái repo ship. Kiro CÓ agent hooks
  (`.kiro/hooks/<id>.json`, có cả Prompt Submit chặn được) mà Ponytail chưa khai thác.
- **Qoder:** rule `.qoder/rules`, **trần 100.000 ký tự** trên toàn bộ rule đang bật, và khi xung
  đột thì rule THẮNG `AGENTS.md`. Hooks khai trong `settings.json` — đúng như repo hướng dẫn;
  IDE có 12 event, CLI 24 event.
- **Cline:** `.clinerules/` là **thư mục**, Cline gộp mọi `.md`/`.txt` bên trong; frontmatter
  `paths:` tùy chọn. Cline có 6 hook nhưng **chỉ macOS/Linux**.
- **Grok:** có rules chính thức (`.grok/rules/`, đọc thêm `.claude/rules/`, `.cursor/rules/`) và
  CÓ hooks đầy đủ 14 event — nên câu "Grok lifecycle hooks không dùng được vì output không chèn
  được instruction" là giới hạn của *event output*, không phải Grok thiếu hook.
- **Devin:** bản cloud dùng **Knowledge** (mỗi item bắt buộc có Trigger Description) + đọc
  `AGENTS.md`; bản CLI có rules `.devin/rules/*.md` và hooks `.devin/hooks.v1.json` 8 event.
  `.devinrules` KHÔNG có trong docs → chưa xác thực.
- Mẫu số chung được xác thực ở Cursor, Windsurf, Qoder, Cline, Grok, Devin: **`AGENTS.md`** —
  đúng là lá bài Ponytail dùng cho tầng chỉ-chỉ-dẫn. Kiro không xác thực `AGENTS.md`.

**Xác thực phía nhà cung cấp (agent web, có URL nguồn) — nhóm plugin/hook:**

- **Claude Code:** `plugin.json` **chỉ `name` là required** (repo tự khai name/version/description
  — sai). Có **33 hook event**, và **`SubagentStart` CÓ thật** → đường sống của
  `ponytail-subagent.js` là chính thức, không phải mẹo. Quan trọng cho kiến trúc Ponytail: chỉ
  **4 event** (`SessionStart`, `UserPromptSubmit`, `UserPromptExpansion`, `PostModelSwitch`) biến
  stdout văn bản thuần thành context; mọi event khác **phải** dùng `hookSpecificOutput.
  additionalContext` — đúng lý do `writeHookOutput()` bọc riêng nhánh `SubagentStart`
  (`ponytail-runtime.js:125`). Có `${CLAUDE_PLUGIN_DATA}` và `${CLAUDE_PROJECT_DIR}` ngoài
  `${CLAUDE_PLUGIN_ROOT}`.
- **Codex:** CÓ hooks chính thức, tên event + cách lồng gần **giống hệt** Claude Code (kể cả
  `SubagentStart`), inject qua `additionalContext` với trần ~2.500 token/message. **Điểm chặn:**
  Codex chỉ tự đọc hooks ở tên+chỗ cố định (`~/.codex/hooks.json`, `<repo>/.codex/hooks.json`,
  hoặc inline `[hooks]` trong `config.toml`, cần bật `features.hooks`) — nên một file tên kiểu
  `claude-codex-hooks.json` **Codex sẽ không tự nạp**; phải symlink/copy thành `.codex/hooks.json`.
  Nội dung JSON thì dùng chung được, chỉ tên file là không.
- **Copilot:** hooks là feature thật, nhưng **schema KHÁC** Claude: `{"version":1,"hooks":{...}}`,
  event **camelCase** (`sessionStart`, `userPromptSubmitted`, `preToolUse`, …), **không có lớp
  matcher lồng** → không chia sẻ file với Claude/Codex được. Đọc ở `.github/hooks/*.json` (agent
  cloud chỉ đọc từ default branch) và `~/.copilot/hooks/`. Riêng **VS Code** (Preview) mới đọc cả
  `.claude/settings.json` với event PascalCase kiểu Claude, nhưng **matcher bị parse rồi bỏ qua**.
- **Gemini CLI:** `gemini-extension.json` required `name`+`version`+`description`; context file
  default `GEMINI.md`. Gemini CÓ hooks nhưng **tên event khác hoàn toàn**
  (`BeforeAgent`/`AfterAgent`/`BeforeModel`/`BeforeTool`/`AfterTool`/`PreCompress`…) → bắt buộc
  có lớp mapping, không dùng chung file.
- **MCP:** `prompts` là **user-controlled** (spec: người dùng chủ động chọn, điển hình là slash
  command) → không auto-inject, nên MCP không thay được hook. Cơ chế always-on duy nhất là
  `InitializeResult.instructions`, và spec chỉ nói **MAY** được thêm vào system prompt → không
  bảo đảm. Đây là lý do kiến trúc `ponytail-mcp/` chỉ là tầng bổ sung, không phải tầng chính.
- **opencode:** `experimental.chat.system.transform` có thật trong type đã publish
  (`@opencode-ai/plugin`), signature `(input:{sessionID?,model}, output:{system: string[]})` —
  đúng cái `.opencode/plugins/ponytail.mjs` đang dùng. `config.skills.paths` và `config.command`
  đều có trong schema. **Sửa một điểm:** `PluginInput` hiện là
  `{client, project, directory, worktree, serverUrl, $}` — **không còn `app`** (`app` chỉ có ở
  bản cũ ≤ v0.5.29). Loader nhận cả `plugin/` và `plugins/`.
- **pi:** `before_agent_start` **đúng là** cho phép trả `{ systemPrompt }`, và nó được **chuỗi
  hoá** qua nhiều extension. Nhưng **package đã đổi tên**: `@mariozechner/pi-coding-agent` đã
  deprecated → `@earendil-works/pi-coding-agent` (0.85.1). `@mariozechner/pi` trên npm bây giờ là
  một tool vLLM khác hẳn. Khoá `pi` trong `package.json` (`extensions`/`skills`) là đúng quy ước.

**Vẫn chưa xác thực (report sẽ ghi rõ là "repo tự khai"):** hooks cho Devin cloud; `.devinrules`;
Codex có cho đặt tên file hooks tuỳ ý hay không; `instructions` như option constructor
`McpServer` trong TS SDK; opencode có thực sự áp dụng mutation `skills`/`command` lúc runtime.

## Hỏi đáp

(Điền khi hỏi đáp với người dùng.)
