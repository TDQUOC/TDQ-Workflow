# BRIEF — Ưu tiên MCP, Auto Setup & Tự động Cập nhật Plugin (`2026-10-20-1115-uu-tien-mcp-auto-setup`)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

"okay hãy set và setup là bổ sung instruction toàn cục và trong hook after compact là luôn ưu tiên dùng mcp và bộ skill của mcp (nếu có) và ưu tiên lập phương án dùng nó trong spec/plan để đáp ứng yêu cầu người dùng, nhớ check connect trước (nếu có mà chưa connect đc thì hướng dẫn người dùng mở lên). ví dụ để code roblox hoặc unity thì luôn check mcp và bộ skill của mcp để hoàn thành yêu cầu người dùng giao. ngoài ra bổ sung thêm là mỗi khi update thì sẽ auto chạy lại setup (test và setup nốt những phần mới được update từ config version cũ đến version mới nhất đag đc cài) và cài hook session start sẽ auto check và update plugin"

## Hiểu & kiến thức

### 1. Phân tích mục tiêu & Hiện trạng kỹ thuật
Yêu cầu bao gồm 3 trụ cột nâng cấp đồng bộ cho toàn bộ hệ thống TDQ Workflow:

1. **Trụ cột 1: Nguyên tắc Ưu tiên MCP & Bộ kỹ năng MCP (MCP-First)**:
   - **Hiện trạng**: `KHOI_HUONG_DAN` hiện tại chỉ mới hướng dẫn gọi `mcp__lsp__start_lsp` cho tầng tìm kiếm code. Chưa có quy định tổng quát bắt buộc Agent phải rà soát và ưu tiên dùng MCP cùng bộ kỹ năng (skills/tools) của MCP trong các tác vụ phát triển đặc thù (Roblox Studio, Unity Engine, Chrome DevTools, Database, Docker...).
   - **Giải pháp**:
     - Cập nhật khối `KHOI_HUONG_DAN` ghim vào `~/.claude/CLAUDE.md`: Thiết lập mục `## Nguyên tắc Ưu tiên MCP & Bộ kỹ năng MCP (MCP-First)` yêu cầu mọi tác vụ tương thích phải ưu tiên lập phương án spec/plan sử dụng MCP và skills của MCP.
     - Cập nhật khối neo phục hồi `[TDQ:ANCHOR]` trong `hooks/scripts/session_start.py`: Bổ sung nguyên tắc `MCP-First` sau khi nén phiên (compact) để Agent không bị quên ngữ cảnh công cụ.
     - Quy định cơ chế **Pre-flight Connection Check**: Trước khi gọi công cụ MCP hoặc giao việc cho sub-agent, phải kiểm tra trạng thái sống/cổng kết nối (ví dụ port 9222 của Chrome CDP, socket của Unity/Roblox). Nếu MCP có đăng ký nhưng chưa kết nối được, BẮT BUỘC hướng dẫn người dùng cách khởi chạy/kết nối thay vì báo lỗi mơ hồ hoặc chuyển sang lệnh thô thiếu an toàn.
     - Cập nhật tài liệu quy trình tại `skills/tdq-spec/references/spec-template.md` (§3b) và `skills/tdq-plan/references/plan-template.md`.

2. **Trụ cột 2: Cơ chế Tự Động Chạy Setup Bù Khi Nâng Cấp Phiên Bản (Incremental Auto-Setup)**:
   - **Hiện trạng**: `tdq_setup.py:tu_dong_cap_nhat_khi_doi_phien_ban` chỉ ghi lại `CLAUDE.md` và dọn máy. Khi có phiên bản mới với dependencies mới, permissions mới trong `settings.json`, hoặc MCP mới, hệ thống không tự động bù đắp các phần thiếu.
   - **Giải pháp**:
     - Nâng cấp `tu_dong_cap_nhat_khi_doi_phien_ban`: So sánh mốc phiên bản cũ (`v_cu` từ `.tdq-phat-hanh.json`) với phiên bản mới (`v_moi`).
     - Tự động chạy lại quy trình cài đặt và kiểm thử các bậc (setup ladder): kiểm tra shim python3, cập nhật quyền allow-list trong `settings.json`, kiểm tra language servers, cấu hình Codex, và chạy hook dry-run xác nhận.
     - Ghi nhận trạng thái hoàn tất vào `.tdq-phat-hanh.json`.

3. **Trụ cột 3: Hook Session Start Tự Động Kiểm Tra & Cập Nhật Plugin**:
   - **Hiện trạng**: `session_start.py` và `kiem_plugin_user()` chỉ kiểm tra và in cảnh báo `bản cài ... lệch instruction ... — chạy /plugin update ...` nếu phiên bản trong `installed_plugins.json` cũ hơn mã nguồn. Người dùng phải gõ lệnh bằng tay.
   - **Giải pháp**:
     - Trong `session_start.py`, bổ sung hàm tự động kiểm tra và nâng cấp plugin scope user.
     - Khi phát hiện phiên bản cài đặt scope user (`v_cai`) cũ hơn phiên bản của repository (`v_nguon`):
       - Gọi lệnh cập nhật chính thức `claude plugin update tdq-workflow@tdq-local -s user -y` không chặn.
       - Hỗ trợ cơ chế tự động đồng bộ cache cục bộ: cập nhật trực tiếp cache `~/.claude/plugins/cache/tdq-local/tdq-workflow/<v_nguon>` và cập nhật bản ghi trong `~/.claude/plugins/installed_plugins.json`.
       - Phát thông báo xác nhận `[TDQ] Đã tự động cập nhật plugin tdq-workflow lên phiên bản <v_nguon> và đồng bộ cấu hình.`

### 2. Năng lực dùng được (Step B0)

Phân vân → DÙNG. Kiểm kê ngày 2026-10-20: 9 skill trên đĩa, cộng skill built-in trong context. Không xoá bảng này kể cả khi không có dòng DÙNG nào.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-setup | plugin:tdq-workflow | NỀN | Cập nhật `KHOI_HUONG_DAN`, logic auto-setup bù version và kiểm tra kết nối MCP |
| tdq-spec | plugin:tdq-workflow | NỀN | Bổ sung quy định rà soát MCP và pre-flight check vào spec template §3b |
| tdq-plan | plugin:tdq-workflow | NỀN | Bổ sung quy định ưu tiên MCP và task kiểm tra kết nối vào plan template |
| tdq-build | plugin:tdq-workflow | NỀN | Thực thi TDD red-green, unit tests và QC |
| tdq-conventions | plugin:tdq-workflow | NỀN | Quy tắc chung và chuẩn hóa anchor recovery block |
| Đã xét 20 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## Hỏi đáp

1. **Phạm vi kiểm tra kết nối MCP (Pre-flight check)**:
   - Cơ chế kiểm tra sẽ áp dụng cho: các server MCP phổ biến đã có trong máy hoặc được khai báo trong `~/.claude.json` / `installed_plugins.json` (như `lsp`, `chrome-devtools`, các MCP Roblox, Unity...). Khi một yêu cầu liên quan đến nền tảng này xuất hiện, hệ thống sẽ thực hiện pre-flight check (ví dụ kiểm tra cổng hoặc lệnh status) trước khi bắt đầu viết code.

2. **Cách thức cập nhật plugin tự động**:
   - Ưu tiên gọi CLI `claude plugin update tdq-workflow@tdq-local -s user -y`. Đồng thời hỗ trợ fallback cập nhật trực tiếp thư mục cache plugin user và file metadata `installed_plugins.json` để bảo đảm luôn luôn cập nhật thành công ngay cả khi CLI đang trong session chạy.

### Lộ trình

- `spec` → `plan` → `implement` → `qc` → `report`
- Mức QC: `full` (Definition of Done 4 chiều: MCP-First instruction & anchor, Pre-flight connection check, Incremental auto-setup, SessionStart auto-update plugin).
