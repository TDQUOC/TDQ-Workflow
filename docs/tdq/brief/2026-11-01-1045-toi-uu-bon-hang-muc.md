# BRIEF — Tối ưu bốn hạng mục sau báo cáo QC
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

“okay vậy hyax  mở request update cả 4 đi”

Hiểu ban đầu: mở request mới để triển khai cả bốn đề xuất đã phân tích từ báo cáo `2026-10-27-1846-kiem-chung-tang-toc`.

1. Kiểm đầu vào calibration trước các vòng đo: định dạng mẫu nhập tay, log và điều kiện thiếu mẫu có thể xác định sớm; giữ nguyên hợp đồng số mẫu/provenance và không sinh output nửa vời khi lỗi.
2. Điều tra và xử lý timeout của `_kiem_song`: test timeout2s đã ghi30,16s. Cơ chế process con `.cmd`/pipe trên Windows là giả thuyết cần xác nhận; kiểm deadline và cleanup process thuộc job, giữ hợp đồng CODEX_HOME.
3. Giảm công việc lặp trong test: tách kiểm parser/schema/công thức/log khỏi các vòng dựng repo/worktree/calibration không cần thiết. Giữ các assertion và các kiểm có mục đích process thật, cleanup, provenance, chống giả evidence.
4. Tự động thêm bảng Top20 case/module chậm nhất từ duration trong evidence hiện có; gắn nguồn, phân biệt tổng duration case với wall clock và không đếm trùng subtest.

Nguồn ban đầu: báo cáo Full ngày31/10, 3594PASS/8skip, runner wall1117,67s; thời gian các case trong bốn file chậm nhất là434,676s, chiếm39,24% tổng case phases. Đây là dữ liệu lịch sử để chọn vùng khảo sát, không phải cam kết tăng tốc.

Phạm vi đề xuất không bật mặc định worker2 hoặc cache, không tự khởi động lại benchmark D9/D10 đã bỏ qua. User đã yêu cầu commit/merge phần cũ rồi mở nhánh mới. Trạng thái thực hiện được ghi bên dưới; không push và chưa được phép triển khai trước gate spec/plan.

## Hiểu & kiến thức

Pipeline chuyên sâu đã được chọn bằng “1a 2b commit merge và mở nhanhs”. Phần cũ đã commit `4cefc13`, merge về nhánh gốc `6ca709e`, rồi về `dev` bằng `6c00d6e`. Không push. Nhánh request mới: `codex/toi-uu-bon-hang-muc`, gốc `dev`; prefix theo quy ước của host Codex. Không mang theo mã nguồn chưa commit của request trước.

### Năng lực dùng được

| Công cụ/skill | Kết luận |
|---|---|
| tdq-intake, tdq-conventions, tdq-setup | Dùng cho intake/state, kiểm môi trường và khảo sát |
| tdq-spec, tdq-plan, tdq-build | Dùng theo các gate sau khi chốt QC |
| tdq-lean | Tham chiếu khi tách test, tránh thêm framework chỉ để tối ưu |
| tdq-status, tdq-check-status | Không cần recovery; state đã kiểm trực tiếp |
| tdq-browser-test | Dùng nếu đầu ra HTML tự động được đưa vào spec; kiểm kết nối trước |
| tdq-browser-research | Không cần scraping; tài liệu kỹ thuật chính thức đã tra ở lượt phân tích trước |
| MCP LSP | Kết nối đã xác nhận bằng start_lsp và find_references |
| Graphify/Grep | Dùng tìm liên kết và kiểm source; graph cảnh báo freshness, không suy completeness từ graph |
| Các skill tài liệu/vẽ/Sites/Figma/media | Không áp dụng: đây là thay đổi repository Python/test/report |

Đã đọc toàn bộ hồ sơ `docs/kien-truc.md`: phần đầu còn ghi NHÁP, giữ các quyết định đã chốt; không import hooks từ scripts, state chỉ ghi qua CLI, không dựng framework mới. Kiến trúc hiện có: CLI Python, pytest/unittest, process ownership adapter, manifest/result/receipt; report cũ là artifact Markdown/HTML gắn SHA.

### Đối chiếu vùng chạm

| Vùng file chạm | Phát hiện qua lớp nào | Tác động & quan hệ |
|---|---|---|
| scripts/tdq_bench.py; tests/test_bench.py | Grep/read + LSP references + Graphify affected depth2 | lenh_thuc_do được CLI dispatch; hiện kiểm mẫu/log sau vòng đo. Chỉ dời kiểm có thể xác định sớm, giữ số mẫu/provenance |
| scripts/tdq_codex.py; scripts/tdq_test_process.py; tests/test_codex_cli.py | Grep/read + LSP references + Graphify affected depth2 | _kiem_song → check → cli. Phải xác nhận nguyên nhân timeout bằng repro, giữ CODEX_HOME/argv/env và chỉ cleanup job sở hữu |
| tests/test_tdq_test.py; tests/test_team_mode.py; tests/test_tdq_runtime_bench.py | Grep/read + duration evidence | Giảm dựng repo/subprocess lặp chỉ với kiểm dữ liệu thuần; giữ integration thật, assertions, case identity và failure coverage |
| scripts/tdq_test_manifest.py; scripts/tdq_test_result.py; scripts/tdq_test.py; report output | Grep/read + bằng chứng result JSON | phases có duration_seconds; cần tổng hợp case/module, thứ tự ổn định, không cộng subtest trùng, không gọi tổng case duration là wall |

Baseline lịch sử đã xác minh SHA result ở lượt phân tích trước: wall1117,674585s; execute1112,446065s; collection2,223637s; verify1,856974s. Không dùng tổng99giờ lịch sử để quy CPU/model. Top20 là tổng hợp dữ liệu đã có, không yêu cầu chạy lại benchmark để hiển thị.

Vòng scope: BỎ — người dùng đã chọn đúng bốn đề xuất cụ thể và phạm vi file/đầu ra đã được khảo sát; không thay đổi worker/cache mặc định hoặc mở lại benchmark cũ.

Đề xuất đầu ra hạng mục4: dữ liệu Top20 case/module trong JSON, bảng CLI và nội dung tái dùng cho report Markdown/HTML. Thiếu duration phải ghi unavailable/partial, không tự suy là0. Không chạy test lại chỉ để sinh report. Chi tiết entrypoint/schema sẽ được trình trong spec.

Tài liệu đã tra ở lượt phân tích: pytest usage/profiling, pytest-xdist known limitations, Python subprocess. Nghiên cứu ngoài bổ sung: bỏ ở bước này vì giả thuyết Windows sẽ được xác minh bằng repro cục bộ; không cần model, tài khoản hoặc cài thêm dependency.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Analyze | CÓ | Chốt QC và hợp đồng từng hạng mục |
| Nghiên cứu mới ngoài repo | BỎ | Có source và tài liệu chính thức từ phân tích trước; cần repro cục bộ |
| Spec → plan | CÓ | Hai gate duyệt riêng của pipeline chuyên sâu |
| Chọn main/subagent | CÓ | Hỏi sau duyệt plan; không kế thừa mode request trước |
| Implement | CÓ | RED/GREEN vùng chạm; không nới assertion/guard |
| QC độc lập/runtime | CÓ | User chọn ultra bằng “a”; mỗi smoke/runtime có cap120s |
| Benchmark D9/D10 cũ | BỎ | User đã bỏ qua; request mới không mở lại phép đo đó |
| Report | CÓ | Trước/sau có provenance, ghi rõ giới hạn số đo |

## Hỏi đáp

- Pipeline: user chọn1a, chuyên sâu.
- Dirty work: user chọn2b và yêu cầu “commit merge và mở nhanhs”; đã commit/merge phần cũ rồi mở nhánh mới từ dev, không push.
- Phạm vi: cả bốn đề xuất, giữ worker1/cacheoff và integrity guard; không commit/push phần triển khai mới nếu chưa có yêu cầu tiếp.
- Mức QC: user chọn “a”, tương ứng ultra; đã ghi state. Viết spec để duyệt, chưa viết plan hoặc sửa source triển khai.
