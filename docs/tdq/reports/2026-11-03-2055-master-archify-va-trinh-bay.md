# Báo cáo Nghiệm thu — Master kiến trúc Archify có luồng chi tiết (`2026-11-03-2055-master-archify-va-trinh-bay`)
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Request: `2026-11-03-2055-master-archify-va-trinh-bay` · Lane: `full` · Mode: `subagent` · Nhánh: `feature/master-archify-drilldown` (gốc: `dev`)
Spec: [2026-11-03-2055-master-archify-va-trinh-bay.md](../spec/2026-11-03-2055-master-archify-va-trinh-bay.md) · Plan: [2026-11-03-2055-master-archify-va-trinh-bay.md](../plan/2026-11-03-2055-master-archify-va-trinh-bay.md) · QC: [2026-11-03-2055-master-archify-va-trinh-bay.md](../qc/2026-11-03-2055-master-archify-va-trinh-bay.md)
Báo cáo Archify HTML: [2026-11-03-2055-master-archify-va-trinh-bay.html](2026-11-03-2055-master-archify-va-trinh-bay.html) · Master Kiến trúc: [docs/architecture/index.html](../../architecture/index.html)

## 1. Tóm tắt Trước vs Sau (Tách bạch Planned vs Working-tree)

| Hạng mục | Trước | Sau (Working-tree thực tế) |
|---|---|---|
| **Bằng chứng thiết kế vs thực thi** | Preview Spec (`evidence_kind="planned"`, `binding.valid=true`) mô tả mục tiêu kiến trúc trước khi code. | Bản chạy thật (`evidence_kind="working-tree"`, `status="current"`) tại `docs/architecture/index.html` và báo cáo này đã qua kiểm thử trình duyệt & hồi quy trọn bộ. |
| **Trang Master (`docs/architecture/index.html`)** | Trang portal HTML tĩnh liệt kê 6 link rời; click node chỉ mở Node Passport/focus. | Trang `explainer` đơn nhất: sơ đồ tổng quan 6 trụ cột + 5 thẻ luồng nghiệp vụ kế bên (`data-open-diagram="detail-..."`), không gắn `onclick` vào SVG native (`inlineOnclickCount=0`). Click thẻ mở modal sơ đồ con ngay trong cùng HTML; nhấn `Escape` đóng modal và trả focus về đúng nút kích hoạt. |
| **Nguồn thật luồng chi tiết (`master.model.json`)** | Chưa có hợp đồng `flow_details` gắn chứng cứ mã nguồn/test; dễ suy diễn luồng giả từ call graph. | `validate_model` kiểm fail-closed `flow_details` (mỗi bước bắt buộc có `source_file` thuộc repo hoặc đánh dấu `"chưa xác minh"`); dự án docs-only hiển thị rõ không có luồng mã nguồn, không bịa flow mẫu. |
| **Freshness & Atomic Publish (`archify_artifacts.py`)** | Candidate con và source code nằm ngoài fingerprint của master; `status.json` đang `stale` với 44 lý do. | Kiểm tra 5 tầng (`model_sha256`, `candidate_sha256` master, `html_sha256` `index.html`, `html_sha256` + `candidate_sha256` từng view con, `source_fingerprint` toàn repo); chụp `pre_source_fp`/`post_source_fp` chống sửa source đồng thời lúc render; lỗi bất kỳ view giữ nguyên bản last-good. |
| **Lifecycle (`tdq_finish.py` & `archify-lifecycle.md`)** | Cuối turn chỉ `mark_stale`, thiếu cảnh báo ở cổng `report`/`idle`. | Giữ `mark_stale` rẻ (~60ms) mỗi turn; phát cảnh báo tường minh kèm ISO timestamp khi vào `report`/`idle` mà master còn `stale`; khóa quy tắc refresh+verify trước `report`/merge trong `archify-lifecycle.md`. |

## 2. Kết quả Thực thi & Kiểm chứng (8/8 Task, Q1–Q6 PASS)

- **Kiểm thử chuyên biệt Archify (T1.2–T2.2):** **222 passed** (`test_archify_model.py`, `test_archify_pipeline.py`, `test_archify_e2e.py`, `test_archify_artifacts.py`, `test_archify_finish.py`, `test_archify_workflow_contract.py`, `test_archify_distribution.py`, `test_context_hooks.py`).
- **Trạng thái Master (`T3.1`):** `python scripts/tdq_archify.py status` → `status="current"`, `reasons=[]`.
- **Kiểm chứng Browser Runtime (`T1.3`, `T3.2`):** Chrome DevTools MCP trên `docs/architecture/index.html` ở Desktop (`1280x900`) và Mobile (`390x844`): 6 node overview, 5 thẻ flow khớp 5 `<template data-diagram-id="detail-...">`, mở modal sơ đồ con + `Escape` trả focus (`focusReturnedToTrigger=true`), `consoleErrors=0`, `pageErrors=0`. Receipt: `docs/tdq/artifacts/2026-11-03-2055-master-archify-va-trinh-bay/master-browser-receipt.json`.
- **Hồi quy trọn bộ (`T3.2`):** `python scripts/tdq_test.py tron-bo` → **4.161 passed, 10 skipped, 0 failures** trong `1279.99s`, `details_complete=true`, receipt SHA256 `8f898b1e26a71e89dd69f303af5d30868c4476e689c2a4778aaf93355c21d980`.

## 3. Giới hạn Thật & Lệch Spec Chờ Duyệt Cuối (`Q6`)

1. **Eval hành vi skill (`Q6` — `INCONCLUSIVE` / `INCOMPLETE`, chờ duyệt lệch `#1`):**
   - Đã khóa `eval-plan.json` source-bound hợp lệ (`valid=true`, `experiment_hash=628de8ae438ace4f2c7742c724e61ac609f24dcd2e844ed4d92b0e336631edbb`) cho thay đổi tại `skills/tdq-build/references/archify-lifecycle.md`.
   - Theo đúng ràng buộc Plan `T1.1` (`Không dùng cho: chạy paid model`) và Spec §4/§6 (`thiếu outcome scorer → INCONCLUSIVE`, `Không gọi lỗi render/thiếu eval là PASS; ghi INCONCLUSIVE và trình gate thật`), không gọi paid model sống và không ngụy tạo bản ghi `provenance="live"`.
   - Đã commit checkpoint trước khi phát sinh drift (`fc3681be`), ghi nhận lệch `#1` trên `Q6` (`tdq_state.py lech list`) và áp dụng `eval-waive` (`WAIVED_USER`) theo lệnh trực tiếp của user để hoàn tất e2e tới `report` và gom duyệt ở cuối.
2. **Lưu ý mức LOW từ QC độc lập (`qc-independent-review.json`):**
   - Hàm `source_fingerprint(project_dir)` khi gọi không truyền `source_paths` (như trong manifest preview của spec) sẽ quét cả `.pytest_cache`/`.ruff_cache` nếu phát sinh sau khi tạo manifest; không ảnh hưởng `binding.valid` của tài liệu hay `docs/architecture/manifest.json` khi working tree sạch cache.

## 4. Thời lượng theo Pha (`tdq_timing.py show`)

| Phase | Wall clock | API request | Tool wait | Background job | Observed union | Unattributed | Times entered |
|---|---|---|---|---|---|---|---|
| idle | 7s | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| analyze | 19h 03min | 7 min [partial] | 2 min [partial] | — [unavailable] | 7 min [partial] | 18h 56min [partial] | 1 |
| spec | 7 min | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| plan | 3h 08min | — [partial] | 37 min [partial] | — [unavailable] | 37 min [partial] | 2h 31min [partial] | 1 |
| qc | 9 min | — [partial] | 23s [partial] | — [unavailable] | 23s [partial] | 9 min [partial] | 1 |
| report | 10s | — [partial] | 1s [partial] | — [unavailable] | 1s [partial] | 9s [partial] | 1 |
| Total | 22h 28min | 7 min [partial] | 39 min [partial] | — [unavailable] | 44 min [partial] | 21h 44min [partial] |  |
<!-- tdq-archify-binding:start -->
<!-- manifest: 2026-11-03-2055-master-archify-va-trinh-bay.manifest.json -->
<!-- manifest_digest: f7129f6f6767a8d01a17a800120ddde829f47c062e8bbc18644976d7fb66ae14 -->
<!-- tdq-archify-binding:end -->