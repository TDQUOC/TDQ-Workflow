# PLAN — Tối ưu bốn hạng mục sau báo cáo QC
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-11-01 · Lane: full · QC: ultra · Spec: [v1.0 đã duyệt](../spec/2026-11-01-1045-toi-uu-bon-hang-muc.md)
Spec được duyệt bằng “duyệt spec”; digest f9d0645304cb8497493f4db2e355966cf3ffe734b226296260a35a69f6ba4a04.
Mode thực thi: subagent — ĐÃ CHỌN bằng “1a”; tham khảo simulate: đội24,5phút so với main26,5phút, gap1,9phút theo output, hệ số agent1,5 và8đợt; đây là calibration cũ, không là ETA. Không coi số mô phỏng là ETA.
Trạng thái plan: HOÀN THÀNH THỰC THI/QC — workflow chưa đóng do worktree cũ;  user “duyệt plan”; mode subagent được user chọn bằng “1a”.

## Quy tắc thi hành

- RED → GREEN mỗi task; ghi receipt trước khi tick. Các lệnh bên dưới là kế hoạch, chưa phải kết quả đã chạy.
- Nhánh hiện tại codex/toi-uu-bon-hang-muc, gốc dev. Không tự commit/push phần triển khai mới. Không mở lại benchmark D9/D10 cũ hoặc đổi mặc định worker/cache.
- Trước sửa source: LSP blast_radius scope all; symbols/callers mới phải tra tiếp. Module report mới đã tìm slow_test_summary qua LSP không có, grep kiểm tên và đồng nghĩa trước tạo; tái dùng formatter/log/atomic helper đã có khi hợp đồng khớp.
- Dùng harness quyền thường đã có, không sửa guard/harness cũ. Guard FAIL làm receipt không đủ chứng nhận kể cả pytest PASS. Không chạy QC dài song song agent/tool/job khác; fail do drift giữ chứng cứ, không retry để tìm khoảng yên tĩnh.
- Mỗi task source chạy thêm vùng chạm sau lệnh test riêng: `python $h --label radius-MA_TASK --evidence-dir $e -- python scripts/tdq_test.py vung-cham --repo . --files CAC_FILE_CHAM --workers 1 --fresh --reuse off`. Thay MA_TASK/CAC_FILE_CHAM bằng mã và danh sách Chạm của chính task; không tự ép Full trong implement.
- Full chỉ QC-F1 và sau vòng fix cuối nếu có sửa. Smoke/runtime từng scenario cap120s; Full có deadline1800s, outer harness2100s. Không đổi timeout để nhận PASS; quá3vòng QC fix báo blocker theo workflow.
- Setup/control-state thử nghiệm dùng project tạm, không reset state thật. Chỉ CLI state ghi state.
- Các task chứng cứ chỉ đọc source; phát hiện lỗi phải quay đúng owner, không sửa chéo vùng.

Lệnh PowerShell từ gốc repo, dùng lại trong các dòng kiểm:

```powershell
$h = 'docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/safe_run.py'
$e = 'docs/tdq/artifacts/2026-11-01-1045-toi-uu-bon-hang-muc'
```

`verify_scope.py`, `runtime_checks.py` và các test mới dưới đây là đầu ra sẽ tạo ở task chủ, không giả là chúng đã tồn tại. Verifier request chỉ điều phối/reuse các phép kiểm semantic Full/receipt đã có; không thêm framework hay thay luật verifier cũ.

## Thiết kế Trước vs Sau

| Vùng | Trước | Sau |
|---|---|---|
| Calibration | Đo trước một số validation | Input xác định sai bị từ chối trước repo/vòng đo |
| Codex check | Một case timeout2s mất30,16s | Ownership/deadline/cleanup và môi trường Codex được khóa bằng regression |
| Test | Kiểm dữ liệu gọi nhiều job/git không liên quan | Kiểm thuần ở lớp thuần, giữ chứng cứ integration thật |
| Report | Cộng duration thủ công | Summary dùng chung; export JSON/MD/HTML offline có nguồn |

Dùng đúng [preview đã duyệt](../spec/2026-11-01-1045-toi-uu-bon-hang-muc-preview.html) và [manifest](../spec/2026-11-01-1045-toi-uu-bon-hang-muc-preview.manifest.json). Không sinh thiết kế khác; đổi hợp đồng phải quay gate spec.

## P0 — Khóa chứng cứ và cổng kiểm

- [x] **T0.1** (e10m) Đăng ký baseline3602case từ result lịch sử, ánh xạ Q1–Q8 và verifier request fail-closed; lưu case mapping, contract/evidence index, source/config/dependency guard cùng command/stdout/exit. Reuse validate_receipt/validate_full_payload và kiểm report semantic từ artifact cũ khi khớp hợp đồng; tự kiểm phát hiện thiếu receipt, source cũ, raw bị đổi, false PASS và thiếu browser. Kiểm binding preview trước code. — Test: `python $e/verify_scope.py --self-test`
  - Chạm: `docs/tdq/artifacts/2026-11-01-1045-toi-uu-bon-hang-muc/verify_scope.py`, `docs/tdq/artifacts/2026-11-01-1045-toi-uu-bon-hang-muc/evidence-index.json`, `docs/tdq/artifacts/2026-11-01-1045-toi-uu-bon-hang-muc/case-mapping.json`
  - Dùng: `tdq-intake`
  - Để: đối chiếu bốn đầu ra và QC ultra đã chọn; không init/reset lại request.
  - Ra: evidence-index và baseline case mapping trong thư mục artifact request.
  - Kiểm: `python $e/verify_scope.py --self-test`
  - Không dùng cho: mở lại phỏng vấn/pipeline hoặc thay spec đã duyệt.
  - Dùng: `tdq-setup`
  - Để: kiểm readiness LSP/Graphify và tool cần cho kiểm, sửa thiếu dependency theo quyền user đã cấp.
  - Ra: preflight.json gắn tool/version và hạn chế thực tế.
  - Kiểm: `python scripts/tdq_lsp.py check`
  - Không dùng cho: đổi config để làm integrity guard PASS.
  - Dùng: `tdq-plan`
  - Để: đối chiếu approval/mode và dependency của đúng plan này trước triển khai.
  - Ra: scope/approval binding lưu trong evidence index.
  - Kiểm: `python scripts/doc_lint.py --pair docs/tdq/spec/2026-11-01-1045-toi-uu-bon-hang-muc.md docs/tdq/plan/2026-11-01-1045-toi-uu-bon-hang-muc.md`
  - Không dùng cho: tự duyệt plan/mode hoặc thay ngưỡng spec.

## P1 — Ba module độc lập

- [x] **T1.1** (e12m) Dời parse/validation input và kiểm thiếu mẫu Codex xác định sớm lên trước calibration. Giữ machine rounds cho input hợp lệ, provenance, số mẫu cuối và lỗi không ghi output. Giảm ngay công việc thừa trong case dữ liệu của bench; ghi mapping assertion trước/sau. — Test: `python $h --label T1.1 --evidence-dir $e -- python -m pytest -q tests/test_bench.py`
  - Chạm: `scripts/tdq_bench.py`, `tests/test_bench.py`
  - Cần: T0.1
- [x] **T1.2** (e20m) Repro timeout Windows .cmd/descendant/pipe trước khi sửa; dùng hoặc tách primitive ownership dùng chung mà không áp env pytest vào Codex. Khóa version/say-hi, HOME/argv/stdin, cleanup job khác, timeout2s toàn lời gọi≤8s và fail-closed khi không nhận ownership. — Test: `python $h --label T1.2 --evidence-dir $e -- python -m pytest -q tests/test_codex_cli.py tests/test_tdq_test_process.py`
  - Chạm: `scripts/tdq_codex.py`, `scripts/tdq_test_process.py`, `tests/test_codex_cli.py`, `tests/test_tdq_test_process.py`
  - Cần: T1.1
- [x] **T1.3** (e14m) Viết summary/renderer thuần trong module report riêng: hai bảng Top20, sort ổn định, tổng execution phases, không cộng subtest trùng; phân loại missing/invalid/duplicate, result cũ và wall riêng. Chung summary cho JSON/MD/HTML, escape text và ghi file atomic. — Test: `python $h --label T1.3 --evidence-dir $e -- python -m pytest -q tests/test_tdq_test_report.py`
  - Chạm: `scripts/tdq_test_report.py`, `tests/test_tdq_test_report.py`
  - Cần: T0.1

## P2 — Giảm test lặp và tích hợp runner

- [x] **T2.1** (e12m) Khóa các case parser/schema/log ở lớp thuần để không dựng repo/git/calibration không liên quan trong runner/team/runtime-bench. Giữ tên case/assertion và proof integration thật; mỗi fixture mutable riêng. Nộp mapping cụ thể và đếm subprocess trước/sau theo case đã chọn, không dùng wall giảm để thay correctness. — Test: `python $h --label T2.1 --evidence-dir $e -- python -m pytest -q tests/test_tdq_test.py tests/test_team_mode.py tests/test_tdq_runtime_bench.py`
  - Chạm: `tests/test_tdq_test.py`, `tests/test_team_mode.py`, `tests/test_tdq_runtime_bench.py`
  - Cần: T1.1, T1.2
- [x] **T2.2** (e18m) Tích hợp slow_tests vào fresh result và bảng CLI; thêm report --result/--out-prefix xuất JSON/MD/HTML cùng SHA input và không gọi runner. Giữ API/status cũ, silent mode, result cũ; lỗi export/unwritable/atomic không che FAIL test hoặc để output hoàn chỉnh giả. Kiểm round-trip thật trên repo fixture. — Test: `python $h --label T2.2 --evidence-dir $e -- python -m pytest -q tests/test_tdq_runner_integration.py tests/test_tdq_test_report.py`
  - Chạm: `scripts/tdq_test.py`, `tests/test_tdq_runner_integration.py`, `tests/test_build_portable.py`
  - Cần: T1.3, T2.1

## P3 — Log và test xuyên tầng

- [x] **T3.1** (e6m) Audit và khóa log mặc định bật/tắt bằng config, timestamp/reason và cleanup/report stages; không secret hoặc payload thô. Nếu thiếu production log, giao sửa đúng task chủ trước khi chứng nhận, task này không sửa module của owner khác. — Test: `python $h --label T3.1 --evidence-dir $e -- python -m pytest -q tests/test_optimize_logging.py tests/test_runtime_logging.py`
  - Chạm: `tests/test_optimize_logging.py`
  - Cần: T2.1, T2.2
- [x] **T3.2** (e8m) Unit/regression xuyên lớp: mọi đầu ra O1–O5 có assertion, compatibility result/receipt, invalid input không gọi job, report không execute, descendant ownership và input XSS/quality. Gắn case mapping cuối; chỉ thêm kiểm có rủi ro cụ thể, không mirror implementation. — Test: `python $h --label T3.2 --evidence-dir $e -- python -m pytest -q tests/test_optimize_contracts.py tests/test_runtime_contracts.py`
  - Chạm: `tests/test_optimize_contracts.py`
  - Cần: T3.1

## P4 — QC ultra trên source đã tích hợp

- [x] **T4.1** (e20m) Cập nhật Master/graph theo source thực trước freeze; chạy Full fresh quyền thường một lần, kiểm inventory baseline3602 và case mới, skip capability, raw sidecar/JUnit/result, source/config/dependency không đổi và cleanup. Giữ raw FAIL; không dùng cache hoặc sample cũ. — Test: `python $h --label QC-F1 --evidence-dir $e --timeout-seconds 2100 --archify-chrome "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" -- python scripts/tdq_test.py tron-bo --repo . --workers 1 --fresh --reuse off --timeout-seconds 1800`
  - Cần: T3.2
  - Dùng: `tdq-build`
  - Để: QC-F1 và Q1–Q6 bằng Full/raw nguồn cuối, fix loop đúng owner.
  - Ra: receipt Full, result và qc-checks.json gắn SHA trong artifact request.
  - Kiểm: `python $e/verify_scope.py Q6`
  - Không dùng cho: benchmark A/B hoặc chứng nhận % tăng tốc từ source khác.
- [x] **T4.2** (e8m) Chạy smoke/runtime CLI thật cho input hợp lệ, từ chối sớm, timeout2s/cleanup/job khác, export offline; tạo runner request tái dùng API/fixture đã có, mỗi scenario có outer cap120s, lưu PID/handshake/elapsed/output/cleanup facts. Giữ nhãn fixture/simulation đúng nghĩa. — Test: `python $h --label runtime --evidence-dir $e --timeout-seconds 700 -- python $e/runtime_checks.py --scenario-timeout 120 --output $e/runtime.json`
  - Chạm: `docs/tdq/artifacts/2026-11-01-1045-toi-uu-bon-hang-muc/runtime_checks.py`
  - Cần: T4.1
- [x] **T4.3** (e8m) Reviewer độc lập đối chiếu diff/source/DoD/receipt, architecture/SOLID và case mapping; không chỉnh code trong review. Findings chuyển về task chủ, vùng chạm và Full sau vòng fix cuối; audit Q1–Q7 rồi lưu reviewer/implementers/source/verdict. — Test: `python $e/verify_scope.py Q7`
  - Cần: T4.2

## P5 — Report và kiểm trình bày

- [x] **T5.1** (e8m) Xuất Top20 từ result Full cuối bằng report offline, viết QC/report MD+HTML kết quả request và giới hạn. So sánh số đo có provenance, không hứa %speedup hoặc dùng timing99giờ làm CPU. Khóa các output tương ứng source/result; ghi rõ không mở lại benchmark cũ và không commit/push tự động. — Test: `python scripts/tdq_test.py report --result $e/final-result.json --out-prefix $e/slow-tests`
  - Cần: T4.3
  - `$e/final-result.json` là bản sao bytes đã kiểm SHA của result được receipt QC-F1 chỉ tới; không sửa payload hoặc dựng result thay thế. Verifier đối chiếu SHA/TDQ_RESULT binding trước export.
- [x] **T5.2** (e6m) Kiểm HTML Top20 và report tổng hợp ở desktop1440×900/mobile375×812: số liệu/link/escape, bảng cuộn riêng, không overflow toàn trang, console sạch. Lưu screenshot/DOM/console và SHA HTML. Đây là viewport browser, không phải thiết bị vật lý. — Test: `python $e/verify_scope.py Q8`
  - Cần: T5.1
  - Dùng: `tdq-browser-test` (mcp)
  - Để: preflight Chrome9222; nếu chưa kết nối chạy `python scripts/tdq_devtool_mcp.py launch`, kiểm lại MCP rồi kiểm nội dung/link/desktop/mobile.
  - Ra: browser.json, screenshot và observation gắn SHA HTML trong artifact request.
  - Kiểm: `python $e/verify_scope.py Q8`
  - Không dùng cho: kết luận hiệu năng hoặc gọi viewport là device proof.

## Ánh xạ đầu ra và preview

| Spec §2 | Task | Node preview |
|---|---|---|
| O1 | T1.1 | input / validate / measure / reject |
| O2 | T1.2 | codex / owned / cleanup |
| O3 | T1.1, T2.1, T3.2 | Kiểm định hai nhánh cal/process trong card giữ hợp đồng |
| O4 | T1.3 | result / summary |
| O5 | T2.2, T5.1 | summary / outputs |
| O6 | T0.1, T4.1–T5.2 | Card QC và evidence outputs |

## Cụm song song

Nếu user chọn subagent: T0.1 trước; T1.1 và T1.3 có thể cùng đợt; T1.2 sau T1.1; T2.1 sau T1.2; T2.2 sau T2.1 và T1.3. Kiểm TCAS tìm được import gián tiếp bench→codex, runner→process, test runner→runner nên các cặp đó được xếp nối tiếp dù khác file; không tuyên bố ba module có thể chứng nhận đồng thời. T3.1 → T3.2 → T4.1 → T4.2 → T4.3 → T5.1 → T5.2 tuần tự. Trong chứng nhận Full/runtime chỉ một owner chạy tool/job, không chạy reviewer tác giả đồng thời. Leader giữ state, chứng nhận parent và browser MCP; mode chỉ được ghi sau user chọn.

## Luật file nóng và bản đồ tác động

Mỗi file sản phẩm chỉ một owner: bench T1.1; codex/process T1.2; report T1.3; runner T2.2. T3.1/T3.2 chỉ sở hữu test mới; muốn sửa production phải trả về owner. Test T1.3 được T2.2 đọc/chạy nhưng chỉ T1.3 được viết. Evidence index/verifier/mapping/runtime từng file một chủ, không cho agent khác ghi đồng thời.

LSP references đã kiểm: _kiem_song → check/cli/tests; lenh_thuc_do → dispatch; chay_tron_bo_result có10reference, IsolatedJob có33reference. Grep xác nhận consumer runtime_bench và các regression/runtime logging; đó là vùng kiểm vỡ lan, không tự mở rộng file sửa. Graphify affected depth2 hỗ trợ hai CLI đầu. File mới report không có symbol slow_test_summary trong index; tìm lại tên và đồng nghĩa trước tạo. Mọi mở rộng source ngoài Chạm phải chứng minh cần cho hợp đồng spec rồi giao đúng owner.

## Definition of Done

Đúng8mục tương ứng Q1–Q8 spec §6, verifier chỉ đọc evidence đã sinh; không chạy Full thêm8lần. Bốn mục QC-F1→F4 kiểm riêng trong báo cáo QC theo skill.

- [x] Q1 Validation sớm không đo/ghi output với input sai, giữ hợp đồng input hợp lệ. — `python $e/verify_scope.py Q1`
- [x] Q2 Timeout2s thoát≤8s, descendant/HOME dọn đúng ownership, caller khác nguyên vẹn. — `python $e/verify_scope.py Q2`
- [x] Q3 Mapping không mất case/assertion; kiểm thuần giảm subprocess, integration thực còn đủ. — `python $e/verify_scope.py Q3`
- [x] Q4 Top20 case/module chính xác, deterministic, chất lượng thiếu đúng và không double-count. — `python $e/verify_scope.py Q4`
- [x] Q5 Fresh result/CLI + exportJSON/MD/HTML cùng nguồn, export không chạy test, lỗi không che verdict. — `python $e/verify_scope.py Q5`
- [x] Q6 Full nguồn cuối đạt, đủ baseline3602 và case mới, skip có lý do, API cũ giữ đúng. — `python $e/verify_scope.py Q6`
- [x] Q7 Smoke/runtime trong120s mỗi scenario và QC độc lập không còn finding correctness. — `python $e/verify_scope.py Q7`
- [x] Q8 HTML desktop/mobile đạt số liệu/link/console/overflow, MD/HTML giữ provenance và giới hạn. — `python $e/verify_scope.py Q8`

## Ước tính và giới hạn số đo

Tổng eNm =150phút trên13task trong6phase (P0–P5), là chi phí thực thi dự kiến, không gồm chờ duyệt; có Full18–20phút theo lịch sử và có thể phát sinh fix. Kết quả simulate bên dưới chỉ chọn mode bằng calibration cũ trên macOS, không phải benchmark runtime mới hoặc cam kết ETA/hiệu năng.

## Preflight khi lập plan

LSP references trả lời được. Chrome cổng9222 chưa lắng nghe; MCP list_pages trả ECONNREFUSED, chưa thực thi browser QA. Chrome đã có tại `C:/Program Files/Google/Chrome/Application/chrome.exe`. Trước T5.2 bật bằng `python scripts/tdq_devtool_mcp.py launch` rồi thử lại list_pages; nếu vẫn chưa kết nối, hướng dẫn user bật Remote Debugging9222 và giữ mục QA chưa đạt, không thay bằng kiểm chuỗi HTML. Bước launch dùng profile debug riêng theo helper, không đóng phiên browser khác.

## Ghi chú triển khai — managed worktree

User đã chọn subagent bằng “1a”. Host yêu cầu tạo worktree qua Codex app; task map đã assign/audit toàn plan trước code. Worktree managed có đường dẫn khác .tdq-worktrees của tdq_team, và request không cho commit phần triển khai mới tự động. Vì vậy tích hợp bằng đối chiếu vùng file, SHA candidate/root, chạy lại lệnh task và parent vùng chạm thay cho CLI check/merge vốn yêu cầu branch+commit và đường dẫn legacy. Không sửa tdq_team để phục vụ riêng cơ chế host; không dùng Git merge hay commit ngầm. Mọi proof/receipt và lý do giữ task được lưu trước khi tick; archive managed worktree sau khi file đã tích hợp và kiểm. Các biến $h/$e ở plan là prelude PowerShell; lệnh parent thực thi dùng đường dẫn literal theo đúng checkout, không chạy alias chưa khai trong shell mới.

Preflight implement: Python3.13.15, pytest9.1.1, xdist3.8.0; Ruff không có command/module, không cài thêm. Helper đã mở Chrome và MCP list_pages kết nối được. Digest cấu hình bảo vệ ổn định qua hai quan sát đầu (không thay cho guard của từng job). Managed worktree T0 đã tạo; hai worktree calibration/report đã được git worktree list xác nhận HEAD6c00d6e, nhưng MCP quản lý app báo Transport closed ở lần hỏi trạng thái sau đó. Không tạo worktree trùng, không xóa dữ liệu; xác minh checkout trực tiếp qua Git trước giao việc, dùng lại worktree phù hợp nếu service chưa hồi phục.

T0.1 parent PASS:3file đối chiếuSHA,14selftest synthetic PASS; Q1–Q8 thiếu receipt đều FAIL. Parent log: artifacts/2026-11-01-1045-toi-uu-bon-hang-muc/T0.1-parent-check.json. Inventory lịch sử3602; assertion baseline gắnBASE6c00d6e, không giả bytecode hiện tại là bảnFull31/10.

Orchestration fallback: spawn_agent kế thừa model báo Unknown model unitypc-codex ở leader và agent hiện có. Không override model/config khi chưa có chỉ đạo model cụ thể; dùng followup_task với implementer đang hoạt động để giao từng task tuần tự tại worktree tách biệt, reviewer hiện có giữ riêng cho T4.3. Mode vẫn subagent, audit giao9/13; phần có thể song song không được giả là đã chạy song song. T1.3 chưa khởi động nên trả checkbox về[ ] cho đến khi giao thực tế.

T1.1 author: worktree `C:/Users/admin/.codex/worktrees/tdq-optimize-calibration/TDQ-Workflow`; before-counter guarded job labelT1.1-work-before/session56834 đang quan sát7case pure dự kiến và1case real integration. Wrapper dùng audit subprocess.Popen/profile _do_mot_luot qua sitecustomize, không đổi test baseline trước đo. Đây là kiểm work count, không là benchmark tăng tốc. Root không poll cùng session với tác giả.

T1.1 candidate:53PASS/39subtest/51,20s, source/dependency stable nhưng .claude.json đổi nên UNCERTIFIED, chưa tick/chưa copy vào source chính. Hai file candidate đã đối chiếuSHA và lưu dưới artifact candidates/T1.1, kèm migration proposal; baseline ROOT giữ nguyên. T1.3 đã giao cùng implementer ở WTreport độc lập sauT0, không chờ gate T1.1 vì chỉ phụ thuộcT0.

T1.3 tích hợp root2file đúngSHA; author guardPASS, parent24test+27subtest guardPASS, parent-radius guardPASS. T1.1 candidate được copy lầnđầu vàoRootđểparentkiểm chức năng nguồn mới (khôngretry before); sourcecũ lưu integration-backup/T1.1 vàWT T0 vẫnBASE. Q3before chưa chứngnhận, không dùngreceiptFAIL.

Gate pause: T1.1 parent mới chạy mộtlần trênRoot sau tíchhợpcandidate:53PASS39subtest51,80s, nhưngFAIL126 .claude.json đổi, source/dependency ổnđịnh/cleanupcomplete. Chưa tickT1.1, taskphụthuộcbịgiữ. T1.3parentunit+radiusPASSđãtick. Top20demo từFullcũ tạiartifact/top20-historical-20261031.html, khônglàQCnguồnmới. Statepause mat-truy-cap chờnguồnghiConfigdừng; chi tiết implementation-checkpoint.md trongartifactrequest.


## Phụ lục được duyệt — ngoại lệ telemetry

User “duyệt” ngày2026-11-01 cho ngoại lệ hai trường usageCount/lastUsedAt trong pluginUsage của .claude.json. Xem [phụ lục phạm vi](../artifacts/2026-11-01-1045-toi-uu-bon-hang-muc/telemetry-exception-approved.md). Helper/receipt cũ bất biến; lượt kiểm mới dùng adapter policy riêng và verifier nhận diện rõ. Đây là thay thế có giới hạn cho yêu cầu không ngoại lệ guard bên trên. State đã resume; T1.1 chỉ tick sau parent/radius mới hợp lệ.

Adapter ngoại lệ đã qua author17test và parent17test16,904s, guardPASS; reviewer độc lập đã xác nhận hai finding resolved. Receipt mới ghi schema/policy riêng, raw+semantic digest và hash adapter/phêduyệt/helper. Lệnh mới dùng $h = docs/tdq/artifacts/2026-11-01-1045-toi-uu-bon-hang-muc/safe_run_telemetry.py; helper/FAIL cũ giữ nguyên. Chi tiết telemetry-policy-integration.json.

T1.1 parent53PASS39subtest45,51s và radius guardPASS theo policy telemetry đãduyệt; đãtick. Receipt mới tại T1.1-integration.json. Q3 before/after counters vẫn cần chứngnhận riêng; không dùng FAIL cũ.

T1.2 đã giao triển khai tiếp tại managedWT calibration. Q3 before chạy7case baseline113,28s childPASS nhưng guardFAIL126 .claude.json ngoài normalizedtelemetry; giữreceipt T1.1-before-certified-ee0f3800565047e09b5b9e5b7ebc72b6, khôngdùngchứngnhận. Quan sát30s sauđó chỉ thấy2fieldđượcmiễn, khôngthay cho bằngchứng lượtFAIL. Rootđang ghi key-path-only observation phục vụchẩnđoánjobmới; khôngmởrộngngoạilệ.

T1.2 tíchhợp4file đúngSHA, preimagegiữlại; author61PASS1POSIXskip25,68s, Rootparent61PASS1skip25,97s và radius10module guardPASS. Reviewerđộc lập nofinding. T1.2-integration.json chứa binding; đãtick.

T2.1 chọn4case pure-work: So counts/budget/log và Team CLI log/defaultoff. GiữintegrationA/B/git/worktree và runtimebench đãpure nên khôngsửa modulekhôngcần. Đợtbaseline mởrộng11case tạiT0WT (7bench+4case mới), labelT2.1-combined-baseline; chưa cókếtquảkhi ghi dòngnày. Không dùng receiptFAIL trước chứngnhận.

Điều chỉnh kiểm tíchhợp T2.1: tácgiả chạy đủ3module theo lệnhtask; parent dùngmột lượt production vung-cham bao gồm đủ cả3module và vùngảnhhưởng để kiểm nguồnRoot saucopy. Khônglặp thêmparentunitcùng3module trướcđó vì parentradius đãthựcthi toàn bộassertions đólạitrênRoot; giữnguyên fresh/workers1/reuseoff/guard vàQC-F1 cuối. Đây là hợpnhất phépkiểm trùngphạmvi, khôngbỏtest hoặcđổingưỡng.

T2.1 parentradiusguardPASS, phủcả3module task; all11migrationrows/43assertionanchors hợp lệ. T2.1[x], T2.2 bắtđầuchuyểngiao. AfterworkcountsQ3 phải thu lại finalRootfreeze, chưaclaimfinalcert.


## Owner fixes sau kiểm tích hợp T2.2

ParentT2.2 guardclean,260PASS/1FAIL/56subtests212,79s: testreleasebudgetđọcHEAD6c00có168path, chỉmiễn2runtimecũnên166>160. So4cefc13^161path→4cefc13/HEAD168path:6module mớiO1–O6 đãduyệt oldspec dòng60–65 và1skillreference runtime-speed.md. NewreportuntrackedkhôngthuộcHEAD nênkhônggâylỗi. T2.2 mở thêm vùng tests/test_build_portable.py đểcậpnhật đúngnamed8committedruntime vànamed9approvedruntime(includereportO4), giữcap160chofilekhác/floor120/excludeddirs; checkHEADimportclosuređểreportbắtbuộcshipkhiHEADimportreport. Khôngđổi productionreleasefilter/khôngpublish/khôngcommit.

T3.1auditđộc lậpvềlog phát hiện summarize_result vẫn_log nênchưathuần, vàOwnedProcessJoblogthiếuphase/cleanup_complete. TrảownerT1.3 sửareportmodule+purityregression, ownerT2.2 chuyểnsummarylogđếncaller_finish_run/export_report, ownerT1.2 bổsungprocessmetadata từfacts thật; T3.1 chỉsởhữu newtests/test_optimize_logging.py. Agentqc11 sởhữucácmoduletrên từtaskgốc; Rootmởownerfixscope đúngcácfilegốc, khôngtạohotfileownerchéo. TestREDtrướcfix; simcleanupFalsegọi cleanupthật rồimớitrảverificationFalse.

T2.2 chức năng đãauthor57PASS+35subtests, reviewerreadonlynofinding; parentchỉbịlegacyHEADbudgetfixture. Vìlogauditkhôngphụthuộctestbudget, T3.1đượcchuẩnbịcandidatecùngownerfixđểkhôngđợi giả; cảT2.2/T3.1 chỉtick sauparentguardPASSđủvùngảnhhưởng vàhợpđồng. Giữphaseimplement, mode subagent, QCultra vàmọingưỡngDoD; khôngmởngoạilệguardmới. Benchsourcechưamởrộng, chỉtestrejectthực; cófindingthật mớitrảownerT1.1.

T1.3 mởlại[>] đúngowner đểđóngfindingpurity (summarycallbackcòn_log). SelectedownerGREEN đãqua; group6module ownerfix/T3.1đangchạy. Khônggiữtrạngtháiđãhoànthànhchohợpđồngthuầnkhifindingchưađượcparentkiểm. T1.2functionalgiữx; logmetadata bổsungđượcchứngnhậntạiT3.1 cùngownerfix.

OwnerfixparentallaffectedguardPASS receipt a31fa0a7c529410ba39392d9fb8c354f; T1.3/T2.2/T3.1 tickx. T3.2 giao tiếp, chỉtestfilemới.

T3.2 parentguardPASS đủ2module, sourcekhôngđổi; T3.2x. Master6view đãpublishworking-tree/source-statuscurrent; launcherbuildphânloạiquáhẹpdoatomicstaging giữlạidiễnraexpected, khôngdùngbuildrecordlàmtestcert. FullQC-F1sắpchạysauSourcefreeze/afterworkproof.

Statephaseqcchuyển bịchặn11ledgerworktreeoldrequestdirtysource, tấtcảmergednhưngchưaclean. Sweepreadonlyxácnhận970,6MB; khôngđụngSource/khôngđánhclosedgiả/khôngđổiguard. Phasevẫ nimplement; cácphépkiểmT4.1đãđượcduyệttrongplantiếptụcthựchiện, ghi rõmetadatablockerchờxửlý riêng.

QC-F1 FullfreshguardPASS; rawXML/sidecar/status/inventorybaselineđãkiểm, T4.1x. Chi tiết QC-F1-check.json; T4.2runtimegiao tiếp. Statephasevẫnimplementdo11foreignWT, khôngbypas sguard.

T4.2 parentvalidatoractualruntime/schema/rawbindingsPASS;4scenario11,3051/0,3453/2,7219/1,2800s đúngsourceFull. Calibrationprivate true.cmd fixturelabel, khôngrealmodel. T4.2x,T4.3independentreviewbắtđầu.

T4.3/T5.1/T5.2 và Q1–Q8 đã parent verifier PASS đúng sourceFull; QC12/12. Browser trực tiếp Chrome CDP khi MCP Transportclosed, đủ4capture/DOM/console/interaction, không phải physicaldevice. Workflow phaseimplement vẫn blocked11foreignWT; chưacommit/push, không bỏguard hoặcđánhledgerclosedgiả.
