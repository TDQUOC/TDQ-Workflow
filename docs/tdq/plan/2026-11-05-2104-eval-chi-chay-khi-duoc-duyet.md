# PLAN — Eval chỉ chạy khi người dùng yêu cầu và đồng ý

Ngày: 2026-11-05 · Spec: ../spec/2026-11-05-2104-eval-chi-chay-khi-duoc-duyet.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — đề xuất, chờ người dùng chốt; mô phỏng 5 task với hệ số agent 1.5: main 10,2 phút, team 8,2 phút (đội nhanh hơn 2,0 phút). Hai file nóng (`scripts/tdq_state.py`, test gate) vẫn do một chủ ghi theo cụm.
Trạng thái plan: ĐÃ DUYỆT.

## Quy tắc thi hành

- Mỗi task: đánh `[~]` trước, viết test đỏ thật → code tối thiểu → test xanh → `[x]` ngay.
- Không sửa `scripts/tdq_eval_contract.py`, `scripts/tdq_skill_eval.py`, `scripts/tdq_eval_hosts.py`, `.github/workflows/test.yml`. Gate chỉ đổi điều kiện vào, không đổi logic kiểm.
- Eval của chính request này: chưa kích hoạt (opt-in); không gọi `eval-enable`, không tạo eval-plan.
- Một full fresh `tron-bo --workers 1 --fresh --reuse off` duy nhất ở QC-F1 sau khi nguồn ổn định; không chạy full ở implement.
- Preview Trước/Sau đã duyệt: `../spec/2026-11-05-2104-eval-chi-chay-khi-duoc-duyet-preview.html` + manifest; không viết lại để che thay đổi thiết kế.

## Thiết kế Trước vs Sau

| Khía cạnh | Trước | Sau |
|---|---|---|
| Gate `implement`/`report` | Tự chặn khi plan chạm skill/hook/plugin mà thiếu eval-plan hoặc `eval-waive` | Bỏ qua mặc định; chỉ chặn khi đã `eval-enable` |
| Ghi đồng ý | `eval-waive --by` ghi lời miễn | `eval-enable --by` ghi lời kích hoạt; bỏ `eval-waive` |
| Luật skill | "Skill changes require eval-plan" | Eval opt-in; chưa bật thì report một dòng |

## P1 — Gate và lệnh trong state

- [>] **T1.1** (e10m) Red→green: thêm `eval-enable --by`, hai gate bỏ qua khi thiếu `eval_enabled`, bỏ `eval-waive` và khóa `eval_waiver` — Test: `python -m pytest tests/test_eval_workflow_gate.py -q`
  - Chạm: `scripts/tdq_state.py`, `tests/test_eval_workflow_gate.py` → `_chan_eval_plan_chua_co`, `_chan_eval_evidence_chua_co`, `_cli_eval_waive` (thay bằng `_cli_eval_enable`), `cli()` (dispatch + usage), `default_state`; LSP refs + Graphify affected: chỉ `cli()` gọi các hàm này; `tdq_eval_contract.py` chỉ được gọi, không sửa.
  - Ra: `eval-enable` ghi `eval_enabled` {by, at}, thiếu `--by` hoặc chưa init thì lỗi; chưa bật thì `phase=implement|report` qua; đã bật thì chặn như cũ; state cũ có `eval_waiver` vẫn load.

## P2 — Luật opt-in

- [ ] **T2.1** (e12m) Red→green: sửa luật để eval là opt-in, bỏ câu ép eval-plan, thêm câu "eval chỉ chạy khi người dùng yêu cầu và đồng ý; chưa bật thì report ghi một dòng" — Test: `python -m pytest tests/test_eval_workflow_gate.py tests/test_ultracode_contract.py -q`
  - Chạm: `skills/tdq-build/SKILL.md`, `skills/tdq-build/references/qc.md`, `skills/tdq-build/references/skill-eval.md`, `skills/tdq-spec/SKILL.md`, `skills/tdq-spec/references/spec-template.md`, `skills/tdq-plan/SKILL.md`, `skills/tdq-intake/SKILL.md`, `tests/test_eval_workflow_gate.py`
  - Cần: T1.1
  - Ra: không file nào còn ép eval-plan cho đổi skill; có câu opt-in; một test đọc 7 file khẳng định điều này.

## P3 — Chỉ mục và ngân sách

- [ ] **T3.1** (e8m) Đồng bộ chỉ mục luật, ngân sách token và `phases.md` sau khi sửa luật — Test: `python scripts/tdq_test.py vung-cham --files skills/tdq-build/SKILL.md skills/tdq-build/references/qc.md skills/tdq-spec/SKILL.md scripts/tdq_state.py`
  - Chạm: `docs/tdq/audit/luat-hien-co.md`, `docs/tdq/token-budget.json`, `skills/tdq-conventions/references/phases.md`
  - Cần: T2.1
  - Ra: `doc_index.py`, `token_budget.py`, `phases-doc --plugin-root` chạy xong; neo luật khớp dòng mới.

## P4 — QC và báo cáo

- [ ] **T4.1** (e12m) QC full: rà diff, hồi quy vùng chạm, một full fresh cuối, đối chiếu DoD — Test: `python scripts/tdq_test.py tron-bo --workers 1 --fresh --reuse off`
  - Dùng: `tdq-lean`
  - Để: review diff, tìm phần thừa của lệnh/gate mới.
  - Ra: danh sách `delete/shrink` nếu có, hoặc `Lean already. Ship.`
  - Kiểm: `git diff dev...HEAD --stat` chỉ gồm file trong Chạm của T1.1–T3.1.
  - Không dùng cho: sửa code hoặc xóa test.
  - Cần: T3.1
- [ ] **T4.2** (e8m) Báo cáo Markdown + Archify HTML: trước/sau, đã test gì, kết quả; ghi "eval: chưa kích hoạt (opt-in)" — Test: `python scripts/tdq_archify.py verify --document docs/tdq/reports/2026-11-05-2104-eval-chi-chay-khi-duoc-duyet.md --manifest docs/tdq/reports/2026-11-05-2104-eval-chi-chay-khi-duoc-duyet.manifest.json`
  - Cần: T4.1

## Cụm song song & file nóng

- Thứ tự: T1.1 → T2.1 → T3.1 → T4.1 → T4.2. `scripts/tdq_state.py` và `tests/test_eval_workflow_gate.py` là file nóng: một chủ ghi, không giao đồng thời.

## Px — Log & test bắt buộc

- Log service: BỎ — chỉ đổi điều kiện gate và CLI state, không thêm runtime; giữ cơ chế thông báo `_fail`/print hiện có. Unit test nằm ngay T1.1/T2.1; full chỉ ở QC-F1.

## Definition of Done

- [ ] Q1 `eval-enable` ghi `eval_enabled` có `by`, `at`; thiếu `--by` hoặc chưa init thì lỗi — `python -m pytest tests/test_eval_workflow_gate.py -q`
- [ ] Q2 Chưa bật: plan chạm skill vẫn qua `phase=implement` và `phase=report` — `python -m pytest tests/test_eval_workflow_gate.py -q`
- [ ] Q3 Đã bật: thiếu eval-plan chặn `implement`, thiếu chứng cứ chặn `report` — `python -m pytest tests/test_eval_workflow_gate.py -q`
- [ ] Q4 `eval-waive` không còn; state cũ có `eval_waiver` vẫn load — `python -m pytest tests/test_eval_workflow_gate.py -q`
- [ ] Q5 7 file luật không còn ép eval-plan; chỉ mục, ngân sách token, `phases.md` khớp — `python scripts/tdq_test.py vung-cham --files skills/tdq-build/SKILL.md skills/tdq-build/references/qc.md skills/tdq-spec/SKILL.md scripts/tdq_state.py`
- [ ] Q6 Hồi quy toàn repo, CI và hợp đồng eval không đổi — `python scripts/tdq_test.py tron-bo --workers 1 --fresh --reuse off`

Khi nhiều DoD gọi cùng selector mà code chưa đổi, chạy chung một lượt và dán cùng receipt/đầu ra. QC-F1 là nơi duy nhất chạy `tron-bo`.

Tổng ước tính 50 phút tác vụ (không gồm chờ duyệt và chờ full suite).
