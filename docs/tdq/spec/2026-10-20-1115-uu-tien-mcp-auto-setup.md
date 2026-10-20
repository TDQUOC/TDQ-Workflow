# SPEC — Ưu tiên MCP, Auto Setup & Tự động Cập nhật Plugin

Ngày: 2026-10-20 · Bản: 1.0 · Brief: ../brief/2026-10-20-1115-uu-tien-mcp-auto-setup.md · Lane: full
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
- Mục tiêu: Bổ sung nguyên tắc toàn cục MCP-First (ưu tiên MCP & bộ kỹ năng của MCP trong spec/plan/thực thi kèm pre-flight connection check), cơ chế auto-setup bù đắp nâng cấp từ phiên bản cũ sang phiên bản mới trong `tdq_setup.py`, và hook SessionStart tự động kiểm tra/nâng cấp plugin scope user.
- Trong phạm vi:
  - Ghim nguyên tắc MCP-First vào `CLAUDE.md` toàn cục qua `scripts/tdq_setup.py:KHOI_HUONG_DAN`.
  - Cập nhật khối neo phục hồi `[TDQ:ANCHOR]` trong `hooks/scripts/session_start.py` mang chỉ dẫn MCP-First sau khi nén phiên (compact).
  - Biên soạn cẩm nang chuẩn `skills/tdq-setup/references/mcp-first-guide.md` hướng dẫn kiểm tra kết nối (pre-flight check) cho các nền tảng phổ biến (Roblox, Unity, Chrome DevTools...) và cách chỉ dẫn người dùng bật server khi chưa kết nối.
  - Cập nhật tài liệu quy trình `skills/tdq-spec/references/spec-template.md` (§3b) và `skills/tdq-plan/references/plan-template.md` đưa việc rà soát và kiểm tra kết nối MCP vào luồng lập phương án.
  - Nâng cấp `scripts/tdq_setup.py:tu_dong_cap_nhat_khi_doi_phien_ban` tự động chạy setup bù các phần mới/thay đổi khi phiên bản cũ nâng lên phiên bản mới.
  - Bổ sung hàm tự động kiểm tra và nâng cấp plugin scope user trong `hooks/scripts/session_start.py`.
  - Viết bộ unit test kiểm chứng toàn diện hành vi.
- NGOÀI phạm vi:
  - Không tự phát triển MCP server mới (chỉ tích hợp, quản lý kết nối và điều phối các MCP hiện có hoặc người dùng cài thêm).
  - Không bypass các cơ chế bảo mật OAuth hoặc tài khoản của dịch vụ bên thứ ba.

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | Yêu cầu nằm trọn trong kiến trúc nội bộ của TDQ Workflow và Claude Code CLI |
| Interview | BỎ | Yêu cầu người dùng đã nêu đầy đủ mục tiêu kỹ thuật rõ ràng trong prompt |
| QC độc lập (agent) | CÓ | Chạy toàn bộ unit test độc lập kiểm chứng hook và logic setup |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Khối ghim instruction MCP-First | `scripts/tdq_setup.py` | `KHOI_HUONG_DAN` chứa mục `## Nguyên tắc Ưu tiên MCP & Bộ kỹ năng MCP (MCP-First)` |
| 2 | Khối neo phục hồi MCP-First sau nén | `hooks/scripts/session_start.py` | `[TDQ:ANCHOR]` chứa chỉ dẫn `MCP-First` khi `source=compact` hoặc `resume` |
| 3 | Cẩm nang hướng dẫn Pre-flight Check MCP | `skills/tdq-setup/references/mcp-first-guide.md` | Hướng dẫn check kết nối cho Roblox, Unity, Chrome DevTools và kịch bản hướng dẫn bật |
| 4 | Cập nhật mẫu Spec và Plan | `skills/tdq-spec/references/spec-template.md`, `skills/tdq-plan/references/plan-template.md` | §3b spec và plan template yêu cầu rà soát MCP và task pre-flight check |
| 5 | Tự động Setup bù khi đổi phiên bản | `scripts/tdq_setup.py` | `tu_dong_cap_nhat_khi_doi_phien_ban` thực hiện setup bù đắp và ghi mốc thành công |
| 6 | Hook SessionStart tự động cập nhật plugin | `hooks/scripts/session_start.py` | Tự động phát hiện lệch version và gọi update/sync plugin scope user |
| 7 | Bộ kiểm thử tự động | Bộ test suite của repo | Toàn bộ kịch bản kiểm tra các đầu ra trên đều PASS |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| `mcp-policy` | `skills/tdq-setup/references/mcp-first-guide.md`, `skills/tdq-spec/references/spec-template.md`, `skills/tdq-plan/references/plan-template.md` | không | 3, 4 |
| `setup-incremental` | `scripts/tdq_setup.py` | `mcp-policy` | 1, 5 |
| `session-hook` | `hooks/scripts/session_start.py` | `setup-incremental` | 2, 6 |

## 3. Cách tiếp cận & lý do
- Chọn:
  - Tích hợp nguyên tắc MCP-First thành một điều luật bất biến trong khối `KHOI_HUONG_DAN` của `tdq_setup.py` (tự động ghim vào `~/.claude/CLAUDE.md`). Điều này bảo đảm mọi agent trong phiên đều đọc được hướng dẫn ngay từ đầu.
  - Tiêm ngắn gọn vào `[TDQ:ANCHOR]` của `session_start.py`: Khi phiên làm việc bị nén (compact), block neo phục hồi sẽ nhắc lại ngay nguyên tắc `MCP-First` để Agent không quên công cụ.
  - Xây dựng cẩm nang chuẩn `mcp-first-guide.md` định nghĩa rõ ràng cách kiểm tra kết nối (pre-flight check) trước khi hành động: kiểm tra port (như 9222 của Chrome), kiểm tra socket/lệnh của Unity/Roblox MCP; nếu phát hiện chưa kết nối được, in câu thông báo cụ thể hướng dẫn người dùng mở lên.
  - Mở rộng hàm `tu_dong_cap_nhat_khi_doi_phien_ban` trong `tdq_setup.py`: So sánh version cũ và mới, tự động chạy kiểm tra và cài đặt/bổ sung các cấu hình cần thiết từ version cũ lên version mới.
  - Bổ sung hàm kiểm tra và cập nhật plugin trong `session_start.py`: Khi phát hiện phiên bản cài đặt scope user cũ hơn version của repo nguồn, tự động chạy lệnh cập nhật hoặc đồng bộ cache plugin.
- Vì: Giải quyết triệt để vấn đề Agent quên dùng MCP, dùng lệnh mù mờ khi thao tác với các nền tảng chuyên biệt như Roblox/Unity, đồng thời giúp việc bảo trì plugin hoàn toàn tự động, người dùng không cần phải chạy lệnh setup hoặc update thủ công mỗi lần có tính năng mới.
- Đã loại:
  - Loại bỏ phương án bắt buộc người dùng tự gõ lệnh cập nhật: Gây gián đoạn trải nghiệm và dễ dẫn đến tình trạng chạy instruction mới trên mã nguồn plugin cũ.

## 3b. Năng lực & công cụ

Phân vân → DÙNG. Kiểm kê ngày 2026-10-20: 9 skill trên đĩa, cộng skill built-in trong context. Không xoá bảng này kể cả khi không có dòng DÙNG nào.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-setup | plugin:tdq-workflow | NỀN | Cập nhật `KHOI_HUONG_DAN`, logic auto-setup bù version và kiểm tra kết nối MCP |
| tdq-spec | plugin:tdq-workflow | NỀN | Bổ sung quy định rà soát MCP và pre-flight check vào spec template §3b |
| tdq-plan | plugin:tdq-workflow | NỀN | Bổ sung quy định ưu tiên MCP và task kiểm tra kết nối vào plan template |
| tdq-build | plugin:tdq-workflow | NỀN | Thực thi TDD red-green, unit tests và QC |
| tdq-conventions | plugin:tdq-workflow | NỀN | Quy tắc chung và chuẩn hóa anchor recovery block |
| Đã xét 20 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc
- Log service bật mặc định: timestamp, đủ chi tiết debug, tắt/giảm được qua config (`TDQ_LOG=0`).
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code viết ra bám 5 nguyên tắc SOLID và clean code invariants trong `skills/tdq-conventions/references/clean-code.md`.

## 5. Ràng buộc & rủi ro
Ràng buộc kiến trúc phải giữ:
- `hooks/scripts/session_start.py`: Head block <= 12 lines / 600 chars; whole output <= 160 lines / 8200 chars; không làm chậm khởi động phiên (> 100ms cho các tác vụ đồng bộ).
- Khối `[TDQ:ANCHOR]` phải bảo toàn các anti-patterns hiện có, chỉ bổ sung ngắn gọn nguyên tắc MCP-First.
- Các lệnh cài đặt hoặc cập nhật plugin tự động phải chạy an toàn, có timeout và fallback, không làm treo hoặc crash hook `SessionStart`.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Lệnh `claude plugin update` bị treo khi không có mạng | Treo hook khởi động phiên làm việc | Giới hạn timeout chặt chẽ (≤ 5s) và hỗ trợ cơ chế chạy detached hoặc đồng bộ cache trực tiếp |
| Khối neo sau nén vượt quá ngân sách dòng/ký tự | Bị cắt cụt thông tin quan trọng | Kiểm soát chặt chẽ độ dài chuỗi neo phục hồi dưới 200 ký tự |
| User chưa cài MCP Roblox/Unity mà yêu cầu đòi hỏi | Agent bị bối rối | Bắt buộc pre-flight check: phát hiện thiếu hoặc chưa kết nối thì hướng dẫn người dùng cài đặt/kết nối |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |
|---|---|---|---|---|
| Q1 | Instruction & Anchor MCP-First | `KHOI_HUONG_DAN` có mục `MCP-First`; `session_start.py` neo sau nén có nhắc `MCP-First` | Baseline chưa có mục MCP-First trong KHOI_HUONG_DAN | Tinh chỉnh vị trí ghim trong template |
| Q2 | Pre-flight Check Guide & Spec/Plan | `mcp-first-guide.md` hướng dẫn check kết nối Roblox, Unity, DevTools; spec §3b và plan template có tiêu chí MCP | Baseline chưa có guide này | Ghim ví dụ cụ thể vào conventions |
| Q3 | Incremental Auto-Setup khi đổi version | `tu_dong_cap_nhat_khi_doi_phien_ban` chạy setup bù và cập nhật mốc phiên bản thành công | Baseline chỉ ghim CLAUDE.md và dọn máy | Gọi lần lượt các hàm setup bậc thiếu |
| Q4 | SessionStart Auto Update Plugin | Khi phiên bản cài user scope cũ hơn repo, hook tự động gọi cập nhật/đồng bộ plugin | Baseline chỉ in dòng cảnh báo | Bổ sung fallback đồng bộ file cache |

DoD: Khối instruction toàn cục và neo sau nén chứa nguyên tắc MCP-First; cẩm nang pre-flight check kết nối hoàn thiện; spec §3b và plan template tích hợp kiểm tra MCP; cơ chế auto-setup bù đắp và hook SessionStart tự động cập nhật plugin hoạt động chính xác với trọn bộ unit test PASS.

## 7. Câu hỏi còn mở
(Không có. Toàn bộ phạm vi kỹ thuật đã được làm rõ.)
