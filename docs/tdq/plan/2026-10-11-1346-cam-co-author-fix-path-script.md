# PLAN — Nghiêm cấm Co-Authored-By và chuẩn hóa đường dẫn script plugin

Ngày: 2026-10-11 · Spec: ../spec/2026-10-11-1346-cam-co-author-fix-path-script.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — Các task sửa đổi văn bản và script gắn liền nhau, chạy tuần tự an toàn nhất (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Setup & Instructions
- P2 — Conventions & Report
- P3 — Script Path Normalization
- P4 — Verification & Token Budget
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Mỗi bước: `tdq_test.py vung-cham`; trọn bộ chỉ ở QC.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Setup & Instructions
- [x] **T1.1** (e5m) Cập nhật `KHOI_HUONG_DAN` trong `scripts/tdq_setup.py` và `docs/notes/user-level-install.md` thêm luật cấm `Co-Authored-By` và attribution trailer — Test: `pytest tests/test_auto_update_setup.py -q`
  - Chạm: `scripts/tdq_setup.py`, `docs/notes/user-level-install.md`
- [x] **T1.2** (e5m) Đồng bộ instruction `~/.claude/CLAUDE.md` và kiểm tra sự xuất hiện của quy tắc cấm — Test: `python scripts/tdq_setup.py`

**Xong P1 khi**: `scripts/tdq_setup.py` và `~/.claude/CLAUDE.md` có đầy đủ quy tắc cấm `Co-Authored-By`.

## P2 — Conventions & Report
- [x] **T2.1** (e5m) Cập nhật `skills/tdq-conventions/SKILL.md` mục 7 và `skills/tdq-build/references/report-template.md` mục 10 cấm rõ ràng `Co-Authored-By: Claude Code...` — Test: `pytest tests/test_skill_shape.py tests/test_luat_skill.py -q`
  - Chạm: `skills/tdq-conventions/SKILL.md`, `skills/tdq-build/references/report-template.md`

**Xong P2 khi**: Văn bản conventions và mẫu report cấm cụ thể tên `Co-Authored-By`.

## P3 — Script Path Normalization
- [x] **T3.1** (e10m) Chuẩn hóa các lệnh gọi `python3 scripts/...` thành `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/..."` trong toàn bộ markdown của `skills/` — Test: `pytest tests/test_skill_shape.py tests/test_luat_skill.py -q`
  - Chạm: `skills/tdq-intake/SKILL.md`, `skills/tdq-intake/references/kiem-lsp-hieu-ung.md`, `skills/tdq-intake/references/quick-lane.md`, `skills/tdq-intake/references/quick-lane-qc.md`, `skills/tdq-setup/SKILL.md`, `skills/tdq-setup/references/uu-tien-tim-kiem.md`, `skills/tdq-plan/references/mode-gate.md`, `skills/tdq-build/SKILL.md`, `skills/tdq-build/references/team-mode.md`, `skills/tdq-build/references/team-mode-tra-cuu.md`, `skills/tdq-build/references/codex-mode.md`, `skills/tdq-check-status/references/report-template.md`, `skills/tdq-check-status/references/bang-lech.md`, `skills/tdq-conventions/references/user-facing-block-vi-du.md`, `skills/tdq-conventions/references/measure-scenario.md`, `skills/tdq-lean/SKILL.md`

**Xong P3 khi**: Không còn lệnh gọi `python3 scripts/` trần nào trong `skills/`.

## P4 — Verification & Token Budget
- [x] **T4.1** (e5m) Chạy `scripts/token_budget.py` và kiểm tra toàn bộ test suite pass 100% — Test: `pytest tests/test_doc_lint.py tests/test_docs_consistency.py tests/test_luat_skill.py -q`
  - Chạm: `docs/tdq/token-budget.json`

**Xong P4 khi**: Toàn bộ test suite pass, 0% drift, token budget cập nhật hợp lệ.

## Definition of Done
- [x] DoD 1: `KHOI_HUONG_DAN` trong `scripts/tdq_setup.py` và `~/.claude/CLAUDE.md` có điều luật cấm `Co-Authored-By` và attribution.
- [x] DoD 2: `skills/tdq-conventions/SKILL.md` và `skills/tdq-build/references/report-template.md` cấm rõ ràng `Co-Authored-By`.
- [x] DoD 3: Không còn bất kỳ lệnh gọi script trần thiếu `${CLAUDE_PLUGIN_ROOT}` trong toàn bộ thư mục `skills/`.
- [x] DoD 4: Toàn bộ test suite pass, drift luật giữ nguyên 0.00%.
