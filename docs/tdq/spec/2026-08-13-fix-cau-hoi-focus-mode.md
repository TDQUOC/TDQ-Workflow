# SPEC — Fix: câu hỏi TDQ bị ẩn khi bật focus mode

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-08-13 · Bản: 1.0 · Brief: ../brief/2026-08-13-fix-cau-hoi-focus-mode.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi
- Mục tiêu: câu hỏi/tóm tắt chờ duyệt của TDQ workflow luôn là "final response" thật của
  turn (không bị gập ẩn dưới "N messages hidden" khi user bật focus mode).
- Trong phạm vi: sửa `skills/tdq-conventions/SKILL.md` §1 bước 4 — (a) bắt buộc dùng lệnh
  `tdq_finish.py`, cấm Edit tay working log; (b) lệnh đó phải chạy TRƯỚC đoạn chat cuối
  cùng kết thúc turn, không gọi thêm tool sau khi đã in đoạn đó.
- NGOÀI phạm vi: sửa từng skill con riêng lẻ (`tdq-intake`, `tdq-spec`, `tdq-plan`,
  `quick-lane`, `tdq-build`) — đã nạp `tdq-conventions` nên tự động thừa hưởng, không cần
  sửa thêm (user chọn 1A). Sửa `hooks/scripts/stop_gate.py` — hook vẫn đúng vai trò chống
  quên log, không phải chỗ có lỗi.

## 1b. Lộ trình
| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | Thuần nội bộ, đã có nguồn từ request `focus-mode-an-cau-hoi` trước |
| Interview | Đã xong (2 câu ở phase analyze) | — |
| QC độc lập (agent) | BỎ | Việc thuần văn bản 1 file, tự đọc lại + doc_lint + tự quan sát hành vi sống của chính các turn sau trong request này |

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Quy tắc mới ở §1 bước 4 | `skills/tdq-conventions/SKILL.md` | Đọc lại có đủ 2 ý: bắt buộc `tdq_finish.py` + chạy trước đoạn chat cuối |
| 2 | Bằng chứng sống — chính các turn build/QC/report của request này tuân quy tắc mới | Working log hôm nay (các mục do `tdq_finish.py` tạo, không phải Edit tay) | Có ≥ 1 entry working log ghi bởi `tdq_finish.py` (không do Edit tool) trong chính request này |

## 3. Cách tiếp cận & lý do
- Chọn: sửa đúng 1 file trung tâm (`tdq-conventions/SKILL.md`), không đụng các skill con
  — vì mọi skill đã "Nạp tdq-conventions trước" nên tự động thừa hưởng (DRY, user chọn 1A).
- Vì: tránh lệch câu chữ giữa nhiều file theo thời gian — đúng rủi ro đã nêu ở brief khi
  so sánh phương án A/B.
- Đã loại: lặp câu chữ ở từng skill con (phương án B) — user từ chối, lý do dễ lệch.
  Sửa `stop_gate.py` để nó tự động lùi thời điểm chặn — loại vì hook chặn ĐÚNG lúc (cuối
  turn thật), vấn đề nằm ở THỨ TỰ hành động của Claude trong turn, không phải ở hook.

## 3b. Năng lực & công cụ
| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| Đã xét toàn bộ skill trong kiểm kê (`skill_inventory.py`) | user/plugin/built-in | KHÔNG | khác lĩnh vực — sửa quy ước vận hành nội bộ TDQ, không khớp domain skill nào |

## 4. Yêu cầu bắt buộc
- Log service: BỎ — việc thuần sửa văn bản skill, không có runtime/mã nguồn chạy được
  nào được tạo mới (script `tdq_finish.py` đã có sẵn, không sửa).
- Không placeholder — câu chữ mới phải nêu rõ HÀNH ĐỘNG cụ thể (gọi lệnh gì, khi nào),
  không chỉ nhắc chung chung "nhớ ghi log sớm hơn".
- Không áp dụng mục unit test riêng — không có code sản xuất trong request này.

## 5. Ràng buộc & rủi ro
| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Một số DỪNG-chờ-user có phase CHƯA đổi (vd viết spec xong vẫn phase=spec, chờ duyệt) — gọi `tdq_finish.py` không có `--phase` thì bước `phase` tự skip, không sao | Nếu quên vẫn được vì script tự skip, không lỗi | Đã đọc `tdq_finish.py:126-128` xác nhận `--phase` là optional, không truyền thì bỏ qua bước đó |
| Quy tắc mới chỉ có hiệu lực khi Claude THẬT SỰ tuân theo ở các turn sau (không có cơ chế máy chặn nếu Claude quên) | Vẫn có thể tái diễn lỗi cũ nếu Claude không đọc kỹ | QC bằng cách tự quan sát — mọi turn build/QC/report còn lại của CHÍNH request này phải dùng `tdq_finish.py` làm bằng chứng, không chỉ sửa văn bản suông |

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | §1 bước 4 mới có đủ 2 ý (bắt buộc lệnh + thứ tự trước) | Đọc lại `tdq-conventions/SKILL.md` §1 | Có câu nêu bắt buộc `tdq_finish.py`, cấm Edit tay, và câu nêu rõ phải chạy TRƯỚC đoạn chat cuối |
| Q2 | `doc_lint.py` PASS | `python3 scripts/doc_lint.py skills/tdq-conventions/SKILL.md` | exit 0 |
| Q3 | Bằng chứng sống: turn build này (viết report) dùng `tdq_finish.py` thay vì Edit tay | Đọc working log hôm nay, tìm entry của turn report được tạo bởi lệnh này (không qua tool Edit) | Có ít nhất 1 entry như vậy |

DoD: §1 bước 4 đã sửa đúng nội dung, Q1-Q3 PASS, report của chính request này minh chứng
quy tắc mới hoạt động thật.

## 7. Câu hỏi còn mở
(rỗng)
