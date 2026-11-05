# Quy tắc làm việc cho Claude

## 1. Quy trình chung
- Làm như chuyên gia kỹ tính: phân tích kỹ, research trước khi kết luận, không đoán.
- Yêu cầu chưa rõ → interview trước. Mọi câu hỏi có option: mỗi option đúng 1 dòng,
  khuôn `- A (đề xuất): nội dung`, cấm gộp option vào đoạn văn.
- Đủ thông tin → plan → tự review → trình plan → **chờ user duyệt** mới làm. Mọi task.
  Không tự vào plan mode; trình plan trong chat hoặc file rồi chờ duyệt.

## 2. Git & worktree
- Project chưa có git → được khởi tạo git/worktree, nhớ kiểm tra merge worktree.
- Tên branch/commit/worktree KHÔNG bắt đầu bằng `claude`, `antigravity`, `gemini`, `codex`.
- Commit message không chứa "generated with…", "được tạo bởi…", Co-Authored-By của AI.
- Chỉ commit/push khi user yêu cầu. Ngoại lệ duy nhất: build TDQ gặp chặn kỹ thuật → tự
  commit để gỡ chặn (message chuẩn, KHÔNG push, liệt kê commit đó trong report).

## 3. Research & độ tin cậy
- Search nhiều hướng trước khi tổng hợp; `tavily-primary` là lớp search mặc định.
- Không bao giờ đưa API key vào câu trả lời, log, lệnh shell hay prompt gửi model.
- Mọi kết luận phải có nguồn — không được bịa thông tin chưa xác định.

## 4. Trình bày
- Ngắn gọn nhất có thể, đi thẳng vào vấn đề chính.

## 5. Log
- Khi develop: log đầy đủ, có timestamp, phục vụ debug. Sản phẩm build ra luôn có log
  service bật mặc định, tắt được qua config.
- Turn có đổi repo → append tóm tắt vào `docs/workinglog/YYYY-MM-DD.md`.

## 6. TDQ Workflow — mặc định tuyệt đối
- **Mọi prompt mới → skill `tdq-intake`**, kể cả câu hỏi nhỏ; message thuộc request đang
  mở thì không tính. Thấy `[TDQ:INTAKE]` → mở intake trước mọi việc.
- Chỉ NGƯỜI DÙNG duyệt, bằng chat thường. Câu chữ mơ hồ → HỎI lại, cấm tự suy diễn duyệt.
- Ghi duyệt/state CHỈ qua `scripts/tdq_state.py`; cấm sửa `docs/tdq/state.json` trực tiếp.
- Gộp gate: duyệt spec → viết plan ngay turn đó; duyệt plan → hỏi cách chạy
  (main | subagent), chọn xong build luôn. Duyệt đã nói sẵn mode → build thẳng.
- Spec/plan/report viết tiếng Việt; report ngắn gọn (10-20 dòng). Tick `[x]` khi task pass.
- Cuối turn có đổi code → `graphify extract . --code-only`.
- Sub-agent: description mở đầu `<model>-<effort>-<việc>`, vd `sonnet-low-research`.

## 7. Chi tiết ở đâu — đọc khi cần, KHÔNG chép lại vào đây
Quy ước chung (working log, failover tavily, định tuyến plugin, QC): `skills/tdq-conventions/`.
Lane, tầng `nhỏ`, khuôn spec/plan, mode thực thi: các skill `tdq-*`.

## 8. Plugin ngoài
Kiểm inventory và kết nối thực; không giả định plugin đã bật. Dùng tool trong quyền đã cấp,
không hỏi lại hành động user yêu cầu rõ. HỎI trước cài mới, OAuth/credential, thao tác phá hủy
hoặc mở rộng file/dịch vụ/người nhận. Không đổi tool để vượt từ chối quyền.

## 9. Bộ nhớ dài hạn
Việc quan trọng (kiến trúc, sở thích user, lỗi tái diễn) → search mem0
(project = tên repo) trước khi kết luận, chốt xong thì `remember` một fact ngắn.
Chi tiết: skill `mem0-memory`.

<!-- TDQ:TOOLS -->
## Bộ tìm kiếm 3 tầng

- Bắt đầu phiên/tra cứu code: gọi `mcp__lsp__start_lsp(root_dir, language_id)` trước (TS/JS cần mở 1 file bằng `open_document` để nhận project).
  Tra symbol: `list_symbols` (trong file), `find_symbol` (workspace), `find_references` (nơi gọi). Gọi LSP mở khóa 10 lượt grep.
  Tên chính xác đã biết → grep. Vỡ lan, bản đồ kiến trúc → graphify.
  Khái niệm mơ hồ → `graphify query "<câu hỏi>"` song song grep nhiều từ đồng nghĩa, rồi gộp.
- Mỗi tầng có phụ thuộc riêng và chết trong im lặng; tầng nào chết thì rơi xuống grep.
- Kiểm các bậc bằng `python <đường dẫn thư mục cài TDQ-Workflow>/scripts/tdq_lsp.py check`; thiếu công cụ thì research nguồn chính thức và đề xuất cài user-level, chờ user duyệt. Chỉ chạy `python <đường dẫn thư mục cài TDQ-Workflow>/scripts/tdq_setup.py` khi phạm vi setup đã được duyệt (Windows có thể dùng `py -3`).
  Luật đầy đủ kèm số đo: `<đường dẫn thư mục cài TDQ-Workflow>/skills/tdq-setup/references/uu-tien-tim-kiem.md`.
- Khảo sát code 3 chiều (Triangulation Code Exploration) trong phase analyze/quick_analyze: Quét rộng bằng Grep tự do không giới hạn quota. Đào sâu cấu trúc bằng LSP (find_references, go_to_definition) và quét vỡ lan bằng Graphify (affected 2 bước). Lập bảng đối chiếu vùng chạm để không bỏ sót mã nguồn khi refactor hoặc mở rộng.
- Tự quyết xử lý LSP: áp dụng `--bo-qua-lsp "<lý do rõ ràng>"` cho tài liệu/nghiên cứu/cài MCP hoặc tham chiếu nội tệp khi phù hợp. Phục hồi công cụ đã cài trong quyền hiện có; thiếu Language Server/dependency thì tìm nguồn chính thức, đề xuất cài user-level và chờ user duyệt, không tự cài hoặc nới quyền.

## Nguyên tắc TDQ Workflow bắt buộc

- Mọi yêu cầu mới từ người dùng BẮT BUỘC phải mở bằng skill `tdq-workflow:tdq-intake` (hoặc `tdq-intake` nếu cài cục bộ) và chạy theo pipeline của TDQ Workflow (quick hoặc full). Tuyệt đối KHÔNG tự ý chuyển sang plan mode của harness (`EnterPlanMode`) khi nhận yêu cầu.
- Yêu cầu chứa '_tdq_direct' → tự động phân tích & tìm kiếm mã nguồn, lập mini-plan và chỉ dừng ở 1 cổng duyệt mini-plan (không hỏi chọn pipeline, không phỏng vấn).
- Ngoại lệ Refactor & Kiến trúc sạch (Rung 1): Khi người dùng yêu cầu Refactor, tái cấu trúc hoặc Clean Architecture/SOLID, cấu trúc sạch và tính mở rộng module đứng TRÊN luật phẫu thuật 1 dòng tối thiểu. Cấm tự ý ép gộp các tầng/lớp hợp lý thành hàm phẳng nếu làm vỡ chủ đích thiết kế.
- Tự phục hồi môi trường (Self-healing): lỗi 'Python was not found' thì dùng Python đã cài (`python` hoặc `py -3`). Chẩn đoán trước; chỉ sửa kết nối/shim trong quyền đã cấp. Không chạy setup toàn phần nếu sẽ cài mới hoặc đổi permission/host ngoài phạm vi.
- Skill báo `Unknown skill` → plugin chưa bật ở project này: đọc `<đường dẫn thư mục cài TDQ-Workflow>/skills/tdq-intake/SKILL.md`, thay `${CLAUDE_PLUGIN_ROOT}` bằng `<đường dẫn thư mục cài TDQ-Workflow>`, làm theo; nhắc người dùng chạy lệnh setup ở trên để bật plugin.
- Không được tự ý đổi mode làm việc hiện tại (`EnterPlanMode`, `ExitPlanMode`...).
- Mọi câu hỏi, lựa chọn option và duyệt gate PHẢI trao đổi trực tiếp trong chat (dạng `1a 2b 3c`, "duyệt spec", "duyệt plan", "duyệt nhanh" hoặc câu tự nhiên). Tuyệt đối CẤM mở popup question UI (`AskUserQuestion`) của agent code.

## Nguyên tắc Ưu tiên MCP & Bộ kỹ năng MCP (MCP-First)

- Luôn ưu tiên dùng MCP và bộ skill của MCP (nếu có); ưu tiên lập phương án dùng MCP trong spec/plan để giải quyết trọn vẹn yêu cầu người dùng.
- Kiểm tra kết nối trước (Pre-flight check): kiểm inventory, schema và endpoint cấu hình thực trước thao tác MCP. Nếu chưa kết nối, tự phục hồi công cụ đã cài trong quyền hiện có rồi probe lại; cần thao tác ngoài quyền thì hướng dẫn user. Không suy trạng thái runtime từ cấu hình.
- Ví dụ: Khi phát triển mã nguồn Roblox hoặc Unity, luôn kiểm tra sự hiện diện của MCP và bộ skill/tool của MCP tương ứng để thực hiện và kiểm chứng thay vì thao tác mù mờ.
Chi tiết cẩm nang: `<đường dẫn thư mục cài TDQ-Workflow>/skills/tdq-setup/references/mcp-first-guide.md`.

## Tự chủ phối hợp công cụ có kiểm chứng

- Mọi task: xác định mục tiêu, input, đích và quyền; lập bước nội bộ ngắn với tool, output và điều kiện xong. Không yêu cầu xuất suy luận kín. Chỉ hỏi thông tin thiếu làm đổi kết quả; giữ gate TDQ.
- Khám phá tool/skill thực trong phiên. Web ưu tiên Chrome MCP; native app/dialog dùng agent-desktop khi cần; file/CLI dùng tool chuyên biệt. Một tool đủ thì không ép phối hợp nhiều tool; chọn đường ít bước nhất vẫn đúng và có quyền.
- Ưu tiên upload_file trực tiếp nếu schema có và browser host đọc được file. Khi chuyển browser/native: kiểm trang, process/window, file và đích bằng quan sát/ref mới; xác minh attachment trước gửi. handle_dialog không mặc định điều khiển Windows picker.
- Download/Save As phải kiểm file cuối tồn tại, loại và nội dung phù hợp; click thành công chưa phải hoàn tất. Chờ event/tool wait nếu có, không poll dồn dập.
- Delivery gửi/upload chưa rõ: quan sát đích trước, không lặp thao tác khi chưa biết kết quả. Retry chỉ khi có dữ kiện mới/điều kiện đổi; không tiến triển thì đổi phương án hợp lệ hoặc báo blocker. Không đổi tool để vượt hành động đã bị từ chối.
- Thiếu tool: research nguồn chính thức, kiểm OS/quyền, đề xuất lệnh cài user-level kèm kiểm chứng và gỡ; chờ user duyệt. Không tự cài mới, đổi permission, OAuth hoặc nới phạm vi file/dịch vụ/người nhận.
- Tự kiểm từng bước và output cuối; báo rõ hoàn tất/partial/blocker bằng bằng chứng. Chất lượng > runtime > context cost. ĐÚNG: upload trực tiếp, kiểm attachment, gửi một lần, kiểm file tải. SAI: gửi lại khi timeout chưa rõ hoặc báo xong chỉ từ click.

## Quy tắc Git và Attribution bắt buộc

- Tuyệt đối KHÔNG thêm dòng `Co-Authored-By: Claude Code...` hoặc bất kỳ attribution trailer nào vào git commit message hoặc PR body. Mọi commit và PR chỉ chứa nội dung kỹ thuật thuần túy do người dùng và agent trao đổi.
- Vùng tự động mang theo khi đổi/hợp nhất nhánh: Khi mở nhánh request hoặc khi merge về nhánh gốc, nếu working tree dirty nhưng CHỈ thuộc `docs/**`, `*.md`, `logs/**`, `*.log`, `graphify-out/**` thì TỰ ĐỘNG mang theo, commit hoặc merge. Không cần dừng lại hỏi người dùng. Chỉ dừng hỏi khi có thay đổi dirty ở mã nguồn (`scripts/`, `src/`, `hooks/`, `tests/`...).

## Chuẩn Trình bày & Báo cáo (Soul & Report)

- Luôn trình bày đơn giản, dễ hiểu, ngắn gọn nhưng trực quan, đầy đủ thông tin để mọi người đọc đều nắm được bản chất và bằng chứng.
- Phase `report` luôn xuất cặp `docs/tdq/reports/<slug>.md` và `Archify HTML` (`docs/tdq/reports/<slug>.html`); khi có cập nhật bắt buộc nêu rõ 4 phần: (1) Trước request trạng thái/flow thế nào, (2) Sau request thế nào, (3) Đã test gì, và (4) Kết quả test ra được cái gì.
<!-- /TDQ:TOOLS -->
