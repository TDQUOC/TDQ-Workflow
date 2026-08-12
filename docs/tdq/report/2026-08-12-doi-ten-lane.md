# REPORT — Đổi nhãn lane: `chế độ nhanh (express)` / `chế độ chuyên sâu (deep)`

Ngày: 2026-08-12 · Plan: ../plan/2026-08-12-doi-ten-lane.md · Chế độ: chuyên sâu (deep)

## Đã làm
- `scripts/tdq_state.py`: thêm `LANE_LABELS` + `lane_label()` (nhãn người đọc) và
  `LANE_ALIASES` + `normalize_lane()` (cửa vào duy nhất cho lane user gõ). `init` và
  `approve` nhận bí danh; `USAGE` và `PHASE_TABLE` nói bằng nhãn mới.
- Hook: `prompt_context.py` thêm `APPROVE_FAST` — chỉ nhận `nhanh|express` khi đứng ngay
  sau từ đồng ý; `bash_gate.APPROVE_CLI` nhận `approve nhanh|express`; `_common`
  `APPROVE_HINTS["quick"]` đổi sang `duyệt nhanh`, vẫn nêu `duyệt quick` còn chạy.
- Văn bản: 6 skill `tdq-*`, bản `portable/`, `README.md`, mô tả plugin, 2 script canvas.
  `phases.md` (2 bản) regenerate từ `PHASE_TABLE`.
- `CHANGELOG.md` mục `0.11.4`, `plugin.json` bump `0.11.3 → 0.11.4`.
- Test mới `tests/test_lane_label.py` (14 test, 38 subtest).

## Không đổi (đúng chốt interview)
Giá trị `lane` trong state vẫn `quick`/`full`; 4 khoá `quick_*`; tên file `quick-lane.md`;
70 tài liệu lịch sử trong `docs/tdq/`. Không migrate state, người dùng cũ gõ `duyệt quick`
hay `init <slug> full` vẫn chạy y nguyên.

## Kết quả kiểm
9/9 hạng mục QC PASS (bằng chứng trong mục `## QC` của plan). `python3 -m pytest tests/ -q`
→ `493 passed, 178 subtests passed`. `doc_lint` sạch.

## Rủi ro còn lại
- `nhanh` là tính từ thường gặp. Đã chặn bằng luật "đứng ngay sau từ đồng ý" và 6 ca test
  (2 ca bẫy: "làm nhanh giúp tôi", "ok làm nhanh nhé"). Nếu sau này có câu bẫy dạng khác,
  thêm vào `ApprovalPhraseTest.AM`.
- Nhãn dài hơn từ cũ nên đã phải rút 3 description skill cho vừa ngân sách 900 ký tự;
  lần thêm skill tới sẽ chạm trần sớm hơn trước.

## Việc chưa làm
Chưa commit — chờ user yêu cầu. Cây làm việc còn `graphify-out/*` dirty từ lần rebuild
trước.
