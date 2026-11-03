# RESEARCH — Instruction/skills đủ chắc để model yếu đi đúng workflow

Ngày: 2026-07-28 · Request: [2026-07-28-instruction-hardening-7b](../requests/2026-07-28-instruction-hardening-7b.md)
Công cụ: `tavily-primary` (4 truy vấn, search_depth=advanced) + WebFetch doc chính thức.

## R1 — PreToolUse có nhận `additionalContext` không? (câu hỏi sống-còn của thiết kế 0.2.0)

- **Nguồn quyết định**: https://code.claude.com/docs/en/hooks (fetch 2026-07-28) — mục *Add context for Claude*: `additionalContext` được hỗ trợ ở **SessionStart, Setup, SubagentStart, UserPromptSubmit, UserPromptExpansion, PreToolUse, PostToolUse, PostToolUseFailure, PostToolBatch, Stop, SubagentStop**. Schema PreToolUse: `permissionDecision: allow|deny|ask|defer` + `permissionDecisionReason` + `additionalContext` + `updatedInput`. "When several hooks return `additionalContext` for the same event, Claude receives all of the values."
- Nhiễu cần loại: https://github.com/anthropics/claude-code/issues/15664 là **feature request cũ** khẳng định PreToolUse KHÔNG có `additionalContext`. Doc chính thức hiện tại phủ định điều đó → issue đã lạc hậu, không dùng làm căn cứ.
- Nguồn phụ xác nhận: hidekazu-konishi.com (Hooks Complete Guide), morphllm.com/claude-code-hooks, claudefa.st/blog/tools/hooks/hooks-guide — đều liệt kê `additionalContext` trong output PreToolUse.
- **Hệ quả**: kiến trúc "hook = remind" của 0.2.0 hợp lệ về mặt cơ chế. **Stop hook cũng nhận `additionalContext`** (inject cuối turn, hội thoại tiếp tục) → có thêm một điểm nhắc chưa dùng đến.
- Cảnh báo từ cùng nguồn: `permissionDecision: "allow"` **không nới** được quyền — nó chỉ bỏ qua prompt xác nhận, không ghi đè rule `deny`/`ask` trong settings. Đúng với ta (ta chỉ dùng allow để không chặn).

## R2 — Instruction dạng văn xuôi KHÔNG phải cơ chế bảo đảm

- github.com/anthropics/claude-code/issues/7777: agent "treat contextual instructions as advisory rather than mandatory process steps"; chính Claude tự chẩn đoán nguyên nhân là **thiếu process gating** — cần buộc *hiển thị hoàn thành từng bước* thay vì tham chiếu checklist sau khi đã làm.
- dev.to/minatoplanb ("200 lines of rules, ignored"): **càng nhiều rule → tỉ lệ tuân thủ càng giảm**; "the only reliable enforcement is code (hooks, pre-commit, CI), not prompts".
- Doc/bài tổng hợp CLAUDE.md (medium/@bijit211987, towardsai): "CLAUDE.md shapes typical agent behavior. It does not guarantee it." Rule nào không được phép vi phạm thì phải nằm trong code chạy bất kể model có hợp tác hay không.
- **Rút ra cho request này**: muốn "agent buộc tuân theo hook" thì đòn bẩy mạnh nhất KHÔNG phải viết thêm chữ, mà là (a) rút gọn số rule, (b) biến rule thành **lệnh script deterministic** để agent chỉ cần chạy, (c) yêu cầu agent **echo dấu vết đã thực thi** để Stop hook kiểm được.

## R3 — Viết prompt/instruction cho model yếu (7B)

- dev.to/superorange0707 (*Production-Grade Prompting Playbook for 7B*): "one prompt, one job"; 7B "love rigid scaffolding" → khung cố định ROLE / TASK / CONSTRAINTS / FORMAT / INPUT; format output phải coi như **hợp đồng** kèm vòng sửa lỗi; chia chuỗi bước nhỏ thay vì một yêu cầu ghép nhiều việc.
- mitjamartini.com (*Prompting Small LLMs*): be precise, be concise, **only do one task at a time**, đừng dựa vào khả năng suy luận, dùng prompt template cố định.
- reddit r/LocalLLaMA (*Prompt Engineering for 7b LLMs*): dùng **delimiter/markdown** để phân tách vùng prompt (markdown là format hiệu quả nhất); chỉ đưa context thiết yếu (nhồi nhiều đoạn không cấu trúc làm model chọn sai phần); few-shot để ghì hành vi; giả định model *sẽ* sai nếu lặp đủ nhiều → phải có guardrail.
- milnepublishing (*Mastering Prompt Engineering*): chain-of-thought và "instruction nhiều phần" chỉ đáng tin ở model lớn; **prompt chaining (chia nhỏ bước)** là cách nâng độ tin cậy cho model nhỏ.
- arxiv 2506.08669 (*Blueprints for SLMs*): SLM nhạy cảm với prompt; blueprint có cấu trúc, tái sử dụng được cho kết quả ổn định hơn mô tả nhiệm vụ ở mức cao.

## R4 — Chuẩn viết skill của Claude Code (giới hạn thực tế khi "viết chi tiết hơn")

- platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices: **giữ thân SKILL.md < 500 dòng**; vượt thì tách sang file trong `references/` theo *progressive disclosure* (3 tầng: metadata → thân skill → file tham chiếu); "for particularly complex workflows, provide a **checklist that Claude can copy into its response and check off** as it progresses".
- Skill Authoring Guide (gist lipex360x): dùng **thể mệnh lệnh** ("Extract the color palette", không "You should…"); **đánh số bước**, header cho từng phase để tham chiếu được ("quay lại bước 2"); mô tả skill phải "pushy" (nêu rõ trigger) vì Claude có xu hướng under-trigger; **định nghĩa format output tường minh**.
- williamspurlock.com: tách một "mega skill" 1.200 dòng thành SKILL.md 200 dòng + 3 file phụ → cải thiện mức tuân thủ chỉ dẫn rõ rệt (con số 40% là quan sát cá nhân, không phải đo chuẩn — chỉ dùng làm định hướng).
- LinkedIn/noahlz (thực chiến): để model chắc chắn đọc file tham chiếu phải ra lệnh kiểu `DELEGATE_TO: [file]` + "STOP, do not proceed until you read the file"; và **"Actually, just use scripts"** — bundle script, bảo model chạy rồi đọc kết quả (in JSON) thay vì viết hàng chục dòng guardrail bằng chữ.

## Kết luận dùng cho spec

1. Cơ chế hook hiện tại đúng và còn dư địa (`Stop.additionalContext`).
2. Không giải bài toán bằng cách viết thêm chữ: **giảm rule, tăng script**. Mỗi bước workflow nên quy về một lệnh `tdq_state.py …` in ra JSON/chỉ dẫn kế tiếp.
3. Skill viết lại theo khuôn cứng: mệnh lệnh, đánh số, có checklist copy được, có ví dụ, có format output tường minh; thân < 500 dòng, chi tiết dài đẩy sang `references/`.
4. Buộc tuân thủ = làm cho việc tuân thủ **kiểm chứng được** (agent echo dấu vết, Stop hook soi), không phải in đậm thêm chữ "BẮT BUỘC".
