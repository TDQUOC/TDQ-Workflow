# Research — 2026-07-31-hybrid-deep-search

Chạy 2026-07-31 16:05 (+07), tavily-primary, 2 truy vấn khác góc + dữ liệu
benchmark nội bộ cùng ngày.

## Truy vấn 1 — pattern orchestration đa agent cho search
- Query: "multi-agent search orchestration planner scout worker pattern broad
  then deep research agents best practices"
- Nguồn: openlayer.com/blog/post/multi-agent-system-architecture-guide;
  langchain.com/blog/choosing-the-right-multi-agent-architecture;
  truefoundry.com/blog/multi-agent-orchestration-frameworks
- Rút ra: pattern chuẩn cho việc này là **supervisor (orchestrator-worker)** —
  1 coordinator plan, giao việc, merge; phù hợp khi các nhánh độc lập.
  LangChain khuyên "complexity should be earned" — chỉ thêm tầng khi có giới
  hạn rõ (ở đây: benchmark chứng minh agy thuần bị sót vendor → tầng scout
  có lý do bằng số liệu).

## Truy vấn 2 — hệ research đa agent của Anthropic (căn cứ chính)
- Query: "Anthropic multi-agent research system orchestrator subagents lessons
  parallel search"
- Nguồn: anthropic.com/engineering/multi-agent-research-system (gốc);
  theaiengineer.substack.com/p/how-anthropic-built-multi-agent-deep
- Rút ra:
  - Lead agent phân tích → spawn 3–5 subagent song song, mỗi subagent cần
    "objective + output format + tools + task boundaries" rõ — đúng khuôn
    brief/route + schema JSON đang có.
  - Song song chỉ lợi khi các nhánh ĐỘC LẬP — phase 1 (scout ∥ agy tổng quát)
    và các route phase 2 đều độc lập → hợp lệ.
  - "Search là nén thông tin": scout chỉ cần trả bản đồ hướng nén, không cần
    quote sâu → xác nhận thiết kế scout "mỏng".

## Dữ liệu benchmark nội bộ (docs/tdq/research/search/, 2026-07-31)
- Run A (agy thuần, flash-low): 233s, 93.1k token Claude, 9 findings, sót
  Deepgram + AssemblyAI dù được chỉ đích danh trong route.
- Run B (Claude+Tavily): 200s, 189.4k token, 16 findings, phủ đủ + finding
  phủ định (OpenAI Realtime không có word-level timestamp).
- Kết luận số liệu: hybrid nhắm ~150–190k token, độ phủ tiệm cận Run B.

## Ground truth model
- `external_models.py list agy` → có `gemini-3.6-flash-medium` (giữa low/high),
  ngoài ra flash 3.5, pro 3.1, claude-sonnet-4-6… Slug default hiện tại trong
  `search_task.py:38` là flash-low, escalation flash-high.
