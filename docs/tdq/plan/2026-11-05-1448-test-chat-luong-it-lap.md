# PLAN — Test TDQ theo tính năng, ít nhưng giữ chất lượng

Ngày: 2026-11-05 · Spec: ../spec/2026-11-05-1448-test-chat-luong-it-lap.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — ĐÃ DUYỆT qua `1a`; mô phỏng trên 7 task/5 wave với hệ số agent 1.5: main 14,3 phút, team 15,3 phút (chênh 1,1 phút); chuỗi phụ thuộc và file nóng khiến một chủ ghi thắng.
Trạng thái plan: ĐÃ DUYỆT.

## Quy tắc thi hành

- Chỉ tính test có oracle hành vi/rủi ro thật; không đặt trần số case toàn repo, không xóa test chỉ vì nhiều, không bịa feature login vào TDQ. Fixture dùng đường dẫn/cấu hình giả trong thư mục tạm; giữ test bảo mật, quyền, dữ liệu, hồi quy.
- Thực thi từng task: đánh `[~]` trước, viết test đỏ thật → code tối thiểu → test xanh → `[x]` ngay. Tách ba số: case ID duy nhất, subtest con, lượt thực thi. Trước mỗi lượt ghi selector, feature/risk, lý do và dự kiến chi phí; không nhiều agent cùng chạy suite.
- Giữ manifest/outcome/fingerprint và fallback full khi không chắc; không thay `.github/workflows/test.yml`, không dùng receipt cũ thay verdict QC cuối. Pilot smoke trên fixture TDQ thực, không dùng service/account thật.
- Đặt một lượt full `--fresh --reuse off` ở QC-F1 sau khi code ổn. Nếu QC sửa nguồn làm verdict mất hiệu lực: chạy lại vùng chạm, và full lần nữa chỉ sau vòng sửa cuối. Mục tiêu tổng smoke khuyến nghị: full ≤5 phút, ultra ≤10 phút linh hoạt với lý do; 120 giây **mỗi** smoke/runtime ultra không đổi. Trượt thời gian không cho bỏ case quan trọng.
- Preview Trước/Sau đã duyệt: `../spec/2026-11-05-1448-test-chat-luong-it-lap-preview.html` + manifest; kiểm binding trước code, không viết lại bản planned để che thay đổi thiết kế.

## Thiết kế Trước vs Sau

| Khía cạnh | Trước | Sau |
|---|---|---|
| Chọn test | Minimum 1+2+1 scenario/feature; runner tự chọn vùng chạm ngay trước chạy | Feature/rủi ro/oracle quyết định case; in selector, lý do và dự kiến số module **trước khi** chạy; test không liên quan không sinh thêm |
| Ngân sách | Hai cổng full, số lượt được đếm nhưng không lập lịch theo nguồn | Tách tập smoke cần thiết với full fresh QC cuối; báo executed/joined/reused và thời gian thực, không cắt test để khớp mốc |
| Nguồn bằng chứng | Lịch sử 4.161 nodeid, không phải scenario nghiệp vụ | Mapping feature → case ID → fixture/oracle và gap; nhận diện test trùng có bằng chứng, giữ full regression |

## P1 — Khóa phép đo và sàng lọc case

- [x] **T1.1** (e12m) Lập eval-plan source-bound trước sửa luật và đo baseline không chạy full: inventory case/feature, lượt chạy lịch sử, smoke selection; phân biệt con số đã đo với đề xuất — Test: `python scripts/tdq_skill_eval.py plan --plan docs/tdq/artifacts/2026-11-05-1448-test-chat-luong-it-lap/eval-plan.json`
  - Ra: `docs/tdq/artifacts/2026-11-05-1448-test-chat-luong-it-lap/eval-plan.json`, `baseline.md` cùng nguồn/giới hạn; không gọi paid model nếu chưa có quyền/đầu vào.
- [x] **T1.2** (e12m) Rà tập case pilot theo feature/rủi ro, ghi case giữ/trùng/gap kèm oracle; không xóa khi chưa chứng minh test còn lại bắt lỗi cũ — Test: `python -m pytest tests/test_tdq_test.py tests/test_tdq_test_receipt.py --collect-only -q`
  - Dùng: `tdq-lean`
  - Để: đối chiếu test trùng hành vi/thời gian cao trong runner pilot, không coi số nodeid nhỏ là chất lượng.
  - Ra: `docs/tdq/artifacts/2026-11-05-1448-test-chat-luong-it-lap/case-audit.md` có feature→case→risk và quyết định giữ/gộp/chưa rõ.
  - Kiểm: `python -m pytest tests/test_tdq_test.py tests/test_tdq_test_receipt.py --collect-only -q`
  - Không dùng cho: xóa test bảo mật hoặc bỏ số lượng lớn khi chưa có negative/mutation evidence.
  - Cần: T1.1

## P2 — Lập danh sách trước chạy, không nhân đôi chứng cứ

- [x] **T2.1** (e22m) Red→green kiểm và thêm đường dry-run selection nhỏ nhất vào runner `vung-cham`: in selector/scope/reason/module trước subprocess, không gọi pytest; không đổi mặc định chạy thật, fallback và manifest — Test: `python -m pytest tests/test_tdq_test.py -q`
  - Chạm: `scripts/tdq_test.py`, `tests/test_tdq_test.py` → `cmd_vung_cham`, `_select_tests`, `ban_kinh`; caller CLI và `tests/test_tdq_test.py` (LSP refs + Graphify affected 2 bước), `tdq_runtime_bench.py` downstream phải giữ API.
  - Cần: T1.2
  - Ra: CLI `vung-cham --plan-only` chỉ đọc, không phát hành PASS/test receipt; path khó/thiếu mapping vẫn báo fallback như execution.
- [x] **T2.2** (e13m) Red→green xác minh bằng fixture một luồng TDQ có thật, case lỗi và chọn test trước chạy; chỉ thêm case kiểm khác oracle, không sinh ma trận giả — Test: `python -m pytest tests/test_tdq_test.py tests/test_tdq_test_receipt.py -q`
  - Chạm: `tests/test_tdq_test.py`, `tests/test_tdq_test_receipt.py` → direct/transitive/fallback, `--plan-only` không gọi process, không đổi behavior case cũ.
  - Cần: T2.1

## P3 — Luật tạo test và lịch QC

- [x] **T3.1** (e16m) Red→green thay minimum scenario cố định bằng bảng Given–When–Then theo feature/risk có fixture/oracle; hướng dẫn dùng evidence cùng nguồn cho task/DoD, giữ full fresh QC cuối và trần runtime per-check — Test: `python -m pytest tests/test_vision_test_loop_doc.py tests/test_luat_test.py tests/test_runtime_contracts.py -q`
  - Chạm: `skills/tdq-build/references/vision-test-loop.md`, `skills/tdq-build/references/qc.md`, `skills/tdq-build/references/runtime-speed.md`, `tests/test_vision_test_loop_doc.py`, `tests/test_luat_test.py` → giữ bảng QC/Stop và suite full; không copy logic Python vào skill.
  - Cần: T1.1, T2.2
  - Ra: luật cho cả repo TDQ/project dùng plugin, rõ cách xử lý input rỗng/edge/error và lý do khi chưa cần case.
  - Ghi chú: rung 2 dùng lại tài liệu hiện có, không tạo thêm chính sách/marker; case mới chỉ thêm khi có oracle khác. Đã thấy test đỏ cho quota cố định; cập nhật QC/runtime, tiếp kiểm xanh và lint.

## P4 — QC có chứng cứ và báo cáo

- [x] **T4.1** (e18m) Đo smoke CLI/fixture không quá 120 giây mỗi check, ghi case/risk và thời gian; sau code ổn chạy đúng một full fresh ở QC-F1, dùng receipt của chính lượt ấy đối chiếu DoD khác; QC độc lập đọc receipt, không mở thêm full — Test: `python -m pytest tests/test_tdq_test.py::VungCham::test_vung_cham_files_chi_chay_module_chon_dat -q`
  - Dùng: `workflow-authoring`
  - Để: QC read-only theo DoD, đối chiếu độc lập selection/receipt và rủi ro test bỏ sót; không phân tán chạy full.
  - Ra: `docs/tdq/qc/2026-11-05-1448-test-chat-luong-it-lap.md` và receipt số case/lượt/thời gian của request.
  - QC: review độc lập phát hiện full nested `selected=10/9` và ANTI-3 còn ép tier; test đỏ/sửa. Full #1 ERROR 13 failed/2 errors; #2 FAIL phases.md; #3 FAIL report visual; #4 pytest 4.162 passed nhưng runner INCOMPLETE do sync-master cùng lúc đổi 39 file; #5 fresh trên nguồn ổn định PASS 4.162 passed/7 skipped, 4.169 ID, receipt complete, 857,25s. Hai lệch Q3 (5/3 full) và Q6 (eval INCONCLUSIVE) đã ghi; Pycache Python là tác dụng phụ lúc import; `--plan-only` chỉ cam kết không ghi artefact TDQ/pytest/ledger.
  - Kiểm: `python scripts/tdq_test.py so --json`
  - Không dùng cho: cho Workflow viết state/Git, mở thêm full suite ở nhiều agent hoặc tự miễn eval.
  - Cần: T3.1
- [x] **T4.2** (e8m) Báo cáo Markdown + Archify HTML về trước/sau, case đã chạy/chưa, mục tiêu thời gian, CI không đổi và giới hạn thật — Test: `python scripts/tdq_archify.py verify --document docs/tdq/reports/2026-11-05-1448-test-chat-luong-it-lap.md --manifest docs/tdq/reports/2026-11-05-1448-test-chat-luong-it-lap.manifest.json`
  - Cần: T4.1

## Cụm song song & file nóng

- Thứ tự: T1.1 → T1.2 → T2.1 → T2.2 → T3.1 → T4.1 → T4.2. `tests/test_tdq_test.py` là file nóng giữa T2.1/T2.2: một chủ ghi hoặc theo thứ tự; không giao đồng thời. `scripts/tdq_test.py` chỉ một task sửa; QC đọc sau khi code ổn, không nhiều agent chạy full. Không dùng Workflow-native worktree thay TDQ state/team.

## Px — Log & test bắt buộc

- Log service runtime của runner giữ timestamp/`TDQ_LOG=0` qua T2.1; kiểm cùng task, không thêm service hoặc config mới. Unit test từng phần nằm ngay ở T2.1/T2.2/T3.1, không chạy full riêng sau implement.

## Definition of Done

- [x] Q1 Case mới gắn feature/rủi ro/fixture/oracle, không xóa test cũ khi thiếu bằng chứng trùng — `python -m pytest tests/test_tdq_test.py tests/test_tdq_test_receipt.py -q`
- [x] Q2 `vung-cham --plan-only` in scope/selector/reason trước khi chạy, không gọi pytest; fallback giữ nguyên — `python -m pytest tests/test_tdq_test.py -q`
- [x] Q3 Cùng nguồn/phạm vi không chạy full thừa trước QC, QC-F1 chạy một full fresh cuối và lưu receipt manifest ID đủ; sửa source sẽ invalidate verdict — `python scripts/tdq_test.py so --json` (đối chiếu với receipt QC-F1 cùng source, không gọi full lần nữa) — receipt cuối PASS; lệch #2 (5/3 full) được người dùng duyệt 2026-11-05.
- [x] Q4 Luật feature/risk thay ép số scenario nhưng giữ ca an toàn/biên/lỗi có rủi ro, CI không đổi — `python -m pytest tests/test_vision_test_loop_doc.py tests/test_luat_test.py tests/test_ci_matrix.py -q`
- [x] Q5 Smoke full/ultra có số liệu và mục tiêu ≤5/≤10 phút chỉ khuyến nghị, không nới per-check 120 giây hoặc cắt test để đạt mốc — `python -m pytest tests/test_runtime_contracts.py tests/test_tdq_test_report.py -q` — contract PASS; tổng smoke INCONCLUSIVE, lệch #3 được người dùng duyệt 2026-11-05.
- [x] Q6 QC `ultra`: full fresh cuối, smoke/runtime có giới hạn, review độc lập và eval provenance trung thực, báo cáo Archify verify — `python scripts/tdq_archify.py verify --document docs/tdq/reports/2026-11-05-1448-test-chat-luong-it-lap.md --manifest docs/tdq/reports/2026-11-05-1448-test-chat-luong-it-lap.manifest.json` — full/HTML PASS; eval INCONCLUSIVE và user duyệt miễn eval #1 ngày 2026-11-05, không gọi model PASS.

Khi nhiều DoD gọi lại cùng selector mà code chưa đổi, chạy chung một lượt và dán cùng receipt/đầu ra cho từng mục; lệnh trong DoD là phép kiểm, không là yêu cầu chạy thêm lần. QC-F1 là nơi duy nhất chạy `tron-bo` nếu không có vòng fix sau đó; Q3 đọc `so` và receipt cùng lượt, Q6 không chạy lại trọn bộ chỉ để tick.

Tổng ước tính 101 phút tác vụ (không gồm chờ duyệt/full suite runtime); ngưỡng smoke chỉ khuyến nghị, không hứa thời gian chạy thật.
