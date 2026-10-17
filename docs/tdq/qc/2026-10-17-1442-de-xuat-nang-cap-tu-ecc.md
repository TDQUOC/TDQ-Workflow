# QC — Đề xuất nâng cấp TDQ Workflow từ ECC
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-10-17 · Plan: `docs/tdq/plan/2026-10-17-1442-de-xuat-nang-cap-tu-ecc.md` · Mức: ultra · Vòng: 1

## 1. Ma trận kiểm định

Có 9 dòng DoD Q-A–Q-I và 4 mục cố định QC-F1–QC-F4, tổng 13 mục. Các dòng Q-A–Q-I dùng lời gọi công cụ Agent tại T3.1 và kiểm CLI bổ trợ, không gọi một agent cho mỗi dòng. Trạng thái CHỜ không phải PASS.

| Mã | Nội dung và phép kiểm | Bằng chứng hiện có | Kết luận |
|---|---|---|---|
| Q-A | Nguồn/snapshot và quan hệ thực tế; Agent QC đối chiếu code/manifest | QC1.1 đã sửa; agent đọc lại đúng snapshot và nguồn thật, `Q-A D06 recheck PASS` | PASS |
| Q-B | Tính lại mẫu thô, tái lập entry point trong temp | Agent tính lại median/p95, tái lập smoke ledger=2; giới hạn mẫu/Unicode/synthetic giữ nguyên | PASS |
| Q-C | Đọc từng trụ cột O2, lần ngược tới O1/source | Agent đối chiếu đủ năm trụ cột, D09/D10 khớp nguồn | PASS |
| Q-D | Kiểm mọi trường của D01–D10 | Agent kiểm đủ dependency, chi phí, rollback và go/no-go | PASS |
| Q-E | Tính lại định lượng, phân loại đo/mô hình/thiếu dữ liệu | Agent tính 418.12/1067.3/2245.9 ms và 26983.98 phiên, khớp báo cáo | PASS |
| Q-F | Dependency và điều kiện vào/ra roadmap | Agent đọc roadmap và tái chạy simulate: main, gap 0.0 phút | PASS |
| Q-G | Kết quả độc lập và xử lý phát hiện không bị che | §3 giữ FAIL vòng đầu, QC1.1, tái kiểm PASS và evidence M1–M7; ghi rõ hai biên runtime exit=1 | PASS |
| Q-H | Lint O1/O2/O3 và suite hiện có | Lint ba artifact 15:49:07 đạt 0 lỗi; suite cuối 134 modules/2602 tests, 9 skip, không failure | PASS |
| Q-I | Git diff/status hai repo; state/log qua CLI | Agent PASS; leader kiểm lại 15:44: chỉ docs/workflow, ECC sạch, diff-check đạt; chưa commit/push | PASS |
| QC-F1 | `python3 scripts/tdq_test.py tron-bo --silent` và `so` | Cả hai lượt đạt 134 modules/2602 tests, 9 skip; runner cuối 481.46s; ngân sách 2/2, 0 radius miss | PASS |
| QC-F2 | `vung-cham --files` cho ba vùng tài liệu; kiểm semantic bởi Agent | 15:43:24: 3 docs, 0/134 modules, 0.52s; không code runtime mới để có module coverage; semantic Q-A–Q-G đạt | KHÔNG ÁP DỤNG unit module; kiểm tài liệu đạt |
| QC-F3 | Giữ từng ràng buộc kiến trúc spec §5 | Sáu đối chiếu cụ thể tại §4, git không có source đổi, state qua CLI | PASS |
| QC-F4 | Clean code | KHÔNG ÁP DỤNG — không sửa file code | KHÔNG ÁP DỤNG |

## 2. Bằng chứng CLI

### Lint và vùng chạm trước QC

O1: lint ngày 2026-10-17 15:23:05, 0 violations, exit 0; vùng chạm 15:23:06, files=1, modules=0/134, fallback=none, ok=True, 0.51s.

O2, output ngày 2026-10-17:

```text
[2026-10-17T15:29:06] doc_lint: done — 0 violation(s) total, exit 0
[2026-10-17T15:29:07+07:00] tdq_test: vung-cham files=1 modules=0/134 fallback=none ok=True seconds=0.51
[TDQ:TEST] PASS — 0 modules tested in 0.51s.
```

Lint ba artifact ngày 2026-10-17 15:31:14: `0 violation(s) total, exit 0`. O3 vùng chạm 15:31:15: `files=1 modules=0/134 fallback=none ok=True seconds=0.52`.

**KHÔNG CÓ TEST runtime module tương ứng O1/O2/O3:** đây là ba tài liệu, không phải node code. Kết quả 0 module không được cộng thành PASS unit coverage. Spec/plan đã bỏ unit test runtime mới có chủ đích; thay bằng lint, kiểm nguồn/số liệu/ngữ nghĩa và suite hiện có. Phải đọc verdict semantic độc lập trước nghiệm thu tài liệu.

### QC-F1 — Trọn suite và ngân sách

Lệnh chạy từ repo chính lúc 15:30:08: `python3 scripts/tdq_test.py tron-bo --silent`, hoàn tất exit 0 lúc 15:38:10. Output quyết định:

```text
[2026-10-17T15:38:10+07:00] tdq_test: tron-bo modules=134 failed=0 missed=0 ok=True seconds=481.63
[TDQ:TEST] PASS — full suite (134 modules) passed in 481.63s.
Ran 2602 tests in 480.820s
OK (skipped=9)
```

Hai dòng unittest được trích từ `docs/tdq/.tdq-test.log`; log có NUL prefix, chỉ loại byte NUL trong bộ nhớ để đọc, không sửa file log hoặc đổi kết quả. 9 skip được giữ nguyên, không gọi 2602 test là tất cả đều thực thi. Tổng wall time runner khác thời gian unittest do overhead.

Lệnh `python3 scripts/tdq_test.py so` lúc 15:38:30:

```text
full-suite runs: 1 of budget 2
radius misses: 0
```

Lượt hồi quy cuối sau QC1.1: cùng lệnh, exit 0 lúc 15:48:49:

```text
[2026-10-17T15:48:49+07:00] tdq_test: tron-bo modules=134 failed=0 missed=0 ok=True seconds=481.46
[TDQ:TEST] PASS — full suite (134 modules) passed in 481.46s.
Ran 2602 tests in 480.682s
OK (skipped=9)
full-suite runs: 2 of budget 2
radius misses: 0
```

Lệnh `so` và lint ba artifact lúc 15:49:07 đều đạt; lint `0 violation(s) total, exit 0`. Không chạy lượt suite thứ ba chỉ để chép output/timing vào hồ sơ. Các chỉnh bookkeeping kết quả sau đây được lint lại bằng lệnh chốt.

Các dòng fixture giả lập publish/consent trong stdout suite không phải thao tác phát hành/cấp quyền thật; git status sau suite chỉ có tài liệu/workflow trong repo chính, ECC vẫn sạch. Không dùng stdout fixture như sự cho phép của người dùng.

### Phạm vi và state

Lệnh kiểm 15:30: `git status --short`, `git diff --stat`, `git -C C:/Users/admin/Documents/ECC status --short`, `python3 scripts/tdq_state.py get muc_qc`, `lech list`, `get lsp_bo_qua`.

Kết quả: `ultra`; `0 item(s), 0 pending`, không có lệch spec được ghi; `lsp_bo_qua` không có giá trị. CLI 15:32 xác nhận `spec_approved=true`, `plan_approved=true`, `implement_mode=main`. Tính lại hash phần nội dung từ heading `## ` đầu tiên theo `sha256_noi_dung` đạt đúng fingerprint niêm phong `8750ab433ba47c9723734fc73e6c52cd50ce6ff42c4040da9823a227d706c53a`; đây không phải SHA-256 toàn file. Hai HEAD vẫn đúng snapshot O1; `git diff --check` không có lỗi whitespace. TDQ tracked dirty chỉ `.tdq-phat-hanh.json`, `STATE.md`, `timing.jsonl`, working log 2026-10-17; untracked là hồ sơ cùng slug. ECC sạch. Những tracked path này đã dirty trước request; không reset/ghi đè để tạo repo sạch giả.

## 3. Kiểm định độc lập

Lời gọi: công cụ `Agent`, `subagent_type=tdq-workflow:tdq-qc-tester`, description `Kiểm định độc lập qc-de-xuat-ecc`, model override `opus`, effort `high` theo vai trò. Lý do override: T3.1 là cổng khó nhất về kiểm chứng xuyên hai repo, tính lại dữ liệu và phản biện độc lập; không dùng agent này chỉ để bọc một lệnh CLI. Người kiểm khác các agent khảo sát O1 và khác leader viết O2. Phạm vi: đọc spec/plan/O1/O2, xác minh nguồn cả hai repo, tính lại bảng và chạy kiểm cô lập khả thi; không sửa source/state, không chạy lại suite do leader đang chạy.

### Verdict vòng đầu và xử lý phát hiện

Agent đã đọc nguồn trực tiếp và tự tái lập phép đo an toàn, không chạy lại trọn suite; đọc log/ledger leader cho Q-H. Kết quả vòng đầu: Q-A FAIL riêng provenance D06; Q-B/Q-C/Q-D/Q-E/Q-F/Q-H/Q-I PASS; Q-G chờ leader ghi kết quả. Không gọi Q-G chờ là tác giả tự duyệt.

**Phát hiện QC1.1, mức vừa:** O1 E-T2 và O2 D06 dẫn `hooks/hooks.metadata.json:271` và `scripts/ci/validate-carrier-closure.js:507`, trong khi file snapshot chỉ 157/229 dòng. Đây là dẫn nguồn sai thật, không phải lint hay thiếu heading. Hai dẫn nguồn đó đã được gỡ khỏi O1/O2.

**Sửa tối thiểu:** dùng `scripts/lib/context-carriers.js:146-170`, leader đọc trực tiếp đoạn nguồn: có registry/profile/compiler/plan/adapter/content digest và carrierDigest; dòng 165 yêu cầu revalidate nguồn khi materialize. Nêu rõ assignment/progress projection là đề xuất của TDQ, không gán thành thuật toán ECC đã có. Không đổi ưu tiên hoặc runtime. Plan thêm QC1.1; lint hai tài liệu 15:40:33 đạt 0 lỗi, vùng chạm 15:40:34 là 0/134 modules, 0.51s. Agent đang tái kiểm riêng finding này.

**Đối chiếu định lượng độc lập vòng đầu:** agent tính lại median/p95 khớp O1, mô hình startup 418.12/1067.3/2245.9 ms; hoàn vốn giả định 26983.98 phiên. Tái lập smoke valid/malformed/recovery giữ ledger=2. Q-C đủ năm trụ cột; Q-D đủ trường; D09/D10 khớp nguồn. Không lấy độ trễ tái lập phải giống từng chữ số làm tiêu chí — chỉ kiểm phương pháp và output/ledger, số mới phải giữ là lần đo khác.

### Tái kiểm QC1.1 và bằng chứng thực thi độc lập

Agent xác nhận dùng đường dẫn tuyệt đối repo chính, HEAD `5c8a9c22a42a59c5a2e0f2941ed92bced36e9df3`, không dùng snapshot worktree. `python -I -B -c …` đọc lại HEAD/nguồn/O1/O2 trả `Q-A D06 recheck PASS`; lint hai file sau sửa lúc 15:41:18: `0 violation(s) total, exit 0`. Q-A đã PASS sau sửa; không còn finding provenance mở.

Các command dưới đây là mô tả lời gọi Python agent đã thực thi, dấu `…` không phải lệnh tái lập copy/paste. Driver đầy đủ và đầu vào gốc tại O1 M1–M7; số tái lập là lần đo độc lập, không thay mẫu gốc.

| Mã | Cách kiểm độc lập đã chạy | Output/oracle thực |
|---|---|---|
| M1 | `python -I -B -c …` đọc/chạy driver O1 M1; 14 subprocess/case, bỏ first và warm-up, n=12 | Median/p95 ms: noop 21.478/22.080; nonconcept 54.270/56.555; LSP 54.812/56.127; ledger=14 |
| M3 | Driver stdlib gọi hook thật, `TDQ_PROJECT_DIR`/cwd=temp Unicode+khoảng trắng, timeout=120 mỗi con | valid/malformed/recovery/empty/nonconcept exit=0; ledger=2, `lsp:find_references`, `phien:smoke` |
| M4 | Import isolated `search_rules`, gọi `la_goi_khai_niem`, không chạy payload | PowerShell/Bash command trực tiếp → `graphify:query`; Write-Output/printf chứa chuỗi → `None` |
| M6 | Import `tdq_team`, 3 Task, B.text=`['Cần: T1.1']`, `quyet_dinh_task`/`chia_dot` | Cả ba `giao`; waves T1.1=1, T1.3=2, T1.2=2 |
| M7 | Import `prompt_context`, gọi hàm thuần `looks_like_approval` | spec/plan/1a/inline/English/XML/phủ định/sửa thêm/rỗng → T/T/F/T/T/T/F/F/F |

Agent cũng tính lại M1 gốc và bảng M2 từ manifest; số M1 tái lập chênh với gốc là nhiễu bình thường, không bị sửa để đạt giá trị mong muốn. M3 độc lập đã bổ sung đường Unicode thật, trong khi phép đo gốc O1 vẫn chỉ chứng minh khoảng trắng.

**Giới hạn runtime cũ phát hiện thêm:** JSON hợp lệ nhưng top-level `null` hoặc `[]` khiến observer exit=1 với `AttributeError`; malformed JSON/empty input có recovery khác và exit=0. Không gọi observer fail-open cho mọi input. Đây là hành vi source hiện có không bị request tài liệu thay đổi; ghi vào giới hạn/đề nghị regression D03/D05, không tự sửa runtime ngoài spec và không giấu thành PASS cho hai case này.

Leader còn chuẩn hóa các dẫn nguồn viết tắt thành đường dẫn tương đối đầy đủ để bấm/tìm được trực tiếp, không đổi kết luận. Driver Python stdlib kiểm sự tồn tại và giới hạn dòng của 34 citation O1 và 14 citation O2 trả `invalid=[]` cho cả hai; đây chỉ là kiểm vị trí, không thay kiểm nội dung độc lập.

Q-G được leader đối chiếu bằng cách ghi đúng verdict ban đầu, finding, sửa và xác nhận độc lập; không yêu cầu agent tự viết/duyệt artifact của họ. Q-H chỉ chốt khi suite cuối và lint cuối hoàn tất.

Sai lệch thao tác công cụ: lời gọi Agent của leader đã truyền `isolation=worktree` dù nhiệm vụ chỉ đọc và không cần worktree; công cụ tạo worktree tạm ở HEAD khác. Leader đã yêu cầu agent dùng đường dẫn tuyệt đối repo chính có HEAD `5c8a9c2`, không dùng cwd worktree để kiểm snapshot. Không nhập/merge bất kỳ thay đổi nào từ worktree đó vào sản phẩm; không xóa cưỡng bức. Đây là thao tác thừa cần tránh, không phải bằng chứng snapshot TDQ đã đổi. Agent sau đó xác nhận đã đọc đúng repo chính. `git worktree list` lúc 15:44:39 chỉ còn worktree chính; worktree agent không còn sau khi tác vụ kết thúc, leader không xóa cưỡng bức hoặc merge nó.

## 4. Ràng buộc kiến trúc và smoke/runtime

Đối chiếu QC-F3 với spec §5:

1. `hooks/` được gọi `scripts/`, không chiều ngược: không sửa import hay file source. Dispatcher D08 chỉ là đề xuất request tương lai, không tạo cạnh import runtime.
2. Chỉ `scripts/tdq_state.py` ghi state: phê duyệt/chuyển phase bằng CLI; working log qua `tdq_finish.py`, không chỉnh state/mirror thủ công.
3. Hook không deny chỉ vì chưa duyệt: không sửa gate; D01/D07 không coi số lần chặn hoặc notification là quyền duyệt. CLI approve vẫn có quyền từ chối theo hợp đồng riêng.
4. Trọn suite tại hai cổng: lượt đầu ở QC-F1; chỉ chạy lượt thứ hai nếu có vòng sửa QC cuối. Không gọi suite trùng vì đổi người kiểm.
5. R14 giữ tại `approve spec`, không đưa vào hook; spec đã niêm phong không sửa nội dung.
6. Mức QC giữ `ultra` do người dùng chọn; mode main không loại thẩm định độc lập.

Smoke entry point hiện có được ghi tại O1 M3: valid → malformed → valid recovery, mỗi con `timeout=120`, exit 0, ledger đúng hai dòng. Shell strings M4 chỉ là input cho recognizer, không được thực thi. Đây là test hook hiện có, không chứng minh dispatcher/parser đề xuất đã chạy.

Runtime mới: KHÔNG ÁP DỤNG — sản phẩm là Markdown, không có service/daemon/handler mới. Không dựng service chỉ để điền một ô ultra và không gọi hook SessionStart của host là phép đo controlled runtime. Kiểm tái lập có output thật của agent đã ghi tại §3, gồm Unicode và biên type lỗi hiện hữu. Các biên lỗi đó không được gọi là runtime đã vá; DoD của request tài liệu yêu cầu phát hiện/giới hạn trung thực, không yêu cầu sửa runtime ngoài phạm vi.

## 5. Lệch spec chờ duyệt

CLI `lech list` tại 15:30: `0 item(s), 0 pending`. Chưa ghi lệch.

## 6. Kết luận hiện tại

NGHIỆM THU TÀI LIỆU ĐẠT: 9/9 DoD PASS; QC-F1 và QC-F3 PASS; QC-F2 không có unit runtime module mới và không được tính thành PASS code coverage, kiểm tài liệu/ngữ nghĩa đã đạt; QC-F4 KHÔNG ÁP DỤNG — không sửa file code. Tổng 13 mục đã có quyết định rõ, không còn mục CHỜ hoặc finding tài liệu mở. Một vòng sửa QC1.1 đã được kiểm lại độc lập. Hai suite đều đạt, 9 skip mỗi lượt giữ nguyên, không có lệch spec chờ duyệt. Các giới hạn runtime hiện hữu được công khai, không tuyên bố đã vá hoặc nâng cấp runtime.
