# Brief — Hoàn thiện tích hợp Archify đầu-cuối
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay vậy hãy mở request để tích hợp nó vào tdq-workflow và xây dựng combine để tận dụng tối đa archify nha

Người dùng chọn `1b`: tách request triển khai mới theo pipeline chuyên sâu; bàn giao request cũ chưa nghiệm thu, giữ tài liệu và mã, kế thừa quyết định trước. Đây không phải yêu cầu làm lại từ đầu hoặc xác nhận kết quả QC cũ.

Mục tiêu: cung cấp BA trực quan trước code ở cả hai pipeline, bản đồ dự án đáng tin, kết hợp Graphify/LSP/agent với Archify; kiểm chứng từ đầu vào tới HTML thật và trải nghiệm dev.

## Hiểu & kiến thức

### Nền kế thừa

- Request trước: `2026-10-24-2145-nghien-cuu-tich-hop-archify`; nhánh `feature/nghien-cuu-tich-hop-archify`.
- Báo cáo và QC cũ đã đính chính CHƯA NGHIỆM THU. Không merge nền chưa đạt về `dev`.
- Adapter, setup, tests và hướng dẫn đã tồn tại; tái sử dụng sau kiểm chứng, không viết lại chỉ vì tách request.
- Preview tổng hợp: `docs/archify-preview.html`; đây là tài liệu tổng hợp, không phải bản đồ đầy đủ hay bằng chứng E2E của adapter.

### Quyết định kế thừa

- Pipeline yêu cầu mới: full; QC: ultra. Chế độ thực thi sẽ được chốt theo plan mới, không tự mang phê duyệt plan cũ sang.
- Full sinh preview tại spec trước duyệt, plan tham chiếu lại. Quick sinh flow ở mini-plan cho nhiều module/refactor; giữ một cổng duyệt.
- Hai tầng: Master Map toàn dự án và Task BA riêng. Standalone HTML, không tự bật server thường trực.
- Hybrid: mặc định agent hiện tại tác giả hóa candidate; endpoint riêng là hướng mở rộng cần client thật, kiểm soát dữ liệu và ngân sách. Không đọc hoặc sao chép bí mật từ harness.
- Giữ ngữ nghĩa, nhánh lỗi và bằng chứng quan trọng; giới hạn số node không được làm mất nghiệp vụ. Nếu cần nhiều hình thì chia góc nhìn và ghi phạm vi.

### Khoảng trống phải khảo sát trước spec mới

- Đối soát CLI với chỉ dẫn skills; phát hiện lỗi finalize, timeout, receipt, đường dẫn và mở file an toàn.
- Kiểm schema bridge bằng Archify thật; kiểm hướng cạnh, provenance, freshness và phạm vi bị lọc.
- `sync_master` hiện ghi JSON; cần xác minh và thiết kế xuất Master HTML, cập nhật theo revision, không trộn thiết kế dự kiến vào hiện trạng.
- Xác minh client endpoint, phạm vi dữ liệu được gửi, giao thức và cách dùng chung agent; không coi biến env là triển khai.
- Đọc log đầy đủ của test nền lỗi; tách hồi quy mới và vấn đề nền bằng chứng thực tế.
- Phân tích khả năng phân phối đa host, đường dẫn gói Archify và điều kiện cài đặt; không ghim đường dẫn máy admin.
- Rà soát phê duyệt artifact, tính nhất quán spec/HTML/plan, trạng thái stale và hành vi fallback.

### Bằng chứng hiện có và giới hạn

- Lần kiểm riêng adapter/setup/doc_lint đạt 143 tests trong phiên trước; cần tái kiểm sau sửa.
- Các tác vụ bpzrsod7w, bsfb9qjx9, b1mf8t6q6 kết thúc exit 1. Chưa kết luận nguyên nhân chỉ từ mã thoát.
- Archify explainer finalize của preview đạt validate/deliver/check; browser gate không chạy trong CLI, đã mở xem thủ công qua DevTools.
- Không dùng các số 800 ms/700 tokens trước đó như số đo. Chưa đo hiệu năng mới.

### Khảo sát thực tế lượt tiếp tục

- LSP pre-flight `detect_lsp_servers` trả lời; đã `start_lsp` Python, `list_symbols` adapter và `find_references(run_finalize)` trả 3 tham chiếu. Chưa coi đây là hoàn tất kiểm chứng toàn module.
- `tdq_lsp.py check`: 6/8 bậc đạt, graph cũ và chứng nhận module Python hết hạn; smoke 3/3 trả lời. `graphify affected run_finalize --depth 2` không có node khớp duy nhất; dùng LSP/đọc nguồn làm bằng chứng, không suy ra không có caller.
- Tái hiện bằng mock tiến trình, không sửa source: exit=1, receipt check=fail, file output cũ tồn tại → `run_finalize` trả status=True. Lỗi xác nhận tại `scripts/tdq_archify.py:284-293`.
- Chạy đúng cú pháp positional trong spec-template → argparse exit 2, yêu cầu `--type`, `--candidate`, `--out`. Lỗi hợp đồng skills/CLI đã xác nhận.
- `sync_master` chỉ ghi JSON (`scripts/tdq_archify.py:570-605`); không tìm thấy tích hợp sync trong `tdq_finish.py`.
- Grep scripts/skills/tests không thấy consumer của `ARCHIFY_AI_ENDPOINT`, `ARCHIFY_API_KEY`, `ARCHIFY_MODEL`; biến cấu hình chưa chứng minh client AI hoạt động.
- Log QC-F1 cũ ghi rõ: 2829 tests, 14 failures, 1 error, 9 skipped, 596.925 giây. Có lỗi runtime inventory, doc indices, luật bị thay đổi, encoding, UTF-8 bootstrap, skill/link contracts và tương thích host. Chưa quy mọi lỗi về Archify nếu chưa so baseline.
- Tái kiểm hai module `test_ma_hoa_subprocess.py`, `test_doc_index.py`: 2 failed, 27 passed. Hai lời gọi subprocess adapter thiếu encoding; chỉ mục quick-lane/plan-template/spec-template lệch.

### Năng lực dùng được

| Skill/công cụ | Nguồn | Phán quyết | Vai trò |
|---|---|---|---|
| tdq-intake/spec/plan/build | plugin:tdq-workflow | DÙNG | Quy trình và cổng duyệt |
| tdq-browser-test | plugin:tdq-workflow | DÙNG | E2E và kiểm tra tương tác HTML sau pre-flight |
| Archify local authoring/delivery | local | DÙNG | Hợp đồng native/explainer, schema và receipt |
| LSP + Grep | MCP/local | DÙNG | Cấu trúc, caller và hợp đồng tích hợp |
| Graphify | local | NỀN | Đồ thị đang stale, chưa dùng làm chứng cứ hiện trạng |
| tdq-lean | plugin:tdq-workflow | DÙNG | Tái sử dụng renderer, không tự viết lại engine |
| dataviz | built-in | DÙNG | Khi dựng sơ đồ preview mới |

### Đối chiếu vùng chạm dự kiến

| Vùng file | Phát hiện qua lớp nào | Tác động |
|---|---|---|
| scripts/tdq_archify.py và tests/test_tdq_archify.py | LSP, đọc nguồn, tái hiện | Hợp đồng finalize, lỗi, bridge, publish |
| skills/tdq-spec, skills/tdq-intake, skills/tdq-plan | Grep, test | Cú pháp CLI, đường dẫn preview, nội dung BA và indices |
| scripts/tdq_finish.py, scripts/tdq_state.py | Grep, đọc nguồn | Mốc cập nhật, liên kết phê duyệt tài liệu/artifact; chưa quyết định phải sửa state |
| scripts/tdq_setup.py, .env.example | Đọc nguồn trước và grep | Cài gói, root discovery, cấu hình endpoint thực sự |
| tests/test_build_portable.py và bộ test contract docs/UTF-8 | Log suite, test vùng hẹp | Phân phối runtime và hồi quy |

### Đề xuất cần quyết định về dữ liệu

Master phải tách snapshot đã commit khỏi preview nhánh đang phát triển. Mỗi artifact ghi nguồn/revision, trạng thái stale và phần bị lược; không tự nhận luôn cập nhật chỉ vì tồn tại HTML. Endpoint riêng chỉ bật theo quyền gửi dữ liệu rõ ràng; không mặc định gửi toàn repo hoặc đọc credential của harness.

### Đối soát độc lập hợp đồng Archify

Agent nghiên cứu đã trả kết quả, không chỉnh source:
- `archify/references/repository-authoring.md:10-25,78-91` và `schemas/common.schema.json:134-163`: sources dùng `line`/`end_line`, không phải `startLine`/`endLine`; trích dẫn được đối soát tại commit cố định, không đại diện working tree chưa commit.
- `archify/bin/finalize.mjs:998-1045`: exit khác 0 không phải hoàn tất; native cần browser gate theo hợp đồng. Explainer có hợp đồng riêng: browser-check có thể not-run. Không áp một luật gate cứng cho mọi loại.
- `archify/delta/architecture-delta.mjs:310-353`: compare tạo so sánh snapshot, không merge mô hình hay chứng minh runtime impact.
- `archify/references/explainer-authoring.md:106`: explainer hỗ trợ tối đa 4 native diagrams. Master có thể là trang tổng quan gọn và các góc nhìn chi tiết, không hứa nhúng vô hạn.
- `archify/bin/archify.mjs:2192-2225` và repository-authoring: CLI dựng/kiểm candidate do agent soạn; không có autonomous scanner tương đương lời hứa trước. Client endpoint phải thuộc tầng TDQ.
- `archify/scripts/check-update.mjs:54-56`: có `ARCHIFY_UPDATE_CHECK_DISABLED=1`; artifact offline không đồng nghĩa mọi lệnh CLI mặc định không có kiểm tra cập nhật mạng.

### Hướng thiết kế đề xuất sau khảo sát

- Phân tách thu thập bằng chứng, tác giả hóa mô hình, kiểm định/giao nhận và lifecycle artifact; không nhồi AI client và renderer vào hàm bridge.
- Hợp đồng BA chung cho Full/Quick: mục tiêu, actor, trigger, quy tắc, happy path, exception path, đầu ra và tiêu chí nghiệm thu; sơ đồ là góc nhìn từ hợp đồng này.
- Master có entry HTML ổn định và inventory phạm vi; nội dung current chỉ từ snapshot đã kiểm chứng. Planned và working-tree preview phải mang nhãn riêng. Dùng compare để trình bày delta, không dùng nó thay engine cập nhật.
- Artifact gắn hash candidate, nguồn và bản spec/mini-plan; thay đổi sau duyệt phải báo stale. Không thêm cổng duyệt thừa.
- Endpoint mặc định tắt; không mượn credential nội bộ của host. Chỉ chạy qua cấu hình người dùng cấp, có allowlist dữ liệu, timeout và giới hạn yêu cầu. Còn cần người dùng chốt giao thức endpoint và chính sách dữ liệu trước khi spec ràng buộc.
- Không viết code hoặc sửa spec đã duyệt cũ trong lượt phân tích này.

### Chốt bổ sung ngày 2026-10-25

Nguyên văn: `1A 2 cho phép gửi hết mọi thứ và endpoint riêng chỉ cần nếu achify không dùng ddc agent hiện đang có ,`.

- Agent-first: Archify nhận candidate do agent hiện tại soạn; không cần endpoint riêng cho đường chạy đã xác minh này.
- Chọn OpenAI-compatible chỉ làm phương án khi agent hiện tại không dùng được. Không xây client dự phòng hoặc bật gọi API chỉ để tận dụng biến env đã thêm trước đó. Nếu phát hiện thật sự cần fallback, ghi rõ điều kiện và yêu cầu endpoint/model được cấu hình, không tự đoán dịch vụ.
- Quyền dữ liệu: người dùng cho phép toàn bộ dữ liệu dự án khi cần endpoint; không mở rộng sang dữ liệu ngoài dự án hay credential riêng của harness. Không có endpoint được cấu hình trong request hiện tại, không gửi dữ liệu mạng ngoài.
- Những biến endpoint chưa có consumer phải được mô tả là chưa hoạt động hoặc gỡ khỏi cấu hình vận hành, không quảng bá scanner đã có.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Khảo sát nguồn cục bộ | CÓ | Đã tái hiện lỗi và đối soát hợp đồng upstream |
| Research web bổ sung | BỎ | Phạm vi ghim bản Archify cục bộ; không xây client API trong đường agent-first |
| Spec và preview | CÓ | Chốt hợp đồng BA, lifecycle, đầu ra và tiêu chí nghiệm thu |
| Plan | CÓ | Tách module theo luồng gọi và khai kiểm thử cụ thể |
| Implement | CÓ | Sau duyệt spec/plan mới; không kế thừa quyền triển khai cũ |
| QC ultra độc lập | CÓ | Test hồi quy, render thật và kiểm tra trình duyệt |
| Report | CÓ | Báo đúng PASS/FAIL/CHỜ, không đóng trước tác vụ nền |

## Hỏi đáp

- Hỏi: tiếp tục request cũ hay tách mới theo pipeline chuyên sâu?
- Đáp nguyên văn: `1b`.
- Hệ quả: giữ lịch sử và mã nguồn; mở request mới, chưa được duyệt spec/plan mới. Không hỏi lại mô hình hai tầng và vị trí preview đã chốt.
