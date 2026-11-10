# BRIEF — Gate cứng cho Trước/Sau + sơ đồ Archify ở spec và report (`2026-11-09-0143-gate-truoc-sau-archify` · full · feature/gate-truoc-sau-archify)
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> "sao từ bản này tôi ko thấy ở spec và report có phân biệt trước và sau request và flow diagram nữa? hãy check từ play3clone project để lấy làm example?" → "1a" (mở request deep, loại feature).

Đọc ban đầu:
- **Mục tiêu:** spec (lane full) và report (cả 2 lane) không thể đi qua cổng khi thiếu phần Trước/Sau + sơ đồ luồng Archify đã render/verify.
- **Phạm vi:** `scripts/tdq_state.py` (gate `approve`, `set phase=idle`), có thể `scripts/doc_lint.py`; tài liệu skill liên quan; test.
- **Ngoài phạm vi:** sửa lại spec/report cũ của play3clone; đổi engine Archify.

## Hiểu & kiến thức

### Bằng chứng (play3clone, điều tra 2026-11-09)
- 6 spec + 11 report từ `11-05-1505` đến `11-07-1649`: đủ §2c Mermaid, `artifacts/<slug>/truoc-sau.archify.md`, `*-preview.manifest.json`, report HTML `data-archify-artifact`.
- 6 spec + 18 report từ `11-08-0005`: 0 Mermaid, 0 trang Trước/Sau, 0 manifest, HTML tự viết (`artifact-design`) hoặc không có.
- Mốc gãy = phiên mới `5c194f0e` (vẫn 0.94.0), không phải đổi version. Phiên này gọi `tdq-spec` 2 lần, `tdq-build` 4 lần; 0 lần render Archify sau request `raw-http-audit`.
- Luật (tdq-spec SKILL bước 1, `archify-ba.md`, `report-template.md` bước 7/7b) vẫn đòi đủ, nhưng chỉ là chữ.

### Gate hiện có (đọc code)
- `_cli_approve` (tdq_state.py:2076) → gate đo duy nhất `_r14_gate` (2048): spec lane full, fail-open khi doc_lint lỗi, escape `--bo-qua-do "<lý do>"` ghi `spec_bo_qua_do`.
- `set phase=...` (2780–2796): `_chan_spec_chua_duyet`, `_chan_worktree_con_mo`, `_chan_eval_plan_chua_co`, `_chan_eval_evidence_chua_co`. Không gate nào ở `report`/`idle` kiểm report.
- `tdq_archify.verify_document_and_manifest(document, manifest, project)` (tdq_archify.py:744) → `status ∈ {current, stale, invalid}` — tái dùng được trực tiếp.
- `doc_lint`: R8 (§3b), R11, R14; không có luật §2c.
- `tdq_finish.step_archify` chỉ cho `docs/architecture/manifest.json` (kiến trúc tổng), không dính spec/report.
- Đường dẫn chuẩn: spec preview `docs/tdq/spec/<slug>-preview.manifest.json`; quick flow `docs/tdq/plan/<slug>-flow.manifest.json`; report `docs/tdq/reports/<slug>.manifest.json` (mẫu thực: request `2026-11-08-1207`).

### Bảng đối chiếu vùng chạm

| Vùng file chạm | Phát hiện qua lớp nào | Tác động & quan hệ |
|---|---|---|
| `scripts/tdq_state.py` `_cli_approve`/`_r14_gate` | Grep + graphify affected (caller duy nhất `cli()`) | thêm gate manifest cạnh R14 |
| `scripts/tdq_state.py` nhánh `set phase` | Grep | thêm gate report khi `phase=idle` |
| `scripts/tdq_archify.py` `verify_document_and_manifest` | LSP open + graphify affected (`handle_verify`) | chỉ gọi, không sửa |
| `scripts/doc_lint.py` | LSP open + Grep | (tùy chọn) luật §2c |
| `tests/test_approve_do_truoc.py`, `test_doc_lint_r14.py`, `test_eval_workflow_gate.py` | Grep | mẫu test gate cần theo |
| `skills/tdq-spec/SKILL.md`, `archify-ba.md`, `tdq-build/references/report-template.md`, `phases` | Read | ghi gate mới vào luật |

### Năng lực dùng được

Phân vân → DÙNG. Kiểm kê ngày 2026-11-09: 11 skill tdq-workflow trên đĩa (lọc), cộng skill built-in trong context.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake / tdq-spec / tdq-plan / tdq-build | plugin:tdq-workflow | NỀN | pipeline đang chạy |
| Đã xét 25 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

### Nghiên cứu ngoài
Bỏ — việc thuần nội bộ, không có ẩn số bên ngoài.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Research web | BỎ | thuần nội bộ |
| Vòng scope | BỎ | phạm vi đã rõ từ điều tra play3clone (3 gate, 1 file chính) |
| spec → plan | CÓ | khung bất biến |
| implement (TDD đỏ→xanh, mode main) | CÓ | 1 file chính + test, không cần chia subagent |
| QC full (vùng chạm + full fresh) | CÓ | `muc_qc=full` |
| QC độc lập (agent) | BỎ | mức full không đòi |
| report MD + Archify HTML | CÓ | khung bất biến; request này tự chịu gate mới (dogfood) |

Luồng nghiệp vụ: (1) gate `approve spec` đòi preview manifest; (2) gate `approve quick` đòi flow manifest; (3) gate `set phase=idle` từ `report` đòi 4 mục + report manifest; (4) lối thoát `archify_bo_qua`.

## Hỏi đáp

- Q1 Gate chặt tới đâu? → **A**: chặn cứng + lối thoát có lý do (ghi state, in report), giống `--bo-qua-do`.
- Q2 Lane express có gate? → **A**: có, `approve quick` đòi `docs/tdq/plan/<slug>-flow.manifest.json` current.
- Q3 Gate report ở đâu? → **A**: `set phase=idle` (từ `report`): `.md` đủ 4 mục + `reports/<slug>.manifest.json` current.
- Q4 Thêm R15 doc_lint cho Mermaid §2c? → **A**: không — manifest đã chứng minh có sơ đồ.
- Q5 Mức QC → **A** `full` (đã `set muc_qc=full`).
- Mốc áp gate: slug ≥ `2026-11-09-0143` (request cũ không bị khóa, như `R14_MOC`).
