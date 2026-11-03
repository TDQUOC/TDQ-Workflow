# QC — 2026-08-17-2001-smoke-test-main-vs-doi

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Spec: `docs/tdq/spec/2026-08-17-2001-smoke-test-main-vs-doi.md` §6 · Plan:
`docs/tdq/plan/2026-08-17-2001-smoke-test-main-vs-doi.md`. 13 hạng mục, chạy ngày
2026-08-17. Mọi output dưới đây chép từ terminal.

## Kết quả

| # | Hạng mục | Kết quả | Bằng chứng |
|---|---|---|---|
| Q1 | Test suite không đỏ | PASS | `python3 -m pytest tests/ -q` → `868 passed, 407 subtests passed in 91.60s` (≥ 839) |
| Q2 | Dựng plan mẫu đúng tham số | PASS | `dung-plan --task 12 --chong 0.25` → `12 task · 3 cặp task chồng file`; `round(0.25×12)=3` nên `C(3,2)=3`; `doc_lint` exit 0 |
| Q3 | Plan mẫu chạy được với công cụ thật | PASS | trong repo tạm: `phan-cong` rc=0 → `Giao agent con: 12/12 task · 3 đợt`; `kiem-ke` rc=0 → `Bản đồ sạch: 12/12`; bản đồ 12 bản ghi, mỗi bản ghi đủ 4 trường |
| Q4 | Công thức mô phỏng kiểm tay được | PASS | `CongThucTest`: 4 task/2 đợt → T_main = 4×100 + 4×10 = 440; T_đội = 2×(20+5+5) + 2×100 + 15 = 275; máy in đúng hai số đó |
| Q5 | Cấm bịa hằng số | PASS | `mo-phong --task 6` không kèm file → rc=1, stderr nêu `--thuc-do`, KHÔNG in bảng |
| Q6 | Lượt chạy thật có số thật | PASS | file thực đo có 6 hằng số, mỗi hằng số `so_mau` ≥ 3 và có `do_tan`; `t_task`, `t_kiem`, `t_hop` mang `nguon=that` |
| Q7 | Quét ra được điểm hoà | PASS | `quet --task 12 --buoc 10` → bảng 11 dòng, `NGƯỠNG: ở tỉ lệ tách được 10% thì thắng-thua đổi chiều main → đội` |
| Q8 | Chất lượng đo đủ 6 chỉ số | PASS (sau vòng fix 1) | vòng QC độc lập đầu chấm FAIL vì ô `main` của dòng "số defect QC độc lập bắt" là câu trỏ đi chỗ khác; đã điền số (8 so với 2), agent chấm lại ra PASS |
| Q9 | Repo thật không bị đụng | PASS | `git worktree list` vẫn 2 dòng như trước; `git branch --list "tdq/*"` rỗng; `git status --short` chỉ có file đầu ra của chính request |
| Q10 | Log service | PASS | `dung-plan --task 2` → stderr 2 dòng, dòng đầu `[2026-08-17T20:42:29] dung-plan · --task 2`; `TDQ_LOG=0` → 0 dòng |
| Q11 | Kết luận trả lời đúng câu user hỏi | PASS | mục `## Kết luận` có `nhanh hơn: mode đội` kèm ba mốc số, và `chất lượng: …` kèm 868/868 so với 9/9 |
| Q12 | Test biên: plan không tách được | PASS | `mo-phong --task 6 --chong 1.0` → 6 đợt, main 12,2 phút so với đội 12,3 phút, `Thắng: main`; `pytest -k bien` xanh |
| Q13 | QC độc lập | PASS (vòng 2) | vòng 1 FAIL 11/12; sau vòng fix 1 agent thứ hai chấm lại 14 hạng mục đều PASS — chi tiết ở mục dưới |

## Q4 — kiểm tay công thức, chép nguyên phép tính

Hằng số đặt sẵn TRONG TEST (code sản phẩm không có số nào như vậy):
`t_task=100`, `t_tick=10`, `t_phat=20`, `t_kiem=5`, `t_hop=5`, `t_don=15`.

Plan 4 task, `chong=0.5` → T1.1 và T1.2 cùng `src/chung.py` nên phải tách hai đợt.
Đợt 1 = {T1.1, T1.3, T1.4}, đợt 2 = {T1.2}.

- `T_main` = 4×100 + 4×10 = **440**
- `T_đội` = 2×(20+5+5) + 2×100 + 15 + max(0, 0−200) = 60 + 200 + 15 = **275**

Ca leader làm chen: 4 task, 2 task cuối phụ thuộc → giao 2 (một đợt), giữ 2.
`chen` = max(0, 2×100 − 1×100) = 100 → `T_đội` = 30 + 100 + 15 + 100 = **245**.

## Lượt chạy THẬT — hai defect lộ ra

Chi tiết ở mục 3 của file kết quả. Tóm tắt:

| # | Defect | Cách vá | Test khoá lại |
|---|---|---|---|
| D1 | `kiem` văng `UnicodeDecodeError` khi `git merge-tree` in byte không phải UTF-8 | `tdq_team._git` đọc output với `errors="replace"` | `test_kiem_khong_chet_khi_git_in_byte_khong_phai_utf8` |
| D2 | Hook `edit_gate` chặn agent con sửa file trong repo tạm vì đọc state của repo thật | chưa vá — ghi nhận làm việc của request sau | (chưa có) |

D1 chứng minh đỏ trước xanh sau: bỏ `errors="replace"` thì test đỏ, thêm lại thì xanh.

## Q13 — kết luận độc lập

Agent `tdq-qc-tester` chạy lại Q1–Q12 (29 lượt tool, 12,5 phút), không đọc file này.
**VERDICT của agent: FAIL — 11/12 PASS, hỏng Q8.** Vài số agent tự đo:

- `pytest tests/ -q` → `868 passed, 407 subtests passed in 72.84s`.
- Q4: agent tự đặt bộ hằng số khác rồi kiểm tay → máy in `6.7 | 3.9`, tay ra 404 giây
  và 235 giây. Khớp cả `phi_dot` lẫn `tong_max`.
- Q9: `STATUS: giong het`, `WORKTREE: giong het`, `BRANCH tdq/*: rong`.
- Bảng độ nhạy `t_phat` ở mục 5 file kết quả: agent chạy lại ra **đúng từng dòng**.
- Q8 FAIL: ô `main` của chỉ số "số defect QC độc lập bắt" là câu trỏ đi chỗ khác, không
  phải một con số.

Phán quyết của agent về thiên vị: **có thiên vị nhẹ, phần lớn đã khai, cộng một lỗ hổng
lớn chưa khai** — thiếu trục độ nhạy theo `he_so_agent` (agent con chậm hơn leader bao
nhiêu lần). Agent tự tính: `K=1` → ngưỡng 10%, `K=1.25` → 30%, `K=1.5` → 40%, `K=2` →
60%, `K=3` → 80%.

### Vòng fix 1 (trần 3 vòng, dùng 1)

| # | Defect agent nêu | Cách vá | Test khoá lại |
|---|---|---|---|
| D1 | `thuc-do --lap 0` + `--mau-that` bịa trọn 6 hằng số mà vẫn ghi `nguon=that` | `--lap` phải ≥ 1; mỗi hằng số ghi thêm `cach_do` = `may` hay `nhap-tay`, và giữ lại mẫu máy đo ở `mau_may` | `test_lap_0_bi_tu_choi`, `test_mau_that_ghi_ro_la_nhap_tay` |
| D2 | `nap_hang_so` nhận `so_mau = 1` | chỗ ĐỌC ép `so_mau` ≥ 3, không chỉ chỗ ghi | `test_so_mau_duoi_nguong_bi_tu_choi_luc_doc` |
| D3 | hằng số âm cho ra bảng thời gian âm | ép số dương hữu hạn | `test_hang_so_am_hoac_vo_cuc_bi_tu_choi` |
| D4 | 5 ca văng traceback thô (plan không có, thư mục ra không có, `giay` không phải số, `giay` null, `--buoc 0`) | bắt lỗi, báo kèm câu lệnh sửa | `test_moi_ca_hong_deu_bao_loi_co_lenh_sua` |
| D5 | `--buoc -10` in bảng rỗng rồi kết luận `None thắng` | `--buoc` phải nằm trong 1–100 | cùng test D4 |
| D6 | Dòng "mode main 366,5 giây" nằm dưới tiêu đề "lượt chạy THẬT" nhưng main chưa hề chạy | viết lại mục 1 file kết quả: tách rõ **đo được** và **suy ra**, sửa cả mục Kết luận | (văn bản, kiểm bằng `doc_lint` và bằng chính agent ở vòng sau) |
| D7 | Q8: ô `main` không phải số | điền số thật cho cả hai mode | (văn bản) |
| D8 | 28 test không phủ ca lỗi D2–D5 | thêm 5 test cho đúng các ca đó | 5 test mới ở `tests/test_bench.py` |

Thêm theo đúng chỗ agent chỉ ra: `mo-phong` và `quet` có tham số `--he-so-agent`, và
file kết quả có bảng độ nhạy theo hệ số đó.

### Chấm lại sau vòng fix 1 — VERDICT: PASS

Agent `tdq-qc-tester` thứ hai chạy 20 lượt tool trong 4 phút, chấm 14 hạng mục, tất cả
PASS. Số agent tự chạy:

- `python3 -m pytest tests/ -q` → `874 passed, 416 subtests passed in 65.98s`.
- `pytest tests/test_bench.py -q` → `34 passed, 22 subtests passed` (28 trước vòng fix).
- D1–D5: `--lap 0`, `so_mau = 1` sửa tay, hằng số âm/0/vô cực, `--plan` không có,
  `--buoc 0` và `--buoc -10` — cả sáu ca đều rc=1, không ca nào in bảng, không traceback.
- Bảng độ nhạy `he_so_agent`: agent tự chạy `quet --he-so-agent 1/1,25/1,5/2/3` ra đúng
  `10% / 30% / 40% / 60% / 80%`, khớp từng dòng của mục 5 file kết quả.
- `grep "TODO\|FIXME\|NotImplemented"` trên hai file: không khớp dòng nào.
- `git status --short`: chỉ 4 file mới của chính request này.

Agent nêu thêm một defect NHẸ: số "868 test" ở mục 2 và mục Kết luận đã lỗi thời sau khi
vòng fix thêm 6 test. Đã sửa thành 874, `doc_lint` vẫn exit 0. Vòng fix dùng 1 trên trần 3.
