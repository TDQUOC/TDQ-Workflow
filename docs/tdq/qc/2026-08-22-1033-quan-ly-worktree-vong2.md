# QC vòng 2 — 2026-08-22-1033-quan-ly-worktree (agent QC độc lập)

Ngày chạy: 2026-08-22 · Repo: /Users/truongdinhquoc/Documents/TDQWorkflow · nhánh tdq-doi-ten-mode-implement
Mốc nền: 37 đỏ, toàn bộ thuộc `tests/test_skill_router.py`.
Mọi probe thủ công chạy trên repo git tạm dựng bằng `tempfile` (harness riêng của QC, không
dùng lại test của tác giả). KHÔNG chạy lệnh git ghi nào lên repo thật.

## 1. Bảng DoD Q1–Q20

| # | Lệnh | Kết quả | Phán |
|---|---|---|---|
| Q1–Q3 | `python3 -m pytest tests/test_worktree_registry.py -q -k "schema or hong or render"` | `15 passed, 6 deselected` | PASS |
| Q3 (tay) | `ghi_md` 2 lần → sha256 | `identical: True ed71c6f6b3bac275` | PASS |
| Q4 | `python3 -m pytest tests/test_team_mode.py -q -k mo_ghi_so` | `1 passed, 137 deselected` | PASS |
| Q4 (tay) | `mo T1.1` trên repo tạm | sổ có 1 dòng, đủ 7 trường, `trang_thai=mo`, `duong_dan` khớp thư mục thật | PASS |
| Q5–Q7 | `python3 -m pytest tests/test_team_mode.py -q -k "hop_"` | `11 passed, 127 deselected` | PASS |
| Q5 (tay) | `hop T1.1` sau khi commit sạch | `Cleaned up: worktree removed, branch ... deleted` · wt False · nhánh task False · tich-hop True · dòng sổ `dong` | PASS |
| Q6 (tay) | `hop T1.2` khi còn `chua_commit.txt` | `reason: the worktree still holds uncommitted changes (chua_commit.txt)` · wt còn · dòng sổ `mo` | PASS |
| Q7 (tay) | `soat --don` khi nhánh chưa merge | `reason: the branch is not in the integration branch yet` · wt còn · nhánh còn | PASS |
| Q8–Q10 | `python3 -m pytest tests/test_team_mode.py -q -k soat` | `11 passed, 127 deselected` | PASS |
| Q8 (tay) | `soat --don` | in đủ `Task/Request/Path/Age/Size/Clean?/Merged?` | PASS |
| Q9 (tay) | thêm worktree ngoài `.tdq-worktrees/` rồi `soat --don` | mục `Out of scope (listed only, never removed…)` · `ngoai still exists: True` | PASS |
| Q10 (tay) | giả `tao_luc=2026-07-01` | `WARNING: T1.1 is 52 days old (threshold 7 days)` | PASS |
| Q10 (tay) | hạ `TRAN_TONG_MB=0`, đặt file 2 MB | `WARNING: worktrees take 2 MB (threshold 0 MB)` | PASS |
| Q11–Q12 | `python3 -m pytest tests/test_state.py -q -k chan_worktree` | `5 passed, 45 deselected` | PASS |
| Q11 (tay) | `tdq_state.py set phase=qc` khi còn dòng mở | rc=2 · `1 worktree(s) still open: T1.2 (...). Clean them up first: … soat --don` | PASS |
| Q12 (tay) | sổ chưa có file / sổ rỗng | rc=0 · `✅ set: … phase=qc` cả hai ca | PASS |
| Q13–Q14 | `python3 -m pytest tests/test_context_hooks.py -q -k worktree` | `4 passed, 24 deselected` | PASS |
| Q13 (tay) | hook với 2 dòng mở | đúng 1 dòng `[TDQ:WORKTREE] 2 worktree(s) still open — run: …` (tổng 2 dòng stdout) | PASS |
| Q14 (tay) | hook với sổ hỏng / thiếu file | rc=0, không traceback, không in gì | PASS |
| Q15 | `python3 scripts/tdq_team.py --help` | liệt kê 8 lệnh: phan-cong kiem-ke cum mo kiem hop soat don | PASS |
| Q15 | `python3 scripts/tdq_state.py --help` | 7 lệnh: next get init set approve reset phases-doc — hành vi (rc=2 + Usage) GIỐNG HỆT bản `git show HEAD:` nên không hồi quy | PASS |
| Q16 | `python3 -m pytest tests/ -q` | `37 failed, 1253 passed, 1448 subtests passed in 99.94s` · `grep ^FAILED \| sed 's/::.*//' \| uniq -c` → chỉ `tests/test_skill_router.py` | PASS |
| Q17 | `tdq_checkportable.py check --root portable_claude` | `CLEAN 85 file(s) match the manifest` | PASS |
| Q17 | `--root portable_codex` | `CLEAN 130 file(s) match the manifest` | PASS |
| Q17 | diff nguồn ↔ portable | 4 file trùng byte, riêng `tdq_state.py` khác đúng 1 dòng rewrite đường dẫn (do build sinh) | PASS |
| Q18 | `doc_lint.py` spec+plan, và brief+qc+team-mode.md | `0 violation(s) total, exit 0` cả hai lượt | PASS |
| Q19 | `pytest tests/test_worktree_registry.py -q -k "goi_y or ly_do"` | `3 passed, 4 subtests passed` | PASS |
| Q19 (tay) | `khoi_goi_y([{... 'ly_do':'ly-do-la'}])` | raise `LoiSo: Unknown blocking reason 'ly-do-la'. The set is closed: ban, chua-merge, khoa, xung-dot` | PASS |
| Q20 | `grep -c soat skills/tdq-build/references/team-mode.md` | `6` (≥ 2) | PASS |
| Q20 (tay) | `hop` bẩn / `soat --don` bẩn | khối `NOT CLEANED UP YET` là phần in CUỐI CÙNG; sạch hết → không in khối | PASS |

## 2. Xác minh F1–F10

| F | Lệnh/probe | Kết quả | Phán |
|---|---|---|---|
| F1 | sổ hỏng `{ khong-phai-json` rồi chạy `mo/hop/soat/soat --don/don` | không lệnh nào traceback; `mo` rc=1 `The worktree ledger is unusable: …`; file hỏng còn nguyên `'{ khong-phai-json'`; không đẻ worktree mồ côi | PASS |
| F2 | dòng sổ thiếu `duong_dan` | gate rc=2 trước, `soat` in `closed row T9.9: thieu-duong-dan`, gate sau rc=0 → hết kẹt | PASS |
| F3 | `soat --don` với worktree `tich-hop` không có dòng sổ | `cleaned: …/tich-hop`, nhánh `tdq/<slug>/tich-hop` vẫn còn; cuối vòng `git worktree list` chỉ còn worktree gốc | PASS |
| F4 | `.env` bị gitignore trong worktree | rc=1, `reason: … uncommitted changes (.env)`, wt còn | PASS |
| F4 | `__pycache__/x.pyc` | rc=0, `cleaned: T1.1` — rác sinh lại không chặn | PASS |
| F5 | `soat --don` còn wt bẩn | rc=1; `hop` sau merge thành công rc=0 | PASS |
| F6 | `pytest -k "hop_don_khi_sach"` | `1 passed, 137 deselected` (chọn trúng test) | PASS |
| F7 | xoá tay thư mục worktree rồi `soat` | `closed row T1.1: bien-mat`; `git worktree list` sạch bản ghi chết; `mo T1.1` lại rc=0 | PASS |
| F8 | `don` với wt bẩn | (xem KM-1: bị lệnh khoá chặn trước khi tới nhánh này; nhánh bẩn có code và test riêng xanh) | PASS có điều kiện |
| F9 | `git check-ignore -v docs/tdq/worktrees.json docs/tdq/worktrees.md` | rc=0, `.gitignore:16` và `:17` | PASS |
| F10 | `grep -n "TRANSLATED into their" team-mode.md` | dòng 150 | PASS |

## 3. Ba câu hỏi săn khiếm khuyết mới

1. Bỏ `--force` khỏi `worktree remove` có kẹt ca nào? → CÓ, 1 ca: worktree bị `git worktree lock`
   mà KHÔNG có dòng sổ (nhánh `la` trong `lenh_soat`, và mọi worktree trong `lenh_don`).
   `_ly_do_chan` chặn `khoa` chỉ chạy cho worktree CÓ dòng sổ. Xem KM-1.
2. `soat` trả mã 1 có phá vòng lặp sóng? → KHÔNG. `grep -rn soat scripts hooks skills agents`
   cho thấy không script/hook nào đọc mã thoát của `soat`; `team-mode.md` chỉ đòi `exit 0`
   cho `kiem-ke`. Mã 1 thuần là tín hiệu cho người đọc.
3. `--ignored=matching` có chặn nhầm rác sinh lại được? → CÓ. Xem KM-2.

## 4. Khiếm khuyết mới

### KM-1 (nặng vừa) — worktree bị KHOÁ mà không có dòng sổ làm chết cả lệnh `soat --don` và `don`

Triệu chứng: `_git(project,"worktree","remove",duong)` ở nhánh "In scope, no ledger row" và
trong `lenh_don` gọi với `check=True` và KHÔNG kiểm `_khoa_khong` trước. Gặp worktree khoá,
`LoiLuat` ném ra giữa vòng lặp → lệnh dừng ngay: các worktree còn lại không được quét, cảnh
báo disk không in, và khối `NOT CLEANED UP YET` KHÔNG BAO GIỜ được in (kể cả cho worktree bẩn
đã phát hiện trước đó). Đúng thứ spec §5 và Q19/Q20 cấm: worktree chặn phải quay về dưới dạng
LÝ DO + phương án, không phải lỗi git thô. Lý do `khoa` đã có sẵn trong tập đóng nhưng đường
này không dùng tới.

Repro:
```
# repo tạm: mo T1.1, tạo thêm worktree la-khoa trong .tdq-worktrees/<slug>/, rồi
git -C <repo> worktree lock <repo>/.tdq-worktrees/<slug>/la-khoa
python3 scripts/tdq_team.py soat --don          # rc=1
# stderr: git worktree remove … failed (128): fatal: cannot remove a locked working tree;
# stdout KHÔNG có "NOT CLEANED UP YET"
```
Bản `don` cùng lỗi: khoá T1.1 + để T1.2 bẩn → `don` rc=1, stdout rỗng, khối gợi ý mất, T1.2
bẩn không được báo.

Nghi ở: `scripts/tdq_team.py:952-960` (nhánh `la:` trong `lenh_soat`) và
`scripts/tdq_team.py:1003-1011` (vòng lặp trong `lenh_don`).

### KM-2 (vừa) — file bị gitignore mà sinh lại được ngoài danh sách `RAC_SINH_LAI` khoá cứng worktree, và cả 2 phương án gợi ý đều không gỡ được

Triệu chứng: `_file_bo_qua_dang_ke` coi MỌI file ignored không khớp 7 chuỗi trong
`RAC_SINH_LAI` là "bẩn". Rác build phổ biến (`build/`, `dist/`, `*.log`, `graphify-out/…`,
`.coverage`) rơi hết vào đây → `soat --don` rc=1 vĩnh viễn. Tệ hơn: khối gợi ý cho lý do `ban`
đưa 2 phương án hành động, cả hai đều KHÔNG xử lý được file ignored — `git add -A` không add
file ignored, `git clean -fd` không xoá file ignored (thiếu `-x`). Chạy đúng lệnh gợi ý xong,
`soat --don` vẫn rc=1 với y nguyên lý do. Đây là vòng chết đúng bằng cái spec sinh ra để chặn.
Chuỗi lý do in ra cũng sai sự thật: gọi file ignored là "uncommitted changes".

Repro:
```
# repo tạm có .gitignore chứa "build/" và "*.log"
mkdir <wt>/build && echo x > <wt>/build/out.o
python3 scripts/tdq_team.py soat --don     # rc=1, reason: … uncommitted changes (build/)
git -C <wt> add -A && git -C <wt> commit -m "wip T1.1"    # "nothing to commit"
git -C <wt> restore -SW . && git -C <wt> clean -fd        # không xoá build/
python3 scripts/tdq_team.py soat --don     # rc=1, y nguyên lý do
```
Nghi ở: `scripts/tdq_team.py:646-664` (`RAC_SINH_LAI`, `_file_bo_qua_dang_ke`) và
`scripts/tdq_worktree_registry.py:41-51` (phương án của lý do `ban` thiếu `clean -fdx`).

### KM-3 (nhẹ) — worktree trong tầm không có dòng sổ chỉ bị kiểm 1/3 điều kiện

`lenh_soat` nhánh `la:` chỉ kiểm `_sach(duong)` rồi xoá; không kiểm `chua-merge`, không kiểm
`khoa`. Đã dựng lại: worktree `la-chua-merge` có commit chưa merge bị xoá thư mục. Không mất
việc (nhánh `nhanh-la` và commit `322c1a7 viec` vẫn truy được) nên chỉ là lệch luật ba điều
kiện của spec §5, không phải mất dữ liệu.
Nghi ở: `scripts/tdq_team.py:952-960`.

### KM-4 (nhẹ) — `unittest.main()` đặt trước 3 lớp test mới nên chạy file trực tiếp bỏ im 25 test

`tests/test_team_mode.py:1320` có `if __name__ == "__main__": unittest.main()`, còn
`SoWorktreeTest` (1323), `LogWorktreeTest` (1497), `VaLuoiWorktreeTest` (1523) nằm SAU nó.
`python3 tests/test_team_mode.py` → `Ran 113 tests … OK`; `pytest` cùng file → `138 tests
collected`. Chênh đúng 25 test worktree, và chênh này im lặng xanh.
Nghi ở: `tests/test_team_mode.py:1319-1320`.

### KM-5 (nhẹ, ghi nhận) — `soat --don` gỡ luôn worktree `tich-hop` giữa sóng

Chạy `soat --don` khi còn task chưa merge sẽ xoá thư mục worktree tích hợp. Không hỏng:
`_bao_dam_tich_hop` dựng lại ở lần `hop` kế tiếp (đã kiểm: `hop T1.1` sau đó rc=0, merge
thành công). Chỉ là churn, ghi lại để biết.

## 5. Kết luận

Q1–Q20 PASS toàn bộ; F1–F10 đã sửa thật. 5 khiếm khuyết mới nằm NGOÀI bảng DoD, trong đó KM-1
và KM-2 chạm đúng cam kết "worktree chặn luôn có phương án gỡ" của spec §5/Q19.

---

# Phần bổ sung — xác minh VÒNG FIX 2 (KM-1..KM-4)

Chạy 2026-08-22, repo tạm `tempfile`, không lệnh git ghi nào lên repo thật.

| KM | Repro (đúng ca vòng 1) | Kết quả | Phán |
|---|---|---|---|
| KM-1a | `worktree lock <la-khoa>` + 1 wt bẩn → `soat --don` | rc=1, KHÔNG còn `failed (128)` ra stderr, khối in đủ **2** mục: `reason: … uncommitted changes (ban.txt)` và `reason: git has this worktree locked` | ĐÃ SỬA |
| KM-1b | `worktree lock <t1.1>` + t1.2 bẩn → `don` | rc=0, `Removed 1 worktree(s) … pruned.`, `NOT CLEANED UP YET: 2` với đủ 2 lý do, không lỗi git thô | ĐÃ SỬA |
| KM-1c | chạy đúng phương án `khoa`: `git worktree unlock` rồi `soat --don` | `cleaned: T1.1`, wt biến mất → phương án gỡ được thật | ĐÃ SỬA |
| KM-2 | `build/out.o` + `test.log` ignored → `soat --don` | rc=1, lý do RIÊNG `bo-qua`: `ignored files here do not regenerate… (build/, test.log)` — hết gọi nhầm là "uncommitted changes" | ĐÃ SỬA |
| KM-2 | chạy đúng phương án 3 in ra: `git -C <wt> clean -fdx && soat --don` | `Removing build/` `Removing test.log` → `soat --don` rc=**0**, `cleaned: T1.1` → hết vòng chết | ĐÃ SỬA |
| KM-2 | `_file_ban` có còn trộn file ignored? | wt vừa bẩn vừa có `build/`: chi tiết chỉ còn `(chua-commit.txt)` | ĐÃ SỬA |
| KM-3 | dòng lạ `la-ban` (bẩn), `la-boqua` (ignored), `la-chua-merge` (có commit) → `soat --don` | `la-ban` và `la-boqua` GIỮ NGUYÊN kèm đúng 2 lý do; `la-chua-merge` vẫn bị gỡ thư mục nhưng nhánh `nhanh-la` + commit `7115cf2 viec` còn nguyên (đúng thiết kế `_ly_do_chan_thu_muc` = khoá·bẩn·bo-qua, merge cố ý không tính vì chỉ gỡ THƯ MỤC) | ĐÃ SỬA |
| KM-4 | `python3 tests/test_team_mode.py` vs `pytest` | `Ran 142 tests … OK` ↔ `142 passed, 21 subtests passed` — khớp, hết 25 test vô hình | ĐÃ SỬA |

## Số đo lại (xác nhận số của coordinator)

| Lệnh | Output |
|---|---|
| `pytest tests/test_team_mode.py -q` | `142 passed, 21 subtests passed in 18.71s` |
| `python3 tests/test_team_mode.py` | `Ran 142 tests in 17.647s` / `OK` |
| `pytest tests/ -q` | `37 failed, 1257 passed, 1452 subtests passed` — 100% đỏ ở `tests/test_skill_router.py` (đúng mốc nền) |
| `pytest -k "bi_khoa_khong_lam_chet or rac_ignored_la_ly_do_rieng or khong_co_dong_so_van_bi_kiem_du"` | `4 passed, 138 deselected` |
| `tdq_checkportable.py check --root portable_claude` / `portable_codex` | `CLEAN 85 file(s)` / `CLEAN 130 file(s)`; `tdq_team.py` + `tdq_worktree_registry.py` trùng byte cả 2 cây |
| `pytest -k "gitignore or rac_sinh_lai or soat_don_dep"` (F4/F5) | `3 passed, 139 deselected` |
| `pytest test_worktree_registry.py -k "goi_y or ly_do"` (Q19) | `3 passed, 5 subtests passed` — tập đóng nay phủ cả `bo-qua` |

## Hồi quy không đỏ thêm

| Ca | Kết quả |
|---|---|
| Đường hạnh phúc đầy đủ: `mo → commit → hop → soat --don → set phase=qc` | `Cleaned up: worktree removed, branch … deleted`; `git worktree list` còn **1 dòng**; gate qc rc=0 |
| `.env` ignored (ý định F4) | vẫn bị chặn, rc=1, nay dưới lý do `bo-qua` chính xác hơn |
| wt CÓ dòng sổ bị khoá | rc=0, dòng sổ VẪN `mo`, `set phase=qc` rc=2 → sổ không lệch thực tế |
| Thư mục của worktree không-có-dòng-sổ bị xoá tay | rc=0, không traceback |

## Khiếm khuyết mới của vòng fix 2

### KM-6 (nhẹ) — mọi lời từ chối của git đều bị dán nhãn `khoa`, kể cả khi không phải khoá

`_go_thu_muc` trả lỗi thô, hai chỗ gọi đều gán cứng `ly_do="khoa"`. Dựng lại bằng cách
`chmod 0500` thư mục cha:

```
reason: git has this worktree locked (error: failed to delete '…/t1.1': Permission denied)
→ unlock it, then sweep again: git worktree unlock …/t1.1 && python3 scripts/tdq_team.py soat
```

Câu lý do sai sự thật và phương án duy nhất (`worktree unlock`) không gỡ nổi lỗi quyền. Nhẹ vì
`chi_tiet` vẫn in nguyên văn câu của git nên user không mù, và lệnh không chết (rc=0, không
traceback). Nghi ở: `scripts/tdq_team.py:735-739`, `:996-998`, `:1045-1047`.

## Kết luận vòng 2

KM-1, KM-2, KM-3, KM-4 sửa thật, xác minh bằng đúng ca repro của vòng 1. KM-5 giữ nguyên theo
thoả thuận. Phát sinh thêm KM-6 mức nhẹ (nhãn lý do sai cho lời từ chối không-phải-khoá).
