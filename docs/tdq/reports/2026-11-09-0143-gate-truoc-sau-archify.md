# Báo cáo: Gate cứng Trước/Sau + sơ đồ Archify (`2026-11-09-0143-gate-truoc-sau-archify`)

Ngày hoàn thành: 2026-11-10 · Lane: full · Mode thực thi: main
Spec: `docs/tdq/spec/2026-11-09-0143-gate-truoc-sau-archify.md`
Plan: `docs/tdq/plan/2026-11-09-0143-gate-truoc-sau-archify.md`

## 1. Trước request (trạng thái/flow)
- Quy định yêu cầu sơ đồ Trước/Sau và 4 phần báo cáo chỉ nằm trong các file tài liệu hướng dẫn (`.md`), không có code kiểm tra tự động tại các cổng duyệt CLI.
- Agent thường xuyên quên hoặc bỏ qua việc render sơ đồ Archify Trước/Sau ở spec (lane full), mini-plan (lane quick) và report (cả 2 lane).
- Lệnh `approve spec` chỉ kiểm tra R14; `approve quick` không kiểm tra sơ đồ; lệnh `set phase=idle` không kiểm tra nội dung report.

## 2. Sau request (trạng thái/flow)
- Bổ sung gate cứng bằng mã nguồn trong `scripts/tdq_state.py`:
  - `_archify_gate`: Bắt buộc file manifest tương ứng (`<slug>-preview.manifest.json` hoặc `<slug>-flow.manifest.json`) phải tồn tại và có trạng thái `current` (hash khớp với tài liệu và artifact) đối với các request mở từ mốc `2026-11-09-0143`. Chặn lệnh `approve spec` (lane full) và `approve quick` (lane express) nếu vi phạm.
  - Cờ khẩn cấp `--bo-qua-archify "<lý do>"`: Cho phép người dùng duyệt vượt gate khi có lý do chính đáng, lưu thông tin vào trường `archify_bo_qua` trong state.
  - `_chan_report_thieu`: Chặn lệnh `set phase=idle` nếu file `docs/tdq/reports/<slug>.md` thiếu bất kỳ mục nào trong 4 mục bắt buộc (*Trước request, Sau request, Đã test, Kết quả test*) hoặc thiếu file report manifest `current` (trừ khi đã có `archify_bo_qua`).
- Cập nhật tài liệu quy định và hướng dẫn: `archify-ba.md`, `archify-quick.md`, `report-template.md` và `phases.md`.

## 3. Đã test gì
- Kiểm thử unit test chuyên biệt `tests/test_archify_gate.py`:
  - Q1: `approve spec` slug mới thiếu/stale manifest bị chặn (exit 1, state không đổi).
  - Q2: `approve spec` có manifest current cho qua.
  - Q3: `approve quick` thiếu manifest bị chặn, có manifest current cho qua.
  - Q4: `--bo-qua-archify` với lý do rỗng bị từ chối; với lý do hợp lệ thì qua và ghi đúng vào state.
  - Q5: `set phase=idle` chặn khi report thiếu file, thiếu mục, hoặc thiếu manifest current; cho qua khi hợp lệ.
  - Q5b: `set phase=idle` với `archify_bo_qua` bỏ qua kiểm tra manifest report nhưng vẫn chặn nếu thiếu 4 mục.
  - Q6: Các request mở trước mốc `2026-11-09-0143` hoặc chưa duyệt gate nào không bị ảnh hưởng.
- Kiểm thử tương thích ngược: `tests/test_approve_do_truoc.py`, `tests/test_e2e_chain.py`, `tests/test_state.py`, `tests/test_phase_table.py`, `tests/test_quick_qc.py`, `tests/test_search_observe.py`.
- Kiểm thử tĩnh: `doc_lint.py skills/` (0 lỗi), `token_budget.py` (khớp hoàn toàn).

## 4. Kết quả test
- `tests/test_archify_gate.py`: 7/7 tests PASS.
- 142 unit tests liên đới vùng chạm: 142/142 tests PASS.
- Test suite lớn (4209 cases): 4207 tests PASS / 2 skip e2e chain cũ đã sửa và pass riêng.
- `doc_lint.py`: 0 vi phạm (exit 0).

## 5. Thời gian thực hiện (Timing)

Request `2026-11-09-0143-gate-truoc-sau-archify` · lane full · opened at 2026-11-09T01:44:08+07:00

| Phase | Wall clock | API request | Tool wait | Background job | Observed union | Unattributed | Times entered |
|---|---|---|---|---|---|---|---|
| idle | 1s | — [partial] | 1s [partial] | — [unavailable] | 1s [partial] | 0s [partial] | 1 |
| analyze | 2h 06min | 6 min [partial] | 17s [partial] | — [unavailable] | 6 min [partial] | 2h [partial] | 1 |
| spec | 16 min | 2 min [partial] | 14s [partial] | — [unavailable] | 2 min [partial] | 14 min [partial] | 1 |
| plan | 32h | 7 min [partial] | 2 min [partial] | — [unavailable] | 9 min [partial] | 31h 51min [partial] | 1 |
| qc | 21 min | 4 min [partial] | 18 min [partial] | — [unavailable] | 21 min [partial] | 4s [partial] | 1 |
| Total | 34h 44min | 18 min [partial] | 20 min [partial] | — [unavailable] | 38 min [partial] | 34h 05min [partial] |  |
<!-- tdq-archify-binding:start -->
<!-- manifest: 2026-11-09-0143-gate-truoc-sau-archify.manifest.json -->
<!-- manifest_digest: 24ddd3a9e4c3cb1a9f1e5d0b6c2e497d7d7645c1db8cc4333ee2c77027e350ef -->
<!-- tdq-archify-binding:end -->