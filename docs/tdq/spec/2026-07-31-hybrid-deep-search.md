# SPEC — Hybrid deep search: Claude scout ∥ agy tổng quát → agy đào sâu

Ngày: 2026-07-31 · Bản: 1.1 (sau review) · Request: ../requests/2026-07-31-hybrid-deep-search.md · Lane: full
Trạng thái: ĐÃ DUYỆT (user "duyệt spec", 2026-07-31 16:21 +07)

## 1. Mục tiêu & phạm vi

- Mục tiêu: nâng deep search (0.5.0) thành flow hybrid 2 phase — phase 1 gồm
  1 agent Claude scout chạy song song 1 agent agy tổng quát để nắm hướng;
  phase 2 gồm ≤3 agent agy đào sâu theo route Claude tổng hợp; mọi findings
  (cả 2 phase) merge chung. Default model agy đổi thành `gemini-3.6-flash-medium`.
  Đích đo được: 1 run E2E thật ra `merged.json` chứa findings từ đủ 3 loại
  slot (scout, agy tổng quát, agy sâu), URL sống 100%.
- Trong phạm vi:
  - `scripts/search_task.py`: đổi default model, thêm `--start-agent` cho `split`.
  - Agent mới `agents/search-scout.md` (Claude + Tavily, vỏ mỏng như search-runner).
  - Viết lại flow trong `skills/tdq-conventions/references/deep-search.md`.
  - Cập nhật khớp: `tavily.md`, `portable/workflow/06-deep-search.md`,
    CLAUDE.md §10 (1 dòng), CHANGELOG + plugin.json 0.6.0.
  - Unit test mới + cập nhật; E2E hybrid 1 topic thật.
- NGOÀI phạm vi:
  - Không đổi schema report (`search_report_schema.json`), luật trigger ≥2 dấu
    hiệu, cap env `TDQ_SEARCH_*`, logic retry/URL-alive/dedup/rank của wrapper.
  - Không thêm engine mới, không đường tắt bỏ phase 1 (user đã loại).
  - Không sửa mode external / external_task.py.

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Default model medium + escalation giữ high; docstring/"Cách dùng" đồng bộ | `scripts/search_task.py` | unit test default/escalation xanh; log run thật chứa `gemini-3.6-flash-medium`; grep docstring không còn tả sai default |
| 2 | `split --start-agent N` (default 1); USAGE cập nhật | `scripts/search_task.py` | unit test: `--start-agent 3` với 3 route → agent 3,4,5; thiếu flag → 1,2,3; USAGE chứa `--start-agent` |
| 3 | Agent scout | `agents/search-scout.md` | test khuôn (needles) xanh; doc_lint exit 0 |
| 4 | Flow hybrid trong doc quy ước | `skills/tdq-conventions/references/deep-search.md` | doc_lint exit 0; test needles flow (2 phase, slot 1/2, start-agent 3, merge cuối) |
| 5 | Docs khớp: tavily.md, portable 06, CLAUDE.md §10 | các file tương ứng | test portable_sync + docs_consistency xanh |
| 6 | Version 0.6.0 | `.claude-plugin/plugin.json`, `CHANGELOG.md` | test changelog↔plugin.json xanh |
| 7 | Run E2E hybrid thật | `docs/tdq/research/search/<run-id>/` | mỗi loại slot có ≥1 finding trong `agent-<k>.json` (đo TRƯỚC merge), URL sống 100%, spot-check 2 nguồn top khớp, token Claude ghi vào report |

## 3. Cách tiếp cận & lý do

- Chọn: pattern orchestrator-worker (Claude chính là orchestrator) với slot cố định:
  - Phase 1 (song song): agent **1** = search-runner (agy) route
    `tổng quát: <chủ đề>`; agent **2** = search-scout (Claude + tavily-primary)
    route `scout: <chủ đề>` — prefix route là QUY ƯỚC nhận diện slot.
    Slot phase 1 gán cố định KHÔNG qua `split` — đây là ngoại lệ có chủ đích
    của luật "code quyết, không tự chia" và phải ghi rõ trong deep-search.md.
  - Format file: cả hai ghi `agent-<k>.json` theo **format file agent** (như
    output `cmd_run`: `agent`, `routes`, `routes_failed`, `findings[]` có thêm
    `url_alive`, `not_found`, `queries_used`) — KHÔNG phải schema report thô
    (schema `additionalProperties:false` không có `url_alive`; merge rank theo
    `url_alive` nên thiếu là bị rank như URL chết). Scout TRẢ THÊM trong final
    message: 3–5 route gợi ý kèm keyword/seed URL.
  - Tổng hợp: orchestrator ĐỌC tín hiệu (route gợi ý scout + queries_used/
    findings của agent 1) để chốt ≤3 route sâu — đọc-để-điều-phối được phép,
    còn merge findings CHỈ qua lệnh `merge` một lần cuối (doc mới phải phân
    biệt 2 việc này). Route chốt ghi thành mục `## Hướng từ phase 1` nối vào
    brief gốc, lưu `brief-phase2.md` trong run-dir.
  - Phase 2: `split --routes "<r…>" --start-agent 3` → agent 3..5 = search-runner
    (agy, brief-phase2). Xong hết → `merge <run-dir>` một lần duy nhất.
  - Degrade phase 1 (3 nhánh, doc phải mô tả đủ): (a) agent 1 engine-failed →
    tiếp tục bằng scout; (b) scout hỏng — định nghĩa: không có `agent-2.json`
    parse được với đủ trường bắt buộc sau khi agent kết thúc → tiếp tục bằng
    agent 1; (c) cả hai hỏng → dừng run, fallback Tavily theo luật cũ. Mọi
    nhánh degrade ghi 1 dòng vào run.log/report. Phase 2 giữ luật
    engine-failed ≥2 → Tavily.
- Vì: benchmark 2026-07-31 (Run A agy thuần 93k token nhưng sót vendor; Run B
  Claude thuần phủ đủ nhưng 189k token ≈ 2×) — hybrid lấy độ phủ của 2 lớp
  bao quát độc lập với chi phí giữa 2 cực; khớp pattern orchestrator-worker
  của Anthropic (nguồn: research/<slug>.md).
- Đã loại: 3 scout Claude (user thu về 1, 16:01) · đường tắt bỏ phase 1 (user
  loại, 16:07) · escalation 3 bậc/thêm pro (tốn quota, chưa có bằng chứng cần) ·
  đánh số động cho phase 1 (slot cố định 1/2 đơn giản, không đụng merge).

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake, tdq-spec, tdq-plan, tdq-build, tdq-status, tdq-conventions | plugin:tdq-workflow | NỀN | workflow đang chạy |
| tavily-search | plugin:tavily | DÙNG | scout phase 1 search rộng (đầu ra #3, #7) |
| tavily-extract | plugin:tavily | DÙNG | scout lấy quote + orchestrator spot-check (đầu ra #7) |
| tavily-best-practices | plugin:tavily | DÙNG | tham chiếu khi viết luật scout trong deep-search.md (đầu ra #4) |
| tavily-cli, tavily-crawl, tavily-map, tavily-research, tavily-dynamic-search | plugin:tavily | KHÔNG | spec §3 đã chọn cách khác tốt hơn (scout chỉ dùng tavily-search/extract MCP) |
| graphify | user | DÙNG | cuối turn build chạy `graphify extract . --code-only` |
| skill-creator, skill-development | plugin | KHÔNG | khác lĩnh vực |
| plugin-structure, plugin-settings, agent-development, command-development, hook-development, mcp-integration | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| claude-md-improver, frontend-design, playground, build-mcp-app, build-mcp-server, build-mcpb, writing-hookify-rules, remember, dataviz, artifact-design, artifact-capabilities, update-config, keybindings-help, claude-api, run, loop, schedule | plugin/built-in | KHÔNG | khác lĩnh vực |
| simplify, security-review, code-review | built-in | KHÔNG | user đã cấm |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: giữ `run.log`/`agent-<k>.log` ISO timestamp; scout
  cũng ghi log hành trình vào `agent-2.log` (query, URL check, số findings);
  tắt qua `TDQ_SEARCH_LOG=0` — với wrapper là enforce bằng code (bắt buộc),
  với scout là best-effort qua khuôn agent (kiểm bằng needles, không unit).
- Không placeholder/TODO stub; findings scout phải qua cùng chuẩn schema +
  URL-alive tự check bằng curl (như Run B đã làm).
- Mỗi thành phần có unit test riêng, chạy bằng `cd tests && python3 -m unittest discover .`.

## 5. Ràng buộc & rủi ro

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Agent `search-scout` mới không nạp vào phiên hiện tại (cache định nghĩa) | Trigger qua agent type mới chỉ test được sau reload | E2E dùng general-purpose + đúng prompt thân agent; mục trigger ghi PENDING reload (tiền lệ 0.5.0) |
| Wall time 2 phase ~7–8 phút | Chậm hơn flow cũ ~2× | Chấp nhận (user chốt luôn 2 phase); trong phase luôn song song |
| Scout route kém → phase 2 đào sai hướng | Kết quả cuối thiếu | Orchestrator gộp thêm tín hiệu agent 1; phase 2 vẫn nhận FULL brief gốc |
| Trùng lặp findings giữa 2 lớp bao quát | Phí quota Gemini | Dedup URL chuẩn hoá đã có trong merge; chấp nhận 40–70% trùng ở lớp tổng quát |
| flash-medium chậm/tốn hơn flash-low | Run dài hơn, quota Gemini tốn hơn | User chốt; timeout 540s/call giữ nguyên, escalation chỉ 1 bậc |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Unit suite toàn repo | `cd tests && python3 -m unittest discover .` | OK, 0 fail; ≥6 test mới (default model, escalation, start-agent ×2, khuôn scout, khuôn deep-search hybrid) |
| Q2 | Doc lint + pair | `doc_lint.py` các file sửa; `--pair spec plan` | exit 0 |
| Q3 | E2E hybrid thật 1 topic | chạy đủ 2 phase → merge | mỗi loại slot ≥1 finding trong `agent-<k>.json` TRƯỚC merge (slot not_found → điều tra + rerun 1 lần, vẫn rỗng → FAIL); URL sống 100%; spot-check 2 nguồn top khớp; token Claude từng agent ghi vào report, tổng ≤250k (mốc so sánh: Run A 93.1k / Run B 189.4k) |
| Q4 | Default model medium | grep `agent-*.log` của run Q3 | mọi call attempt đầu dùng `gemini-3.6-flash-medium` |
| Q5 | Escalation medium→high | unit `RetryEscalationTest` cập nhật | retry dùng `gemini-3.6-flash-high`, ≤2 retry giữ nguyên |
| Q6 | Degrade phase 1 | (a) giả lập agent 1 engine-failed (slug sai) trong run nháp; (b)+(c) needles trên deep-search.md | (a) flow vẫn ra route + kết quả từ scout, có dòng degrade trong run.log/report; (b)(c) doc mô tả đủ 3 nhánh + định nghĩa scout-failed, test needles xanh |
| Q7 | Docs + version khớp | test docs_consistency + portable_sync; grep plugin.json | 0.6.0 nhất quán, portable ≤10 dòng README giữ luật |
| Q8 | Log service | đọc log run Q3; run nháp `TDQ_SEARCH_LOG=0` | log đủ trường ISO; LOG=0 không sinh agent log |

DoD: Q1–Q8 PASS; đầu ra #1–#7 đều có bằng chứng; report ≤50 dòng; working log
ghi đủ; trigger qua agent type `search-scout` được phép PENDING reload (như 0.5.0).

## 7. Câu hỏi còn mở

(rỗng)
