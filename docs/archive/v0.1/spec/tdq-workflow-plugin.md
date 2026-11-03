# Spec: TDQWorkflow Plugin cho Claude Code

- **Phiên bản spec**: v0.1.7 — 2026-07-27 (rev bổ sung sau duyệt theo yêu cầu user: tick plan ngay khi xong từng task, không chờ cuối turn; rev: working log về `docs/workinglog/`; mục 9 — Tavily; mục 3.1 — lazy load; approve gate hướng dẫn lệnh duyệt + validate bằng state có detail file; bảo vệ state.json; lane quick có cửa duyệt nhẹ + ghi summary plan vào working log trước implement)
- **Trạng thái**: ĐÃ DUYỆT (user duyệt v0.1.6 — 2026-07-27)
- **Nguồn**: `idea.md` + interview 2026-07-27 + research (docs chính thức Claude Code v2.1+, Superpowers, BMAD, Spec Kit, Graphify)

---

## 1. Ý tưởng & mục tiêu

Đóng gói toàn bộ quy trình làm việc trong `idea.md` thành **một Claude Code plugin chuẩn** tên `tdq-workflow`, để mọi task được làm đúng ngay từ những lần implement đầu, giảm tối đa vòng "làm rồi sửa".

Nguyên tắc thiết kế rút từ research:
- Instruction dài trong CLAUDE.md bị **drift** (model đọc nhưng không tuân thủ ổn định khi context đầy) → phần bắt buộc phải enforce bằng **hooks** (deterministic), phần phương pháp đưa vào **skills** nhỏ theo từng phase.
- Điểm duyệt (approval) phải **deterministic từ phía người dùng** (lệnh user gõ tay), không tin vào việc model tự ghi nhận "user đã duyệt".
- Mô hình tham chiếu: Superpowers (spec → plan → subagent implement, adversarial self-review) + BMAD (roleplay chuyên gia theo phase) — chắt lọc, không copy.

## 2. Scope

### 2.1 Trong scope (MVP)
1. Plugin `tdq-workflow` hoàn chỉnh, chạy được trong repo này qua `claude --plugin-dir .`:
   - 10 skills (7 phase + approve + status + quy ước nền).
   - 3 agents (implementer, reviewer, qc-tester).
   - Bộ hooks enforce (gate + remind) với script Python 3 (stdlib only).
2. Hệ thống doc chuẩn hóa (một cây `docs/` duy nhất — hết lẫn `doc/` và `docs/`).
3. README.md (tiếng Việt): cài đặt, sử dụng, test.
4. `docs/notes/user-level-install.md`: hướng dẫn install user-level + chỉnh `~/.claude/CLAUDE.md` cho tương thích (tránh rule trùng lặp). **Không tự install vào user-level.**
5. Test suite cho hooks (red/green) + smoke test end-to-end.

### 2.2 Ngoài scope (MVP)
- Publish marketplace công khai; auto-install graphify không hỏi; MCP server riêng; hỗ trợ ngoài Claude Code (Codex/Cursor); enforce chất lượng *nội dung* spec bằng hook (chỉ enforce được trình tự và hành vi tool).

## 3. Kiến trúc plugin

```
TDQWorkflow/
├── .claude-plugin/plugin.json        # name: tdq-workflow, v0.1.0
├── skills/
│   ├── tdq-start/SKILL.md            # Intake: nhận yêu cầu, đề xuất lane, hỏi user
│   ├── tdq-analyze/SKILL.md          # Analysis & Complete yêu cầu (interview loop)
│   ├── tdq-spec/SKILL.md             # Thiết lập spec
│   ├── tdq-plan/SKILL.md             # Thiết lập plan
│   ├── tdq-implement/SKILL.md        # Implement (main-agent | subagent-driven)
│   ├── tdq-qc/SKILL.md               # Quality Check
│   ├── tdq-report/SKILL.md           # Report
│   ├── tdq-approve/SKILL.md          # USER-ONLY: duyệt spec/plan
│   ├── tdq-status/SKILL.md           # USER-ONLY: xem trạng thái workflow
│   └── tdq-conventions/SKILL.md      # Nền: quy ước doc/git/log/research (user-invocable: false)
├── agents/
│   ├── tdq-implementer.md            # Thực thi 1 task của plan (isolation: worktree)
│   ├── tdq-reviewer.md               # Adversarial review spec/plan trước khi trình user
│   └── tdq-qc-tester.md              # QC độc lập theo spec/plan
├── hooks/
│   ├── hooks.json
│   └── scripts/
│       ├── session_start.py          # inject state + check graphify
│       ├── prompt_context.py         # UserPromptSubmit: nhắc phase hiện tại
│       ├── approve_gate.py           # UserPromptExpansion(tdq-approve): set approved
│       ├── edit_gate.py              # PreToolUse Edit|Write|...: chặn code trước duyệt
│       ├── bash_gate.py              # PreToolUse Bash: chặn naming git phạm quy + ghi trực tiếp state.json
│       └── stop_gate.py              # Stop: nhắc working log + graphify + tick plan
├── scripts/tdq_state.py              # helper đọc/ghi state.json
├── tests/                            # test hooks (red/green) + fixture stdin JSON
├── docs/                             # spec/plan/notes/workinglog của chính repo này
└── README.md
```

**Ngôn ngữ**: toàn bộ nội dung skill/agent/hook viết **tiếng Anh** (tuân thủ ổn định, ít token). Mọi output hướng người dùng (câu hỏi interview, spec, plan, report, summary) **bắt buộc tiếng Việt** — ghi rõ trong từng skill.

### 3.1 Lazy load & ngân sách token (bắt buộc)

Cơ chế nền của Claude Code đã lazy sẵn — plugin phải giữ và siết thêm bằng các rule sau:

| Thành phần | Cơ chế load của Claude Code | Rule bắt buộc của plugin |
|---|---|---|
| Skills | Lúc start chỉ nạp name + description; body SKILL.md chỉ nạp khi được gọi | Description ≤ 2 dòng/skill (tổng metadata cả plugin ≤ ~500 token). Body mỗi SKILL.md ≤ 500 dòng. Nội dung dài (template spec/plan, quy tắc Tavily đầy đủ, checklist QC) tách vào `references/*.md` trong thư mục skill — chỉ đọc khi phase đó thật sự cần (progressive disclosure) |
| Hooks | Process ngoài — 0 token khi không output | **Im lặng mặc định**: không liên quan → exit 0, không output. `UserPromptSubmit` (bắn mỗi prompt) chỉ inject ≤ 1 dòng và chỉ khi có request active (lane full, hoặc quick đang chờ duyệt); `SessionStart` inject ≤ 3 dòng; không inject lại thông tin đã có trong context |
| Agents | Chỉ nạp name + description; system prompt nạp khi spawn | Không preload `tdq-conventions` qua `skills:` frontmatter của agent trừ khi agent cần toàn bộ nội dung ngay từ đầu — mặc định chỉ trỏ đường dẫn để tự đọc khi cần |
| Thiết kế phase | — | Tách 10 skill theo phase để **chỉ phase đang chạy chiếm context**; không bao giờ gộp cả workflow vào một file luôn-nạp (vừa chống drift vừa tiết kiệm token) |

- Không dùng dynamic context injection (`` !`cmd` ``) nặng trong SKILL.md; state chỉ đọc qua hook/script khi cần.
- Ngân sách tổng: chi phí context cố định của plugin khi idle (metadata + inject mặc định) **< ~800 token/phiên** — có test đo ở mục 10.

## 4. State machine

File trạng thái per-project: `docs/tdq/state.json`

```json
{
  "schema_version": 1,
  "active_request": "2026-07-27-ten-task",
  "lane": "full",                  // "quick" | "full" | null
  "phase": "spec",                 // idle|analyze|spec|plan|implement|qc|report
  "spec_file": null,               // "docs/tdq/spec/<slug>.md" — đăng ký khi trình spec cho user
  "spec_approved": false,
  "spec_sha256": null,             // hash nội dung file lúc duyệt (detail/audit)
  "spec_approved_at": null,
  "plan_file": null,               // "docs/tdq/plan/<slug>.md" — đăng ký khi trình plan
  "plan_approved": false,
  "plan_sha256": null,
  "plan_approved_at": null,
  "quick_approved": false,         // lane quick: duyệt plan ngắn trình trong chat
  "quick_approved_at": null,
  "implement_mode": null,          // "main" | "subagent"
  "updated_at": "..."
}
```

- Skills cập nhật state qua `scripts/tdq_state.py`.
- **Riêng `spec_approved`/`plan_approved`/`quick_approved` chỉ được set bởi hook `approve_gate.py`** khi user gõ tay `/tdq-workflow:tdq-approve spec|plan|quick` (skill này `disable-model-invocation: true` → model không thể tự gọi). Đây là gate duyệt deterministic.
- **Đăng ký file trước khi mời duyệt**: skill `tdq-spec`/`tdq-plan` phải set `spec_file`/`plan_file` vào state ngay khi trình cho user.
- **Approve validate bằng state** (`approve_gate.py`): khi user gõ lệnh duyệt → check (1) đúng thứ tự: `approve plan` đòi `spec_approved=true` trước; (2) `spec_file`/`plan_file` đã đăng ký, file tồn tại và không rỗng. Pass → set `*_approved=true` + ghi detail (`*_file`, `*_sha256`, `*_approved_at`). Fail → **block expansion**, báo lỗi tiếng Việt ngắn (chưa có gì chờ duyệt / thiếu file / sai thứ tự), state không đổi. Với `approve quick`: đòi `lane="quick"` + có `active_request` đang mở + chưa approved → set `quick_approved=true` + `quick_approved_at` (plan quick nằm trong chat + working log, không cần file); sai lane/không có gì chờ → block như trên.
- **Sau duyệt**: nếu nội dung spec đổi (sha256 lệch) → hook inject cảnh báo "spec đã thay đổi sau khi duyệt — cần trình duyệt lại" (không tự hủy approve). Plan được phép cập nhật tick status + task fix từ QC loop (mục 5.5) — hash plan chỉ là audit lúc duyệt. Riêng lane quick: sau duyệt phải **append summary plan vào working log trước khi sửa file ngoài `docs/**`** — edit_gate enforce (check mtime working log hôm nay > `quick_approved_at`).
- Skill `tdq-approve` có `argument-hint: [spec|plan|quick]` (hiện trong autocomplete); gõ thiếu/sai arg hoặc không có gì đang chờ duyệt → trả lời usage ngắn bằng tiếng Việt cho user, không đổi state.
- **UX duyệt**: tại mọi điểm chờ duyệt, Claude bắt buộc hiển thị khối hướng dẫn tiếng Việt cho user, ví dụ: "➤ Để duyệt: gõ `/tdq-workflow:tdq-approve spec` (hoặc `plan`/`quick` tùy điểm chờ) · Để chỉnh sửa: nhắn góp ý trực tiếp" — không bao giờ để user phải tự nhớ lệnh.

## 5. Workflow 7 bước (chi tiết theo idea.md, đã tinh chỉnh)

### 5.0 Intake — `tdq-start`
- Đọc yêu cầu + repo hiện có (ưu tiên `graphify query` nếu có graph).
- Ghi yêu cầu gốc vào `docs/tdq/requests/YYYY-MM-DD-<slug>.md`.
- **Đề xuất lane kèm summary siêu ngắn** (quick: làm thẳng, vẫn ghi log; full: 6 bước) → **hỏi user chọn** (AskUserQuestion) mỗi lần nhận yêu cầu. Set `lane` theo lựa chọn.
- **Lane quick — vẫn có 1 cửa duyệt nhẹ (bắt buộc)**: phân tích nhanh → trình **ngay trong chat** (không tạo file spec/plan) plan ngắn gọn nhất có thể (≤ 10 dòng): (1) summary việc sẽ làm, (2) file/khu vực sẽ đụng, (3) cách quick validate/test sau khi làm, (4) hướng dẫn duyệt "➤ Để duyệt: gõ `/tdq-workflow:tdq-approve quick` · Góp ý: nhắn trực tiếp" → **chờ user duyệt** (edit_gate chặn code thật cho tới khi duyệt).
- Sau khi duyệt quick: **append summary plan đó vào `docs/workinglog/YYYY-MM-DD.md` trước, rồi mới implement** (gate enforce theo mục 4) → implement end-to-end → chạy quick validate/test đã nêu → báo kết quả ngắn trong chat. Vẫn giữ bash gate (naming git + state.json), graphify update.

### 5.1 Analysis & Complete yêu cầu — `tdq-analyze`
- Roleplay: kiến trúc sư phần mềm + PM + BA + chuyên gia thẩm định yêu cầu (giàu kinh nghiệm, kỹ tính).
- Đọc code/file hiện có; web research đa hướng theo **quy tắc khai thác Tavily (mục 9)** (primary → backup 1 lần khi lỗi → WebSearch phải xin phép; nguồn rõ ràng, không bịa, không lộ API key) để biết yếu tố cần có của MVP loại này.
- Những gì chưa rõ (MVP là gì, use case, tech stack, thư viện, device, ưu tiên, UI/UX + style + wireframe/prototype, chuẩn bị version sau...): **không đoán** — lập danh sách câu hỏi, mỗi câu có option đề xuất + summary siêu ngắn, hỏi qua AskUserQuestion, ghi vào `docs/tdq/questions/<slug>.md`. Recheck bổ sung câu hỏi → loop đến khi đủ.
- Cần model/library → hỏi user có muốn download không. **Cấm placeholder** cho tính năng/model/engine.
- Kết quả research ghi `docs/tdq/research/<slug>.md`; phân tích sâu (DB, kiến trúc, design...) ghi vào `docs/tdq/knowledge/`.

### 5.2 Thiết lập spec — `tdq-spec`
- Roleplay như 5.1. Spec **tiếng Việt**, lưu `docs/tdq/spec/<slug>.md`.
- Nội dung tối thiểu: ý tưởng, scope, tech stack + library, tổ chức, tính năng, design, **MVP test tổng (kèm expect output red/green)**, scope QC/test/validate, cần download/install gì.
- Sản phẩm build ra phải có **log service mặc định bật** (tắt được qua config): log đầy đủ data + timestamp, event-level nếu có UI, phục vụ debug/detect issue; cho phép capture app/web khi cần.
- Subagent `tdq-reviewer` adversarial review spec → tự fix hoặc bổ sung câu hỏi interview.
- Trình user: đường dẫn spec + summary ≤ 50 dòng, **cuối message luôn kèm hướng dẫn duyệt**: "➤ Để duyệt spec: gõ `/tdq-workflow:tdq-approve spec` · Để chỉnh sửa: nhắn góp ý" → chờ duyệt. User bổ sung → quay lại phân tích/update → trình lại (kèm hướng dẫn duyệt như trên). Tuyệt đối không đi tiếp khi chưa duyệt (edit_gate chặn thật).

### 5.3 Thiết lập plan — `tdq-plan`
- Roleplay: chuyên gia đúng lĩnh vực của spec + master prompter, kỹ tính.
- Plan **tiếng Việt**, lưu `docs/tdq/plan/<slug>.md`, phủ 100% spec: mỗi task có hướng dẫn chi tiết, cách validate/QC, output cần đạt, note, **unit test/task test**, checkbox status; cuối plan có MVP test tổng thể.
- Self-review loop + `tdq-reviewer` review đến khi ổn.
- Trình user: đường dẫn + summary ≤ 100 dòng, **cuối message luôn kèm hướng dẫn duyệt**: "➤ Để duyệt plan: gõ `/tdq-workflow:tdq-approve plan` · Để chỉnh sửa: nhắn góp ý" → chờ duyệt. Sau duyệt: hỏi user chọn **sub-agent driven** hay **main-agent implement**, note vào plan + state.

### 5.4 Implement — `tdq-implement`
- Theo mode đã chọn:
  - **subagent-driven**: main agent điều phối; mỗi task → 1 `tdq-implementer` (worktree riêng, roleplay + prompt chi tiết theo task); xong → main agent check, pass mới merge về repo; nhớ kiểm tra merge worktree.
  - **main-agent**: main agent tự làm từng task theo plan.
- Bắt buộc: tick status vào plan **NGAY khi từng task chuyển trạng thái (doing/done) — tick liền sau khi task xong, không gom chờ cuối turn**; unit test của task fail → fix đến pass; **không dừng giữa chừng — end-to-end trong 1 turn**; đang chờ subagent thì chờ/thiết lập trigger tiếp tục, không ngắt turn. Không chạy MVP test tổng ở bước này.
- Git: tên branch/commit/worktree không bắt đầu bằng `claude|antigravity|gemini|codex`; không chèn "generated with claude/..." vào commit (hook enforce).

### 5.5 Quality Check — `tdq-qc`
- Roleplay developer + QC chuyên nghiệp, kỹ tính; dùng agent `tdq-qc-tester` độc lập.
- Check report test từng task (nghi ngờ → test lại) + chạy MVP test tổng theo spec/plan.
- Bug → ghi `docs/tdq/qc/<slug>.md` (issue gì, nguyên nhân) → quay lại `tdq-plan` bổ sung task fix (**không cần duyệt lại**, giữ implement mode cũ) → implement fix → QC lại. Loop đến pass hết.

### 5.6 Report — `tdq-report`
- Tổng hợp spec/plan/QC: tiến độ task, kết quả QC, output MVP, cách chạy project, port, account mặc định (nếu có). ≤ 50 dòng, tiếng Việt, lưu `docs/tdq/reports/<slug>.md` + trình bày trong chat.

## 6. Hooks (enforce — hybrid gate)

| # | Event | Hành vi |
|---|-------|---------|
| 1 | `SessionStart` | Inject tóm tắt `state.json` (đang ở phase nào, chờ gì) + check graphify đã cài chưa (thiếu → nhắc, đề nghị cài, không tự cài) |
| 2 | `UserPromptSubmit` | Khi có request đang mở (lane full, hoặc quick đang chờ duyệt): inject 1 dòng nhắc phase hiện tại + việc phải làm tiếp; nếu đang chờ duyệt spec/plan/quick thì dòng nhắc kèm lệnh duyệt chính xác để Claude hiển thị cho user |
| 3 | `UserPromptExpansion` matcher `tdq-approve` | Validate bằng state (đúng thứ tự spec→plan; `spec_file`/`plan_file` đã đăng ký + file tồn tại, không rỗng; `quick` đòi lane quick + request đang mở) → set approved + ghi detail (path, sha256, timestamp; quick: timestamp); fail → block expansion + báo lỗi VI, state không đổi (deterministic, chỉ khi user gõ tay) |
| 4 | `PreToolUse` `Edit\|Write\|MultiEdit\|NotebookEdit` | Lane full + chưa duyệt spec/plan + file ngoài `docs/**` → **deny**, reason đồng thời remind Claude: hoàn thành spec/plan, trình user và **hiển thị cho user lệnh duyệt chính xác** "gõ `/tdq-workflow:tdq-approve spec|plan` để duyệt, hoặc nhắn góp ý" (block + remind + hướng dẫn duyệt). Lane quick: chưa `quick_approved` + file ngoài `docs/**` → **deny** + remind trình plan ngắn trong chat kèm lệnh `/tdq-workflow:tdq-approve quick`; đã duyệt quick nhưng working log hôm nay chưa cập nhật sau lúc duyệt (mtime ≤ `quick_approved_at`) → **deny** nhắc append summary plan vào working log trước khi implement. Ghi vào `docs/**` luôn được phép — **ngoại lệ duy nhất `docs/tdq/state.json`: deny Edit/Write trực tiếp mọi lúc** (state chỉ đổi qua helper script/hook). Nếu spec đã duyệt nhưng sha256 lệch → inject cảnh báo cần trình duyệt lại |
| 5 | `PreToolUse` `Bash` | (a) Chặn `git branch/checkout -b/commit/worktree` có tên bắt đầu `claude\|antigravity\|gemini\|codex` hoặc commit message chứa "generated with claude/gemini/codex"; (b) chặn lệnh Bash ghi trực tiếp vào `docs/tdq/state.json` (redirect `>`/`>>`, `tee`, `sed -i`, `mv/cp` đè...) — đọc (`cat`/`jq`) vẫn được → deny + reason |
| 6 | `Stop` | Turn có thay đổi repo mà chưa append working log hôm nay / chưa graphify update / plan chưa tick → block 1 lần với reason nhắc làm; tối đa 1 block/turn (chống loop) |

## 7. Hệ thống doc chuẩn hóa (một layer đáng tin)

```
docs/
├── tdq/
│   ├── state.json
│   ├── requests/    # yêu cầu gốc mỗi task
│   ├── questions/   # interview Q&A
│   ├── research/    # kết quả web research (có nguồn)
│   ├── knowledge/   # phân tích sâu: DB, kiến trúc, design...
│   ├── spec/
│   ├── plan/
│   ├── qc/          # bug log + QC report
│   └── reports/
└── workinglog/YYYY-MM-DD.md   # working log theo ngày
```

Working log: `docs/workinglog/YYYY-MM-DD.md` — append mỗi turn có thay đổi repo (Stop hook nhắc). Khác convention user-level cũ (`docs/superpowers/workinglog/`); note install user-level sẽ hướng dẫn cập nhật rule này cho khớp.

## 8. Graphify

- Cài qua package (`uv tool install graphifyy` hoặc pip), **không clone repo**.
- `SessionStart` check; thiếu → hỏi user cho phép cài.
- Sau turn đổi code: Stop hook nhắc chạy graphify update. Skills ưu tiên `graphify query` thay cho grep khi cần hiểu tổng thể (graphify tự có hook nudge riêng — plugin không làm trùng).

## 9. Quy tắc khai thác Tavily (bake vào `tdq-conventions`, áp dụng cho mọi bước research)

Nguồn: Tavily official docs — Agents guide + Best Practices (Search/Extract/Crawl/Research) + schema 5 tool MCP thực tế của server `tavily-primary`/`tavily-backup`.

### 9.1 Chọn đúng tool theo nhu cầu

| Nhu cầu | Tool |
|---|---|
| Chưa biết nguồn, cần thông tin web mới nhất | `tavily_search` — luôn bắt đầu từ đây |
| Đã có URL, cần full nội dung sạch | `tavily_extract` (tối đa 20 URL/call) |
| Tìm đúng trang trong 1 site trước khi lấy nội dung | `tavily_map` → rồi extract (nhanh/rẻ hơn crawl) |
| Lấy nội dung nhiều trang của 1 site (docs, ingest kiến thức) | `tavily_crawl` |
| Chủ đề rộng nhiều nhánh, cần tổng hợp có trích nguồn end-to-end | `tavily_research` (`model`: mini = hẹp, pro = rộng, auto mặc định; ~20 req/phút) |

### 9.2 Search hiệu quả

- Query **< 400 ký tự**, kiểu search-engine, mỗi query 1 chủ đề; vấn đề phức tạp → **tách nhiều sub-query** (khớp rule "search đa hướng"); dedupe kết quả theo URL trước khi tổng hợp.
- `search_depth`: `advanced` khi khám phá nguồn/so sánh/cần độ tin cao; `basic` tra cứu nhanh; `fast`/`ultra-fast` chỉ khi cần latency thấp.
- `max_results`: 5 (câu hỏi tập trung) / 8–10 (research rộng) — đặt cao hơn dễ lẫn kết quả chất lượng thấp.
- Độ tin cậy nguồn: `include_domains` (docs chính thức, .edu, nguồn uy tín) / `exclude_domains` (content farm) — giữ danh sách ngắn, đúng mục tiêu.
- Độ mới: `time_range` hoặc `start_date`/`end_date` cho chủ đề biến động nhanh (version, release, giá).
- **Không** bật `include_raw_content` — dùng pattern 2 bước ở 9.3; dùng trường `score` (0–1) của kết quả để chọn lọc nguồn tốt trước khi extract.

### 9.3 Pattern chuẩn (grounded + tiết kiệm token)

1. **Search → Extract**: search tìm nguồn → lọc URL theo `score`/domain tin cậy → `tavily_extract` các URL tốt nhất, kèm `query` để rerank đúng đoạn liên quan; `extract_depth=advanced` cho trang có bảng/JS/khó extract.
2. **Map → Extract**: cần đúng 1–2 trang trong docs site → `tavily_map` (lọc `select_paths` regex) → extract trang trúng đích.
3. **Crawl có kiểm soát**: cần cả cụm trang → `instructions` mô tả bằng ngôn ngữ tự nhiên trang cần lấy + `select_paths`/`select_domains` + bắt đầu `max_depth`/`limit` nhỏ rồi tăng dần nếu thiếu.
4. **Research prompt**: 1 câu task rõ ràng + context thiết yếu + format output mong muốn — không dump background thừa.
- Kết quả chốt ghi `docs/tdq/research/<slug>.md` kèm URL nguồn + ngày truy cập (đáp ứng rule "mọi thông tin có căn cứ").

### 9.4 Failover (giữ nguyên rule hiện có)

- `tavily-primary` → chỉ khi lỗi kết nối/xác thực/timeout/quota/tool → `tavily-backup` đúng 1 lần → `WebSearch` phải nêu lỗi + xin phép user. Kết quả rỗng hợp lệ ≠ lỗi → tinh chỉnh query trên primary. Không bao giờ lộ API key.

## 10. QC / test / validate cho chính plugin (checklist rule 9)

1. `claude plugin validate . --strict` pass.
2. **Unit test hooks (red/green)**: feed stdin JSON fixture cho từng script → expect đúng allow/deny/additionalContext. Ví dụ: red = Edit `src/a.py` khi `spec_approved=false` → deny; green = Edit `docs/tdq/spec/x.md` cùng state → allow; red = Edit/Write hoặc Bash ghi `docs/tdq/state.json` → deny; red = `/tdq-approve plan` khi `spec_approved=false` hoặc `plan_file` chưa tồn tại → block, state không đổi; green = `/tdq-approve spec` khi `spec_file` hợp lệ → `spec_approved=true` + đủ detail (path, sha256, timestamp); lane quick: red = Edit `src/a.py` khi `quick_approved=false` → deny, red = đã duyệt quick nhưng working log chưa cập nhật sau duyệt → deny, green = duyệt + log đã append → allow, red = `/tdq-approve quick` khi `lane="full"` → block. Tương tự cho bash-gate, stop.
3. **Smoke test e2e**: chạy `claude --plugin-dir .` với 1 task mẫu trong project test tạm, chạy cả 2 lane (full + quick) → verify: intake hỏi lane, gate chặn code trước duyệt, `/tdq-approve` mở gate (quick: bắt ghi summary plan vào working log trước implement), log được ghi, report ra đúng chỗ.
4. **Token budget check (mục 3.1)**: đếm token metadata (description các skill/agent) + inject mặc định của hooks < ~800/phiên idle; test hook im lặng: fixture "prompt thường, không có request active" → hook không output gì (0 token).
5. Kết quả test ghi vào `docs/tdq/qc/`.

**Cần download/install**: không có gì bắt buộc (hook dùng Python 3 stdlib có sẵn trên macOS); graphify là tùy chọn, hỏi trước khi cài. Không cần model.

## 11. Deliverables (Expect_Output)

1. Plugin `tdq-workflow` v0.1.0 hoàn chỉnh trong repo này (bộ skill + rule + hook đảm bảo workflow).
2. README.md (VI).
3. `docs/notes/user-level-install.md` — note chỉnh instruction user-level + cách install user scope (không tự install); gồm hướng dẫn đổi rule working log user-level từ `docs/superpowers/workinglog/` → `docs/workinglog/`.
4. Test suite + kết quả QC.

## 12. Giới hạn & rủi ro (minh bạch)

- Hook enforce được **trình tự và hành vi tool**, không enforce được chất lượng nội dung spec/plan — phần đó dựa vào skill + adversarial review.
- Điểm duyệt đã deterministic (`/tdq-approve` model không gọi được, validate bằng state + detail file) và `state.json` được bảo vệ 2 lớp (deny Edit/Write trực tiếp; chặn pattern Bash ghi thường gặp). Rủi ro còn lại: Bash obfuscated vẫn có thể lách về lý thuyết — chấp nhận ở v0.1, ghi nhận theo dõi. Gate "log trước implement" ở lane quick chỉ check mtime (working log được cập nhật sau lúc duyệt), không kiểm nội dung entry — chấp nhận.
- Stop hook phải giới hạn 1 block/turn để tránh vòng lặp treo phiên.
