# Brief — Eval chỉ kích hoạt khi người dùng yêu cầu và đồng ý

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay bây giờ mở request updatye lại là eval sẽ không tự động mở, chỉ kích hoạt khi người dùng yêu cầu và đồng ý kích hoạt

**Đọc lần đầu:**
- Mục tiêu: eval hành vi skill (eval-plan, gate `implement`/`report`, `pre_report`) chuyển từ tự động bật khi đổi skill/hook/plugin sang opt-in: chỉ chạy khi người dùng yêu cầu và xác nhận kích hoạt.
- Điểm chạm đã thấy: `scripts/tdq_state.py` (Gate `implement` L2259, Gate `report` L2293), `scripts/tdq_eval_contract.py` (`_gate`, `_valid_waiver`), CLI `eval-waive`, `skills/tdq-build/references/skill-eval.md`, câu "Skill changes require valid eval-plan" trong `skills/tdq-build/SKILL.md`, intake brief mục "eval need".
- Eval need: request này sửa hành vi gate/skill nên theo luật cũ cần eval-plan; theo chính yêu cầu mới, eval không tự mở, nên không tự kích hoạt cho request này trừ khi người dùng đồng ý.
- Chưa rõ: (1) cách ghi đồng ý kích hoạt (cờ state riêng hay lệnh `eval-enable`); (2) gate khi chưa kích hoạt: bỏ qua hẳn hay ghi `NOT_ENABLED`; (3) giữ `eval-waive` hay thay bằng cờ; (4) phạm vi: chỉ eval hành vi skill hay cả `tdq_skill_eval`/audit khác.

## Hiểu & kiến thức

### Năng lực dùng được
| Năng lực | Verdict | Lý do |
|---|---|---|
| `tdq-spec`, `tdq-plan`, `tdq-build` | DÙNG | pipeline deep của request |
| `tdq-lean` | DÙNG (review) | giữ diff nhỏ nhất |
| `tdq-browser-*`, `tdq-setup`, `tdq-status`, skill ngoài (dataviz, claude-api…) | BỎ | không liên quan |

### Bảng đối chiếu vùng chạm
| Vùng file chạm | Phát hiện qua lớp nào | Tác động & quan hệ |
|---|---|---|
| `scripts/tdq_state.py` `_chan_eval_plan_chua_co` (L2258), `_chan_eval_evidence_chua_co` (L2292), `_cli_eval_waive` (L2353), gọi trong `cli()` L2803-2814, usage L101, default state L286-287 | Grep + LSP + Graphify (`affected`: chỉ `cli()` gọi) | Hai gate chặn `set phase=implement/report` khi `Chạm:` có skill/hook/plugin mà thiếu `eval_plan_file`/`eval_waiver` |
| `scripts/tdq_eval_contract.py`, `scripts/tdq_skill_eval.py` | Grep + Graphify | Logic phân loại/kiểm chứng độc lập, KHÔNG sửa; `tdq_skill_eval.py` vẫn chạy tay khi cần |
| `tests/test_eval_workflow_gate.py` (4 test) | Grep | đổi 2 test gate, xóa test waiver, thêm test `eval-enable` |
| `skills/tdq-build/SKILL.md:72`, `references/qc.md:114`, `references/skill-eval.md` | Grep | câu "skill changes require eval-plan" phải thành opt-in |
| `skills/tdq-spec/SKILL.md:28`, `references/spec-template.md:125`, `skills/tdq-plan/SKILL.md:48`, `skills/tdq-intake/SKILL.md:46` | Grep | còn ép "eval-plan if skills change", "eval need" |
| `docs/tdq/audit/luat-hien-co.md`, `token-budget.json`, `phases.md` | Grep | neo luật/ngân sách token cập nhật sau khi sửa luật |

### Quyết định đã chốt
- **Cờ `eval_enabled` trong state (hỏi 1a):** lệnh mới `tdq_state.py eval-enable --by "<lời người dùng>"` ghi `eval_enabled` = {by, at}. Chưa có cờ thì cả hai gate bỏ qua (return). Có cờ thì gate chạy như cũ (cần `eval_plan_file`, chứng cứ `pre_report`).
- **Bỏ `eval-waive` (hỏi 2b):** mặc định gate đã tắt nên miễn là thừa; xóa `_cli_eval_waive`, dòng dispatch, usage, khóa `eval_waiver`, test waiver. State cũ còn khóa `eval_waiver` thì bỏ qua, không lỗi.
- **Agent không tự nhắc eval (hỏi 3a):** luật skill chỉ ghi "eval: chưa kích hoạt (opt-in)" trong report; chỉ khi người dùng nhắc tới eval thì hỏi một câu xác nhận rồi mới `eval-enable`. Bỏ "eval need" khỏi brief, "eval-plan" khỏi chuẩn spec/plan.
- **QC `full` (hỏi 4a).**
- Không đụng `tdq_eval_contract.py`, `tdq_skill_eval.py`, CI.
- Loại bỏ: giữ `eval-waive` (thừa); B chỉ-dựa-`eval_plan_file` (không lưu lời đồng ý).

### Lộ trình
| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| analyze → spec → plan → implement → qc → report | CÓ | khung bất biến |
| research ngoài | BỎ | thuần nội bộ, không ẩn số ngoài |
| QC độc lập bằng agent | BỎ | muc_qc=full, không phải ultra |
| Workflow implement | BỎ | một file code hot (`tdq_state.py`) + vài file luật, một chủ ghi |

## Hỏi đáp
1. Cách ghi đồng ý kích hoạt → A: lệnh `eval-enable --by`, cờ `eval_enabled` trong state. (user: `1a`)
2. `eval-waive` → B: bỏ hẳn lệnh và test. (user: `2b`)
3. Agent khi chưa nhắc eval → A: không tự đề xuất; nhắc thì hỏi xác nhận một câu. (user: `3a`)
4. QC → A: `full`. (user: `4a`)
