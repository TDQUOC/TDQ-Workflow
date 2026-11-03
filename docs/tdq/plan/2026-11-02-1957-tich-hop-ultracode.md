# PLAN — Tích hợp Ultracode vào TDQ Workflow

Ngày: 2026-11-02 · Spec: ../spec/2026-11-02-1957-tich-hop-ultracode.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — user duyệt; subagent dùng model cc1
Trạng thái plan: HOÀN THÀNH

## Quy tắc thi hành

1. TDQ leader là state/Git writer duy nhất; Workflow agent không gọi state/approval/commit/merge/push.
2. Không token ceiling; mọi route có danh sách hữu hạn và accounting đầy đủ.
3. Không thêm canonical lane/state key/phase/gate/adapter/CLI/worktree manager.
4. `tdq_team.py` là owner duy nhất của implement worktree; không dùng Workflow native isolation.
5. TDD red→green; không commit/push khi chưa được user yêu cầu.

## Thiết kế Trước vs Sau

| Khía cạnh | Hiện trạng (Trước) | Thiết kế mới (Sau) |
|---|---|---|
| Lane | express/deep | Hai lane cũ + modifier `_ultracode`; state vẫn quick/full |
| Express | Agent thủ công | Workflow route hữu hạn, vẫn một gate |
| Deep | Pipeline hiện hữu | Analyze/QC + tùy chọn spec/plan review/implement |
| Read-only | Edit/Write gate, shell còn khe hở | Edit/Bash gate + assigned docs path + structured fallback |
| Implement | TDQ worktrees | Vẫn TDQ worktrees; Workflow chỉ điều phối implementer |
| Token | Có thể có target | Không ceiling; finite route termination |

Preview đã duyệt: `docs/tdq/spec/2026-11-02-1957-tich-hop-ultracode-preview.html`.

## Eval-plan

- Baseline: TDQ main/batch Agent path, cùng case/host/model/tool envelope.
- Candidate: `_ultracode` Workflow routing, không token ceiling.
- KEEP khi tăng unique verified findings/completeness và không tăng false-positive; token/latency chỉ báo cáo.
- Eval-plan: `docs/tdq/artifacts/2026-11-02-1957-tich-hop-ultracode/eval-plan.json`.

## P1 — Modifier và routing

- [x] **T1.1** Parse `_ultracode` từ raw-human input; state CLI chỉ nhận quick/full — Test: `python -m pytest tests/test_ultracode_routing.py -q -k lane`
  - Chạm: `skills/tdq-intake/SKILL.md`, `skills/tdq-intake/references/lane-decision.md`, `tests/test_ultracode_routing.py`
- [x] **T1.2** Express route hữu hạn, fallback/accounting trong mini-plan, không gate mới — Test: `python -m pytest tests/test_ultracode_routing.py -q -k express`
  - Chạm: `skills/tdq-intake/references/quick-lane.md`, `tests/test_ultracode_routing.py`
- [x] **T1.3** Deep Analyze/QC + tùy chọn spec/plan review/implement, không state/gate mới — Test: `python -m pytest tests/test_ultracode_routing.py -q -k deep`
  - Chạm: `skills/tdq-intake/references/analyze-full.md`, `skills/tdq-spec/SKILL.md`, `skills/tdq-plan/SKILL.md`, `skills/tdq-build/SKILL.md`, `tests/test_ultracode_routing.py`

## P2 — Contract, permission và host

- [x] **T2.1** Shared contract: inherited subtask, no state/Git, finite/no ceiling, accounting, assigned report path, structured fallback — Test: `python -m pytest tests/test_ultracode_contract.py -q -k contract`
  - Chạm: `skills/tdq-conventions/references/ultracode.md`, `skills/tdq-conventions/SKILL.md`, `tests/test_ultracode_contract.py`
- [x] **T2.2** Harden Edit/Bash mutation gate; state deny; artifact reports allow — Test: `python -m pytest tests/test_edit_gate.py tests/test_bash_gate.py -q -k ultracode`
  - Chạm: `hooks/scripts/edit_gate.py`, `hooks/scripts/bash_gate.py`, `tests/test_edit_gate.py`, `tests/test_bash_gate.py`
- [x] **T2.3** Interactive/`claude -p`/Agent SDK host contract và denial fallback — Test: `python -m pytest tests/test_ultracode_contract.py -q -k host`
  - Chạm: `skills/tdq-conventions/references/ultracode.md`, `tests/test_ultracode_contract.py`

## P3 — Ownership, QC và eval

- [x] **T3.1** TDQ team owns implement worktrees; no Workflow native isolation — Test: `python -m pytest tests/test_ultracode_contract.py -q -k worktree`
  - Chạm: `skills/tdq-build/references/team-mode.md`, `skills/tdq-conventions/references/ultracode.md`, `tests/test_ultracode_contract.py`
- [x] **T3.2** QC only approved DoD + QC-F1–F4; fail-closed accounting — Test: `python -m pytest tests/test_ultracode_contract.py -q -k accounting`
  - Chạm: `skills/tdq-build/references/qc.md`, `skills/tdq-conventions/references/ultracode.md`, `tests/test_ultracode_contract.py`
- [x] **T3.3** Eval quality-first KEEP/DROP; token only reported — Test: `python -m pytest tests/test_ultracode_contract.py tests/test_eval_workflow_gate.py -q -k eval`
  - Chạm: `skills/tdq-build/references/skill-eval.md`, `skills/tdq-conventions/references/ultracode.md`, `tests/test_ultracode_contract.py`
- [x] **T3.4** Doc index/token/lint dưới trần — Test: `python scripts/token_budget.py --kiem`
  - Chạm: các file luật trên, `docs/tdq/token-budget.json`, `docs/tdq/audit/luat-hien-co.md`
- [x] **Tx.1** Unit test vùng chạm — Test: `python -m pytest tests/test_ultracode_routing.py tests/test_ultracode_contract.py tests/test_edit_gate.py tests/test_bash_gate.py -q`

## P4 — QC ultra

- [x] **T4.1** Interactive runtime probe; unsupported path dùng structured fallback trung thực — Test: `python -c "import json;d=json.load(open('docs/tdq/artifacts/2026-11-02-1957-tich-hop-ultracode/runtime-interactive.json'));assert d['verdict'] in ('PASS','UNSUPPORTED') and (d['complete']==(not d['errors'] and not d['omitted']))"`
- [x] **T4.2** `claude -p` PARTIAL; Agent SDK UNSUPPORTED có evidence — Test: `python -c "import json;d=json.load(open('docs/tdq/artifacts/2026-11-02-1957-tich-hop-ultracode/runtime-hosts.json'));assert all(x['verdict'] in ('PASS','PARTIAL','UNSUPPORTED','DENIED') for x in d['hosts'])"`
- [x] **T4.3** Eval report có quyết định điều kiện — Test: `python -c "assert 'KEEP' in open('docs/tdq/artifacts/2026-11-02-1957-tich-hop-ultracode/eval-report.md',encoding='utf-8').read()"`
- [x] **T4.4** Full suite, lint/token, hook resilience, QC độc lập, visual HTML — Test: `python scripts/tdq_test.py tron-bo`
  - Dùng: `Archify`, `tdq-browser-test` (mcp)
  - Ra: `docs/tdq/qc/2026-11-02-1957-tich-hop-ultracode-preview.png`

## Phục hồi sự cố

- [x] **R1** Khôi phục diff tracked bị reset nhầm; test/lint/token xác nhận không mở rộng phạm vi — Test: `python -m pytest tests/test_ultracode_routing.py tests/test_ultracode_contract.py tests/test_bash_gate.py tests/test_luat_skill.py -q`

## Cụm song song

Một cụm tuần tự sau phục hồi: các task luật dùng chung test/contract nóng; chỉ runtime T4.1 được giao subagent cc1. Thứ tự P1 → P2 → P3 → P4 giữ dependency và tránh hai writer.

## Hợp đồng năng lực

- Dùng: `Workflow`, `workflow-authoring`
  - Để: khảo sát và runtime probe hữu hạn, structured output
  - Ra: runtime receipts + eval report trong artifact request
  - Kiểm: receipts có terminal verdict và accounting
  - Không dùng cho: state/Git ownership hoặc native implement worktree
- Dùng: `tdq-reviewer`, `tdq-qc-tester`, `tdq-implementer`
  - Để: review/QC độc lập và implement có điều kiện trong TDQ worktree
  - Ra: QC verdict + structured fallback
  - Kiểm: evidence có PASS/FAIL/UNSUPPORTED, không giả PASS
  - Không dùng cho: approval/merge/push
- Dùng: `LSP/Graphify/Grep` (mcp)
  - Để: blast radius và chứng minh không cần sửa state schema
  - Ra: vùng file `Chạm:` trong plan
  - Kiểm: `scripts/tdq_state.py` và `scripts/tdq_team.py` không đổi
  - Không dùng cho: mutation
- Dùng: `Archify`
  - Để: preview Trước/Sau đã duyệt
  - Ra: HTML + manifest + ảnh QC
  - Kiểm: browser thấy 4 sơ đồ, console 0 lỗi
  - Không dùng cho: thiết kế khác spec

## Definition of Done

- [x] Q1 Suffix routing canonical hóa, state chỉ quick/full, non-human không kích hoạt.
- [x] Q2 Express route hữu hạn, mini-plan đầy đủ, một gate.
- [x] Q3 Deep route không tạo gate/state mới.
- [x] Q4 State/Git safety và TDQ worktree ownership.
- [x] Q5 Edit/Bash mutation deny, artifact docs allow, state deny, plugin fallback.
- [x] Q6 Completion accounting đầy đủ, thiếu → `complete=false`.
- [x] Q7 Không token ceiling, finite run, không budget loop.
- [x] Q8 Ba host có terminal verdict trung thực.
- [x] Q9 Eval KEEP/DROP quality-first, runtime KEEP còn điều kiện.
- [x] Q10 Regression full suite/lint/budget/hook.
- [x] Q11 Ponytail: không adapter/CLI/state/lane/phase/role/worktree manager mới.
