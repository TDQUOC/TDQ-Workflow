# BRIEF — Phân tích và đề xuất xử lý 10 issue nền
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay vậy giúp tôi mở request phân tích và đề xuất phương án xử liis cả 10 issue

Mục tiêu: phân tích nguyên nhân và đề xuất phương án xử lý đủ 10 issue nền đã ghi trong QC Archify; chưa triển khai sửa mã nguồn, chưa commit/push/merge.

Đầu ra dự kiến: bảng từng issue gồm bằng chứng tái hiện, nguyên nhân gốc, phân biệt lỗi sản phẩm/hợp đồng/test, phương án tối thiểu đúng, file bị ảnh hưởng, test bảo vệ và thứ tự xử lý. Không tự tăng ngưỡng hoặc làm lỏng assert để suite xanh.

Phạm vi 10 issue: Next step của browser skills; reference thiếu link trực tiếp; link chrome-devtools-mcp-scripts.md chết; bảng giới hạn 9/11 skills; description 2051/1800; bootstrap UTF-8 ở 5 entrypoint; link vision-test-loop ở spec; JSON output search gate; bán kính test 4/3 modules; đường dẫn hook Antigravity trên Windows.

## Hiểu & kiến thức

Bằng chứng kế thừa: docs/tdq/qc/2026-10-24-2348-hoan-thien-archify.md. Suite cuối 2974 tests, 9 failures, 1 error, 10 skipped; 10 lỗi đã đối chứng trên a03d698 và 5d6570d. Khi phân tích phải xác minh nguyên nhân từ code, không xem tên test hoặc suy đoán trong báo cáo là kết luận nguyên nhân.

User đã cho phép tách request. Đã xuất snapshot đầy đủ của state Archify bằng tdq_state.py get và xác minh JSON bằng state gốc trước init: `docs/tdq/2026-10-24-2348-hoan-thien-archify.resume.json`. Hướng dẫn tiếp tục: `docs/tdq/reports/2026-10-24-2348-hoan-thien-archify-resume.md`. Archify chưa nghiệm thu; 6 worktree và mọi thay đổi nguồn/test vẫn giữ nguyên. Request mới active full/analyze trên nhánh docs/phan-tich-muoi-issue, nhánh gốc feature/hoan-thien-archify; dirty source kế thừa không thuộc đầu ra request phân tích và không được gom commit tự động.

Pre-flight: MCP LSP khởi động thành công. Setup smoke 3 tầng trả lời được, nhưng graph stale và chứng nhận Python module hết hạn. Init dùng --bo-qua-lsp với lý do chỉ phân tích/đề xuất tài liệu; không dùng exemption để bỏ tra code. Không cần API/endpoint hoặc nghiên cứu web khi các câu hỏi đều là nội bộ repo.

### Khảo sát nguyên nhân và vùng chạm

- Đã đọc đầy đủ docs/kien-truc.md: hồ sơ vẫn mang nhãn nháp; không tự coi mọi dòng cũ là quyết định mới. Quy tắc hiện hành và test là nguồn đối chiếu.
- I08: search_rules.py:838–839 miễn tìm kiếm ở analyze/quick_analyze/spec; fixture test_reminder_contract.py:174 đặt analyze nhưng :190 đòi JSON deny. Probe trực tiếp: analyze=True, implement=False. Đề xuất đổi fixture denial sang phase được gate áp dụng và thêm case allow không output; không phục hồi chặn phase analyze.
- I09: tdq_test.py:198–203 regex quét cả source text, gồm comment/docstring. test_subagent_start.py:118 nhắc ask_gate trong lịch sử cấu hình, được chọn như một textual dependency; cap3 tại test_tdq_test.py:224 trượt với4. Đề xuất giữ selector bảo thủ, thiết kế fixture xác định + test tích hợp chứng minh caller/scanner; không xóa caller hoặc tăng3→4 thuần túy.
- I10: build_portable.py:436 cố ý quote đường dẫn; test_tuong_thich_host.py:70 split()[-1] giữ nháy và làm vỡ path có khoảng trắng. Probe xác nhận đường dẫn thực tuyệt đối nhưng token bị cắt không tuyệt đối. Đề xuất kiểm parsed argv theo nền tảng/contract thay split, thêm Windows/POSIX/khoảng trắng/Unicode/relative/~ cases; chưa suy runtime host pass khi chưa chạy host thật.
- Tái hiện targeted3 test trên main: 3 failed trong1.65s, đúng ba triệu chứng cũ. Không sửa source hay test.

| Vùng file chạm khi sửa tương lai | Phát hiện qua lớp nào | Tác động & quan hệ |
|---|---|---|
| search_rules.py, search_gate.py, test_reminder_contract.py | Read/Grep + LSP references quyet_dinh (8 kết quả, metadata vị trí hạn chế) | Hook và replay dùng chung quyết định phase; fixture phải phản ánh chính sách |
| tdq_test.py, test_tdq_test.py, test_subagent_start.py | Grep/Read + Graphify affected ban_kinh depth2 | cmd_vung_cham → ban_kinh; main caller gián tiếp; graph stale nên không dùng làm chứng cứ đầy đủ |
| build_portable.py, test_tuong_thich_host.py | Read/Grep | Generator quote path, consumer test parse sai; không thay generator trước khi chứng minh lỗi |
| Skill/docs/UTF8 tests và source tương ứng | Agent đọc source/test hiện tại, đã báo kết quả | Next-step, direct links, registry, description và UTF8 thuộc các nguồn khác nhau; đồng bộ chỉ khi được phép fix |

Nhóm I01–I07 đã có phân tích read-only:

- I01: browser skills là công cụ dùng nhiều phase; đề xuất ghi phase không đổi và trả quyền điều phối cho caller thay gán cứng qc/analyze.
- I02/I03: link reference từ skill chủ conventions/setup; xử lý link chết trước khi nối guide. Kiểm nội dung scripts/tdq_devtool_mcp.py thay vì tạo file hướng dẫn rỗng.
- I04: thiếu hai keys browser trong SKILL_LINE_LIMITS, không phải cần xóa skill. Đề xuất khai giới hạn mới có số đo và shape tests, không tăng giới hạn hiện hữu. Các con số cap agent đề xuất chỉ là ứng viên, chưa phê duyệt.
- I05: cô đọng description để giữ trần1800 và routing semantics. Không lấy phép trừ ước lượng của agent thành số đo sau sửa; phải có câu ứng viên thật, đo lại và kiểm router ở báo cáo đề xuất.
- I06: scripts dùng utf8_io, hooks dùng đường bootstrap chung khi đúng dependency; không mặc định thêm sys.path nếu Python entrypoint đã có sẵn. Thiếu import là fact; lỗi Unicode thực tế phải kiểm với encoding cưỡng bức, không phán mọi Windows luôn cp1252.
- I07: kiểm cả SKILL.md lẫn spec-template vì test dừng tại failure đầu; bổ sung liên kết trực tiếp thay chỉ nhắc tên Vision Test Loop, giữ trần dòng.

Các lệnh PASS trong phần phương án của agent là kết quả kỳ vọng tương lai, không phải test đã chạy sau patch: không có patch trong request này. Bỏ quy kết luật reference là chuẩn bên ngoài; đây là hợp đồng repo đã xác minh.

### Năng lực dùng được

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | Ghi phạm vi và giữ request cũ |
| tdq-spec | plugin:tdq-workflow | NỀN | Hợp đồng báo cáo trước duyệt |
| tdq-conventions | plugin:tdq-workflow | NỀN | State, nhật ký và bảo toàn dữ liệu |
| dataviz | built-in | DÙNG | Sơ đồ luồng phân tích Mermaid, không palette tùy chỉnh |
| Đã xét 8 skill TDQ khác và các skill chuyên biệt có trong phiên | plugin/built-in | KHÔNG | khác lĩnh vực hoặc chưa đến phase; browser không cần cho báo cáo Markdown, không thêm runtime |

Bỏ research web vì không có ẩn số ngoài repo; bỏ phỏng vấn phạm vi lặp vì user đã chốt đủ 10 issue và chưa fix. Không dựng HTML Archify mới cho request chỉ phân tích tài liệu; sơ đồ quy trình trong spec không phải thiết kế thay đổi production.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| analyze | CÓ | Kiểm source/test và phân loại đủ 10 issue; đối chiếu lỗi thực với kỳ vọng test |
| spec/plan | CÓ | Chốt hợp đồng đầu ra báo cáo và cách kiểm chứng, không cấp phép sửa production |
| implement | CÓ — chỉ tài liệu | Viết báo cáo đề xuất; không sửa scripts/hooks/tests/skills để fix issue |
| qc | CÓ — full | Kiểm dẫn nguồn, đủ 10 issue, test vùng liên quan và một lượt full suite tại cổng; lỗi nền ghi trung thực, không fix trong request tài liệu |
| report | CÓ | Bàn giao đề xuất và liên kết snapshot để tiếp tục Archify khi user yêu cầu |

## Hỏi đáp

> 1a 2a note request này sau khi xử lí xong sẽ có thể continue, và request mowiis là muốn đưa phương án đề xuất chưa fix

Đã chốt: pipeline chuyên sâu, tách request mới, bảo toàn Archify để continue; phạm vi chỉ phân tích/đề xuất, chưa fix. Không cần hỏi lại phạm vi 10 issue. User trả lời `1a` lúc 12:00 ngày 2026-10-25: QC full, đã ghi muc_qc=full qua tdq_state.py. Hoàn tất request tài liệu không tự sửa 10 lỗi hoặc tự nghiệm thu Archify.
