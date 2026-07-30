# Khuôn spec

Copy nguyên khối dưới đây vào `docs/tdq/spec/<slug>.md` rồi điền. Xoá mục nào không
áp dụng, nhưng phải nói rõ **vì sao** không áp dụng.

```markdown
# SPEC — <tên việc>

Ngày: YYYY-MM-DD · Bản: 1.0 · Request: ../requests/<slug>.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi
- Mục tiêu: <1–3 câu, đo được>
- Trong phạm vi: <gạch đầu dòng>
- NGOÀI phạm vi: <gạch đầu dòng — nêu rõ để khỏi trôi việc>

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | | | |

## 3. Cách tiếp cận & lý do
- Chọn: <cách làm>
- Vì: <lý do, kèm nguồn research nếu có>
- Đã loại: <phương án> — vì <lý do>

## 3b. Năng lực & công cụ
Chép từ `knowledge/<slug>.md` mục "Năng lực dùng được". Phân vân → DÙNG.
Không xoá mục này kể cả khi mọi dòng là KHÔNG. Mỗi dòng DÙNG một skill riêng.
Phán quyết chỉ nhận: DÙNG / KHÔNG (+ 1 trong 4 lý do đóng) / NỀN (skill khung đang chạy).

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| <tên> | <user\|project\|plugin:x\|built-in> | DÙNG | <đầu ra hoặc task nào> |
| <tên> | built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc
- Log service bật mặc định: timestamp, đủ chi tiết debug, tắt/giảm được qua config.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.

## 5. Ràng buộc & rủi ro
| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | | | |

DoD: <liệt kê điều kiện đủ để tuyên bố xong>

## 7. Câu hỏi còn mở
(Phải RỖNG. Còn câu hỏi → quay lại phase analyze.)
```

## Kiểm trước khi trình

- Mọi đầu ra ở §2 đều có ít nhất một hạng mục QC ở §6.
- §3b có mặt và mỗi skill trong bảng kiểm kê (knowledge) có đúng 1 dòng — máy kiểm bằng
  `doc_lint.py` rule R8.
- Điều kiện PASS ở §6 đo được bằng lệnh, không phải cảm tính.
- §7 rỗng.
- Không câu nào dùng từ mơ hồ ("phù hợp", "tối ưu", "nếu cần") mà không kèm ngưỡng cụ thể.
