# QC — TDQ 0.2.0 (soft gates)

Ngày: 2026-07-28 · Spec: [spec](../spec/2026-07-28-soft-gates-remind.md) §4 · Plan: [plan](../plan/2026-07-28-soft-gates-remind.md)

## 1. Unit / e2e

| Hạng mục (spec §4) | Lệnh | Kết quả |
|---|---|---|
| Toàn bộ suite | `cd tests && python3 -m unittest discover .` | **OK — 65 test**, 0 fail (trước: 83 test của 0.1.8, đã xoá 18 test của `approve_gate` + nhánh invite) |
| edit_gate không còn deny | `test_edit_gate.py` (11 test, có `test_never_denies_in_any_scenario` quét 3 state × 3 fixture) | PASS |
| bash_gate không còn deny | `test_bash_gate.py` (8 test, mọi case cũ đổi sang `allow` + có `additionalContext`) | PASS |
| `approve` ghi đủ field + sha256 | `test_approve_writes_all_fields` | PASS (sha256 khớp `sha256_file`, `--by` 500 ký tự → lưu 200) |
| Idempotent exit 0 | `test_approve_is_idempotent` | PASS (lần 2 in "đã duyệt lúc …", timestamp không đổi) |
| Cảnh báo nhưng vẫn ghi | `test_approve_warns_but_records` | PASS (sai lane + plan trước spec → stderr cảnh báo, state vẫn true, rc 0) |
| `set` ghi được field duyệt | `test_cli_can_set_approval_keys` | PASS (test "bảo vệ" cũ đã đảo chiều) |
| `load()` bù khoá schema 2 | `test_load_backfills_approved_by` | PASS |
| stop_gate không còn kiểm dòng mời | `TestStopGateNoInviteCheck` (5 test) | PASS (sai lane/thiếu mode/duyệt lại → im lặng; log cũ → vẫn block) |
| prompt_context nhắc ghi nhận duyệt | `test_plan_pending_hint_has_mode`, `test_full_pending_spec_approval`, `test_quick_unapproved` | PASS (có `approve`, `--mode`, `--by`, `HỎI`) |
| E2E cả 2 lane theo CLI mới | `test_e2e_chain.py` | PASS |

## 2. Cấu hình

- `grep -rn '"deny"' hooks/ scripts/` → không còn kết quả.
- `hooks/hooks.json`: không còn mục `UserPromptExpansion` (`grep -c` = 0 trên bản cài).
- `claude plugin validate . --strict` → ✔ Validation passed.
- `claude plugin update tdq-workflow@tdq-local` → 0.1.8 → **0.2.0** (user scope).

## 3. Smoke bản cài 0.2.0 (chạy trên cache `~/.claude/plugins/cache/tdq-local/tdq-workflow/0.2.0`)

| # | Kiểm | Kết quả |
|---|---|---|
| a | Edit `src/a.py` khi lane quick chưa duyệt | `permissionDecision: "allow"` + `additionalContext` nhắc trình mini-plan và chạy `approve quick --by` |
| b | `approve quick` hai lần | lần 1 `✅ Đã ghi nhận …` rc 0; lần 2 `ℹ️ … đã duyệt lúc …` rc 0 |
| c | Stop hook khi repo đổi mà log cũ | `{"decision":"block", …}` — vẫn chặn đúng |
| d | `approve_gate.py` trong cache | không tồn tại (đã xoá khỏi package) |

## 4. Kết luận

**PASS** toàn bộ DoD §5 của spec. Không có bug mở. Rủi ro đã ghi nhận (không phải bug): state duyệt nay do Claude ghi — dấu vết còn lại là `*_approved_by` + working log; nếu về sau thấy Claude tự suy diễn duyệt, bước siết tiếp theo là `permissionDecision: "ask"` chứ không quay lại `deny`.
