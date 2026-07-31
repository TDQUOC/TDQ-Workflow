# Knowledge — 2026-07-31-hybrid-deep-search

Trạng thái: analyze XONG (interview vòng 1 đã chốt 16:07) — sẵn sàng spec.

## Năng lực dùng được

Phân vân → DÙNG. Không xoá bảng này kể cả khi mọi dòng là KHÔNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake, tdq-spec, tdq-plan, tdq-build, tdq-status, tdq-conventions | plugin:tdq-workflow | NỀN | workflow đang chạy |
| tavily-search | plugin:tavily | DÙNG | scout Claude phase 1 search rộng (đã dùng ở analyze) |
| tavily-extract | plugin:tavily | DÙNG | scout lấy quote khi cần xác nhận nhanh nguồn |
| tavily-best-practices | plugin:tavily | DÙNG | tham chiếu khi viết luật scout trong deep-search.md |
| tavily-cli, tavily-crawl, tavily-map, tavily-research, tavily-dynamic-search | plugin:tavily | KHÔNG | spec §3 đã chọn cách khác tốt hơn (scout dùng tavily-search/extract MCP; crawl/map/research ngoài phạm vi flow) |
| graphify | user | DÙNG | cuối turn build chạy `graphify extract . --code-only` theo CLAUDE.md §10 |
| skill-creator, skill-development | plugin | KHÔNG | khác lĩnh vực (chỉ sửa skill có sẵn, không tạo skill mới) |
| plugin-structure, plugin-settings, agent-development, command-development, hook-development, mcp-integration | plugin:plugin-dev | KHÔNG | khác lĩnh vực (không đổi cấu trúc plugin/agent mới) |
| claude-md-improver, frontend-design, playground, build-mcp-app, build-mcp-server, build-mcpb, writing-hookify-rules, remember, dataviz, artifact-design, artifact-capabilities, update-config, keybindings-help, claude-api, run, loop, schedule | plugin/built-in | KHÔNG | khác lĩnh vực |
| simplify, security-review, code-review (built-in) | built-in | KHÔNG | user đã cấm (review dùng built-in /code-review khi user gọi, không tự bật) |

## Hiện trạng code (đọc 2026-07-31)
- `scripts/search_task.py`: `DEFAULT_MODEL = "gemini-3.6-flash-low"` (dòng 38),
  `ESCALATION_MODEL = "gemini-3.6-flash-high"` (dòng 39); effort nằm trong slug,
  agy không có flag riêng. Subcommand split/run/merge; cap qua env
  `TDQ_SEARCH_MAX_AGENTS` (settings.json = 3).
- `agents/search-runner.md`: vỏ mỏng chạy wrapper + watcher foreground (fix
  QC vòng 2, đã validate 3/3 phiên mới).
- `skills/tdq-conventions/references/deep-search.md`: luật trigger ≥2 dấu hiệu,
  chia route, fallback Tavily khi engine-failed ≥2 — sẽ phải viết lại flow hybrid.
- Test: `tests/test_search_task.py` 41 test (suite 326); có test khuôn agent
  (`SearchRunnerAgentTest`) và test docs consistency (CHANGELOG↔plugin.json).
- Benchmark evidence: `docs/tdq/research/search/2026-07-31-stt-wordlevel{,-claude}/`.

## Quyết định đã chốt (từ request + interview)
- Flow 2 phase: Phase 1 = 1 Claude scout ∥ 1 agy tổng quát (song song);
  Phase 2 = agent agy đào sâu theo route Claude tổng hợp từ phase 1.
- agy là engine ưu tiên; default model đổi thành `gemini-3.6-flash-medium`.
- Cap Claude toàn flow ≤3 agent (phase 1 dùng 1).
- Cap agy phase 2: **3** (giữ `TDQ_SEARCH_MAX_AGENTS=3`).
- Escalation: **medium → high** (giữ ≤2 retry, chỉ đổi điểm xuất phát).
- Findings phase 1 (scout + agy tổng quát): **gộp vào kết quả cuối** — ghi
  theo **format file agent** (như output `cmd_run`, có `url_alive`/`not_found`/
  `queries_used`) để merge rank đúng; xem spec 1.1 §3.
- **Luôn chạy đủ 2 phase** — không có đường tắt bỏ scout; cổng vào duy nhất
  vẫn là luật trigger deep search ≥2 dấu hiệu.

## Ràng buộc
- Tổng agent: phase 1 = 1 Claude + 1 agy; phase 2 ≤3 agy → ≤5 slot/run,
  Claude chỉ 1 (dưới cap ≤3 user đặt).
- Ước lượng: ~160–190k token Claude/run, wall ~7–8 phút (2 phase tuần tự,
  trong phase chạy song song).
- Không cần model/download mới (flash-medium đã có trong agy trên máy).
- QC/test: unit test cho default model + escalation mới, khuôn agent/skill
  cập nhật, E2E hybrid thật 1 topic, suite + doc_lint xanh.

## Phương án đã loại
- Scout 3 agent Claude (bản đầu): user thu về 1 agent (16:01) — đủ nắm hướng,
  rẻ ~3× token phase 1.
- Đường tắt bỏ phase 1: user loại (16:07) — ưu tiên flow đồng nhất.
- Escalation 3 bậc / thêm pro: loại — tốn quota, chưa có bằng chứng cần.

## Nguồn
- Nội bộ: benchmark 2 run cùng ngày (xem research/<slug>.md).
- Ngoài: anthropic.com/engineering/multi-agent-research-system (orchestrator-
  worker, subagent cần objective/format/boundaries rõ, song song cần độc lập).
