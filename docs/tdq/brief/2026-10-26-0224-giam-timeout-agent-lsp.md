# Giảm timeout và thời gian chờ agent-lsp
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn
> Mở request handel cả 6 cái bạn đề xuất đi

### Đọc hiểu lần đầu
- Mục tiêu: xử lý đủ sáu nhóm cải thiện agent-lsp đã trao đổi, giảm chờ kéo dài mà không giảm chất lượng phân tích code.
- Phạm vi dự kiến:
  1. Chọn công cụ theo nhiệm vụ: truy vấn symbol cụ thể, Grep cho chuỗi/cấu hình, Graphify cho phụ thuộc rộng; thay yêu cầu blast_radius vô điều kiện bằng chính sách phù hợp.
  2. Giới hạn chờ có hiệu lực: phân biệt idle timeout, hard deadline, cancellation và ngân sách indexing riêng; không chỉ viết quy tắc trong prompt.
  3. Giới hạn blast_radius: chỉ file cần phân tích, exported mặc định, transitive tắt mặc định; không giả định filter giảm công việc nội bộ.
  4. Quản lý vòng đời server, workspace/worktree và indexing: tái sử dụng đúng project; không diễn giải symbols=0 thành không có ảnh hưởng.
  5. Retry/fallback/concurrency: không retry nguyên trạng, ngắt chuỗi lỗi theo workspace, giới hạn truy vấn nặng và phối hợp server dùng chung.
  6. Telemetry và benchmark: p50/p95, thời gian chờ, kết quả hữu ích, fallback/restart và độ bao phủ caller có đáp án chuẩn.
- Bằng chứng đầu vào từ điều tra chỉ đọc trước: 302 lượt gọi trong 786 transcript; 5 timeout có thông báo không có response/progress trong 1800 giây (4 tại claudecodeui, 1 tại TDQ-Workflow); 14 lượt trả đồ thị trên 60 giây; một lượt 308 giây trả symbols=0. Đây là thời gian đầu-cuối, không phải CPU server; chưa xác định nguyên nhân nội bộ.
- Bằng chứng timeout: `C:/Users/admin/.claude/projects/C--Users-admin-Documents-Projects-ForAgentCode-TDQ-Workflow/3b281cef-5b28-4d52-bfab-47f44c648e94.jsonl:3982`; `C:/Users/admin/.claude/projects/C--Users-admin-Documents-claudecodeui/6fbdfb21-44c4-418f-8e0c-97cfd18c702c.jsonl:30599`.
- Cần khảo sát: khả năng timeout/cancel của client và agent-lsp đang cài; nơi sở hữu instruction bắt buộc blast_radius; phạm vi thay đổi trong TDQ so với dependency bên ngoài. Không tự sửa plugin bên ngoài hoặc coi giảm timeout là sửa xong nguyên nhân treo.
- Các ngưỡng 10–60 giây đã đề xuất là giả thuyết benchmark, chưa phải cam kết hay cấu hình đã xác minh.
- Tái hiện cần sandbox và deadline thực để tránh lặp lại 30 phút chờ; chưa gọi lại tác vụ từng treo.
- Loại dự kiến: bugfix. Pipeline đề xuất: full, vì chạm chính sách, điều phối MCP, hooks/setup và kiểm chứng đa project.

## Hiểu & kiến thức

### Môi trường và mức độ bằng chứng
- Pre-flight 2026-10-26: agent-lsp 0.19.2; 7/8 bậc đạt, smoke 3/3; Graphify có cảnh báo độ mới không chặn. Smoke môi trường không chứng minh blast_radius hết treo.
- Request đã mở theo lane full, loại bugfix, nhánh `bugfix/giam-timeout-agent-lsp`, nhánh gốc `dev`; phase analyze. Chưa sửa source/settings, chưa duyệt spec/plan.
- Dependency binary: `C:/Users/admin/.local/bin/agent-lsp.exe`. Source local: `C:/Users/admin/Documents/Resreach_LSPPlugin/agent-lsp`.
- Cảnh báo provenance: source local HEAD `38ca4880dd5d499a76fe83ecaaa1bd5040e266fc` thuộc v0.23.0, KHÔNG phải binary 0.19.2. Những kết luận dưới đây đã đối chiếu bằng `git show v0.19.2:<path>` tại commit `c7ea45e5a3f1d971293a7f56337deb2afb5bbe71`; không dùng số dòng HEAD cho tag cũ.
- Log chứng minh triệu chứng 1800 giây ở client. Chưa có tái hiện có kiểm soát hoặc stack trace chứng minh nguyên nhân của năm lượt đó; không gọi lại batch từng treo khi chưa có trần thời gian và cleanup đã kiểm chứng.

### Năng lực dùng được
Kiểm kê ngày 2026-10-26: bộ lọc `lsp mcp timeout benchmark` trả 11 skill trên đĩa; đã xét thêm các skill built-in trong context. Có mặt trên đĩa không đồng nghĩa gọi được qua Skill.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | Mở request, điều tra log, khảo sát ba chiều |
| tdq-conventions | plugin:tdq-workflow | NỀN | Luật state, gate, working log và ranh giới chỉnh sửa |
| tdq-spec | plugin:tdq-workflow | NỀN | Đặc tả sau khi chốt bằng chứng kỹ thuật |
| tdq-build | plugin:tdq-workflow | NỀN | Chỉ triển khai sau duyệt plan |
| tdq-lean | plugin:tdq-workflow | NỀN | Tránh thêm proxy/framework khi cấu hình chuẩn đủ dùng |
| tdq-setup / tdq-plan / tdq-check-status | trên đĩa | NỀN | Tham chiếu script/tài liệu theo pipeline; không giả định có Skill callable |
| update-config | built-in | DÙNG | Kiểm tra schema, merge cấu hình và chứng minh hook lifecycle |
| claude-api | built-in | DÙNG | Phân biệt API timeout với Claude Code MCP; dẫn sang tài liệu harness, không thêm SDK API |
| Các skill còn lại đã xét | plugin/built-in | KHÔNG | khác lĩnh vực |

### Đối chiếu vùng chạm
| Vùng file chạm | Phát hiện qua lớp nào (Grep/LSP/Graphify) | Tác động & quan hệ |
|---|---|---|
| `skills/tdq-setup/references/uu-tien-tim-kiem*.md` | Grep/Read | Chính sách chọn tool; bảng phân loại blast radius chưa thống nhất với mô tả phía trên |
| `scripts/tdq_setup.py`, `scripts/tdq_lsp.py` | Grep/Read | Cài binary, ghi cấu hình MCP, doctor; timeout subprocess hiện có không phải timeout MCP đang gọi |
| `scripts/lsp_module.py`, `tests/test_lsp_module.py` | Grep/LSP/Graphify | Sinh start/open/references và kiểm môi trường; LSP trả 4 refs dạng tổng quát, thiếu vị trí nên chỉ dùng làm tín hiệu; Graphify affected loi_goi_mcp không có node |
| `hooks/scripts/lsp_gate.py`, `tests/test_lsp_gate.py` | Grep/Read | Gate hiện chỉ kiểm root/language cho start_lsp; giữ hành vi JS/TS chung family, project ngoài bảng không bị chặn |
| `hooks/hooks.json`, `hooks/scripts/search_observe.py`, `tests/test_search_observe.py` | Grep/Graphify/Read | Pre ghi attempt có chủ đích để không chặn fallback khi LSP lỗi; Post không có duration/outcome; chưa đăng ký PostToolUseFailure |
| `scripts/search_rules.py`, `scripts/search_replay.py`, `tests/test_search_rules.py`, `tests/test_search_replay.py` | Grep/Graphify/Read | Graphify affected la_goi_khai_niem depth 2 dẫn tới observer/replay; replay bỏ tool_result nên chưa đo latency |
| agent-lsp upstream tag v0.19.2 | Agent nghiên cứu + git show đối chiếu | Chỉ đọc dependency; không sửa source/plugin/binary bên ngoài request TDQ |

Đồ thị có cảnh báo freshness và kết quả nhiễu; không xem kết quả rỗng hoặc refs tổng quát là bằng chứng không có ảnh hưởng. Đã đọc đầy đủ `docs/kien-truc.md`; giữ ranh giới hooks → scripts, không đảo chiều.

### Phát hiện đã kiểm chứng
1. **Nguồn instruction:** tag v0.19.2 `cmd/agent-lsp/server.go:326-353` hardcode chỉ thị blast_radius trước mọi edit trong `ServerOptions.Instructions`. Context MCP phiên hiện tại cũng chứa nguyên văn này. Không phải yêu cầu chỉ nằm trong TDQ.
2. **Giới hạn nội bộ không đồng nghĩa hard wall-clock:** `internal/tools/change_impact.go:81-89` đặt context 90s; `:457` đặt 15s/symbol; `:467-512` có pool 16, acquire semaphore không select ctx rồi wg.Wait. `internal/lsp/client.go:814-839` gọi writeRaw trước khi tạo timer và trước select ctx.Done. Đây là điểm có khả năng vượt budget nếu thao tác trước select bị kẹt, CHƯA phải nguyên nhân đã tái hiện của log thực tế.
3. **Cancellation:** nhánh timeout/context trong `internal/lsp/client.go:830-839` chỉ xoá pending và return, không gửi `$/cancelRequest` trong nhánh này. Không được báo server downstream đã dừng chỉ vì client hết chờ.
4. **Warmup:** tag v0.19.2 `internal/lsp/warmup.go:56` có firstRefTimeout 300s, `:78` có mutex; cần kiểm đường truyền context và tài nguyên dùng chung khi tái hiện. Không khẳng định daemon luôn warm hoặc mọi query sẽ về mili-giây.
5. **Hook lifecycle:** hooks.json đăng ký observer tại PreToolUse và PostToolUse, không có PostToolUseFailure. `tests/test_search_observe.py:63-69` yêu cầu attempt mở khoá fallback ngay cả khi LSP chưa initialized. Telemetry outcome phải tách khỏi credit này, không vô tình tạo vòng lặp ép gọi lại LSP.
6. **Cấu hình client có sẵn:** tài liệu chính thức `https://code.claude.com/docs/en/env-vars.md` (tra ngày 2026-10-26) ghi:
   - `MCP_TIMEOUT`: startup, ms, mặc định 30000.
   - `MCP_TOOL_TIMEOUT`: tool execution, ms, mặc định 100000000; per-server `timeout` trong `.mcp.json` ghi đè cho server đó.
   - `CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT`: không response/progress, ms; mặc định stdio 1800000, network 300000; 0 tắt; tối thiểu 1000, bị cap theo tool timeout.
   - Per-server timeout >=1000 cũng đặt SÀN idle window; do đó không được giả định timeout riêng 60s và idle global 15s sẽ cho LSP idle 15s. Tính tương tác này phải có test.
   - Các thông số tài liệu hiện hành chưa được kiểm chứng runtime trên phiên đang chạy; không mặc định trường timeout của `.mcp.json` được hỗ trợ y hệt tại mọi host/config location.
7. **Timeout hook khác timeout tool:** schema update-config định nghĩa timeout cho command hook; hook trả xong không còn kiểm soát thời gian MCP. Post hook chỉ quan sát sau khi lệnh kết thúc, không thể tự chấm dứt lệnh đang treo.

### Hướng xử lý sáu nhóm — chưa phải thiết kế đã duyệt
| Nhóm | Hướng ưu tiên | Điều kiện giữ chất lượng |
|---|---|---|
| 1. Chọn tool | Quy tắc theo nhiệm vụ, bỏ yêu cầu blast_radius vô điều kiện trong hướng dẫn TDQ; nhận diện instruction upstream vẫn còn | Refactor/rename vẫn cần semantic references phù hợp, không thay bằng text match rồi coi tương đương |
| 2. Budget/cancel | Kiểm chứng timeout per-server có sẵn trước khi cân nhắc adapter TDQ; tách startup/indexing/query; kiểm cancel thực | Không đổi timeout global cho các MCP không liên quan; không báo cancellation thành công nếu downstream còn chạy |
| 3. Blast radius hẹp | Batch nhỏ theo file cần thiết, exported, transitive=false mặc định; nâng phạm vi khi nhiệm vụ đòi hỏi | Ghi rõ partial/warnings; filter chỉ được coi giảm việc khi có bằng chứng |
| 4. Workspace/indexing | Đúng root/language, TS/JS open_document, tái sử dụng đúng workspace, scope chỉ khi hiểu dependency | Không loại tests/callers ngoài scope; không coi symbols=0 là sạch; worktree không dùng nhầm snapshot |
| 5. Retry/concurrency | Không retry nguyên trạng, breaker theo workspace/tool, budget hàng đợi, giới hạn heavy call | Không kill/restart daemon dùng chung; tool sửa code không tự retry; denied/user-cancel không biến thành health failure |
| 6. Telemetry/benchmark | Ghép attempt/result bằng ID, duration/outcome, cold/warm, p50/p95 và caller oracle | Tách error/partial/empty/unmatched; timestamps âm không vào latency; không lưu nội dung code/prompt/secret |

### Phương án loại và giới hạn
- Loại: chỉ đổi timeout hook; chỉ viết prompt rồi tuyên bố deadline có hiệu lực; tự patch plugin/binary ngoài; restart tất cả server khi một query lỗi.
- Chưa chọn proxy mới: phải chứng minh cấu hình chuẩn không đáp ứng trước; proxy cũng không tự giải quyết downstream cancellation trong broker dùng chung.
- Không áp dụng mù `scope=scripts,src`: có thể làm mất test callers và tham chiếu liên module.
- Không nâng agent-lsp tự động lên source HEAD v0.23.0; cần kiểm tương thích và scope riêng nếu thay dependency.

### Lộ trình
| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Analyze: đối chiếu version và client capability | CÓ | Đã xác minh nguồn instruction, tag và phân biệt các timeout |
| Analyze: tái hiện giới hạn chờ có kiểm soát | CÓ | Chưa chạy; cần fixture server chậm/không đọc stdin, kiểm cancellation và cleanup dưới watchdog độc lập |
| Spec → plan | CÓ | Giữ cổng duyệt, chốt cơ chế enforcement và tiêu chí cả sáu nhóm sau bằng chứng |
| Implement | CÓ | Chỉ sau duyệt; test đỏ thật cho hành vi được sửa |
| QC ultra | CÓ | Người dùng đã chọn 3c (muc_qc=ultra): kiểm đầy đủ + rà bảo mật + test tự động cho mọi tiêu chí |
| Benchmark/runtime có giới hạn | CÓ | Bằng chứng chức năng của timeout, không chỉ tốc độ unit test; cần ghi budget và cleanup trong spec |
| Agent QC độc lập | CÓ | Kiểm cancellation/shared-server và caller coverage; đưa vào route để duyệt cùng spec |
| Fan-out triển khai nhiều agent | BỎ | Chưa thấy công việc tách biệt cần thiết; tránh thay đổi đồng thời config/lifecycle |
| Report | CÓ | Báo số đo trước/sau, chất lượng, trường hợp chưa hỗ trợ và rollback |

### Các luồng chức năng cấu thành request
- **Luồng 1 (Chính sách chọn tool & trung hòa chỉ thị upstream):** Đồng bộ quy tắc chọn công cụ theo nhiệm vụ trong `skills/tdq-setup/references/uu-tien-tim-kiem.md`, `uu-tien-tim-kiem-chi-tiet.md` và `KHOI_HUONG_DAN` trong `scripts/tdq_setup.py`; ghi rõ quy tắc ghi đè chỉ thị `IMPORTANT: call blast_radius before editing any file` từ `agent-lsp` MCP server instructions và sửa mâu thuẫn phân loại `blast_radius` giữa dòng 21 và bảng dòng 72.
- **Luồng 2 (Giới hạn chờ MCP có hiệu lực):** Trong `scripts/tdq_setup.py`, cấu hình mặc định `CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT = "90000"` (90 giây) vào khối `env` của `~/.claude/settings.json` khi người dùng chưa tự đặt giá trị riêng; không đặt `timeout` riêng trên server `lsp` trong `~/.claude.json` nếu điều đó nâng sàn idle window vượt 90 giây.
- **Luồng 3 (Kiểm soát phạm vi `blast_radius`, vòng đời workspace & circuit breaker tại `lsp_gate.py`):** Mở rộng matcher trong `hooks/hooks.json` để `hooks/scripts/lsp_gate.py` kiểm soát cả `mcp__lsp__start_lsp` và `mcp__lsp__blast_radius` (cùng các truy vấn LSP nặng khi workspace đang mở mạch ngắt):
  - Với `blast_radius`: chỉ cho phép khi `changed_files` không rỗng và `<= 3` file, `scope` là `"exported"` (hoặc mặc định không truyền `"all"`), `include_transitive` là `false` (hoặc mặc định); chặn và hướng dẫn dùng `find_references` + `graphify affected` khi vượt ngưỡng.
  - Với circuit breaker theo workspace: khi sổ tìm kiếm ghi nhận lỗi/timeout liên tiếp của LSP trong cùng workspace/request, tự động mở mạch ngắt tạm thời cho `blast_radius` (và hướng dẫn fallback sang `find_references` hoặc `Grep` + `Graphify`) thay vì để agent retry nguyên trạng; không tự kill/restart daemon `agent-lsp` dùng chung.
  - Với vòng đời workspace/indexing: giữ nguyên kiểm tra `root_dir`/`language_id` cho `start_lsp`, cảnh báo không suy diễn `symbols=0` là không có ảnh hưởng và giữ quy tắc `open_document` chỉ dùng 1 file mồi cho TS/JS.
- **Luồng 4 (Telemetry thời gian chạy, phân loại kết quả & benchmark caller coverage):**
  - Mở rộng `hooks/hooks.json` đăng ký thêm `PostToolUseFailure` cho `mcp__lsp__.*` vào `hooks/scripts/search_observe.py`.
  - Trong `hooks/scripts/search_observe.py`: bảo toàn 100% cơ chế ghi nhận `khai_niem` ở `PreToolUse` (để không làm gãy quyền mở khóa `Grep` khi LSP lỗi); bổ sung ghi nhận kết quả thực thi ở `PostToolUse`/`PostToolUseFailure` kèm `duration_ms` (ghép cặp từ mốc `PreToolUse` theo `tool_use_id` hoặc cặp gọi gần nhất) và `outcome` (`ok`, `empty`, `error`, `timeout`), không lưu nội dung code/prompt/secret.
  - Trong `scripts/search_replay.py` (và `scripts/search_rules.py`): bổ sung hàm tổng hợp telemetry (`p50`, `p95`, tỷ lệ `ok`/`empty`/`error`/`timeout`, đối chiếu độ phủ caller với tập đáp án chuẩn/oracle) từ transcript JSONL và từ sổ tìm kiếm.

## Hỏi đáp
- Người dùng yêu cầu xử lý đủ sáu nhóm, sau đó trả lời `1a`: chọn chế độ chuyên sâu/full.
- Vòng hỏi đáp chốt chính sách cuối phase `analyze` (người dùng trả lời `1a 2a 3c`):
  - **Câu 1 (`1a`):** Chọn chặn có điều kiện đối với `mcp__lsp__blast_radius` tại `hooks/scripts/lsp_gate.py` — cho phép khi `changed_files` ≤ 3 file, `scope="exported"`, `include_transitive=false` và workspace không mở circuit breaker; chặn và hướng dẫn chuyển sang `find_references` + `graphify affected` khi vượt ngưỡng hoặc khi workspace vừa bị timeout/lỗi.
  - **Câu 2 (`2a`):** Chọn đặt mặc định `CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT = "90000"` (90 giây) qua `scripts/tdq_setup.py` khi người dùng chưa tự cấu hình giá trị riêng.
  - **Câu 3 (`3c`):** Chọn mức QC **siêu kỹ (`muc_qc=ultra`)** — kiểm đầy đủ, rà lỗ hổng bảo mật và viết test tự động cho mọi tiêu chí.
