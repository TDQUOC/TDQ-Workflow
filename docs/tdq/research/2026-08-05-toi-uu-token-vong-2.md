# Research: Tối ưu token vòng 2 — biện pháp lâu dài cho agentic workflow

Request: `2026-08-05-toi-uu-token-vong-2`. Vòng 1 đã làm mẹo một lần (gộp bash, lint đúng file, CLI 1 dòng, test theo module, giao research cho subagent). Vòng 2 tìm biện pháp **đổi cấu trúc/luật**.

## 1. Context engineering chính thức của Anthropic

**Truy vấn:** `Anthropic context engineering agents just-in-time retrieval compaction structured note-taking`

**Nguồn:**
- https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents (bài kỹ thuật chính thức, anthropic.com/engineering)
- https://console.anthropic.com/docs/en/agents-and-tools/tool-use/memory-tool (docs chính thức, memory tool)
- https://platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools (cookbook chính thức)

**Điều rút ra:**
- Anthropic dùng đúng 3 kỹ thuật cho long-horizon work: **compaction, structured note-taking, sub-agent architecture** — không có kỹ thuật thứ 4.
- Context window luôn bị "context pollution" dù có mở rộng cỡ nào — nghĩa là fix cấu trúc quan trọng hơn chờ context window lớn hơn.
- "Clearing tool calls and results" (xoá kết quả tool cũ khỏi context) được gọi là "one of the safest, lightest touch forms of compaction" — vì tool đã gọi sâu trong lịch sử thì model không cần thấy raw result nữa.
- Just-in-time retrieval: 3 pattern cụ thể — (a) lightweight identifiers (truyền ID thay vì object đầy đủ, agent tự gọi lại khi cần), (b) progressive disclosure (list file → metadata → nội dung), (c) autonomous exploration (cấp tool khám phá thay vì dump toàn bộ dữ liệu).
- Memory tool (docs chính thức): "Memory supports just-in-time context retrieval... keeps the active context focused on the current task" — dùng chung với compaction: "compaction keeps the active context small without client-side bookkeeping, and memory preserves the information that must survive summarization."

## 2. Claude Code context editing / tool-result clearing / `/compact` vs `/clear`

**Truy vấn:** `Claude Code context editing tool result clearing /compact /clear 2026`

**Nguồn:**
- https://platform.claude.com/docs/en/build-with-claude/context-editing (docs chính thức — cơ chế `clear_tool_uses_20250919`, `compact_20260112`)
- https://platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools (cookbook, ví dụ config)

**Điều rút ra:**
- API có 2 cơ chế tách biệt qua beta header: **context editing** (`context-management-2025-06-27`) xoá tool result/thinking block cũ phía client-controlled bằng config; **compaction** (`compact_20260112`) tóm tắt cả conversation phía server khi gần giới hạn context window.
- Config mẫu cho tool-result clearing: `trigger: {type: "input_tokens", value: 150000}`, `keep: {type: "tool_uses", value: 6}`, `clear_at_least: {type: "input_tokens", value: 30000}`, `exclude_tools: [...]` — nghĩa là có thể set ngưỡng token, giữ N tool call gần nhất, và loại trừ tool quan trọng (vd. memory) khỏi việc bị xoá.
- **Cảnh báo quan trọng cho cache:** "Tool result clearing: Invalidates cached prompt prefixes when content is cleared... You'll incur cache write costs each time content is cleared" — nên dùng `clear_at_least` để mỗi lần xoá đủ lớn mới bõ trả phí ghi cache lại.
- Best practice cộng đồng (nhiều nguồn đồng thuận): dùng `/clear` khi **chuyển task khác hẳn** (đổi feature, đổi layer, agent đi sai hướng) — tránh dựa vào auto-compact; dùng `/compact` khi vẫn task đó nhưng gần giới hạn context.
- Claude Code trigger auto-compact ở ~75% context utilization (không đợi đầy hẳn) để còn "headroom" hoàn thành task.
- CLAUDE.md quá to (vd. 55KB) làm session compact liên tục và bị model tự hạ ưu tiên nội dung — giải pháp cộng đồng: tách thành `learnings/` từng file riêng theo tool, agent `ls`/`grep`/`cat` theo nhu cầu thay vì load hết — giảm 55KB → 24KB mà giữ nguyên nội dung.

## 3. Prompt caching — cách tính phí cache_read, TTL, invalidation

**Truy vấn:** `Anthropic prompt caching cache_read pricing percentage TTL 5 minute 1 hour invalidation` + `docs.claude.com prompt caching pricing 5 minute 1 hour cache write multiplier official`

**Nguồn:**
- https://platform.claude.com/docs/en/about-claude/pricing (docs giá chính thức)
- https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-use-with-prompt-caching (docs chính thức)

**Điều rút ra (số liệu chính thức):**
- Multiplier cố định trên mọi model hiện hành: **cache write 5 phút = 1.25× giá input gốc; cache write 1 giờ = 2× giá input gốc; cache read (hit) = 0.1× giá input gốc** (giảm 90%).
- Hoà vốn: cache 5 phút chỉ cần **1 lần đọc lại** là đã lời so với không cache; cache 1 giờ cần **≥2 lần đọc lại** mới hoà vốn — vậy nếu route/skill chỉ dùng 1 lần trong phiên, KHÔNG nên set TTL 1 giờ.
- Cache bị **invalidate hoàn toàn** nếu prefix thay đổi dù chỉ 1 ký tự/khoảng trắng — cache khớp theo tiền tố token chính xác, không phải theo nội dung ngữ nghĩa. Đổi model giữa chừng (vd. Sonnet ↔ Opus) hoặc đổi `effort` cũng invalidate cache vì KV-cache theo từng model.
- Tool-result clearing (mục 2) tự nó làm invalidate cache tại điểm bị xoá — đánh đổi giữa "context nhỏ" và "giữ cache ấm" phải cân nhắc cùng nhau, không tách rời.
- Kết quả server tool (web search, web fetch, code execution) được **tự động** đặt breakpoint cache 5 phút, độc lập với TTL mình set thủ công.
- Cộng đồng ghi nhận sự cố: đầu tháng 3/2026 Anthropic đổi default TTL nền tảng từ 1 giờ về lại 5 phút, gây tăng 20–32% chi phí cache-creation cho ai không biết — dẫn chứng từ việc parse 119.866 API call thực tế (nguồn: keepmyprompts.com, digitalapplied.com). Bài học: đừng giả định TTL mặc định, phải set tường minh và kiểm tra `cache_creation_input_tokens`/`cache_read_input_tokens` trong response.

## 4. Giảm số API call / tool call — batching, code execution thay vì tool call, progressive disclosure

**Truy vấn:** `reduce tool calls agent loop batching code execution MCP instead of tool calls`

**Nguồn:**
- https://www.anthropic.com/engineering/code-execution-with-mcp (bài kỹ thuật chính thức Anthropic)
- https://github.com/modelcontextprotocol/modelcontextprotocol/discussions/1780 (thảo luận chính thức MCP org, có benchmark cộng đồng)
- https://www.getmaxim.ai/articles/code-execution-with-mcp-how-code-mode-cuts-agent-token-costs-by-90 (phân tích thứ cấp, số liệu dẫn lại từ Anthropic)

**Điều rút ra:**
- Anthropic khuyến nghị: khi có sandbox code-execution, expose MCP server như **code API** thay vì gọi tool trực tiếp — agent viết code (loop, điều kiện, xử lý dữ liệu) trong sandbox, chỉ kết quả cuối mới vào context.
- Ví dụ định lượng chính thức từ Anthropic: workflow Google Drive → Salesforce giảm từ **150.000 token xuống 2.000 token (giảm 98.7%)** khi chuyển từ chuỗi tool call sang 1 đoạn code chạy trong sandbox.
- Cơ chế: agent chỉ load tool cần dùng (progressive disclosure qua file-tree các tool khả dụng) thay vì nhồi hết định nghĩa tool + toàn bộ kết quả trung gian vào context; dữ liệu trung gian ở lại execution environment.
- Đánh đổi: cần sandbox có cách ly (sandboxing, resource limit, giám sát) — thêm overhead vận hành, không miễn phí.
- Benchmark cộng đồng độc lập (thảo luận MCP GitHub #1780): khi 1 lần gọi MCP trả về nhiều artifact, loop code-execution ngắn hơn **11–15×** so với loop gọi tool `Write` từng file một.

## 5. Viết CLI/script cho agent tiêu thụ

**Truy vấn:** `Claude agent skills progressive disclosure design CLI for agent consumption quiet json output`

**Nguồn:**
- https://www.speakeasy.com/blog/engineering-agent-friendly-cli
- https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive (deep dive kỹ thuật về cơ chế Skill tool trong Claude Code)

**Điều rút ra:**
- Pattern CLI agent-friendly cụ thể: `speakeasy run --quiet --output json` — `--quiet` tắt spinner/progress/log rườm rà, `--output json` trả đúng status + đường dẫn/lỗi liên quan, không in lại nội dung. Tự động giảm độ "chatty" khi phát hiện flag `--non-interactive`.
- Skill (SKILL.md) là cơ chế progressive disclosure 3 lớp có sẵn trong Claude Code: (1) chỉ tên+description load vào context lúc khởi động, (2) full SKILL.md load khi được chọn, (3) file reference/script chỉ load khi thực thi bước đó — do đó tách hướng dẫn dài ra `references/*.md` thay vì nhồi hết vào SKILL.md chính là cách giảm token đúng cấu trúc, không phải mẹo.
- Nguyên tắc thiết kế skill từ Vercel (trích lại qua Speakeasy): **skill tập trung, hẹp phạm vi (focused) hiệu quả hơn skill ôm đồm (comprehensive)**.
- Với CLI/script nội bộ (không phải public), cùng nguyên tắc áp dụng được: script nên có mode im lặng mặc định, in JSON/1-dòng khi chạy dưới agent, exit code rõ ràng thay vì agent phải đọc log để suy luận thành công/thất bại.

## 6. Kinh nghiệm thực chiến cộng đồng 2026 — giảm chi phí Claude Code trên codebase lớn

**Truy vấn:** `Claude Code reduce token cost large codebase 2026 tips`

**Nguồn:**
- https://www.notdiamond.ai/blog/how-to-reduce-claude-code-costs-without-sacrificing-output-quality
- https://boringbot.substack.com/p/how-to-save-millions-in-claude-tokens
- https://github.com/Sagargupta16/claude-cost-optimizer

**Điều rút ra:**
- notdiamond.ai khuyến nghị cấu trúc, không phải mẹo: giữ CLAUDE.md **dưới ~1.500 token**; chuyển procedure dài sang Skills (thân skill chỉ tốn token khi được gọi); dùng kiểu tham chiếu `@docs/testing.md` cho doc phân tầng — Claude Code chỉ đọc chain khi cần, không inline sẵn.
- Cảnh báo: đổi model giữa chừng trong 1 phiên (Sonnet ↔ Opus) hoặc đổi effort-level làm mất cache đã "ấm" — nên quyết định model/effort trước khi context tích luỹ nhiều, không đổi giữa chừng khi cache đang có lợi.
- boringbot.substack.com — case đã đo: chuyển 5 file rule "procedure-heavy" thành Skills (chỉ load khi cần) + scope 8 rule domain-specific vào đúng thư mục liên quan → giảm rule luôn-load từ 1.358 dòng xuống 807 dòng (**giảm 41%**). Nguyên tắc chung: "path-scoped rules" — rule chỉ load khi đang chạm đúng thư mục, không load toàn bộ rule cho mọi session.
- Nhấn mạnh: nhóm đạt tiết kiệm 90% làm điều "structurally different" — không phải chỉ bật cache mặc định mà là đổi cấu trúc project (rule scoping, skill hoá, doc phân tầng).

## Điều áp dụng được cho TDQ

1. **Bật tool-result clearing (context editing) cho subagent research/build loop** — set `clear_tool_uses`, `keep` (giữ N tool call gần nhất), `clear_at_least` đủ lớn để bõ phí re-cache. Đây là fix trực tiếp cho nguyên nhân #1 (Read file lớn 32,96M) và #3 (tavily thô 15,11M) trong báo cáo đo — kết quả Read/tavily cũ không cần giữ nguyên văn sau khi đã dùng xong. (Nguồn: platform.claude.com/docs/en/build-with-claude/context-editing)
2. **Chuyển tool call rời rạc (đặc biệt Bash 178 lần) sang code-execution pattern khi có thể** — để subagent viết 1 script/1 lệnh gộp xử lý logic (loop, điều kiện) thay vì Claude tự lặp gọi Bash từng bước; kết quả trung gian không cần vào context chính. (Nguồn: anthropic.com/engineering/code-execution-with-mcp — case giảm 98.7% token)
3. **Ép digest subagent trả về ngắn, có ngưỡng cứng** (vd. ≤1.500–2.000 ký tự) thay vì để subagent tự quyết — đúng nguyên nhân #4 (digest 13k ký tự/lần). Kèm quy tắc "không dán kết quả tool thô vào digest".
4. **Dùng structured note-taking (memory files) cho các route nghiên cứu dài** — thay vì giữ toàn bộ lịch sử tìm kiếm trong context, ghi finding ra file (`docs/tdq/research/*.md` đã làm đúng) rồi agent đọc lại khi cần, không cần giữ nguyên trong context sau khi ghi. (Nguồn: anthropic.com/engineering/effective-context-engineering-for-ai-agents)
5. **Áp dụng progressive disclosure triệt để hơn cho skill TDQ**: SKILL.md chính giữ ngắn, đẩy hết quy trình chi tiết/ví dụ dài sang `references/*.md` — chỉ load khi thực sự cần bước đó (đã làm một phần, nên rà lại các skill dài để tách thêm). (Nguồn: leehanchung.github.io deep-dive + Speakeasy)
6. **CLI/script nội bộ (`scripts/*.py`) chuẩn hoá `--quiet`/output JSON 1 dòng + exit code**, cấm script tự in lại nội dung file đã ghi — áp dụng cho toàn bộ `scripts/` chứ không riêng CLI đã sửa ở vòng 1. (Nguồn: speakeasy.com/blog/engineering-agent-friendly-cli)
7. **Không đổi model/effort giữa chừng trong 1 phiên/route đang "ấm cache"** — chốt model+effort trước khi context tích luỹ (đã có luật "chốt engine+model lúc lập plan" — nên áp thêm luật không đổi effort giữa chừng 1 build phase). (Nguồn: notdiamond.ai)
8. **Set TTL cache theo tần suất đọc lại thực tế, không mặc định 1 giờ**: route/skill chỉ dùng 1 lần trong phiên → dùng TTL 5 phút (hoà vốn ở 1 lần đọc); route lặp lại nhiều lần (vd. system prompt của subagent lặp) → cân nhắc TTL 1 giờ (hoà vốn ở ≥2 lần đọc). (Nguồn: platform.claude.com/docs/en/about-claude/pricing)
9. **Rà soát CLAUDE.md/skill dài theo path-scoping**: rule/kiến thức chỉ áp dụng cho 1 thư mục/loại việc thì chuyển vào skill hoặc file scoped riêng thay vì để trong file luôn-load — tham khảo case giảm 41% rule luôn-load. (Nguồn: boringbot.substack.com)
10. **Không đổi cache prefix giữa chừng** (đừng chèn timestamp/nội dung động vào đầu prompt hệ thống của subagent) — vì invalidate cache toàn bộ theo tiền tố, không phải theo nội dung. (Nguồn: platform.claude.com/docs/en/about-claude/pricing + tool-use-with-prompt-caching)

## Đơn giá xác nhận (2026-08-05)

Nguồn đọc trực tiếp: https://platform.claude.com/docs/en/about-claude/pricing (truy cập 2026-08-05).
Agent `search-scout` fail ("Prompt is too long") → main tự đọc trang giá, ghi lại ở đây.

| Loại token | Opus 5 (USD/1M) | Sonnet 5 (USD/1M) | Hệ số so với base input |
|---|---|---|---|
| Base input | 5,00 | 2,00 | 1,00 |
| Cache write TTL 5 phút | 6,25 | 2,50 | **1,25** |
| Cache write TTL 1 giờ | 10,00 | 4,00 | **2,00** |
| Cache read (hit/refresh) | 0,50 | 0,20 | **0,10** |
| Output | 25,00 | 10,00 | **5,00** |

Trang giá ghi thẳng bảng hệ số nhân: 5m write 1.25x · 1h write 2x · cache hit 0.1x.
Hệ số output/input = 5,0 đúng cho cả Opus 5, Sonnet 5 và Haiku 4.5 — công thức quy đổi
không phụ thuộc model đang dùng.

**Đính chính so với knowledge mục 1:** công thức cũ dùng cache_write = 1,25 (TTL 5 phút).
Phiên Claude Code hiện tại chạy TTL 1 giờ, tức hệ số 2,00. Vì vậy `token_audit.py` phải
cho chọn TTL, mặc định 1 giờ:

```
chi phí ≈ cache_read×0,1 + cache_write×W + input×1 + output×5     (W = 2,0 khi TTL 1h; 1,25 khi TTL 5m)
```

Sonnet 5 đang ở giá giới thiệu 2/10 USD đến 31-08-2026, sau đó lên 3/15 — tỷ lệ giữ nguyên.
