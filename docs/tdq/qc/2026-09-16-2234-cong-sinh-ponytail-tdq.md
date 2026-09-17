# QC — Nội hoá lối code Ponytail vào TDQ-Workflow
Ngày: 2026-09-17 · Plan: ../plan/2026-09-16-2234-cong-sinh-ponytail-tdq.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

13 hạng mục DoD + 4 hạng mục cố định QC-F1→F4. Mọi dòng dưới đây là đầu ra thật, chạy trong
lượt này, không có dòng nào suy ra từ lần đo trước.

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Thân luật 7 bậc + món 8, chia hai chỗ | `(cd tests && python3 -m unittest test_than_luat)` · `python3 scripts/i18n_check.py skills/tdq-build/references/rules/chung.md` | `Ran 7 tests … OK` · `0 line(s)`, exit 0 | PASS |
| Q2 | Bộ lọc 4 mức, `off` rỗng, mức lạ về `full` | `(cd tests && python3 -m unittest test_luat_gon)` | `Ran 11 tests … OK` | PASS |
| Q3 | Kênh phiên chèn thật, trần khối đầu 12/600 | `(cd tests && python3 -m unittest test_context_hooks test_token_budget)` | `Ran 43 tests … OK` | PASS |
| Q4 | Dòng nhắc ngắn chỉ ở phase `implement`, 6 mã | `(cd tests && python3 -m unittest test_prompt_context test_common)` | `Ran 46 tests … OK` | PASS |
| Q5 | Kênh sub-agent, `hooks.json` 6 mục/5 sự kiện | `(cd tests && python3 -m unittest test_subagent_start)` | `Ran 11 tests … OK` | PASS |
| Q6 | Khoá `muc_gat` qua CLI, mọi đường lỗi ra `full` | `(cd tests && TDQ_PROJECT_DIR=$(mktemp -d) python3 -m unittest test_state_muc_gat)` | `Ran 10 tests … OK` | PASS |
| Q7 | Skill `tdq-lean` ba chế độ, router đọc tới được | `(cd tests && python3 -m unittest test_skill_lean)` | `Ran 9 tests … OK` | PASS |
| Q8 | Cổng nợ marker, không framework không fixture | `(cd tests && python3 -m unittest test_kiem_no_marker)` · `python3 scripts/kiem_no_marker.py` | `Ran 15 tests … OK` · `1 marker(s), 0 missing`, exit 0 | PASS |
| Q9 | Đo bằng hiệu ứng thật, thân luật in đúng một lần | `(cd tests && python3 -m unittest test_kenh_luat_dedupe)` + bảng 4 mức của T5.2 | `Ran 14 tests … OK` · bảng dán ở dưới | PASS |
| Q10 | Bản portable sinh lại, `kien-truc.md` ghi 6 hook | `python3 scripts/build_portable.py` · `grep -c '6 hook' docs/kien-truc.md` | exit 0, 104/156/94 file · `1` | PASS |
| Q11 | Tập test đỏ lệch 0 so với baseline `main` | `python3 -m unittest discover tests` hai bên, `comm` hai chiều · `grep -c 2026-09-17` hai file test | 11 tên đỏ cả hai bên, `comm` rỗng hai chiều · `7` và `4` | PASS |
| Q12 | Không ghi ra ngoài repo, Ponytail không bị sửa | `git -C ~/Documents/ponytail status --porcelain` | rỗng — **đỏ lúc đầu vòng 1, xanh sau QC1.1** | PASS |
| Q13 | Luật món 8 được giữ, không class thừa | `grep -c '^class '` ba file mới + đọc tay | `0` cả ba · đọc tay ghi ở dưới | PASS |
| QC-F1 | Toàn bộ suite, đúng một lần | `python3 -m unittest discover tests` | `Ran 1907 tests in 114.458s` · `FAILED (failures=290, errors=4, skipped=14)` | PASS |
| QC-F2 | Hồi quy vùng `Chạm:` | test của từng module bị chạm | 16 module, 15 xanh, 1 đỏ đúng bằng `main` | PASS |
| QC-F3 | Ràng buộc kiến trúc spec §5 | 11 phép kiểm, liệt kê ở dưới | 11/11 giữ | PASS |
| QC-F4 | Clean code 5 câu SOLID | đọc tay ba file mới | 5/5 "có", không phải sửa gì | PASS |

## Bằng chứng

### Q11 — lệch 0 so với baseline `main`

Nhánh (cây làm việc hiện tại) và `main` sạch (worktree tách rời tại `4faed21`), cả hai chạy
**không** export `TDQ_PROJECT_DIR`:

```
nhánh: Ran 1907 tests in 114.458s
       FAILED (failures=290, errors=4, skipped=14)      → 11 tên đỏ
main:  Ran 1802 tests in 112.848s
       FAILED (failures=290, errors=4, skipped=15)      → 11 tên đỏ

comm -23 nhanh main  → rỗng   (không có tên nào đỏ riêng trên nhánh)
comm -13 nhanh main  → rỗng   (không có tên nào nhánh đã sửa)
```

Nhánh chạy hơn `main` **105 test**, tất cả xanh — đó là test lượt này thêm. Mười một tên đỏ
trùng nhau là nợ sẵn có của `main`:

```
test_doc_dup.LogTest.test_bang_luon_ra_stdout_ke_ca_khi_tat_log
test_doc_dup.LogTest.test_bien_moi_truong_tat_duoc_log
test_doc_dup.LogTest.test_co_quiet_thi_stderr_rong
test_doc_dup.ThoatTest.test_chay_xong_thoat_0
test_doc_dup.TokenTest.test_cap_trung_co_so_token_lon_hon_khong
test_rules_library.ChiMuc.test_chi_muc
test_skill_router.KhoTest.test_moi_duong_dan_khac_rong_deu_mo_duoc
test_skill_router.KhoTest.test_so_ban_ghi_khop_skill_inventory
test_token_audit.UsageTotalsTest.test_cong_don_usage_va_dem_api_call
unittest.loader._FailedTest.test_check_canvas_layout
unittest.loader._FailedTest.test_team_chong_conflict
```

**Cách đếm tên** (ghi lại vì lần đầu trong phase implement tôi đếm sai): `unittest` in subtest
thành `FAIL: test_x (module.Class.test_x) [tham số]`. Tên phải bóc từ đường dẫn trong ngoặc và
bỏ phần `[tham số]`. Đếm cả tham số thì riêng `test_skill_router` hoá thành 285 "tên".

Hai file test có ghi chú lý do + ngày cho ba assertion trần bị sửa:
`tests/test_context_hooks.py` 7 lần chuỗi `2026-09-17`, `tests/test_token_budget.py` 4 lần.

### Q9 — bảng 4 mức gắt, đo bằng đầu ra thật của hook (chép từ T5.2)

Chạy `session_start.py` bằng payload thật, mỗi mức một `session_id` riêng để dedupe không che
lần sau; giá trị mức đọc THẲNG từ `docs/tdq/state.json` chứ không tin dòng khai.

| `muc_gat` | Giá trị trên đĩa | Số dòng thân luật hook in ra | `so_dong` trong sổ lượt |
|---|---|---|---|
| `off` | `off` | 0 | không có dòng nào |
| `lite` | `lite` | 72 | 72 |
| `full` | `full` | 133 | 133 |
| `ultra` | `ultra` | 139 | 139 |

Bốn mức ra bốn số khác nhau, `off` ra 0, `so_dong` khớp đầu ra thật từng mức.

### Q12 — đỏ thật ở vòng 1, đã vá bằng QC1.1

```
$ git -C ~/Documents/ponytail status --porcelain
?? docs/tdq/
```

Nguyên nhân: lúc phase analyze, cwd của vài lượt là `~/Documents/ponytail`, nên hook TDQ
(`resolve_project_dir` lấy `cwd` của payload) tạo `docs/tdq/` ở ĐÓ rồi ghi hai file nháp của
phiên: `.tdq-prompt-last.json` và `.tdq-turn.jsonl`. Đã đọc kiểm cả hai trước khi xoá — chỉ
chứa `session`, `digest`, mốc thời gian và đường dẫn tương đối, không có nội dung của Ponytail
và không có khoá bí mật. **Không file nào của Ponytail bị sửa**: `git diff` rỗng cả trước lẫn
sau. Sau khi xoá `docs/tdq/`:

```
$ git -C ~/Documents/ponytail status --porcelain     → rỗng
$ git -C ~/Documents/ponytail diff --stat            → rỗng
```

[XÁC THỰC] Gốc của việc này nằm **ngoài phạm vi** request: hook ghi state theo project của cwd
là thiết kế sẵn có của plugin. Đọc một repo bên thứ ba khi TDQ đang cài sẽ luôn để lại nháp ở
đó, nên phép kiểm Q12 phải chạy ở CUỐI lượt.

### Q13 — đọc tay ba file mới

| File | Dòng | `class` | Hàm top-level | Chuỗi gọi dài nhất |
|---|---|---|---|---|
| `hooks/scripts/luat_gon.py` | 76 | 0 | 2 | `session_start` → `doc_than_luat` → `loc_than_luat` = 2 nhịp |
| `hooks/scripts/subagent_start.py` | 55 | 0 | 1 | `main` → `doc_than_luat`/`loc_than_luat` = 2 nhịp |
| `scripts/kiem_no_marker.py` | 135 | 0 | 8 | `main` → `quet` → `scan_file` → `marker_text` = 3 nhịp |

Không file nào quá 3 nhịp, đúng ngưỡng món 8. Phức tạp: hàm nặng nhất là `main` của
`kiem_no_marker.py` — một vòng `for` ba nhánh cộng hai `if` phẳng, không lồng quá một tầng, nên
dưới sàn `cyclomatic ≤ 10 / cognitive ≤ 15`. `loc_than_luat` là một vòng `for` hai `if` phẳng.
Không hàm nào cần tách.

### QC-F2 — hồi quy vùng `Chạm:`

Mỗi dòng `Chạm:` của plan → test của module giữ node bị ảnh hưởng:

```
test_than_luat           Ran  7 tests  OK        test_build_portable      Ran 61 tests  OK
test_luat_gon            Ran 11 tests  OK        test_log_kenh_luat       Ran 10 tests  OK
test_context_hooks +
  test_token_budget      Ran 43 tests  OK        test_luat_skill          Ran 11 tests  OK
test_prompt_context +
  test_common            Ran 46 tests  OK        test_luat_gate_chat      Ran  7 tests  OK
test_subagent_start      Ran 11 tests  OK        test_tdq_lsp_skill       Ran  5 tests  OK
test_skill_lean          Ran  9 tests  OK        test_reference_mot_tang  Ran  4 tests  OK
test_kiem_no_marker      Ran 15 tests  OK        test_state_muc_gat       Ran 10 tests  OK
test_kenh_luat_dedupe    Ran 14 tests  OK
```

Một module đỏ, đúng bằng `main` chứ không phải hồi quy của lượt này:

```
test_skill_router   Ran 18 tests   FAILED (failures=285)
   → đúng 2 tên đỏ: test_moi_duong_dan_khac_rong_deu_mo_duoc, test_so_ban_ghi_khop_skill_inventory
```

Không có node nào thiếu test, nên không có dòng `KHÔNG CÓ TEST` nào.

### QC-F3 — 11 ràng buộc kiến trúc của spec §5

| Ràng buộc | Phép kiểm | Kết quả |
|---|---|---|
| `kien-truc.md:12` luật là văn bản, không chạy được | `grep -nE '^(import |def |class )' chung.md` | 5 dòng, cả 5 nằm TRONG fence ```` ``` ```` (ví dụ RIGHT/WRONG), không phải cơ chế |
| `kien-truc.md:13` bản portable SINH, cấm sửa tay | `python3 scripts/build_portable.py` | exit 0, sinh lại 104/156/94 file |
| `kien-truc.md:15` số hook | `hooks.json` đếm bằng `json` | `6 muc / 5 su kien`, `docs/kien-truc.md` ghi "6 hook" |
| `kien-truc.md:25` chỉ `tdq_state.py` ghi state | `grep -c state.json` ba file mới | `0` cả ba |
| `kien-truc.md:26` file code mới ở `scripts/` hoặc `hooks/` | liệt kê đường dẫn | `hooks/scripts/luat_gon.py`, `hooks/scripts/subagent_start.py`, `scripts/kiem_no_marker.py` |
| `kien-truc.md:49` không chạm `soul.md` | `git diff --stat main -- …/soul.md` | rỗng |
| `kien-truc.md:51` luật trong `skills/` viết tiếng Anh | `i18n_check` trên `chung.md` | 0 dòng tiếng Việt, exit 0 |
| `soul.md:99` tầng 1–2 ở thân, tầng 3 ở reference | `test_than_luat` + `test_luat_skill` | cả hai xanh |
| `_common.py:70` mã thứ sáu phải khai trong spec trước | `grep -c 'TDQ:GON'` | spec 3 lần, `_common.py` 2 lần |
| `session_start.py:8` trần khối đầu 12 dòng/600 ký tự | `test_token_budget` | xanh, số trần cũ không bị hạ |
| Không thêm dependency ngoài stdlib | `grep '^import\|^from'` ba file mới | chỉ `os`, `sys`, `datetime` và module nội bộ của repo |

### QC-F4 — 5 câu SOLID cho ba file mới

- **SRP — có.** `doc_than_luat` chỉ đọc đĩa, `loc_than_luat` chỉ lọc chuỗi, `marker_text` chỉ
  bóc chữ, `has_upgrade_path` chỉ phán quyết. Mỗi hàm một lý do để đổi.
- **OCP — có.** Thêm một mức gắt = thêm một dòng vào `CAT_THEO_MUC`; thêm một đuôi file cần
  quét = thêm một phần tử vào `SCAN_SUFFIXES`. Không phải mở thân hàm nào.
- **LSP — có.** Không có kế thừa. Mọi nhánh `return` của `doc_than_luat` trả `str`
  (`""` khi lỗi), `scan_file` luôn trả `list`, `main` luôn trả `int` — cùng kiểu, cùng hợp
  đồng lỗi.
- **ISP — có.** Mọi tham số đều được dùng trong thân hàm; không hàm nào nhận tham số để đó.
- **DIP — có.** Ba kênh đều đi qua `luat_gon.py` chứ không tự đọc lại file luật; mức gắt đọc
  qua `tdq_state.muc_gat_hieu_luc`, không hàm nào tự parse `state.json`.

Không câu nào "không", nên không phải sửa mã ở vòng QC.

## Kết luận

**PASS toàn bộ** — 13 hạng mục DoD và 4 hạng mục cố định đều PASS.

Một hạng mục đỏ thật ở đầu vòng 1: **Q12**, do lượt này để rác hook trong repo bên thứ ba
Ponytail. Đã thêm task vá **QC1.1** vào plan, làm xong và tick trong cùng vòng; không cần vòng
2. Nợ mang sang report: 11 tên test đỏ có sẵn trên `main` (không thuộc phạm vi request này) và
`tdq-lean` chỉ vào `docs/tdq/audit/skill-index.json` sau lần cài plugin kế tiếp.
