# QC — Vá Lỗ Hổng Gate 3 Tầng (`2026-11-08-1207-va-lo-hong-edit-gate-3-tang` · full · main · muc_qc=full)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| DoD | Lệnh kiểm | Kết quả | Bằng chứng |
|---|---|---|---|
| Q1 Edit ngoài `docs/` khi còn cổng chờ → deny; `docs/**` và đã duyệt đủ → không deny | `python -m unittest tests.test_edit_gate tests.test_codex_edit_gate` | PASS | 63 test OK; `test_unapproved_gate_denies_source_only` (src deny, docs/state không deny), `test_full_approved_silent` |
| Q2 Ca play3clone (có `turn_start`, không signal) → deny; signal khớp → im; không `turn_start` → chỉ nhắc | `python -m unittest tests.test_bash_gate` | PASS | `test_approve_denied_without_any_signal_play3clone`, `test_approve_silent_when_signal_matched`, `test_failopen_no_signal_row`, `test_approve_reminds_when_signal_mismatch_without_prompt_hook` |
| Q3 Signal `spec` khớp mà `approve plan` cùng prompt → deny | `python -m unittest tests.test_bash_gate` | PASS | `test_one_prompt_opens_one_gate` |
| Q4 Không còn `set phase=implement` trước duyệt quick; lint 0 lỗi | `python scripts/doc_lint.py skills/tdq-intake/references/quick-lane.md skills/tdq-conventions/references/phases.md` | PASS | `test_quick_analyze_khong_nhay_implement_truoc_duyet`; doc_lint exit 0 sau khi đo lại `token_budget.py` |
| Q5 Full fresh xanh | `python scripts/tdq_test.py tron-bo --workers 1 --fresh --reuse off` | PASS | 4202 test, 10 skip, 926 s, `details_complete=True`; result `docs/tdq/cache/test-runs/3df348232a8e68c3/3ad8dab13edb4d1c91efcf5f18af95b3/result.json` sha256 `47de563a…` |

## Vòng fix 1

Lần full fresh đầu: 4 đỏ, đều do hành vi đổi có chủ đích, và receipt mất hiệu lực vì `tdq_finish.py` rebuild `graphify-out/` giữa lúc suite chạy.

| Test đỏ | Nguyên nhân | Sửa |
|---|---|---|
| `test_e2e_chain` full + quick | Kỳ vọng cũ "trước duyệt vẫn sửa được src" | Đổi sang deny |
| `test_doc_index` | Chỉ mục dòng `quick-lane.md` lệch (file +1 dòng) | `doc_index.py` sinh lại |
| `test_luat_skill` số dòng | 3 neo luật vào `quick-lane.md` lệch 1 dòng | Cộng 1 trong `luat-hien-co.md` |

Còn 16/329 neo lệch ở `skills/tdq-build/SKILL.md` — có sẵn từ HEAD (4,9% < ngưỡng 5%), ngoài phạm vi.

## Vùng chạm

- `tests.test_bash_gate tests.test_compliance_protocol tests.test_edit_gate tests.test_codex_edit_gate tests.test_stop_gate tests.test_prompt_context` → 274 test OK.
- `tests.test_phase_table tests.test_state_phase tests.test_quick_qc tests.test_skill_shape` → 59 test OK.

## Phát hiện trong lúc làm

- Chặn `set phase=implement` khi không có signal sẽ chặn nhầm vòng fix QC (plan đã duyệt từ trước). Đã thêm điều kiện bỏ qua khi cổng đích đã duyệt + test `test_setphase_fix_round_after_plan_approved_not_denied`.
- `tests/test_compliance_protocol.py::test_edit_gate_reminders` khóa cứng hành vi cũ (allow) — cập nhật kỳ vọng sang deny theo spec 1.1.
- `phases-doc` qua PowerShell thêm BOM — đã bỏ để dòng 1 không đổi.
