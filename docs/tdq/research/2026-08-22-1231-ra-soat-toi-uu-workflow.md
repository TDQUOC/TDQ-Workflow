# Research: rà soát tối ưu cách viết plugin tdq-workflow (SKILL.md + reference + agent files)

Mục tiêu: tìm căn cứ để rút gọn/viết lại cách trình bày các file skill/reference/agent trong
plugin `tdq-workflow`, **không đổi luật**, chỉ đổi cách viết, mà không làm giảm compliance của
model. 4 truy vấn tavily, mỗi truy vấn ghi nguồn (tiêu đề + URL + ngày nếu có) và phần "Suy ra".

---

## Query 1 — Anthropic Agent Skills SKILL.md authoring best practices progressive disclosure

Nguồn:
- "Skill authoring best practices" — platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
  (tài liệu chính thức Anthropic, không có ngày public rõ trên trang crawl được).
  Trích: "Keep SKILL.md body under 500 lines for optimal performance. If your content exceeds
  this, split it into separate files using progressive disclosure patterns." Giới hạn field:
  `name` tối đa 64 ký tự (chữ thường/số/gạch ngang, không XML tag, không từ khoá dành riêng);
  `description` tối đa 1024 ký tự, không rỗng, không XML tag.
- "Anthropic's Agent Skills" — medium.com/@nimritakoul01/anthropics-agent-skills-0ef767d72b0f
  (không rõ ngày). Mô tả 3 pattern viết SKILL.md: (1) high-level guide + link reference cho
  chi tiết nâng cao, (2) tổ chức theo domain — tách file riêng theo domain để tránh nạp context
  không liên quan, (3) conditional details — chỉ link tới file phụ khi thật sự cần.
- "Skill Authoring Patterns from Anthropic's Best Practices" — generativeprogrammer.com
  (Substack, 2026). Nhấn mạnh: SKILL.md 800 dòng nhồi hết chi tiết tốn context như nhau dù
  request có cần phần đó hay không — lý do chính để tách reference file.
- superpowers/writing-skills/anthropic-best-practices.md (GitHub, obra/superpowers, mirror của
  tài liệu Anthropic) — cùng nội dung 500-dòng + progressive disclosure, thêm phần "description
  tốt" (ví dụ cụ thể: "Generate descriptive commit messages by analyzing git diffs. Use when
  the user asks for help writing commit messages...") vs "description mơ hồ" (tránh "Helps with
  documents", "Processes data").

Suy ra cho repo này:
- 7 SKILL.md hiện tại nếu đang < 500 dòng thì đã trong ngưỡng khuyến nghị chính thức — không
  cần ép cắt xuống dưới ngưỡng đó bằng mọi giá, ưu tiên đúng cấu trúc hơn đúng số dòng.
  Nên đo lại độ dài từng SKILL.md so với mốc 500 dòng làm baseline khách quan.
- Field `description` (phần luôn nạp — 1.4k token always-loaded) nên viết cụ thể "làm gì +
  dùng khi nào" trong một câu, đúng mẫu Anthropic khuyến nghị, không mô tả mơ hồ — đây là chỗ
  rẻ nhất để cải thiện độ chính xác routing mà không đụng vào rule nào.
  vàng: dưới 1024 ký tự (giới hạn cứng), nhưng nên ngắn hơn nhiều — theo ví dụ Anthropic chỉ
  ~1-2 câu.
- 35 file reference nên tiếp tục theo pattern "domain-specific" (đã đúng hướng plugin hiện tại
  dùng — mỗi skill có reference riêng) — không gộp lại một file lớn.

---

## Query 2 — Context engineering: instruction dilution, over-long system prompt, compliance

Nguồn:
- Augment Code — "Context Engineering: Enhancing Agentic Swarm Coding..." augmentcode.com
  (không rõ ngày, bài blog 2025-2026). Trích bảng failure mode: "System prompt decay: content
  cạnh tranh (competing content volume) — instruction lặp lại tiêu tốn budget và cũng suy giảm
  theo". Dẫn nghiên cứu "Lost in the Middle" (Liu et al.) — thông tin ở giữa context nhận ít
  attention hơn đầu/cuối, không prompt nào sửa được hiệu ứng vị trí này.
- Firecrawl — "Context Engineering vs Prompt Engineering for AI Agents" firecrawl.dev/blog.
  Trích: nghiên cứu Databricks — độ chính xác giảm quanh mốc ~32k token (Llama 3.1 405B), sớm
  hơn với model nhỏ hơn. 4 kiểu context fail: poisoning, distraction, confusion, clash.
- tianpan.co/blog/2026-04-14-the-instruction-position-problem (2026-04-14). Trích: "Critical
  rules buried in the middle of a long system prompt degrade compliance rates by 30–50% so với
  cùng rule đặt ở đầu." Và: model cho thấy tới 61.8% biến thiên hiệu năng khi instruction bị
  viết lại/đổi vị trí dù ý nghĩa ngữ nghĩa không đổi — degradation cao nhất ở các ràng buộc
  hành vi kiểu "phải không được làm gì" (behavioral constraints / cấm).

Suy ra cho repo này:
- Đây là bằng chứng mạnh nhất cho việc **vị trí** của luật quan trọng hơn cả độ dài: luật cấm/
  hard-constraint (ví dụ mục 2, 6, 8 trong CLAUDE.md — không tự ý duyệt, ghi state chỉ qua
  script, không cài plugin mới không hỏi) nên nằm ở đầu hoặc cuối file, không chôn giữa đoạn
  văn dài.
- 10.8k token loaded-on-skill-call là dưới ngưỡng 32k nơi Databricks thấy độ chính xác bắt đầu
  giảm — nên rủi ro "quá dài" ở tầng skill hiện tại có vẻ chưa tới ngưỡng nguy hiểm; rủi ro thật
  sự nằm ở cách sắp xếp/lặp lại nội dung (system prompt decay do nội dung trùng lặp), không
  phải tổng số token.
- Rà lại các file xem có rule bị lặp ở nhiều chỗ (trùng giữa CLAUDE.md, tdq-conventions, và
  từng SKILL.md) — hợp nhất về một nguồn duy nhất sẽ giảm "competing content volume" đúng cơ
  chế mà Augment Code mô tả.

---

## Query 3 — Prompt compression kỹ thuật, giữ hành vi, cắt được bao nhiêu trước khi giảm chất lượng

Nguồn:
- Microsoft Research — "LLMLingua: Innovating LLM efficiency with prompt compression"
  microsoft.com/en-us/research/blog (2023). Nén tới 20x vẫn giữ được reasoning/summarization/
  dialogue capability (đo bằng EM). Model nhỏ (LLaMA-7B) chọn token theo perplexity để cắt.
- NeuralTrust — "Prompt Compression: Cut Token Costs Without Losing Quality" neuraltrust.ai.
  Trích: "Manual restructuring của system prompt dài dòng thường đạt 20-40% giảm mà KHÔNG mất
  chất lượng." Selective Context: giảm 50% với suy giảm BERTScore chỉ 0.023 (gần như không
  đổi). LLMLingua: <2% mất hiệu năng ở 20x nén trên benchmark CoQA/HotpotQA/TriviaQA.
- arXiv 2310.05736 (LLMLingua gốc, Jiang et al., Microsoft, 2023): nén 20x chỉ giảm 1.5 điểm
  hiệu năng trên 4 dataset (GSM8K, BBH, ShareGPT, Arxiv). Ablation cho thấy hầu hết module đều
  quan trọng, riêng "distribution alignment" bỏ đi chỉ giảm 0.5 điểm — phần khác giảm ~10% nếu
  bỏ.
- prompthub.us blog phân tích lại paper LLMLingua: nén cao (20x) đặc biệt mạnh với reasoning
  toán/logic — vượt cả baseline không nén trong vài trường hợp; nhưng khuyến cáo không nén quá
  20x vì hiệu năng "plateau rồi rơi nhanh", và có lập luận nên giữ compression đủ thấp để người
  còn đọc hiểu được bằng mắt thường (không chỉ máy hiểu).

Suy ra cho repo này:
- Các kỹ thuật trên (LLMLingua, Selective Context) là nén tự động bằng model phụ cho prompt
  RAG/runtime — KHÔNG áp dụng trực tiếp cho việc con người biên tập lại markdown tĩnh. Nhưng
  con số "manual restructuring đạt 20-40% giảm mà không mất chất lượng" (NeuralTrust) là mốc
  tham chiếu hợp lý cho việc viết lại thủ công: đặt mục tiêu cắt 20-40% số từ mỗi file mà không
  bỏ rule nào, thay vì đặt mục tiêu cắt token tối đa.
- Nguyên tắc ẩn trong ablation LLMLingua áp dụng được: **không phải phần nào của prompt cũng
  nén được như nhau** — phần chứa rule/constraint cứng phải giữ nguyên độ rõ, phần ví dụ/diễn
  giải/lặp lại là nơi nên cắt trước.
- Không có nguồn nào nói rule/luật (không phải ví dụ) có thể bị paraphrase tự do mà giữ nguyên
  compliance — paraphrase luật là rủi ro cao hơn xoá câu thừa, nên khi tối ưu ưu tiên: xoá lặp >
  rút gọn ví dụ > paraphrase câu luật (chỉ làm khi chắc chắn giữ nguyên nghĩa).

---

## Query 4 — Đo compliance / regression khi sửa instruction

Nguồn:
- IFEval — "Instruction-Following Evaluation for LLMs" (Zhou et al. 2023), qua emergentmind.com
  và alphaxiv.org/abs/2311.07911. Đo compliance bằng constraint có thể kiểm tra máy được (định
  dạng, độ dài, ngôn ngữ...). Có 2 metric: strict accuracy (một lỗi = cả response fail) và loose
  accuracy. Đây là benchmark hình mẫu cho việc viết test đo "có tuân thủ luật hay không" một
  cách máy kiểm được, thay vì chỉ đọc bằng mắt.
- Latitude — "How to Measure Instruction-Following in LLMs" latitude.so/blog. Giới thiệu thêm
  AdvancedIF (11/2025, Meta Superintelligence Labs + Princeton + CMU) — benchmark tập trung vào
  system-prompt steerability và multi-turn — gần với tình huống "sửa SKILL.md rồi xem agent có
  còn theo đúng luật không".
- Cekura — "Testing AI Chat Agents for Instruction-Following Failures" cekura.ai. Trích:
  "Instruction-following can regress after small changes" — khuyến nghị chạy regression test
  sau MỌI lần sửa prompt/workflow, dùng baseline + so sánh lặp lại (repeated runs) chứ không chỉ
  test một lần.
- tianpan.co (đã trích ở Query 2) đề xuất cụ thể: "positional sensitivity regression test" —
  đặt cùng một rule ở nhiều vị trí khác nhau trong prompt và đo tỷ lệ tuân thủ ở mỗi vị trí,
  coi bất kỳ thay đổi prompt nào là "potential compliance regression until proven otherwise".

Suy ra cho repo này:
- Repo đã có `scripts/tdq_eval.py` và thư mục `evals/` (thấy trong git status) — đúng hướng đề
  xuất của Cekura: cần bộ test case regression chạy được cho MỖI luật quan trọng trước/sau khi
  sửa file, không chỉ đọc lại bằng mắt.
- Nên tạo bộ "checklist tuân thủ" kiểu IFEval cho các rule cứng của CLAUDE.md/tdq-conventions
  (per-rule PASS/FAIL, không phải điểm tổng) — vì strict accuracy (một lỗi = fail cả rule đó)
  sát với cách TDQ đang tick `[x]` per-task.
- Sau mỗi lần viết lại file, nên chạy lại kịch bản thật (transcript mẫu) qua đúng những luật đã
  sửa vị trí/cách viết, để bắt được compliance regression trước khi merge — không có nguồn nào
  nói "đọc lại bằng mắt là đủ".

---

## Kết luận rút ra

1. Giữ SKILL.md dưới ~500 dòng là ngưỡng chính thức Anthropic khuyến nghị, không phải mục tiêu
   để ép cắt xuống mức tối thiểu — chỉ cắt file nào thực sự vượt/gần ngưỡng.
   (Nguồn: platform.claude.com/docs — Skill authoring best practices, Anthropic chính thức)
2. Viết `description` theo mẫu "làm gì + dùng khi nào" trong 1 câu cụ thể, tránh mô tả mơ hồ —
   đây là đòn bẩy rẻ nhất vì description luôn được nạp (always-loaded).
   (Nguồn: superpowers/writing-skills/anthropic-best-practices.md, mirror tài liệu Anthropic)
3. Luật cấm/hard-constraint phải nằm ở đầu hoặc cuối file, không chôn giữa đoạn văn dài — vị
   trí ảnh hưởng compliance 30-50%, mạnh hơn cả việc giảm tổng số từ.
   (Nguồn: tianpan.co/blog/2026-04-14-the-instruction-position-problem, 2026-04-14)
4. 10.8k token loaded-on-skill-call còn cách xa ngưỡng nguy hiểm ~32k token (nơi độ chính xác
   bắt đầu rơi theo nghiên cứu Databricks) — không cần hoảng vì tổng token, cần hoảng vì nội
   dung trùng lặp/rải rác nhiều nơi ("system prompt decay" do competing content volume).
   (Nguồn: firecrawl.dev/blog/context-engineering, trích nghiên cứu Databricks)
5. Khi biên tập thủ công, đặt mục tiêu cắt 20-40% số từ mỗi file mà không đổi nghĩa — đây là
   mốc "manual restructuring không mất chất lượng" đã được ghi nhận, cao hơn thì rủi ro tăng.
   (Nguồn: neuraltrust.ai/blog/prompt-compression-guide)
6. Thứ tự ưu tiên khi cắt: xoá nội dung lặp giữa các file trước → rút gọn ví dụ/diễn giải →
   paraphrase câu luật (rủi ro cao nhất, chỉ làm khi chắc chắn giữ nguyên nghĩa, không tự suy
   diễn).
   (Nguồn: suy luận từ ablation LLMLingua — arXiv 2310.05736 — không có nguồn trực tiếp nói
   paraphrase luật an toàn, nên tự thận trọng)
7. Sau khi sửa cách viết bất kỳ file luật nào, phải chạy lại test/transcript qua đúng những
   luật đã đổi vị trí/cách diễn đạt trước khi coi là xong — không đọc lại bằng mắt là đủ.
   (Nguồn: cekura.ai — Testing AI Chat Agents for Instruction-Following Failures)
8. Cân nhắc thêm bộ test kiểu "per-rule PASS/FAIL" (giống IFEval strict accuracy) cho các luật
   cứng của CLAUDE.md/tdq-conventions, tận dụng `scripts/tdq_eval.py` đã có sẵn trong repo.
   (Nguồn: IFEval — Zhou et al. 2023, qua alphaxiv.org/abs/2311.07911)
</content>
</invoke>
