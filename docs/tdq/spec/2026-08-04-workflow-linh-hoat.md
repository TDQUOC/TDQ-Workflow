# SPEC — TDQ workflow linh hoạt & bớt ma sát

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-08-04 · Bản: 1.0 · Request: ../requests/2026-08-04-workflow-linh-hoat.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi

- **Mục tiêu:** giảm số turn của lane full từ 4 lượt duyệt/chờ xuống 2 (duyệt spec, duyệt plan+mode), bỏ bước review tự động sau spec/plan, cho phép chọn model/effort cho từng sub-agent, và thêm bước quyết lộ trình để workflow tự co giãn theo task. Đo bằng: §6.
- **Trong phạm vi:**
  - `skills/tdq-{intake,spec,plan,build,conventions}/SKILL.md` + các `references/` liên quan.
  - `scripts/tdq_state.py` — chỉ hằng `PHASE_TABLE` (văn bản `action`/`checklist`/`forbidden`/`done_when`). KHÔNG đổi schema state.
  - `skills/tdq-conventions/references/phases.md` — sinh lại bằng `tdq_state.py phases-doc`.
  - Frontmatter 7 file trong `agents/` — thêm `model` + `effort`.
  - `portable/workflow/0{1..4}-*.md`, `portable/workflow/phases.md`, `portable/AGENTS.md` — sync.
  - `~/.claude/CLAUDE.md` mục 9 — sửa các luật đã đổi.
  - Test: cập nhật/bổ sung trong `tests/`.
- **NGOÀI phạm vi:**
  - Đổi schema `docs/tdq/state.json` (không thêm trường `route`) — D6.
  - Xoá agent `tdq-reviewer` (giữ nguyên file, chỉ bỏ gọi mặc định) — D1.
  - Đổi logic chặn của 3 hook (`prompt_context.py`, `bash_gate.py`, `stop_gate.py`): research §A xác nhận hook hiện tại đã tương thích với việc gộp turn; chỉ sửa nếu QC phát hiện lệch.
  - Mode external, deep-search, `external_task.py`, `search_task.py` — không đụng.

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Bỏ gọi mặc định `tdq-reviewer`, giữ 1 dòng "gọi tay khi user yêu cầu" | `skills/tdq-spec/SKILL.md` bước 2, `skills/tdq-plan/SKILL.md` bước 3 | `grep -c "tdq-reviewer" skills/tdq-spec/SKILL.md skills/tdq-plan/SKILL.md` — mỗi file đúng 1 lần, và không còn từ "gọi agent `tdq-reviewer`" ở dạng bắt buộc |
| 2 | Bỏ luật "spec và plan khác turn"; sau `approve spec` → viết plan NGAY cùng turn | `skills/tdq-spec/SKILL.md` (dòng 9 + "Bước kế tiếp"), `PHASE_TABLE["spec"]["forbidden"]` | `grep -L "turn mới" skills/tdq-spec/SKILL.md` khớp; `python3 -c` đọc `PHASE_TABLE["spec"]["forbidden"]` không chứa "cùng turn với spec" |
| 3 | Bỏ bước hỏi mode riêng; mode do Claude ĐỀ XUẤT trong plan, user chốt lúc duyệt | `skills/tdq-plan/SKILL.md` bước 1, `PHASE_TABLE["plan"]["checklist"]` | bước 1 của tdq-plan không còn câu "HỎI user chọn mode … Chờ user trả lời"; checklist[0] của phase `plan` là "Đề xuất mode …" |
| 4 | Sau `approve plan --mode X` → build NGAY cùng turn | `skills/tdq-plan/SKILL.md` mục "Bước kế tiếp", `skills/tdq-build/SKILL.md` Luật cứng | không còn chữ "turn mới"/"turn tiếp theo" trong 2 file (`grep`) |
| 5 | Luật hỏi: giữ AskUserQuestion + BẮT BUỘC câu cuối "Bạn muốn bổ sung thêm gì không?" có phương án mở | `skills/tdq-intake/references/interview.md` mục "Hỏi thế nào" | file chứa nguyên văn chuỗi `Bạn muốn bổ sung thêm gì không?`; test kiểm chuỗi này tồn tại |
| 6 | Lane quick mới: có web search + phân tích + interview khi có ẩn số; **một file mini-spec/plan gộp**, một lần duyệt | `skills/tdq-intake/SKILL.md` Phần C, `PHASE_TABLE["quick"]` | Phần C có bước research và bước interview có điều kiện; checklist phase `quick` nêu file `docs/tdq/plan/<slug>.md` |
| 7 | Bước quyết lộ trình: mục `## Lộ trình` trong knowledge + tóm tắt trong spec, duyệt chung với spec | `skills/tdq-intake/SKILL.md` Phần B bước 5/6, `skills/tdq-spec/SKILL.md` bước 1, `spec-template.md` | `spec-template.md` có mục Lộ trình; intake Phần B có bước ghi `## Lộ trình` |
| 8 | Heuristic chọn model/effort cho sub-agent | `skills/tdq-conventions/references/subagent-tuning.md` (file mới) + 1 dòng trỏ tới nó trong `tdq-conventions/SKILL.md` | file tồn tại, có bảng vai→model→effort và luật override qua tham số `model` của Agent tool |
| 9 | Frontmatter 7 agent có `model` + `effort` | `agents/*.md` | test mới đọc frontmatter 7 file, khẳng định có cả 2 trường và giá trị nằm trong tập hợp lệ |
| 10 | `phases.md` sinh lại khớp `PHASE_TABLE` | `skills/tdq-conventions/references/phases.md`, `portable/workflow/phases.md` | `tests/test_phase_table.py` xanh |
| 11 | Bản portable khớp bản skill | `portable/workflow/0{1..4}-*.md`, `portable/AGENTS.md` | `tests/test_portable_sync.py` xanh |
| 12 | `~/.claude/CLAUDE.md` mục 9 khớp luật mới | `~/.claude/CLAUDE.md` | mục 9 không còn câu "Spec và plan không lập trong cùng một turn"; có câu về gộp gate + câu hỏi mở |

## 3. Cách tiếp cận & lý do

- **Chọn:** sửa **văn bản luật** (5 SKILL.md + `PHASE_TABLE` + references + portable + CLAUDE.md) và **frontmatter agent**; giữ nguyên schema state và logic chặn của hook.
- **Vì:** research §A cho thấy rào "phải sang turn mới" nằm hoàn toàn ở văn bản skill, không ở hook — `prompt_context.py` tính `pending` theo từng prompt (mỗi lần duyệt vẫn là một prompt riêng), còn `bash_gate.NEXT_PHASE_TARGET` cho phép `approve spec` rồi `set phase=plan` trong cùng turn. Bộ này đang có 448 test xanh; đổi văn bản là đường ít rủi ro nhất mà vẫn đạt đủ 6 yêu cầu.
- **Đã loại:**
  - Thêm trường `route` vào state (schema v3→v4) — vì Q9=a: kéo theo migration + sửa nhiều test, lợi ích chỉ là hook nhắc đúng bước.
  - Xoá hẳn agent `tdq-reviewer` — vì Q1=1 (giữ để gọi tay).
  - Bỏ lane, một luồng duy nhất tự chọn độ nặng — vì Q4=1.
  - Nhân đôi agent thành biến thể nhẹ/nặng để đổi `effort` động — vì Q8=a: Agent tool chưa có tham số `effort` (github.com/anthropics/claude-code/issues/43083), nhân đôi file dễ lệch nội dung.

## 3b. Năng lực & công cụ

Chép từ `knowledge/2026-08-04-workflow-linh-hoat.md` mục "Năng lực dùng được".

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake, tdq-spec, tdq-plan, tdq-build, tdq-conventions, tdq-status | plugin:tdq-workflow | NỀN | chính workflow đang chạy — đồng thời là đối tượng bị sửa |
| skill-creator | plugin:skill-creator | DÙNG | rà hình dạng 5 SKILL.md sau khi sửa (đầu ra #1–#7) |
| tavily-search | plugin:tavily | DÙNG | đã dùng ở phase analyze xác minh trường `effort`/`model` (đầu ra #8, #9) |
| update-config | built-in | DÙNG | chỉnh `~/.claude/settings.json` nếu QC phát hiện hook cần cấu hình lại |
| graphify | user | DÙNG | rebuild code graph cuối turn build |
| plugin-dev:agent-development | plugin:plugin-dev | KHÔNG | thiếu quyền/công cụ skill đó cần |
| claude-md-improver, revise-claude-md | plugin:claude-md-management | KHÔNG | thiếu quyền/công cụ skill đó cần |
| plugin-structure, plugin-settings, command-development, hook-development, skill-development | plugin:plugin-dev | KHÔNG | thiếu quyền/công cụ skill đó cần |
| dataviz, artifact-design, artifact-diagramming, artifact-capabilities, frontend-design, playground | built-in | KHÔNG | khác lĩnh vực |
| build-mcp-app, build-mcp-server, build-mcpb, mcp-integration | plugin:mcp-server-dev, plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| writing-hookify-rules, hookify:configure, hookify:hookify, hookify:list, hookify:help | plugin:hookify | KHÔNG | khác lĩnh vực |
| remember, remember:doctor | plugin:remember | KHÔNG | khác lĩnh vực |
| tavily-crawl, tavily-map, tavily-extract, tavily-research, tavily-cli, tavily-best-practices, tavily-dynamic-search | plugin:tavily | KHÔNG | spec §3 đã chọn cách khác tốt hơn — tavily-search đã đủ |
| feature-dev, code-review, security-review, simplify, review, init, run | built-in | KHÔNG | khác lĩnh vực |
| claude-api, keybindings-help, schedule, loop, fewer-permission-prompts | built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- **Log service:** sản phẩm ở đây là doc + hằng Python, không có runtime mới. Log hiện có (`tdq_state._info/_warn`, `docs/tdq/external/<slug>/run.log`, sổ turn `.tdq-turn.jsonl`) giữ nguyên, không tắt, không giảm chi tiết. Không thêm service log mới vì không có tiến trình mới nào chạy.
- Không placeholder, không TODO stub trong SKILL.md/`PHASE_TABLE`.
- Mỗi đầu ra ở §2 có ít nhất một test chạy được bằng một lệnh (`python3 -m unittest`).
- Mọi thay đổi bước đánh số ở `skills/tdq-{intake,spec,plan,build}` phải làm SONG SONG ở `portable/workflow/` trong cùng task.

## 5. Ràng buộc & rủi ro

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Gộp turn spec→plan làm mất "cửa sổ dừng" để user đổi hướng trước khi tốn công lập plan | Plan lập ra có thể phải bỏ nếu user đổi ý sau khi thấy plan | Giữ nguyên 2 lần duyệt (Q3=1): spec vẫn duyệt riêng; chỉ bỏ khoảng chờ turn |
| Bỏ `tdq-reviewer` mặc định làm lọt lỗi spec/plan (hôm qua nó tìm ra 5 finding thật) | Chất lượng spec/plan giảm | Giữ bước "tự review" + `doc_lint.py` (R8) và `--pair` bắt buộc exit 0; ghi rõ trong skill là user gọi tay được |
| `effort` frontmatter ĐÈ mức effort của phiên | Agent nặng bị ép nghĩ nông dù user để phiên mức cao | Chỉ đặt effort thấp cho agent thuần cơ học (runner bọc script); implementer/qc dùng `inherit`/mức cao. Ghi luật này vào `subagent-tuning.md` |
| Vượt trần dòng SKILL.md (spec/plan trần 100, intake 120, conventions 120) | `doc_lint` R6 fail | Nội dung mới (heuristic model, luật hỏi) đặt trong `references/`, SKILL.md chỉ giữ 1 dòng trỏ tới |
| Sửa `PHASE_TABLE` mà quên sinh lại `phases.md` (2 nơi: skills + portable) | `test_phase_table.py` fail hoặc doc lệch âm thầm | Task riêng chạy `phases-doc` cho cả 2 đường dẫn, đặt SAU task sửa `PHASE_TABLE` |
| Lane quick nặng thêm khiến việc 5 phút mất công | User khó chịu | Quick chỉ 1 file gộp + 1 lần duyệt; research/interview có điều kiện rõ: chỉ khi có ẩn số bên ngoài hoặc câu hỏi làm đổi kết quả |
| Sửa `~/.claude/CLAUDE.md` (ngoài repo) không có test bảo vệ | Luật global lệch với skill | Task riêng, kiểm bằng `grep` nêu ở §6 Q9 |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Toàn bộ test suite | `python3 -m unittest discover -s tests -p "test_*.py"` | 0 fail, 0 error, số test ≥ 448 |
| Q2 | Lint doc của 5 skill sửa đổi | `python3 scripts/doc_lint.py skills/tdq-*/SKILL.md` | exit 0 |
| Q3 | Lint cặp spec↔plan của chính request này | `python3 scripts/doc_lint.py --pair docs/tdq/spec/2026-08-04-workflow-linh-hoat.md docs/tdq/plan/2026-08-04-workflow-linh-hoat.md` | exit 0 |
| Q4 | `phases.md` khớp `PHASE_TABLE` ở cả 2 nơi | `tests/test_phase_table.py` + diff `tdq_state.py phases-doc` với file trên đĩa | test xanh, diff rỗng |
| Q5 | Bản portable khớp bản skill | `python3 -m unittest tests.test_portable_sync -v` | xanh |
| Q6 | Không còn rào "turn mới" giữa spec→plan→build | `grep -rn "turn mới\|turn tiếp theo" skills/ portable/workflow/` | không có dòng nào nói phải sang turn mới giữa spec/plan/build |
| Q7 | `tdq-reviewer` không còn là bước bắt buộc | `grep -n "tdq-reviewer" skills/tdq-spec/SKILL.md skills/tdq-plan/SKILL.md` | mỗi file ≤1 dòng, và dòng đó ở dạng tùy chọn ("khi user yêu cầu") |
| Q8 | Frontmatter 7 agent có `model` + `effort` hợp lệ | test mới `tests/test_agent_frontmatter.py` | xanh; `model` ∈ {sonnet,opus,haiku,fable,inherit,model-id}, `effort` ∈ {low,medium,high,xhigh,max} |
| Q9 | CLAUDE.md global đã sync | `grep -c "Spec và plan không lập trong cùng một turn" ~/.claude/CLAUDE.md` | trả 0 |
| Q10 | Luật hỏi có câu bổ sung bắt buộc | `grep -c "Bạn muốn bổ sung thêm gì không?" skills/tdq-intake/references/interview.md` | ≥1 |
| Q11 | Lane quick có research + interview + file gộp | đọc `skills/tdq-intake/SKILL.md` Phần C + test khoá bước | Phần C có bước web search, bước interview có điều kiện, và nêu file `docs/tdq/plan/<slug>.md` |
| Q12 | Chạy thử luồng gộp bằng project rác | `TDQ_PROJECT_DIR=<tmp> python3 scripts/tdq_state.py` chuỗi: init → set phase=spec → approve spec → set phase=plan → approve plan --mode main → set phase=implement | mọi lệnh exit 0, `next` sau mỗi bước trỏ đúng phase kế tiếp |

**DoD:** Q1–Q12 đều PASS, có bằng chứng (lệnh + output thật) ghi trong `docs/tdq/qc/2026-08-04-workflow-linh-hoat.md`; mọi task trong plan đã tick `[x]`; report ≤50 dòng đã viết.

## 7. Câu hỏi còn mở

(rỗng)
