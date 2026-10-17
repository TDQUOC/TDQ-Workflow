# REPORT — Đề xuất nâng cấp TDQ Workflow từ ECC toàn diện hơn
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-10-17 · Lane full · Mode main · QC yêu cầu ultra · O2
Cập nhật phê duyệt: người dùng “duyệt lệch”; CLI ghi cả #1/#2 lúc2026-10-17T17:27:04+07:00, còn0lệch chờ. Hoàn thành theo fallback được duyệt, giữ FAIL Q-I/Q-J nguyên bản và giới hạn kiểm độc lập. Các đoạn “chờ duyệt” bên dưới phản ánh thời điểm bàn giao trước phê duyệt này. Chưa có yêu cầu commit, cleanup worktree hoặc triển khai runtime.
TDQ `1d78ca86ca5b0710f357d8436ec7d9d2d7562b54` · ECC `76aaa77df6adc5b889e689007bf99b9a4f74af34`

## 1. Kết luận dễ hiểu

**TDQ nên học cách ECC làm cho quyết định có bằng chứng, không nên nhập nguyên hệ thống ECC.** Nền TDQ đã có nhiều hơn bảng đề xuất cũ gợi ra: phục hồi sau compact, eval chạy lặp, chấm trace theo thứ tự, DAG/same-file exclusion, kiểm kê skill, lazy load, nhiều adapter và phân model theo vai trò.

Bản này đối chiếu **D01–D10 và cả G1–G8**, hợp nhất thành **13 phiếu có điều kiện**. Không phải mười tám tính năng cần xây. Nhiều phiếu chỉ nên thử khi đo thấy vấn đề; một số quyết định đúng là giữ nguyên hoặc không làm.

| Quyết định | Nói ngắn gọn | Phiếu |
|---|---|---|
| **Nên làm trước** | Chỉ nhận duyệt từ đúng người/đúng gate; kiểm sản phẩm thật; bịt chỗ lệch hook và schema trên Windows | U01–U03 |
| **Củng cố có giới hạn** | Review không giả vờ đã kiểm; parser có giới hạn; hash không lẫn tiến độ; nhắc ngắn nhưng không hạ bảo vệ | U04–U07 |
| **Mở thí điểm khi có baseline** | Bàn giao bền sau compact; eval/trace tái lập; bài học có kiểm duyệt; tìm skill đúng hơn | U10–U13 |
| **Chỉ tối ưu sau đo** | Gom process cùng event; cảnh báo dependency hoặc cải tiến conflict probe | U08–U09 |
| **Giữ nguyên** | Nhỏ + quick/full, quyền chọn QC/lane/model; cấu hình inherit/override; DAG và khóa cùng file | G5/G8 và nền hiện có |
| **Không làm mặc định** | Tự học thành luật, shared writable venv/node_modules, daemon/control plane, router tự hạ model, bỏ gate sau N lần | D10, G2/G7/G8 |

**Điều có thể kỳ vọng:** ít quyết định sai nguồn; nghiệm thu trung thực hơn; dễ biết vì sao workflow lỗi; ít mất thông tin khi bàn giao. **Chưa thể hứa:** tăng chất lượng bao nhiêu %, giảm token bao nhiêu %, giảm conflict bao nhiêu % hoặc ROI tiền. Chưa có corpus/đối chứng để tính các số đó.

**Gói mở request triển khai đầu tiên:** U01 + U02 + phần coverage/schema đã tái lập của U03, dự toán **8/16/32 giờ người** thấp/cơ sở/cao. Đây là ba estimate cũ còn phù hợp, không gồm mọi host, chuyển nền tảng hoặc làm hết capability inventory. Chia thành request nhỏ có test độc lập, không triển khai tất cả 13 phiếu một đợt.

**Windows/PowerShell trước. macOS và Linux xử lý sau**, ngoài nghiệm thu hiện tại. Báo cáo này chưa sửa tính năng runtime, chưa chạy eval model thật, chưa phát hành. O1 chứa dữ liệu/lệnh/giới hạn; O3 chứa QC và kết quả kiểm cuối, không dùng lời hứa tại đây thay verdict QC.

## 2. Bản đồ hiện trạng: phần có sẵn không cần xây lại

Nguồn chi tiết và phân tầng chứng cứ: `docs/tdq/research/2026-10-17-1621-de-xuat-ecc-toan-dien.md` (O1), §2–§5. “Có code” không đồng nghĩa hiệu quả đã được đo.

| Nhóm | TDQ đã có | Học từ ECC ở đâu | Khoảng học thực / quyết định |
|---|---|---|---|
| Hooks/latency | Manifest matcher riêng, observer pre/post chịu lỗi | Dispatcher nội trình, denial rút gọn | Chỉ gom event có lợi sau đo, không xóa observer mù quáng — U07/U08 |
| Team/worktree | DAG, b-level, file exclusion, map hash, lifecycle | Digest có scope, advisory/probe | Phân biệt identity; advisory không thay DAG — U06/U09 |
| Quality/review | Ultra độc lập, DoD, suite | Outcome/skeptic, incomplete giữ unresolved | Tính trung thực acceptance/outcome — U01/U02/U04 |
| Shell | Recognition có nesting/depth và PowerShell | Bounded scanner | Budget/type/unknown, không sandbox — U05 |
| Windows/host | Python stdlib, UTF-8 helper, adapters | Executable đúng ngữ nghĩa shell | Coverage/capability theo đường gọi thực — U03 |
| G1 context | SessionStart compact anchor request/phase/plan | Suggest/PreCompact, chọn đúng worktree | Checkpoint tối thiểu có task/blocker và nguồn, không thêm hook phát hiện compact — U10 |
| G2 learning | Knowledge/rules/reminders biên soạn | Vault unreviewed, provenance, revoke; instinct riêng | Chuẩn bài học ứng viên duyệt tay, không auto-promote — U12 |
| G3 eval | 12 ca, subprocess run, score/report/sign test; **real-run CLI lấy auth qua macOS Keychain, Windows chưa dùng được theo đường đó** | Candidate identity, paired policy/receipt | Offline scorer dùng lại; auth/launcher Windows cần scope riêng U03→U11 trước live eval, không engine mới |
| G4 trace | L003/L005/L013 đã kiểm thứ tự; step_audit | Before/after + prerequisite evidence | Bổ sung missing/unknown/task scope vào scorer hiện có — U11 |
| G5 risk | Tier nhỏ + quick/full, đã có security/API/money | Ví dụ tie-breaker nhiều cỡ | **Giữ**; calibration chỉ khi có ca sai, không thêm Standard lane |
| G6 skill | Inventory nguồn, protected rows, lazy language rules | Identifier tokenization, hybrid retrieval | Đo misses, chuẩn hóa tiếng Việt trước; không chép vector engine — U13 |
| G7 sessions | Adapter mỏng, worktree, host lifecycle | Session identity/control plane ECC2 | Handoff/parity gộp U10/U03; **không xây daemon** |
| G8 role models | Inherit/high và override theo task | ECC có opus/sonnet/haiku theo role | **Giữ**; sửa capability docs qua U03 khi được giao, không tuyên bố model nào tốt hơn |

Bốn điều chỉnh quan trọng so với digest khảo sát: TDQ đã có security tie-breaker; scorer đã kiểm temporal order; ECC không toàn Sonnet; retrieval n-gram ECC không hiểu mọi từ đồng nghĩa. `effort: high` không phải mức tối đa, `inherit` không bảo đảm model mạnh nhất. Hướng dẫn TDQ nói Agent không có effort parameter đã lệch schema công cụ phiên hiện tại; phải theo capability thực từng host, không áp một luật cho mọi host.

## 3. Ánh xạ minh bạch D01–D10

Báo cáo cũ cùng ngày, slug `2026-10-17-1442-de-xuat-nang-cap-tu-ecc`, giữ nguyên để truy lịch sử; không âm thầm sửa.

| ID cũ | Xử lý mới | Lý do |
|---|---|---|
| D01 | Giữ → U01 | Quyền duyệt/nguồn tin vẫn ưu tiên số một |
| D02 | Giữ → U02 | Fixture validator không thay acceptance thật |
| D03 | Sửa phạm vi → U03 | Windows trước; gộp G7/G8 parity, không hứa mọi host/OS |
| D04 | Giữ → U04, dùng kết quả đo U11 | Ultra đã có; chuẩn evidence/outcome, không thêm reviewer vô hạn |
| D05 | Giữ → U05; schema trace ở U11 | Chia payload hook/recognition khỏi parser transcript để không đếm hai lần |
| D06 | Giữ có điều kiện → U06 | Phải replay stale, projection ngữ nghĩa không chỉ body hash |
| D07 | Giữ → U07 | Giảm thông báo không giảm quyền |
| D08 | Hoãn tối ưu tới khi đo → U08 | Nền startup có số lịch sử, critical path chưa có |
| D09 | Thử hẹp/hoãn → U09 | TDQ đã có DAG/file exclusion; chọn advisory **hoặc** probe, không full TCAS |
| D10 | Không làm shared mutable cache; hoãn feasibility | TDQ chưa có bottleneck install; estimate 2/4/8h cũ chỉ nghiên cứu consumer, không triển khai cache |

G1/G7 → U10; G2 → U12; G3/G4 → **một** U11; G6 → U13; G5/G8 giữ nền hiện có. Nhờ gộp này không tạo thêm ba engine context/trace/session trùng chức năng.

## 4. Phiếu nâng cấp

Quy ước chung: các điểm tích hợp là **dự kiến cho request tương lai**, không phải quyền sửa hiện tại. Mọi phiếu có công sức tại §5; giờ gồm code/tài liệu, test và review cơ bản, không gồm model-run/host không truy cập được. Không triển khai nếu phương án giữ nguyên đã đủ. Rollback không xóa evidence thật, không tự phục hồi trạng thái duyệt cũ hoặc nới policy.

### U01 — Duyệt đúng nguồn, đúng gate

- **Liên hệ/ưu tiên:** D01; P0. Vấn đề: text recognizer có thể nhận notification chứa “spec approved”, bỏ `1a`; TDQ đã có CLI approval/hash, không cần state machine mới. Nguồn TDQ `hooks/scripts/prompt_context.py:40-83,91-117`; ECC `workflows/orch-review.workflow.js:64-108,245-287` dạy tách outcome/evidence, không có patch provenance host sẵn.
- **Tối thiểu/điểm tích hợp:** adapter tách trusted human/system/unknown theo contract thật → parser đáp án của gate đã trình → CLI chỉ ghi khi lời người dùng thật cho phép. Log event kind/gate/schema/hash tối thiểu, không raw prompt/secret. Nếu host không có trustworthy origin, giữ manual conservative; blacklist XML không đủ.
- **Ví dụ trước → sau:** notification “spec approved” khiến nhắc ghi duyệt → chỉ được ghi “sự kiện hệ thống, không có quyền duyệt”; người dùng `1a` tại mode → map đúng danh sách đã trình, không suy `1a` luôn là approve.
- **Giữ nguyên/dependency:** agent tự phân biệt nguồn như hiện tại; rủi ro phụ thuộc mô hình còn đó. Cần khảo sát host schema trước auto-recognition; không phụ thuộc engine mới. Công 4/8/16h, duy trì §5.
- **Rủi ro/rollback:** false negative làm hỏi lại, diagnostics lộ dữ liệu; rollback adapter/parser riêng, giữ luật không cấp quyền từ notification.
- **Đo/go-no-go:** corpus human/quote/negation/system/tool/unknown cùng gate; GO khi mọi ca quyền sai nguồn không grant, câu hợp lệ ghi đúng và mutation metadata không tự approve. Không có provenance → NO-GO auto-grant, vẫn GO parser/manual fallback. Chưa có precision/recall traffic.

### U02 — Kiểm sản phẩm thật, không lấy fixture thay

- **Liên hệ/ưu tiên:** D02; P0. TDQ đã có unit validator; vấn đề thiếu artifact mà fixture xanh. TDQ `tests/test_report_kien_truc_ecc.py:211-225`; ECC review `:248-255,280-283` giữ incomplete thay approve.
- **Tối thiểu:** tách acceptance artifact bắt buộc ở QC khỏi unit validator. Thiếu bắt buộc → FAIL; ở worktree chưa tới cổng có thể SKIP rõ, không cộng SKIP vào acceptance PASS. Dùng entry point test hiện có, chưa thêm framework/cờ nếu không cần.
- **Ví dụ:** xóa report thật mà test vẫn xanh nhờ fixture → unit validator xanh nhưng acceptance đỏ; khôi phục report đúng → acceptance xanh.
- **Giữ nguyên/dependency:** QC đọc file thủ công và công khai suite không chứng minh tồn tại. Cần chốt artifact nào bắt buộc/cổng nào; độc lập U01, làm song song theo file khi triển khai. Công 1/2/4h.
- **Rủi ro/rollback:** dev đỏ trước khi sản phẩm hình thành; rollback acceptance wiring, không gắn nhãn fixture là sản phẩm thật.
- **Đo/go-no-go:** missing/malformed/valid artifact, oracle độc lập fixture. GO khi phân biệt đúng ba trạng thái và worktree chưa tới gate không bị xanh giả; chưa suy chất lượng mọi test tăng bao nhiêu %.

### U03 — Parity Windows/PowerShell và capability thật

- **Liên hệ/ưu tiên:** D03, G7/G8; P0 cho coverage/schema đã có case. TDQ có adapter/UTF-8 nhưng matcher lệch: `hooks/hooks.json:58-71,104-110`, recognition `search_rules.py:646-668`. ECC `scripts/lib/windows-bash.js:19-85` kiểm đúng launcher; Node `.cmd` patch không áp thẳng Python. O1 §3-G8 ghi tuning docs lệch effort schema.
- **Tối thiểu:** inventory host→tool→matcher→payload→recognition→observer→executable; sửa đúng đường thiếu đã tái lập, schema object ở hook boundary và capability docs theo host. Nhánh Bash chỉ chọn launcher khi cần semantics Bash, không cấm WSL hợp lệ toàn cục. Phần host rộng hơn gói P0 phải scope lại. Inventory phải ghi cả eval real-run đang dùng macOS Keychain; thiết kế auth Windows là nhánh khảo sát riêng trước U11 live-run, không nằm coverage fix P0 hoặc tự đọc tài khoản hiện tại.
- **Ví dụ:** PowerShell gọi tìm kiếm hợp lệ mà observer không ghi → cùng payload/case được nhận đúng một lần; null/[] → diagnostic/behavior có hợp đồng thay AttributeError. Effort chỉ gửi khi host hỗ trợ.
- **Giữ nguyên/dependency:** dùng Bash nhất quán, ghi hạn chế host; chưa cần host mới. Cần host Windows hiện hành và tên tool thật; schema semantics chia U05, parser transcript chia U11. Công 3/6/12h cho một host và coverage fix.
- **Rủi ro/rollback:** duplicate hook, shell đổi semantics, lộ log; rollback matcher/selector nhỏ, không đổi toàn máy. Giữ stdout protocol/stderr riêng.
- **Đo/go-no-go:** matcher và payload đầu-cuối, đường Unicode/khoảng trắng, wrong type/empty, executable đúng và duplicate count. GO khi có trace host thật và oracle; test Python driver không thay PowerShell integration. macOS/Linux ngoài nghiệm thu.

### U04 — Review có outcome và chứng cứ

- **Liên hệ/ưu tiên:** D04, dùng U11; P1. TDQ ultra đã độc lập (`skills/tdq-build/references/qc.md:34-40,73-110`); ECC `workflows/orch-review.workflow.js:220-287` tách confirmed/refuted/uncertain/unverified và dimension lỗi.
- **Tối thiểu:** chuẩn finding gồm location/scenario/evidence/verdict/giới hạn. Một lượt skeptic chỉ cho finding ảnh hưởng quyết định; verifier lỗi/null = chưa kiểm. Không nhập cứng confidence .8 hoặc vote đa số làm ground truth. Tích hợp template reviewer/QC và aggregator hiện có khi thật sự cần schema máy.
- **Ví dụ:** reviewer “không thấy lỗi” sau tool timeout → “unverified, không được dùng làm nghiệm thu”; finding bác bỏ có reproduction/source thay câu tự tin.
- **Giữ nguyên/dependency:** template evidence hiện tại + review thủ công đủ cho volume nhỏ. U02 trước để acceptance không xanh giả; U11 cung cấp corpus nếu đo tác động, không cần đợi engine mới. Công 4/8/16h.
- **Rủi ro/rollback:** correlated errors, infinite review/stuck vì false finding; cap một phản biện, giữ unresolved để quyết bằng nguồn; rollback về ultra một lượt vẫn ghi thiếu kiểm.
- **Đo/go-no-go:** corpus lỗi và case sạch do người khác gán nhãn, precision/recall/cost per confirmed issue và timeout rate. GO thí điểm nếu case lỗi verifier không approve và evidence tái lập; mở rộng chỉ sau holdout đạt guardrail user duyệt. Chưa định lượng tác động.

### U05 — Parser bounded và unknown đúng tầng

- **Liên hệ/ưu tiên:** D05; P1. TDQ recognition có depth cap (`scripts/search_rules.py:159-242`), ECC scanner budget `scripts/hooks/lib/shell-scan.js:6-12`; không bên nào nhờ đó thành shell sandbox.
- **Tối thiểu:** input length, type, cumulative work/nesting/output budget đi qua helper; kết quả recognized/not-recognized/unsupported-or-exhausted. Dùng trên search recognition; caller observer có thể bỏ ghi concept khi unknown, caller an toàn không được tự allow vì chưa hiểu. U03 sở hữu hook JSON type, U11 sở hữu transcript type; không tính lại các patch này ở U05.
- **Ví dụ:** chuỗi cực dài/nesting vượt khả năng → dừng có reason unknown, không crash hoặc tuyên bố “lệnh an toàn”. Không thực thi adversarial strings khi benchmark parser.
- **Giữ nguyên/dependency:** depth cap/timeout hiện tại nếu chưa có ca chậm; công khai giới hạn. U03 xác định shell và contract; công 4/8/16h, không gồm AST shell đầy đủ.
- **Rủi ro/rollback:** false unknown, đếm bước tốn công, regex/helper ngoài budget; rollback implementation mới nhưng giữ diagnostics/timeout và case. Không blanket fail-open security gate.
- **Đo/go-no-go:** boundary length/nesting/invalid/unicode và ordinary commands; elapsed/work-count theo oracle, output cap, mọi đường helper liên quan. GO khi không đổi decision an toàn và budget bao vùng tuyên bố. NO-GO claim “mọi regex tuyến tính/chặn mọi lệnh nguy hiểm”.

### U06 — Hash đúng mục đích

- **Liên hệ/ưu tiên:** D06/G7; P1 có điều kiện. TDQ approval body/team whole-plan hash (`tdq_state.py:569-589`, `tdq_team.py:345-396`); ECC `scripts/lib/context-carriers.js:146-170` tách identity trong descriptor proposed/inactive; `scripts/lib/context-profile-store.js:181-198,225-238` mới enforce hash/rebuild carrier trước apply/materialization.
- **Tối thiểu:** đặc tả/version assignment projection: task ID/file/dependency/contract/test; progress/header tách riêng. Approval hash giữ ngữ nghĩa được duyệt, không reuse assignment hash. Tích hợp map lifecycle hiện có sau replay legacy. Đây là thiết kế TDQ, ECC không cung cấp projection tương đương.
- **Ví dụ:** chỉ tick task → không phải phân công lại; đổi `Chạm:`/`Cần:`/test bắt buộc → map stale. Đổi sang body hash đơn thuần vẫn có tick nên chưa đủ.
- **Giữ nguyên/dependency:** reassign conservative sau mọi thay đổi; có thể tốt hơn nếu ít dùng team. Cần replay chứng minh stale dư, hiểu lifecycle và compatibility. Công 2/4/8h.
- **Rủi ro/rollback:** bỏ field có nghĩa, hash canonical drift; fail closed không parse được, schema version/migration. Rollback hash toàn file/regenerate map, không sửa approval hồi tố.
- **Đo/go-no-go:** matrix semantic vs progress edits, replay tần suất và thời gian reassign. GO khi semantic edit luôn invalidates và progress-only không; nếu không có vấn đề thực thì HOLD. Chưa đo tiết kiệm.

### U07 — Nhắc ngắn, bảo vệ không đổi

- **Liên hệ/ưu tiên:** D07/G1; P1. TDQ có reminder/breaker riêng (`search_gate.py:43-44,126-129`); ECC `gateguard-fact-force.js:1613-1634` rút denial lặp.
- **Tối thiểu:** reason code/turn/ordinal, thông điệp đầu đủ remediation; lần lặp rút gọn nhưng giữ deny/allow, thay evidence phải hiện lại chi tiết. Điểm tích hợp formatter/reminder ledger hiện có, không engine chống lặp mới.
- **Ví dụ:** ba lần cùng lý do ghi ba đoạn dài → một đoạn đầy đủ và hai dòng mã + cách phục hồi; lần thứ tư **không** tự cho qua.
- **Giữ nguyên/dependency:** giữ verbosity khi chưa thấy nhiễu thực. U01 để phân nguồn/scope turn; công 1/2/4h.
- **Rủi ro/rollback:** mất remediation hoặc che lỗi mới; giữ first/full log có minimization, rollback format, không đổi decision. Không dùng whitespace/comment stripping làm proof trivial edit.
- **Đo/go-no-go:** replay trước/sau cùng decisions, bytes/messages và khả năng phục hồi do người kiểm; token chỉ từ usage/tokenizer thật. GO khi giữ semantics và đủ recovery, không chỉ giảm chữ. Không cộng với saving U10 nếu cùng đoạn context.

### U08 — Dispatcher chỉ khi giảm đường găng

- **Liên hệ/ưu tiên:** D08; P2. Manifest TDQ Bash pre hai process, Edit pre một; ECC `.run(rawInput)` (`scripts/hooks/bash-hook-dispatcher.js:22-52,123-174`). O1/H1 có startup lịch sử, chưa có dispatcher TDQ.
- **Tối thiểu:** đo host trước, tách pure/result của đúng hai handler Bash pre → dispatcher một payload/result allow/deny/context/error, giữ order/exit/stdout/ledger. Không import mù script có sys.exit/global, không daemon.
- **Ví dụ:** Bash event spawn hai Python tuần tự → nếu đo chứng minh, một Python chạy hai handler tương đương; Edit vốn một process → không hứa tiết kiệm tại đó.
- **Giữ nguyên/dependency:** independent hooks cô lập lỗi có thể tốt hơn khi host chạy song song. Cần U03/U07 và baseline critical-path; công 4/8/16h chỉ một event.
- **Rủi ro/rollback:** blast radius chung, context protocol sai; error policy theo handler, không blanket except→allow. Rollback manifest về scripts riêng.
- **Đo/go-no-go:** corpus decision/stdout/exit/ledger tương đương, randomized end-to-end latency cold-ish/warm, p50/p95 với mẫu đủ. GO chỉ khi đường găng tốt hơn và không mất an toàn; không hơn thì bỏ. Median noop ~21ms không phải toàn 55ms observer hay % phiên.

### U09 — Advisory/probe không thay DAG

- **Liên hệ/ưu tiên:** D09; P2/HOLD. TDQ `tdq_team.py:215-312,662-898` đã DAG/same-file/probe. ECC proximity `distance.js:1-315` noisy-OR, `worktree-lifecycle/git.js:125-144` probe hiện đại.
- **Tối thiểu:** chọn **một** nhánh: advisory quan hệ chưa khai để tác giả quyết `Cần:`; hoặc capability-probed merge-tree, phân clean/conflict/error, fallback chỉ unsupported. Không tự biến mọi import thành DAG edge hoặc port full TCAS.
- **Ví dụ:** hai task file khác nhưng dùng chung interface → cảnh báo có source để tác giả quyết; Git lỗi môi trường → error, không giả clean.
- **Giữ nguyên/dependency:** explicit DAG/file exclusion/probe hiện có nếu conflict chưa đáng kể. Cần U06 cho map ổn định và corpus/case cụ thể; công 3/6/12h cho **một** nhánh, cả hai cần estimate lại.
- **Rủi ro/rollback:** false advisory mất song song, graph stale, merge-tree ghi Git objects; thử repo tạm/capability Git thật, rollback nhánh mới, giữ hard exclusion/test-before-merge.
- **Đo/go-no-go:** clean/conflict/error oracle, false advisory, đường găng và conflict lịch sử. GO thử khi tái lập nhu cầu và không nới semantics; thiếu history → HOLD. Tree proximity không phải xác suất conflict.

### U10 — Checkpoint bàn giao nhỏ trên state/plan sẵn có

- **Liên hệ/ưu tiên:** G1/G7; thí điểm P1 sau lỗi nền. TDQ `session_start.py:239-257` có anchor và X1 đã chạy thật; ECC `pre-compact.js:59-90` chọn đúng session/worktree, suggest-compact có heuristic.
- **Tối thiểu:** checkpoint **dẫn xuất**, không nguồn state thứ hai: request/phase/plan+digest, task `[~]`, blocker/chưa kiểm, next command/evidence pointer, owner/session và timestamp. Đọc nguồn được phép, phát khi resume/compact hoặc phase handoff, không mỗi tool. Adapter cần xác định đúng project/worktree; thử cap để anchor thiết yếu sống. Không tự LLM summary hoặc gợi compact theo tool-count mặc định.
- **Ví dụ:** sau nén nhớ plan nhưng quên test đang chờ → thấy “T2.1 đang làm, chưa kiểm lint, nguồn plan hash…, tiếp theo kiểm …”; checkpoint stale → nhắc đọc lại nguồn, không điều khiển ghi state.
- **Giữ nguyên/dependency:** anchor hiện có + đọc plan nếu replay đã đủ. Cần U01 nguồn tin, U06 nếu dùng assignment digest; bản tối thiểu dùng digest content hiện có không cần chờ U06. Công 3/6/12h.
- **Rủi ro/rollback:** stale/conflicting memory, secret trong blocker, cap cắt anchor; tối thiểu hóa/allowlist, nguồn thật thắng, rollback output enrichment, không xóa state.
- **Đo/go-no-go:** replay resume/compact/task complete/long path/law levels và stale cross-worktree với oracle task/next-check; chấm thiếu thông tin/chỉ dẫn sai/bytes. GO nếu khôi phục đúng, stale không tự ghi/approve, budget giữ nội dung thiết yếu; chưa có lỗi đáng kể thì giữ nền, không tuyên bố giảm % context loss.

### U11 — Một đường eval/trace tái lập, không engine mới

- **Liên hệ/ưu tiên:** G3/G4, hỗ trợ U04; P1 thí điểm. TDQ `tdq_eval.py:44-57,182-217,325-421,624-677` đã repeated run/scorer temporal; X1 đủ/đảo/thiếu/chỉ xanh phân biệt đúng, null/[] AttributeError. ECC candidate/paired policy (`ecc2/src/harness_eval.rs:185-200,488-530`), temporal prerequisite (`skill-comply/scripts/grader.py:28-140`).
- **Tối thiểu:** dùng `tdq_eval.py` hiện có: experiment manifest khóa base/candidate/corpus/check-set/host/model/quyền; CLI branch parameters có validation khi dùng; schema event/tool-result/task identity, missing/unsupported/skip tách PASS. Bổ sung oracle theo case lỗi thật; không thêm DSL trước khi hardcoded checks trở thành bottleneck, không import hooks vào scripts. Không chạy model để triển khai scorer. **Real-run Windows còn gap riêng:** `tdq_eval.py:883-899` gọi `lay_token:679-689` dùng macOS `security`/Keychain. U03 phải xác định auth/launcher contract hợp lệ, U11 tích hợp và kiểm cô lập trước live run; chưa có quyền đọc credential/chi API. Không suy scorer offline đã smoke thành live-run Windows sẵn sàng.
- **Ví dụ:** sửa policy rồi so hai nhánh hardcode cũ → manifest chỉ rõ cặp commit và check-set; thiếu result hoặc không nhận tool → unknown/missing, không “tuân thủ 100%”. Trace xanh→đỏ vốn đã bị phát hiện, không bán lại như tính năng mới.
- **Giữ nguyên/dependency:** rescore fixture và manifest thủ công nếu ít dùng. U02 trước nghiệm thu; U03 host tool naming trước mở rộng trace. Công 6/12/24h gộp parser/corpus/manifest, không cộng G3/G4 riêng.
- **Rủi ro/rollback:** rubric drift/post-hoc, false violation tool alias, đồng nhất N/A với đạt; giữ version và record cũ, validate unknown, rollback scorer theo manifest, không ghi đè raw trace. Không đọc transcript riêng không được phép.
- **Đo/go-no-go:** deterministic labeled corpus gồm ordering, prerequisite failed, missing/result/error/wrong type/tool alias/task scope; chấm lại cùng manifest phải giống. GO cho schema/oracle nếu case nhãn đúng và run không gọi API; **model eval thật chỉ sau user duyệt corpus/quyền/budget**. Chưa có holdout thì không claim precision/recall model tăng.

### U12 — Bài học ứng viên có nguồn và duyệt tay

- **Liên hệ/ưu tiên:** G2; thử hẹp P2. TDQ có `docs/tdq/knowledge/`, rules/reminders; ECC `memory-vault-format.js:5-60` unreviewed/status/provenance/secret patterns, `scripts/memory.js:60-77` context không policy. Instinct promote/prune là module khác, không nhập cùng vault thành một pipeline.
- **Tối thiểu:** dùng Markdown knowledge, metadata source request/commit/evidence, điều kiện áp dụng, candidate/reviewed/rejected/superseded, người duyệt/time/review-date; retrieval không nạp candidate như luật. Checklist manual secret/privacy và regex chỉ là phòng vệ phụ nếu có writer CLI được giao sau. Không quét transcript nền; không tự tạo skill/luật hoặc auto-promote theo confidence.
- **Ví dụ:** một lần tool lỗi → agent ghi “mọi host luôn lỗi” thành luật → nay chỉ ứng viên có scope/trace, bị từ chối hoặc duyệt phạm vi hẹp; khi nguồn thay đổi được supersede/thu hồi.
- **Giữ nguyên/dependency:** duyệt thủ công bằng template hiện tại nếu volume ít. U01 bảo đảm nguồn duyệt, U02 acceptance metadata; công 2/4/8h chỉ template/checklist/validation nhỏ, không vault/daemon/locking engine.
- **Rủi ro/rollback:** memory poisoning, lộ secret, rule creep và stale. Regex không bảo đảm sạch; allowlist nội dung, không raw prompt, không policy auto-load. Rollback retrieval/template mới, đánh dấu superseded, giữ evidence audit không secret; dữ liệu nhạy cảm xử lý theo policy riêng, không tùy tiện giữ.
- **Đo/go-no-go:** corpus synthetic secret/false lesson/stale/cross-project và manual review, đo tỷ lệ ứng viên được dùng thật/lỗi lặp/context cost. GO khi candidate không thể nới quyền/auto-load, thu hồi có tác dụng, không ghi bí mật thử nghiệm ra log. Thiếu nhu cầu → giữ manual; chưa định lượng giảm lỗi.

### U13 — Tìm skill đúng hơn trước khi tăng kho skill

- **Liên hệ/ưu tiên:** G6; thử P2. TDQ `_filter` substring casefold/protected sources (`skill_inventory.py:226-236`), B0 và lazy load đã có. ECC `context-retrieval.js:3-33,38-101` dùng token/hybrid offline, không true synonyms tổng quát.
- **Tối thiểu:** corpus query Việt/Anh/identifier với nhãn DÙNG/NỀN/KHÔNG; đo baseline, chỉ chuẩn hóa camelCase/snake_case/Unicode nếu misses thật. Giữ protected rows, nguồn và khả năng `--tat-ca`; không coi danh mục trên đĩa là quyền gọi. Không sinh triggers LLM hoặc sao BM25/vector mặc định.
- **Ví dụ:** query `buildFindUserQuery` bỏ sót mô tả “find user” → token chuẩn hóa tìm được nhưng vẫn cho biết nguồn, không tự invoke; tiếng Việt không bị tokenizer ASCII cắt hết dấu.
- **Giữ nguyên/dependency:** substring + từ khóa khác và đọc inventory đầy đủ; có thể đủ với kho nhỏ. U11 phương pháp/corpus dùng lại, nhưng có thể đo offline độc lập. Công 2/4/8h.
- **Rủi ro/rollback:** false positive nạp thừa, Unicode làm sai, cache stale; giữ provenance/protected rows, rollback filter, full inventory vẫn dùng được.
- **Đo/go-no-go:** recall@k/precision@k trên holdout, protected-source invariant, latency và bytes của inventory; review phân biệt skill được phép. GO chỉ nếu misses giảm theo nhãn mà không tăng context vô kiểm soát; nếu baseline đủ thì không thay. Không suy saving token từ bytes.

## 5. Công sức, duy trì và phạm vi bất định

Đơn vị **giờ người**, một người quen Python/TDQ và có một host Windows kiểm được. Thấp/cơ sở/cao là kịch bản kỹ thuật, không confidence interval hay báo giá. Cơ sở phân rã thành **thiết kế/triển khai/kiểm**, bao gồm review nhỏ trong kiểm. Mức cao tính thêm legacy/edge cases, mức thấp đường gọi rõ. Chưa gồm model API runs, corpus lớn gán nhãn, macOS/Linux, host mới hoặc release. Duy trì là **giờ/tháng hoạt động có chạm khu vực đó**, không cộng tự động mỗi tháng và không có dữ liệu lịch sử để bảo đảm.

| Phiếu | Thấp / cơ sở / cao | Phân rã cơ sở | Duy trì thấp / cơ sở / cao | Ngoài estimate |
|---|---:|---:|---:|---|
| U01 | 4 / 8 / 16 | 2 / 3 / 3 | .25 / .5 / 1 | Thiết kế protocol host không cung cấp provenance |
| U02 | 1 / 2 / 4 | .5 / .5 / 1 | 0 / .25 / .5 | Acceptance mọi sản phẩm tương lai |
| U03 | 3 / 6 / 12 | 1 / 2 / 3 | .5 / 1 / 2 | Mọi adapter/OS; inventory rộng phải scope lại |
| U04 | 4 / 8 / 16 | 2 / 3 / 3 | .5 / 1 / 2 | Corpus review gán nhãn lớn |
| U05 | 4 / 8 / 16 | 2 / 3 / 3 | .25 / .5 / 1 | AST/interpreter shell đầy đủ |
| U06 | 2 / 4 / 8 | 1 / 1 / 2 | .25 / .5 / 1 | Migrate mọi plan legacy không đọc được |
| U07 | 1 / 2 / 4 | .5 / .5 / 1 | 0 / .25 / .5 | Thiết kế gate mới |
| U08 | 4 / 8 / 16 | 2 / 3 / 3 | .5 / 1 / 2 | Gom mọi event/daemon |
| U09 | 3 / 6 / 12 | 1.5 / 2 / 2.5 | .5 / 1 / 2 | Cả hai nhánh/full TCAS |
| U10 | 3 / 6 / 12 | 1.5 / 2 / 2.5 | .25 / .5 / 1 | LLM summary/cross-host control plane |
| U11 | 6 / 12 / 24 | 3 / 4 / 5 | .5 / 1 / 2 | Live model eval, auth/credential Windows cần scope riêng, DSL/engine mới |
| U12 | 2 / 4 / 8 | 1 / 1 / 2 | .25 / .5 / 1 | Auto-learning/vault/daemon |
| U13 | 2 / 4 / 8 | 1 / 1 / 2 | .25 / .5 / 1 | Hybrid retrieval/LLM triggers |

Gói P0 U01–U03: **8/16/32h**, phân rã cơ sở 3.5h thiết kế +5.5h triển khai +7h kiểm =16h. Nếu U01 host provenance không có, thu hẹp sang parser/manual fallback, không dùng estimate làm lý do bịa metadata. U03 baseline vài đường thiếu không gồm kiểm mọi capability.

Không lập “tổng dự án 13 phiếu” bằng cộng bảng: U08/U09 có điều kiện, U10/U11/U12/U13 có thể không cần làm; corpus/design/inventory dùng chung. Ước lượng gói kế tiếp phải loại công giao nhau sau khi scope. Duy trì không phải tiết kiệm và không quy giờ người thành tiền/token khi không có đơn giá/dữ liệu.

## 6. Hiệu quả có thể kiểm và điều chưa biết

### Dữ liệu đã có, không phải speedup đã triển khai

- O1 X1 mới: 4 trace synthetic phân biệt ordering/missing; rỗng/malformed có `LoiThieuSo`, null/[] có `AttributeError` chưa sửa; hook startup/compact exit0 và anchor đúng. Chứng minh đường code và giới hạn, không đo chất lượng mô hình.
- O1 H1 lịch sử: Python noop median 21.346ms; observer nonconcept 54.825ms/LSP 55.887ms, n=12. p95 nearest-rank n=12 là max, không SLA. Không đo host critical path, không lấy 55ms làm toàn bộ tiết kiệm dispatcher.
- Mô hình minh họa **mới, overhead=0**, `N * k * 21.346ms`, k=1: N20→426.920ms, N50→1067.300ms, N100→2134.600ms. Trừ overhead/host parallelism thì lợi ích có thể 0 hoặc âm. Không phải bảng scenario cũ, không cộng hai bảng, không kết luận giảm phút/phiên.

### Ma trận lợi ích và cách tránh cộng chồng

| Cụm | Primary metric dự kiến | Chưa có | Không cộng chồng |
|---|---|---|---|
| U01/U02/U04 | Sai nguồn cấp quyền; acceptance false pass; confirmed/refuted/unverified đúng nhãn | Corpus độc lập/traffic | Một false approval không tính thành ba lỗi giảm |
| U03/U05/U11 | Coverage tool/payload đúng; crash/unknown; oracle trace | Host trace đủ/biên lớn | Hook JSON type ở U03, transcript ở U11, work budget U05 |
| U06/U09 | Stale dư, conflict/false advisory, đường găng | Lịch sử đủ | Chỉ tính reassign/conflict tiết kiệm một lần |
| U07/U10/U13 | Phục hồi đúng, bytes/messages, recall skill có nhãn | Baseline compact/misses | Cùng đoạn không được tính tiết kiệm hai lần; bytes không token |
| U08 | End-to-end p50/p95 event mục tiêu | Prototype/host scheduling | Process bỏ trùng observer chỉ tính một lần |
| U12 | Bài học hữu ích được duyệt, lỗi lặp và revoke đúng | Corpus/volume/thời gian theo dõi | Không quy số bài học thành chất lượng/tokens giảm |
| G5/G8 giữ nguyên | Regression intake, capability model đúng | Eval đủ để đổi cấu hình | Không hạch toán “không xây” là savings đo được |

### Thiết kế đánh giá cho request triển khai sau

1. **Chốt trước:** primary metric, oracle, corpus version/holdout, guardrail chất lượng/quyền, ngân sách và stopping condition được user duyệt. Test tuân thủ khác test chất lượng code.
2. **Đối chứng:** cùng nhiệm vụ, quyền, host/tool contract, model/version/effort và output bar. Cặp baseline/candidate cùng corpus; đổi thứ tự randomized/counterbalanced, ghi OS/cache/concurrency. Không so kết quả hai snapshot khác task như A/B.
3. **Oracle:** nhãn nguồn cấp quyền từ host contract; missing artifact bằng filesystem; temporal/tool-result nhãn deterministic; chất lượng review/skill do người kiểm độc lập. Không dùng model tự tin làm ground truth.
4. **Mẫu số:** lỗi/timeout/missing/unsupported/skip ghi riêng; N/A không thành PASS. Primary pass rate chỉ trên ca applicable định trước, đồng thời công bố coverage và missing rate toàn bộ; không bỏ ca khó hậu nghiệm.
5. **Phân tích:** sign test/paired comparison chỉ khi giả định hợp, report discordant pairs và effect size; task lặp cùng repo/session có tương quan, phải group hoặc công khai giới hạn. Tách mã thêm sau khi xem kết quả; nhiều metric không chọn thắng tùy ý.
6. **Chi phí:** giờ người, wall-clock đường găng, CPU/process count và token usage thật tách riêng. Có API run thì xin quyền/budget riêng trước; request này không chạy. Không có dữ liệu đủ → giữ thí điểm/HOLD, không bịa %.

## 7. Roadmap theo dependency và điều kiện vào/ra

Không chốt lịch phát hành/version. Đây là lộ trình đề xuất, cần request triển khai riêng và quyền tương ứng.

| Chặng | Vào | Làm / khả năng song song | Ra hoặc dừng |
|---|---|---|---|
| R0 — Baseline/contract | Windows host đang dùng, snapshot/case rõ | U01 schema nguồn; U02 artifact contract; U03 parity inventory tối thiểu, không cài mới | Reproduction + oracle + điểm chạm + estimate cập nhật; provenance thiếu thì giữ manual |
| R1 — Sửa lỗi nền | R0 có đường tái lập | U01/U02/U03 theo vùng file riêng; một chủ ghi manifest | Acceptance mất artifact đỏ; notification không duyệt; matcher/payload/tool đúng; rollback riêng từng thay đổi |
| R2 — Evidence ổn định | R1 và corpus/offline cases | U04 sau U02; U05 sau U03; U07 sau U01; U11 sau U02/U03. U06 chỉ khi replay stale cần sửa | Không mất quyền/coverage; oracle/version rõ, trace missing không PASS; không đủ dữ liệu → giữ nền |
| R3 — Thí điểm context/knowledge | R1, baseline mất context/knowledge/misses | U10 tối thiểu dùng content digest hiện có; U06 cần nếu mở assignment-aware. U12 sau U01/U02; U13 offline độc lập, dùng phương pháp U11 | Replay/holdout có lợi có giới hạn, không stale auto-write/auto-rule, protected sources giữ nguyên; không hơn thì bỏ |
| R4 — Performance/team tùy nhu cầu | U03/U07 và measured critical path cho U08; U06 + history cho U09 | U08 một event; U09 một nhánh advisory/probe, không mở full engine | Semantics tương đương và đường găng/case thật tốt hơn; không chứng minh thì NO-GO/HOLD |

Các cạnh chính: `U02→U04`; `U03→U05`; `U01→U07`; `U03+U07+baseline→U08`; `U06+history→U09`; `U02+U03→U11`; `U01+U02→U12`. U10 bản tối thiểu không phụ thuộc assignment projection mới; chỉ bản assignment-aware mới cần U06. Không vẽ dependency chỉ vì chung chủ đề.

### Backlog macOS và Linux — xử lý sau

**Ngoài nghiệm thu hiện tại**, theo yêu cầu người dùng. Không coi Python stdlib hoặc ECC ghi “cross-platform” là bằng chứng đã chạy hai OS này.

Điều kiện quay lại: Windows P0 ổn, có máy/CI và quyền kiểm host tương ứng, corpus contract đóng băng; mở request riêng xác định shell/executable/path/symlink/process lifecycle và dependency isolation. Bằng chứng cần: matcher/tool names thật, Unicode/space paths, quoting/stdout protocol, permission/process cleanup, tests/smoke với timeout, no orphan/cross-project write. Không mang mutable junction Windows sang symlink POSIX mặc định. Chi phí/ETA hai nền tảng **chưa ước tính**, không nằm 8/16/32h P0.

## 8. Những điều không làm và lý do

- Không shared writable venv/node_modules dù lock hash khớp; ABI/absolute paths/quyền ghi vẫn khác. D10 chỉ xét feasibility 2/4/8h khi consumer nặng chứng minh install là bottleneck, không phải estimate cache production.
- Không daemon Rust/SQLite/control plane/cron chỉ vì ECC2 có; TDQ host lifecycle đủ cho phạm vi hiện tại. Không ghi “tiết kiệm vài tuần” vì chưa có baseline dự án đối ứng.
- Không tự học từ transcript riêng, auto-promote instinct thành policy/skill, áp confidence như xác suất; không copy helper bỏ fcntl rồi suy an toàn Windows.
- Không thêm Standard lane, model router hay tự downgrade model; TDQ đã có policy lựa chọn. Lệch capability docs xử lý đúng host, không áp schema phiên này cho mọi host.
- Không nới gate, bỏ same-file exclusion/DAG, tự chèn mọi import làm dependency, hoặc nhả block sau vài lần lặp. Hook nhắc không trở thành deny chỉ vì “chưa duyệt”.
- Không chép code ECC đáng kể mà bỏ MIT notice; quy tắc không attribution trailer commit không miễn nghĩa vụ giấy phép. Không thêm dependency/dịch vụ/API cho báo cáo này.

## 9. Trạng thái bàn giao

**Lệch quy trình chờ duyệt #1 (Q10 trong CLI = Q-J):** lời gọi khảo sát/QC, kể cả kiểm cuối, truyền worktree isolation thừa; reviewer/kiểm cuối override opus thay inherit. Đã buộc đọc absolute repo chính, ghi lịch sử FAIL và kiểm vùng ghi/worktree; không dùng kết quả này để xóa sai thao tác. LSP trong một worktree QC đã tạo untracked pyrightconfig; worktree đó được giữ, không force cleanup. Lệnh Git của kiểm cuối bị harness chặn nên phần diff độc lập chưa có; chỉ có output leader trước đó, không chạy lại để né chặn. Người dùng chưa duyệt lệch; xem O3 §3 và `tdq_state.py lech list`. Không có quyền mặc định từ notification hoặc reviewer.

**Lệch kiểm định chờ duyệt #2 (Q9 trong CLI = Q-I):** leader đã chạy X1 thật; reviewer chỉ đối chiếu source/oracle vì harness từ chối lệnh tái lập scorer trước thực thi. Không thử lại hoặc nhờ agent khác vượt chặn; thiếu lượt tái lập độc lập theo plan. Giữ kết luận có giới hạn và xin người dùng duyệt phần thiếu kiểm này, không gọi X1 là independent QC rerun.

**Kiểm định:** ba chiều phản biện đã hoàn tất; sửa phân rã P0 và gap eval Windows/citation đã được người phát hiện tái kiểm. Kiểm cuối độc lập đạt Q-A–Q-G, nhưng trả FAIL Q-I/Q-J theo tiêu chí nguyên bản và CHỜ suite lần2/evidence Git độc lập tại thời điểm kiểm. Leader giữ nguyên verdict lịch sử đó. Suite2 sau sửa đã kết thúc17:19:57, notification completed exit0:134module, failed0, missed0,434.79s; suite1 đạt134module/failed0/435.42s. Ledger17:22:34 xác nhận2/2 lượt, radius misses0; không chạy lượt3. Q-H/QC-F1 được leader cập nhật bằng output thật, không gọi là independent rerun mới. Không có thống kê testcase/skip mới đáng tin từ output silent/log dùng chung bị ghi đè; không thay bằng số lịch sử hoặc suy skip0. Lint ba artifact17:23:28 đạt0 violations; vùng tài liệu2file0module/0.51s, không là code coverage. Bảng kết quả cuối trong O3 là nguồn quyết định; hai lệch vẫn chờ duyệt, không tuyên bố “ultra sạch hoàn toàn”.

Sản phẩm của request là O1/O2/O3 cùng brief/spec/plan và log workflow, không phải runtime mới. Các lỗi hiện hữu nêu trên chưa được sửa bởi báo cáo. Đã hoàn thành ba task chính và ba task sửa QC, đóng hồ sơ theo fallback để trình duyệt hai lệch; không tự nghiệm thu điều kiện nguyên bản còn FAIL. Kết quả lint/suite/phản biện/kiểm cuối và giới hạn nằm tại `docs/tdq/qc/2026-10-17-1621-de-xuat-ecc-toan-dien.md`. Chưa commit, push, merge hoặc phát hành trong request này; không mặc định quyền từ “duyệt plan”. Báo cáo dài hơn bản bàn giao thông thường vì phải giữ đủ13phiếu và nguồn/ước tính/điều kiện đo theo spec.

## Thời gian

Output thật của `tdq_timing.py show --transcript-dir C:/Users/admin/.claude/projects/C--Users-admin-Documents-Projects-ForAgentCode-TDQ-Workflow` lúc17:23:45, snapshot trước khi viết phần bàn giao cuối; không phải effort triển khai nâng cấp:

Request `2026-10-17-1621-de-xuat-ecc-toan-dien` · lane full · opened at 2026-10-17T16:24:58+07:00

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 0s | 0s | 1 |
| analyze | 15 min | 9 min | 1 |
| spec | 4 min | 31s | 1 |
| plan | 4 min | 4 min | 1 |
| implement | 16 min | 16 min | 1 |
| qc | 20 min | 20 min | 1 |
| report | 0s | 0s | 1 |
| **Total** | **59 min** | **54 min** | |
