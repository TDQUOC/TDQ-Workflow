# Research — 2026-07-31-audit-full-workflow

## Truy vấn 1 (tavily-primary, advanced): prompt engineering small local LLM instruction following limitations agentic workflow reliability

- Nguồn chính:
  - https://thirdeyedata.ai/data-ai-industry-insights/top-small-language-models-for-agentic-ai-solutions-development
  - https://futureagi.com/blog/small-language-models-agentic-ai-2025
  - https://web.dev/articles/practical-prompt-engineering
- Điều rút ra:
  - SLM/model tham số thấp: yếu ở long-horizon planning, dễ lỗi tool-calling,
    hallucination khi input nhiễu → cần **schema enforcement + validation ở tầng
    ngoài model** (đúng hướng plugin đang làm: wrapper script + JSON schema).
  - Prompt cho model nhỏ phải **chi tiết, cụ thể, format output tường minh**
    ("Only output the integer" style) — prompt kiểu gợi ý ngầm sẽ hỏng.
  - Production stack chuẩn: SLM làm việc hẹp + **fallback lên model mạnh khi
    low-confidence** — khớp thiết kế fallback Claude-tự-làm khi engine hỏng ≤3 attempt.

## Truy vấn 2 (tavily-primary, advanced): multi-agent LLM pipeline failure modes state machine orchestration edge cases 2025

- Nguồn chính:
  - MAST taxonomy (NeurIPS 2025, 1.600+ trace, 7 framework) — qua
    https://www.glukhov.org/ai-systems/architecture/multi-agent-orchestration-patterns
    và https://www.augmentcode.com/guides/why-multi-agent-llm-systems-fail-and-how-to-fix-them
  - https://www.linkedin.com/pulse/multi-agent-orchestration-production-playbook-reliable-nick-gupta-azcwe
- Điều rút ra (khung chấm audit):
  - MAST: 3 nhóm gốc lỗi hệ đa agent — **(1) specification ambiguity 33%**
    (vai trò mơ hồ, trùng việc, bỏ verify), **(2) coordination breakdown**,
    **(3) verification gap**. Audit nên chấm từng contract agent/skill theo 3 trục này.
  - Nguyên tắc "deterministic workflow quanh nondeterministic reasoning" (LLM quyết
    định gì, workflow engine bảo đảm chạy được) — plugin đã theo (state CLI, hook,
    wrapper); audit kiểm chỗ nào còn dựa vào "model tự nhớ luật" thay vì máy ép.

## Khảo sát nội bộ (đọc code turn analyze)

- Bề mặt audit: 6 skill (+9 references), 7 agent def, 8 script chính + 2 sample,
  5 hook script + hooks.json, 28 test file (338 test), portable/ (bản mirror), CLAUDE.md §10.
- **Issue thấy sớm #1**: `scripts/tdq_state.py:576` — `re.sub(..., r'`\\1`', item)`
  escape sai → `phases.md` (file tự sinh) chứa literal `` `\1` `` thay vì lệnh thật
  ở mục analyze/spec/plan (3 dòng hướng dẫn mất nội dung). Model cấp thấp đọc bảng
  này sẽ không có lệnh để chạy. Fix 1 dòng + regenerate + test.
- Ma trận case dự kiến cho audit (sẽ chốt ở interview):
  lane {quick, full} × mode {main, subagent, external} × deep search {2-phase,
  degrade a/b/c} × sự cố {engine hỏng, compact/restart phiên, request đè request,
  approve mơ hồ, worktree bẩn, hook fail} × model {Claude, agy/codex slug thấp}.
