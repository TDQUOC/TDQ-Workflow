# PLAN — Vá điểm mù verify-by-effect (0.3.1)

Spec: `../spec/2026-07-29-turn-effect-blindspot.md` (đã duyệt 2026-07-29) · Trạng thái plan: **HOÀN THÀNH** (QC PASS 12/12)

Nguyên tắc: mỗi task có test riêng, đi **red → green**; pass là tick `[x]` ngay.
Thứ tự phụ thuộc: P1 (helper) → P2 (ghi snapshot) → P3 (đối chiếu) → P4 (doc/đóng gói) → P5 (QC).

## P1 — Helper trong `scripts/tdq_state.py`

- [x] **T1.1** `repo_status_digest(cwd)` → `str|None`
  - Chạy `git -C <cwd> status --porcelain` qua `subprocess.run(timeout=2, capture_output=True)`;
    băm stdout bằng `sha256`. rc≠0 / `FileNotFoundError` / `TimeoutExpired` / mọi `OSError` → `None`.
  - Test `tests/test_turn_snapshot.py::test_digest_changes_on_new_file`: `git init` trong tmpdir,
    lấy digest, tạo file mới, lấy lại → khác nhau.
  - Test `…::test_digest_none_outside_git`: tmpdir không phải git repo → `None`, không raise.
- [x] **T1.2** `turn_snapshot(cwd)` → `{"log_rel","log_sha","repo_sha"}`
  - `log_rel` = `docs/workinglog/<hôm nay>.md`; `log_sha` = `sha256_file` hoặc `None` khi chưa có file.
  - Test `…::test_snapshot_without_log_file` và `…::test_snapshot_with_log_file` (sha khớp `sha256_file`).

## P2 — Ghi ảnh chụp đầu turn (`hooks/scripts/prompt_context.py`)

- [x] **T2.1** Sau `turn_log_clear`, `turn_log_append(cwd, "turn_start", session=…, **turn_snapshot(cwd))`
  - Test `tests/test_turn_ledger.py::test_prompt_context_writes_turn_start`: chạy hook, đọc sổ turn,
    đúng **1** dòng `kind="turn_start"`, đúng session, có đủ 3 khoá.
- [x] **T2.2** Không hồi quy ngân sách/hành vi
  - Test cũ `test_context_hooks` + `test_token_budget` vẫn xanh (snapshot không in ra context).

## P3 — Đối chiếu cuối turn (`hooks/scripts/stop_gate.py`)

- [x] **T3.1** Đọc dòng `turn_start` đầu tiên của session; thiếu → `snapshot = None`.
  - Test `tests/test_stop_gate.py::test_no_snapshot_behaves_like_030`: không có `turn_start`,
    có `observe edit`, không `log_written` → vẫn chặn `[TDQ:LOG]` (hành vi 0.3.0).
- [x] **T3.2** `logged` = `observe log_written` **hoặc** log đã đổi trên đĩa
  - Đổi = `sha256(log_rel hiện tại) != log_sha`, **hoặc** log của ngày hiện tại tồn tại mà
    `log_rel` trong snapshot là ngày khác (turn qua nửa đêm).
  - Test `…::test_shell_append_log_not_blocked` (**chặn oan — bug gốc**): snapshot có log_sha,
    ghi thêm vào file log bằng `open(...,"a")` (không qua Edit), có `observe edit` → **không** chặn.
- [x] **T3.3** `edited` = `observe edit` (ngoài `docs/workinglog`) **hoặc** `repo_sha` đã đổi
  - Test `…::test_shell_only_change_is_blocked` (**bỏ lọt**): repo git, snapshot, tạo `src/a.py`
    bằng Python (không `observe` nào), không ghi log → chặn `[TDQ:LOG]`.
- [x] **T3.4** Tên file trong `reason`: ưu tiên path từ `observe edit`; không có thì lấy path đầu
  trong `git status --porcelain` khác đầu turn; cắt ≤60 ký tự; không có gì thì ghi `repo`.
  - Test `…::test_block_reason_names_shell_created_file`: reason chứa `src/a.py`.
- [x] **T3.5** Repo không phải git (`repo_sha=None`): chiều `logged` vẫn vá được, chiều `edited`
  giữ nguyên 0.3.0.
  - Test `…::test_non_git_repo_log_via_shell_not_blocked`.
- [x] **T3.6** Không hồi quy: toàn bộ `test_stop_gate` + `test_e2e_chain` cũ vẫn xanh.
- [x] **T3.7** Resilience: `stop_gate` không raise khi `turn_start` méo (thiếu khoá, sai kiểu).
  - Test `…::test_malformed_turn_start_row` → exit 0, không traceback.

## P4 — Doc & đóng gói 0.3.1

- [x] **T4.1** `skills/tdq-conventions/references/reminder-codes.md`: mô tả `TDQ:LOG` được xác minh
  bằng ledger **hoặc** hiệu ứng trên đĩa; nêu giới hạn khi project không phải git repo.
- [x] **T4.2** Đồng bộ y hệt sang `portable/workflow/references/reminder-codes.md`
  (`test_portable_sync` + `doc_lint.py skills portable` exit 0).
- [x] **T4.3** `README.md` mục verify-by-effect: hook nhìn **hiệu ứng trên đĩa**, không nhìn tên tool.
- [x] **T4.4** `CHANGELOG.md`: mục `## 0.3.1` — sửa chặn oan `[TDQ:LOG]` + bịt lỗ bỏ lọt shell-only.
- [x] **T4.5** `.claude-plugin/plugin.json` → `0.3.1`; `claude plugin validate . --strict` PASS
  (`test_docs_consistency` khoá version ↔ changelog).
- [x] **T4.6** Gỡ + cài lại plugin user-level để cache lấy 0.3.1 (uninstall → `rm -rf` cache 0.3.0 → install).

## Task phát sinh từ QC

- [x] **QC1.1** Vân tay repo bỏ lọt khi **sửa nội dung file untracked**: `status --porcelain`
  vẫn in `?? path` y hệt, còn `diff HEAD` không đụng tới file untracked (và repo chưa có
  commit thì không có `HEAD`). Smoke (b) vì thế không chặn dù `sed -i` đã đổi file thật.
  - Sửa: `repo_status_digest` băm thêm `size:mtime_ns` của các path `??` (cap 200 file).
  - Test `tests/test_turn_snapshot.py::test_digest_catches_edit_of_untracked_file`.

## P5 — QC & report

- [x] **T5.1** `python3 -m unittest discover tests` → OK, tổng ≥ 172 test.
- [x] **T5.2** `python3 scripts/doc_lint.py skills portable` → exit 0.
- [x] **T5.3** Smoke trên bản cài user-level (mỗi lệnh đặt `TDQ_PROJECT_DIR` riêng):
  (a) mở turn → `cat >>` vào log hôm nay → Stop **không** chặn;
  (b) mở turn → `sed -i` sửa 1 file code, không ghi log → Stop **chặn**;
  (c) đo thời gian thật của `git status --porcelain` trên repo này, ghi số vào QC.
- [x] **T5.4** Viết `docs/tdq/qc/2026-07-29-turn-effect-blindspot.md` (bảng hạng mục + bằng chứng).
- [x] **T5.5** Viết `docs/tdq/reports/2026-07-29-turn-effect-blindspot.md` (≤50 dòng).
- [x] **T5.6** Append working log 2026-07-29; chạy `graphify extract . --code-only`; hỏi user về commit.

## Definition of Done

Đúng 7 mục §7 của spec. QC fail → thêm task fix vào plan này (không cần duyệt lại) và loop đến khi pass.

## Việc chờ user (không nằm trong DoD)

- `tdq_state.py init 2026-07-29-turn-effect-blindspot full` sẽ xoá state của request trước.
- T7.2 của plan 0.3.0: sửa `~/.claude/CLAUDE.md` §10.
- Commit mốc 0.3.0 trước khi bắt tay fix.
