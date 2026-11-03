# SPEC — Nâng cấp TDQ Workflow toàn diện từ đề xuất ECC
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-10-17 · Bản: 1.0 · Lane: full · QC: ultra
Brief: ../brief/2026-10-17-1741-nang-cap-tdq-toan-dien.md
Nguồn đề xuất: ../reports/2026-10-17-1621-de-xuat-ecc-toan-dien.md
Trạng thái: CHỜ DUYỆT — chưa cho phép triển khai runtime

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

Triển khai các sửa lỗi nền và thí điểm có điều kiện của U01–U13, làm TDQ duyệt đúng gate/nguồn, nghiệm thu sản phẩm thật, biểu diễn thiếu bằng chứng trung thực và hoạt động ổn định trên Windows. Tối ưu chỉ được bật khi đối chứng chứng minh lợi ích và không giảm chất lượng/quyền; không lấy số tính năng được viết làm chỉ tiêu.

### Trong phạm vi

- U01/U02/U03 là nền ưu tiên: approval bảo thủ, acceptance đúng checkout, payload/launcher/coverage host có hợp đồng.
- U04/U05/U07/U11: outcome có evidence, parser có budget, nhắc ngắn nhưng decision không đổi, evaluator/trace offline tái lập.
- U06/U08/U09/U10/U12/U13 đều phải được đánh giá và có quyết định có nguồn: triển khai tối thiểu, giữ nền hoặc HOLD theo §3. Không âm thầm bỏ phiếu hoặc ép xây mọi nhánh.
- Nghiệm thu native Windows cho Claude Code, Codex, OpenCode và Antigravity là mục tiêu. Phân biệt contract tĩnh, fixture, launcher availability và host-observed runtime.
- Người dùng chọn “1c”: chưa chuẩn bị/cài OpenCode; nghiệm thu thực host này CHỜ. Antigravity2.22.0 đã tìm thấy executable nhưng chưa quan sát hook runtime. Các host còn lại cũng chưa được coi PASS từ việc có launcher.
- Eval chỉ scorer/manifest/trace offline và auth preflight mock. Không đọc credential/transcript riêng, không gọi model/API trả phí. Nếu host không có đường quan sát vô hại trong quyền hiện tại, giữ CHỜ và báo lệch; không đổi thành fixture PASS.
- Fan-out khảo sát/triển khai đã được cho phép; số agent theo dependency và chủ file. Chọn implement_mode vẫn là cổng riêng sau plan, không suy ra từ quyền khảo sát.
- Cập nhật tests, contract/skill/agent docs và compatibility trong vùng thực sự thay đổi; ghi kết quả đo, limitation, rollback, quyết định GO/HOLD/NO-GO.

### NGOÀI phạm vi

- Triển khai/nghiệm thu macOS/Linux giai đoạn này; vẫn giữ CI hiện hữu cho các OS đó.
- Daemon/control plane/session router mới, shared writable venv/node_modules/cache, full TCAS, shell sandbox hoặc shell AST đầy đủ, embedding/vector/LLM retrieval, trace DSL mới.
- Auto-learning thành policy, auto-promote candidate, quét transcript nền, tự hạ model/effort, nới gate hoặc đổi soul.
- Tải/cài/đăng nhập host, sửa user-level settings/PATH/plugin cache, live model eval hoặc truy cập secret store. Quyền đọc vị trí cài đặt không cấp các quyền này.
- Bump phiên bản/phát hành/push hoặc thay luồng dev/main; commit và merge xin riêng theo workflow. ECC chỉ đọc, không nhập nguyên hệ thống ECC.

### Cơ sở bằng chứng

HEAD khảo sát TDQ1096e16; ECC76aaa77df6adc5b889e689007bf99b9a4f74af34; plugin0.71.0; Python sàn3.11, máy khảo sát3.13.15. S là nguồn tĩnh, T là test tồn tại, X là execution mới, H là số lịch sử, M là mô hình/ước lượng, ? là chưa biết. Báo cáo request trước không thay execution mới của request này.

Chưa có suite/benchmark runtime mới trong request triển khai. Setup và graph refresh ở analyze có side effect đã ghi brief; không lặp setup hoặc dọn worktree/cache để tạo vẻ sạch.

## 1b. Lộ trình

Lộ trình từ brief, đã cập nhật QC và quyết định trì hoãn OpenCode. Duyệt spec là duyệt lộ trình này, chưa phải duyệt plan hoặc mode.

| Bước/phase | CÓ-BỎ | Vì sao / skill |
|---|---|---|
| analyze — nguồn hiện tại + nhóm chuyên sâu | CÓ, đã làm | tdq-intake; phân vùng quyền/acceptance, Windows/parser, team/checkpoint, eval/knowledge/retrieval |
| Web/ECC audit mới | BỎ audit mới; CÓ tra contract host chính thức | Dùng snapshot/báo cáo đã có; đã tra cài OpenCode generic, không gửi repo; chỉ tra tiếp contract còn thiếu, không audit CVE/pricing |
| spec → plan | CÓ | tdq-spec rồi tdq-plan theo tài liệu khả dụng; hai cổng chat, không harness plan mode |
| implement theo wave, một chủ file | CÓ sau gate/mode | tdq-build; red→green, DAG và vùng file; fan-out không sửa chung hub đồng thời |
| đo U06/U08/U09/U10/U13 và no-op/HOLD | CÓ | Giữ nền khi không chứng minh được nhu cầu/lợi ích; U12 giữ thủ công nếu đủ |
| review/QC độc lập + hồi quy | CÓ | Ultra user đã chọn, gồm tdq-qc-tester độc lập; code-review/security-review/simplify đúng vùng, evidence thay vote |
| report/commit/release | CÓ report; commit/release xin riêng | tdq-build; báo cả FAIL/CHỜ/HOLD, không tự phát hành hoặc push |

## 2. Đầu ra cụ thể

Các vị trí dưới đây là điểm tích hợp, không bắt buộc tạo file mới nếu helper hiện có đáp ứng. Test cụ thể và lệnh kiểm nằm trong plan.

| # | Đầu ra | Đường dẫn/vị trí | Đo “xong” bằng |
|---|---|---|---|
| O01 | U01 approval parser/descriptor và CLI guard, fallback manual có nhãn | `hooks/scripts/prompt_context.py`, `scripts/tdq_state.py`, approval contract | Đúng nguồn/gate/snapshot; stale/sai lane/order không ghi duyệt thành công; legacy không được nâng assurance hồi tố |
| O02 | U02 unit và acceptance sản phẩm thật tách biệt | bộ kiểm báo cáo ECC hiện hữu (đường dẫn test cụ thể khai tại plan), contract QC | Thiếu/malformed/valid khác nhau; không đọc sibling/ancestor hoặc fallback fixture để xanh |
| O03 | U03 capability matrix và sửa boundary/Windows coverage | `hooks/hooks.json`, `_common.py`, launcher/adapter hiện hữu | Mỗi đường host/tool/matcher/payload/observer có trạng thái và evidence; host thật không bị thay bằng driver |
| O04 | U04 finding outcome và QC evidence semantics | `scripts/tdq_state.py`, `agents/tdq-reviewer.md`, `agents/tdq-qc-tester.md`, QC contract | Unverified/missing/timeout không thành clean PASS; evidence và execution state tách nhau |
| O05 | U05 bounded search recognition và caller semantics | `scripts/search_rules.py`, `scripts/search_replay.py`, search hooks | Recognized/not-recognized/unknown phân biệt; budget xuyên helper; unknown không cấp concept credit hoặc tự allow |
| O06 | U06 assignment digest theo mục đích hoặc giữ legacy có lý do | `scripts/tdq_team.py`, stale-map caller | Matrix semantic/progress edit đúng; phiên bản/migration rõ; approval seal và progress SHA không bị thay |
| O07 | U07 formatter thông báo lặp không đổi decision | `hooks/scripts/_common.py`, search/edit gate liên quan | Replay decision/exit/ledger giữ baseline; reason mới hiện đầy đủ, recovery còn dùng được |
| O08 | U08 baseline đường găng + quyết định dispatcher hẹp | Hook Bash pre, `scripts/context_surface.py`, hồ sơ đo request | Chỉ bật sau chứng minh tương đương và đường găng tốt hơn; không đạt thì giữ manifest riêng |
| O09 | U09 quyết định HOLD hoặc thí điểm đúng một nhánh có case | `scripts/tdq_team.py`, hồ sơ request | Mặc định HOLD do thiếu history; chỉ GO khi case cụ thể tái lập và oracle tách clean/conflict/error/unsupported |
| O10 | U10 checkpoint dẫn xuất tối thiểu hoặc giữ anchor có evidence | `hooks/scripts/session_start.py`, state/plan readers | Đúng task/next/source/worktree; thiếu/corrupt không tự ghi hoặc nhận đã xong; cap sau rewrite |
| O11 | U11 manifest/scorer/parser/record offline và preflight mock | `scripts/tdq_eval.py`, `evals/` | Cùng manifest cho kết quả tái lập; missing/result/type/task-scope không false green; không API/credential |
| O12 | U12 template/checklist/validation knowledge có provenance | `docs/tdq/knowledge/`, references conventions, validator dev tối thiểu | Candidate không thành policy; review/revoke/supersede có dấu vết; legacy không auto-reviewed |
| O13 | U13 corpus và chuẩn hóa/filter skill có điều kiện | `scripts/skill_inventory.py`, consumer inventory, corpus dev | Full description tìm trước condense; provenance/protected rows/tat-ca giữ; bật thay đổi chỉ khi holdout tốt hơn |
| O14 | Hồ sơ thực thi, QC ultra, capability/measurement và báo cáo | plan/qc/reports cùng slug, contract docs vùng chạm | Mỗi O có evidence/giới hạn; GO/HOLD/CHỜ có nguyên nhân; lệch không được tính PASS |

## 2b. Ranh giới module

Ranh giới dựa trên caller/import, không chỉ tên thư mục. LSP Python đã khởi tạo và trả tham chiếu `read_payload`, nhưng batch blast-radius timeout1800s; không chứng nhận semantic coverage đầy đủ. Đã fallback graphify và đọc/grep tên import/caller chính xác. Plan phải bổ sung radius thực khi áp dụng, không coi bảng là bằng chứng mọi caller đã kiểm.

Quan hệ đã kiểm: các hook gọi `_common.read_payload`; `_common` dùng `tdq_state`; prompt_context gọi approval hash, stop_gate gọi `qc_result_state`. Search hooks và search_replay dùng search_rules. edit_gate lazy-import guard từ tdq_team; team dùng state và tự kiểm map trong lifecycle. setup_status, skill_router, skill_tokens dùng inventory; inventory gọi condense trước filter là gap cần sửa. scripts chỉ đọc hook AST khi đo/radius, không import hook runtime.

| Module | Vùng file sở hữu | Phụ thuộc module | Đầu ra §2 |
|---|---|---|---|
| M1 quyền, hook và phục hồi | `scripts/tdq_state.py`; `hooks/scripts/_common.py`, `prompt_context.py`, `edit_gate.py`, `stop_gate.py`, `session_start.py`, `search_gate.py`, `search_observe.py`, `bash_gate.py`; các bộ kiểm state/prompt/common/search-gate/search-observe do M1 sở hữu, đường dẫn cụ thể tại plan | M2 cho recognition; M4 cho team guard; M3 cho host contract | O01,O03,O04,O05,O07,O08,O10 |
| M2 recognition bounded | `scripts/search_rules.py`, `scripts/search_replay.py`; bộ kiểm recognition/replay do M2 sở hữu, đường dẫn cụ thể tại plan | Không import M1; nhận dialect/payload đã chuẩn hóa | O05 |
| M3 host và launcher | `hooks/hooks.json`; `scripts/tdq_ten_lenh.py`, `tdq_codex_mcp.py`, `utf8_io.py`, `build_portable.py`; `.opencode/plugins/tdq-workflow.js`; `.codex-plugin/`, `.agents/plugins/`; bộ kiểm portable/Codex contract do M3 sở hữu, đường dẫn cụ thể tại plan | M1/M2 là contract được gọi; không duplicate logic | O03,O08 |
| M4 team và identity | `scripts/tdq_team.py`, `scripts/tdq_bench.py`; bộ kiểm team/conflict do M4 sở hữu, đường dẫn cụ thể tại plan | Đọc state qua M1; không writer state mới | O06,O09 |
| M5 evaluator offline | `scripts/tdq_eval.py`; `evals/`; bộ kiểm evaluator do M5 sở hữu, đường dẫn cụ thể tại plan | Đọc state/log utility M1; nhận host aliases M3 | O11 |
| M6 skill retrieval | `scripts/skill_inventory.py`, `skill_router.py`, `skill_tokens.py`, `setup_status.py`; bộ kiểm inventory/router/token do M6 sở hữu, đường dẫn cụ thể tại plan | Đọc log/state utility M1; không phụ thuộc model | O13 |
| M7 knowledge thủ công | `docs/tdq/knowledge/`; template/schema knowledge mới dưới conventions và validator dev dưới scripts nếu helper chưa đủ | Dùng approval/evidence contract M1; không auto-policy | O12 |
| M8 tích hợp, nghiệm thu và contract chung | bộ kiểm báo cáo ECC hiện hữu (đường dẫn test cụ thể khai tại plan); `scripts/context_surface.py`; `agents/tdq-reviewer.md`, `agents/tdq-qc-tester.md`; các references approval/QC/team/capability trừ file M7; hồ sơ request; `docs/kien-truc.md` nếu cần ghi quyết định mới | Các module trên; nhận patch theo wave | O02,O04,O08,O14 |

Đây là vùng sở hữu thiết kế; không phải yêu cầu sửa mọi file được liệt kê. File mới/test mới phải khai đường dẫn cụ thể trong plan, không wildcard trao quyền ghi. Không module nào cùng ghi file đã giao module khác. M1 là hub: các thay đổi U01/U04/U07/U10 vào đây tuần tự dưới một chủ file; agent có thể trả đề xuất/test độc lập, không đồng thời apply. Manifest M3 chỉ đổi sau M1/M2 ổn định; tối ưu U08 không được kéo hai module sửa manifest cùng lúc.

## 3. Cách tiếp cận & lý do

### U01 — Quyền duyệt không suy từ chuỗi trông giống lời người dùng

- Tách candidate recognition khỏi quyết định và writer. Không nội suy raw prompt vào shell command; dữ liệu duyệt không trở thành cú pháp shell.
- Descriptor gate bám active_request, target, lane/phase hợp lệ, artifact path/body hash hiện có, options thực đã trình và revision/schema. Writer xác minh snapshot mong đợi trước khi lưu, không hash file mới rồi coi là file người dùng đã nhìn thấy.
- Metadata từ chính agent, XML wrapper hoặc `role=user` không chứng thực human. Chỉ host contract cung cấp nguồn đáng tin mới được đánh dấu trusted; host không hỗ trợ dùng manual conservative và nhãn assurance, không tự grant.
- `1a` chỉ có nghĩa theo gate/options đã trình; bare letter không approve khi không có gate tương ứng. Quote, phủ định, notification, tool/agent output và unknown không tự cấp quyền.
- CLI sai lane/order/request/path/hash không “warn rồi record anyway”. Reapproval có chủ đích tại QC vẫn được hỗ trợ khi đúng artifact/context; không khóa cứng mọi approval vào phase spec.
- Dữ liệu legacy/manual vẫn đọc được, có nhãn chưa xác minh; không tự xóa hoặc nâng thành trusted. Một descriptor snapshot không phải state store thứ hai.

### U02/U04 — Sản phẩm và chứng cứ là oracle

- Unit validator được dùng fixture; acceptance đọc artifact ở đúng root checkout. Thiếu artifact bắt buộc tại cổng QC là FAIL. Chạy trước cổng có thể SKIP có lý do, không tính acceptance PASS. Không dùng sibling worktree/ancestor hoặc fixture thay file thiếu.
- Finding có location, input/scenario, evidence pointer, outcome confirmed/refuted/uncertain/unverified và giới hạn. Execution PASS/FAIL/SKIP/PENDING là trục riêng.
- Aggregator không dùng token PASS đơn lẻ làm bằng chứng, không bỏ unknown row để xanh. Giữ compatibility hồ sơ cũ bằng nhãn legacy/unverified, không sửa lịch sử để hợp schema mới.
- Reviewer lỗi/null/timeout là chưa kiểm. Một lượt skeptic cho finding ảnh hưởng quyết định; không thêm vote đa số hoặc review vô hạn. Leader chịu trách nhiệm ledger và kiểm nguồn, agent không tự ghi QC thay leader.

### U03/U05 — Boundary, dialect và budget tách tầng

- Hook JSON phải là object, fields được kiểm type trước `.get` và trước dùng path/tool/command. Empty, invalid JSON, null, array, scalar có diagnostic/decision contract theo event; không blanket exception→allow hoặc crash AttributeError. Payload không hợp lệ không sinh observe/concept/approval giả.
- Capability matrix gồm host/version, tool name, matcher pre/post, payload origin/schema, deny spelling, launcher, shell dialect, UTF-8, project/worktree resolution và evidence level. Sửa post-observer PowerShell theo case tái lập; không nhét PowerShell vào POSIX matcher rồi gọi parity.
- Dùng selector executable hiện có; đúng semantics shell, Unicode/khoảng trắng/quote path, UTF-8stdin/stdout/stderr. Không đổi PATH/global config. Adapter OpenCode không được dùng text bơm vào user-content làm bằng chứng nguồn human.
- Search parser trả recognized/not-recognized/unknown với reason unsupported/malformed/exhausted. Budget input/work/nesting/output truyền xuyên helper, không reset mỗi recursive branch; giới hạn từ corpus đo tại plan trước khi bật, có boundary tests và operational counters.
- PowerShell chỉ nhận subset đã kiểm; POSIX shlex không trở thành parser PowerShell tổng quát. Observer unknown không cấp credit; safety caller không tự allow. Readiness breaker hiện hữu là semantics riêng, không bị âm thầm thay.
- Adversarial commands chỉ là dữ liệu parser; tuyệt đối không execute để thử recognition.

### U06/U09 — Team identity không thay quyền duyệt hoặc scheduler

- Trước U06, replay một plan temp để phân biệt progress-only và semantic stale. Khi tái lập stale dư, dùng assignment projection có version cho plan dependency tường minh: task order/phase/ID/contract/test/deps/file zones/MCP/estimate và mọi field thực sự tham gia phân công.
- Progress checkbox/header dẫn xuất có thể loại chỉ khi reader hiện hành không dùng để suy dependency. Legacy implicit-prose/tick vẫn conservative, không migration mù.
- Dùng chung helper ở assign và mọi stale check/guard, parse+hash cùng snapshot; map write atomic. Unknown version/unparseable không giả current. Map/digest không phải authentication hoặc concurrency lock. Không thay approval body seal hay SHA kiểm tiến độ.
- U09 mặc định HOLD: chưa history/case đủ. Nếu trong replay phát hiện case thật, chọn đúng một nhánh advisory hoặc probe. Probe phải tách clean/conflict/error/unsupported, chỉ unsupported mới fallback; oracle dùng repo temp, không sửa HEAD/index/worktree người dùng, công khai object write nếu Git thực hiện. Advisory không tự sinh hard DAG edge.
- DAG, same-file exclusion và test-before-merge giữ nguyên. Không xây cả advisory lẫn probe để đủ phiếu.

### U07/U08 — Tối ưu sau khi khóa semantics

- Formatter nhận decision đã tính; rút gọn denial lặp theo reason/evidence/gate-task/turn, không chỉ code. Lần đầu hoặc evidence đổi hiện đủ remediation; lần sau vẫn có mã và đường phục hồi, ledger không mất tác động quyết định.
- Baseline search_gate có readiness breaker sau các denial khi stamp chưa sẵn sàng. Giữ đúng decision sequence thật đó; không hứa mọi lần đều deny, không thêm/xóa breaker dưới tên dedupe.
- U08 chỉ thí điểm đúng event Bash pre. Đo baseline host scheduling/critical path trước; số Python noop lịch sử không chứng minh lợi ích dispatcher.
- Nếu được đo hợp lệ, prototype result/effect tách stdout/exit/deny/context/order/ledger trước khi gom. So sánh paired, counterbalanced, ghi cold-ish/warm/cache/concurrency; primary metric và tập ca khóa trước candidate, không chọn metric thắng hậu nghiệm.
- Chỉ GO khi quyết định/effects tương đương, đường găng cải thiện ngoài nhiễu đo và không làm xấu tail theo guardrail đã khóa. Nếu không quan sát host hoặc kết quả bất định/không lợi: NO-GO bật dispatcher, giữ handler riêng và lưu số đo. Không daemon, không gom SessionStart background lifecycle.

### U10 — Checkpoint dẫn xuất, nguồn thật luôn thắng

- Dùng renderer nhỏ đọc state không-heal và plan bằng reader hiện hữu. Chỉ request/phase/plan+digest, task đang làm/đã giao tách nhau, owner known/unknown, pause/deviation code, next và evidence pointer được allowlist.
- Không lấy prose blocker/transcript/raw prompt làm authority; không LLM summary, không checkpoint file/state mới, không tự init/approve.
- Missing/corrupt/stale/cross-project phải nói thiếu/chưa xác minh, không “done”. Tick hoàn thành không chứng minh test đã chạy. Timestamp là thời điểm dựng checkpoint, không thời điểm nghiệm thu.
- Giữ cap anchor hiện có, kiểm cả sau absolute-path rewrite; phần nhận dạng/next thiết yếu sống trước khi cắt tùy chọn. Nếu không cải thiện replay phục hồi, giữ anchor nền với lý do.

### U11 — Củng cố scorer hiện hữu, không live auth ngầm

- Manifest versioned khóa base/candidate commit, corpus/check-set/scorer version, host/tool aliases, permission profile, model identity khi có; offline không giả có model run. Base/candidate khác corpus không được gọi paired experiment.
- Kiểm nested types và tool-result presence, invocation/result identity, ordering/prerequisite và task/plan scope. Không ghép evidence task khác, không coi missing result như command thành công; missing/unsupported/invalid/SKIP khác N/A và PASS.
- Re-score sinh record version mới trỏ raw trace bất biến, giữ scorer/manifest identity và kết quả cũ. Không overwrite lịch sử để “hết FAIL”. Cùng trace/manifest cho cùng verdict deterministic.
- Auth Windows chỉ preflight mock: credential source không khả dụng cho thông báo có nghĩa, không gọi macOS Keychain hoặc secret store. Không chạy `claude -p`, không bypassPermissions trong profile thử mới, không bỏ isolation config/plugin/HOME.
- Evaluator vẫn dev tooling theo build_portable; không tự đưa corpus/knowledge/evaluator vào release bundle.

### U12/U13 — Curation và retrieval offline tối thiểu

- U12 dùng Markdown/template/checklist nhỏ: candidate/reviewed/rejected/superseded, source request/commit/evidence, scope, reviewer/time/review-date và quan hệ thay thế. Human review là thông tin có evidence, không chỉ trường agent tự điền.
- Legacy không auto-reviewed; candidate không auto-load policy hoặc tự nới quyền. Revoke/supersede có tác dụng khi đọc. Synthetic secret dùng test, không đọc secret thật/harvest_secrets; regex chỉ lớp phụ, không bảo đảm hết bí mật. Không bulk-convert toàn kho.
- U13 khóa corpus query Việt/Anh/identifier và holdout trước filter candidate; so inventory hiện hữu. Tìm trên mô tả đầy đủ trước render condense; giữ source/provenance và xử lý cùng tên khác nguồn không âm thầm giấu bản project.
- NFC/casefold và camel/snake/acronym tokenization; bỏ dấu, kể cả đ→d, chỉ tín hiệu phụ. Chỉ bật ranking mới khi holdout giảm miss mà guardrail irrelevant/context không xấu; baseline đủ thì giữ. Protected rows và `--tat-ca` không mất, thấy trên đĩa không phải quyền invoke.
- Không embedding/API/cache engine mới. Đo bytes khác token; không tuyên bố tiết kiệm token khi chưa có tokenizer/usage thật.

## 3b. Năng lực & công cụ

Bảng kế thừa brief; DÙNG có điều kiện không tự tạo đầu ra ngoài §2. Tên skill trên đĩa không cấp quyền gọi nếu phiên không liệt kê.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | Mở/phân tích request full, đã thực hiện |
| tdq-conventions | plugin:tdq-workflow | NỀN | Đọc luật state/log/git/ngôn ngữ, không invoke trực tiếp |
| tdq-spec | plugin:tdq-workflow | NỀN | Spec và gate hiện tại |
| tdq-build | plugin:tdq-workflow | NỀN | Implement/QC/report sau gate |
| tdq-lean | plugin:tdq-workflow | NỀN | Giữ tối thiểu, không port toàn ECC |
| tdq-status | plugin:tdq-workflow | NỀN | Kiểm phase khi thiếu context |
| tdq-plan, tdq-setup, tdq-check-status | plugin trên đĩa | NỀN | Theo tài liệu/CLI; không đoán skill không được liệt kê, không lặp setup |
| plugin-authoring | built-in | DÙNG | Contract đã đọc; không áp mô hình mod TSX vào command-hook Python; chỉ phần tích hợp host đúng scope |
| code-review | built-in | DÙNG | Review patch runtime, không thay DoD |
| security-review | built-in | DÙNG | Approval provenance, shell/payload, credential boundary và evidence |
| simplify | built-in | DÙNG | Sau code chạy đúng; reuse và complexity trong vùng |
| claude-api | built-in | DÙNG | Chỉ tra contract nếu phần preflight CLI cần; không gọi model/API hoặc đổi provider |
| workflow-authoring | built-in | DÙNG | Chỉ nạp khi thực sự chọn Workflow đã được cho fan-out; direct Agent không cần Workflow |
| Các skill còn lại đã xét | plugin/user/built-in | KHÔNG | khác lĩnh vực |

LSP→graphify/grep theo loại truy vấn, fallback khi tầng hỏng đã ghi; không tăng timeout hoặc đổi config để giấu thiếu evidence. Không mem0 tool khả dụng thì ghi thiếu, không bịa lookup. Đọc-only không tạo worktree hoặc override model/effort tự ý; triển khai theo mode và hợp đồng host thật, không suy tool nào cũng có capability như nhau.

## 4. Yêu cầu bắt buộc

- Log service bật mặc định, timestamp và event/reason/schema đủ debug, có cấu hình tắt/giảm theo utility hiện có. stdout chỉ protocol/CLI output, diagnostics vào stderr/ledger đúng contract; không raw prompt/secret/transcript. Không tạo logging engine mới.
- Không placeholder/TODO stub hoặc mock trình bày như dữ liệu thật. Mỗi thành phần có unit test và failure-path riêng, chạy bằng lệnh trong plan; fixture/mock chỉ chứng minh phần được mô phỏng.
- Red→green có execution thật; không fake red hoặc blind assert. Vùng chạm và radius chạy bằng công cụ hiện có; hub có thể khiến fallback toàn suite, không né để đạt quota.
- Code theo clean-code/SOLID và rule Python/JavaScript đúng ngôn ngữ, không thêm abstraction nếu helper sẵn có đủ. Source không import tests; scripts không import hooks.
- Suite đầy đủ theo các cổng QC quy định; QC sửa lại thì chạy cổng cuối tương ứng. Không nhận kết quả suite báo cáo cũ làm của request này.
- Mỗi shared file chỉ một chủ; chủ manifest/state giữ patch theo wave, không parallel write. Không tùy tiện reset/stash/xóa dirty docs/log/graphify/worktree được giữ từ trước.
- Giữ Python sàn hiện tại và runtime stdlib; không dependency/package mới cho adapter. Không install, model-call hoặc thay global settings để test xanh.
- Tài liệu/đối thoại tiếng Việt theo doc_lang; rules, comments/docstrings và chuỗi máy theo conventions hiện hành.

## 5. Ràng buộc & rủi ro

### Ràng buộc kiến trúc phải giữ

Từ `docs/kien-truc.md:19-29,44-118`, áp những quyết định đã chốt; phần NHÁP không tự biến thành luật mới:

- “`hooks/` được gọi `scripts/`; `scripts/` **không** được import `hooks/`” — helper/caller U01/U05/U06/U10/U11 giữ một chiều.
- “`skills/` chỉ được **nhắc tên lệnh** của `scripts/`, cấm chép nội dung script vào skill” — contract docs không chứa bản implementation thứ hai.
- “Chỉ `scripts/tdq_state.py` được ghi `docs/tdq/state.json`; mọi nơi khác chỉ đọc qua CLI.” — descriptor/map/checkpoint không mở state writer khác; pure helper nội bộ dùng reader không-heal đã có.
- “File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/`” — ngoại lệ adapter host theo quyết định2026-09-21; tests giữ ở tests theo tầng hiện hữu.
- “`tests/` gọi được vào mọi tầng; không tầng nào được import `tests/`.”
- “hook chỉ nhắc và kiểm bằng hiệu ứng thật, không trả `deny` vì lý do 'chưa duyệt'.” — CLI approval validation không trở thành hook deny chỉ do thiếu duyệt.
- QC có các cổng full-suite, radius fallback và ngân sách hiện hữu; R14 đo/fallback trước duyệt; QC level do người dùng chọn. Không giảm ultra vì môi trường thiếu.
- Adapter mỏng dùng chung nguồn skills; release/dev filtering giữ. Request mở/gộp theo nhánh gốc đã user chọn, không tự đổi mô hình nhánh hoặc publish main.

Không cần model mới cho sản phẩm offline. Không download/install mới trong quyền hiện tại; OpenCode không pin/cài phiên bản vì user đã trì hoãn. Antigravity2.22.0 availability không phải integration evidence. MIT code substantial nếu thực sự sao chép phải giữ license; commit không attribution không miễn nghĩa vụ license.

| Rủi ro | Ảnh hưởng | Cách giảm / rollback |
|---|---|---|
| Host không có trustworthy origin | False approval hoặc không nhận lời hợp lệ | Manual conservative có nhãn, không tự chứng thực; rollback recognizer không khôi phục quyền cũ |
| Descriptor/current artifact lệch snapshot | Duyệt thứ chưa trình | Bind expected snapshot/options; stale bị từ chối, trình lại đúng gate |
| Schema evidence làm hồ sơ cũ đỏ | Mất compatibility hoặc sửa lịch sử | Legacy/unverified rõ, không tự biến PASS cũ thành verified; giữ record cũ |
| Budget/parser dialect quá hẹp | False unknown hoặc loop gây chậm | Corpus ordinary+adversarial, work counters/boundary; unknown không safety allow |
| Projection bỏ field có nghĩa | Map current giả, phân công sai | Schema version + mutation matrix + legacy conservative; rollback whole-file/reassign |
| Dispatcher gom fault boundary | Đổi deny/order/latency tail | NO-GO mặc định trước benchmark, equivalence oracle, rollback manifest riêng |
| Checkpoint stale hoặc có dữ liệu nhạy cảm | Hướng dẫn sai, lộ dữ liệu | Allowlist, nguồn thật thắng, cap sau rewrite; rollback enrichment không xóa state |
| Eval/report tái chấm ghi đè | Không tái lập, false green | Manifest/raw identity bất biến và record version mới |
| Retrieval/knowledge thành policy tự động | Poisoning, context phình, nới quyền | Candidate manual, provenance/protected rows, holdout, revoke; không auto-invoke |
| LSP timeout, graph thiếu cạnh, host CHỜ | Không đủ chứng minh nghiệm thu | Fallback nguồn/caller, ghi giới hạn; không chứng nhận full blast-radius hoặc host PASS |

## 6. QC & Definition of Done

Mức ultra theo lựa chọn “1c 2a 3a 4a”. §6 chỉ giữ điều kiện, không giữ lệnh kiểm. Các giới hạn parser/metric mẫu đo được sẽ được khóa trong plan trước candidate; không có SLA hay phần trăm speedup tự suy từ số lịch sử.

| # | Hạng mục kiểm | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |
|---|---|---|---|---|
| Q-A | O01 quyền/gate | Corpus human/quote/negation/system/tool/unknown và options đúng gate; sai nguồn/stale/sai lane/order không ghi approval; reapproval hợp lệ tại QC và manual assurance đúng | S: prompt_context ghép prompt, CLI còn warn rồi ghi; chưa corpus execution mới | Sửa guard/parser; host thiếu nguồn tin dùng manual conservative, không auto-grant; lỗi quyền chưa sửa giữ FAIL |
| Q-B | O02 acceptance | Unit fixture tách acceptance; missing bắt buộc FAIL, malformed FAIL, valid đúng root PASS; sibling/ancestor không cứu; SKIP trước gate không cộng đạt | S: resolver/fallback fixture hiện có | Giữ acceptance đỏ đến khi sản phẩm thật đạt; không tạo fixture cứu, không thêm scope artifact tương lai |
| Q-C | O03 capability/Windows | Matrix host/tool/matcher/schema/observer/launcher có evidence level; payload lỗi không crash/credit giả; Unicode/quote/UTF-8 và duplicate behavior đúng contract | S: post-observer thiếu PowerShell; X availability claude/codex, Antigravity2.22.0; OpenCode chưa tìm thấy trong phạm vi kiểm | Sửa đường tái lập trong quyền; host không quan sát giữ CHỜ/lech, không cài/login hoặc lấy driver làm PASS |
| Q-D | O04 outcome/evidence | Confirmed/refuted/uncertain/unverified không lẫn execution; evidence thiếu/timeout/null không clean PASS; legacy có nhãn; finding quyết định có phản biện và evidence độc lập | S: qc_result_state chủ yếu đọc token, chưa kiểm evidence | Giữ unresolved/FAIL/CHỜ, sửa aggregator/template; không dùng đa số hoặc tự tin thay bằng chứng |
| Q-E | O05 parser | Type/input/work/nesting/output được bound xuyên đường tuyên bố; ordinary đúng oracle, unsupported/exhausted là unknown; caller không cấp quyền/credit từ unknown | S: depth cap có sẵn, cumulative budget và PowerShell grammar còn gap; chưa đo throughput mới | Khóa subset/corpus/budget đo tại plan trước bật; chưa bao phủ thì không claim bounded toàn parser và giữ FAIL vùng chưa sửa |
| Q-F | O06 identity | Progress-only và semantic mutation phân biệt đúng; order/deps/files/test/contract thay đổi làm stale; legacy/unparseable/version lạ conservative; mọi caller cùng helper | S: raw whole-file plan_sha trong assign/lifecycle, chưa replay mới | Giữ whole-file/reassign cho legacy hoặc vùng chưa đủ projection; HOLD optimization, không đổi approval/progress hash |
| Q-G | O07 reminder | Replay decision/exit/order/effects khớp baseline kể cả breaker; first/new-reason đủ remediation, repeat ngắn hơn mà còn recovery | S/T: reminder dedupe và readiness-breaker tồn tại; chưa đo bytes mới | Giữ formatter cũ nếu mất remediation/lợi ích; sửa semantics regression trước nghiệm thu |
| Q-H | O08 dispatcher | Protocol/effects tương đương, paired host measurement chứng minh giảm đường găng ngoài nhiễu và không hại tail theo guardrail khóa trước; không gộp event ngoài scope | H: noop median21.346ms, observer khoảng55ms, mẫu12 chỉ lịch sử, chưa host critical-path/prototype | NO-GO bật dispatcher nếu thiếu host trace/lợi ích/equivalence; giữ hooks riêng, báo số đo và quyết định, không hứa speedup |
| Q-I | O09 team advisory/probe | HOLD có lý do thiếu nhu cầu hoặc đúng một nhánh có reproduction/oracle, không giả error thành clean; DAG/file exclusion/test-before-merge giữ | S: đã có DAG/probe; chưa history/case nhu cầu mới | HOLD như baseline; không triển khai thêm nhánh để đủ tính năng, không nới hard guard |
| Q-J | O10 checkpoint | Replay resume/compact/long-path/ultra/missing/corrupt/stale/cross-worktree trả task/next/source đúng; đọc không-heal; cap output cuối không cắt thông tin thiết yếu | S: anchor hiện có cap160lines/8200chars trước rewrite; chưa replay mới sau sửa | Giữ anchor nền hoặc giảm field tùy chọn; không state/checkpoint writer mới, không giả hoàn tất |
| Q-K | O11 offline evaluator | Corpus nhãn deterministic đúng ordering/prerequisite/result-presence/type/alias/task scope; cùng manifest tái lập; record mới không ghi đè; preflight mock không truy cập secret/API/model | S: scorer temporal đã có, nested type/result-presence/rescore có gap; chưa chạy corpus request mới | Sửa scorer/validation; giữ missing/unsupported/unverified; không chạy live để bù evidence hoặc tuyên bố Windows live-ready |
| Q-L | O12 knowledge | Synthetic candidate/false lesson/stale/cross-project được phân loại; candidate/legacy không auto-policy; review/supersede/revoke có provenance; log không chứa synthetic secret | S: knowledge Markdown hiện hữu, chưa schema provenance thống nhất | Giữ manual template/checklist, không bulk migration/writer/auto-learning; thiếu duyệt giữ candidate |
| Q-M | O13 retrieval | Baseline/holdout khóa trước; full description không mất match do condense; Unicode/identifier đúng nhãn; provenance/protected/tat-ca invariant, candidate chỉ bật khi cải thiện miss không xấu guardrail | S: condense trước filter, dedup name có thể giấu nguồn; chưa corpus score mới | Giữ filter/ranking nền và full inventory; chỉ ship phần sửa được corpus chứng minh, không claim hiểu mọi từ đồng nghĩa |
| Q-N | O14 hồi quy/kiến trúc | Suite vùng/radius và các cổng full thực chạy; không regression chưa giải quyết; luật import/state/adapter/release/language giữ; reviewer độc lập nêu coverage/giới hạn | T/H: CI3OS×Python3.11/3.13 tồn tại, suite request cũ không là execution mới | Sửa trong vòng QC cho phép; còn lỗi ghi FAIL/lech, không gọi ultra sạch; OS ngoài phạm vi không claim đã chạy |
| Q-O | O14 smoke/runtime ultra | Mỗi lượt smoke và runtime vô hại kết thúc trong120giây, exit/effects đúng, không API/credential hoặc app/config mutation trái quyền | M: cap120giây/lượt từ qc.md của ultra; baseline request mới chưa chạy, biên thời gian chưa biết; cap là safety limit không dự báo runtime | Timeout là FAIL; không tự nâng cap, thu gọn ca độc lập vẫn đủ oracle hoặc giữ FAIL/lech; quyền mới chỉ xin tại cổng thích hợp |
| Q-P | O03/O14 nghiệm thu host | Claude Code/Codex/OpenCode/Antigravity có observation runtime đúng từng contract, không dùng presence/version/payload giả thay; kết quả hiện thiếu phải hiện rõ CHỜ | X: chỉ availability đã kiểm, chưa acceptance runtime; OpenCode user chọn trì hoãn, Antigravity chưa launch | OpenCode CHỜ đã được chọn; host khác thiếu đường no-cost cũng CHỜ/lech. Tiếp tục các đầu ra đủ điều kiện, báo hoàn thành có giới hạn, tuyệt đối không full-host PASS |

### Điều kiện tuyên bố hoàn thành

- Mọi O trong §2 có artifact/evidence hoặc quyết định HOLD/NO-GO đúng contract. HOLD có điều kiện không phải code đã triển khai và không tự đồng nghĩa PASS runtime.
- Các sửa lỗi quyền, acceptance, parser/scorer và regression có test execution thật; không tồn tại false approval/false acceptance được che bằng fallback.
- Hồ sơ phân biệt đạt triển khai offline, kiểm contract/fixture và nghiệm thu host thực. Chỉ khi từng host có evidence thực mới được nói nghiệm thu toàn bộ host; lựa chọn trì hoãn OpenCode không miễn yêu cầu trung thực này.
- Mọi threshold/cap trượt áp dụng fallback đã chọn, ghi lệch với bằng chứng, báo người dùng ở report; không dừng giữa implement để hỏi lại ngưỡng và không âm thầm đổi spec.
- Nếu còn CHỜ/FAIL/lech, report giữ trạng thái đó và xin duyệt lệch; không gọi hoàn tất ultra sạch. Không dùng hồ sơ request trước hoặc source tĩnh để lấp execution còn thiếu.
- Không cộng trùng lợi ích giữa reminder/checkpoint/retrieval hoặc các phiếu; thời gian người, wall-clock, bytes và token được phân biệt. Không có số đo thì không công bố phần trăm tiết kiệm/chất lượng tăng.

## 7. Câu hỏi còn mở
