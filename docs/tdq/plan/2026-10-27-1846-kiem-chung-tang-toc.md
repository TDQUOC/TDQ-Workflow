# PLAN — Kiểm chứng và tăng tốc TDQ Workflow

Ngày: 2026-10-27 · Spec: [bản 1.0 đã duyệt](../spec/2026-10-27-1846-kiem-chung-tang-toc.md) · Lane: full · QC: ultra
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — simulation trên plan này cho Winner đội, chênh 10,1 phút (main 40,7; team 30,7; hệ số agent 1,5). Calibration cũ chỉ là mô hình chọn mode, không phải ETA thực tế. (ĐÃ CHỌN: user trả lời 1a)
Trạng thái plan: **HOÀN THÀNH THEO PHẠM VI ĐIỀU CHỈNH** — 24 task thực hiện, 2 task benchmark SKIPPED_USER; không chứng nhận hiệu năng hoặc toàn DoD gốc 12/12. Phạm vi do user điều chỉnh ngày 2026-10-31; phê duyệt plan gốc giữ nguyên.

Spec được duyệt bằng “duyệt spec” lúc 2026-10-27T19:37:07+07:00, digest `99704b17f6dff9211df2599b1c3532741a14587c77d40cf8ed08a95f1bbdb66e`. Plan gốc đã duyệt, mode subagent; kết quả thực thi và bằng chứng cuối nằm trong báo cáo. Hai benchmark được user bỏ qua, gate report gốc phụ thuộc benchmark không áp dụng; không sửa spec hoặc verifier để thay đổi ngưỡng.

## Mục lục

- Quy tắc thi hành và lệnh kiểm
- Thiết kế Trước vs Sau
- P0 — Chuẩn bị chứng cứ và môi trường
- P1 — Nền tảng kiểm đúng
- P2 — Các module tối ưu
- P3 — Tích hợp và phép đo
- P4 — Log và kiểm hồi quy
- P5 — QC Ultra và benchmark
- P6 — Báo cáo và bàn giao
- Vùng ảnh hưởng, luật file nóng và cụm song song
- Ánh xạ đầu ra
- Definition of Done
- Ước tính và giới hạn

## Quy tắc thi hành và lệnh kiểm

1. Mỗi task chuyển `[ ]` → `[~]` → test đỏ có ý nghĩa → thực hiện → test xanh → `[x]` ngay. Không tạo lỗi giả, xóa assertion hoặc sửa expected chỉ để xanh. Phụ thuộc nằm ở `Cần:`; không triển khai trước khi user duyệt plan và chọn mode.
2. Chỉ sửa vùng file đã khai. Mở rộng để giữ hợp đồng phải ghi ảnh hưởng, cập nhật task chủ; thay đổi thiết kế/đầu ra cần trở lại gate phù hợp. Không commit, merge, push, release hoặc cập nhật plugin cài trên máy.
3. Mọi collection/test/subprocess chạy dưới quyền thường và HOME/USERPROFILE/basetemp riêng. Chụp digest cấu hình thật trước/sau; không sao chép secret. Nếu host đang elevated, dùng đường chạy quyền thường đã kiểm chứng; không chứng nhận kết quả elevated là baseline user thường. Giữ nguyên encoding nghiệp vụ, không áp PYTHONUTF8 toàn cục để làm xanh.
4. Test state dùng `TDQ_PROJECT_DIR` trỏ project fixture; thao tác quản lý request thật vẫn qua state CLI. T0.1 dựng harness artifact riêng, không phải framework mới trong sản phẩm. Lệnh kiểm harness tự chạy trong workspace tạm.
5. Test vùng chạm chạy sau task; khi runner mới chưa sẵn dùng pytest module cụ thể bên dưới. Sau T3.1 dùng thêm runner `vung-cham --khong-ep-tron-bo`. Chỉ chạy Full correctness tại QC-F1 và lần cuối sau sửa QC. Sáu lượt Full A/B là benchmark riêng, có ledger đầy đủ, không dùng để giấu số lượt chạy.
6. Cache off, reuse off, workers=1 khi bàn giao. Full QC luôn fresh. Tăng tốc không đạt ngưỡng được ghi lệch và dùng fallback spec; lỗi correctness phải sửa, không đổi thành cảnh báo hiệu năng.
7. Lệnh có `$TdqEvidence`/`$TdqSafeRun` dùng hai biến PowerShell bên dưới. Harness trả nguyên exit code, ghi stdout/stderr, timeout và fingerprint; không coi lỗi không tạo receipt là PASS. `verify_dod.py` kiểm bằng chứng thật và digest, không chỉ đọc một boolean PASS. Mất file, evidence cũ, thiếu case hoặc config bị đổi đều trả nonzero.

```powershell
$TdqEvidence = 'docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc'
$TdqSafeRun = "docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/safe_run.py"
```

## Thiết kế Trước vs Sau

| Vùng | Hiện tại | Sau dự kiến |
|---|---|---|
| Coverage | 3306 case tổng hợp từ nhiều lượt; full cũ bỏ sót pytest function | Manifest ID và observed outcomes trong cùng job; missing/XPASS/all-skip không PASS |
| Runner | Auto workers, bỏ plugin tmpdir; thiếu timeout cây con | 1 worker mặc định, legacy parallel=2, fixture riêng và timeout/cancel có ownership |
| Test lặp | Chạy lại; thiếu receipt đủ kiểm chứng | Eligible cùng key mới reused/joined; fresh luôn chạy, FAIL không bị che |
| Preflight và log | Probe/parse có phần lặp | Readiness giữ live probe; transcript hash toàn nội dung rồi reuse parse từng file |
| Đề xuất tốc độ | Mẫu nhỏ cũ, không đại diện suite hiện tại | 3 cặp Full A/B và 3 cặp mỗi cache, báo mọi sample, variance và fallback |

Giữ [preview đã duyệt](../spec/2026-10-27-1846-kiem-chung-tang-toc-preview.html) và [manifest](../spec/2026-10-27-1846-kiem-chung-tang-toc-preview.manifest.json); không sinh thiết kế khác. Task T1.2/T1.3/T2.1/T3.1 ứng với nhánh test; T2.2/T2.3 ứng với nhánh readiness/transcript; T3.2/T5.3/T5.4 ứng với phép đo. Quy tắc freshness và non-PASS áp dụng mọi nhánh.

## P0 — Chuẩn bị chứng cứ và môi trường

- [x] **T0.1** (e16m) Tạo harness quyền thường, snapshot cấu hình, môi trường riêng và bộ kiểm evidence D1–D12; fixture tự kiểm phát hiện receipt giả/thiếu/đổi digest, config mutation và timeout. — Test: `python -X utf8 "docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/safe_run.py" --self-test`
  - Chạm: `docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/safe_run.py`, `docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/verify_dod.py`
  - Lưu source/OS/Python/package/privilege và inventory 3306 case cũ làm đối chiếu, không gọi đó là kết quả full mới. Harness có timeout ngoài, chỉ dừng cây nó sở hữu; checker yêu cầu source fingerprint cuối phù hợp.
- [x] **T0.2** (e3m) Kiểm lại binding preview và spec đã duyệt; ghi receipt liên kết làm mốc kiến trúc. — Test: `python -X utf8 C:/Users/admin/Documents/Projects/ForAgentCode/TDQ-Workflow/scripts/tdq_archify.py verify --project C:/Users/admin/Documents/Projects/ForAgentCode/TDQ-Workflow --document C:/Users/admin/Documents/Projects/ForAgentCode/TDQ-Workflow/docs/tdq/spec/2026-10-27-1846-kiem-chung-tang-toc.md --manifest C:/Users/admin/Documents/Projects/ForAgentCode/TDQ-Workflow/docs/tdq/spec/2026-10-27-1846-kiem-chung-tang-toc-preview.manifest.json`
  - Dùng: `archify`
  - Để: kiểm manifest/digest của preview đã duyệt theo hướng dẫn Archify đã dùng ở spec.
  - Ra: `docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/preview-binding-check.json`.
  - Kiểm: `python -X utf8 C:/Users/admin/Documents/Projects/ForAgentCode/TDQ-Workflow/scripts/tdq_archify.py verify --project C:/Users/admin/Documents/Projects/ForAgentCode/TDQ-Workflow --document C:/Users/admin/Documents/Projects/ForAgentCode/TDQ-Workflow/docs/tdq/spec/2026-10-27-1846-kiem-chung-tang-toc.md --manifest C:/Users/admin/Documents/Projects/ForAgentCode/TDQ-Workflow/docs/tdq/spec/2026-10-27-1846-kiem-chung-tang-toc-preview.manifest.json` trả 0 chỉ khi binding và file liên quan khớp.
  - Không dùng cho: render thiết kế mới, sửa repo Archify hoặc chứng nhận implementation.
  - Cần: T0.1

## P1 — Nền tảng kiểm đúng

- [x] **T1.1** (e12m) Chuẩn hóa helper tokenizer portable và inventory fixture độc lập máy; thực thi đủ sáu assertion cũ, giữ skip capability có lý do. — Test: `python -X utf8 docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/safe_run.py --label T1.1 -- python -m pytest -q tests/test_skill_tokens.py`
  - Chạm: `tests/helper.py`, `tests/test_skill_tokens.py`
  - Cần: T0.2
- [x] **T1.2** (e18m) Tạo manifest case và bổ sung result v2: mixed/param/class/subtest, skip/xfail/xpass, duplicate/collection error, missing/extra; giữ keys cũ và mapping JUnit. — Test: `python -X utf8 docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/safe_run.py --label T1.2 -- python -m pytest -q tests/test_tdq_test_manifest.py tests/test_tdq_test_result.py`
  - Chạm: `scripts/tdq_test_manifest.py`, `scripts/tdq_test_result.py`, `tests/test_tdq_test_manifest.py`, `tests/test_tdq_test_result.py`
  - Cần: T1.1
- [x] **T1.3** (e22m) Tạo process adapter: isolated collection/execution, per-job/worker temp, timeout toàn job, cancel và Windows ownership; POSIX group có nhánh kiểm riêng. — Test: `python -X utf8 docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/safe_run.py --label T1.3 -- python -m pytest -q tests/test_tdq_test_process.py`
  - Chạm: `scripts/tdq_test_process.py`, `tests/test_tdq_test_process.py`
  - Cần: T1.1
  - Smoke process thật phải chứng minh child đã dừng, PID lạ không bị kill và non-PASS giữ nguyên. Không chỉ mock subprocess; POSIX chưa chạy ghi chưa chứng nhận.

## P2 — Các module tối ưu

- [x] **T2.1** (e24m) Tạo receipt/fingerprint và atomic lease: default-deny eligibility, invalidation toàn envelope, owner PID/start/nonce, join deadline, crash/cancel và terminal verdict. — Test: `python -X utf8 docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/safe_run.py --label T2.1 -- python -m pytest -q tests/test_tdq_test_receipt.py`
  - Chạm: `scripts/tdq_test_receipt.py`, `tests/test_tdq_test_receipt.py`
  - Cần: T1.2, T1.3
  - Mutation từng source/test/untracked/file-list/docs-read/config/dependency/interpreter/OS/privilege/env/flag/selector/schema/fixture/project/request; secret chỉ digest. Before/after mismatch, thiếu evidence, legacy hoặc FAIL không reused. Test mới chưa khai dependency giữ ineligible.
- [x] **T2.2** (e20m) Tạo và tích hợp readiness cache opt-in với live probe; truyền kết quả setup ngay invocation, giữ invalidation config/binary/source/graph/disconnect. — Test: `python -X utf8 docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/safe_run.py --label T2.2 -- python -m pytest -q tests/test_tdq_readiness.py tests/test_tdq_setup.py tests/test_tdq_lsp.py tests/test_tu_khoi_tao.py tests/test_auto_update_setup.py`
  - Chạm: `scripts/tdq_readiness.py`, `scripts/tdq_setup.py`, `scripts/tdq_lsp.py`, `hooks/scripts/session_start.py`, `tests/test_tdq_readiness.py`, `tests/test_tdq_setup.py`, `tests/test_tdq_lsp.py`, `tests/test_tu_khoi_tao.py`, `tests/test_auto_update_setup.py`
  - Cần: T1.2, T1.3
  - Không cache kết quả symbol query thành sự thật; không thay policy updater/install. Hook gọi scripts đúng chiều kiến trúc, không import ngược.
- [x] **T2.3** (e18m) Tạo cache parse từng transcript và tích hợp timing; hash toàn nội dung, stable read, normalized events, recompute aggregate/filter/dedup/quality. — Test: `python -X utf8 docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/safe_run.py --label T2.3 -- python -m pytest -q tests/test_transcript_cache.py tests/test_transcript.py tests/test_timing.py tests/test_timing_lifecycle.py`
  - Chạm: `scripts/tdq_transcript_cache.py`, `scripts/tdq_transcript.py`, `scripts/tdq_timing.py`, `tests/test_transcript_cache.py`, `tests/test_transcript.py`, `tests/test_timing.py`, `tests/test_timing_lifecycle.py`
  - Cần: T1.2, T1.3
  - Đổi file thì reparse toàn file; append/truncate/replace/delete/parser-version/request-window đều được kiểm. Active/unreadable/partial không báo complete. Không lưu raw prompt/tool payload vào cache/report.

## P3 — Tích hợp và phép đo

- [x] **T3.1** (e25m) Tích hợp runner duy nhất với manifest/process/receipt; CLI và API cũ, worker hữu hạn, full mixed dùng pytest, action/provenance/ledger không đếm giả. — Test: `python -X utf8 docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/safe_run.py --label T3.1 -- python -m pytest -q tests/test_tdq_test.py tests/test_tdq_runner_integration.py`
  - Chạm: `scripts/tdq_test.py`, `tests/test_tdq_test.py`, `tests/test_tdq_runner_integration.py`
  - Cần: T2.1
  - Thực hiện lần lượt P0 fresh path rồi P1 reused/joined trong cùng task chủ file. Test cả defaults, --workers, --parallel=2, xung đột usage error, --timeout-seconds=1800, --fresh, --reuse off|auto và positional API cũ/new keyword-only. Bỏ `-p no:tmpdir`; không auto toàn CPU. Thiếu pytest khi suite mixed trả incomplete/error.
- [x] **T3.2** (e18m) Tạo CLI benchmark và verifier samples có schema: full-pairs, cache-pairs, runtime-smoke, verify; thứ tự đảo, hash/case parity, mọi failure và verify/wait/execute/resource time. — Test: `python -X utf8 docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/safe_run.py --label T3.2 -- python -m pytest -q tests/test_tdq_runtime_bench.py`
  - Chạm: `scripts/tdq_runtime_bench.py`, `tests/test_tdq_runtime_bench.py`
  - Cần: T3.1, T2.2, T2.3
  - Dùng public APIs/CLI, không sửa rule PASS. Fixtures nhỏ kiểm phép tính/false parity/timeouts và simulated label; suite thật chạy ở T5.3. CLI output lưu JSON/JSONL cùng evidence digest; thiếu mẫu không được verifier chấp nhận.
- [x] **T3.3** (e8m) Viết hướng dẫn batch read độc lập, activation/off/fresh/1 worker và fallback theo bằng chứng; giữ gate/QC và thứ tự mutation. — Test: `python -X utf8 scripts/doc_lint.py skills/tdq-intake/SKILL.md skills/tdq-setup/SKILL.md skills/tdq-conventions/SKILL.md skills/tdq-conventions/references/context-budget.md skills/tdq-build/references/runtime-speed.md`
  - Chạm: `skills/tdq-intake/SKILL.md`, `skills/tdq-setup/SKILL.md`, `skills/tdq-conventions/SKILL.md`, `skills/tdq-conventions/references/context-budget.md`, `skills/tdq-build/references/runtime-speed.md`, `docs/tdq/token-budget.json`
  - Điều chỉnh triển khai: viết hướng dẫn theo CLI đã có trong lúc benchmark hoàn thiện; T4.2 vẫn chờ mọi task tích hợp được chứng nhận. Sửa cả context-budget để không giữ luật batch mâu thuẫn; cập nhật token lock bằng công cụ có sẵn, không tăng giới hạn.
  - Cần: T2.2, T2.3
  - Không sửa plugin cache đã cài. Tách hướng dẫn opt-in khỏi khuyến nghị: chỉ report có số đo đạt mới khuyến nghị bật; gate/mutation/dependent read luôn tuần tự.

## P4 — Log và kiểm hồi quy

- [x] **T4.1** (e8m) Kiểm log service các module mới: mặc định bật, timestamp/reason/action/verify-wait-execute, cấu hình tắt, không secret/raw payload; yêu cầu task chủ sửa nếu thiếu. — Test: `python -X utf8 docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/safe_run.py --label T4.1 -- python -m pytest -q tests/test_runtime_logging.py`
  - Chạm: `tests/test_runtime_logging.py`
  - Cần: T2.2, T2.3
  - Log được viết cùng implementation tại từng task chủ; task này kiểm hợp đồng xuyên module, không tạo thêm service framework. Có thể chuẩn bị test trên candidate T3.1/T3.2 đã freeze API; T4.2 vẫn yêu cầu chứng nhận đầy đủ cả hai task trước Full.
- [x] **T4.2** (e12m) Hoàn thiện unit/regression xuyên tầng và dependency boundary; kiểm bộ test mới có case lỗi thật, coverage/timing/accounting và rollback. — Test: `python -X utf8 docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/safe_run.py --label T4.2 -- python -m pytest -q tests/test_runtime_contracts.py tests/test_tdq_test_manifest.py tests/test_tdq_test_process.py tests/test_tdq_test_receipt.py tests/test_tdq_readiness.py tests/test_transcript_cache.py tests/test_tdq_runtime_bench.py tests/test_tdq_runner_integration.py tests/test_runtime_logging.py`
  - Chạm: `tests/test_runtime_contracts.py`
  - Cần: T3.3, T2.2, T2.3, T0.1
  - Chuẩn bị test xuyên tầng trên candidate đã tích hợp; chỉ chạy lệnh chứng nhận khi mọi dependency đã freeze. T5.1 giữ gate chứng nhận T2.1/T3.1/T3.2/T4.1/T4.2, không bỏ qua task đang chờ môi trường.
  - Kiểm scripts không import hooks/tests, không ghi state trực tiếp; bảo toàn ledger lịch sử và CLI reader cũ. Dùng fixture kiểm corruption, không chỉ assert mirror implementation.

## P5 — QC Ultra và benchmark

- [x] **T5.1** (e14m) QC-F1 chạy full fresh trên source đã tích hợp; expected/observed khớp, đối chiếu 3306 case gốc + case mới và giải thích mọi skip/remap. — Test: `python -X utf8 docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/safe_run.py --label QC-F1 --archify-chrome "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" -- python scripts/tdq_test.py tron-bo --repo . --workers 1 --fresh --reuse off --timeout-seconds 1800`
  - Cần: T4.2, T4.1, T3.2, T3.1, T2.1
  - Không dùng 3206/3306 của lượt cũ thay cho kết quả mới. Thu manifest/outcomes/config digest và command/environment receipt. Chỉ chuyển benchmark khi correctness đạt.
- [x] **T5.2** (e12m) Smoke runtime thực tế: tmp_path, timeout/cancel/descendants, hai caller join, owner crash, freshness và cold/warm log; giới hạn ngoài 120 giây mỗi kịch bản. — Test: `python -X utf8 docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/safe_run.py --label runtime --archify-chrome "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" -- python scripts/tdq_runtime_bench.py runtime-smoke --scenario-timeout 120 --output "docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/runtime.json"`
  - Cần: T5.1
  - Fixture process/log dựng được gắn simulation; log Claude/Codex thật là nhóm riêng, giữ privacy. Evidence gồm elapsed, child identities và verdict, không chỉ exit code cha.
- [x] **T5.3** — **SKIPPED_USER** Người dùng bỏ qua benchmark Full bằng “có thể skip bench mà tổng hợp cho tôi ko?”. Đã giữ mọi mẫu/receipt; không chứng nhận parity hay ngưỡng tăng tốc. — Kiểm: benchmark-user-waiver-20261031.md, lệch Q9 đã duyệt.
  - Cần: T5.2
  - Timeout từng job 1800 giây, harness toàn phép đo phải đủ sáu job và cleanup, không áp timeout smoke cho Full. Giữ raw samples cả failed/retry. Chỉ khuyến nghị 2 workers khi parity đạt và median giảm ít nhất 20%; nếu không giữ serial, ghi lệch hiệu năng.
- [x] **T5.4** — **SKIPPED_USER** Người dùng bỏ qua benchmark cache/reuse/readiness/transcript. Giữ các tính năng off, không chứng nhận lợi ích cold/warm hoặc log thật. — Kiểm: benchmark-user-waiver-20261031.md, lệch Q10 đã duyệt.
  - Cần: T5.3
  - Cache cold/warm dùng cùng implementation/input; reset cache theo namespace đã xác nhận, không xóa rộng. Đường không warm nhanh hơn giữ off. Fixture nhỏ không được dùng suy ra % tăng tốc session thật.
- [x] **T5.5** (e20m) Agent QC độc lập review code/DoD/receipts, kiến trúc và adversarial checks; xử lý findings trong task chủ, chạy vùng chạm và Full fresh cuối nếu có sửa QC. — Test: `python -X utf8 "docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/verify_dod.py" D11`
  - Cần: T5.4
  - Agent độc lập bắt buộc dù build main; không tự suy thành chọn subagent mode. Ghi findings có file/line/severity, verdict và evidence; tối đa vòng QC theo skill. Source đổi sau benchmark làm proof hết hiệu lực: đo lại phần chịu ảnh hưởng và Full khi cần, không dùng số cũ cho bản mới.

## P6 — Báo cáo và bàn giao

- [x] **T6.1** (e12m) Viết QC và report Markdown/HTML: trước–sau, tất cả mẫu, wall/resource time, giới hạn POSIX, đề xuất tiếp theo, cách tắt và provenance link; không kết luận speedup khi D9/D10 SKIPPED_USER. — Kiểm phạm vi điều chỉnh: gọi trực tiếp `verify_dod.verify_report` với `evidence-index.json:summary_report`, lưu kết quả và lệnh trong `summary-scope-validation.json`; không gọi gate report gốc phụ thuộc benchmark.
  - Chạm: `docs/tdq/qc/2026-10-27-1846-kiem-chung-tang-toc.md`, `docs/tdq/reports/2026-10-27-1846-kiem-chung-tang-toc.md`, `docs/tdq/reports/2026-10-27-1846-kiem-chung-tang-toc.html`
  - Cần: T5.5
  - Báo rõ ngưỡng nào đạt, ngưỡng nào dùng fallback; không hứa giảm % tổng session từ sample riêng lẻ. Giữ nguyên lỗi/lượt thử lịch sử, tách job correctness và benchmark.
- [x] **T6.2** (e6m) Kiểm report desktop/mobile, link evidence và chốt D1–D8/D11 theo source cuối; D9/D10 SKIPPED_USER, D12 kiểm báo cáo theo phạm vi điều chỉnh. — Kiểm: `verify_dod.verify_report` và Chrome DevTools MCP, lưu `summary-scope-validation.json` cùng `report-browser.json`; không thay verifier hoặc tuyên bố gate benchmark gốc PASS.
  - Dùng: `tdq-browser-test` (mcp)
  - Để: preflight MCP/DevTools trước, kiểm HTML desktop/mobile, overflow, nội dung và links; lưu screenshots và console verdict.
  - Ra: `docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/report-browser-check.json` và ảnh tương ứng.
  - Kiểm: `verify_dod.verify_report` kiểm số liệu, receipt/browser evidence và tất cả liên kết local trong phạm vi mới đã được user yêu cầu.
  - Không dùng cho: thay benchmark bằng browser timing hoặc tự publish report.
  - Cần: T6.1
  - Nếu MCP mất kết nối, hướng dẫn kết nối trước; fallback kiểm file/render phải báo riêng, không gọi là đã đạt visual QA.

## Vùng ảnh hưởng, luật file nóng và cụm song song

LSP Python đã khởi động và trả references sau indexing: `chay_tron_bo_result` 4 (2 production/2 test), `read_transcripts` 13 (2/11), `from_junit_xml` 2, `chay_kiem` 6, `kiem_mot_lenh` 2, `doc_san_sang` 10, `khoi_tao_nen` 13, `co_bo_dem_token` 11. Không coi lần trả lỗi indexing là không có caller. Đối chiếu exact-name grep và graph canonical hai bước trong analyze: runner → wrapper/CLI; transcript → timing.tong_hop → timing.main. Graphify CLI bản này không có affected/query; dùng graph có fingerprint nguồn, không bịa output CLI.

| Vùng | Task chủ ghi | Consumer phải regression |
|---|---|---|
| helper/tokenizer | T1.1, hoàn thành sớm | Test dùng co_bo_dem_token; bộ Full |
| manifest/result | T1.2 | runner/JUnit/ledger readers, T3.1/T4.2 |
| process | T1.3 | runner và benchmark; runtime smoke |
| receipt | T2.1 | runner, two-callers, benchmark |
| setup/LSP/session_start | T2.2 | search_rules/readiness readers, auto-update/setup tests |
| transcript/timing | T2.3 | timing lifecycle/report counter readers |
| tdq_test.py và integration tests | T3.1 duy nhất | CLI legacy, vung-cham/tron-bo, mixed suite |
| runtime benchmark | T3.2 duy nhất | verifier, raw samples, report |
| skill hướng dẫn | T3.3 duy nhất | doc_lint, review thứ tự gate/batch |

**Luật file nóng:** một file chỉ có một task chủ ở `Chạm:`. T1.1 nâng helper lên trước; T3.1 giữ toàn bộ tích hợp runner, không tách nhiều agent cùng sửa tdq_test.py. T4/T5 phát hiện thiếu phải giao lại task chủ, không tạo writer cạnh tranh. Leader sở hữu plan/state/log và ghép evidence. Các consumer chỉ đọc trong task khác, không mở rộng write scope ngầm.

## Cụm song song

Nếu user chọn subagent, T0 → T1.1; sau đó T1.2 và T1.3 độc lập; tiếp T2.1/T2.2/T2.3 có thể chia ba nhánh; T3.1 chỉ chờ T2.1, T3.2 đợi cả ba nhánh tích hợp; T3.3 và T4.1 độc lập sau T3.2, T4.2 đợi cả hai. T5.1 đến T6.2 tuần tự. T6.2 có `(mcp)` giữ ở leader có tool. T0 harness, toàn suite, benchmark và state/log giữ một owner; không benchmark cạnh job test khác. Nếu main, theo topo này tuần tự; agent QC vẫn độc lập.

Trước sửa một symbol chưa có trong khảo sát phải tra references bổ sung và kiểm diagnostics sau sửa. Các file mới chưa có callers; dependency dự kiến ở bảng trên là hợp đồng tích hợp, không giả là LSP đã thấy code mới.

## Ánh xạ đầu ra

| Đầu ra spec §2 | Task triển khai | Bằng chứng |
|---|---|---|
| O1 Manifest/kết quả | T1.2, T3.1 | D1, D2, D4 |
| O2 Isolation/timeout/worker/tokenizer | T1.1, T1.3, T3.1 | D2, D3, D4 |
| O3 Receipt/reuse/join | T2.1, T3.1 | D5, D6 |
| O4 Readiness/batch | T2.2, T3.3 | D7 |
| O5 Transcript cache | T2.3 | D8 |
| O6 Benchmark/opt-in/rollback | T3.2, T3.3, T5.3, T5.4 | D9, D10 |
| O7 QC/report/evidence | T0.1, T4.1, T4.2, T5.1, T5.2, T5.5, T6.1, T6.2 | D11, D12 |

## Definition of Done

Đúng 12 ô, tương ứng 12 dòng spec §6. Một lệnh mỗi ô; verifier đọc bằng chứng của các task, không chạy Full thêm 12 lần. Evidence phải gắn source cuối và test outcome thật. D9/D10 trả kết quả có nhãn `PERFORMANCE_MET` hoặc `FALLBACK_RECORDED`; fallback chỉ được chấp nhận khi dữ liệu đo đủ, correctness đạt, trạng thái off/serial và bản ghi lệch tồn tại. Không gắn nhãn đạt tốc độ cho fallback.

- [x] D1 Expected/observed từng case khớp, có mixed/param/duplicate/error/subtest và đối chiếu 3306 gốc + case mới. — `python -X utf8 "docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/verify_dod.py" D1`
- [x] D2 Đủ sáu assertion tokenizer thực thi bằng fixture; skip có lý do/capability, không giấu lỗi. — `python -X utf8 "docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/verify_dod.py" D2`
- [x] D3 tmp_path, isolation, timeout/cancel, child cleanup thật và cấu hình thật không đổi. — `python -X utf8 "docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/verify_dod.py" D3`
- [x] D4 Full fresh cuối đủ inventory, CLI/ledger v2 tương thích, failure provenance, giới hạn POSIX khai rõ. — `python -X utf8 "docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/verify_dod.py" D4`
- [x] D5 Reuse có provenance, mutation toàn fingerprint/eligibility và evidence corruption không trả PASS giả. — `python -X utf8 "docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/verify_dod.py" D5`
- [x] D6 Hai caller một job, verdict đúng; owner crash/cancel/lease bounded, khác flags không join. — `python -X utf8 "docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/verify_dod.py" D6`
- [x] D7 Readiness warm giảm probe tĩnh, vẫn live-check và invalidation; batch không đảo dependency/gate. — `python -X utf8 "docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/verify_dod.py" D7`
- [x] D8 Transcript cold/warm/off cùng dữ liệu nghiệp vụ, mutation/active-file không báo complete sai. — `python -X utf8 "docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/verify_dod.py" D8`
- [x] D9 **SKIPPED_USER, không phải PASS hiệu năng.** Bỏ qua ngưỡng ba cặp/parity/median theo yêu cầu người dùng; giữ1worker. Quyết định Q9 đã duyệt.
- [x] D10 **SKIPPED_USER, không phải PASS hiệu năng.** Bỏ qua ngưỡng ba cặp cache theo yêu cầu người dùng; giữ reuse/readiness/transcript off. Quyết định Q10 đã duyệt.
- [x] D11 Runtime từng scenario ≤120 giây, QC độc lập có evidence, không còn lỗi correctness trong phạm vi kiểm. — `python -X utf8 "docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/verify_dod.py" D11` PASS; nhãn runtime `PERFORMANCE_MET` chỉ là ngân sách scenario, không chứng nhận speedup D9/D10.
- [x] D12 **Phạm vi điều chỉnh theo user — PASS component report, không phải PASS gate benchmark gốc:** Report MD/HTML đủ số đo đã có, raw samples, giới hạn, before/after, rollback; desktop/mobile và links đạt qua `verify_dod.verify_report`. Gate CLI D12 gốc yêu cầu D9/D10 đầy đủ: không áp dụng theo waiver, không ghi PASS gốc.

## Ước tính và giới hạn

Tổng 7 phase, 20 task, 348 phút (5 giờ 48 phút) khi cộng ước tính từng task, không gồm chờ duyệt; có khoảng 65 phút cho sáu Full samples dựa baseline lịch sử 688 giây/lượt serial. Đây là dự toán công việc tuần tự, không phải cam kết thời gian hay tốc độ sẽ đạt. QC fix hoặc benchmark hết hiệu lực sẽ làm tăng thời gian và được ghi rõ.

Simulation mode dùng plan này, hệ số agent 1.5 và calibration `docs/tdq/bench/2026-08-17-2001-smoke-test-main-vs-doi-thuc-do.json`. Kết quả: 20 task, 12 assignable, 8 leader, 10 wave; main 40,7 phút, team 30,7 phút, Winner đội (gap 10,1 phút theo số chưa làm tròn). Mô hình dùng thời lượng task từ calibration, không dùng tổng eNm 348 phút; tuyệt đối không báo 30,7 phút là thời gian thực hiện cả request. Calibration cũ khác OS/workload; kết quả chỉ hỗ trợ chọn cách triển khai, không thay benchmark sản phẩm T5.3/T5.4. Receipt: [plan-mode-simulation.txt](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/plan-mode-simulation.txt). Không chọn mode thay user.

Ghi chú triển khai: Test command dùng đường dẫn cụ thể để tdq_team.check chạy được. Tích hợp file đã review bằng copy và đối chiếu SHA; không commit, merge Git, push hoặc cập nhật plugin đã cài. Giữ evidence độc lập của từng worktree.

Ghi nhan T2.2: 143 tests PASS; peer review tim thay cache inventory can dung cung quy tac bo qua generated cache. Regression input-change-during-read da RED that; dang sua truoc khi dong task. Cache chi static version/inventory, doctor va smoke luon live.

T2.2 done: live doctor disconnect regression, source/config/graph/filelist invalidation, same inventory exclusion, handoff stamp neutrality, receipt read race regression PASS. Conservative hash cost stays measured in T5.4; default cache off.

T2.2 final review: handle input becoming unreadable during warm verification with fresh fallback; split receipt validation/publication to keep each function under complexity ceiling.

T2.3 integrated: 167 PASS, no skip, ordinary privilege, config digests unchanged. T2.2 source tests 147 PASS but guard rejected a run because real .claude.json changed; retain attempt and verify again, cause not yet established.

T2.2 config recheck: 147 tests PASS under ordinary user and config guard PASS; failed concurrent-config attempt retained.

T2.2 benchmark contract: add optional stats dictionary to report real cache hit/miss, verify/execute/write timings. Existing return values and default-off behavior remain unchanged; needed for D10 measurement.

T2.2 telemetry tested and guard PASS: optional stats carries static probe hits/misses/probe_calls and verify/execute/write/wait timings; total ladder wall includes live checks separately.

T2.1 integrated quiet: 57 tests PASS, config guard PASS. Concurrent tool activity correlates with pluginUsage drift; keep strict guard and run final correctness/benchmarks without concurrent tool/agent work. Exact writer remains unproven.

T2.1 integration review follow-up: revalidate current fingerprint after receipt lookup/join; source mutation while waiting must not return a stale PASS. Runner proceeds on fresh execution integration while owner fixes this cache boundary.

T2.1 racefix: 65 tests PASS, strict config guard PASS; reviewed files integrated and copied into T3.1. Same public API; stale lookup/join/owner results cannot certify PASS.

T0.1 follow-up: finalize semantic DoD validation against actual manifest/runtime/benchmark contracts, beyond generic integrity checking; exclude only generated architecture/status.json from harness source proof. Artifact changes do not alter production behavior.

T1.2 integration regression: preserve known legacy FAIL when sidecar coverage is incomplete (do not downgrade failure to INCOMPLETE); simplify validation functions to complexity floor. Separate owner task while runner continues its declared file area.

T2.2 style review: normalize newly added CLI help to machine-string English and replace assigned lambda with named local function; no behavioral change, syntax/diff checks sufficient before finalFull.

T1.2 integration fix: 114 tests PASS under ordinary user, strict config guard PASS; parent task check PASS. Known FAIL/ERROR survives incomplete sidecar, validation complexity reduced; reviewed hash-matched copies integrated into root and runner.

T0.1 semantic verifier integrated: parent self-test PASS, 10 harness checks including 12 semantic fixtures. DoD remains unverified until source-bound final Full/benchmark/QC/browser artifacts exist; missing proof fails closed.

T3.1 parent check: 112 case PASS + 12 subtests, 94.86 giây; guard126 vì .claude.json đổi. Quan sát riêng ngoài test cũng thấy pluginUsage đổi, chưa xác định writer. Giữ task mở; chỉ copy candidate để phát triển consumer, không coi là chứng nhận.

Archify lifecycle: cập nhật Master theo dependency source thực, bỏ nhãn cũ 43 CLI scripts. Model runtime-verification biểu diễn working-tree, không tuyên bố QC hoặc tốc độ đã đạt. Sync Master sau source freeze, trước Full/benchmark; giữ nguyên preview spec đã duyệt.

Pre-Full consumer review: đối chiếu JUnit/sidecar từng case/outcome; sửa fingerprint effective environment và bảo toàn failure/provenance khi finalize lỗi. Mọi lỗi correctness phải sửa trước Full/benchmark chứng nhận.

T2.3 Windows integration follow-up: tên file tạm cache ghép digest và UUID có thể vượt MAX_PATH. Rút ngắn riêng tên tạm, giữ full cache key/provenance và atomic replace; có RED đường dẫn dài thực.

T1.2 parity fix integrated: 72 cases PASS + 53 subtests, normal privilege/config guard PASS, parent check PASS. IDs/file identity/phase/subtest event counts and outcomes agree across JUnit and sidecar. T3.1 candidate updated with environment/finalization fixes; parent check pending with this adapter.

T2.1 pre-Full follow-up: từ chối timeout NaN/Inf; lỗi publish/hash/finalize giữ failure, case và process đã quan sát, đồng thời đánh dấu evidence chưa đủ. Không đổi ngưỡng hoặc luật reuse.

T2.3 Windows path fix integrated: 148 cases PASS + 21 subtests, parent check/config guard PASS. Real target 250 characters writable; old temporary path 282 failed, short same-directory temporary now works. Full64 content key and atomic replace preserved; replace-failure keeps existing entry.

T2.1 candidate sync: 109 case PASS ở tác giả và parent; lượt tác giả guard PASS, parent guard126 vì .claude.json đổi. T0.1 mở lại để capture lỗi cleanup/finalization thành receipt FAIL, giữ nguyên source/config guard. Sau sửa harness, parent T2.1 đã PASS đầy đủ 109 case trong 47.61 giây.

T3.1 chứng nhận lại sau khoảng T4.2 ổn định: parent check PASS, guard cấu hình/source và cleanup PASS. Bắt đầu QC-F1, giữ mọi lượt thất bại trước đó.

## QC vòng 1 — fix

QC-F1 đã chạy: 3579 case; 3411 pass, 158 fail, 10 skip theo outcome chuẩn hóa; stdout pytest đếm thêm subtest riêng. Mọi 3306 case gốc vẫn có mặt. Receipt FAIL giữ nguyên: config_guard cũng phát hiện .claude.json đổi. Chưa được chạy benchmark trước correctness.

- [x] **QC1.1** Sửa helper hook dùng đúng project fixture khi harness có TDQ_PROJECT_DIR, giữ explicit override; bổ sung regression môi trường nhiễu và encoding subprocess. — Test: `python -X utf8 docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/safe_run.py --label QC1.1 -- python -m pytest -q tests/test_helper_isolation.py tests/test_bash_gate.py tests/test_compliance_protocol.py tests/test_context_hooks.py tests/test_e2e_chain.py tests/test_edit_gate.py tests/test_header_duong_dan.py tests/test_kenh_luat_dedupe.py tests/test_prompt_context.py tests/test_stop_gate.py tests/test_subagent_start.py tests/test_team_chong_conflict.py tests/test_team_mode.py tests/test_turn_ledger.py tests/test_ma_hoa_subprocess.py`
  - Chạm: `tests/helper.py`, `tests/test_helper_isolation.py`
  - Cần: T4.2
- [x] **QC1.2** Khôi phục dependency Archify có provenance trong sandbox và project fixture riêng cho acceptance; giữ yêu cầu native browser, không skip hoặc nới guard. — Test: `python -X utf8 docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/safe_run.py --label QC1.2 --archify-chrome "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" -- python -m pytest -q tests/test_archify_e2e.py`
  - Chạm: `docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/safe_run.py`, `tests/test_archify_e2e.py`
  - Cần: T4.2
- [x] **QC1.3** Sửa entrypoint benchmark theo utf8_io; sửa scanner phân biệt Path.open binary với text và cập nhật ghi chú import POSIX có guard trong báo cáo tương thích. — Test: `python -X utf8 docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/safe_run.py --label QC1.3 -- python -m pytest -q tests/test_tdq_runtime_bench.py tests/test_utf8_io.py tests/test_bao_cao_da_nen_tang.py tests/test_dem_da_nen_tang.py`
  - Chạm: `scripts/tdq_runtime_bench.py`, `tools_kiem/dem_da_nen_tang.py`, `tests/test_dem_da_nen_tang.py`, `docs/tdq/report/2026-09-03-1648-kiem-da-nen-tang-host-tuong-thich.md`
  - Cần: T4.2
- [x] **QC1.4** Đồng bộ registry luật với hướng dẫn batch đã duyệt; giữ neo cũ và ghi neo mới, cập nhật kiểm sáu nhóm cấm chạy đồng thời; sửa câu chỉ còn bốn nhóm. — Test: `python -X utf8 docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/safe_run.py --label QC1.4 -- python -m pytest -q tests/test_luat_skill.py tests/test_step_budget.py`
  - Chạm: `docs/tdq/audit/luat-hien-co.md`, `skills/tdq-conventions/references/context-budget.md`, `tests/test_step_budget.py`, `docs/tdq/token-budget.json`
  - Cần: T4.2
QC1.2 đã qua parent check với Edge native và config/source/dependency guard PASS; P2 CLI > inherited browser đã RED/GREEN và review độc lập đóng finding. QC1.1/QC1.3 vẫn chưa chứng nhận do config drift; Full sau sửa và benchmark chưa chạy. Không lặp lại test chỉ để tìm khoảng cấu hình yên tĩnh.

2026-10-31 QC1.3: reviewer độc lập đối chiếu SHA root/worktree trùng byte, không có finding mới. Parent check root quyền thường PASS: 57 tests và 34 subtests trong 98.30 giây; child/harness exit 0, config/source/dependency guard và cleanup PASS. Receipt: `runs/QC1.3-codex-20261031-0292e87250e442b68d6663afcc521a04/receipt.json` trong thư mục artifact request. Tích hợp bằng copy đã kiểm SHA theo ghi chú triển khai, không Git merge/commit.

2026-10-31 QC1.1: reviewer độc lập đối chiếu SHA root/worktree trùng byte, không có finding mới. Parent check root quyền thường PASS; child/harness exit 0, config/source/dependency guard và cleanup PASS. Receipt: `runs/QC1.1-codex-20261031-fafa0d7dfe6c4124b329fb4b46b86000/receipt.json`. Cả bốn task sửa QC vòng 1 đã được chứng nhận, bắt đầu Full fresh sau sửa. Chưa chứng nhận POSIX hay hiệu năng.

## QC vòng 2 — fix

Full fresh 2026-10-31: 3599 case, 3590 pass, 1 fail, 8 skip, coverage complete không missing/extra/duplicate; 1304.34 giây. Case lỗi: `tests/test_tdq_finish.py::KhoaTokenTest::test_khoa_chay_khi_cham_file_luat`. Harness còn phát hiện `.claude.json` thay đổi; source/dependency guard và cleanup không lỗi. Receipt FAIL giữ nguyên: `runs/QC-F1-codex-20261031-0e56356e147e430b84172ce2feaf5f0e/receipt.json`. Chưa chạy runtime/benchmark.

- [x] **QC2.1** Sửa fixture của kiểm khóa token để chạy đúng trong HOME cô lập; giữ assertion kiểm nhánh khóa token và khả năng báo lỗi thật, không nới guard. Nếu chẩn đoán cho thấy lỗi sản phẩm thay vì fixture, báo leader để mở rộng đúng task chủ trước khi sửa. — Test: `python -X utf8 docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/safe_run.py --label QC2.1 -- python -m pytest -q tests/test_tdq_finish.py tests/test_skill_tokens.py`
  - Chạm: `tests/test_tdq_finish.py`
  - Cần: T4.2
  - Dùng lại worktree qc1.1 đã đối chiếu candidate; không đổi nhánh, commit hoặc Git merge. Leader chỉ tích hợp file đã review và kiểm SHA. Chứng nhận Full/benchmark chỉ sau khi nguồn ghi cấu hình thật dừng.

QC2.1 hoàn tất: chuyển unit sinh khóa sang project tạm, mock riêng factory counter và chạy sinh_khoa thật; kiểm JSON token/hash, missing counter -> skip, counter lỗi -> fail và không sinh lock. Không thay production, không chấp nhận fail cho nhánh thành công. Reviewer độc lập không có finding, candidate/root SHA `dea25348cbcbaff173d8b1c418c15bd06d0bc96862f3a5b067088ac972419d07`, LSP 0 diagnostic. Author 20 PASS/7.03s; parent root `QC2.1-parent-20261031-60866b17fb6340b6884c73093a54c447` PASS với cả test_tdq_finish.py và test_skill_tokens.py, guard/cleanup PASS. RED thật là Full root; lượt author mang nhãn red thực tế 18 PASS do không có venv và KHÔNG được dùng làm RED. Exception tokenizer gốc chưa xác định vì assertion cũ không in detail. Chưa chạy lại Full khi tiền đề cấu hình thật chưa được giải quyết; tiến độ 18/25, T5.1 còn mở.

## Tiếp tục sau xác nhận “đã dừng” — 2026-10-31

- Mã nguồn không đổi so với QC2.1 parent (`aa8c7875bdad62957e0ef14287d490dfd3b4add9dce85e3488e22935fd75a5a8`); Master current, team audit PASS, resume state.
- T5.1 Full fresh PASS: 3601 case, 3593 pass, 8 skip, 0 fail/error; wall1196.17s, execute1189.76s. Harness/child exit0, config/source/dependency guard và cleanup PASS. Receipt `runs/QC-F1-after-writers-stopped-20261031-dd68c0bd37a142bb9f89d1eef8ba3609/receipt.json`. D1–D8 verifier PASS; 3306 case gốc đủ, không remap. Evidence index v2 và output từng check đã lưu.
- T5.2 runtime PASS 6/6 scenario, mỗi scenario dưới120s; verifier khớp nguồn Full. Receipt `runs/runtime-after-writers-stopped-20261031-0698bde3870643258b86f9929d6a83d2/receipt.json`; `runtime.json` có số đo, heartbeat, join và owner-crash evidence.
- T5.3 chưa hoàn tất. Sample1 (1worker) chạy1179.75s, outcomes3593pass/8skip, nhưng runner INCOMPLETE vì `docs/tdq/.tdq-turn.jsonl` đổi trong job. Ledger ghi SessionStart19:05:20. Harness còn phát hiện `.claude/CLAUDE.md` và `.claude.json` đổi; chưa quy kết tiến trình ghi cụ thể. Dừng đúng child benchmark43260 (parent59164) sau kiểm command/parent, để harness đóng job và lưu receipt FAIL/cleanupcomplete. Không dừng phiên khác, không sửa guard hoặc cấu hình.
- Giữ partial report và bản lưu `benchmark-full.interrupted-20261031-1905.json` cùng sampleJSONL; receipt `runs/benchmark-full-after-writers-stopped-20261031-5ed8df791a8c45e2a2376e6d27d5eea1/receipt.json`. Không dùng sample này làm PASS hoặc suy ra tốc độ. T5.3 `[~]`, tiến độ20/25, D9–D12 chưa chứng nhận.
- Pause mat-truy-cap: cần các phiên/tiến trình ngoài job ngừng ghi config và ledger trong toàn cửa sổ đo. Sau xác nhận, kiểm source/receipts và identity đối chiếu chéo trước sáu sample mới. Fingerprint Full có workinglog ngày31, trong khi projection hiện chỉ loại workinglog ngày mở request27; finish cập nhật log31 nên phải kiểm input tương đương, chứng nhận Full mới nếu cần theo hợp đồng, không tự nới exclusion/guard. Các lượt bị ngắt được giữ nguyên.

## QC vòng 3 — fix

Sau xác nhận lần hai, PID20356 không còn; source không đổi nhưng workinglog31 lệch identity nên đã làm mới Full và runtime. Full mới 3593pass/8skip,3601case,1124.88s, mọi guard/cleanup PASS; D1–D8 PASS. Runtime mới6/6PASS. Nguồn giữa Full và đầu vào benchmark đã đối chiếu khớp trước khi đo.

Cặp benchmark đầu chạy thật, từng sample đều runner PASS: workers1=1113.6633989s, workers2=610.2338293s. Tuy nhiên parity chi tiết FAIL: 293 case chứa subtest có tham số bị thêm một lớp repr qua xdist; manifest3601ID, outcome/capability/reason/phases vẫn khớp. Không nới bộ kiểm parity hoặc dùng số thời gian này để chứng nhận D9. Dừng đúng child benchmark52760,parent50216 để harness seal receipt FAIL; giữ `benchmark-full.parity-failed-20261031.json` và JSONL/raw. Sample3 bị ngắt không là số đo hợp lệ.

- [x] **QC3.1** Sửa việc tuần tự hóa metadata subtest qua pytest/xdist để tham số được biểu diễn đúng một lần, giữ đầy đủ thông tin case/phase/subtest và các verdict; thêm regression serial/2worker bằng process thật. Làm hai fixture subtest xác định về thứ tự set và label payload chứa temp path; giữ nguyên assertion và số scenario. Giữ nguyên parity verifier và guard. — Test: `python -X utf8 docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/safe_run.py --label QC3.1 -- python -m pytest -q tests/test_tdq_test_manifest.py tests/test_tdq_test_result.py tests/test_tdq_runner_integration.py tests/test_tdq_runtime_bench.py tests/test_bao_cao_gitflow.py tests/test_subagent_start.py`
  - Chạm: `scripts/tdq_test_manifest.py`, `tests/test_tdq_test_manifest.py`, `tests/test_bao_cao_gitflow.py`, `tests/test_subagent_start.py`
  - Cần: T4.2
  - Dùng lại worktree t1.2 đã có, không commit/merge hoặc sửa ngoài vùng. Leader tích hợp theo SHA sau review độc lập, parent check, refresh Master nếu stale rồi Full fresh cuối và runtime trước sáu sample benchmark mới. Source đổi làm proof cũ thành lịch sử; giữ mọi receipt và sample.

QC3.1 producer candidate: RED thật1fail/16pass; GREEN116pass+73subtests159.51s, guard/cleanup sạch, LSP0diagnostic. Hai lượt GREEN chưa đạt trước đó được giữ nguyên. Diagnostic hai Full cũ chỉ decode trong RAM, không sửa raw/verifier:293case/2790leaf lệch encoding giảm còn2case/14leaf. test_bao_cao_gitflow lặp set làm đổi thứ tự15subtest; test_subagent_start đưa temp cwd vào label metadata. Mở rộng đúng hai fixture trong cùng QC3.1 để deterministic, không nới parity hoặc xóa assertion/scenario.

QC3.1 đã tích hợp4file theo SHA và review độc lập không finding. Root vung-cham7module PASS235case90.08s, hai consumer bổ sung PASS; cảhai receipt guard/cleanup sạch. Master current, LSP0diagnostic4file, gitdiffcheck sạch; verifier không đổi. D1–D8 mở lại chờ Full trên source cuối. Tấtcảproof trước sửa được giữ làm lịch sử.

Chốt source QC3: Full fresh3594pass/8skip,3602case1117.67s; D1–D8 PASS,3306gốcđủ; runtime6/6PASS, guard/cleanup sạch. Source SHA81c1946345d8495ef32dbb3924de801020c957c5599918b9c3d4317c5f3278ad. Benchmark sourcecuối sample1PASS1159.99s; sample2 ngắt khi.codex/config.toml đổi21:58:38, ledger/source khôngđổi. Receipt9e893fa6giữFAIL,cleanupcomplete; archive benchmark-full.config-drift-QC3-20261031.json. T5.3cònmở,21/26task. QC độc lập sơ bộ không có codefinding mới, verdict PRELIMINARY/INCOMPLETE; chưaD9–D12. Đãpausetrởlạimat-truy-cap,chưaquywriter; chatColoring_Systemđangactive chỉlàquan sát, khôngcódirectconfigwriteproof. Dựthảophốihợpchatkhácchưagửi,chờquyềnrõcủauser. Checkpoint: codex-checkpoint-QC3-20261031.md.

## Điều chỉnh phạm vi theo người dùng — 2026-10-31

Nguyên văn: “có thể skip bench mà tổng hợp cho tôi ko?”. T5.3/T5.4 và D9/D10 đóng hành chính dưới nhãn SKIPPED_USER, không là test PASS hoặc ngưỡng đạt. Không chạy thêm benchmark, không gửi dự thảo phối hợp chat khác. Hoàn tất QC correctness/runtime độc lập, báo cáo và browser QA; gate report cũ phụ thuộc benchmark đầy đủ được ghi không áp dụng và kiểm nội dung/link/browser theo phạm vi mới riêng, không sửa verifier/spec gốc. Giữ1worker, các cache off; không commit/merge/push/đổi nhánh khi chưa được yêu cầu.

## Chốt bàn giao theo phạm vi điều chỉnh — 2026-10-31

QC độc lập cuối và D11 PASS, source giữ SHA `81c1946345d8495ef32dbb3924de801020c957c5599918b9c3d4317c5f3278ad`. Báo cáo [Markdown](../reports/2026-10-27-1846-kiem-chung-tang-toc.md), [HTML](../reports/2026-10-27-1846-kiem-chung-tang-toc.html) và [QC](../qc/2026-10-27-1846-kiem-chung-tang-toc.md) đã tích hợp. Chrome DevTools MCP kiểm desktop 1440×900 và mobile 375×812: không tràn ngang toàn trang, không console/network error, anchor/focus/details và cuộn bảng mobile hoạt động. Đây là viewport browser, không phải thiết bị vật lý. `verify_dod.verify_report` PASS với 30 link và 4 numeric binding; lệnh, exit0 và output lưu [summary-scope-validation.json](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/summary-scope-validation.json), screenshot/DOM bind SHA tại `report-browser.json`.

26 task đã xử lý: 24 thực hiện, 2 benchmark SKIPPED_USER. DoD theo phạm vi điều chỉnh: 10 mục kiểm đạt, 2 bỏ qua theo yêu cầu; không tuyên bố 12/12 DoD gốc PASS. Không chạy thêm benchmark hoặc Full trong lượt tổng hợp, không gửi chat khác. Giữ mặc định1worker và reuse/readiness/transcript off. Chưa commit/merge/push/đổi nhánh; giữ metadata nhánh để bàn giao.
