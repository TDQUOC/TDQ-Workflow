# Thêm pyrightconfig, đo lại LSP, rồi sửa luật thứ tự tìm kiếm

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay thử 1a trước và báo cáo lại cho tôi

Chọn option 1a, nguyên văn option:

> mở request gộp bước 1 + 2 (thêm `pyrightconfig.json`, đo lại, sửa luật)

Đọc lần đầu:
- **Mục tiêu, hai phần nối tiếp nhau**:
  1. Thêm thật `pyrightconfig.json` khai `include` + `extraPaths`, rồi **đo lại** 3 loại truy
     vấn của báo cáo `2026-09-02-2057` để có con số công bằng — số cũ đo khi LSP đang hỏng.
  2. Sửa `uu-tien-tim-kiem.md` + 5 chỗ móc **theo đúng số đo mới**, không theo dự đoán.
- **Ràng buộc thứ tự**: phần 2 phụ thuộc kết quả phần 1. Nếu đo lại cho thấy LSP mạnh lên
  đáng kể thì nội dung sửa luật sẽ khác hẳn so với khi nó vẫn yếu. Không được viết sẵn nội
  dung luật trước khi có số.
- **Điều đã chốt bất kể số ra sao**: bỏ ràng buộc "BẮT BUỘC gọi song song LSP + lumen ở mọi
  truy vấn ký hiệu code". Đo cũ cho thấy nó tốn thêm một lệnh gọi mỗi lần tìm mà không thêm
  kết quả nào; đây cũng đúng động cơ "chậm" user nêu ở request 2057.
- **Phạm vi đoán**: thêm `pyrightconfig.json` ở gốc repo; sửa
  `skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md` (file gốc) và 5 chỗ móc trong
  `tdq-intake` x2, `tdq-spec`, `tdq-plan`, `tdq-build`; `tests/test_tdq_lsp_skill.py` so 5 chỗ
  với file gốc nên sửa lẻ một chỗ là đỏ test; `docs/tdq/audit/luat-hien-co.md` nếu số dòng
  lệch; 3 bundle portable nếu `skills/` đổi.
- **Rủi ro đã biết**: lần thử tạm ở request 2255 cho 34 caller nhưng vẫn thiếu `tdq_team.py`,
  `tdq_timing.py`, `tdq_checkstatus.py`. Có thể cần chỉnh `extraPaths` thêm, hoặc chấp nhận
  độ phủ chưa trọn và ghi rõ.
- **Trạng thái thang**: `tdq_lsp.py kiem` chạy 00:17 hôm nay vẫn **6/6 ĐẠT** — đúng như đã
  biết, thang không nhìn thấy vấn đề cấu hình này. Thêm bậc kiểm là việc riêng, ngoài request.
- **Chỗ chưa rõ**: nếu số đo mới cho thấy LSP đáng giá hơn hẳn, có sửa luật ngay trong request
  này không, hay dừng lại trình số cho user quyết?

## Hiểu & kiến thức

- User chọn **2c** → phạm vi thu lại còn **thêm cấu hình + đo + báo cáo**. Sửa
  `uu-tien-tim-kiem.md` và 5 chỗ móc **rời sang request khác**. Vậy request này không chạm
  `skills/`, không phải dựng lại 3 bundle portable, không phải đụng
  `docs/tdq/audit/luat-hien-co.md`.
- `pyrightconfig.json` là file **giữ lại thật**, không phải file tạm như ở request 2255.
  Nó nằm ở gốc repo, không phải file Python nên `doc_lint` không đụng tới, nhưng phải kiểm
  không làm đỏ thêm test nào — mốc đỏ hiện tại là **101 fail / 1453 pass**.
- Chỗ chưa lý giải được từ request 2255: bản thử tạm cho **34 caller**, thấy đủ 5 hook và
  nhóm test, nhưng không thấy `tdq_team.py`, `tdq_timing.py`, `tdq_checkstatus.py` — cả ba
  đều nằm trong `scripts/`, tức đã nằm trong `include` lẫn `extraPaths`. Hai giả thuyết:
  output `find_callers` bị cắt ở 35 ký hiệu, hoặc ba file đó gọi qua `tdq_state.load(...)`
  dạng thuộc tính nên call hierarchy xếp khác. Phải phân biệt lúc đo, không đoán.
- Ground truth đã có sẵn từ request 2057, dựng bằng AST: **27 lệnh gọi ở 12 file**. Dùng lại,
  không dựng lại.
- Số cũ để so: LSP 1/12 file ở truy vấn quan hệ, 1/6 ở truy vấn tên chính xác, và ở truy vấn
  khái niệm trả 78 kết quả với đích xếp hạng 28.

## Hỏi đáp

- Lane → user chọn **A: nhanh (express)**.
- Nếu số đo mới cho thấy LSP đáng giá hơn → user chọn **C: chỉ đo và báo cáo, sửa luật để
  sang request khác**.
