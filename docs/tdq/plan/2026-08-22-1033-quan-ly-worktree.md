# PLAN — Quản lý vòng đời worktree của workflow

Ngày: 2026-08-22 · Spec: ../spec/2026-08-22-1033-quan-ly-worktree.md (bản 1.1, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — user CHỐT làm trực tiếp lúc 2026-08-22T10:56 (đề xuất đo được là subagent, đội thắng 4.0 phút: 24.5 so với 28.5; user chọn khác, mode là thứ user nói)
Trạng thái plan: HOÀN THÀNH — mode main (user chọn "b" lúc 2026-08-22T10:56)

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Module sổ worktree
- P2 — Vòng đời: mo / hop / soat
- P3 — Điểm chặn ở state
- P4 — Hook nhắc
- P5 — Luật & bản portable
- P6 — Log & test bắt buộc
- Hợp đồng skill khung
- Cụm song song
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy test của module đang sửa; full suite để dành chạy đúng một lần ở P6.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Mọi test chạm git phải dựng repo tạm bằng `tempfile`, cấm chạy trên repo thật.

## P1 — Module sổ worktree

- [x] **T1.1** (e20m) Viết `scripts/tdq_worktree_registry.py`: schema 7 trường (`slug`, `ma_task`, `nhanh`, `duong_dan`, `tao_luc`, `trang_thai`, `dong_luc`), hàm đọc/mở dòng/đóng dòng, đọc file hỏng thì trả sổ rỗng + cảnh báo và KHÔNG ghi đè — Test: `python3 -m pytest tests/test_worktree_registry.py -q -k "schema or hong"`
  - Chạm: `scripts/tdq_worktree_registry.py`, `tests/test_worktree_registry.py` → file mới, chưa node nào phụ thuộc
- [x] **T1.2** (e12m) Sinh `docs/tdq/worktrees.md` từ JSON, hai lần sinh cho ra file giống hệt nhau từng byte — Test: `python3 -m pytest tests/test_worktree_registry.py -q -k render`
  - Chạm: `scripts/tdq_worktree_registry.py`, `tests/test_worktree_registry.py`
  - Cần: T1.1
- [x] **T1.3** (e14m) Bảng TẬP ĐÓNG lý do chặn → phương án (`ban`, `xung-dot`, `chua-merge`, `khoa`) và hàm dựng khối gợi ý; lý do ngoài tập → raise, cấm trả khối rỗng — Test: `python3 -m pytest tests/test_worktree_registry.py -q -k "goi_y or ly_do"`
  - Chạm: `scripts/tdq_worktree_registry.py`, `tests/test_worktree_registry.py`
  - Cần: T1.1

**Xong P1 khi**: `python3 -m pytest tests/test_worktree_registry.py -q` xanh và `docs/tdq/worktrees.md` sinh được từ một sổ mẫu.

## P2 — Vòng đời: mo / hop / soat

- [x] **T2.1** (e12m) `lenh_mo` mở một dòng sổ (trạng thái `mo`) ngay sau khi `git worktree add` thành công — Test: `python3 -m pytest tests/test_team_mode.py -q -k "mo_ghi_so"`
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_mode.py` → node `lenh_mo()`
  - Cần: T1.1
- [x] **T2.2** (e24m) `lenh_hop`: sau khi merge xong, kiểm ba điều kiện (`git status --porcelain` rỗng · nhánh nằm trong `git branch --merged <tich-hop>` · `kiem` xanh) rồi `git worktree remove` + `git branch -d` nhánh task, đóng dòng sổ; nhánh tích hợp luôn giữ — Test: `python3 -m pytest tests/test_team_mode.py -q -k "hop_don_khi_sach"`
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_mode.py` → node `lenh_hop()`
  - Cần: T2.1
- [x] **T2.3** (e16m) Thiếu bất kỳ điều kiện nào → KHÔNG xoá gì, dòng sổ vẫn `mo`, in khối gợi ý của T1.3 với đúng lý do — Test: `python3 -m pytest tests/test_team_mode.py -q -k "hop_giu_khi_ban or hop_giu_khi_chua_merge"`
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_mode.py` → node `lenh_hop()`
  - Cần: T2.2, T1.3
- [x] **T2.4** (e26m) Lệnh mới `soat`: liệt kê 5 cột (đường dẫn · tuổi ngày · dung lượng · sạch/bẩn · đã-merge/chưa) cho worktree dưới `.tdq-worktrees/`; mục riêng "ngoài tầm" chỉ liệt kê không xoá; dòng sổ trỏ vào thư mục không tồn tại thì tự đóng với lý do `bien-mat`; cảnh báo khi tổng > 500 MB hoặc tuổi > 7 ngày — Test: `python3 -m pytest tests/test_team_mode.py -q -k soat`
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_mode.py` → node `main()` (Hub, bậc 20)
  - Cần: T1.1, T1.3
- [x] **T2.5** (e10m) `soat --don`: dọn hàng loạt theo đúng luật ba điều kiện, cái nào không đủ thì rơi vào khối gợi ý — Test: `python3 -m pytest tests/test_team_mode.py -q -k "soat_don"`
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_mode.py` → node `main()` (Hub, bậc 20)
  - Cần: T2.4, T2.2

**Xong P2 khi**: `python3 -m pytest tests/test_team_mode.py -q` xanh.

## P3 — Điểm chặn ở state

- [x] **T3.1** (e14m) `set phase=qc` thoát khác 0 khi sổ còn dòng `mo`, in số dòng còn mở + lệnh gỡ; sổ trống hoặc chưa có file thì không chặn — Test: `python3 -m pytest tests/test_state.py -q -k "chan_worktree"`
  - Chạm: `scripts/tdq_state.py`, `tests/test_state.py` → node `main()` (Hub, bậc 20)
  - Cần: T1.1

## P4 — Hook nhắc

- [x] **T4.1** (e12m) `prompt_context.py` in đúng một dòng `[TDQ:WORKTREE] <n> worktree chưa dọn — chạy soat` khi sổ còn dòng mở; sổ sạch/hỏng/thiếu → không in gì và thoát 0 — Test: `python3 -m pytest tests/test_context_hooks.py -q -k worktree`
  - Chạm: `hooks/scripts/prompt_context.py`, `tests/test_context_hooks.py`
  - Cần: T1.1

## P5 — Luật & bản portable

- [x] **T5.1** (e12m) `team-mode.md`: thêm mục sổ worktree + lệnh `soat`, và LUẬT bắt buộc chép khối gợi ý xuống cuối turn khi còn worktree chưa dọn; thêm `soat` vào mục Self-check — Test: `python3 scripts/doc_lint.py skills/tdq-build/references/team-mode.md` = 0 và `python3 -m pytest tests/test_user_facing_block.py tests/test_reference_mot_tang.py -q` xanh
  - Chạm: `skills/tdq-build/references/team-mode.md`
  - Cần: T2.4, T2.5
- [x] **T5.2** (e10m) Dựng lại hai cây portable — Test: `python3 scripts/build_portable.py && python3 scripts/tdq_checkportable.py check --root portable_claude && python3 scripts/tdq_checkportable.py check --root portable_codex` đều CLEAN
  - Chạm: `portable_claude/`, `portable_codex/`
  - Cần: T5.1

## Hợp đồng skill khung

Hai skill spec §3b đánh `DÙNG` là skill khung của chính hai phase còn lại, không gắn vào
một task đơn lẻ nào; hợp đồng của chúng ghi ở đây.

- Hợp đồng khung — phase plan
  - Dùng: `tdq-plan`
  - Để: biến spec đã duyệt thành plan checkbox này, mỗi task một lệnh kiểm; nạp trước khi viết
    dòng task đầu tiên. Agent ngoài không có skill system: đọc `skills/tdq-plan/SKILL.md` rồi làm theo.
  - Ra: `docs/tdq/plan/2026-08-22-1033-quan-ly-worktree.md`
  - Kiểm: `python3 scripts/doc_lint.py --pair docs/tdq/spec/2026-08-22-1033-quan-ly-worktree.md docs/tdq/plan/2026-08-22-1033-quan-ly-worktree.md` thoát 0
  - Không dùng cho: viết code, chấm QC, hay quyết mode thay user
- Hợp đồng khung — phase implement/qc/report
  - Dùng: `tdq-build`
  - Để: chạy P1–P6 theo luật đỏ→xanh, rồi QC theo DoD và viết report; nạp ngay khi vào phase
    implement. Agent ngoài không có skill system: đọc `skills/tdq-build/SKILL.md` rồi làm theo.
  - Ra: `docs/tdq/qc/2026-08-22-1033-quan-ly-worktree.md` và `docs/tdq/reports/2026-08-22-1033-quan-ly-worktree.md`
  - Kiểm: `python3 -m pytest tests/ -q` cho ≤ 37 đỏ và hai file trên tồn tại
  - Không dùng cho: sửa spec đã seal, tự duyệt thay user, tự push

## Cụm song song

Kết luận: **một cụm**. Lý do đo được: 5 trong 10 task chạm chung `scripts/tdq_team.py`, và
`tdq_worktree_registry.py` là hợp đồng chung mà P2–P4 đều đọc nên phải xong trước
(lý do đóng `hop-dong`). Hai task còn lại chạm `hooks/` và `skills/` — thuộc `TIEN_TO_FILE_LUAT`,
`phan-cong` xếp `tu_lam` bắt buộc (lý do đóng `file-luat`). Số task có vùng `Chạm:` không giao
nhau và không phải file luật: **1** (T3.1). Trần tốc độ của mode đội vì thế là 1 — không có gì
để chạy song song.

## P6 — Log & test bắt buộc

Việc này CÓ runtime.

- [x] **T6.1** (e8m) Mọi lần mở/đóng/xoá một dòng sổ ghi một dòng log có timestamp qua `_log()` sẵn có, tắt được bằng `TDQ_LOG=0` — Test: `python3 -m pytest tests/test_worktree_registry.py tests/test_team_mode.py -q -k log`
  - Chạm: `scripts/tdq_worktree_registry.py`, `scripts/tdq_team.py`
  - Cần: T2.5
- [x] **T6.2** (e12m) Chạy full suite đúng một lần — Test: `python3 -m pytest tests/ -q` cho số đỏ ≤ 37 và mọi test đỏ đều thuộc `tests/test_skill_router.py`
  - Cần: T5.2, T6.1

## Definition of Done

Trỏ về §6 của spec (Q1–Q20).

- [x] Q1–Q3 — module sổ đọc/ghi/sinh `.md` đúng, file hỏng không bị ghi đè: `python3 -m pytest tests/test_worktree_registry.py -q -k "schema or hong or render"` xanh
- [x] Q4 — `mo` ghi sổ: `python3 -m pytest tests/test_team_mode.py -q -k mo_ghi_so` xanh
- [x] Q5–Q7 — `hop` dọn khi sạch, giữ khi bẩn/chưa merge: `python3 -m pytest tests/test_team_mode.py -q -k "hop_"` xanh
- [x] Q8–Q10 — `soat` đủ 5 cột, tôn trọng vùng ngoài tầm, cảnh báo ngưỡng có số thật: `python3 -m pytest tests/test_team_mode.py -q -k soat` xanh
- [x] Q11–Q12 — chặn `phase=qc` đúng lúc, không chặn oan: `python3 -m pytest tests/test_state.py -q -k chan_worktree` xanh
- [x] Q13–Q14 — hook nhắc đúng và không giết turn: `python3 -m pytest tests/test_context_hooks.py -q -k worktree` xanh
- [x] Q19–Q20 — khối gợi ý đủ phương án và nằm cuối turn: `python3 -m pytest tests/test_worktree_registry.py -q -k "goi_y or ly_do"` xanh và `grep -c "soat" skills/tdq-build/references/team-mode.md` ≥ 2
- [x] Q15 — hub `main()` không mất sub-command: `python3 scripts/tdq_team.py --help` liệt kê đủ 8 lệnh và `python3 scripts/tdq_state.py --help` đủ 7 lệnh
- [x] Q16 — test suite không tệ hơn mốc nền: `python3 -m pytest tests/ -q` cho ≤ 37 đỏ
- [x] Q17–Q18 — portable CLEAN và lint tài liệu sạch: `python3 scripts/tdq_checkportable.py check --root portable_claude` + `--root portable_codex` CLEAN, `python3 scripts/doc_lint.py docs/tdq/spec/2026-08-22-1033-quan-ly-worktree.md docs/tdq/plan/2026-08-22-1033-quan-ly-worktree.md` = 0

## QC

Vòng fix 1 (QC độc lập trả FAIL ở Q2, kèm 8 khiếm khuyết ngoài bảng DoD). Theo luật thi
hành số 5: thêm task fix vào đây, không cần duyệt lại.

- [x] **F1** (e12m) Sổ hỏng không còn làm `mo`/`hop` văng traceback, và `mo` kiểm ghi được sổ TRƯỚC khi `git worktree add` nên không đẻ worktree mồ côi — Test: `python3 -m pytest tests/test_team_mode.py -q -k "so_hong"`
  - Chạm: `scripts/tdq_worktree_registry.py`, `scripts/tdq_team.py`, `tests/test_team_mode.py`
- [x] **F2** (e6m) Dòng sổ thiếu `duong_dan` bị đóng với lý do `thieu-duong-dan` thay vì ném KeyError làm kẹt cổng qc — Test: `python3 -m pytest tests/test_team_mode.py -q -k "thieu_duong_dan"`
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_mode.py`
  - Cần: F1
- [x] **F3** (e8m) Worktree trong tầm mà không có dòng sổ (điển hình là `tich-hop`) được liệt kê và dọn khi sạch, nhánh tích hợp vẫn giữ — Test: `python3 -m pytest tests/test_team_mode.py -q -k "tich_hop_nhung_giu_nhanh"`
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_mode.py`
  - Cần: F1
- [x] **F4** (e10m) File bị gitignore mà không sinh lại được (vd `.env`) tính là bẩn; bỏ `--force` khỏi mọi `worktree remove` — Test: `python3 -m pytest tests/test_team_mode.py -q -k "gitignore or rac_sinh_lai"`
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_mode.py`
- [x] **F5** (e3m) `soat` trả mã 1 khi còn worktree bẩn (spec §2 đầu ra 4); `hop` vẫn trả 0 sau merge thành công — Test: `python3 -m pytest tests/test_team_mode.py -q -k "soat_don_dep"`
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_mode.py`
- [x] **F6** (e2m) Đổi tên test để `-k "hop_don_khi_sach"` ở DoD chọn đúng test — Test: `python3 -m pytest tests/test_team_mode.py -q -k "hop_don_khi_sach"`
  - Chạm: `tests/test_team_mode.py`
- [x] **F7** (e3m) Chạy `git worktree prune` sau khi đóng dòng có thư mục đã biến mất — Test: `python3 -m pytest tests/test_team_mode.py -q -k soat`
  - Chạm: `scripts/tdq_team.py`
- [x] **F8** (e5m) Lệnh `don` cũ bỏ qua worktree còn việc chưa commit và in khối gợi ý — Test: `python3 -m pytest tests/test_team_mode.py -q -k "don_khong_xoa"`
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_mode.py`
- [x] **F9** (e2m) `.gitignore` thêm `docs/tdq/worktrees.json` và `.md` để không commit đường dẫn tuyệt đối của máy user — Test: `git check-ignore -v docs/tdq/worktrees.json docs/tdq/worktrees.md` trả 0
  - Chạm: `.gitignore`
- [x] **F10** (e4m) `team-mode.md` bắt DỊCH khối `NOT CLEANED UP YET` sang `doc_lang` của user, lệnh giữ nguyên văn — hết mâu thuẫn với `user-facing-block.md:7` — Test: `grep -n "TRANSLATED into their" skills/tdq-build/references/team-mode.md`

Vòng fix 2 (QC vòng 2 trả PASS cho Q1–Q20 nhưng bắt 5 khiếm khuyết mới; KM-1 và KM-2 chạm
cam kết "worktree bị chặn luôn có phương án gỡ được" ở spec §5 nên phải sửa).

- [x] **F11** (e12m) Worktree bị `git worktree lock` không còn làm chết cả lượt `soat --don`/`don`: `_go_thu_muc()` chạy `worktree remove` với `check=False`, git từ chối thì thành một dòng lý do `khoa` trong khối gợi ý — Test: `python3 -m pytest tests/test_team_mode.py -q -k "bi_khoa_khong_lam_chet"`
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_mode.py`
- [x] **F12** (e14m) Rác ignored không sinh lại được có lý do chặn riêng `bo-qua` với 3 phương án gỡ được thật (`git clean -fdx` + quét lại), không còn bị gọi nhầm là "uncommitted changes"; `soat` trả 1 cho cả `ban` lẫn `bo-qua` — Test: `python3 -m pytest tests/test_team_mode.py -q -k "rac_ignored_la_ly_do_rieng"`
  - Chạm: `scripts/tdq_worktree_registry.py`, `scripts/tdq_team.py`, `skills/tdq-build/references/team-mode.md`, `tests/test_team_mode.py`
  - Cần: F11
- [x] **F13** (e6m) Worktree trong tầm không có dòng sổ được kiểm đủ điều kiện cấp thư mục (khoá · bẩn · rác ignored) qua `_ly_do_chan_thu_muc()` dùng chung với `don` — Test: `python3 -m pytest tests/test_team_mode.py -q -k "khong_co_dong_so_van_bi_kiem"`
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_mode.py`
  - Cần: F11
- [x] **F14** (e2m) `unittest.main()` chuyển xuống cuối `tests/test_team_mode.py` — 25 test worktree không còn bị bỏ im lặng khi chạy file trực tiếp — Test: `python3 tests/test_team_mode.py` báo cùng số test với `python3 -m pytest tests/test_team_mode.py -q`
  - Chạm: `tests/test_team_mode.py`

Vòng fix 3 (vòng cuối trong trần 3) — QC vòng 2 xác minh F11–F14 đạt, chỉ còn một khiếm
khuyết nhẹ mới.

- [x] **F15** (e6m) Lời từ chối của git không còn bị dán cứng nhãn `khoa`: lý do mới `git-tu-choi` in nguyên văn câu git kèm phương án đúng; nhãn `khoa` chỉ dùng khi worktree thật sự bị lock — Test: `python3 -m pytest tests/test_team_mode.py -q -k "git_tu_choi or khoa_that"`
  - Chạm: `scripts/tdq_worktree_registry.py`, `scripts/tdq_team.py`, `tests/test_team_mode.py`
