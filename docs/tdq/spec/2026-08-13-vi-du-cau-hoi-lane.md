# SPEC — Ví dụ & hướng dẫn thân thiện cho câu hỏi kiểu A/B/C

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-08-13 · Bản: 1.0 · Brief: ../brief/2026-08-13-vi-du-cau-hoi-lane.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi
- Mục tiêu: mọi câu hỏi khuôn A/B/C của TDQ (chọn lane, chọn mode, vòng interview) có
  thêm 1 đoạn ngắn, thân thiện, cho người dùng lần đầu biết gõ gì (chữ cái hoặc câu tự
  nhiên) để dẫn tới gì; đồng thời rà lại 3 dòng `➤ Duyệt:` xem có cần bổ sung tương tự
  không.
- Trong phạm vi:
  - Sửa khối "Dòng hướng dẫn trả lời" trong `skills/tdq-intake/references/interview.md`
    (đang có 1 dòng chung chung, đổi thành nêu rõ nguyên tắc "gõ chữ cái HOẶC gõ nguyên
    câu tự nhiên khớp ý" + 1 ví dụ minh hoạ trung tính).
  - Rà + kết luận (giữ nguyên hoặc bổ sung) từng dòng `➤ Duyệt:` ở `skills/tdq-spec/SKILL.md`,
    `skills/tdq-plan/SKILL.md`, `skills/tdq-intake/references/quick-lane.md`.
- NGOÀI phạm vi: đổi cơ chế hook nhận diện câu duyệt (`edit_gate.py`, `prompt_context.py`
  hay tương đương); đổi nội dung câu hỏi (option A/B/C) hiện có; thêm ví dụ vào các dòng
  hỏi/thông báo khác không thuộc khuôn A/B/C hoặc dòng `➤ Duyệt:` (vd log, brief).

## 1b. Lộ trình
| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | Thuần nội bộ, không có ẩn số bên ngoài (thư viện/API/phiên bản) |
| Interview | CÓ (đã xong ở brief, 2 câu) | Có 2 điểm ảnh hưởng kết quả, đã hỏi & chốt (1A, 2B) |
| QC độc lập (agent) | BỎ | Việc văn bản 4 file, tự đọc lại đủ kiểm, không cần agent riêng |

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Khối hướng dẫn trả lời (nguyên tắc + ví dụ trung tính) thay cho dòng hint cũ | `skills/tdq-intake/references/interview.md` | Đọc lại: có cả câu ví dụ gõ tắt lẫn ví dụ câu tự nhiên, không gắn cứng vào 1 lane cụ thể |
| 2 | Kết luận rà soát + sửa (nếu cần) dòng `➤ Duyệt:` | `skills/tdq-spec/SKILL.md` | Đọc lại: dòng `➤ Duyệt:` giữ nguyên hoặc có thêm 1 vế ngắn nói rõ bước tiếp theo |
| 3 | Kết luận rà soát + sửa (nếu cần) dòng `➤ Duyệt:` | `skills/tdq-plan/SKILL.md` | Đọc lại: dòng `➤ Duyệt:` giữ nguyên hoặc có thêm 1 vế ngắn nói rõ bước tiếp theo |
| 4 | Kết luận rà soát + sửa (nếu cần) dòng `➤ Duyệt:` | `skills/tdq-intake/references/quick-lane.md` | Đọc lại: dòng `➤ Duyệt:` giữ nguyên hoặc có thêm 1 vế ngắn nói rõ bước tiếp theo |
| 5 | Ghi lại kết luận rà soát (giữ nguyên hay sửa, vì sao) vào chính plan | `docs/tdq/plan/2026-08-13-vi-du-cau-hoi-lane.md` | Mục P2 của plan liệt kê đủ 3 file, mỗi dòng có kết luận |

## 3. Cách tiếp cận & lý do
- Chọn: đổi khối hint cuối `interview.md` từ 1 câu chung chung sang khuôn 2 phần —
  nguyên tắc ngắn ("gõ chữ cái A/B/C, hoặc gõ nguyên câu tự nhiên khớp ý bạn chọn") + 1
  dòng ví dụ trung tính minh hoạ cả 2 cách, không gắn cứng nội dung theo 1 câu hỏi cụ thể
  (vì file này dùng chung cho nhiều loại câu hỏi khác nhau — lane, mode, interview tuỳ
  chọn — gắn cứng ví dụ "lane full" vào đây sẽ sai ngữ cảnh khi áp dụng cho câu hỏi mode).
- Vì: theo hỏi đáp brief 1A (cả 2 kiểu ví dụ) — nhưng ví dụ cụ thể theo NGỮ CẢNH câu hỏi
  chỉ hợp lý nếu gắn đúng câu hỏi đó; ở khuôn dùng chung chỉ nêu nguyên tắc chung là đúng
  kỹ thuật, tránh gây hiểu lầm khi áp dụng sang câu hỏi khác lane.
- Với 3 dòng `➤ Duyệt:`: rà từng dòng xem đã tự đủ (nêu rõ trả lời nào → bước gì tiếp
  theo) hay còn thiếu, chỉ sửa dòng thật sự thiếu — theo 2B (rà, không mặc định sửa hết).
- Đã loại: viết thêm ví dụ CỤ THỂ NGAY TRONG interview.md cho từng loại câu hỏi (lane,
  mode...) — vì loại câu hỏi dùng khuôn này có thể mở rộng về sau, hard-code ví dụ theo
  từng loại làm file phình và dễ lệch khi thêm câu hỏi mới; nguyên tắc chung + 1 ví dụ
  trung tính là đủ để người đọc suy ra cách trả lời cho câu hỏi bất kỳ.

## 3b. Năng lực & công cụ
| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| Đã xét 0 skill khác | — | KHÔNG | khác lĩnh vực — việc thuần sửa văn bản 4 file markdown, không cần tool/skill/MCP ngoài |

## 4. Yêu cầu bắt buộc
- Log service: BỎ — không có runtime, chỉ sửa 4 file tài liệu markdown hướng dẫn.
- Không placeholder, không TODO stub.
- "Test" cho việc văn bản là đọc lại đúng nội dung + `doc_lint.py` sạch cho từng file
  đổi (không có unit test code vì không có code).

## 5. Ràng buộc & rủi ro
| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Thêm quá nhiều chữ vào khối hint làm câu hỏi dài, rối mắt | Giảm tính "ngắn gọn thân thiện" mà chính yêu cầu này muốn đạt | Giới hạn khối hint ≤ 3 dòng (1 nguyên tắc + 1 ví dụ), không liệt kê hết mọi trường hợp |
| Sửa dòng `➤ Duyệt:` làm lệch câu chữ giữa 3 file (mỗi file người đọc khác lúc khác) | Câu duyệt không nhất quán, dễ user gõ sai | Rà cả 3 cùng lúc trong 1 phase (P2), so sánh chéo trước khi tick xong |

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Khối hint `interview.md` đúng khuôn mới | Đọc file, đối chiếu §2 đầu ra 1 | Có nguyên tắc + ví dụ trung tính, ≤ 3 dòng, không gắn cứng 1 lane |
| Q2 | 3 dòng `➤ Duyệt:` đã rà, có kết luận | Đọc `docs/tdq/plan/2026-08-13-vi-du-cau-hoi-lane.md` mục P2 | Đủ 3 file, mỗi dòng ghi rõ "giữ nguyên" hoặc nội dung đã sửa + lý do |
| Q3 | doc_lint sạch cho các file đã sửa | `python3 scripts/doc_lint.py <từng file đổi>` | Exit 0, không lỗi |
| Q4 | Không phá cấu trúc khuôn A/B/C hiện có | Đọc lại `interview.md` toàn bộ | Các khối khuôn hỏi A/B/C phía trên không đổi, chỉ đổi đúng khối hint cuối |

DoD: Q1–Q4 đều PASS, có bằng chứng (đọc file/lệnh) ghi trong `docs/tdq/qc/<slug>.md`.

## 7. Câu hỏi còn mở
(Rỗng — 2 câu hỏi ở brief đã chốt đủ.)
