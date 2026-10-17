# REPORT — Đề xuất nâng cấp TDQ Workflow từ ECC và ước tính hiệu quả
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-10-17 · Lane: full · Chế độ: main · QC yêu cầu: ultra
Nguồn: TDQ `5c8a9c22a42a59c5a2e0f2941ed92bced36e9df3`; ECC `76aaa77df6adc5b889e689007bf99b9a4f74af34`.

Báo cáo dài hơn report workflow thông thường vì đây chính là sản phẩm đề xuất chi tiết được duyệt, không phải một bản tóm tắt triển khai. Không có tính năng runtime nào được sửa hoặc phát hành trong request này.

## 1. Kết luận điều hành

**Nên học nguyên tắc của ECC, không nhập nguyên hệ thống.** TDQ đã có những nền tảng quan trọng: DAG task, chia wave chống trùng file, fingerprint approval/team, kiểm thử trước merge và QC độc lập mức ultra. Vì vậy, thay thế các phần này bằng TCAS, một engine Rust hoặc một tầng orchestrator mới chưa có căn cứ.

Thứ tự khuyến nghị:

1. **P0 — tính toàn vẹn quyết định:** chuẩn hóa nguồn tin ở cổng duyệt và nhận câu trả lời `1a`; tách kiểm artifact thật khỏi fixture validator; sửa độ phủ hook theo host/tool thực tế.
2. **P1 — độ ổn định có giới hạn rõ:** outcome/evidence của review, ngân sách parser và thông báo chặn lặp không đổi quyền; xác định đúng các loại fingerprint.
3. **P2 — tối ưu có thử nghiệm:** dispatcher theo từng event, conflict probe hiện đại và advisory dependency. Chỉ đưa vào sau khi có phép đo đường găng hoặc lịch sử đủ chứng minh lợi ích.
4. **Chưa làm:** mutable dependency symlink/junction dùng chung; trivial bypass dựa xóa whitespace/comment; thay gate bằng cảnh báo sau nhiều lần bị chặn; áp confidence 0.8 như xác suất đúng 80%; port ECC wholesale.

**Bằng chứng định lượng đã có:** Python rỗng median **21.346 ms**; observer không concept **54.825 ms**, observer LSP **55.887 ms**, mỗi loại **12 mẫu chính**. Đây là chi phí subprocess độc lập, **không** phải số đo dispatcher hay độ trễ cả phiên. Giả thuyết startup 80–150 ms trong khảo sát sơ bộ không được xác nhận trên máy này.

**Ước tính hiệu quả:** mô hình loại một process có thể tránh khoảng **21 ms thành phần startup/event**, nhưng lợi ích đường găng có thể bằng không hoặc âm nếu host đang chạy song song hoặc dispatcher thêm overhead. Chưa có dữ liệu để tuyên bố phần trăm tăng chất lượng review, giảm conflict, tiết kiệm token hoặc ROI tiền.

**Các con số công sức bên dưới là ước tính kỹ thuật, không phải đo runtime hoặc báo giá.** Một người hiểu TDQ, có môi trường Windows và một host kiểm thử hiện hành; gồm code/test/review cơ bản, không gồm điều tra host không có quyền truy cập hoặc hỗ trợ mọi adapter mới.

## 2. Đọc bằng chứng và phân biệt hiện trạng

Hồ sơ dữ liệu, lệnh tái lập và nguồn đầy đủ: `docs/tdq/research/2026-10-17-1442-de-xuat-nang-cap-tu-ecc.md` (O1). Các ID `E-*`, `M*` bên dưới trỏ về hồ sơ đó. Nguồn ECC tương đối với `C:/Users/admin/Documents/ECC`; nguồn TDQ tương đối với repo này.

| Trụ cột | TDQ đã có | Khoảng thiếu có căn cứ | Kỹ thuật ECC nên học |
|---|---|---|---|
| Hooks & Latency | Matcher riêng, observer chịu lỗi pre/post, breaker khi thiếu readiness | Một số event spawn nhiều process; nhắc lặp/đường host cần kiểm; chưa đo critical path | Dispatch in-process theo event, gom context đúng protocol, rút ngắn denial không hạ gate |
| Multi-Agent & Worktree | DAG `Cần:`, b-level, file exclusion, fingerprint và test/merge | Hash team và approval có mục đích khác; dependency không khai và merge-tree legacy cần khảo sát | Proximity advisory, identity có scope, lifecycle/outcome rõ |
| Quality & Review | QC ultra độc lập, suite và DoD | Fixture fallback có thể che thiếu artifact; outcome không xác minh cần rõ; parser duyệt thiếu provenance | Evidence/proof, skeptic có giới hạn, giữ uncertain/unverified |
| Shell Safety | Parser tìm kiếm đã xét subshell/heredoc, depth cap, hiểu PowerShell ở hàm recognition | Không thấy ngân sách tổng; parser nhận diện không phải sandbox; matcher/observer không đối xứng | Bounded scanner, trạng thái unknown, tách chuỗi dữ liệu khỏi executable command |
| Cross-Platform Stability | Python stdlib, UTF-8 helper và test Windows | Python/shell executable, path/adapter và shell-specific quoting cần kiểm theo đường gọi | Kiểm executable thật và điều kiện nền tảng, không sao chép bản vá Node không liên quan |

### Những giả thuyết đã được sửa sau khi đọc code

- **Không đúng:** mọi Edit spawn ba hook; M2 cho thấy Edit/Write pre chỉ một command, Bash pre hai, LSP query observer pre và post.
- **Không đúng:** TDQ chưa có dependency graph/fingerprint. `scripts/tdq_team.py:215-312,345-377` đã có; M6 xác nhận dependency và same-file được tách wave.
- **Không đúng:** TDQ không hỗ trợ PowerShell hoàn toàn. Matcher search_gate và hàm recognition có hỗ trợ, nhưng bash_gate và post observer không match PowerShell trong manifest này.
- **Chưa chứng minh:** TDQ có CVE giống ECC, hoặc cần venv cache. Mã Node/Windows liên quan có điều kiện riêng; repo TDQ không có manifest dependency nặng tại gốc qua kiểm tra hiện tại.
- **Không đúng cho phiên này:** notification đã làm state approved. Hook phát hướng dẫn sai nhưng leader không làm theo; các phê duyệt state chỉ được ghi từ lời người dùng thật.

## 3. P0 — Đề xuất nên mở request triển khai trước

### D01 — Cổng duyệt dựa nguồn tin và đáp án đúng hợp đồng chat

**Vấn đề và bằng chứng:** `E-Q3`, M7; `hooks/scripts/prompt_context.py:40-83,91-117`. Hàm thuần nhận `duyệt spec`/`duyệt plan`, nhưng trả false cho `1a` ở mode; chuỗi thông báo chứa “spec approved” lại được coi như duyệt. Trong phiên thực hook từng hiểu sai notification, nhưng chưa xác minh vì sao câu tiếng Việt rõ ràng bị host báo không rõ ở một số lượt.

**Học từ ECC:** phân biệt kết quả có cấu trúc và bằng chứng thay vì suy quyền từ văn bản tự do (`workflows/orch-review.workflow.js:64-108,245-287`). ECC không cung cấp sẵn bản vá host provenance cho TDQ; đây là áp dụng nguyên tắc, không phải copy giải thuật tương đương.

**Thay đổi tối thiểu/điểm tích hợp:** adapter phân loại human input/system event trước recognizer; chỉ ghi phê duyệt từ lời người dùng ở gate đang chờ. Đồng bộ parser đáp án số+chữ với danh sách đã trình (`1a` không đồng nghĩa mọi số+a ở mọi cuộc phỏng vấn). Lưu metadata tối thiểu: event kind, gate, normalized answer, kết quả, hash/schema payload; không mặc định log raw prompt/secret.

**Cơ chế đề xuất:**

```text
classify_origin(payload, host_contract)
  -> trusted_human: parse answer against the currently offered gate
  -> system/tool/background: never grant approval
  -> unknown: do not infer approval; keep context and let user clarify
```

Nguồn tin đáng tin phải do host cung cấp hoặc do đường tích hợp bảo đảm; blacklist tiền tố XML chỉ là phòng vệ phụ. Không sửa state để “khớp” nhận định của hook.

**Không làm:** giữ nhắc hiện tại và buộc agent xét người nói thủ công; đây là fallback đang ngăn lỗi trong phiên, nhưng phụ thuộc mô hình và trái hợp đồng trả lời `1a`.

**Dependency/công sức:** trước hết kiểm schema của host đang dùng; **4/8/16 giờ** thấp/cơ sở/cao, gồm hồi quy câu duyệt, phủ định, trích dẫn, notification, Unicode và mode. Chưa có schema phân biệt nguồn thì phần auto-recognition phải giữ conservative; không bịa cờ host.

**Hiệu quả:** loại được lớp false approval do nội dung notification ở đường tích hợp đã phân loại; chưa đo tỷ lệ trên traffic. Có test M7 tái lập cho sai lệch `1a`, không tuyên bố tăng precision/recall theo phần trăm.

**Rủi ro/rollback:** làm quá chặt gây hỏi lại, diagnostic lộ dữ liệu; tối thiểu hóa log và giữ đọc câu tự nhiên. Rollback recognizer/adapter nhưng giữ luật không lấy notification làm duyệt; không rollback dữ liệu approval đã có.

**Go/no-go:** GO mở request nhỏ; chỉ nghiệm thu khi human approval/negation/quotation và system completion có kết quả đúng, host provenance được chứng minh, thay đổi metadata không tự duyệt spec/plan. Không GO cho auto-grant dựa regex thuần.

### D02 — Tách artifact acceptance khỏi fixture validator

**Vấn đề và bằng chứng:** `E-Q2`, `tests/test_report_kien_truc_ecc.py:211-225`: thiếu báo cáo thật thì kiểm fixture rồi return. Validator unit test có giá trị, nhưng test đó không còn chứng minh sản phẩm tồn tại khi thiếu file.

**Học từ ECC:** verifier không chạy/null và dimension lỗi giữ unresolved, không biến thành APPROVE (`workflows/orch-review.workflow.js:248-255,280-283`).

**Thay đổi tối thiểu:** tách nhóm unit validator và acceptance artifact. Với sản phẩm bắt buộc ở QC: thiếu file là FAIL. Trong worktree phát triển chưa có artifact: có thể SKIP rõ, nhưng SKIP không được cộng thành acceptance PASS. Không thêm cờ strict mới nếu entry point QC hiện có đã phân biệt được ngữ cảnh.

**Không làm:** giữ fallback và bắt QC đọc artifact thủ công; chấp nhận rằng suite xanh không chứng minh giao file, phải nêu rõ giới hạn đó.

**Dependency/công sức:** xác định artifact là bắt buộc ở bước nào; **1/2/4 giờ** cho tách test, case thiếu/khôi phục file, đảm bảo isolated worktree không bị báo PASS giả.

**Hiệu quả:** kiểm được tính trung thực của trạng thái nghiệm thu cho artifact cụ thể; không chứng minh logic của mọi test khác đúng.

**Rủi ro/rollback:** có thể làm workflow phát triển trước khi tạo report bị đỏ; tách test thay vì mở rộng skip. Rollback thay đổi acceptance test, không phục hồi fixture fallback dưới nhãn “đã kiểm file thật”.

**Go/no-go:** GO trước các tối ưu hiệu năng; mất artifact bắt buộc phải làm acceptance đỏ, fixture validator vẫn xanh độc lập, khôi phục artifact đúng thì acceptance xanh.

### D03 — Ma trận host/tool và kiểm executable Windows đúng đường gọi

**Vấn đề và bằng chứng:** `E-W1/W2`, M2/M4; `hooks/hooks.json:58-71,104-110`. Search gate có PowerShell, post observer không có; hàm recognition PowerShell dùng được. Vì thế một đường tìm kiếm hợp lệ qua PowerShell có thể không được quan sát đầy đủ theo manifest này. Chưa đo tỷ lệ trong host thật.

**Học từ ECC:** `scripts/lib/windows-bash.js:19-46,57-85` kiểm launcher/path trước chọn Bash. `scripts/hooks/pre-bash-commit-quality.js:263-307` xử lý riêng đường `.cmd` Node; không áp bản vá đó vào mọi Python subprocess.

**Thay đổi tối thiểu:** inventory entry point theo host/tool name thực → matcher → parser → observer; thêm những matcher thật sự thiếu cùng test đầu-cuối. Setup chẩn đoán executable thực (`python3`/Python/Git Bash/WSL), chỉ chọn Git Bash khi tác vụ yêu cầu semantics Bash, không cấm WSL hợp lệ nói chung. Kiểm đường có khoảng trắng và Unicode; giữ stdout machine protocol tách stderr log. QC đã tái lập observer top-level JSON `null`/`[]` exit=1 với `AttributeError`: thêm schema/type validation và regression tương ứng trong request D03/D05, không mở rộng kết luận malformed JSON exit=0 thành mọi input đều fail-open.

**Không làm:** dùng Bash thống nhất trong phiên và ghi rõ PowerShell chưa phủ observer; giảm bề mặt lỗi nhưng làm trải nghiệm Windows lệ thuộc shell.

**Dependency/công sức:** một host Windows đang dùng và adapter được hỗ trợ; **3/6/12 giờ**. Nền tảng/host khác thêm test theo request riêng, không hứa tương thích mọi máy.

**Hiệu quả:** khôi phục quan sát và chẩn đoán đúng đường thực thi; chưa gán tỷ lệ giảm lỗi Windows. M3 chỉ kiểm khoảng trắng, không được gọi là test Unicode.

**Rủi ro/rollback:** hook chạy hai lần ở adapter đổi tên tool, chọn sai shell làm khác semantics; test matcher và payload thật trước. Rollback manifest/selector riêng, giữ helper UTF-8; không tự chỉnh cấu hình toàn máy.

**Go/no-go:** GO cho coverage fix đã tái lập; selector chỉ GO khi TDQ thật sự gọi Bash và đã chứng minh launcher sai. Không GO chỉ vì ECC có bản vá WSL/CVE.

## 4. P1 — Độ ổn định trước tối ưu

### D04 — Schema outcome/evidence và skeptic có giới hạn

**Vấn đề và bằng chứng:** `E-Q1`; TDQ đã có ultra độc lập, nên không thiếu hoàn toàn reviewer thứ hai. Khoảng học được là cách biểu diễn confirmed/refuted/uncertain/unverified và incomplete dimension. ECC `workflows/orch-review.workflow.js:263-287` dùng confidence 0.8 để bác bỏ, không chứng minh độ chính xác 80%.

**Thay đổi tối thiểu:** outcome của finding gồm location, input/state gây lỗi, evidence/proof, verdict và giới hạn; review lỗi nghiêm trọng có một lượt phản biện khác tác giả. Null/lỗi verifier là “chưa kiểm”, không “không có lỗi”. Chỉ bác bỏ khi có lập luận kiểm chứng được; chưa cần một confidence threshold mới cho TDQ. Chỉ verify finding ảnh hưởng quyết định, không spawn agent cho mọi lời khuyên.

**Không làm:** giữ QC ultra và ép ghi reason/evidence bằng template hiện có; vẫn có giá trị nếu chưa đủ volume để cần schema máy.

**Dependency/công sức:** D02 để acceptance không xanh giả; **4/8/16 giờ** cho hợp đồng, lỗi verifier, dedup đơn giản và regression; chưa gồm tạo corpus gán nhãn lớn.

**Hiệu quả/đo:** precision/recall và cost per confirmed issue trên corpus lỗi có nhãn độc lập, holdout không trùng mẫu thiết kế; hiện **chưa định lượng**. Đo token/time bằng telemetry thật nếu có, không đo từ số chữ trả lời.

**Rủi ro/rollback:** agent cùng mắc lỗi tương quan, fail-closed làm đình trệ vì false finding; đánh giá evidence và giới hạn một lượt, không nhập vô hạn chuỗi skeptic. Rollback về QC ultra một lượt, vẫn giữ unresolved và sự thật về verifier lỗi.

**Go/no-go:** thử diện hẹp; chỉ mở rộng nếu corpus cho chất lượng không giảm và chi phí chấp nhận được theo ngưỡng user duyệt ở request triển khai. Không GO cho confidence tự chấm làm oracle.

### D05 — Ngân sách parser và trạng thái không hỗ trợ

**Vấn đề và bằng chứng:** `E-S1`; TDQ `scripts/search_rules.py:159-242` có depth cap, không có chứng cứ phủ work budget tổng. ECC `scripts/hooks/lib/shell-scan.js:6-12` có `24*(L+1)+4096`.

**Thay đổi tối thiểu:** giới hạn input length, tổng bước, nesting và output; budget truyền qua helper/recursion, không reset mỗi nhánh. Parse trả `recognized / not-recognized / unsupported-or-budget-exhausted` theo mục đích caller. Search observer có thể không ghi concept khi unknown; một security gate riêng không được tự allow input chưa hiểu. Chưa xây AST interpreter hoặc cơ chế giải mã mọi PowerShell payload.

**Không làm:** giữ depth cap và timeout process, công khai parser chỉ recognition; phù hợp nếu chưa thấy input/path gây chậm nhưng không đủ để khẳng định bounded work.

**Dependency/công sức:** D03 để biết shell/entry point; **4/8/16 giờ**, giả định stdlib hiện có, benchmark parser Python và adversarial strings chỉ làm dữ liệu. Hằng số ECC là tham khảo, không chép làm bảo đảm.

**Hiệu quả/đo:** thời gian parse và bước đã tiêu trên length/nesting boundary; không tự khẳng định tuyến tính cho toàn pipeline nếu regex/helper ngoài budget. Chưa có baseline throughput parser để gán phần trăm cải thiện.

**Rủi ro/rollback:** false unknown với lệnh dài hợp lệ, chi phí đếm bước, fallback fail-open sai tầng; rollout nhận diện trước, không nới quyền shell. Rollback budget implementation về parser hiện tại kèm timeout, giữ warning unknown và test corpus.

**Go/no-go:** GO prototype trong request riêng khi boundary/timeout test được xác định; NO-GO cho tuyên bố “chặn mọi lệnh nguy hiểm” hoặc “triệt tiêu mọi ReDoS”.

### D06 — Fingerprint theo mục đích, không băm lại tiến độ

**Vấn đề và bằng chứng:** `E-T2`; approval hash bỏ header, team map hash toàn plan. Tick task vẫn nằm trong phần thân nên **không thể** sửa triệt để stale chỉ bằng đổi sang `sha256_noi_dung`.

**Học từ ECC:** `scripts/lib/context-carriers.js:146-170` tách registry/profile/compiler/plan/adapter/content digest rồi tạo carrierDigest; dòng 165 yêu cầu tái kiểm nguồn khi materialize. Học nguyên tắc định danh theo mục đích; projection assignment/progress bên dưới là thiết kế đề xuất cho TDQ, không phải thuật toán tương đương đã có trong ECC.

**Thay đổi tối thiểu:** đặc tả canonical assignment projection gồm task ID, vùng file, dependency, test/contract và schema version; tách progress checkbox/header không ảnh hưởng phân công. Approval fingerprint giữ nội dung người dùng đã duyệt; thay dependency/vùng file/test bắt buộc làm map stale. Không “ignore mọi Markdown diff”.

**Không làm:** reassign sau mọi thay đổi plan, giữ chặn conservative; có thể đủ khi team ít dùng. Cần đo stale/reassign thật trước khi ưu tiên cao.

**Dependency/công sức:** corpus plan legacy/parser và compatibility map; **2/4/8 giờ**, không phải 0.5 giờ thay hai dòng. Kiểm đường cập nhật SHA trong vòng đời map trước migration.

**Hiệu quả/đo:** số stale hợp lệ và stale chỉ do tiến độ trên replay plan; hiện chưa đo tần suất thực. Không kết luận TDQ hiện deadlock hoặc mọi tick đều bị chặn nếu chưa replay lifecycle.

**Rủi ro/rollback:** bỏ sót field làm đổi ý nghĩa nhưng hash không đổi; version projection và fail closed khi không đọc được. Rollback dùng hash toàn file/map regeneration, không thay approval hash.

**Go/no-go:** GO khi replay chứng minh invalidation dư thừa; thay mỗi field ngữ nghĩa phải stale, thay progress-only không stale; NO-GO nếu projection bỏ mất hợp đồng hoặc file zone.

### D07 — Giảm nhiễu denial, không giảm quyền bảo vệ

**Vấn đề và bằng chứng:** `E-H2/H3`; ECC rút ngắn full denial lặp, TDQ có breaker giới hạn ở missing readiness. Không có phép đo số token hoặc tỷ lệ stuck hiện tại.

**Thay đổi tối thiểu:** giữ reason code, deny/allow và remediation; dedupe theo turn/reason hoặc rút ngắn từ lần lặp, ghi ordinal/evidence thay đổi. Không tự đổi block thành reminder, không xóa thông báo cần user quyết định. Không thêm trivial edit bypass mới chỉ vì đổi ít dòng.

**Không làm:** giữ thông báo hiện có; log giúp điều tra nhưng nhiễu/context có thể tăng.

**Dependency/công sức:** D01 xác định event nguồn, giữ gate semantics; **1/2/4 giờ**. Không cần lexer đa ngôn ngữ.

**Hiệu quả/đo:** số byte/message và số lần lặp trên replay; token cần tokenizer/provider usage thật. Chưa định lượng. Không cộng lợi ích với dispatcher nếu cùng loại observer/process.

**Rủi ro/rollback:** ẩn mất lý do gốc, agent không biết đường phục hồi; lưu chi tiết qua log/first occurrence và code ổn định. Rollback format/dedupe, không đổi gate decision.

**Go/no-go:** GO rút ngắn khi ma trận quyết định trước/sau giống nhau và thông báo vẫn đủ phục hồi. NO-GO cho nhả gate sau ba lần chặn hoặc stripping whitespace/comment như proof edit vô hại.

## 5. P2 — Tối ưu chỉ khi phép đo chứng minh

### D08 — Dispatcher theo event, giữ nguyên protocol và thứ tự

**Vấn đề và bằng chứng:** `E-H1`, M1/M2. Bash pre hai process; Edit pre chỉ một. ECC dùng module `.run()` trong một process, nhưng hook TDQ đang có `sys.exit`, helper global/env và output riêng nên không thể import hàng loạt rồi gọi main một cách mù quáng.

**Thay đổi tối thiểu:** trước hết tách logic pure/result của đúng hai hook Bash pre cần gom; một dispatcher parse payload một lần, gọi từng handler có result rõ (`allow/deny/context/error`), giữ stdout protocol, stderr log và exit behavior. Không tạo daemon hoặc engine Rust. Observer pre/post không xóa mặc định vì pre bảo đảm ghi nhận LSP call thất bại.

**Không làm:** giữ independent hooks để cô lập lỗi; nếu host chạy pre song song, lựa chọn này có thể tốt hơn.

**Dependency/công sức:** D03 đo host thực và D07 giữ reason code; **4/8/16 giờ** cho adapter kết quả, regression, Windows smoke và measurement. Không gồm refactor mọi hook.

**Hiệu quả:** xem mô hình §7. Chưa có dispatcher chạy thực, không cam kết tăng 30% hoặc 50–100 ms mỗi tool. Test cả cold-ish first invoke/warm và host critical path.

**Rủi ro/rollback:** một lỗi handler làm hỏng các hook còn lại, thay thứ tự cạnh tranh ledger, cộng context sai. Không blanket `except -> allow`; error policy theo từng handler bảo vệ, đặc biệt hook deny phải giữ chính sách. Rollback manifest về script độc lập, không cần thay state format.

**Go/no-go:** chỉ GO nếu quyết định/exit/stdout/ledger tương đương trên corpus, critical path tốt hơn ở host mục tiêu và không giảm an toàn. Nếu không hơn thì NO-GO, không xây tầng dispatch để “đẹp kiến trúc”.

### D09 — Advisory dependency/lifecycle, chưa thay DAG bằng TCAS

**Vấn đề và bằng chứng:** `E-T1/T3`, M6. TDQ đã tách same-file và explicit dependency; import giữa file khác có thể chưa được tác giả khai nhưng không đồng nghĩa phải tuần tự mọi importer.

**Học từ ECC:** `distance.js` kết hợp overlap/dependency/tree qua noisy-OR; `scripts/lib/worktree-lifecycle/git.js:125-144` dùng merge-tree hiện đại. Tree proximity là heuristic, không thể chứng minh semantic conflict.

**Thay đổi tối thiểu:** cảnh báo file relation chưa khai và ghi nguồn quan hệ, để author quyết `Cần:`; không tự chèn cạnh import vào DAG. Với conflict probe, kiểm capability Git, phân biệt exit clean/conflict/error, dùng output machine-readable khi hỗ trợ; legacy fallback chỉ khi tính năng không hỗ trợ, không vì bất kỳ lỗi bất ngờ nào.

**Không làm:** tiếp tục explicit dependencies, file exclusion và probe hiện tại. Không có lịch sử merge conflict lặp thì đây có thể là phương án chi phí thấp nhất.

**Dependency/công sức:** D06 ổn định map, nguồn dependency đủ tin cậy; **3/6/12 giờ** cho một nhánh nhỏ advisory hoặc probe, không bao gồm full TCAS đa ngôn ngữ. Full TCAS sẽ cần request/scoping riêng; không dùng estimate này cho nó.

**Hiệu quả/đo:** replay task có nhãn conflict/no-conflict, thời gian probe và false advisory. Hiện chưa định lượng mức giảm xung đột; M6 chỉ chứng minh scheduler sẵn có. Đổi merge-tree có thể giảm một git spawn nhưng có thể ghi Git objects, không phải hoàn toàn “không ghi gì”.

**Rủi ro/rollback:** false dependency làm mất song song, thông báo sai nếu Git error bị coi clean. Rollback chỉ advisory/probe mới; không bỏ hard exclusion/DAG/test-before-merge.

**Go/no-go:** HOLD đến khi có lịch sử/case cụ thể; GO thử nếu tạo conflict/clean/error oracle trong repo tạm và không đổi behavior an toàn. Không tự kết luận Git version minimum từ tên cờ, phải capability probe.

### D10 — Dependency cache: chưa dùng mutable symlink/junction

**Vấn đề và bằng chứng:** `E-T4`; ECC Rust fingerprint manifests rồi liên kết thư mục dependency khi trùng hash. TDQ bỏ `node_modules/.venv` khi dọn rác, không cung cấp cache tương đương. Nhưng TDQ hiện chủ yếu stdlib và runtime host.

**Thay đổi tối thiểu được cân nhắc cho consumer nặng:** ưu tiên package-manager download cache đã có, tạo environment riêng và install theo lockfile, cache key gồm OS/arch/runtime ABI/toolchain/manifest/lock. Chỉ nghiên cứu immutable artifact hoặc copy-on-write khi measurement chứng minh install là bottleneck. Không thêm cache manager vào repo này.

**Không làm:** giữ environment độc lập/host interpreter đúng nhu cầu hiện tại; an toàn và nhẹ hơn shared writable dependency.

**Dependency/công sức:** cần consumer có dữ liệu install thật và contract cô lập; **2/4/8 giờ chỉ cho feasibility study**, không phải estimate triển khai cache production.

**Hiệu quả/đo:** `install tránh được − validate − isolate − bảo trì`; hiện chưa định lượng. Không lấy thời gian npm/venv giả để tạo ROI cho TDQ stdlib.

**Rủi ro/rollback:** shared mutable node_modules/venv làm bẩn main/agent khác, venv absolute path và native ABI; lock hash không ngăn được. Với thử nghiệm sau này, bỏ link và tạo môi trường riêng, bảo đảm không xóa target hoặc dữ liệu người dùng.

**Go/no-go:** NO-GO cho shared mutable symlink/junction mặc định. Chỉ xét lại ở consumer nặng khi cache key và quyền ghi/cô lập được chứng minh, phép đo hoàn vốn dương.

## 6. Ma trận ưu tiên và chi phí duy trì

Giờ là giờ công của một người hiểu dự án, không quy đổi tiền/token. Cột thấp/cơ sở/cao là phạm vi công sức; không phải confidence interval thống kê. Rủi ro là nhận định kỹ thuật, không xác suất được đo.

| ID | Quyết định | Giờ thấp/cơ sở/cao | Duy trì bổ sung | Vì sao xếp như vậy |
|---|---|---|---|---|
| D01 | P0, GO request riêng | 4 / 8 / 16 | Corpus host và câu duyệt khi adapter thay đổi | Có sai lệch recognizer tái lập và ranh giới quyền duyệt |
| D02 | P0, GO | 1 / 2 / 4 | Artifact acceptance cho mỗi đầu ra bắt buộc | Khắc phục false acceptance cụ thể, thay đổi hẹp |
| D03 | P0, GO coverage; selector có điều kiện | 3 / 6 / 12 | Ma trận host/tool/executable | Manifest không đối xứng, parser đã hỗ trợ một phần |
| D04 | P1, thử hẹp | 4 / 8 / 16 | Nhãn findings và corpus holdout | TDQ đã có QC độc lập, cần outcome rõ hơn là thêm agent đại trà |
| D05 | P1, prototype có giới hạn | 4 / 8 / 16 | Budget/corpus khi grammar đổi | Giới hạn công việc, không hứa shell sandbox |
| D06 | P1, cần replay stale | 2 / 4 / 8 | Version projection/map legacy | Đã có hash; tránh một fix “hai dòng” không đúng vấn đề |
| D07 | P1, format/dedupe | 1 / 2 / 4 | Reason code và recovery instructions | Giảm nhiễu nhưng giữ gate decision |
| D08 | P2, đo trước GO | 4 / 8 / 16 | Conformance handler/host protocol | Lợi ích chưa chứng minh trên critical path |
| D09 | P2, HOLD lịch sử/case | 3 / 6 / 12 | Dependency extractor/Git behavior | Không thay DAG bằng noisy-OR và không biến import thành thứ tự tự động |
| D10 | NO-GO mutable cache | 2 / 4 / 8 cho feasibility | OS/ABI/runtime/cache invalidation nếu làm sau | Repo hiện không có bottleneck dependency nặng đã đo |

**Gói ưu tiên D01–D03:** 8/16/32 giờ công theo ba kịch bản, chưa gồm discovery host ngoài quyền truy cập. Không cộng tất cả D01–D10 thành một cam kết vì D09/D10 là conditional/HOLD và có phần nghiên cứu dùng chung. Không đề xuất thực hiện gói nào trong request hiện tại.

Duy trì không quy ra “giờ mỗi tháng” khi chưa có tần suất thay host/toolchain và incident; nêu đơn vị công việc thực cần theo dõi thay vì số giả.

## 7. Ước tính hiệu quả, ROI và cách đo tiếp

### 7.1. Mô hình startup cho D08 — không phải số cải thiện thực

Từ M1, min/median/max Python rỗng là 20.906/21.346/22.459 ms. Xét giả định **một process được loại mỗi Bash pre event**, N lần liên quan, overhead dispatcher chưa đo:

| Kịch bản mô hình | N giả định | Startup tham chiếu ms | Startup tổng tránh trước overhead |
|---|---:|---:|---:|
| Thấp | 20 | 20.906 | 418.120 ms |
| Cơ sở | 50 | 21.346 | 1067.300 ms |
| Cao | 100 | 22.459 | 2245.900 ms |

N=20/50/100 là giả định workload, **không** phải số event trung bình đo từ phiên này. Min/max trong 12 mẫu không phải biên tin cậy. Tiết kiệm ròng thành phần bằng cột cuối trừ `N × overhead_dispatch`; overhead cần đo sau PoC. Nếu dispatcher tuần tự hóa hai hook vốn host chạy song song, wall-clock có thể tăng. Đây không phải ROI bảo đảm dương.

Ví dụ hòa vốn thời gian: giả định dispatcher mất 8 giờ người để triển khai và mỗi phiên tránh 1.0673 giây máy, `8×3600/1.0673 ≈ 26,984 phiên` nếu **cố tình** quy đổi một giây máy thành một giây người. Giả định quy đổi này thường sai; phép tính chỉ minh họa tại sao không nên ưu tiên một refactor lớn bằng vài mili giây startup. Nếu thời gian máy không chặn người, không có hoàn vốn giờ người từ chỉ số này. Không cộng thêm 55 ms observer vào lợi ích startup của cùng process.

### 7.2. Hiệu quả ổn định/QC

| Nhóm | Đã biết | Chưa thể nói | Phép đo tiếp |
|---|---|---|---|
| D01/D02 | Case sai có thể tái lập hoặc nguồn chỉ rõ | Tỷ lệ giảm sai approval/false acceptance toàn hệ thống | Human/system/quotation/negation corpus có nguồn tin thật; artifact bắt buộc thiếu/khôi phục |
| D03/D05/D07 | Có coverage gap và parser bounded-depth hiện có | Tăng độ an toàn bao nhiêu phần trăm, token tiết kiệm bao nhiêu | Replay host/tool; input dài/lồng/quote/encoded chỉ là dữ liệu; byte/time và token usage thật |
| D04 | Quy tắc giữ unresolved của ECC rõ | Tăng precision/recall chỉ nhờ thêm skeptic | Corpus ground truth độc lập, holdout; so precision/recall và cost/confirmed issue |
| D06/D09 | DAG và hai loại hash đã có | Giảm conflict/stale bao nhiêu phần trăm | Replay map lifecycle và lịch sử conflict có nhãn; không dùng ví dụ synthetic làm production stats |
| D10 | Nguy cơ shared writable cache rõ về cơ chế | Lợi ích install cache ở consumer chưa đo | Cài theo lock trong environment riêng, warm/cold download cache và kiểm quyền ghi |

Đối với mỗi thử nghiệm triển khai sau: ghi baseline trước, cấu hình thử sau, dữ liệu thô và phiên bản; kiểm behavior trước đo tốc độ. Lưu cả kết quả âm/không cải thiện. Không biến go/no-go thành số ngưỡng tùy ý trước khi biết nền.

## 8. Roadmap dự kiến, không phải lịch phát hành

| Giai đoạn nhãn dự kiến | Nội dung | Dependency/điều kiện vào | Điều kiện ra và rollback |
|---|---|---|---|
| v0.72.0 — correctness trước | D01, D02, phần coverage của D03 | Request riêng và spec/plan được duyệt; host schema/nguồn tin kiểm được | Corpus human/system/negation/1a đúng, artifact thiếu không xanh giả, adapter quan sát đúng; rollback riêng từng patch, giữ state thật |
| v0.73.0 — bounded stability | D05, D07; thử D04 | v0.72.0 đạt; biết đường parser/caller và có tập kiểm | Budget/unknown và deny semantics đúng, skeptic không che thiếu kiểm; rollback parser/format hoặc trở về ultra hiện có |
| v0.74.0 — identity và performance thử nghiệm | D06, PoC D08 | Replay stale có chứng cứ, trace host critical path; không phụ thuộc D04 nếu PoC không dùng review schema mới | Hash phân công không đổi vì progress nhưng đổi vì hợp đồng; dispatcher tương đương và thật sự nhanh hơn; không đạt thì bỏ D08 |
| v0.75.0 — mở rộng chỉ khi có nhu cầu | D09; cân nhắc D10 feasibility cho consumer nặng | D06/map ổn định, conflict/install history đủ; không ép làm để lấp phiên bản | Advisory/probe phân biệt clean/conflict/error; cache giữ environment độc lập; mutable shared link vẫn NO-GO |

D01/D02/D03 có thể tách patch nhỏ theo quyền truy cập, không cần chờ gom thành một release lớn. Không tự thêm cờ cấu hình, daemon, DB, registry hay engine mới nếu template/tool hiện tại đủ. Mốc nào không đạt điều kiện thì hoãn/loại nội dung thay vì phát hành cho đúng số phiên bản.

## 9. Những kỹ thuật nên loại hoặc điều chỉnh

- **Loại tự hạ deny sau số lần chặn:** số lần lặp không tạo quyền. Học rút ngắn thông báo, không học suy giảm bảo vệ.
- **Loại trivial whitespace/comment bypass đại trà:** Python indentation, directive, shebang và dữ liệu trong string làm signature lexical không đủ chứng minh hành vi giữ nguyên.
- **Loại mutable venv/node_modules symlink mặc định:** hash lockfile không ngăn ghi, không khóa ABI và không làm venv relocatable.
- **Không thay DAG/file exclusion bằng TCAS:** proximity là advisory bổ sung, không chứng cứ không xung đột.
- **Không thêm fingerprint như tính năng mới:** đã có; sửa mục đích và invalidation khi có replay xác nhận.
- **Không áp ngưỡng confidence 0.8 như xác suất:** heuristic ECC chỉ phục vụ quyết định refutation, không phải benchmark chất lượng.
- **Không port Node Windows workaround/Rust engine hoặc toàn bộ rule/skill ECC:** không cùng đường thực thi, thêm chi phí duy trì ngoài nhu cầu hiện tại.
- **Không cam kết CVE/an toàn tuyệt đối:** đây là khảo sát nội bộ snapshots, không threat assessment toàn host hoặc CVE audit hiện hành.

## 10. Kiểm định, giới hạn và trạng thái bàn giao

**Đã làm:** O1 hồ sơ bằng chứng và đo nền, O2 mười đề xuất cùng roadmap, O3 hồ sơ kiểm định độc lập. Sản phẩm chỉ Markdown; không nhập mã, không thay policy hoặc phát hành runtime.

**QC độc lập:** kiểm đủ Q-A–Q-I; một lỗi provenance D06 được phát hiện, thêm QC1.1, sửa O1/O2 và được người kiểm xác nhận lại PASS. Nguồn đúng là `scripts/lib/context-carriers.js:146-170`. Mẫu tái lập độc lập giữ đúng ledger/oracle; không ép số độ trễ phải trùng mẫu gốc. Q-G được leader ghi theo kết quả thực, không biến CHỜ thành đồng ý của người dùng.

**Kiểm hồi quy:** lượt QC-F1 đầu đạt 134 modules, `Ran 2602 tests in 480.820s`, `OK (skipped=9)`; runner 481.63s, 0 radius miss. Lượt hồi quy cuối sau sửa QC đạt `Ran 2602 tests in 480.682s`, `OK (skipped=9)`; runner 481.46s, 134 modules, không failure, 0 radius miss. Ngân sách suite 2/2 lượt. Nghiệm thu 9/9 DoD đạt, một finding tài liệu đã sửa và tái kiểm độc lập; không còn finding tài liệu mở. Lint O1/O2/O3 đã đạt 0 lỗi; vùng chạm ba tài liệu chọn 0 module, không phải bằng chứng unit coverage.

Hồ sơ QC và output quyết định: `docs/tdq/qc/2026-10-17-1442-de-xuat-nang-cap-tu-ecc.md`. Có 13 mục: 9 DoD và 4 cố định; QC-F2 không có runtime module mới, QC-F4 không sửa code. Không giả PASS cho unit module không tồn tại hoặc runtime đề xuất chưa được triển khai.

Giới hạn cố định: chỉ đo subprocess Python/observer hiện có, không triển khai dispatcher/scanner/cache/skeptic mới; corpus precision/recall, production conflict history, token telemetry và install bottleneck chưa có. Graph cũ/import LSP thiếu được bù bằng nguồn/manifest có vị trí, không suy luận phủ định. M3 gốc kiểm khoảng trắng, phép tái lập độc lập đã kiểm Unicode thật; giới hạn mẫu gốc vẫn giữ. Top-level JSON `null`/`[]` gây `AttributeError` ở observer hiện hữu; chưa sửa, không coi là regression do tài liệu. ECC code không được thực thi. Mọi proposal vẫn cần request triển khai riêng. Sai thao tác gọi QC với worktree thừa đã được ghi tại O3; agent xác nhận dùng repo chính đúng snapshot, không merge sản phẩm từ worktree và `git worktree list` sau đó chỉ còn repo chính.

**Lệch spec chờ duyệt:** không có; CLI `lech list` trả 0 item, 0 pending. Việc ghi nhận giới hạn runtime cũ không thêm quyền sửa source hoặc nới điều kiện nghiệm thu.

**Giấy phép khi triển khai sau:** nếu sao chép phần đáng kể mã ECC theo MIT, phải giữ copyright/license notice tương ứng. Quy tắc không thêm attribution trailer vào commit/PR không loại bỏ nghĩa vụ giấy phép trong mã hoặc tài liệu phân phối. Request này chỉ đối chiếu và đề xuất, không nhập mã ECC.

**Git:** chưa commit, chưa push; giữ nguyên source/runtime hai repo. Plan đã hoàn thành 3 task gốc và QC1.1; đang ở cổng bàn giao, chờ người dùng trả lời commit/chưa trước bước kết thúc nhánh request.

## Thời gian

Lệnh: `python3 scripts/tdq_timing.py show --transcript-dir C:/Users/admin/.claude/projects/C--Users-admin-Documents-Projects-ForAgentCode-TDQ-Workflow`, chạy lúc 2026-10-17T15:50:13+07:00. Đường transcript được chỉ rõ vì mặc định CLI tính sai tên thư mục trên host này và bỏ cột model; không tự ước số thay thế. Bảng dưới chép nguyên output tại thời điểm bàn giao, chưa gồm thời gian chờ người dùng trả lời cổng commit. Model time là số công cụ trích từ transcript, không phải token usage hoặc tổng chi phí tất cả agent.

Request `2026-10-17-1442-de-xuat-nang-cap-tu-ecc` · lane full · opened at 2026-10-17T14:43:20+07:00

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 8s | 4s | 1 |
| analyze | 10 min | 10 min | 1 |
| spec | 18 min | 6 min | 1 |
| plan | 5 min | 4 min | 1 |
| mode | 49s | 37s | 1 |
| implement | 13 min | 13 min | 1 |
| qc | 20 min | 20 min | 1 |
| report | 15s | 5s | 1 |
| **Total** | **1h 06min** | **55 min** | |
