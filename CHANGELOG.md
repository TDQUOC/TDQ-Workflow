# Changelog

Mới nhất trên cùng. Ngày theo múi giờ máy phát hành.

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

## 0.55.0 — 2026-10-03

Luật tìm kiếm 4 tầng giờ được **cưỡng chế**, không chỉ được nhắc. Soi một phiên thật trên
excalidraw: ~20 lần grep qua 4 request, 0 lần hỏi lumen hay LSP cho tới khi user phải hỏi luật.
Báo cáo: `docs/tdq/reports/2026-10-03-0015-ep-luat-tim-kiem.md`.

- **Cổng tìm kiếm (`hooks/scripts/search_gate.py`, mã `TDQ:SEARCH`).** `PreToolUse` trên
  `Bash|Grep|PowerShell` **chặn** lần tìm code đi tắt tầng khái niệm. Request chưa hỏi
  lumen/LSP/graphify → chặn. Một lần hỏi mở khoá 10 lần tìm; sau đó grep kiểu đoán mò bị chặn
  lại. Miễn: lọc danh sách file, và tên có nguyên văn trong prompt. Phát lại phiên excalidraw:
  bắt 11, bắt oan 0, lọt 0. Đây là một điểm chặn mới — quyết định ghi ở `docs/kien-truc.md`.
- **Không kẹt.** Cổng đứng xuống khi tầng khái niệm chưa dựng xong hoặc mốc báo không tầng nào
  sẵn sàng. Nó cũng đứng xuống sau 3 lần chặn mà request chưa ghi được lần hỏi nào. Mỗi lần đứng
  xuống, nó nói ra một lần mỗi lượt.
- **Codex có cùng cổng.** Codex đã bỏ hook đi theo plugin, nên `tdq-setup` ghi `.codex/hooks.json`
  cấp project bằng đường tuyệt đối; khi plugin lên bản, entry cũ được sửa tại chỗ, không nhân
  đôi. `tdq-setup` cũng khai MCP lumen + LSP qua `codex mcp add` — chỉ thêm, có backup.
- **Tự dựng bộ tìm kiếm.** `SessionStart` ở một project thật (có `.git`) chưa sẵn sàng sẽ khởi
  động dựng nền tách rời, có khoá pid chống chạy chồng; tắt bằng `TDQ_KHOI_TAO_NEN=0`.
- **Thang kiểm thật hơn.** Bậc 3 khởi động language server thật; smoke grep theo ngôn ngữ thật
  của project; thang 8 bậc + smoke 4 tầng chạy bằng một lệnh.
- **Đường dẫn tuyệt đối trong output hook** khi project không có `scripts/` của plugin — lệnh in
  ra ở project khác giờ chạy được nguyên văn.
- **`scripts/search_replay.py`** phát lại một transcript qua đúng luật của cổng, để đo lại N khi
  có thêm phiên thật.

## 0.54.0 — 2026-10-02

Workflow nạp ít chữ hơn mà không mất một luật nào: **sàn tuân thủ của một request lane `full`
giảm 55.439 → 49.531 token (−10,7%)**, trong khi số mục luật TĂNG 334 → 342. Báo cáo:
`docs/tdq/reports/2026-09-28-2324-toi-uu-context-workflow.md`.

- **Cổng nhắc đọc lại (`hooks/scripts/read_gate.py`).** Đo trên một phiên thật 22,76 MB:
  `tdq_state.py` bị đọc 12 lần, `build_portable.py` 19 lần. Riêng hai file đó là 28% nội dung
  đọc vào. Và 98,2% input của phiên là đọc lại context đã giữ. Cổng CHỈ NHẮC, một lần cho mỗi
  file, và im khi `offset/limit` nhắm vùng chưa đọc hoặc khi file đã đổi. Nó giữ SỔ RIÊNG chứ
  không dùng sổ lượt chung. Lý do: sổ lượt bị xoá ở mỗi prompt. Ký ức dựng trên đó không thấy
  được đúng cái nó phải bắt — việc đọc lại qua nhiều lượt của một phiên.
- **Chỉ mục dòng cho file luật dài (`scripts/doc_index.py`).** Mỗi file dài nhận một khối chú
  thích HTML `<!-- muc-luc-dong: Tên=đầu-cuối · … -->`, nhờ đó đọc ĐÚNG MỘT MỤC bằng
  `offset/limit` thay cho đọc trọn file. Khối ở dạng chú thích chứ không phải bảng vì một bảng
  cùng lượng thông tin tốn ~230 token/file — tốn đúng vào ngân sách nó đang đi tiết kiệm.
- **Trần 3.500 token mỗi file luật, cưỡng chế được ở CI.** CI cố ý không có tokenizer, nên
  `scripts/token_budget.py` đo trên máy CÓ tokenizer và khoá con số bằng `sha256` trong
  `docs/tdq/token-budget.json`; rule **R13** của `doc_lint` chỉ so hash. Không dùng dòng hay byte
  làm đại lượng thay thế: đo trên 43 file, token/dòng lệch 4,1 lần và byte/token lệch 1,81 lần.
  Ba file vượt trần đã được dời phần CÓ ĐIỀU KIỆN sang file em — không nén luật, theo `soul.md`.
- **Bảy file em TẦNG 1.** Phần chỉ cần khi gặp đúng ca được tách khỏi file cha và trỏ thẳng từ
  `SKILL.md`, đúng luật một tầng. `plan-template` 5.067 → 3.493, `quick-lane` 4.356 → 3.419,
  `team-mode` 3.652 → 3.313, `uu-tien-tim-kiem` 3.449 → 2.067 token.
- **Câu luật tìm kiếm còn một bản.** Sáu bản nguyên văn của cùng một câu (1.125 token) thành một
  bản gốc + năm con trỏ ba dòng.
- **CI in bảng bề mặt context** (`continue-on-error`, một tổ hợp). Nó là SỐ ĐO, không phải luật:
  luật trần token mới được làm đỏ build.

## 0.53.0 — 2026-09-28

Bộ tìm kiếm chuyển từ "có cài" sang "chứng minh được là đang trả lời đúng", và **breaking
change**: skill `tdq-lsp-setup` đổi tên thành `tdq-setup`. Báo cáo:
`docs/tdq/reports/2026-09-28-0910-lumen-check-va-setup-tool.md`.

- **BREAKING — `tdq-lsp-setup` → `tdq-setup`.** Không giữ bí danh: gõ tên cũ sẽ không thấy gì.
  Tên cũ nói skill này chỉ lo LSP. Thực tế nó vốn đã cài cả lumen, và nay nhận luôn việc cài đủ
  phụ thuộc cho workflow. Bốn nhóm đã đổi theo: bảng trần dòng của `doc_lint`, danh sách thứ tự
  nạp của `build_portable`, năm chỗ trích luật tìm kiếm, và file test chống lệch.
- **Bậc 5 hết mù với chuyện "sống mà trả lời sai".** Nó từng chỉ hỏi "ollama có chạy không", nên
  suốt phiên 2026-09-28 nó báo ĐẠT trong khi MCP `lumen` chết cả phiên (`CONNECTION_CLOSED`).
  Nay nó hỏi lumen một câu thật rồi đọc câu trả lời, và đo xem index có nội dung MỚI của cây làm
  việc hay không. Cả hai phép đo đi bằng CLI: lumen 0.0.42 khai `defaultFreshnessTTL = 30s`, nên
  đường MCP có thể trả lời từ một lần "fresh" đã cũ.
- **Bậc 5 không còn dò ollama bằng PATH.** Socket được hỏi TRƯỚC; `which` chỉ còn để phân biệt
  "cài rồi mà đang ngủ" với "chưa cài bao giờ". Đo trên macOS: `/opt/homebrew/bin/ollama` có
  thật và login shell tìm ra, nhưng `shutil.which` từ tiến trình không-login trả `None` — thứ tự
  cũ kết luận "thiếu ollama" và in lệnh cài cho một daemon đang phục vụ.
- **Thêm bậc 8 — đồ thị graphify.** Công cụ thứ tư của bộ tìm kiếm trước nay không có bậc nào.
  Nó hỏng đúng kiểu một index không ai dựng lại. Đo được 2026-09-28: đồ thị cũ 8 ngày, 34% node
  (845/2415) trỏ vào thư mục đã xoá.

## 0.52.0 — 2026-09-27

CI xanh trên cả ba hệ ở lần chạy thứ hai, và **breaking change**: sàn Python lên 3.11. Báo cáo:
`docs/tdq/reports/2026-09-27-1905-ci-do-ba-he.md`.

- **BREAKING — sàn Python 3.8 → 3.11.** `PYTHON_MIN` đổi, lớp dự phòng `tomllib = None` trong
  `tdq_codex.py` bỏ hẳn cùng 6 guard `skipIf` của nó, ma trận CI đổi `3.10` → `3.11`. Ai đang
  chạy 3.8–3.10 sẽ không dùng được bản này. 3.11 là bản đầu tiên có `tomllib` trong thư viện
  chuẩn, và nay là bản thấp nhất được CI chạy thật.
- **Header `SessionStart` không còn phụ thuộc độ dài đường dẫn** — lỗi sản phẩm, đo trên macOS.
  Khối đầu có trần 600 ký tự và tính cả dòng `Project: <đường dẫn>`. Thư mục tạm của runner macOS
  là `/var/folders/36/tjdph2t965j8snz9_vkdnw0r0000gn/T/tmpXXXX`, đủ dài để `cap()` cắt mất dòng
  lệnh. Đường dẫn là dữ liệu của user, nên phần nhường là phần HIỂN THỊ.
  `duong_hien_thi()` giữ hai đoạn cuối trong trần 32 ký tự (`…/ForAgentCode/TDQ-Workflow`), còn
  `STATE.md` vẫn giữ đường dẫn tuyệt đối đầy đủ.
- **Phép kiểm dấu ngã hỏi đúng câu** — `con_dau_nga_chua_bung()` trong `tdq_checkportable.py`,
  dùng chung cho sản phẩm và ba file test. Bản cũ ("có ký tự ngã là sai") báo đỏ oan trên runner
  Windows, nơi thư mục nhà có dạng 8.3 (`RUNNER~1`). Tệ hơn: nó nuốt luôn nhánh `elif` phía sau,
  nên phép kiểm THẬT — bundle dựng dưới thư mục nhà của máy khác — không bao giờ chạy ở đó.
- **Fixture test viết theo hệ đang chạy** — 9 ca của `test_shim_python3` dựng PATH giả bằng đường
  dẫn Windows cho mọi hệ, mà `os.pathsep` trên POSIX là dấu hai chấm nên đường dẫn ổ đĩa bị xé
  làm hai. Sản phẩm vốn đúng; nay 9 ca đó chạy THẬT trên cả ba hệ thay vì bị skip, cộng một ca
  canh chính cái bẫy đó.
- **Cổng D7 không còn tự tắt trong im lặng** — `_cham_d7` từng `continue` khi không đọc được mốc
  thời gian của commit. Một mốc lạ vì thế làm cổng "agent khác vừa commit" tắt hẳn, mà trông y
  như "không có ai commit thêm". Nay nó báo rõ là không kết luận được.
- **Vá lỗi 0.50.0 để lại** — `_in_ket_qua` vẫn gọi `da_trusted()` và `duong_config_codex()`, hai
  hàm biến mất cùng lớp trust: một `NameError` ngồi chờ từ bản đó tới nay.
- **Đo trên máy thật, không đoán** — Linux (3.14.4) 1993 ca; macOS pyenv 3.13.15 và brew 3.14.7
  đều 1993 ca; Windows 3.13.15 2016 ca. Tất cả 0 fail, 0 error. CI xanh cả 6 job (run 36322434130).

## 0.51.0 — 2026-09-23

Mức độ QC thành quyết định của user, hỏi một lần trước khi viết spec. Báo cáo:
`docs/tdq/reports/2026-09-23-1148-hoi-muc-qc.md`.

- **Khoá `muc_qc`** — `lite|full|ultra|off`, mặc định `full`, chuẩn hoá fail-closed như
  `muc_gat`: giá trị rác, trống hay sai kiểu đều về `full`, nên không gõ nhầm nào mua được một
  vòng QC rẻ hơn. `schema_version` 5 → 6. `next` và `STATE.md` in mức QC trên dòng riêng, không
  gộp với `Lean level` — hai thang khác nhau, gộp là mời nhầm.
- **Hỏi ở đâu** — cuối phase `analyze` (bước 5c của `analyze-full.md`), TRƯỚC khi viết spec §6,
  vì hỏi sau là phải sửa mục user đã duyệt. Lane express hỏi ngay trong khối mời duyệt sẵn có,
  không thêm lượt dừng nào.
- **Bảng mức × loại kiểm** — một bảng duy nhất trong `skills/tdq-build/references/qc.md`, mỗi ô
  là CÓ hoặc KHÔNG cho bốn loại: DoD, unit test, smoke test, runtime test, cộng cột QC độc lập
  bằng agent. Mức mặc định `full` **không** chạy runtime test: đó là loại từng treo rất lâu, và
  một vòng QC treo thì bị bỏ dở, mất nhiều hơn được. `ultra` mới chạy runtime và gọi
  `tdq-qc-tester` — trước đây agent này treo vào câu "việc lớn hoặc rủi ro cao", không ngưỡng
  nào đo được, nên thực tế không bao giờ chạy.
- **Trần 120 giây** cho mỗi phép smoke/runtime: chạm trần thì giết tiến trình và ghi FAIL kèm
  lệnh, rồi phân tích xem là lỗi thật hay việc cần chạy lâu thật. Cấm tự nâng trần — nâng phải
  hỏi user, vì nâng trần cho một phép đang đỏ là vặn bóng đèn cho đèn khỏi sáng.
- **Gỡ cờ `--no-qc`** của `approve quick` cùng khoá `quick_qc_skipped`: một cơ chế duy nhất cho
  cả hai lane. Lệnh cũ chết kèm câu chỉ sang `set muc_qc=off`. Dòng nhắc duyệt không còn mời bỏ
  QC — `off` vẫn đặt tay được nhưng không bao giờ được bày ra trong danh sách chọn.
- **Test** — hai file mới khoá khoá state và luồng hỏi, một file khoá bảng mức cùng luật trần.
  Ba ca cũ ghim `schema_version = 5` nay đọc số từ chính sản phẩm.

## 0.50.0 — 2026-09-21

Học cách superpowers tổ chức: một nguồn `skills/`, mỗi host một adapter mỏng, không còn bản sao
nào trong repo. Báo cáo: `docs/tdq/reports/2026-09-21-0029-hoc-superpowers-da-host.md`.

- **Adapter Codex CLI** — `.agents/plugins/marketplace.json` (`"url": "./"`) và
  `.codex-plugin/plugin.json` (`"skills": "./skills/"`). Đo trên Codex CLI 0.155.1:
  `codex plugin list` ra `tdq-workflow@tdq-local`. Policy xác thực phải là `ON_INSTALL` hoặc
  `ON_USE` — CLI từ chối `NONE`, test khoá giá trị.
- **Adapter OpenCode** — `.opencode/plugins/tdq-workflow.js`, JavaScript thuần (`node:path`,
  `node:fs`, `node:url`), đọc thẳng `skills/*/SKILL.md`, bọc try/catch mọi bước để một lỗi không
  kéo sập plugin khác của host. Hướng dẫn cài ở `.opencode/INSTALL.md`.
- **Antigravity sinh tại chỗ** — `build_portable.py --sinh-agy` sinh layout vào
  `~/.gemini/config/plugins/tdq-workflow/` trên máy người dùng, bất biến, từ chối ghi đè thư
  mục không phải do nó sinh. Đường dẫn tuyệt đối vì thế là của đúng máy chạy.
- **Gỡ ba bundle** — `portable_claude/`, `portable_codex/`, `antigravity_portable/` ra khỏi repo
  (`git rm`, lịch sử còn nguyên). `build_portable.py` 1077 → 634 dòng, không còn hàm hay hằng nào
  không có nơi dùng (khoá bằng test đo khả năng với tới từ `main`); bỏ cờ `--only` (được nhận
  rồi lờ đi), và chạy không cờ nay thoát 2 thay vì dựng lại bundle NGAY TRONG repo.
  `tdq_checkportable.py` 675 → 560 dòng: bỏ lớp trust/codex, thiếu `manifest.json` chỉ còn là
  NOTE; giữ `setup --shim` và phần kiểm môi trường.
- **Sửa lỗi mã hoá của 0.49.0** — 89 lời gọi `subprocess` chế độ văn bản (20 trong `scripts/`)
  và 36 `open()` trong test chưa khai `encoding=`, nên Windows giải mã đầu ra UTF-8 bằng cp1252
  và `proc.stdout` thành `None`. Con số "1983 ca, 0 fail" của 0.49.0 đo khi máy có
  `PYTHONUTF8=1`; bỏ biến đó thì là 273 error. Khoá bằng `tests/test_ma_hoa_subprocess.py`
  (đọc AST, bắt cả lời gọi trải nhiều dòng). `codex_edit_gate.py` ép UTF-8 tại chỗ vì không
  được import `scripts/`.
- **`utf8_io` im trên pipe** — dòng "forced 2 stream(s)" chỉ in khi stderr là console (hoặc
  `TDQ_UTF8_LOG_FORCE=1`). Nó chạy lúc import, trước khi script đọc `--quiet` của chính mình,
  nên hook và test không có cách tắt.
- **Header `SessionStart`** — dòng nhắc graphify và dòng nhắc tên lệnh Python chuyển ra sau
  trần 600 ký tự, thành đoạn riêng. Trên Windows đường dẫn dài từng cắt dòng graphify còn
  `graphify is n…`.
- **Suite chạy được trên máy sạch** — thiếu pytest, anthropic-tokenizer, graphify, node hay
  codex thì ca tương ứng thành skip có ghi lý do: 1917 ca, 0 fail, 0 error, 30 skip. Phép dò
  tokenizer nay hỏi chính `skill_tokens` — bản cũ tìm `.venv-tokens/bin/python`, nên trên
  Windows ba ca luôn bị skip dù đã cài.
- **CI ba hệ** — `.github/workflows/test.yml`: Ubuntu, macOS, Windows × Python 3.10 và 3.13,
  không cài công cụ ngoài, không bật chế độ UTF-8, tắt `core.autocrlf` trước checkout. Chưa
  chạy lần nào trên GitHub.
- **Lumen trên Windows** — `tdq_lsp.py` cảnh báo khi plugin lumen thiếu `bin/lumen` và in lệnh
  chép `lumen-windows-amd64.exe` sang; script `run` của lumen đoán sai tên hệ dưới Git Bash.
- **Tài liệu** — README viết lại phần cài cho bốn host; `docs/kien-truc.md` thay tầng "luật bản
  ngoài" bằng tầng Adapter và ghi ngoại lệ đường dẫn adapter vào `Đã chốt`.

## Lịch sử cũ hơn

Bản 0.49.0 đến 0.37.0 nằm ở `docs/CHANGELOG-archive-2.md`. Các bản này được tách dần để giữ file
chính dưới trần 500 dòng của `doc_lint` R6 (bản 0.49.0 dời ngày 2026-10-19). Bản 0.36.0 trở xuống
nằm ở `docs/CHANGELOG-archive.md` — tách ra ngày 2026-09-17 vì cùng lý do. Chữ nghĩa giữ nguyên,
không xoá dòng nào.
