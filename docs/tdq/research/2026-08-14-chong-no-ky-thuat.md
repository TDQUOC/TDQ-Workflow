# Research: chống nợ kỹ thuật khi agent code (2026-08-14)

## 1. Architecture fitness functions / conformance testing

Truy vấn: architecture fitness functions ArchUnit dependency-cruiser import-linter
deptrac automated conformance testing 2025

Nguồn:
- https://handsonarchitects.com/blog/2026/protecting-architecture-with-automated-tests-in-python
- https://www.infoq.com/articles/fitness-functions-architecture
- https://www.thoughtworks.com/en-us/insights/articles/fitness-function-driven-development
- https://www.archunit.org/userguide/html/000_Index.html

Rút ra:
- Fitness function là test tự động hoá ràng buộc kiến trúc, chạy trong CI như
  unit test bình thường (ArchUnit cho Java, PyTestArch cho Python).
- Cơ chế: khai báo rule kiểu "layer A không được import layer B", assert bằng
  bytecode/AST analysis, fail build khi vi phạm.
- Giá trị cốt lõi: bắt lỗi kiến trúc ngay khi agent tạo dependency sai hướng,
  không chờ review thủ công phát hiện.
- Chi phí: cần chọn/viết tool tương ứng ngôn ngữ dự án, viết rule ban đầu
  (thường vài chục dòng rule cho layer + cycle check), chạy như một bước CI.
- Hạn chế: chỉ bắt vi phạm cấu trúc (dependency, layer, import), không bắt
  trùng lặp logic hay lệch convention đặt tên.

## 2. Architecture Decision Records làm ràng buộc cho AI agent

Truy vấn: Architecture Decision Records ADR constraint input for AI coding
agent LLM context 2025

Nguồn:
- https://codemyspec.com/blog/architectural-decision-records
- https://blog.thestateofme.com/2025/07/10/using-architecture-decision-records-adrs-with-ai-coding-assistants
- https://github.com/me2resh/agent-decision-record

Rút ra:
- ADR ghi quyết định kiến trúc dạng ngôn ngữ tự nhiên có cấu trúc (context,
  option, decision, consequence) — agent đọc trước khi code để tránh drift.
- Không có ADR, agent tự chọn công nghệ/pattern khác chuẩn đã chốt (ví dụ đổi
  framework, thêm ORM song song) khi gặp mơ hồ; nghiên cứu ArXiv ghi nhận agent
  có xu hướng vi phạm ràng buộc tăng dần theo thời gian nếu ràng buộc mơ hồ.
- Pattern "Pre-Made Decisions": viết ADR chuẩn stack trước khi code, agent đọc
  → agent tuân theo; pipeline CI verify agent có tuân theo thật không (ADR là
  gợi ý, CI là cổng chặn).
- Biến thể mới: Agent Decision Records (AgDR) — agent tự ghi ADR khi nó ra
  quyết định kỹ thuật, có trường agent/model/timestamp để truy vết sau này.
- Chi phí: mỗi ADR là một file markdown ngắn (thường 20-40 dòng), không cần
  script mới, chỉ cần quy ước thư mục + yêu cầu agent đọc trước khi plan.

## 3. AI agent gây technical debt — số liệu và mô hình thất bại

Truy vấn: GitClear AI code duplication technical debt study 2024 2025 copy
paste refactor rate

Nguồn:
- https://www.gitclear.com/ai_assistant_code_quality_2025_research
- https://gitclear-public.s3.us-west-2.amazonaws.com/GitClear-AI-Copilot-Code-Quality-2025.pdf
- https://leaddev.com/technical-direction/how-ai-generated-code-accelerates-technical-debt
- https://www.tembo.io/blog/ai-technical-debt

Rút ra:
- GitClear phân tích 211 triệu dòng code (2020-2024): "refactor" (đo bằng dòng
  "moved") giảm từ 25% (2021) xuống dưới 10% (2024).
- Code trùng lặp (block ≥5 dòng giống đoạn liền kề) tăng gấp 8 lần trong 2024;
  2024 là năm đầu tiên dòng "copy/paste" vượt dòng "moved" trong lịch sử đo.
- Code churn (dòng bị sửa lại trong vòng 2 tuần sau khi viết) tăng từ 5.5% lên
  7.9% — dấu hiệu code viết ra không đủ chín, phải vá gấp.
- Cơ chế thất bại: agent ưu tiên viết đoạn mới giống cái cũ thay vì trích
  hàm dùng chung, vì "viết lại" rẻ hơn "tìm và tái dùng" trong ngữ cảnh agent.
- Hệ quả: mỗi bản sao là một điểm phân kỳ riêng — sửa 1 bug phải sửa N nơi,
  chi phí bảo trì tăng tuyến tính theo N bản sao.

## 4. Guardrail thực tế: CLAUDE.md, reuse-first, blast-radius

Truy vấn: AGENTS.md CLAUDE.md guardrail AI coding agent reuse-first read
before write blast radius impact analysis

Nguồn:
- https://arxiv.org/html/2601.20404v1
- https://dev.to/maxkrivich/ai-coding-agent-security-practical-guardrails-for-claude-code-copilot-and-codex-och
- https://spacelift.io/blog/claude-code-for-infrastructure-as-code
- https://nljug.org/foojay/%F0%9F%A4%96-5-best-practices-for-working-with-ai-agents-subagents-skills-and-mcp

Rút ra:
- CLAUDE.md/AGENTS.md là file ngữ cảnh đọc đầu phiên, chứa quy ước kiến trúc,
  coding convention, test rule — cơ chế rẻ nhất vì không cần chạy tool riêng.
- Nguyên tắc thực chiến được trích dẫn: "đưa agent vào cùng bộ kiểm tra mà
  senior review dùng — house lint, design-pattern enforcement — thay vì chỉ
  sandbox nó"; agent fail nhanh khi vi phạm rule tốt hơn agent chỉ bị cô lập.
- Mẫu hình 3 lớp guardrail: CLAUDE.md ghi sự kiện đứng (facts, kiến trúc);
  skill ghi quy trình lặp lại; hook ép buộc hành vi xác định (chạy test sau
  edit, chặn lệnh nguy hiểm, yêu cầu duyệt).
- "Blast radius" xuất hiện như nguyên tắc: giới hạn phạm vi agent được sửa,
  build kiểm tra trước khi merge vào main — không tìm thấy công cụ chuyên dụng
  "impact analysis" riêng cho AI agent ngoài phạm vi lint/test hiện có.
- Chi phí: một file markdown (CLAUDE.md/AGENTS.md), không cần script mới; hook
  ép chạy test/lint cần vài chục dòng cấu hình.

## 5. Cổng QC tự động phát hiện trùng lặp / vi phạm quy ước

Truy vấn: SonarQube jscpd code duplication detection quality gate CI 2025

Nguồn:
- https://medium.com/@lamjed.gaidi070/sonarqube-in-2025-the-ultimate-guide-to-code-quality-ci-cd-integration-alerting-43e96018d36f
- https://community.sonarsource.com/t/quality-gate-doesnt-appear-to-be-working/148785
- https://community.sonarsource.com/t/code-duplication-quality-gate-and-default-branch/26999

Rút ra:
- SonarQube CPD (Copy-Paste Detector) quét token, đánh dấu block trùng vượt
  ngưỡng (mặc định min ~10 dòng/100 token tuỳ ngôn ngữ); Quality Gate mặc định
  chặn merge khi trùng lặp trên "new code" vượt 3%.
- Cơ chế thực thi: chạy `sonar-scanner` trong CI, set
  `-Dsonar.qualitygate.wait=true` để pipeline chờ kết quả rồi mới cho merge.
- jscpd là bản nhẹ, mã nguồn mở, chạy CLI không cần server — phù hợp check cục
  bộ nhanh trước khi đẩy lên CI nặng.
- Điểm yếu thực tế: false positive với đoạn lặp cấu trúc hợp lệ (ví dụ
  attribute lặp trong nhiều controller, javadoc lặp) — cần exclude pattern,
  tốn công tinh chỉnh ban đầu.
- Chi phí: cần server SonarQube hoặc CLI jscpd, cấu hình ngưỡng + exclusions
  (vài chục dòng property), thêm một bước CI chờ quality gate.

## 6. Spec-driven development chống drift kiến trúc

Truy vấn: GitHub Spec Kit spec-driven development architecture drift
prevention AI coding agent 2025; constitution.md enforce definition of done

Nguồn:
- https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit
- https://github.com/github/spec-kit/blob/main/spec-driven.md
- https://linuxera.org/spec-driven-development-with-spec-kit
- https://www.augmentcode.com/guides/what-is-spec-driven-development

Rút ra:
- Spec Kit có `constitution.md` — file "hiến pháp" bất biến, agent phải đọc và
  pass "constitutional check" trước khi lập plan và trước khi code.
- Cơ chế ép buộc: plan template có "Phase -1: Pre-Implementation Gates" với
  checklist boolean (vd Simplicity Gate, Anti-Abstraction Gate) — agent tự
  đánh dấu pass/fail, không pass thì không được sang phase code.
- Article I "Library-First": mọi feature bắt đầu như một library độc lập, ép
  modular hoá thay vì viết thẳng logic rải rác — giảm khả năng trùng lặp.
- TDQ hiện có spec → plan → build nhưng thiếu: (a) file "hiến pháp" kiến trúc
  cố định để agent tự kiểm tra trước khi build, (b) gate boolean bắt agent tự
  chứng minh không phá simplicity/không tạo abstraction thừa.
- Chi phí: một file constitution ổn định qua nhiều request (không viết lại
  mỗi lần), cộng vài dòng checklist chèn vào khuôn plan hiện có.

## Ứng viên cơ chế cho TDQ

- Constitution file kiến trúc: chặn agent tự đổi stack/pattern; cần 1 file
  markdown ổn định, đọc ở đầu build, không cần script.
- Fitness function CI (ArchUnit/PyTestArch/dependency-cruiser tuỳ stack):
  chặn dependency sai layer; cần chọn tool theo ngôn ngữ, viết rule ban đầu.
- Duplication gate (jscpd hoặc SonarQube CPD): chặn copy-paste thay vì tái
  dùng; cần cấu hình ngưỡng, thêm bước CI, có thể cần exclude pattern.
- ADR bắt buộc cho quyết định kỹ thuật: chặn lệch quyết định đã chốt; mỗi
  ADR một file ngắn, không cần script mới.
- Definition-of-done gate kiểu boolean (Simplicity/Anti-Abstraction): chặn
  over-engineering và trùng lặp; thêm vài dòng checklist vào khuôn plan.
- "Reuse-first" rule trong CLAUDE.md: yêu cầu agent grep trước khi viết hàm
  mới; không cần script, chỉ cần một quy tắc rõ trong file ngữ cảnh.
- Blast-radius declaration trước khi sửa: agent liệt kê file/module bị ảnh
  hưởng trước khi edit; thêm một bước report trong plan, không cần tool.
- AgDR tự động (agent tự ghi quyết định khi code): dùng truy vết sau này khi
  phát hiện drift; cần một script nhỏ ghi file theo mẫu khi agent quyết định.
