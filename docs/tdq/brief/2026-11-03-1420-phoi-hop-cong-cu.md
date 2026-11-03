# BRIEF — Phối hợp công cụ tự động
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay tôi muốn là phân tích và thiết kế TDQ-Workflow sẽ setup user-instruction là alway suy nghĩ và tận dụng kết hợp nhiều công cụ/ mcp lại để làm việc và luôn lập internal step để cố gắng auto hoàn thanhf, ví dụ như một task chrome upload video gửi gemini edit thì sẽ mở chrome bằng chrome mcp r mở mục uplaod , sau đó dùng agent computer để chọn file phù hợp uplaod lên và dùng tiếp chrome mcp nhạp promt và chờ xong khi download thì chrome trigger download và agent desktop sẽ chọn vị trí lưu và bấm lưu, tương tự như vậy với  các task khác là agent sẽ luôn hỏi và tìm các công cụ để thực hiện tasks được giao và luôn làm phương án nhanh nhất tiện nhất hãy mở request update cho tdq-workflow setup và có toàn quyền setup vào user-instruction để set đó là soul để agentic automatic thông minh nhaast có thể

Mục tiêu: đưa nguyên tắc tự lập bước thực thi và phối hợp công cụ vào soul cùng user-instruction do TDQ setup quản lý. Chủ động khám phá năng lực, kiểm kết nối, chọn công cụ phù hợp từng bước, đổi công cụ khi có lý do và kiểm chứng kết quả thực tế.

Quyền đã nêu: cho phép cập nhật user-instruction qua setup trong phạm vi thiết kế được duyệt. Không suy diễn thành bỏ approval, thay quyền bảo mật, tải dữ liệu riêng tư lên dịch vụ bất kỳ hoặc ghi đè file chưa được phép.

Ưu tiên thiết kế: dùng một công cụ nếu đã đủ; phối hợp nhiều công cụ khi cần. Web ưu tiên Chrome MCP, desktop/dialog native ưu tiên agent-desktop; dùng upload trực tiếp/download API sẵn có trước khi mở hộp thoại hệ điều hành. Không lặp vô hạn khi công cụ thất bại.

## Hiểu & kiến thức

Khảo sát sơ bộ Workflow chỉ đọc hoàn tất 1/1 agent. `scripts/tdq_setup.py:980-1065` đã có `KHOI_HUONG_DAN`, `khoi_huong_dan()` và `ghim_huong_dan_tool()`, quản lý khối TDQ:TOOLS trong `~/.claude/CLAUDE.md`; tái dùng thay vì tạo bộ ghi instruction mới. `soul.md`, `plugin-routing.md` và `mcp-first-guide.md` đã có nguyên tắc chất lượng/MCP-first nhưng chưa hợp nhất vòng phối hợp công cụ và kiểm chứng từng bước.

Setup kiểm tra bậc 1–6 đạt; bậc 7 Graphify và bậc 8 kiểm chứng LSP theo module còn thiếu, exit 3; không coi là môi trường đã đạt hoàn toàn. Chờ chọn pipeline trước khảo sát sâu và chỉnh luật.

### Phạm vi đã chốt

Claude Code user-level trước; cập nhật soul, instruction do TDQ quản lý và routing. Tự tìm, dùng, kết nối/phục hồi công cụ đã cài trong quyền hiện có. Nếu thiếu: tìm web từ nguồn chính thức, đề xuất cài user-level kèm mục đích, quyền cần, kiểm chứng và gỡ; chỉ cài sau user duyệt. Không sửa instruction của Codex/OpenCode/Antigravity. QC ultra đã ghi qua CLI.

### Kết quả khảo sát

Workflow sâu hoàn tất 2/2 nhánh, không lỗi/thiếu. Writer `ghim_huong_dan_tool()` (`scripts/tdq_setup.py:1039`) thay khối TDQ:TOOLS và giữ nội dung quanh khối; hiện chưa backup/ghi nguyên tử, chưa từ chối marker lỗi. `thuc_hien_setup_bu()` bắt lỗi ghi instruction nhưng vẫn có thể tiến stamp; phải sửa để không báo thành công giả. Đây là điều kiện bảo toàn dữ liệu khi setup user-level, không phải dựng framework mới.

LSP references và Graphify affected sâu 2 do nhánh source xác minh: caller gồm `main`, `chay_cli`, `thuc_hien_setup_bu`, `tu_dong_cap_nhat_khi_doi_phien_ban`. Hook SessionStart kích hoạt setup bù; không thêm state/phase/hook để định tuyến công cụ.

| Vùng file | Lớp phát hiện | Tác động |
|---|---|---|
| `scripts/tdq_setup.py`, `hooks/scripts/session_start.py` | LSP/Graphify/Grep | Đồng bộ instruction và báo kết quả |
| `skills/tdq-conventions/SKILL.md`, `references/soul.md`, `references/plugin-routing.md` | Read/Grep | Luật thường trực và chọn công cụ |
| `skills/tdq-setup/SKILL.md`, `references/mcp-first-guide.md` | Read/Grep | Setup, pre-flight và đề xuất cài thiếu |
| `tests/test_claude_md_core.py`, `tests/test_auto_update_setup.py` | Grep | Bảo toàn instruction, retry và stamp |

### Năng lực dùng được

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake, tdq-conventions, tdq-spec, tdq-plan, tdq-build | plugin:tdq-workflow | NỀN | Pipeline và approval |
| tdq-setup | plugin:tdq-workflow | DÙNG | Kiểm setup user-level |
| tdq-browser-test | plugin:tdq-workflow | DÙNG | Preview và smoke browser |
| workflow-authoring | built-in | DÙNG | Khảo sát/QC hữu hạn, read-only |
| update-config | built-in | DÙNG | Kiểm ranh giới instruction/permission khi cần |
| Đã xét 18 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

### Nguồn năng lực thực

- https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/tool-reference.md — `upload_file` chọn file trực tiếp; không coi handle_dialog là native file picker.
- https://chromedevtools.github.io/devtools-protocol/tot/Browser/ — CDP download event không mặc định đồng nghĩa MCP expose tính năng; kiểm file sau tải.
- `C:/Users/admin/Documents/agent-desktop/skills/agent-desktop-windows/SKILL.md` và `references/troubleshooting.md` — cần desktop tương tác; không tự vượt UIPI/UAC; không retry khi hành động có thể đã xảy ra.

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Analyze + research | CÓ | Hai nhánh read-only đã hoàn tất; xác minh capability và writer |
| Spec rồi plan | CÓ | Hai cổng duyệt, sơ đồ Trước/Sau |
| Implement | CÓ | Tái dùng writer và rule hiện có; mode chốt tại plan |
| QC ultra + Workflow QC độc lập | CÓ | Unit, hồi quy, smoke/runtime an toàn theo DoD |
| Report | CÓ | Markdown + HTML, giới hạn và bằng chứng |
| Workflow implement/native worktree | BỎ | Không cần thêm cơ chế writer/worktree |

Không đặt trần token cho routing của request; công việc phân nhánh hữu hạn. Thiết kế runtime vẫn giới hạn retry theo tiến triển, không lặp để đốt token.

## Hỏi đáp

- User chọn `1a_ultracode`: Deep với modifier Ultracode cho riêng request; canonical lane `full`. Branch `feature/phoi-hop-cong-cu`, gốc `dev`, phase analyze.
- Modifier là lựa chọn rõ ràng từ user, độc lập với thông báo chế độ Ultracode toàn phiên đang tắt. Workflow chỉ đọc hữu hạn; TDQ leader giữ state/Git, không đặt token ceiling.
- Vòng scope cần chốt host đích và độ tự phục hồi; không hỏi lại mục tiêu tự lập bước, phối hợp công cụ và ghi user-instruction đã được yêu cầu.
- Khảo sát sâu: 2/2 nhánh hoàn tất, chỉ đọc.
- User chốt: «1a 2a và nếu thiếu thì có thể sreach web để đề xuất install vào user-level nha 3a». Nghĩa là Claude Code trước; tự phục hồi công cụ đã cài, tìm web và đề xuất cài thiếu chứ không tự cài; QC ultra.
- Không còn câu hỏi thay đổi phạm vi trước spec.
