# 2026-08-09-trigger-tieng-viet

## Nguyên văn

> mở request thêm cụm tiếng Việt vào regex

Nối tiếp quan sát cuối request `2026-08-09-sua-mo-ta-skill-inventory`: `TRIGGER_RE` trong
`scripts/skill_inventory.py` chỉ khớp cụm tiếng Anh
(`use when|use this|whenever|when the user|trigger`), nên skill viết mô tả tiếng Việt bị cắt
cụt ở 60 ký tự và mất câu "dùng khi nào".

### Mục tiêu

Bảng kiểm kê năng lực B0 giữ được tín hiệu định tuyến cho cả skill mô tả tiếng Việt, giống
như đã làm được với skill tiếng Anh.

### Đo thật (274 skill trên máy, 2026-08-09)

Thử regex nháp `dùng khi|dùng cho|gọi khi|áp dụng khi|khi user|khi cần|lane full|lane quick`:
**5 skill** có mô tả dài hơn 60 ký tự, KHÔNG có cụm tiếng Anh nào, nhưng CÓ cụm tiếng Việt —
đúng 5 skill của chính TDQ: `tdq-build`, `tdq-intake`, `tdq-plan`, `tdq-spec`, `tdq-status`.
(`tdq-conventions` không dính vì mô tả nó nói "không gọi trực tiếp".)

Lợi ích nhỏ về số lượng (5/274) nhưng đúng chỗ: đây là 6 skill điều khiển chính workflow.
Chi phí gần như bằng 0 — thêm nhánh vào một hằng số regex.

### Phạm vi đoán

- `scripts/skill_inventory.py`: nối thêm nhánh tiếng Việt vào `TRIGGER_RE`.
- `tests/test_skill_inventory.py`: thêm test mô tả tiếng Việt có cụm trigger sau ký tự 60.

Không đụng `doc_lint.py`, khuôn bảng §3b, hook, state, gate duyệt.

### Chỗ chưa rõ

- Danh sách cụm chốt lấy những gì. Nghiêng về `dùng khi|dùng cho|gọi khi|áp dụng khi|khi cần`.
- Có tính `lane full` / `lane quick` là cụm trigger không — nó là điều kiện dùng thật của
  `tdq-build`/`tdq-plan`/`tdq-spec`, nhưng là từ riêng của TDQ, không phải khuôn chung.
- Có bump version trong turn này không.

## Hiểu & kiến thức

## Hỏi đáp
