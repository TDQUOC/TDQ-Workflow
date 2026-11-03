# PLAN — TDQ workflow linh hoạt & bớt ma sát

Ngày: 2026-08-04 · Spec: ../spec/2026-08-04-workflow-linh-hoat.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — mọi task đụng chung một nhóm file khoá chặt nhau (`PHASE_TABLE` → `phases.md` → `portable/` → test), thứ tự phụ thuộc dày, không tách worktree song song được mà không conflict.
Trạng thái plan: HOÀN THÀNH (mode main)

## Năng lực → task

(Mỗi dòng DÙNG ở spec §3b phải có mặt ở đây VÀ có khối hợp đồng 6 trường trong task.)

| Skill | Task | Đầu ra bắt buộc |
|---|---|---|
| skill-creator | T5.1 | 5 SKILL.md qua rà hình dạng, `doc_lint.py skills/tdq-*/SKILL.md` exit 0 |
| tavily-search | T2.1 | dòng nguồn docs trong `references/subagent-tuning.md` (URL + ngày tra) |
| update-config | T5.4 | kết luận ghi trong `docs/tdq/qc/<slug>.md`: settings.json cần đổi hay không |
| graphify | T5.5 | `graphify-out/graph.json` mtime mới hơn lúc bắt đầu build |

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: viết test trước (đỏ) → code → test xanh → tick `[x]` NGAY vào file này.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Nguồn sự thật: PHASE_TABLE + phases.md (đầu ra #2, #3, #6, #10)

- [x] **T1.1** Sửa `PHASE_TABLE["spec"]` trong `scripts/tdq_state.py`: `forbidden` bỏ vế "Viết plan trong cùng turn với spec" (giữ vế "tự suy diễn là user đã duyệt"); `checklist` bước cuối đổi thành "User duyệt → chạy approve NGAY rồi viết plan trong CÙNG turn" — Test: `python3 -m unittest tests.test_phase_table -v` xanh và `python3 -c "import sys;sys.path.insert(0,'scripts');from tdq_state import PHASE_TABLE;assert 'cùng turn với spec' not in PHASE_TABLE['spec']['forbidden']"` exit 0
- [x] **T1.2** Sửa `PHASE_TABLE["plan"]`: `action` bỏ "Hỏi mode thực thi", `checklist[0]` đổi thành "ĐỀ XUẤT mode thực thi ngay trong plan (main|subagent|external) + lý do — không hỏi riêng"; thêm bước cuối "User duyệt kèm mode → approve rồi build trong CÙNG turn" — Test: `python3 -c "…;assert not PHASE_TABLE['plan']['checklist'][0].startswith('Hỏi user mode') and 'ĐỀ XUẤT' in PHASE_TABLE['plan']['checklist'][0]"` exit 0
- [x] **T1.3** Sửa `PHASE_TABLE["quick"]`: `action`/`checklist` phản ánh lane quick mới — bước 1 "Phân tích + web search khi có ẩn số bên ngoài", bước 2 "Interview khi còn câu làm đổi kết quả", bước 3 "Viết mini-spec/plan GỘP vào `docs/tdq/plan/<slug>.md`", giữ các bước duyệt/log/implement — Test: `python3 -c "…;c=PHASE_TABLE['quick']['checklist'];assert any('docs/tdq/plan/' in x for x in c) and any('search' in x.lower() for x in c)"` exit 0
- [x] **T1.4** Sinh lại `skills/tdq-conventions/references/phases.md` và `portable/workflow/phases.md` bằng `tdq_state.py phases-doc` (không sửa tay) — Test: `python3 -m unittest tests.test_phase_table tests.test_docs_consistency -v` xanh; `diff <(python3 scripts/tdq_state.py phases-doc --plugin-root) skills/tdq-conventions/references/phases.md` rỗng

**Xong P1 khi**: 3 mục PHASE_TABLE đã sửa, 2 file phases.md sinh lại khớp, toàn bộ test suite xanh.

## P2 — Heuristic model/effort cho sub-agent (đầu ra #8, #9)

- [x] **T2.1** Viết mới `skills/tdq-conventions/references/subagent-tuning.md`: bảng vai→`model`→`effort` mặc định cho 7 agent; luật override `model` qua tham số Agent tool lúc gọi (theo độ khó/độ dài task); cảnh báo `effort` frontmatter ĐÈ mức effort của phiên nên chỉ đặt thấp cho agent thuần cơ học; mục Nguồn ghi 2 URL docs + ngày tra — Test: `python3 scripts/doc_lint.py skills/tdq-conventions/references/subagent-tuning.md` exit 0 và `grep -c "code.claude.com/docs/en/sub-agents" <file>` ≥1
  - Dùng: `tavily-search` (mcp)
  - Nạp: gọi skill `tavily-search` TRƯỚC bước đỏ của task này. Agent ngoài không có skill system: đọc `skills/tavily-search/SKILL.md` của plugin tavily rồi làm theo.
  - Để: xác minh lại (tại thời điểm build) danh sách giá trị hợp lệ của `model`/`effort` và việc plugin subagent có honor 2 trường này không, trước khi chốt bảng mặc định.
  - Ra: mục `## Nguồn` trong `skills/tdq-conventions/references/subagent-tuning.md` có ≥2 URL kèm ngày tra.
  - Kiểm: `grep -cE "https://code\.claude\.com/docs/en/(sub-agents|model-config)" skills/tdq-conventions/references/subagent-tuning.md` trả về 2.
  - Không dùng cho: chọn model cho engine ngoài (codex/agy) — việc đó thuộc `external_models.py`, không đụng.
- [x] **T2.2** Thêm 1 dòng trong `skills/tdq-conventions/SKILL.md` §9 (hoặc mục mới ≤3 dòng) trỏ tới `references/subagent-tuning.md` — Test: `grep -c "subagent-tuning" skills/tdq-conventions/SKILL.md` =1 và `python3 scripts/doc_lint.py skills/tdq-conventions/SKILL.md` exit 0 (trần 120 dòng)
- [x] **T2.3** Viết test mới `tests/test_agent_frontmatter.py`: đọc frontmatter 7 file `agents/*.md`, khẳng định có `model` và `effort`, giá trị nằm trong tập hợp lệ (`model` ∈ {sonnet,opus,haiku,fable,inherit} hoặc khớp `^claude-[\w.-]+$`; `effort` ∈ {low,medium,high,xhigh,max}) — Test: chạy test này TRƯỚC khi sửa agent → phải FAIL (đỏ)
- [x] **T2.4** Thêm `model` + `effort` vào frontmatter 7 file trong `agents/`: `tdq-implementer` (inherit/high), `tdq-qc-tester` (inherit/high), `tdq-reviewer` (inherit/high), `search-scout` (sonnet/medium), `search-runner` (haiku/low), `codex-runner` (haiku/low), `agy-runner` (haiku/low) — Test: `python3 -m unittest tests.test_agent_frontmatter -v` xanh (chuyển đỏ→xanh) và `python3 -m unittest tests.test_skill_shape -v` vẫn xanh

**Xong P2 khi**: `subagent-tuning.md` tồn tại + được trỏ tới, 7 agent có model/effort, test mới xanh.

## P3 — Skill: gộp gate, bỏ reviewer mặc định, lộ trình (đầu ra #1, #2, #3, #4, #7)

- [x] **T3.1** `skills/tdq-spec/SKILL.md`: bỏ dòng 9 "Không bao giờ viết spec và plan trong cùng một turn"; bước 2 bỏ "gọi agent `tdq-reviewer`" → thay bằng 1 dòng "Cần review sâu → user gọi tay agent `tdq-reviewer`"; mục "Bước kế tiếp" đổi thành "…rồi sang tdq-plan NGAY trong cùng turn"; bước 1 thêm yêu cầu chép mục `## Lộ trình` từ knowledge vào spec — Test: `grep -c "turn mới" skills/tdq-spec/SKILL.md` =0; `grep -c "tdq-reviewer" …` =1; `grep -c "Lộ trình" …` ≥1; `python3 scripts/doc_lint.py skills/tdq-spec/SKILL.md` exit 0
- [x] **T3.2** `skills/tdq-plan/SKILL.md`: xoá bước 1 "HỎI user chọn mode … Chờ user trả lời" → thay bằng "ĐỀ XUẤT mode + lý do, ghi thẳng vào dòng `Mode thực thi:` của plan"; bước 3 bỏ gọi `tdq-reviewer` (giữ dòng tùy chọn); bỏ "Không viết cùng turn với spec"; "Bước kế tiếp" → sang tdq-build NGAY cùng turn — Test: `grep -c "Chờ user trả lời" skills/tdq-plan/SKILL.md` =0; `grep -c "turn mới" …` =0; `python3 scripts/doc_lint.py skills/tdq-plan/SKILL.md` exit 0 (trần 100 dòng)
- [x] **T3.3** `skills/tdq-build/SKILL.md`: Luật cứng nêu rõ "vào build ngay trong turn user duyệt plan, không chờ user nhắn tiếp"; bỏ mọi chữ "turn mới" nếu có — Test: `grep -c "turn mới" skills/tdq-build/SKILL.md` =0 và `python3 scripts/doc_lint.py skills/tdq-build/SKILL.md` exit 0 (trần 150)
- [x] **T3.4** `skills/tdq-spec/references/spec-template.md`: thêm mục `## 1b. Lộ trình` (phase sẽ chạy/bỏ + skill sẽ dùng + lý do) vào khuôn, và thêm 1 dòng ở mục "Kiểm trước khi trình" — Test: `grep -c "Lộ trình" skills/tdq-spec/references/spec-template.md` ≥2
- [x] **T3.5** `skills/tdq-plan/references/plan-template.md`: mục "Dòng `Mode thực thi`" ghi rõ đây là ĐỀ XUẤT của Claude (không hỏi trước), user chốt lúc duyệt bằng "duyệt plan mode <X>" — Test: `grep -c "duyệt plan mode" skills/tdq-plan/references/plan-template.md` ≥1
- [x] **T3.6** Viết test mới `tests/test_gate_merge.py`: khoá 4 bất biến — (a) không file nào trong `skills/tdq-{spec,plan,build}/SKILL.md` chứa "turn mới"; (b) `tdq-spec`/`tdq-plan` mỗi file ≤1 lần nhắc `tdq-reviewer`; (c) `PHASE_TABLE['spec']['forbidden']` không chứa "cùng turn với spec"; (d) `interview.md` chứa câu hỏi bổ sung bắt buộc — Test: `python3 -m unittest tests.test_gate_merge -v` xanh (chạy trước T3.1 phải đỏ)

**Xong P3 khi**: 3 SKILL.md + 2 template đã sửa, `test_gate_merge` xanh, `doc_lint` cả 5 skill exit 0.

## P4 — Lane quick mới + luật hỏi mở (đầu ra #5, #6, #7)

- [x] **T4.1** `skills/tdq-intake/references/interview.md`: mục "Hỏi thế nào" giữ AskUserQuestion, thêm luật BẮT BUỘC câu cuối mỗi vòng: `Bạn muốn bổ sung thêm gì không?` với ≥1 phương án mở để user gõ tự do — Test: `grep -c "Bạn muốn bổ sung thêm gì không?" skills/tdq-intake/references/interview.md` ≥1
- [x] **T4.2** `skills/tdq-intake/SKILL.md` Phần B: thêm bước ghi mục `## Lộ trình` vào `knowledge/<slug>.md` (phase sẽ chạy/bỏ + skill + lý do) và nêu rõ user duyệt spec là duyệt luôn lộ trình; "Bước kế tiếp" của Phần B bỏ chữ "turn mới" — Test: `grep -c "Lộ trình" skills/tdq-intake/SKILL.md` ≥1; `grep -c "turn mới" …` =0
- [x] **T4.3** `skills/tdq-intake/SKILL.md` Phần C (lane quick) viết lại: (1) phân tích + web search qua tavily-primary khi có ẩn số bên ngoài, (2) interview khi còn câu làm đổi kết quả (dùng luật `interview.md`), (3) viết **mini-spec/plan gộp** vào `docs/tdq/plan/<slug>.md` (scope in/out + task có test + DoD, ≤40 dòng) rồi trình tóm tắt ≤10 dòng, (4) một lần duyệt → log → implement → report ngắn — giữ trần 120 dòng, đẩy chi tiết sang `references/quick-lane.md` nếu vượt — Test: `python3 scripts/doc_lint.py skills/tdq-intake/SKILL.md` exit 0 và `grep -c "docs/tdq/plan/" skills/tdq-intake/SKILL.md` ≥1
- [x] **T4.4** Cập nhật `tests/test_skill_docs.py` / `tests/test_skill_shape.py` cho hình dạng mới (số bước, nội dung bắt buộc) — Test: `python3 -m unittest tests.test_skill_shape tests.test_skill_docs -v` xanh

**Xong P4 khi**: luật hỏi + lộ trình + lane quick mới đã vào skill, test hình dạng xanh.

## P5 — Đồng bộ portable, CLAUDE.md, rà chất lượng (đầu ra #11, #12)

- [x] **T5.1** Rà hình dạng 5 SKILL.md đã sửa (frontmatter, mô tả trigger, độ dài, bước đánh số liên tục) — Test: `python3 scripts/doc_lint.py skills/tdq-*/SKILL.md` exit 0 và `python3 -m unittest tests.test_skill_shape -v` xanh
  - Dùng: `skill-creator`
  - Nạp: gọi skill `skill-creator` TRƯỚC bước đỏ của task này. Agent ngoài không có skill system: đọc `~/.claude/plugins/*/skills/skill-creator/SKILL.md` rồi làm theo.
  - Để: soi 5 SKILL.md vừa sửa xem `description` còn mô tả đúng trigger sau khi đổi luồng, và cấu trúc bước còn mạch lạc.
  - Ra: danh sách sửa đã áp dụng, ghi 1 dòng/skill trong `docs/tdq/qc/2026-08-04-workflow-linh-hoat.md`.
  - Kiểm: `python3 scripts/doc_lint.py skills/tdq-intake/SKILL.md skills/tdq-spec/SKILL.md skills/tdq-plan/SKILL.md skills/tdq-build/SKILL.md skills/tdq-conventions/SKILL.md` exit 0.
  - Không dùng cho: viết skill mới hoặc đổi tên skill — spec §1 đã loại khỏi phạm vi.
- [x] **T5.2** Sync `portable/workflow/01-intake.md`, `02-spec.md`, `03-plan.md`, `04-build.md` theo đúng danh sách bước mới của 4 skill tương ứng — Test: `python3 -m unittest tests.test_portable_sync -v` xanh
- [x] **T5.3** Sync `portable/AGENTS.md` (luật gộp gate, bỏ review mặc định, lane quick mới) — Test: `python3 -m unittest tests.test_portable_sync -v` xanh và `grep -c "CLAUDE_PLUGIN_ROOT" portable/AGENTS.md` =0
- [x] **T5.4** Sửa `~/.claude/CLAUDE.md` mục 9: bỏ câu "Spec và plan không lập trong cùng một turn"; thêm luật gộp gate (duyệt spec → plan ngay; "duyệt plan mode <X>" → build ngay), luật câu hỏi kết thúc bằng "Bạn muốn bổ sung thêm gì không?", lane quick mới; kiểm luôn settings.json có cần đổi không — Test: `grep -c "Spec và plan không lập trong cùng một turn" ~/.claude/CLAUDE.md` =0 và `grep -c "duyệt plan mode" ~/.claude/CLAUDE.md` ≥1
  - Dùng: `update-config`
  - Nạp: gọi skill `update-config` TRƯỚC bước đỏ của task này. Agent ngoài không có skill system: đọc `~/.claude/plugins/.../skills/update-config/SKILL.md` rồi làm theo.
  - Để: xác định thay đổi luật lần này có đòi chỉnh `~/.claude/settings.json` (hook/env) hay không; có thì chỉnh đúng cách, không thì ghi rõ "không cần".
  - Ra: một dòng kết luận trong `docs/tdq/qc/2026-08-04-workflow-linh-hoat.md` mục Q9.
  - Kiểm: `python3 -c "import json;json.load(open('/Users/truongdinhquoc/.claude/settings.json'))"` exit 0 (file vẫn hợp lệ dù có sửa hay không).
  - Không dùng cho: bật/tắt plugin — việc đó theo `plugin_tiers.py`, ngoài phạm vi spec.
- [x] **T5.5** Chạy `graphify extract . --code-only` cập nhật code graph sau khi sửa `scripts/tdq_state.py` — Test: `test -n "$(find graphify-out/graph.json -newermt '-10 minutes')"` trả về true
  - Dùng: `graphify`
  - Nạp: gọi skill `graphify` TRƯỚC bước đỏ của task này. Agent ngoài không có skill system: đọc `~/.claude/skills/graphify/SKILL.md` rồi làm theo.
  - Để: rebuild code graph sau thay đổi `scripts/tdq_state.py` (CLAUDE.md mục 9 yêu cầu cuối turn có đổi code).
  - Ra: `graphify-out/graph.json` và `graphify-out/GRAPH_REPORT.md` được ghi lại.
  - Kiểm: `find graphify-out/graph.json -newermt '-10 minutes' | grep -q graph.json` exit 0.
  - Không dùng cho: phân tích kiến trúc hay đề xuất refactor — chỉ rebuild graph.

**Xong P5 khi**: portable sync xanh, CLAUDE.md đã đổi, graph rebuild xong.

## P6 — Log & test bắt buộc

- [x] **T6.1** Xác nhận không thêm runtime mới nên không thêm log service; log sẵn có (`tdq_state._info/_warn`, sổ turn `.tdq-turn.jsonl`) vẫn bật mặc định và không bị giảm chi tiết — Test: `python3 -m unittest tests.test_turn_ledger tests.test_state -v` xanh và `grep -c "_info\|_warn" scripts/tdq_state.py` không giảm so với trước khi sửa
- [x] **T6.2** Chạy toàn bộ test suite bằng một lệnh — Test: `python3 -m unittest discover -s tests -p "test_*.py"` → 0 fail, 0 error, số test ≥ 448

## Definition of Done

Trỏ về §6 spec. Từng hạng mục + lệnh kiểm:

| # | Lệnh kiểm | PASS khi |
|---|---|---|
| Q1 | `python3 -m unittest discover -s tests -p "test_*.py"` | 0 fail/error, ≥448 test |
| Q2 | `python3 scripts/doc_lint.py skills/tdq-*/SKILL.md` | exit 0 |
| Q3 | `python3 scripts/doc_lint.py --pair docs/tdq/spec/2026-08-04-workflow-linh-hoat.md docs/tdq/plan/2026-08-04-workflow-linh-hoat.md` | exit 0 |
| Q4 | `python3 -m unittest tests.test_phase_table` + diff `phases-doc` với 2 file trên đĩa | xanh, diff rỗng |
| Q5 | `python3 -m unittest tests.test_portable_sync` | xanh |
| Q6 | `grep -rn "turn mới" skills/ portable/workflow/` | không dòng nào bắt sang turn mới giữa spec/plan/build |
| Q7 | `grep -n "tdq-reviewer" skills/tdq-spec/SKILL.md skills/tdq-plan/SKILL.md` | mỗi file ≤1 dòng, dạng tùy chọn |
| Q8 | `python3 -m unittest tests.test_agent_frontmatter` | xanh |
| Q9 | `grep -c "Spec và plan không lập trong cùng một turn" ~/.claude/CLAUDE.md` | =0 |
| Q10 | `grep -c "Bạn muốn bổ sung thêm gì không?" skills/tdq-intake/references/interview.md` | ≥1 |
| Q11 | đọc Phần C của `skills/tdq-intake/SKILL.md` | có bước web search, interview có điều kiện, nêu `docs/tdq/plan/<slug>.md` |
| Q12 | `TDQ_PROJECT_DIR=<tmp>` chuỗi init → set phase=spec → approve spec → set phase=plan → approve plan --mode main → set phase=implement | mọi lệnh exit 0, `next` sau mỗi bước trỏ đúng phase kế tiếp |
