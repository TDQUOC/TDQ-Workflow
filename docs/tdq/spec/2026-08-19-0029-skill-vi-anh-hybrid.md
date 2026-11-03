# SPEC — Hybrid skill: luật tiếng Anh, giao tiếp user tiếng Việt

Ngày: 2026-08-19 · Bản: 1.0 · Brief: ../brief/2026-08-19-0029-skill-vi-anh-hybrid.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi
- Mục tiêu: trả lời 2 câu hỏi user đặt ra — (1) có pattern "song ngữ có chủ đích" nào giữ
  được output/rule/behavior đúng như bản Việt trong khi luật viết tiếng Anh không; (2) vì
  sao bộ skill tiếng Anh khác (vd. `superpowers`) user đang dùng "có vẻ ổn" dù user gõ
  tiếng Việt — rồi cập nhật vào đề án `de-an-toi-uu-context.md` + report riêng.
- Trong phạm vi: đối chiếu 5 truy vấn research (đã làm ở analyze) với đề án cũ và kết luận
  request liền trước (2026-08-18-2358); viết mục quyết định mới vào file audit; report
  tóm tắt phát hiện + có/không nên làm patch hybrid.
- NGOÀI phạm vi: KHÔNG patch bất kỳ skill thật nào (đã hỏi + user chọn 1A ở scope round) —
  không sửa `skills/`, không sửa `~/.claude/settings.json`, không tạo gate đo ngôn ngữ đầu
  ra mới. Các mặt cũ vẫn ngoài phạm vi: bảo mật, trải nghiệm người dùng cuối, an toàn dữ
  liệu, hiệu năng runtime script (kế thừa từ 2026-08-17-2121).

## 1b. Lộ trình
Chép từ brief mục `### Lộ trình`.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ (đã xong ở analyze, 5 truy vấn) | ẩn số ngoài: có pattern hybrid thật không, vì sao skill Anh khác vẫn ổn |
| Vòng scope | CÓ (đã làm ở chat) | quyết định lớn (patch thật hay chỉ research) — user chọn 1A+2A |
| Interview chi tiết thêm | BỎ | không còn câu hỏi nào đổi kết quả |
| QC độc lập (agent) | BỎ | tài liệu thuần, tự QC đối chiếu DoD là đủ |
| Chia subagent | BỎ | một luồng viết tài liệu, không tách được |

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Mục kết luận mới về pattern hybrid, thêm vào đề án cũ | `docs/tdq/audit/de-an-toi-uu-context.md` | `grep -c "Vòng 2026-08-19 (2)"` ≥ 1, `doc_lint` exit 0 |
| 2 | Report tổng hợp: trả lời 2 câu hỏi user + khuyến nghị | `docs/tdq/reports/2026-08-19-0029-skill-vi-anh-hybrid.md` | file tồn tại, `doc_lint` exit 0 |

## 2b. Ranh giới module
Một module, không tách được — report đọc trực tiếp từ mục vừa viết vào đề án.

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| audit + report | `docs/tdq/audit/de-an-toi-uu-context.md`, `docs/tdq/reports/2026-08-19-0029-skill-vi-anh-hybrid.md` | không | 1, 2 |

## 3. Cách tiếp cận & lý do
- Chọn: thêm mục mới vào CUỐI đề án cũ (giữ nguyên "Vòng 2026-08-19" của request trước,
  không viết đè), ghi rõ đây là bổ sung — pattern hybrid có thật nhưng KHÔNG đổi khuyến
  nghị "không dịch nguyên khối"; report trả lời thẳng 2 câu hỏi user đặt ra.
- Vì: giữ lịch sử suy luận liền mạch, không lặp nội dung; user cần câu trả lời trực tiếp
  cho câu hỏi cụ thể vừa hỏi, không chỉ số liệu chung chung.
- Đã loại: viết lại đề án — không cần, 4/5 hướng D/C/B/E không đổi; patch thật ngay — user
  đã chọn không làm ở request này (1A+2A).

## 3b. Năng lực & công cụ
| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `tdq-spec`, `tdq-plan`, `tdq-build` | plugin:tdq-workflow | DÙNG | đang chạy phase tương ứng |
| `tdq-conventions` | plugin:tdq-workflow | NỀN | skill khung |
| `tavily-primary` | mcp | DÙNG | 5 truy vấn đã chạy ở analyze |
| Đã xét 280+ skill khác | plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc
- Log service: BỎ — không tạo/sửa file mã nguồn chạy được, chỉ tài liệu.
- Không placeholder, không TODO stub.
- Mỗi đầu ra kiểm bằng `doc_lint.py` + `grep` đúng như bảng §2.
- Không áp SOLID/rule ngôn ngữ — không có code trong phạm vi.

## 5. Ràng buộc & rủi ro
Ràng buộc kiến trúc phải giữ: không chạm dòng nào ngoài `docs/tdq/` — chỉ ghi tài liệu.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Report lặp nội dung research đã viết, không thêm giá trị | user tốn thời gian đọc trùng | report chỉ tóm tắt trả lời trực tiếp 2 câu hỏi, chi tiết đầy đủ ở research/audit |
| Kết luận "pattern hybrid khả thi nhưng CHƯA áp dụng" bị hiểu nhầm là đã an toàn để làm ngay | patch tương lai bỏ qua rủi ro còn lại (thiếu gate đo ngôn ngữ đầu ra) | report ghi rõ điều kiện cần trước khi patch: cần thêm gate kiểm output tiếng Việt |

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Đề án cũ có mục mới, không viết đè mục "Vòng 2026-08-19" của request trước | mục cũ giữ nguyên, mục mới nối tiếp sau |
| Q2 | Report trả lời trực tiếp 2 câu hỏi user đặt ra | report có 2 đoạn/mục rõ ràng ứng với 2 câu hỏi |
| Q3 | doc_lint sạch trên cả 2 file đầu ra | `doc_lint.py <file>` exit 0 từng file |
| Q4 | Không file mã nguồn nào bị đổi | `git status --short -- docs/tdq` chỉ liệt kê file trong `docs/tdq/` |

DoD: hai đầu ra §2 tồn tại, đạt Q1–Q4, report giúp user quyết được bước kế tiếp (kể cả
phương án "chưa làm gì thêm").

## 7. Câu hỏi còn mở
(rỗng)
