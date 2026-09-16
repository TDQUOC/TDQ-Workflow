# RESEARCH — cong-sinh-ponytail-tdq (chạy đồng thời hai plugin always-on: tdq-workflow + ponytail)
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-09-16 · Slug: `2026-09-16-2234-cong-sinh-ponytail-tdq`
Bối cảnh đã đo trước: cả hai plugin đăng ký hook trùng `SessionStart` + `UserPromptSubmit`; Ponytail thêm `SubagentStart`; cả hai đều sinh `AGENTS.md` ở gốc project.

Nhãn tin cậy: `[XÁC THỰC]` = tài liệu chính thức code.claude.com/agents.md · `[BÊN-THỨ-BA]` = blog/GitHub issue · `[SUY-CODE]` = suy luận từ code/hành vi đo được.

Lưu ý phương pháp: tavily primary + backup đều trả `429 excessive requests` trong ~2 phút đầu; đã bù bằng WebFetch trực tiếp vào tài liệu chính thức (nguồn mạnh hơn) rồi chạy lại 4 truy vấn tavily khi key hồi. Mọi trích dẫn dưới đây đều có URL.

---

## Truy vấn 1 — Claude Code gộp hook từ nhiều plugin trên cùng một sự kiện thế nào?

Truy vấn: `Claude Code multiple plugins hooks same event merge order additionalContext` (tavily, 429) → WebFetch `https://code.claude.com/docs/en/hooks` + `https://code.claude.com/docs/en/plugins-reference`

Nguồn:
- https://code.claude.com/docs/en/hooks (Hooks reference — tài liệu chính thức)
- https://code.claude.com/docs/en/plugins-reference (Plugins reference)
- https://github.com/anthropics/claude-code/issues/10871 (BUG: plugin-registered hooks executed twice)
- https://github.com/anthropics/claude-code/issues/10225 (BUG: UserPromptSubmit hooks from plugins match but never execute)

Điều suy ra:

1. **Tất cả hook khớp đều chạy, song song, KHÔNG có cái nào "thắng".** `[XÁC THỰC]` Trích nguyên văn tài liệu: *"All matching hooks run in parallel. If you define the same handler in more than one settings file, it runs once. A plugin's or skill's copy of the same handler stays separate."*
   → Hệ quả trực tiếp cho ta: cơ chế dedupe CHỈ áp dụng cho cùng một handler khai báo ở nhiều **settings file**. Bản copy do **plugin** cung cấp được coi là tách biệt và **không bị dedupe**. Hai plugin ⇒ hai lần chạy, luôn luôn. Không có cửa để "plugin A đè plugin B".

2. **Thứ tự KHÔNG xác định.** `[XÁC THỰC về "parallel"] + [SUY-CODE về "không xác định"]` Tài liệu khẳng định chạy song song nhưng **không nêu bất cứ quy tắc thứ tự nào** giữa các hook khác nhau. Vì vậy không được thiết kế dựa trên giả định "TDQ chạy trước Ponytail" hay ngược lại. **CHƯA TÌM ĐƯỢC** bất kỳ tài liệu nào mô tả thứ tự ưu tiên/ordering key cho hook (không có field `priority`, `order`, `runAfter` nào được document).

3. **Cách nhiều `additionalContext` được hợp nhất: KHÔNG CÓ TÀI LIỆU.** `[CHƯA TÌM ĐƯỢC]` Đã kiểm 2 lần (WebFetch toàn trang hooks reference, rồi WebFetch riêng anchor `#add-context-for-claude`): tài liệu mô tả `additionalContext` như một field string trong `hookSpecificOutput`, mô tả từng event nào cho phép field đó, nhưng **không nói nhiều hook cùng event thì nối (concat) hay ghi đè (last-wins)**. Đây là lỗ hổng tài liệu thật, không phải do tìm thiếu.
   - `[SUY-CODE]` Suy luận có cơ sở: với `SessionStart`/`UserPromptSubmit`, stdout dạng plain-text của hook cũng được inject làm context; mô hình "inject nhiều nguồn" + việc hook chạy song song khiến **nối là khả năng cao hơn last-wins**, nhưng đây là suy luận, KHÔNG phải sự thật đã xác thực. **Phải tự đo bằng thực nghiệm trước khi thiết kế phụ thuộc vào nó.**
   - Cách đo được tài liệu gợi ý: `[XÁC THỰC]` hook `InstructionsLoaded` để log đúng file chỉ dẫn nào được nạp, khi nào, vì sao (https://code.claude.com/docs/en/memory). Cộng thêm `/context` để xem "Memory files" và `/hooks` để xem số hook đã đăng ký theo từng nguồn.

4. **Một plugin KHÔNG có cách nào tắt hook của plugin khác.** `[XÁC THỰC]` Tài liệu nói rõ: *"Hook entries merge across settings levels rather than replacing each other: user, project, and local settings add their own hooks without removing managed ones"* và cách duy nhất để tắt là `disableAllHooks: true` — tắt **toàn bộ**, không chọn lọc. Không tồn tại cơ chế override/suppress một hook cụ thể. Muốn bỏ một hook thì phải xoá entry trong JSON của chính nguồn đó (tức người dùng phải tự disable plugin, không phải plugin tự dàn xếp).
   - `[XÁC THỰC]` Đòn bẩy duy nhất ở tầng người dùng: `/plugin` disable cả plugin, hoặc `--settings '{"disableAllHooks": true}'` cho một lần chạy.

5. **Hai bug thật đã ghi nhận, ảnh hưởng trực tiếp tới kịch bản hai plugin:** `[BÊN-THỨ-BA]`
   - Issue #10871: hook đăng ký qua plugin **chạy hai lần với hai PID khác nhau**; `/hooks` hiện "2 hooks" dù plugin chỉ khai 1. Xác nhận trên `SessionStart`, `Notification`, `PreCompact`, "likely affects all hook types". Hệ quả: **side effect nhân đôi** (ghi file, thông báo, log). Với TDQ có hook ghi state/working log thì đây là rủi ro tính đúng đắn, không chỉ là ồn.
   - Issue #10225: hook `UserPromptSubmit` khai trong plugin `hooks.json` **được register và match nhưng không execute** (silent failure), trong khi cùng cấu hình đặt ở `~/.claude/settings.json` lại chạy. Issue bị gắn nhãn `duplicate` (đã có báo cáo khác). Hệ quả: đừng tin "khai là chạy" — phải kiểm bằng hiệu ứng thật.
   - `[XÁC THỰC]` Có một hạn chế liên quan đáng lưu: *"For security reasons, plugin-shipped agents don't support `hooks`"* (plugins-reference) — subagent do plugin ship không được tự khai hook riêng.

---

## Truy vấn 2 — Hợp đồng của `SubagentStart`, so với `SessionStart`/`UserPromptSubmit`

Truy vấn: `"SubagentStart" Claude Code hook agent_type additionalContext subagent context injection` (tavily-backup) + WebFetch anchor `#subagentstart`

Nguồn:
- https://code.claude.com/docs/en/hooks (mục SubagentStart, bảng decision control, bảng timeout)
- https://github.com/anthropics/claude-code/issues/23885 (feature request: SubagentStart nên hỗ trợ `updatedPrompt`)
- https://blakecrosley.com/blog/claude-code-hooks-explained , https://hidekazu-konishi.com/entry/claude_code_hooks_complete_guide.html (bảng tổng hợp bên thứ ba)

Điều suy ra:

1. **Bắn khi nào:** `[XÁC THỰC]` khi một subagent được spawn. Matcher lọc theo **agent type** — giá trị ví dụ: `general-purpose`, `Explore`, `Plan`, tên agent tự định nghĩa, và **tên có namespace plugin dạng `^my-plugin:reviewer$`**. → Đây là đòn bẩy cực kỳ quan trọng: **Ponytail (hoặc TDQ) có thể giới hạn hook của mình chỉ bắn cho subagent của chính mình bằng regex matcher theo namespace plugin.** Đây là cơ chế "namespace" duy nhất được document trong toàn bộ lớp hook.

2. **Input schema:** `[XÁC THỰC]` ngoài common fields (`session_id`, `transcript_path`, `cwd`, `permission_mode`, `hook_event_name`, `prompt_id`, `scratchpad_dir` có thể vắng), có riêng `agent_id` (định danh duy nhất của instance subagent) và `agent_type` (tên agent mà matcher lọc theo).

3. **Không chặn được:** `[XÁC THỰC]` nguyên văn: *"SubagentStart hooks can't block subagent creation, but they can inject context into the subagent."* Bảng decision control xếp `SessionStart, SubagentStart, PostModelSwitch` vào nhóm **"Context only — No blocking or decision control"**.

4. **Chèn context vào đâu:** `[XÁC THỰC]` `hookSpecificOutput.additionalContext` = *"String added to the subagent's context at the start of its conversation, before its first prompt."* Tức chèn vào **đầu hội thoại của subagent**, KHÔNG phải system prompt.
   - `[BÊN-THỨ-BA]` Issue #23885 nêu đúng điểm yếu này: `additionalContext` "appends to user context, not system prompt", và *"During context pruning, critical rules may be dropped"*. Người báo cáo đo được rule non-compliance ~60% với luật worktree, ~40% với bước review, và gọi cách "duplicate rules in SubagentStart additionalContext" là *"verbose, fragile"*. Issue bị đóng dạng `duplicate` → tính năng `updatedPrompt` **chưa có**. Bài học cho ta: **đừng coi `SubagentStart.additionalContext` là hàng rào cứng cho luật bắt buộc**; nó là context mềm, có thể bị prune.

5. **Timeout:** `[XÁC THỰC]` mặc định theo loại hook: `command`/`http`/`mcp_tool` = **600s**, `prompt` = 30s, `agent` = 60s. `SubagentStart` **không** nằm trong danh sách event bị hạ mặc định.
   - Ngược lại, `UserPromptSubmit` **bị hạ xuống 30s** (cùng `PreModelSwitch`, `PostModelSwitch`). Và khi `UserPromptSubmit` timeout: *"any `additionalContext`, is discarded. The prompt still reaches Claude without that context."* → **fail-open**: prompt vẫn đi qua, chỉ mất context; transcript hiện notice nêu tên hook + timeout. (Ngoại lệ: Agent SDK callback hook trên event này thì timeout **chặn** prompt, vì có thể đang làm policy gate — từ v2.1.208.)
   - **Đây là phát hiện quan trọng cho thiết kế cộng sinh:** hai hook `UserPromptSubmit` chạy song song trong cùng ngân sách 30s. Nếu hook nào chậm (đọc state, git, gọi python), nó tự mất context mà **không** báo lỗi rõ ràng. Ngân sách 30s là ngân sách phải chia sẻ về mặt tài nguyên máy, không phải 30s mỗi bên một cách thoải mái.

6. **Khả năng chặn, so sánh ba event:** `[XÁC THỰC]`
   | Event | Chặn được? | Exit 2 làm gì | stdout plain-text thành context? |
   |---|---|---|---|
   | `SessionStart` | Không | — | Có |
   | `UserPromptSubmit` | **Có** | Chặn xử lý prompt và **xoá prompt** | Có |
   | `SubagentStart` | Không | — | Chỉ qua `additionalContext` |
   → Chỉ `UserPromptSubmit` là điểm chặn thật. Nếu **cả hai plugin** đều dùng exit 2 ở đây làm gate, thì bên nào exit 2 trước sẽ xoá prompt của người dùng và bên kia mất tác dụng — **xung đột nghiêm trọng nhất trong toàn bộ bức tranh**, và không có cách dàn xếp bằng cấu hình.

7. `[XÁC THỰC]` Hai lưu ý phụ về `SessionStart`: (a) nó bắn **trước khi MCP server sẵn sàng**, kể cả với `--continue`/`--resume`; Claude Code **bỏ qua** các `mcp_tool` hook của event này. (b) Chỉ `SessionStart` mới có thể nhận field `model`, và *"Claude Code doesn't always include it"*. (c) `SessionStart` còn nhận thêm `initialUserMessage`, `watchPaths`, `sessionTitle`, `reloadSkills` — **các field này KHÔNG phải string cộng dồn**; hai plugin cùng set `initialUserMessage` hay `sessionTitle` là xung đột kiểu "một giá trị, hai người ghi", và tài liệu **không nói ai thắng** (`[CHƯA TÌM ĐƯỢC]`).

8. `[XÁC THỰC]` Hook chạy **cả bên trong subagent**: *"Hooks from settings files, managed policy settings, and plugins also run inside subagents. When a subagent calls a tool, tool events such as PreToolUse and PostToolUse fire the same configured hooks as in the main conversation."* → chi phí và trùng lặp nhân theo số subagent, không chỉ theo số session.

---

## Truy vấn 3 — Tiền lệ thực tế: hai bộ "always-on rules" cùng lúc

Truy vấn: `two AI coding agent rule files conflict AGENTS.md CLAUDE.md duplicate instructions precedence problem` + `Claude Code two plugins installed conflict overwrite generated AGENTS.md marketplace plugin interoperability namespace` (tavily-backup)

Nguồn:
- https://gist.github.com/0xdevalias/f40bc5a6f84c4c5ad862e314894b2fa6 (notes on AI Agent Rule/Instruction/Context files)
- https://modelbehaviors.substack.com/p/agentsmd-gets-it-wrong-in-2-ways (Josh Wand)
- https://github.com/microsoft/apm/issues/1120 (name collisions because plugins are deployed without namespacing)
- https://www.deployhq.com/blog/ai-coding-config-files-guide
- https://arxiv.org/html/2608.28497v1 (empirical study of Claude Code plugin marketplaces)
- https://promptarmor.substack.com/p/hijacking-claude-code-via-injected (bối cảnh an ninh hook plugin)

Điều suy ra:

1. **Vấn đề đã được đặt tên chính xác bởi cộng đồng.** `[BÊN-THỨ-BA]` Gist của 0xdevalias nêu đúng cái ta đang gặp: *"'same file copied to every tool' is not the same as compatibility. A `CLAUDE.md` loaded natively, a SessionStart hook injecting the same content, and a generated Cursor rule can all put similar bytes in context through different mechanisms. That's where duplicate context / token waste / surprising precedence bugs show up."* Và: *"the hard part is no longer 'which filename exists?' but 'what did this tool actually load, and with what semantics?'"*
   → Kết luận thiết kế: bài toán cộng sinh **không phải** bài toán nội dung luật, mà là bài toán **kênh nạp (loading channel)**. Cùng một luật vào context qua 2 kênh khác nhau = trả token 2 lần + tranh chấp ưu tiên khó debug.

2. **Cách giải quyết xung đột luật mà cộng đồng thực dùng — có ba mẫu, và chỉ một mẫu không tự bịa:** `[BÊN-THỨ-BA]`
   - (a) **Một nguồn sự thật + tham chiếu**: giữ một file gốc, các file tool-specific chỉ *reference* chứ không copy. deployhq nói thẳng: *"Maintain one source of truth (`AGENTS.md`) and have tool-specific files reference it. Don't copy-paste the same rules into `CLAUDE.md`, `.cursorrules`, and `copilot-instructions.md`."*
   - (b) **Phân tầng theo vai trò file**: AGENTS.md giữ context portable của project; CLAUDE.md chỉ giữ phần đặc thù Claude Code (compaction, subagent preference, permission override) — https://www.termdock.com/en/blog/claude-md-common-mistakes
   - (c) **Override file có tên riêng** (mẫu `AGENTS.override.md` / danh sách filename cấu hình được) — tồn tại ở một số tool khác, **không có ở Claude Code** (`[XÁC THỰC]` phản chứng: xem Truy vấn 4).
   - **KHÔNG tìm được** bất cứ "merge tool" chuẩn hay quy ước namespace nào cho rule file. `[CHƯA TÌM ĐƯỢC]` Không có công cụ hợp nhất rule được cộng đồng chấp nhận. Có công cụ *kiểm tra* tuân thủ (RuleProbe — https://dev.to/moonrunnerkc/same-instruction-file-same-score-completely-different-failures-46fp) nhưng đó là verify, không phải merge.

3. **Precedence "file gần nhất thắng" là mô hình duy nhất được spec hoá, và nó vỡ đúng ở ca của ta.** `[BÊN-THỨ-BA]` Josh Wand chỉ ra spec AGENTS.md giả định: chỉ có một file đang được sửa, có file đang được sửa, scope của rule file trùng directory nó nằm trong, và **không có mismatch giữa các file lồng nhau** (ví dụ cha: "chỉ viết functional test!", con: "chỉ viết unit test!"). Ca của ta là **hai nguồn ngang hàng ở CÙNG một directory (gốc project)** — mô hình proximity không phân xử được, vì khoảng cách bằng nhau.

4. **Tiền lệ collision ở tầng plugin: đã có, và cách xử lý là namespace.** `[BÊN-THỨ-BA]` microsoft/apm issue #1120: khi hai plugin định nghĩa skill cùng tên (`analyze`), *"the last-installed package silently overwrites the first. A warning is emitted, but there's no way to have both coexist."* Issue này đồng thời xác nhận đối chứng: *"Claude Code natively namespaces plugin commands and skills using a plugin:name convention. Plugin developers rely on this."*
   → Kết luận: Claude Code **đã** namespace skill/command/agent theo `plugin:name`. Phần **chưa** được namespace là (i) hook trên event dùng chung, và (ii) **file sinh ra trên đĩa** — `AGENTS.md` ở gốc project là tài nguyên toàn cục không có namespace. Đây chính xác là hai mặt trận xung đột của ta.

5. `[BÊN-THỨ-BA]` Bối cảnh rủi ro cần nhớ khi cài plugin bên thứ ba có `UserPromptSubmit` hook: PromptArmor đã trình diễn plugin dùng đúng hook đó để **ghi đè file permission** của Claude Code mỗi lần người dùng submit prompt. Không phải cáo buộc Ponytail, nhưng là lý do phải đọc và pin version hook của plugin ngoài chứ không auto-update mù.

---

## Truy vấn 4 — Chuẩn `AGENTS.md`: nhiều nguồn cùng ghi một file? include/compose?

Truy vấn: WebFetch `https://agents.md/` (spec gốc) + WebFetch `https://code.claude.com/docs/en/memory`

Nguồn:
- https://agents.md/ (spec AGENTS.md)
- https://code.claude.com/docs/en/memory (Claude Code memory — mục AGENTS.md, Import additional files, How CLAUDE.md files load)

Điều suy ra:

1. **Spec AGENTS.md KHÔNG nói gì về nhiều nguồn cùng ghi một file, KHÔNG có include, KHÔNG có compose, KHÔNG có merge.** `[XÁC THỰC — phản chứng]` Spec chỉ nói về **lồng theo thư mục**: *"Place another AGENTS.md inside each package. Agents automatically read the nearest file in the directory tree, so the closest one takes precedence"* và *"The closest AGENTS.md to the edited file wins; explicit user chat prompts override everything."*
   → Toàn bộ mô hình phân xử của spec là **proximity theo thư mục**. Với hai generator cùng ghi `./AGENTS.md`, spec **không có gì để nói**: về phía filesystem đó là một file, ai `Write` sau thì thắng tuyệt đối và nội dung bên kia biến mất. Đây không phải xung đột "luật với luật", mà là **xung đột ghi file, mất dữ liệu**.

2. **ĐIỂM QUYẾT ĐỊNH — Claude Code KHÔNG đọc AGENTS.md.** `[XÁC THỰC]` Nguyên văn: *"Claude Code reads `CLAUDE.md`, not `AGENTS.md`. If your repository already uses `AGENTS.md` for other coding agents, create a `CLAUDE.md` that imports it."*
   → Nghĩa là: việc cả hai plugin sinh `AGENTS.md` ở gốc project **tự nó không đưa gì vào context Claude Code**, trừ khi có `CLAUDE.md` import/symlink nó. Hai hệ quả:
   - (a) Nếu hai plugin trông vào AGENTS.md như kênh nạp luật của Claude Code, cả hai đều **đang sai cơ chế**, hoặc đang nạp qua kênh khác (hook `additionalContext`) và AGENTS.md chỉ là sản phẩm phụ cho tool khác. Cần kiểm chứng thực tế từng plugin.
   - (b) Tranh chấp AGENTS.md có thể **hạ cấp từ "xung đột luật" xuống "xung đột artifact"** — dễ giải hơn nhiều: tách file, hoặc một file + `@import`.

3. **Claude Code CÓ cơ chế compose, và nó là đường thoát sạch nhất.** `[XÁC THỰC]`
   - `@path/to/import` trong CLAUDE.md: file được import expand và nạp vào context lúc launch; cho cả path tương đối và tuyệt đối; **đệ quy tối đa 4 hop**; parser bỏ qua code span/fenced block (viết `` `@README` `` để không import). Mẫu chính thức được nêu trong tài liệu: `@AGENTS.md` ở đầu CLAUDE.md rồi thêm phần Claude-specific bên dưới.
   - Symlink `ln -s AGENTS.md CLAUDE.md` cũng được, nếu không cần thêm nội dung riêng cho Claude.
   - **Concat, không override**: *"All discovered files are concatenated into context rather than overriding each other. Across the directory tree, content is ordered from the filesystem root down to your working directory"*; trong cùng directory, `CLAUDE.local.md` được append **sau** `CLAUDE.md`. → **Thứ tự nạp rule file là XÁC ĐỊNH** (khác hẳn thứ tự hook). Đây là tài nguyên thiết kế quý: nếu chuyển tranh chấp từ tầng hook sang tầng rule file, ta đổi một cơ chế non-deterministic lấy một cơ chế deterministic.
   - `.claude/rules/*.md`: nhiều file, mỗi file một chủ đề, discover đệ quy, **rule không có `paths` frontmatter được nạp lúc launch với cùng priority như `.claude/CLAUDE.md`**; rule có `paths` chỉ nạp khi Claude đọc file khớp glob. `~/.claude/rules/` nạp **trước** project rules (project rules ưu tiên cao hơn). → **`.claude/rules/` là namespace tự nhiên cho hai bộ luật: mỗi plugin một file riêng, không ai ghi đè ai, thứ tự xác định, và có thể path-scope để giảm context cost.**
   - `claudeMdExcludes` (glob theo absolute path, **array merge across layers**, đặt được ở mọi settings layer) = van cắt chọn lọc ở tầng rule file. **Đối lập rõ với tầng hook, nơi chỉ có `disableAllHooks` kiểu tất-cả-hoặc-không.**

4. `[XÁC THỰC]` Cảnh báo về ngân sách: CLAUDE.md nên **dưới 200 dòng**; *"Longer files consume more context and reduce adherence"*; file > 4 MiB bị skip; và **import không giảm context** (*"imported files still load and enter the context window at launch"*). Hai bộ luật always-on cộng lại rất dễ vượt ngưỡng adherence. `[XÁC THỰC]` Thêm: *"if two rules contradict each other, Claude may pick one arbitrarily"* — chính thức xác nhận luật mâu thuẫn = hành vi tuỳ hứng, không có tie-break.

5. `[XÁC THỰC]` Cơ chế liên quan đáng biết cho kịch bản hợp nhất: `/import` (từ v2.1.213) *"appends a one-time copy of instruction files such as `AGENTS.md` to the matching `CLAUDE.md`"* và mang theo MCP server, command, subagent, skill. Và `/init` với `CLAUDE_CODE_NEW_INIT=1` đọc cả `AGENTS.md`, `.cursor/rules/`, `.windsurf/rules/`, `.clinerules`. → Có đường nhập chính thức, một chiều, một lần.

---

## Tổng hợp: cái gì XÁC THỰC, cái gì KHÔNG BIẾT

**Đã xác thực (thiết kế được dựa vào):**
- Mọi hook khớp đều chạy song song; bản copy của plugin không bị dedupe; không có API thứ tự; không có cách tắt chọn lọc hook của plugin khác (chỉ `disableAllHooks` toàn bộ, hoặc disable cả plugin).
- `SubagentStart`: không chặn được, chỉ inject `additionalContext` vào đầu hội thoại subagent, timeout 600s (command), matcher theo agent type **và hỗ trợ regex namespace plugin** → đây là cơ chế cách ly duy nhất được document ở tầng hook.
- `UserPromptSubmit` là điểm chặn duy nhất trong ba event (exit 2 = xoá prompt), timeout mặc định hạ xuống 30s, timeout thì fail-open bỏ `additionalContext`.
- Claude Code đọc `CLAUDE.md` chứ **không** đọc `AGENTS.md`. Rule file được **concat theo thứ tự xác định**, có `@import` (4 hop), có `.claude/rules/` với path-scope, có `claudeMdExcludes` cắt chọn lọc.
- Spec AGENTS.md chỉ phân xử bằng proximity thư mục; không có include/compose/merge; không nói gì về nhiều nguồn ghi cùng một file.

**KHÔNG tìm được câu trả lời (phải tự đo, không được đoán bù):**
- `additionalContext` từ nhiều hook cùng một event: **nối hay ghi đè?** Tài liệu im lặng hoàn toàn. Đã kiểm 2 lần.
- Thứ tự thực tế các hook cùng event (tài liệu chỉ nói "parallel", không nói gì thêm).
- Ai thắng khi hai `SessionStart` hook cùng set field **non-string**: `initialUserMessage`, `sessionTitle`, `watchPaths`, `reloadSkills`.
- Có "merge tool" hay quy ước namespace chuẩn cho rule file: không tồn tại trong cộng đồng.
- Bug #10871 (hook plugin chạy 2 lần) đã fix ở version nào: không tìm được thông tin đóng issue.

**Cần đo bằng thực nghiệm trước khi lập spec** (đề xuất: hai hook `SessionStart` giả, mỗi hook in một marker riêng; rồi `/context` + `InstructionsLoaded` hook + `/hooks` để đọc kết quả thật):
1. Hai `additionalContext` → context cuối chứa một marker hay hai?
2. Hook plugin có chạy 2 lần trên version Claude Code đang dùng không?
3. Hook `UserPromptSubmit` của plugin có thực sự execute không (issue #10225)?
