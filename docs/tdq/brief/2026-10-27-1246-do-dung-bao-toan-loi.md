# Đợt 1: đo đúng và bảo toàn lỗi
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay hãy note lại và mở request làm đợt 1

Người dùng đồng ý ghi lại phương án tối ưu đã trình bày trong chat và yêu cầu mở request triển khai đợt 1. Phạm vi được chọn là đo đúng, bảo toàn kết quả FAIL và kiểm tra lỗi qua phụ thuộc. Đây là yêu cầu mới sau cuộc khảo sát; không suy diễn thành phê duyệt spec, plan hoặc các đợt còn lại.

### Phương án đã thống nhất

| Đợt | Công việc | Kết quả mong muốn |
|---|---|---|
| 1 — request này | Chuẩn hóa số đo; sửa nhận diện transcript; giữ đầy đủ lỗi pytest; kiểm tra lỗi qua phụ thuộc gián tiếp | Có số liệu đáng tin và bằng chứng chất lượng đủ để đánh giá các tối ưu sau |
| 2 — request sau | Hợp nhất preflight; quản lý job/test theo dấu vân tay đầu vào; gộp thao tác độc lập | Bớt kiểm tra, chạy test và vòng điều phối trùng |
| 3 — request sau | Thử worker giới hạn; đồng bộ luật theo pha; A/B toàn luồng trước khi đổi mặc định | Tăng tốc có số đo và vẫn giữ phạm vi QC cần thiết |

Nguyên tắc: giảm công việc lặp còn giữ nguyên giá trị chứng nhận; không giảm thời gian bằng cách làm mất lỗi, bỏ bằng chứng cần thiết hoặc suy diễn quyền của người dùng.

### Phạm vi đợt 1

| Hạng mục | Hiện trạng đã có bằng chứng | Dự định xử lý | Kỳ vọng |
|---|---|---|---|
| Thời gian | `tdq_timing._giay_model` cộng khoảng cách sự kiện assistant, gồm cả tool; bỏ khoảng trên 300 giây | Phân biệt khoảng API/model quan sát, tool, job nền và phần chưa xác định; xử lý chồng lấp, thiếu sự kiện | Không gán thời gian tool cho model; không biến dữ liệu thiếu thành 0 |
| Transcript | `token_audit.default_transcript_dir` sinh sai tên thư mục Claude trên Windows | Tìm đúng transcript theo host/project; có trạng thái rõ khi không tìm hoặc không ghép được log | Bộ đo đọc đúng nguồn Claude/Codex được hỗ trợ, không nhầm project |
| Kết quả pytest | Parser parallel giữ FAIL nhưng mất module khi node ID chứa `::` | Chuẩn hóa kết quả test, bảo toàn verdict và thông tin lỗi; chọn định dạng cấu trúc ở spec | FAIL, lỗi collection, timeout, output thiếu/hỏng không biến thành PASS |
| Phụ thuộc gián tiếp | Fixture `core → facade → test_facade`: direct chọn rỗng nhưng test thực sự FAIL | Thêm kiểm thử hồi quy tái hiện lỗi; bảo vệ bước chứng nhận trước lựa chọn rỗng hoặc thiếu phạm vi | Lỗi qua module trung gian bị phát hiện tại mốc kiểm chứng bắt buộc |

Vùng dự kiến: `scripts/tdq_timing.py`, `scripts/token_audit.py`, `scripts/tdq_test.py`, các consumer và test liên quan. Đây là vùng ứng viên từ audit, chưa thay thế khảo sát ảnh hưởng khi lập spec/plan. Cách khắc phục selector và tương thích dữ liệu cũ sẽ được chốt sau khảo sát, không mặc định chạy full ở mọi bước.

### DoD đề xuất cho đợt 1

| Mã | Điều kiện hoàn thành | Cách kiểm chứng |
|---|---|---|
| D1 | Tách đúng thời gian quan sát API/model và tool; không cộng thời gian chồng lấp thành wall time; thiếu bằng chứng được đánh dấu chưa xác định | Fixture lịch sự kiện có thời lượng biết trước, gồm streaming, khoảng trống, khoảng dài hơn 300 giây và job nền |
| D2 | Tìm đúng transcript của project trên Windows; đường dẫn không tồn tại hoặc log không ghép được không được báo như dữ liệu hợp lệ bằng 0 | Fixture Claude/Codex theo định dạng hỗ trợ; project có tên/đường dẫn dễ gây nhầm; đối chiếu log thật đã chọn |
| D3 | Kết quả pytest giữ đúng trạng thái cùng thông tin test/module lỗi trong chế độ tuần tự và song song | Fixture node ID có `::`, nhiều lỗi, lỗi collection, timeout, tiến trình bị hủy và output thiếu/hỏng |
| D4 | Lỗi cài ở module lõi nhưng test chỉ import module trung gian phải được bắt; không có chứng nhận PASS sai chỉ vì chọn ra 0 test | Fixture tối thiểu `core → facade → test_facade`; ghi nhận đỏ trước sửa và xanh sau sửa của regression test |
| D5 | Các consumer hiện có và log lịch sử được xử lý theo hợp đồng tương thích được chốt trong spec | Test đọc dữ liệu cũ và mới; kiểm schema/version khi cần; không âm thầm đổi nghĩa chỉ số |
| D6 | Giữ scope, quyền, điều kiện tick và mức QC được chọn; full QC khi được yêu cầu phải chứng nhận đúng trạng thái cuối | Kiểm hồi quy runner/gate và kiểm thử cuối theo mức QC do người dùng chọn |
| D7 | Có báo cáo trước/sau, cách tái lập, giới hạn dữ liệu và phương án quay lui | Lưu command, fixture, verdict và mẫu đầu ra; phân biệt số đo thực với mục tiêu tối ưu |

Đợt 1 nghiệm thu độ đúng và bảo toàn chất lượng, không lấy giảm runtime 20% làm điều kiện hoàn tất riêng. Mục tiêu giảm ít nhất 20% median thời gian agent hoạt động thuộc đánh giá A/B toàn lộ trình ở đợt 3. Mức giảm 47,3% đã đo chỉ thuộc một cặp chạy bộ con 389 test, không phải mức giảm toàn workflow.

### Ngoài phạm vi đợt 1

Chưa triển khai dùng lại PASS bằng fingerprint, quản lý/join job, bỏ setup trùng, gom checkpoint, đổi worker mặc định, viết lại toàn bộ luật hoặc cache artifact. Không tự tạo thêm gate duyệt hay suy diễn phê duyệt các đợt 2–3 từ yêu cầu này.

### Bằng chứng nguồn

- [Báo cáo khảo sát Markdown](C:/Users/admin/Documents/TDQ-Reports/2026-10-27-runtime-cost/bao-cao.md) và [bản HTML](C:/Users/admin/Documents/TDQ-Reports/2026-10-27-runtime-cost/bao-cao.html), ngày 27/10/2026.
- [Thử nghiệm tái hiện](C:/Users/admin/Documents/TDQ-Reports/2026-10-27-runtime-cost/evidence/experiments.json), [đường dẫn transcript](C:/Users/admin/Documents/TDQ-Reports/2026-10-27-runtime-cost/evidence/windows-transcript-path.json) và [metrics 5 phiên](C:/Users/admin/Documents/TDQ-Reports/2026-10-27-runtime-cost/evidence/session-metrics.json).
- Snapshot khảo sát và HEAD khi tiếp nhận request: `3e0ef5f8a148cbf8aae1e932995e844e8f62ccd9`, TDQ 0.84.2, nhánh `dev`.

### Trạng thái tiếp nhận

Người dùng trả lời `1a`, chọn chế độ chuyên sâu (`full`); tiếp nhận lúc 12:50 ngày 27/10/2026, Asia/Bangkok. Đã khởi tạo request `2026-10-27-1246-do-dung-bao-toan-loi`, loại `bugfix`, phase `analyze`; nhánh `bugfix/do-dung-bao-toan-loi` mở từ `dev` và dự kiến gộp về `dev`.

Request trước `2026-10-26-0224-giam-timeout-agent-lsp` đang `idle`. Khi tiếp nhận, working tree chỉ có `docs/tdq/STATE.md` thay đổi từ trước; không có mã nguồn đang sửa dở. Giữ nguyên thay đổi đó. Người dùng đã chọn QC Full bằng câu trả lời `1a` ở lượt tiếp theo; đã ghi `muc_qc=full`. Sau đó người dùng nhắn `duyệt spec`, đã ghi phê duyệt lúc 13:21:48 ngày 27/10/2026. Plan được duyệt lúc 13:49:57 cùng ngày bằng câu `duyệt plan`; phase hiện là `mode`, chờ người dùng chọn cách thực thi.

## Hiểu & kiến thức

### Năng lực dùng được

Kiểm kê ngày 27/10/2026 bằng `skill_inventory.py --loc "telemetry runtime timing transcript pytest test runner regression quality"`: 28 skill trên đĩa, hiển thị 11 và lọc 17; đã đối chiếu thêm các skill built-in trong context.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | Tiếp nhận và khảo sát đợt 1 |
| tdq-conventions | plugin:tdq-workflow | NỀN | State, approval, nhật ký, kiến trúc và quy tắc chất lượng |
| tdq-setup | plugin:tdq-workflow | NỀN | Preflight đã đạt; không chạy lại khi bằng chứng vẫn còn hợp lệ |
| tdq-spec | plugin:tdq-workflow | NỀN | Viết spec sau khi chốt mức QC |
| archify | local:C:/Users/admin/Documents/archify/archify | DÙNG | Dựng và kiểm sơ đồ HTML thiết kế dự kiến, liên kết với spec |
| tdq-plan | plugin:tdq-workflow | NỀN | Lập plan sau khi spec được duyệt |
| tdq-build | plugin:tdq-workflow | NỀN | Triển khai, QC và báo cáo sau khi plan được duyệt |
| tdq-lean | plugin:tdq-workflow | NỀN | Giữ thay đổi đúng phạm vi, tránh dựng nền telemetry quá mức cần thiết |
| tdq-status | plugin:tdq-workflow | NỀN | Báo trạng thái bằng dữ liệu trên đĩa |
| tdq-check-status | plugin:tdq-workflow | NỀN | Phục hồi nếu phiên bị ngắt; hiện chưa cần kích hoạt |
| tdq-browser-research | plugin:tdq-workflow | NỀN | Không kích hoạt: nguồn ngoài là một URL tài liệu pytest đã biết, không cần SPA |
| tdq-browser-test | plugin:tdq-workflow | NỀN | Không kích hoạt: không có thay đổi UI trong phạm vi đợt 1 |
| 17 skill trên đĩa còn lại và các skill built-in về ảnh, tài liệu, bảng tính, trình chiếu, cài plugin | user/plugin/built-in | KHÔNG — khác lĩnh vực | Request sửa CLI Python và hợp đồng dữ liệu nội bộ, không tạo các loại artifact tương ứng |

### Môi trường và giới hạn khảo sát

- Nguồn hiện tại vẫn ở commit `3e0ef5f8a148cbf8aae1e932995e844e8f62ccd9`; chưa sửa source trong request này.
- Python cục bộ `3.13.15`, pytest `9.1.1`, pytest-xdist `3.8.0`. Không có `pyproject.toml` hoặc `requirements-test.txt` ở root; CI thực tế nằm trong `.github/workflows/test.yml`.
- CI hiện chạy `unittest` trên Windows/macOS/Linux và Python 3.11/3.13, không cài pytest hoặc công cụ ngoài. Không được biến pytest thành dependency bắt buộc của đường chạy tuần tự.
- Đã đọc toàn bộ `docs/kien-truc.md`. Phần mô tả đầu tài liệu còn nhãn nháp; không tự nâng toàn bộ thành luật đã được duyệt. Giữ các quyết định đã chốt có liên quan: scripts không import hooks, state chỉ ghi qua CLI, test cuối theo các cổng QC hiện có, và nhánh request quay về dev.
- Preflight đã đạt 8/8 bậc và smoke 3/3; LSP Python qua MCP trả 3 tham chiếu cho mẫu kiểm hiệu ứng; graph đã làm mới. Bằng chứng còn hiệu lực khi `init` request.

### Đối chiếu vùng chạm ba chiều

| Vùng file chạm | Phát hiện qua lớp nào (Grep/LSP/Graphify) | Tác động & quan hệ |
|---|---|---|
| `scripts/tdq_timing.py` | Grep, LSP outline và references, Graphify depth 2 | `_giay_model` → `tong_hop` → bảng Markdown/đồng hồ/sổ timing; LSP `tong_hop` trả 3 tham chiếu |
| `scripts/token_audit.py`, `scripts/step_audit.py` | Grep, LSP references, Graphify depth 2 | `default_transcript_dir` có 8 tham chiếu; dùng bởi token audit, step audit, timing và bước đóng sổ của state |
| `scripts/tdq_test.py` | Grep, LSP outline/references, Graphify depth 2 | `ban_kinh` → `cmd_vung_cham`; `chay_tron_bo` → `cmd_tron_bo` → sổ test và phép đếm bỏ sót; LSP runner trả 2 tham chiếu |
| `scripts/tdq_state.py`, `scripts/tdq_finish.py` | Grep và đọc caller, đối chiếu LSP | State import timing muộn để tránh vòng import; finish gọi CLI timing bằng subprocess. Cần giữ đóng sổ một lần và không làm init lỗi vì thống kê |
| `tests/test_timing.py`, `tests/test_token_audit.py`, `tests/test_step_budget.py` | Grep và đọc fixture | Một số test đang khẳng định khoảng assistant là thời gian model; cần thay fixture theo hợp đồng số đo đúng, không đơn giản xóa test đỏ |
| `tests/test_tdq_test.py`, `tests/test_next_tron_bo.py`, `tests/test_tdq_finish.py`, `tests/test_archify_finish.py` | Grep và đọc consumer/fixture | Khóa CLI, verdict, sổ test, ngân sách full suite và tích hợp finish; test parallel hiện mới kiểm exit code, chưa khóa đầy đủ tên module |
| `skills/tdq-build/references/report-template.md`, `skills/tdq-status/SKILL.md` | Grep theo tên lệnh | Cần phản ánh đúng ý nghĩa cột thời gian; chỉ sửa diễn giải gắn với dữ liệu mới, không mở rộng thành viết lại luật toàn workflow |

Graphify được truy vấn bằng ID cụ thể: `scripts_tdq_timing_tong_hop`, `scripts_token_audit_default_transcript_dir`, `scripts_tdq_test_ban_kinh`, `scripts_tdq_test_chay_tron_bo`, đều depth 2. Graph không chứa test và không thấy đầy đủ lời gọi import muộn; đã bổ sung bằng LSP/grep. Kết quả “không thấy cạnh” không được dùng để kết luận không có ảnh hưởng.

### Tái hiện trên mã hiện tại

Chạy `python -X utf8 C:/Users/admin/AppData/Local/Temp/tdq-phase1-analysis.py`; script chỉ đọc source và tạo fixture ngoài repo. Kết quả được lưu tại [tdq-phase1-analysis.json](C:/Users/admin/AppData/Local/Temp/tdq-phase1-analysis.json). Đây là phép tái hiện baseline, không phải bản sửa hoặc QC triển khai.

| Mã | Trigger và nguyên nhân | Kết quả quan sát |
|---|---|---|
| E1 | `_giay_model` chỉ nhận mốc assistant, không có thông tin start/end của API hay tool | Khoảng 120 giây bị ghi 120 giây model; khoảng 360 giây bị ghi 0. Không đủ căn cứ xác định hai khoảng này là model hoặc chờ người dùng |
| E2 | Tên thư mục Claude sinh từ đường dẫn Windows không khớp thư mục thật | Đường sinh kết thúc bằng `projects/-Users-admin-Documents-Projects-ForAgentCode-TDQ-Workflow` không tồn tại; `projects/C--Users-admin-Documents-Projects-ForAgentCode-TDQ-Workflow` tồn tại |
| E3 | Parser kiểm token phải kết thúc `.py`, trong khi pytest trả node ID có `::` | Đưa output của test FAIL thực vào runner hiện tại: `ok=false`, `failed_modules=[]` |
| E4 | Phase implement dùng lựa chọn trực tiếp; `chay_module([])` trả True | Fixture core → facade → test: direct `[]`, transitive `[test_facade.py]`; CLI in `PASS — 0 modules tested`, exit 0; chạy pytest thật trên fixture trả exit 1 |
| E5 | Cùng fixture E4 xuất JUnit XML bằng pytest cục bộ | XML giữ `classname=tests.test_facade.TestFacade`, `name=test_value`, một failure; có thể lấy dữ liệu cấu trúc thay vì cắt token màn hình |

Tệp test trong fixture cố ý có lỗi để tái hiện. FAIL này không phải lỗi phát sinh do thay đổi source TDQ. Toàn bộ bằng chứng audit trước vẫn dùng được vì snapshot nguồn chưa đổi.

### Dữ liệu host và hướng xử lý đề xuất

1. Tách việc tìm log, đọc/chuẩn hóa sự kiện và tổng hợp khoảng thời gian. CLI hiện có vẫn là điểm vào; không dựng daemon, database hay dịch vụ telemetry mới.
2. Claude: ghép `api-request.id` với `assistant.requestRef`, chọn mốc phản hồi cuối của cùng request; ghép tool bằng ID trong từng session. Chỉ gọi đây là khoảng API quan sát, không phải thời gian GPU thuần.
3. Codex: đã đối chiếu lại metadata hai log đã khảo sát; `session_meta.cwd` đúng project. Log có `custom_tool_call`/`custom_tool_call_output` theo `call_id`, `task_started`/`task_complete`, nhưng không có cặp API start/end riêng. Có thể đo khoảng tool/turn có bằng chứng; thời gian model độc lập phải ghi chưa xác định khi thiếu dữ liệu.
4. Không dùng `turn duration - tool duration` để suy ra model, và không gọi mọi khoảng trống là chờ duyệt. Job nền chưa có mốc hoàn tất phải giữ trạng thái chưa đủ bằng chứng; không coi thời điểm host trả quyền điều khiển là thời điểm job đã xong.
5. Tính hợp khoảng, cắt theo cửa sổ request/phase, loại trùng ID, báo mức đầy đủ và số cặp chưa ghép. Phân biệt tổng tài nguyên thực thi với wall time; không cộng child với parent thành thời gian người dùng chờ.
6. Phân giải log theo host và project, giữ đường chỉ định tường minh. Codex phải lọc metadata project trước khi tổng hợp; không gộp phiên khác project hoặc suy từ mtime. Không sao chép nội dung hội thoại hay secret vào fixture được commit.
7. Dùng schema/version và nguồn đo rõ ràng; giữ khả năng đọc dữ liệu cũ, không viết lại sổ lịch sử. Số đo kiểu cũ phải mang nhãn ước lượng cũ khi trình bày, không trộn với số đo mới như cùng định nghĩa.
8. Đường pytest ưu tiên JUnit XML có sẵn, đọc bằng thư viện chuẩn; đường unittest lấy thông tin từ đối tượng kết quả. Chuẩn hóa status, test count, failures và mức đầy đủ; exit code, lỗi collection, report thiếu/hỏng và thông tin không ánh xạ được phải giữ trạng thái không đạt hoặc chưa đủ bằng chứng.
9. Phân biệt no-op chỉ sửa tài liệu/không có đầu vào với source thay đổi nhưng chọn rỗng. Trường hợp sau phải thử lựa chọn bắc cầu hoặc fallback rộng phù hợp; vẫn không có test thì báo thiếu bằng chứng, không in PASS. Lượt trực tiếp có test chỉ chứng minh phạm vi đã chạy; mốc QC dùng phạm vi bắt buộc hiện có. Không thêm bộ lập lịch mốc tích hợp mới của đợt 2–3 vào request này.

Đã đối chiếu [tài liệu pytest về JUnit XML](https://docs.pytest.org/en/stable/how-to/output.html#creating-junitxml-format-files): pytest có tùy chọn xuất XML. Kết quả E5 xác nhận định dạng thực trên phiên bản cục bộ, gồm classname thay vì giả định luôn có thuộc tính file. Chưa có nhu cầu nghiên cứu rộng hoặc tải thêm dependency; chỉ đọc URL đã biết nên không giao một vòng research nhiều truy vấn cho agent khác.

### Quyết định và các hướng không chọn

- Đã chốt phạm vi đợt 1, loại bugfix, pipeline full, ngôn ngữ tài liệu/chat tiếng Việt. Chuỗi máy, comment và docstring code theo tiếng Anh như repo hiện hành.
- Vòng scope: BỎ — người dùng đã chọn đợt 1 với phạm vi và DoD cụ thể từ báo cáo; bề mặt CLI, host, dữ liệu và tương thích đã suy ra được từ source/CI.
- Không chọn vá duy nhất regex `.py`: sửa được một triệu chứng nhưng không đủ bảo toàn thông tin collection/error và output thiếu.
- Không chọn quy mọi khoảng assistant ngắn thành model hoặc mọi khoảng dài thành idle; không có căn cứ trong log.
- Không chọn chuyển cả runner sang pytest: phá điều kiện CI sạch chỉ dùng thư viện chuẩn. Không tăng worker hoặc thêm cơ chế reuse ở request này.
- Không chạy lại toàn suite trong analyze: source chưa đổi; phép tái hiện nhỏ đã chứng minh nguyên nhân, và audit trước có baseline 389 test. Trọn suite được thực hiện đúng giai đoạn QC nếu mức QC chọn yêu cầu.
- Mức QC đã chốt: người dùng trả lời `1a` cho câu hỏi QC, chọn Full. Đã ghi vào state qua CLI; lựa chọn này không phải phê duyệt spec hoặc plan.
- Trong spec bổ sung nhãn quy thuộc phiên: lọc đúng project chưa chứng minh mọi phiên trong cùng cửa sổ thuộc riêng request. Khi không có liên kết session tường minh, ghi `project_window`, không khẳng định quy thuộc độc quyền.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Analyze và tái hiện nguyên nhân | CÓ — đã làm | Đối chiếu ba chiều, consumer, log host, CI và fixture lỗi |
| Research bổ sung diện rộng | BỎ | Đã có audit và tài liệu pytest chính thức; hiện không còn câu hỏi ngoài repo cần nhiều truy vấn |
| Spec | CÓ | Dùng tdq-spec chốt hợp đồng dữ liệu, ranh giới adapter/tổng hợp/runner, tương thích và DoD với QC Full |
| Sơ đồ thiết kế HTML | CÓ | Dùng Archify dựng preview có nhãn dự kiến và manifest gắn với spec; không coi là mã đã triển khai |
| Plan | CÓ | Sau duyệt spec; chia task kèm test đỏ → xanh và vùng ảnh hưởng thực |
| Implement | CÓ | Sau duyệt plan; thực hiện đúng đợt 1, giữ log và bằng chứng theo task |
| Chia việc phát triển cho agent | BỎ ở spec | Cách thực thi do người dùng chốt sau plan; lựa chọn đó chỉ đổi người thực hiện, không đổi DoD |
| QC: DoD và kiểm hồi quy | CÓ | QC Full: DoD, toàn suite, vùng chạm, kiến trúc và clean code; dùng tdq-build |
| Smoke/runtime và QC độc lập | BỎ | QC Full không thêm các vòng kiểm này; vẫn phải kiểm đủ hành vi của DoD bằng fixture/unit test |
| Browser/visual QC sản phẩm | BỎ | Không sửa UI sản phẩm; preview Archify được kiểm riêng khi sinh spec |
| Benchmark A/B tăng tốc toàn workflow | BỎ | Thuộc đợt 3; đợt 1 ưu tiên độ đúng, không hứa giảm 20% runtime |
| Report và bàn giao | CÓ | Báo thay đổi, test, giới hạn dữ liệu, tương thích và phương án quay lui |

## Hỏi đáp

### Đã trả lời

| Câu hỏi / quyết định | Phương án đã đưa | Trả lời nguyên văn | Kết quả ghi nhận |
|---|---|---|---|
| Mở request cho đợt nào? | Đợt 1 của lộ trình ba đợt đã trình bày trong chat | `okay hãy note lại và mở request làm đợt 1` | Chỉ triển khai đợt 1, ghi note cả lộ trình |
| Chọn pipeline? | 1A: chuyên sâu; 1B: nhanh | `1a` | `lane=full`, tiếp nhận lúc 12:50 ngày 27/10/2026; loại bugfix giữ như đề xuất |
| Chọn mức QC? | 1A: Full; 1B: Lite; 1C: Ultra | `1a` | `muc_qc=full`, phase `spec`; không suy diễn thành duyệt spec/plan |
| Duyệt spec? | Spec v1.0, thiết kế preview và 7 DoD | `duyệt spec` | `spec_approved=true`, ghi qua CLI lúc 13:21:48 ngày 27/10/2026, Asia/Bangkok; chuyển phase `plan` |
| Duyệt plan? | 5 giai đoạn, 11 task, 7 DoD và QC Full | `duyệt plan` | `plan_approved=true`, ghi qua CLI lúc 13:49:57 ngày 27/10/2026, Asia/Bangkok; phase `mode`, chưa chọn cách thực thi |
| Chọn cách thực thi? | A: giao trợ lý; B: làm trực tiếp | `1a` | `implement_mode=subagent`, triển khai ngay theo nhóm; 7 task giao, 4 task người điều phối giữ |

### Trạng thái triển khai

Không còn câu hỏi cần chốt trước spec. Người dùng đã chọn Full cho cả pipeline và mức QC ở hai câu hỏi riêng.

Đã viết và được duyệt [spec v1.0](../spec/2026-10-27-1246-do-dung-bao-toan-loi.md) cùng [preview thiết kế](../spec/2026-10-27-1246-do-dung-bao-toan-loi-preview.html), đăng ký spec_file qua CLI. Giữ nguyên snapshot spec gắn manifest; trạng thái phê duyệt hiện hành nằm trong state CLI. Browser-check gốc của Archify gặp lỗi Chrome pipe Windows; đã kiểm bổ sung qua Chrome CDP và xem ảnh, desktop đọc rõ, mobile cần kéo/thu phóng. Chi tiết nằm ở [biên bản kiểm spec](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/spec-review.md).

Đã lập và được duyệt [plan đợt 1](../plan/2026-10-27-1246-do-dung-bao-toan-loi.md): 5 giai đoạn, 11 task, tổng ước tính công việc 85 phút; giữ 7 DoD và QC Full. Người dùng chọn `1a` cho cách thực thi, đã ghi `implement_mode=subagent` qua CLI và chuyển `implement`. Bản phân công đã qua audit: 7 task giao, 4 task người điều phối giữ; không trùng vùng file. Mô phỏng dùng hằng số cũ chỉ là cơ sở đề xuất, không phải ETA hay benchmark thực.

Lựa chọn chạy nhóm bao gồm nhánh/worktree riêng, commit task và hợp nhất nội bộ vào nhánh request sau khi kiểm; đây là thao tác cần thiết của cách chạy người dùng vừa chọn. Các commit nội bộ được liệt kê trong báo cáo. Commit bàn giao cuối, merge về `dev`, push và nâng bản plugin vẫn nằm ngoài bước triển khai hiện tại.

Ghi nhận điều phối: hook hiện so hash toàn bộ plan, nên chỉ đổi tick cũng làm bản đồ cũ. Đã dùng CLI `assign` và `audit` để đồng bộ sau tick; không tắt hook, không sửa luật trong request này. Đây là chi phí điều phối có thể xem xét ở đợt 2–3, không mở rộng phạm vi sửa đợt 1.

Ghi nhận thêm trong triển khai: không chạy `sweep --clean` khi còn task đang hoạt động, vì một worktree mới chưa có diff có thể bị hiểu là đã merge. Một lượt đã dọn nhầm worktree T2.2 khi agent mới chỉ đọc; đã mở lại cùng nhánh, không mất thay đổi. T1.2/T2.2 sau merge còn thư mục rỗng do daemon LSP giữ khóa; đã xác minh đúng cây tiến trình thuộc task hoàn tất, dừng riêng cây đó và xóa thư mục rỗng. LSP tra caller ở `tdq_state.py` có lượt treo; đã ghi giới hạn và dùng caller đã đối chiếu bằng grep. Không sửa các cơ chế điều phối này trong đợt 1.

T2.4 giữ nguyên phép tính step/token/cost, chỉ sửa nhãn và cách diễn giải. `tdq_finish` lần đầu báo R13 stale vì bản cache không thấy tokenizer của checkout; đã đặt `TDQ_TOKENS_VENV` riêng cho tiến trình để dùng `.venv-tokens/Scripts/python.exe` sẵn có. Lượt sau đếm thật 58 file và lint đạt; không cài dependency hay dùng ước lượng ký tự. `docs/tdq/token-budget.json` là đầu ra sinh tự động của bước finish đã có trong plan. Master architecture vẫn stale từ trước, được giữ nguyên giới hạn.
