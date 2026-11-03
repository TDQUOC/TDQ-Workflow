# QC — Đợt 1: đo đúng và bảo toàn lỗi

Ngày: 2026-10-27 · Plan: ../plan/2026-10-27-1246-do-dung-bao-toan-loi.md · Vòng sửa: 2 · Mức: Full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Môi trường thực: Windows, Python 3.13.15; pytest 9.1.1 và xdist 3.8.0 có sẵn. Không đặt UTF-8 toàn cục cho suite, không cài thêm dependency. Các fixture sửa state/finish dùng project và HOME tạm. Không chạy smoke/runtime session riêng ở mức Full. Mọi đường dẫn bằng chứng dưới đây tương đối với hồ sơ này.

## Bảng nghiệm thu

| # | Hạng mục | Lệnh đã chạy / bằng chứng | Kết quả | Đánh giá |
|---|---|---|---|---|
| D1 | Timing/union/quality | `python -m unittest discover -s tests -p test_timing.py` | 63 test, 4.168s, exit 0 | PASS |
| D2 | Nguồn Claude/Codex | `python -m unittest discover -s tests -p test_transcript.py` | 50 test, 0.136s, exit 0 | PASS |
| D3 | Verdict hai backend | `python -m unittest discover -s tests -p "test_tdq_test*.py"` | 141 test, 14.283s, exit 0 | PASS |
| D4 | Lựa chọn gián tiếp | `python -m unittest discover -s tests -p test_tdq_test.py -k IndirectSelection` | 12 test, 1.874s, exit 0 | PASS |
| D5 | Tương thích/lịch sử | `python -m unittest discover -s tests -p test_phase1_contract.py -k Compatibility` | 4 test, 1.363s, exit 0 | PASS |
| D6 | Trạng thái cuối và QC Full | Dùng cùng lượt QC-F1, kết hợp F2–F4 | 3.206 unittest + 84 pytest, tổng 12 skip, không còn failure ở lượt chứng nhận | PASS trong môi trường nêu dưới |
| D7 | Bằng chứng/bàn giao | Lint QC/report, đối chiếu output và binding/hash preview | Lint 0 lỗi; 14 kiểm nội dung/hash/nguồn/giới hạn đều đúng | PASS |
| QC-F1 | Toàn unit suite và sổ | `python scripts/tdq_test.py tron-bo`, sau đó `so --json` | Lượt 3: 3.206 test, 10 skip, exit 0; giữ hai lượt FAIL trước | PASS |
| QC-F2 | Hồi quy vùng chạm/consumer | Selector vùng chạm chọn full; dùng bằng chứng F1 và bổ sung sáu module pytest | 167/167 module có bằng chứng thu thập; consumer và test sửa đều có mặt | PASS bằng kết quả kết hợp, không chạy lại toàn suite |
| QC-F3 | Giữ ranh giới kiến trúc/ngôn ngữ | AST + diff/caller; i18n toàn file và so với baseline | Không import hooks/tests; 2 module mới chỉ stdlib; 0 finding i18n mới | PASS trên phạm vi thay đổi |
| QC-F4 | Clean code | Rà 5 nguyên tắc, AST và review hàm sửa | Nhánh AST tối đa 10; giới hạn công cụ nêu dưới | PASS qua rà soát |

## Bằng chứng D1–D5 và RED/GREEN

Các biên nhận lưu command, cwd, thời điểm, thời lượng và exit; `.stdout.txt`/`.stderr.txt` cạnh mỗi biên nhận giữ output đầy đủ: [D1](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-D1.json), [D2](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-D2.json), [D3](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-D3.json), [D4](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-D4.json), [D5](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-D5.json).

Trích kết thúc các lượt chạy, lần lượt D1–D5:

```text
Ran 63 tests in 4.168s / OK
Ran 50 tests in 0.136s / OK
Ran 141 tests in 14.283s / OK
Ran 12 tests in 1.874s / OK
Ran 4 tests in 1.363s / OK
```

Không cộng các số trên thành số test khác nhau: D4 nằm trong D3; các nhóm đều còn được toàn suite kiểm. Các lượt D1–D5 chạy đồng thời khi QC-F1 đang chạy, vì vậy thời lượng không phải benchmark tốc độ tuần tự hay A/B.

[Baseline E1–E4](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/baseline.json) giữ lỗi trước sửa. [RED T3.2](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/tdq-t3.2-red.txt) chạy đúng hai regression trên snapshot `3e0ef5f`: `model_giay=120` thay vì null và direct rỗng exit 0 dù indirect lỗi. [GREEN T3.2](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/tdq-t3.2-green.txt) có 6 test qua entry point thật, trong đó 4 Compatibility. [T3.1 GREEN](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/tdq-t3.1-green.txt) có 9 test log/JSON; RED baseline bắt cả status `--json` xuất text. RED baseline là bằng chứng hồi quy, không phải lỗi còn tồn tại ở bản mới.

## QC vòng 1 — lỗi thực và cách xử lý

[QC-F1 đầu](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-F1.json): 3.206 test trong 590.148s; 9 skip, 5 failure, exit 1. Ledger giữ FAIL, `details_complete=true`, bốn failed module và bốn module bỏ sót so với lượt vùng chạm trước đó. Không xóa hoặc viết lại lượt đỏ này.

| Lỗi | Nguyên nhân và thay đổi | Kiểm lại |
|---|---|---|
| Hai subtest Archify full/quick | Chrome pipe đóng trước phản hồi trong phiên elevated. Không sửa test/engine; chạy native gate ở tiến trình quyền thường qua Explorer | `test_archify_e2e.py`: 2 test gồm subtest full/quick, 12.788s, exit 0 |
| Ngân sách cây release 161 > 160 | Baseline 159 file, thêm đúng hai module runtime được duyệt. Kiểm hai module có trong release/manifest và import closure; giữ trần 160 cho mọi file còn lại | `test_build_portable.py`: 37 test, 5.962s, exit 0; check và merge đều chạy lại kiểm thật |
| Chỉ mục report-template lệch | Sinh lại chỉ mục của đúng file đã đổi | `test_doc_index.py`: 26 test, 0.085s, exit 0 |
| Neo luật L037 cũ | Giữ câu lịch sử, trỏ neo hiện hành sang định nghĩa timing v2; không chèn lại phát biểu model-time sai | `test_luat_skill.py`: 11 test, 0.143s, exit 0; token lock đếm thật 58 file |

[Bối cảnh quyền thường và cách tái lập](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC1.2-context.md) · [Archify GREEN](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC1.2-normal.json) · [portable RED](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/tdq-qc1.1-red.txt) · [portable GREEN](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/tdq-qc1.1-green.txt) · [laws](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC1.3-GREEN-laws.json) · [index](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC1.3-GREEN-index.json).

Lượt vùng chạm ngay sau sửa tài liệu còn FAIL vì bản sửa portable chưa hợp nhất; biên nhận `QC1.3-radius.json` giữ nguyên. Sau hợp nhất, [vùng chạm 20/167 module](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC1.3-radius-GREEN.json) đạt **281 test, 6 skip, exit 0**, không fallback. Toàn suite được chạy lại sau vòng này. Việc probe Chrome/Edge rồi đổi bối cảnh tiến trình thuộc xử lý cùng lỗi môi trường, không phải mở rộng scope source.

## QC vòng 2 — cô lập fixture cập nhật plugin

[Lượt Full thứ hai](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-F1-final.json), tên biên nhận lịch sử có chữ `final`, thực tế **FAIL**: 3.206 test, 669.091s test / 670.659s tiến trình, 10 skip, 1 failure. Tên file không được dùng thay verdict. Archify native đã qua; failure còn lại là `test_tu_dong_cap_nhat_plugin_user_with_cli_runner`.

Test này truyền repo thật vào `goc_plugin`; fake CLI không cập nhật metadata nên updater chuyển sang nhánh copy thật, kéo theo `.claude/worktrees/.../.pytest_cache` không đọc được ở quyền thường. QC2.1 sửa **test fixture**, tạo nguồn plugin/HOME/project tạm, giữ copy fallback thật, kiểm payload, manifest, version/installPath/scope. CLI discovery và tiến trình CLI được giả lập để test không cài plugin thật; copy và ghi metadata không mock. Không sửa runtime updater, ACL hoặc xóa các worktree cũ.

[GREEN 6 test](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/tdq-qc2.1-green.txt) · [check](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC2.1-check.json) · [merge](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC2.1-merge.json) · [hồi quy quyền thường](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC2.1-normal-radius.json): **46 test, 0 skip, exit 0**, chọn 3/167 module bắc cầu. Lượt Full thứ ba là kiểm cuối sau vòng sửa thứ hai. Dự kiến ban đầu là hai lượt; sổ máy cuối ghi `tron_bo=3`, `ngan_sach=3`. Báo đúng ba lượt thực tế và giữ nguyên các lượt đỏ.

**Sự cố fixture và khắc phục:** lượt kiểm đầu của agent lúc 15:00:48 chưa có cờ cô lập đã để test setup cũ ghim block TDQ trong `C:/Users/admin/.claude/CLAUDE.md` sang nguồn checkout. File này không có backup tự động. Đã ghim lại block đúng bản cài Claude 0.84.2 được chỉ rõ khi bắt đầu phiên, giữ nội dung ngoài block; [biên nhận lần đầu](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC2.1-user-config-repair.json). Fixture QC2.1 mới đặt HOME/USERPROFILE/TDQ_PROJECT_DIR tạm và cờ an toàn trong setUp.

Sau Full lần ba, kiểm hash phát hiện block bị ghi lại lúc 15:15:43; [kiểm cuối ban đầu](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-final-user-config-check.json) giữ kết quả false. Đã tái lập an toàn bằng HOME riêng: `SessionStart` thấy project chưa có mốc phiên bản thì gọi `thuc_hien_setup_bu`, vốn ghi instruction mà chưa chặn bằng `TDQ_KHONG_CHAM_MAY`. `tests/test_tu_khoi_tao.py` gọi hook với project `.git` tạm nhưng không đổi HOME; thời điểm chạy phù hợp với lần ghi. [Probe cô lập](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-user-config-isolated-probe.stdout.txt) xác nhận cơ chế, không phải trace trực tiếp PID của lần ghi cũ. Bốn file hook/setup/helper/test liên quan không đổi so với baseline.

Đã [ghim lại lần cuối](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-user-config-final-repair.stdout.txt) lúc 15:23 sau khi xác nhận block hiện tại đúng mẫu checkout và nội dung ngoài block trùng backup trước; hash sau sửa trùng lần phục hồi đầu. Backup riêng: `C:/Users/admin/AppData/Local/Temp/tdq-phase1-user-claude-before-final-repin.md`. Không đưa nội dung cá nhân vào repo; không có snapshot trước sự cố nên không tuyên bố khôi phục byte-for-byte bản ban đầu. **Khoảng trống cô lập của hook cũ vẫn còn**, cần request riêng; cờ an toàn hiện có chưa đủ để bảo đảm mọi fixture không ghi HOME thật. Đây là giới hạn được ghi nhận, không phải mục đã sửa trong đợt 1.

**Giới hạn còn lại ngoài scope:** runtime updater hiện vẫn có thể copy vào cây `.claude/worktrees` nếu người gọi đưa một checkout chứa cache cá nhân làm nguồn plugin. Đây là vấn đề bộ lọc đóng gói/cập nhật cần request riêng; kết quả test mới chứng nhận cập nhật từ nguồn plugin hợp lệ, không chứng nhận mọi checkout bẩn. Việc cô lập fixture không được hiểu là đã sửa runtime updater.

## QC-F1/F2 — bằng chứng cuối và phạm vi thực chạy

[Full sau QC2](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-F1-after-QC2.json) bắt đầu 15:05:02, kết thúc 15:16:31: **3.206 test, 10 skip, 0 failure, exit 0**. Unittest đo 686.773s; runner đo 688.08s; biên nhận tiến trình đo 688.269s. Các số đo có điểm đầu/cuối khác nhau, không thay nhau tùy ý. HEAD là `d1b90b825596e84aba7136b02a545bc2fa06c21a`; 342 hash nguồn/test/skill giữ trong context. Quyền thường, không đặt `PYTHONUTF8`/`PYTHONIOENCODING` toàn cục.

Hợp 19 đường dẫn source/test thực sửa cho selector vùng chạm: 129/167 module đạt ngưỡng 60%, vì vậy chọn full. Không chạy lại cùng 11 phút chỉ để đổi nhãn QC-F2. Đã đối chiếu HEAD, hash, inventory, các consumer finish/next/token/step và test mới với lượt Full hiện tại. Đối chiếu ban đầu phát hiện unittest chỉ thu thập **161/167 module**; [proof ban đầu](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-F2-final-proof.json) giữ exit 1, không đổi thành PASS.

Sáu module viết dạng hàm pytest (`test_archify_artifacts`, `test_canvas_draw`, `test_check_canvas_layout`, `test_harvest`, `test_stop_batching`, `test_tcas_ast`) được chạy bổ sung tường minh. Lần đầu JUnit có 84 test, 0 failure nhưng tiến trình exit 1 vì pytest dọn symlink `pytest-current` cũ bị Access denied; [stderr](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-F2-pytest-supplement.stderr.txt) được giữ, không tính lượt này là PASS. Chạy lại với `--basetemp` riêng, không đổi ACL/xóa cache cũ: [kết quả](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-F2-pytest-isolated.json) **82 passed, 2 skipped, 6.45s; tiến trình 6.845s, exit 0**.

[Proof kết hợp](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-F2-combined-proof.stdout.txt) xác nhận đủ 167/167 module, source không đổi giữa hai lượt, JUnit và exit thống nhất, mọi check true. Dùng chính parser `tdq_test_result` và mapper của runner để đọc XML; không thêm bản ghi ledger giả cho lượt pytest chạy trực tiếp. Tổng hai tập không trùng là **3.290 test, 12 skip**. PASS ở đây không có nghĩa 12 ca skip đã được kiểm hoặc lệnh stdlib tự chạy được mọi test pytest.

[Sổ cuối](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-ledger-final.stdout.txt) ghi `tron_bo=3`, `ngan_sach=3`, `bo_sot=5`, `radius_complete=true`: năm module có failure từng bị vùng chạm trước đó bỏ sót được giữ trong lịch sử, dù lượt cuối đã xanh. Không tuyên bố “0 bỏ sót”. Ba tiến trình Full tiêu tốn tổng 1.951,093s, khoảng 32,5 phút; không lấy độ dài các lượt này để suy ra speedup của sản phẩm.

## Những test được skip

[Inventory skip](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-skip-inventory.stdout.txt) liệt kê 9 khai báo skip trong 3.206 test. Ba ca kiểm quyền POSIX không áp dụng trên Windows. Sáu ca `test_skill_tokens.py` kiểm tokenizer bị skip vì detector dùng `.venv-tokens/bin/python`; máy Windows thực có `.venv-tokens/Scripts/python.exe`. Vì vậy lý do máy in “thiếu tokenizer” không đủ để kết luận thư viện thật sự thiếu. Finish đã dùng tokenizer Windows này để đếm thật 58 file. Chưa sửa detector ngoài phạm vi request; sáu ca skip không được tính là đã kiểm thành công.

Ở quyền thường có thêm một skip động: `test_archify_delivery.TestAtomicDelivery.test_atomic_delivery_rejects_symlink`, vì môi trường không cho tạo symlink. Đã [kiểm riêng với verbose](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-normal-symlink.stderr.txt), xác nhận đúng lý do. Vì vậy tổng ở bối cảnh này là 10 skip; không thay quyền Windows để làm mất skip.

Lượt bổ sung pytest có hai skip symlink trong `test_archify_artifacts.py`; lý do nằm trong [JUnit XML](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-F2-pytest-isolated.xml). Tổng hai tập là 12 skip có lý do.

Không suy số test PASS bằng phép trừ số failure từ tổng: unittest có subtest, còn skip nằm trong tổng test đã chạy. Báo riêng tests/skipped/failures theo output thật.

## QC-F3 — kiến trúc và ngôn ngữ

| Luật spec §5 | Đối chiếu | Kết quả |
|---|---|---|
| scripts không import hooks | AST tất cả 7 source thay đổi | 0 import cấm |
| Không tầng runtime nào import tests | Cùng AST, gồm import nằm trong hàm | 0 import cấm |
| Skill chỉ hướng dẫn lệnh, không chép script | Diff report-template/status chỉ đổi nhãn và diễn giải timing | Giữ ranh giới |
| Chỉ tdq_state ghi state | Hai module mới không ghi state; timing chỉ đọc qua tdq_state và append timing; runner append ledger như cũ | Không thêm writer/quyền |
| Runtime mới đúng tầng | Chỉ thêm `scripts/tdq_transcript.py` và `scripts/tdq_test_result.py`, đều stdlib | Đúng tầng, không dependency mới |
| Giữ import timing muộn/approval | Diff state chỉ sửa `_dong_so_request_cu`: resolver auto và log sau khôi phục env | Không đổi approval gate |
| Ngôn ngữ theo tầng | Scan toàn file exit 1; scan chênh với snapshot nền exit 0 | 63 finding cũ, 0 finding mới |

[AST cuối](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-F3-final-structure.stdout.txt) · [lệnh i18n và exit 1](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-F3-i18n.json) · [đối chiếu từng finding sau QC fix](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/QC-F3-final-i18n-delta.stdout.txt).

63 finding toàn file gồm 56 ở state, 3 help text ở runner và 4 ở report-template; đều trùng nội dung baseline. **Không chứng nhận toàn bộ các file đã sạch i18n.** Phạm vi nghiệm thu là thay đổi giữ luật, không mở rộng thành đợt chuyển ngôn ngữ mã cũ; không thêm marker bỏ qua, không sửa scanner để xanh.

## QC-F4 — năm câu tự kiểm

| Nguyên tắc | Trả lời và bằng chứng |
|---|---|
| SRP | Có: adapter đọc/ghép sự kiện; parser kết quả thuần dữ liệu; timing hợp khoảng; runner điều phối và ghi sổ. Hàm CLI ghép các phần, không nhân bản parser. |
| OCP | Có trong các loại metric/verdict đã yêu cầu: dùng bảng `METRIC_NAMES`, `KINDS` và outcome mapping. Schema host mới vẫn cần parser được kiểm riêng; chưa có yêu cầu host thứ ba nên không dựng interface dự phòng. |
| LSP | Có theo hợp đồng hiện hữu: hai backend cùng trường kết quả; wrapper cũ giữ bool/tuple, true chỉ PASS. Timing giữ `None` khi không có request theo API cũ và giữ khóa model ở v2 dưới dạng null. |
| ISP | Có: project/source/filter truyền đúng nơi dùng; parser chỉ nhận kết quả/XML/inventory, không kéo state hay filesystem vào. |
| DIP | Có: token audit dùng wrapper đường dẫn của adapter; runner dùng chung parser/module mapper; state dùng entry point timing muộn và giữ quyền ghi state tại chỗ cũ. |

[Bộ kiểm AST có thể chạy lại](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/verify_structure.py) đếm nhánh của hàm mới/sửa, tối đa 10; đã đọc lại các hàm sát ngưỡng và cấu trúc lồng, tự rà cognitive không vượt 15. Đây là **ước lượng AST và review thủ công**, không phải chứng nhận từ radon/ruff. Máy thiếu ruff/radon/cognitive_complexity; chưa chạy linter/đo cognitive bằng công cụ, không ghi chúng là PASS. Không cài thêm theo phạm vi đã duyệt. `git diff --check` đạt; LSP diagnostics của step audit không có lỗi. LSP caller của state có lượt treo, đã dùng fallback grep và test consumer, không coi lượt treo là bằng chứng ngữ nghĩa thành công.

## D7 — snapshot thiết kế

Trước sửa, [T0.1 verify](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/T0.1-verify.json) current. Sau sửa cuối, [verify thực](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/D7-final-preview.stdout.txt) exit 1 với 14 file nguồn/skill/test đã đổi, **binding current/valid=true**; [năm kiểm binding/hash](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/D7-final-binding.json) đều đúng. Preview vẫn là snapshot planned đã duyệt, không được bind lại để che source drift. Master architecture stale có từ trước, không nằm trong đợt sửa này. Lỗi Chrome pipe ban đầu và kiểm CDP desktop/mobile bổ sung nằm trong [biên bản preview](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/spec-review.md); việc native E2E qua sau khi đổi bối cảnh không viết lại receipt preview cũ.

## Lệch spec chờ duyệt

CLI `tdq_state.py lech list`: `no spec deviation recorded`. Các giới hạn baseline i18n, công cụ lint, môi trường Windows và preview planned được công khai; không tuyên bố chúng đã được sửa hoặc đã chạy CI mọi nền tảng.

## Kết luận

D1–D7 và QC-F1–F4 đã đạt trong phạm vi/môi trường công khai ở trên. [Lint](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/D7-doc-lint.json) và [đối chiếu nội dung](../artifacts/2026-10-27-1246-do-dung-bao-toan-loi/D7-content-proof.json) kiểm số test/exit, ledger, nguyên output timing, preview, HEAD, 342 hash source và cấu hình sau phục hồi; không chỉ kiểm file có tồn tại. Không còn sửa source đang chờ hoặc test thất bại trong các lượt chứng nhận cuối. Các lỗi baseline ngoài scope vẫn được ghi nguyên trạng. Phase `report` chờ quyết định commit/bàn giao; chưa đóng request thành idle.
