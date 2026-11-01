# QC độc lập sơ bộ — Kiểm chứng và tăng tốc TDQ Workflow
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-10-31 · Request: `2026-10-27-1846-kiem-chung-tang-toc`

- reviewer: `gpt61sol_high_review_qc13`
- implementers: `root`, `gpt61sol_high_review_qc11`, các implementer TDQ lịch sử thuộc T1.1/T1.2/T1.3, T2.1/T2.2/T2.3 và T3.1.
- source_sha256: `81c1946345d8495ef32dbb3924de801020c957c5599918b9c3d4317c5f3278ad`
- verdict: **PRELIMINARY/INCOMPLETE**
- code_findings: **0 finding mới được xác nhận trong phạm vi review**.
- Không chứng nhận D9, D10, D11 cuối hoặc hoàn thành request bằng tài liệu này.

## 1. Phạm vi và cách kiểm

Review độc lập source/evidence ở root; đối chiếu spec §2, §2b, §5, §6 và DoD D1–D12. Reviewer không triển khai các thay đổi sản phẩm đang được kiểm. Các review QC1.3, QC2.1 và QC3.1 trước đó của reviewer này cũng chỉ đọc source; không tự sửa candidate.

Đã đọc luồng điều phối runner, adapter manifest/result, process isolation, receipt/fingerprint/lease, readiness, transcript/cache và bộ kiểm benchmark; đối chiếu thay đổi integration/helper/fixture liên quan. Đã xem regression cho invalidation, lỗi publish/finalize, timeout/cancel, owner crash, join/reuse accounting, readiness disconnect và transcript mutation/privacy. Review này không thay thế chứng nhận POSIX thật, benchmark đủ mẫu hoặc browser QA bàn giao cuối.

Thao tác trong lượt review: đọc file/diff, LSP Python, tính hash; gọi các hàm verifier thuần đọc trên evidence đã lưu. Không chạy test, benchmark, setup, install, build, browser, sửa config/source/state/plan/report hoặc Git commit/merge. Tệp QC sơ bộ này là artifact duy nhất được tạo.

`source_sha256` được tính bằng chính `safe_run.source_snapshot(root)` trên 1398 input; khớp snapshot trước/sau của Full cuối và runtime cuối. Đây là snapshot harness với danh sách generated exclusions được công khai trong `safe_run.py:23–31,58–71`, không phải chứng minh scope hermetic để bật reuse. Eligibility/fingerprint sản phẩm được kiểm riêng trong `tdq_test_receipt.py`.

## 2. Evidence đã xác minh độc lập

### Full fresh cuối trên source QC3

[Receipt Full cuối](runs/QC-F1-final-after-QC3-20261031-6add68337dd44ca9b785b1603918f786/receipt.json) có child/harness exit 0, `verdict=PASS`, `elevated=false`, `failures=[]`; source/config/dependency trước–sau bằng nhau, isolation cleanup `complete`.

Lệnh trong receipt dùng runner production `tdq_test.py tron-bo`, workers 1, `--fresh --reuse off`, timeout 1800 giây. Reviewer đã gọi `verify_dod.verify_full` để kiểm digest binding từ stdout đến result, từng evidence file, raw execution sidecar, JUnit và coverage tính lại; không chỉ dựa vào dòng tổng pytest.

| Chỉ số | Kết quả |
|---|---|
| Case hiện tại | 3602 |
| Verdict chuẩn hóa | 3594 pass, 0 fail, 0 error, 8 skip, 0 xfail, 0 xpass |
| Coverage | Complete; missing/extra/duplicate đều rỗng |
| Baseline gốc | Đủ 3306 case; 0 remap |
| Action | `executed` |
| Wall runner | 1117.6745853999746 giây |
| Collection | 2.2236369000165723 giây |
| Execution | 1112.4460645000217 giây |
| Verify | 1.8569735000492074 giây |

Result được stdout receipt bind đến `docs/tdq/cache/test-runs/c030d75ca44ab99e/e23f6ac6de544713b9cc3c68b5224dda/result.json`, SHA-256 `2cdfe6b492528e488ad459f764647c37ac45cba485351ae091b34e95a09481dc`.

Tám skip có reason không rỗng và capability `runtime-reported`: ba case symlink không được môi trường hỗ trợ; bốn case cần hành vi POSIX/permission không có trên Windows; một case `tdq_state.py` không có argparse `--help`. Không dùng các skip này để chứng nhận POSIX.

### DoD D1–D8

[Kết quả verifier đã lưu](dod-checks-final-QC3.json) ghi PASS D1–D8. Reviewer cũng gọi `verify_regressions` trên Full raw đã xác minh và `verify_baseline`; các hàm này chỉ kiểm evidence, không chạy lại test.

| Check | Regression/assertion bắt buộc đã có evidence | Trạng thái sơ bộ |
|---|---:|---|
| D1 — coverage | 76 | Evidence phù hợp; đủ baseline 3306 → 3602 |
| D2 — skip/tokenizer | 27 | Evidence phù hợp |
| D3 — process/fixture/isolation | 14 | Evidence phù hợp trên Windows quyền thường |
| D4 — hồi quy/tương thích | 121 | Evidence phù hợp; giới hạn POSIX giữ rõ |
| D5 — reuse | 61 | Evidence phù hợp |
| D6 — join | 37 | Evidence phù hợp |
| D7 — readiness/batch | 18 | Evidence phù hợp |
| D8 — transcript | 20 | Evidence phù hợp |

SHA-256 `dod-checks-final-QC3.json`: `c14f087143e8bc25f5f5969ed8137faaf2225089c57becba5bbacfbb8cc2f7af`.

### Runtime smoke cuối

[Receipt runtime](runs/runtime-final-after-QC3-ed06898fbca3436baf4a965c036e004a/receipt.json) có exit 0, guard sạch, cleanup complete và cùng source snapshot Full. Reviewer gọi `tdq_runtime_bench.verify_report(runtime-final.json, expected_source=full.source_before)` chỉ đọc; kết quả `valid=true`, không có lỗi, đủ 6/6 scenario.

| Scenario | Thời gian giây | Evidence chính |
|---|---:|---|
| process-timeout | 3.422056 | Timeout giữ non-PASS bên trong; cleanup/heartbeat xác nhận cây owned dừng |
| process-cancel | 0.641515 | Cancel giữ non-PASS bên trong; cleanup/heartbeat xác nhận cây owned dừng |
| join | 5.785336 | Một execution; caller nhận `executed` và `joined`, cùng PASS |
| owner-crash | 5.926354 | Owner exit 1; kiểm bounded và cleanup |
| freshness | 5.685250 | Chuỗi action `executed`, `reused`, `executed` |
| transcript | 0.353202 | Warm hit có evidence, semantics được kiểm |

Các scenario là process thật trên fixture có nhãn `simulation`, không phải số đo toàn workflow trên log thật. Tất cả dưới 120 giây/scenario. Tên verdict máy `PERFORMANCE_MET` ở runtime chỉ áp dụng điều kiện runtime smoke, không chứng minh ngưỡng tăng tốc D9/D10.

[runtime-final.json](runtime-final.json) SHA-256: `60cd3107d1f61ec3e3bfd3e5633cc0b53305427b49a67d635805976bf4daca4d`.

## 3. Review mã nguồn và ranh giới kiến trúc

| Vùng / đầu ra | Đối chiếu source và evidence | Kết luận sơ bộ |
|---|---|---|
| O1 — Manifest/result | `tdq_test_manifest.py:22–26,88–128,303–348`; `tdq_test_result.py:368–432,465–519`: giữ ID/tham số, tách parent/subtest, kiểm phase/skip provenance, đối chiếu JUnit/sidecar; XPASS không thành PASS, lỗi quan sát được không bị thiếu evidence xóa mất. QC3 chụp context trước xdist, outcome/reason sau hook; regression serial/2 worker bao phủ cả pytest và unittest. | Không có finding mới |
| O2 — Isolation/process | `tdq_test_process.py`: bootstrap chỉ khởi chạy target sau khi gán Windows Job Object; kill-on-close, TerminateJobObject và active-process query kiểm cleanup. HOME/TMP/basetemp tách job/worker, không sửa HOME của caller. Một deadline chung cho collection/execution; timeout/cancel/cleanup lỗi bị runner hạ non-PASS. Không import state hoặc tests. | Không có finding mới; POSIX chưa được chứng nhận trên host thật |
| O3 — Eligibility/freshness | `tdq_test_receipt.py:98–193,287–369,622–661`: thiếu policy, case không được khai báo hoặc envelope không chứng minh được thì fresh; fingerprint gồm nội dung/file list, request/project, runtime/dependency/env/flags và implementation. Receipt cũ thiếu/corrupt/non-PASS không được reuse; kiểm lại input sau lookup/wait. Off là mặc định, fresh fence thu hồi proof cũ. | Không có finding mới |
| O3 — Lease/publication | `tdq_test_receipt.py:195–273,422–570`: PID kèm creation identity, không chiếm lease chỉ vì timestamp cũ; join có deadline và nonce. Publish nguyên tử, kiểm ownership, commit marker cuối cùng. Finalize lỗi giữ verdict/provenance đã quan sát và không để prepared PASS thành terminal proof. | Không có finding mới |
| Runner/accounting | `tdq_test.py:756–789,1019–1244,1307–1327`: collect trước execute trong sandbox; kiểm launch thực tế và manifest hai phase. Reused/joined có source receipt, execute_seconds=0; ledger không đếm lại chúng thành Full đã thực thi. Benchmark có classification riêng và vẫn được ghi/count công khai. | Không có finding mới |
| O4 — Readiness/live | `tdq_readiness.py`; `tdq_lsp.py:281–292,327–361,662–728`; setup/hook gọi theo chiều hiện có. Chỉ version binary và language inventory đi đường static cache; config/doctor/module/graph freshness và smoke vẫn live. Handoff kiểm digest lại; lỗi cache quay về probe. Mode mặc định off. | Không có finding mới; hiệu quả thời gian D10 còn thiếu |
| O5 — Transcript/privacy | `tdq_transcript.py:133–232,249–332,397–415,515–550`; `tdq_transcript_cache.py`: mỗi lookup đọc/hash toàn bytes, identity trước/sau; append/truncate/replace/delete/version làm miss hoặc partial. Cache trace chỉ giữ metadata/counter/issue/mark chuẩn hóa, không giữ prompt hoặc tool payload thô; selection, dedup, ghép span và quality tính lại. Atomic replace, retention và off oracle có regression. | Không có finding mới; không suy cache thành O(1) hoặc log thật complete |
| O6 — Benchmark/verifier | `tdq_runtime_bench.py:522–675`: bind raw result/evidence, kiểm detailed parity, launch/options, fresh/off, cùng source/environment, thứ tự cặp và wall components. Verifier không được nới để nhận metadata lệch. | Source phù hợp; chưa đủ evidence performance |
| Quy tắc tầng §5 | Process/receipt/manifest/result/cache không import hook/test helper để thực thi sản phẩm; receipt không import runner. Hook gọi scripts; không có thay đổi trực tiếp state writer trong vùng feature được review. Các tham số mới của API giữ keyword-only và mặc định bảo thủ. | Không có finding mới trong vùng chạm |

Các regression đã xem gồm invalidation source/config/env/dependency/flags; tampered evidence; fresh failure fence; publish/commit fault; worker launch mismatch; missing pytest không fallback full PASS; child ownership/control process; token unit fixture gọi `sinh_khoa` thật; reuse/join ledger; disconnect live; transcript cold/warm/off, privacy và unstable source. Full cuối đã chứa các test này; reviewer không chạy lại chúng.

Hai fixture QC3 chỉ ổn định metadata: `test_bao_cao_gitflow.py:128` giữ nguyên tập nhánh/assertion, thêm sort; `test_subagent_start.py:63–68` giữ bốn payload thực và rc==0, đổi label từ temp payload sang scenario. Không giảm case/assertion để đạt parity.

## 4. Phát hiện mã nguồn

**Không có finding correctness/kiến trúc mới được xác nhận trong phạm vi source và evidence đã review.** Đây là kết quả review sơ bộ, không phải bảo đảm không còn lỗi hoặc verdict QC cuối. Các giới hạn evidence bên dưới không được đổi thành lỗi mã nguồn khi chưa có bằng chứng quy nguyên nhân.

## 5. Evidence còn thiếu hoặc bị chặn

| Mục | Trạng thái và điều kiện còn thiếu |
|---|---|
| D9 — Full A/B | [benchmark-full.json](benchmark-full.json) hiện chỉ có một sample workers=1, PASS, wall 1159.9919125000015 giây. Sample2 bị ngắt; chưa đủ ba cặp đảo thứ tự, chưa thể chứng nhận detailed parity hoặc median giảm 20%. Không dùng cặp lịch sử trước QC3 thay proof trên source cuối. |
| Chặn môi trường | [Receipt benchmark cuối](runs/benchmark-full-final-after-QC3-9e893fa657584476a8a85ee20c8110ae/receipt.json) là FAIL; exit/harness -1, `config_guard: config changed during command`, cleanup complete. Leader báo `.codex/config.toml` đổi lúc 21:58:38 khi sample2 chạy, đã dừng đúng child40992/parent8904. Reviewer không tự quy tác giả ghi config; không sửa hoặc nới guard. |
| D10 — Reuse/readiness/transcript A/B | Chưa có proof cuối đủ ít nhất ba cặp cho từng đường và log thật theo hợp đồng. Unit/runtime fixture kiểm correctness không thay cho số đo cold/warm thực. |
| D11 — Agent QC cuối | Phần runtime có proof 6/6; tài liệu này là PRELIMINARY/INCOMPLETE. Chưa tạo verdict cuối hoặc binding D11 PASS khi D9/D10 chưa hoàn tất và findings chưa qua quy trình đóng cuối. |
| D12 — Report/browser | Chưa chứng nhận báo cáo MD/HTML cuối, số liệu/liên kết cuối và khả năng đọc desktop/mobile. Preview/checkpoint browser cũ không thay proof report cuối. Reviewer chưa mở browser trong lượt này. |
| POSIX | Chưa có host POSIX thật cho process-group/permission; giữ giới hạn này khi bàn giao. |

SHA-256 của snapshot [benchmark-full.json](benchmark-full.json) tại thời điểm review: `949935021aa6993fc14911def482d415423c5a7a02a429e5f6aa67f9d51e86a3`. Đây là report partial, không có chứng nhận performance cuối.

## 6. Điều kiện để chuyển sang QC cuối

1. Nguồn ghi cấu hình/ledger ngoài job phải dừng trong toàn cửa sổ đo; kiểm lại source, input fingerprint và dependency/config guard, không dựa riêng vào khoảng yên tĩnh ngắn.
2. Giữ mọi receipt/raw/sample bị đỏ hoặc ngắt. Chỉ dùng đủ mẫu mới hợp lệ trên input/source cuối để xác minh D9 và D10; đối chiếu detailed parity nguyên trạng.
3. Nếu có source/input drift, đánh giá lại tính hiện hành của Full/runtime theo hợp đồng; không tự mở rộng exclusion hoặc dùng snapshot harness thay fingerprint sản phẩm.
4. Hoàn thành QC độc lập cuối, xử lý finding nếu phát sinh, kiểm DoD còn lại và report/browser desktop/mobile. Tối ưu chưa đạt ngưỡng giữ off/serial theo fallback đã duyệt, không tuyên bố tăng tốc thành công.

Verdict của artifact này giữ **PRELIMINARY/INCOMPLETE**. Chỉ Full correctness và runtime có evidence hiện hành được xác minh ở đây; request và T5.5 chưa được tuyên bố hoàn tất.
