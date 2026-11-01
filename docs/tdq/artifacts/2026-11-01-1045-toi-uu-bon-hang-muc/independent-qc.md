# QC độc lập — Tối ưu bốn hạng mục
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-11-01 · Request: `2026-11-01-1045-toi-uu-bon-hang-muc` · Task: T4.3

- reviewer: `/root/gpt61sol_high_review_qc13`
- implementers: `/root`, `/root/gpt61sol_high_review_qc11`
- source_sha256: `6f03e5bec06c11ed1bc7d9c14609d09ce9f3b55f2fc0b069057c80cce97543bc`
- verdict: **PASS — QC nguồn cuối về correctness, runtime, kiến trúc/SOLID và Q1–Q7**.
- Finding chưa xử lý trong phạm vi QC: **0**. Các finding integrity trước đó đã được sửa và tái kiểm nguồn.
- Q8/browser/báo cáo bàn giao được kiểm riêng; không tuyên bố request đã hoàn tất hoặc chứng nhận phần trăm tăng tốc Full.

## 1. Phạm vi và tính độc lập

Reviewer đối chiếu spec §2/§3c/§4/§5/§6, plan, diff từ baseline và source cuối. Đã review calibration, Codex/process, test dữ liệu thuần, summary/render/export, runner integration, portable packaging và adapter telemetry của request. Reviewer chỉ đọc source/evidence, thực hiện verifier/tính hash chỉ đọc, rồi tạo hai artifact QC; không triển khai hoặc sửa source, không chạy lại test, runtime hoặc benchmark.

Source được tính lại bằng `safe_run.source_snapshot(root)` của helper frozen; khớp source trước/sau của Full và runtime cuối. Snapshot harness có generated exclusions công khai; không dùng nó thay điều kiện eligibility/fingerprint sản phẩm. Các artifact raw và receipt lịch sử vẫn được giữ, không nâng các lượt FAIL trung gian thành PASS.

Ngoại lệ telemetry được người dùng duyệt riêng tại [phụ lục](telemetry-exception-approved.md): chỉ bỏ giá trị scalar của `pluginUsage.*.usageCount` và `lastUsedAt` trong `.claude.json`. Presence/type/structure, plugin mới/xóa và toàn bộ cấu hình khác vẫn được kiểm. Receipt mới có schema/policy riêng, raw/projected audit và hash adapter/approval; helper và FAIL cũ không bị sửa. Không mô tả receipt theo policy này là raw config hoàn toàn không đổi.

## 2. QC-F1 — Full correctness và tương thích

[Receipt Full cuối](runs/QC-F1-final-a114787b746743078d2bfb03a7fdfab9/receipt.json) được kiểm lại bằng `verify_scope.full_result`: policy/receipt integrity, command production, fresh/off/workers1, digest TDQ_RESULT, raw sidecar/JUnit và coverage đều phù hợp. Child/harness exit 0, quyền thường, capture và cleanup complete; source/dependency ổn định. Raw config có đổi nhưng projected config không đổi theo đúng policy đã duyệt.

| Chỉ số | Kết quả |
|---|---|
| Case hiện tại | 3665 |
| Verdict chuẩn hóa | 3657 pass, 8 skip, 0 fail/error/xfail/xpass |
| Baseline | Giữ đủ 3602 case; 0 remap |
| Coverage | Complete, không missing/extra/duplicate |
| Runner wall | 1030.256894399994 giây |
| Result SHA-256 | `ec60b7816e0f7efc06f5b4784e3fd3f5c3ea0adf604ddbbeaac8cff700e7d7d2` |

[final-result.json](final-result.json) là bản sao byte-bound của result từ receipt, không phải result dựng lại. Tám skip có reason/capability: ba giới hạn symlink, bốn giới hạn POSIX/permission trên Windows, một entrypoint không dùng argparse `--help`. Không dùng Windows để chứng nhận POSIX thật.

**QC-F1: PASS** trên source cuối theo policy telemetry đã duyệt. Thời gian của một Full này không chứng minh phần trăm tăng tốc so với lượt lịch sử khác source/input.

## 3. QC-F2 — DoD và runtime

Reviewer gọi các hàm `verify_scope.verify` chỉ đọc trên index và evidence hiện hành, không chạy các test bên dưới lần nữa.

| Check | Regression được đối chiếu trong Full | Kết luận |
|---|---:|---|
| Q1 — validation sớm | 53 | PASS; lỗi xác định được bị từ chối trước measurement/output |
| Q2 — timeout/ownership | 57 | PASS; runtime timeout2s đáp ứng cap8s, descendant/HOME/control được kiểm |
| Q3 — giảm công việc test lặp | 322 | PASS; 11 changed tests có 11 migration/assertion mapping, baseline không mất case |
| Q4 — Top20 | 25 | PASS; hai bảng 20 hàng, sort/tổng phase/quality khớp kiểm độc lập |
| Q5 — offline export | 58 | PASS; cùng input SHA, offline không chạy suite, source verdict và atomic failure được giữ |
| Q6 — Full/tương thích | 7 | PASS; mixed identity, legacy result và portable export có regression |
| Q7 — logging/runtime/QC | 9 và 3 obligation logging | PASS trong QC này; bốn runtime contract đạt, reviewer/source/report được bind trong JSON kèm theo |

Q3 được verifier kiểm cả assertion mapping và receipt observation trước/sau, không chỉ so số test. [final-work-proof.json](final-work-proof.json) có **11 pure case thực tế bằng 0 subprocess/calibration/git**, cùng **bốn integration thực tế còn làm việc**: calibration có 403 process call/3 measurement/342 git; runner-to-ledger 3 process; worktree log 39 process/35 git; fixture Full A/B sáu job có 18 process. Đây là work-count thực, không phải benchmark tăng tốc tổng hoặc mở lại D9/D10.

[Receipt runtime cuối](runs/T4.2-author-final-4c5dde6a400d4dabb8afddff8638efad/receipt.json), [runtime.json](runtime.json) và [parent check](T4.2-parent-check.json) đã được reviewer kiểm lại digest, source, raw bindings, ownership/cleanup và facts bằng `runtime`/`runtime_contracts`.

| Scenario | Giây | Classification | Điều kiện được chứng minh |
|---|---:|---|---|
| calibration-valid | 11.3050513 | fixture-process | API/CLI thật gọi vòng đo và tạo output đủ mẫu; shell fixture cục bộ có nhãn |
| reject-early | 0.3452787 | real-process | Exit lỗi, 0 measurement, không output mới |
| timeout-cleanup | 2.7218578 | fixture-process | Timeout2s; có handshake descendant sống; process owned dừng, HOME lượt được dọn, control process/HOME khác nguyên vẹn |
| report-offline | 1.2800396 | real-process | 0 runner call; input SHA nguyên vẹn; đủ JSON/MD/HTML |

Tất cả dưới 120 giây/scenario. Reviewer đã đọc producer runtime: fixture `.cmd` tạo descendant thật, quan sát PID/HOME trước–sau; timeout dùng `_kiem_song` thật; không giả PID hoặc dùng mock thay proof OS. Không gọi fixture này là lần thực thi model/API Codex thật.

[Offline export cuối](runs/final-offline-export-ed7b52e79d6c40d4859e87c4e2cfb4d0/receipt.json) có guard PASS và TDQ_REPORT bind ba format vào cùng input `ec60b781…e7d7d2`. Summary trong result, CLI và renderer dùng cùng hợp đồng; report không biến FAIL/ERROR/INCOMPLETE của source thành PASS.

**QC-F2: PASS cho Q1–Q7 và runtime đã nêu.** Q8 HTML/bàn giao nằm ở T5.1/T5.2; không lấy verdict này thay browser QA hoặc việc đóng toàn request.

## 4. QC-F3 — source, kiến trúc và ràng buộc spec §5

| Vùng | Review kỹ thuật và kết luận |
|---|---|
| Calibration | `tdq_bench.py:562–640` tách parse/validation trước `_do_mot_luot`, parse log một lần, kiểm sample dương/hữu hạn và shortfall dự đoán trước đo; input hợp lệ vẫn đo thật và kiểm count quan sát sau đo. Giữ machine/manual/log provenance. PASS. |
| Codex/process | `tdq_codex.py:152–227,426–460` dùng primitive chung, version/say-hi có deadline riêng theo spec3c; HOME tạo dở được factory dọn nếu chưa return, HOME đã nhận được dọn riêng sau probe. `OwnedProcessJob` giữ caller env/HOME, `IsolatedJob` giữ API và lớp pytest; bootstrap chỉ chạy target sau assignment, stdin DEVNULL, shared cleanup budget5s, không kill theo tên toàn máy. PASS. |
| Test dữ liệu | Các case format/schema/log dùng API thật và fixture riêng; phần cơ khí được thay bằng dữ liệu ở đúng unit seam. Mục đích measurement, Git/worktree, CLI round-trip và ownership vẫn có integration thực tế, được mapping/work-count xác minh. PASS. |
| Summary/export | `tdq_test_report.py` chỉ dùng stdlib; tổng setup/call/teardown execution một lần, không cộng subtest lần hai; duplicate/invalid/missing giữ partial/unavailable, module incomplete không được rank như đầy đủ. Sort deterministic; HTML/Markdown escape; input SHA và JSON commit marker bind MD/HTML; lỗi staging/commit có rollback. PASS. |
| Runner | `_finish_run` finalize source/status/timing rồi tính summary một lần trước persist; CLI dùng field đã tính, TDQ_RESULT cuối, silent không thêm Top20, ledger loại summary lớn. Error summary/persist giữ FAIL/raw facts và bỏ summary/result artifact cũ. Fingerprint bind report module. `report` dispatch trước project/state resolver và không chạy lại suite. PASS. |
| Portable/release | Module report mới ở `scripts/`; existing packaging giữ dependency. Test budget giữ ngưỡng160 cho mọi file khác, chỉ miễn các runtime module đã duyệt và report mới; thêm regression HEAD import report thì release phải giữ module, kể cả đường filter. Không tăng trần chung hoặc bỏ assertion. PASS. |
| Quy tắc tầng | Hooks → scripts; không thêm scripts → hooks hoặc sản phẩm → tests. Process/summary không ghi state; state writer giữ tập trung. Không ghép ownership vào renderer; không thêm framework/service/dependency. PASS trong vùng thay đổi. |
| Guard và mặc định | Giữ worker1, reuse/cache off và Full fresh; adapter telemetry là ngoại lệ được duyệt, không sửa config cá nhân hoặc helper/FAIL cũ. Log metadata có timestamp/reason/cleanup; không in prompt/tool payload thô. PASS theo phạm vi đã phê duyệt. |

Đã kiểm `git diff --check` vùng source/test thay đổi, không có lỗi whitespace. Ruff **UNAVAILABLE**: không có command trên PATH, không có module; không cài thêm và không ghi Ruff PASS. Kiểm thủ công/Full không được trình bày như đã chạy Ruff.

**QC-F3: PASS** trong vùng thay đổi, với giới hạn OS và workflow metadata ghi ở §7.

## 5. QC-F4 — năm câu hỏi SOLID

Áp dụng `skills/tdq-conventions/references/clean-code.md`, theo cách đọc hàm/module của repository; không tạo abstraction chỉ để có tên nguyên tắc.

| Câu hỏi | Có/Không | Bằng chứng |
|---|---|---|
| SRP — mỗi hàm và lớp vừa viết có đúng một lý do thay đổi không? | Có trong vùng chạm | Calibration chuẩn bị input riêng vòng đo; ownership riêng env pytest; summary riêng renderer/export; runner điều phối qua API. Không nhét process control vào report. |
| OCP — có thể thêm một case bằng một dòng dữ liệu hoặc subclass, không mở thân hàm và không sửa lớp cũ không? | Có tại các điểm mở rộng đã review | HANG_SO, outcome/phase, format output và test ma trận dùng bảng/list; `IsolatedJob` bổ sung lớp env qua subclass của primitive chung. Không tuyên bố thêm backend/OS hoàn toàn mới chỉ cần một dòng. |
| LSP — khi có kế thừa, subtype thay parent không phá hợp đồng; khi không có kế thừa, mọi nhánh return giữ cùng type và error contract không? | Có | API init `IsolatedJob` giữ nguyên, enter trả self, run trả facts nhất quán; caller Codex giữ env, caller pytest vẫn isolated. Result/verdict lỗi không đổi thành PASS; legacy result có quality unavailable thay số0 giả. |
| ISP — mọi tham số truyền vào có thực sự được dùng bên trong không? | Có | Summary nhận result, renderer nhận summary; export nhận path/prefix/digest, không nhận toàn state. Process nhận env/deadline có mục đích; API mới keyword-only giữ caller cũ. |
| DIP — có đi qua shared entrypoint hiện có thay vì tự cài lại các chi tiết không? | Có | Codex và pytest dùng cùng primitive ownership; runner/report cùng summary API; CLI offline dùng exporter; formatter test gọi API/log thật thay tự dựng hành vi sản phẩm. |

**QC-F4: PASS qua review thủ công và evidence regression nguồn cuối.** Không suy đánh giá này thành bảo đảm toàn repository không có technical debt.

## 6. Finding và tái kiểm resolution

| Finding trước | Severity | Resolution đã đọc và kiểm |
|---|---|---|
| Helper frozen được load trước khi kiểm PINNED hash | P2 | `safe_run_telemetry.py:37–42` kiểm hash cả hai helper bằng stdlib trước mọi exec_module; regression mismatch không được load helper. Resolved. |
| Receipt mới còn được parse theo JSON permissive của helper cũ | P2 | `strict_json` từ chối duplicate keys, NaN/Infinity; validate receipt preparse, kiểm lại byte identity và giữ validator frozen. Regression duplicate schema và receipt ký lại có non-finite. Resolved. |
| Bool có thể bằng0 ở exit/harness guard | P2 | `safe_run_telemetry.py:199–202` dùng `type(...) is int` cho cả hai trường, regression False/True. Resolved. |

Adapter hiện hành SHA-256 `4691d65c5fbedfd4500d13f42ff3d7d6628a449cbaadf6f00df3c40bb6eba1e6`. Hai helper legacy vẫn đúng pinned hash. `normal_dispatch` relaunch đúng adapter qua `__file__`, raw/projected audit bảo vệ đủ config names/type/presence; schema/policy lạ hoặc audit/snapshot thiếu bị từ chối. Các sửa HOME allocation và cleanup log metadata cũng đã có regression trong Full nguồn cuối.

Không có finding correctness/kiến trúc mới chưa xử lý trong lần formal QC này. Reviewer không sửa mã nguồn để đóng finding.

## 7. Giới hạn và chuyển giao

- Không chứng nhận POSIX trên host thật; tám skip và reason giữ nguyên trong evidence.
- Không có benchmark A/B tương đương cho % tăng tốc Full; không mở lại D9/D10 của request trước. Work-count giảm và một lượt Full nhanh hơn lịch sử không đủ để suy %speedup.
- [Phase blocker](phase-transition-blocker.json) ghi phase còn `implement`: 11 worktree dirty của request cũ chặn chuyển metadata sang `qc`. Không xóa worktree/source, đánh closed giả hoặc bypass guard; đây là vướng mắc metadata chưa xử lý riêng, không bị che bởi verdict nguồn/evidence ở đây.
- Q8/report/browser và việc đóng toàn request là bước riêng. Reviewer không chạy browser trong lượt này và không lấy thông báo capture của tác giả thay chứng nhận độc lập Q8.
- Các raw FAIL/intermediate receipt giữ lịch sử; chỉ source-bound Full/runtime/final-work/export hiện hành được dùng cho verdict này.

**Kết luận T4.3: PASS — source `6f03e5bec06c11ed1bc7d9c14609d09ce9f3b55f2fc0b069057c80cce97543bc`, reviewer `/root/gpt61sol_high_review_qc13`, không finding chưa xử lý trong scope correctness/runtime/architecture và Q1–Q7.** JSON kèm theo bind report digest và các finding resolved; người phụ trách cập nhật evidence index/Q7, hoàn tất Q8/bàn giao và xử lý metadata blocker riêng. Không có quyền commit/push mới từ verdict này.
