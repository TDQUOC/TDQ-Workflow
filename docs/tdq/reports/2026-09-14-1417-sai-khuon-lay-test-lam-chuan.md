# REPORT — Sai khuôn lấy test làm chuẩn (`2026-09-14-1417-sai-khuon-lay-test-lam-chuan` · lane full · mode main · 12 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 `tdq_codex.py`: hằng `MA_LY_DO_CHAY_LAI_TEST` (2 mã) + `can_chay_lai_test` + `dung_phan_quyet`, JSON của `run` thêm `ly_do`, `can_chay_lai_test` · P2 test đầu-cuối `RunDauCuoiTest` (Codex giả, `CODEX_HOME` giả) · P3 luật `codex-mode.md` bước 4/6 + mục tự kiểm 6, checklist mode `codex` trong `tdq_state.py`, sinh lại 3 bundle · P4 ca log `TDQ_LOG=0`, 2 lượt Codex thật, hồi quy · P5 bump 0.47.0, chuyển mục 0.26.0 sang archive.
**Kết quả:** JSON phán quyết 3 → 5 khoá · lượt sai khuôn: trước bị tính fail cứng → nay leader chạy lại test, xanh thì tick kèm `(cứu bằng test · ly_do=<mã>)` · lượt thật Q8 (`ag/gemini-3.8-flash-medium`) ra `fail`/`ket-qua-sai-khuon`/`true` ở lượt 1, test chạy lại xanh · `CHANGELOG.md` 498 → 492 dòng.
**Kiểm:** module `test_codex_*` 121 OK · `test_bench` 46 OK · `test_state` 56 OK · bộ đầy đủ nhánh 1802 test/290 fail/4 error vs HEAD 1785/291/4, 0 fail/error chỉ ở nhánh · doc_lint 0 · QC PASS 10/10 DoD + 4/4 mục cố định, 0 vòng fix.
**Đầu ra:** `scripts/tdq_codex.py` · `skills/tdq-build/references/codex-mode.md` · `tests/test_codex_run.py`, `tests/test_codex_cli.py` · QC: `docs/tdq/qc/2026-09-14-1417-sai-khuon-lay-test-lam-chuan.md` · Backup: không sửa ngoài repo.
**Giới hạn:** bộ đầy đủ vẫn còn ~290 fail/4 error có sẵn từ trước (không thuộc request này) · `test_codex_edit_gate.TestChanNgoaiVung` lệch 3 test khi chạy cả bộ lúc đang implement, chạy riêng xanh — nợ kỹ thuật về cô lập test · `i18n_check scripts/tdq_state.py` còn 7 dòng tiếng Việt có sẵn ở HEAD · T5.0 tách khỏi T5.1 giữa chừng vì cổng TICK, ghi rõ trong plan · lint Python chưa kiểm (máy không có `ruff`).
**Git:** commit trên `feature/sai-khuon-lay-test-lam-chuan`, merge `--no-ff` vào `main`, xoá nhánh, commit sổ trạng thái — đã uỷ quyền trước ("1a và merge vào main và pump version và commit") · không push.

## Thời gian

Request `2026-09-14-1417-sai-khuon-lay-test-lam-chuan` · lane full · opened at 2026-09-14T14:19:04+07:00

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 10 min | 19s | 1 |
| analyze | 7 min | 7 min | 1 |
| spec | 5 min | 4 min | 1 |
| plan | 47 min | 9 min | 1 |
| implement | 20 min | 20 min | 1 |
| qc | 20s | 18s | 1 |
| **Total** | **1h 29min** | **42 min** | |
