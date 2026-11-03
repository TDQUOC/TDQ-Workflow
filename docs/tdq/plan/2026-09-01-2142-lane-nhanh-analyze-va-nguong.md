# QUICK — lane nhanh: pha analyze có tên + ngưỡng B0/B1/B2

**Ngày:** 2026-09-01 · Brief: ../brief/2026-09-01-2142-lane-nhanh-analyze-va-nguong.md · Lane: quick
**Trạng thái:** CHỜ DUYỆT
**Ước tính sẽ dùng skill:** tdq-conventions, tdq-lsp-setup
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Phạm vi
- Trong: phương án 2a — lane nhanh có pha `analyze` HIỆN TÊN trong bảng pha, KHÔNG thêm cổng
  duyệt. `CONG_THEO_LANE` và `APPROVE_TARGETS` giữ nguyên, lane nhanh vẫn đúng một cổng.
- Trong: ngưỡng ba bước viết thành luật chữ + bắt buộc ghi dòng lý do khi BỎ một bước.
- Bỏ vòng phạm vi: user đã chốt cả 3 câu, phạm vi đóng. Bỏ web search: thuần nội bộ.
- NGOÀI: thêm cổng duyệt phân tích (đó là 2c, user chốt 2a).
- NGOÀI: dọn nợ lint có sẵn ngoài các file request này chạm.

## Task
- [x] **T1** Thêm hàng `quick_analyze` vào `PHASE_TABLE` + `PHASE_ORDER`, và `phase_key` trả
  hàng đó khi `lane=quick` và `phase=analyze` — Test: `python3 -m pytest tests/test_phase_table.py
  tests/test_state_phase.py -q` xanh; test mới khẳng định `phase_key` trả `quick_analyze`
  - Chạm: `scripts/tdq_state.py`, `tests/test_phase_table.py`
- [x] **T2** Thêm khoá state `brief_file` (đặt được qua `set`, mặc định None) — Test: test mới
  `set brief_file=docs/tdq/brief/x.md` rồi `get brief_file` trả đúng giá trị
  - Chạm: `scripts/tdq_state.py`, `tests/test_state.py`
- [x] **T3** `quick-lane.md`: 9 → 10 bước (chèn bước phân tích ghi vào brief trước bước viết
  mini-plan), thêm mục ngưỡng B0/B1/B2 kèm luật "BỎ bước nào phải ghi 1 dòng lý do vào
  `## Phạm vi` của mini-plan" — Test: `python3 scripts/doc_lint.py skills/tdq-intake` thoát 0
  - Chạm: `skills/tdq-intake/references/quick-lane.md`, `skills/tdq-intake/SKILL.md`
- [x] **T3b** Sửa vi phạm R5 còn lại ở `quick-lane.md` (câu 41 từ) — tách thành 2 câu; task
  riêng vì cổng `edit_gate` chặn đúng: T3 đụng nhiều file hơn một task nên đáng tách
  - Chạm: `skills/tdq-intake/references/quick-lane.md`
- [x] **T4** Sinh lại `phases.md`, bump version + CHANGELOG, dựng lại 3 bundle portable —
  Test: `tdq_checkportable.py check` in CLEAN cho cả 3 bundle
  - Chạm: `skills/tdq-conventions/references/phases.md`, `CHANGELOG.md`, `portable_claude/`,
    `portable_codex/`, `antigravity_portable/`

## Definition of Done
- `python3 -m pytest tests/ -q` không vượt mốc đỏ 101 fail, không file mới nào vào bảng lỗi
- `python3 scripts/doc_lint.py skills/tdq-intake skills/tdq-conventions/references/phases.md` thoát 0
- `phase_key` trả `quick_analyze` đúng điều kiện, và `cong_dang_cho` với lane quick vẫn chỉ
  đòi đúng cổng `quick` — chứng minh bằng test
- 3 bundle portable đều in CLEAN

## QC
Năm mục dưới đây chốt TRƯỚC khi implement theo yêu cầu user ("bổ sung QC vào plan này");
bằng chứng thật điền vào từng dòng ngay sau khi implement xong.
- Q1 test từng task: **PASS** — `pytest tests/test_phase_table.py tests/test_state_phase.py
  tests/test_state.py tests/test_quick_qc.py tests/test_token_budget.py -q` → 95 passed,
  28 subtests passed, 0 fail.
- Q2 DoD "pytest không vượt mốc đỏ 101 fail": **PASS** — `pytest tests/ -q` → `101 failed,
  1453 passed`, đúng mốc đỏ; 5 file trong bảng lỗi đều đỏ sẵn (test_bench, test_doc_lint,
  test_luat_skill, test_rules_library, test_skill_router), không file mới nào vào bảng.
- Q3 DoD "doc_lint skills/tdq-intake + phases.md thoát 0": **PASS** — `0 violation(s)
  total, exit 0`. (2 vi phạm R5 còn lại của repo nằm ở `tdq-build/SKILL.md` và
  `tdq-lsp-setup/references/uu-tien-tim-kiem.md` — NGOÀI phạm vi, xem `## Phạm vi`.)
- Q4 DoD "`phase_key` trả `quick_analyze` đúng điều kiện, `cong_dang_cho` lane quick vẫn chỉ
  đòi cổng `quick`": **PASS** — `test_lane_quick_van_chi_mot_cong` xanh: khẳng định
  `CONG_THEO_LANE["quick"] == ("quick",)`, `"analyze" not in APPROVE_TARGETS`, và
  `cong_dang_cho` lane quick pha analyze vẫn trả `"quick"`. Mục canh 2a không trượt thành 2c.
- Q5 DoD "3 bundle portable in CLEAN": **PASS** — dựng lại sau lần cắt cuối: portable_claude
  90 file, portable_codex 138, antigravity_portable 83, cả ba in CLEAN.
- Ngoài DoD, tự phát hiện: bảng luật `docs/tdq/audit/luat-hien-co.md` còn neo vào chữ "nine
  steps" cũ ở 5 dòng (L222–L224, L242, L245) → đã cập nhật neo + số dòng;
  `test_moi_luat_con_nguyen_trong_skill` từ đỏ chuyển xanh, độ lệch 62/329 → 57/329.

## QC vòng 1 — fix
- [x] **QC1.1** `test_skill_body_points_to_quick_lane` đòi SKILL.md chứa đúng chuỗi "The nine
  execution steps" — cập nhật test sang "ten" — Test: `pytest tests/test_quick_qc.py -q` xanh
  - Chạm: `tests/test_quick_qc.py`
- [x] **QC1.2** `quick-lane.md` 228 dòng, vượt trần 215 của `test_token_budget` — cắt gọn về
  dưới trần, không mất luật — Test: `pytest tests/test_token_budget.py -q` xanh
  - Chạm: `skills/tdq-intake/references/quick-lane.md`
- [x] **QC1.3** Cắt tiếp `quick-lane.md` 219 → **215** dòng, không mất luật nào (gộp câu, giữ nguyên bảng ngưỡng) —
  Test: `pytest tests/test_token_budget.py -q` xanh
  - Chạm: `skills/tdq-intake/references/quick-lane.md`
