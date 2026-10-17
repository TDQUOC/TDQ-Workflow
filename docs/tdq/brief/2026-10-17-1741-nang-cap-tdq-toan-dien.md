# BRIEF — Nâng cấp TDQ Workflow toàn diện từ đề xuất ECC
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> và mở request để update full đề xuất trên để nâng cấp TDQ-Workflow

> 1a 2a fan out subagent tuỳ thích để phân tích chuyên sâu và apply chuyên sâu để nâng cấp triệt để tdq-workflow

Hiểu ban đầu: mở request feature/full để triển khai13phiếu U01–U13 trong `docs/tdq/reports/2026-10-17-1621-de-xuat-ecc-toan-dien.md`, giữ dependency và điều kiện go/no-go, Windows/PowerShell trước, macOS/Linux sau. Người dùng cho phép fan-out khảo sát và triển khai chuyên sâu; không coi đó là bỏ cổng spec/plan hoặc tự duyệt thay đổi kiến trúc. Chưa sửa runtime trong analyze.

Đã duyệt hoàn tất request cũ: giữ/mang theo metadata/log và graphify dirty, merge commit1d3f5e6 bằng merge1096e16 về `docs/deep-research-kien-truc-ecc`, xóa nhánh request cũ; không push, không cleanup worktree tồn đọng. State cũ đã idle trước init mới.

Còn chốt sau khảo sát: contract phê duyệt theo host, phạm vi auth Windows cho live eval, khả năng bật U08/U09 có điều kiện, mức QC và ranh giới rollout. Mọi đề xuất không làm trong báo cáo vẫn giữ, không coi “triệt để” là quyền tạo daemon/router/cache dùng chung hoặc nới gate.

## Hiểu & kiến thức

### Năng lực dùng được

Kiểm kê2026-10-17: `skill_inventory.py --loc "hook approval parser Windows eval trace checkpoint memory retrieval agent review"` trả9skill TDQ, ẩn16skill khác; đã xét thêm built-in trong context. Chỉ gọi skill có trong danh sách user-invocable thực của phiên, tên trên đĩa không tự cấp quyền gọi.

| Skill/công cụ | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | Mở và phân tích request full |
| tdq-conventions | plugin:tdq-workflow | NỀN | State/log/git/ngôn ngữ; đọc file, không gọi trực tiếp |
| tdq-spec | plugin:tdq-workflow | NỀN | Chốt spec sau hỏi đáp |
| tdq-build | plugin:tdq-workflow | NỀN | Triển khai/QC/report sau spec và plan duyệt |
| tdq-lean | plugin:tdq-workflow | NỀN | Giữ tối thiểu, không nhập nguyên ECC |
| tdq-status | plugin:tdq-workflow | NỀN | Kiểm phase khi cần |
| tdq-plan, tdq-setup, tdq-check-status | plugin trên đĩa | NỀN | Chỉ theo tài liệu/CLI hiện hữu; không đoán tên skill gọi khi không được liệt kê |
| plugin-authoring | built-in | DÙNG | Đã đọc contract; skill dành mod TSX mới không khớp command hooks Python hiện hữu: không tạo mod/hot-reload/UI hoặc thay mô hình plugin; áp dụng chỉ khi có tích hợp host được giao rõ |
| code-review | built-in | DÙNG | Review code thay đổi sau implement, không thay DoD |
| security-review | built-in | DÙNG | Kiểm biên dữ liệu/quyền/credential sau thay đổi |
| simplify | built-in | DÙNG | Kiểm reuse/độ gọn sau code chạy đúng, không refactor ngoài vùng |
| claude-api | built-in | DÙNG | Chỉ nếu scope auth/CLI/model API cần tra hợp đồng; chưa cấp quyền gọi model/API |
| workflow-authoring | built-in | DÙNG | Chỉ nếu cần Workflow orchestration đã được user cho fan-out; hiện dùng4Agent trực tiếp, chưa gọi Workflow |
| Các skill còn lại đã xét | plugin/user/built-in | KHÔNG | khác lĩnh vực; không có chart/UI/deploy/cấu hình harness trong phạm vi hiện tại |

### Baseline và bằng chứng thao tác

- Repo chính HEAD1096e16; nhánh request `feature/nang-cap-tdq-toan-dien`, gốc `docs/deep-research-kien-truc-ecc`. ECC chỉ đọc HEAD76aaa77df6adc5b889e689007bf99b9a4f74af34. Plugin0.71.0, Python sàn3.11 theo build/CI; host hiện Python3.13.15, Git2.56.0.windows.1, Windows11. Không sửa runtime trong analyze.
- Setup/check17:41:07–29:7/8bậc đạt, cảnh báo graph stale37phút; rung8Python đã chứng minh, HTML không đủ mẫu. Không tự bypass gate. Setup đã tắt broker mồ côi pid9064 thuộc DailyWorkingLog và ghi nợ mem0-memory thiếu; đây là side effect thật, không nói setup thuần đọc. `mem0-memory` không có công cụ/skill, không giả kết quả.
- `graphify extract . --code-only`17:41:47 làm mới2267nodes/4538edges,128communities; không LLM/network. God nodes mới:cli35,main23,load22,Changelog22,_git21. Đồ thị là chỉ mục, không chứng minh source/test đúng. `list_symbols(build_portable.py)` lỗi closed network connection; dùng graphify và Read/Grep fallback, không khẳng định LSP truy vấn thành công.
- Đã đọc toàn bộ `docs/kien-truc.md`: phần đầu còn NHÁP; mục Đã chốt có ràng buộc thật phải giữ, gồm hooks→scripts không ngược, một state writer, không deny vì chưa duyệt, kiểm suite ở2cổng và kiến trúc adapter mỏng. Quyết định2026-10-14 nói dev/main; request này mở từ nhánh hiện tại đã user chốt, không tự chuyển dev/main hoặc phát hành. Cần giữ quyết định release riêng, không sửa quy tắc kiến trúc để hợp nhánh tiện tay.
- `scripts/build_portable.py:44-77` loại docs/tests và evaluator khỏi release; U11 có thể là dev tooling, không tự đưa evaluator/knowledge riêng repo vào bundle. `.github/workflows/test.yml` có CI3OS×Python3.11/3.13, không phải bằng chứng đã chạy macOS/Linux trong request này; không gỡ CI các OS đó.
- Sai thao tác parent cần giữ:4lời gọi Agent đã truyền `isolation=worktree`, `model=fable`, `effort=high` dù mô tả nói chỉ đọc/inherit; effort override không được user chỉ định mức cụ thể. Đã gửi correction cho cả4: đọc absolute repo chính, không cwd snapshot6ddd1a4, không LSP start/setup/ghi/cleanup. Git worktree list17:44 có4worktree locked ở6ddd1a4 và worktree cũ adf…; không force cleanup. Không gọi quyền fan-out là quyền cho các override sai này, không xóa lịch sử hoặc claim đã tuân thủ tuyệt đối.
- Agent U11–U13 báo Grep bị TDQ:SEARCH chặn do chưa concept query; tiếp tục Read đường dẫn đã biết/Glob, không nhờ parent chạy cùng lệnh để né chặn. Khảo sát là nguồn tĩnh, chưa suite/smoke/performance mới.

### Phạm vi đã chốt

- Mặt CHỌN: nâng cấp chức năng U01–U13, tính đúng/độ tin cậy/quyền duyệt, maintainability và tối ưu có điều kiện theo báo cáo đã chốt.
- Mặt LOẠI: macOS/Linux triển khai-nghiệm thu giai đoạn này; daemon/controlplane mới, shared mutable dependency cache, tự học thành luật, tự hạ model, nới gate.
- Bối cảnh: một repo plugin hiện hữu0.71.0, một máy Windows hiện có;4nhóm khảo sát chạy song song, số agent implement sẽ theo dependency/file ownership sau plan, không tạo số lượng làm mục tiêu.
- Mức đầu tư suy ra: đầy đủ — chạm hook/approval/state/team/parsers và công cụ phát triển đang dùng, cần regression/failure-path thực, không đồng nghĩa rewrite toàn repo.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| analyze — nguồn hiện tại +4nhóm chuyên sâu | CÓ | Phân vùng U01/02/04/07;U03/05/08;U06/09/10;U11/12/13, không trùng vùng chính |
| Web/ECC audit mới | BỎ audit mới; CÓ tra contract host chính thức | Dùng snapshot/báo cáo đã có; đã tra hướng dẫn cài OpenCode generic, không gửi dữ liệu repo; chỉ tra tiếp khi thiếu contract host, không audit CVE/pricing |
| spec → plan | CÓ | Hai cổng user; chốt behavior/oracle/go-no-go/migration trước apply |
| implement theo wave, một chủ file | CÓ | User cho fan-out, thực thi chỉ sau gate và mode được ghi; không đồng thời sửa file nóng |
| đo U06/U08/U09/U10/U13 và no-op/HOLD | CÓ | Không ép tối ưu khi thiếu nhu cầu/lợi ích, không coi thiếu implementation là tự trượt khi spec cho giữ nền |
| review/QC độc lập + hồi quy | CÓ | User đã chọn ultra; kiểm nội dung thật thay nhiều vote, host chưa quan sát không được PASS |
| report/commit/release | CÓ report; commit/release xin riêng | Không phát hành/push hoặc sửa bản plugin đang cài từ quyền phân tích |

## Hỏi đáp

- Người dùng yêu cầu mở request triển khai full theo báo cáo, rồi chọn nguyên văn “1a 2a fan out subagent tuỳ thích để phân tích chuyên sâu và apply chuyên sâu để nâng cấp triệt để tdq-workflow”. Đã ghi full, cho phép khảo sát/triển khai fan-out; spec/plan chưa duyệt. Được giữ/mang theo dirty metadata/log/graphify khi switch để merge request cũ và mở mới; không push/cleanup.
- Vòng scope: không hỏi lại các mặt đã chốt bởi toàn bộ13phiếu/báo cáo và lựa chọn Windows trước; còn hỏi host ưu tiên, quyền live eval, rollout và QC sau digest. Chưa tự lấy mức ultra từ request cũ.
- Chờ đủ digest4nhóm và vòng hỏi có ảnh hưởng sản phẩm; chưa viết spec hoặc apply runtime.

### Kết quả khảo sát đã nhận — U01/U02/U04/U07 và U11/U12/U13

Chứng cứ S/tĩnh, chưa chạy lại tests hoặc live eval. Leader đã đọc trực tiếp `prompt_context.py:264-306`, `tdq_state.py:1954-2008`, `tdq_eval.py:669-740` để xác minh các quyết định chính, không lấy mọi claim digest làm kết quả đã kiểm.

- **U01:** hook chỉ gợi lệnh, không tự approve; hiện ghép60ký tự prompt vào shell command và khẳng định user duyệt, thiếu provenance/gate snapshot. CLI warn sai lane/order rồi vẫn ghi. Hướng thiết kế: parser/candidate bảo thủ + descriptor gate qua writer hiện hữu, bind request/path/hash/phase/options; không tự coi role=user hoặc flag origin=human là chứng thực. Legacy/manual có nhãn mức bảo đảm, không hồi tố. Cần tránh hardcode chỉ approve spec ở phase spec vì reapproval có thể tại QC.
- **U02:** `tests/test_report_kien_truc_ecc.py:68-84,211-225` có resolver sibling/ancestor và fallback fixture khi thiếu report. Acceptance phải root đúng checkout, missing/malformed/valid rõ; unit fixture giữ riêng, không bắt artifact tương lai trước gate. Cần giải quyết test suite sạch trong checkout/worktree khi artifact lịch sử không là đầu ra request mới.
- **U04:** outcome finding confirmed/refuted/uncertain/unverified tách khỏi execution PASS/FAIL/SKIP/PENDING; `tdq_state.py:877-917` hiện đọc token verdict, chưa đủ chứng minh evidence. Leader ghi QC, agent chỉ trả evidence; unknown/timeout không clean pass; một skeptic cho finding quyết định, không review vô hạn.
- **U07:** formatter tách decision; signature reason/evidence/gate-task dùng ledger có sẵn, reason đổi hiện full. **Baseline search_gate đã có breaker** khi readiness stamp thiếu sau3denial (`search_gate.py:105-129`, test_search_gate.py:173-187). Không hứa mọi lần deny khi baseline cho allow; giữ nguyên semantics hiện hữu, không thêm hoặc xóa breaker dưới danh nghĩa format.
- **U11:** offline scorer có thể triển khai độc lập auth. Manifest khóa base/candidate/corpus/scorer/host/check-set, parser kiểm nested types và result presence, missing/unsupported/invalid tách N/A/PASS; scope task/plan không ghép evidence chéo. Re-score ghi result version mới, không ghi đè lịch sử/raw trace. Source hiện live eval hardcode macOS Keychain và bypassPermissions; không chạy hoặc đọc token, không mặc định đưa bypass vào profile mới. Auth Windows/live budget phải quyết riêng, không bỏ config/plugin isolation để login chạy.
- **U12:** template knowledge hiện hữu + validation nhỏ, candidate/reviewed/rejected/superseded, evidence/scope/reviewer/time, không auto-load policy, không bulk-promote legacy. Không reuse `claude_export.harvest_secrets` vì đọc secret thật; regex chỉ phụ trợ, synthetic fixtures không lộ diagnostics.
- **U13:** agent chỉ ra filter sau condense và dedup theo name/user trước project có thể làm mất match/provenance (`skill_inventory.py:205-236`). Đo corpus Việt/Anh/identifier trước, tìm trên full description rồi render condense, NFC/casefold/token split, không dấu tín hiệu phụ; protected rows/tat-ca/invoke permission giữ. Claim caller toàn workspace chưa đầy đủ do Grep agent bị gate chặn, không tự chứng nhận hết.

### Kết quả khảo sát đã nhận — U03/U05/U06/U08/U09/U10

- **U03:** leader kiểm `hooks/hooks.json:58-71,104-110` xác nhận pre-search có PowerShell, post-observer thiếu PowerShell. `_common.py:97-110` trả JSON thẳng, caller `.get` không bảo đảm object. Sửa boundary typed và coverage cụ thể, inventory phân declared/fixture-tested/host-observed/unsupported/unknown. Không thêm PowerShell vào bash_gate regex POSIX rồi tự nói parity. Launcher chung/UTF-8stdin/quote path cần test integration Windows thật, không chỉ payload giả.
- **U05:** parser có depth nhưng chưa cumulative work/output budget và dialect PowerShell subset. Unknown phải tách khỏi not-recognized, observer không cấp concept credit khi unknown, safety caller không auto-allow; readiness breaker hiện hữu tách riêng không bị format/parser sửa ngầm. Command adversarial chỉ là chuỗi phân tích, không execute. Số budget chốt sau corpus/baseline, không lấy ECC làm bảo đảm tuyến tính.
- **U06:** leader đọc `tdq_team.py:345-410` xác nhận plan_sha dùng whole-file, assign ghi trực tiếp. Progress tick làm thay fingerprint, ảnh hưởng lifecycle. Đề xuất versioned assignment digest cho plan dependency tường minh, giữ seal approval và turn/progress SHA nguyên mục đích; legacy implicit-prose conservative. Projection gồm order/phase/ID/contract/test/deps/files/MCP/estimate, không bỏ checkbox mù khi logic legacy dùng tick. CLI và hook stale check phải chung helper, parse+hash cùng snapshot; atomic map write không phải workflow state writer mới. Digest không chứng thực map chống sửa tay/concurrency.
- **U08:** chưa đo host scheduling/critical path nên HOLD implementation dispatcher hiện tại; baseline/prototype theo gate trong spec. Hai main có exit/global/effects không thể import nối đơn giản; nếu GO phải result/effect contract, preserve deny/stdout/order/ledger, không blanket except→allow, không spawn hotpath/daemon. Không gom SessionStart background lifecycle.
- **U09:** HOLD advisory/new probe vì chưa history cụ thể, không ép build cảhai. Hiện nonzero probe bị chặn bảo thủ, nhưng nhãn conflict/error chưa tách; đây là gap chứ chưa chứng minh false clean. Nếu user muốn mở nhánh, ưu tiên probe clean/conflict/error/unsupported, chỉ unsupported fallback, corpus temp Git và no HEAD/index/worktree mutation; modern merge-tree có thể ghi objects nên công khai. DAG/file exclusion/test-before-merge không đổi.
- **U10:** pure derived renderer đọc không-heal, compact/resume task[~]/[>] tách, digest/source, pause/deviation codes và next hiện hữu. Không đọc prose blocker/transcript làm authority, owner không có thì unknown; tick[x] không chứng minh test. Không state/checkpoint file thứ2. Test cap cả output sau path rewrite và compact×ultra×long path, nguồn thật thắng missing/corrupt/stale/cross-project; không tự init/approve.
- Các agent U01/U03/U06 đã thử LSP thụ động/start trước khi dừng theo correction, kết nối lỗi; không chứng nhận side effects ngoài tracked source/config diff rỗng. U03/U06 digest từ nguồn tĩnh, chưa chạy test/benchmark. Cả4nhóm đã hoàn tất; notification U01 cuối xác nhận chỉ bàn giao, không khảo sát thêm. Source/config tracked diff17:49rỗng. Leader cũng đã kiểm resolver sibling/ancestor trực tiếp `test_report_kien_truc_ecc.py:68-84`.

### Vòng hỏi trước spec — đã trả lời

Nguyên văn người dùng: **“1c 2a 3a 4a”**. CLI ghi `muc_qc=ultra` lúc2026-10-17T17:54:37+07:00. Chốt: cả4host Claude Code/Codex/OpenCode/Antigravity cần nghiệm thu thực trên Windows; eval chỉ offline và auth preflight mock, không credential/model trả phí; không bổ sung khác. Phạm vi host mở rộng thay đề xuất1A cũ, không tự thu hẹp về fixture. Spec/plan chưa duyệt.

Kiểm môi trường17:54: `command -v` thấy launcher claude/codex, không thấy opencode/antigravity/agy. PowerShell Get-Command/Get-Process trả không có output; không đủ chứng minh các ứng dụng chưa cài. Chưa cài/tải/đăng nhập/thay cấu hình host hoặc khởi model. Cần user cung cấp môi trường/đường dẫn hoặc chọn chuẩn bị môi trường; không lấy test adapter giả lập thay nghiệm thu4host thực.

Chuẩn bị môi trường — user chọn nguyên văn **“1a”**: cho kiểm vị trí cài đặt thông dụng chỉ đọc; chưa cấp quyền tải/cài/sửa cấu hình/đăng nhập. Đã tìm thấy `C:/Users/admin/AppData/Local/Programs/antigravity/Antigravity.exe`; uninstall registry xác nhận DisplayName Antigravity2.22.0, DisplayVersion2.22.0. Chưa chạy executable, chưa chứng minh hook runtime. Không có bin/resources/app theo layout đã thử, không suy CLI từ kiểu VSCode.

OpenCode: chưa thấy executable/shim ở PATH, Local Programs, .local/bin, npm shim root, Scoop app/shim, WinGet Links, Chocolatey bin hoặc uninstall registry đã kiểm. Các ảnh/provider source tên opencode dưới npm là tích hợp của ứng dụng khác, không chứng minh OpenCode đã cài. Glob toàn Local bị timeout20s, không lặp quét rộng hoặc tuyên bố không tồn tại trên cả máy.

Tra tài liệu chính thức `https://opencode.ai/docs/` bằng WebFetch chỉ gửi câu hỏi generic cài Windows, không gửi repo/credential: có native Windows qua npm `npm install -g opencode-ai`, Scoop/Chocolatey và binary `https://github.com/anomalyco/opencode/releases`; trang khuyến nghị WSL nhưng request hiện Windows-native trước nên không tự chuyển WSL. Chưa tải/cài, chưa pin version; cần duyệt cài hoặc user cung cấp đường dẫn. Nếu duyệt, xác minh version/package chính thức, ưu tiên prefix thư mục kiểm thử tách biệt để không đổi npm global/PATH; package install có thể chạy lifecycle scripts, cần kiểm trước. Chỉ version/help/offline contract, không auth/model tự động.

Các câu hỏi và lựa chọn đã trình:

1. Host nghiệm thu: A đề xuất Claude Code + WindowsPowerShell thật, Codex/OpenCode/Antigravity kiểm contract/fixture và ghi unknown nếu không quan sát host; B thêm Codex integration thật, nếu cần model thì ngân sách xin riêng; C cả4host thật, phải có môi trường/quyền từng host. Không hỏi lại Windows trước/macOS Linux sau.
2. Eval: A đề xuất scorer/manifest/trace offline và auth preflight mock, không live model/credential; B chuẩn bị cả live-run Windows nhưng chỉ chạy sau duyệt corpus/permission/budget riêng, không đọc secret store hoặc bỏ isolation. Đây là quyền mới, không suy từ fan-out subagent.
3. QC: A đề xuất ultra, gồm DoD/suite/hồi quy/kiến trúc/clean-code+smoke/runtime vô hại và QC độc lập; B full không runtime; C lite chỉ vùng chạm. Chưa ghi muc_qc theo dự đoán hoặc copy request cũ.
4. Bổ sung: A không/tiếp tục; B user nói thêm. Khi trả lời, ghi nguyên văn vào brief và CLI muc_qc; scope còn thiếu mới hỏi tiếp, không tự duyệt spec/plan.

Quyết định môi trường tiếp theo — user chọn nguyên văn **“1c”**: chưa chuẩn bị/cài OpenCode lúc này; giữ nghiệm thu thực OpenCode **CHỜ**, không thay bằng fixture hoặc version/help. Vẫn giữ mục tiêu cả4host Windows nhưng không tuyên bố hoàn tất nghiệm thu tất cả khi chưa đủ evidence. Antigravity mới xác minh vị trí/version, chưa chứng minh runtime. Các host không có đường kiểm vô hại, không model/credential cũng giữ CHỜ và báo lệch; không tự tải/cài/login để đạt chỉ tiêu. Đây là fallback đã chọn, không còn câu hỏi analyze. Phase đã chuyển spec; chưa duyệt spec/plan hoặc chọn implement_mode cho request mới.

Giới hạn tra quan hệ ở phase spec: LSP đã start Python thành công và trả17tham chiếu `read_payload` dưới dạng ref opaque; truy vấn `blast_radius` trên4file `_common.py`, `search_rules.py`, `tdq_team.py`, `skill_inventory.py` không có response/progress và timeout1800s. Không tăng timeout/đổi config/lặp truy vấn rộng. Rơi xuống graphify query + đối chiếu import/caller trực tiếp; module boundary là kết quả kiểm nguồn có giới hạn, không chứng nhận semantic blast-radius đầy đủ. Chưa chạy suite/benchmark mới cho request triển khai.

Mặc định kỹ thuật để đưa spec nếu không có thay đổi phạm vi: legacy/manual approval có nhãn, không hồi tố; U06 version mới cho dependency tường minh, legacy conservative; U09 HOLD tới case cụ thể; U08 chỉ GO sau benchmark semantics/critical-path; U10 owner thiếu=unknown; U12 legacy không auto-reviewed; U13 giữ provenance/tat-ca, chỉ đổi filter nếu corpus chứng minh. Không hỏi user chọn algorithm có thể quyết từ source/test.


### Hợp đồng đo và rollout dự kiến

- Không chạy model/API hoặc đọc credential/transcript thật trong baseline/test; live-run chỉ sau quyền/corpus/permission/budget tách rõ. Không thay `bypassPermissions` bằng chế độ bỏ kiểm khác rồi gọi an toàn.
- Host thực hiện có launcher claude,codex,WindowsPowerShell,node; không thấy opencode/pwsh trong PATH qua command-v17:46. Đây chỉ là availability, không là host integration đã smoke hoặc CLI version hỗ trợ.
- Rung7vẫn cảnh báo graph cũ0phút sau extract, không gọi8/8đạt. Đồ thị dùng làm chỉ mục, mọi quyết định bám source; source/config tracked diff17:46 rỗng, không chứng minh cache/worktree sạch.
- Runtime/skill/adapter sửa theo wave, một chủ tdq_state.py và manifest; các vùng nóng dự kiến prompt_context/_common/team/eval cần khai caller/test tại spec. `tdq_test.py` có fallback trọn suite nếu radius≥0.6; không hứa đúng2lượt bất chấp tool tự chọn toàn suite, cần phân biệt explicit gate budget và fallback radius, giữ chất lượng trước thời gian.
- Không phát hành/push/update plugin cache/user-level settings hoặc đổi soul. Bump version/changelog chỉ theo scope chuẩn bị release được chốt, không tự sửa version0.71.0 trong analyze.

