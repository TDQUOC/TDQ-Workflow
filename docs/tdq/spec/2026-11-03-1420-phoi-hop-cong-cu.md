# SPEC — Phối hợp công cụ tự động có kiểm chứng
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Ngày: 2026-11-03 · Bản: 1.0 · Lane: full · Modifier: ultracode
Brief: ../brief/2026-11-03-1420-phoi-hop-cong-cu.md
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi

Agent chủ động hoàn tất task bằng chuỗi bước nội bộ và công cụ thích hợp, không chờ người dùng chỉ từng thao tác. Chọn đường ít bước nhất trong các phương án đúng, có quyền và kiểm chứng được; giữ chất lượng > runtime > context cost.

Trong phạm vi: soul và luật thường trực; routing web/native/file; setup và cập nhật khối user-instruction Claude Code; bảo toàn nội dung riêng; tìm web để đề xuất công cụ còn thiếu; kiểm chứng kết quả từng bước và kết quả cuối.

Ngoài phạm vi: framework điều phối mới, state/phase/hook mới, tự sửa permission để vượt chặn, tự cài công cụ chưa duyệt, tự đăng nhập/OAuth, cập nhật instruction host khác. Ví dụ Gemini là kịch bản thiết kế, không phải quyền tải video riêng tư hay cam kết Gemini có tính năng chỉnh sửa bất kỳ.

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Analyze + research | CÓ | Hai nhánh read-only đã hoàn tất; xác minh capability và writer |
| Spec rồi plan | CÓ | Hai cổng duyệt, sơ đồ Trước/Sau |
| Implement | CÓ | Tái dùng writer và rule hiện có; mode chốt tại plan |
| QC ultra + Workflow QC độc lập | CÓ | Unit, hồi quy, smoke/runtime an toàn theo DoD |
| Report | CÓ | Markdown + HTML, giới hạn và bằng chứng |
| Workflow implement/native worktree | BỎ | Không cần thêm cơ chế writer/worktree |

## 2. Đầu ra cụ thể

| # | Đầu ra | Vị trí | Đo xong bằng |
|---|---|---|---|
| O1 | Nguyên tắc tự chủ và phối hợp công cụ | soul + thân conventions | Có bước, điều kiện dùng, ngoại lệ và self-check |
| O2 | Contract routing chung | plugin-routing + MCP-first guide | Web/native/direct upload/download/missing tool có lối đi rõ |
| O3 | Instruction user-level cập nhật an toàn | `scripts/tdq_setup.py`, `~/.claude/CLAUDE.md` | Khối TDQ đồng bộ; phần riêng nguyên vẹn; backup và no-op kiểm được |
| O4 | Regression và eval | tests + artifacts request | Red-green, corpus đối chứng và smoke hữu hạn |
| O5 | Áp dụng máy hiện tại và báo cáo | user-level Claude + report request | Kiểm nội dung sau setup, không sửa permission/OAuth |

## 2b. Ranh giới module

| Module | Vùng file | Quan hệ đã xác minh | Đầu ra |
|---|---|---|---|
| Luật | `skills/tdq-conventions/SKILL.md`, `references/soul.md`, `references/plugin-routing.md` | Agent đọc; không import runtime | O1/O2 |
| Hướng dẫn setup | `skills/tdq-setup/SKILL.md`, `references/mcp-first-guide.md` | Trỏ CLI hiện có; không bộ cài mới | O2/O3 |
| Đồng bộ instruction | `scripts/tdq_setup.py` | `ghim_huong_dan_tool()` được CLI và setup bù gọi; LSP/Graphify sâu hai bước xác minh | O3/O5 |
| Tích hợp phiên | `hooks/scripts/session_start.py` | Gọi auto-update khi version đổi; chỉ chạm nếu cần truyền trạng thái thất bại | O3 |
| Kiểm chứng | tests setup/soul/routing + artifacts | Fixture user-home tạm; không sửa tài khoản thật khi chạy unit | O4 |

Không dùng writer Claude cho Codex/OpenCode/Antigravity. Không import hooks ngược vào scripts.

## 2c. Luồng hoạt động & Sơ đồ kiến trúc

HTML: `2026-11-03-1420-phoi-hop-cong-cu-preview.html`, gồm bốn view Trước/Sau: thực thi task và đồng bộ instruction. Đây là thiết kế planned, không phải chứng nhận đã triển khai.

| Khía cạnh | Trước | Sau |
|---|---|---|
| Chọn công cụ | Bảng plugin tĩnh, có giả định mọi plugin bật | Kiểm inventory/tool schema và kết nối trong phiên |
| Thực hiện | Chọn tool riêng lẻ, chuyển tool chưa có contract chung | Bước nội bộ gắn input, công cụ, điều kiện hoàn tất và fallback |
| Browser/desktop | Có hướng dẫn riêng, dễ dùng desktop cho web | Chrome MCP cho web; agent-desktop chỉ phần native cần thiết |
| Thiếu công cụ | Hướng dẫn setup rời rạc | Research nguồn chính thức, đề xuất user-level, chờ duyệt cài |
| Ghi instruction | Ghi trực tiếp; marker lỗi và lỗi update chưa chặt | Validate, backup, thay nguyên tử; lỗi không tiến stamp thành công |

Luồng dự phòng văn bản: yêu cầu → kiểm phạm vi/quyền → tìm tool và pre-flight → lập bước → thực hiện → đọc lại trạng thái → chuyển tool nếu cần → kiểm đầu ra cuối → báo cáo. Thiếu tool chuyển sang đề xuất cài; thiếu quyền dừng đúng chỗ.

## 3. Cách tiếp cận & lý do

Tái dùng `KHOI_HUONG_DAN`, `khoi_huong_dan()`, `ghim_huong_dan_tool()` và lifecycle update hiện có. Soul giữ nguyên thứ tự ưu tiên; bổ sung nguyên tắc tự chủ có bằng chứng. Thân conventions và khối user-instruction chứa luật ngắn thường trực; hướng dẫn chi tiết nằm ở reference hiện có.

Bỏ giả định lịch sử «mọi plugin đã bật» và việc luôn hỏi lại mỗi thao tác ghi đã được user yêu cầu rõ. Quyền task chỉ áp dụng đúng file, dịch vụ, người nhận, đầu ra và hành động đã nêu. Không tự mở rộng quyền khi đổi tool.

Không dựng planner engine, capability registry hay adapter framework. Không buộc dùng nhiều tool; một tool đủ thì dùng một tool. Không tạo cơ chế poll mới khi host đã có tín hiệu hoàn tất.

Nguồn: Chrome DevTools MCP tool-reference (upload_file/handle_dialog/get_network_request); CDP Browser downloadProgress; agent-desktop Windows skill tại repo local. Những API không xuất hiện trong tool schema hiện tại không được coi là dùng được.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake, tdq-conventions, tdq-spec, tdq-plan, tdq-build | plugin:tdq-workflow | NỀN | Pipeline và approval |
| tdq-setup | plugin:tdq-workflow | DÙNG | Kiểm setup user-level |
| tdq-browser-test | plugin:tdq-workflow | DÙNG | Preview và smoke browser |
| workflow-authoring | built-in | DÙNG | Khảo sát/QC hữu hạn, read-only |
| update-config | built-in | DÙNG | Kiểm ranh giới instruction/permission khi cần |
| Đã xét 18 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

Chrome MCP kiểm kết nối trước dùng. Agent-desktop chỉ thao tác fixture đã chỉ định; không đóng Chrome cá nhân để giải quyết launch ambiguity. CLI/file tool giữ nhiệm vụ xử lý và kiểm file local.

## 3c. Giải thuật & Xử lý cốt lõi

### Agent thực thi task

1. Xác định mục tiêu, đầu vào, nơi nhận/lưu và phạm vi quyền. Thiếu thông tin làm đổi kết quả thì hỏi đúng phần đó; không hỏi lại điều đã rõ.
2. Tra tool/skill đang có, đọc schema khi cần và pre-flight. Thứ tự phụ thuộc công việc: web ưu tiên Chrome MCP, native ưu tiên agent-desktop; file/CLI dùng công cụ chuyên biệt.
3. Lập danh sách bước nội bộ đủ ngắn, mỗi bước có input, output, tool và điều kiện thành công. Đây là kế hoạch hành động, không yêu cầu xuất suy luận kín.
4. Thực hiện bước, kiểm trạng thái thực trước bước kế. Khi chuyển browser/native phải đối chiếu trang, process/window, tên file và đích; chụp lại ref sau thay đổi UI.
5. Ưu tiên upload trực tiếp qua tool nếu đủ quyền truy cập file. Chỉ dùng file picker native khi cần. Download kiểm file tồn tại, loại và nội dung phù hợp; không suy ra hoàn tất từ click.
6. Lỗi chưa gây tác dụng có thể phục hồi trong quyền hiện có. Chỉ retry khi có dữ kiện mới hoặc thay đổi điều kiện; cùng lỗi không tiến triển thì đổi cách hoặc báo blocker. Hành động có thể đã gửi/upload không lặp trước khi kiểm kết quả.
7. Nếu thiếu tool: research web, kiểm nguồn/phù hợp OS/quyền, đề xuất lệnh user-level, kiểm sau cài và cách gỡ. Chưa được duyệt thì không cài và không tự đổi permission.
8. Chờ theo event/tool wait khi có; tránh polling liên tục. Chỉ báo hoàn tất khi output kiểm được; phần chưa làm nêu rõ.

Ví dụ Gemini: xác nhận video và tác vụ → browser chọn attachment trực tiếp nếu hỗ trợ → native picker chỉ khi cần → xác minh attachment → gửi prompt đã được yêu cầu → chờ trạng thái xử lý → tải → Save As nếu xuất hiện → kiểm file cuối. Không dùng ví dụ này để tự tải file thật lên dịch vụ trong QC.

### Writer instruction

1. Đọc UTF-8 nghiêm ngặt; phân loại chưa có khối, một khối hợp lệ hoặc marker lỗi/lặp/đảo. Trường hợp lỗi giữ nguyên file và báo lỗi có đường dẫn, không nối khối để che lỗi.
2. Sinh khối mới bằng nguồn hiện có. Giữ nội dung ngoài khối, BOM và kiểu newline của file; file mới dùng UTF-8. Không đổi nội dung thì không ghi/backup.
3. Trước thay đổi file có sẵn: tạo backup không ghi đè backup cũ; ghi file tạm cùng thư mục rồi `os.replace`. Giữ quyền truy cập phù hợp, không nới ACL.
4. Đọc lại/đối chiếu để xác minh. Khi lỗi ghi hoặc replace: giữ file gốc; báo thất bại; không tiến stamp hay phát thông báo «đã cập nhật».
5. Chỉ khi đồng bộ bắt buộc thành công mới ghi stamp version. Setup lần sau retry khi trước đó thất bại. Với bản phát triển cùng version, chạy setup tường minh; không thêm state hash tự động mới.

Độ phức tạp writer: O(n) thời gian và bộ nhớ theo kích thước instruction. Tool task có O(s) bước theo kế hoạch hữu hạn; thời gian dịch vụ ngoài không suy ra từ thuật toán và không cam kết tốc độ phần trăm.

## 3d. Mental Model cho Fresher Dev

Agent như người phụ trách công việc: dùng đúng dụng cụ cho từng đoạn, kiểm kết quả trước bàn giao, không bắt khách hướng dẫn từng nút. Đổi dụng cụ không làm quyền truy cập rộng hơn.

- Pre-flight: kiểm tool kết nối và đủ khả năng trước thao tác.
- Handoff: chuyển đúng đối tượng công việc giữa browser/native/file.
- Bằng chứng hoàn tất: trạng thái hoặc file đọc lại được, không phải lời tool báo click thành công.
- Managed block: phần instruction TDQ quản lý, không phải toàn bộ file cá nhân.

## 4. Yêu cầu bắt buộc

Log runtime bật mặc định bằng cơ chế sẵn có, timestamp và nguyên nhân đủ debug; cho tắt qua cấu hình log hiện có. Không ghi nội dung instruction riêng, tin nhắn, token hay file upload vào log.

TDD cho writer/update; eval-plan trước implement cho thay đổi hành vi skill. Eval gồm route đúng, route thừa, thiếu tool, từ chối quyền và kết quả chưa rõ; không coi test chuỗi từ khóa là chứng nhận hiệu quả agent thật.

Backup + rollback thao tác user-level là bắt buộc. Chỉ áp dụng instruction thật trên máy hiện tại sau fixture và kiểm hồi quy đạt. Quyền áp dụng đã được user cấp cho request này, nhưng vẫn giữ các cổng spec/plan.

## 5. Ràng buộc & rủi ro

Giữ tầng luật/CLI/hook hiện có; state chỉ ghi qua CLI. Không thay mode harness, không permission bypass, không cập nhật instruction host khác. Không thêm package mới cho writer.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Nội dung user bị ghi đè | Mất cấu hình cá nhân | Validate marker, backup, atomic replace, test CRLF/Unicode |
| Stamp che lỗi | Phiên sau không retry | Không ghi thành công khi writer lỗi; test hook thực qua fixture |
| UI thay đổi lúc handoff | Sai file hoặc sai người nhận | Quan sát mới, đối chiếu identity, dừng khi mơ hồ |
| Retry gây gửi trùng | Tác dụng ngoài ý muốn | Phân loại delivery, kiểm trạng thái trước lặp |
| Capability bị suy đoán | Agent treo hoặc báo xong giả | Schema đang có là căn cứ, lỗi/thiếu báo thật |
| Cài công cụ vượt quyền | Thay môi trường ngoài phạm vi | Chỉ đề xuất; user duyệt mới cài user-level |

## 6. QC & Definition of Done

QC `ultra`: full unit suite tại QC-F1, hồi quy vùng chạm, smoke setup/runtime an toàn, Workflow QC độc lập hữu hạn. Smoke browser dùng dữ liệu mẫu local; không gọi Gemini thật, không gửi Zalo thật, không đổi clipboard/tài khoản cá nhân để chứng minh routing.

| # | Hạng mục kiểm | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |
|---|---|---|---|---|
| Q1 | Luật thường trực và soul | Nêu đủ lập bước, khám phá, phối hợp, tự kiểm, giữ chất lượng và quyền | Có MCP-first; chưa có contract chung | Sửa luật và chạy lại corpus |
| Q2 | Routing và handoff | Web chọn Chrome MCP; native dùng desktop khi cần; không ép nhiều tool; kiểm identity | upload_file có schema; thử Zalo trước cho thấy desktop composer không editable | Chọn fallback hợp lệ, nêu thiếu capability |
| Q3 | Thiếu công cụ | Research và đề xuất user-level; không cài trước duyệt | User chốt 2a + đề xuất từ web | Báo blocker, không nới quyền |
| Q4 | Bảo toàn instruction | Nội dung ngoài khối và encoding giữ nguyên; backup đúng; lần chạy lại no-op | Writer hiện ghi trực tiếp và errors=replace | Giữ/khôi phục bản gốc, không áp dụng máy thật |
| Q5 | Update thất bại | Lỗi đọc/ghi/replace/marker không tiến stamp, phiên sau retry; không báo thành công giả | Caller hiện bắt lỗi rồi có thể ghi stamp | Sửa propagation, kiểm hook fixture |
| Q6 | Chống lặp và sai hoàn tất | Gửi/upload có thể đã xảy ra thì quan sát trước; download có file mới báo xong; retry hữu hạn theo tiến triển | Thiếu contract thống nhất | Ghi kết quả partial, không giả PASS |
| Q7 | Tương thích | Tests hiện hữu và eval có chứng cứ; không sửa state schema/permission/host khác | Kiến trúc và tests khảo sát đã ghi brief | Fix và rerun vùng bị ảnh hưởng |
| Q8 | Setup thật + report | CLAUDE.md user-level có luật mới, backup và phần riêng đối chiếu đạt; report nêu giới hạn | Máy có Chrome MCP và agent-desktop, môi trường LSP module chưa đầy đủ | Không ghi thật nếu fixture trượt; báo lý do |

Không đặt ngưỡng tốc độ suy đoán; đo số bước và kết quả thực trên corpus. Giới hạn runtime smoke theo quy tắc QC hiện có, không tăng trần để giấu hang.

## 7. Câu hỏi còn mở
<!-- tdq-archify-binding:start -->
<!-- manifest: 2026-11-03-1420-phoi-hop-cong-cu-preview.manifest.json -->
<!-- manifest_digest: 8f9501654f4f723b351d70d3443f17bdd4a781a3b3d239169d46b693980587a1 -->
<!-- tdq-archify-binding:end -->