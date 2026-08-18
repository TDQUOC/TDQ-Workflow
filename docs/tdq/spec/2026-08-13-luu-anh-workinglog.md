# SPEC — Lưu & nhúng ảnh đính kèm vào working log

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-08-13 · Bản: 1.0 · Brief: ../brief/2026-08-13-luu-anh-workinglog.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi
- Mục tiêu: khi user gửi ảnh đính kèm trong một turn phải ghi working log (đổi repo),
  ảnh đó được copy vào repo và nhúng bằng markdown ngay trong mục log của turn đó, thay
  vì chỉ nằm ở cache tạm session.
- Trong phạm vi: thêm quy ước + hướng dẫn thao tác vào `skills/tdq-conventions/SKILL.md`
  §6 (Working log) — bước copy ảnh, quy ước đặt tên/thư mục, cách chèn markdown vào chuỗi
  `--log` của `tdq_finish.py`.
- NGOÀI phạm vi: sửa code `scripts/tdq_finish.py` (không cần — script đã ghi verbatim
  chuỗi truyền vào `--log`); nén/resize/transcode ảnh; cơ chế dọn ảnh cũ tự động; áp dụng
  cho ảnh KHÔNG phải do user gửi (vd ảnh Claude tự tạo).

## 1b. Lộ trình
| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Phân tích (đã xong) | CÓ | Đọc `tdq_finish.py`, xác nhận cơ chế cache ảnh, chốt 3 câu hỏi mở |
| Research web | BỎ | Thuần nội bộ (quy ước + lệnh `cp`), không có ẩn số bên ngoài cần search |
| Interview | CÓ (đã xong) | 3 câu hỏi: commit git hay không, áp dụng ảnh nào, quy ước tên/thư mục |
| QC độc lập (agent) | BỎ | Việc nhỏ (sửa 1 file quy ước), tự QC đủ bằng cách giả lập 1 turn có ảnh |

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Quy ước mới trong `tdq-conventions` §6 | `skills/tdq-conventions/SKILL.md` | Đọc lại: có đủ 3 chốt (git, phạm vi áp dụng, tên/thư mục) đúng tinh thần user duyệt |
| 2 | Thư mục ảnh mẫu (bằng chứng cơ chế hoạt động) | `docs/workinglog/assets/<slug>/1.png` | File tồn tại, được git track, working log hôm đó có dòng `![...]` trỏ đúng file |

## 3. Cách tiếp cận & lý do
- Chọn: không sửa code — chỉ thêm quy ước thao tác thủ công (Claude tự làm mỗi lần) vào
  `tdq-conventions` §6, vì `tdq_finish.py::step_worklog` đã ghi verbatim chuỗi `--log`
  (đọc code xác nhận ở brief), nên markdown ảnh chèn sẵn trong chuỗi đó tự động render
  đúng mà không cần đổi script.
- Vì: giảm bề mặt thay đổi (0 dòng code Python), đúng tinh thần "sửa quy ước" mà user đã
  chốt lúc mở request; script không có logic đặc biệt nào cần thêm.
- Đã loại: thêm cờ `--image` vào `tdq_finish.py` để script tự copy+chèn — vì không cần
  thiết, tăng phức tạp code cho một việc `cp` + string nối đơn giản mà Claude tự làm được
  ngay trong turn (ảnh đã hiện sẵn trong context nhờ path cache).

## 3b. Năng lực & công cụ
| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-conventions | project | NỀN | Skill khung đang chạy, là nơi sửa |
| Đã xét ~90 skill khác (kiểm kê `skill_inventory.py`) | user/plugin/built-in | KHÔNG | khác lĩnh vực — không skill nào lo copy-file/nhúng-markdown, việc này thuần Bash `cp` + sửa văn bản |

## 4. Yêu cầu bắt buộc
- Log service: BỎ — việc này chỉ sửa tài liệu quy ước (`SKILL.md`), không tạo/sửa file
  mã nguồn chạy được.
- Không placeholder: quy ước viết đủ bước thật (copy → đặt tên → chèn markdown), không
  để chỗ "TODO".
- Test: không có unit test code (thuần văn bản); "test" là QC thủ công — giả lập một
  turn có ảnh đính kèm, chạy đúng quy ước mới, kiểm file + link (xem §6).

## 5. Ràng buộc & rủi ro
| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Screenshot chứa thông tin nhạy cảm (email, token, nội dung riêng tư) bị commit vào git | Rò rỉ nếu repo được push/chia sẻ | User đã chọn A (chấp nhận track git) khi duyệt câu hỏi 1 — không thêm bước giảm thiểu tự động; nêu rõ trong quy ước để Claude/user tự ý thức khi review diff trước khi push |
| Thư mục `assets/<slug>/` phình dần nếu nhiều ảnh trong 1 request | Repo nặng hơn theo thời gian | Chấp nhận (đã cân nhắc ở câu hỏi 1, không nằm trong phạm vi giảm thiểu của request này) |
| Đường dẫn cache ảnh không còn tồn tại lúc copy (vd hook lỗi, ảnh bị dọn sớm) | Copy fail, mất dữ liệu ảnh | Quy ước ghi rõ: copy NGAY trong turn nhận ảnh; nếu copy lỗi thì báo user thay vì âm thầm bỏ qua |

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | `tdq-conventions/SKILL.md` §6 có đủ 3 chốt (git, phạm vi áp dụng, tên/thư mục) | Đọc lại đoạn quy ước | Đúng tinh thần user duyệt: track git, mọi ảnh trong turn đổi repo, thư mục `assets/<slug>/<n>.<ext>` |
| Q2 | `doc_lint.py` pass | `python3 scripts/doc_lint.py skills/tdq-conventions/SKILL.md` | Exit 0 |
| Q3 | Cơ chế hoạt động đúng thực nghiệm | Giả lập: copy 1 ảnh mẫu vào `docs/workinglog/assets/<slug>/1.png`, ghi 1 dòng working log có `![test](assets/<slug>/1.png)` | File tồn tại, `git status` thấy file mới (chưa track = đúng, chưa commit), link markdown trỏ đúng path tương đối từ `docs/workinglog/<ngày>.md` |

DoD: Q1–Q3 đều PASS, không còn câu hỏi mở, `skills/tdq-conventions/SKILL.md` đã cập nhật
và lint sạch.

## 7. Câu hỏi còn mở
(rỗng)
