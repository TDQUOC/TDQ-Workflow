# Brief — Test theo tính năng, ít nhưng có giá trị, hạn chế chạy lặp
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay hãy mở request xử lí lại test của tdq-worklflow, là sẽ chỉ tạo những test case cần thiết, không spawm test (focus vào chất lượng thay vì số lượng), cố gắng test ít nhất, và focus và case thực tế est theo feature + simulation data + smoke budget và sắp xếp trước khi test và hạn chế 1 bài test làm lại nhiều lần

Đọc đầu:
- Tái tổ chức cách TDQ chọn, tạo và chạy test; chất lượng phát hiện lỗi quan trọng hơn tổng số case.
- Gom theo tính năng và hành vi thực tế; dùng dữ liệu mô phỏng có kiểm soát, đầu vào và kết quả mong đợi rõ ràng.
- Lập danh sách test và thứ tự chạy trước khi thực thi. Chọn bộ nhỏ nhất đủ kiểm chứng thay đổi và rủi ro liên quan.
- Smoke budget xét số scenario và thời gian; khoảng 100–200 từng thảo luận là định hướng, chưa phải trần cứng cho toàn repo.
- Rà test trùng/ít giá trị trước khi gộp hoặc bỏ; không đổi tên/gộp hàng nghìn case dưới một test để làm đẹp số.
- Hạn chế chạy lại test không đổi giữa implement, QC, review và release. Chỉ tái dùng kết quả khi nguồn, phụ thuộc, dữ liệu, môi trường và phạm vi còn phù hợp; lỗi hoặc bằng chứng thiếu phải chạy lại có lý do.
- Bảo toàn test an toàn, mất dữ liệu, quyền truy cập và hồi quy quan trọng. Không thay hành vi thật bằng mock luôn trả thành công.
- Tận dụng runner, manifest, receipt, lựa chọn vùng chạm và cơ chế reuse đã có; chưa quyết định thêm framework hoặc cấu hình mới.
- Cần khảo sát riêng test của TDQ và luật TDQ hướng dẫn agent viết test cho project khác.
- Phân biệt số test cha, parameterized cases, subtests và scenario nghiệp vụ. Không cộng các lượt chạy lại thành số case duy nhất.
- Số 3.811 case/25 lỗi trước đó đến từ pytest chạy không giới hạn thư mục. Không dùng số đó làm baseline của runner TDQ vốn chọn `tests/`.
- Ultracode đang bật: điều phối khảo sát/review hữu hạn, chia vùng không trùng; không cho nhiều agent cùng chạy một suite.
- Chưa sửa/xóa test, chưa chạy full suite; chờ chốt pipeline trước khi init state và mở nhánh.

## Hiểu & kiến thức

### Năng lực dùng được

Kiểm kê 2026-11-05: `skill_inventory.py --loc` giữ 11 skill TDQ liên quan/đang bật; đã xét thêm built-in `workflow-authoring`, `run`, `code-review`, `simplify` theo inventory phiên.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `tdq-intake`, `tdq-spec`, `tdq-plan`, `tdq-build`, `tdq-conventions` | plugin:tdq-workflow | NỀN | Pipeline full và luật về test/QC. |
| `tdq-lean` | plugin:tdq-workflow | DÙNG | Soi test thừa, trùng, không đo hành vi; chỉ đề xuất xóa có chứng cứ. |
| `workflow-authoring` | built-in | DÙNG | Phối hợp khảo sát/review độc lập theo subsystem; không nhiều agent chạy cùng suite. |
| `tdq-browser-test` | plugin:tdq-workflow | KHÔNG | khác lĩnh vực — request không đổi UI; smoke CLI của TDQ đo qua CLI/fixture, không tạo login/UI giả. |
| `tdq-setup` | plugin:tdq-workflow | NỀN | Kiểm kết nối LSP; hiệu ứng theo module Python đã chứng minh bằng `find_references symbols=3`, `ghi-kiem python:. 3`. |
| Các skill còn lại (bao gồm `run`, `simplify`, `code-review` trong inventory phiên) | plugin/built-in | KHÔNG | khác lĩnh vực ở pha phân tích; đánh giá lại khi spec chốt vùng chạm. |

### Hiện trạng đo được (không lấy số test làm thước đo chất lượng)

- Có 193 module `tests/test_*.py` trong `tests/`. Receipt full lưu từ request 2026-11-03 ghi 4.161 node ID duy nhất, 10 skipped, ~1.280 giây; đó là kết quả lịch sử, không phải suite đã chạy cho request này. Subtest là bằng chứng con, không tự động thành scenario nghiệp vụ độc lập.
- `scripts/tdq_test.py vung-cham` chọn theo path, nhắc module, reverse import qua AST và test quét thư mục; `ban_kinh` rơi về full khi số module chọn ≥60% hoặc thông tin thiếu. Ở `implement`, đường chọn trực tiếp khác `qc`; không thể coi chỉ chạy direct là đủ cho rủi ro xuyên module.
- `scripts/tdq_test.py tron-bo` chạy pytest hai lượt: collect manifest rồi execute/JUnit/sidecar; thiếu/trùng/lệch ID hoặc process lỗi → `INCOMPLETE`. `--reuse auto` là opt-in và yêu cầu `docs/tdq/reuse-policy.json` khai dependency hợp lệ; file policy này hiện không tồn tại. Mặc định `--reuse off`, final correctness yêu cầu fresh. `so` chỉ đếm, không cấm quá ngân sách.
- Chính sách deep `full/ultra`: QC-F1 phải chạy trọn bộ, QC-F2 kiểm vùng chạm, thêm full sau vòng fix cuối; express chỉ chạy task/DoD, không full suite. `vision-test-loop.md` bắt tối thiểu 1 happy-path + 2 boundary + 1 failure/recovery cho mỗi feature; đây là quy tắc số tình huống, chưa chứng minh mỗi tình huống có giá trị.
- CI hiện dùng `python -m unittest discover tests` trên 3 OS × 2 Python, không phải pytest runner; thay đổi lựa chọn test chỉ trong `tdq_test.py` không đổi lịch CI. Chạy `python -m pytest --collect-only -q` ở root đã gặp 25 lỗi collection vì pytest quét cả bản backup dưới `docs/`; KHÔNG coi 3.811 node root thu trước lỗi là mẫu số hợp lệ. Chạy lại toàn bộ suite chỉ sau khi có kế hoạch và phạm vi đủ an toàn.
- Repo TDQ là công cụ workflow, không có tính năng login sản phẩm; ví dụ login với user giả chỉ là nguyên tắc dùng cho project có login, không tạo fixture login giả trong TDQ. Không gộp test con hoặc bỏ regression cần thiết chỉ để đẹp số.
- Nguồn bên ngoài: [pytest markers](https://docs.pytest.org/en/stable/how-to/mark.html), [cache `--lf`/`--ff`](https://docs.pytest.org/en/stable/how-to/cache.html), [fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html), [Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html). Marker chọn nhóm, `--lf` chỉ chạy lỗi cũ và không thay full; factory fixture cách ly dữ liệu mô phỏng; scope rộng dễ rò trạng thái. Chưa có số đo chứng minh 100–200 scenario bắt đủ rủi ro TDQ.

### Lộ trình đề xuất (deep ultracode)

| Bước/phase | CÓ/BỎ | Vì sao |
|---|---|---|
| analyze: Workflow khảo sát + phản biện theo ba vùng | CÓ — hoàn tất | Runner, luật và inventory được kiểm riêng; không dùng số case làm KPI. |
| research bên ngoài, CI/trường hợp pytest | CÓ — đã đối chiếu | pytest markers/cache/fixtures là khả năng, không coi là bằng chứng tăng chất lượng. |
| spec → plan: rà tác động và duyệt hai cổng | CÓ | Đổi luật viết test và lịch QC cần user chốt. |
| review spec và plan độc lập | CÓ | Chống mất test an toàn và cổng hồi quy trọn bộ. |
| implement: mã nguồn + luật + test chọn vùng | CÓ, chỉ sau duyệt plan | Ưu tiên cơ chế hiện có; chưa thêm dependency/CI change. TDQ giữ độc quyền state, Git, worktree. |
| QC dựa DoD, full fresh cuối và kiểm thực tế | CÓ | Smoke nhanh không thay full; sửa sau verdict thì chạy lại phần bị ảnh hưởng. |
| report Markdown + Archify HTML | CÓ | Ghi trước/sau, case chạy/chưa chạy, mục tiêu thời gian đạt/chưa đạt. |
| Workflow implement song song | BỎ nếu vùng chạm chung | Runner, rule và test có file nóng; tránh nhiều tác giả hoặc test runner chạy chồng. |

### Tam giác khảo sát và vùng chạm

| Vùng file | Phát hiện qua lớp nào | Tác động, quan hệ |
|---|---|---|
| `scripts/tdq_test.py`, `tdq_test_manifest.py`, `tdq_test_receipt.py`, `tdq_test_result.py` | LSP + Graphify affected 2 bước + Grep | Chọn case, chống bỏ sót, receipt và số lượt; nhiều test runner/module phụ thuộc; sửa phải giữ identity/provenance. |
| `skills/tdq-build/references/qc.md`, `runtime-speed.md`, `vision-test-loop.md`, `SKILL.md`, `skills/tdq-intake/references/quick-lane-qc.md` | Grep/Read; Graphify bỏ `skills` | Luật minimum scenario, cổng full, reuse và mức QC; đổi cần duyệt rõ, không âm thầm hạ chất lượng. |
| `tests/test_tdq_test*.py`, `tests/test_runtime_contracts.py`, `.github/workflows/test.yml` | LSP find_references + Grep/Read | Kiểm runner, CI unittest khác pytest, các ca chứng minh selection/receipt; giữ red/negative/permission. |
| `docs/tdq/reuse-policy.json`, `docs/kien-truc.md` | kiểm tồn tại + Read | Policy reuse chưa tồn tại; kiến trúc nháp ghi hai cổng full, đối chiếu skill hiện hành trước khi đổi. |

**Phạm vi đã chốt theo câu trả lời `1ab 2a cho full và b cho ultra, chỉ là redcommend có thể nới ở ultra`:** Rà test/runner của repo TDQ **và** luật TDQ hướng dẫn agent viết test cho project khác. Không đổi CI trong request này. Mục tiêu đề xuất cho smoke: QC `full` ≤5 phút; QC `ultra` ≤10 phút và có thể nới nếu test cần cho chất lượng. Đây là mục tiêu đo, không phải quyền bỏ case quan trọng.

### Phạm vi đã chốt

- Mặt CHỌN: chất lượng case theo feature và dữ liệu mô phỏng; hiệu năng chọn/chạy smoke; kiểm chứng giữ test quan trọng trong repo TDQ và luật cho project khác.
- Mặt LOẠI: thay đổi CI (`.github/workflows/test.yml`), ép trần 100–200 case trên toàn repo, xóa test để đạt số đẹp.
- Bối cảnh: 193 module, 4.161 nodeid trên receipt lịch sử; CI 3 OS × 2 Python hiện riêng; chưa có mục tiêu số phút toàn suite hay baseline smoke hiện tại.
- Mức đầu tư suy ra: đầy đủ — tác động cổng chất lượng và nhiều project downstream; mục tiêu ≤5 phút `full`, ≤10 phút `ultra` mới là khuyến nghị cần đo, không là trần cứng.

**Quyết định đã chốt trước Spec:** Ngân sách đề xuất ≤5 phút (`full`) và ≤10 phút (`ultra`) chỉ áp dụng **bộ smoke**, không thay cổng hồi quy trọn bộ. Đặt một lượt full `--fresh --reuse off` ở cổng QC cuối, tránh gọi full sớm/lặp khi nguồn không đổi; sau sửa đổi phải chạy lại kiểm chứng bị ảnh hưởng và full nếu thay đổi có thể làm mất hiệu lực verdict cuối. Không dùng receipt cũ thay cổng QC cuối. Giữ manifest/đối chiếu case ID, fallback khi selection không đầy đủ và không thay CI. Giới hạn theo thời gian chỉ được báo đạt/trượt với số đo trên cùng máy; không cắt test an toàn hay âm thầm tăng trần QC đã duyệt. Mức QC của request này: `ultra` theo lời user `1a`.

## Hỏi đáp

- User chốt pipeline: `1a ultracode` (deep + orchestration).
- Vòng scope: `1ab 2a cho full và b cho ultra, chỉ là redcommend có thể nới ở ultra` — chọn A (repo TDQ), B (luật cho project khác), không chọn C (CI); mục tiêu smoke `full` ≤5 phút, `ultra` ≤10 phút linh hoạt để không giảm bảo vệ.
- Vòng chi tiết: `1a 2a` — mục tiêu thời gian chỉ dành cho smoke; một lượt full fresh tại cổng QC cuối, không tái dùng receipt cũ thay verdict cuối.
- Mức QC cho request: `1a` — `ultra`; full suite cuối còn nguyên, smoke/runtime thực và review độc lập.
