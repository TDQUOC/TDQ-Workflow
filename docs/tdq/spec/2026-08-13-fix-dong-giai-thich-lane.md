# SPEC — Fix dòng giải thích pipeline gây rối khi đọc lại tóm tắt

Ngày: 2026-08-13 · Bản: 1.0 · Brief: ../brief/2026-08-13-fix-dong-giai-thich-lane.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi
- Mục tiêu: khi Claude trình "Tóm tắt spec/plan" trong chat mà cần trích nguyên khối
  mẫu/khuôn có sẵn (ví dụ khuôn câu hỏi A/B kèm giải thích 2 pipeline), phải gắn nhãn rõ
  đó là khuôn mẫu — không phải câu hỏi sống của turn hiện tại — để đọc lại transcript
  không bị nhầm là đang hỏi lại lane dù đã chọn xong.
- Trong phạm vi: sửa `skills/tdq-spec/SKILL.md` bước 4 ("Trình bày & DỪNG") và
  `skills/tdq-plan/SKILL.md` bước 5 ("Trình bày & DỪNG") — thêm đúng 1 câu quy ước mỗi
  file.
- NGOÀI phạm vi: `skills/tdq-intake/references/lane-decision.md` (khuôn câu hỏi lane thật
  — không có vấn đề gì, giữ nguyên); `tdq-conventions/SKILL.md` (user chọn không mở rộng
  thành quy ước chung cho report/mọi tóm tắt khác, chỉ giới hạn spec + plan).

## 1b. Lộ trình
| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Phân tích (đã xong) | CÓ | Sửa lại nhận định sai ban đầu (tưởng lỗi ở lane-decision.md), xác định đúng 2 file |
| Research web | BỎ | Thuần nội bộ (quy ước trình bày của chính skill) |
| Interview | CÓ (đã xong) | 2 câu: cách gắn nhãn khuôn mẫu, phạm vi ghi quy ước (spec+plan hay chung) |
| QC độc lập (agent) | BỎ | Việc nhỏ (thêm 1 câu quy ước vào 2 file), tự QC đủ bằng đọc lại + doc_lint |

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Câu quy ước gắn nhãn khuôn mẫu trong tóm tắt spec | `skills/tdq-spec/SKILL.md` bước 4 | Đọc lại: có câu yêu cầu gắn nhãn khi trích nguyên khối mẫu |
| 2 | Câu quy ước tương tự trong tóm tắt plan | `skills/tdq-plan/SKILL.md` bước 5 | Đọc lại: có câu tương tự, nhất quán với bước 4 của spec |

## 3. Cách tiếp cận & lý do
- Chọn: thêm đúng 1 câu quy ước vào bước "Trình bày & DỪNG" của cả `tdq-spec` và
  `tdq-plan` — không đổi cấu trúc bước, không đổi giới hạn dòng (≤50/≤10) đã có.
- Vì: đây là 2 chỗ DUY NHẤT hướng dẫn Claude cách viết tóm tắt trình user duyệt; thêm quy
  ước tại nguồn đảm bảo áp dụng nhất quán cho mọi request tương lai có đầu ra là khuôn/mẫu
  văn bản (không chỉ riêng request `ux-cau-hoi-lane` vừa gặp).
- Đã loại: sửa `lane-decision.md` — vì đọc lại xác nhận khuôn câu hỏi lane thật không có
  vấn đề, nó chỉ được dùng khi hỏi SỐNG (lúc đó giải thích 2 pipeline là cần thiết, chưa
  ai chọn); vấn đề chỉ phát sinh khi TRÍCH LẠI khuôn đó làm ví dụ trong tóm tắt của 1
  request KHÁC đã qua bước chọn lane.
- Đã loại: sửa `tdq-conventions/SKILL.md` thành quy ước chung mọi loại tóm tắt (report,
  brief...) — user chốt câu 2 (2A) giới hạn đúng phạm vi spec + plan, tránh lan rộng khi
  chưa có bằng chứng vấn đề xảy ra ở report/brief.

## 3b. Năng lực & công cụ
| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-spec | project | NỀN | File cần sửa (bước 4) |
| tdq-plan | project | NỀN | File cần sửa (bước 5) |
| Đã xét ~90 skill khác (kiểm kê `skill_inventory.py`) | user/plugin/built-in | KHÔNG | khác lĩnh vực — không skill nào lo cách Claude viết tóm tắt duyệt, thuần sửa văn bản 2 file |

## 4. Yêu cầu bắt buộc
- Log service: BỎ — chỉ sửa tài liệu quy ước (`tdq-spec/SKILL.md`, `tdq-plan/SKILL.md`),
  không tạo/sửa file mã nguồn chạy được.
- Không placeholder: viết đủ câu quy ước thật, có ví dụ nhãn cụ thể như đã chốt trong
  brief, không để "..." mập mờ.
- Test: không có unit test code (thuần văn bản); "test" là đọc lại đối chiếu câu quy ước
  đã thêm + `doc_lint.py`.

## 5. Ràng buộc & rủi ro
| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Thêm câu quy ước làm bước "Trình bày & DỪNG" dài hơn, có thể làm Claude quên áp dụng | Vấn đề tái diễn ở request tương lai khác | Đặt câu quy ước ngay sát chỗ nói về giới hạn dòng tóm tắt, ngắn gọn, có ví dụ nhãn cụ thể để dễ áp dụng máy móc |
| Chỉ sửa spec+plan, không sửa report — nếu report tương lai gặp tình huống tương tự thì vẫn lặp lỗi | Phải mở request fix mới nếu phát sinh ở report | Chấp nhận (user chốt 2A, giới hạn phạm vi đúng bằng chứng đã thấy) |

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | `tdq-spec/SKILL.md` bước 4 có câu quy ước gắn nhãn khuôn mẫu | Đọc lại bước 4 | Có câu yêu cầu gắn nhãn "(khuôn mẫu — ...)" khi trích nguyên khối mẫu |
| Q2 | `tdq-plan/SKILL.md` bước 5 có câu quy ước tương tự | Đọc lại bước 5 | Có câu tương tự, nhất quán cách diễn đạt với Q1 |
| Q3 | `doc_lint.py` pass | `python3 scripts/doc_lint.py skills/tdq-spec/SKILL.md skills/tdq-plan/SKILL.md` | Exit 0 |

DoD: Q1–Q3 đều PASS, không còn câu hỏi mở.

## 7. Câu hỏi còn mở
(rỗng)
