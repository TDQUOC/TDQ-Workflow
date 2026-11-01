# QC độc lập cuối theo phạm vi bỏ benchmark
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-10-31 · Request: `2026-10-27-1846-kiem-chung-tang-toc`

- reviewer: `gpt61sol_high_review_qc13`
- implementers: `root`, `gpt61sol_high_review_qc11`, các implementer TDQ lịch sử T1.1/T1.2/T1.3, T2.1/T2.2/T2.3 và T3.1.
- source_sha256: `81c1946345d8495ef32dbb3924de801020c957c5599918b9c3d4317c5f3278ad`
- verdict: **PASS trong phạm vi correctness/runtime/architecture đã điều chỉnh**.
- Phạm vi máy đọc: `correctness/runtime/architecture only; D9/D10 SKIPPED_USER; D12 report/browser separate`.
- findings: **0 finding chưa xử lý** trong phạm vi review.

## 1. Quyết định phạm vi và giới hạn verdict

Nguyên văn người dùng: **“có thể skip bench mà tổng hợp cho tôi ko?”**

Theo [waiver người dùng](benchmark-user-waiver-20261031.md), T5.3/D9 và T5.4/D10 được ghi **SKIPPED_USER**. Đây không phải PASS hiệu năng hoặc fallback đã có đủ số đo. Không chứng nhận parity Full A/B cuối, ngưỡng giảm median 20%, lợi ích cold/warm hay phần trăm tăng tốc. Giữ mặc định một worker; reuse/readiness/transcript cache off.

Verdict này chốt D1–D8 và phần QC độc lập correctness/runtime/architecture của D11. **Không tuyên bố toàn DoD 12/12 hoặc request đã hoàn tất**; D12 báo cáo Markdown/HTML và browser desktop/mobile được kiểm riêng. Giữ nguyên spec/verifier và mọi evidence lịch sử. Bản [QC sơ bộ](qc-preliminary-20261031.md) tiếp tục là hồ sơ review nguồn chi tiết; trạng thái chưa hoàn tất ở bản đó được thay bằng verdict có phạm vi nêu ở đây sau quyết định bỏ benchmark.

Reviewer độc lập với implementers: chỉ đọc source/diff/evidence và tạo artifact QC; không triển khai sản phẩm hoặc sửa candidate. Lượt chốt này không chạy test, benchmark, setup/build, cài dependency, sửa config/source/state/plan hay commit/merge.

## 2. Xác minh source và bằng chứng hiện hành

Đã tính lại `safe_run.source_snapshot(root)` bằng chính hàm harness: SHA trên khớp Full cuối và runtime cuối. Snapshot này có generated exclusions công khai, không được dùng thay điều kiện hermetic/fingerprint của sản phẩm.

[Receipt Full fresh cuối](runs/QC-F1-final-after-QC3-20261031-6add68337dd44ca9b785b1603918f786/receipt.json) dùng production runner, workers 1, fresh/reuse off. Child/harness exit 0, quyền thường, guard sạch, cleanup complete. Reviewer kiểm lại chỉ đọc `verify_full`: digest result/evidence, raw execution sidecar, JUnit và coverage tính lại đều phù hợp.

- 3602 case: **3594 pass, 8 skip, 0 fail/error/xfail/xpass**.
- Đủ 3306 case baseline, 0 remap; không missing/extra/duplicate.
- Skip có reason/capability; các case POSIX/symlink không được môi trường hỗ trợ giữ nhãn đúng. Không chứng nhận POSIX trên host thật từ kết quả Windows.
- Runner wall 1117.6745853999746 giây; đây là thời gian correctness của một lượt, không phải bằng chứng tăng tốc A/B.

Reviewer đã kiểm lại `verify_regressions` trên Full hiện hành, không chạy lại test:

| Check | Số regression/assertion bắt buộc có evidence | Kết quả |
|---|---:|---|
| D1 — coverage | 76 | PASS |
| D2 — skip/tokenizer | 27 | PASS |
| D3 — process/fixture/isolation | 14 | PASS trên Windows quyền thường |
| D4 — hồi quy/tương thích | 121 | PASS trong phạm vi host; POSIX giữ giới hạn |
| D5 — reuse | 61 | PASS correctness |
| D6 — join | 37 | PASS correctness |
| D7 — readiness/batch | 18 | PASS correctness |
| D8 — transcript | 20 | PASS correctness |

[Kết quả DoD đã lưu](dod-checks-final-QC3.json) khớp các kiểm trên. [Receipt runtime](runs/runtime-final-after-QC3-ed06898fbca3436baf4a965c036e004a/receipt.json) và [runtime-final.json](runtime-final.json) cùng source Full; verifier chỉ đọc với `expected_source=full.source_before` trả valid, không lỗi, **6/6 scenario dưới 120 giây**: timeout, cancel, join, owner-crash, freshness và transcript.

Runtime dùng process thật trên fixture có nhãn simulation; không gọi đây là số đo toàn workflow/log thật. Join có một execution, hai caller nhận executed/joined; timeout/cancel và owner-crash kiểm cleanup bounded. Verdict máy `PERFORMANCE_MET` của runtime chỉ nói điều kiện smoke, không phải D9/D10.

## 3. QC-F3 — ràng buộc spec §5 và kiến trúc

| Ràng buộc | Kết luận và bằng chứng |
|---|---|
| Hook → scripts; scripts không import hooks | PASS trong vùng feature: hook/session_start gọi CLI hiện có; runner/process/receipt/readiness/transcript không phụ thuộc hook để thực thi sản phẩm. |
| State có writer tập trung | PASS trong vùng chạm: cache/receipt không ghi state; điều phối giữ CLI state hiện có. Lượt QC không thay state. |
| Sản phẩm không import test helper | PASS: process/receipt/manifest/result/cache dùng module sản phẩm và stdlib; tests phụ thuộc sản phẩm theo chiều kiểm chứng. |
| Ranh giới module §2b | PASS: manifest/result chuẩn hóa và phán quyết; process sở hữu cây tiến trình; receipt quản fingerprint/lease/proof, không import runner; runner điều phối; timing tiêu thụ transcript. |
| Full correctness và provenance | PASS: Full cuối fresh/off với source-bound raw evidence; thiếu pytest không được chứng nhận full bằng unittest fallback; lỗi quan sát được không bị thiếu evidence biến thành PASS. |
| Eligibility/freshness/accounting | PASS correctness: reuse default-deny, explicit policy và fingerprint; nonce/creation identity và deadline cho join; commit marker cuối; reused/joined không tăng giả execution count. Xem `tdq_test_receipt.py:98–193,287–369,422–570,622` và `tdq_test.py:1101–1244,1307–1327`. |
| Live readiness | PASS correctness: chỉ cache phần tĩnh; config/doctor/module/graph freshness/smoke vẫn live; handoff kiểm digest lại, lỗi cache về probe. Xem `tdq_lsp.py:662–728`, `tdq_readiness.py` và regression D7. |
| Transcript privacy và partial semantics | PASS correctness: đọc/hash toàn bytes, kiểm identity, cache trace chuẩn hóa không giữ prompt/tool payload thô; selection/dedup/quality tính lại; unstable/unreadable không được gọi complete. Xem `tdq_transcript.py:133–232,397–415,515`, `tdq_transcript_cache.py` và regression D8. |
| Dependency, quyền và OS | Không cài/nâng dependency, nâng quyền hoặc tạo POSIX VM để làm xanh. Chứng nhận hiện tại là Windows quyền thường; POSIX chưa được kiểm trên host thật. |
| Benchmark và bàn giao | D9/D10 SKIPPED_USER theo waiver; không thay verifier hoặc bỏ case/assertion để nhận PASS. D12 report/browser tách riêng. |

**QC-F3: PASS trong phạm vi correctness/runtime/architecture.** Không có finding mới cần sửa so với review sơ bộ. Các hạn chế benchmark đã được chuyển thành waiver có chủ thể phê duyệt, không thành finding mã nguồn.

## 4. QC-F4 — năm câu hỏi SOLID

Đã đọc `skills/tdq-conventions/references/clean-code.md`; áp dụng cách đọc functions/modules của repository, không dựng interface/framework chỉ để thỏa tên nguyên tắc. Reviewer không viết source trong lượt này.

| Câu hỏi | Có/Không | Bằng chứng trong phạm vi thay đổi |
|---|---|---|
| SRP — hàm/lớp có một lý do thay đổi? | Có | Phân riêng collector/result, process, receipt, static readiness và transcript cache. Hàm điều phối gọi adapter; kiểm evidence/phán quyết không bị trộn với state writer. |
| OCP — thêm biến thể dữ liệu cùng hợp đồng bằng bảng/subclass thay vì sửa lớp cũ? | Có trong các điểm mở rộng đã review | Outcome/schema/scenario và ma trận mutation/worker được khai báo bằng dữ liệu; regression bổ sung bằng parametrization/list fixture. Không suy điều này thành lời hứa thêm backend hoặc cơ chế OS mới chỉ cần một dòng dữ liệu. |
| LSP — giữ hợp đồng type/error giữa các nhánh/adapter? | Có | Result giữ schema công khai và status rõ; process trả facts nhất quán; receipt trả action/provenance/timings, lỗi không tự thành PASS; adapter giữ FAIL/ERROR đã quan sát khi evidence thiếu. Kiểm bằng D1/D3–D6 và raw Full/runtime. |
| ISP — tham số truyền vào được dùng đúng mục đích? | Có | Cache nhận project/request/input/probe/parser cụ thể; process nhận repo/env/deadline; consumer có keyword-only options và mặc định bảo thủ, không yêu cầu toàn state object để làm việc không liên quan. |
| DIP — dùng entrypoint dùng chung thay vì sao chép chi tiết? | Có | Runner dùng process/receipt/manifest/result; setup và check dùng chung readiness; timing gọi transcript reader; hook gọi CLI và state writer vẫn tập trung. |

**QC-F4: PASS qua review thủ công và evidence regression đã có.** Ruff **UNAVAILABLE**: không có command `ruff` trên PATH và `importlib.util.find_spec('ruff')` trả không có module. Không cài Ruff, không ghi Ruff PASS và không dùng việc thiếu Ruff để thay đổi verdict test. Các câu trả lời trên là đánh giá phạm vi thay đổi đã review, không tuyên bố toàn repository đã hoàn hảo về SOLID.

## 5. Kết luận và chuyển giao

**PASS — correctness/runtime/architecture theo phạm vi người dùng đã điều chỉnh; D9/D10 SKIPPED_USER; D12 report/browser separate.** Không có finding chưa xử lý trong scope này. Tệp JSON kèm theo bind reviewer, implementers, source, waiver và digest của báo cáo này để kiểm bằng `verify_dod.verify_qc` mà không sửa verifier.

Evidence gốc và review sơ bộ được giữ nguyên. D12 vẫn cần người phụ trách bàn giao kiểm Markdown/HTML, desktop/mobile và liên kết evidence theo phạm vi đã bỏ benchmark. Không suy verdict này thành PASS hiệu năng hoặc toàn DoD 12/12.
