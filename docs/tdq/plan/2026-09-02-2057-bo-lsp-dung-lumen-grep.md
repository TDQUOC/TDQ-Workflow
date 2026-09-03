# QUICK — Bỏ LSP chỉ dùng lumen + grep: nên không, mất bao nhiêu

**Ngày:** 2026-09-02 · Brief: ../brief/2026-09-02-2057-bo-lsp-dung-lumen-grep.md · Lane: quick
**Trạng thái:** XONG
**Ước tính sẽ dùng skill:** tdq-lsp-setup
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Phạm vi
- Trong: đo đối chứng thật trên chính repo này — 3 loại truy vấn × 3 lớp (LSP / lumen / grep),
  mỗi lần ghi **trúng hay trượt so với ground truth** và **thời gian thực**.
- Trong: research ngoài (B2) về giới hạn của semantic search so với LSP, giao sub-agent.
- Trong: ra 1 báo cáo `docs/tdq/report/<slug>.md` trả lời rời nhau 3 câu: nên bỏ không · chất
  lượng giảm bao nhiêu (số) · case nào bắt buộc LSP.
- NGOÀI: **không sửa** `uu-tien-tim-kiem.md` hay 5 chỗ móc, không đổi cấu hình MCP/lumen.
  Theo khuyến nghị hay không là quyết định riêng của user → chọn đổi thì mở request thi hành
  sau, như cách 2301 → 2355 đã làm.
- Bỏ B0: có tiền lệ — `2026-08-26-0015-test-ranking-lsp-lumen-grep` chạm đúng khu vực này và
  đã QC PASS. Bỏ vòng phạm vi: câu hỏi của user đóng kín phạm vi, chỉ 1 khu vực.

## Task
- [x] **T1** Truy vấn **tên symbol chính xác** qua 3 lớp (LSP `find_symbol`, lumen
  `semantic_search`, `grep -rn`), ground truth lấy từ file thật — Test: cả 3 lớp có output
  thật dán vào báo cáo, mỗi lớp ghi trúng/trượt + thời gian đo bằng đồng hồ thật
  - Chạm: `docs/tdq/report/2026-09-02-2057-bo-lsp-dung-lumen-grep.md`
- [x] **T2** Truy vấn **khái niệm mơ hồ** (không có tên symbol để bám) qua 3 lớp — Test: như T1
  - Chạm: cùng file báo cáo
- [x] **T3** Truy vấn **quan hệ** ("ai gọi hàm này", "đổi hàm này thì vỡ gì") qua 3 lớp — Test:
  như T1, đếm số caller đúng mỗi lớp tìm được trên tổng ground truth
  - Chạm: cùng file báo cáo
- [x] **T4** B2 research ngoài: giới hạn embedding search với câu hỏi có đáp án đúng duy nhất,
  giao sub-agent, digest ≤ 1.500 ký tự — Test: digest có ≥ 3 nguồn dẫn được
  - Chạm: cùng file báo cáo
- [x] **T5** Viết báo cáo: bảng số T1–T3, tỉ lệ trúng mất đi khi bỏ LSP, danh sách case bắt
  buộc LSP, khuyến nghị dứt khoát — Test: `python3 scripts/doc_lint.py docs/tdq/report` thoát 0
  - Chạm: `docs/tdq/report/2026-09-02-2057-bo-lsp-dung-lumen-grep.md`

## Definition of Done
- Báo cáo có bảng 3 loại truy vấn × 3 lớp, mỗi ô có trúng/trượt và thời gian thực đo được.
- Có **một con số** trả lời "chất lượng giảm bao nhiêu" (tỉ lệ trúng trước/sau), kèm cách tính.
- Có danh sách case bắt buộc dùng LSP, mỗi case nêu lý do lumen+grep không thay được.
- `doc_lint.py docs/tdq/report` thoát 0 và `git status --porcelain` không hiện file nào trong
  `skills/`, `scripts/`, `hooks/`.

## QC
- Q1 test từng task: **PASS** — T1/T2/T3 mỗi lớp đều có output thật dán vào báo cáo mục 1–3
  kèm thời gian kẹp đồng hồ; T4 digest 6 gạch đầu dòng, **6 nguồn** dẫn được (≥ 3 theo yêu
  cầu); T5 `doc_lint.py docs/tdq/report` → `0 violation(s) total, exit 0` trên 8 file.
- Q2 DoD "bảng 3 loại truy vấn × 3 lớp, mỗi ô có trúng/trượt và thời gian": **PASS** — ba
  bảng ở mục 1, 2, 3, mỗi ô có recall và giây đo được.
- Q3 DoD "một con số cho 'giảm bao nhiêu' kèm cách tính": **PASS** — mục 5: **0 %**, bảng
  đối chiếu 5 cột, cách tính ghi rõ (recall so ground truth, đường ống là hợp các lớp), kèm
  3 giới hạn của phép đo.
- Q4 DoD "danh sách case bắt buộc LSP, mỗi case nêu lý do lumen+grep không thay được":
  **PASS** — mục 6, 4 case, mỗi case có lý do; case rename dẫn thẳng số dương tính giả đo
  được ở mục 3.
- Q5 DoD "`doc_lint.py docs/tdq/report` thoát 0 và `git status --porcelain` không hiện file
  trong `skills/`, `scripts/`, `hooks/`": **PASS** — lint exit 0; `git status --porcelain`
  chỉ hiện `docs/` và `graphify-out/` (hai file graphify đã bẩn từ trước request này).
- Phát sinh đáng chú ý: ground truth của T3 phải dựng bằng phân tích AST riêng, vì dùng bất
  kỳ lớp nào trong ba lớp đang đo để chấm điểm chính nó là vòng lặp logic. Việc này ngoài dự
  kiến của plan nhưng nằm trong T3.
