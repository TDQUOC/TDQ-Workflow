# REPORT — Mode thứ ba `codex implement` (`2026-09-10-2247-mode-codex-implement` · lane full · mode main · 35/35 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 `tdq_state.py` nhận mode thứ ba (`VALID_MODES`/`MODE_LABELS`, `modes --json` làm nguồn máy đọc được, dòng `cmd` của hàng `mode` SINH từ `VALID_MODES` thay vì gõ tay ba tên) · P2 `scripts/tdq_vungfile.py` mới: `chup-moc`/`hau-kiem`/`hoan-tac`, mốc git theo từng task, đối chiếu `git diff` với vùng file đã khai · P3 `scripts/tdq_codex.py` mới: `check`/`run`/`beat`, một lượt `codex exec`, đọc file kết quả, log 7 mảnh ghi sha256 prompt · P4 `hooks/scripts/codex_edit_gate.py` mới: dịch `apply_patch` và 5 dạng lệnh shell của Codex sang `file_path` cho `edit_gate.py`, deny `[TDQ:VUNG]` khi ghi ngoài vùng hoặc vào vùng khoá · P5 `.codex/hooks.json` viết tay (đúng 2 matcher `PreToolUse`) · P6-P9 tầng luật: `tdq-plan/SKILL.md`, `mode-gate.md` (khối hỏi 3 lựa chọn + khối 2 lựa chọn cho máy không chạy được Codex), `codex-mode.md`, `tdq_bench.py` mô phỏng thêm cột codex · P10 log/test/hồi quy.

**Kết quả:** mode thực thi 2 → 3 · `modes --json` trả 3 hàng kèm `chon_duoc`+`ly_do` (trước: không có lệnh nào máy đọc được) · test mới 7 file, tất cả xanh · số dòng tiếng Việt trong các file request chạm: 227 → 0.

**Kiểm:** 15 module test của DoD đều OK (`discover tests -p "<file>.py"`) · `doc_lint.py --pair` exit 0 · QC 31 hạng mục: 25 PASS, 3 PARTIAL (Q1, Q21b, Q26), 1 SKIP có tuyên bố (Q13), 1 FAIL vì nợ có sẵn (Q24) · `graphify extract . --code-only` 2322 node / 4939 cạnh, `affected` không có node vỡ.

**Đầu ra:** `scripts/tdq_codex.py`, `scripts/tdq_vungfile.py`, `hooks/scripts/codex_edit_gate.py`, `.codex/hooks.json`, `skills/tdq-build/references/codex-mode.md`, 7 file test · QC: `docs/tdq/qc/2026-09-10-2247-mode-codex-implement.md`. Không sửa file nào ngoài repo.

**Giới hạn:** (1) Q13 (sandbox chặn ghi ra ngoài repo) và nửa "biến mốc sống qua sandbox" của Q21b CHƯA chạy: cần một lượt `codex exec` thật, tức cần bạn bật cờ đồng ý — tôi cố ý không bật hộ, vì gọi CLI ngoài là quyết định của bạn. Mở lại bằng `python3 scripts/tdq_checkportable.py setup --codex` rồi `python3 scripts/tdq_codex.py setup-model <ten-model>`. (2) Q24 "suite 0 fail" KHÔNG đạt: suite ở HEAD trước request đã 290 fail / 4 error (đo bằng worktree tách rời), lần chạy sau request ra ĐÚNG cùng danh sách — request thêm 0 fail mới. (3) `i18n_check.py` còn đỏ 207 dòng tiếng Việt cũ ở `scripts/hooks/agents` và 44 dòng ở `skills/tdq-intake|tdq-spec|tdq-plan`, đều nằm ngoài `Chạm:` của request. Vá (2) và (3) nên là request riêng, sửa lẫn vào đây thì không tách được lỗi mới với lỗi cũ. (4) Plan ghi sai tên node Hub `cmd_build()` — `build_portable.py` không có hàm đó; hai node thật đã kiểm là `sinh_ban_codex()` và `_sinh_hooks_codex()`.

**Git:** chưa commit gì. Đang ở nhánh `feature/mode-codex-implement`, gốc `main`.

## Thời gian

Request `2026-09-10-2247-mode-codex-implement` · lane full · opened at 2026-09-10T22:56:56+07:00
| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 7s | 4s | 1 |
| analyze | 52 min | 19 min | 1 |
| spec | 12h 56min | 57 min | 1 |
| plan | 23h 13min | 1h 46min | 1 |
| qc | 3 min | 3 min | 1 |
| report | 40s | 37s | 1 |
| **Total** | **37h 05min** | **3h 05min** | |
