# REPORT — Workflow linh hoạt: gộp gate, quick đủ bước, lộ trình động

Ngày: 2026-08-04 · Lane: full · Mode: main · Trạng thái: **HOÀN THÀNH**
Spec: ../spec/2026-08-04-workflow-linh-hoat.md · Plan: ../plan/2026-08-04-workflow-linh-hoat.md (25/25 task)
QC: ../qc/2026-08-04-workflow-linh-hoat.md (Q1–Q12 PASS)

## Đã làm được gì

1. **Bỏ tdq-reviewer khỏi luồng mặc định.** `tdq-spec`/`tdq-plan` chỉ còn tự review bằng
   `doc_lint.py`; agent `tdq-reviewer` giữ nguyên để user gọi tay khi cần review sâu.
2. **Sub-agent chỉnh được model + thinking.** 7 agent có `model` + `effort` trong frontmatter
   làm mặc định; Claude nâng/hạ động khi task nặng/nhẹ hơn thường lệ. Khoá bằng
   `tests/test_agent_frontmatter.py`.
3. **Gộp gate, hết turn trống.** Duyệt spec → viết plan NGAY cùng turn; duyệt plan kèm mode
   ("duyệt plan mode main|subagent|external") → vào build NGAY cùng turn. Vẫn đủ 2 lần duyệt.
   Mode giờ do plan ĐỀ XUẤT sẵn, user chỉ chốt/đổi lúc duyệt — không còn lượt hỏi mode riêng.
4. **Câu hỏi mở cuối mỗi vòng interview.** Vẫn dùng interface câu hỏi, nhưng bắt buộc kết thúc
   bằng "Bạn muốn bổ sung thêm gì không?" (`Không, đủ rồi — làm tiếp đi` / `Có — tôi nói thêm`).
5. **Lane quick có đủ bước tư duy.** Phân tích → web search (khi có ẩn số ngoài) → interview
   (khi còn câu hỏi đổi kết quả) → mini-spec/plan GỘP 1 file `docs/tdq/plan/<slug>.md` ≤40 dòng
   → 1 gate duyệt. Chi tiết + khuôn: `skills/tdq-intake/references/quick-lane.md` (file mới).
6. **Lộ trình động, không fix cứng.** Cuối phase analyze ghi mục `## Lộ trình` vào knowledge
   (bảng bước/phase | CÓ-BỎ | vì sao), chép sang spec §1b — user duyệt spec là duyệt luôn lộ
   trình. Khung bất biến giữ nguyên: phân tích → spec/plan → implement → report.

## File đã đổi

- Skill: `tdq-intake` (+ `references/quick-lane.md` mới, `interview.md`, `lane-decision.md`),
  `tdq-spec` (+ `spec-template.md`), `tdq-plan` (+ `plan-template.md`), `tdq-build`, 7 agent.
- Portable: `AGENTS.md`, `workflow/01-intake.md`, `02-spec.md`, `03-plan.md`, `04-build.md`,
  `references/{quick-lane.md mới, spec-template.md, plan-template.md, phases.md}`.
- Core: `scripts/tdq_state.py` (PHASE_TABLE cho phép chuỗi cùng turn).
- Test mới: `tests/test_gate_merge.py`, `tests/test_agent_frontmatter.py`, thêm class
  `QuickLaneThinkingStepsTest` vào `tests/test_skill_docs.py`.
- Global: `~/.claude/CLAUDE.md` mục 9 (bỏ luật "spec và plan không cùng turn", thêm 5 luật mới).
  `~/.claude/settings.json`: **không cần đổi** (không thêm hook/env).

## Kiểm chứng

- Toàn suite: `cd tests && python3 -m unittest discover -s . -p "test_*.py"` → **462 test, OK**.
- `doc_lint.py` trên 6 SKILL.md và `--pair` spec↔plan: exit 0.
- `phases.md` (bản skill + bản portable) diff rỗng so với `PHASE_TABLE`.
- Code graph rebuild: `graphify extract . --code-only` (2580 node, 3646 edge).

## Lưu ý

- Trong lúc QC tôi chạy nhầm `tdq_state.py init` thiếu `TDQ_PROJECT_DIR` làm xoá state thật;
  đã khôi phục ngay bằng CLI, chỉ còn `previous_request` lưu slug rác `2026-08-04-thu-nghiem`.
- **Chưa commit** — chờ bạn quyết.
