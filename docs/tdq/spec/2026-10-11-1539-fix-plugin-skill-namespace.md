# SPEC — Khắc phục lỗi Unknown skill tdq-intake do thiếu namespace plugin

Ngày: 2026-10-11 · Bản: 1.0 · Brief: ../brief/2026-10-11-1539-fix-plugin-skill-namespace.md · Lane: full
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
- Mục tiêu: Ngăn chặn lỗi `Unknown skill: tdq-intake` khi Claude Code gọi tool `Skill` bằng cách chuẩn hóa câu chữ hướng dẫn chỉ định rõ namespace plugin `tdq-workflow:tdq-intake` (hoặc fallback `tdq-intake`), áp dụng đồng bộ trong `CLAUDE.md`, hook `prompt_context.py` và tài liệu cài đặt.
- Trong phạm vi:
  1. Cập nhật `KHOI_HUONG_DAN` trong `scripts/tdq_setup.py` hướng dẫn mở request bằng `tdq-workflow:tdq-intake` (hoặc `tdq-intake` nếu cài cục bộ), đồng bộ vào `~/.claude/CLAUDE.md`.
  2. Cập nhật dòng nhắc `[TDQ:INTAKE]` trong `hooks/scripts/prompt_context.py` để nhắc cả 2 định dạng `tdq-workflow:tdq-intake (or tdq-intake)` mà vẫn đảm bảo độ dài không vượt trần.
  3. Cập nhật tài liệu `docs/notes/user-level-install.md`.
  4. Đảm bảo toàn bộ unit test, doc lint và kiểm tra mốc luật đạt yêu cầu.
- NGOÀI phạm vi: Can thiệp vào mã nguồn máy chủ CloudCLI bên ngoài repository này.

## 1b. Lộ trình
Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | Nguyên nhân lỗi và cơ chế plugin namespace đã được xác định chính xác |
| Interview | BỎ | Yêu cầu đã rõ ràng từ báo cáo điều tra |
| QC độc lập (agent) | BỎ | Mức QC chọn là full, DoD và test từng task là đủ |

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Khối chỉ dẫn ghim hướng dẫn đúng namespace skill | `scripts/tdq_setup.py`, `docs/notes/user-level-install.md` | khối hướng dẫn chứa chuỗi namespace |
| 2 | Hook nhắc nhở intake chứa namespace | `hooks/scripts/prompt_context.py` | dòng nhắc nhở intake chứa namespace và độ dài đạt chuẩn |
| 3 | Đồng bộ instruction và cập nhật token budget | `~/.claude/CLAUDE.md`, `docs/tdq/token-budget.json` | kiểm tra tính nhất quán tài liệu đạt yêu cầu |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| Setup & Instructions | `scripts/tdq_setup.py`, `docs/notes/user-level-install.md` | không | 1 |
| Hook Prompt Context | `hooks/scripts/prompt_context.py` | không | 2 |
| Verification & Token Budget | `docs/tdq/token-budget.json` | Setup & Instructions, Hook Prompt Context | 3 |

## 3. Cách tiếp cận & lý do
- Chọn: Chỉ định rõ ràng định dạng `tdq-workflow:tdq-intake (or tdq-intake)` trong cả instruction ghim ở `CLAUDE.md` lẫn hook nhắc nhở ngữ cảnh `[TDQ:INTAKE]`.
- Vì: Claude Code phân biệt skill của plugin theo tiền tố `<plugin-name>:<skill-name>`. Khi instruction ghi rõ tiền tố này, model sẽ truyền đúng chuỗi vào tool `Skill` mà không đoán mò tên ngắn gây lỗi `Unknown skill`.
- Đã loại: Chỉ ghi mỗi `tdq-workflow:tdq-intake` — vì nếu người dùng cài đặt skill dưới dạng thư mục cục bộ cá nhân (`~/.claude/skills/`), tiền tố sẽ không tồn tại; do đó ghi kèm phương án dự phòng `(or tdq-intake)` là bao quát nhất.

## 3b. Năng lực & công cụ
| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `tdq-setup` | plugin:tdq-workflow | DÙNG | Cập nhật logic ghim instruction vào `~/.claude/CLAUDE.md` |
| `tdq-conventions` | plugin:tdq-workflow | DÙNG | Quy tắc gọi skill và định danh namespace |
| Đã xét 15 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc
- Log service: BỎ — việc này chỉ sửa đổi văn bản hướng dẫn và hook string, không có runtime service mới.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code viết ra bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md`.

## 5. Ràng buộc & rủi ro
Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md` — chỉ những dòng việc này chạm tới, không chép cả file):
- Ràng buộc kiến trúc phải giữ: không chạm dòng nào — chỉ sửa đổi chuỗi nhắc nhở và mẫu template hướng dẫn

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Chuỗi `[TDQ:INTAKE]` vượt quá trần ký tự của test | Test nhắc nhở intake sẽ fail | Cắt gọn từ ngữ không cần thiết, đo trước độ dài chuỗi |

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |
|---|---|---|---|---|
| Q1 | Chuỗi nhắc nhở intake | Chứa `tdq-workflow:tdq-intake` và độ dài dòng không vượt trần | — | — |
| Q2 | Khối hướng dẫn setup | Chứa `tdq-workflow:tdq-intake` trong `KHOI_HUONG_DAN` | — | — |
| Q3 | Test suite | Toàn bộ test suite pass, không trôi mốc luật | — | — |

DoD:
- `KHOI_HUONG_DAN` trong `scripts/tdq_setup.py` và `~/.claude/CLAUDE.md` chứa `tdq-workflow:tdq-intake`.
- Hook `prompt_context.py` nhắc đúng chuỗi `tdq-workflow:tdq-intake (or tdq-intake)` và test liên quan pass.
- Toàn bộ test suite pass, drift mốc luật giữ 0.00%.

## 7. Câu hỏi còn mở
(Trống)
