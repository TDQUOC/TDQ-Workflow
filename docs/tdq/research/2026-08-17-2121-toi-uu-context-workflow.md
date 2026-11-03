# Research: tối ưu context workflow (token tiếng Việt vs tiếng Anh)

Ngày: 2026-08-17 · Công cụ: `mcp__tavily-primary__tavily_search` (không cần fallback backup, primary hoạt động tốt).

## Truy vấn 1 — Tỷ lệ token tiếng Việt/tiếng Anh (Claude tokenizer)

**Query:** `Claude tokenizer Vietnamese vs English tokens per character ratio`

**Nguồn:**
- https://intuitionlabs.ai/articles/token-optimization-chatgpt-claude-costs
- https://blog.gopenai.com/counting-claude-tokens-without-a-tokenizer-e767f2b6e632
- https://shipyard.build/blog/claude-code-tokens
- https://news.ycombinator.com/item?id=47829178 (thread thảo luận, không phải nguồn số liệu chính thức)
- https://tokencontributions.substack.com/p/whole-words-and-claude-tokenization
- https://arxiv.org/html/2604.14210v1 (Mythbuster: Chinese vs English token cost — không phải tiếng Việt nhưng cùng phương pháp đo)

**Truy vấn bổ sung (góc nhìn khác):** `"Vietnamese" tokenizer tokens per word GPT cl100k multiplier compared English`
- https://gptforwork.com/guides/openai-gpt-tokens — bảng số liệu tổng hợp theo ngôn ngữ (nguồn thứ cấp, dẫn lại một "study" không nêu tên)
- https://community.openai.com/t/tokenizer-is-so-high-in-vietnamese/27692 — ví dụ cụ thể: "One" = 1 token nhưng "Một" = 5 token (cl100k, GPT tokenizer)
- https://arxiv.org/html/2604.14210v1 — bảng ZH/EN ratio theo nhiều tokenizer (cl100k, Qwen, GLM, Mistral, Llama)

### Điều rút ra
- **Không có số liệu chính thức từ Anthropic** về tỷ lệ token tiếng Việt/tiếng Anh cho Claude tokenizer riêng. Anthropic không công khai chi tiết tokenizer của Claude (xác nhận qua intuitionlabs.ai và grohan.co ở truy vấn 4).
- Với **cl100k (GPT/tiktoken)** — dùng làm tham chiếu vì không có số liệu Claude-specific: **tiếng Việt ≈ 3.3 token/từ**, so với **tiếng Anh ≈ 1.3 token/từ** (nguồn: gptforwork.com, dẫn lại một "study" không nêu rõ tên — độ tin cậy TRUNG BÌNH, không phải nguồn học thuật/chính thức). Tức tỷ lệ ~2.5x token cho cùng nội dung khi viết bằng tiếng Việt so với tiếng Anh trên tokenizer cl100k.
- Ví dụ cụ thể trên OpenAI cl100k: từ "One" = 1 token, từ "Một" (nghĩa tương đương) = 5 token — minh chứng cực đoan cho việc tiếng Việt có dấu bị tokenizer gốc Anh phạt nặng (community.openai.com, một báo cáo cá nhân, không phải benchmark có kiểm soát).
- Cơ chế giải thích (từ arxiv 2604.14210, dù đo tiếng Trung không phải tiếng Việt): tỷ lệ token phụ thuộc vào **độ phủ vocabulary của tokenizer với ngôn ngữ đó**, không phải bản chất ngôn ngữ. Tokenizer thiên về tiếng Anh (cl100k) phạt ngôn ngữ khác ~15%+ tuỳ ngôn ngữ; tokenizer có vocab mở rộng cho ngôn ngữ đích thì tỷ lệ giảm hẳn hoặc thậm chí đảo ngược.
- Claude's tokenizer nhỏ hơn và có vẻ tối ưu hoá nhiều cho tiếng Anh (theo tokencontributions.substack.com: 8311/10000 từ Anh thông dụng là 1 token trong Claude3 tokenizer) — gợi ý tiếng Việt (có dấu, Unicode tổ hợp) nhiều khả năng cũng bị phạt tương tự hoặc nặng hơn cl100k, nhưng **không có số đo trực tiếp**.

**KHÔNG TÌM ĐƯỢC nguồn:** con số tokens/character hoặc multiplier chính xác cho **Claude tokenizer cụ thể** với tiếng Việt. Số 3.3 token/từ và ví dụ "Một"=5 token đều đo trên tokenizer OpenAI (cl100k), không phải Claude. Mức tin cậy cho việc suy ra sang Claude: THẤP (chỉ là suy luận tương tự, không phải đo trực tiếp).

---

## Truy vấn 2 — System prompt tiếng Anh nhưng yêu cầu trả lời ngôn ngữ khác có giảm compliance không

**Query:** `LLM system prompt English instructions but respond in another language instruction following degradation research`

**Nguồn:**
- https://aclanthology.org/2026.findings-eacl.254.pdf (Improving Long Context Instruction Following)
- https://openreview.net/pdf/848f1332e941771aa491f036f6350af2effe0513.pdf ("Curse of Instructions")
- https://lilt.com/blog/multilingual-llm-performance-gap-analysis (blog thương mại, không phải academic)
- https://arxiv.org/html/2409.07054v1 (Native vs Non-Native Language Prompting)
- https://arxiv.org/html/2503.07539v2 (XIFBench: Evaluating LLMs on Multilingual Instruction Following)
- https://aclanthology.org/2024.findings-acl.818.pdf (RefuteBench)

### Điều rút ra
- **Không tìm được nghiên cứu nào trả lời trực tiếp** câu hỏi hẹp: "viết system prompt bằng tiếng Anh nhưng bắt output bằng ngôn ngữ khác thì compliance có giảm không, so với việc viết cả prompt lẫn output cùng một ngôn ngữ". Đây là khoảng trống nghiên cứu thực sự — các bài tìm được đều nói về (a) suy giảm theo độ dài context, (b) suy giảm theo số lượng instruction cùng lúc, (c) hiệu năng đa ngôn ngữ nói chung.
- XIFBench (arxiv 2503.07539) là gần nhất về mặt chủ đề: đánh giá multilingual instruction following, nhưng thiết kế thử nghiệm của họ là dịch cả prompt và instruction sang cùng ngôn ngữ mục tiêu, không tách riêng biến "ngôn ngữ prompt vs ngôn ngữ output".
- LILT blog (nguồn thương mại, không phải academic, độ tin cậy THẤP-TRUNG BÌNH) tổng hợp: hiệu năng LLM giảm đều 3-7% ở Instruction Retention khi chuyển từ tiếng Anh sang ngôn ngữ khác trong hội thoại multi-turn; quy nguyên nhân >70-80% do "tokenizer inefficiencies và English-centric reasoning" — nhưng không tách biệt được nguyên nhân do ngôn ngữ prompt vs ngôn ngữ output.
- "Curse of Instructions" (OpenReview, học thuật) chứng minh: độ chính xác tuân thủ giảm theo hàm mũ với số lượng instruction đồng thời — liên quan gián tiếp (system prompt dài, nhiều rule → giảm compliance), không liên quan trực tiếp đến ngôn ngữ.
- **Anthropic không có tài liệu chính thức công khai** về chủ đề này (không tìm thấy trong kết quả search; docs Anthropic về prompt engineering không đề cập vấn đề ngôn ngữ prompt vs ngôn ngữ output).

**KHÔNG TÌM ĐƯỢC nguồn** trả lời trực tiếp câu hỏi 2. Kết luận: đây là giả thuyết hợp lý dựa trên suy luận gián tiếp (nhiều rule + ngôn ngữ khác nhau → tăng tải nhận thức mô hình), nhưng KHÔNG có bằng chứng thực nghiệm xác nhận hoặc bác bỏ cho riêng biến "ngôn ngữ system prompt khác ngôn ngữ output". Độ tin cậy: THẤP (suy luận, không phải kết luận có nguồn).

---

## Truy vấn 3 — Kỹ thuật giảm token system prompt mà không mất rule

**Query:** `Anthropic prompt engineering reduce system prompt tokens progressive disclosure long system prompts`

**Nguồn:**
- https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents (**chính thức Anthropic**)
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices (**chính thức Anthropic**)
- https://bosio.digital/articles/context-engineering-rules (blog bên thứ ba, phân tích lại bài Anthropic)
- https://news.ycombinator.com/item?id=43909409 (thảo luận, không phải nguồn kỹ thuật)
- https://www.indiehackers.com/post/... (reverse-engineer Claude Code prompt, blog cá nhân)
- https://github.com/zircote/.claude/blob/main/skills/anthropic-prompt-engineer/SKILL.md (skill cộng đồng, không chính thức)

### Điều rút ra — CÓ BẰNG CHỨNG CHÍNH THỨC (Anthropic)
- Bài **"Effective context engineering for AI agents"** (anthropic.com/engineering) là nguồn chính thức, định nghĩa **context engineering** là bước tiến hoá của prompt engineering: "chiến lược để chọn lọc và duy trì tập token tối ưu trong lúc suy luận". Nguyên tắc chính thức được nêu: tìm "tập token nhỏ nhất có hàm lượng thông tin cao nhất" (không trích nguyên văn số liệu, nhưng khẳng định hướng "ít mà đủ").
- **Progressive disclosure** là kỹ thuật được Anthropic áp dụng thực tế trong sản phẩm của chính họ (theo bosio.digital tổng hợp lại từ nguồn Anthropic): thay vì nhồi hết vào system prompt, tách phần "code review", "verification" ra thành **skills chỉ được gọi khi cần** — đúng mô hình progressive disclosure/on-demand loading. Tool definitions cũng dùng "deferred loading" — công cụ chỉ tốn token khi thực sự được tra cứu/dùng.
- Tài liệu chính thức **claude-prompting-best-practices** (platform.claude.com) khẳng định nguyên tắc chung: rõ ràng, trực tiếp, dùng XML tag để phân tách nội dung — nhưng không đưa số liệu benchmark cụ thể về % token tiết kiệm.
- Nguồn không chính thức (indiehackers.com, blog cá nhân reverse-engineer Claude Code) đề xuất bảng phân loại "System Prompt vs User Message Reminder" và khuyến nghị dùng **prompt caching** để tiết kiệm chi phí lặp lại (không phải giảm số token thực, mà giảm chi phí/độ trễ khi prefix lặp lại) — đây là kỹ thuật CHÍNH THỨC của Anthropic (prompt caching được nhắc trong docs chính thức của Anthropic ở nhiều nơi khác, không trong kết quả search này nhưng là tính năng đã biết).
- **Viết rule dạng bảng thay vì văn xuôi**: không tìm thấy nguồn chính thức Anthropic nào khẳng định trực tiếp kỹ thuật này giảm token mà giữ được rule. Chỉ có gợi ý gián tiếp qua ví dụ thực tế trong bài indiehackers.com (họ dùng bảng để tổ chức "khi nào dùng system prompt vs user message") — đây là quan sát thực hành cộng đồng, KHÔNG có benchmark hay bằng chứng khoa học nào đo % tiết kiệm token.

### Phân biệt evidence-backed vs blog-only
| Kỹ thuật | Nguồn chính thức Anthropic? | Ghi chú |
|---|---|---|
| Progressive disclosure (tách skill, tải khi cần) | CÓ (anthropic.com/engineering, xác nhận qua bosio.digital tổng hợp) | Đã áp dụng thực tế trong sản phẩm Anthropic |
| Deferred tool loading | CÓ (cùng bài trên) | Cùng nguồn |
| Prompt caching | CÓ (tính năng chính thức, đã biết rộng rãi, không phải chỉ blog) | Giảm CHI PHÍ lặp lại, không giảm SỐ TOKEN gốc |
| Viết rule dạng bảng thay vì văn xuôi | KHÔNG — chỉ blog/cộng đồng | Không có số liệu benchmark |
| "Mỗi token đều quan trọng" / tối thiểu hoá context | CÓ định hướng chung (anthropic.com/engineering) nhưng KHÔNG có công thức/số liệu cụ thể | Nguyên tắc định tính, không định lượng |

---

## Truy vấn 4 — Công cụ đếm token Claude chính xác (offline/API)

**Query:** `count_tokens API Claude accurate token counter offline library tiktoken wrong`

**Nguồn:**
- https://github.com/anthropics/skills/blob/main/skills/claude-api/shared/token-counting.md (**chính thức Anthropic — skill repo**)
- https://grohan.co/2026/02/10/ctoc (reverse-engineer, bên thứ ba, có mã nguồn mở)
- https://github.com/shaunburdick/token-count (công cụ CLI bên thứ ba)
- https://blog.gopenai.com/counting-claude-tokens-without-a-tokenizer-e767f2b6e632
- https://stackoverflow.com/questions/78767238/best-way-to-count-tokens-for-anthropic-claude-models-using-the-api
- https://www.propelcode.ai/blog/token-counting-tiktoken-anthropic-gemini-guide-2025

### Điều rút ra
- **Công cụ chính xác, chính thức, được khuyến nghị:** endpoint `POST /v1/messages/count_tokens` (SDK: `client.messages.count_tokens()` / `client.messages.countTokens()`). Đây là API online, cần gọi Anthropic, nhưng cho số chính xác 100% khớp billing — nguồn: chính tài liệu skill Anthropic đã có sẵn trong môi trường làm việc (`skills/claude-api/shared/token-counting.md`).
- **`tiktoken` (tokenizer OpenAI) SAI cho Claude**: theo skill chính thức, tiktoken **undercount ~15-20%** trên văn bản thông thường, và **sai nhiều hơn nữa với code hoặc văn bản không phải tiếng Anh** — đây là điểm liên quan trực tiếp đến câu hỏi 1 (tiếng Việt), khẳng định rằng nếu dùng tiktoken để ước lượng token tiếng Việt cho Claude thì sai số càng lớn hơn mức 15-20% cơ bản.
- **Ước lượng offline (không cần gọi API) — độ chính xác từ thấp đến khá**:
  - Heuristic của Anthropic "1 token ≈ 3.5 ký tự tiếng Anh" — theo blog.gopenai.com, sai số **lên tới ~20% MAPE**, kém hơn cả tiktoken trong benchmark của họ.
  - `tiktoken` dùng làm proxy: sai số **~12% MAPE** (đo trên 3 cuốn tiểu thuyết dài, benchmark độc lập, không chính thức).
  - "Legacy Anthropic tokenizer" (tokenizer công khai cũ, dùng cho Claude 2.1 trở về trước) dùng làm proxy cho model mới: sai số thấp nhất trong nhóm ước lượng offline, **~1-2% MAPE** — nhưng đây là hàng cũ, không đảm bảo còn khớp với tokenizer Claude 4.x/5.
  - Công cụ mới `ctoc` (grohan.co, mã nguồn mở, reverse-engineer từ chính API count_tokens, vocab 36,495 token đã xác minh): tự nhận đạt **~96% độ chính xác** so với count_tokens thật, chạy offline. Đây là nguồn bên thứ ba (không phải Anthropic), độ tin cậy TRUNG BÌNH (có phương pháp rõ ràng, mã nguồn mở, nhưng không phải benchmark độc lập bên thứ ba xác nhận).
  - `token-count` (Rust CLI, shaunburdick/token-count trên GitHub): hỗ trợ "adaptive estimation" offline cho Claude + tuỳ chọn gọi API để lấy số chính xác — không có số liệu độ chính xác cụ thể được nêu trong kết quả search.
- **Kết luận thực dụng cho việc đo trước/sau của TDQ**: dùng `count_tokens` API (chính xác tuyệt đối, có sẵn trong skill claude-api đã load) làm phương pháp đo chính. Không dùng tiktoken hay heuristic ký tự để so sánh trước/sau vì sai số đủ lớn để làm nhiễu kết luận, đặc biệt với tiếng Việt (sai số tiktoken còn tệ hơn với non-English).

**KHÔNG TÌM ĐƯỢC nguồn:** thư viện Python/JS offline chính thức từ Anthropic để đếm token Claude mà không cần gọi API (Anthropic đã ngừng công khai tokenizer cho model mới — xác nhận qua stackoverflow: "Note that this is only accurate for older models... For newer models this can only be used as a _very_ rough estimate").

---

## Tổng kết độ tin cậy theo câu hỏi

| Câu hỏi | Có số liệu Claude-specific? | Độ tin cậy |
|---|---|---|
| 1. Tỷ lệ token VN/EN | KHÔNG (chỉ có số liệu cl100k/GPT làm tham chiếu) | THẤP — chỉ suy luận sang Claude |
| 2. English prompt + non-English output có giảm compliance | KHÔNG có nghiên cứu trực tiếp | THẤP — suy luận gián tiếp |
| 3. Kỹ thuật giảm token system prompt | CÓ (progressive disclosure, deferred loading — chính thức Anthropic) | CAO cho 2 kỹ thuật này; THẤP cho "viết bảng thay văn xuôi" |
| 4. Công cụ đếm token chính xác | CÓ (`count_tokens` API — chính thức) | CAO cho API; TRUNG BÌNH cho ước lượng offline (`ctoc` ~96%) |
