# Khuôn spec

Copy nguyên khối dưới đây vào `docs/tdq/spec/<slug>.md` rồi điền. Xoá mục nào không
áp dụng, nhưng phải nói rõ **vì sao** không áp dụng.

```markdown
# SPEC — <tên việc>

Ngày: YYYY-MM-DD · Bản: 1.0 · Brief: ../brief/<slug>.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi
- Mục tiêu: <1–3 câu, đo được>
- Trong phạm vi: <gạch đầu dòng>
- NGOÀI phạm vi: <gạch đầu dòng — nêu rõ để khỏi trôi việc. Có chạy vòng scope thì
  BẮT BUỘC chép các mặt bị loại ở brief `### Phạm vi đã chốt` vào đây>

## 1b. Lộ trình
Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ/BỎ | <lý do> |
| Interview | CÓ/BỎ | <lý do> |
| QC độc lập (agent) | CÓ/BỎ | <lý do> |

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | | | |

## 3. Cách tiếp cận & lý do
- Chọn: <cách làm>
- Vì: <lý do, kèm nguồn research nếu có>
- Đã loại: <phương án> — vì <lý do>

## 3b. Năng lực & công cụ
Chép từ brief mục `### Năng lực dùng được`. Phân vân → DÙNG.
Một dòng cho mỗi skill DÙNG hoặc NỀN, cộng đúng một dòng tổng cho phần còn lại.
Không xoá mục này kể cả khi không có dòng DÙNG nào.
Phán quyết chỉ nhận: DÙNG / KHÔNG (+ 1 trong 4 lý do đóng) / NỀN (skill khung đang chạy).

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| <tên> | <user\|project\|plugin:x\|built-in> | DÙNG | <đầu ra hoặc task nào> |
| Đã xét <N> skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc
- Log service bật mặc định: timestamp, đủ chi tiết debug, tắt/giảm được qua config.
  Dòng này bắt buộc **chỉ khi việc này có runtime** — tức plan sẽ có ít nhất một task tạo
  hoặc sửa file mã nguồn chạy được. Không có runtime (chỉ sửa tài liệu, khuôn mẫu, cấu
  hình) → thay dòng này bằng `Log service: BỎ — <lý do một câu>`.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code viết ra bám 5 nguyên tắc SOLID theo
  `skills/tdq-conventions/references/clean-code.md`, và bám rule ngôn ngữ trong
  `skills/tdq-build/references/rules/`. Luật này luôn áp, không có cổng bật/tắt.

## 5. Ràng buộc & rủi ro
Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md` — chỉ những dòng việc này
chạm tới, không chép cả file):
- <nguyên văn dòng luật gọi / đã chốt> — việc này chạm ở <file/hàm>

Không chạm dòng nào → ghi `Ràng buộc kiến trúc phải giữ: không chạm dòng nào — <lý do
một câu>`. Chưa có `docs/kien-truc.md` → quay lại analyze sinh theo luật hồ sơ kiến
trúc, không bỏ trống khối này.

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
- §1b có mặt: mỗi bước/phase của workflow được ghi rõ CÓ chạy hay BỎ, kèm lý do.
- §3b có mặt: mỗi skill DÙNG và NỀN có một dòng riêng, phần còn lại gom vào dòng tổng
  `Đã xét <N> skill khác` — máy kiểm bằng `doc_lint.py` rule R8.
- Điều kiện PASS ở §6 đo được bằng lệnh, không phải cảm tính.
- §7 rỗng.
- Không câu nào dùng từ mơ hồ ("phù hợp", "tối ưu", "nếu cần") mà không kèm ngưỡng cụ thể.

## Checklist scope — trả lời được hết mới trình

| Câu hỏi | Trả lời phải nằm ở |
|---|---|
| Việc này làm RA cái gì? | §1 mục tiêu + §2 bảng đầu ra |
| Các mặt bị loại ở vòng scope đã ghi chưa? | §1 mục NGOÀI phạm vi |
| Có gì MỚI so với hiện trạng? | §3 cách tiếp cận |
| Output cụ thể là file/lệnh/màn hình nào? | §2 cột đường dẫn/vị trí |
| Có cần model không (tên, nơi chạy, chi phí)? | §1 phạm vi + §5 ràng buộc |
| Có cần download/cài đặt gì không? | §5 ràng buộc — ghi rõ tên gói và bản |
| QC/test/validate làm thế nào? | §6 bảng QC + DoD |

Còn một ô chưa trả lời được → chưa đủ điều kiện trình spec, quay lại phase analyze.
