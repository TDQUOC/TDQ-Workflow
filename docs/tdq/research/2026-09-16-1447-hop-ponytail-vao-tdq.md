# Research — Hợp lối code Ponytail vào TDQ-Workflow
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

> Quy ước mức tin cậy trong file này:
> - **[XÁC THỰC]** = có trong tài liệu chính thức `code.claude.com/docs` (domain docs mới; `docs.claude.com/en/docs/claude-code/*` redirect 301 sang đây — kiểm bằng WebFetch, xem Câu 1).
> - **[SUY-CODE]** = suy ra từ file thật đã đọc trong máy, có `đường-dẫn:dòng`.
> - **[BÊN-THỨ-BA]** = issue tracker `anthropics/claude-code`, repo Ponytail, hoặc blog. Không phải cam kết của Anthropic.

---

## Câu 1 — Danh sách hook event Claude Code hỗ trợ chính thức; có event nào chạy khi sub-agent bắt đầu?

**Truy vấn đã dùng**
- `WebFetch https://docs.claude.com/en/docs/claude-code/hooks` → trả về `301 Moved Permanently` sang `https://code.claude.com/docs/en/hooks`. (Phát hiện phụ: URL docs cũ đã đổi domain.)
- `WebFetch https://code.claude.com/docs/en/hooks` (prompt: liệt kê đủ event + khả năng bơm ngữ cảnh)
- `WebFetch https://code.claude.com/docs/en/hooks#userpromptsubmit-decision-control`
- tavily: `Claude Code hooks SubagentStop SessionStart UserPromptSubmit additionalContext full list of hook events`
- tavily: `Claude Code SubagentStart hook additionalContext inject instructions into subagent hookSpecificOutput`

**Nguồn**
- https://code.claude.com/docs/en/hooks (trang Hooks reference chính thức)
- https://code.claude.com/docs/en/hooks#hook-lifecycle
- https://github.com/anthropics/claude-code/issues/69545 (bảng thực nghiệm PreToolUse/Agent)
- https://github.com/anthropics/claude-code/issues/39814 (updatedInput bị bỏ qua cho Agent tool)
- https://github.com/DietrichGebert/ponytail/issues/252 (chính Ponytail mô tả vấn đề + cách fix)
- `/Users/tdq/Documents/ponytail/hooks/claude-codex-hooks.json:16-27`
- `/Users/tdq/Documents/ponytail/hooks/ponytail-runtime.js:123-129`

**Kết luận**

Danh sách 32 event chính thức **[XÁC THỰC]**:

`SessionStart`, `Setup`, `UserPromptSubmit`, `UserPromptExpansion`, `PreToolUse`, `PermissionRequest`, `PermissionDenied`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `Notification`, `MessageDisplay`, `SubagentStart`, `SubagentStop`, `TaskCreated`, `TaskCompleted`, `Stop`, `StopFailure`, `TeammateIdle`, `InstructionsLoaded`, `ConfigChange`, `CwdChanged`, `DirectoryAdded`, `FileChanged`, `WorktreeCreate`, `WorktreeRemove`, `PreCompact`, `PostCompact`, `PreModelSwitch`, `PostModelSwitch`, `Elicitation`, `ElicitationResult`.

→ **TDQ-Workflow hiện dùng 5 event, tức mới khai thác ~15% bề mặt hook.**

**`SubagentStart` TỒN TẠI và bơm được ngữ cảnh vào sub-agent — đây là phát hiện quan trọng nhất.** Trích nguyên văn trang docs chính thức **[XÁC THỰC]**:

> `additionalContext` | String added to the subagent's context at the start of its conversation, before its first prompt.

```json
{ "hookSpecificOutput": { "hookEventName": "SubagentStart", "additionalContext": "Follow security guidelines for this task" } }
```

Bảng decision-control chính thức **[XÁC THỰC]**:

> | SessionStart, SubagentStart, PostModelSwitch | Context only | `hookSpecificOutput.additionalContext` adds context for Claude. SessionStart also accepts `initialUserMessage`, `watchPaths`, `sessionTitle`, and `reloadSkills`. No blocking or decision control |

Cơ chế bơm — nguyên văn **[XÁC THỰC]**:

> The `additionalContext` field passes a string from your hook into Claude's context window. Claude Code wraps the string in a system reminder and inserts it into the conversation at the point where the hook fired. Claude reads the reminder on the next model request, but it doesn't appear as a chat message in the interface.

Với exit code 0 + stdout thô **[XÁC THỰC]**:

> For most events, Claude Code writes stdout to the debug log and doesn't show it in the transcript. The exceptions are `UserPromptSubmit`, `UserPromptExpansion`, `SessionStart`, and `PostModelSwitch`, where Claude Code adds plain-text stdout as context that Claude can see and act on.

→ **`SubagentStart` KHÔNG nhận stdout thô**, bắt buộc dùng JSON `hookSpecificOutput`. Ponytail đã đụng đúng bug này và ghi chú thẳng trong code **[SUY-CODE]** (`ponytail-runtime.js:123-129`):

> `// Native Claude: SessionStart accepts raw stdout, but SubagentStart needs the hookSpecificOutput JSON form or the context is dropped.`

Bảng khả năng bơm ngữ cảnh theo event (phần TDQ quan tâm):

| Event | Bơm được text vào ngữ cảnh model? | Bằng cách nào |
|---|---|---|
| `SessionStart` | Có | stdout thô **HOẶC** `hookSpecificOutput.additionalContext`; thêm `initialUserMessage`, `reloadSkills` |
| `UserPromptSubmit` | Có | stdout thô **HOẶC** `hookSpecificOutput.additionalContext`; chèn ngay trước prompt người dùng |
| `UserPromptExpansion` | Có | stdout thô |
| `PostModelSwitch` | Có | stdout thô / `additionalContext` |
| `SubagentStart` | **Có** | **CHỈ** `hookSpecificOutput.additionalContext` (stdout thô bị drop) |
| `PreToolUse` | Không | chỉ block / `updatedInput` / `systemMessage` (hiện lên transcript, không phải ngữ cảnh model) |
| `PostToolUse` | Có | `hookSpecificOutput.additionalContext` |
| `Stop` / `SubagentStop` | Có | `decision: "block"` + `reason`, **hoặc** `hookSpecificOutput.additionalContext` cho phản hồi không-lỗi mà vẫn tiếp tục hội thoại |
| `InstructionsLoaded` | **Không** | "None — No decision control. Used for side effects like logging or cleanup" |

**GIẢ ĐỊNH SAI CẦN SỬA — `PreToolUse` matcher `Task` không dùng được:**
- Matcher của `PreToolUse` lọc theo **tool name** (ví dụ `Bash`, `Edit|Write`, `mcp__.*`) **[XÁC THỰC]**.
- Matcher của `SubagentStart` lọc theo **agent type** (`general-purpose`, `Explore`, `Plan`, tên agent tự định nghĩa, hoặc dạng plugin-scoped `^my-plugin:reviewer$`) **[XÁC THỰC]**.
- Tool sinh sub-agent trong Claude Code bản hiện tại tên là **`Agent`**, không phải `Task` **[XÁC THỰC — tên tool `Agent` xuất hiện trong tool-list của chính phiên này; `Task` là tên cũ]**. Và theo thực nghiệm công khai, `PreToolUse(matcher: "Agent")` **không fire** khi spawn sub-agent; `PermissionRequest(matcher: "Agent")` cũng không **[BÊN-THỨ-BA — issue #69545]**.
- → Chặn/điểm-móc vòng đời sub-agent **phải** đi qua `SubagentStart` / `SubagentStop`, **không** đi qua `PreToolUse`.

**Giới hạn đã biết của `SubagentStart` [BÊN-THỨ-BA]:**
- `updatedInput` (sửa prompt / sửa `model` của sub-agent) bị **bỏ qua im lặng** (issue #39814, #69545).
- `decision: "block"` / exit 2 cũng bị bỏ qua — không chặn được sub-agent (issue #69545).
- `additionalContext` **không** phải system prompt → là mục tiêu của context compression khi hội thoại dài; đã có 2 feature request xin `updatedPrompt` để luật khỏi bị nén mất (issue #23885, #23901).
- Hook input của `SubagentStart` **không** chứa model được yêu cầu (issue #69545).

**Mức tin cậy:** danh sách event + cơ chế `additionalContext` = **xác thực**. Việc `PreToolUse`/`Agent` không fire và `updatedInput` bị bỏ qua = **bên thứ ba (issue tracker chính thức của Anthropic, nhiều issue độc lập trùng khớp)**. Việc `SubagentStart` cần JSON chứ không stdout = **xác thực (docs) + suy ra từ code Ponytail**.

---

## Câu 2 — Skill được kích hoạt thế nào; có cách nào luôn-bật mọi lượt?

**Truy vấn đã dùng**
- `WebFetch https://docs.claude.com/en/docs/claude-code/skills` → 301 sang `https://code.claude.com/docs/en/skills`
- `WebFetch https://code.claude.com/docs/en/skills`
- `WebFetch https://code.claude.com/docs/en/memory`
- tavily: `Claude Code ".claude/rules" directory always applied rules memory CLAUDE.md docs`

**Nguồn**
- https://code.claude.com/docs/en/skills
- https://code.claude.com/docs/en/memory (mục `Organize rules with .claude/rules/`)
- https://code.claude.com/docs/en/claude-directory (bảng file/scope)
- https://konadu.dev/how-claude-code-loads-claude-rules (đối chiếu bên thứ ba)

**Kết luận**

Skill có **hai đường kích hoạt**, và đường tự động là thật **[XÁC THỰC]**:

> "Claude uses skills when relevant, or you can invoke one directly with `/skill-name`."
> `description` (Recommended): What the skill does and when to use it. Claude uses this to decide when to apply the skill.

Các field frontmatter điều khiển kích hoạt **[XÁC THỰC]**:

| Field | Tác dụng |
|---|---|
| `description` | Model đọc để tự quyết có nạp skill hay không |
| `when_to_use` | Text bổ sung, gắn thêm vào description cho quyết định nạp |
| `disable-model-invocation: true` | Tắt tự-nạp; chỉ còn gọi tay bằng `/name` |
| `user-invocable: false` | Ẩn khỏi menu `/`, chỉ Claude gọi được ("background knowledge users shouldn't invoke directly") |
| `paths` | Glob giới hạn phạm vi tự-kích-hoạt theo file |

→ **Giả định "skill chỉ nạp khi gõ `/ten-skill`" là SAI.** Skill tự nạp theo `description` khi model thấy liên quan. Nhưng đó là *xác suất*, không phải *bảo đảm*.

**KHÔNG có `alwaysApply` cho skill [XÁC THỰC]** — docs không có field nào như vậy, và docs nói rõ ngược lại:

> Rules load into context every session or when matching files are opened. For task-specific instructions that don't need to be in context all the time, use skills instead, **which only load when you invoke them or when Claude determines they're relevant to your prompt.**

**Cơ chế "luôn-bật" đúng là `.claude/rules/*.md`, KHÔNG phải skill [XÁC THỰC]:**

> Rules without `paths` frontmatter are loaded at launch with the same priority as `.claude/CLAUDE.md`.
> Rules can be scoped to specific files using YAML frontmatter with the `paths` field. These conditional rules only apply when Claude is working with files matching the specified patterns.
> Personal rules in `~/.claude/rules/` apply to every project on your machine. (User-level rules are loaded before project rules, giving project rules higher priority.)
> All `.md` files are discovered recursively, so you can organize rules into subdirectories.
> The `.claude/rules/` directory supports symlinks.

→ Vậy có **4 bậc luôn-bật**, từ yếu đến mạnh:
1. **Skill auto-invoke** (`description` tốt) — nhẹ nhất về context, nhưng model có thể bỏ qua.
2. **`.claude/rules/*.md` không có `paths`** — nạp mỗi phiên, ngang ưu tiên `CLAUDE.md`. **[XÁC THỰC]**
3. **`.claude/rules/*.md` có `paths`** — chỉ nạp khi Claude đọc file khớp glob. Đây chính là "luật code chỉ bật khi đang chạm code". **[XÁC THỰC]**
4. **Hook bơm `additionalContext`** (`SessionStart` + `UserPromptSubmit` + `SubagentStart`) — cách duy nhất *tái-neo* luật giữa phiên dài và là cách duy nhất chạm được sub-agent.

Cảnh báo quan trọng từ docs — rule/CLAUDE.md **không** phải enforcement **[XÁC THỰC]**:

> Claude treats them as context, not enforced configuration. To block an action regardless of what Claude decides, use a PreToolUse hook instead.
> CLAUDE.md content is delivered as a user message after the system prompt, not as part of the system prompt itself. Claude reads it and tries to follow it, but there's no guarantee of strict compliance.

Và về conflict **[XÁC THỰC]**: *"if two rules contradict each other, Claude may pick one arbitrarily."* — Ponytail đã đụng đúng chuyện này: khi có rule always-on của Cursor, hook của nó **rút lui không bơm bản thứ hai** để tránh hai bản luật chỏi nhau **[SUY-CODE]** (`/Users/tdq/Documents/ponytail/hooks/ponytail-runtime.js:59-75`, issue #817).

**Mức tin cậy:** toàn bộ = **xác thực**.

---

## Câu 3 — Giới hạn của việc bơm luật mỗi lượt qua `UserPromptSubmit`

**Truy vấn đã dùng**
- tavily: `Claude Code UserPromptSubmit hook additionalContext size limit truncation token cost every turn`
- `WebFetch https://code.claude.com/docs/en/hooks#json-output` (prompt nhắm riêng vào "10,000 / truncation / spill to file")
- `WebFetch https://code.claude.com/docs/en/memory` (giới hạn dòng/byte của CLAUDE.md, MEMORY.md)

**Nguồn**
- https://code.claude.com/docs/en/hooks (mục "Add context for Claude")
- https://code.claude.com/docs/en/memory
- https://code.claude.com/docs/en/costs
- https://github.com/anthropics/claude-code/issues/51537 (cap 10.000 ký tự của `persistHookOutput`)
- https://github.com/anthropics/claude-code/issues/65385 (spill ra file + model bỏ không Read)
- https://docs.rhi.zone/claude-code-hooks (khảo sát thực nghiệm schema `UserPromptSubmit`)

**Kết luận**

**a) Có cap, nhưng cap KHÔNG nằm trong tài liệu chính thức.** Tôi fetch trang hooks hai lần nhắm riêng vào từ khoá giới hạn/truncation và **không tìm được nguồn xác thực** — docs không nêu số. Số cụ thể chỉ có ở issue tracker **[BÊN-THỨ-BA]**:
- Từ ~v1.0.100: stdout của `<user-prompt-submit-hook>` bị **cắt cứng ở 10.000 ký tự**.
- Từ v2.1.89 (~cuối 3/2026): hàm nội bộ `persistHookOutput` áp **cap 10.000 ký tự cho MỌI loại hook**, kể cả `SessionStart` (trước đó `SessionStart` không có cap). Changelog công bố 50.000 nhưng code thực tế là `1e4`.
- Khi vượt cap: nội dung đầy đủ được **ghi ra file** `hook-{hookId}-additionalContext.txt` và **chỉ đường dẫn + ~500 ký tự preview** được chèn vào hội thoại (issue #65385).
- Hệ quả đắt: theo issue #65385, Opus đọc file spill 100% số lần, còn Sonnet 4.6 **luôn bỏ qua** lời Read và trả lời bằng đúng preview ~500 ký tự.

→ **Luật dài hơn ~10.000 ký tự sẽ im lặng biến thành một dòng đường dẫn mà model tuỳ tâm mới đọc.** Đây là ràng buộc thiết kế cứng nhất trong toàn bộ research này.

**b) Có tính vào context cost mỗi lượt.** Docs nói `additionalContext` được *"wraps the string in a system reminder and inserts it into the conversation at the point where the hook fired"* **[XÁC THỰC]** → nó thành nội dung hội thoại, tích luỹ theo lượt. Thêm nữa, docs khảo sát bên thứ ba ghi: *"injected `additionalContext` is saved in the session transcript and replayed on `/resume`"* **[BÊN-THỨ-BA — rhi.zone]**. Và docs chi phí chính thức nói *"Token costs scale with context size"* cùng việc prompt caching chỉ giảm giá cho **nội dung lặp lại giống nhau** **[XÁC THỰC]**.

→ Suy ra: bơm một khối luật **cố định, byte-for-byte giống nhau** mỗi lượt thì cache-friendly; bơm khối **biến đổi theo lượt** (có timestamp, có state khác nhau) thì **phá cache prefix** và trả full giá input mỗi lượt.

**c) Thực hành khuyến nghị (tổng hợp, có nguồn)**
- Giữ khối bơm mỗi lượt **ngắn** — docs khuyên CLAUDE.md dưới 200 dòng vì *"Longer files consume more context and reduce adherence"* **[XÁC THỰC]**; cùng lý lẽ áp cho hook injection.
- Đặt luật **tĩnh** vào `.claude/rules/` (nạp 1 lần/phiên, sống qua `/compact` theo docs), chỉ để hook bơm phần **động** (mode hiện tại, state, nhắc theo điều kiện).
- Dùng `paths:` frontmatter để luật code chỉ vào ngữ cảnh khi Claude thật sự đọc file code — docs nói thẳng mục đích là *"reducing noise and saving context space"* **[XÁC THỰC]**.
- Bơm **có điều kiện**, không bơm vô điều kiện: chính TDQ-Workflow đã làm vậy **[SUY-CODE]** — `prompt_context.py` chỉ `print(text)` sau khi dựng text theo state (`/Users/tdq/.claude/plugins/cache/tdq-local/tdq-workflow/0.46.0/hooks/scripts/prompt_context.py:168,316,323`).
- Ponytail cũng bơm có điều kiện: mode `off` hoặc không có flag → hook **thoát không in gì** **[SUY-CODE]** (`ponytail-subagent.js:19`).

**Mức tin cậy:** cơ chế + cost = **xác thực**; con số cap 10.000 và hành vi spill-ra-file = **bên thứ ba (issue tracker chính thức, hai issue độc lập, có số phiên bản và tên biến)**. **Không tìm được nguồn xác thực từ tài liệu Anthropic cho con số này** — cần tự benchmark trước khi dựa vào.

---

## Câu 4 — Cơ chế "mode"/cấu hình theo phiên (`/lenh lite|full|ultra` bền tới hết phiên)

**Truy vấn đã dùng**
- Đọc trực tiếp implementation đã chạy thật của Ponytail (nguồn mạnh nhất cho câu này)
- `WebFetch https://code.claude.com/docs/en/hooks` (tìm API phiên chính thức)
- tavily: `Claude Code SubagentStart hook additionalContext ...` (bắt được issue #252 của Ponytail)

**Nguồn**
- `/Users/tdq/Documents/ponytail/hooks/claude-codex-hooks.json:1-41`
- `/Users/tdq/Documents/ponytail/hooks/ponytail-runtime.js:6` (`const STATE_FILE = '.ponytail-active';`)
- `/Users/tdq/Documents/ponytail/hooks/ponytail-runtime.js:31-58` (`statePath`, `setMode`, `clearMode`, `readMode`)
- `/Users/tdq/Documents/ponytail/hooks/ponytail-mode-tracker.js:42-133`
- `/Users/tdq/Documents/ponytail/hooks/ponytail-subagent.js:16-25`
- `/Users/tdq/Documents/ponytail/commands/ponytail-help.toml:2`
- https://code.claude.com/docs/en/hooks
- https://github.com/anthropics/claude-code/issues/55506 (hook input KHÔNG có token usage)

**Kết luận**

**KHÔNG có API phiên chính thức để lưu mode.** Tôi không tìm được bất kỳ mục nào trong docs cho phép hook ghi/đọc state phiên. Hook input chỉ có `session_id`, `transcript_path`, `cwd`, `permission_mode`, `hook_event_name`, `prompt`, `scratchpad_dir`, `agent_id`, `agent_type`… **[XÁC THỰC cho danh sách field; "không có API state" = không tìm được nguồn xác thực nào nói có]**. Issue #55506 củng cố: hook payload không mang cả token usage, chứng tỏ bề mặt state được expose rất hẹp **[BÊN-THỨ-BA]**.

**Cách làm được kiểm chứng = hook + flag file trên đĩa.** Ponytail làm đúng vậy, và nó đang chạy production **[SUY-CODE]**:

1. **Nơi lưu**: một file phẳng `~/.claude/.ponytail-active` chứa **duy nhất chuỗi mode** (`ponytail-runtime.js:6,31-43`). Không JSON, không schema. `readMode()` trả `null` nếu file không tồn tại, và *"Absent flag = ponytail off"* (`ponytail-runtime.js:50`).
2. **Ai ghi**: hook `UserPromptSubmit` (`ponytail-mode-tracker.js`) **tự parse text của người dùng**, nhận ra `/ponytail lite|full|ultra|off`, rồi `setMode()`. Tức **không dùng slash-command của Claude Code làm nơi đổi state** — dùng hook đọc prompt thô.
3. **Ai đọc & bơm**: `SessionStart` (`ponytail-activate.js`) bơm ruleset đầu phiên; `SubagentStart` (`ponytail-subagent.js:16-25`) đọc mode rồi bơm cùng ruleset vào từng sub-agent.
4. **Hai tầng mode**: mode *phiên* (flag file, đổi bằng `/ponytail <mode>`) và mode *mặc định* (`writeDefaultMode()` → `~/.config/ponytail/config.json` + env `PONYTAIL_DEFAULT_MODE`), thứ tự phân giải: **env var → config file → `full`** (`ponytail-help.toml:2`, `ponytail-mode-tracker.js:55-65`).
5. **Chỉ bơm khi ĐỔI mode**, không bơm lại mỗi lượt: `modeSwitched` gate ở `ponytail-mode-tracker.js:42,86-101` — lượt bình thường chỉ in header ngắn, không in lại toàn bộ luật. Đúng khuyến nghị ở Câu 3.

**Cảnh báo về phạm vi [SUY-CODE]:** `statePath` là **một file duy nhất trong `~/.claude/`, KHÔNG gắn `session_id`** (`ponytail-runtime.js:31,40`). → Hai phiên Claude Code song song **dùng chung một mode, đá nhau**. Nếu TDQ cần mode per-session, phải đưa `session_id` (có trong hook input) vào tên file — Ponytail chưa làm.

**Đối chiếu với TDQ-Workflow:** TDQ đã có sẵn kiến trúc state file này ở dạng chín hơn — `docs/tdq/state.json` + CLI `tdq_state.py` (theo CLAUDE.md của người dùng: *"Ghi state CHỈ bằng CLI đó"*). Nghĩa là **TDQ không cần phát minh cơ chế mode mới**, chỉ cần thêm một trường mode vào state hiện có và một nhánh parse trong `prompt_context.py`.

**Mức tin cậy:** "không có API phiên chính thức" = **không tìm được nguồn xác thực nào nói có** (kết luận phủ định, độ chắc trung bình-cao). Cơ chế flag-file = **suy ra từ code đang chạy production của Ponytail**, đã xác minh bằng nhiều file.

---

## Hệ quả cho thiết kế

- **Bắt buộc thêm hook `SubagentStart`.** Không có nó, bộ luật chống over-engineering vô hình với `tdq-implementer` — chính con agent viết code. Đây là lỗ hổng lớn nhất của TDQ hiện tại (5 hook, không có `SubagentStart`). Ponytail phải mở issue #252 để fix đúng lỗ này; TDQ nên học trực tiếp, không cần trả giá lần hai.
- **`SubagentStart` phải in JSON `{"hookSpecificOutput":{"hookEventName":"SubagentStart","additionalContext":...}}`.** `print(text)` thô như `session_start.py:37` và `prompt_context.py:323` đang làm sẽ bị **drop im lặng** ở event này.
- **Bỏ ý định dùng `PreToolUse` matcher `Task`/`Agent` để chặn sub-agent.** Không fire. Mọi thứ liên quan vòng đời sub-agent đi qua `SubagentStart`/`SubagentStop`.
- **Không thiết kế cơ chế "chặn" sub-agent bằng hook.** `SubagentStart` là *context only*: `decision:"block"`, exit 2, `updatedInput` đều bị bỏ qua. Muốn chặn cứng hành vi thì phải là `PreToolUse` trên `Edit|Write|Bash` — TDQ đã có sẵn `edit_gate.py`/`bash_gate.py`, đó là nơi cài luật cứng.
- **Chia luật làm hai tầng, không nhồi hết vào hook.** Phần bất biến của bộ luật → `.claude/rules/*.md` **có `paths:` glob khớp file code** (nạp khi chạm code, tiết kiệm context, sống qua `/compact`). Phần động (mode hiện tại, state request, nhắc theo điều kiện) → hook bơm.
- **Ngân sách cứng: giữ mỗi lần bơm dưới ~10.000 ký tự, mục tiêu thực tế thấp hơn nhiều.** Vượt cap → nội dung bị đẩy ra file tạm và chỉ còn ~500 ký tự preview; Sonnet 4.6 được ghi nhận không bao giờ Read file đó. Tức **luật dài = luật không tồn tại**.
- **Chỉ bơm toàn văn luật khi mode ĐỔI; lượt thường chỉ bơm một dòng header.** Sao chép đúng gate `modeSwitched` của Ponytail. Vừa hợp soul "context cost", vừa tránh nhắc lặp gây nhiễu.
- **Giữ khối bơm byte-for-byte giống nhau giữa các lượt** để prompt caching còn ăn; đừng chèn timestamp hay số đếm thay đổi vào khối luật.
- **Skill KHÔNG phải nơi đặt luật luôn-bật.** Docs nói thẳng skill chỉ nạp on-demand. Nhưng skill auto-invoke theo `description` là thật — nên `tdq-conventions` vẫn đúng chỗ cho *quy trình tra cứu sâu*, còn *luật phải luôn có mặt* thì thuộc `.claude/rules/`.
- **Không dùng `InstructionsLoaded` để bơm gì cả** — nó là "None / no decision control", chỉ dùng để **log** xem rule nào thật sự đã nạp. Dùng nó làm công cụ tự-kiểm cho TDQ, không làm kênh bơm.
- **Mode `lite|full|ultra` tái dùng `docs/tdq/state.json` + `tdq_state.py`, không tạo flag file mới.** TDQ đã có layer state chín hơn Ponytail; thêm một trường mode là đủ.
- **Nếu làm mode: gắn `session_id` vào state.** Ponytail dùng một file global trong `~/.claude/` nên hai phiên song song đá nhau. TDQ có `session_id` trong hook input — dùng nó.
- **Phát hiện một mode phải bằng hook `UserPromptSubmit` parse prompt thô, không dựa vào slash-command.** Slash-command chỉ bung thành prompt cho model; nó không ghi state. Ponytail chọn đúng đường này.
- **Chống hai bản luật chỏi nhau.** Docs cảnh báo rule mâu thuẫn khiến Claude "pick one arbitrarily". Nếu bộ luật vào cả `.claude/rules/` và hook injection, hook phải **phát hiện rule đã có và rút lui** — đúng pattern `cursorRulePath()` của Ponytail.
- **Tự benchmark cap 10.000 ký tự trước khi dựa vào nó.** Con số này chỉ có ở issue tracker, không có trong tài liệu chính thức, và có thể đổi theo phiên bản. Viết một test nhỏ trong TDQ đo ngưỡng thật.

---

## Ghi chú về chất lượng nguồn

- Tài liệu chính thức Claude Code **đã chuyển domain**: `docs.claude.com/en/docs/claude-code/*` → `code.claude.com/docs/en/*` (301). Mọi link cũ trong doc TDQ nên cập nhật.
- Trang `code.claude.com/docs/en/hooks` khi fetch bị **truncate ở phần cuối**, nên vài anchor (`#add-context-for-claude`, `#json-output`) trả về "không thấy" dù nội dung đó có thật — tôi lấy được nguyên văn các đoạn đó qua kết quả search trích từ chính trang này. Có `code.claude.com/docs/llms.txt` làm index đầy đủ nếu cần đào sâu hơn.
- **Không tìm được nguồn xác thực** cho: (a) con số cap ký tự của `additionalContext`; (b) sự tồn tại của một API state phiên chính thức; (c) `additionalContext` có được replay khi `/resume` hay không (chỉ có khảo sát bên thứ ba ở rhi.zone).
