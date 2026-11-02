# Yêu cầu — Eval chất lượng skill và plugin
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay duyệt mở request áp dụng cả 5 việc vào tdq

User đã duyệt phạm vi năm đề xuất trong chat, yêu cầu mở request mới cho TDQ Workflow:
1. Yêu cầu kế hoạch eval khi tạo hoặc sửa hành vi skill/hook; phân biệt thay đổi hành vi với sửa tài liệu thuần túy.
2. So sánh baseline/candidate cùng điều kiện, có lặp và cân bằng thứ tự; hỗ trợ có/không có skill mục tiêu khi phù hợp.
3. Đo riêng kích hoạt đúng, hoàn thành đúng, token/chi phí/thời gian/retry và số lần người dùng phải chỉnh.
4. Ghi nhận, chấm và báo cáo riêng theo model/host; thiếu chứng cứ là chưa kiểm, không suy thành PASS.
5. Dùng kết quả để đề xuất giữ, rút gọn hoặc bỏ luật; cùng chất lượng nhưng ít chi phí hơn vẫn có giá trị.

Hướng đã chốt: mở rộng `scripts/tdq_eval.py`, tái dùng corpus/scorer/manifest đã có, không dựng framework mới. User đã bỏ thí nghiệm Ponytail `full` so với `ultra`; mặc định Ponytail giữ `ultra`, không dùng kết quả Eval để tự đổi lựa chọn này.

Nguồn tham khảo: file báo cáo video do user cung cấp và tài liệu chính thức Anthropic đã đối chiếu trong lượt phân tích trước. Các số liệu doanh nghiệp trong file chưa xác minh không dùng làm tiêu chí nghiệm thu TDQ.

Request trước `2026-11-01-1045-toi-uu-bon-hang-muc`: 13/13 task đã hoàn thành và code đã phát hành đến 0.85.1, nhưng metadata vẫn phase implement do 11 worktree cũ dirty. D7 là các commit do chính phiên này tạo theo yêu cầu user, không phải bằng chứng agent lạ. Không xóa worktree, không giả đóng guard, không ghi đè state trước khi lưu checkpoint và chốt pipeline.

Pipeline full đã chọn bằng “1a”. Chưa quyết định: phạm vi áp dụng gate, model/host ban đầu, ngân sách live eval, corpus/holdout, rubric chất lượng và ngưỡng quyết định. Chưa cấp quyền mặc định cho một loạt phiên LLM trả phí hoặc release/push của request mới.

## Hiểu & kiến thức

Đã init request mới từ checkpoint cũ sau khi user chọn full. Nhánh `codex/eval-chat-luong-skill`, gốc `dev`, BASE `8da67529e13afe0045bc39934b58b4bd8309e760`, phase analyze. Không sửa source trong lượt này.

### Năng lực dùng được

Kiểm kê 2026-11-01: scanner có 29 skill trên đĩa, bộ lọc giữ 11 TDQ và ẩn 18 skill; đã xét thêm catalog built-in trong context.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / lý do |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | Mở request, khảo sát và phỏng vấn |
| tdq-setup | plugin:tdq-workflow | NỀN | Preflight LSP/Graphify; không lấy smoke thay module-effect proof |
| tdq-conventions | plugin:tdq-workflow | NỀN | State, tài liệu, ngôn ngữ, working log |
| tdq-check-status | plugin:tdq-workflow | NỀN | Đọc checkpoint request trước khi init |
| tdq-spec | plugin:tdq-workflow | NỀN | Spec sau khi chốt đầu vào |
| tdq-plan | plugin:tdq-workflow | NỀN | Kế hoạch có eval/DoD và duyệt riêng |
| tdq-build | plugin:tdq-workflow | NỀN | Triển khai/QC sau duyệt plan |
| tdq-lean | plugin:tdq-workflow | NỀN | Tái dùng bộ đo, giữ giải pháp đủ nhỏ |
| skill-creator | built-in | DÙNG | Rà soát thay đổi skill: scope, trigger, invariants, forward-test độc lập và validator không thay eval |
| archify | local installed | DÙNG | Preview workflow planned cho spec, native validate/render/bind và kiểm browser |
| Các skill còn lại trên đĩa và built-in không liên quan | user/plugin/built-in | KHÔNG | Khác lĩnh vực; chưa chọn HTML/browser report nên chưa dùng browser-test |

### Khảo sát code và vùng ảnh hưởng

Python 3.13.15, pytest 9.1.1, xdist 3.8.0; plugin nguồn 0.85.1. CLI `claude.exe` và `codex.ps1` hiện diện trên Windows; chưa kiểm auth/model bằng một phiên live và chưa gọi model.

| Vùng file chạm dự kiến | Lớp tìm kiếm | Tác động & quan hệ |
|---|---|---|
| scripts/tdq_eval.py | Grep + Graphify depth2; LSP thử nhưng process exited | chay_phien → chay_va_cham → callback chay; CLI setup/run/score/report, parser, chi phí, manifest và report |
| tests/test_tdq_eval.py, tests/test_eval_manifest.py | Grep | Oracle và fixture cho scorer, paired identity, rescore append-only, offline preflight; không gọi model |
| evals/tuan-thu, evals/tdq-upgrade-offline.json | Read/Grep | Corpus hành vi cũ và golden offline; không coi fixture là lần model thực thi |
| skills/tdq-intake, tdq-spec, tdq-plan, tdq-build và reference QC | Read/Grep | Khai báo thay đổi cần eval, khóa kế hoạch trước chạy, kiểm evidence và báo cáo; chưa có gate giá trị skill bắt buộc |
| scripts/tdq_state.py, scripts/doc_lint.py, hooks/scripts/*gate.py | Read/Grep, chờ chốt vị trí gate | Chỉ thêm logic ở entry point thật sự cần; chưa quyết định sửa state/hook; không dựng validator trùng nhau |
| scripts/build_portable.py, tests/test_build_portable.py | Grep | tdq_eval bị loại khỏi cả portable và main; phải chốt chỉ dùng trong repo phát triển hay ship cho project cài plugin |
| .github/workflows/test.yml | Read | Hiện unittest + context_surface diagnostic; chưa có eval A/B bắt buộc. CI nền trước còn FAIL, không tự mở rộng sang sửa toàn CI |

Đã đọc đầy đủ docs/kien-truc.md: profile còn nhãn NHÁP, có các quyết định đã chốt ở cuối. Giữ hướng phụ thuộc hiện có, một nguồn skills và một writer state. Mục Ponytail full trong lịch sử profile đã cũ; code/rule 0.85.1 là ultra. Không sửa profile để chốt lại kiến trúc trong lượt khảo sát.

Preflight setup/check: 6/8 bậc đạt; grep/LSP/Graphify smoke 3/3 trả lời. MCP start/open thành công nhưng find_references(chay_phien) báo LSP process exited; không khai references PASS. Graphify affected depth2 tìm được hai caller chay_phien, không tìm thấy caller tao_manifest_eval; grep tìm tests và call nội tệp nên “graph trống” không có nghĩa không có caller. Miễn LSP lúc init chỉ cho brief/spec, không dùng làm chứng nhận code.

### Nền tảng và khoảng trống đã xác nhận

- Có runner Claude CLI, hai snapshot viet/lai cố định, corpus cũ, scorer tất định, 60 bản ghi lịch sử; chưa chứng nhận hiệu quả bản TDQ hiện tại.
- Manifest đã có base/candidate/corpus/check_set/scorer/permission/model/offline; validator paired hiện chỉ so corpus và check_set, chưa bảo đảm cùng host/model/permission/tool budget.
- Runner native đang gọi claude -p với model hằng và bypassPermissions; auth token helper hướng Keychain macOS. Không lấy cách này làm thiết kế mặc định cho Windows/Codex hoặc ngầm cấp thêm quyền.
- `total_cost_usd` thiếu bị chuyển thành 0.0; lỗi chấm cũng ghi chi_phi=0.0; tổng chi phí/report có nhánh `or 0.0`. Chưa thể dùng số 0 này làm bằng chứng miễn phí hay cơ sở cứng bảo vệ ngân sách.
- Budget hiện kiểm tổng đã ghi trước phiên kế tiếp, retry không có kiểm trần riêng trong vòng lặp; thiết kế mới phải xử lý reservation/cap theo khả năng host, unknown và lỗi transport, không tự chạy thêm để bù dữ liệu.
- Context_surface có cột token ước lượng; token_audit có phép đo carry-cost từ transcript. Phải tách estimated/context bytes với usage/billed cost thực tế và cache usage.
- Trạng thái execution, quality, comparability và metric availability cần tách riêng. Chưa có live run không được tự biến thành khuyến nghị giữ/bỏ có chứng nhận.

### Hướng thiết kế đề xuất, chờ chốt spec

Tái dùng CLI/parser/scorer/manifest và process ownership hiện có. Legacy report vẫn đọc dữ liệu cũ; thí nghiệm mới khóa manifest/corpus/holdout/rubric trước chạy, không trộn records cũ hay ghi đè raw trace. Hai adapter host thực chỉ khi user chọn hai host; không dựng framework plugin adapter cho trường hợp chưa yêu cầu.

Ba nhóm kết quả riêng: trigger đúng/sai/ngữ cảnh không nên kích hoạt; chất lượng nhiệm vụ qua artifact/test oracle; hiệu suất bằng usage/time/retry/intervention được quan sát. Thiếu metric là unavailable, không phải 0. Model/host chưa chạy là UNTESTED. Lỗi hạ tầng không được gán thành skill kém hoặc lén bỏ khỏi chi phí/thống kê.

Giữ/rút gọn/bỏ là khuyến nghị có bằng chứng và ngưỡng chốt trước, không tự xóa luật hoặc đổi mặc định ultra user đã yêu cầu. Baseline/candidate không được khác quyền/guard ngoài biến thử nghiệm đã khóa. Bộ test quá dễ và baseline đã trần cần được báo là chưa phân biệt được, không suy skill vô dụng.

Nghiên cứu nguồn chính thức đã hoàn tất bởi reviewer độc lập theo analyze-full bước3: [tệp nghiên cứu](../research/2026-11-01-1854-eval-chat-luong-skill.md), 4 truy vấn; chỉ đọc web, không chạy model/eval trả phí. Kết luận: eval-first, baseline/candidate, multiple-model checks; khóa repetitions/holdout/grader; phân biệt usage/estimate/billing; có nhánh chưa đủ bằng chứng. Đã đối chiếu skill-creator built-in: validator chỉ kiểm cấu trúc, không chứng minh quyết định tốt; forward-test không được cho agent đáp án mong đợi.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Scope và phỏng vấn | CÓ | Đã chốt gate cho repo/project, hai host và QC; không chạy pilot Ponytail |
| Research nguồn chính thức | CÓ | Kiểm thiết kế A/B, grader và usage; không vay số doanh nghiệp chưa xác minh |
| Spec → duyệt → plan → duyệt | CÓ | Pipeline full user đã chọn; live profile là input khi gọi runner, không đặt ngân sách giả định |
| Triển khai và test theo task | CÓ | Sau duyệt plan; cần code và fixture thực |
| Chia subagent triển khai | CÓ | Chọn mode sau duyệt plan, không suy mode từ request cũ |
| QC độc lập/runtime | CÓ | User chọn QC ultra; dùng process fixture và CLI preflight, không gọi model để thay smoke |
| Live pilot Ponytail full/ultra | BỎ | User nói rõ không cần A/B hai mức; giữ mặc định ultra |
| Báo cáo và đóng hồ sơ | CÓ | Có provenance, coverage, giới hạn, comparability và khuyến nghị |

## Hỏi đáp

- Phạm vi năm việc: đã duyệt bằng câu user ở trên.
- Pipeline: full, user “1a”.
- Request cũ: đã lưu previous-state.checkpoint.json trước init; user yêu cầu mở request mới và chọn full sau khi đã được báo tình trạng state cũ.
- 1. Gate: user chọn B — cả repo TDQ và project cài plugin. Gate dành cho thay đổi hành vi skill/hook/plugin, không tự mở rộng thành live eval cho mọi thay đổi code ứng dụng. Thiết kế phải giải quyết giới hạn packaging hiện tại: tdq_eval/corpus dev đang bị loại khỏi release; ưu tiên dùng chung core/contract thay vì chép hai runner.
- 2. Host/model đầu tiên: user chọn A — Claude Code + Codex trên Windows hiện tại, báo cáo riêng từng host/model. Model ID cụ thể sẽ khóa trước chạy, không dùng alias thay đổi trong một cặp; host chưa kiểm được không được suy PASS.
- 3. Pilot Ponytail: sau lựa chọn 3c, user làm rõ “à không vậy ko cần test A/B giữa full với ultra đâu, mặc định là ultra luôn”. BỎ pilot này; không tiếp tục hỏi ngân sách cho nó. Không coi 10 USD/16 phiên hoặc bất kỳ hạn mức nào trước đó là đã duyệt. Cơ chế Eval tổng quát vẫn hỗ trợ baseline/candidate cho những thay đổi skill/plugin khác; chạy model thật cần cấu hình thực thi riêng, không tự khởi chạy do gate hoặc do cài plugin.
- 4. QC: user chọn A — ultra (Full + smoke/runtime + reviewer độc lập); đã ghi `muc_qc=ultra` qua CLI. Ponytail ultra là cấu hình riêng.

Phạm vi và mức QC đã rõ; ngân sách của pilot Ponytail không còn là đầu vào cần chốt để viết spec. Giữ năm cải tiến Eval tổng quát, không mở lại các lựa chọn 1/2/4 hoặc hỏi thêm về so sánh full/ultra. Chưa có phiên model trả phí được chạy.

- User “okay tiếp tục”: chuyển sang spec. Spec v1.0 có O1–O7, Q1–Q10, runtime dùng chung core và không gọi model từ gate/install/report. Cơ chế được kiểm bằng oracle/process fixture, hiệu quả agent thực tế giữ UNTESTED nếu chưa có live trace; không tự chuyển loại claim sau khi xem số.
- Preview đã native render và browser-check PASS, binding current; đã xem ảnh desktop qua Chrome direct CDP vì MCP Transport closed. Một warning không chặn về UI renderer chưa dịch toàn bộ tiếng Việt được giữ trong receipt; nội dung/roles thiết kế đã tùy biến.
