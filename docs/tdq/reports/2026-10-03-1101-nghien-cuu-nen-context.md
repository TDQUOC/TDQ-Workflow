# REPORT — Nén context và rút thời gian máy của workflow (`2026-10-03-1101-nghien-cuu-nen-context`)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Tóm tắt

Phát hiện chính: file luật chỉ là phần nhỏ của chi phí; tiền nằm ở **hội thoại tích luỹ** bị đọc lại mọi lượt (~90% context mỗi lượt, TB 491k token/lượt) và ở **các lần chạy trọn bộ test** (59 lần, 26,1% thời gian máy).
- (a) Hội thoại/cache: tách/compact ở mọi mốc phase bớt 94M – 108M token/request (62–71%), chỉ tách ở đầu request bớt 63M – 76M (42–50%); giây máy bớt nhỏ (110 – 424 s/request).
- (b) Test: chạy vùng chạm ở bước trung gian, trọn bộ chỉ ở 2–3 cổng → ≈ 1.240 – 1.780 s máy/request (55–68% thời gian trọn bộ).
- (c) File luật và hook: nén luật bớt thật ≈ 1,3k – 2,7k token đọc/full request (≈ 0,2% context một request); hook resume ≈ 42k token/phiên exc1; `edited_text_file` cận trên ≈ 204k/phiên.
- Nên làm trước: H5 (test vùng chạm), H2 (phiên mới mỗi request); sau khi đo lại: H1 (compact ở mọi phase).
- Không đáng làm: H4 (trợ lý đọc nặng giao lẻ — lỗ tiền và giờ máy), H7 như một request riêng (≈ 0,2% context); H3 chỉ đáng một câu luật (≈ $3,7 một lần).
- H10/H11 (giảm cổng duyệt) bớt ≈ 0 s máy và đổi bằng kiểm soát của user — để user quyết, xem "Thứ tự đề xuất".
- Sửa số: "31%" của đo nội bộ là test rộng; full suite ≥ 200 s là 18.085 / 69.300 s = **26,1%** máy (mục "Số chạy lại").
- 38 số bên ngoài đã kiểm: 28 khớp, 3 lệch nhỏ, 7 không xác minh được và không được dùng.

## Kiểm chéo số bên ngoài

Phạm vi: mọi con số bên ngoài trong `docs/tdq/research/2026-10-03-1101-nghien-cuu-nen-context.md` có thể làm căn cứ đề xuất. Mỗi nguồn sơ cấp được mở lại ngày 2026-10-03 (WebFetch; với arXiv HTML, raw GitHub và blog thì tải thêm bằng curl rồi grep đúng câu). Số "không xác minh được" bị **loại khỏi căn cứ** đề xuất. Mã N<số> được ghi cạnh số tương ứng trong file nghiên cứu.

| Mã | Con số (như trong file nghiên cứu) | Nguồn sơ cấp đã mở | Nguồn nói gì | Kết luận |
|---|---|---|---|---|
| N1 | Đọc cache 0,1× giá input; Opus 5.5: 0,05×; Fable/Mythos 5.1: 0,025× (1.1, 1.2) | platform.claude.com/docs/en/build-with-claude/prompt-caching | "Cache read tokens are 0.1 times"; chú thích: "Cache hits and refreshes on Claude Opus 5.5 are priced at 0.05x"; Fable 5.1 và Mythos 5.1 "0.025x" | khớp |
| N2 | Ghi cache 5m = 1,25×, 1h = 2× (1.2) | platform.claude.com/docs/en/build-with-claude/prompt-caching | "5-minute cache write tokens are 1.25 times… 1-hour cache write tokens are 2 times" | khớp |
| N3 | Ngưỡng cache tối thiểu 512 token cho Opus 5.5/Sonnet 5.5/Fable 5 (1.2) | platform.claude.com/docs/en/build-with-claude/prompt-caching | "512 tokens for Claude Fable 5.1, Claude Mythos 5.1, Claude Opus 5.5, Claude Opus 5, Claude Sonnet 5.5, Claude Fable 5, and Claude Mythos 5" | khớp |
| N4 | 50k token × $0,20/MTok ≈ $0,01/lượt (1.2) | platform.claude.com/docs/en/build-with-claude/prompt-caching | Opus 5.5 cache hit $0,20/MTok; 50.000 × 0,20 / 10⁶ = $0,01 | khớp |
| N5 | TTL: subscription hội thoại chính 1h; subagent/workflow/compaction 5m; API key 5m (1.1) | code.claude.com/docs/en/prompt-caching | Bảng TTL: Main conversation "One hour" (subscription trong hạn mức) / "Five minutes" (API key, credits, cloud); "Everything else" (subagent, workflow, fork, compaction) 5 phút | khớp |
| N6 | Dòng `Prompt cache (main)` cần v2.1.251+; nguyên nhân miss v2.1.260+ (1.1) | code.claude.com/docs/en/prompt-caching; code.claude.com/docs/en/costs | "Both require Claude Code v2.1.251 or later"; "The likely-cause text requires Claude Code v2.1.260 or later" | khớp |
| N7 | Hook output trần 10.000 ký tự; vượt → file + preview 2.000 ký tự; không yêu cầu Claude đọc file (1.4) | code.claude.com/docs/en/hooks | "capped at 10,000 characters"; "a preview of up to the first 2,000 characters"; "Claude Code doesn't ask Claude to read the file" | khớp |
| N8 | Listing skill = 1% context window; description + when_to_use cắt ở 1.536 ký tự (1.5) | code.claude.com/docs/en/skills | "The budget scales at 1% of the model's context window"; "truncated at 1,536 characters" | khớp |
| N9 | Sau compaction giữ 5.000 token đầu mỗi skill, tổng 25.000 token (1.5) | code.claude.com/docs/en/skills | "keeping the first 5,000 tokens of each… a combined budget of 25,000 tokens" | khớp |
| N10 | Codex: listing skill ≤ 2% context hoặc 8.000 ký tự (1.5, 4.6) | learn.chatgpt.com/docs/build-skills | "at most 2% of the model's context window, or 8,000 characters when the context window is unknown" — 8.000 chỉ là mức dự phòng khi không biết context window | khớp |
| N11 | Codex AGENTS.md trần `project_doc_max_bytes` = 32 KiB, cắt im lặng (4.6) | learn.chatgpt.com/docs/agent-configuration/agents-md (redirect từ developers.openai.com/codex/guides/agents-md); github.com/openai/codex/issues/7138 | "32 KiB by default", "stops adding files once the combined size reaches the limit"; issue #7138 "AGENTS.md is silently truncated without any warning" — đóng "not planned" | khớp |
| N12 | SKILL.md < 500 dòng; file tham chiếu > 100 dòng cần mục lục; ví dụ ~50 vs ~150 token; ≥ 3 eval (1.6) | platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices | "under 500 lines"; "reference files longer than 100 lines, include a table of contents"; "approximately 50 tokens" / "approximately 150 tokens"; "Build three scenarios", "At least three evaluations created" | khớp |
| N13 | Subagent trả tóm tắt 1.000–2.000 token (1.7) | anthropic.com/engineering/effective-context-engineering-for-ai-agents (2025-09-29) | "returns only a condensed, distilled summary of its work (often 1,000-2,000 tokens)" | khớp |
| N14 | CLAUDE.md < 200 dòng; agent teams ~7× token so với phiên thường (1.8) | code.claude.com/docs/en/costs | "Aim to keep CLAUDE.md under 200 lines"; "Agent teams use approximately 7x more tokens than standard sessions when teammates run in plan mode" — 7× gắn với điều kiện teammate chạy plan mode | khớp |
| N15 | Tối đa 20 subagent đồng thời, sâu 3 tầng; tổng description subagent ≤ 15.000 token (1.9) | code.claude.com/docs/en/sub-agents | "when 20 subagents are running… fails"; độ sâu mặc định 3; "exceed 15,000 tokens, Claude Code shows a warning" (ngưỡng cảnh báo, không phải trần cứng) | khớp |
| N16 | Context editing −84% token, memory + context editing +39%, context editing đơn +29%, eval 100 lượt (1.10) | claude.com/blog/context-management (2025-09-29) | "100-turn web search evaluation… reducing token consumption by 84%"; "improved performance by 39% over baseline"; "Context editing alone delivered a 29% improvement" | khớp |
| N17 | AGENTS.md (2602.11988): không tăng tỉ lệ thành công, chi phí suy luận tăng > 20% (2.1) | arxiv.org/abs/2602.11988 (v3) | "does not generally improve task success rates, while increasing inference cost by over 20% on average" | khớp |
| N18 | 2602.11988: file do dev viết tốt hơn file LLM sinh ~7 điểm (2.1) | arxiv.org/html/2602.11988 (§4.2) | Dev-provided "+2,4% on average (p=21%)"; LLM-generated "reduced by 0.5% and 2%" (SWE-bench / CTXbench); dev-file chỉ có trên CTXbench → chênh ≈ 2,4 − (−2) = 4,4 điểm; abstract không nêu số chênh | lệch: ≈ 4,4 điểm (dev +2,4% vs LLM −2% trên CTXbench) |
| N19 | AGENTS.md (2601.20404): 10 repo, 124 PR; runtime trung vị −28,64%, output token −16,58% (2.1) | arxiv.org/abs/2601.20404 (2026-01-28, sửa 2026-03-30) | "10 repositories… 124 pull requests"; "lower median runtime (Δ 28.64%) and reduced output token consumption (Δ 16.58%)" | khớp |
| N20 | arXiv 2605.10039: 1.650 phiên Claude Code; không biến cấu trúc file nào có khác biệt; OR 0,944 (~5,6%/hàm) (2.2) | arxiv.org/abs/2605.10039 | Bài **tồn tại**: "Instruction Adherence in Coding Agent Configuration Files: A Factorial Study of Four File-Structure Variables" (Damon McMillan, 2026-05-11); "1,650 Claude Code CLI sessions"; "None of the four structural variables… produces a detectable contrast after multiple-testing correction"; "approximately 5.6% lower odds… (OR = 0.944)" | khớp |
| N21 | IFScale (2507.11538): 20 model, tốt nhất 68% ở 500 chỉ dẫn, primacy bias (2.3) | arxiv.org/abs/2507.11538 (2025-07-15) | "20 state-of-the-art models"; "only achieve 68% accuracy at the max density of 500 instructions"; ba kiểu suy giảm; primacy bias | khớp |
| N22 | Context rot: 18 model; LongMemEval ~300 token vs ~113k (2.4) | trychroma.com/research/context-rot (2025-07-14) | "18 LLMs"; focused ≈ 300 token vs "the full 113k token LongMemEval input"; một distractor đã giảm, bốn càng tệ | khớp |
| N23 | arXiv 2606.10209: 71,0% / 1,48M / 14,56h → 79,0% / 535K / 5,39h → 91,6% / 553K / 5,79h; GPT-5 + Sonnet 4.5; 50 task (2.5) | arxiv.org/abs/2606.10209 | Bài **tồn tại**: "Less Context, Better Agents: Efficient Context Engineering for Long-Horizon Tool-Using LLM Agents" (Lodha và cộng sự, 2026-06-08); 50 task hotel expense; 1.480.996 / 535.274 / 553.374 token; 14,56 / 5,39 / 5,79 giờ; 71,0 / 79,0 / 91,6% | khớp |
| N24 | LLMLingua-2: nén 2–5×, end-to-end nhanh tới 2,9× (2.6) | arxiv.org/abs/2403.12968 | Nén 2x–5x; "end-to-end latency" 1,6x–2,9x | khớp |
| N25 | Multi-agent research: +90,2%; ~15× token (agent đơn ~4×); token giải thích 80% phương sai; thời gian −90% (3.1) | anthropic.com/engineering/multi-agent-research-system (2025-06-13) | "outperformed single-agent Claude Opus 4 by 90.2%"; "about 4×… about 15× more tokens"; "explains 80% of the variance"; "cut research time by up to 90%" | khớp |
| N26 | Tool search −85% token, Opus 4.5 79,5% → 88,1%; programmatic tool calling −37% (3.4) | anthropic.com/engineering/advanced-tool-use (2025-11-24) | "85% reduction in token usage"; "improved from 79.5% to 88.1%"; "43,588 to 27,297 tokens, a 37% reduction" | khớp |
| N27 | Một đoạn prompt đẩy tỉ lệ gọi tool song song lên ~100% (3.2) | platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices | "you can boost this to ~100%" (số nằm ở trang prompting best practices; trang parallel-tool-use chỉ có mẫu prompt, không có số) | khớp |
| N28 | Agentless: 27,33% SWE-bench Lite, $0,34/issue (3.3) | arxiv.org/abs/2407.01489 (v2) và /abs/2407.01489v1 | v1 (2024-07-01): "highest performance (27.33%) and lowest cost ($0.34)"; bản hiện hành v2 (2024-10-29): "32.00%, 96 correct fixes… low cost ($0.70)" | lệch: bản hiện hành 32,00% / $0,70 (27,33% / $0,34 là v1) |
| N29 | Agent thông thường ~$3,34/issue (3.3) | arxiv.org/abs/2407.01489 (v1, v2) | Không abstract nào có số $3,34 | không xác minh được: không có trong abstract v1/v2 — loại khỏi căn cứ |
| N30 | Blog caching: stub `defer_loading` ~1/10 chi phí nạp đủ (1.3) | claude.dev/blog/lessons-from-building-claude-code-prompt-caching-is-everything/ (2026-04-30) | Bài mô tả stub chỉ có tên tool; "one tenth the price" trong bài là giá cache hit của lời gọi compaction, không phải tỉ lệ stub/tool đầy đủ | không xác minh được: bài không nêu tỉ lệ chi phí stub — loại khỏi căn cứ |
| N31 | superpowers: skill bootstrap ~420 từ ≈ ~600 token (4.1) | raw.githubusercontent.com/obra/superpowers/main/skills/using-superpowers/SKILL.md | `wc -w`: 487 từ cả frontmatter, 460 từ phần thân; câu "even a 1% chance… ABSOLUTELY MUST invoke the skill" có thật | lệch: ≈ 460 từ thân (487 kể frontmatter); số token chưa đo |
| N32 | Cline Memory Bank: đọc toàn bộ 6 file mỗi task (4.4) | docs.cline.bot/prompting/cline-memory-bank | "I MUST read ALL memory bank files at the start of EVERY task"; 6 file lõi | khớp |
| N33 | Issue openai/codex#45999: SessionStart với additionalContext lỗi trên codex-cli 0.154.0 (1.4) | github.com/openai/codex/issues/45999 | Issue tồn tại (2026-09-16, đóng "not planned"): "Codex reports `SessionStart Failed` and nothing is injected" khi có `additionalContext`; trang nhắc 0.154.0 | khớp |
| N34 | Codex subagent ≤ 6 đồng thời (1.9, 3.1) | learn.chatgpt.com/docs/agent-configuration/subagents (redirect từ developers.openai.com/codex/subagents) | "When you leave `agents.max_concurrent_threads_per_session` unset, Codex chooses the default" — không nêu số; 6 và 8 chỉ xuất hiện trong ví dụ cấu hình | không xác minh được: docs chính thức không công bố mặc định — loại khỏi căn cứ |
| N35 | Test chọn lọc giảm ~50% thời gian / CI nhanh 2× (3.6, đề xuất G) | testmon.org; engineering.instawork.com/… | testmon.org không nêu số tiết kiệm (chỉ xác nhận "always re-executes tests which failed last time"); blog Instawork trả HTTP 403 | không xác minh được: nguồn có số không mở được, trang công cụ không nêu số — loại khỏi căn cứ |
| N36 | Kiro: khuyên 3–5 file steering mỗi task (2.7) | kiro.dev/docs/steering/ | Bốn chế độ always / fileMatch / manual / auto có thật; docs chính thức không nêu số file khuyên dùng | không xác minh được: chỉ có ở blog bên thứ ba — loại khỏi căn cứ |
| N37 | BMAD "tiết kiệm tới 90% token" (4.3) | augmentcode.com/guides/bmad-method-ai-development | Trang không chứa con số 90%; ngược lại nhắc người dùng than BMAD đốt nhiều token | không xác minh được: nguồn được dẫn không có số này — loại khỏi căn cứ |
| N38 | Model nhỏ "5–10× rẻ hơn", Explore "1,5–3K vs 35–45K token" (3.5) | mindstudio.ai/blog/smart-orchestrator-cheaper-sub-agent-models-claude-code | Có câu "5-10x" nhưng không dẫn phép đo; không có cặp số 1,5–3K vs 35–45K | không xác minh được: blog không đo, số Explore không có trong bài — loại khỏi căn cứ |

Tóm tắt: 38 số đã kiểm — 28 khớp, 3 lệch (N18, N28, N31), 7 không xác minh được (N29, N30, N34–N38). Ba số đáng ngờ nhất đều đứng: giá đọc cache 0,05× của Opus 5.5 (N1), hai bài arXiv 2605.10039 và 2606.10209 có thật và số khớp (N20, N23), trần Codex 32 KiB và 8.000 ký tự (N10, N11; 8.000 chỉ là mức dự phòng khi không biết context window). Các số lệch đều nhỏ và không lật hướng đề xuất nào; các số không xác minh được đều đến từ blog bên thứ ba (đã gắn **[chưa kiểm]** sẵn) hoặc là phép suy diễn, nên bỏ khỏi căn cứ. Riêng đề xuất G mất con số "−50%": đề xuất vẫn có thể giữ, nhưng lợi ích phải tự đo.

## Bản đồ chi phí

Nguồn số: `docs/tdq/research/2026-10-03-1101-do-noi-bo.md` (gọi tắt "đo nội bộ"; phương pháp từng số ở mục 0–3 file đó). Ba số lớn nhất đã được chạy lại độc lập ngày 2026-10-03 (bảng "Số chạy lại" cuối mục). "Thời gian máy" = agent làm việc + tool + test, **không** gồm thời gian chờ user. Phiên `tdqwf` = transcript chính `b77dddd9-…` của TDQ-Workflow; `exc1` = phiên excalidraw có cài plugin TDQ.

### Context — xếp theo cỡ

Đơn vị không đồng nhất (có số là tổng phiên, có số là mỗi lần); xếp theo tổng token mà nguồn đó đẩy qua model trong một phiên đo.

| # | Trung tâm chi phí | Số đo | Cách đo (đo nội bộ) |
|---|---|---|---|
| 1 | Hội thoại tích luỹ bị đọc lại ở mọi lượt (phiên dài, ít compact) | TB 491k token/lượt × 2.624 lượt → cache_read 1.273M token (tdqwf); ~90% context mỗi lượt là hội thoại tích luỹ, prefix cố định chỉ 38–46k | `message.usage` input + cache_read + cache_creation, khử trùng theo `message.id` (§1.1) |
| 2 | Ghi cache lạnh lại toàn bộ prefix sau chờ user/resume | 24 lượt ≥ 50k = 11,7M token = 74% cache_creation tdqwf (exc1: 0,94M = 58%) | `cache_creation_input_tokens` ≥ 50k mỗi lượt (§1.1) |
| 3 | Phí cố định mỗi subagent | lượt đầu TB 22,1k (tdqwf) / 25,9k (exc1); 83 subagent ≈ 2,5M token cache_creation | lượt API đầu mỗi `subagents/*.jsonl` (§1.1, §5.3) |
| 4 | Output lệnh shell ở main | Bash tdqwf ≈ 831k token, trong đó đọc/tìm bằng shell 895 lệnh ≈ 456k | độ dài tool_result theo tool, phân loại lệnh bằng regex, hệ số ký tự/token hiệu chỉnh (§1.3–1.4) |
| 5 | `edited_text_file` — harness chèn lại snippet khi plan/QC bị sửa ngoài lượt | 381 lần ≈ 204k token (tdqwf) | attachment `edited_text_file` (§1.5) |
| 6 | Hook TDQ ở dự án người dùng | ≈ 57k token/phiên exc1, ~46k là SessionStart resume (~2,1k × 22) | attachment hook + tokenizer thật trên mẫu (§1.6, §2) |
| 7 | Prompt giao subagent nằm lại ở main | exc1 42 prompt ≈ 38k token (TB 3.336 ký tự) | input của tool Agent (§1.6) |
| 8 | Luật workflow đọc vào (Skill + đọc `skills/**.md` qua shell) | exc1 ≈ 10k + 19k = 29k token | tool_result Skill/shell theo đường dẫn (§1.6) |
| 9 | Bộ file luật (trần nếu nạp hết) | 100.858 token / 62 file; comment HTML 6.021 (6,1%), trùng nguyên văn chỉ 1.038 (1%) | tokenizer thật từng file (§4) |

### Thời gian máy — xếp theo cỡ (11 cửa sổ request, máy 69.300 s = 14,9% treo tường 464.820 s)

| # | Trung tâm chi phí | Giây | % máy | Cách đo (đo nội bộ §3) |
|---|---|---|---|---|
| 1 | Model sinh token (phần máy không nằm trong tool) | 40.853 | 59% | khe event không kết thúc ở tool_result |
| 2 | Test rộng (mọi lệnh `unittest`/`pytest`/`vitest`/`tsc`…) | 21.454 | 31% | khe `assistant` → `tool_result` của lệnh test |
| 2a | — trong đó full suite ≥ 200 s (59 lần, TB ~307 s, đã tăng 284 → 363 s) | 18.085 | 26% | thời lượng tool_use → tool_result ≥ 200 s |
| 3 | Shell khác | 5.779 | 8,3% | như trên, lệnh không phải test |
| 4 | Độ trễ thêm vì context > 600k (nằm trong #1) | ≈ 1.400 | ≈ 2% | trung vị độ trễ theo bucket context (§3.4) |
| — | Theo phase: implement | 41.949 | 60,5% | cửa sổ phase dựng lại, xấp xỉ (§3.3) |

Subagent chạy song song 14.989 s không cộng vào "máy" (main chờ song song).

### Số chạy lại

Đã chạy lại ba số lớn nhất ngày 2026-10-03 bằng script tạm viết lại theo mô tả của đo nội bộ (`%TEMP%\tdqt12\m.py`, đã xoá sau khi đo; Python 3.13, chỉ đọc transcript và `timing.jsonl`). Transcript tdqwf vẫn đang lớn lên (chính phiên này ghi thêm: 40,7 MB → 41,2 MB, 2.624 → 2.651 lượt), nên mỗi số được tính hai lần: cắt tại 2026-10-03 04:17 UTC (mốc dữ liệu của đo nội bộ) và toàn file hiện tại. Lệch nhỏ ở bản toàn file là do phiên đang chạy, không phải do phương pháp.

| Số | Trợ lý báo | Chạy lại (2026-10-03) | Lệch % | Phương pháp / lệnh |
|---|---|---|---|---|
| Context TB mỗi lượt gọi API (tdqwf main) | TB 491k · trung vị 476k · p90 858k · max 966k · 2.624 lượt | cắt 04:17Z: TB 491.168 · trung vị 476.041 · p90 857.666 · max 966.403 · 2.624 lượt; toàn file: TB 491.806 · 2.651 lượt | 0,0% (cắt) · +0,2% (toàn file) | mỗi dòng `assistant` có `message.usage`, khử trùng theo `message.id`; context = `input_tokens + cache_read_input_tokens + cache_creation_input_tokens` |
| Thời gian máy (11 cửa sổ) | 69.300 s máy · 391.562 s chờ · 3.933 s không rõ | 69.299 s · 391.562 s · 3.933 s | 0,0% | gộp event `user/assistant` mọi transcript main của dự án, cắt theo `[started_at, closed_at]` của `timing.jsonl` (từ 09-20); khe kết thúc ở prompt người hoặc kết quả `AskUserQuestion` = chờ; kết thúc ở tool_result test/Agent = máy; khe khác > 900 s = không rõ |
| Full suite ≥ 200 s / thời gian máy | 59 lần · 18.085 s · "30,9%" | 61 lần · 19.177 s = 27,7% máy | +6,0% giây · +3,4% lần | thời lượng tool_use → tool_result của lệnh Bash/PowerShell khớp `unittest\|pytest\|vitest\|tsc`, ≥ 200 s, kết quả nằm trong cửa sổ |
| Test rộng / thời gian máy | 21.454 s = 31% | 21.747 s = 31,4% | +1,4% | khe `assistant` → `tool_result` của lệnh test (cùng regex) |
| Tỉ lệ ghi cache lạnh (tdqwf main) | 24 lượt ≥ 50k · 11,7M token · 74,1% cache_creation | cắt 04:17Z: 24 lượt · 11.715.576 / 15.811.966 = 74,1%; toàn file: 11.715.576 / 15.856.936 = 73,9% | 0,0% (cắt) · −0,3% (toàn file) | `cache_creation_input_tokens` ≥ 50.000 mỗi message (khử trùng `message.id`), chia tổng cache_creation |

Lý do lệch > 5% và điều cần sửa trong cách đọc số:
- Full suite +6,0%: toàn bộ chênh nằm ở request 09-21 (18 lần chạy lại so với 16); bảy request còn lại khớp tới giây. Hai lần thừa là hai lần chạy suite **song song** với một lần chạy khác (09-21 04:20 UTC 547 s và 04:39 UTC 539 s); bỏ hai lần chồng thời gian đó còn 59 lần · ≈ 18.091 s (lệch 0,0%). Đo nội bộ không ghi luật gộp lần chạy chồng nhau, nên bản chạy lại để nguyên.
- Số "31%" ở dòng 3 bảng tóm tắt đo nội bộ ghép sai cặp: 18.085 s / 69.300 s = **26,1%**, không phải 30,9%; 30,9–31% là tỉ lệ **test rộng** (21.454 s). Bản đồ trên dùng 26% cho full suite ≥ 200 s và 31% cho mọi lần chạy test.
- Khi chạy lại phải tính prompt người dạng danh sách khối `text` (không chỉ chuỗi) là "chờ user"; nếu không, một khe 16.809 s ở request 10-03-0015 rơi vào "không rõ" thay vì "chờ" (số máy không đổi).

## Thử nghiệm

### T2.2 — thời gian test

Chạy ngày 2026-10-03 trên bản sao `git clone --local` của repo (commit `ea9f878`, nhánh `docs/nghien-cuu-nen-context`) ở `%TEMP%\tdq-thu-nghiem\t22`; Python 3.13.15, Windows 11, 24 luồng CPU. Mọi lệnh chạy từ gốc bản sao trong **Git Bash**. Repo thật và worktree không chạy test nào; sau khi đo, `git status` của bản sao vẫn sạch, không thêm nhánh hay worktree. Thư mục `%TEMP%\tdq-thu-nghiem` (bản sao + script đo tạm) đã xoá sau khi đo. Đây chỉ là phép đo; request này không đổi workflow.

| # | Phép đo | Kết quả | Lệnh chạy lại (gốc bản sao, Git Bash) |
|---|---|---|---|
| a | Trọn bộ test, một tiến trình | **353,9 s** treo tường · 2.425 test · OK (skipped=29) | `time python -m unittest discover tests` |
| a′ | Như (a) nhưng gọi từ PowerShell | 322,7 s · **26 fail + 1 error** (test_bench 3, test_team_mode 9, test_team_chong_conflict, test_gitflow_doi, test_timing): `'true' is not recognized` — test gọi lệnh `true`, chỉ có trong PATH của Git Bash | `Measure-Command { python -m unittest discover tests }` |
| b | Từng module riêng (126 module, mỗi module một tiến trình) | tổng 355,7 s (≈ (a): phí khởi động mỗi tiến trình không đáng kể); trung vị 0,43 s/module; 10 module chậm nhất = 245,0 s = **68,9%** | `for f in tests/test_*.py; do m=$(basename $f); TIMEFORMAT="$m %R"; time python -m unittest discover tests -p $m 2>/dev/null; done 2>&1 \| sort -k2 -nr \| head -10` |
| c | Vùng chạm của request 0732 (10 module, một tiến trình) | **24,4 s** · 266 test · OK = **6,9%** của (a) (tổng đo riêng từng module: 22,9 s) | `time python -c "import sys,unittest;l=unittest.TestLoader();s=unittest.TestSuite([l.discover('tests',pattern=p) for p in sys.argv[1:]]);sys.exit(not unittest.TextTestRunner().run(s).wasSuccessful())" test_doc_lint_r14.py test_approve_do_truoc.py test_lech_spec.py test_implement_pause.py test_ask_gate.py test_subagent_start.py test_stop_gate.py test_agy_hooks.py test_luat_dung.py test_build_portable.py` |
| d1 | Song song 4 tiến trình (chia module theo thời gian đo ở (b), tham lam: module chậm nhất vào nhóm nhẹ nhất → 4 nhóm ≈ 88,9 s) | lần 1: **149,6 s**, 1 nhóm FAILED (errors=2); lần 2: **180,8 s**, 1 nhóm FAILED (`test_bench.ThucDoTest.test_repo_that_khong_moc_nhanh_hay_worktree_nao`) | như (c), mỗi nhóm một tiến trình chạy cùng lúc; danh sách nhóm sinh từ kết quả (b) |
| d2 | Song song 8 tiến trình (cùng cách chia; nhóm test_bench một mình 72,8 s) | **111,9 s**, 1 nhóm FAILED (errors=4) | như (d1) với 8 nhóm |

Danh sách module vùng chạm ở (c) = mọi file test nêu ở dòng `Test:` và `Chạm:` của `docs/tdq/plan/2026-10-03-0732-do-truoc-lam-mot-turn.md`: `test_doc_lint_r14` 0,35 s · `test_approve_do_truoc` 3,62 · `test_lech_spec` 2,26 · `test_implement_pause` 0,90 · `test_ask_gate` 0,81 · `test_subagent_start` 0,71 · `test_stop_gate` 9,48 · `test_agy_hooks` 2,12 · `test_luat_dung` 0,09 · `test_build_portable` 2,51.

10 module chậm nhất của trọn bộ (đo riêng, lệnh (b)):

| # | Module | Test | Giây | % tổng 355,7 s |
|---|---|---|---|---|
| 1 | `test_bench.py` | 46 | 72,8 | 20,5% |
| 2 | `test_team_mode.py` | 152 | 43,5 | 12,2% |
| 3 | `test_codex_cli.py` | 32 | 33,6 | 9,4% |
| 4 | `test_claude_export.py` | 64 | 22,7 | 6,4% |
| 5 | `test_tdq_finish.py` | 17 | 21,2 | 5,9% |
| 6 | `test_team_chong_conflict.py` | 25 | 20,0 | 5,6% |
| 7 | `test_tu_khoi_tao.py` | 34 | 11,3 | 3,2% |
| 8 | `test_stop_gate.py` | 104 | 9,5 | 2,7% |
| 9 | `test_timing.py` | 30 | 5,4 | 1,5% |
| 10 | `test_gitflow_doi.py` | 4 | 5,1 | 1,4% |
| | **Cộng** | 508 | **245,0** | **68,9%** |

Sáu module đầu (git worktree/nhánh thật, subprocess) chiếm 60,0%; 116 module còn lại cộng 110,7 s.

Song song: nhanh hơn 49–68% treo tường nhưng **chưa dùng được**: lần chạy nào cũng có một nhóm đỏ, mỗi lần một test khác — các test git/worktree dùng chung trạng thái repo (vd. test_bench kiểm "repo thật không mọc nhánh hay worktree nào" trong khi nhóm khác đang tạo). Hai lần 4 tiến trình lệch nhau 21% (149,6 vs 180,8 s), và 4 nhóm cân 88,9 s vẫn mất ≥ 150 s → tranh chấp tài nguyên (git/đĩa), không chỉ chia việc. Muốn song song phải cô lập trạng thái repo cho từng tiến trình trước.

**Tiết kiệm ước tính nếu chạy vùng chạm ở bước trung gian, giữ trọn bộ ở cổng phase.** Giả định:
- Hiện tại 7,4 lần trọn bộ/request (Bản đồ chi phí, 59 lần / 8 request). Sau đổi: **N = 2–3** lần trọn bộ ở cổng (vd. cuối implement + sau sửa QC [+ trước merge]), 7,4 − N lần còn lại thay bằng chạy vùng chạm.
- Một lần chạy vùng chạm ≤ 24,4 s (số (c) là hợp của mọi task trong request; một bước trung gian thường chỉ chạm 1–3 module, trung vị 0,43 s/module → đây là cận trên).
- Giá một lần trọn bộ: 307 s (TB lịch sử, đo nội bộ) đến 353,9 s (đo hôm nay).

| Kịch bản | Trước (7,4 × trọn bộ) | Sau (N × trọn bộ + (7,4 − N) × 24,4 s) | Tiết kiệm/request |
|---|---|---|---|
| N = 3, trọn bộ 307 s | 2.272 s | 921 + 107 = 1.028 s | 1.244 s (54,7%) |
| N = 3, trọn bộ 353,9 s | 2.619 s | 1.062 + 107 = 1.169 s | 1.450 s (55,4%) |
| N = 2, trọn bộ 307 s | 2.272 s | 614 + 132 = 746 s | 1.526 s (67,2%) |
| N = 2, trọn bộ 353,9 s | 2.619 s | 708 + 132 = 840 s | 1.779 s (67,9%) |

→ **Tiết kiệm ≈ 1.240–1.780 s mỗi request (≈ 21–30 phút), tức 55–68% thời gian chạy trọn bộ.** Quy ra thời gian máy: phần trọn bộ ≥ 200 s đang chiếm 26,1% máy, sau đổi còn ≈ 8–12% → giảm ≈ 14–18 điểm % thời gian máy. Rủi ro đổi lại: lỗi ở module ngoài vùng chạm chỉ lộ ở cổng phase (muộn hơn), nên cần cổng trọn bộ thật sự bắt buộc; và vùng chạm phải lấy đúng từ dòng `Chạm:` của plan (với 0732, `Chạm:` đã nêu đủ 10 module test).

### T2.1 — nén file luật

Chạy ngày 2026-10-03 trên bản sao `skills/` (commit `71b8919`, nhánh `docs/nghien-cuu-nen-context`) ở `%TEMP%\tdq-thu-nghiem\t21`; mỗi cách nén chạy trên một bản sao riêng `work\<cách>-<lane>\skills`. Tokenizer thật: `.venv-tokens` + `anthropic_tokenizer.count_tokens`. `skills/` `hooks/` `scripts/` `tests/` `agents/` của repo thật không bị sửa (`git status --porcelain` rỗng); `scripts/doc_index.py` và `scripts/i18n_check.py` của repo chỉ được **gọi** trên bản sao. Thư mục `%TEMP%\tdq-thu-nghiem\t21` (bản sao + script) **đã xoá** sau khi đo.

Tập bắt buộc đọc: đúng danh sách 23 file (full) / 9 file (quick) của spec; SKILL.md chỉ tính thân (bỏ frontmatter `\A---\n.*?\n---\n`), CRLF → LF, đếm từng file rồi cộng. Đếm lại gốc ra 50.893 / 18.631, lệch 5 và 2 token so với số mốc 50.898 / 18.633 (< 0,01%, do cách cắt frontmatter).

| # | Cách nén (trên bản sao) | Full trước → sau | Quick trước → sau | Lệnh chạy lại (trong `%TEMP%\tdq-thu-nghiem\t21`) |
|---|---|---|---|---|
| 0 | Gốc | 50.893 | 18.631 | `python exp.py base --repo=<repo>` |
| 1 | Bỏ chú thích HTML **không phải** marker | 50.893 → 50.893 (**0**) | 18.631 → 18.631 (**0**) | `python exp.py e1 --repo=<repo>` |
| 1b | Giữ mọi marker, chỉ cắt phần lý do sau `i18n-allow:` → `<!-- i18n-allow -->` | → 49.877 (−1.016 · −2,0%) | → 18.271 (−360 · −1,9%) | `python exp.py e1b --repo=<repo>` |
| 2 | Dời khối mẫu/ví dụ sang file em `<tên>-mau.md`, để lại 1 dòng trỏ | → 41.626 (−9.267 · −18,2%) gộp | → 17.295 (−1.336 · −7,2%) gộp | `python exp.py e2 --repo=<repo> -v` |
| 3 | Gộp câu gần trùng (Jaccard 4-gram ký tự ≥ 0,9, câu ≥ 8 từ) — giữ lần đầu theo thứ tự đọc | → 50.337 (−556 · −1,1%) | → 18.572 (−59 · −0,3%) | `python exp.py e3 --repo=<repo> -v` |
| 4 | Kết hợp 1 + 1b + 2 + 3 | → 40.238 (−10.655 · −20,9%) gộp | → 16.928 (−1.703 · −9,1%) gộp | `python exp.py all --repo=<repo> -v` |

Mọi dòng: sau khi sửa, `doc_index.py` của repo được chạy lại trên các file có chỉ mục dòng của bản sao (cách 2/3 làm lệch 9 file full, 1 file quick) rồi `doc_index.py --kiem` → exit 0; số "sau" đã gồm chỉ mục mới. `i18n_check.py` trên bản sao: 133 dòng báo ở gốc = 133 ở 1b (marker rút gọn vẫn có hiệu lực), 132 ở cách 4.

**"Gộp" ≠ "bớt thật".** Cột trên là token rời tập bắt buộc đọc. Phần thật sự không vào context mỗi request (ròng) sau khi trừ khối mẫu vẫn phải đọc vì việc của lane luôn cần nó:

| # | Full ròng/request | Quick ròng/request | Rủi ro chất lượng |
|---|---|---|---|
| 1 | 0 | 0 | — Không có chú thích nào "chỉ để người đọc": toàn bộ 3.419 token chú thích của tập full (6,7%) và 1.233 của quick (6,6%) là marker có công cụ đọc → **không đụng được**: `muc-luc-dong` 15 khối = 1.217 (quick 5 = 530, `doc_index.py`), `i18n-allow` 154 = 2.094 (quick 49 = 703, `i18n_check.py` — luật gắn khối mẫu bằng chú thích ngay trên fence), `luat-gon` 44 (`hooks/scripts/luat_gon.py` cắt khối luật gọn), `luat-mode-allow` 46 (`tests/test_luat_mode.py`), `doc-lint: allow` 18 (`doc_lint.py`). |
| 1b | **1.016** (luôn được) | **360** | Thấp. `i18n_check.py` chỉ tìm chữ `i18n-allow` trong dòng; mất lý do viết cho người sửa file (vì sao dòng đó phải giữ tiếng Việt). Sau 1b còn 2.403 (full) / 873 (quick) token marker thật sự không bớt được. |
| 2 | ≈ **0 – 1.400**; thường ≈ 500 | **−178** (lỗ) | Chia 3 hạng khối dời (số token khối kèm marker, con trỏ ~25–33 token/khối): **A — ví dụ RIGHT/WRONG, không bao giờ chép** (`rules/chung.md` 3 khối 133+130+131, `rules/python.md` 125 = 519; ròng 413): bớt thật, rủi ro agent không mở ví dụ khi phân vân. **B — chỉ dùng theo trường hợp**: `mode-gate.md` khối 3 phương án 551 / 2 phương án 503 (chỉ một khối được in; chỉ bớt được nếu mỗi khối một file em hoặc đọc theo dòng — gộp chung một file em thì đọc lại cả hai), `team-mode.md` khuôn prompt giao task 495 (cần mỗi lần mode subagent — 5/6 request full gần nhất là subagent), `interview.md` 3 khối 378 (cần khi có vòng hỏi). **C — chép mỗi request của lane** (full 7.348: `plan-template` 3.103, `spec-template` 2.454, `report-template` 449, `lane-decision` 70+431, `skill-inventory` 256, `analyze-full` hỏi mức QC 224, `qc.md` 169+192; quick 1.514: `quick-lane` 283+269+328, `lane-decision` 70+431, `quick-lane-qc` 133): file em **vẫn bị đọc** đúng lúc viết spec/plan/QC/report/khối hỏi → không bớt gì, thêm 1 lượt Read + con trỏ (full −253, quick −178). Tạp: khuôn QC trong `qc.md` lồng fence nên bị cắt làm 2 phần, 1 dòng ≈ 20 token còn lại file gốc. |
| 3 | ≈ **280** an toàn (gộp 556) | ≈ **59** | 12 câu trùng (full; 520 token khác file), 2 câu (quick). Không gộp được 274 token: câu "4-layer search order is a MANDATORY rule… Read sections 1 and 2…" lặp **cố ý** ở 4 SKILL.md + `analyze-full.md` (mỗi skill nạp riêng, luật ép từ request 10-03-0015). Còn lại gộp được: `Done when:` / `Next step:` chép từ SKILL.md sang `qc.md`, `report-template.md`, `analyze-full.md`, `quick-lane.md` (marker R3 của `doc_lint.py` chỉ bắt buộc trong SKILL.md, bản gốc vẫn còn), câu "This is the whole of Part C…" (`report-template.md` ≈ `qc.md`). Câu "Write the simplest, most direct code…" trùng giữa `tdq-build/SKILL.md` và `chung.md`: phải xoá ở SKILL.md, **không** ở `chung.md` (nằm trong khối `luat-gon` mà hook bơm cho subagent). |
| 4 | ≈ **1.300 – 2.700**; thường ≈ 1.800 (3,5%) | ≈ **240** (1,3%) | Cộng rủi ro của 1b + 2 + 3. Tính ròng: 10.655 − khối C 7.227 − khối B được dùng (mode-gate 494–542 [hoặc cả 1.036 nếu một file em], team 0/483, interview 0/353) − câu trùng cố ý 274. Chưa trừ phí ~9–11 lượt Read thêm (vài chục token/lượt + một lượt gọi nếu không đọc song song) → ròng thực có thể thấp hơn ≈ 0,4k. Quick: 1.703 − khối C 1.462 = 241, gần như chỉ còn 1b. |

**Quy ra context.** Tập bắt buộc đọc vào context **một lần** mỗi request, rồi nằm lại trong **mọi** lượt gọi API sau đó (đa phần là cache_read) tới khi compact; compact hiếm (4 lần/13 ngày, Bản đồ chi phí). Lượt API mỗi request full: 135–604 (trung vị 378, đo nội bộ §3.2; excalidraw 1.126), quick 17. File luật đọc dần theo phase (intake đầu request, build/QC/report về sau) → giả định mỗi token còn được chở qua 30–80% số lượt của request: **≈ 40–480 lượt**, điển hình ≈ 190 (50% × 378).

| Cách | Token đọc bớt/request (full) | Token chở bớt/request (full, × 40–480 lượt) | Điển hình (× 190) | So với context một request full (378 × 491k ≈ 186M) |
|---|---|---|---|---|
| 1b | 1.016 | 41k – 488k | ≈ 193k | ≈ 0,1% |
| 2 ròng | 0 – 1.400 | 0 – 672k | ≈ 95k (500) | ≈ 0,05% |
| 3 ròng | ≈ 280 | 11k – 134k | ≈ 53k | ≈ 0,03% |
| 4 ròng | 1.300 – 2.700 | 52k – 1,3M | ≈ 342k (1.800) | ≈ 0,2% |
| 4 gộp (cận trên lý thuyết, nếu không file em nào phải đọc lại) | 10.655 | 426k – 5,1M | ≈ 2,0M | ≈ 1,1% |

Quick: ròng ≈ 240 token đọc × ~10 lượt ≈ 2,4k token chở — không đáng kể.

→ **Kết luận T2.1:** nén file luật bằng ba cách này chỉ bớt thật **≈ 1,3–2,7k token đọc/full request (2,6–5,3% tập bắt buộc đọc)**, tức ≈ 0,2% context một request; con số "−20,9%" chỉ là token rời tập bắt buộc đọc, ba phần tư trong đó (khuôn spec/plan/QC/report, khối hỏi) bị đọc lại ngay khi việc cần. Chú thích HTML không phải mỏ: 100% là marker công cụ. Phần chắc ăn và rẻ nhất là 1b (−1.016 / −360, không đổi hành vi, công cụ vẫn xanh) và nhóm A (ví dụ RIGHT/WRONG, −413). So với hội thoại tích luỹ (~491k/lượt, Bản đồ #1), file luật là nguồn nhỏ — nén nó không thay được việc compact/cắt hội thoại.

Cách dựng lại script (đã xoá, viết lại theo mô tả; `<repo>` = gốc worktree, `$py` = `.venv-tokens/Scripts/python.exe`, `PYTHONIOENCODING=utf-8`):
- Chuẩn bị: `New-Item -ItemType Directory -Force $env:TEMP\tdq-thu-nghiem\t21; Copy-Item -Recurse <repo>\skills $env:TEMP\tdq-thu-nghiem\t21\skills`.
- `lane.py`: hai danh sách FULL/QUICK ở trên; `body()` = đọc UTF-8, CRLF → LF, cắt frontmatter của SKILL.md; tổng = Σ `count_tokens(body)`.
- `exp.py <mode>`: chép `skills` sang `work\<mode>-<lane>\skills`, áp bước, chạy `<repo>\scripts\doc_index.py <các file có muc-luc-dong>` rồi `--kiem`, đếm lại bằng `lane.py`. Bước 1: xoá `<!--.*?-->` không khớp `^<!--\s*(muc-luc-dong:|i18n-allow|doc-lint: allow|luat-gon:|luat-mode-allow)`. Bước 1b: `re.sub(r"<!--\s*i18n-allow:[^>]*?-->", "<!-- i18n-allow -->")`. Bước 2: fence ` ``` `/`~~~` ≥ 40 token khớp danh sách 22 dòng đầu (file + dòng đầu khối) của bảng hạng A/B/C trên, mang theo dòng `<!-- i18n-allow… -->` ngay trên fence, thay bằng `→ [<tên>-mau.md](<tên>-mau.md) §k (Read it when needed).`. Bước 3: ghép dòng thành đoạn (ngắt ở dòng trống, mục danh sách, heading, bảng, fence, chú thích khối), tách câu ở `[.!?]` trước khoảng trắng, chuẩn hoá (bỏ chú thích, dấu markdown, chữ thường), so với mọi câu đã gặp trong lane: trùng hash hoặc Jaccard 4-gram ký tự ≥ 0,9 → xoá lần sau.
- Kiểm marker: `$py <repo>\scripts\i18n_check.py work\e1b-full\skills | Select -Last 1` (so với `… skills`).

### T2.3 — hội thoại tích luỹ và cache

Chạy ngày 2026-10-03, **chỉ đọc** transcript tdqwf (`C--Users-admin-Documents-Projects-ForAgentCode-TDQ-Workflow/b77dddd9-….jsonl`, 41,4 MB, 2.661 lượt API sau khử trùng `message.id`, bỏ lượt `<synthetic>`) và `docs/tdq/timing.jsonl`. Script tạm `%TEMP%\tdqt23\t23.py` (Python 3.13) **đã xoá** sau khi đo; mã nguồn đầy đủ ở cuối tiểu mục. Đây là phép ước lượng phản thực (counterfactual) trên số đo cũ, không chạy lại phiên nào; request này không đổi workflow.

**Phạm vi chung.** Request = cửa sổ `[started_at, closed_at]` của `timing.jsonl` có lượt API trong transcript: 9 dòng = 8 request full (09-20-1823 … 10-03-0732) + 1 dòng hủy 09-27-1905 (9 lượt); cộng 2.430 lượt, Σ context 1.216M token, máy 58.569 s, trong đó model 32.172 s (đo nội bộ §3.2). Mốc phase = lệnh `tdq_state.py set phase=<x>` (và `approve plan … --mode` ⇒ implement) trong tool_use Bash/PowerShell, bỏ lệnh thử có `TDQ_PROJECT_DIR`; tổng 52 mốc (kể cả đầu request). Compact thật = `system/compact_boundary`. Đơn vị chi phí = **token input tương đương**: input × 1 + cache_read × 0,05 (Opus 5.5, N1) hoặc × 0,1 (Opus 5, mức chung N1) + ghi cache 1h × 2 / 5m × 1,25 (N2); toàn bộ ghi cache của main là loại 1h (trường `cache_creation.ephemeral_1h_input_tokens`, khớp N5). Quy ra tiền chỉ để minh hoạ: Opus 5.5 input $4/MTok (suy từ N1 + N4: $0,20 = 0,05×). Độ trễ máy = bảng trung vị theo cỡ context ở đo nội bộ §3.4: **thấp** dùng trung vị lượt output < 200 token (2,3 / 2,7 / 3,0 / 3,8 s cho < 100k / 100–300k / 300–600k / > 600k) — tách được hiệu ứng cỡ context khỏi độ dài output; **cao** dùng trung vị mọi lượt (3,9 / 4,4 / 4,9 / 7,3 s) — lẫn cả việc lượt nặng sinh output dài hơn.

#### (i) Tách phiên / compact có chủ đích ở mỗi mốc phase

Phương pháp: với mỗi lượt k sau mốc reset s cùng request, context phản thực `c'ₖ = min(cₖ, R + max(0, cₖ − cₛ))` — tức hội thoại trước mốc được thay bằng R, phần tăng sau mốc giữ nguyên. Nếu trong đoạn đã có compact thật thì từ đó không tính tiết kiệm. Chi phí phản thực: lượt đầu sau mốc ghi lạnh cả R (× 2); lượt vốn là ghi lạnh ≥ 50k ghi c'ₖ thay cₖ; lượt khác giữ nguyên phần input/ghi mới, phần đọc cache = c'ₖ − phần mới. R gồm: prefix cố định (`ctx_first` 38–46k, đo nội bộ §1.1) + phần phải đọc của phase + bản bàn giao 3–5k.
- **R cao (ước thấp)** = 46.000 + 50.893 (cả tập bắt buộc đọc lane full, T2.1 — coi như phase mới đọc lại toàn bộ luật và artifact) + 5.000 = **101.893**.
- **R thấp (ước cao)** = 38.000 + 6.000 (luôn nạp 3.643 + một SKILL.md phase ~2,5k, `skill_tokens.py --theo-phase`, đo nội bộ §4) + 3.000 = **47.000**.

| Kịch bản | Token context bớt (9 cửa sổ) | Mỗi request (÷ 8) | % Σ context | Chi phí bớt (token input tương đương) | Mỗi request | Giây máy bớt (thấp – cao) | Mỗi request |
|---|---|---|---|---|---|---|---|
| Chỉ tách phiên ở đầu request (9 mốc) | 507M – 610M | 63M – 76M | 42% – 50% | 48,7M – 60,0M (37% – 46% của 130,3M) | 6,1M – 7,5M | 879 – 2.698 s | 110 – 337 s |
| Tách/compact ở **mọi** mốc phase (52 mốc) | 755M – 865M | 94M – 108M | 62% – 71% | 67,5M – 84,2M (52% – 65%) | 8,4M – 10,5M | 1.157 – 3.392 s | 145 – 424 s |

Nguồn số đầu vào: context/chi phí từng lượt = `message.usage` của transcript; R = đo nội bộ §1.1, §4 và T2.1; bảng độ trễ = đo nội bộ §3.4; hệ số giá = N1, N2, N5.

Theo request (mọi mốc phase, R cao → R thấp): 09-20-1823 52–64% · 09-21-0029 70–77% · 09-23-1148 68–79% · 09-27-1905 77–84% · 09-28-0910 47–63% · 09-28-2324 58–64% · 10-03-0015 65–72% · 10-03-0732 57–71% token context. Chỉ tách ở đầu request thì chênh lớn giữa các request (8% ở 09-28-0910, 10% ở 09-20-1823 vì phiên vừa compact/mới mở; 58–70% ở 09-21, 09-27) — phần lớn tiết kiệm đến từ việc **không chở hội thoại của request trước**; cắt thêm ở mỗi phase cộng ≈ 20 điểm %.

Quy đổi: 67,5M – 84,2M token input tương đương ≈ **$270 – $337** cho 8 request theo giá Opus 5.5 (≈ $34 – $42/request). Thời gian máy bớt 1.157 – 3.392 s = **2,0% – 5,8% máy** (3,6% – 10,5% thời gian model); cận thấp (cùng cỡ output) đáng tin hơn. Phí chưa trừ: mỗi mốc sinh một bản bàn giao 3–5k token output (52 mốc ≈ 156k – 260k output, tức 20k – 33k/request — nhỏ hơn hai bậc so với phần bớt) và một lượt ghi lạnh R (đã trừ trong cột chi phí). Rủi ro chất lượng: mất chi tiết không nằm trong bàn giao/artifact; ngược lại, context ngắn hơn giảm "context rot" (N22) và sau compact Claude Code chỉ giữ 5.000 token đầu mỗi skill, **không** gắn lại file luật đọc bằng Read (N9) — nên compact chủ đích phải kèm đọc lại phần phải đọc của phase, đúng như R cao đã tính.

#### (ii) Đẩy việc đọc nặng cho trợ lý chỉ trả tóm tắt

Phương pháp: mỗi tool_result (Bash/PowerShell/Read/Grep) ≥ ngưỡng T ký tự trong cửa sổ request được thay bằng bản tóm ≤ 1.500 ký tự; token bớt = (ký tự − 1.500) / hệ số ký tự/token (Bash 2,75 · PowerShell 2,78 · Read 2,65 · Grep 2,7, đo nội bộ §0) − prompt giao P (nằm lại ở main), nhân với số lượt API còn lại tới compact thật hoặc hết request (không cộng dồn với (i)). Phí trợ lý trả ở context **của nó**, không ở main: ≥ 2 lượt × S₀ (lượt đầu cố định) + nội dung đọc; chi phí = (S₀ + nội dung) × 1,25 (subagent ghi cache 5m, N5; subagent thường không chia cache với main) + S₀ × 0,1. Thời gian: mỗi lần giao tốn ≥ 2 lượt × ~3,9 s (bucket < 100k) nếu main chờ.

| Kịch bản | Lệnh được giao | Token context main bớt (9 cửa sổ) | Mỗi request | % Σ context | Chi phí ròng (gồm phí trợ lý) | Token trợ lý thêm | Giây model main bớt | Giây chờ trợ lý thêm (≥ n × 7,8 s) |
|---|---|---|---|---|---|---|---|---|
| Thấp: chỉ Bash/PowerShell ≥ 8.000 ký tự, bỏ output `tdq_*.py`/`doc_lint` (chỉ dẫn cho agent), S₀ = 25,9k, P = 500 | 21 | 9,7M | 1,2M | 0,8% | **+0,22M** (lãi ≈ $0,9 tổng) | 1,17M | 18 – 40 s | ≈ 164 s |
| Cao: Bash/PowerShell/Read/Grep ≥ 3.000 ký tự, S₀ = 22,1k, P = 200 | 155 | 31,4M | 3,9M | 2,6% | **−1,73M** (lỗ ≈ $7 tổng) | 7,17M | 43 – 93 s | ≈ 1.209 s |

Nguồn số đầu vào: độ dài tool_result và vị trí lượt = transcript; S₀ 22,1k / 25,9k = lượt đầu subagent tdqwf / exc1 (đo nội bộ §1.1); bản tóm 1.000–2.000 token (N13) → chọn 1.500 ký tự (chặt hơn); fork chia cache với main, subagent thường không (kiểm chéo, N5).

Vì sao nhỏ: trong 2.075 tool_result đọc ở 9 cửa sổ, chỉ 155 cái ≥ 3.000 ký tự (39% ký tự) và 31 cái ≥ 8.000 (14%); 456k token "đọc bằng shell" của Bản đồ #4 rải trên 895 lệnh, TB ≈ 1.400 ký tự/lệnh — đã nhỏ hơn bản tóm. Phần main bớt là đọc cache rẻ (0,05–0,1×), còn trợ lý phải **ghi** cache ~22–26k mỗi lần (1,25×) ⇒ giao lẻ từng lệnh **lỗ** về chi phí và thời gian (thêm 164 – 1.209 s chờ để bớt 18 – 93 s model). Chỉ có lời khi một trợ lý gom **nhiều** lần đọc nặng của cùng một việc (một S₀ cho nhiều kết quả) và chạy nền — đúng là cách mode subagent đang làm cho task build. → **Ước lượng ròng (ii): ≈ 0 – 1,2M token context main/request (0 – 0,8%), chi phí ròng ≈ −0,2M … +0,03M/request**; thấp hơn (i) hai bậc.

#### (iii) Giữ tiền tố ổn định — 24 lượt ghi cache lạnh

Phương pháp: lượt `cache_creation_input_tokens` ≥ 50.000 (như Bản đồ #2), phân loại theo thứ tự: có `compact_boundary` ngay trước → compact; model khác lượt trước (bỏ `<synthetic>`) → đổi model; khe thời gian từ lượt API trước > 1 h → hết TTL 1h (N5); 5 phút – 1 h → khác; còn lại → khác. Đã soát thêm từng lượt: có hook `SessionStart:resume` ở 5/24 lượt (#3, #8, #14, #19, #23) nhưng cả 5 đều có khe > 1 h ⇒ resume không phải nguyên nhân riêng; không có skill nào mang `model:` trước lượt lạnh; không có lượt lạnh nào sau khe 5 phút – 1 h.

| Nguyên nhân | Lượt | Token ghi | Khe trước lượt | Tránh được? | Tiết kiệm nếu tránh (token input tương đương) |
|---|---|---|---|---|---|
| Compact (09-28 02:35, 10-02 10:36) | 2 | 0,12M (58k, 65k) | 2–3 phút | Không — đã là bản nhỏ sau compact | 0 |
| Đổi model Opus 5 → Opus 5.5 (10-02 15:54) | 1 | 0,49M | 9 phút (cache vẫn ấm) | **Có**: đổi model đúng lúc cache đã lạnh hoặc ngay sau một mốc reset/compact | 0,49M × (2 − 0,1) ≈ **0,92M** (≈ $3,7) |
| User vắng > 1 h (TTL 1h hết) | 21 | 11,11M | 66 phút – 84 giờ; 6 lượt < 90 phút = 2,85M | Không tránh việc ghi (cần giữ cache ấm — Claude Code không có, và đổi workflow); **thu nhỏ được** bằng (i) | xem dưới |
| **Cộng** | **24** | **11,72M** (73,9% cache_creation 15,88M toàn file) | | | |

Thu nhỏ bằng (i): trong 9 cửa sổ có 7,78M token ghi lạnh (phần còn lại 3,94M nằm giữa hai request hoặc trong request đang mở). Với context phản thực của (i), cùng các lượt lạnh đó chỉ ghi **1,57M – 2,34M** (reset mọi phase) hoặc 3,97M – 4,63M (chỉ đầu request) ⇒ bớt 5,4M – 6,2M token ghi = **10,9M – 12,4M token input tương đương** (≈ $44 – $50 cho 8 request) — **đã nằm trong** cột chi phí của (i), không cộng thêm. Đổi lại, (i) tự sinh 52 lượt ghi lạnh cỡ R (47k – 102k) ở mốc phase; đã trừ trong (i).

→ **Ước lượng (iii) riêng: 1/24 lượt tránh được (0,49M token ghi, ≈ 0,9M token input tương đương ≈ 4% chi phí ghi lạnh); cận cao lý thuyết 7/24 (thêm 6 lượt khe 66–90 phút, 2,85M) nếu có cơ chế giữ cache ấm — ngoài phạm vi vì đổi workflow.** Đòn bẩy thật cho ghi lạnh là cỡ context lúc user quay lại, tức (i). Không thấy lượt lạnh nào do CLAUDE.md/skill/tool đổi giữa phiên (mọi lượt ngoài compact/đổi model đều sau khe > 1 h). Ghi nhận phụ: 10 lượt lạnh đầu (tới 09-28) vẫn đọc cache 29.951 token (phần system prompt dùng chung), từ lượt sau compact 09-28 thì đọc 0 — transcript không cho biết vì sao, chênh ≈ 30k × 14 lượt ≈ 0,4M token ghi.

#### Kết luận T2.3

| Đòn bẩy | Token context bớt / request | Chi phí bớt / request (token input tương đương) | Giây máy bớt / request | Ghi chú |
|---|---|---|---|---|
| (i) tách/compact ở mỗi mốc phase | **94M – 108M (62–71%)** | 8,4M – 10,5M (52–65%) | 145 – 424 s (2,0–5,8% máy) | lớn nhất; chất lượng phụ thuộc bản bàn giao + đọc lại luật phase (N9) |
| (i′) chỉ tách phiên ở đầu request | 63M – 76M (42–50%) | 6,1M – 7,5M | 110 – 337 s | rẻ nhất về rủi ro: artifact spec/plan/report đã là bàn giao |
| (ii) trợ lý đọc nặng chỉ trả tóm tắt | 0 – 1,2M (0–0,8%) ròng | −0,2M … +0,03M | âm (chờ trợ lý > phần bớt) | chỉ lời khi gom nhiều lần đọc và chạy nền |
| (iii) tiền tố ổn định | 0 (context không đổi) | ≈ 0,1M (1 lượt đổi model) | ≈ 0 | ghi lạnh do user vắng > 1 h; thu nhỏ qua (i) |

Giới hạn: một phiên (tdqwf, phát triển chính workflow, ít compact) — exc1 không đo lại ở đây; mô hình độ trễ là trung vị theo bucket, không hồi quy; phản thực giả định phần tăng sau mốc không đổi (thực tế agent có thể phải đọc lại nhiều hơn R cao). Số thô: chạy lệnh dưới.

Mã nguồn script (chạy: `python t23.py "<…>/projects/C--Users-admin-Documents-Projects-ForAgentCode-TDQ-Workflow/b77dddd9-9fc5-4b98-9a39-c7aaf7e1b748.jsonl" docs/tdq/timing.jsonl`, `PYTHONIOENCODING=utf-8`; transcript đang lớn lên nên số có thể nhích nhẹ):

```python
# T2.3 — hội thoại tích luỹ và cache. Chỉ đọc. python t23.py <transcript tdqwf .jsonl> <docs/tdq/timing.jsonl>
import json, re, sys
from datetime import datetime
F = sys.argv[1]
ts = lambda s: datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
LAT_HI = [(1e5, 3.9), (3e5, 4.4), (6e5, 4.9), (9e9, 7.3)]   # do-noi-bo §3.4: trung vị mọi lượt
LAT_LO = [(1e5, 2.3), (3e5, 2.7), (6e5, 3.0), (9e9, 3.8)]   # trung vị lượt output < 200 token
lat = lambda c, T: next(v for b, v in T if c < b)
RATIO = {'Bash': 2.75, 'PowerShell': 2.78, 'Read': 2.65, 'Grep': 2.7}   # ký tự/token, do-noi-bo §0
calls, marks, results, tools, seen = [], [], [], {}, set()
for line in open(F, encoding='utf-8'):
    d = json.loads(line); t = d.get('type')
    if t == 'system' and d.get('subtype') == 'compact_boundary':
        marks.append((len(calls), ts(d['timestamp']), 'compact')); continue
    if t == 'assistant':
        m = d['message']; u = m.get('usage') or {}
        if m.get('model') == '<synthetic>' or not u: continue
        for c in m.get('content') or []:
            if c.get('type') == 'tool_use':
                i = c.get('input') or {}
                cmd = str(i.get('command') or i.get('file_path') or i.get('pattern') or '')
                tools[c['id']] = (c['name'], cmd)
                if c['name'] in ('Bash', 'PowerShell') and 'TDQ_PROJECT_DIR' not in cmd:   # bỏ lệnh thử trong test
                    for mm in re.finditer(r'tdq_state\.py"?\s+(set\s+phase=(\w+)|approve\s+plan[^\n;|&]*--mode)', cmd):
                        marks.append((len(calls) + 1, ts(d['timestamp']), mm.group(2) or 'implement'))
        if m['id'] in seen: continue
        seen.add(m['id']); e = u.get('cache_creation') or {}
        calls.append(dict(t=ts(d['timestamp']), model=m['model'], inp=u.get('input_tokens', 0),
            rd=u.get('cache_read_input_tokens', 0), cc=u.get('cache_creation_input_tokens', 0),
            c1h=e.get('ephemeral_1h_input_tokens', 0), c5m=e.get('ephemeral_5m_input_tokens', 0)))
    if t == 'user' and isinstance(d['message']['content'], list):
        for c in d['message']['content']:
            if c.get('type') == 'tool_result' and c.get('tool_use_id') in tools:
                x = c.get('content'); n = len(x) if isinstance(x, str) else sum(len(y.get('text', '')) for y in x or [])
                results.append((len(calls), *tools[c['tool_use_id']], n))
N = len(calls)
for c in calls: c['ctx'] = c['inp'] + c['rd'] + c['cc']; c['r'] = 0.05 if '5-5' in c['model'] else 0.1
cost = lambda c: c['inp'] + c['rd'] * c['r'] + c['c1h'] * 2 + c['c5m'] * 1.25   # token input tương đương (N1, N2)
# request = cửa sổ [started_at, closed_at] của docs/tdq/timing.jsonl (argv[2]); mốc reset = đầu request + mỗi phase mới
reqs = []
for line in open(sys.argv[2], encoding='utf-8'):
    j = json.loads(line); A, B = ts(j['started_at']), ts(j['closed_at'])
    ks = [k for k, c in enumerate(calls) if A <= c['t'] < B]
    if not ks: continue
    q = dict(slug=j['slug'], a=ks[0], b=ks[-1] + 1, resets=[ks[0]], compacts=[], last=None); reqs.append(q)
    for k, tt, v in sorted(marks):
        if not (A <= tt < B): continue
        if v == 'compact': q['compacts'].append(k)
        elif v != q['last'] and v != 'idle' and k > q['resets'][-1] and k < q['b']: q['resets'].append(k); q['last'] = v
def lever_i(q, R, every_phase=True):
    s, cut, sv, cu, lt, lt2, cw = None, False, 0, 0, 0, 0, 0
    for k in range(q['a'], min(q['b'], N)):
        c = calls[k]
        if k in (q['resets'] if every_phase else q['resets'][:1]): s, cut = k, False
        if s is not None and any(s < x <= k for x in q['compacts']): cut = True
        cf = c['ctx'] if s is None or cut else min(c['ctx'], R + max(0, c['ctx'] - calls[s]['ctx']))
        if (k == s and not cut) or c['cc'] >= 50000: c2 = cf * 2               # ghi lạnh cỡ cf (1h = 2x)
        else: c2 = c['inp'] + c['cc'] * (2 if c['c1h'] else 1.25) + max(0, cf - c['inp'] - c['cc']) * c['r']
        sv += c['ctx'] - cf; cu += cost(c) - c2; cw += cf if c['cc'] >= 50000 else 0
        lt += lat(c['ctx'], LAT_LO) - lat(cf, LAT_LO); lt2 += lat(c['ctx'], LAT_HI) - lat(cf, LAT_HI)
    return sv, cu, lt, lt2, cw
def lever_ii(q, ok, T, S0, P, skip_tdq):
    ends = sorted(q['compacts'] + [q['b']]); gain = cu = add = n = 0; red = [0] * N
    for k, name, cmd, ch in results:
        if not (q['a'] <= k < q['b']) or name not in ok or ch < T: continue
        if skip_tdq and re.search(r'tdq_\w+\.py|doc_lint', cmd): continue
        tok = (ch - 1500) / RATIO[name] - P; end = min(next(e for e in ends if e > k), N)
        n += 1; gain += tok * (end - k); add += 2 * S0 + ch / RATIO[name]
        cu += tok * sum(calls[j]['r'] for j in range(k, end)) + tok * 2 - (S0 + ch / RATIO[name]) * 1.25 - S0 * 0.1
        for j in range(k, end): red[j] += tok
    rng = range(q['a'], min(q['b'], N))
    lt = sum(lat(calls[j]['ctx'], LAT_LO) - lat(max(0, calls[j]['ctx'] - red[j]), LAT_LO) for j in rng)
    lt2 = sum(lat(calls[j]['ctx'], LAT_HI) - lat(max(0, calls[j]['ctx'] - red[j]), LAT_HI) for j in rng)
    return n, gain, cu, add, lt, lt2
M = lambda x: f'{x/1e6:.2f}M'
RLO, RHI = 46000 + 50893 + 5000, 38000 + 6000 + 3000   # R cao (ít tiết kiệm) / R thấp (nhiều tiết kiệm)
print('calls', N, 'requests', len(reqs), 'compacts', sum(1 for m in marks if m[2] == 'compact'))
S = {}
for q in reqs:
    rng = range(q['a'], min(q['b'], N)); ctx = sum(calls[k]['ctx'] for k in rng) or 1; c0 = sum(cost(calls[k]) for k in rng) or 1
    out = dict(ctx=ctx, cost=c0, n=len(rng), cold=sum(calls[k]['cc'] for k in rng if calls[k]['cc'] >= 50000),
               rq_lo=lever_i(q, RLO, False), rq_hi=lever_i(q, RHI, False), ph_lo=lever_i(q, RLO), ph_hi=lever_i(q, RHI),
               off_lo=lever_ii(q, ('Bash', 'PowerShell'), 8000, 25900, 500, True), off_hi=lever_ii(q, tuple(RATIO), 3000, 22100, 200, False))
    for k, v in out.items(): S.setdefault(k, []).append(v)
    r = out; print(f"{q['slug'][:28]:28} n={r['n']:4} resets={len(q['resets'])} ctx={M(ctx)} cost={M(c0)} cold={M(r['cold'])}")
    for key in ('rq_lo', 'rq_hi', 'ph_lo', 'ph_hi'):
        v = r[key]; print(f"   (i) {key}: tok {M(v[0])} ({v[0]/ctx:.0%}) cost {M(v[1])} ({v[1]/c0:.0%}) s {v[2]:.0f}/{v[3]:.0f} coldwrite' {M(v[4])}")
    for key in ('off_lo', 'off_hi'):
        v = r[key]; print(f"   (ii) {key}: n={v[0]} tok {M(v[1])} ({v[1]/ctx:.1%}) cost {M(v[2])} ({v[2]/c0:.1%}) sub+ {M(v[3])} s {v[4]:.0f}/{v[5]:.0f}")
tot = lambda key, i: sum(v[i] for v in S[key])
print('TOTAL ctx', M(sum(S['ctx'])), 'cost', M(sum(S['cost'])), 'cold', M(sum(S['cold'])))
for key in ('rq_lo', 'rq_hi', 'ph_lo', 'ph_hi'):
    print(f"  {key}: tok {M(tot(key,0))} ({tot(key,0)/sum(S['ctx']):.0%}) cost {M(tot(key,1))} ({tot(key,1)/sum(S['cost']):.0%}) s {tot(key,2):.0f}/{tot(key,3):.0f} coldwrite' {M(tot(key,4))}")
for key in ('off_lo', 'off_hi'):
    print(f"  {key}: n={tot(key,0)} tok {M(tot(key,1))} ({tot(key,1)/sum(S['ctx']):.1%}) cost {M(tot(key,2))} sub+ {M(tot(key,3))} s {tot(key,4):.0f}/{tot(key,5):.0f}")
inw = [r for r in results if r[1] in RATIO and any(q['a'] <= r[0] < q['b'] for q in reqs)]
for T in (1500, 3000, 8000):
    g = [r for r in inw if r[3] >= T]; print(f'results>={T}: {len(g)}/{len(inw)} chars {sum(r[3] for r in g)/max(1, sum(r[3] for r in inw)):.0%}')
cmp = {m[0] for m in marks if m[2] == 'compact'}; rows = []
for k, c in enumerate(calls):
    if k == 0 or c['cc'] < 50000: continue
    dt = c['t'] - calls[k - 1]['t']
    why = 'compact' if k in cmp else 'model' if c['model'] != calls[k - 1]['model'] else 'ttl>1h' if dt > 3600 else 'ttl>5m' if dt > 300 else 'khac'
    rows.append((why, c['cc'], dt))
for w in sorted({r[0] for r in rows}):
    g = [r for r in rows if r[0] == w]
    print('cold', w, len(g), M(sum(r[1] for r in g)), 'dt min %.0f-%.0f' % (min(r[2] for r in g) / 60, max(r[2] for r in g) / 60),
          '<90min', sum(1 for r in g if r[2] < 5400), M(sum(r[1] for r in g if r[2] < 5400)))
print('cold total', len(rows), M(sum(r[1] for r in rows)), 'all cc', M(sum(c['cc'] for c in calls)))
```

## Bảng đề xuất

Mỗi hướng một dòng; mọi số lấy từ các mục trên của báo cáo này hoặc từ `docs/tdq/research/2026-10-03-1101-do-noi-bo.md` (gọi tắt "đo nội bộ"), nguồn ghi ở cột cuối. Phép tính duy nhất thêm ở đây là nhân/chia trên các số đó, có ghi cách tính. "Thời gian máy" = agent làm việc + tool + test, **không** gồm thời gian chờ user. Token input tương đương và giá $ theo cách quy đổi của T2.3 (Opus 5.5: đọc cache 0,05×, ghi 1h 2×, N1/N2; input $4/MTok). Cột "Công sức" là ước lượng định tính (nhỏ / vừa / lớn), chưa đo. Không có số bên ngoài nào thuộc nhóm "không xác minh được" (N29, N30, N34–N38) được dùng. Bảng **không** xếp thứ tự làm — thứ tự ở mục sau.

Đọc nhanh nơi có tiền: (a) hội thoại tích luỹ là mỏ duy nhất cỡ chục triệu token mỗi request (H1, H2); (b) test là mỏ thời gian máy lớn nhất đo được (H5); (c) file luật và hook chỉ là phần lẻ (H7–H9, ≤ 0,2% context); giảm cổng duyệt (H10, H11) gần như không bớt thời gian máy.

| Mã | Hướng | Nhóm (a/b/c) | Tiết kiệm context | Tiết kiệm thời gian máy | Cái giá chất lượng / kiểm soát | Công sức (ước lượng) | Rủi ro | Codex | Nguồn số |
|---|---|---|---|---|---|---|---|---|---|
| H1 | Tách phiên / compact có chủ đích ở **mọi** mốc phase, kèm bản bàn giao 3–5k và đọc lại luật của phase | a | **94M – 108M token/request (62–71%)**; chi phí 8,4M – 10,5M token input tương đương (52–65%) ≈ **$34 – $42/request** | 145 – 424 s/request (2,0–5,8% máy); cận thấp đáng tin hơn | Mất chi tiết không nằm trong bàn giao/artifact; phí bàn giao 20k – 33k token output/request. Bù lại: context ngắn giảm context rot (N22) | Lớn | Agent phải đọc lại nhiều hơn R cao đã tính → tiết kiệm thật thấp hơn; compact không gắn lại file luật đọc bằng Read (N9) — quên đọc lại là mất luật | Áp được về nguyên lý (phiên mới + artifact làm bàn giao); không bơm bàn giao qua SessionStart vì `additionalContext` lỗi trên codex-cli 0.154.0 (N33); giá/TTL cache của Codex chưa kiểm | T2.3 (i) bảng "Kết luận T2.3" dòng (i); N9, N22, N33 |
| H2 | Chỉ tách phiên ở **đầu** mỗi request (không chở hội thoại request trước) | a | **63M – 76M token/request (42–50%)**; chi phí 6,1M – 7,5M token input tương đương | 110 – 337 s/request | Gần như không mất gì: spec/plan/report đã là bàn giao giữa các request. Chênh lớn giữa request (8–10% khi phiên vừa compact/mới mở, 58–70% ở 09-21, 09-27) | Nhỏ | Thấp; mất ngữ cảnh "trò chuyện" giữa hai request liên quan | Áp được nguyên vẹn (mở phiên Codex mới mỗi request) | T2.3 (i) dòng "Chỉ tách phiên ở đầu request" và dòng (i′) |
| H3 | Đổi model ngay sau mốc reset/compact hoặc khi cache đã lạnh, không đổi giữa lúc cache ấm | a | 0 (context không đổi) | ≈ 0 s | Không | Nhỏ (một câu luật) | Không đáng kể | Không áp được như số đo (cơ chế cache Codex chưa kiểm) | T2.3 (iii) dòng "Đổi model": 0,92M token input tương đương ≈ $3,7 **một lần** trong cả phiên — **giá trị thấp** |
| H4 | Giao việc đọc output nặng cho trợ lý chỉ trả tóm tắt, **giao lẻ** từng lệnh | a | 0 – 1,2M token/request (0–0,8%) ròng; chi phí ròng −0,2M … +0,03M token input tương đương/request (có thể **lỗ**) | **Âm**: trên 9 cửa sổ thêm ≈ 164 – 1.209 s chờ trợ lý để bớt 18 – 93 s model | Bản tóm có thể bỏ sót chi tiết mà main cần | Vừa | Lỗ tiền và giờ máy; **không nên làm** ở dạng giao lẻ — chỉ có lời khi gom nhiều lần đọc của một việc và chạy nền (mode subagent đã làm) | Như Claude Code về nguyên lý; không dùng số giới hạn subagent của Codex (N34 không xác minh được) | T2.3 (ii) bảng hai kịch bản; N13 |
| H5 | Bước trung gian chỉ chạy test **vùng chạm** (lấy từ dòng `Chạm:` của plan); trọn bộ chỉ ở **2–3 cổng phase** (cuối implement, sau sửa QC [, trước merge]) | b | Chưa đo (output test nhỏ so với hội thoại) | **≈ 1.240 – 1.780 s/request** (55–68% thời gian trọn bộ; trọn bộ ≥ 200 s từ 26,1% xuống ≈ 8–12% máy) | Lỗi ở module ngoài vùng chạm lộ muộn hơn (ở cổng phase thay vì ngay bước đó); cổng trọn bộ phải thật sự bắt buộc | Nhỏ – vừa (gỡ mâu thuẫn luật: "EXACTLY ONCE" ở `tdq-build/SKILL.md` với "sau mỗi phase chạy toàn bộ" ở `plan-template.md` và vòng fix QC ở `qc.md`) | `Chạm:` thiếu module → bước trung gian xanh giả; 27 test đỏ khi gọi từ PowerShell (`true`) → lệnh test phải chạy trong Git Bash, nếu không cổng đỏ giả | Áp nguyên vẹn (lệnh test không phụ thuộc agent) | T2.2 bảng kịch bản N = 2–3 và dòng (a), (a′), (c); Bản đồ chi phí thời gian máy #2a; đo nội bộ §5.1 |
| H6 | Chạy trọn bộ **song song** (4–8 tiến trình) sau khi cô lập trạng thái git/worktree cho từng tiến trình | b | 0 | Mỗi lần trọn bộ 353,9 s → 111,9 – 180,8 s (nhanh hơn 49–68%); với 2–3 lần trọn bộ/request còn lại sau H5 ≈ 346 – 726 s/request (= 2–3 × 173,1 – 242,0 s) | **Hiện chưa dùng được**: lần chạy nào cũng có một nhóm đỏ, mỗi lần một test khác | Lớn (cô lập repo tạm cho các test git/worktree) | Test chập chờn làm mất tin vào cổng; hai lần 4 tiến trình lệch nhau 21% → tranh chấp git/đĩa | Áp nguyên vẹn | T2.2 dòng (a), (d1), (d2) và đoạn "Song song" |
| H7 | Nén file luật: rút gọn marker `i18n-allow` (1b), dời ví dụ RIGHT/WRONG hạng A, gộp câu gần trùng không cố ý (3) | c | ≈ 1,3k – 2,7k token đọc/full request (điển hình 1,8k ≈ 3,5% tập bắt buộc đọc); chở qua các lượt ≈ 342k (52k – 1,3M) ≈ **0,2% context một request**; quick ≈ 240 token | ≈ 0 s (chưa đo, không kỳ vọng) | Thấp: mất lý do viết cho người sửa file (1b); agent có thể không mở ví dụ khi phân vân (A) | Vừa | Thấp; dời khuôn spec/plan/QC/report (hạng C) **lỗ** vì vẫn bị đọc lại. **Giá trị thấp** — không thay được H1/H2 | Lợi tương đối lớn hơn nếu luật nằm trong AGENTS.md (trần 32 KiB cắt im lặng, N11) hoặc listing skill (≤ 2% context, N10) | T2.1 bảng "ròng" và "Quy ra context", Kết luận T2.1; N10, N11 |
| H8 | SessionStart lúc **resume** không bơm lại toàn văn luật gặt `[TDQ:GON]` (giữ ở startup; UserPromptSubmit đã có bản tóm 1 dòng) | c | ≈ 1,9k token × 22 resume ≈ 42k token/phiên exc1 (exc2: 13 × 1,9k ≈ 25k) — nhỏ | ≈ 0 s | Nếu phiên bị compact giữa chừng thì bản toàn văn có thể rơi khỏi context — cần bơm lại sau compact | Nhỏ | Agent làm trái luật gặt ở phiên resume dài | Không áp: SessionStart `additionalContext` vốn không bơm được trên codex-cli 0.154.0 (N33) | Đo nội bộ §2 (bảng hook, dòng SessionStart resume), §5.4; Bản đồ chi phí context #6 |
| H9 | Không sửa plan/QC ngoài lượt khi main đã đọc file đó (vd. gom sổ sách team ghi một lần), để harness khỏi chèn lại snippet `edited_text_file` | c | Cận trên ≈ 204k token/phiên tdqwf (381 lần); exc1 ≈ 13k | ≈ 0 s | Main thấy trạng thái plan chậm hơn nếu sổ sách bị gom | Nhỏ – vừa | Cơ chế chưa tách đủ để ước phần ròng tránh được — số là cận trên | Chưa rõ (cơ chế chèn snippet là của harness Claude Code) | Bản đồ chi phí context #5; đo nội bộ §1.5, §1.6, §5.5 |
| H10 | **Giảm cổng duyệt**: gộp duyệt spec và duyệt plan thành **một** cổng (trình spec + plan cùng lúc) | a (gián tiếp) | Gián tiếp: mỗi lần chờ > 1 h bị bỏ tránh một lần ghi cache lạnh TB ≈ 0,53M token (11,11M / 21) ≈ 1,0M token input tương đương (0,53M × (2 − 0,05)) ≈ $4; số cổng chờ > 1 h bị bỏ **chưa đo**; nếu đã có H1 thì lần ghi lạnh chỉ còn cỡ R (47k – 102k) | **≈ 0 s máy**: việc viết spec/plan vẫn phải làm; chỉ bớt thời gian chờ (ngoài mục tiêu). Spec bị bác sau khi plan đã viết → **tốn thêm** máy của plan (5.942 s máy cho phase plan trên 11 cửa sổ) | **Kiểm soát**: user mất điểm dừng giữa "làm gì" và "làm thế nào"; sai hướng ở spec chỉ thấy khi đọc cả hai, và plan phải viết lại | Vừa | Lỗi spec lan vào plan; user duyệt lướt một khối lớn hơn | Áp nguyên vẹn (cổng là luật skill + script state) | T2.3 (iii) dòng "User vắng > 1 h"; đo nội bộ §3.3 (plan 5.942 s máy, chờ 17.628 s; spec 1.788 / 7.379 s) |
| H11 | **Giảm cổng duyệt**: QC sạch thì tự đi tiếp tới report, không dừng hỏi; vẫn giữ duyệt merge/đóng request | a (gián tiếp) | Gián tiếp như H10 (≈ 1,0M token input tương đương mỗi lần chờ > 1 h được bỏ); số lần **chưa đo** | **≈ 0 s máy**; chỉ bớt chờ ở qc/report (171.316 s và 83.566 s chờ trên 11 cửa sổ — ngoài mục tiêu, và không phải toàn bộ là chờ cổng) | **Kiểm soát**: user không còn xem kết quả QC trước khi report được viết; nếu QC (do agent chấm) "sạch" sai thì lỗi đi thẳng tới bước merge | Nhỏ – vừa | QC sai dương tính sạch; giữ cổng merge là chốt chặn cuối | Áp nguyên vẹn | T2.3 (iii); đo nội bộ §3.3 (qc 3.779 s máy, report 5.547 s máy) |

**H1 — tách/compact ở mọi mốc phase.** Workflow đổi: mỗi lần chuyển phase (analyze → spec → plan → implement → qc → report), phiên làm việc được khép bằng một bản bàn giao ngắn (việc đã quyết, file đã chạm, việc còn mở) rồi mở lại sạch; phase mới đọc lại SKILL.md và các reference của chính nó, cộng artifact (spec/plan/QC). Số đáng tin vì là phản thực trên đúng 2.430 lượt API của 9 cửa sổ request thật, đã tính phí ghi lạnh R ở mỗi mốc và lấy R cao = đọc lại cả tập bắt buộc đọc 50.893 token (T2.3 (i)); khoảng 62–71% đến từ hai đầu R. Điều có thể sai: phần tăng sau mốc được giả định không đổi — nếu agent phải đọc lại code/log nhiều hơn R, tiết kiệm co lại; bản bàn giao thiếu một quyết định thì phase sau làm lại hoặc làm sai — đây là cái giá chất lượng, đi ngược soul nếu không kiểm. Đo sau khi đổi: chạy lại script T2.3 trên transcript các request mới (context TB/lượt, Σ token input tương đương/request, số lượt ghi lạnh), và so số phát hiện QC-F/vòng sửa QC mỗi request với 8 request trước để bắt suy giảm chất lượng.

**H2 — tách phiên ở đầu request.** Workflow đổi: mỗi request mới bắt đầu ở phiên mới (hoặc compact ngay sau intake), thay vì nối tiếp phiên của request trước. Số đáng tin cùng lý do H1 (cùng phản thực T2.3 (i), 9 mốc), và dao động giữa request được giải thích rõ: request nào mở trên phiên vừa compact thì gần như không lợi. Điều có thể sai: hai request liền nhau dùng chung bối cảnh mà artifact không ghi lại; nhưng spec/plan/report đã là bàn giao chuẩn nên rủi ro thấp nhất trong nhóm (a). Đo sau: tỉ lệ context ở lượt API đầu mỗi request (kỳ vọng ≈ prefix 38–46k thay vì hàng trăm nghìn) và Σ context/request theo script T2.3.

**H3 — đổi model đúng lúc.** Workflow đổi: khi cần đổi model, làm ngay sau mốc reset/compact hoặc sau khi user vắng lâu (cache đã lạnh). Số đáng tin vì là đúng một lượt đổi model đo được trong transcript (0,49M token ghi khi cache còn ấm 9 phút, T2.3 (iii)); nhưng chỉ một lần trong cả phiên nên giá trị thấp. Có thể sai: không gì đáng kể. Đo sau: đếm lượt ghi lạnh ≥ 50k có model khác lượt trước (phân loại "model" của T2.3 (iii)).

**H4 — trợ lý đọc nặng giao lẻ.** Ghi vào bảng để nói thẳng: hướng này **không** có lời. Số đáng tin vì tính cả hai phía — phần main bớt là đọc cache rẻ (0,05–0,1×), còn mỗi lần giao trợ lý phải ghi cache ~22–26k ở 1,25× (T2.3 (ii)); output đọc bằng shell trung bình ≈ 1.400 ký tự/lệnh, đã nhỏ hơn bản tóm. Có thể sai: nếu tương lai có nhiều tool_result rất lớn (≥ 8.000 ký tự) thì cận thấp nhích lên, nhưng vẫn cỡ < 1% context. Đo sau (nếu thử): đếm tool_result ≥ 3.000 / ≥ 8.000 ký tự mỗi request và giây chờ Agent ở main.

**H5 — test vùng chạm ở bước trung gian.** Workflow đổi: luật build/plan/QC nói một nghĩa — bước trung gian chạy module test của vùng chạm (từ `Chạm:`), trọn bộ chỉ ở 2–3 cổng phase cố định; gỡ mâu thuẫn hiện có khiến trọn bộ chạy 7,4 lần/request (đo nội bộ §5.1). Số đáng tin vì cả hai đầu đều đo thật: trọn bộ 353,9 s và vùng chạm 0732 24,4 s chạy trên bản sao (T2.2 (a), (c)), số lần chạy lấy từ 59 lần thật; vùng chạm 24,4 s là hợp của mọi task nên là cận trên. Có thể sai: plan khai `Chạm:` thiếu → bước trung gian xanh giả, lỗi lộ ở cổng và tốn một vòng sửa; lệnh test gọi từ PowerShell đỏ 27 test vì `true` (T2.2 (a′)) — cổng phải chạy trong Git Bash hoặc sửa các test đó trước, nếu không agent sẽ chạy lại vì đỏ giả. Request 0732 đã tự giảm còn 2 lần trọn bộ (đo nội bộ §3.2), nên phần còn lại để ăn có thể nhỏ hơn nếu thói quen mới đã giữ. Đo sau: số lần lệnh test ≥ 200 s mỗi request (mục tiêu 2–3) và giây "test rộng" theo phương pháp đo nội bộ §3; chất lượng = số lỗi cổng trọn bộ bắt được mà vùng chạm bỏ sót.

**H6 — trọn bộ song song.** Workflow đổi: trước tiên các test git/worktree mỗi test có repo tạm riêng; sau đó lệnh trọn bộ chia module theo thời gian đo thành 4–8 nhóm chạy cùng lúc. Số đáng tin ở phần tốc độ (T2.2 (d1), (d2) đo thật), nhưng con số tiết kiệm/request là suy ra (2–3 lần × 173,1 – 242,0 s) và **chưa dùng được** vì cả ba lần chạy đều có nhóm đỏ. Có thể sai: sau khi cô lập, tranh chấp đĩa vẫn giữ thời gian ≥ 150 s như lần 4 nhóm; test chập chờn làm hỏng lòng tin vào cổng — với soul "chất lượng trước", cổng đỏ giả là cái giá không nhận được. Đo sau: chạy song song ≥ 3 lần liên tiếp, yêu cầu 0 nhóm đỏ, ghi giây treo tường mỗi lần.

**H7 — nén file luật.** Workflow đổi: không đổi hành vi; chỉ rút gọn chữ trong `skills/` (marker `i18n-allow` bỏ phần lý do, ví dụ RIGHT/WRONG ra file em, câu gần trùng giữ một bản). Số đáng tin vì đo bằng tokenizer thật trên bản sao, `doc_index.py --kiem` và `i18n_check.py` vẫn xanh (T2.1), và đã trừ phần vẫn bị đọc lại. Kết luận phải nói thẳng: ≈ 0,2% context một request, nhỏ hơn H1/H2 hơn hai bậc; chú thích HTML 100% là marker công cụ nên không phải mỏ. Có thể sai: agent không mở file ví dụ đúng lúc phân vân → chất lượng code giảm nhẹ mà không ai thấy. Đo sau: `skill_tokens.py --theo-phase` và số token tập bắt buộc đọc full/quick theo cách đếm T2.1.

**H8 — SessionStart resume gọn.** Workflow đổi: hook SessionStart chỉ bơm toàn văn luật gặt lúc startup (và sau compact); lúc resume chỉ bơm thẻ trạng thái và bước kế. Số đáng tin vì đo bằng tokenizer thật trên mẫu hook (~1,9k token luật gặt trong ~2,1k mỗi lần) và đếm đúng 22 lần resume ở exc1 (đo nội bộ §2) — nhưng chỉ ở phiên người dùng có UI resume ở hầu hết prompt; ở tdqwf không đo. Có thể sai: phiên resume rất dài mà bản toàn văn đã bị compact mất → agent quên luật gặt. Đo sau: cộng attachment `hook_success` SessionStart mỗi phiên dự án người dùng (cách đo nội bộ §1.6).

**H9 — tránh `edited_text_file`.** Workflow đổi: file plan/QC mà main đang giữ trong context không bị ghi song song từng chút (vd. sổ sách team gom một lần ở mốc merge). Số là cận trên (toàn bộ 381 lần chèn, đo nội bộ §1.5); phần thật sự tránh được chưa tách. Có thể sai: một phần lần chèn là do chính main sửa ngoài lượt hợp lệ, không bỏ được. Đo sau: đếm attachment `edited_text_file` theo filename mỗi request.

**H10 — gộp duyệt spec + plan (giảm cổng).** Workflow đổi: agent viết spec rồi plan liền một mạch và trình một lần; user duyệt một lần trước implement. Cái giá về kiểm soát là thật: user mất điểm dừng để chỉnh "làm gì" trước khi agent tốn công "làm thế nào", và một khối duyệt lớn hơn dễ bị duyệt lướt — trong khi implement chiếm 60,5% máy (đo nội bộ §3.3), nên sai hướng lọt qua cổng là đắt nhất. Về thời gian máy: **không bớt** — việc viết spec và plan vẫn phải làm; khi spec bị bác, phần plan đã viết là máy bỏ đi, tức có thể **tăng** máy. Thứ nó bớt là thời gian chờ (user đã loại khỏi mục tiêu) và, gián tiếp, những lần ghi cache lạnh khi user vắng > 1 h ở cổng đó (21/24 lần ghi lạnh là sau user vắng > 1 h, TB ≈ 0,53M token mỗi lần, T2.3 (iii)); nếu H1 đã làm thì lợi này co còn cỡ R. Có thể sai: số cổng spec rơi vào khe > 1 h chưa đo nên lợi có thể ≈ 0. Đo trước khi quyết: với mỗi lượt ghi lạnh ≥ 50k, xác định phase và lệnh AskUserQuestion/approve ngay trước nó (mở rộng phân loại T2.3 (iii)); sau khi đổi: số lần spec/plan bị bác hoặc viết lại.

**H11 — QC sạch thì tự đi tới report (giảm cổng).** Workflow đổi: khi QC không còn phát hiện nào cần sửa, agent viết report luôn thay vì dừng hỏi; cổng duyệt merge/đóng request vẫn giữ. Cái giá về kiểm soát: user không còn xem QC trước report; QC do agent chấm có thể "sạch" sai, khi đó lỗi tới tận cổng merge — chốt chặn cuối là duy nhất. Về thời gian máy: ≈ 0 (qc 3.779 s và report 5.547 s máy trên 11 cửa sổ vẫn phải chạy); phần lớn thời gian ở qc/report là chờ (171.316 s và 83.566 s, đo nội bộ §3.3), ngoài mục tiêu, và một phần trong đó là chờ qua đêm chứ không phải chờ cổng. Lợi cache gián tiếp như H10, số lần chưa đo. Đo sau: cùng phân loại lượt ghi lạnh theo phase như H10, cộng số lỗi bị phát hiện sau report (ở cổng merge hoặc request sau) so với trước khi đổi.

## Thứ tự đề xuất

Xếp theo giá trị / rủi ro / công sức, với soul chất lượng > runtime > context cost. Số ở mỗi dòng lấy từ "Bảng đề xuất".

**Làm trước**
1. H5 — test vùng chạm ở bước trung gian, trọn bộ ở 2–3 cổng: mỏ thời gian máy lớn nhất đo được (≈ 1.240 – 1.780 s/request), công sức nhỏ – vừa, chất lượng giữ nhờ cổng trọn bộ bắt buộc (H5).
2. H2 — phiên mới ở đầu mỗi request: 63M – 76M token/request (42–50%), công sức nhỏ, gần như không mất gì vì spec/plan/report đã là bàn giao (H2).
3. H3 — đổi model ngay sau mốc reset/compact: chỉ một câu luật, giá trị thấp (≈ 0,92M token input tương đương một lần) nên gộp vào request khác, không mở riêng (H3).

**Làm sau khi đo lại**
4. H1 — compact ở mọi mốc phase: thêm ≈ 20 điểm % so với H2 nhưng rủi ro chất lượng cao nhất (bàn giao thiếu, quên đọc lại luật — N9); chỉ làm sau khi đo lại context/request trên các request đã có H2 (H1).
5. H6 — trọn bộ song song: nhanh hơn 49–68% treo tường nhưng cả ba lần đều có nhóm đỏ; phải cô lập trạng thái git/worktree rồi chạy ≥ 3 lần liền 0 nhóm đỏ trước (H6).
6. H9 — tránh `edited_text_file`: 204k token/phiên chỉ là cận trên; tách phần ròng tránh được trước khi đổi sổ sách team (H9).
7. H8 — SessionStart resume gọn: ≈ 42k token/phiên exc1, nhỏ; đo thêm trên phiên dự án người dùng khác trước khi đụng hook (H8).

**Để user quyết (giảm cổng duyệt)** — đây là lựa chọn, không phải khuyến nghị:
- H10 — gộp duyệt spec + plan: ≈ 0 s máy (có thể tăng máy khi spec bị bác); đổi bằng mất điểm dừng giữa "làm gì" và "làm thế nào". Lợi gián tiếp ≈ 1,0M token input tương đương mỗi lần chờ > 1 h được bỏ, số lần chưa đo (H10).
- H11 — QC sạch thì tự viết report: ≈ 0 s máy; đổi bằng việc user không xem QC trước report, cổng merge là chốt chặn duy nhất (H11).
- Nếu muốn có số trước khi quyết: phân loại các lượt ghi lạnh ≥ 50k theo phase và cổng ngay trước nó (mở rộng T2.3 (iii)).

**Không nên làm**
- H4 — trợ lý đọc nặng giao lẻ: chi phí ròng −0,2M … +0,03M token/request và thêm 164 – 1.209 s chờ để bớt 18 – 93 s model (H4).
- H7 như một request riêng: ≈ 0,2% context một request, nhỏ hơn H1/H2 hơn hai bậc; riêng 1b (rút gọn marker `i18n-allow`, −1.016 token) có thể đi kèm khi request khác đã sửa các file đó (H7).

### Request tiếp theo nên mở: `test-vung-cham-buoc-trung-gian`

Lý do chọn H5 thay vì H2: soul đặt runtime trên context cost, H5 là mỏ thời gian máy lớn nhất đo được, và cách đo trước/sau đã có sẵn; H2 nhỏ tới mức có thể đi kèm như một câu luật nếu user muốn.

Phạm vi:
- Gỡ mâu thuẫn luật chạy test giữa `tdq-build/SKILL.md` ("EXACTLY ONCE"), `plan-template.md` ("sau mỗi phase chạy toàn bộ") và vòng sửa ở `qc.md`: bước trung gian chạy module test của dòng `Chạm:`, trọn bộ chỉ ở 2–3 cổng phase cố định.
- Cổng trọn bộ chạy trong Git Bash (hoặc sửa các test gọi `true`) để không còn 27 test đỏ giả khi gọi từ PowerShell (T2.2 (a′)).
- Không đổi cổng duyệt của user.

Thước đo thành công:
- Số lần lệnh test ≥ 200 s mỗi request giảm từ 7,4 xuống 2–3, và giây "test rộng" mỗi request giảm theo (phương pháp đo nội bộ §3, cùng regex như mục "Số chạy lại").
- Chất lượng không giảm: đếm số lỗi mà cổng trọn bộ bắt được còn vùng chạm bỏ sót, và số vòng sửa QC mỗi request so với 8 request trước.
- Script đo của báo cáo này làm thước trước/sau: mã T2.3 in đủ ở trên; lệnh T2.2 (a), (c) chạy lại được; phép đo thời gian máy ở "Số chạy lại" có mô tả phương pháp đủ để viết lại.

## Giới hạn

- **Cửa sổ dữ liệu**: số nội bộ đến từ hai transcript — tdqwf (`b77dddd9-…`, phiên phát triển chính workflow, ít compact: 4 lần/13 ngày) và exc1 (excalidraw, có cài plugin TDQ) — cùng `docs/tdq/timing.jsonl` từ request 09-20 tới 10-03 (11 cửa sổ cho thời gian máy, 9 cửa sổ cho T2.3), mốc dữ liệu 2026-10-03 04:17 UTC. Chỉ một máy Windows 11; chưa đo trên macOS/Linux hay trên Codex.
- **Số không xác minh được** (N29, N30, N34–N38) bị loại khỏi căn cứ và không được dùng ở bất kỳ đề xuất nào; riêng H5 vì thế không dựa vào số "−50%" bên ngoài mà dựa vào phép đo T2.2.
- **Test song song** (H6) chưa dùng được: mỗi lần chạy đều có một nhóm đỏ; số tiết kiệm của H6 là suy ra, không phải đo.
- **Script T2.1 đã xoá** sau khi đo: số của T2.1 có phương pháp viết thành chữ (mục "Cách dựng lại script") nhưng không có mã nguồn đính kèm như T2.3; script chạy lại ba số lớn ở "Số chạy lại" cũng đã xoá. Ai chạy lại phải viết lại theo mô tả, số có thể lệch nhỏ.
- **Khoảng, không phải điểm**: H1, H2, H5, H7 cho khoảng theo giả định (R cao/thấp, N = 2–3, 30–80% số lượt); cận thấp của giây máy (cùng cỡ output) đáng tin hơn. Độ trễ theo cỡ context là trung vị theo bucket, không hồi quy.
- **Thời gian model không tách sạch khỏi thời gian tool** ở mọi request: thời gian model là khe event không kết thúc ở tool_result, mốc phase dựng lại xấp xỉ, và còn 3.933 s "không rõ" không gán được cho model hay tool.
- T2.3 là phản thực trên số đo cũ, giả định phần tăng sau mốc không đổi; exc1 không đo lại ở T2.3.
