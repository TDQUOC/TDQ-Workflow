# SPEC — Nghiêm cấm Co-Authored-By và chuẩn hóa đường dẫn script plugin

Ngày: 2026-10-11 · Bản: 1.0 · Brief: ../brief/2026-10-11-1346-cam-co-author-fix-path-script.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## Mục lục

- 1. Mục tiêu & phạm vi
- 1b. Lộ trình
- 2. Đầu ra cụ thể
- 2b. Ranh giới module
- 3. Cách tiếp cận & lý do
- 3b. Năng lực & công cụ
- 4. Yêu cầu bắt buộc
- 5. Ràng buộc & rủi ro
- 6. QC & Definition of Done
- 7. Câu hỏi còn mở

## 1. Mục tiêu & phạm vi
- Mục tiêu: Ngăn chặn triệt để tình trạng chèn attribution/Co-Authored-By vào commit và PR, đồng thời chuẩn hóa toàn bộ lệnh gọi script nội bộ trong `skills/` dùng biến `${CLAUDE_PLUGIN_ROOT}` để chạy đúng trên mọi thư mục làm việc của người dùng.
- Trong phạm vi:
  1. Thêm luật cấm `Co-Authored-By` và attribution trailer vào `KHOI_HUONG_DAN` trong `scripts/tdq_setup.py` và đồng bộ vào `~/.claude/CLAUDE.md`.
  2. Bổ sung luật cấm tường minh `Co-Authored-By: Claude Code...` vào `skills/tdq-conventions/SKILL.md` (§7) và `skills/tdq-build/references/report-template.md` (§10).
  3. Quét và thay thế toàn bộ lệnh `python3 scripts/...` thành `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/..."` trong toàn bộ các file markdown của `skills/`.
  4. Đảm bảo toàn bộ test suite pass, không trôi mốc luật, và token budget cập nhật hợp lệ.
- NGOÀI phạm vi: Thay đổi hành vi của hook ngoài hoặc sửa đổi các công cụ của bên thứ ba.

## 1b. Lộ trình
Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | Yêu cầu đã rõ ràng từ hệ thống nội bộ và hình ảnh người dùng cung cấp |
| Interview | BỎ | Đã làm rõ phạm vi qua brief và các file liên quan |
| QC độc lập (agent) | BỎ | Mức QC chọn là full, DoD và test từng task là đủ |

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Khối chỉ dẫn ghim cấm Co-Authored-By | `scripts/tdq_setup.py`, `docs/notes/user-level-install.md` | khối hướng dẫn có dòng cấm attribution |
| 2 | Quy chuẩn conventions và report cấm Co-Authored-By | `skills/tdq-conventions/SKILL.md`, `skills/tdq-build/references/report-template.md` | văn bản conventions có cấm rõ tên trailer |
| 3 | Toàn bộ script call trong skills dùng CLAUDE_PLUGIN_ROOT | Các file markdown trong `skills/` | không còn lệnh gọi script trần thiếu biến môi trường |
| 4 | Cập nhật token budget và kiểm thử toàn diện | `docs/tdq/token-budget.json` | kiểm tra tính nhất quán tài liệu đạt yêu cầu |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| Setup & Instructions | `scripts/tdq_setup.py`, `docs/notes/user-level-install.md` | không | 1 |
| Conventions & Report | `skills/tdq-conventions/SKILL.md`, `skills/tdq-build/references/report-template.md` | Setup & Instructions | 2 |
| Skills Script Path Normalization | `skills/tdq-intake/**`, `skills/tdq-setup/**`, `skills/tdq-plan/**`, `skills/tdq-build/**`, `skills/tdq-check-status/**`, `skills/tdq-lean/**` | không | 3 |
| Verification & Token Budget | `docs/tdq/token-budget.json`, `tests/**` | tất cả | 4 |

## 3. Cách tiếp cận & lý do
- Chọn:
  1. Ghi đè chỉ dẫn vào `~/.claude/CLAUDE.md`: Harness Anthropic có quy định rõ ràng rằng chỉ dẫn của người dùng trong `CLAUDE.md` có quyền ưu tiên cao hơn system reminder về attribution. Do đó đưa vào `KHOI_HUONG_DAN` của `tdq_setup.py` là giải pháp dứt điểm nhất.
  2. Dùng biến `${CLAUDE_PLUGIN_ROOT}`: Đây là biến chuẩn môi trường plugin được hỗ trợ bởi Claude Code và các adapter, đảm bảo script luôn trỏ đúng vào thư mục cài đặt plugin dù người dùng đang ở bất kỳ thư mục dự án nào.
- Vì: Giải quyết triệt để lỗi đường dẫn `No such file or directory` và lỗi tự chèn `Co-Authored-By`.
- Đã loại: Dùng đường dẫn tương đối `scripts/` — vì sẽ gãy ngay lập tức khi mở session ở project khác.

## 3b. Năng lực & công cụ
| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `tdq-setup` | plugin:tdq-workflow | DÙNG | Cập nhật logic ghim instruction vào `~/.claude/CLAUDE.md` |
| `tdq-conventions` | plugin:tdq-workflow | DÙNG | Quy tắc Git và quy chuẩn gọi script |
| `tdq-intake` | plugin:tdq-workflow | DÙNG | Chuẩn hóa đường dẫn script trong SKILL.md và references |
| `tdq-build` | plugin:tdq-workflow | DÙNG | Chuẩn hóa đường dẫn script trong SKILL.md và references |
| `tdq-plan` | plugin:tdq-workflow | DÙNG | Chuẩn hóa đường dẫn script trong mode-gate.md |
| `tdq-check-status` | plugin:tdq-workflow | DÙNG | Chuẩn hóa đường dẫn script trong references |
| Đã xét 15 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc
- Log service: BỎ — việc này chỉ sửa văn bản quy tắc trong skills, mẫu instruction và đường dẫn gọi script, không có runtime service.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code viết ra bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md`.

## 5. Ràng buộc & rủi ro
Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md` — chỉ những dòng việc này chạm tới, không chép cả file):
- Ràng buộc kiến trúc phải giữ: không chạm dòng nào — chỉ sửa cấu hình lệnh gọi trong skills và template instruction

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Đổi text trong `SKILL.md` làm vượt trần số dòng | Vi phạm cấu trúc skill | Kiểm tra độ dài từng file, viết cô đọng giữ nguyên số dòng |
| Sửa dòng làm trôi mốc anchored laws | Vi phạm kiểm thử luật mỏ neo | Kiểm tra vị trí sửa so với các mốc luật được neo |

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |
|---|---|---|---|---|
| Q1 | Lệnh gọi script trong `skills/` | Không còn lệnh gọi script trần thiếu biến môi trường | — | — |
| Q2 | Cấm Co-Authored-By | Có điều luật cấm trong khối hướng dẫn và conventions | — | — |
| Q3 | Line count và drift | Tuân thủ trần dòng và giữ nguyên mốc luật | — | — |

DoD:
- Lệnh gọi script trong toàn bộ `skills/` đều có tiền tố `"${CLAUDE_PLUGIN_ROOT}/"`.
- `KHOI_HUONG_DAN` trong `scripts/tdq_setup.py` có mục cấm `Co-Authored-By`.
- `~/.claude/CLAUDE.md` được đồng bộ điều luật mới.
- Toàn bộ test suite pass, không có vi phạm drift luật.

## 7. Câu hỏi còn mở
(Trống)
