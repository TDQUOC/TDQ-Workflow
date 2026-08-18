# SPEC — Skill tiếng Anh vs tiếng Việt + phương án tối ưu bộ workflow

Ngày: 2026-08-19 · Bản: 1.0 · Brief: ../brief/2026-08-18-2358-skill-en-vs-vi-toi-uu.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi
- Mục tiêu: cập nhật đề án tối ưu context (`docs/tdq/audit/de-an-toi-uu-context.md`, viết
  2026-08-17) bằng research + thực nghiệm mới, ra KẾT LUẬN CUỐI về câu hỏi "viết skill
  bằng tiếng Anh có tối ưu hơn tiếng Việt không", và report tổng hợp phương án patch cho user chọn.
- Trong phạm vi: đối chiếu 3 truy vấn research mới + 1 thực nghiệm dịch thật (đã làm ở
  analyze) với đề án cũ; viết mục quyết định cuối vào file audit; report ngắn liệt kê
  phương án patch theo thứ tự ưu tiên.
- NGOÀI phạm vi (chép từ brief — vòng scope BỎ, dùng lại phạm vi đã chốt ở request
  2026-08-17-2121): bảo mật · trải nghiệm người dùng cuối · an toàn dữ liệu · hiệu năng
  runtime của script. NGOÀI phạm vi thêm của chính request này: KHÔNG thực thi patch nào
  (không sửa `skills/`, không sửa `~/.claude/settings.json`) — dừng ở report + đề án.

## 1b. Lộ trình
Chép từ brief mục `### Lộ trình`.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ (đã xong ở analyze) | ẩn số ngoài: ảnh hưởng ngôn ngữ chỉ dẫn tới độ chính xác |
| Thực nghiệm đo thêm | CÓ (đã xong ở analyze) | kiểm chứng số cũ trên mẫu lớn hơn |
| Vòng scope | BỎ — dùng lại phạm vi đã chốt ở request 2026-08-17-2121 |
| QC độc lập (agent) | BỎ — tài liệu, không sửa code sản phẩm, tự QC đối chiếu DoD là đủ |
| Chia subagent | BỎ — một luồng viết tài liệu, không có task tách file rời nhau |

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Mục quyết định cuối về hướng A, thêm vào đề án cũ | `docs/tdq/audit/de-an-toi-uu-context.md` | `grep -c "Vòng 2026-08-19"` ≥ 1, `doc_lint` exit 0 |
| 2 | Report tổng hợp + phương án patch xếp thứ tự | `docs/tdq/reports/2026-08-18-2358-skill-en-vs-vi-toi-uu.md` | file tồn tại, `doc_lint` exit 0, có đủ 4 hướng còn lại D/C/B/A |

## 2b. Ranh giới module
Một module, không tách được nữa — cả hai đầu ra đọc cùng một nguồn (đề án cũ + research
mới) và report §2 phụ thuộc trực tiếp vào đầu ra §2 mục 1.

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| audit + report | `docs/tdq/audit/de-an-toi-uu-context.md`, `docs/tdq/reports/2026-08-18-2358-skill-en-vs-vi-toi-uu.md` | không | 1, 2 |

## 3. Cách tiếp cận & lý do
- Chọn: thêm một mục "Vòng 2026-08-19" vào CUỐI đề án cũ (không viết lại đề án từ đầu),
  ghi kết luận cuối về hướng A dựa trên bằng chứng mới; report tóm tắt + trỏ vào đề án.
- Vì: đề án cũ (5 hướng A–E, thứ tự D→C→B→A, E không làm) vẫn đúng và không có gì phải
  sửa — chỉ CÓ THÊM một mảnh bằng chứng làm chắc thêm kết luận về hướng A. Viết chèn thêm
  giữ được lịch sử suy luận, đúng luật "báo cáo ngắn gọn, không lặp lại nội dung đã có".
- Đã loại: viết lại toàn bộ đề án từ đầu — vì không có gì trong 4/5 hướng (D, C, B, E)
  bị bằng chứng mới ảnh hưởng, viết lại là lặp nội dung vô ích.

## 3b. Năng lực & công cụ
| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `tdq-spec`, `tdq-plan`, `tdq-build` | plugin:tdq-workflow | DÙNG | đang chạy phase tương ứng |
| `tdq-conventions` | plugin:tdq-workflow | NỀN | skill khung |
| `scripts/skill_tokens.py` | project | DÙNG | đo lại trần token (đã chạy ở analyze) |
| Đã xét 280 skill khác | plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc
- Log service: BỎ — việc này không tạo/sửa file mã nguồn chạy được, chỉ tài liệu.
- Không placeholder, không TODO stub.
- Mỗi đầu ra kiểm bằng `doc_lint.py` + `grep` đúng như bảng §2, chạy được bằng lệnh.
- Không áp SOLID/rule ngôn ngữ — không có code trong phạm vi.

## 5. Ràng buộc & rủi ro
Ràng buộc kiến trúc phải giữ: không chạm dòng nào — việc này chỉ ghi tài liệu audit/report,
không sửa `scripts/`, `hooks/`, `skills/`.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Report lặp lại y hệt đề án cũ, không thêm giá trị | user tốn thời gian đọc trùng | report chỉ tóm ≤15 dòng + trỏ file, phần chi tiết mới nằm ở mục bổ sung trong đề án |
| Kết luận "hướng A không đáng làm" bị hiểu nhầm là cấm tuyệt đối | user mất lựa chọn nếu sau này có bằng chứng ngược lại | ghi rõ đây là khuyến nghị dựa trên bằng chứng hiện có, không phải khoá cứng |

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Đề án cũ có mục kết luận mới, không bị viết đè phần cũ | 4 hướng D/C/B/E giữ nguyên nội dung so với bản 2026-08-17; mục mới chỉ CHÈN THÊM |
| Q2 | Report đủ 2 phần: tóm tắt phát hiện mới + danh sách phương án patch xếp thứ tự | report có bảng phương án, mỗi dòng có mức rủi ro và bước kế tiếp cụ thể |
| Q3 | doc_lint sạch trên cả 2 file đầu ra | `doc_lint.py <file>` exit 0 từng file |
| Q4 | Không file mã nguồn nào bị đổi | `git status --short` chỉ liệt kê file trong `docs/tdq/` |

DoD: hai đầu ra §2 tồn tại, đạt Q1–Q4, user nhận được report có đủ phương án để chọn
bước kế tiếp (kể cả phương án "không làm gì thêm").

## 7. Câu hỏi còn mở
(rỗng)
