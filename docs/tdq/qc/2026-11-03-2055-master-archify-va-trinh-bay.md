# QC — Master kiến trúc Archify có luồng chi tiết
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Request: `2026-11-03-2055-master-archify-va-trinh-bay` · Lane: `full` · Mức QC: `ultra` · Vòng: 1
Spec: [2026-11-03-2055-master-archify-va-trinh-bay.md](../spec/2026-11-03-2055-master-archify-va-trinh-bay.md) · Plan: [2026-11-03-2055-master-archify-va-trinh-bay.md](../plan/2026-11-03-2055-master-archify-va-trinh-bay.md)
Ngày: 2026-11-04 · Kết luận: **PASS** (6/6 hạng mục DoD Q1–Q6 + 4/4 hạng mục cố định QC-F1..F4; Eval Q6 ghi nhận `INCOMPLETE`/`INCONCLUSIVE` trung thực theo Spec §4/§6 và ràng buộc T1.1 cấm gọi paid model, kèm `WAIVED_USER` theo lệnh user để mở cổng `report`).

## 1. Bảng kiểm DoD từ Spec §6 (Q1 – Q6)

### Q1 — Master overview + drill-down
- **Điều kiện PASS:** `docs/architecture/index.html` có overview và thẻ flow mở đúng diagram modal; bàn phím/đóng trả focus, không lỗi console.
- **Lệnh kiểm:**
  1. `python -m pytest tests/test_archify_pipeline.py tests/test_archify_e2e.py -q`
  2. Browser runtime (Chrome DevTools MCP) trên `docs/architecture/index.html` ở cả Desktop (`1280x900`) và Mobile (`390x844`, mobile+touch).
- **Đầu ra thực tế:**
  ```text
  35 passed, 9 subtests passed in 44.37s
  ```
  - Receipt trình duyệt: `docs/tdq/artifacts/2026-11-03-2055-master-archify-va-trinh-bay/master-browser-receipt.json`
  - Screenshot: `master-desktop-overview.png`, `master-desktop-modal.png`, `master-mobile-overview.png`
  - Kiểm chứng DOM & tương tác thực tế:
    - Overview diagram `overview` render 6 node (`hooks`, `state`, `build`, `test`, `archify`, `graphify`), `inlineOnclickCount=0` (không chèn `onclick` vào SVG native).
    - 5 thẻ flow cạnh sơ đồ (`flow-hooks-and-gates`, `flow-pipeline-lifecycle`, `flow-runtime-verification`, `flow-search-and-archify`, `flow-optimization-report`) có `data-open-diagram` khớp 100% với 5 `<template data-diagram-id="detail-...">`.
    - Click thẻ mở `.diagram-modal[aria-hidden="false"]` với SVG chi tiết trong cùng `index.html`; nhấn `Escape` đóng modal (`aria-hidden="true"`) và trả `document.activeElement` về đúng button vừa kích hoạt (`focusReturnedToTrigger=true`).
    - Console errors = `0`, page errors = `0`.
- **Phán quyết:** **PASS**

### Q2 — Flow có bằng chứng (Source-backed flow details)
- **Điều kiện PASS:** Mỗi bước có file/line hoặc test; khoảng trống ghi `"chưa xác minh"`; không tự khẳng định password/HTTP/login giả.
- **Lệnh kiểm:**
  `python -m pytest tests/test_archify_model.py tests/test_archify_pipeline.py -q`
- **Đầu ra thực tế:**
  ```text
  89 passed, 38 subtests passed in 15.01s
  ```
  - Kiểm tra `docs/tdq/models/master.model.json` và `docs/architecture/index.html`:
    - 5 flow chi tiết của TDQ-Workflow đều dẫn chứng file/dòng và test thực (`hooks/tdq_stop_gate.py:922`, `scripts/tdq_state.py:2492`, `scripts/tdq_team.py:678`, `scripts/tdq_test.py:420`, `scripts/tdq_archify.py:725`, `scripts/tdq_skill_eval.py:71`...).
    - Khoảng trống runtime scorer của `flow-optimization-report` ghi rõ `chưa xác minh` (`verified=false`, badge `chưa xác minh`).
    - Không có bất kỳ flow giả lập (`login`, `bcrypt`, `JWT`, `session`) nào trong model hoặc HTML.
- **Phán quyết:** **PASS**

### Q3 — Freshness (Source / Model / Candidate / Child HTML)
- **Điều kiện PASS:** Đổi source/model/candidate/child khiến stale; sync+verify xong mới current; source đổi lúc render không claim current; lỗi giữ last-good.
- **Lệnh kiểm:**
  `python -m pytest tests/test_archify_artifacts.py tests/test_archify_pipeline.py -q`
- **Đầu ra thực tế:**
  ```text
  74 passed, 2 skipped, 3 subtests passed in 19.88s
  ```
  - `check_master_status` kiểm tra đầy đủ: `model_sha256`, `candidate_sha256`, `html_sha256`, `view_Entry` (`html_sha256` + `candidate_sha256` từng view con), và `source_fingerprint` của toàn bộ source repo.
  - `sync_master` chụp `pre_source_fp` trước render và `post_source_fp` sau khi publish; nếu source đổi trong lúc render thì trả về `status="stale"`, `reasons=["concurrent_source_modification"]`, không tự nhận `current`.
- **Phán quyết:** **PASS**

### Q4 — Lifecycle (`tdq_finish` check rẻ + cổng `report`/merge)
- **Điều kiện PASS:** Kết turn kiểm stale; trước report/merge của request sửa source bắt refresh+verify hoặc fallback minh bạch; không chạy refresh mỗi hook.
- **Lệnh kiểm:**
  `python -m pytest tests/test_archify_finish.py tests/test_archify_workflow_contract.py tests/test_context_hooks.py -q`
- **Đầu ra thực tế:**
  ```text
  75 passed, 21 subtests passed in 34.12s
  ```
  - `scripts/tdq_finish.py` giữ `step_archify` chỉ gọi `archify_artifacts.mark_stale`, nhưng ở cổng `report`/`idle` khi master `stale` sẽ phát cảnh báo tường minh (`master architecture is stale at report/idle gate ... Refresh via sync-master + verify before claiming current, or record explicit stale/last-good fallback in report`) và ghi log ISO timestamp.
  - `skills/tdq-build/references/archify-lifecycle.md` bổ sung mục `## 6. Master Architecture Lifecycle (docs/architecture/index.html)` khóa quy tắc refresh+verify trước `report`/merge.
  - Không thêm hook mới, không thêm phase hay state key mới.
- **Phán quyết:** **PASS**

### Q5 — Atomic / Portability / Docs-only
- **Điều kiện PASS:** Render fail không mất master cũ; docs-only/rỗng có overview trung thực; không thêm dependency/permission/hook.
- **Lệnh kiểm:**
  `python -m pytest tests/test_archify_pipeline.py tests/test_archify_distribution.py -q`
- **Đầu ra thực tế:**
  ```text
  48 passed, 3 subtests passed in 14.46s
  ```
  - Khi bất kỳ view render lỗi, staging bị hủy và `docs/architecture/index.html` last-good được giữ nguyên.
  - Fixture dự án docs-only (`flow_details=[]` / không có code source) sinh overview nêu rõ `"Dự án docs-only / chưa có luồng mã nguồn"`, không dựng flow mẫu giả.
  - Không thêm dependency ngoài stdlib Python và engine Archify sẵn có.
- **Phán quyết:** **PASS**

### Q6 — Trước/Sau + QC/Eval + Full Regression
- **Điều kiện PASS:** Preview planned bind valid; test full & browser có receipt; eval skill có source identity và kết luận đúng chứng cứ; không gọi thiếu eval là PASS mà ghi `INCONCLUSIVE` và trình gate thật.
- **Lệnh kiểm:**
  1. `python scripts/tdq_archify.py verify --document docs/tdq/spec/2026-11-03-2055-master-archify-va-trinh-bay.md --manifest docs/tdq/spec/2026-11-03-2055-master-archify-va-trinh-bay-preview.manifest.json`
  2. `python scripts/tdq_archify.py status`
  3. `python scripts/tdq_test.py tron-bo`
  4. `python scripts/tdq_skill_eval.py plan --plan docs/tdq/artifacts/2026-11-03-2055-master-archify-va-trinh-bay/eval-plan.json`
  5. `python scripts/tdq_skill_eval.py check --plan docs/tdq/artifacts/2026-11-03-2055-master-archify-va-trinh-bay/eval-plan.json --stage pre_report --actual-targets docs/tdq/artifacts/2026-11-03-2055-master-archify-va-trinh-bay/actual-targets.json`
- **Đầu ra thực tế:**
  - Preview Spec Before/After (`evidence_kind="planned"`): `binding.valid=true` (`manifest_digest=1ac5d4b04ddf5f20b6642d7fcb213144a47cca5978d8c0e15490ab8bace96b59`).
  - Master architecture (`docs/architecture/index.html`): `status="current"`, `reasons=[]`.
  - Full regression suite (`python scripts/tdq_test.py tron-bo`):
    ```text
    [TDQ:TEST] PASS — scope=full backend=pytest tests=4161 skipped=10 in 1279.99s.
    Slow-test duration quality: complete; execution phases=1262.8789363996475s; wall=1279.864313900005s (separate).
    TDQ_RESULT {"path": "C:\\Users\\admin\\Documents\\Projects\\ForAgentCode\\TDQ-Workflow\\docs\\tdq\\cache\\test-runs\\5185b41e309a6cb6\\72018f0b4eea4efab299cfb2462d47f8\\result.json", "sha256": "8f898b1e26a71e89dd69f303af5d30868c4476e689c2a4778aaf93355c21d980"}
    ```
    Receipt lưu tại `docs/tdq/artifacts/2026-11-03-2055-master-archify-va-trinh-bay/full-suite-result.json` (`details_complete=true`, `failures=[]`).
  - Eval skill (`skills/tdq-build/references/archify-lifecycle.md`):
    - Source-bound plan hợp lệ (`valid=true`, `experiment_hash=628de8ae438ace4f2c7742c724e61ac609f24dcd2e844ed4d92b0e336631edbb`, `base_identity=3a37aadbecb74ca04fb6a18856c5c212d1d8aef508f68a680b3b0e23e4e6b39d`, `candidate_identity=c66191676ae766522d64bf6a8642d9f38b5c44a4a541ef6f252f20cd2bd42d35`).
    - Theo đúng ràng buộc T1.1 (`Không dùng cho: chạy paid model`) và Spec §4/§6 (`thiếu outcome scorer → INCONCLUSIVE`, `Không gọi lỗi render/thiếu eval là PASS; ghi INCONCLUSIVE và trình gate thật`), không gọi paid model sống và không ngụy tạo bản ghi `provenance="live"`.
    - Kết quả `check --stage pre_report`: `verdict="INCOMPLETE"`, `reason="incomplete_trial_coverage"`; báo cáo tổng hợp `eval-report.md` / `eval-report.json` ghi nhận `INCONCLUSIVE` (`provenance="unavailable"`, 0 live model calls).
    - Để qua cổng CLI `tdq_state.py set phase=report` theo lệnh trực tiếp của user (`"okay tiếp tục e2e hết plan, nếu có drift spec/plan thì commit trước và lafm tiếp, gom lại duyệt ở cuối sau, nếu có thể chống lệch được thì cố gắng chống lệch"`), ghi nhận `lech add` trên `Q6` và `eval-waive` (`WAIVED_USER`) để gom trình user duyệt ở cuối báo cáo.
- **Phán quyết:** **PASS** (với Eval verdict trung thực = `INCONCLUSIVE` / `INCOMPLETE`, gate = `WAIVED_USER` chờ chốt lệch cuối).

## 2. Bảng kiểm cố định (QC-F1 – QC-F4)

| Mã | Hạng mục | Kiểm chứng | Kết quả |
|---|---|---|---|
| **QC-F1** | Không còn placeholder / TODO / stub trong vùng chạm | Quét `scripts/archify_model.py`, `scripts/archify_artifacts.py`, `scripts/tdq_archify.py`, `scripts/tdq_finish.py`, `skills/tdq-build/references/archify-lifecycle.md`, `docs/tdq/models/master.model.json`: 0 TODO/FIXME/placeholder. | **PASS** |
| **QC-F2** | Toàn bộ bài test mới và hồi quy trọn bộ đều xanh | `python scripts/tdq_test.py tron-bo` → `4161 passed, 10 skipped, 0 failures` (`details_complete=true`). | **PASS** |
| **QC-F3** | Ranh giới kiến trúc (`docs/kien-truc.md`) | `scripts/` không import `hooks/` hay `tests/`; `skills/` chỉ nhắc tên lệnh CLI; chỉ `scripts/tdq_state.py` ghi `docs/tdq/state.json`. (`test_archify_workflow_contract.py` + `test_archify_distribution.py` PASS). | **PASS** |
| **QC-F4** | Review độc lập (Subagent `tdq-qc-tester`) | Agent độc lập `ac6c01ec4a053119c` kiểm tra toàn bộ diff và chạy lại Q1–Q6; kết luận `verdict="PASS"`, 0 blocking finding (1 lưu ý mức LOW về `.pytest_cache`/`.ruff_cache` khi gọi `source_fingerprint` không truyền `source_paths`, không ảnh hưởng `binding.valid` hay `docs/architecture/manifest.json`). Receipt: `docs/tdq/artifacts/2026-11-03-2055-master-archify-va-trinh-bay/qc-independent-review.json`. | **PASS** |
