# Nghiên cứu: nén context và giảm thời gian máy của tdq-workflow mà không hạ chất lượng
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-10-03 · Phiên bản đang xét: tdq-workflow 0.56.0
Mốc đo hiện tại (tokenizer thật): luôn nạp 2.704 token/phiên; lane full đọc 23 file luật ≈ 50.898 (tệ nhất 68.407); lane quick ≈ 18.633 (tệ nhất 36.142).

## Phương pháp và giới hạn

- Công cụ: WebSearch + WebFetch. **Tavily MCP không có trong phiên này**, nên không dùng tavily; mọi trích dẫn lấy từ WebSearch/WebFetch.
- WebFetch tóm tắt trang bằng model nhỏ, nên con số được ghi kèm nguồn; con số quan trọng đã lấy từ trang gốc (docs Anthropic, arXiv) khi có thể.
- Đánh dấu: **[cũ]** = nguồn trước 2025; **[chưa kiểm]** = blog/bên thứ ba, không phải nguồn gốc hoặc chưa đối chiếu được.
- Mỗi phát hiện: truy vấn → nguồn → phát hiện → hệ quả cho tdq. Cột "Codex?" ghi phát hiện có áp dụng cho Codex không.

---

## Góc 1 — Hướng dẫn chính thức của Anthropic / Claude Code

### 1.1 Prompt caching trong Claude Code: thứ gì phá cache, thứ gì không
- Truy vấn: fetch `code.claude.com/docs/en/prompt-caching`.
- Nguồn: https://code.claude.com/docs/en/prompt-caching (docs hiện hành, truy cập 2026-10-03).
- Phát hiện:
  - Cache khớp theo **tiền tố chính xác**; đổi bất kỳ chỗ nào trong tiền tố → tính lại mọi thứ phía sau. Không có cache theo từng file.
  - Thứ tự lớp: system prompt + tool definitions → project context (CLAUDE.md, memory) → hội thoại.
  - **Giữ cache**: skill/command được gọi (chèn như user message ở cuối), hook/skill/agent của plugin ("Claude Code never invalidates the cache for a plugin's skills, commands, agents, hooks…"), sửa CLAUDE.md giữa phiên (nhưng không có hiệu lực tới khi /clear, /compact, restart), đổi permission mode, /rewind, spawn subagent.
  - **Phá cache**: đổi model (kể cả skill có frontmatter `model` khác model phiên → lượt đó là model switch), đổi effort (trừ Opus 5.5/Sonnet 5.5/Fable 5.1 qua API key/subscription), bật fast mode, thêm/bớt MCP khi không dùng tool search, compaction (lớp hội thoại), nâng cấp Claude Code.
  - TTL: subscription trong hạn mức → hội thoại chính 1h; subagent/workflow/compaction → 5m. API key → 5m mặc định. Chỉnh bằng `promptCacheTtl`, `subagentPromptCacheTtl`, frontmatter `experimental.cacheTtl`.
  - Fork **dùng chung cache của cha**; subagent thường **không** đọc cache cha (tiền tố khác), tự làm nóng cache riêng.
  - `/usage` có dòng `Prompt cache (main)`: % input từ cache, số miss, nguyên nhân miss (v2.1.251+/2.1.260+).
- Hệ quả cho tdq:
  - 23 file luật đọc bằng Read nằm ở **lớp hội thoại** → mỗi lượt sau được đọc lại ở giá cache (0,1× giá input; Opus 5.5 là 0,05×). Nghĩa là chi phí $ của 50k token luật không lớn nếu cache ấm; cái đắt thật là (a) **context rot/attention** (xem 2.2–2.4) và (b) **lần ghi cache đầu + mỗi lần cache lạnh**.
  - Tránh mọi skill tdq khai `model:` khác model phiên (mỗi lần gọi = 1 lượt mất cache toàn bộ). Nếu muốn model rẻ cho bước cơ học → dùng subagent hoặc `context: fork` (đổi model của fork, không đổi phiên).
  - Hook output là append → không phá cache, nhưng **mỗi chữ hook in ra cộng dồn vĩnh viễn** vào hội thoại (cho tới compaction). Hook UserPromptSubmit in nhắc lại mỗi prompt = chi phí tuyến tính theo số prompt.
  - Implement song song: **fork + worktree** thừa hưởng toàn bộ luật đã đọc và cache của cha → không phải đọc lại 23 file; subagent thường phải nạp lại luật cần thiết và trả giá ghi cache riêng (TTL 5m).
  - Dùng `/usage` → `Prompt cache (main)` làm thước đo chính thức khi QC một thay đổi nén context.
- Codex? Một phần: Codex cũng cache theo tiền tố ở phía OpenAI nhưng cơ chế/TTL khác; các mục cụ thể (fork, promptCacheTtl, /usage) là riêng Claude Code.

### 1.2 Kinh tế cache: ghi 1,25× / 2×, đọc 0,1× (Opus 5.5: 0,05×), tối thiểu 512 token
- Truy vấn: "Claude prompt caching TTL 5 minutes 1 hour cache invalidation"; fetch docs API.
- Nguồn: https://platform.claude.com/docs/en/build-with-claude/prompt-caching
- Phát hiện: ghi 5m = 1,25× giá input; ghi 1h = 2×; đọc = 0,1× (Opus 5.5: 0,05×; Fable/Mythos 5.1: 0,025×). Ngưỡng tối thiểu để cache: 512 token cho Opus 5.5/Sonnet 5.5/Fable 5. Đổi tool definitions → mất toàn bộ cache; đổi system → mất system + messages.
- Hệ quả: với cache ấm, 50k token luật ở mỗi lượt Opus 5.5 ≈ 50k × $0,20/MTok = $0,01/lượt — rẻ. Lợi ích của việc cắt token luật vì thế **chủ yếu là chất lượng (attention) và độ trễ lượt đầu**, không phải tiền. Điều này khớp Soul: chất lượng > runtime > context cost. Ưu tiên cắt luật **không liên quan tới bước hiện tại** hơn là nén câu chữ.
- Codex? Nguyên tắc "tiền tố ổn định trước, động sau" áp dụng; con số giá riêng Anthropic.

### 1.3 Bài học "Prompt caching is everything" (2026-04-30)
- Nguồn: https://claude.dev/blog/lessons-from-building-claude-code-prompt-caching-is-everything/ (redirect từ claude.com/blog).
- Phát hiện: Plan mode là **tool** chứ không đổi system prompt; tool MCP gửi stub `defer_loading` (~1/10 chi phí nạp đủ); thông tin lỗi thời được **append `<system-reminder>`** thay vì sửa system prompt; compaction fork tái dùng tiền tố y hệt; nhóm Claude Code "alert on prompt cache hit rate and declare SEVs if too low".
- Hệ quả: thiết kế hook tdq kiểu "nhắc lại" bằng system-reminder là đúng hướng cache-safe. Nhưng nên **in ngắn và chỉ khi trạng thái đổi** (ví dụ chỉ in khi phase đổi, không in mỗi prompt).
- Codex? Nguyên tắc chung áp dụng.

### 1.4 Hook output: trần 10.000 ký tự, vượt thì bị cắt thành file + preview 2.000 ký tự
- Nguồn: https://code.claude.com/docs/en/hooks
- Phát hiện: stdout của SessionStart/UserPromptSubmit/UserPromptExpansion/PostModelSwitch vào context; `additionalContext` được bọc system-reminder, chèn tại điểm hook chạy. Mỗi chuỗi trần **10.000 ký tự**; vượt → lưu file, chỉ để path + preview 2.000 ký tự, **Claude không được yêu cầu đọc file** đó. Docs khuyên: luật tĩnh để ở CLAUDE.md, hook chỉ cho trạng thái môi trường / luật có điều kiện.
- Hệ quả: kiểm mọi hook tdq không bao giờ vượt 10k ký tự (nếu vượt, phần đuôi coi như mất im lặng — rủi ro chất lượng). Hook nên mang **trạng thái** (phase, lane, file luật cần đọc tiếp), không mang **nội dung luật**.
- Codex? Codex có SessionStart/UserPromptSubmit/SubagentStart với additionalContext (https://developers.openai.com/codex/hooks); **[chưa kiểm]** issue openai/codex#45999 báo SessionStart với additionalContext lỗi trên codex-cli 0.154.0 — dùng stdout thuần cho Codex an toàn hơn.

### 1.5 Skills: danh sách mô tả chiếm ~1% context; thân SKILL.md chỉ nạp khi gọi; sau compaction chỉ giữ 5.000 token đầu mỗi skill
- Nguồn: https://code.claude.com/docs/en/skills
- Phát hiện: listing skill có ngân sách ký tự = **1% context window**; description + when_to_use cắt ở **1.536 ký tự**. Sau compaction, Claude Code gắn lại lần gọi gần nhất của mỗi skill, **giữ 5.000 token đầu**, tổng **25.000 token**, ưu tiên skill gọi gần nhất. Có `context: fork` (chạy skill trong subagent, mặc định background), `disable-model-invocation`, `allowed-tools`, và `` !`cmd` `` chạy shell trước khi gửi skill (output thay chỗ placeholder; lệnh lỗi → hủy cả skill).
- Hệ quả:
  - **Quan trọng**: file luật tdq đọc bằng Read **không** được gắn lại sau compaction như skill. Hook nhắc đọc lại hiện có là cần thiết; nhưng có thể thay bằng: đặt luật lõi của bước trong **thân SKILL.md** (≤5.000 token đầu) để được tự gắn lại.
  - Dùng `` !`python scripts/...` `` trong SKILL.md để **script xác định** tính sẵn trạng thái (phase, lane, danh sách file luật cần đọc, mục nào của file) thay vì để model đọc STATE.md rồi suy luận → bớt 1–3 round-trip mỗi lần vào skill.
  - Mô tả skill tdq: đặt use case chính đầu tiên; giữ tổng listing nhỏ để không bị cắt mô tả.
- Codex? Codex cũng progressive disclosure: listing skill ≤ **2% context hoặc 8.000 ký tự** (https://learn.chatgpt.com/docs/build-skills). `!cmd`, `context: fork`, cơ chế gắn lại 5.000 token là riêng Claude Code.

### 1.6 Skill authoring best practices: SKILL.md < 500 dòng, tham chiếu một cấp, file >100 dòng có mục lục, script được chạy chứ không nạp
- Nguồn: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- Phát hiện: "Claude is already very smart — chỉ thêm thứ Claude chưa biết"; ví dụ bản gọn ~50 token vs bản dài ~150 token. SKILL.md < 500 dòng; tham chiếu **chỉ một cấp** từ SKILL.md (tham chiếu lồng → Claude có thể chỉ `head -100` và đọc thiếu); file tham chiếu > 100 dòng cần **mục lục ở đầu**; tổ chức theo domain để chỉ đọc file liên quan; "Prefer scripts for deterministic operations" — script chạy, chỉ output tốn token; mẫu plan-validate-execute với script kiểm; **eval trước, viết tối thiểu sau** (≥3 kịch bản, so baseline không skill).
- Hệ quả: tdq đã có line-index + offset/limit (khớp khuyến nghị mục lục). Cần kiểm: (a) có chuỗi tham chiếu 2 cấp (file luật → file luật khác) không — nếu có, đó là chỗ đọc thiếu tiềm ẩn; (b) đoạn nào giải thích thứ model đã biết (định nghĩa TDD, git…) → cắt; (c) bước kiểm nào đang để LLM làm mà script làm được.
- Codex? Áp dụng (chuẩn SKILL.md dùng chung).

### 1.7 Context engineering (2025-09-29): tập token nhỏ nhất có tín hiệu cao, just-in-time, tool-result clearing, subagent trả 1.000–2.000 token
- Nguồn: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Phát hiện: "smallest possible set of high-signal tokens"; context rot — mỗi token thêm làm cạn "attention budget"; giữ định danh nhẹ (path, query) và nạp lúc cần; compaction ưu tiên recall rồi tinh chỉnh precision; **tool result clearing** là dạng compaction an toàn nhất; ghi chú có cấu trúc ra file; subagent trả bản tóm tắt **1.000–2.000 token**; system prompt ở "đúng độ cao" (không quá cứng, không quá mơ hồ).
- Hệ quả: chuyển từ "lane full đọc 23 file" sang "mỗi bước đọc file của bước đó" (just-in-time theo phase). Định chuẩn output subagent tdq ≤ ~2.000 token.
- Codex? Áp dụng (nguyên tắc).

### 1.8 Quản lý chi phí Claude Code: CLAUDE.md < 200 dòng, hook tiền xử lý, subagent cho thao tác dài dòng, model nhỏ cho subagent
- Nguồn: https://code.claude.com/docs/en/costs
- Phát hiện: CLAUDE.md < 200 dòng, chuyển luật chuyên biệt sang skill; hook PreToolUse lọc output test chỉ còn FAIL/ERROR ("từ hàng chục nghìn token xuống hàng trăm"); giao chạy test/log cho subagent; `model: haiku` cho subagent đơn giản; `CLAUDE_CODE_SUBAGENT_MODEL`; agent teams ~**7×** token so với phiên thường; `/compact` có hướng dẫn giữ gì; /clear giữa các task không liên quan.
- Hệ quả: tdq có thể thêm **hook/script lọc output test** (chỉ in tóm tắt + lỗi) — vừa giảm context vừa giảm thời gian đọc. Mục "Compact instructions" trong luật tdq nên nói rõ giữ: phase, lane, spec path, task đang làm.
- Codex? Lọc output qua script: áp dụng. Hook PreToolUse sửa lệnh (`updatedInput`): kiểm lại trên Codex.

### 1.9 Subagent: nạp gì lúc khởi động
- Nguồn: https://code.claude.com/docs/en/sub-agents
- Phát hiện: subagent thường nạp system prompt riêng + task + **toàn bộ CLAUDE.md/AGENTS.md** + git status + skill trong field `skills` (**full content**); không có lịch sử hội thoại. Explore/Plan bỏ CLAUDE.md và git status; `omitClaudeMd: true` bỏ CLAUDE.md. Fork kế thừa hội thoại + cache. Mặc định tối đa 20 subagent đồng thời, sâu 3 tầng. Tổng description subagent ≤ 15.000 token. Explore hiện chạy **Opus** trên subscription (không còn Haiku) — có thể override bằng agent `Explore` riêng `model: haiku`.
- Hệ quả: subagent implement của tdq nên dùng field `skills:` để **preload đúng 1 skill luật implement** thay vì để subagent tự đọc nhiều file; hoặc dùng fork khi cần toàn bộ ngữ cảnh spec/plan. Subagent chỉ đọc/tra cứu: cân nhắc `omitClaudeMd: true`.
- Codex? Codex có subagent GA (≤6 đồng thời theo blog **[chưa kiểm]** https://codex.danielvaughan.com/2026/03/27/codex-cli-in-2026-whats-new/); field `skills`/fork/worktree là riêng Claude Code.

### 1.10 Context editing + memory tool: −84% token, +39% hiệu năng (API)
- Nguồn: https://claude.com/blog/context-management (Anthropic, 2025-09; số liệu nội bộ Anthropic).
- Phát hiện: eval web-search 100 lượt: context editing giảm **84%** token và cho phép hoàn thành workflow lẽ ra hết context; memory + context editing **+39%** so với baseline; context editing đơn lẻ **+29%**.
- Hệ quả: bằng chứng rằng **bỏ kết quả tool cũ không hạ mà còn tăng chất lượng**. Trong Claude Code, việc này tự động (tool-result clearing là "expected rebuild"). Với tdq: ghi trạng thái ra file (STATE.md đã có) là đúng; để luật đọc rồi bị dọn là chấp nhận được nếu bước kế đọc lại đúng phần cần.
- Codex? Nguyên tắc áp dụng; API feature là của Anthropic.

---

## Góc 2 — Nén prompt/context trong thực tế và đánh đổi chất lượng

### 2.1 Context files (AGENTS.md) — hai kết quả trái chiều
- Truy vấn: "AGENTS.md context files evaluation coding agents performance cost study 2026 arxiv".
- Nguồn A: https://arxiv.org/abs/2602.11988 (ETH Zurich, 2026-02-12).
  - Phát hiện: context file **không tăng** tỉ lệ thành công nói chung, **tăng chi phí suy luận >20%**; file do dev viết tốt hơn file LLM sinh ~7 điểm; **chỉ dẫn được tuân thủ tốt** → agent khám phá/test/suy luận nhiều hơn; **tổng quan repo không giúp ích**.
- Nguồn B: https://arxiv.org/abs/2601.20404 (2026-01-28, sửa 2026-03-30): 10 repo, 124 PR — có AGENTS.md → runtime trung vị **−28,64%**, output token **−16,58%**, mức hoàn thành tương đương.
- Hệ quả: luật **chỉ dẫn hành động cụ thể** (lệnh test, đường dẫn, quy ước khác chuẩn) đáng giá; **văn bản giải thích/tổng quan** tốn chi phí mà không thêm chất lượng. Mỗi luật tdq "bắt buộc làm thêm X" sẽ được làm → đội runtime; cần soát luật nào kích hoạt công việc không đổi chất lượng đầu ra.
- Codex? Áp dụng trực tiếp (AGENTS.md là định dạng của Codex).

### 2.2 Cấu trúc file luật không quyết định độ tuân thủ; độ dài phiên mới quyết định
- Nguồn: https://arxiv.org/abs/2605.10039 (2026-05-11), 1.650 phiên Claude Code CLI.
- Phát hiện: kích thước file, vị trí chỉ dẫn, kiến trúc file (một hay nhiều file), mâu thuẫn ở file kề — **không biến nào tạo khác biệt phát hiện được** sau hiệu chỉnh đa kiểm định. Mỗi hàm sinh thêm trong phiên → odds tuân thủ giảm ~**5,6%** (OR 0,944).
- Hệ quả: (a) nén câu chữ/đổi định dạng luật **khó** mang lại chất lượng đo được — đừng kỳ vọng; (b) tuân thủ suy giảm theo **độ dài phiên làm việc** → luật cần được **nhắc đúng lúc** (just-in-time ở bước dùng) hơn là nạp hết từ đầu; củng cố giá trị của hook nhắc lại + implement theo task nhỏ trong subagent sạch.
- Codex? Đo trên Claude Code; nguyên lý có lẽ chung **[chưa kiểm cho Codex]**.

### 2.3 Mật độ chỉ dẫn: tối đa 68% ở 500 chỉ dẫn, thiên vị chỉ dẫn đầu
- Nguồn: https://arxiv.org/abs/2507.11538 (IFScale, 2025-07).
- Phát hiện: 20 model; model tốt nhất chỉ **68%** ở 500 chỉ dẫn đồng thời; 3 kiểu suy giảm (model reasoning: gần hoàn hảo tới ngưỡng rồi rơi); **primacy bias** (ưu tiên chỉ dẫn xuất hiện sớm).
- Hệ quả: tổng số "luật bắt buộc" đang hiệu lực cùng lúc là biến chất lượng thật. Lane full nạp 23 file → có thể hàng trăm điều khoản cùng lúc. Đếm số điều khoản MUST đang hiệu lực mỗi phase và đặt luật quan trọng nhất **lên đầu** file/đầu SKILL.md.
- Codex? Áp dụng (đo đa model).

### 2.4 Context rot: mọi model đều suy giảm theo độ dài input; prompt tập trung ~300 token >> đầy đủ ~113k
- Nguồn: https://www.trychroma.com/research/context-rot (Chroma, 2025-07-14).
- Phát hiện: 18 model đều giảm khi input dài, kể cả tác vụ đơn giản; **một distractor** đã giảm hiệu năng, bốn càng tệ; LongMemEval: bản tập trung (~300 token) tốt hơn rõ rệt bản đầy đủ (~113k), kể cả khi bật thinking. Claude ít ảo giác nhất trước distractor nhưng hay từ chối/abstain.
- Hệ quả: luật **gần giống nhưng không áp dụng** cho bước hiện tại (ví dụ luật implement khi đang ở spec) chính là "distractor". Lý do chất lượng mạnh nhất để chia luật theo phase.
- Codex? Áp dụng.

### 2.5 Cắt tỉa lịch sử tool + tóm tắt: tăng hoàn thành 71% → 91,6%, giảm token 1,48M → 553k, thời gian 14,56h → 5,79h
- Nguồn: https://arxiv.org/abs/2606.10209 (2026-06-08), GPT-5 và Claude Sonnet 4.5, 50 task.
- Phát hiện: full history 71,0% / 1,48M token / 14,56h; giữ 5 tool call gần nhất 79,0% / 535K / 5,39h; cắt + tóm tắt **91,6%** / 553K / 5,79h.
- Hệ quả: bằng chứng định lượng rằng **ít context hơn → vừa nhanh hơn vừa tốt hơn** trong tác vụ dài. Với tdq: handoff giữa phase bằng tóm tắt có cấu trúc (STATE.md/brief) và bắt đầu phase mới với context sạch có thể tốt hơn kéo dài một phiên.
- Codex? Áp dụng (nguyên lý).

### 2.6 Nén kiểu LLMLingua: 2–5× nén, độ trễ −2,9×, nhưng nhắm vào prompt dữ liệu, không phải luật
- Nguồn: https://arxiv.org/abs/2403.12968 (LLMLingua-2, 2024) **[cũ]**; https://arxiv.org/abs/2606.24083 (CAVEWOMAN, 2026, chưa đọc chi tiết **[chưa kiểm]**).
- Phát hiện: nén token-classification đạt 2–5×, end-to-end nhanh tới 2,9×; đánh giá trên QA/tóm tắt/toán — không phải chỉ dẫn hành vi.
- Hệ quả: **không khuyến nghị** nén tự động file luật tdq: luật là chỉ dẫn chính xác (đường dẫn, lệnh, điều kiện) — xóa token kiểu LLMLingua có rủi ro làm mất phủ định/điều kiện; kết hợp 2.2 (định dạng không đổi tuân thủ) → lợi ích chất lượng ≈ 0, rủi ro > 0. Nén **thủ công** (bỏ giải thích model đã biết, khử trùng lặp) vẫn đáng.
- Codex? Như trên.

### 2.7 Kiro steering: chế độ nạp always / fileMatch / manual / auto; khuyên 3–5 file mỗi task
- Nguồn: https://kiro.dev/docs/steering/ ; tóm tắt bên thứ ba https://kirotutorial.com/concepts/steering/ **[chưa kiểm số 3–5]**.
- Phát hiện: luật có frontmatter khai khi nào nạp (luôn, theo glob file đang sửa, khi gọi tên, hay tự chọn theo mô tả).
- Hệ quả: tương đương với Claude Code `paths:` rules (nạp khi đọc file khớp — xem 1.1) và skill. tdq có thể gắn **luật theo loại file** (ví dụ luật viết test chỉ nạp khi chạm `tests/**`) qua rules có `paths:` thay vì đọc thủ công.
- Codex? Codex không có fileMatch; AGENTS.md lồng theo thư mục là thay thế gần nhất.

---

## Góc 3 — Tốc độ workflow agent (thời gian máy)

### 3.1 Song song hóa: subagent 3–5 + tool song song → giảm tới 90% thời gian (research), nhưng coding ít việc song song thật
- Nguồn: https://www.anthropic.com/engineering/multi-agent-research-system (Anthropic, 2025-06).
- Phát hiện: đa agent +90,2% so với Opus 4 đơn; token ≈ 15× chat (agent đơn ≈ 4×); token giải thích 80% phương sai; 3–5 subagent song song, mỗi subagent 3+ tool song song → thời gian research **−90%**; "most coding tasks involve fewer truly parallelizable tasks than research".
- Hệ quả: song song hóa trong tdq nên nhắm (a) **tra cứu/khám phá/review độc lập** (song song tốt), (b) implement chỉ khi task thật sự độc lập file. Đổi thời gian lấy token: chấp nhận được theo Soul (runtime > context cost).
- Codex? Áp dụng (Codex subagent ≤6 đồng thời **[chưa kiểm]**).

### 3.2 Gọi tool song song: một câu trong prompt đẩy tỉ lệ gần ~100%
- Nguồn: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices ; https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use
- Phát hiện: model mới đã song song mặc định; thêm đoạn "whenever you perform multiple independent operations, invoke all relevant tools simultaneously…" đưa tỉ lệ lên ~100%.
- Hệ quả: thêm **một dòng** vào luật lõi tdq: "đọc nhiều file luật/nguồn độc lập → gọi song song trong một lượt". 23 file đọc tuần tự = 23 round-trip; song song = 1–3. Rẻ nhất, lợi lớn về thời gian.
- Codex? Codex cũng hỗ trợ tool song song; câu nhắc áp dụng **[chưa kiểm mức tăng]**.

### 3.3 Script xác định thay bước LLM: tiết kiệm token và thời gian; Agentless $0,34 vs $3,34/issue
- Nguồn: Skill best practices (1.6) — "More reliable than generated code; Save tokens; Save time"; Agentless https://arxiv.org/abs/2407.01489 **[cũ, 2024]**.
- Phát hiện: Agentless (pipeline cố định localize → repair → validate) $0,34/issue vs ~$3,34 agent; hiệu năng cao nhất nhóm open-source SWE-bench Lite lúc đó (27,33%).
- Hệ quả: các bước tdq có đầu ra xác định (cập nhật STATE.md, timing.jsonl, kiểm định dạng spec/plan, bump version, tạo CHANGELOG, đếm token, chọn file luật theo phase/lane) → giao **script Python** gọi một lệnh; LLM chỉ đọc kết quả ngắn. Mỗi bước như vậy bớt vài round-trip.
- Codex? Áp dụng hoàn toàn (script độc lập agent).

### 3.4 Programmatic tool calling / tool search: −37% / −85% token
- Nguồn: https://www.anthropic.com/engineering/advanced-tool-use (Anthropic, 2025-11).
- Phát hiện: tool search −85% token định nghĩa tool, độ chính xác Opus 4.5 79,5% → 88,1%; programmatic tool calling −37% token trên research phức tạp, giữ kết quả trung gian ngoài context, bớt round-trip.
- Hệ quả: trong Claude Code tool search đã mặc định. Ý tưởng chuyển được: **gộp chuỗi thao tác thành một lệnh script** (ví dụ "chạy test + lint + đo token + cập nhật state" trong 1 lệnh trả JSON ngắn) thay vì 4 lượt tool.
- Codex? Ý tưởng gộp lệnh áp dụng; API feature là của Anthropic.

### 3.5 Định tuyến model: subagent cơ học dùng model nhỏ
- Nguồn: https://code.claude.com/docs/en/costs và /sub-agents (chính thức); số "5–10× rẻ hơn", "Explore 1,5–3K vs 35–45K token" từ https://www.mindstudio.ai/blog/smart-orchestrator-cheaper-sub-agent-models-claude-code **[chưa kiểm]**.
- Phát hiện: docs khuyên `model: haiku` cho subagent đơn giản; Haiku/Sonnet nhanh hơn Opus.
- Hệ quả: các subagent tdq làm việc cơ học (tra cứu file, chạy test và tóm tắt, kiểm định dạng) → `model: haiku` hoặc `sonnet`; giữ model mạnh cho spec/plan/review. **Rủi ro chất lượng**: best practices yêu cầu test skill trên mọi model định dùng — cần eval trước khi đổi.
- Codex? Codex cho chọn model theo profile/subagent; áp dụng tương tự **[chưa kiểm cú pháp]**.

### 3.6 Test chọn lọc theo thay đổi: −50% thời gian test
- Nguồn: https://testmon.org/ ; https://engineering.instawork.com/test-impact-analysis-the-secret-to-faster-pytest-runs-e44021306603 **[chưa kiểm, blog doanh nghiệp]**.
- Phát hiện: pytest-testmon chỉ chạy test phụ thuộc code đổi; báo cáo giảm ~50% / CI nhanh 2×; luôn chạy lại test fail lần trước.
- Hệ quả: vòng TDD trong implement dùng test chọn lọc (`--testmon` hoặc chạy file test của task) + **chạy full suite một lần ở QC cuối**. Giữ chất lượng nhờ cổng full suite; giảm thời gian vòng trong.
- Codex? Áp dụng (công cụ ngoài agent).

### 3.7 Lọc output test trước khi vào context
- Nguồn: https://code.claude.com/docs/en/costs (ví dụ hook PreToolUse lọc FAIL/ERROR, `head -100`).
- Hệ quả: giảm token và thời gian model đọc log; dùng `pytest -q --tb=short` hoặc script bọc trả tóm tắt. Rủi ro: mất ngữ cảnh lỗi → giữ đủ traceback của test fail.
- Codex? Áp dụng qua script; hook sửa lệnh cần kiểm trên Codex.

### 3.8 Plan mode và chặn sớm để tránh làm lại
- Nguồn: https://code.claude.com/docs/en/costs ("plan mode… preventing expensive re-work"); superpowers (4.1).
- Hệ quả liên quan đề xuất gộp cổng duyệt: cổng duyệt **trước implement** có giá trị kinh tế (tránh làm lại). Gộp spec + plan thành một cổng giảm một lượt chờ nhưng **không** giảm thời gian máy đáng kể; lợi ích chính là giảm thời gian chờ user — ngoài phạm vi "thời gian máy". Xem mục đề xuất.

---

## Góc 4 — Framework workflow mã nguồn mở tương đương

### 4.1 superpowers (obra)
- Nguồn: https://github.com/obra/superpowers ; https://raw.githubusercontent.com/obra/superpowers/main/skills/using-superpowers/SKILL.md
- Phát hiện: SessionStart hook chỉ tiêm **một** skill bootstrap `using-superpowers` (~420 từ ≈ ~600 token) dạy "kiểm skill trước khi làm, dù 1% khả năng áp dụng"; ~20 skill, mỗi skill nạp khi cần; luồng brainstorming → writing-plans → subagent-driven-development; mỗi task 2–5 phút giao subagent mới với **đường dẫn file chính xác, code, bước kiểm**, review sau mỗi task. Hỗ trợ Codex. Không công bố số token.
- Hệ quả: bề mặt luôn nạp của superpowers (~600 token) < tdq (2.704). Khác biệt lớn hơn: superpowers **không có lane bắt đọc hàng chục file**; luật nằm trong skill của từng bước. Mẫu "plan đủ chi tiết để subagent không cần đọc luật chung" là cách giảm context cho implement.
- Codex? Có.

### 4.2 GitHub spec-kit
- Nguồn: https://github.com/github/spec-kit
- Phát hiện: constitution (một lần) → specify → plan → tasks → implement; mỗi lệnh là một template/skill riêng, review sau mỗi bước; hỗ trợ nhiều agent qua integration key (Codex nằm trong danh sách theo README trước đây **[chưa kiểm phiên bản hiện tại]**).
- Hệ quả: mỗi lệnh chỉ nạp template của nó → tương đương "luật theo phase". Constitution là nguồn nguyên tắc duy nhất, các template tham chiếu tới nó (giống soul.md của tdq).
- Codex? Có (theo README).

### 4.3 BMAD Method: shard tài liệu thành story file tự đủ
- Nguồn: https://bmad-code-org-bmad-method-6.mintlify.app/advanced/shard-documents ; con số "tiết kiệm tới 90% token" từ https://www.augmentcode.com/guides/bmad-method-ai-development **[chưa kiểm]**.
- Phát hiện: PRD/architecture lớn bị shard; Scrum Master agent viết story file chứa **đủ** ngữ cảnh cho Dev agent → Dev không cần đọc tài liệu gốc.
- Hệ quả: cùng mẫu với 4.1: **dồn công vào bước plan** để mỗi task tự đủ → subagent implement không đọc lại 23 file luật.
- Codex? Có (framework đa agent).

### 4.4 Cline Memory Bank: phản ví dụ
- Nguồn: https://docs.cline.bot/prompting/cline-memory-bank
- Phát hiện: "MUST read ALL memory bank files at the start of EVERY task" (6 file); không có phân tích chi phí token.
- Hệ quả: đây chính là mẫu tdq lane full đang gần giống (đọc nhiều file bắt buộc). Các framework mới hơn (superpowers, Kiro, Claude skills) đều đi theo hướng ngược lại: nạp có điều kiện.
- Codex? Không liên quan trực tiếp.

### 4.5 aider conventions: một file nhỏ, read-only, cache
- Nguồn: https://aider.chat/docs/usage/conventions.html
- Phát hiện: nạp CONVENTIONS.md bằng `--read` để read-only và được prompt cache; ví dụ chỉ vài gạch đầu dòng.
- Hệ quả: luật luôn nạp nên **nhỏ, ổn định byte-for-byte** (để cache) — tdq 2.704 token luôn nạp: kiểm hook SessionStart không in dữ liệu thay đổi (ngày giờ, đếm) trước phần tĩnh.
- Codex? Nguyên tắc áp dụng.

### 4.6 Codex: AGENTS.md trần 32 KiB, skill listing ≤2% context / 8.000 ký tự
- Nguồn: https://developers.openai.com/codex/guides/agents-md ; https://learn.chatgpt.com/docs/build-skills ; issue cắt im lặng https://github.com/openai/codex/issues/7138
- Phát hiện: Codex nối AGENTS.md từ gốc xuống, dừng ở `project_doc_max_bytes` = **32 KiB**, cắt im lặng; skill progressive disclosure như Claude.
- Hệ quả: bản Codex của tdq phải giữ AGENTS.md dưới 32 KiB (vượt → mất luật im lặng, rủi ro chất lượng); luật phase nên đi qua skill.

---

## Tổng hợp: đề xuất cho tdq-workflow (xếp theo Soul: chất lượng > runtime > context)

| # | Đề xuất | Lợi (ước) | Rủi ro chất lượng | Codex? |
|---|---|---|---|---|
| A | **Nạp luật theo phase/bước** thay vì lane full đọc 23 file một lần (just-in-time). Hook/`!cmd` báo đúng file + mục cần cho bước hiện tại | Context hoạt động giảm mạnh (ước 50k → 10–20k mỗi bước); ít distractor (2.3, 2.4) | Thấp nếu bản đồ bước → luật đầy đủ; cần eval | Có (qua skill) |
| B | **Đọc file luật song song** một lượt (1 dòng trong luật lõi) | 23 round-trip → 1–3 | Không | Có |
| C | **Script xác định** cho bước cơ học + `` !`cmd` `` trong SKILL.md để tiêm trạng thái tính sẵn | Bớt round-trip, bớt token suy luận | Giảm (script ổn định hơn) | Script: có; `!cmd`: không |
| D | Luật lõi mỗi phase đặt **trong thân SKILL.md, 5.000 token đầu** để tự gắn lại sau compaction | Bớt phụ thuộc hook nhắc đọc lại | Tăng (không mất luật sau compact) | Một phần |
| E | Implement song song bằng **fork + worktree** (dùng chung cache, không đọc lại luật) hoặc subagent với `skills:` preload một skill implement; plan đủ chi tiết kiểu superpowers/BMAD | Bớt nạp lại luật mỗi subagent | Trung tính; cần plan tốt | Một phần |
| F | Subagent cơ học dùng `model: haiku/sonnet`; KHÔNG đặt `model:` trong skill chạy ở phiên chính | Nhanh hơn, rẻ hơn; tránh mất cache | Có — phải eval trên model nhỏ | Một phần |
| G | Test chọn lọc trong vòng TDD + full suite một lần ở QC; lọc output test | Ước −50% thời gian test vòng trong | Thấp nhờ cổng full suite | Có |
| H | Hook in **ngắn, chỉ khi trạng thái đổi**, không chứa nội dung luật; luôn < 10.000 ký tự; phần tĩnh SessionStart ổn định byte | Bớt token cộng dồn mỗi prompt | Không | Có (Codex: dùng stdout thuần) |
| I | Soát luật: bỏ giải thích model đã biết, bỏ "tổng quan repo", khử trùng lặp; KHÔNG dùng nén tự động LLMLingua | Vừa phải | Thấp (thủ công) | Có |
| J | Đo bằng `/usage` → `Prompt cache (main)` + eval ≥3 kịch bản trước/sau | Cho phép quyết định dựa số | — | Một phần |

### Về gộp cổng duyệt (spec + plan)
- Thời gian máy tiết kiệm: nhỏ (bớt một lượt dừng/tóm tắt). Lợi chính là bớt thời gian chờ người — ngoài phạm vi đo "thời gian máy".
- **Chi phí kiểm soát của user**: mất điểm dừng để sửa hướng **trước** khi plan được viết; nếu spec sai thì plan viết trên spec sai bị bỏ (lãng phí token/thời gian máy — ngược mục tiêu). Docs Claude Code coi plan mode là chống làm lại tốn kém.
- Phương án dung hòa: gộp chỉ ở lane quick, hoặc gộp khi spec ngắn và user bật cờ; giữ tách ở lane full.

## Danh sách nguồn
- https://code.claude.com/docs/en/prompt-caching
- https://code.claude.com/docs/en/costs
- https://code.claude.com/docs/en/hooks
- https://code.claude.com/docs/en/skills
- https://code.claude.com/docs/en/sub-agents
- https://platform.claude.com/docs/en/build-with-claude/prompt-caching
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use
- https://claude.dev/blog/lessons-from-building-claude-code-prompt-caching-is-everything/ (2026-04-30)
- https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents (2025-09-29)
- https://www.anthropic.com/engineering/multi-agent-research-system (2025-06)
- https://www.anthropic.com/engineering/advanced-tool-use (2025-11)
- https://claude.com/blog/context-management (2025-09)
- https://arxiv.org/abs/2602.11988 (2026-02) · https://arxiv.org/abs/2601.20404 (2026-01/03) · https://arxiv.org/abs/2605.10039 (2026-05) · https://arxiv.org/abs/2606.10209 (2026-06) · https://arxiv.org/abs/2507.11538 (2025-07)
- https://www.trychroma.com/research/context-rot (2025-07-14)
- https://arxiv.org/abs/2403.12968 [cũ] · https://arxiv.org/abs/2407.01489 [cũ]
- https://github.com/obra/superpowers · https://github.com/github/spec-kit · https://kiro.dev/docs/steering/ · https://docs.cline.bot/prompting/cline-memory-bank · https://aider.chat/docs/usage/conventions.html
- https://developers.openai.com/codex/guides/agents-md · https://learn.chatgpt.com/docs/build-skills · https://developers.openai.com/codex/hooks
- [chưa kiểm] mindstudio.ai, augmentcode.com, kirotutorial.com, codex.danielvaughan.com, engineering.instawork.com
