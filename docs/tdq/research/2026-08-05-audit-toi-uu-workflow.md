# Research: Giảm chi phí token/thời gian dài hạn cho agentic coding workflow

Request: 2026-08-05-audit-toi-uu-workflow
Ngày: 2026-08-05
Phương pháp: 4 truy vấn Tavily (`tavily-primary`, search_depth=advanced), góc độ khác nhau.

## Truy vấn 1: prompt caching cost reduction agentic workflow best practices

- Nguồn: https://www.cockroachlabs.com/blog/agentic-ai-costs-at-scale
  - Rút ra: Prompt caching là đòn bẩy chi phí lớn nhất, effort thấp nhất; hoà vốn chỉ sau ~2.3 lần tái sử dụng cùng prefix trong cửa sổ TTL 1h.
  - evidence_quote: "Prompt caching is the highest-return first move to reduce agentic AI costs. On Anthropic's platform, cache reads on Claude Sonnet 4.6 cost $0.30 per million tokens against a standard rate of $3.00, a 90% reduction on every token that hits the cache. Break-even lands at 2.3 reuses of the same cached prefix within the one-hour TTL window."
- Nguồn: https://www.mindstudio.ai/blog/prompt-caching-claude-code-token-savings
  - Rút ra: Cache breaker phổ biến nhất là nội dung động chèn TRƯỚC breakpoint, đổi thứ tự nội dung, hoặc đổi model — 3 thói quen giữ cache sống: front-load nội dung ổn định, batch context 1 lần đầu session, theo dõi cache hit/miss.
  - evidence_quote: "The most common cache breakers are dynamic content injected before the breakpoint, content reordering, and model switches. The three habits that maximize savings: front-load stable context before cache breakpoints, batch context in one initial load per session, and monitor cache hit/miss rates in API response metadata."
- Nguồn: https://arxiv.org/html/2601.06007v2 (paper đánh giá prompt caching long-horizon agentic)
  - Rút ra: Với Claude Sonnet 4.5, caching hệ prompt hệ thống (system prompt) tiết kiệm ~78.5% chi phí, ~22.9% time-to-first-token; caching thêm lịch sử hội thoại/tool-call chỉ lợi ích biên nhỏ vì system prompt chiếm phần lớn.
  - evidence_quote: "Claude Sonnet 4.5 | System Prompt | 78.5% | 22.9% ... The consistency of cost savings across cache strategies suggests that the primary driver of cost reduction is caching the large system prompt, which remains stable across all requests within a session."

## Truy vấn 2: context window bloat từ hooks/subagents, cách giảm token usage

- Nguồn: https://hackernoon.com/navigating-claude-code-the-context-window-tax
  - Rút ra: Hook lọc output TRƯỚC khi Claude đọc (vd grep FAIL/ERROR từ test log) có thể giảm 80,000 token xuống 2,000 token; nguyên tắc áp dụng cho mọi output verbose (log file, API response).
  - evidence_quote: "A hook that greps test output for FAIL and ERROR before returning it to Claude is not just a nice-to-have — on a large test suite, it can cut tool output from 80,000 tokens to 2,000."
- Nguồn: https://institute.sfeir.com/en/claude-code/claude-code-context-management/optimization
  - Rút ra: Kích hoạt Plan mode mặc định cho task không cần sửa file giảm ~50% token tiêu thụ (case thực tế: review code 38k → 18k token, giảm 53%). Prompt có cấu trúc (list, chỉ dẫn trực tiếp) tiết kiệm ~30% token so với prompt dạng văn xuôi.
  - evidence_quote: "In practice, a code review session drops from 38,000 to 18,000 tokens in Plan mode, a 53% savings... Key takeaway: activate Plan mode by default for any task that does not require file modification - you halve consumption."
- Nguồn: https://claudefa.st/blog/guide/mechanics/context-management
  - Rút ra: Ví dụ thực từ Anthropic — subagent đọc 6,100 token file nhưng chỉ trả về 420 token kết quả; ~5,700 token nội dung file KHÔNG BAO GIỜ chạm main context. Lưu ý: subagent không kế thừa lịch sử hội thoại/auto-memory của phiên chính, cần cấp đủ context trong task prompt.
  - evidence_quote: "Anthropic's own walkthrough makes the savings concrete: in their example, a subagent read 6,100 tokens of files and returned a 420-token result... a subagent does not inherit your conversation history or your main session's auto memory, so give it enough context in the task prompt to work on its own."

## Truy vấn 3: subagent context isolation pattern, hiệu quả token đa-agent

- Nguồn: https://www.langchain.com/blog/choosing-the-right-multi-agent-architecture
  - Rút ra: Pattern Subagents xử lý ít hơn 67% tổng token so với pattern Skills trong task multi-domain, nhờ context isolation — mỗi subagent chỉ mang context liên quan, tránh tích luỹ token khi nhồi nhiều skill vào 1 hội thoại.
  - evidence_quote: "In this scenario, Subagents processes 67% fewer tokens overall compared to Skills due to context isolation. Each subagent works only with relevant context, avoiding the token bloat that accumulates when loading multiple skills into a single conversation."
- Nguồn: https://jtanruan.medium.com/context-engineering-in-llm-based-agents-d670d6b439bc
  - Rút ra: Đánh đổi quan trọng — hệ multi-agent (Claude điều phối Claude subagent) đạt ~90% cải thiện hiệu năng trên task nghiên cứu phức tạp, NHƯNG tổng token tiêu thụ có thể gấp ~15 lần so với single-agent chat cùng task (do mỗi agent có prompt riêng, overhead điều phối).
  - evidence_quote: "Anthropic reported that their multi-agent system (Claude orchestrating Claude subagents) solved certain complex queries far better than a single agent could... However, this strategy comes with costs. Multi-agent systems 'burn through tokens fast' — Anthropic observed that their multi-agent runs used ~15× more tokens in total than a single-agent chat on the same task."
- Nguồn: https://www.jeremydaly.com/context-engineering-for-commercial-agent-systems
  - Rút ra: Isolation nên đi kèm scoped input rõ ràng — parent quyết định context nào vào subagent (explicit), không để subagent kế thừa toàn bộ ngữ cảnh parent (implicit) vì làm ô nhiễm reasoning và khó debug/replay.
  - evidence_quote: "The isolation is deliberate: The subagent's token budget is its own. The parent controls what enters the subagent's window... If context inheritance is implicit, debugging multi-agent behavior requires reconstructing invisible state. If context inheritance is explicit, each agent's behavior is independently replayable."

## Truy vấn 4: system prompt size best practice — CLAUDE.md, skills, token cost

- Nguồn: https://www.blockchain-council.org/claude-ai/system-prompt-slimming-for-claude
  - Rút ra: Best practice phổ biến — giữ CLAUDE.md dưới ~5,000 token / 200 dòng vì nó load MỖI session, mọi thứ dư thừa trở thành overhead lặp lại.
  - evidence_quote: "A widely adopted best practice is keeping it under roughly 5,000 tokens or 200 lines so it remains useful without becoming costly. Because it loads every time, anything unnecessary inside it becomes recurring overhead."
- Nguồn: https://boringbot.substack.com/p/how-to-save-millions-in-claude-tokens
  - Rút ra: 20,000–30,000 token đã bị tiêu trước khi user gõ chữ đầu tiên (system prompt + CLAUDE.md + memory + tên tool MCP + mô tả skill) — đây là bề mặt tối ưu đòn bẩy cao nhất. Đề xuất: CLAUDE.md dưới 500 token (case thực giảm 91.9% context), chuyển rule domain-specific sang `.claude/rules/` với `paths:` frontmatter để ẩn cho tới khi cần (case giảm 41% overhead).
  - evidence_quote: "Every Claude Code session starts with 20,000–30,000 tokens already consumed before you type a single character... CLAUDE.md under 500 tokens, path-scoped rules for the rest — strip CLAUDE.md to only what Claude can't infer from code (91.9% context reduction); move domain-specific rules to `.claude/rules/` with `paths:` frontmatter so they're invisible until needed (41% overhead reduction documented)."
- Nguồn: https://github.com/Piebald-AI/claude-code-system-prompts (video liên quan: youtube.com/watch?v=pBK7RjrtCPw — "Claude Code SKILLS.md are a token trap")
  - Rút ra: Skill riêng lẻ có thể nặng bất ngờ — ví dụ nêu trong video: một skill "plan CEO review" chiếm 21,000 token TRƯỚC KHI gọi bất kỳ skill con nào; `/doctor` slash command chiếm 15,359 token, `/init` chiếm 7,828 token. Cảnh báo "skills bloat" là chi phí ẩn dồn tích khi số skill tăng.
  - evidence_quote: "Just this skill, before it calls any other skills, before it does anything else, basically, this file that I'm showing you is 21,000 tokens... Skill: /doctor slash command (15359 tks) - Diagnostic workflow for auditing and fixing Claude Code installation health, unused context, local memory duplication, hooks, version currency, and permission prompts."

## Tổng hợp — nguyên tắc quan trọng nhất

1. Prompt caching là đòn bẩy #1: giữ system prompt/tool-def ổn định, front-load trước breakpoint, không chèn nội dung động phía trước cache — hoà vốn chỉ sau ~2 lần tái dùng.
2. Lọc output TRƯỚC khi vào context (hook grep log/test-output) — giảm token verbose 40x mà không mất thông tin cần thiết.
3. Subagent = context isolation thật sự (giảm ~67% token so với nhồi nhiều skill vào 1 hội thoại) nhưng có phí điều phối — parent phải scope input tường minh, không để subagent kế thừa toàn bộ lịch sử.
4. CLAUDE.md/skill là overhead LẶP LẠI mỗi session — cắt CLAUDE.md xuống dưới ~500 token, đẩy rule domain-specific ra file `paths:`-scoped, tránh skill "nặng" nạp sẵn hàng chục nghìn token trước khi làm gì.
5. Plan mode mặc định cho task không sửa file có thể giảm ~50% token của phiên đó.
