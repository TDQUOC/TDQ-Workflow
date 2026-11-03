# Bỏ LSP, chỉ dùng lumen + grep — nên không, mất bao nhiêu chất lượng

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay bây giờ mở request phân tích và resreach xem nếu chỉ dùng lumen + gerp và bỏ qua lsp
> thì có nên không? và chất lượng có giảm không nếu giảm thì giảm được bao nhiêu, và những
> case nào nên dùng lsp

Đọc lần đầu:
- **Mục tiêu**: quyết định có nên gỡ tầng LSP khỏi luật tìm kiếm của TDQ hay không, và nếu
  giữ thì giữ cho những case nào. Ba câu hỏi tách bạch:
  1. Bỏ LSP có nên không?
  2. Chất lượng giảm không — giảm **bao nhiêu** (phải ra con số, không nói cảm tính).
  3. Case nào **phải** dùng LSP.
- **Phạm vi đoán**: `skills/tdq-lsp-setup/` (luật gốc thứ tự tìm kiếm), 5 chỗ móc câu luật
  (`tdq-intake` x2, `tdq-spec`, `tdq-plan`, `tdq-build`), `scripts/tdq_lsp.py` (thang 6 bậc),
  cấu hình MCP `lsp` + lumen, và 3 bundle portable nếu luật đổi.
- **Chỗ chưa rõ**:
  - Đầu ra muốn là BÁO CÁO khuyến nghị, hay sửa luôn luật trong `skills/`?
  - "Chất lượng giảm bao nhiêu" đo bằng cách nào — chạy đối chứng thật trên repo này, hay
    tổng hợp từ nguồn ngoài?
  - Động cơ đằng sau là gì: chi phí cài đặt, tốc độ, hay context cost? Câu trả lời đổi hẳn
    cách cân đo.

## Hiểu & kiến thức

- **Luật gốc** nằm ở `skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md`. Mục 2 đã có sẵn
  bảng so khả năng: LSP trả lời chính xác 5 loại câu hỏi (định nghĩa ở đâu, ai gọi, kiểu gì,
  rename an toàn, lỗi hiện tại); lumen chỉ mạnh đúng 1 việc — truy vấn khái niệm không có tên
  symbol để bám. Đây là điểm tựa của câu "case nào phải dùng LSP".
- **Luật là mềm, không phải hook chặn** (mục 1): dùng grep thẳng cho symbol là lỗi QC, không
  bị máy từ chối. Nên "bỏ LSP" ở đây là đổi văn bản luật + 5 chỗ móc, không phải gỡ hạ tầng.
- **5 chỗ móc**: `tdq-intake/SKILL.md` + `references/analyze-full.md`, `tdq-spec`, `tdq-plan`,
  `tdq-build`. `tests/test_tdq_lsp_skill.py` so 5 chỗ với file gốc, sửa lẻ một chỗ là đỏ test.
- **Tiền lệ đo**: request `2026-08-26-0015-test-ranking-lsp-lumen-grep` đã chạy đúng phép đo
  này (3 loại truy vấn × 3 lớp) và QC PASS, nhưng bảng kết quả chỉ trình trong chat — repo
  không giữ số. Log `docs/workinglog/2026-08-26.md` còn ghi lumen với model cũ trúng 0/5 ở
  truy vấn khái niệm, đổi sang embedding tốt hơn mới lên 3/5. Tức chất lượng lumen phụ thuộc
  model, không phải hằng số → phải đo lại chứ không trích lại số cũ.
- **Động cơ user đã chốt**: (b) chậm, và (d) muốn biết LSP có thừa không. Vậy trục cân đo là
  thời gian mỗi lần tìm + tỉ lệ trúng, không phải chi phí cài đặt.
- **Ba câu hỏi đầu ra** phải trả lời rời nhau: nên/không nên · mất bao nhiêu (số) · case bắt buộc.

## Hỏi đáp

- Hỏi lane → user chọn **B: nhanh (express)**.
- Hỏi động cơ → user chọn **b (chậm)** + **d (muốn biết LSP có thừa không)**.
- Chưa hỏi lại: đầu ra là báo cáo hay sửa luôn luật. Chốt trong mini-plan là **chỉ ra báo
  cáo**; user có thể bác ngay ở cổng duyệt — đúng tinh thần express một cổng.
