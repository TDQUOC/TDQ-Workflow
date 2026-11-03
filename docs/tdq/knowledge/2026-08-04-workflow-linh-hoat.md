# Knowledge — 2026-08-04-workflow-linh-hoat

## Năng lực dùng được

Phân vân → DÙNG. Không xoá bảng này kể cả khi mọi dòng là KHÔNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake, tdq-spec, tdq-plan, tdq-build, tdq-conventions, tdq-status | plugin:tdq-workflow | NỀN | chính workflow đang chạy — đồng thời là ĐỐI TƯỢNG bị sửa |
| skill-creator | plugin:skill-creator | DÙNG | rà lại hình dạng SKILL.md sau khi sửa 5 skill (frontmatter, độ dài, mô tả trigger) |
| tavily-search | plugin:tavily | DÙNG | đã dùng ở phase analyze để xác minh trường `effort`/`model` của subagent frontmatter |
| update-config | built-in | DÙNG | nếu phải chỉnh `~/.claude/settings.json` cho hook (chỉ khi cần) |
| graphify | user | DÙNG | rebuild code graph cuối turn build (repo có hook post-commit) |
| plugin-dev:agent-development | plugin:plugin-dev | KHÔNG | thiếu quyền/công cụ skill đó cần — plugin on_demand đang tắt, và việc chỉ sửa frontmatter model/effort đã có docs chính thức |
| claude-md-improver, revise-claude-md | plugin:claude-md-management | KHÔNG | thiếu quyền/công cụ skill đó cần — plugin on_demand đang tắt; sửa CLAUDE.md ở đây là sửa 1 mục đã biết rõ |
| dataviz, artifact-design, artifact-diagramming, artifact-capabilities, frontend-design, playground | built-in | KHÔNG | khác lĩnh vực |
| build-mcp-app, build-mcp-server, build-mcpb, mcp-integration | plugin:mcp-server-dev, plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| plugin-structure, plugin-settings, command-development, hook-development, skill-development | plugin:plugin-dev | KHÔNG | thiếu quyền/công cụ skill đó cần — plugin on_demand đang tắt |
| writing-hookify-rules, hookify:* | plugin:hookify | KHÔNG | khác lĩnh vực — hook của repo này viết tay bằng Python, không qua hookify |
| remember, remember:doctor | plugin:remember | KHÔNG | khác lĩnh vực |
| tavily-crawl, tavily-map, tavily-extract, tavily-research, tavily-cli, tavily-best-practices, tavily-dynamic-search | plugin:tavily | KHÔNG | spec §3 đã chọn cách khác tốt hơn — tavily-search đã đủ, không cần crawl/map |
| feature-dev, code-review, security-review, simplify, review, init, run | built-in | KHÔNG | khác lĩnh vực — đây là sửa doc/skill + hook, không phải phát triển tính năng app |
| claude-api, update-config(keybindings-help), schedule, loop, fewer-permission-prompts | built-in | KHÔNG | khác lĩnh vực |

## Quyết định đã chốt (từ interview vòng 1 + 2)

| # | Quyết định | Lý do |
|---|---|---|
| D1 | **Bỏ gọi mặc định agent `tdq-reviewer`** ở tdq-spec bước 2 và tdq-plan bước 3. **Giữ file** `agents/tdq-reviewer.md` để gọi tay khi user yêu cầu. | Q1=1. Giữ file ⇒ `tests/test_skill_shape.py::ReadOnlyAgentToolsTest` vẫn xanh. |
| D2 | **Model sub-agent: heuristic, Claude tự quyết mỗi lần gọi** qua tham số `model` của Agent tool. Frontmatter mỗi agent đặt `model` + `effort` mặc định hợp vai. | Q2=1 + Q8=a. Agent tool không có tham số `effort` (research §B) ⇒ effort chỉ tĩnh được. |
| D3 | **Ghép gate, không tách turn**: vẫn 2 lần duyệt (spec; rồi plan+mode) nhưng `duyệt spec` → viết plan NGAY trong cùng turn; `duyệt plan mode <X>` → build NGAY trong cùng turn. Bỏ luật "spec và plan không cùng turn" và bỏ bước hỏi mode riêng trước khi viết plan. | Q3=1. Mode được đề xuất trong plan, user chốt lúc duyệt. |
| D4 | **Giữ 2 lane quick/full**, cho co giãn bên trong. Lane quick = **một file mini-spec/plan gộp** (`docs/tdq/plan/<slug>.md` rút gọn: scope + task + DoD), **một lần duyệt**, có web search + phân tích + interview khi thật sự có ẩn số. | Q4=1 + Q10=a. |
| D5 | **Giữ interface AskUserQuestion**; mỗi vòng hỏi BẮT BUỘC có câu cuối "Bạn muốn bổ sung thêm gì không?" với 1 phương án mở để user trả lời tự do. | Q6 (user đổi ý ở vòng 1). |
| D6 | **Bước quyết lộ trình (routing)** sau interview: Claude ghi mục `## Lộ trình` vào `knowledge/<slug>.md` (phase sẽ chạy / bỏ, skill sẽ dùng, lý do), tóm tắt lại trong spec; **user duyệt spec là duyệt luôn lộ trình**. Không thêm trường `route` vào state. | Q9=a. Tránh đổi schema state (v3→v4) và kéo theo nhiều test. |
| D7 | **Được sửa** hook approval-gate (`prompt_context.py`, `bash_gate.py`, `stop_gate.py`) và `scripts/tdq_state.py`. | Q5=có. |
| D8 | Sửa đồng bộ: `~/.claude/CLAUDE.md` mục 9, `portable/workflow/0{1..4}-*.md`, `portable/AGENTS.md`, `phases.md` (sinh lại bằng `phases-doc`). | Giả định nêu ở questions vòng 2, user không phản đối. |

## Ràng buộc kỹ thuật

1. `PHASE_TABLE` trong `scripts/tdq_state.py` là nguồn sự thật duy nhất; `skills/tdq-conventions/references/phases.md` phải sinh lại bằng `tdq_state.py phases-doc`, cấm sửa tay. `tests/test_phase_table.py` khoá cứng.
2. Trần dòng SKILL.md (`doc_lint.SKILL_LINE_LIMITS`): intake 120, spec 100, plan 100, build 150, conventions 120. Nội dung thêm mà vượt trần → đẩy sang `references/`.
3. `tests/test_portable_sync.py` so KHỚP TỪNG BƯỚC đánh số giữa `skills/tdq-{intake,spec,plan,build}/SKILL.md` và `portable/workflow/0{1..4}-*.md` ⇒ mọi sửa đổi bước phải làm song song hai nơi.
4. Hook hiện tại KHÔNG cản việc gộp turn: `prompt_context.py` tính `pending` theo từng prompt của user (mỗi lần duyệt vẫn là 1 prompt riêng); `bash_gate.NEXT_PHASE_TARGET` cho phép `approve spec` rồi `set phase=plan` trong cùng turn. Việc phải sửa là **văn bản nhắc** (`render_next`, `PHASE_TABLE.forbidden/action/checklist`), không phải logic chặn.
5. `effort` trong frontmatter subagent **đè lên** mức effort của phiên (docs model-config) ⇒ đặt effort thấp cho agent nặng sẽ làm hỏng chất lượng ngay cả khi user để phiên ở mức cao. Chỉ đặt effort thấp cho agent thuần cơ học (runner bọc script).
6. Plugin subagent bỏ qua `permissionMode`/`mcpServers`/`hooks`, nhưng **honor `model` và `effort`** (docs sub-agents).

## Cách tiếp cận đã chọn

Sửa **văn bản luật** (skill + PHASE_TABLE + portable + CLAUDE.md) + **frontmatter agent**, giữ nguyên schema state. Đây là thay đổi ít rủi ro nhất cho một bộ đã có 448 test đang xanh, và đủ để đạt cả 6 yêu cầu.

## Phương án đã loại

- **Thêm trường `route` vào state (schema v4)** — loại theo Q9=a: kéo theo migration + sửa nhiều test, lợi ích chỉ là hook nhắc đúng bước.
- **Xoá hẳn agent `tdq-reviewer`** — loại theo Q1=1.
- **Bỏ lane, một luồng duy nhất** — loại theo Q4=1.
- **Nhân đôi agent thành biến thể nhẹ/nặng để đổi effort động** — loại theo Q8=a (gấp đôi file, dễ lệch nội dung).

## Lộ trình (D6 — áp cho chính request này)

| Phase | Chạy? | Lý do |
|---|---|---|
| analyze | ✅ đã xong | 2 vòng interview, research xác minh `effort`/`model` |
| spec | ✅ | thay đổi chạm 5 skill + 3 hook + state + portable + CLAUDE.md → cần scope in/out rõ |
| plan | ✅ | nhiều file, cần thứ tự phụ thuộc (PHASE_TABLE trước → phases.md sinh lại → portable sync) |
| implement | ✅ | mode do user chốt lúc duyệt plan |
| qc | ✅ | DoD = toàn bộ 448+ test xanh + doc_lint exit 0 + phases.md khớp |
| report | ✅ | ≤50 dòng |

Skill sẽ dùng khi build: `skill-creator` (rà hình dạng SKILL.md), `graphify` (rebuild graph cuối turn).

## Nguồn

- https://code.claude.com/docs/en/sub-agents — bảng frontmatter (`model`, `effort`, danh sách trường bị bỏ qua với plugin subagent).
- https://code.claude.com/docs/en/model-config — thứ tự ưu tiên effort; "Skill and subagent frontmatter: set `effort`…".
- https://github.com/anthropics/claude-code/issues/25669, /issues/43083 — Agent tool chưa có tham số `effort` (feature request đang mở).
- Nội bộ: `docs/tdq/research/2026-08-04-workflow-linh-hoat.md` mục A (bảng đọc code).
