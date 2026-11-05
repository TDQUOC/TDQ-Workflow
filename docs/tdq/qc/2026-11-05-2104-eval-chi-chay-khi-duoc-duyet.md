# QC — Eval chỉ chạy khi người dùng yêu cầu và đồng ý

Ngày: 2026-11-05 · Plan: ../plan/2026-11-05-2104-eval-chi-chay-khi-duoc-duyet.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả thật | Trạng thái |
|---|---|---|---|---|
| Q1 | `eval-enable` ghi `by`, `at`; thiếu `--by`/chưa init bị từ chối | `python -m pytest tests/test_eval_workflow_gate.py -q` | 10 passed/5,06s; test `test_eval_enable_records_by_and_at`, `test_eval_enable_requires_by`; probe CLI trong thư mục chưa init: hai trường hợp rc=2 | PASS |
| Q2 | Chưa bật: hai gate không chặn | Cùng lượt `python -m pytest tests/test_eval_workflow_gate.py -q` | `test_implement_requires_eval_plan_when_behavioral_targets_present` (nhánh chưa bật) và `test_report_gate_skipped_without_eval_enable` đạt | PASS |
| Q3 | Đã bật: chặn thiếu plan/chứng cứ | Cùng lượt `python -m pytest tests/test_eval_workflow_gate.py -q` | Nhánh đã bật trong `test_implement_requires_eval_plan_when_behavioral_targets_present` chặn thiếu plan; `test_report_gate_blocks_when_evidence_missing_or_incomplete` chặn thiếu chứng cứ; đều đạt | PASS |
| Q4 | Bỏ `eval-waive`; state cũ vẫn đọc | Cùng lượt `python -m pytest tests/test_eval_workflow_gate.py -q` | `test_eval_waive_command_removed` và `test_legacy_eval_waiver_key_is_ignored` đạt; probe lệnh cũ trả rc=2 | PASS |
| Q5 | 7 file luật, chỉ mục, ngân sách, `phases.md` | `python scripts/tdq_test.py vung-cham --files skills/tdq-build/SKILL.md skills/tdq-build/references/qc.md skills/tdq-spec/SKILL.md scripts/tdq_state.py`; `python scripts/doc_index.py --kiem` (7 file); `python scripts/token_budget.py --kiem`; `python scripts/doc_lint.py --pair <spec> <plan>` | Vùng chạm PASS: 2.068 passed, 2 skipped, 1.150 subtests/412,34s; 2.070 case ID, `details_complete=true`, fingerprint trùng. Test luật opt-in có trong 10 passed; `doc_index`, `token_budget`, `doc_lint` exit 0. `phases.md` không đổi vì `PHASE_TABLE` không đổi. | PASS |
| Q6 | Hồi quy toàn repo, CI/hợp đồng eval không đổi | `python scripts/tdq_test.py tron-bo --workers 1 --fresh --reuse off`; `git diff dev...HEAD --name-only -- scripts/tdq_eval_contract.py scripts/tdq_skill_eval.py scripts/tdq_eval_hosts.py .github/workflows/test.yml` | PASS: 4.168 passed, 7 skipped, 2.724 subtests/788,96s; 4.175 case ID; `details_complete=true`; `action=executed`, `receipt_reason=fresh`; `source_before.key=source_after.key=4c180f920d8b4c16d8c34bf22bc3c3eef53c077d62ec9ad0227969b8523216ea`; diff của bốn file cấm rỗng | PASS |
| QC-F1 | Full fresh cuối và sổ lượt | Cùng receipt Q6; `python scripts/tdq_test.py so --json` | `tron_bo=1`, `bo_sot=0`, `radius_complete=false`; lượt cuối `executed=1`, `reused=0`, `joined=0`. Không suy `bo_sot=0` là bán kính hoàn chỉnh. | PASS phạm vi đã đo |
| QC-F2 | Hồi quy vùng chạm | Receipt Q5 và Q6; `python -m pytest tests/test_eval_workflow_gate.py -q` | Vùng chạm 2.070 case ID PASS; full 4.175 case ID PASS; 10 test gate PASS. Không có node runtime vùng chạm thiếu test. | PASS |
| QC-F3 | Ràng buộc kiến trúc | Diff nguồn; `python scripts/doc_lint.py --pair <spec> <plan>` | Spec §5 ghi không đổi tầng/lệnh gọi; giữ `tdq_eval_contract.py`, `tdq_skill_eval.py`, CI nguyên vẹn. | PASS |
| QC-F4 | Clean code/lean | Rà diff `dev...HEAD` và 5 câu trong `skills/tdq-conventions/references/clean-code.md` | SRP CÓ — lệnh mới chỉ ghi cờ; OCP CÓ — tái dùng cơ chế gate/CLI hiện có, không thêm abstraction; LSP CÓ — cùng kiểu trả về/lỗi với lệnh cũ; ISP CÓ — `cwd`, `rest` được dùng; DIP CÓ — ghi state qua CLI/save có sẵn. Lean already. Ship. | PASS |

## Bằng chứng

- Full fresh: `../cache/test-runs/bb382e4ee6a1d168/60e4979e5b254809986a0ce944a72466/result.json`, SHA256 `3166a7ee6345b20d0a4268c2cf5dc229e88ac7949a8272e18ef8f82763fac6c9`.
- Vùng chạm cuối: `../cache/test-runs/bb382e4ee6a1d168/67cd906a2c6e4e478381ecc36dbe258e/result.json`, SHA256 `ff372a5c731cd366dc0e35e40749c3367bc066596627c242e7566892e5b8bb8a`.
- Lượt vùng chạm đầu FAIL (`test_doc_lint.py`) vì `qc.md` vượt 3500 token và token budget cũ; đã rút câu và khóa lại budget. Lượt đó bị sửa nguồn cùng lúc nên không dùng làm verdict. Lượt vùng chạm cuối PASS trên nguồn ổn định; 96 test liên quan + 59 subtests PASS/12,49s trước lượt cuối.
- Eval của request này **chưa kích hoạt (opt-in)**; không tạo eval-plan, không chạy model trial; full pytest không phải chứng cứ hiệu quả model. Bản xem trước spec planned bị stale sau thay đổi nguồn; không coi là bằng chứng nghiệm thu.

## Lệch spec chờ duyệt

Không có.

## Kết luận

Q1–Q6 và QC-F1–F4 PASS trong phạm vi đo được. Eval chưa kích hoạt theo yêu cầu; không gán kết luận hiệu quả model. CI không đổi; `radius_complete=false` được giữ rõ trong báo cáo.
