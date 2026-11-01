# Kiểm chứng toàn bộ các đợt và đề xuất tăng tốc runtime
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> mở reqeust thực hiện toàn bộ các đợt check và sau đó cung cấp đè xuất improve runtime speed cho tôii

Cách hiểu ban đầu: mở request kế tiếp để kiểm chứng toàn bộ ba đợt đã đề xuất, đo chất lượng và runtime, rồi cung cấp phương án cải thiện tốc độ có bằng chứng. Các thay đổi production, nếu cần để kiểm chứng, phải được mô tả rõ trong spec và plan được duyệt; không tự biến mọi phương án thử nghiệm thành mặc định.

Phạm vi dự kiến:

1. Chất lượng test: inventory từng case, skip trên Windows/POSIX, tokenizer, fixture tmp_path, isolation HOME/basetemp, timeout và dọn worker. Tái hiện lỗi; xác định và kiểm chứng cách sửa.
2. Tránh công việc lặp: thử nghiệm receipt/fingerprint, invalidation, dùng chung job trùng, readiness cache và batch thao tác độc lập. Có ca đối chứng đổi đầu vào, kết quả lỗi/thiếu và tình huống đồng thời.
3. Tốc độ thực thi: benchmark serial với 2 worker sau khi đủ điều kiện; kiểm chứng cache transcript trên dữ liệu append/truncate/replace/delete và chất lượng partial/unknown. Phân biệt thử nghiệm mô hình với implementation thật.
4. Báo cáo cuối Markdown và HTML: hiện trạng, lỗi và giới hạn còn lại, test/evidence, số đo trước–sau, mức tin cậy, thứ tự triển khai, DoD và phương án quay lại. Phân biệt wall time với tổng thời gian tài nguyên.

Pipeline full đã được người dùng chọn bằng `1a`; loại request bugfix vì cần xử lý các khoảng trống test/runner trước khi đánh giá tối ưu. Request đã khởi tạo lúc 19:02 ngày 27/10/2026, phase analyze.

Ranh giới ban đầu: không commit/merge/push, không phát hành/cài bản plugin mới, không đổi mặc định parallel/cache khi chưa đạt tiêu chí được duyệt. Benchmark phải bảo vệ cấu hình thật và giữ cả kết quả FAIL/ERROR.

## Hiểu & kiến thức

Nguồn kế thừa: [review chi tiết](../reports/2026-10-27-1246-do-dung-bao-toan-loi-test-review.md).

- Kết quả review trước: collection 3.306 case; bổ sung 16 case bỏ sót được 15 pass/1 skip; tổng evidence chuẩn có 13 skip. Không phải tất cả đường chạy đều đạt.
- Parallel smoke: tắt tmpdir gây thiếu tmp_path; cùng case giữ plugin thì pass. Chưa có Full parallel đạt.
- Tokenizer: venv Windows có thư viện nhưng sáu test skip sai đường dẫn; chạy assertion trực tiếp được 5 pass/1 fail, case fail phụ thuộc số nhóm plugin cài trên máy.
- Full gần nhất mất 688,269 giây trên HEAD d1b90b825596e84aba7136b02a545bc2fa06c21a. Đây là baseline lịch sử, không phải cam kết mức tiết kiệm.
- Mục tiêu A/B đề xuất: ít nhất ba cặp đảo thứ tự; cùng nguồn/env/node IDs; không tăng lỗi/skip/race; median giảm ít nhất 20% mới cân nhắc bật 2 worker. Mục tiêu chưa được duyệt và chưa đạt bằng chứng.
- Preflight 18:47 ngày 27/10/2026: setup và lsp check exit 0; 8/8 bậc đạt, smoke 3/3. Setup cập nhật shim/instruction theo cơ chế hiện tại. Một nợ đã biết: instruction nhắc mem0-memory nhưng máy không có skill này.
- Request trước 2026-10-27-1246-do-dung-bao-toan-loi được lưu tại [snapshot state](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/previous-request-state.json), gồm các approval cũ và phase report. Không chuyển approval sang request mới.
- Đã mở nhánh bugfix/kiem-chung-tang-toc từ bugfix/do-dung-bao-toan-loi; nhanh_goc ghi đúng nhánh cha. Đây là request kế thừa chưa merge, không mở từ dev vì cần giữ bản sửa đợt trước. Việc tích hợp về dev phải xử lý cả nhánh cha khi được cho phép; chưa commit/merge/push.
- Working tree trước đổi nhánh chỉ có tài liệu/log/graphify; không có source dirty. Tài liệu cũ được mang theo.

### Năng lực dùng được

Inventory trên đĩa: 28 skill, bộ lọc giữ 11 skill TDQ và ẩn 17 skill; đã xét thêm catalog trong context. Không cần dịch vụ trả phí hoặc tải model để kiểm chứng Python/pytest hiện tại.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | Mở request, phân tích và phỏng vấn |
| tdq-conventions | plugin:tdq-workflow | NỀN | State, approval, log, giới hạn phase |
| tdq-setup | plugin:tdq-workflow | NỀN | Preflight đã đạt; không lặp setup khi chưa có thay đổi |
| tdq-spec | plugin:tdq-workflow | NỀN | Đầu ra, hợp đồng chất lượng, ngưỡng và fallback |
| tdq-plan | plugin:tdq-workflow | NỀN | Task, test và thứ tự triển khai |
| tdq-build | plugin:tdq-workflow | NỀN | Thực hiện và QC sau duyệt plan |
| tdq-lean | plugin:tdq-workflow | NỀN | Soát độ phức tạp của cache/runner mới |
| tdq-browser-test | plugin:tdq-workflow | NỀN | Kiểm báo cáo HTML cuối; preflight browser tại lúc sử dụng |
| tdq-browser-research | plugin:tdq-workflow | NỀN | Chỉ cần nếu nguồn nghiên cứu đòi SPA; hiện dùng tài liệu chính thức tĩnh |
| tdq-status | plugin:tdq-workflow | NỀN | Báo trạng thái khi được hỏi |
| tdq-check-status | plugin:tdq-workflow | NỀN | Phục hồi khi chuyển phiên; không lặp khi state đã biết |
| 17 skill khác trên đĩa và các skill artifact/app trong context | user/plugin/context | KHÔNG | Khác lĩnh vực; chưa có yêu cầu tài liệu Office, thiết kế Figma hoặc thao tác dịch vụ ngoài |

### Đối chiếu vùng tác động và môi trường

Môi trường xác minh: Python 3.13.15, pytest 9.1.1, pytest-xdist 3.8.0; Windows. Hồ sơ docs/kien-truc.md đã đọc: phần tầng vẫn ghi NHÁP, các quyết định lịch sử giữ nguyên; không nâng bản nháp thành quy tắc đã duyệt.

| Vùng file chạm | Phát hiện qua lớp nào | Tác động & quan hệ |
|---|---|---|
| scripts/tdq_test.py; scripts/tdq_test_result.py | Grep + đọc định nghĩa; Graphify hai bước | chay_tron_bo_result được chay_tron_bo và cmd_tron_bo gọi. Backend pytest tắt tmpdir, dùng auto workers; subprocess.run chưa truyền timeout. Cần kiểm tương thích wrapper, ledger và parser kết quả. |
| tests/test_tdq_test.py; tests/test_team_chong_conflict.py; tests/test_archify_artifacts.py | Grep, evidence review trước | Regression runner, module trộn unittest/pytest và fixture tmp_path thật. Không chỉ bổ sung module thiếu. |
| tests/test_skill_tokens.py; tests/helper.py; scripts/skill_tokens.py | Grep + đọc source | tests/helper.py đã có co_bo_dem_token sử dụng API thật và venv của production. Tái sử dụng helper thay vì thêm cách dò venv thứ ba; fixture inventory phải xác định. |
| scripts/tdq_transcript.py; scripts/tdq_timing.py; tests/test_transcript.py | Grep + Graphify hai bước | read_transcripts → caller tong_hop → main của timing. Giữ semantics quality/partial/unavailable và ghép span khi thử cache. |
| scripts/tdq_finish.py; scripts/tdq_setup.py; scripts/tdq_lsp.py; hooks/scripts/session_start.py | Evidence trước và tìm kiếm tên chính xác | Consumer kết quả, readiness và cô lập môi trường; chỉ sửa khi thuộc phạm vi được chốt. |
| Receipt/fingerprint/cache/job dùng chung mới | Khoảng trống thiết kế | Cần thử nghiệm invalidation, concurrency, timeout, trạng thái lỗi và chi phí xác minh; chưa có bằng chứng đủ để bật mặc định. |

LSP start_lsp Python thành công. Truy vấn blast_radius hai file có transitive chưa trả kết quả trong thời gian dành cho phân tích nên đã dừng chờ; truy vấn find_references hẹp cũng chưa trả kết quả trước khi dừng chờ. Không coi đây là bằng chứng không có caller. Cần chẩn đoán khả năng timeout/readiness khi triển khai; kết quả hiện tại dựa trên source và graph, chưa có xác nhận caller bằng LSP.

Graphify CLI hiện tại không hỗ trợ affected (chỉ trả hướng dẫn); đã đọc graph.json, lọc cạnh calls và duyệt ngược đúng hai bước. Graph built_at_commit khớp d1b90b825596e84aba7136b02a545bc2fa06c21a. Kết quả: chay_tron_bo, cmd_tron_bo, tong_hop ở bước 1; timing.main ở bước 2. Dữ liệu tests không được suy ra từ graph; dùng Grep cho tests. Đây là fallback minh bạch, không giả lập thành lệnh affected thành công.

### Cơ sở phương án và phép đo

- [pytest-xdist distribution](https://pytest-xdist.readthedocs.io/en/stable/distribution.html): n=2 giới hạn worker; loadfile giữ cả file trong một worker, chưa bảo đảm các file không tranh tài nguyên. Vì vậy phải kiểm isolation trước A/B.
- [Python subprocess](https://docs.python.org/3/library/subprocess.html): run có timeout tùy chọn và xử lý tiến trình con khi hết hạn. Không suy rộng thành đã dọn cả cây worker; cần test riêng trên Windows và đúng Python 3.13 đang dùng. Trang tài liệu mặc định hiện trả bản 3.15 nên chi tiết tương thích phải đối chiếu 3.13 lúc thiết kế implementation.
- Nghiên cứu tự đọc hai URL chính thức đã biết theo ngoại lệ của analyze-full; không phát sinh tìm kiếm đa hướng hoặc subagent ở bước này. Kết quả nằm trong brief.
- Đối chiếu A/B phải cùng backend pytest: serial n=0 với n=2, cùng node IDs, cùng Python/deps, quyền, fixture và flags. Không so unittest thiếu hàm pytest với pytest đầy đủ rồi nhận là tăng tốc.
- Baseline mới được thu sau khi có nền test hợp lệ và manifest. Mỗi cặp A/B ghi thứ tự, wall time, trạng thái, skip, source/env fingerprint; tối thiểu ba cặp đảo thứ tự là đề xuất cần đưa vào spec. Không trộn full correctness run với số lần benchmark; báo ngân sách thực tế, không che các lượt chạy vượt thông lệ QC.
- Nếu không đạt mục tiêu tốc độ, giữ serial/cache tắt và báo kết quả đo cùng nguyên nhân; không giảm coverage hoặc sửa ngưỡng để nhận pass.
- Không dùng cache PASS để bỏ kiểm mới khi source, dependency, config, runner, selection, quyền hoặc dữ liệu fixture thay đổi. Giữ phân biệt missing/partial/error.
- Không cần phỏng vấn lại các vùng công việc: người dùng đã chọn toàn bộ ba đợt. Còn cần chốt ranh giới triển khai production so với thử nghiệm và mức QC.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Phân tích và chốt phạm vi | CÓ — đã làm | Người dùng chọn triển khai cả P0/P1/P2 và QC Ultra |
| Spec → plan | CÓ | Duyệt riêng; có hợp đồng dữ liệu, phép đo và fallback |
| Preview thiết kế Archify | CÓ | Bản dự kiến gắn với spec; không phải bằng chứng đã triển khai |
| Sửa P0 và kiểm hồi quy | CÓ | Coverage, tokenizer, fixture, isolation, timeout tạo baseline đúng |
| Triển khai P1 | CÓ | Receipt, reuse, join job, readiness và batch được tích hợp thật |
| Triển khai P2 | CÓ | Worker có giới hạn và cache transcript được tích hợp thật |
| Research diện rộng lặp lại | BỎ | Kế thừa bằng chứng; chỉ tra thêm unknown kỹ thuật cụ thể |
| Smoke/simulation/A-B | CÓ | Đầu ra bắt buộc; chạy mã thật và phân biệt dữ liệu dựng với log thật |
| QC Ultra + agent QC độc lập | CÓ | Toàn suite, DoD, smoke/runtime và review độc lập |
| Chế độ build main/subagent | CÓ — chốt sau plan | Không suy từ agent QC độc lập thành chọn chế độ triển khai |
| Report Markdown/HTML | CÓ | Hiện trạng, trước–sau, giới hạn, đề xuất tiếp theo và rollback |

## Hỏi đáp

- Người dùng đã yêu cầu mở request kế tiếp và kiểm chứng toàn bộ các đợt; không hỏi lại có muốn làm hay không.
- Chọn pipeline: người dùng trả lời 1a — full; đã lưu snapshot và khởi tạo request kế tiếp, mở nhánh riêng.
- Người dùng trả lời nguyên văn `1b 2aa`: chọn B triển khai P0/P1/P2 vào workflow. `2aa` được hiểu là gõ lặp chữ a của 2A: QC Ultra; đã thông báo cách hiểu trong chat và ghi muc_qc=ultra bằng CLI.
- Mọi đợt đều là implementation thật, kèm kiểm chứng. Không thay bằng chỉ simulation. Tối ưu không đạt chất lượng hoặc hiệu quả phải giữ đường chạy an toàn và báo lệch, không công bố tăng tốc giả.
- Chế độ main/subagent cho build chốt sau duyệt plan; việc có agent QC độc lập là yêu cầu Ultra, không quyết định thay người dùng chế độ build.
- Không còn câu hỏi về phạm vi hoặc QC; chuyển phase spec. Chưa duyệt spec/plan, chưa sửa production.
- Kiểm tra LSP lại ở phase spec: read_transcripts có 13 tham chiếu (2 production, 11 test); chay_tron_bo_result có 4 (2 production, 2 test). go_to_definition tại lời gọi timing.tong_hop trả 1 định nghĩa. Kết hợp với Grep và graph đã đọc để xác định ranh giới, không còn chỉ dựa vào kết quả LSP chờ dở của lượt trước.
