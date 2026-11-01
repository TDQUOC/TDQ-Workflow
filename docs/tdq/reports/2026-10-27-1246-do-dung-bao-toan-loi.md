# REPORT — Đợt 1: đo đúng và bảo toàn lỗi

Request `2026-10-27-1246-do-dung-bao-toan-loi` · lane full · mode subagent · QC Full · ngày 27/10/2026.
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Kết quả:** đã triển khai phần đo thời gian có căn cứ và bảo toàn kết quả test trên nhánh `bugfix/do-dung-bao-toan-loi`. Có 11 task gốc và 4 task xử lý QC; 9 task giao trợ lý, 6 task do người điều phối giữ theo vùng file. QC đã hoàn tất hai vòng sửa; phần bàn giao Git còn chờ quyết định của người dùng.

**Ý nghĩa thực tế:** từ đây có thể phân biệt thời gian quan sát được với thời gian chưa giải thích được, và không dùng kết quả thiếu test/thiếu chi tiết làm chứng nhận xanh. Đây là nền tảng để tối ưu tiếp; **chưa chứng minh giảm runtime toàn workflow**. Worker mặc định, cổng duyệt và mức QC không đổi. Chưa cài bản sửa vào plugin cache, chưa nâng phiên bản, chưa push hoặc hợp nhất về `dev`.

Báo cáo dài hơn mẫu ngắn vì cần giữ rõ các lượt QC đỏ, phạm vi hai backend, sự cố cấu hình và giới hạn đo. [Hồ sơ QC đầy đủ](../qc/2026-10-27-1246-do-dung-bao-toan-loi.md) · [Spec đã duyệt](../spec/2026-10-27-1246-do-dung-bao-toan-loi.md) · [Plan và DoD](../plan/2026-10-27-1246-do-dung-bao-toan-loi.md).

## Trước và sau

| Điểm nghẽn chất lượng dữ liệu | Trước, đã tái lập | Sau, đã kiểm |
|---|---|---|
| Đo thời gian | Gap giữa hai phản hồi 120s được gọi là model time; gap 360s bị loại thành 0 | V2 dùng span có đầu/cuối và ID; API/tool/job/union/unattributed có quality và reason; `model_giay=null`, không còn cắt gap trên 300s |
| Khoảng chạy đồng thời | Khó phân biệt phần chồng nhau, dễ diễn giải sai thời gian máy làm việc | Gộp khoảng, cắt theo request/phase; ví dụ wall 20s, API 10s, tool 10s → union 15s, unattributed 5s |
| Nguồn log Windows | Slug Claude tạo thiếu drive nên không tìm được thư mục thật | Adapter chung chuẩn hóa đường dẫn, kiểm host/project/session; hỗ trợ Claude/Codex, không lấy log project khác để bù dữ liệu thiếu |
| Bảo toàn lỗi pytest | Tiến trình FAIL nhưng danh sách module lỗi rỗng | Đọc JUnit và exit cùng nhau, giữ lỗi/module hoặc unmapped; chi tiết thiếu được đánh dấu, không mất lỗi qua fallback |
| Direct selector rỗng | CLI exit 0, “PASS — 0 modules tested”, trong khi test qua facade đang FAIL | Thử phụ thuộc bắc cầu rồi fallback an toàn; không có test cho source → INCOMPLETE; no-op/tài liệu không liên quan → SKIP |
| Tương thích và lịch sử | Chỉ số cũ dễ bị đọc như model compute | V1/step audit ghi rõ legacy estimate; wrapper cũ giữ dạng trả về; close chỉ append một lần, không viết lại lịch sử |

[Baseline có output thật](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/baseline.json) · [Regression RED trên baseline](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/tdq-t3.2-red.txt) · [GREEN qua entry point thật](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/tdq-t3.2-green.txt).

Nguồn chính: [adapter transcript](../../../scripts/tdq_transcript.py), [parser kết quả](../../../scripts/tdq_test_result.py), [timing](../../../scripts/tdq_timing.py), [runner/selector](../../../scripts/tdq_test.py). Chỉ thêm hai module runtime, đều dùng stdlib; không tạo dịch vụ hoặc dependency mới.

## Kiểm chứng và DoD

| DoD | Kết quả và căn cứ |
|---|---|
| D1 — timing/union/quality | PASS: 63 test timing; fixture overlap, biên phase, log thiếu và không đoán model time |
| D2 — nguồn Claude/Codex | PASS: 50 test adapter; thêm probe đọc log thực ở phần dưới |
| D3 — bảo toàn verdict/lỗi | PASS: 141 test runner/parser; malformed/missing XML, exit mâu thuẫn, skip-only, timeout và lỗi collection không thành PASS |
| D4 — phụ thuộc gián tiếp | PASS: 12 test IndirectSelection; direct xanh vẫn không thay thế kiểm bắc cầu/QC |
| D5 — tương thích/lifecycle | PASS: 4 test Compatibility, các consumer có trong Full; lịch sử append-only và close-once |
| D6 — QC cuối | PASS trong môi trường Windows đã nêu: 3.206 unittest + 84 pytest, 12 skip có lý do; QC-F1–F4 có bằng chứng |
| D7 — hồ sơ/binding/quay lui | PASS: lint 0 lỗi và 14 kiểm nội dung/hash đều đúng; snapshot planned và phương án quay lui được ghi rõ |

Không cộng các nhóm D1–D5 thành số test khác nhau vì có giao nhau. Lượt chứng nhận gồm hai tập không trùng: **3.290 test được thu thập, 12 skip, không có failure trong hai lượt cuối, cả hai tiến trình exit 0**. Unittest: 3.206 test/686.773s, runner 688.08s, tiến trình 688.269s; pytest bổ sung: 82 passed/2 skipped, tiến trình 6.845s. [Full cuối](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-F1-after-QC2.json) · [Pytest bổ sung](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-F2-pytest-isolated.json).

Selector vùng chạm đạt 129/167 module nên chọn full. Đã dùng lại Full cùng HEAD/hash, rồi bổ sung sáu module viết hàm pytest mà unittest không thu thập. [Proof kết hợp](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-F2-combined-proof.stdout.txt) xác nhận 167/167 module và toàn bộ consumer bắt buộc có mặt. Đây là chứng nhận từ hai backend kết hợp; lệnh stdlib riêng chưa chứng minh chạy hết hàm pytest.

Ba lượt Full thực tế: **5 failure → 1 failure → 0 failure**, mất tổng khoảng **32,5 phút tiến trình**. Đã sửa fixture portable để tính đúng hai module được duyệt, đồng bộ chỉ mục/neo luật, cô lập fixture cập nhật plugin. Archify native chạy được ở quyền thường qua Explorer; không sửa engine hoặc hạ kiểm tra. [Sổ cuối](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-ledger-final.stdout.txt) giữ `tron_bo=3`, `ngan_sach=3`, `bo_sot=5`, `radius_complete=true`. Năm module từng bị bỏ sót trong lịch sử vẫn được giữ dù lượt cuối xanh.

Pytest bổ sung lần đầu có 0 assertion lỗi nhưng exit 1 do dọn thư mục TEMP cũ bị từ chối quyền; giữ nguyên lượt đó và chỉ nhận lượt dùng `--basetemp` riêng có exit 0. Không đổi ACL hoặc xóa cache/worktree cũ.

## Log thực và cách đọc số đo

[Probe hai session của đợt audit](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/real-source-check.json): Claude đọc 23.722.946 byte trong 0,284s, nhận 1.576 span API và 1.565 span tool, đều partial do thiếu/xung đột/sự kiện chưa hỗ trợ. Codex đọc 907.915 byte trong 0,008s, nhận 21 span tool complete trong log đã chọn; API và job unavailable. Không giữ nội dung hội thoại/raw payload trong artifact.

Các thời lượng trên chỉ là đọc hai nguồn đã chọn, không phải benchmark toàn workflow hoặc chi phí dò mọi log. Lệnh `timing show` tự dò nguồn của request ở 15:24 mất 5,812s và vẫn có quality partial. Cần giữ quality và attribution `project_window`: cửa sổ thời gian của project không chứng minh tất cả hoạt động thuộc riêng request này. Không lấy unattributed để kết luận người dùng ngồi chờ, model đang tính hoặc đã tiết kiệm bao nhiêu token/chi phí.

## Giới hạn và sự cố cần biết

- Môi trường chứng nhận: Windows, Python 3.13.15; không chạy ma trận CI mọi OS/Python. Không đặt UTF-8 toàn cục để che lỗi tiến trình con. 12 skip gồm 3 kiểm quyền POSIX, 6 detector tokenizer dùng đường POSIX trên Windows và 3 ca symlink quyền thường. Các ca skip không được tính là đã kiểm thành công; finish vẫn dùng tokenizer Windows thật để đếm 58 file.
- I18n toàn file còn 63 finding cũ; đối chiếu diff không có finding mới. Ruff/radon/cognitive_complexity không có sẵn, không cài thêm; AST ước lượng nhánh tối đa 10 và review thủ công thay cho chứng nhận chính thức từ các công cụ đó. LSP đã dùng nhưng có lượt treo ở caller state; đã ghi fallback grep/test consumer.
- Preview HTML là thiết kế `planned` đã duyệt. Binding/document/manifest/HTML hash giữ nguyên; verifier báo stale vì 14 file source/skill/test đã đổi. Không bind lại để che drift. Master architecture đã stale từ trước, chưa sửa trong đợt này. [Đối chiếu binding](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/D7-final-binding.json).
- Full test làm block TDQ trong `C:/Users/admin/.claude/CLAUDE.md` trỏ về checkout. Đã tái lập cơ chế ở HOME tạm: nhánh cập nhật phiên bản của `SessionStart` cũ ghi instruction dù bật cờ an toàn. Đã ghim lại đúng plugin Claude 0.84.2, giữ phần ngoài block và kiểm hash. Backup riêng ở `C:/Users/admin/AppData/Local/Temp/tdq-phase1-user-claude-before-final-repin.md`; không đưa cấu hình cá nhân vào repo. Không có snapshot trước sự cố nên không tuyên bố khôi phục byte-for-byte bản ban đầu. **Lỗ hổng cô lập của nhánh setup cũ chưa được sửa**, cần request riêng. [Probe](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-user-config-isolated-probe.stdout.txt) · [Biên nhận khôi phục cuối](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-user-config-final-repair.stdout.txt).
- Runtime updater cũ vẫn có thể copy cache/worktree nếu nhận checkout bẩn làm nguồn plugin; lần này sửa fixture dùng nguồn plugin hợp lệ, không sửa bộ lọc updater. Bốn worktree có sẵn được giữ nguyên. Hai file hook của task QC2.1 được chuyển giữ tại `C:/Users/admin/AppData/Local/Temp/tdq-qc2.1-preserved-1505/` trước khi dọn worktree task.

**Lệch spec chờ duyệt:** CLI hiện không có mục nào. Những giới hạn baseline trên được công khai; không tuyên bố đã sửa toàn bộ lỗi sẵn có của repository. Đợt 2/3 chưa triển khai.

## Git và quay lui

HEAD source đã chứng nhận: `d1b90b825596e84aba7136b02a545bc2fa06c21a`; baseline `3e0ef5f8a148cbf8aae1e932995e844e8f62ccd9`. Các commit nội bộ phục vụ checkpoint/hợp nhất task: `645b94e`, `04bb176`, `960d630`, `d082701`, `84fd7a5`, `6274303`, `252c318`, `1b0839c`, `dfd7649`, `152df67`, `514357d`, `1e32603`, `b29eef2`, `1654582`, cùng các merge task. Chưa tạo commit bàn giao cuối, chưa merge về `dev`, chưa push/cài plugin.

Nếu chưa bàn giao, tiếp tục dùng plugin cache 0.84.2 đang cài; thay đổi source nằm riêng trên nhánh request. Nếu cần quay lui sau khi hợp nhất, tạo revert có kiểm tra các commit nguồn của request rồi chạy lại phạm vi ảnh hưởng; không reset cưỡng bức hoặc xóa lịch sử timing/ledger. Giữ nhãn v1/v2 và toàn bộ biên nhận đỏ để kiểm toán. Không khôi phục bừa backup cấu hình vì backup ghi nhận trạng thái sau sự cố, không phải bản trước sự cố.

Ưu tiên tiếp theo được đề xuất, chưa thực hiện: sửa cô lập HOME/nhánh setup trong test; làm rõ coverage unittest/pytest và detector tokenizer Windows; sau đó mới thử tái sử dụng bằng chứng theo hash và giảm preflight lặp ở đợt 2. Đợt 3 mới thử worker/A–B với cùng phạm vi chất lượng. Không hạ QC hoặc đổi worker chỉ dựa trên mô phỏng cũ.

## Thời gian

Snapshot lúc vào phase report, không phải thời điểm kết thúc toàn request. Dưới đây là nguyên output stdout của `python -X utf8 scripts/tdq_timing.py show`; [biên nhận](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/report-timing.json) giữ command/exit và stderr riêng. Các cột có thể chồng nhau; giữ nguyên mọi nhãn partial/unavailable.

Request `2026-10-27-1246-do-dung-bao-toan-loi` · lane full · opened at 2026-10-27T12:50:47+07:00

| Phase | Wall clock | API request | Tool wait | Background job | Observed union | Unattributed | Times entered |
|---|---|---|---|---|---|---|---|
| idle | 1s | — [partial] | 1s [partial] | — [unavailable] | 1s [partial] | 0s [partial] | 1 |
| analyze | 12 min | — [partial] | 19s [partial] | — [unavailable] | 19s [partial] | 12 min [partial] | 1 |
| spec | 19 min | — [partial] | 28s [partial] | — [unavailable] | 28s [partial] | 19 min [partial] | 1 |
| plan | 29 min | — [partial] | 27s [partial] | — [unavailable] | 27s [partial] | 28 min [partial] | 1 |
| mode | 2 min | — [partial] | 5s [partial] | — [unavailable] | 5s [partial] | 2 min [partial] | 1 |
| implement | 37 min | — [partial] | 7 min [partial] | — [unavailable] | 7 min [partial] | 30 min [partial] | 1 |
| qc | 55 min | — [partial] | 8 min [partial] | — [unavailable] | 8 min [partial] | 47 min [partial] | 1 |
| report | 1s | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| Total | 2h 33min | — [partial] | 17 min [partial] | — [unavailable] | 17 min [partial] | 2h 17min [partial] |  |

Model compute time is unavailable (`model_giay=null`). API includes network/provider latency; tool time is host wait. Observed metrics may overlap; unattributed time is not assumed user/model time.
Transcript attribution: project_window. Complete covers selected supported observations only.
- api_request_seconds: missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema;no_confirmed_span_in_window
- tool_call_seconds: conflicts,missing_pairs,unknown_events,unreadable_or_uncertain_source
- background_job_seconds: schema_has_no_confirmed_lifecycle
- observed_union_seconds: conflicts,missing_pairs,unknown_events,unreadable_or_uncertain_source;missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema
- unattributed_seconds: wall_minus_observed_union;conflicts,missing_pairs,unknown_events,unreadable_or_uncertain_source;missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema
