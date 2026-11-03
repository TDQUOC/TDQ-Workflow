# QC — Đề xuất nâng cấp ECC toàn diện hơn
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-10-17 · Plan: `docs/tdq/plan/2026-10-17-1621-de-xuat-ecc-toan-dien.md` · Mức ultra · O3
Trạng thái: ĐÃ CHỐT KIỂM theo fallback; người dùng đã duyệt cả lệch #1/#2 bằng nguyên văn “duyệt lệch”, CLI ghi 2026-10-17T17:27:04+07:00; sổ lệch còn0chờ. Hai lượt suite đạt; không nghiệm thu ultra sạch hoàn toàn. Verdict FAIL Q-I/Q-J nguyên bản vẫn giữ. Các dòng “chờ duyệt/chưa duyệt” dưới đây là lịch sử trước phê duyệt này, không phải trạng thái hiện tại. Phê duyệt lệch không cấp quyền commit, cleanup worktree hay triển khai runtime.

## 1. Phạm vi và sổ thực thi

10 DoD Q-A–Q-J + QC-F1–F4 = 14 mục quyết định. Runtime mới/UI/unit mới không áp dụng do không sửa code; smoke dùng entry point TDQ hiện hữu và synthetic trace, không mô phỏng như runtime sản phẩm mới.

| Mã | Kiểm/evidence hiện có | Verdict hiện tại |
|---|---|---|
| Q-A | O1 §1–§4 snapshot/source; reviewer nguồn tái kiểm citation QC1.3 | PASS kiểm cuối |
| Q-B | O1 §2/§3, O2 §2; bổ sung gap eval auth Windows QC1.3 | PASS kiểm cuối sau sửa |
| Q-C | O2 §3 ánh xạ D01–D10, reviewer nguồn | PASS kiểm cuối |
| Q-D | O2 §4/§5 13 phiếu; reviewer thiết kế kiểm đủ trường | PASS kiểm cuối |
| Q-E | O1 §6/O2 §5/§6; QC1.2 sửa phân rã, reviewer tái kiểm đúng | PASS kiểm cuối sau sửa |
| Q-F | O2 §7 dependency/Windows/backlog; hai reviewer thiết kế và định lượng đạt | PASS kiểm cuối |
| Q-G | Ba chiều phản biện + kiểm cuối khác tác giả, lịch sử findings/sửa/tái kiểm tại §3/§4 | PASS kiểm cuối |
| Q-H | Lint ba artifact0; suite1 435.42s và suite2 434.79s, mỗi lượt134module/failed0/exit0 | PASS evidence leader cập nhật sau notification; kiểm cuối trước đó CHỜ, không phải rerun độc lập mới |
| Q-I | O1 §5 X1 thật; không tái lập độc lập do harness từ chối; CLI lệch #2 Q9 | Kiểm cuối FAIL; fallback PASS (lệch, chờ duyệt), không đạt nguyên bản |
| Q-J | Source/ECC diff leader rỗng; sai isolation/model/side effect; Git độc lập bị chặn; lệch #1 Q10 | Kiểm cuối FAIL; fallback PASS (lệch, chờ duyệt), không đạt nguyên bản |
| QC-F1 | Hai lượt đạt134module/failed0; 435.42s và434.79s; ledger2/2, radius misses0 | PASS hai lượt, không chạy lượt3 |
| QC-F2 | Vung-cham0/134module; nguồn/semantic do reviewers và kiểm cuối đọc | PASS phần kiểm tài liệu; unit coverage KHÔNG ÁP DỤNG |
| QC-F3 | Spec §5 đối chiếu §5; leader diff thật đã có, Git kiểm cuối bị chặn | PASS theo evidence leader, giới hạn độc lập thuộc lệch #1; kiểm cuối CHỜ diff độc lập |
| QC-F4 | Không sửa code | KHÔNG ÁP DỤNG |

## 2. Bằng chứng đã chạy

- T1.1 đỏ thực: doc_lint O1 chưa tồn tại → exit2 not found, không unit test giả. X1 16:53:18 Windows Python3.13.15: ordered/reversed/missing/green-only đúng oracle; empty/malformed `LoiThieuSo`, null/[] `AttributeError` là hạn chế chưa vá; temp state CLI exit0; startup không anchor, compact có anchor/details, cả hai exit0. Driver/input/output tại O1 §5, timeout30 mỗi con/120 toàn driver; không model/API/ECC execution.
- T1.1 xanh 16:57:35: doc_lint O1 0 violations; 16:57:36 vung-cham files1 modules0/134 fallback none okTrue seconds0.5. Đã tick ngay trước bắt đầu T2.1.
- T2.1 đỏ thực: doc_lint O2 chưa tồn tại → exit2 not found. Xanh17:01:31 lint0; 17:01:32 vung-cham files1 modules0/134 fallback none okTrue seconds0.5. Đã tick trước T3.1.
- Hash/source delta/git status và worktree list tại O1 §1. Source từ snapshot H1 đến HEAD không đổi trong hooks/scripts/tests/skills/agents; số H1 không được gọi phép đo mới.
- **QC-F1 mới**: background `python3 scripts/tdq_test.py tron-bo --silent`, khởi17:02:33, xong17:09:48, exit0. Output quyết định: `tron-bo modules=134 failed=0 missed=0 ok=True seconds=435.42`; `[TDQ:TEST] PASS — full suite (134 modules) passed in 435.42s.` Chế độ silent không in số testcase/skip, vì thế không nhập 2602/9 của request cũ làm kết quả mới. Không kết luận skip=0. Ledger17:11:33 `full-suite runs: 1 of budget 2`, `radius misses: 0`. Ledger lưu phase implement do command bắt đầu trước finish chuyển qc, nhưng đây là lượt QC-F1 đã chỉ định, không có lượt implement completion suite riêng. Các thông điệp lỗi/CHƯA ĐẠT trong log fixture không phải verdict suite fail; verdict runner/exit0 mới quyết định.
- **QC1.3 source findings**: reviewer nguồn Q-A PASS có hai citation nhỏ cần sửa, Q-B FAIL do bỏ sót real-run eval macOS Keychain; Q-C PASS. Leader xác minh `tdq_eval.py:679-689,883-899`, `context-profile-store.js:181-198,225-238`, đã sửa O1/O2 gap auth Windows/offline-vs-run, owner U03→U11 và phần auth ngoài estimate; sửa citation descriptor vs enforce và PreCompact call/ghi summary. Lint3 file17:11:33=0, vùng chạm2 file0module17:11:34; reviewer nguồn đã tái kiểm Q-A/Q-B PASS; MEDIUM gap Windows và hai LOW citation đã đóng. Q-C PASS từ lượt đầu. QC1.3 tick sau lint/vùng chạm đạt; không còn finding nguồn mở trong phạm vi kiểm.
- Git worktree list17:11:34 sau research/reviewer nguồn kết thúc chỉ còn repo chính và worktree định lượng có untracked pyrightconfig. Temp worktree test và worktree reviewer khác không còn trong list; không chạy prune/remove. Spec hash khớp, source/ECC không bị sửa. QC1.1 đạt phần ghi hồ sơ/kiểm nguồn, lịch sử thao tác vẫn lệch #1.

## 3. Phản biện, sai thao tác và xử lý

Hai research digest chỉ làm chỉ mục; O1 §4 ghi các claim sai bị bác trước O2. Ba reviewer phân chiều đã kiểm độc lập nguồn, thiết kế/an toàn và định lượng/roadmap; kiểm cuối đã trả verdict tại §4. Các đoạn thời điểm trước dưới đây là lịch sử, không phải tác vụ còn chạy.

**Sai thao tác phải công khai:** lời gọi khảo sát trước và cả ba lời gọi reviewer QC đã truyền `isolation=worktree` thừa dù plan cấm; QC còn override `model=opus` thay vì để inherit. Không coi đây là người dùng cấp quyền worktree/model hoặc sự tuân thủ đúng hợp đồng. Đã gửi yêu cầu chỉ đọc absolute repo chính, không dùng cwd snapshot, không ghi/merge/switch và ghi giới hạn. Worktree khảo sát đã tự dọn theo git list trước QC; worktree QC cần xác minh sau khi agent kết thúc, không force delete. Không thể sửa quá khứ lời gọi; sẽ ghi lệch Q-J qua CLI, giữ evidence và khắc phục vùng nguồn/quyền ghi, không che bằng PASS tuyệt đối. Lời gọi kiểm cuối cũng **đã lặp sai isolation/model override**, dù prompt nói không; đã gửi yêu cầu absolute-source/no-write ngay. Vì vậy không tuyên bố cơ chế lời gọi đã được sửa; deviation #1 bao gồm cả kiểm cuối. Không có lý do từ user cho các override này. Kiểm cuối không được LSP/setup/ghi/agent con và không tái lập lệnh đã bị từ chối.

Reviewer thiết kế/an toàn đã trả Q-D PASS, Q-F PASS, Q-J FAIL quy trình; không thấy finding thiết kế khác. Finding MEDIUM tại plan:28/91: isolation tạo worktree sai snapshot (worktree HEAD `6ddd1a408197db87ea675942362558fd34f76375`, repo chính `1d78ca86ca5b0710f357d8436ec7d9d2d7562b54`), nhưng reviewer xác nhận chỉ đọc absolute repo chính. Finding LOW tại plan:98: override opus trái inherit, không suy chất lượng từ model. Lịch sử state/log chỉ được kiểm qua evidence CLI có trong phiên, không có audit host đầy đủ.

Đã mở **QC1.1** trước sửa, ghi thêm sự cố QC hiện tại vào O1 §1, giữ FAIL lịch sử này. CLI `lech add --q Q-J` bị từ chối vì chỉ nhận Q số; gọi lại `--q Q10` (DoD thứ 10, ánh xạ Q-J) thành công17:03:35: `id=1 q=Q10 trang_thai=cho`. Chưa có lời người dùng duyệt lệch. Giải pháp bảo toàn evidence/source, không sửa source, không xóa cưỡng bức worktree, yêu cầu kiểm cuối không isolation/override. Reviewer thiết kế tái kiểm QC1.1 PASS phần ghi hồ sơ, không xóa Q-J FAIL lịch sử. Reviewer định lượng còn phát hiện side effect LSP khởi động nhầm cwd worktree, tạo untracked `.claude/worktrees/agent-adf3b8806d259eb5d/pyrightconfig.json`; worktree này được giữ, không xóa/sửa để che dấu, không tự force cleanup. Đây là bổ sung phạm vi deviation #1, không phải source repo chính được phép sửa. Leader đã đọc target: include scripts, pythonVersion3.11, basic, thiếu import warnings tắt; file này chỉ ở worktree agent-adf…, không thay pyrightconfig repo chính. Không xóa vì không có quyền cleanup phá hủy ngoài output hiện tại. Git list cuối còn chờ agent nguồn kết thúc.

**QC1.2 / finding định lượng MEDIUM:** Q-E FAIL lịch sử: O2 dòng tổng P0 ghi 3.5+6+6.5 dù bảng là U01 2/3/3, U02 .5/.5/1, U03 1/2/3. Đã mở QC1.2 rồi sửa thành **3.5+5.5+7=16h**; tổng P0 8/16/32h không đổi. Reviewer tính lại medians/p95/model và 13 phân rã đúng; Q-F PASS. Reviewer đã tái kiểm trực tiếp dòng sửa: Q-E PASS trong phạm vi kiểm, Q-F PASS; F1 đóng. 17:06:57 lint hai tài liệu 0 violations và vung-cham0/134 module, không unit coverage; QC1.2 tick ngay sau đạt.

**Giới hạn Q-I quan trọng:** reviewer định lượng đối chiếu tĩnh driver/source và thấy oracle phù hợp, nhưng harness đã từ chối lệnh tái lập scorer trước thực thi. Không có output smoke mới của reviewer. Không yêu cầu agent khác/leader chạy lại cùng thao tác bị chặn để lách permission. X1 của leader16:53 vẫn là lần thực thi thật đã có, không biến thành independent rerun. Kiểm cuối chỉ được kiểm evidence/source và báo giới hạn; CLI17:06:56 đã ghi deviation **#2 Q9 ánh xạ Q-I**, trạng thái chờ người dùng, không ghi PASS đầy đủ giả.

Git worktree list17:07: repo chính HEAD1d78ca8; reviewer nguồn còn chạy ở worktree locked; reviewer định lượng worktree6ddd1a4 giữ untracked pyrightconfig; thêm temp `tmp2gs1stcz/nhanh/lai` f620094 prunable xuất hiện trong khi suite đang chạy (các test eval có fixture worktree), chưa kết luận orphan nguồn nào trước khi suite xong. Không prune/remove. Source/config repo chính diff rỗng, ECC status rỗng.

## 4. Kiểm cuối độc lập

Agent `tdq-workflow:tdq-qc-tester` khác tác giả/digest/ba reviewer đã đọc artifact/source và tính lại bằng stdlib. **Verdict nguyên bản: FAIL Q-I/Q-J; CHỜ Q-H/QC-F1/QC-F3**. Không biến verdict này thành PASS tuyệt đối. Q-A/B/C/D/E/F/G PASS; QC-F2 PASS phần chứng cứ vùng tài liệu, không code coverage; QC-F4 N/A. Lint tự kiểm0; 13/13 phân rã đúng, P0=3.5+5.5+7. QC1.2/QC1.3 đã được xác nhận sửa đúng.

Hai MEDIUM còn lại trùng lệch #1/#2, không phải finding nội dung báo cáo mới: isolation/model/side effect và thiếu independent rerun. Reviewer không chạy lại lệnh bị từ chối. Lệnh Git của kiểm cuối cũng bị harness chặn, nên chưa có diff độc lập; sử dụng output Git thật leader đã có (17:11/17:15), **không chạy lại hoặc nhờ agent khác để né chặn**, giữ giới hạn này trong Q-J/QC-F3 và lệch #1. Không coi sha256sum khớp spec là chứng minh toàn bộ working tree sạch.

Kiểm cuối đọc suite1 đạt nhưng không poll suite2. Leader nhận notification task `bethughw5` completed exit0 và đọc output: 17:19:57 `tron-bo modules=134 failed=0 missed=0 ok=True seconds=434.79`, `[TDQ:TEST] PASS — full suite (134 modules) passed in 434.79s.` Q-H/F1 được cập nhật bằng evidence này, không gọi là tester tự chạy lại. Ledger17:22:34: `full-suite runs: 2 of budget 2`, `radius misses: 0`. Việc bổ sung evidence chờ khác với tự bác finding FAIL. Chưa có người dùng duyệt hai lệch. Log `.tdq-test.log` đã đọc có NUL và dòng2602/skipped9 nhưng bị vùng-chạm mở lại trong lúc suite chạy; không dùng nó làm thống kê mới đáng tin hoặc kết luận skip0; giữ số module/failed/exit từ output riêng của task.

## 5. Đối chiếu ràng buộc kiến trúc (QC-F3)

| Ràng buộc spec §5 | Bằng chứng hiện tại |
|---|---|
| hooks gọi scripts, không import ngược | Source không diff; O2 U11 cấm import hooks vào scripts; driver khảo sát không là runtime mới |
| skills nhắc CLI, không chép implementation | Không sửa skill; O1 driver trong hồ sơ đo, không chép vào skill |
| State chỉ qua tdq_state.py | CLI approve/set/lech/finish của leader có output trong phiên; temp state X1 qua set CLI; không tuyên bố audit host toàn lịch sử |
| Hook không deny vì chưa duyệt | Không đổi hook; U01 tách nhắc/CLI approval, U05 unknown không được biến thành nới quyền |
| Hai cổng suite | QC-F1 và sau sửa cuối đều đạt; ledger2/2, radius misses0; reviewer không tự chạy suite, không thêm lượt3 |
| QC do user chọn | `tdq_state.py get muc_qc` = ultra; mode = main; không giảm do docs |
| ECC/source/spec giữ nguyên | ECC status rỗng, source/config diff rỗng; body spec hash khớp; graph dirty là phát sinh tìm kiếm được giữ riêng |

## 6. Lệch spec chờ người dùng quyết định

- **#1 — Q10 = Q-J:** ngưỡng không worktree/inherit; đo được isolation/model sai ở khảo sát, ba reviewer **và kiểm cuối**, một worktree LSP tạo pyrightconfig. Phương án thực áp: giữ hồ sơ FAIL, source absolute, kiểm diff và không force cleanup. Dòng `chon` CLI #1 từng ghi dự định “kiểm cuối bỏ isolation/model” nhưng thực tế **không đạt**; O3/report bổ sung sự thật này, không trình dự định làm kết quả. Chưa có duyệt. Không thêm deviation trùng chỉ để che bản ghi trước.
- **#2 — Q9 = Q-I:** thiếu tái lập scorer độc lập do harness từ chối; dùng evidence X1 thật + đối chiếu source/oracle, không né quyền. Chưa có duyệt.

Theo qc.md:200, leader ghi fallback là **PASS (lệch, chờ duyệt)** để kết thúc nghiên cứu và trình quyết định; kiểm cuối vẫn trả **FAIL Q-I/Q-J** theo tiêu chí nguyên bản. Hai verdict phải giữ song song: không có nghĩa đạt điều kiện nguyên bản hoặc user đã đồng ý. User bác lệch thì mở fix/kiểm phù hợp, không tự duyệt #1/#2 bằng notification.

## 7. Giới hạn và kết luận hiện tại

- Đã hoàn thiện hồ sơ QC để trình quyết định: Q-A–Q-G PASS độc lập; Q-H PASS theo suite/lint thật được leader bổ sung; Q-I/Q-J FAIL nguyên bản, fallback PASS (lệch, chờ duyệt). QC-F1/F2 đạt trong phạm vi nêu trên; F3 còn giới hạn diff độc lập thuộc #1; F4 N/A. Không có quyền tuyên bố ultra sạch hoàn toàn hoặc tự commit. Spec body SHA-256 kiểm mới: `334f59a02898505b64c248956ca7058f90c13919e1ba3f442ecd9586e3ded400`, khớp bản đã duyệt; O1/O2/O3 tồn tại thật.
- 17:05:08 sau QC1.1: lint ba artifact 0 violations; vung-cham files3 modules0/134 fallback none okTrue seconds0.51; diff --check không lỗi whitespace (Git cảnh báo CRLF metadata đã có). Reviewer thiết kế tái kiểm QC1.1 PASS phần ghi hồ sơ, Q-J vẫn FAIL lịch sử. Kiểm cuối sẽ dùng lệch #1 chưa duyệt, không biến thành tuân thủ tuyệt đối.
- 0 module vùng tài liệu không là PASS code coverage; semantic phải kiểm nguồn thật.
- Không chạy eval model thật/transcript cá nhân/ECC code; Mac/Linux xử lý sau, chưa kiểm.
- Lỗi runtime có từ trước chỉ là evidence, không vá trong request tài liệu.
- 17:17:12 lint cả sáu hồ sơ brief/spec/plan/O1/O2/O3: 0 violations, R14=0 findings. Không sửa spec để làm QC xanh. Ledger silent chỉ ghi module/failed/seconds, `.tdq-test.log` được runner mở lại mỗi lượt/vùng chạm nên không dùng log bị ghi đè suy số testcase/skip; giữ giới hạn thống kê thay vì dùng số lịch sử.
