# Điều tra LSP không thấy caller khác file — và thang kiểm thiếu bậc

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> 1c

Chọn option 1c ở cuối báo cáo `2026-09-02-2057-bo-lsp-dung-lumen-grep`, nguyên văn option:

> mở request điều tra trước cái `find_callers` 1/12 file

Đọc lần đầu:
- **Mục tiêu**: tìm ra vì sao `mcp__lsp__find_callers` trên `scripts/tdq_state.py:303`
  (`load`) chỉ trả về caller nằm trong chính file đó, trong khi ground truth dựng bằng AST là
  **27 lệnh gọi ở 12 file** — thiếu toàn bộ 5 file hook, `tdq_team.py`, `tdq_timing.py`,
  `tdq_checkstatus.py` và 3 file test.
- **Vì sao gấp**: nếu chỉ mục liên file không có thật thì `rename_symbol` và `blast_radius`
  đang không đáng tin trên repo này. Đó đúng là hai case mà báo cáo vừa xếp vào nhóm "bắt
  buộc dùng LSP" — tức khuyến nghị đó hiện đang đứng trên giả định chưa kiểm.
- **Phạm vi đoán**: cấu hình MCP server `lsp`, workspace folder mà language server nhận
  (`hooks/` và `tests/` có nằm trong không), language server Python đang chạy là cái nào và
  nó có dựng chỉ mục toàn workspace không, ảnh hưởng của việc `hooks/scripts/*.py` nạp
  `tdq_state` bằng thao tác `sys.path` thay vì import gói chuẩn.
- **Một nghi ngờ cụ thể**: 5 file hook đều thêm đường dẫn vào `sys.path` lúc chạy rồi mới
  import. Kiểu nạp động này là thứ chỉ mục tĩnh thường không lần ra được — nếu đúng vậy thì
  đây là **giới hạn thật của phân tích tĩnh**, không phải lỗi cấu hình, và kết luận sẽ khác
  hẳn: không có gì để "sửa".
- **Phần thứ hai của việc**: thang `python3 scripts/tdq_lsp.py kiem` báo **6/6 ĐẠT** (chạy
  lại 22:55 hôm nay vẫn 6/6) nhưng không phát hiện được vấn đề này — nó kiểm sự **tồn tại**
  của từng bậc, không kiểm **chất lượng chỉ mục**. Có nên thêm một bậc kiểm bằng hiệu ứng
  thật (hỏi một câu có đáp án biết trước, so kết quả) hay không.
- **Chỗ chưa rõ**: đầu ra là báo cáo chẩn đoán, hay sửa luôn cấu hình + thêm bậc 7 vào thang?

## Hiểu & kiến thức

Đọc code (B1) đã dựng được 4 dữ kiện, giả thuyết ban đầu **được củng cố mạnh**:

1. **Mọi caller ngoài file đều nạp động.** `hooks/scripts/_common.py:19` chèn `scripts/` vào
   `sys.path` lúc chạy rồi mới `import tdq_state`; 5 file hook đều đi qua nó. `tdq_team.py:70`,
   `tdq_timing.py:31`, `tests/helper.py:10` làm y hệt. Không có gói Python nào — `scripts/`
   không phải package, không có `__init__.py`.
2. **Không có file cấu hình nào khai `scripts/` là gốc import**: repo không có
   `pyproject.toml`, `pyrightconfig.json`, `setup.cfg`, `mypy.ini`, cũng không có `conftest.py`.
   Nghĩa là không có đường nào để một công cụ phân tích tĩnh biết `import tdq_state` trỏ đi đâu.
3. **Đo lại bằng công cụ thứ hai cho cùng kết quả**: `find_references` trên `load` trả 17
   tham chiếu, tất cả nằm dưới namespace `TDQWorkflow/scripts`, không một file `hooks/` hay
   `tests/` nào. Vậy không phải lỗi riêng của `find_callers`.
4. **`get_diagnostics` trên `hooks/scripts/stop_gate.py` trả 0 lỗi.** Đây là chi tiết ngược
   chiều giả thuyết và phải giữ lại: nếu server thật sự không resolve được `import tdq_state`
   thì thường sẽ có cảnh báo. Không có cảnh báo nghĩa là **hoặc** server resolve được mà không
   liên kết ngược, **hoặc** server này không báo lỗi import. Chưa phân biệt được — đây chính
   là chỗ cần thí nghiệm quyết định.

Phát hiện phụ, không nằm trong câu hỏi ban đầu: `find_references` trả về `ref_1..ref_17`
**không kèm file và số dòng** nào. Kết quả ở dạng này gần như không dùng được để đọc code,
độc lập với chuyện thiếu caller.

## Hỏi đáp

- Lane → user chọn **A: nhanh (express)**.
- Đầu ra → user chọn **A: chỉ chẩn đoán + khuyến nghị, chưa sửa gì**.
