# QC — Hạn chế ngắt giữa plan

Ngày: 2026-11-06 · Plan: ../plan/2026-11-06-1250-han-che-ngat-giua-plan.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Bằng chứng thực | Trạng thái |
|---|---|---|---|
| Q1 | Stop còn task thì nhắc chính xác; không block pause/`[>]`/ngoài phase | Test đỏ thật 5 failed/15 passed, sau sửa `python -m pytest tests/test_stop_gate.py -q`: 116 passed, 23 subtests; `test_unfinished_uu_tien_task_dang_lam` và ca plan trống/pause/dispatched đạt. | PASS |
| Q2 | Lần bốn hạ cấp, ghi STUCK/task; tick tiến triển reset | Cùng 116 test Stop: `test_unfinished_tran_ba_lan`, `test_unfinished_tran_reset_khi_co_tien_trien` đạt, reason ≤300 ký tự; vùng chạm Stop 379 passed/141 subtests, receipt PASS stable SHA256 `915ef06b82af7da2d44e6ce528b972e6c120bbe5fa1c6a1a78fa05b32e6ff6a8`. | PASS |
| Q3 | Resume/compact nhắc task đang làm/đầu còn mở; `[>]` chỉ chờ | Test đỏ thật 3 failed/5 passed; `python -m pytest tests/test_context_hooks.py tests/test_prompt_context.py -q`: 94 passed, 146 subtests; vùng chạm SessionStart 275 passed/369 subtests, receipt PASS SHA256 `cc7b4415f59d442e59a0fb6b748c7b46198a773785d90d735e4e42e498af0cb3`. | PASS |
| Q4 | Plan/spec/lech/commit giữ gate và pause | Test đỏ thật 1 failed/16 passed; `python -m pytest tests/test_luat_skill.py tests/test_runtime_contracts.py -q`: 29 passed, 329 subtests; `doc_index.py`, `token_budget.py` cập nhật; vùng luật sau rút gọn 593 passed/1 skipped, 625 subtests, receipt PASS SHA256 `fceb4ef21c6cb7541e8b9eb68a403efd5cd4f33c969d1ed3e071b94a232e7213`. | PASS |
| Q5 | `/goal` tùy chọn, không tự bật | Test đỏ thật 1 failed, sau sửa 29 passed/329 subtests; nội dung `skills/tdq-build/SKILL.md` nêu user confirms, task+DoD+QC receipt, chỉ hướng dẫn người dùng tự bật, không tạo session hay model trial. | PASS (hướng dẫn; không thử goal runtime) |
| Q6 / QC-F1 | Full fresh toàn repo | `python scripts/tdq_test.py tron-bo --workers 1 --fresh --reuse off`: 4.180 passed, 7 skipped, 2.724 subtests, 4.187 case ID, 793,74s pytest/800,34s runner; receipt PASS `details_complete=true`, source before/after trùng, `action=executed`, `receipt_reason=fresh`; SHA256 `2da3dd7bc06a44ab91fc0e0fb10a0093e02c0e2fafc9d004172970a86d1c3490`. `git diff --name-only -- hooks/scripts/agy_stop_gate.py .github/workflows/test.yml`: rỗng. | PASS |
| QC-F2 | Hồi quy vùng chạm | Stop 379 PASS, SessionStart 275 PASS, luật 593 PASS/1 skipped; targeted phối hợp 239 passed, 498 subtests; full 4.187 case ID PASS. Hai lượt vùng chạm Stop trước đó INCOMPLETE vì Ruff chạy song song đổi `.ruff_cache`, không dùng làm verdict; lượt cuối nguồn ổn định PASS. | PASS |
| QC-F3 | Kiến trúc | `tdq_team.py audit`: 0 problem; `doc_lint.py --pair` exit 0; không đổi Antigravity/CI, không thêm scheduler/state writer/model call. | PASS |
| QC-F4 | Clean code | SRP CÓ: helper chọn task chỉ đọc plan, hook chỉ quyết định Stop; OCP CÓ trong phạm vi task, reuse `_TASK_LINE`; LSP CÓ: reason vẫn chuỗi/None; ISP CÓ: helper chỉ nhận path; DIP CÓ: hook đọc state qua module chung, không ghi state. Ruff `--select F821,F822` PASS; Ruff toàn file có cảnh báo cũ, không coi lint tổng PASS. Lean: không thêm dependency/config; tránh scheduler thừa. | PASS phần kiểm được |

## Bằng chứng và giới hạn

- Full receipt: `../cache/test-runs/c4c6ae9443193579/5500d4db4f2b4b85b78be8f80122eaf9/result.json`. Sổ `tron_bo=1`, `bo_sot=0` nhưng `radius_complete=false`, không suy số 0 thành bán kính đầy đủ.
- `eval: chưa kích hoạt (opt-in)`. `/goal 1a` do người dùng bật trong session với điều kiện không đo được; không coi đó là bằng chứng Q5 hoặc hiệu quả model. TDQ không tự bật goal; không có thử nghiệm paid-model trong QC.
- Stop chỉ hoạt động khi host phát sự kiện kết lượt. API/tool treo giữa lượt không được cơ chế này cứu. Sau ba lần không tiến triển hook hạ cấp để tránh vòng lặp; không bảo đảm plan luôn hoàn tất.
- Report HTML sẽ kiểm `status=current`, `binding.valid=true` sau render; đây là kiểm artefact, không là browser visual gate.

## Lệch spec chờ duyệt

Không có.

## Kết luận

Q1–Q6, QC-F1–F4 PASS trong phạm vi kiểm; hiệu quả model nhỏ trong thực địa chưa đo. Full fresh trên nguồn ổn định; không chạy lại chỉ để tick DoD.
