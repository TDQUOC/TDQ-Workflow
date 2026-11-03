# QUICK — Đo precision, recall và ranking Graphify
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
**Ngày:** 2026-10-20 · Brief: ../brief/2026-10-19-2352-do-precision-recall-ranking.md · Lane: quick
**Trạng thái:** HOÀN THÀNH — “duyệt nhanh”, QC full · Ước tính đã dùng skill: dataviz (cập nhật bảng HTML)

## Phạm vi
- Trong: graph Photoboth360 hiện có; 11 file JS nghiệp vụ nodeserver, 12 truy vấn tính năng; imports_from và contains/functions; raw logs, FP/FN, precision/recall/F1 và ranking; cập nhật HTML.
- NGOÀI: không rebuild graph/call API, không sửa Graphify/source Photoboth360, không đo token A/B hoặc suy rộng toàn repo; giữ nguyên audit cũ chưa commit.
- Bỏ B0: harness/audit/HTML sẵn có; cần oracle nghiêm ngặt mới, không tái sử dụng substring PASS cũ làm relevance.
- Bỏ B2: đã đọc mã package cài đặt, xác định scorer và BFS context; không có ẩn số cần tra web. Bỏ scope round vì tập đo gọn, đầu ra đã rõ.
- Gold set độc lập output, ghi path/symbol/dòng và hash source/graph/package; đóng băng trước chạy; dữ liệu thiếu thì báo thiếu, không đổi đáp án để tăng điểm.
- Ngoài 11 file là unjudged; báo tỷ lệ judged, không coi là FP. Precision/recall công bố là scoped; số full-graph ranking chỉ chấm trong phạm vi đã gán nhãn.
- CLI NODE là traversal context, không phải ranking. Đo riêng `_score_nodes` nội bộ; khử trùng file bằng vị trí đầu, nêu score và ties; đo P@5/Recall@5/Hit@5/MRR@10 có tên rõ phạm vi.
- Timeout/parse error báo ERROR và tỷ lệ lỗi, không giả thành tập rỗng; graph/source thay đổi giữa chạy thì kết quả không hợp lệ, giữ log để điều tra.

## Task
- [x] **T1** Đọc đủ 11 file, tạo gold set 12 queries và tập cạnh chuẩn; đóng băng hash trước xem output — Test: source evidence tồn tại, query có relevant/nonrelevant, không node ID lấy từ graph làm oracle.
  - Chạm: `evals/photoboth360_precision_gold.json`
- [x] **T2** Viết harness và kiểm công thức/parser bằng fixture; chạy offline graph/CLI, lưu raw và tổng hợp — Test: fixture TP/FP/FN, zero denominator, dedup/ties/error; chạy harness đầy đủ, xác minh hash trước/sau.
  - Chạm: `evals/audit_photoboth360_precision.py`, `evals/test_photoboth360_precision.py`, `evals/photoboth360_precision_logs.jsonl`, `evals/photoboth360_precision_summary.md`
- [x] **T3** Cập nhật HTML với kết quả mới và giới hạn; nghiệm thu QC — Test: số liệu khớp logs, HTMLParser, link nguồn tồn tại, doc_lint brief/plan.
  - Chạm: `docs/tdq/reports/graphify-danh-gia-nhanh.html`, `docs/tdq/plan/2026-10-19-2352-do-precision-recall-ranking.md`

## Definition of Done
- Q1 Gold set 11 file/12 truy vấn có chứng cứ và hash, không sửa sau xem output; chốt edge semantics và universe — kiểm validator source/hash.
- Q2 Mỗi phép đo có expected/actual, TP/FP/FN cụ thể, unjudged, raw stdout/stderr hoặc scored list, latency/error và fingerprint — kiểm schema logs.
- Q3 Có micro/macro precision/recall/F1; P@5/Recall@5/Hit@5/MRR@10 của scorer scoped; chỉ số CLI context tách riêng, denominator/ties/zero cases ghi rõ — unit tests và chạy harness.
- Q4 Kết quả đỏ vẫn báo trung thực, không ngưỡng PASS cho chất lượng Graphify; HTML khớp kết quả và nguồn; doc_lint 0 lỗi — đối chiếu logs/HTML.

## QC vòng 1 — fix
- [x] **QC1.1** Ghi latency tổng cho mỗi record truy vấn và tái tạo log chính, giữ bản log trước sửa — Test: mọi record imports/functions/query có `latency_ms`; integrity và gold hash đạt.
  - Chạm: `evals/audit_photoboth360_precision.py`, `evals/photoboth360_precision_logs.jsonl`, `evals/photoboth360_precision_logs.pre-query-latency.jsonl`, `docs/tdq/plan/2026-10-19-2352-do-precision-recall-ranking.md`

## QC
- T1 PASS: 11 source hashes/12 evidence sets và literal import inventory khớp; frozen gold SHA256 `ce0f5e3a21d420d1e8289dbebc146888a4f9680ff029e161fa861d360edaf1fa` trước query output.
- T2 PASS: hai lần chạy cùng gold, 12 unit tests PASS và 12 CLI queries OK mỗi lần; integrity trước/sau khớp. Lần đầu lưu `.initial.jsonl`, log chính có raw stdout/stderr, source snapshots, evidence và latency; số đếm không đổi.
- Kết quả giữ nguyên: imports TP57/FP0/FN5; callable inventory TP22/FP0/FN5; scorer scoped top5 TP12/FP30/FN2; CLI context TP4/FP14/FN10. Không đổi gold.
- T3 PASS: HTML links/IDs valid; số liệu hiển thị khớp benchmark summary đã parse; integrity record hiện diện; doc_lint 0 lỗi. Lần validator đầu so chuỗi với JSON pretty-print sai định dạng, đã đổi thành so dữ liệu parse, không đổi số liệu/HTML.
- QC1.1 PASS: log cũ thiếu query total latency được bảo toàn ở `.pre-query-latency.jsonl`; 34 measured records trong log chính đều có latency và integrity retained. Rerun 12 tests + 12 queries không đổi kết quả.
- QC cuối PASS: `python evals/test_photoboth360_precision.py` → 12 tests OK; schema logs 36 records/34 latency/frozen gold/integrity đạt; HTML links/anchors đạt; `doc_lint` → 0 violation(s). Ruff/HTMLHint không cài, browser runtime không chạy theo QC full.
- Ruff không cài nên chưa kiểm; 12 fixture tests và complexity screen nội bộ đạt (mọi function ≤10 branch/comprehension nodes). Không runtime trình duyệt/HTMLHint theo QC full.
