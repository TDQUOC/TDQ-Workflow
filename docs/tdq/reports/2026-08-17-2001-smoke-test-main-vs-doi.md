# REPORT — Smoke test có số: mode main so với mode đội (`2026-08-17-2001-smoke-test-main-vs-doi` · lane full · mode main · 20 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1–P3 dựng `scripts/tdq_bench.py` (4 lệnh con: `dung-plan`, `thuc-do`, `mo-phong`, `quet`) dùng lại đúng `tdq_team.doc_plan`/`quyet_dinh_task`/`chia_dot` chứ không chép luật · P4 chạy THẬT một đợt 3 agent `tdq-implementer` trong repo git tạm để lấy hằng số · P5 viết file kết quả trả lời hai câu user hỏi · P6 QC 13 hạng mục + 2 vòng agent QC độc lập + 1 vòng fix.

**Kết quả:** mode đội đo được **2,4 phút** trên 3 task rời nhau; mode main **6,1 phút** là số SUY RA (main chưa hề chạy bài thi này) · ngưỡng hoàn vốn của mode đội **10%** số task tách được nếu agent con nhanh ngang leader, **40%** nếu agent con chậm gấp rưỡi, **60%** nếu chậm gấp đôi — con số nên dùng để quyết định là **30–60%**, không phải 10% · plan không tách được (6 task cùng một file) thì đội THUA: 12,3 so với 12,2 phút · chất lượng hoà (0 xung đột, 0 task làm lại ở cả hai mode), khác biệt thật là lượt chạy đội lộ ra 2 defect mà 839 unit test không bắt được.

**Kiểm:** `python3 -m pytest tests/ -q` → `874 passed, 416 subtests` (trước request: 839) · `pytest tests/test_bench.py -q` → 34 test · `doc_lint` exit 0 trên spec, plan, file kết quả · QC 13/13 hạng mục PASS, agent QC độc lập vòng 1 FAIL (11/12, hỏng Q8) → vòng fix 1 vá 8 defect → agent thứ hai chấm lại 14/14 PASS · repo thật không mọc nhánh hay worktree nào (`git worktree list` và `git branch --list "tdq/*"` giống hệt trước sau).

**Đầu ra:** `docs/tdq/bench/2026-08-17-2001-smoke-test-main-vs-doi-ket-qua.md` (kết luận) · `scripts/tdq_bench.py` + `tests/test_bench.py` (công cụ tái dùng) · `docs/tdq/bench/2026-08-17-2001-smoke-test-main-vs-doi-thuc-do.json` (hằng số, ghi rõ `nguon` và `cach_do` từng số) · `docs/tdq/qc/2026-08-17-2001-smoke-test-main-vs-doi.md`.

**Giới hạn:** `t_phat` mới đo phần cơ học 0,45 giây, CHƯA gồm thời gian leader viết prompt cho từng agent — phần đắt nhất của việc phát đợt; đó là lý do mọi ngưỡng đều nên đọc kèm bảng độ nhạy ở mục 5 file kết quả · mode main chưa chạy lượt thật nào, số 6,1 phút là suy ra · defect "hook `edit_gate` chặn agent con sửa file trong repo tạm" đã ghi nhận nhưng CHƯA vá, để lại cho request sau · một sửa ngoài phạm vi đã làm vì lượt chạy thật bắt được: `tdq_team._git` đọc output git với `errors="replace"`.

**Git:** chưa commit gì. Không có commit gỡ chặn nào trong request này. Nhánh `tdq-doi-ten-mode-implement` vẫn giữ 2 commit chưa push của request trước.

## Thời gian

| Phase | Treo tường | Model chạy | Số lần vào |
|---|---|---|---|
| idle | 1 giây | 0 giây | 1 |
| analyze | 4 phút | 3 phút | 1 |
| spec | 9 phút | 3 phút | 1 |
| plan | 4 phút | 4 phút | 1 |
| implement | 20 phút | 20 phút | 1 |
| qc | 31 phút | 31 phút | 1 |
| report | 5 giây | 0 giây | 1 |
| **Tổng** | **1 giờ 08 phút** | **1 giờ 02 phút** | |
