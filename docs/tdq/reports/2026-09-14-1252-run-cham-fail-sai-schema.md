# REPORT — `run` chấm fail dù Codex làm đúng (`2026-09-14-1252-run-cham-fail-sai-schema` · lane full · mode main · 10 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 `scripts/tdq_codex.py`: bóc đúng 1 rào code bọc trọn file (nhãn rỗng/`json`) · chỉ `xong` là boolean `true` mới tính xong · tập mã lý do đóng `MA_LY_DO` (6 mã) · schema thêm `additionalProperties: false` · dòng log của lượt không xong có đuôi `· ly_do=<mã>` · P2 test bench đọc dòng log thật · P3 luật `codex-mode.md` (khuôn prompt đòi JSON trần, 3 luật đọc kết quả) + sinh lại bundle · P4 test + 2 lượt Codex thật
**Kết quả:** dạng JSON bọc rào: `fail` → `xong` · `{"xong": false}`: trước chấm `xong` (chỉ kiểm có khoá) → nay `fail` kèm `ly_do=model-bao-chua-xong` · lượt thật Q10 `xong` 27.1s, Q11 `fail` 61.4s
**Kiểm:** `test_codex_run.py` 54 OK · `test_codex_*.py` 104 OK · `test_bench.py` 46 OK · `test_build_portable.py` 61 OK · i18n 0 dòng · doc_lint 0 vi phạm · QC PASS 12/12 DoD + 4/4 mục cố định, 0 vòng fix
**Đầu ra:** `scripts/tdq_codex.py` · `tests/test_codex_run.py` · `tests/test_bench.py` · `skills/tdq-build/references/codex-mode.md` · 3 bundle · QC: `docs/tdq/qc/2026-09-14-1252-run-cham-fail-sai-schema.md`
**Giới hạn:** bộ đầy đủ 1785 test 293 fail/4 error, mốc HEAD 1771 test 290/4: 3 fail thêm ở `test_codex_edit_gate.TestChanNgoaiVung` do test gọi hook thật vào sổ lượt của repo, hook chặn TICK từ lượt sửa thứ 3 khi repo đang implement/qc (đã chứng minh: chạy lần 1 OK, lần 2 FAIL; hook và test không đổi) → nợ cô lập test, ngoài phạm vi · `_cli_run` chưa có test đơn vị đầu-cuối, chỉ được phủ bằng lượt thật · `portable_codex.zip` không sinh lại (không ai sinh/đọc, không chứa `tdq_codex.py`) · ruff chưa kiểm (máy không có) · plan ghi nhầm "6 test cũ `PhanQuyetTest`", thực tế là 5
**Git:** chưa commit · nhánh `bugfix/run-cham-fail-sai-schema`, hợp về `main`

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 21s | 20s | 1 |
| analyze | 11 min | 11 min | 1 |
| spec | 7 min | 5 min | 1 |
| plan | 7 min | 7 min | 1 |
| implement | 25 min | 25 min | 1 |
| qc | 13s | 12s | 1 |
| report | 0s | 0s | 1 |
| **Total** | **50 min** | **50 min** | |

Phase `qc` hiện 13s vì file QC và bằng chứng được soạn cuối phase implement, trước lệnh chuyển phase.
