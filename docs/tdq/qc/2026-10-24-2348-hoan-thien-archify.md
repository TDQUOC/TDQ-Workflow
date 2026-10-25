# QC — Archify đầu-cuối

Ngày: 2026-10-25 · Plan: ../plan/2026-10-24-2348-hoan-thien-archify.md
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Trạng thái: PASS TOÀN BỘ (đã hoàn tất xử lý 10 lỗi nền và dọn 6 worktree tại request `2026-10-25-1510-xu-ly-issue-nen`; lượt chạy `tdq_test.py tron-bo` đạt `Ran 2977 tests in 662.963s — OK (0 failures, 0 errors, 10 skipped)`).

## Đối chiếu Definition of Done

| # | Kết quả hiện tại | Bằng chứng / giới hạn |
|---|---|---|
| Q1 | PASS vùng chức năng | Delivery/adapter âm tính và smoke đã chạy; không thay full-suite |
| Q2 | PASS vùng chức năng | Model tests + validator engine thật; artifacts/model/pipeline/adapter sau sửa 149 passed |
| Q3 | PASS vùng chức năng | Workflow contract 6 tests + 2 subtests; E2E Full/Quick render, bind, mutation đều đạt |
| Q4 | PASS vùng chức năng | Master index/views, source mutation và refresh đạt E2E; MCP đi từ index sang overview thành công |
| Q5 | PASS vùng chức năng | Regression artifacts/rollback/binding và finish; 5 findings reviewer đã kiểm lại |
| Q6 | PASS vùng chức năng | Setup/distribution/build 101 passed; engine local và agent-first |
| Q7 | PASS đường dùng đã kiểm, có giới hạn UI | Native browser gates đạt; MCP zoom/focus/node search/link navigation; console không error/warn; mobile cuộn canvas/toolbar nội bộ, không tuyên bố đạt toàn bộ checklist responsive |
| Q8 | PASS | Toàn bộ 2977 tests PASS (0 failures, 0 errors); reviewer độc lập và `tdq-qc-tester` xác nhận PASS |
| QC-F1 | PASS | Lượt cuối sau sửa lỗi nền: 2977 tests, 0 failures, 0 errors, 10 skipped; exit 0 |
| QC-F2 | PASS | Toàn bộ các nhóm test chức năng và quy chuẩn đều PASS |
| QC-F3 | PASS qua review | Không import hooks vào scripts, không ghi state trực tiếp, không triển khai endpoint client |
| QC-F4 | PASS qua review và diagnostics | 5 câu self-check bên dưới; pyright 0 errors |

## Bằng chứng đã chạy

| Kiểm | Kết quả thật | Giới hạn |
|---|---|---|
| Delivery/model/artifacts/pipeline và test adapter | 167 passed trong lần chạy tổng hợp 01:08 | Unit và smoke explainer; không chứng minh native browser |
| Setup/distribution/build_portable | 101 passed | Có kiểm closure thay đếm cứng runtime |
| Finish freshness | 35 passed | Bao gồm source/revision/child change; không gọi render/AI |
| Workflow contract/docs/index/ledger | 108 passed, 331 subtests passed lúc 01:19 | Quy chuẩn đã wired, chưa hoàn tất demo Full/Quick/Master native |
| Pyright 4 module Archify | 0 errors, 0 warnings | Kiểu không thay thế runtime test |
| Cụm Archify sau full runner | 238 passed, 2 subtests passed trong 24.21s | Delivery/model/pipeline/distribution/finish/workflow/adapter/setup; không gồm artifacts đang sửa import, không thay E2E |
| Native workflow engine thật | FAIL browser-check, validate/deliver/check pass | Chrome và Edge đều lỗi pipe trong process elevated |
| Runner vùng chạm bwto9if6p | STOPPED do background timeout 120s | Không được ghi PASS, chưa có full-suite request mới |

Các lệnh pytest đã dùng được ghi trong plan; test logs tool phiên hiện tại là bằng chứng. Không cộng các lượt lặp thành số test riêng biệt.

## Chặn môi trường native browser

- Probe `ctypes.windll.shell32.IsUserAnAdmin()` trả True.
- Archify diagnostic `viewer/browser-check-runtime`: `Chrome DevTools read pipe failed: stream ended`; process còn chạy, pipe không nhận byte.
- Upstream yêu cầu thử từ non-elevated PowerShell, ngoài elevated/compatibility-mode parent.
- Đã thử Chrome mặc định và ARCHIFY_CHROME trỏ Edge; đều FAIL. Không tắt sandbox, không sửa upstream, không chuyển browser gate sang not-run cho native.
- CDP 9222 trả HTTP 200; kết nối MCP này không thay thế receipt browser-check native của Archify.
- ĐÃ GỠ CHẶN lúc 01:41: dùng Explorer desktop ShellExecute để chạy riêng PowerShell với Elevated=False, giữ nguyên phiên agent elevated và sandbox mặc định. Log `docs/tdq/native-browser-probe.log`: 4 gates PASS, ExitCode=0, duration 3468ms.
- E2E `tests/test_archify_e2e.py` chạy non-elevated: 2 passed, 2 subtests passed trong 12.79s, ExitCode=0 (`docs/tdq/archify-e2e.log`). Bao gồm Full/Quick render+verify+document mutation và Master render+source mutation+refresh.
- MCP đã mở native artifact, zoom 100→125%, focus Approval Gate mở Semantic Passport và quan hệ; console không error/warn. Screenshot desktop/mobile đã xem: `docs/tdq/native-desktop.png`, `docs/tdq/native-mobile.png`. Mobile có scrollbar canvas khi focus, không tuyên bố không overflow.
- Trọn suite pytest chạy qua quyền thường đã kết thúc ExitCode=1 (`docs/tdq/archify-full-qc.log`). Log chỉ giữ progress, thiếu summary nên không suy số lỗi từ cache lịch sử. Runner elevated bc05i8o0h đã chủ động dừng, không tính PASS.
- E2E sau nhập QC1: `python -m pytest tests/test_archify_e2e.py -q --tb=short` đạt 2 passed, 2 subtests passed trong 13.33s, Elevated=False, ExitCode=0; log `docs/tdq/archify-e2e.log`.
- Kiểm mobile bổ sung bằng MCP emulation thật 375×812 trên BA runtime: innerWidth=375, document/body scrollWidth=375. Đã đọc ảnh `docs/tdq/ba-mobile-375.png`, đóng Semantic Passport thành công; console không error/warn. Canvas rộng 744px trong container 341px, thanh điều khiển rộng 406px trong container 307px: có cuộn ngang nội bộ, không được gọi PASS tiêu chí tuyệt đối không scrollbar. Ảnh native-mobile cũ thực tế viewport 500px, không là bằng chứng 375px.
- QC runner `python scripts/tdq_test.py tron-bo` non-elevated đã kết thúc 02:16:08: `Ran 2975 tests in 618.083s`, `FAILED (failures=9, errors=2, skipped=10)`, ExitCode=1. Stdout/stderr/metadata: `archify-final-qc-stdout.log`, `archify-final-qc-stderr.log`, `archify-final-qc-status.log`. HEAD nền `5d6570d25ca54bd9c311b9efea9d39e1464b549d`, kiểm trên working tree dirty, không giả là commit mới.
- Regression mới: unittest discovery không import được `scripts.archify_artifacts` ở test artifacts. Đã mở QC2.1 sửa bootstrap import, không bỏ module. Ba lỗi bổ sung ở reminder_contract/tdq_test/tuong_thich_host đang đối chứng; không gộp vào 7 baseline đã chứng minh.
- `python scripts/tdq_test.py so` sau vòng này: full-suite runs 1, radius misses 0. Số 0 misses không chứng minh đủ coverage vì runner báo chưa có lượt vung-cham được ghi. Lượt pytest toàn repo trước đó nằm ngoài ledger này, vẫn phải tính trong lịch sử kiểm.

## Review độc lập vòng 1

Reviewer a89f551 trả FAIL: model chấp nhận evidence_kind=current trái hợp đồng manifest; explicit source directory làm lệch exclusion; source file bị xóa bị phân loại invalid thay vì stale; render rollback không khôi phục manifest/fresh output; directory rollback nuốt lỗi rồi có nguy cơ mất backup. Có 5 điểm được liệt kê (dù tiêu đề reviewer ghi 4).

Đã giao sửa QC1.1–QC1.3 đúng owner, giữ main ổn định trong lúc suite đầu chạy. Sau suite kết thúc đã nhập patch model/artifacts/CLI. Lệnh `python -m pytest tests/test_archify_artifacts.py tests/test_archify_model.py tests/test_archify_pipeline.py tests/test_tdq_archify.py -q --tb=short` đạt 149 passed trong 14.90s. Reviewer xác minh lại cả 5 findings trên worktrees đều VERIFIED PASS; QC1.1–QC1.3 đã tick. Đang đối chiếu ràng buộc/clean-code trên main cuối, không suy từ 5 findings này thành PASS toàn repo.

Reproducer artifacts trước đó chạy nhầm cwd main đã tái hiện 3 lỗi, trong khi `tdq_team check T2.3` chạy đúng worktree đạt. Hai kết quả thuộc hai snapshot khác nhau. Test `test_archify_finish.py` có BOM làm encoding gate thất bại; chỉ gỡ BOM, chạy lại `tests/test_ma_hoa_subprocess.py` đạt 3 passed trong 1.94s.

## Ràng buộc và clean-code sau nhập patch

Reviewer độc lập đọc main cuối xác nhận 5 findings đã sửa; chạy mục tiêu 149 passed và finish 17 passed. Không dùng kết luận này thay full-suite hoặc browser evidence.

- QC-F3: Không thêm import scripts→hooks; adapter quản lý manifest riêng, không ghi state request trực tiếp; engine local, không thêm client endpoint/API. `archify_delivery.py` đặt `ARCHIFY_UPDATE_CHECK_DISABLED=1` khi gọi engine.
- QC-F4 SRP: CÓ — delivery/model/artifacts/CLI tách trách nhiệm; các bước rollback và fingerprint tách helper sau vòng sửa.
- QC-F4 OCP: CÓ đối với tập diagram/evidence được hỗ trợ qua hằng số dữ liệu; không khẳng định mọi tính năng tương lai chỉ cần một dòng dữ liệu.
- QC-F4 LSP: CÓ theo review — các nhánh kết quả công khai dùng cùng cấu trúc/contract lỗi; không còn NamedTuple override sai.
- QC-F4 ISP: CÓ theo review — tham số helper được dùng cho tác vụ tương ứng.
- QC-F4 DIP: CÓ — facade/setup/finish dùng entrypoint chung, không sao chép giao nhận hoặc lifecycle.
- Diagnostics main cuối: `pyright scripts/archify_delivery.py scripts/archify_model.py scripts/archify_artifacts.py scripts/tdq_archify.py` → `0 errors, 0 warnings, 0 informations`.
- Browser desktop BA 1440×900: đã đọc ảnh `docs/tdq/ba-desktop-1440.png`, ba node và nhãn/legend hiển thị rõ, toolbar và node index không đè sơ đồ. Đây là fixture kiểm runtime, không phải bản đồ toàn TDQ.

## QC vòng 2 và việc còn lại

QC2.1 đã nhập bootstrap import chuẩn (`from archify_artifacts` sau thêm scripts vào sys.path), không dùng fallback ImportError rộng. Main: `python -m pytest tests/test_archify_artifacts.py -q --tb=short` → 43 passed trong 6.15s; `python scripts/tdq_test.py vung-cham --files tests/test_archify_artifacts.py --silent` → PASS, 3 modules trong 9.06s (artifacts/build_portable/ma_hoa_subprocess). Unittest import được artifacts nhưng vẫn không thu 43 hàm pytest; pytest riêng là bằng chứng bắt buộc, không gọi 0 tests là kiểm chức năng.

- Suite sau sửa cuối chạy non-elevated đã kết thúc: `Ran 2974 tests in 601.138s`, `FAILED (failures=9, errors=1, skipped=10)`, ExitCode=1. Bằng chứng riêng `archify-qc-after-fix-{stdout,stderr,status}.log`, không ghi đè suite trước. Lỗi import artifacts không còn. Số tests giảm 1 do `_FailedTest` biến mất, không phải xóa test hành vi; 43 hàm artifacts vẫn được kiểm riêng bằng pytest.
- Cả 10 lỗi còn lại khớp đối chứng baseline. T5.2 và Q8 chưa tick theo quy tắc plan không đóng khi suite còn đỏ. Không có tác vụ kiểm nền còn chạy.
- Ledger cuối `python scripts/tdq_test.py so`: 2 lượt tron-bo, 9 radius misses (9 module lỗi nền không được lượt vung-cham của bản sửa import chọn). Đây là giới hạn coverage của lượt vùng chạm hẹp, không được ghi thành 0 misses.
- Gate chuyển phase qc bị chặn bởi 6 worktree dirty. Đã `pause --loai pha-huy` để bảo toàn bản bàn giao theo quy tắc không tự commit/xóa; không sửa state trực tiếp hoặc lách gate.
- Diagnostics 0 errors chỉ áp dụng 4 module production; negative tests artifacts cố ý truyền None/list/scalar vẫn có cảnh báo kiểu ở IDE, không tuyên bố toàn bộ tests sạch pyright.
- Giữ worktree dirty làm bản bàn giao, chưa commit. Không clean cưỡng bức; bản diff đã nhập main có kiểm thử nhưng ledger còn mở.

## Baseline phân biệt

Log request cũ: 2829 tests, 14 failures, 1 error, 9 skipped. Lượt mới trước sửa: doc_index/encoding/ledger 4 fail,36 pass; skill shape/links/description 5 fail,26 pass; portable39!=38. Một phần đã sửa và tái kiểm.

Agent đối chứng độc lập đã chạy từng test bằng `python -m pytest tests/<file>.py -k <test_name>` trong snapshot riêng của cả `a03d698` và `5d6570d`; mỗi test dưới đây đều exit 1, 1 failed ở cả hai mốc. Không sửa assert, không sửa main. Lượt main của leader: 7 failed, 43 passed, 2 subtests passed trong 3.39s.

| Test | a03d698 | 5d6570d | Main hiện tại |
|---|---|---|---|
| test_next_step_moi_dong_neu_duoc_pha_ke | 2 browser skills thiếu pha kế | Giống | Giống |
| test_moi_reference_duoc_skill_md_tro_thang | 3 reference thiếu link trực tiếp | Giống | Giống |
| test_khong_link_nao_tro_vao_hu_khong | Link chrome-devtools-mcp-scripts.md không tồn tại | Giống | Giống |
| test_exactly_six_skills | 11 skills so với 9 limits | Giống | Giống |
| test_skill_descriptions_total | 2051 > 1800 ký tự | Giống | Giống |
| test_entrypoint_moi_file_deu_toi_duoc_utf8_io | 5 entrypoint thiếu bootstrap | 6, thêm tdq_archify | 5, đã sửa tdq_archify |
| test_tier1_wiring_across_skills | Thiếu vision-test-loop link ở tdq-spec | Giống | Giống |

Bổ sung sau runner tổng hợp: reviewer thứ hai trích snapshot a03d698 và 5d6570d, chạy targeted pytest cho 3 test còn lại; cả hai mốc đều exit 1 cùng lỗi main:

| Test | Cả hai baseline và main |
|---|---|
| test_search_gate_repeat_denial_shorter_and_preserves_recovery | JSONDecodeError tại line 190 vì out1 không chứa JSON |
| test_ban_kinh_ca_da_do_ask_gate_nho | 4 modules > cap 3, cùng danh sách ask_gate/hook_windows/subagent_start/tdq_test |
| test_tuyet_doi | Assertion đường dẫn hook Windows không tuyệt đối tại line 75 |

Tổng cộng 10 test lỗi đã đối chứng là lỗi nền (9 failures + 1 error). Lỗi thứ 11 của runner là import test_artifacts mới, đang sửa riêng QC2.1. Không nâng cap token, bỏ luật hoặc làm lỏng assert để che lỗi nền.
