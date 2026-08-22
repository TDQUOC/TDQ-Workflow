# QC — Quản lý vòng đời worktree của workflow

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Ngày: 2026-08-22 · Spec: ../spec/2026-08-22-1033-quan-ly-worktree.md · Plan: ../plan/2026-08-22-1033-quan-ly-worktree.md
Số hạng mục: 20 (Q1–Q20 ở §6 spec) · Vòng fix đã chạy: 3/3
QC độc lập vòng 2 (bằng chứng đầy đủ): ./2026-08-22-1033-quan-ly-worktree-vong2.md

## Mục lục

- Kết quả từng hạng mục
- Vòng fix 1 — 10 khiếm khuyết QC độc lập bắt được
- Vòng fix 2 — 5 khiếm khuyết QC vòng 2 bắt được
- Vòng fix 3 — nhãn lý do cho lời từ chối của git
- Lệch spec đã ghi nhận
- Kết luận

## Kết quả từng hạng mục

| # | Kết quả | Bằng chứng |
|---|---|---|
| Q1 | PASS | `pytest tests/test_worktree_registry.py -q -k "schema or hong or render"` → `15 passed, 6 deselected` |
| Q2 | PASS | cùng lệnh trên (nhóm `hong`); thêm `pytest tests/test_team_mode.py -q -k so_hong` → `2 passed`: sổ hỏng thì `mo`/`soat` không văng traceback, không đẻ worktree mồ côi |
| Q3 | PASS | nhóm `render` của lệnh Q1 — sinh hai lần cho ra hai chuỗi giống nhau từng byte |
| Q4 | PASS | `pytest tests/test_team_mode.py -q -k mo_ghi_so` → `1 passed, 137 deselected` |
| Q5 | PASS | `pytest tests/test_team_mode.py -q -k "hop_"` → `11 passed, 127 deselected` (gồm `hop_don_khi_sach`) |
| Q6 | PASS | cùng lệnh Q5 — ca bẩn giữ nguyên worktree, dòng sổ vẫn `mo` |
| Q7 | PASS | cùng lệnh Q5 — ca chưa merge không xoá nhánh, không xoá worktree |
| Q8 | PASS | `pytest tests/test_team_mode.py -q -k soat` → `11 passed, 127 deselected`; bảng in đủ 7 cột (thêm Task, Request ngoài 5 cột spec đòi) |
| Q9 | PASS | cùng lệnh Q8 — worktree ngoài `.tdq-worktrees/` chỉ nằm ở mục "Out of scope", còn nguyên sau `soat --don` |
| Q10 | PASS | cùng lệnh Q8 — cảnh báo in kèm số MB và số ngày thật, ngưỡng 500 MB / 7 ngày |
| Q11 | PASS | `pytest tests/test_state.py -q -k chan_worktree` → `5 passed, 45 deselected` |
| Q12 | PASS | cùng lệnh Q11 — sổ trống/thiếu/hỏng đều không chặn |
| Q13 | PASS | `pytest tests/test_context_hooks.py -q -k worktree` → `4 passed, 24 deselected` |
| Q14 | PASS | cùng lệnh Q13 — sổ hỏng/thiếu thì hook im lặng, thoát 0 |
| Q15 | PASS | `python3 scripts/tdq_team.py --help` liệt kê `{phan-cong,kiem-ke,cum,mo,kiem,hop,soat,don}` = 8 lệnh; `python3 scripts/tdq_state.py` in usage đủ 7 lệnh `next/get/init/set/approve/reset/phases-doc` |
| Q16 | PASS | `python3 -m pytest tests/ -q` → `37 failed, 1253 passed, 1448 subtests passed in 102.30s`, toàn bộ 37 đỏ thuộc `tests/test_skill_router.py` — đúng mốc nền |
| Q17 | PASS | `build_portable.py` → `85 file(s) in portable_claude`, `130 file(s) in portable_codex`; `tdq_checkportable.py check` cho cả hai → `CLEAN`. Skill có mục `## The worktree ledger`, `grep -c soat team-mode.md` = 6 |
| Q18 | PASS | `doc_lint.py <spec> <plan>` → `0 violation(s) total, exit 0` |
| Q19 | PASS | `pytest tests/test_worktree_registry.py -q -k "goi_y or ly_do"` → `3 passed, 4 subtests passed`; 4 lý do đóng, mỗi lý do ≥ 1 phương án kèm lệnh, lý do lạ ném `LoiSo` |
| Q20 | PASS | cùng lệnh Q19 + `pytest tests/test_team_mode.py -q -k "don_khong_xoa or gitignore"`: khối `NOT CLEANED UP YET` in cuối kết quả lệnh, dọn sạch thì không in |

## Vòng fix 1 — 10 khiếm khuyết QC độc lập bắt được

Agent QC vòng 1 trả `FAIL` ở Q2 kèm 9 khiếm khuyết ngoài bảng DoD. Toàn bộ đã sửa, ghi ở
mục `## QC` của plan (F1–F10):

| # | Mức | Nội dung | Sửa bằng |
|---|---|---|---|
| F1 | nặng-vừa | Sổ hỏng làm `mo`/`hop` văng traceback, và `mo` tạo worktree TRƯỚC khi biết ghi được sổ → worktree mồ côi | `kiem_ghi_duoc()` gọi trước `git worktree add`; `main()` bắt `LoiSo` |
| F2 | vừa | Dòng sổ thiếu `duong_dan` ném KeyError → kẹt cổng qc vĩnh viễn | đóng dòng với lý do `thieu-duong-dan` |
| F3 | vừa | Worktree `tich-hop` không có dòng sổ nên không ai dọn | liệt kê "In scope, no ledger row", `--don` gỡ thư mục, giữ nhánh |
| F4 | vừa | `git worktree remove` xoá cả file bị gitignore (`.env` mất hẳn) | `git status --porcelain --ignored=matching` + danh sách rác sinh lại được; bỏ `--force` |
| F5 | nhẹ | `soat` luôn trả 0 kể cả còn worktree bẩn | trả 1 khi còn lý do `ban`; `hop` vẫn trả 0 sau merge |
| F6 | nhẹ | Tên test không khớp `-k` trong DoD | đổi tên test |
| F7 | nhẹ | Không `prune` sau khi đóng dòng có thư mục đã biến mất | thêm `git worktree prune` |
| F8 | nhẹ | Lệnh `don` cũ vẫn xoá worktree còn việc | bỏ qua worktree bẩn + in khối gợi ý |
| F9 | nhẹ | `worktrees.json/.md` không gitignore → commit đường dẫn tuyệt đối máy user | thêm 2 dòng vào `.gitignore` |
| F10 | mâu thuẫn i18n | Skill bắt chép khối `NOT CLEANED UP YET` NGUYÊN VĂN tiếng Anh, trái `user-facing-block.md:7` | đổi luật: dịch khối sang `doc_lang`, lệnh giữ nguyên văn |

Test hồi quy khoá 10 ca này: lớp `VaLuoiWorktreeTest` trong `tests/test_team_mode.py`
(7 test) + `ChanWorktreeTest` + `TestNhacWorktree`.

## Vòng fix 2 — 5 khiếm khuyết QC vòng 2 bắt được

Agent QC vòng 2 trả `VERDICT: PASS` — Q1–Q20 xanh hết và F1–F10 sửa thật — nhưng bắt thêm
5 khiếm khuyết nằm NGOÀI bảng DoD. KM-1 và KM-2 chạm đúng cam kết spec §5 "worktree bị
chặn luôn có phương án gỡ được", nên vào vòng fix 2 (F11–F14). KM-5 chỉ ghi nhận.

| # | Mức | Nội dung | Sửa bằng |
|---|---|---|---|
| KM-1 | nặng-vừa | Worktree bị `git worktree lock` mà không có dòng sổ làm `soat --don` và `don` ném `LoiLuat` giữa vòng lặp → mất luôn khối gợi ý của các worktree bẩn đã phát hiện | `_go_thu_muc()` chạy `worktree remove` với `check=False`; git từ chối thì thành một dòng lý do `khoa` trong khối, lượt quét chạy tiếp (F11) |
| KM-2 | vừa | Rác ignored ngoài `RAC_SINH_LAI` (`build/`, `*.log`, `.coverage`) khoá cứng worktree; bị gọi nhầm là "uncommitted changes" và cả 2 phương án gợi ý đều vô hiệu (`git add -A` không add file ignored, `git clean -fd` thiếu `-x`) → vòng chết rc=1 | lý do chặn riêng `bo-qua` với 3 phương án, trong đó `git -C <wt> clean -fdx && soat --don` gỡ được thật; `_file_ban()` không trộn file ignored nữa; `soat` trả 1 cho cả `ban` lẫn `bo-qua` (F12) |
| KM-3 | nhẹ | Worktree trong tầm không có dòng sổ chỉ bị kiểm 1/3 điều kiện (bỏ khoá và chưa-merge) | `_ly_do_chan_thu_muc()` (khoá · bẩn · rác ignored) dùng chung cho nhánh dòng-lạ và cho `don`; `_ly_do_chan()` = hàm đó cộng điều kiện đã-merge (F13) |
| KM-4 | nhẹ | `unittest.main()` nằm TRƯỚC 3 lớp test mới → `python3 tests/test_team_mode.py` bỏ im lặng 25 test | chuyển xuống cuối file; nay cả hai đường chạy đều báo 142 test (F14) |
| KM-5 | nhẹ (ghi nhận) | `soat --don` gỡ worktree `tich-hop` giữa sóng, `_bao_dam_tich_hop` dựng lại nên `hop` kế tiếp vẫn rc=0 | không sửa — chỉ là churn, không mất việc, không đỏ hạng mục Q nào |

Ba câu săn khiếm khuyết agent trả lời: (a) bỏ `--force` CÓ kẹt đúng một ca = KM-1, đã sửa;
(b) `soat` trả 1 KHÔNG phá vòng lặp sóng — không script/hook nào đọc mã thoát của `soat`,
`team-mode.md` chỉ đòi exit 0 cho `kiem-ke`; (c) `--ignored=matching` CÓ chặn nhầm rác sinh
lại được = KM-2, đã sửa.

Test hồi quy khoá 4 ca: `test_worktree_bi_khoa_khong_lam_chet_ca_luot_soat`,
`test_worktree_bi_khoa_khong_lam_chet_don`,
`test_rac_ignored_la_ly_do_rieng_va_phuong_an_go_duoc_that` (chạy đúng lệnh gợi ý in ra rồi
kiểm lại, để phương án không bao giờ là lời hứa suông),
`test_worktree_khong_co_dong_so_van_bi_kiem_du_dieu_kien`.

Số đo sau vòng fix 2: `pytest tests/test_team_mode.py -q` → `142 passed, 21 subtests`;
`python3 tests/test_team_mode.py` → `Ran 142 tests OK`; `pytest tests/test_state.py
tests/test_context_hooks.py tests/test_worktree_registry.py -q` → `99 passed, 24 subtests`;
full suite → `37 failed, 1257 passed, 1452 subtests` (đúng mốc nền); portable → `CLEAN 85`
+ `CLEAN 130`; i18n_check ba kind → 0 dòng.

## Vòng fix 3 — nhãn lý do cho lời từ chối của git

QC vòng 2 probe lại đúng 4 ca repro của vòng 1 và xác nhận KM-1…KM-4 sửa thật:
worktree bị `lock` cho `rc=1` kèm `reason: git has this worktree locked` thay vì chết giữa
lượt · `git worktree unlock` rồi `soat --don` cho `cleaned: T1.1` · `build/out.o` +
`test.log` cho `reason: ignored files here do not regenerate…`, chạy đúng phương án
`git clean -fdx` rồi quét lại cho `rc=0, cleaned: T1.1` — hết vòng chết · `_file_ban` hết
trộn file ignored · dòng lạ bẩn/ignored được GIỮ, dòng lạ chưa merge chỉ mất thư mục còn
commit `7115cf2` vẫn truy được · `python3 tests/test_team_mode.py` khớp `pytest` ở 142 test.

Khiếm khuyết mới duy nhất, mức nhẹ:

| # | Mức | Nội dung | Sửa bằng |
|---|---|---|---|
| KM-6 | nhẹ | Mọi lời từ chối của git bị dán nhãn `khoa`, kể cả lỗi quyền — `chmod 0500` thư mục cha cho `reason: git has this worktree locked (Permission denied)`, phương án `worktree unlock` không gỡ nổi | lý do mới `git-tu-choi` in nguyên văn câu git kèm phương án đúng; `_ly_do_tu_choi()` chỉ chọn nhãn `khoa` khi `_khoa_khong()` xác nhận worktree thật sự bị lock (F15) |

Test hồi quy: `test_git_tu_choi_khong_phai_khoa_thi_khong_dan_nhan_khoa` (dựng đúng ca
`chmod 0500` của agent) và `test_worktree_khoa_that_van_giu_nhan_khoa` (nhãn `khoa` không bị
mất khi lock thật).

Số đo sau vòng fix 3: `pytest tests/test_team_mode.py -q` → `144 passed, 21 subtests`;
`python3 tests/test_team_mode.py` → `Ran 144 tests OK`; `pytest tests/test_worktree_registry.py
-q` → `21 passed, 18 subtests`; full suite → `37 failed, 1259 passed, 1455 subtests` (đúng mốc
nền); portable → `CLEAN 85` + `CLEAN 130`; i18n_check ba kind → 0 dòng.

## Lệch spec đã ghi nhận

`docs/tdq/worktrees.md` sinh ra bằng **tiếng Anh**, không theo `doc_lang` như spec §4 viết.
Lý do: đúng tiền lệ của file sổ sinh tự động anh em là `docs/tdq/STATE.md`, và tránh phải
nuôi một bảng dịch cho nội dung máy sinh. QC độc lập đánh giá lệch này **chấp nhận được**
cho `worktrees.md`, nhưng KHÔNG chấp nhận cho khối `NOT CLEANED UP YET` — khối đó nay đã
bắt buộc dịch (F10). Dòng spec §4 nên sửa ở lần cập nhật spec kế tiếp; không sửa trong
request này vì §4 là mục có đánh số, sửa sẽ làm vỡ sha đã duyệt.

## Kết luận

20/20 hạng mục PASS (QC độc lập vòng 2 trả `VERDICT: PASS` hai lần: một cho bảng DoD, một
cho vòng fix 2). Ba vòng fix đã chạy, đúng trần: vòng 1 gỡ 10 khiếm khuyết, vòng 2 gỡ 4
trong 5 khiếm khuyết mới, vòng 3 gỡ KM-6. Còn lại duy nhất KM-5 ở mức nhẹ, ghi nhận chứ
không sửa (churn dựng lại `tich-hop`, không mất việc, không đỏ hạng mục nào). Test suite đúng mốc nền: 37 đỏ, tất cả ở `tests/test_skill_router.py`,
không liên quan request này.
