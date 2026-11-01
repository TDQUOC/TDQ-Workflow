# Checkpoint sau xác nhận đã dừng — 2026-10-31
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Request `2026-10-27-1846-kiem-chung-tang-toc`, nhánh `bugfix/kiem-chung-tang-toc`, lane full, phase implement, mode subagent, QC ultra. Người dùng đã xác nhận “đã dừng”. Tiến độ hiện tại **20/25**, task đang làm **T5.3**; D1–D8 đã PASS và tick, D9–D12 chưa được chứng nhận.

## Kết quả đã chứng nhận

- Source không đổi so với QC2.1 parent: `aa8c7875bdad62957e0ef14287d490dfd3b4add9dce85e3488e22935fd75a5a8`. Master Architecture current, team audit 0 vấn đề, đã resume qua CLI. Không sửa source trong lượt này.
- **T5.1 Full fresh PASS**: 3601 case, **3593 pass, 8 skip, 0 fail/error**. Wall1196.1738528s, execute1189.7622809s, collection2.5681402s, verify2.5366852s. Harness và child exit0, config/source/dependency guard và cleanup PASS. [Receipt](runs/QC-F1-after-writers-stopped-20261031-dd68c0bd37a142bb9f89d1eef8ba3609/receipt.json).
- **D1–D8 PASS** bằng verifier semantic, không chạy thêm Full: [output checks](dod-checks-current.json), [index v2](evidence-index.json). Cả3306 case gốc còn, không remap, tăng295case. Mọi skip có reason và capability. Lượt này chứng nhận source sau QC2.1; các lượt FAIL trước vẫn giữ nguyên.
- **T5.2 runtime PASS6/6**: process-timeout3.44s, process-cancel0.66s, join6.25s, owner-crash6.25s, freshness6.09s, transcript0.37s; mọi scenario dưới120s, outer cleanup true. Heartbeat con ngừng sau timeout/cancel; hai caller thực thi đúng1job; actions fresh/reused/fresh và warm transcript được kiểm. [Runtime JSON](runtime.json), [receipt](runs/runtime-after-writers-stopped-20261031-0698bde3870643258b86f9929d6a83d2/receipt.json). Verifier runtime valid, nguồn khớp Full; chưa thay thế QC độc lập/D11.

## Benchmark bị ngắt vì môi trường thay đổi

Chạy CLI full-pairs thật với3cặp, workers1/2, reuseoff; thứ tự dự kiến1–2,2–1,1–2. Không có agent hoặc test khác do leader chạy đồng thời.

- Sample1 (1worker) wall1179.7468935s, outcomes3593pass/8skip. Runner trả **INCOMPLETE**, không PASS: `docs/tdq/.tdq-turn.jsonl` thay đổi trong job. Không dùng sample này suy ra tốc độ hoặc cho D9 đạt.
- Ledger có dòng mới: `SessionStart`19:05:20+07, source startup, code TDQ:GON, session `779a2d50-142a-43f4-9792-ebbee180a3a8`.
- Harness còn phát hiện hai cấu hình thật đổi digest: `.claude/CLAUDE.md`, `.claude.json`. Không có source/dependency guard failure; cleanup complete. Không sửa, khóa hay hoàn nguyên các file đó.
- Sau khi biết sample1 không còn đủ điều kiện, leader xác minh đúng harness và parent/command của benchmark child rồi dừng **chỉ child PID43260, parent59164**. Harness còn sống để đóng Windows Job Object, dọn cây con và lưu receipt FAIL; child/harness code-1 là dừng chủ động, không gọi là timeout hoặc test failure. Không dừng phiên người dùng.
- [Receipt FAIL đã seal](runs/benchmark-full-after-writers-stopped-20261031-5ed8df791a8c45e2a2376e6d27d5eea1/receipt.json), [diagnostic](benchmark-interruption-20261031.json), [partial report lưu riêng](benchmark-full.interrupted-20261031-1905.json), [sample JSONL](benchmark-full.interrupted-20261031-1905.samples.jsonl). Giữ cả partial report gốc và raw samples; không biến INCOMPLETE thành PASS.

## Khoanh vùng phiên mới

Quan sát tiến trình chỉ đọc sau khi ngắt benchmark: `claude.exe` PID20356, mở19:05:19.628464+07, executable từ VS Code extension `anthropic.claude-code-2.1.314-win32-x64`. Parent là Code.exe PID32544, mở19:05:15.043737+07. Thời điểm sát SessionStart19:05:20; đây là tương quan, **chưa chứng minh PID20356 ghi cả hai cấu hình**. Không đọc hoặc lưu nội dung cấu hình/secret, không sửa hay dừng tiến trình này.

## Điều kiện và bước tiếp tục

Đã pause `mat-truy-cap` bằng state CLI. Cần dừng nguồn ghi config/ledger trong toàn cửa sổ benchmark, đặc biệt kiểm phiên Claude Code mới trong VS Code nêu trên và các phiên chạy setup TDQ. Một khoảng yên tĩnh ngắn hoặc sample pytest xanh không thay thế guard.

Khi người dùng xác nhận: kiểm source, receipt và projection đối chiếu chéo trước khi bắt đầu lại **T5.3**. Không chỉ xét code hoặc SHA của harness: fingerprint sản phẩm của Full chứa `docs/workinglog/2026-10-31.md`, trong khi `_comparison_exclusions` hiện chỉ loại ngày mở request2026-10-27. Lệnh finish cuối lượt sẽ cập nhật workinglog ngày31. Vì vậy phải kiểm toàn bộ identity giữa Full và input benchmark mới trước, và chứng nhận Full mới nếu input chưa tương đương theo hợp đồng; không tự loại thêm input hoặc nới per-job guard. Tránh chạy đủ sáu sample rồi mới biết source không khớp.

Bản partial đã lưu riêng, sáu sample mới vẫn phải đủ và chạy tuần tự. Sau đó T5.4 cache-pairs (tách fixture/log thật), T5.5 QC độc lập, D9–D12 và report MD/HTML desktop/mobile. Giữ mặc định1worker, reuse/readiness/transcript off cho tới khi đủ bằng chứng.

Không commit, Git merge, push, đổi nhánh, xóa worktree, nới guard hoặc cập nhật plugin đã cài trong lượt này.
