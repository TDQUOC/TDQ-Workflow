# QUICK — Điều tra LSP không thấy caller khác file

**Ngày:** 2026-09-02 · Brief: ../brief/2026-09-02-2255-dieu-tra-lsp-cross-file.md · Lane: quick
**Trạng thái:** XONG
**Ước tính sẽ dùng skill:** tdq-lsp-setup
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Phạm vi
- Trong: chạy thí nghiệm quyết định để phân biệt hai khả năng còn lại ở mục 4 của brief —
  language server không resolve được `import tdq_state`, hay resolve được mà không liên kết
  ngược. Cách phân biệt: tạo tạm cấu hình khai `scripts/` là gốc import, hỏi lại đúng câu
  `find_callers`, **rồi xoá cấu hình đi**, so kết quả trước/sau.
- Trong: xác định language server Python nào đang thật sự phục vụ, vì khả năng liên kết
  liên file khác nhau hẳn giữa các server.
- Trong: ra báo cáo `docs/tdq/report/2026-09-02-2255-dieu-tra-lsp-cross-file.md`: nguyên nhân
  gốc, có sửa được không, và nếu sửa được thì giá phải trả là gì.
- NGOÀI: **không sửa** cấu hình để giữ lại, không thêm bậc 7 vào `tdq_lsp.py`, không sửa
  `uu-tien-tim-kiem.md`. File cấu hình dựng ở thí nghiệm là **tạm và bị xoá trong cùng task**.
- Bỏ B0: có tiền lệ liền trước — báo cáo `2026-09-02-2057` chạm đúng khu vực này hôm nay.
- Bỏ vòng phạm vi: phạm vi là một câu hỏi chẩn đoán duy nhất.

## Task
- [x] **T1** Xác định server Python đang phục vụ và workspace folder nó nhận — Test: có tên
  server cụ thể và danh sách thư mục gốc, dán output thật vào báo cáo
  - Chạm: `docs/tdq/report/2026-09-02-2255-dieu-tra-lsp-cross-file.md`
- [x] **T2** Thí nghiệm quyết định: ghi tạm cấu hình khai `scripts/` là gốc import, restart
  server, chạy lại `find_callers` trên `scripts/tdq_state.py:303`, ghi số file caller tìm
  được, **xoá file cấu hình ngay trong task này** — Test: `git status --porcelain` sau task
  không hiện file cấu hình nào mới; báo cáo có số trước (1/12) và số sau
  - Chạm: `docs/tdq/report/2026-09-02-2255-dieu-tra-lsp-cross-file.md`
- [x] **T3** Viết báo cáo: nguyên nhân gốc, sửa được hay không, giá phải trả, và khuyến nghị
  cho thang `kiem` — Test: `python3 scripts/doc_lint.py docs/tdq/report` thoát 0
  - Chạm: `docs/tdq/report/2026-09-02-2255-dieu-tra-lsp-cross-file.md`

## Definition of Done
- Báo cáo nêu **một** nguyên nhân gốc, kèm bằng chứng phân biệt được hai khả năng ở brief mục 4.
- Có con số caller tìm được trước và sau thí nghiệm, trên cùng câu hỏi, cùng ground truth 12 file.
- Có khuyến nghị rõ: sửa được / không sửa được, và nếu sửa thì đánh đổi gì.
- `doc_lint.py docs/tdq/report` thoát 0 và `git status --porcelain` không hiện file mới ngoài
  `docs/`.

## QC
- Q1 test từng task: **PASS** — T1 `detect_lsp_servers` → pyright-langserver;
  `list_workspace_folders` → `workspace_folders [0]`; `get_server_capabilities` → dán vào
  báo cáo mục 1. T2 `git status --porcelain` sau task **không hiện `pyrightconfig.json`**,
  báo cáo có số trước 13 và sau 34. T3 `doc_lint.py docs/tdq/report` → exit 0.
- Q2 DoD "một nguyên nhân gốc, kèm bằng chứng phân biệt được hai khả năng ở brief mục 4":
  **PASS** — nguyên nhân: thiếu `pyrightconfig.json` khai `extraPaths`. Hai khả năng ở brief
  mục 4 hoá ra là câu hỏi sai: `get_diagnostics` nằm trong `UnsupportedTools`, nên kết quả
  "0 lỗi" chưa bao giờ là bằng chứng. Đã ghi phần sửa sai này ở mục 2 của báo cáo.
- Q3 DoD "con số caller trước và sau, cùng câu hỏi, cùng ground truth": **PASS** — bảng A/B/A
  ở mục 3: 13 → 13 (chỉ thêm workspace folder) → 34 (có cấu hình) → 13 (xoá cấu hình).
- Q4 DoD "khuyến nghị rõ: sửa được / không, đánh đổi gì": **PASS** — mục 4: sửa được bằng một
  file `pyrightconfig.json`, không đổi code.
- Q5 DoD "`doc_lint.py docs/tdq/report` thoát 0, `git status --porcelain` không file mới ngoài
  `docs/`": **PASS** — lint exit 0; git chỉ hiện `docs/` và 3 file `graphify-out/` đã bẩn từ
  trước request này.
- Phát sinh: bước A′ (thêm workspace folder mà không đổi kết quả) không có trong plan. Thêm
  vào vì thiếu nó thì không tách được biến, và bước A″ xoá cấu hình cũng vậy — không có nó thì
  không loại trừ được giả thuyết "khởi động lại server mới là nguyên nhân".
