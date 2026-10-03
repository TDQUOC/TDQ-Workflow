# REPORT — Nén context và rút thời gian máy của workflow (`2026-10-03-1101-nghien-cuu-nen-context`)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

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
