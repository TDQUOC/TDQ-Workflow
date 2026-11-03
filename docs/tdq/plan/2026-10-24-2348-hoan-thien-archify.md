# PLAN — Hoàn thiện Archify đầu-cuối

Ngày: 2026-10-25 · Spec: ../spec/2026-10-24-2348-hoan-thien-archify.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — ĐỀ XUẤT từ simulate: đội 12.3 so với main 22.4 phút model time, chênh 10.1 phút với hệ số agent 1.5; đây là mô hình hiệu chuẩn cũ, không phải thời gian thực nghiệm của request mới. User chốt sau duyệt plan.
Trạng thái plan: HOÀN THÀNH — user chọn subagent bằng `1a`

## Quy tắc thi hành

1. Mỗi task có test hành vi trước, đỏ vì lỗi hoặc thiếu chức năng thật → sửa → xanh → tick ngay. Test của module nằm cùng task, không chờ cuối mới viết.
2. Chỉ sửa vùng đã khai. Nguồn mới giữ tiếng Anh theo quy ước repo; tài liệu user tiếng Việt. Không sửa spec đã duyệt hoặc engine Archify ngoài repo.
3. Mọi phép kiểm ghi thời điểm, commit, exit code và output vào thư mục bằng chứng của request. Lệnh mới nêu dưới đây là đầu ra phải xây, không giả là đã tồn tại.
4. Không chạy song song các suite có ghi ledger/state. Test state dùng project tạm; không gọi init/reset trên request thật.
5. Unit test dùng mock để kiểm lỗi, nhưng E2E phải dùng engine thật. Browser thiếu/timeout là FAIL hoặc CHỜ, không phải PASS. Không đóng QC khi còn tác vụ nền chưa kết thúc.
6. Không có client endpoint mới, không đọc key host, không gọi API ngoài. Node/Archify local là đường chạy; tắt update-check trong kiểm thử offline.
7. Không commit/push/merge về nhánh gốc khi chưa được yêu cầu. Nếu chọn subagent, bàn giao diff từ worktree; không để agent tự commit trái quy tắc này. Giữ nguyên dirty docs kế thừa.
8. QC lỗi → thêm task sửa dưới vòng tương ứng, tối đa theo quy tắc QC. Không giảm điều kiện PASS, bỏ luật hoặc sửa assert chỉ để làm suite xanh.

## Thiết kế Trước vs Sau

| Vùng | Trước | Sau |
|---|---|---|
| Adapter | Finalize lỗi vẫn thành công; encoding thiếu, đường dẫn shell nội suy | Contract exit/receipt/hash, timeout, UTF-8, mở file không diễn dịch shell |
| Bridge | Trích nguồn sai schema, cắt node âm thầm | Candidate hợp schema, coverage, evidence và quan hệ có loại/hướng |
| Master | Chỉ JSON | Index HTML và views, snapshot có revision, stale khi nguồn đổi |
| BA | Skill gọi CLI không khớp | Agent-first, preview đúng gate Full/Quick, manifest liên kết tài liệu |
| QC | Mock xanh bị coi như E2E, kết luận trước suite nền | Bằng chứng âm tính, runtime/browser thật, baseline phân biệt hồi quy |

## Bằng chứng phạm vi và baseline

- LSP `list_symbols` và `find_references(run_finalize)` đã chạy ở analyze. Lượt plan đã gọi `blast_radius` cho adapter và finish; kết quả có nhiều self-edge và không đủ vị trí caller để tin là đầy đủ. Đối soát bằng Grep: adapter được dùng trong unit tests; finish có caller tests riêng và hợp đồng hook/Windows cần hồi quy.
- Graphify hiện stale, affected không tìm node run_finalize duy nhất; không coi đồ thị này là bằng chứng vùng chạm đầy đủ. Không chạy semantic extraction có chi phí trong bước plan.
- Baseline kế thừa: `5d6570d` (trước request mới, chứa phần tích hợp cũ) và nền trước tích hợp `a03d698`. Ghi hash thực tế khi QC; phân biệt lỗi đã tồn tại trên hai mốc với lỗi do đợt mới.
- Log cũ: 2829 tests, 14 failures, 1 error, 9 skipped. Hai lỗi đã tái hiện ở encoding adapter và doc indices. Các lỗi khác phải đọc log và chạy đối chứng, không phán là ngoài phạm vi chỉ từ tên test.

## P1 — Khóa hợp đồng và chuẩn bị bằng chứng

- [x] **T1.1** (e18m) Khóa contract CLI/manifest/BA và baseline trước sửa; ghi mapping hành vi về spec O1–O7, chụp trạng thái các lỗi cũ — Test: `python scripts/doc_lint.py docs/kien-truc-tich-hop-archify.md`
  - Chạm: `docs/kien-truc-tich-hop-archify.md`
  - Dùng: `Archify authoring/delivery`
  - Để: Đối chiếu trực tiếp schema và delivery ở gói local 3.2.0, không tin báo cáo cũ
  - Ra: `docs/kien-truc-tich-hop-archify.md`
  - Kiểm: `python scripts/doc_lint.py docs/kien-truc-tich-hop-archify.md`
  - Không dùng cho: Sửa upstream hoặc triển khai scanner AI
  - Dùng: `LSP/Grep` (mcp)
  - Để: Kiểm symbol/callers trước sửa; dùng text fallback khi kết quả LSP không đủ tin
  - Ra: `docs/kien-truc-tich-hop-archify.md`
  - Kiểm: `python scripts/doc_lint.py docs/kien-truc-tich-hop-archify.md`
  - Không dùng cho: Giả lập caller hoặc coi graph stale là current
  - Chi tiết: lưu baseline failures vào bằng chứng QC; kết quả lint chỉ chứng minh định dạng, leader đối chiếu nguồn trước tick.

**Contract cần khóa trong T1.1:** CLI render dùng cờ `--type --candidate --out`; giữ tên lệnh cũ check/render/open/bridge/sync-master nhưng công khai thay đổi semantics trong docs. Thêm freshness/binding check qua một lệnh CLI; tên/flags chốt ở T1.1 rồi test khóa, các task sau không tự đặt khác nhau. Manifest versioned lưu source snapshot, document content digest, candidate/artifact hashes, engine/receipt và coverage. Digest tài liệu bỏ chính khối binding khi tính để tránh vòng tự băm; hash manifest được ghi vào tài liệu trước cổng duyệt, checksum kiểm lại trước code.

## P2 — Nền runtime và mô hình

- [x] **T2.1** (e30m) Sửa giao nhận và root discovery; tách module delivery, giữ CLI facade tương thích có kiểm soát; viết test lỗi và log stderr mặc định — Test: `python -m pytest tests/test_tdq_archify.py tests/test_archify_delivery.py -q`
  - Chạm: `scripts/tdq_archify.py`, `scripts/archify_delivery.py`, `tests/test_tdq_archify.py`, `tests/test_archify_delivery.py`
  - Cần: T1.1
  - Chi tiết: test exit 1 + receipt pass giả, HTML cũ, JSON scalar/null, thiếu gate, native browser skipped, explainer not-run hợp lệ, hash mismatch, timeout và file có Unicode/ký tự shell. Dùng utf8_io cho entrypoint, encoding rõ và subprocess an toàn. Không giữ NamedTuple override sai kiểu chỉ vì test cũ mong đợi. Root explicit sai phải báo, không âm thầm dùng bản khác trên máy. Tách check_environment đủ dùng để setup tái sử dụng, không giữ đường dẫn admin.

- [x] **T2.2** (e28m) Xây mô hình coverage/evidence và chuyển đổi Graphify đúng schema; không suy vai trò chỉ từ tên hoặc biến cạnh vô hướng thành call — Test: `python -m pytest tests/test_archify_model.py -q`
  - Chạm: `scripts/archify_model.py`, `tests/test_archify_model.py`
  - Cần: T1.1
  - Chi tiết: path/line/end_line và repository revision; stable IDs, duplicate ID/edge, invalid range/path, empty graph, graph stale, thiếu remote, dirty snapshot, truncated coverage. Quan hệ chưa chứng minh hướng lưu trong inventory/unknown, không render thành mũi tên call. Planned không trích mã chưa tồn tại. Agent cung cấp mapping module/domain, bridge không tự biến directory thành kiến trúc nghiệp vụ. Không hard cap node làm mất scope; explicit slice phải kèm excluded count/IDs hoặc inventory.

- [x] **T2.3** (e30m) Xây manifest, freshness và cơ chế publish giữ snapshot tốt; dữ liệu được duyệt không tự đổi sau render — Test: `python -m pytest tests/test_archify_artifacts.py -q`
  - Chạm: `scripts/archify_artifacts.py`, `tests/test_archify_artifacts.py`
  - Cần: T1.1
  - Chi tiết: candidate, document, source fingerprint và HTML thay đổi đều bị phát hiện; planned/current/working-tree/partial tách bằng trường rõ, freshness độc lập với evidence kind. Exclude docs/architecture và output-derived khỏi source fingerprint. Tệp tạm độc quyền, path confinement, lock stale có quy tắc phục hồi, rollback khi publish lỗi, cạnh tranh giữa hai request. Dùng snapshot/version directory và entry publication sau cùng để không trộn HTML/receipt/manifest của hai phiên; không sửa HTML sau khi receipt đã khóa hash.

## P3 — Kết nối chạy thật và môi trường

- [x] **T3.1** (e32m) Kết nối model/delivery/artifacts vào CLI; sync-master dựng index HTML và views từ model agent-authored, bridge chỉ chuẩn bị evidence; thêm status/binding check — Test: `python -m pytest tests/test_archify_pipeline.py -q`
  - Chạm: `scripts/tdq_archify.py`, `tests/test_archify_pipeline.py`
  - Cần: T2.1, T2.2, T2.3
  - Chi tiết: task render nhận document context để lưu binding; CLI không có context báo artifact chưa gắn duyệt, không giả registered. Master index dùng Archify explainer hoặc native theo model, giữ entry docs/architecture/index.html; bảng inventory link views, nhiều view thì chia trang theo giới hạn upstream. Graph raw không đủ ngữ nghĩa thì yêu cầu agent authoring và không publish current. Index và receipt phải cùng bytes được kiểm, không dùng compare như merge. Test missing model/candidate, partial render và giữ bản tốt.

- [x] **T3.2** (e16m) Setup/root khả chuyển, cấu hình agent-first và phân phối runtime đủ dependency — Test: `python -m pytest tests/test_tdq_setup.py tests/test_archify_distribution.py -q`
  - Chạm: `scripts/tdq_setup.py`, `.env.example`, `scripts/build_portable.py`, `tests/test_tdq_setup.py`, `tests/test_archify_distribution.py`, `tests/test_build_portable.py`
  - Cần: T2.1, T2.2, T2.3
  - Chi tiết: tái sử dụng kiểm môi trường từ delivery, không duplicate dò root; khai ARCHIFY_ROOT và hướng dẫn local package. Biến endpoint chưa dùng phải loại khỏi cấu hình active hoặc ghi reserved/inactive rõ, không default model gpt-4o như scanner thật. Test package ở đường dẫn khác, path có dấu/khoảng trắng, no browser theo loại; kiểm closure runtime thực tế thay vì chỉ đổi con số assert. Không tự tải/cài Archify từ URL chưa xác minh.

- [x] **T3.3** (e18m) Gắn freshness vào finish mà không auto gọi AI/render hoặc đánh to-be thành current — Test: `python -m pytest tests/test_tdq_finish.py tests/test_archify_finish.py -q`
  - Chạm: `scripts/tdq_finish.py`, `tests/test_tdq_finish.py`, `tests/test_archify_finish.py`
  - Cần: T2.3, T3.1
  - Chi tiết: dự án chưa có manifest thì skip; đổi source/config/contract đánh stale và in việc refresh cần agent. Chỉ đổi output/log không tự kích hoạt vòng lặp. Lỗi kiểm freshness có trạng thái fail/unknown rõ và không chặn ghi nhật ký. Sau merge workflow recheck revision, không dùng timestamp report thay snapshot. Kiểm đường gọi Windows subprocess, không import hooks hoặc ghi state trực tiếp.

## P4 — Hướng dẫn BA hai pipeline và đồng bộ luật

- [x] **T4.1** (e25m) Tích hợp hướng dẫn tác giả hóa BA, preview trước duyệt, kiểm binding trước code và refresh sau thay đổi ở Full/Quick — Test: `python -m pytest tests/test_archify_workflow_contract.py -q`
  - Chạm: `skills/tdq-spec/SKILL.md`, `skills/tdq-spec/references/spec-template.md`, `skills/tdq-spec/references/archify-ba.md`, `skills/tdq-intake/SKILL.md`, `skills/tdq-intake/references/quick-lane.md`, `skills/tdq-intake/references/archify-quick.md`, `skills/tdq-plan/references/plan-template.md`, `skills/tdq-build/SKILL.md`, `skills/tdq-build/references/archify-lifecycle.md`, `tests/test_archify_workflow_contract.py`
  - Cần: T3.1, T3.2, T3.3
  - Dùng: `tdq-spec`
  - Để: Full preview, đường dẫn và khối binding trước duyệt spec
  - Ra: `skills/tdq-spec/references/archify-ba.md`
  - Kiểm: `python -m pytest tests/test_archify_workflow_contract.py -q`
  - Không dùng cho: Thêm cổng duyệt hình hoặc sửa spec đã duyệt
  - Dùng: `tdq-intake`
  - Để: Quick flow khi nhiều module/refactor, bỏ HTML cho việc nhỏ có lý do
  - Ra: `skills/tdq-intake/references/archify-quick.md`
  - Kiểm: `python -m pytest tests/test_archify_workflow_contract.py -q`
  - Không dùng cho: Ép full spec vào Quick
  - Dùng: `tdq-plan`
  - Để: Task trace về node/rule/criterion của BA đã duyệt
  - Ra: `skills/tdq-plan/references/plan-template.md`
  - Kiểm: `python -m pytest tests/test_archify_workflow_contract.py -q`
  - Không dùng cho: Vẽ lại thiết kế khác mà không duyệt lại
  - Dùng: `tdq-build`
  - Để: Kiểm binding trước code, refresh Master sau QC/merge, giữ lỗi là lỗi
  - Ra: `skills/tdq-build/references/archify-lifecycle.md`
  - Kiểm: `python -m pytest tests/test_archify_workflow_contract.py -q`
  - Không dùng cho: Auto gọi endpoint hoặc auto merge branch
  - Tiến độ: Full/Quick/build đã có reference trực tiếp; bỏ positional CLI sai ở Quick, đang đồng bộ templates và chạy test contract.
  - Chi tiết: chỉ link artifact tồn tại và đạt kiểm; thiếu engine dùng fallback có nhãn, không in đường dẫn giả. Contract dùng PLUGIN_ROOT tuyệt đối cho CLI, output theo project root, không giả target repo có scripts TDQ. Trace Full/Quick trên fixture; current/working-tree/planned rõ. Đọc skill liên quan để sửa hướng dẫn, không chạy lifecycle mở request mới từ bên trong task.

- [x] **T4.2** (e16m) Khôi phục luật bị nén mất ở request trước, đồng bộ indices/token lock/ledger và rà clean-code — Test: `python -m pytest tests/test_doc_index.py tests/test_doc_lint.py tests/test_luat_skill.py tests/test_archify_workflow_contract.py -q`
  - Chạm: `skills/tdq-intake/references/quick-lane.md`, `docs/tdq/audit/luat-hien-co.md`, `docs/tdq/token-budget.json`, `skills/tdq-plan/references/plan-template.md`, `skills/tdq-spec/references/spec-template.md`
  - Cần: T4.1
  - Dùng: `tdq-lean`
  - Để: Giữ đầy đủ quy tắc; tách nội dung có điều kiện, không cắt luật để đạt token cap
  - Ra: `docs/tdq/audit/luat-hien-co.md`
  - Kiểm: `python scripts/token_budget.py --kiem`
  - Không dùng cho: Giảm chất lượng hoặc xóa evidence để test xanh
  - Tiến độ: 329 neo nội dung đã khớp; đang đồng bộ dòng neo chính xác và giới hạn line/token bằng chuyển chỉ dẫn BA sang reference, không bỏ luật.
  - Chi tiết: dùng generator sẵn có cho indices và token lock; ledger cần neo khớp nội dung thật. Không đổi tests bảo vệ luật thành assert lỏng. Nếu phát hiện lệch không thuộc request, lưu baseline trước khi đề xuất mở rộng sửa.

## P5 — Kiểm chứng đầu-cuối và báo cáo

- [x] **T5.1** (e30m) Dựng fixture Full/Quick/Master bằng engine thật, mutation freshness/binding và kiểm trình duyệt — Test: `python -m pytest tests/test_archify_e2e.py -q`
  - Chạm: `tests/test_archify_e2e.py`, `tests/fixtures/archify/ba.json`, `tests/fixtures/archify/workflow.json`, `tests/fixtures/archify/master.json`, `docs/tdq/qc/2026-10-24-2348-hoan-thien-archify.md`
  - Cần: T3.1, T3.2, T3.3, T4.2
  - Dùng: `tdq-browser-test` (mcp)
  - Để: Pre-flight CDP trước khi mở preview; xem layout và thử zoom/focus/view links trên file thật
  - Ra: `docs/tdq/qc/2026-10-24-2348-hoan-thien-archify.md`
  - Kiểm: `python -m pytest tests/test_archify_e2e.py -q`
  - Không dùng cho: Thay browser evidence bằng unit mock hoặc screenshot chưa xem
  - Dùng: `dataviz`
  - Để: Chọn dạng sơ đồ rõ luồng; nhãn và bảng không phụ thuộc màu để hiểu
  - Ra: `tests/fixtures/archify/workflow.json`
  - Kiểm: `python -m pytest tests/test_archify_e2e.py -q`
  - Không dùng cho: Tạo lại renderer hay thêm dashboard không cần
  - Chi tiết: E2E không skip khi thiếu engine; báo precondition FAIL/CHỜ. Mỗi smoke/runtime có cap 120s theo QC, không nâng cap tự ý. Test tạo repo fixture tạm có commit, cấu hình root engine local và tắt update-check; không dùng API key. Chạy CLI render đúng như skill, đọc receipt và hash, mở file bằng Chrome, xác nhận không console error ảnh hưởng dùng. Native gate và explainer gate kiểm riêng. Lưu riêng automated check và review thị giác; test exit 0 không chứng minh đã quan sát screenshot.

- [x] **T5.2** (e25m) Chạy QC tổng hợp và reviewer độc lập, phân biệt lỗi baseline, ghi report trung thực — Test: `python scripts/tdq_test.py tron-bo`
  - Chạm: `docs/tdq/qc/2026-10-24-2348-hoan-thien-archify.md`, `docs/tdq/reports/2026-10-24-2348-hoan-thien-archify.md`
  - Cần: T5.1
  - [x] Đã thu kết quả suite sau QC2.1: 2974 tests, 9 failures, 1 error, 10 skipped trong 601.138s; và sau request `2026-10-25-1510-xu-ly-issue-nen` xử lý dứt điểm 10 lỗi nền + dọn 6 worktree: `Ran 2977 tests in 662.963s — OK (0 failures, 0 errors, 10 skipped)`.
  - Chi tiết: QC-F1 chạy trọn suite một lần tại cổng, sau vòng sửa cuối thêm một lần; không đè kết quả nền bằng test hẹp. QC-F2 chạy vung-cham; QC-F3 kiểm luật import/state; QC-F4 kiểm clean-code và diagnostics. Reviewer đọc spec/plan/diff/log và thử lỗi, không chỉ lặp check environment. Nếu suite còn đỏ, task không tick xong chỉ vì baseline cũng đỏ: ghi đúng ngoại lệ đã chứng minh và kết luận CHƯA PASS TOÀN REPO, trình người dùng. Không tự đóng request khi có lỗi do thay đổi chưa sửa.

## Cụm song song

- Đợt contract: T1.1 trước mọi task.
- Đợt nền: T2.1, T2.2, T2.3 độc lập file, đọc chung contract đã chốt.
- Đợt kết nối: T3.1 và T3.2 sau nền; T3.3 sau T3.1/T2.3.
- Đợt luật: T4.1 → T4.2 tuần tự (leader giữ file luật nếu mode subagent).
- Đợt nghiệm thu: T5.1 → T5.2 tuần tự, không fan-out test toàn repo.

## Luật file nóng

- `scripts/tdq_archify.py`: T2.1 sửa facade/delivery, T3.1 kết nối model/lifecycle sau khi T2.1 xong; không đồng thời.
- Các template và quick-lane: T4.1 trước T4.2; cùng chủ ghi leader, thay đổi khác phải báo task chủ.
- File QC: T5.1 ghi runtime evidence trước T5.2 tổng hợp, không ghi song song.
- Test của model/delivery/artifacts thuộc chủ module; integration tests ở file riêng, không sửa test người khác trong lúc chạy.

## Log & test bắt buộc

Log runtime và test âm tính thuộc T2.1; test model thuộc T2.2, manifest thuộc T2.3, integration/setup/finish thuộc P3. Không thêm task test trùng và tick xong bằng một lần pytest hẹp. Mọi bước chạy vùng chạm sau thay đổi, suite toàn bộ theo ngân sách cổng ở T5.2.

## Definition of Done

- [x] Q1 Exit/receipt/hash/timeout/open an toàn — `python -m pytest tests/test_archify_delivery.py tests/test_tdq_archify.py -q`
- [x] Q2 Schema và evidence thật — `python -m pytest tests/test_archify_model.py tests/test_archify_e2e.py -q`
- [x] Q3 Full/Quick đúng gate và cú pháp — `python -m pytest tests/test_archify_workflow_contract.py tests/test_archify_pipeline.py -q`
- [x] Q4 Master HTML, coverage và stale/refresh — `python -m pytest tests/test_archify_pipeline.py tests/test_archify_e2e.py -q`
- [x] Q5 Binding/publish/lifecycle không giả current — `python -m pytest tests/test_archify_artifacts.py tests/test_archify_finish.py -q`
- [x] Q6 Khả chuyển và agent-first — `python -m pytest tests/test_archify_distribution.py tests/test_tdq_setup.py -q`
- [x] Q7 Browser E2E — `python -m pytest tests/test_archify_e2e.py -q`; kèm bắt buộc snapshot/screenshot và log tương tác MCP do người kiểm quan sát
- [x] Q8 Hồi quy và review độc lập — `python scripts/tdq_test.py tron-bo`; kèm reviewer verdict, đối chứng baseline, ledger `python scripts/tdq_test.py so` và không còn tác vụ nền đang chạy

Các lệnh test nêu là kiểm ở plan; khi runtime chưa được tạo, không chạy rồi tính lỗi import/file thiếu là RED hợp lệ. Tests mới phải kiểm hành vi và thất bại đúng nguyên nhân.

## QC vòng 1 — sửa sau review độc lập

- [x] **QC1.1** Sửa fingerprint explicit directory/deleted source và rollback directory không nuốt lỗi — Test: `python -m pytest tests/test_archify_artifacts.py -q`
  - Chạm: `scripts/archify_artifacts.py`, `tests/test_archify_artifacts.py`
  - Cần: T2.3
- [x] **QC1.2** Sửa giao dịch render rollback HTML/manifest/receipt/document khi bind lỗi — Test: `python -m pytest tests/test_archify_pipeline.py -q`
  - Chạm: `scripts/tdq_archify.py`, `tests/test_archify_pipeline.py`
  - Cần: T3.1
- [x] **QC1.3** Tách evidence_kind khỏi freshness current theo hợp đồng — Test: `python -m pytest tests/test_archify_model.py -q`
  - Chạm: `scripts/archify_model.py`, `tests/test_archify_model.py`
  - Cần: T2.2

Reviewer vòng đầu trả FAIL. Đã dùng lại worktree của owner module, nhập diff sau check không commit; 149 tests mục tiêu PASS trên main, E2E sau nhập 2 tests + 2 subtests PASS. Reviewer kiểm lại 5 findings trên main xác nhận đã sửa. Chưa nghiệm thu toàn repo: còn đối chứng baseline và QC tổng hợp; các task P2/P3 đã tick chỉ phản ánh kiểm tại thời điểm đó.

## QC vòng 2 — tương thích runner chuẩn

- [x] **QC2.1** Sửa bootstrap import của test artifacts để runner unittest chuẩn import được; giữ pytest riêng thu đủ hàm test — Test: `python -m pytest tests/test_archify_artifacts.py -q`
  - Chạm: `tests/test_archify_artifacts.py`
  - Cần: QC1.1
  - Chi tiết: full runner 2975 tests có lỗi import scripts.archify_artifacts; đây là lỗi tích hợp test của request mới, không được quy về baseline. Không sửa assert hoặc bỏ module khỏi discovery. Owner sửa worktree, kiểm import theo môi trường runner và pytest trước nhập.
