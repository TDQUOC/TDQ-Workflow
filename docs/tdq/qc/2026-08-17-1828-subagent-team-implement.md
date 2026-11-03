# QC — 2026-08-17-1828-subagent-team-implement

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Spec: `docs/tdq/spec/2026-08-17-1828-subagent-team-implement.md` §6 · Plan:
`docs/tdq/plan/2026-08-17-1828-subagent-team-implement.md`. 23 hạng mục, chạy ngày
2026-08-17. Mọi output dưới đây là output thật, chép từ terminal.

## Kết quả

| # | Hạng mục | Kết quả | Bằng chứng |
|---|---|---|---|
| Q1 | Test suite không đỏ | PASS | `python3 -m pytest tests/ -q` → `834 passed, 394 subtests passed in 49.38s` (≥ 767) |
| Q2 | `[>]` được đọc đúng | PASS | `pytest tests/test_team_mode.py -k TickState -q` → `6 passed`; ca 4 `[>]` + 1 `[~]` cho `doing_count=1`, `dispatched_count=4` |
| Q3 | Hook nới đúng chỗ, chặt đúng chỗ | PASS | `pytest tests/test_team_mode.py tests/test_edit_gate.py -k "Hook or gate or tick" -q` → `44 passed` |
| Q4 | Chia cụm từ chối cụm giao nhau | PASS | `pytest tests/test_team_mode.py -k Cum -q` → `3 passed`; hai task chung file rơi vào hai đợt |
| Q5 | Dò xung đột trước merge chạy thật | PASS | `pytest tests/test_team_mode.py -k Git -q` → `8 passed`; `kiem` báo XUNG ĐỘT, exit khác 0, repo tạm không đổi |
| Q6 | Hợp tuần tự vào nhánh tích hợp | PASS | cùng lớp `GitTest`; 3 nhánh rời nhau vào nhánh tích hợp, `git log` đủ 3 commit |
| Q7 | Dọn worktree sạch | PASS | cùng lớp `GitTest`; sau `don` thì `git worktree list` chỉ còn worktree gốc |
| Q8 | Log service | PASS | `tdq_team.py kiem-ke` in `[2026-08-17T19:37:17] kiem-ke · project=…` ở stderr; `TDQ_LOG=0` im hoàn toàn |
| Q9 | Luật chống ngưng đủ ngoại lệ | PASS | `tdq-conventions/SKILL.md` §1 mục 7 có luật + đúng 3 mục đánh số; test `test_conventions_co_luat_chong_ngung_va_dung_3_ngoai_le` xanh |
| Q10 | Cặp spec-plan và mọi doc hợp lệ | PASS | `doc_lint.py --pair <spec> <plan>` → exit 0; lint 10 file luật/doc đã sửa → exit 0 |
| Q11 | Hai bundle portable còn sạch | PASS | `build_portable.py` rồi `tdq_checkportable.py check --root …` → `SẠCH 79 file` và `SẠCH 124 file` |
| Q12 | Repo thật không bị đụng | PASS | sau toàn bộ test: `git worktree list` vẫn 2 dòng (gốc + worktree ngoài request), `git branch --list "tdq/*"` rỗng |
| Q13 | Quyết định tách/giữ đúng luật | PASS | `CumTest`; 3 task rời vào cùng đợt, task phụ thuộc và task `(mcp)` bị giữ kèm mã lý do |
| Q14 | Vùng file đã giao bị khoá | PASS | `CumTest`; task chạm vùng đang khoá không được xếp đợt |
| Q15 | Bản đồ phân công sinh đúng | PASS | `pytest -k "PhanCong or KiemKe" -q` → `13 passed, 8 subtests`; json đủ bản ghi, mỗi bản ghi 4 trường |
| Q16 | Kiểm kê bắt task giữ lại vô cớ | PASS | `KiemKeTest`; bản đồ có `tu_lam` thiếu lý do → exit khác 0, in đúng mã task |
| Q17 | Hook chặn main lách luật | PASS | `HookTest`; payload sửa file của task `giao` chưa có nhánh → chặn kèm `[TDQ:TEAM]`; cùng file khi task là `tu_lam` thì không chặn |
| Q18 | File luật đủ khuôn ba mục | PASS | `pytest tests/test_team_mode.py -k Khuon -q` → `8 passed, 9 subtests` |
| Q19 | Bảng tra quyết định đầy đủ | PASS | `KhuonTest`; bảng có đúng 4 nhóm giữ lại + dòng mặc định GIAO, đủ cột dấu hiệu và cột lệnh kiểm |
| Q20 | Ví dụ ĐÚNG/SAI và khuôn prompt | PASS | `KhuonTest`; 5 cặp ĐÚNG/SAI (≥4) và khuôn prompt đủ 7 trường |
| Q21 | Lệnh nêu trong skill là lệnh có thật | PASS | `test_moi_lenh_neu_trong_file_luat_deu_co_that` quét file luật, mọi lệnh con có trong `tdq_team.LENH` |
| Q22 | Thông điệp lỗi nêu việc phải làm | PASS | `KiemKeTest`; stderr chứa cả mã task lẫn câu lệnh sửa |
| Q23 | QC độc lập | PASS | agent `tdq-qc-tester` chạy lại độc lập — kết luận ở mục dưới |

## Q23 — kết luận độc lập

Agent `tdq-qc-tester` tự chạy lại Q1–Q22 (46 lượt tool, ~10,7 phút), không đọc file QC này.
**VERDICT của agent: PASS 22/22**, không hạng mục nào FAIL. Vài số agent tự đo được:

- `pytest tests/ -q` → `834 passed, 394 subtests passed`.
- Q3: bơm 3 payload vào `edit_gate.py` → `[>]`×3 `deny=False` · `[~]`×2 `deny=True TDQ:TICK` ·
  không dấu nào `deny=True`.
- Q5: `kiem T1.1` trên repo tạm → `XUNG ĐỘT`, rc=1, `repo KHONG doi: True`.
- Q7: `don` → `Đã gỡ 4 worktree`, `.git/worktrees ton tai? False`.
- Q12: status/worktree/branch trước-sau đều `GIONG HET`, `tdq/* = 0`.
- Q17: cùng một file — task `giao` → `deny=True TDQ:TEAM`; task `tu_lam` → `deny=False`.

Nhưng agent nêu 5 lỗi mà bộ test đầu không bắt được, trong đó 2 lỗi phá đúng cơ chế
chống lách luật. Đã vá hết trong **một vòng fix** (trần 3 vòng, dùng 1):

| # | Lỗi agent nêu | Cách vá | Test khoá lại |
|---|---|---|---|
| D1 | Xoá `vung_file` của task `giao` → `kiem-ke` vẫn báo sạch, hook hết chặn | `lenh_kiem_ke` soi cả nhánh `giao`: vùng file rỗng hoặc thiếu trường đều đỏ | `test_giao_ma_vung_file_rong_thi_kiem_ke_do` |
| D2 | Bản đồ JSON hỏng → hook fail-open (`deny=False`) | thêm kiểu `ban-do-hong`, hook CHẶN kèm `[TDQ:TEAM]` | `test_ban_do_hong_thi_hook_chan_chu_khong_mo_toang` |
| D3 | Bản đồ hỏng làm CLI văng `JSONDecodeError` | `_boi_canh` bắt lỗi đọc, ném `LoiLuat` kèm lệnh sửa | `test_ban_do_hong_thi_cli_bao_lenh_sua_chu_khong_van_traceback` |
| D4 | Danh sách file xung đột luôn rỗng (`+++ b/` không khớp output `merge-tree`) | `_file_xung_dot` đọc khối `changed in both` → dòng `our/base/their` | `test_kiem_neu_dung_ten_file_xung_dot` |
| D5 | `cum` không nói vì sao task chưa được phát | in dòng `HOÃN N task của đợt sau (đợi đợt X hợp xong)` | `test_cum_noi_ro_vi_sao_task_chua_duoc_phat` |

Phần D5 agent còn nói "chỉ 1/6 file luật có khuôn ba mục trong khi plan tuyên bố 6 file
đều đạt" — đọc lại plan thì chỉ T4.1 (`team-mode.md`) yêu cầu khuôn ba mục, đúng phạm vi
R9 của `doc_lint`. Không phải lỗi, không sửa.

Ghi chú `assert not ten.startswith(TEN_CAM)` là assert chết: đúng, nhưng giữ lại có chủ ý —
nó chặn hồi quy nếu ai đổi tiền tố nhánh `tdq/` sau này.

Sau vòng fix, chạy lại: `pytest tests/ -q` → **839 passed, 394 subtests**; hai bundle
portable sinh lại đều `SẠCH`; `doc_lint --pair` exit 0; repo thật vẫn không có nhánh
`tdq/*` và không worktree lạ.

## Chỗ lệch so với spec

- Trần dòng của `tdq-conventions/SKILL.md` nâng 133 → 143 trong `SKILL_LINE_LIMITS`
  (`scripts/doc_lint.py`), kèm comment lý do. Hai luật thêm vào §1 là luật tầng runtime,
  phải nạp mỗi turn nên không nén xuống references được. Spec không nhắc trần này.
- Ngoài ra không có chỗ lệch: mọi đầu ra §2 của spec đều có mặt.
