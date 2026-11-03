# REPORT — Tách nhánh dev để phát triển và nhánh main để phát hành sạch (`2026-10-14-1713-tach-nhanh-dev-main-release` · lane full · mode main · 6 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 mở rộng `scripts/build_portable.py` với bộ lọc đường dẫn release (`RELEASE_EXCLUDE_DIRS`, `RELEASE_EXCLUDE_FILES`, `RELEASE_EXCLUDE_SCRIPTS`, `la_duong_dan_release`, `loc_muc_ls_tree`) và chế độ phát hành nhánh `main` sạch (`--sinh-main [--nguon] [--nhanh-dich] [--dry-run]`) qua Git plumbing trên `GIT_INDEX_FILE` tạm (`git ls-tree -r -z`, `git update-index -z --index-info`, `git write-tree`, `git commit-tree`, `git update-ref`) · P2 bổ sung `nhanh_goc_mac_dinh(repo)` vào `scripts/tdq_test.py` tự động ưu tiên nhánh gốc `dev` khi `refs/heads/dev` tồn tại · P3 cập nhật quy ước mô hình 2 nhánh `dev` (develop) và `main` (release sạch) trong `skills/tdq-intake/references/nhanh-request.md`, `docs/kien-truc.md` và khóa `docs/tdq/token-budget.json` · P4 kiểm chứng Log service bật mặc định (`TDQ_LOG=0` tắt), bao đóng AST 35 script runtime và xử lý 2 task QC (`QC1.1`, `QC1.2`).
**Kết quả:** Số file trên nhánh release `main` giảm từ `1,472 files (~19.8 MB)` xuống `136 files (~1.15 MB)` (giảm `90.8%` số file và `93.5%` dung lượng, loại bỏ toàn bộ `docs/`, `tests/`, `evals/`, `graphify-out/`, `.taskmaster/`, `tools_kiem/`, `.github/`, `CHANGELOG-archive.md`, `pyrightconfig.json`, `scripts/samples/` và 12 script dev-only; bảo toàn 100% bao đóng 35 script runtime) · Tạo commit snapshot trên `main` mất `~0.12s`, idempotent khi cây runtime không đổi và không chạm working tree.
**Kiểm:** `python scripts/tdq_test.py tron-bo` 133 modules / 2,580 tests OK (`skipped=9`, `failed=0`, `missed=0`) · `doc_lint.py` 0 vi phạm · `token_budget.py --kiem` 50/50 file khớp khóa · `i18n_check.py` 0 dòng vi phạm · QC PASS 4/4 mục DoD (`Q1`–`Q4`) và 4/4 mục cố định (`QC-F1`–`QC-F4`), đã sửa 2 defect tồn đọng (`QC1.1`, `QC1.2`).
**Đầu ra:** `scripts/build_portable.py` · `scripts/tdq_test.py` · `skills/tdq-intake/references/nhanh-request.md` · `docs/kien-truc.md` · `tests/test_build_portable.py` · `tests/test_tdq_test.py` · `docs/tdq/qc/2026-10-14-1713-tach-nhanh-dev-main-release.md` · Backup: không có.
**Giới hạn:** Nhánh `dev` và nhánh `main` sạch sẽ được khởi tạo/xuất bản ngay sau khi bạn duyệt commit và gộp nhánh request `feature/tach-nhanh-dev-main-release` theo đúng phạm vi `1a` đã chốt.
**Lệch spec chờ duyệt:** không có.
**Git:** chưa commit (đang ở nhánh `feature/tach-nhanh-dev-main-release`).

## Thời gian

Request `2026-10-14-1713-tach-nhanh-dev-main-release` · lane full · opened at 2026-10-14T17:15:01+07:00

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 0s | — | 1 |
| analyze | 10 min | — | 1 |
| spec | 6 min | — | 1 |
| plan | 3 min | — | 1 |
| implement | 15 min | — | 1 |
| qc | 38 min | — | 1 |
| report | 0s | — | 1 |
| **Total** | **1h 12min** | **—** | |

Model column is `—`: the transcript of this session could not be read.
