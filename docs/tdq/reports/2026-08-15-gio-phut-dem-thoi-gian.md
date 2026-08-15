# REPORT — Slug có giờ phút + đếm thời gian mỗi request và mỗi phase (`2026-08-15-gio-phut-dem-thoi-gian` · lane full · mode main · 14 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 slug `YYYY-MM-DD-HHMM-<kebab>` đồng bộ 9 chỗ luật, `parse_slug()` đọc cả hai
định dạng, `init` từ chối slug ghi mới thiếu giờ phút · P2 `scripts/tdq_timing.py` mới
(`show` | `status` | `close`) đo song song treo tường (mốc state) và model chạy (transcript,
bỏ khoảng chờ > 300 giây) · P3 state schema 4 thêm `started_at` + `phase_history`, `init`
và `tdq_finish --phase idle` tự đóng sổ vào `docs/tdq/timing.jsonl` · P4 khuôn report bắt
buộc mục `## Thời gian`, `tdq-status` in thêm dòng `⏱` · P5 log service + 31 test ·
P6 phát hành 0.20.0.
**Kết quả:** suite 608 → 639 test, không đỏ · `show` trên 18 transcript: 0,80 giây
(trần 2,0) · 269 file tài liệu cũ giữ nguyên tên, vẫn đọc được.
**Kiểm:** `python3 -m pytest -q` → 639 passed, 312 subtests · `doc_lint.py` 13 file exit 0 ·
QC PASS 20/20 hạng mục DoD + QC-F1/F2/F3, 1 defect (QC1.1) phát hiện và sửa trong vòng 1.
**Đầu ra:** `scripts/tdq_timing.py` · `scripts/tdq_state.py` · `scripts/tdq_finish.py` ·
`tests/test_timing.py` · QC: `docs/tdq/qc/2026-08-15-gio-phut-dem-thoi-gian.md`.
**Giới hạn:** request này mở TRƯỚC khi tính năng tồn tại, nên `state.json` không có mốc của
analyze/spec/plan/implement — `started_at` được vá tay về 12:05 (giờ mở request ghi trong
working log), bảng dưới chỉ có phase từ `qc` trở đi. Request kế tiếp sẽ có đủ mọi phase ·
`CHANGELOG.md` chạm trần 500 dòng của doc_lint nên các mục 0.7.0 → 0.11.4 được xoay vòng
sang `docs/archive/CHANGELOG-0.7-0.11.4.md` (không xoá nội dung nào) · clean code TẮT theo
spec §4 nên không chạy `code_rule_scan.py`.
**Git:** chưa commit gì — không có commit gỡ chặn nào trong lượt build này.

## Thời gian

Request `2026-08-15-gio-phut-dem-thoi-gian` · lane full · mở lúc 2026-08-15T12:05:00+07:00

| Phase | Treo tường | Model chạy | Số lần vào |
|---|---|---|---|
| qc | 3 phút | 3 phút | 1 |
| report | 1 giây | 0 giây | 1 |
| **Tổng** | **48 phút** | **47 phút** | |

Hai cột cố ý khác nguồn: treo tường tính cả lúc chờ user duyệt, model chạy chỉ tính lúc máy
làm. Ở request này hai số gần bằng nhau vì phần lớn thời gian là build liên tục; phase nào
lệch lớn về sau nghĩa là phase đó tốn thời gian CHỜ, không phải tốn sức làm.
