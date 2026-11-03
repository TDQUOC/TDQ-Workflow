# QC — 0.1.7 state reset khi có yêu cầu mới

Ngày: 2026-07-28 · Plan: [plan](../plan/2026-07-28-state-reset-on-new-request.md) · Kết quả: **PASS**

| DoD (spec mục 6) | Bằng chứng | Kết quả |
|---|---|---|
| Full suite PASS bằng 1 lệnh | `cd tests && python3 -m unittest discover .` → Ran 77 tests, OK (67 cũ + 10 mới) | PASS |
| `validate --strict` PASS, plugin user-level 0.1.7 | `✔ Validation passed`; `Plugin "tdq-workflow" updated from 0.1.6 to 0.1.7` | PASS |
| Mời duyệt sai lane bị chặn TRƯỚC khi tới tay user (kể cả transcript trễ) | Smoke (a) trên cache 0.1.7: dòng mời ở message TRƯỚC + tool_result + message cuối không mời → `{"decision":"block", … lane full … init …}` | PASS |
| Sau `init` lane quick thì duyệt quick chạy được | Smoke (b): state reset đủ khoá (`previous_request=2026-07-28-kiosk`, phase idle, spec/plan file null, implement_mode null) + cảnh báo `⚠️ Ghi đè…`; smoke (c): `USER APPROVED QUICK PLAN`, rc 0 | PASS |
| Working log đủ | `docs/workinglog/2026-07-28.md` có entry 18:00 + entry kết quả | PASS |
| Không field duyệt nào set được ngoài approve_gate | `test_cli_rejects_protected_keys` (gồm `implement_mode`) vẫn xanh | PASS |

## Edge case đã kiểm
- Lời mời duyệt của **lượt trước** (đã qua 1 prompt user thật) không bị chặn lại — `test_invite_before_previous_user_prompt_is_ignored`.
- `Stop hook feedback` không được coi là prompt user mới → vẫn quét tiếp trong cùng lượt.
- Entry `type=user` mang tool_result (content dạng list) không cắt lượt.
- State schema cũ (thiếu `previous_request`) vẫn nạp được, không mất dữ liệu — `test_load_backfills_missing_keys`.
- `init` lên request đã ở phase `report` và không còn field duyệt → im lặng (không cảnh báo thừa).

## Không đạt / còn nợ
Không có.
