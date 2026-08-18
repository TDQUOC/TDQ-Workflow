# SPEC — Rút gọn UX câu hỏi chọn lane

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-08-13 · Bản: 1.0 · Brief: ../brief/2026-08-13-ux-cau-hoi-lane.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi
- Mục tiêu: câu hỏi "chọn lane" mà `tdq-intake` in ra chat gọn hơn — bỏ dòng kỹ thuật
  `Cỡ:/Cần:`, gọi là "pipeline" khi nói với user, thêm 1 câu giải thích ngắn nghĩa 2
  pipeline, kết bằng lời mời chọn + hướng dẫn trả lời.
- Trong phạm vi: sửa `skills/tdq-intake/SKILL.md` (bước 2, Phần A) và
  `skills/tdq-intake/references/lane-decision.md` (mục "Dòng tự nhận định" + "Khuôn câu
  hỏi").
- NGOÀI phạm vi: đổi khoá `lane` trong `state.json`/`tdq_state.py` (giữ nguyên thuật ngữ
  nội bộ); sửa `references/interview.md` (khối hint dùng chung cho MỌI câu hỏi A/B/C,
  không riêng câu chọn lane); đổi bảng quyết/tiêu chí ở `lane-decision.md` (chỉ đổi CÁI
  GÌ được in ra, không đổi cách quyết định).

## 1b. Lộ trình
| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Phân tích (đã xong) | CÓ | Xác định đúng 2 file cần sửa, chốt format mới qua 4 câu hỏi |
| Research web | BỎ | Thuần nội bộ (copywriting UX của chính skill) |
| Interview | CÓ (đã xong) | 4 câu: bỏ dòng Cỡ/Cần, đổi tên gọi lane→pipeline, thêm giải thích nghĩa, chọn lane |
| QC độc lập (agent) | BỎ | Việc nhỏ (đổi văn bản 2 file), tự QC đủ bằng đọc lại + doc_lint |

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Bước 2 Phần A viết lại theo format mới | `skills/tdq-intake/SKILL.md` | Đọc lại: không còn nhắc in dòng `Cỡ:/Cần:` ra chat, câu hỏi dùng "pipeline" |
| 2 | Khuôn câu hỏi mẫu viết lại | `skills/tdq-intake/references/lane-decision.md` | Đọc lại: khuôn khớp đúng format đã chốt trong brief (không có dòng Cỡ/Cần, có câu giải thích nghĩa 2 pipeline, câu hỏi dùng "pipeline") |

## 3. Cách tiếp cận & lý do
- Chọn: chỉ sửa 2 file — nơi DUY NHẤT chứa chuỗi `"Bạn muốn chạy lane nào?"` hiện với
  user; giữ nguyên bảng quyết định + toàn bộ thuật ngữ `lane` trong code/state.
- Vì: đọc code xác nhận chuỗi này chỉ xuất hiện ở 2 chỗ (brief mục "Đọc code"); đổi tối
  thiểu, không lan sang state/CLI (rủi ro phá vỡ tương thích với `tdq_state.py init
  <slug> <quick|full>` vẫn nhận đối số `lane`).
- Đã loại: sửa `interview.md` để nhét câu giải thích pipeline vào khối hint chung — vì
  khối đó dùng cho MỌI câu hỏi A/B/C trong toàn hệ thống (không riêng lane), nhét nội
  dung riêng của lane vào đó sẽ làm hint bị lệch ngữ cảnh ở những câu hỏi khác.
- Đã loại: đổi hẳn thuật ngữ `lane` thành `pipeline` xuyên suốt code/state — vì user chốt
  câu 2 (2A) chỉ đổi CÁCH GỌI lúc hiển thị, không đổi thuật ngữ nội bộ; đổi xuyên suốt sẽ
  kéo theo sửa `tdq_state.py`, mọi skill `tdq-*`, ngoài phạm vi được duyệt.

## 3b. Năng lực & công cụ
| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | project | NỀN | Skill khung đang chạy, là nơi sửa |
| Đã xét ~90 skill khác (kiểm kê `skill_inventory.py`) | user/plugin/built-in | KHÔNG | khác lĩnh vực — không skill nào lo copywriting/UX câu hỏi, thuần sửa văn bản |

## 4. Yêu cầu bắt buộc
- Log service: BỎ — chỉ sửa tài liệu quy ước (`SKILL.md`, `lane-decision.md`), không
  tạo/sửa file mã nguồn chạy được.
- Không placeholder: viết đủ khuôn câu hỏi thật (như trong brief mục "Chốt kiến thức"),
  không để "..." mập mờ.
- Test: không có unit test code (thuần văn bản); "test" là đọc lại đối chiếu format đã
  chốt + `doc_lint.py`.

## 5. Ràng buộc & rủi ro
| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Bỏ dòng `Cỡ:/Cần:` khỏi chat làm user mất thông tin để tự đánh giá độ phức tạp việc | User duyệt lane mà không biết Claude đang cân nhắc gì | Chấp nhận (user đã chốt 1A — ưu tiên gọn, thông tin đó vẫn còn NỘI BỘ, dùng để chọn đề xuất A) |
| Câu giải thích nghĩa 2 pipeline làm khối hint dài hơn, có thể vượt giới hạn hiển thị gọn | Câu hỏi dài hơn trước dù mục tiêu là "gọn" | Chấp nhận — 1 câu ngắn/pipeline, tổng thêm ≤ 2 dòng, đổi lại bỏ được dòng Cỡ/Cần nên tổng độ dài không tăng |

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | `tdq-intake/SKILL.md` bước 2 không còn yêu cầu in `Cỡ:/Cần:` ra chat, dùng "pipeline" | Đọc lại đoạn bước 2 | Đúng tinh thần user chốt (1A, 2A) |
| Q2 | `lane-decision.md` khuôn câu hỏi khớp format đã chốt | Đọc lại mục "Khuôn câu hỏi" | Có đủ: không dòng Cỡ/Cần, câu hỏi dùng "pipeline", có câu giải thích nghĩa 2 pipeline, có khối hint trả lời |
| Q3 | `doc_lint.py` pass | `python3 scripts/doc_lint.py skills/tdq-intake/SKILL.md skills/tdq-intake/references/lane-decision.md` | Exit 0 |

DoD: Q1–Q3 đều PASS, không còn câu hỏi mở.

## 7. Câu hỏi còn mở
(rỗng)
