# PLAN — Tách nhánh dev để phát triển và nhánh main để phát hành sạch

Ngày: 2026-10-14 · Spec: ../spec/2026-10-14-1713-tach-nhanh-dev-main-release.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — tdq_bench.py simulate đo 4 task / 2 đợt: subagent 6.1 phút so với main 8.1 phút (lợi 2.0 phút ở hệ số agent 1.5)
Trạng thái plan: HOÀN THÀNH

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Bộ lọc đường dẫn release và chế độ phát hành nhánh `main` sạch (`--sinh-main`)
- P2 — Tự động nhận diện nhánh gốc `dev` trong `scripts/tdq_test.py`
- P3 — Cập nhật tài liệu quy ước 2 nhánh `dev` / `main` và khóa ngân sách token
- P4 — Log & test bắt buộc
- Cụm song song
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Mỗi bước: `tdq_test.py vung-cham`; trọn bộ chỉ ở QC.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Bộ lọc đường dẫn release và chế độ phát hành nhánh `main` sạch (`--sinh-main`)

- [x] **T1.1** (e10m) Mở rộng `scripts/build_portable.py` và bộ unit test `tests/test_build_portable.py` (TDD đỏ → xanh): định nghĩa tập hằng số lọc release (`RELEASE_EXCLUDE_DIRS`, `RELEASE_EXCLUDE_FILES`, `RELEASE_EXCLUDE_SCRIPTS`), hàm `la_duong_dan_release(rel_path)`, `loc_muc_ls_tree(raw_bytes)` và `sinh_nhanh_main(repo, nguon="dev", nhanh_dich="main", dry_run=False)` dùng Git plumbing trên `GIT_INDEX_FILE` tạm (`git ls-tree -r -z`, `git update-index -z --index-info`, `git write-tree`, `git commit-tree`, `git update-ref`), tích hợp cờ CLI `--sinh-main [--nguon] [--nhanh-dich] [--dry-run]` — Test: `python -m unittest tests/test_build_portable.py`
  - Chạm: `scripts/build_portable.py`, `tests/test_build_portable.py` → `build_portable.main()`, `build_portable.log()` (nguồn: `mcp__lsp__blast_radius` trên `scripts/build_portable.py`)

**Xong P1 khi**: `python -m unittest tests/test_build_portable.py` chạy xanh 100% các bài test lọc đường dẫn release, tạo commit `--sinh-main`, tính chất idempotent, `--dry-run` và bảo toàn các chế độ `--sinh-agy`, `--sinh-hook-claude`, `--dest` cũ.

## P2 — Tự động nhận diện nhánh gốc `dev` trong `scripts/tdq_test.py`

- [x] **T2.1** (e6m) Bổ sung hàm `nhanh_goc_mac_dinh(repo)` vào `scripts/tdq_test.py` và unit test trong `tests/test_tdq_test.py` (TDD đỏ → xanh): khi `docs/tdq/state.json` không khai `nhanh_goc`, tự động kiểm tra sự tồn tại của `refs/heads/dev` trong repo để ưu tiên trả về `"dev"` trước khi fallback về `NHANH_GOC_MAC_DINH` (`"main"`) — Test: `python -m unittest tests/test_tdq_test.py`
  - Chạm: `scripts/tdq_test.py`, `tests/test_tdq_test.py` → `tdq_test.cmd_vung_cham` (nguồn: `mcp__lsp__blast_radius` trên `scripts/tdq_test.py`)

**Xong P2 khi**: `python -m unittest tests/test_tdq_test.py` chạy xanh 100% cả trường hợp repo chỉ có `main` lẫn trường hợp repo có cả `dev` và `main`.

## P3 — Cập nhật tài liệu quy ước 2 nhánh `dev` / `main` và khóa ngân sách token

- [x] **T3.1** (e4m) Cập nhật `skills/tdq-intake/references/nhanh-request.md` và `docs/kien-truc.md` ghi nhận quy ước nhánh phát triển `dev` và lệnh xuất bản sang nhánh `main` (`scripts/build_portable.py --sinh-main`), chạy `scripts/doc_index.py --tat-ca` và `scripts/token_budget.py` để đồng bộ `docs/tdq/token-budget.json` — Test: `python scripts/doc_lint.py skills/tdq-intake/references/nhanh-request.md && python scripts/token_budget.py --kiem`
  - Chạm: `skills/tdq-intake/references/nhanh-request.md`, `docs/kien-truc.md`, `docs/tdq/token-budget.json`
  - Cần: T1.1, T2.1

**Xong P3 khi**: `doc_lint.py` và `token_budget.py --kiem` đạt 0 vi phạm.

## P4 — Log & test bắt buộc

- [x] **T4.1** (e4m) Kiểm chứng Log service bật mặc định của `scripts/build_portable.py --sinh-main` (xuất ISO timestamp ra `stderr`, tắt hoàn toàn qua `TDQ_LOG=0`), kiểm tra bao đóng AST 35 script runtime trên nhánh release và kiểm tra `i18n_check.py` trên toàn bộ file chạm — Test: `python -m unittest tests/test_build_portable.py tests/test_tdq_test.py && python scripts/i18n_check.py scripts/build_portable.py scripts/tdq_test.py skills/tdq-intake/references/nhanh-request.md`
  - Chạm: `tests/test_build_portable.py`, `tests/test_tdq_test.py`
  - Cần: T3.1

**Xong P4 khi**: Log service test xanh và `i18n_check.py` đạt 0 vi phạm.

## Cụm song song

- **Đợt 1 (Song song được)**: `T1.1` (chạm `scripts/build_portable.py`, `tests/test_build_portable.py`) và `T2.1` (chạm `scripts/tdq_test.py`, `tests/test_tdq_test.py`) — không giao vùng file.
- **Đợt 2 (Tuần tự sau Đợt 1)**: `T3.1` (cập nhật `skills/tdq-intake/references/nhanh-request.md`, `docs/kien-truc.md` và khóa `docs/tdq/token-budget.json`).
- **Đợt 3 (Tuần tự sau Đợt 2)**: `T4.1` (kiểm chứng log service, bao đóng AST 35 script runtime và `i18n_check.py`).

## Definition of Done

- [x] Q1 Bộ lọc đường dẫn release bảo toàn trọn vẹn bao đóng 35 script runtime và loại bỏ triệt để file dev/test (≤ 150 files trên nhánh release) — `python -m unittest tests/test_build_portable.py -k "release"`
- [x] Q2 Lệnh CLI `build_portable.py --sinh-main` tạo commit snapshot sạch trên nhánh đích, idempotent khi không đổi, hỗ trợ `--dry-run`, giữ nguyên working tree và hồi quy xanh cho các hàm Hub `build_portable.main()` / `build_portable.log()` — `python -m unittest tests/test_build_portable.py`
- [x] Q3 Tự động nhận diện nhánh gốc `dev` trong `scripts/tdq_test.py` khi `refs/heads/dev` tồn tại và fallback về `main` khi không có — `python -m unittest tests/test_tdq_test.py -k "nhanh_goc"`
- [x] Q4 Tài liệu quy ước nhánh, chuẩn ngôn ngữ 3 tầng và khóa ngân sách token đạt 0 vi phạm — `python scripts/doc_lint.py skills/tdq-intake/references/nhanh-request.md && python scripts/token_budget.py --kiem && python scripts/i18n_check.py scripts/build_portable.py scripts/tdq_test.py skills/tdq-intake/references/nhanh-request.md`

## QC vòng 1 — fix

- [x] **QC1.1** (e3m) Kiểm tra `la_project_that(cwd)` trước khi `session_start.py` tự động cập nhật phiên bản, bật `ignore_cleanup_errors=True` cho `TemporaryDirectory` của tiến trình nền detached trong `tests/test_tu_khoi_tao.py` và chuẩn hóa đường dẫn `${CLAUDE_PLUGIN_ROOT}/` trong `tests/test_codex_cli.py` — Test: `python -m unittest discover -s tests -p "test_codex_cli.py" && python -m unittest discover -s tests -p "test_tu_khoi_tao.py"`
  - Chạm: `hooks/scripts/session_start.py`, `tests/test_tu_khoi_tao.py`, `tests/test_codex_cli.py`
- [x] **QC1.2** (e2m) Bổ sung retry ngắn khi `git worktree add` hoặc `.lock` thoáng qua trên Windows trong `scripts/tdq_team.py` — Test: `python -m unittest discover -s tests -p "test_team_chong_conflict.py"`
  - Chạm: `scripts/tdq_team.py`
