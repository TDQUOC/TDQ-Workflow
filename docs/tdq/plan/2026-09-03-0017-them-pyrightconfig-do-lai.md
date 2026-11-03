# QUICK — Thêm pyrightconfig, đo lại LSP

**Ngày:** 2026-09-03 · Brief: ../brief/2026-09-03-0017-them-pyrightconfig-do-lai.md · Lane: quick
**Trạng thái:** XONG
**Ước tính sẽ dùng skill:** tdq-lsp-setup
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Phạm vi
- Trong: thêm thật `pyrightconfig.json` ở gốc repo, khai `include` + `extraPaths` cho
  `scripts/` và `hooks/scripts/`. File này GIỮ LẠI.
- Trong: đo lại 3 loại truy vấn của báo cáo `2026-09-02-2057` bằng LSP sau khi có cấu hình,
  so với số cũ trên cùng ground truth (27 lệnh gọi ở 12 file, dựng bằng AST, dùng lại).
- Trong: làm rõ vì sao bản thử tạm thiếu `tdq_team.py`, `tdq_timing.py`, `tdq_checkstatus.py`.
- Trong: báo cáo `docs/tdq/report/2026-09-03-0017-them-pyrightconfig-do-lai.md`.
- NGOÀI: **không sửa** `uu-tien-tim-kiem.md` và 5 chỗ móc — user chọn 2c, để sang request
  khác. Không dựng lại bundle portable, không thêm bậc vào `tdq_lsp.py`.
- Bỏ B0: tiền lệ liền trước, hai báo cáo hôm nay chạm đúng khu vực này.
- Bỏ B2: không có ẩn số ngoài repo; nghiên cứu ngoài đã làm ở request 2057.

## Task
- [x] **T1** Thêm `pyrightconfig.json`, khởi động lại server — Test: `list_workspace_folders`
  trả về gốc repo và `find_callers` trên `scripts/tdq_state.py:303` trả **> 13** ký hiệu
  - Chạm: `pyrightconfig.json`
- [x] **T2** Kiểm không hồi quy — Test: `python3 -m pytest tests/ -q` không vượt mốc đỏ
  **101 fail**, không file mới vào bảng lỗi
- [x] **T3** Đo lại 3 loại truy vấn bằng LSP (tên chính xác · khái niệm · quan hệ), và phân
  biệt hai giả thuyết về 3 file còn thiếu — Test: mỗi loại có output thật và con số recall
  trên cùng ground truth, dán vào báo cáo
  - Chạm: `docs/tdq/report/2026-09-03-0017-them-pyrightconfig-do-lai.md`
- [x] **T4** Viết báo cáo: bảng trước/sau, kết luận số "bỏ LSP mất bao nhiêu" có đổi không,
  khuyến nghị cho request sửa luật — Test: `python3 scripts/doc_lint.py docs/tdq/report`
  thoát 0
  - Chạm: `docs/tdq/report/2026-09-03-0017-them-pyrightconfig-do-lai.md`

## Definition of Done
- `pyrightconfig.json` tồn tại ở gốc repo và `find_callers` thấy caller ngoài file.
- `pytest tests/ -q` không vượt mốc đỏ 101 fail, không file mới vào bảng lỗi.
- Báo cáo có bảng trước/sau cho cả 3 loại truy vấn, cùng ground truth, kèm output thật.
- Nói rõ 3 file còn thiếu là do đâu, hoặc ghi thẳng là chưa xác định được.
- `doc_lint.py docs/tdq/report` thoát 0; `git status --porcelain` không hiện file nào trong
  `skills/`.

## QC
- Q1 test từng task: **PASS** — T1 `find_callers` trả 35 ký hiệu (mốc cũ 13), có caller ngoài
  file. T2 `pytest tests/ -q` → **101 failed / 1453 passed**, đúng mốc đỏ, không file mới.
  T3 đo đủ 3 loại truy vấn, có số recall trên cùng ground truth. T4 `doc_lint.py
  docs/tdq/report` → exit 0.
- Q2 DoD "cấu hình tồn tại và `find_callers` thấy caller liên file": **PASS** —
  `pyrightconfig.json` ở gốc repo; độ phủ 15/15 file.
- Q3 DoD "pytest trong mốc": **PASS** — 101 fail y hệt mốc, bảng file đỏ không có tên mới.
- Q4 DoD "báo cáo có bảng trước/sau cho cả 3 loại truy vấn": **PASS** — mục 3.1, 3.2, 3.3.
- Q5 DoD "3 file thiếu được lý giải hoặc ghi rõ chưa xong": **PASS** — mục 3.1: cả ba chưa bao
  giờ thiếu; là lỗi đọc output của tôi, đã ghi thẳng vào báo cáo.
- Q6 DoD "doc_lint exit 0 và `git status --porcelain` không hiện gì trong `skills/`": **PASS**.
- Phát sinh: ground truth dựng lại cho **15 file** chứ không phải 12 như số cũ — bản đếm cũ bỏ
  sót nhóm hook gọi `load(cwd)` dạng tên trần. Đã dùng số 15 để chấm, ghi rõ ở mục 2.
- Phát sinh: thêm khoá `exclude` cho 3 bundle portable, không có trong plan. Thêm vì nếu không
  thì kết quả tìm tên lẫn bản sao portable — đúng loại nhiễu báo cáo 2057 đã ghi nhận.
