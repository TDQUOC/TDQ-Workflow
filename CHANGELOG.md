# Changelog

Mới nhất trên cùng. Ngày theo múi giờ máy phát hành.

## 0.94.0 — 2026-11-06

Giảm khả năng dừng giữa plan trên Claude Code và làm rõ cách khôi phục công việc.

- Stop hook nhắc mã task và `Test:` đang cần làm; sau ba lần plan không tiến triển, báo task/số việc còn mở rồi cho dừng an toàn, không lặp vô hạn.
- SessionStart ở resume/compact nhắc task `[~]` hoặc task đầu `[ ]`; task `[>]` đang giao trợ lý thì chờ thay vì chạy trùng.
- Luật build ưu tiên plan, lấy spec đã duyệt làm chuẩn khi xung đột; lệch nhỏ dùng `lech add` rồi tiếp tục. `/goal` chỉ là tùy chọn người dùng chủ động bật, không tự chạy model đánh giá.
- Kiểm thử: full fresh 4.180 passed, 7 skipped, 2.724 subtests; 4.187 case ID, receipt PASS. Chưa đo hiệu quả trên model nhỏ ngoài thực địa; không cứu API/tool treo giữa lượt.

## 0.93.0 — 2026-11-06

Eval cho thay đổi skill/hook/plugin chuyển sang opt-in, chỉ kích hoạt khi người dùng yêu cầu và đồng ý.

- Thêm `tdq_state.py eval-enable --by "<lời người dùng>"` ghi sự đồng ý và thời điểm vào state; trước khi bật, gate `implement`/`report` không chặn. Khi bật, gate vẫn kiểm eval-plan và chứng cứ như cũ.
- Bỏ `eval-waive`; state cũ còn khóa `eval_waiver` vẫn đọc được nhưng khóa này không còn hiệu lực. Đồng bộ luật intake/spec/plan/build/QC và tài liệu đánh giá.
- Kiểm thử: full fresh 4.168 passed, 7 skipped, 2.724 subtests; vùng chạm 2.068 passed, 2 skipped; eval model chưa kích hoạt (opt-in), không có kết luận hiệu quả model.

## 0.92.0 — 2026-11-05

Khắc phục tự động MCP plugin `tdq-workflow` bị đứt trên Claude Desktop sau update.

- Tự đồng bộ `mcpServers` từ `~/.claude.json` vào `.mcp.json` trong cache plugin active khi setup, chạy nền `--nen`, auto-update và setup bù.
- Tự mở quyền cho MCP plugin LSP và Chrome DevTools.
- Hook/Search Gate nhận đúng `mcp__plugin_tdq-workflow_lsp__*`, nhưng từ chối server không thuộc TDQ dù tên chứa `lsp`.
- Kiểm thử: 206 passed, 4 subtests passed, 0 failures; QC ultra độc lập PASS.

## 0.91.0 — 2026-11-05

Chuẩn hóa Report dễ hiểu kèm Archify HTML, cập nhật Soul và tự động ghim vào User-Instruction.

- Phase `report` luôn sinh cặp `docs/tdq/reports/<slug>.md` và `Archify HTML` (`docs/tdq/reports/<slug>.html`) dễ hiểu, trực quan cho mọi độc giả. Khi có cập nhật bắt buộc nêu rõ: Trước request, Sau request, Đã test gì, Kết quả test.
- `soul.md` và `tdq-conventions/SKILL.md` khóa nguyên tắc luôn trình bày đơn giản, dễ hiểu, ngắn gọn nhưng trực quan, đầy đủ thông tin.
- `KHOI_HUONG_DAN` (`scripts/tdq_setup.py`, `docs/claude-md-mau.md`) tự động ghim vào `~/.claude/CLAUDE.md` cả khi cài mới (`tdq_setup.py` & `--nen`) lẫn khi update. Phần riêng của người dùng ngoài `<!-- TDQ:TOOLS -->` được bảo toàn nguyên vẹn.
- Kiểm thử: 94 passed, 170 subtests passed, 0 failures; QC độc lập (`muc_qc=ultra`) PASS.

## 0.90.0 — 2026-11-04

Master kiến trúc Archify: overview, luồng chi tiết và nguồn bằng chứng kiểm chứng được.

- Trang master có 6 trụ cột và 5 thẻ luồng mở sơ đồ con trong modal; hỗ trợ bàn phím, trả focus, không chèn `onclick` vào SVG native.
- Model luồng gắn file/dòng/test, ghi `chưa xác minh` khi thiếu bằng chứng; dự án docs-only không bịa luồng mẫu.
- Freshness kiểm model, candidate, HTML con và source; publish atomic giữ last-good khi lỗi, cảnh báo stale tại cổng report/idle.
- Browser desktop/mobile PASS; hồi quy 4.161 passed, 10 skipped, 0 failures. Eval paid-model AB/BA chưa chạy: `INCONCLUSIVE` theo lệch Q6 đã duyệt.

## 0.89.0 — 2026-11-03

Tự chủ phối hợp công cụ có kiểm chứng, giữ nguyên dữ liệu người dùng khi ghim instruction.

- Luật thường trực có "tool completion loop": xem inventory công cụ thật, lập bước nội bộ, preflight kết nối, thực thi bằng một công cụ nếu đủ, kiểm kết quả thật, handoff theo identity mới; delivery mơ hồ thì quan sát trước khi lặp.
- Thiếu công cụ: tìm nguồn chính thức, đề xuất cài user-level kèm kiểm chứng/gỡ; chờ duyệt trước khi cài. Bỏ luật cũ tự cài dependency LSP trong managed instruction.
- Writer instruction: marker đúng một cặp, UTF-8 strict, giữ byte ngoài block, backup duy nhất, file tạm cùng thư mục, fsync/readback, `os.replace`, rollback báo đường backup, lượt hai no-op không tạo backup.
- Windows ACL so theo semantics: owner/group/control/revision và từng ACE đúng thứ tự; bỏ khác biệt offset/padding. Giữ `SE_DACL_AUTO_INHERITED` bằng request bit chỉ trên bản copy của lời gọi `SetFileSecurityW`; descriptor lỗi bị từ chối trước khi đọc pointer.
- Lỗi writer không tiến version stamp và không báo thành công giả; hook SessionStart hiển thị lỗi đã lọc, không lộ nội dung riêng.
- Evaluator fail-closed: trace rỗng/thiếu terminal không PASS, kiểm UTF-8/schema, gắn corpus/model/A-B snapshot, khóa scorer theo source+bytecode+rubric, thiếu cost thì ghi `unavailable` chứ không ghi 0.
- Hồi quy: 4.126 passed, 12 skipped, 0 failures trên 4.138 ca; 2.669 subtest; Pyright 0 lỗi trên writer và test ACL.

## 0.88.0 — 2026-11-03

Report nghiệm thu trực quan chung cho Express và Deep.

- Express chuyển từ `implement/QC` sang phase `report` đã có, rồi mới sang `idle`; CLI từ chối đóng trực tiếp từ `implement`.
- Cả hai lane dùng chung báo cáo Markdown và HTML Archify độc lập từ task, DoD, QC và kết quả thực tế. Manifest ghi đúng provenance `working-tree`; output thiếu hoặc stale phải báo fallback.
- Giữ duy nhất một cổng duyệt Express, không thêm phase, state key hay renderer. Tăng regression cho state, hook, report và Archify.

## 0.87.0 — 2026-11-03

Tích hợp điều phối Ultracode qua hậu tố lane, bảo toàn độc quyền kiểm soát TDQ và siết chặt an toàn subagent.

- **Hậu tố lane `_ultracode`:** Hỗ trợ `express_ultracode`, `deep_ultracode`, `1a_ultracode` từ input người dùng; bóc tách trước khi ghi nhận state để bảo tồn hai lane canonical `quick` và `full`.
- **Định tuyến Express & Deep có kiểm soát:** Express tự động kích hoạt workflow hữu hạn kèm fallback mini-plan và hạch toán hoàn tất (fail-closed completion accounting) trong 1 cổng duyệt; Deep hỗ trợ khảo sát analyze/QC và review spec/plan song song.
- **Siết chặt quyền hạn subagent (Least Privilege):** Edit/Bash mutation gate chặn subagent sửa mã nguồn hoặc file state trước phase `implement`. Subagent chỉ được ghi báo cáo tại `docs/tdq/artifacts/<request>/<agent-id>.md` hoặc trả structured fallback.
- **Quản lý worktree đơn quyền:** Bác bỏ Workflow native isolation (`isolation: 'worktree'`), toàn bộ nhiệm vụ thực thi phân tán được ủy quyền và kiểm soát va chạm độc quyền qua `tdq_team.py`.
- **Đánh giá và kiểm thử toàn diện:** Bổ sung kiểm thử hợp đồng, định tuyến và bộ rào chắn; full test suite đạt 3.991 test PASS, 5 SKIP, 0 FAIL.

## 0.86.0 — 2026-11-02

Spec Trước/Sau trực quan và subagent nghiên cứu chỉ đọc.

- Spec chuyên sâu và mini-plan nhanh khi sửa thứ đã có dùng một HTML Archify `explainer` gồm sơ đồ hiện tại và sau cập nhật; chữ chỉ mô tả phụ trợ, feature mới ghi rõ chưa có hiện trạng.
- `edit_gate` nhận diện subagent qua `agent_id`, chặn sửa project ngoài `docs/` trước phase `implement`, vẫn cho phép research/log/report và giữ rào `Chạm:` khi triển khai.
- QC/DoD truy về hành vi nghiệp vụ hoặc luồng cũ phải giữ; test đỏ trước, report sinh sẵn thân PR nhưng không tự mở PR.
- Bổ sung regression cho hook, template spec, cả hai pipeline Archify, luật subagent và report; vùng chạm đạt 199 test + 382 subtest, smoke hook thật PASS.

## 0.85.1 — 2026-11-01

Đặt mặc định Ponytail ở mức `ultra`.

- State mới, state thiếu khoá và giá trị không hợp lệ đều dùng `muc_gat=ultra`; fallback của bộ lọc luật đồng bộ cùng mức này.
- Giữ nguyên lựa chọn rõ ràng `lite`, `full`, `ultra`, `off`; không nâng cấp cưỡng bức các project đã chọn mức riêng.
- Mức QC (`muc_qc`) vẫn mặc định `full`, độc lập với mức gắt Ponytail.
- Đồng bộ bảng cường độ và regression cho default/fallback, CLI và khả năng chọn mức khác.

## 0.85.0 — 2026-11-01

Tối ưu calibration, quản lý tiến trình Codex và báo cáo test; giữ mặc định bảo thủ.

- **Calibration từ chối input sai trước vòng đo**, không tạo output mới; giữ nguồn mẫu hợp lệ.
- **Codex dùng process ownership chung**, dọn đúng descendants/HOME và giữ deadline riêng cho từng probe.
- **Giảm công việc test lặp:** 11 ca kiểm thuần không gọi subprocess/calibration/Git; integration thực vẫn được giữ.
- **Top20 case/module và export offline JSON/Markdown/HTML**, cộng execution phases đúng, không đếm subtest hai lần, giữ verdict và provenance của result gốc.
- **Củng cố runner và timing:** lưu structured outcomes, kiểm inventory/receipt, giữ lỗi gốc, phân biệt wall/API/tool time và phần chưa đo được.
- **Kiểm chứng nguồn trước bump:** Full 3.657 PASS, 8 SKIP; giữ 3.602 case baseline, thêm 63 case; QC 12/12 và browser desktop/mobile đạt. Timeout2s dọn trong 2,72s ở fixture Windows.
- **Giới hạn:** D9/D10 `SKIPPED_USER`; chưa có A/B để kết luận % tăng tốc. Giữ worker1, cache/reuse off; chưa chứng nhận POSIX từ lượt Windows này.

## 0.84.2 — 2026-10-26

Giảm Timeout Và Thời Gian Chờ agent-lsp (Mạch Ngắt Circuit Breaker & Idle Timeout 90s).

- **Thiết lập giới hạn chờ Idle Timeout 90s (`scripts/tdq_setup.py`).** Tự động cấu hình `CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT = "90000"` trong `~/.claude/settings.json`, cắt đứt hoàn toàn nguy cơ client bị treo 1.800 giây khi server LSP kẹt socket hoặc semaphore worker pool.
- **Cổng kiểm soát phạm vi và mạch ngắt Circuit Breaker (`hooks/scripts/lsp_gate.py`, `hooks/hooks.json`).** Chặn có điều kiện lệnh gọi `blast_radius` khi `changed_files` > 3 tệp, `scope != "exported"`, hoặc `include_transitive=true`. Tự động ngắt mạch (trạng thái MỞ) khi lần gọi `blast_radius` gần nhất thất bại hoặc có ≥2 lỗi LSP liên tiếp, điều hướng an toàn sang `find_references` hoặc `Grep` + `Graphify`.
- **Quan sát thời gian chạy và phân loại kết quả LSP (`hooks/scripts/search_observe.py`).** Đăng ký hook `PostToolUseFailure`, đo lường chính xác `duration_ms` và gán nhãn 4 trạng thái `outcome` (`ok`, `empty`, `error`, `timeout`), bảo toàn hợp đồng mở khóa `khai_niem` ở `PreToolUse`.
- **Thống kê phân vị độ trễ và đối chiếu Caller Oracle (`scripts/search_rules.py`, `scripts/search_replay.py`).** Cung cấp các hàm thuần tính toán p50/p95, max_ms và đối chiếu độ phủ caller oracle (`recall`, `precision`); CLI `--lsp-telemetry` xuất báo cáo telemetry LSP trực tiếp từ transcript JSONL hoặc file sổ.

## 0.84.1 — 2026-10-26

Sửa nạp luật SessionStart khi workspace chưa mở request.

- **Giảm context khi chưa có request (`hooks/scripts/session_start.py`).** Chỉ chèn toàn bộ thân luật `[TDQ:GON]` trong phase `implement`; workspace mới hoặc idle chỉ nhận một dòng trỏ tới luật.
- **Kiểm thử hồi quy.** Bổ sung kiểm tra workspace không có `active_request` và workspace chưa có `state.json`; giữ nguyên nạp luật khi implement và cơ chế chống nhắc trùng.

## 0.84.0 — 2026-10-25

Tối Ưu Độ Trễ (Latency) Test Runner, Chạy Test Song Song Đa Nhân & Fallback Windows Elevated Cho Archify.
Kế hoạch: `docs/tdq/plan/2026-10-25-2225-tat-remember-toi-uu-latency.md`.

- **Phân Tầng Test Runner Vùng Chạm (`scripts/tdq_test.py`).** Trong phase `implement`, lệnh `vung-cham` chỉ chạy các test modules trong phạm vi ảnh hưởng trực tiếp (`chosen`), không tự động leo thang 100% trọn bộ suite trừ khi có cờ `--ep-tron-bo`. Giảm thời gian chờ test từ 638s xuống còn 65s (~90%).
- **Kiểm Thử Song Song Đa Nhân (`pytest-xdist`).** Tích hợp cờ `--parallel` tự động phân phối test trên toàn bộ CPU workers (`pytest -n auto -p no:tmpdir`), triệt tiêu lỗi phân quyền symlink temp trên Windows và chạy toàn bộ unit tests trong vài giây.
- **Fallback Nghiệm Thu Archify Khi Chạy Quyền Windows Elevated (`scripts/archify_delivery.py`).** Tự động thiết lập `ARCHIFY_CHROME_NO_SANDBOX=1` khi tiến trình chạy dưới quyền Administrator để tránh đứt anonymous pipes. Nghiệm thu an toàn cổng `browser-check` khi các cổng nghiệm thu tĩnh và chữ ký artifact HTML đã xác thực thành công trên đĩa.

## 0.83.0 — 2026-10-25

Tự Động Cập Nhật (Auto-Update) Plugin TDQ-Workflow Trong Claude Code & Chống Hạ Cấp Phiên Bản.
Kế hoạch: `docs/tdq/plan/2026-10-25-2025-auto-update-plugin.md`.

- **Cơ chế Tự động Cập nhật Đa Tầng (`scripts/tdq_setup.py`, `hooks/scripts/session_start.py`).** Tự động phát hiện phiên bản mới từ đa nguồn (`cwd` dự án nguồn, `marketplaces/tdq-local`, `GOC_PLUGIN`, `GOC_REPO`). Tiến hành cập nhật bản cài user-scope `tdq-workflow@tdq-local`.
- **Kiểm tra Cập nhật Ngầm Tách Biệt & Điều Tiết (Throttle).** Khởi chạy tiến trình kiểm tra cập nhật remote GitHub ngầm tách biệt hoàn toàn không chặn phiên làm việc. Tự động điều tiết tần suất kiểm tra định kỳ 2 giờ qua mốc thời gian.
- **Bộ Chốt Chặn Chống Hạ Cấp Phiên Bản (Anti-Downgrade Safeguard).** So sánh phiên bản dạng số học ngữ nghĩa `(major, minor, patch)`. Ngăn chặn việc ghi đè mốc phiên bản hoặc cập nhật ngược từ các cache cũ.

## 0.82.0 — 2026-10-25

Tích Hợp Trực Quan Hóa Kiến Trúc Archify 2 Tầng, Chrome DevTools MCP & Xuất Bản Master Map Flagship.
Kế hoạch: `docs/tdq/plan/2026-10-25-1648-mastermap-va-readme-pro.md`.

- **Kiến trúc Trực quan Archify 2 Tầng (`tdq_archify.py`, `archify_delivery.py`, `archify_model.py`, `archify_artifacts.py`).** Tầng 1 sinh bản đồ nghiệp vụ tương tác (`preview.html`) và khóa chữ ký SHA-256 vào Spec/Plan. Tầng 2 xuất bản **Master Map** (`docs/architecture/index.html`) và kiểm tra độ tươi qua `tdq_finish.py`.
- **Tích hợp Chrome DevTools MCP & Kiểm thử UI 5 Lớp (`tdq_devtool_mcp.py`, `tdq-browser-test`, `tdq-browser-research`).** Bổ sung hai kỹ năng kiểm định giao diện E2E 5 lớp. Hỗ trợ thu thập dữ liệu SPA với cơ chế chờ thích ứng.
- **Xuất bản Master Map 4 Góc Nhìn & Thiết kế lại `README.md` chuẩn Flagship.** Chuẩn hóa 4 mô hình kiến trúc với nhãn chú giải đúng miền nghiệp vụ TDQ-Workflow. Nâng cấp `README.md` kèm hướng dẫn cài đặt từ A–Z và xử lý 10 lỗi kiểm thử nền tảng.

## 0.81.0 — 2026-10-20

Xác Thực Thực Nghiệm Khảo Sát 3 Chiều Trên Codebase Thực Tế & Hoàn Thiện Quy Trình Refactor.

- **Thực nghiệm đo đạc độ bao phủ trên Codebase lớn (`claudecodeui`).** Chứng minh Tam Giác Khảo Sát 3 Chiều tăng độ bao phủ mã nguồn lên +102% so với chỉ dùng text grep truyền thống. Phát hiện trọn vẹn 41 callers ngầm và 3 modules liên đới.
- **Chứng minh hiệu quả gỡ rào cản Search Gate.** Cổng nhận diện chính xác phase khảo sát, cho phép 100% lệnh quét diện rộng tự do. Kỷ luật nghiêm ngặt trong phase implement vẫn được bảo toàn nguyên vẹn.
- **Bảo toàn chuẩn mực kiến trúc sạch.** Xác thực ngoại lệ Rung 1 loại bỏ hoàn toàn hiện tượng ép phẳng layer, bảo vệ thiết kế phân lớp khi tái cấu trúc.

## 0.80.0 — 2026-10-20

Nâng Cấp Khảo Sát Code 3 Chiều & Bảo Toàn Chủ Đích Refactor Kiến Trúc.
Kế hoạch: `docs/tdq/plan/2026-10-20-1355-nang-cap-khao-sat-3-chieu-refactor.md`.

- **Mở khóa Grep tự do trong Phase Khảo sát (`search_gate.py`, `search_rules.py`).** Không giới hạn quota và không deny tool Grep trong các phase `analyze`, `quick_analyze` và `spec`. Duy trì nghiêm ngặt kỷ luật cổng 3 tầng khi bước vào phase `implement`.
- **Tam Giác Khảo Sát 3 Chiều (`SKILL.md`, `analyze-full.md`, `quick-lane.md`).** Chuẩn hóa quy trình: Grep quét rộng gom candidate files, LSP đào sâu cấu trúc symbol ngầm, Graphify quét vỡ lan hiệu ứng domino. Bắt buộc lập bảng đối chiếu vùng chạm trong brief.
- **Ngoại lệ Refactor & Clean Architecture cho Rung 1 (`chung.md`).** Khi người dùng yêu cầu Refactor hoặc SOLID, cấu trúc sạch và tính mở rộng module đứng trên luật phẫu thuật 1 dòng tối thiểu. Nghiêm cấm tự ý ép gộp các layer/adapter thành hàm phẳng.
- **Khối so sánh Trước vs Sau & Đồng bộ Toàn cục (`spec-template.md`, `plan-template.md`, `CLAUDE.md`).** Chuẩn hóa bảng so sánh Trước vs Sau cho spec/plan. Đồng bộ quy tắc vào instruction toàn cục.

## 0.79.0 — 2026-10-20

Triệt Tiêu Hoàn Toàn Hiện Tượng Cửa Sổ Command Console Chớp Nháy Trên Windows.
Kế hoạch: `docs/tdq/plan/2026-10-20-1230-fix-chop-nhay-console-windows.md`.

- **Bao bọc cờ CREATE_NO_WINDOW toàn diện (`tdq_ten_lenh.py`).** Tự động gắn cờ `0x08000000` cho mọi lệnh `subprocess.run` và `subprocess.Popen` trên Windows, ngăn chặn Windows kernel cấp phát console window.
- **Tiến trình chạy nền & Hook (`session_start.py`, `codex_edit_gate.py`).** Khởi chạy `tdq_setup.py --nen` và hook con hoàn toàn vô hình, không làm chớp nháy màn hình khi mở phiên hoặc duyệt code.
- **Các lệnh Git nội bộ & NTFS Junctions (`tdq_team.py`, `tdq_state.py`, `tdq_test.py`).** Đồng bộ 100% cuộc gọi git status, rev-parse, merge-tree và mklink qua cờ ẩn cửa sổ.

## 0.78.0 — 2026-10-20

Quyền Tự Quyết Cổng LSP, Tự Cài Dependency & Bảo Toàn Quy Tắc Qua Compaction.
Kế hoạch: `docs/tdq/plan/2026-10-20-1200-tu-quyet-lsp-gate.md`.

- **Toàn quyền tự quyết cổng LSP (`tdq-intake`, `tdq_state.py`).** Tự động áp dụng `--bo-qua-lsp` cho tài liệu, nghiên cứu, dọn dẹp và cài đặt MCP. Với dự án lập trình, Agent tự phân tích kịch bản và tự quyết định bỏ qua an toàn nếu tham chiếu nội tệp.
- **Tự động tìm kiếm & cài đặt dependency LSP (`uu-tien-tim-kiem.md`).** Khi thiếu Language Server, Agent có quyền tự động tìm kiếm và cài đặt (`npm`, `uv`, `pipx`, `brew`). Hoàn tất môi trường cho task mà không cần hỏi người dùng.
- **Cơ chế bảo toàn qua Compaction (`session_start.py`).** Tiêm nguyên tắc `LSP-Autonomy` vào khối neo phục hồi `[TDQ:ANCHOR]`. Đảm bảo Agent không bị mất ngữ cảnh tự quyết sau khi nén phiên.

## 0.77.0 — 2026-10-20

Tự Động Mang Theo & Hợp Nhất File Docs và Graphify Khi Đổi Nhánh (Auto-Carry Zone).
Kế hoạch: `docs/tdq/plan/2026-10-20-1145-auto-carry-docs-graphify.md`.

- **Mở rộng Vùng Tự Động Mang Theo (`tdq-intake`, `nhanh-request.md`).** Cho phép tự động chuyển nhánh khi working tree dirty thuộc `docs/**`, `*.md`, `logs/**`, `*.log`, `graphify-out/**`. Không dừng lại hỏi người dùng nếu không có dirty ở mã nguồn.
- **Tự động Commit & Merge khi Kết thúc Request (`report-template.md`).** Các thay đổi dirty ở tài liệu và đồ thị graphify được tự động add/commit hoặc merge về nhánh gốc. Tránh việc git switch bị chặn và triệt tiêu các hộp thoại xác nhận lặp lại.
- **Đồng bộ Quy Tắc Toàn Cục (`scripts/tdq_setup.py`, `CLAUDE.md`).** Bổ sung điều luật auto-carry zone vào `KHOI_HUONG_DAN` ghim tự động vào `CLAUDE.md` giúp toàn bộ phiên làm việc tuân thủ nhất quán.

## 0.76.0 — 2026-10-20

Ưu tiên MCP & Kỹ năng MCP Toàn Cục, Pre-flight Check, Auto-Setup Incremental & Auto-Update Plugin.
Kế hoạch: `docs/tdq/plan/2026-10-20-1115-uu-tien-mcp-auto-setup.md`.

- **Nguyên tắc Toàn cục MCP-First (`scripts/tdq_setup.py`, `CLAUDE.md`).** Bổ sung điều luật bắt buộc trong `KHOI_HUONG_DAN`. Luôn ưu tiên dùng MCP và bộ kỹ năng MCP trong spec, plan và thực thi cho môi trường chuyên biệt (Roblox, Unity, Chrome DevTools, DB, Docker).
- **Khối Neo Phục Hồi sau Nén (`session_start.py`).** Tiêm nguyên tắc `MCP-First` vào khối `[TDQ:ANCHOR]` khi phiên làm việc bị nén (`compact`) hoặc phục hồi (`resume`), chống tình trạng Agent quên công cụ.
- **Cẩm nang Pre-flight Connection Check (`mcp-first-guide.md`).** Chuẩn hóa kịch bản kiểm tra kết nối (cổng 9222 Chrome CDP, socket Unity, bridge Roblox Studio). Bổ sung câu thông báo hướng dẫn người dùng bật server khi chưa mở.
- **Tự động Setup Bù khi Đổi Version (`tdq_setup.py`).** Nâng cấp `tu_dong_cap_nhat_khi_doi_phien_ban` và `thuc_hien_setup_bu`: Tự động so sánh phiên bản cũ/mới, cài bù shim, ghim instruction, đồng bộ cấu hình Codex và kiểm thử hook dry-run.
- **Hook SessionStart Tự động Cập nhật Plugin (`session_start.py`).** Tự động phát hiện bản cài plugin scope user cũ hơn mã nguồn repository. Kích hoạt cập nhật CLI hoặc đồng bộ cache trực tiếp không cần thao tác thủ công.

## 0.75.0 — 2026-10-20

Nâng cấp Graphify Full Extraction, Wiki Provenance & Cấu hình Custom Provider An toàn.
Kế hoạch: `docs/tdq/plan/2026-10-20-0032-graphify-full-wiki-search.md`.

- **Cấu hình Custom Provider an toàn & Degraded Runner (`tdq_graphify.py`, `docs/tdq/config.json`).** Bổ sung cấu hình `GRAPHIFY_CUSTOM_PROVIDER` (`enabled`, `endpoint`, `model`, `api_key_env`). API key chỉ đọc từ biến môi trường, tuyệt đối không lưu secret trong repo/config/manifest/log. Tự động kích hoạt chế độ `code-only degraded` kèm hướng dẫn chi tiết khi chưa cấu hình hoặc thiếu API key, đảm bảo không ngắt quãng workflow. Khi cấu hình hợp lệ nhưng lệnh extraction/wiki thất bại, hệ thống fail-closed và cảnh báo sử dụng LSP + grep.
- **Quy trình Full Extraction Transaction & Wiki Provenance.** Hợp nhất toàn bộ luồng full extract và export wiki vào một transaction kiểm soát tính tươi mới (freshness). Xác thực tính toàn vẹn dựa trên mã băm nội dung mã nguồn, tài liệu, ignore file, provider endpoint/model và sự hiện diện của wiki (`graphify-out/wiki/index.md`). Loại trừ output wiki khỏi đầu vào để triệt tiêu nguy cơ self-ingest.
- **Tích hợp Tự khởi tạo & Bậc 7 Kiểm tra Tìm kiếm.** Đồng bộ `tdq_setup.py` và `tdq_lsp.py` nhận diện trạng thái full fresh vs degraded, bảo vệ bộ tìm kiếm 3 tầng không dùng đồ thị/wiki cũ khi chưa đồng bộ.
- **Benchmark A/B 3 Biến thể & Phán quyết Giữ nguyên Selector 3 Tầng.** Khảo sát thực nghiệm đo lường 3 cấu hình (code-only, full, full+wiki) trên TDQ-Workflow và Photoboth360. Dữ liệu chứng minh Graphify hỗ trợ tốt bản đồ cấu trúc macro và community wiki nhưng ngữ cảnh BFS từ CLI chưa vượt trội so với LSP/grep, quyết định giữ vững thứ tự tìm kiếm 3 tầng chuẩn.

## 0.74.0 — 2026-10-19

Tích hợp Chrome DevTools MCP tự động hóa & Bộ đôi kỹ năng Trình duyệt Chuyên sâu.
Kế hoạch: `docs/tdq/plan/2026-10-18-1630-feasibility-enable-devtoolmcp.md`.

- **Cấu hình & Tự động hóa Chrome DevTools MCP (`tdq_devtool_mcp.py`).** Bổ sung cờ cấu hình `ENABLE_DEVTOOL_MCP` trong `.claude-plugin/plugin.json`. Hỗ trợ kiểm tra phi chặn (< 30ms) tại `session_start.py` và auto-setup zero-prompt `~/.claude.json`. Cấp quyền wildcard `mcp__chrome-devtools__*` trong `settings.json` và tạo profile cách ly `~/ChromeDevProfile`. Tự động khởi chạy Chrome ở chế độ nền khi CDP port 9222 chưa mở.
- **Kỹ năng Kiểm thử Trình duyệt Phân vùng 5 lớp (`tdq-browser-test`).** Ra mắt skill kiểm thử E2E UI/UX theo quy trình 5 lớp. Bao gồm: Visual Layout, Interactive Elements, Responsive Breakpoints, Console/Network Errors, Accessibility/Contrast. Chống kiểm thử sơ sài, đảm bảo web mượt mà và không lỗi ẩn.
- **Kỹ năng Cào Dữ liệu & Nghiên cứu Web Phòng thủ (`tdq-browser-research`).** Ra mắt skill trích xuất dữ liệu và Deep Research web chuyên sâu. Trang bị cơ chế Adaptive Polling và Exponential Backoff Timeout. Tự động phục hồi khi trang tải chậm hoặc SPA rendering phức tạp.
- **Tài liệu Hướng dẫn & Tích hợp Setup.** Bổ sung cẩm nang `chrome-devtools-mcp-guide.md` tại `skills/tdq-setup/references/`. Tích hợp kiểm tra tự động vào quy trình `tdq_setup.py`.

## 0.73.1 — 2026-10-18

Bảo tồn tinh túy kiến trúc TDQ Workflow & Xác thực Đa nền tảng Cross-Platform.
Kế hoạch: `docs/tdq/plan/2026-10-18-0056-kiem-thu-cross-platform.md`.

- **Xác thực Đa nền tảng Thực tế (Cross-Platform Verification).** Kiểm thử trực tiếp qua SSH trên cả 3 môi trường phân tán: Windows 11 Host, macOS Sequoia Apple Silicon (ARM64) và Linux Ubuntu (x86_64). Đồng bộ mã nguồn, cache plugin, chạy 100% xanh bộ test suite cốt lõi (0.07s trên macOS, 0.18s trên Linux) và khởi tạo dự án mẫu thành công.
- **Bản thiết kế Bất biến & 6 Trụ cột Tinh túy (`tinh-tuy-tdq-workflow.md`).** Chuẩn hóa văn bản kiến trúc bảo tồn vĩnh viễn các giá trị cốt lõi. Tài liệu bao gồm: Hiệu năng thực thi (Stop-Batching, NTFS Junctions), Kỷ luật ngữ cảnh (Strategic Compaction, Digest <= 1.500 chars), An toàn song song (TCAS AST Collision). Đồng thời quy định: Học tập có kiểm duyệt (Governed Harvest), Clean Code Invariants & Soul, và Đội ngũ 6 Subagents phân nhiệm theo Least Privilege.

## 0.73.0 — 2026-10-18

Nâng cấp toàn diện TDQ Workflow từ Master Blueprint chắt lọc tinh hoa Everything Claude Code (ECC).
Kế hoạch: `docs/tdq/plan/2026-10-18-0009-nang-cap-toan-dien-tdq-workflow.md`.

- **Stop-Batching Architecture (Tầng 2 Hook).** Chuyển đổi kiểm tra cú pháp và doc_lint sang ghi đệm buffer tạm (`stop_batch_checker.py`). Cơ chế chỉ chạy gộp một lần tại sự kiện `Stop`, giảm 99.6% độ trễ trên Windows 11 (0.26 ms vs 70.6 ms).
- **Strategic Compaction Gate (Tầng 2 Hook).** Tích hợp bộ đếm trọng số tiêu thụ ngữ cảnh (`strategic_compact_gate.py`). Cảnh báo nén phát ra tại ranh giới tự nhiên (`spec_approved`, `plan_approved`, `wave_transition`), không đứt gãy mạch TDD.
- **Document Placement Gate (Tầng 2 Hook).** Cưỡng chế kỷ luật không gian lưu trữ (`doc_file_gate.py`), chặn đứng tình trạng agent tự ý xả các tệp Markdown rác ngoài các thư mục quy định (`docs/tdq/`, `docs/workinglog/`, `skills/`, `agents/`, `tests/`).
- **TCAS AST Import Collision Avoidance (Tầng 3 CLI).** Nâng cấp `tdq_team.py` bóc tách quan hệ import tĩnh bằng `ast.parse` (`detect_tcas_collision`). Tự động phân tách wave cho các task phụ thuộc ngầm nhằm triệt tiêu xung đột ngữ nghĩa.
- **NTFS Directory Junction Sharing (Tầng 3 CLI).** Tự động chia sẻ `node_modules` và `.venv` từ repo gốc vào worktree qua `mklink /J` trên Windows 11, rút ngắn thời gian cấp phát worktree từ 120s xuống dưới 10 mili-giây.
- **Governed Continuous Learning CLI (Tầng 3 CLI).** Ra mắt `scripts/tdq_harvest.py` với vùng cách ly `docs/tdq/knowledge/candidates/` và quy trình kiểm duyệt CLI thủ công ngăn ngừa 100% rủi ro Memory Poisoning.
- **Đội Ngũ 6 Subagents Tinh Hoa & Clean Code Invariants (Tầng 1 Luật).** Chuẩn hóa JSON Schema `TDQ_HANDOFF_PAYLOAD` (< 200 tokens). Bổ sung 3 subagent mới (`tdq-security-reviewer`, `tdq-build-resolver`, `tdq-refactor-cleaner`). Tích hợp luật đối kháng `Adversarial Skeptic` (Fail-Closed >= 0.80) và Clean Code Invariants vào `soul.md`.

## 0.72.0 — 2026-10-17

Nâng cấp toàn diện hệ thống TDQ Workflow từ nghiên cứu kiến trúc và giải thuật ECC v2.2.3.
Kế hoạch: `docs/tdq/plan/2026-10-17-1741-nang-cap-tdq-toan-dien.md`.

- **Windows Parity & UTF-8 Stdio.** Mở rộng matcher `Bash|PowerShell` trong `hooks/hooks.json` cho `PreToolUse` (bash_gate) và `PostToolUse` (search_observe). Nâng cấp `utf8_io.py` ép UTF-8 cho cả `sys.stdin` an toàn trên Windows locale cp1252. Bao bọc quote-path chống lỗi khoảng trắng thư mục trên launcher Antigravity. Tách lọc wrapper `<TDQ_WORKFLOW>` từ OpenCode ngăn kích hoạt nhầm duyệt.
- **Protocol đo lường Dispatcher (O08) & Phán quyết NO-GO.** Thiết lập protocol đo lường paired runs baseline vs candidate trên Windows host. Thực nghiệm 10 runs đạt speedup 48.67% nhưng vi phạm tương đương ngữ nghĩa (equivalence FAIL); đưa ra phán quyết NO-GO chính xác, bảo toàn trọn vẹn kiến trúc hook riêng rẽ hiện hành (`bash_gate.py` và `search_gate.py`).
- **Hợp đồng kiểm duyệt nghiêm ngặt (Strict Provenance).** Chuẩn hóa cơ chế phê duyệt: cấm suy luận approval từ text phi nhân tạo, notification hay trích dẫn; kích hoạt re-approval khi scope hoặc plan bị thay đổi ngữ nghĩa.
- **Phân định kết quả QC (Anti-False Clean PASS).** Bổ sung `ANTI-6` trong `qc.md` và `test_plan_tick.py`, nghiêm cấm coi timeout, crash, missing hay unknown/unverified là clean PASS.
- **Bộ phân tích ngân sách 4 chiều.** Nâng cấp `search_rules.py` với ngân sách 4 chiều (`input_chars`, `work_units`, `nesting`, `output_items`), chặn an toàn lệnh malformed/unknown không cấp credit khái niệm.
- **Tối thiểu hóa dữ liệu & Logging ISO chuẩn hóa.** Chuẩn hóa ISO timestamp trên stderr, hỗ trợ tắt sạch qua `TDQ_LOG=0`. Giảm thiểu dữ liệu mang vác trong turn ledger và context hook.
- **Khung đánh giá Offline & Knowledge Contract.** Xây dựng bộ công cụ eval hoàn toàn offline (`tdq_eval.py`, `evals/tdq-upgrade-offline.json`) và hợp đồng quản lý tri thức (`tdq_knowledge.py`).

## 0.71.0 — 2026-10-16

Áp dụng nâng cấp triết lý và kiến trúc Andrej Karpathy vào TDQ Workflow.
Kế hoạch: `docs/tdq/plan/2026-10-16-1410-nang-cap-triet-ly-karpathy.md`.

- **Kỷ luật phẫu thuật cấp dòng (Surgical Changes).** Bổ sung quy tắc vào `chung.md` cấm drive-by refactor, cấm sửa comment hay quote style lân cận. Mọi dòng thêm mới hoặc chỉnh sửa trong git diff phải truy vết trực tiếp về yêu cầu.
- **Quy tắc dọn rác của chính mình.** Tinh chỉnh Intentionality trong `chung.md`: chỉ dọn dẹp biến, hàm và import mồ côi do chính thay đổi của mình tạo ra. Dead code có sẵn từ trước chỉ nêu trong báo cáo, cấm tự ý xóa.
- **Luật YAGNI đứng trên SOLID.** Bổ sung vào `clean-code.md`: cấm tạo Interface, Abstract Class hay Strategy Pattern cho code chỉ dùng 1 lần. Một use case chỉ viết một hàm phẳng duy nhất; chỉ trừu tượng hóa khi có ca thứ hai.
- **Tư duy phản biện (Think Before Coding).** Bổ sung vào `interview.md`: chủ động phản biện giải pháp quá phức tạp và đề xuất phương án đơn giản hơn kèm ước lượng công sức thay vì thụ động làm theo.
- **Tâm thức Karpathy cho Subagents.** Bổ sung vào `agents/tdq-implementer.md` 4 nguyên lý Karpathy và vòng lặp hướng mục tiêu `[Step] -> verify: [Test]`.
- **Tối ưu hóa bộ lọc thân luật.** Cập nhật `hooks/scripts/luat_gon.py`: ở mức `full` lọc bỏ 56 dòng ví dụ dài, giảm ~500 tokens mang vác cho mỗi lượt gọi tool trong phase `implement` và mỗi khi gọi `SubagentStart`.
- **JIT Micro-rules phẫu thuật.** Cập nhật `hooks/scripts/edit_gate.py` nhắc nhở `surgical edits only, no single-use abstraction` dưới trần 200 ký tự khi sửa code lần đầu.

## 0.70.0 — 2026-10-15

Tối ưu hóa toàn diện instruction và kiến trúc Lazy Loading ngữ cảnh cho model tier thấp.
Kế hoạch: `docs/tdq/plan/2026-10-15-1425-cap-nhat-full-de-xuat-instruction.md`.

- **Bộ mã cấm tường minh (`ANTI-1` .. `ANTI-6`).** Tích hợp chuẩn hóa bộ 6 mã cấm cơ học (Fake Red, Blind Assertion, Dirty State Git, Late Tick, Raw Dump, Broad Area) vào các tài liệu hướng dẫn và agent. Giúp các mô hình nhỏ tránh lỗi cú pháp, assertion rỗng và vi phạm checklist.
- **Thư viện Cookbooks thực chiến (Tầng 3).** Xây dựng thư viện Cookbooks tại `skills/tdq-build/references/rules/cookbooks/` với các giải pháp thực chiến cho Python và TypeScript/JS (async concurrency, database transaction context manager, domain error handling, clean architecture dependency injection, structured ISO logging).
- **JIT Micro-injection & Neo Phục Hồi sau Compaction.** Hook `edit_gate.py` tự động mớm 3 dòng quy tắc vàng khi sửa code lần đầu; hook `session_start.py` trang bị Khối Neo Phục Hồi `[TDQ:ANCHOR]` ngắn gọn (< 200 tokens) trỏ lại state, plan và mã cấm khi phiên bị nén (compaction); hook `prompt_context.py` tự mớm DoD checklist khi vào phase `qc`.
- **Chế độ Silent CLI trong `tdq_test.py`.** Hỗ trợ cờ `--silent` ghi log chi tiết ra `docs/tdq/.tdq-test.log`, terminal chỉ in `≤ 2` dòng tóm tắt và lỗi chính, bảo vệ context window khỏi rác log kiểm thử.
- **Bảo toàn hàng rào Codex.** Tinh chỉnh `_la_repo_plugin` trong `scripts/tdq_codex_mcp.py` bảo đảm `.codex/hooks.json` của repo TDQ Workflow luôn giữ đúng hàng rào 2 cổng viết tay.

## 0.69.0 — 2026-10-15

Khắc phục lỗi CLI `tdq_team clean <task>`, tự động phát hiện ngôn ngữ dự án trong search gate và ghim hướng dẫn 3 bước LSP.
Kế hoạch: `docs/tdq/plan/2026-10-15-0958-dieu-tra-loi-lsp-search-team-clean.md`.

- **Hỗ trợ tham số cho lệnh clean.** `scripts/tdq_team.py clean [task]` hỗ trợ tham số task tùy chọn; báo `already cleaned` và thoát `0` nếu task đã được dọn bởi `merge`, tránh văng lỗi CLI cú pháp `exit 2`.
- **Phát hiện ngôn ngữ tự động trong search gate.** `hooks/scripts/search_gate.py` và `scripts/search_rules.py` tự động phát hiện ngôn ngữ dự án (`typescript`, `python`, `go`, `rust`...). Câu thông báo in đúng `language_id` thực tế thay vì gán cứng `e.g. python`, đồng thời tự gợi ý `mcp__lsp__list_symbols` khi grep trong file cụ thể.
- **Hướng dẫn cơ học 3 bước khởi tạo LSP.** `KHOI_HUONG_DAN` trong `scripts/tdq_setup.py`, `CLAUDE.md` và tài liệu tìm kiếm nêu rõ quy trình: gọi `start_lsp` đầu phiên kèm `language_id`. Đối với TypeScript/JS cần mở file bằng `open_document` để tránh bẫy "No Project" trước khi tra cứu symbol.

## 0.68.0 — 2026-10-15

Tách 2 nhánh `dev` (phát triển) và `main` (release sạch), tích hợp khung mindset kiểm thử thực tế và Vision Test Loop.
Kế hoạch: `docs/tdq/plan/2026-10-14-1713-tach-nhanh-dev-main-release.md`.

- **Mô hình 2 nhánh `dev` và `main`.** Nhánh `dev` là nhánh phát triển chính lưu giữ đầy đủ mã nguồn, tài liệu, test và công cụ nội bộ; nhánh `main` là nhánh phát hành gọn sạch (~135 files, giảm 90.8% số file và 93.5% dung lượng).
- **Lệnh phát hành Git plumbing.** Mở rộng `scripts/build_portable.py` với cờ `--sinh-main [--nguon] [--nhanh-dich] [--dry-run]` tự động tạo commit snapshot release độc lập trên `main` qua Git plumbing (`commit-tree` trên `GIT_INDEX_FILE` tạm), tránh xung đột merge `modify/delete` và không làm bẩn working tree hiện tại.
- **Tự động nhận diện nhánh gốc.** `scripts/tdq_test.py` tự động nhận diện nhánh `dev` làm `nhanh_goc` mặc định khi tồn tại trong repo để tính vùng chạm chính xác.
- **Vision Test Loop & Mindset kiểm thử thực tế.** Công cụ `scripts/tdq_vision_diff.py` và hướng dẫn `skills/tdq-build/references/vision-test-loop.md` hỗ trợ đối chiếu giao diện hình ảnh, Canvas Padding, Masking, Bounding Box đánh số, xuất báo cáo `.md`/`.html` và tích hợp Figma.

## 0.67.0 — 2026-10-14

Bổ sung chế độ kích hoạt nhanh `_tdq_direct` tự động phân tích mã nguồn và chỉ có 1 cổng duyệt mini-plan.
Kế hoạch: `docs/tdq/plan/2026-10-14-1022-che-do-tdq-direct.md`.

- **Nhận diện `_tdq_direct` trong prompt.** Hook `prompt_context.py` nhận diện từ khóa `_tdq_direct` (không phân biệt hoa thường) khi chưa có request mở hoặc phase idle, phát tín hiệu `[TDQ:INTAKE]` chạy thẳng chế độ direct.
- **Tự động hóa luồng tiếp nhận.** Skill `tdq-intake` và `quick-lane.md` bỏ qua hỏi chọn pipeline & phỏng vấn, tự động `init <slug> quick`, mở git branch và chuyển thẳng Part C; chạy tìm kiếm 3 tầng (LSP, graphify, grep), lập mini-plan ≤ 40 dòng trong `docs/tdq/plan/<slug>.md`, chỉ dừng đúng 1 cổng duyệt `quick_approved` rồi implement.
- **Đồng bộ khối ghim instruction.** Bổ sung nguyên tắc `_tdq_direct` vào `KHOI_HUONG_DAN` của `tdq_setup.py` và mẫu `docs/claude-md-mau.md`.

## 0.66.0 — 2026-10-11

Khắc phục lỗi Unknown skill tdq-intake do thiếu namespace plugin `tdq-workflow:`.
Kế hoạch: `docs/tdq/plan/2026-10-11-1539-fix-plugin-skill-namespace.md`.

- **Namespace đầy đủ cho skill.** Hướng dẫn trong `KHOI_HUONG_DAN`, `~/.claude/CLAUDE.md` và tài liệu ghi rõ `tdq-workflow:tdq-intake`. Giữ dự phòng `(hoặc tdq-intake nếu cài cục bộ)`.
- **Chuẩn hóa hook prompt_context.** Dòng nhắc `[TDQ:INTAKE]` dùng `tdq-workflow:tdq-intake`, đảm bảo độ dài không vượt trần test.

## 0.65.0 — 2026-10-11

Cấm attribution trailer `Co-Authored-By`, chuẩn hóa đường dẫn script plugin trong toàn bộ skills.
Kế hoạch: `docs/tdq/plan/2026-10-11-1346-cam-co-author-fix-path-script.md`.

- **Cấm Co-Authored-By.** Thêm điều luật vào `KHOI_HUONG_DAN` của `tdq_setup.py`; đồng bộ `~/.claude/CLAUDE.md`, conventions và mẫu report.
- **Chuẩn hóa đường dẫn script.** Các lệnh nội bộ trong `skills/` dùng `${CLAUDE_PLUGIN_ROOT}` để chạy đúng khi working directory là project khác.

## 0.64.0 — 2026-10-11

Siết chặt cổng duyệt: yêu cầu lệnh chính thức hoặc đủ động từ + tân ngữ, gỡ bỏ duyệt tự nhiên trần.
Kế hoạch: `docs/tdq/plan/2026-10-11-1327-siet-chat-cong-duyet-lenh.md`.

- **Siết cổng duyệt.** Xóa `ACTION_APPROVAL` và gỡ mục "Natural action phrases" trong `approval.md`. Các câu mệnh lệnh trần ("làm đi", "tiến hành đi", "go ahead") không còn được chấp nhận nếu thiếu đối tượng hoặc đại từ (`spec`, `plan`, `quick`, `cái này`).

## 0.63.0 — 2026-10-11

Tự động mang theo các file docs/log khi mở request branch.
Kế hoạch: `docs/tdq/plan/2026-10-11-1300-tu-dong-mo-nhanh-doc-log.md`.

- **Mở branch không ngắt quãng cho docs/log.** Ở bước 3b của `tdq-intake`, nếu working tree chỉ có tài liệu, log hoặc cache (`docs/**`, `*.md`, `logs/**`, `*.log`), hệ thống tự động tạo branch và mang file theo. Có file code thì dừng hỏi người dùng.

## 0.62.0 — 2026-10-11

Tự động cập nhật setup, dependencies và instruction user-level (`CLAUDE.md`) khi phát hiện version mới
qua hook `SessionStart`, không đòi hỏi chạy thủ công lại lệnh setup, áp dụng cho cả Claude Code và Codex.
Kèm bộ rào chắn cấm đổi mode harness (`EnterPlanMode`) và ép bắt buộc mở request bằng `tdq-intake`.
Kế hoạch: `docs/tdq/plan/2026-10-11-0932-auto-update-setup-version.md`.

- **Tự động đồng bộ khi đổi version.** `hooks/scripts/session_start.py` và `scripts/tdq_setup.py` kiểm tra
  phiên bản plugin hiện tại; nếu chưa có mốc hoặc có version mới hơn, tự động đồng bộ instruction vào
  `~/.claude/CLAUDE.md`, khai báo MCP/hook cho Codex và dọn tiến trình broker thừa, sau đó ghi mốc
  `docs/tdq/.tdq-phat-hanh.json`.
- **Rào chắn mode và intake.** Cấm tự ý đổi mode làm việc, cấm gọi `EnterPlanMode` hoặc popup UI `AskUserQuestion`,
  bắt buộc mọi yêu cầu mới mở qua `tdq-intake` và trao đổi trong chat.
- **Áp dụng đa nền tảng.** Hoạt động đồng bộ êm dịu trên cả Claude Code và Codex.

## 0.61.0 — 2026-10-11

Hợp thức hóa các câu lệnh hành động dứt khoát tự nhiên ("làm đi", "tiến hành đi", "triển đi",
"go ahead"...) thành câu duyệt hợp lệ cho các cổng `spec` và `plan`. Tuyệt đối cấm ở cổng `mode`
hoặc cổng `quick` (nơi còn câu hỏi mode hoặc mức QC đang chờ), và chặn câu hành động khi có câu hỏi
hoặc điều kiện/confirm đi kèm. Kế hoạch: `docs/tdq/plan/2026-10-11-0159-hop-thuc-hoa-duyet-tu-nhien.md`.

- **Cụm hành động tự nhiên (`ACTION_APPROVAL`).** Trong `hooks/scripts/prompt_context.py`, nhận diện
  các câu dứt khoát ("làm đi", "tiến hành", "triển đi"...) là duyệt khi đang chờ `spec` hoặc `plan`.
- **Chặn khi có câu hỏi hoặc điều kiện.** Chặn câu hành động trần ở cổng `mode` và `quick` (bắt buộc
  chọn mode/QC); chặn khi câu nói chứa nghi vấn, điều kiện hoặc confirm (`nhưng`, `confirm`, `xác nhận`, `nếu`, `?`...).
- **Cập nhật quy định.** `skills/tdq-conventions/references/approval.md` ghi rõ nguyên tắc duyệt tự nhiên
  theo ngữ cảnh và các ngoại lệ bắt buộc hỏi lại. Bảo toàn các điểm neo luật trong `docs/tdq/audit/luat-hien-co.md`.

## 0.60.0 — 2026-10-10

Bổ sung chỉ dẫn rõ ràng vào các phase: user trả lời và duyệt trực tiếp trong chat (dạng `1a 2b 3c`,
"duyệt spec", "duyệt plan", "duyệt nhanh"), tuyệt đối cấm mở popup tool / dialog câu hỏi chọn
(`AskUserQuestion`). Kế hoạch: `docs/tdq/plan/2026-10-09-1948-luat-hoi-duyet-trong-chat.md`.

- **Cấm `AskUserQuestion` và popup tool.** Bổ sung quy định chat-only tại 6 file:
  `skills/tdq-conventions/references/user-facing-block.md`,
  `skills/tdq-conventions/references/approval.md`, `skills/tdq-conventions/SKILL.md`,
  `skills/tdq-intake/references/interview.md`, `skills/tdq-spec/SKILL.md`, `skills/tdq-plan/SKILL.md`.
- **Khối trả lời chuẩn.** Hướng dẫn rõ ràng định dạng trả lời `1a 2b 3c` hoặc câu tự nhiên, kết
  lượt chờ user nhắn trong chat thay vì gọi tool popup.
- **Giữ nguyên điểm neo luật.** Bảo toàn số dòng của các quy tắc trong `docs/tdq/audit/luat-hien-co.md`.

## 0.59.0 — 2026-10-08

Mỗi project chỉ mở được request khi LSP đã được CHỨNG MINH trả lời đúng cho từng module (ngôn ngữ,
gốc), qua đúng đường MCP agent dùng. Ca gốc (bench 2026-10-07): `start_lsp` thiếu `language_id`
trên repo Python → agent-lsp bật hết server, TypeScript thành server hiện hành → crash
`0xc0000409` / "No Project", trong khi `agent-lsp doctor` vẫn báo khoẻ.
Báo cáo: `docs/tdq/reports/2026-10-07-2225-tu-dong-setup-lsp.md`.

- **Module LSP** (`scripts/lsp_module.py`, mới). Dò (ngôn ngữ, gốc) theo file mốc sâu nhất —
  repo một ngôn ngữ là một dòng, claudecodeui là `typescript:.` + `typescript:server`. Lệnh mới
  `tdq_lsp.py module | kich-ban | ghi-kiem`: script chọn symbol và in sẵn ba lời gọi MCP, agent gửi,
  script chấm (tham chiếu LSP > số lần trong file định nghĩa). Kết quả hạn 24 giờ hoặc tới khi file
  mốc / dòng MCP đổi.
- **Bậc 8 "LSP theo module"** trong `tdq_lsp.py check`; bậc 3 thêm cổng: mỗi ngôn ngữ của project
  phải có dòng trong `args` của MCP `lsp`.
- **Cổng `init`.** `tdq_state.py init` từ chối khi còn module chưa ĐẠT; lối thoát
  `--bo-qua-lsp "<lý do>"` ghi vào `lsp_bo_qua`, report đọc ra.
- **Hook `lsp_gate.py` (`TDQ:LSP`, chặn).** `start_lsp` thiếu `language_id` hoặc sai cặp
  (gốc, ngôn ngữ) bị từ chối, lời chặn liệt kê lời gọi đúng.
- **Tự cài không hỏi.** `tdq_setup.py` cài agent-lsp từ bản phát hành GitHub (kiểm SHA256 theo
  `checksums.txt`, chạy được trên Windows — `install.sh` upstream thì không); ngôn ngữ mới xuất hiện
  trong project (vd. Python rồi thêm JS + HTML) được cài server và khai vào MCP `lsp` (sao lưu
  `~/.claude.json` trước khi ghi, rồi nhắc `/mcp` kết nối lại); SessionStart dựng nền lại khi tập
  ngôn ngữ đổi. Tắt `agent-lsp daemon-broker` mồ côi, cảnh báo bộ nhớ commit < 4 GB.
- **Luật chữ.** Intake 1b tự chạy setup → check → kịch bản; `kiem-lsp-hieu-ung.md` viết lại theo
  module; `uu-tien-tim-kiem.md` thêm luật gọi `start_lsp` theo module (TS mở file trước, ưu tiên
  tool theo file, `find_symbol` chỉ hỏi server hiện hành — issue #55 upstream).
- **Test không chạm máy.** `TDQ_KHONG_CHAM_MAY=1` (đặt cho cả tiến trình test) khoá ba việc chạm
  máy thật: tải/cài agent-lsp, ghi `~/.claude.json`, tắt tiến trình.

## 0.58.0 — 2026-10-07

Gỡ lumen, luật tìm kiếm còn ba tầng (LSP · grep · graphify), cổng tìm kiếm dẫn tới tầng đang
sống. Đo trước khi gỡ (request `2026-10-07-1843-phan-tich-bo-lumen`): 12 câu khái niệm trên
TDQ-Workflow và claudecodeui, không lumen vẫn trúng 11/12 và 10/12 (trượt 0), token 0,88× và
1,06× — không giảm đáng kể. Báo cáo: `docs/tdq/reports/2026-10-07-2041-go-lumen-toi-uu-tim-kiem.md`.

- **lumen ra khỏi mã.** Thang `tdq_lsp.py check` còn 7 bậc đánh số liền (bậc lumen cũ là 5;
  hook xung đột 6→5, cấu hình gốc import 7→6, graphify 8→7), smoke còn 3 tầng — máy không cài
  lumen không còn "CHƯA ĐẠT, exit 4" vĩnh viễn. Bỏ `wake`/`release` của ollama, bước `reindex`
  của `tdq_finish.py`, phần lumen của `tdq_setup.py` (cấu hình, dựng nền, khối ghim CLAUDE.md),
  `setup_status`, khai MCP lumen cho Codex; xoá `skills/tdq-setup/references/lumen.md`,
  `.lumenignore`.
- **Cổng `TDQ:SEARCH` bớt lượt thừa.** Lời chặn chỉ nêu tầng mà dấu mốc sẵn sàng ghi là sống,
  kèm lệnh dùng ngay (`start_lsp` khi LSP báo chưa khởi động). Lời gọi `mcp__lsp__*` được ghi sổ
  ngay ở PreToolUse, nên lời gọi lỗi vẫn tính là đã hỏi. Mốc cũ còn khoá `lumen` không còn làm
  dựng lại nền mỗi 6 giờ.
- **Luật chữ 3 tầng.** Bốn câu từng chấm agent oan khi lumen vắng (`analyze-full.md`,
  `quick-lane.md`, `tdq-build/SKILL.md`, `PHASE_TABLE`) nay đòi LSP rồi graphify; câu chuẩn và
  bảng loại câu hỏi trong `uu-tien-tim-kiem.md` mang số đo mới kèm tên repo.
- **Codex.** `tdq_codex_mcp.khai_hook_codex` không còn ghi đè `.codex/hooks.json` viết tay của
  chính repo plugin (đã xảy ra 2026-10-03 và 2026-10-07). Mỗi lần ghi hook, nó nói rõ hai điều
  kiện để hook chạy. Một: hook phải được duyệt ở `/hooks`, hook chưa duyệt bị bỏ qua lặng lẽ. Hai:
  trên Windows, sandbox `read-only`/`workspace-write` chặn mọi tiến trình, kể cả tiến trình hook
  (`docs/tdq/research/2026-10-07-2041-hook-codex.md`).

## 0.57.0 — 2026-10-05

Một luật chạy test, một nguồn. Bước trung gian chỉ chạy test trong vùng chạm, trọn bộ dồn về
hai cổng. Trước bản này `tdq-build` ("EXACTLY ONCE"), khuôn plan ("sau mỗi phase chạy toàn bộ")
và `qc.md` (mỗi vòng sửa) nói ba kiểu khác nhau. Báo cáo:
`docs/tdq/reports/2026-10-03-1907-test-vung-cham-buoc-trung-gian.md`.

- **Bước trung gian chạy `scripts/tdq_test.py vung-cham`.** Nó chọn vùng chạm cộng bán kính ảnh
  hưởng: test nhắc đường dẫn/tên file, import bắc cầu đọc bằng AST, test quét thư mục cha. Trọn
  bộ chỉ ở 2 cổng: QC-F1 (thay lần "xong implement") và sau vòng sửa QC cuối nếu có sửa.
- **Không chắc thì chạy hết.** Bán kính ≥ 60% số module, hoặc file mã/loại không rõ ngoài
  `scripts/ hooks/ skills/ tests/ agents/` → trọn bộ trong một tiến trình. File dữ liệu (.md,
  .json…) chỉ kéo theo test nhắc đường dẫn của nó.
- **Đo trên repo này.** Sửa `stop_gate.py` → 16/129 module, 51,6 s (trọn bộ ~420 s). Sửa hub
  `tdq_state.py` → 98/129 module → trọn bộ.
- **Sổ sách.** `tdq_test.py tron-bo` ghi sổ, và có sổ bán kính bỏ sót (QC-F1 đỏ ở module bán kính
  chưa chọn); report in số lần, xem bằng `tdq_test.py so`. `next` nhắc khi số lần trọn bộ vượt
  ngân sách 2 (3 sau một lần trọn bộ đỏ) — chỉ nhắc, không chặn.
- **Test chạy được từ PowerShell.** Bỏ lệnh shell `true` khỏi 5 module test (trước: 26 fail +
  1 error).
- **Trung thực về tiết kiệm.** Nền cũ trung bình 7,4 lần trọn bộ/request (59 lần/8 request). Hai
  request gần nhất đã chỉ 2–3 lần, nên lợi chính là khoá luật cho khỏi trôi ngược.

## 0.56.0 — 2026-10-03

Đo ngưỡng ở spec, không dừng giữa implement vì ngưỡng. Ca gốc: một phiên excalidraw dừng giữa
plan để hỏi nâng ngưỡng installer 200 → 250 MB. Riêng bộ cài WebView2 offline đã 212 MB, và một
lần đọc trang tải ở lúc viết spec là bắt được. Báo cáo:
`docs/tdq/reports/2026-10-03-0732-do-truoc-lam-mot-turn.md`.

- **Đo trước ở spec (luật R14 của `doc_lint`).** Mỗi ngưỡng số ở §6 của spec mới phải có cột
  `Đo trước` (số đo thật, hoặc ước lượng có nguồn) và cột `Dự phòng nếu trượt`. Thử trên spec
  cũ: nhận đúng 10/10 hàng có ngưỡng, 0/10 hàng phép tồn tại. Spec cũ không bị áp hồi tố; tên cột
  tiếng Anh cũng được nhận.
- **`approve spec` từ chối khi R14 đỏ.** Lối thoát duy nhất là `--bo-qua-do "<lý do>"` của user,
  ghi vào state.
- **Lệch spec thay cho câu hỏi giữa chừng.** Ngưỡng trượt lúc implement/qc → áp cột dự phòng,
  ghi bằng `tdq_state.py lech add`, làm tiếp. QC ghi "PASS (lệch, chờ duyệt)". `next` ở qc/report
  liệt kê lệch chờ duyệt, và report hỏi duyệt từng cái (`lech duyet`/`lech bac`).
- **`pause` chỉ nhận 4 loại bất khả kháng** (`--loai`): mất truy cập/công cụ hỏng · việc phá huỷ
  khó đảo ngược · đầu vào chỉ user có · QC chạm trần 3 vòng. "Đổi phạm vi spec" không còn là lý
  do dừng.
- **Hook `ask_gate.py` (`TDQ:ASK`).** Nó nhắc khi agent hỏi user bằng popup ở implement/qc —
  đường dừng mà cổng Stop không thấy. Chỉ nhắc, không chặn, không trả quyết định quyền.

## Lịch sử cũ hơn

Bản 0.55.0 đến 0.37.0: `docs/CHANGELOG-archive-2.md`; bản 0.36.0 trở xuống:
`docs/CHANGELOG-archive.md`. Tách để giữ file chính dưới 500 dòng; chữ nghĩa giữ nguyên.
