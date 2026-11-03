# QC — workflow linh hoạt (gộp gate, lane quick đủ bước, lộ trình động)

Spec: ../spec/2026-08-04-workflow-linh-hoat.md · Plan: ../plan/2026-08-04-workflow-linh-hoat.md
Ngày chạy: 2026-08-04 · Mode: main

## Kết quả

| # | Hạng mục | Bằng chứng (lệnh + output thật) | Kết quả |
|---|---|---|---|
| Q1 | Toàn bộ test suite | `cd tests && python3 -m unittest discover -s . -p "test_*.py"` → `Ran 462 tests in 41.898s / OK` | **PASS** (462 ≥ 448) |
| Q2 | Lint 6 SKILL.md | `python3 scripts/doc_lint.py skills/tdq-*/SKILL.md` → không output, `exit=0` | **PASS** |
| Q3 | Lint cặp spec↔plan | `python3 scripts/doc_lint.py --pair docs/tdq/spec/<slug>.md docs/tdq/plan/<slug>.md` → `exit=0` | **PASS** |
| Q4 | `phases.md` khớp `PHASE_TABLE` | `phases-doc --plugin-root \| diff - skills/tdq-conventions/references/phases.md` → rỗng; `phases-doc \| diff - portable/workflow/phases.md` → rỗng; `test_phase_table` xanh | **PASS** |
| Q5 | Portable khớp skill | `python3 -m unittest test_portable_sync` → OK (trong lượt 16 test cùng `test_phase_table`, `test_agent_frontmatter`) | **PASS** |
| Q6 | Không còn rào "turn mới" | `grep -rn "turn mới\|turn tiếp theo" skills/ portable/workflow/ \| wc -l` → `0` | **PASS** |
| Q7 | `tdq-reviewer` là tùy chọn | `grep -c "tdq-reviewer"` → tdq-spec: 1, tdq-plan: 1; cả hai dòng: "Cần review sâu hơn thì user yêu cầu — khi đó mới gọi agent `tdq-reviewer` (tùy chọn)." | **PASS** |
| Q8 | Frontmatter 7 agent có `model` + `effort` | `python3 -m unittest test_agent_frontmatter` → OK | **PASS** |
| Q9 | CLAUDE.md global đã sync | `grep -c "Spec và plan không lập trong cùng một turn" ~/.claude/CLAUDE.md` → `0`; `grep -c "duyệt plan mode"` → `2` | **PASS** |
| Q10 | Câu hỏi mở bắt buộc | `grep -c "Bạn muốn bổ sung thêm gì không?" skills/tdq-intake/references/interview.md` → `1` | **PASS** |
| Q11 | Quick có search + interview + file gộp | Phần C của `skills/tdq-intake/SKILL.md`: dòng "web search qua `tavily-primary` TRƯỚC khi viết gì", "interview theo [references/interview.md]", "Viết mini-spec/plan GỘP 1 file `docs/tdq/plan/<slug>.md`, ≤ 40 dòng" | **PASS** |
| Q12 | Chạy thử luồng gộp (project rác) | `TDQ_PROJECT_DIR=<scratch>/q12`: init → set phase=spec → approve spec → set phase=plan → approve plan --mode main → set phase=implement, mọi lệnh `exit=0`; `next` sau mỗi bước trỏ đúng phase; `get phase` cuối = `implement` | **PASS** |

## Ghi chú

- **settings.json (T5.4):** KHÔNG cần đổi. Thay đổi lần này chỉ chạm prose của
  skill/portable/CLAUDE.md và frontmatter agent — không thêm/bớt hook, không thêm biến env.
  Hook TDQ (`prompt_context.py`, `bash_gate.py`, `stop_gate.py`) do plugin đăng ký, không nằm
  trong `~/.claude/settings.json` (file này chỉ có hook `plugin_tiers.py reset`).
  Kiểm hợp lệ: `python3 -c "import json;json.load(open('~/.claude/settings.json'))"` exit 0.
- **T6.1 log:** không thêm runtime mới; `grep -c "_info\|_warn" scripts/tdq_state.py` = 24,
  bằng đúng bản HEAD (`git show HEAD:scripts/tdq_state.py` = 24) → log không bị giảm.
  `test_turn_ledger` + `test_state`: 37 test OK.
- **Sự cố trong lúc QC:** chạy nhầm `tdq_state.py init` thiếu `TDQ_PROJECT_DIR` nên state thật
  bị xoá; đã khôi phục ngay bằng chính CLI (init → spec_file → approve spec → plan_file →
  approve plan --mode main → phase=qc). `spec_sha256` khớp bản cũ; `plan_sha256` khác vì plan đã
  tick `[x]`. Trường `previous_request` còn lưu slug rác `2026-08-04-thu-nghiem` — vô hại.

**DoD: ĐẠT** — Q1–Q12 đều PASS, mọi task trong plan đã tick `[x]` (25/25, 0 task chưa tick).
