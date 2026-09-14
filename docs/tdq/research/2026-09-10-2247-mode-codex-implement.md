# RESEARCH — Mode implement thứ ba: leader Claude Code → sub-agent Claude → `codex exec` trong worktree riêng
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-09-10 · Request: `2026-09-10-2247-mode-codex-implement` · Công cụ: Tavily (`tavily-primary`), 6 truy vấn.
Quy ước ghi nguồn: **[CHÍNH THỨC]** = docs OpenAI/ChatGPT Learn hoặc issue/PR trên `openai/codex`; **[KINH NGHIỆM]** = blog/gist/reddit/bên thứ ba; **[KHÔNG TÌM ĐƯỢC]** = đã tìm mà không có nguồn.

## Góc 1 — `codex exec` trong tự động hoá: approval, sandbox, output-schema, exit code

Truy vấn: `Codex CLI codex exec non-interactive automation CI approval_policy sandbox_mode workspace-write --output-schema JSON exit code`

Nguồn:
- https://learn.chatgpt.com/docs/non-interactive-mode — **[CHÍNH THỨC]** (docs "Non-interactive mode")
- https://github.com/openai/codex/discussions/7740 — **[CHÍNH THỨC-ish]** (discussion trong repo openai/codex)
- https://gist.github.com/alexfazio/359c17d84cb6a5af12bac88fa1db9770 — **[KINH NGHIỆM]** (81 thí nghiệm flag trên exec mode, có retest v0.114.0)
- https://www.developersdigest.tech/blog/codex-exec-ci-headless-guide, https://continuumcode.ai/guides/codex-cli, https://majesticlabs.dev/blog/202607/codex-cli-configuration-guide, https://smartscope.blog/en/generative-ai/chatgpt/codex-cli-approval-modes-no-approval — **[KINH NGHIỆM]**
- https://blakecrosley.com/blog/codex-untrusted-approval-policy-retired — **[KINH NGHIỆM]** dẫn lại PR #39630 (v0.149.0)

Suy ra được gì:
1. **`codex exec` vốn đã ép `approval: never`** — gist đo trên exec mode: đặt `approval_policy=on-request` (qua `-c` hay `-a`) thì stderr vẫn in `approval: never`, vì exec không có TTY để hỏi. **[KINH NGHIỆM, nhưng khớp docs]**: docs non-interactive khuyên đúng giá trị `never` cho chạy không người trực. → Cờ `-c approval_policy="never"` ta đang dùng là *thừa nhưng vô hại*, giữ lại để tường minh và chống trường hợp config user khác.
2. **`approval_policy` chỉ còn 3 giá trị**: `untrusted` bị khai tử ở v0.149.0 (PR #39630) và cấu hình còn khai `untrusted` sẽ **fail với lỗi rõ ràng** — ta đang ở 0.154.0 nên tuyệt đối không sinh ra `untrusted` ở bất kỳ đâu. `sandbox_mode`: `read-only` | `workspace-write` | `danger-full-access`. **[KINH NGHIỆM dẫn PR chính thức]**
3. **Mặc định của `codex exec` là `read-only`** (nhiều nguồn đồng thuận) → bắt buộc truyền `-s workspace-write`, khớp với thứ ta đã đo. `--full-auto` là compat cũ, in cảnh báo deprecate → **không dùng**. **[KINH NGHIỆM]**
4. **`--output-schema <file.json>` là tính năng chính thức** để ép khuôn JSON câu trả lời cuối, dùng chung với `-o <path>` để ghi ra file. Docs nêu đúng ca dùng của ta: "structured data for downstream steps… stable fields (job summaries, risk reports)". **[CHÍNH THỨC]** → **đáng tin để làm giao thức báo cáo task giữa Codex và sub-agent Claude**, thay cho việc parse văn xuôi. Schema nên `additionalProperties: false` + `required` đầy đủ (đúng như ví dụ docs).
5. **Luồng I/O tách rõ**: tiến trình phát progress ra **stderr**, message cuối ra **stdout**, `--json` cho JSONL sự kiện máy đọc, `-o/--output-last-message <path>` ghi message cuối ra file. **[CHÍNH THỨC + KINH NGHIỆM]** → sub-agent Claude nên đọc file `-o` (đã dùng `-o last.txt`) chứ đừng scrape stdout, và nếu cần theo dõi tiến độ thì bật `--json` ghi ra file log riêng.
6. **Hai cờ cách ly cấu hình rất đáng dùng**: `--ignore-user-config` (không nạp `$CODEX_HOME/config.toml`) và `--ignore-rules` (bỏ qua `.rules` execpolicy của user/project) — docs nói thẳng là dành cho "controlled automation environment". **[CHÍNH THỨC]** → đây là đòn bẩy để mode mới **không bị config cá nhân của người dùng làm lệch**; nhưng lưu ý nó cũng bỏ luôn cấu hình ta muốn (xem góc 2: nếu ta dựa vào `config.toml` để bật hooks thì KHÔNG được dùng `--ignore-user-config`).
7. **MCP `required = true` làm exec exit lỗi** nếu server không init được. **[CHÍNH THỨC]** → nếu prompt Codex không cần MCP thì đừng bật MCP required trong CODEX_HOME của mode này.
8. **Exit code cho máy đọc**: nguồn chỉ nói mức "exits cleanly, chain được với grep/jq" và ca MCP required → exit lỗi. **Bảng mã exit cụ thể (0/1/2/timeout) thì KHÔNG TÌM ĐƯỢC** trong docs. → Thiết kế không được dựa duy nhất vào exit code: phải xác minh bằng *hiệu ứng thật* (git diff/status trong worktree + test chạy lại) cộng với JSON `--output-schema`.

## Góc 2 — Hooks của Codex CLI: schema, event, matcher, hook trust

Truy vấn: `Codex CLI hooks .codex/hooks.json PreToolUse matcher shell apply_patch hook trust --dangerously-bypass-hook-trust`

Nguồn:
- https://learn.chatgpt.com/docs/hooks — **[CHÍNH THỨC]**
- https://github.com/openai/codex/issues/32491 — **[CHÍNH THỨC]** (bug: exec bỏ qua trust đã persist)
- https://agenticcontrolplane.com/blog/codex-cli-hooks-reference, https://symposium.dev/design/agent-details/codex-cli.html, https://aicatchup.com/news/codex-hooks-programmatic-access-tokens, https://blakecrosley.com/blog/codex-hooks-make-the-harness-real — **[KINH NGHIỆM]**
- https://github.com/falcosecurity/prempti/blob/main/hooks/codex/README.md — **[KINH NGHIỆM]** (một dự án security thật đang mount hook vào Codex)

Suy ra được gì:
1. **Schema `.codex/hooks.json` của ta đúng dạng**: `{"hooks": {"<Event>": [{"matcher": "...", "hooks": [{"type": "command", "command": "...", "timeout": N}]}]}}`. Chỉ `type: "command"` thực thi (`prompt`/`agent` được parse nhưng bỏ qua). `matcher` là **regex khớp `tool_name` + alias**; bỏ trống hoặc `"."` là khớp tất cả. Hook user (`~/.codex/hooks.json`) và project (`<repo>/.codex/hooks.json`) **cộng dồn**, cả hai đều chạy. Ngữ cảnh truyền qua **stdin JSON**, có field `cwd`; **không có biến env kiểu `CLAUDE_PROJECT_DIR`**. **[CHÍNH THỨC cho schema/matcher; KINH NGHIỆM cho chi tiết cộng dồn/không env]**
2. **Matcher canonical: `Bash`, `apply_patch` (và `apply_patch` khớp luôn alias `Edit`/`Write`), tên MCP `mcp__server__tool`** — docs hooks nói đúng như vậy. **[CHÍNH THỨC]** → hai matcher trong bản mẫu `portable_codex/.codex/hooks.json` (`apply_patch`, `Bash`) **là tên có thật, không phải bịa**. Không có matcher tên `shell`; "shell tool" là cách gọi nội bộ, matcher là `Bash`.
3. **Event có thật**: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PermissionRequest`, `PostToolUse`, `Stop` (+ các event khác, một nguồn nói tổng 11 lifecycle event). **[CHÍNH THỨC cho danh sách trên; con số 11 là KINH NGHIỆM]** → bản mẫu của ta dùng `SessionStart`/`UserPromptSubmit`/`PreToolUse`/`Stop` đều hợp lệ. `PermissionRequest` **không chạy khi approval là `never`** (nó chỉ chạy khi Codex định hỏi) → **vô dụng cho mode này**, đừng trông vào nó.
4. **`PreToolUse` của Codex chỉ có quyền `deny`** — `allow`/`ask`/`updatedInput` được parse nhưng **bị từ chối** ở runtime. **[KINH NGHIỆM, nhiều nguồn đồng thuận]** → gate của ta phải thiết kế theo *một quyết định duy nhất: deny + reason*. Không thể rewrite đường dẫn, không thể "ask người dùng".
5. **Cạm bẫy nặng nhất — độ phủ tool không chắc chắn**: docs hooks nói `PreToolUse` thấy shell (`Bash`), unified exec, `apply_patch` (alias `Edit`/`Write`), MCP tool; nhưng một nguồn phân tích **[KINH NGHIỆM]** khẳng định thực tế hiện tại `PreToolUse` chỉ phủ shell tool và khuyên "diễn đạt mọi sửa file qua shell vì hook bắt chắc đường Bash", còn `symposium.dev` cũng ghi "chỉ Bash event bắn PreToolUse". Thêm nữa: `write_stdin` **không** chạy lại `PreToolUse` cho command đã pass, và hosted tool (WebSearch) không đi qua hook local. → **Kết luận thiết kế**: gate `Bash` là đường phòng thủ *chính* (và ta đã đo được Codex ghi file bằng `/bin/zsh -lc "printf … > file"`, tức đi qua đúng đường này); gate `apply_patch` là *bổ sung*, phải coi như **có thể không bắn**. Không được coi hook là hàng rào duy nhất.
6. **Hook trust chặn đúng ca của ta**: hook project không tự chạy — phải được trust (qua `/hooks` trong TUI) hoặc đến từ nguồn managed (MDM/cloud/`requirements.toml`). Docs: "cannot ship a security hook to a team by dropping it in a repo and assuming it is active". Cho tự động hoá đã tự vet nguồn, **`--dangerously-bypass-hook-trust` chạy các hook đang enable mà không cần trust đã persist** (đúng một lần gọi). **[CHÍNH THỨC]**
7. **Và có bug đã ghi nhận**: issue #32491 (0.144.1) — `codex exec` **bỏ qua trust đã persist**, hook project chỉ chạy khi truyền `--dangerously-bypass-hook-trust`, dù `hooks/list` báo `enabled: true, trustStatus: trusted`. **[CHÍNH THỨC — issue mở]** → Nếu mode mới muốn hook gate chạy, **phải truyền `--dangerously-bypass-hook-trust` mỗi lần gọi `codex exec`**, không thể trông vào việc trust một lần. (Chưa kiểm tra được issue đã fix ở 0.154.0 hay chưa → **cần đo trên máy**, và dù fix rồi thì truyền cờ vẫn an toàn.)
8. **Có thể phải bật feature flag**: hai nguồn nói hooks là experimental, **tắt mặc định**, bật bằng `[features] codex_hooks = true` trong `config.toml`, và không có trên Windows; một nguồn khác (mới hơn) nói "hooks enabled by default". **[KINH NGHIỆM — MÂU THUẪN]** → phải đo thực tế trên 0.154.0; và nếu cần flag trong `config.toml` thì **không được dùng `--ignore-user-config`**, phải bơm flag qua `CODEX_HOME` riêng của mode (xem góc 3) hoặc qua `-c features.codex_hooks=true`.
9. **Đường phòng thủ thay cho hook — sandbox writable roots**: `[sandbox_workspace_write]` có `writable_roots`, `network_access`, `exclude_slash_tmp`, `exclude_tmpdir_env_var`; v0.100.0+ có `read_only_access` để giới hạn cả vùng đọc. Có nguồn còn nêu bảng `[permissions.<profile>.filesystem]` với giá trị `write`/`read`/`none` theo glob (ví dụ `"/.env" = "none"`) và execpolicy `.rules` với `decision = "prompt"`. **[KINH NGHIỆM]** — cú pháp permissions/rules này **không xác nhận được trong docs chính thức qua các truy vấn đã chạy**. → Hướng đúng cho hàng rào file-scope: **cách ly bằng worktree + sandbox `workspace-write` giới hạn ở đúng worktree đó** (OS-level, Codex không bypass được), rồi **kiểm hậu kiểm bằng `git status/diff` so với vùng file đã khai** ở phía sub-agent Claude/leader. Hook chỉ là lớp phát hiện sớm.
10. **Lịch sử sandbox từng có CVE**: CVE-2025-59532 — Codex ≤0.38.0 coi `cwd` do model sinh ra là writable root, vá ở 0.39.0 bằng canonicalize theo nơi user khởi động session. **[CHÍNH THỨC — advisory]** → củng cố: hãy để `-C <worktree>` do leader truyền, đừng để prompt/model quyết định cwd; và pin/ghi lại version Codex trong log.

## Góc 3 — Chạy nhiều `codex exec` song song: xung đột `$CODEX_HOME`

Truy vấn: `multiple parallel codex exec processes concurrently CODEX_HOME lock sqlite session history conflict --ephemeral`

Nguồn:
- https://github.com/openai/codex/issues/11435 — **[CHÍNH THỨC]** "Multiple parallel codex exec instances interfere via shared session restore"
- https://github.com/openai/codex/issues/20213 — **[CHÍNH THỨC]** "Multi-terminal codex CLI freezes due to SQLite lock contention with no BUSY retry"
- https://github.com/openai/codex-plugin-cc/issues/382 — **[CHÍNH THỨC]** (repo OpenAI) "Concurrent sessions race on shared ~/.codex — app-server spawned without an isolated CODEX_HOME", dẫn thêm codex#14233, codex#10887
- https://youtrack.jetbrains.com/issue/AIR-5634 — **[KINH NGHIỆM]** (JetBrains Air: một `CODEX_HOME` dùng chung → lỗi migration sqlite)
- https://nimbalyst.com/blog/how-to-run-multiple-codex-agents-in-parallel, https://www.codeagentswarm.com/en/guides/run-multiple-codex-sessions — **[KINH NGHIỆM]**

Suy ra được gì:
1. **Đây là rủi ro số 1 của thiết kế song song, và nó có thật, đã được ghi nhận**: nhiều `codex exec` chạy đồng thời **đọc/khôi phục session của nhau** → "prompt của instance A xuất hiện trong instance B", hỏi resume ngoài ý muốn, fail phi tất định trong CI. **[CHÍNH THỨC — issue #11435, mở từ 0.98.0]**
2. **`~/.codex` không an toàn cho nhiều tiến trình ghi**: issue #382 liệt kê chính xác các file bị mutate đồng thời — `.codex-global-state.json` (ghi kiểu temp+rename, để lại rác `.tmp-…` khi bị clobber), `state_5.sqlite(-wal/-shm)`, `logs_2.sqlite`, `goals_1.sqlite`, `memories_1.sqlite`, `session_index.jsonl`, `models_cache.json`, `shell_snapshots/`. Issue #20213: contention trên `state_5.sqlite`/`logs_2.sqlite` **không có retry SQLITE_BUSY** → treo/deadlock, chỉ ctrl-C cứu được. **[CHÍNH THỨC]**
3. **Cách chữa được chính repo OpenAI xác nhận là đúng hướng: `CODEX_HOME` riêng cho mỗi tiến trình.** Issue #382 gọi "per-workspace isolation" là fix shippable, còn advisory lock/`CODEX_STATE_HOME` là fix sâu nhưng chưa có. **[CHÍNH THỨC]** → **Thiết kế phải cấp `CODEX_HOME=<dir riêng>` cho từng sub-agent** (ví dụ `<scratch>/codex-home/<task-id>`), copy sẵn `config.toml` tối thiểu + auth vào đó.
4. **`--ephemeral` tồn tại và chỉ có ở `exec`** (issue #382 nói rõ: "`codex exec --ephemeral` exists but only for `exec`"), và một guide **[KINH NGHIỆM]** liệt kê nó trong nhóm cờ hành vi của exec. → Ta *chạy đúng `exec`* nên dùng được. Nhưng **ngữ nghĩa chính xác của `--ephemeral` (có bỏ ghi session/history/sqlite hay không) thì KHÔNG TÌM ĐƯỢC tài liệu** → phải coi là *bổ trợ*, không thay thế `CODEX_HOME` riêng, và phải đo `codex exec --help` trên 0.154.0.
5. **Ghi chú thêm**: `[history] persistence = "none"` là công tắc chính thức có trong config mẫu **[KINH NGHIỆM]** → đáng đặt trong `config.toml` của CODEX_HOME riêng để giảm ghi chung.
6. **Auth dùng chung**: mỗi `CODEX_HOME` riêng sẽ **không có sẵn login** (`CODEX_HOME` relocate cả root, "how you run two accounts" — **[KINH NGHIỆM]**). → Phải copy file auth từ `~/.codex` sang, hoặc dùng API key qua env. Đây là một task thật trong plan, không phải chi tiết nhỏ.
7. **Worktree là bắt buộc, không phải tuỳ chọn**: mọi nguồn kinh nghiệm hội tụ "hai agent trong cùng một checkout là mất việc". Cũng khuyên **giới hạn số session đồng thời** và viết `AGENTS.md` mạnh ở gốc repo vì mỗi session Codex đọc nó lúc khởi động. **[KINH NGHIỆM]** → nên có tham số cap song song (ví dụ 2–4) và một `AGENTS.md` (hoặc file brief per-task) mang luật vùng-file thay vì nhồi hết vào prompt.
8. **Version skew làm hỏng state**: JetBrains AIR-5634 — `state_5.sqlite` do binary khác ghi → `app-server` fail "migration 1 … has been modified". **[KINH NGHIỆM]** → thêm lý do nữa để `CODEX_HOME` của mode này là thư mục **do ta tạo mới**, không dùng chung với `~/.codex` của người dùng.

## Góc 4 — Kinh nghiệm cho một agent CLI điều khiển agent CLI khác

Truy vấn: `orchestrate Codex CLI from Claude Code subagent pitfalls timeout streaming output lost context verify result` và `Claude Code orchestrating codex exec pitfalls lessons learned`

Nguồn (tất cả **[KINH NGHIỆM]**, không có docs chính thức nào cho pattern này):
- https://madewithlove.com/blog/claude-up-front-codex-in-the-back
- https://www.xda-developers.com/claude-orchestrating-codex-agents
- https://www.abdelaziznotes.com/posts/stop-letting-llms-orchestrate-your-ai-agents
- https://github.com/shinpr/sub-agents-skills
- https://nimbalyst.com/blog/orchestrating-claude-code-and-codex-together
- https://www.sitepoint.com/codex-53-production-workflow-vs-claude-complex-refactoring

Suy ra được gì:
1. **"Codex báo tests pass" không phải bằng chứng.** Bài xda ghi đúng cái bẫy này và nói phần quan trọng nhất trong thiết kế plugin của họ là *Claude chạy lại chính các kiểm tra đó và tự quan sát kết quả*. → **Bắt buộc**: sau mỗi `codex exec`, sub-agent Claude tự chạy test/validate của task trong worktree đó và tự đọc `git diff --stat` + danh sách file thay đổi; chỉ khi đó mới tick `[x]`.
2. **Chi phí orchestration là thật và lệch nặng về phía leader.** Đo của xda: Claude ~9M token vs Codex ~1.2M (≈8x cho orchestrator). madewithlove: overhead orchestration ~5–7K token mỗi round-trip, và có ca "wrapper tốn hơn cả việc" → *pattern này không dành cho task nhỏ*. → Mode mới nên có **ngưỡng áp dụng** (task đủ lớn: nhiều file, cần đọc repo, cần chạy test) và leader phải phát prompt **cô đặc** (đường dẫn + DoD + vùng file), không dán cả spec.
3. **Timeout phải đặt tường minh và dài.** `shinpr/sub-agents-skills` (bộ orchestrator đa CLI thật) đặt `--timeout` default **600000ms = 10 phút**; mục troubleshooting đầu tiên của họ là "timeout errors or authentication failures". → Thiết kế cần: timeout per-task cấu hình được (mặc định ≥10 phút), và phân biệt rõ **timeout** vs **fail** vs **deny bởi gate** trong log.
4. **Thu hồi output của subagent là điểm dễ mất dữ liệu nhất.** abdelaziznotes đo "background output loss ~40%": trong một session 5 agent, 2/5 lỗi thu output (một trả rỗng, một trả JSON thô thay vì summary), và **orchestrator có thể không nhận ra mình thiếu gì**. → Củng cố quyết định ở góc 1: **kênh kết quả phải là file trên đĩa** (`-o` + `--output-schema`, cộng log `--json`), và leader phải **kiểm tra sự tồn tại + parse được** của file đó, coi "thiếu file/parse fail" là FAIL rõ ràng thay vì im lặng bỏ qua.
5. **Hai lớp dịch prompt làm lệch ý và mất tính tái lập.** madewithlove liệt kê: prompt qua 2 lớp (Claude soạn → Codex bọc) mỗi lớp lệch một chút; **hành vi ẩn** (Codex có thể âm thầm kích skill, tuân `AGENTS.md`, hoặc từ chối vì guardrail mà ta không biết nếu không đào log); cùng một prompt chạy 2 lần có thể đi 2 đường. → Thiết kế cần: **ghi nguyên văn prompt đã gửi cho Codex vào log service** (đúng luật "log service bật mặc định" của TDQ), giữ `--json` log để truy hành vi ẩn, và **không** giả định tính tái lập.
6. **Đừng để một agent vừa review vừa sửa; và một file luật, không hai.** nimbalyst: "giving the reviewing agent write access → nó sẽ sửa thay vì báo, và bạn mất bài review"; đồng thời cảnh báo hai file chỉ dẫn (`CLAUDE.md` vs `AGENTS.md`) **drift trong hai tuần** và drift đó vô hình — cách chữa: lấy `AGENTS.md` làm nguồn, `CLAUDE.md` import bằng `@AGENTS.md`. → Trong mode mới: QC vẫn do agent **read-only** làm (đúng `tdq-qc-tester` hiện có, không cho Codex tự QC chính mình); và luật vùng-file/test-command nên có **một nguồn duy nhất** mà cả Claude và Codex cùng đọc.
7. **Prompt mơ hồ → Codex sửa lan.** sitepoint: prompt kiểu "clean up the auth module" cho Codex quá nhiều tự do và sinh refactor ngoài ý; test flaky càng tệ (Codex sẽ sửa code không liên quan để chữa test chập chờn, loop không hội tụ). → Prompt phát cho Codex phải nêu: **danh sách file được phép sửa, lệnh test chính xác, và "không sửa gì khác"**; và phải xác nhận test của task không flaky trước khi phát.
8. **KHÔNG TÌM ĐƯỢC**: tài liệu chính thức của OpenAI hay Anthropic về pattern "agent CLI gọi agent CLI khác" (không có trang docs nào; tất cả là blog/skill cộng đồng). Cũng **không tìm được** báo cáo nào về ca cụ thể *sub-agent Claude Code trong git worktree gọi `codex exec` + hook gate* — thiết kế này là đất mới, nên phải tự đo và tự log.

## Việc phải đo trên máy trước khi lập plan (do research không kết luận được)
1. `codex exec --help` trên 0.154.0: có `--ephemeral`? có `--dangerously-bypass-hook-trust`? có `--ignore-user-config` / `--ignore-rules` / `--output-schema` / `--json`?
2. Hooks có cần `[features] codex_hooks = true` ở 0.154.0 không (hai nguồn mâu thuẫn).
3. Issue #32491 còn không: `.codex/hooks.json` project có bắn khi `codex exec` **không** truyền `--dangerously-bypass-hook-trust`?
4. `PreToolUse` matcher `apply_patch` có thực bắn trong exec mode không (bắt Codex sửa file bằng patch thay vì `printf >`), hay chỉ `Bash` bắn.
5. Hai `codex exec` song song với `CODEX_HOME` riêng: có còn hiện tượng session-restore lẫn nhau / treo sqlite?
6. Bảng exit code thật của `codex exec` cho các ca: thành công, bị hook deny, timeout, MCP required fail.
