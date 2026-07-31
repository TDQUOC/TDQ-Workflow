# Knowledge — 2026-07-31-audit-full-workflow

## Năng lực dùng được

| Năng lực | Nguồn | Phán quyết | Vì sao |
|---|---|---|---|
| tdq-conventions/intake/spec/plan/build/status | plugin tdq-workflow | DÙNG | Chính là đối tượng audit + khung chạy request |
| tavily-best-practices + tools tavily-primary | plugin tavily | DÙNG | Research khung audit (đã dùng), spot-check khi cần |
| deep-search hybrid (search-runner ∥ search-scout) | plugin tdq-workflow | DÙNG | Đo lại token E2E + verify trigger scout (PENDING 0.6.0) |
| agents codex-runner/agy-runner/tdq-implementer/qc-tester/reviewer | plugin tdq-workflow | DÙNG | Sample E2E external + review spec/plan |
| graphify | user skill | DÙNG | Cập nhật code graph cuối turn đổi code |
| skill-creator, plugin-dev, hookify, playground… | plugin khác | KHÔNG | Không chạm scope audit |

## Quyết định đã chốt (interview vòng 1 — questions/ cùng slug)

1. **Scope model thấp = harden contract**, KHÔNG thêm engine local mới trong
   request này (tách request riêng nếu muốn tích hợp ollama…).
2. **2 sample E2E gọi engine thật**, chạy trong sandbox `TDQ_PROJECT_DIR`:
   - S1: quick external trọn vòng, model thấp nhất trong list engine.
   - S2: full mini mode main + nhánh sự cố (approve mơ hồ, request đè, engine hỏng).
3. **Gộp 2 PENDING 0.6.0**: đo lại token deep search E2E (≤250k) + verify
   trigger agent type `search-scout` (phiên này là phiên mới sau reload).

## Cách tiếp cận đã chọn

Audit 3 lớp, khung chấm theo MAST (spec ambiguity / coordination / verification
gap — nguồn trong research/ cùng slug):

- **Lớp 1 — review tĩnh chéo**: 6 skill + references, 7 agent def, 8 script,
  5 hook, portable/, CLAUDE.md §10 — tìm mâu thuẫn luật, khoảng trống state
  machine, prompt không đủ tường minh cho model yếu (tiêu chí: lệnh cụ thể,
  format output tường minh, không dựa "model tự nhớ").
- **Lớp 2 — sample E2E thật** (S1, S2 ở trên) để lộ issue động.
- **Lớp 3 — fix**: issue → note vào file audit → nguyên nhân gốc → task fix
  red→green (QC-loop trong chính request này).

Phương án loại: chỉ review tĩnh không E2E (không lộ issue động, user yêu cầu
sample thật); thêm engine local ngay (phình scope — user chốt tách riêng).

## Ràng buộc

- Sample E2E KHÔNG được đụng state/doc thật: mọi lệnh state trong sample đặt
  `TDQ_PROJECT_DIR=<sandbox>` ngay trên lệnh; worktree/branch theo quy ước tên;
  không commit trong sandbox trừ khi sample cần (sandbox git riêng thì được).
- Issue đã thấy sớm #1 (trước interview): `tdq_state.py:576` regex escape sai →
  `phases.md` tự sinh chứa literal `` `\1` `` mất 3 dòng lệnh (analyze/spec/plan).
- Token đo qua `<usage>` của từng subagent như tiền lệ 0.6.0.

## Nguồn

- `docs/tdq/research/2026-07-31-audit-full-workflow.md` (MAST, SLM prompt
  practices, khảo sát nội bộ).
- Tiền lệ: QC/report 0.5.0 + 0.6.0 (`docs/tdq/qc|reports/2026-07-31-*.md`).
