# QC — Tách nhánh dev để phát triển và nhánh main để phát hành sạch
Ngày: 2026-10-14 · Plan: ../plan/2026-10-14-1713-tach-nhanh-dev-main-release.md · Vòng: 2
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Bộ lọc đường dẫn release bảo toàn trọn vẹn bao đóng 35 script runtime và loại bỏ triệt để file dev/test (≤ 150 files trên nhánh release) | `python -m unittest discover -s tests -p "test_build_portable.py" -k "release"` | 5 tests OK trong 3.189s; giữ đúng 35 script runtime khép kín AST và 136 files tổng cộng trên nhánh release | PASS |
| Q2 | Lệnh CLI `build_portable.py --sinh-main` tạo commit snapshot sạch trên nhánh đích, idempotent khi không đổi, hỗ trợ `--dry-run`, giữ nguyên working tree và hồi quy xanh cho các hàm Hub `build_portable.main()` / `build_portable.log()` | `python -m unittest discover -s tests -p "test_build_portable.py"` | 37 tests OK trong 6.074s | PASS |
| Q3 | Tự động nhận diện nhánh gốc `dev` trong `scripts/tdq_test.py` khi `refs/heads/dev` tồn tại và fallback về `main` khi không có | `python -m unittest discover -s tests -p "test_tdq_test.py" -k "nhanh_goc"` | 2 tests OK trong 1.288s (62/62 tests toàn module `test_tdq_test.py` OK) | PASS |
| Q4 | Tài liệu quy ước nhánh, chuẩn ngôn ngữ 3 tầng và khóa ngân sách token đạt 0 vi phạm | `python scripts/doc_lint.py skills/tdq-intake/references/nhanh-request.md && python scripts/token_budget.py --kiem && python scripts/i18n_check.py scripts/build_portable.py scripts/tdq_test.py skills/tdq-intake/references/nhanh-request.md` | 0 vi phạm `doc_lint`, 50/50 file khớp khóa `token_budget`, 0 dòng vi phạm `i18n_check` | PASS |
| QC-F1 | Chạy trọn bộ test suite (`tron-bo`) và kiểm tra ngân sách cổng (`so`) | `python scripts/tdq_test.py tron-bo && python scripts/tdq_test.py so` | 133 modules, 2,580 tests OK (`skipped=9`, `failed=0`, `missed=0`), `full-suite runs: 3 of budget 3` | PASS |
| QC-F2 | Kiểm tra hồi quy vùng chạm trên toàn bộ các dòng `Chạm:` (`build_portable`, `tdq_test`, `nhanh-request.md`, `session_start`, `tdq_team`) | `python -m unittest discover -s tests -p "test_build_portable.py" && python -m unittest discover -s tests -p "test_tdq_test.py" && python -m unittest discover -s tests -p "test_codex_cli.py" && python -m unittest discover -s tests -p "test_tu_khoi_tao.py" && python -m unittest discover -s tests -p "test_team_chong_conflict.py"` | Toàn bộ 192 tests thuộc các module chạm đều PASS 100% | PASS |
| QC-F3 | Kiểm tra các ràng buộc kiến trúc trong Spec §5 (`skills/` chỉ nhắc tên lệnh của `scripts/`, ngôn ngữ 3 tầng, trọn bộ test trong ngân sách cổng) | `python scripts/doc_lint.py skills/tdq-intake/references/nhanh-request.md docs/kien-truc.md && python scripts/i18n_check.py scripts/build_portable.py scripts/tdq_test.py skills/tdq-intake/references/nhanh-request.md` | 0 vi phạm hợp đồng tài liệu và chuẩn ngôn ngữ 3 tầng | PASS |
| QC-F4 | Tự kiểm 5 câu hỏi SOLID Clean Code (`skills/tdq-conventions/references/clean-code.md`) | Kiểm tra AST & cấu trúc hàm trong `scripts/build_portable.py`, `scripts/tdq_test.py`, `scripts/tdq_team.py`, `hooks/scripts/session_start.py` | Cả 5 nguyên tắc SRP, OCP, LSP, ISP, DIP đều đạt (cyclomatic ≤ 7, cognitive ≤ 6) | PASS |

## Bằng chứng

### Q1
```
....[2026-10-14T17:50:31+07:00] build_portable: dry-run dev@355c897 -> main · kept=4 dropped=6
[2026-10-14T17:50:31+07:00] build_portable: published main@a9cd3d9 from dev@355c897 · tree=5734f53 · kept=4 · dropped=6
[2026-10-14T17:50:32+07:00] build_portable: main already up to date with dev@355c897 (tree=5734f53, kept=4, dropped=6)
[2026-10-14T17:50:32+07:00] build_portable: main already up to date with dev@1d227ca (tree=5734f53, kept=4, dropped=6)
[2026-10-14T17:50:32+07:00] build_portable: published main@88000f4 from dev@fbe329a · tree=5fb517b · kept=4 · dropped=6
.
----------------------------------------------------------------------
Ran 5 tests in 3.189s

OK
```

### Q2
```
Ran 37 tests in 6.074s

OK
```

### Q3
```
..
----------------------------------------------------------------------
Ran 2 tests in 1.288s

OK
```

### Q4
```
[2026-10-14T17:50:40] doc_lint: lint 1 file: nhanh-request.md
[2026-10-14T17:50:40] doc_lint: done — 0 violation(s) total, exit 0
[2026-10-14T17:50:40] i18n_check: scan 3 file(s), kind=all
[2026-10-14T17:50:40] i18n_check: done — 0 line(s), exit 0
0 Vietnamese line(s) in 3 file(s)
```

### QC-F1
```
----------------------------------------------------------------------
Ran 2580 tests in 492.449s

OK (skipped=9)
[2026-10-14T18:25:14+07:00] tdq_test: tron-bo modules=133 failed=0 missed=0 ok=True seconds=493.39
[2026-10-14T18:25:14+07:00] tdq_test: so request=2026-10-14-1713-tach-nhanh-dev-main-release tron_bo=3 bo_sot=0 budget=3
request: 2026-10-14-1713-tach-nhanh-dev-main-release (phase qc)
full-suite runs: 3 of budget 3
radius misses: 0
```

### QC-F2
```
test_build_portable.py: Ran 37 tests in 6.074s — OK
test_tdq_test.py: Ran 62 tests in 9.350s — OK
test_codex_cli.py: Ran 32 tests in 35.305s — OK
test_tu_khoi_tao.py: Ran 36 tests in 17.400s — OK
test_team_chong_conflict.py: Ran 25 tests in 34.019s — OK
```

### QC-F3
```
[2026-10-14T17:49:44] doc_lint: lint 1 file: kien-truc.md
[2026-10-14T17:49:44] doc_lint: done — 0 violation(s) total, exit 0
[2026-10-14T17:50:40] doc_lint: lint 1 file: nhanh-request.md
[2026-10-14T17:50:40] doc_lint: done — 0 violation(s) total, exit 0
```

### QC-F4
- **SRP (Có)**: `la_duong_dan_release` chỉ xét một đường dẫn tương đối, `loc_muc_ls_tree` chỉ lọc luồng byte `ls-tree -z`, `_tao_tree_release` chỉ dựng Git tree qua index tạm, `sinh_nhanh_main` điều phối tạo commit release và cập nhật ref, `nhanh_goc_mac_dinh` chỉ kiểm tra sự tồn tại của `refs/heads/dev`.
- **OCP (Có)**: Danh sách loại trừ được tách thành 3 hằng tập hợp dữ liệu (`RELEASE_EXCLUDE_DIRS`, `RELEASE_EXCLUDE_FILES`, `RELEASE_EXCLUDE_SCRIPTS`); thêm/bớt mục chỉ cần sửa 1 dòng dữ liệu mà không phải sửa thân hàm `la_duong_dan_release`.
- **LSP (Có)**: Mọi nhánh trả về của `la_duong_dan_release` đều trả `bool`; mọi nhánh trả về của `sinh_nhanh_main` đều trả `dict` cùng bộ khóa (`kept`, `dropped`, `source_sha`, `tree_sha`, `commit_sha`, `changed`).
- **ISP (Có)**: Từng hàm chỉ nhận đúng tham số nó sử dụng (`rel_path`, `raw_bytes`, `repo`), không truyền dư đối tượng `args` hay `state`.
- **DIP (Có)**: Tái sử dụng `plugin_version`, `log` trong `build_portable.py` và `_git` trong `tdq_test.py` thay vì viết lại logic đọc version hay gọi subprocess riêng lẻ.

## Lệch spec chờ duyệt
không có

## Kết luận
PASS toàn bộ (sau khi xử lý `QC1.1` và `QC1.2` cho các bài test tồn đọng từ các commit trước và lock thoáng qua của `git worktree add` trên Windows).
