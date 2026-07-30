# PLAN — Vá chặn oan do vân tay repo (0.3.2)

Nguồn: audit 0.3.1 trong chat 2026-07-29 (user duyệt "sửa theo đề xuất") · Trạng thái plan: **HOÀN THÀNH** (QC PASS 10/10)

Nguyên tắc: mỗi task một test, red → green; pass là tick `[x]` ngay.
Thứ tự: P1 (helper) → P2 (stop_gate) → P3 (log service) → P4 (doc/đóng gói) → P5 (QC).

## P1 — `scripts/tdq_state.py`: vân tay chỉ tính file "thật"

- [x] **T1.1 (A)** Loại trừ sổ sách bằng **git pathspec**, không lọc ở Python:
  `BOOKKEEPING_PATHS = ("docs/tdq", "docs/workinglog")` → `:(top,exclude)<p>`, áp cho cả
  `status --porcelain -uall` lẫn `diff HEAD` trong `repo_status_digest` và `repo_status_paths`.
  - Test `test_turn_snapshot.py::test_digest_ignores_bookkeeping_writes`,
    `…::test_digest_ignores_worklog_append`, `…::test_paths_exclude_bookkeeping`.
- [x] **T1.2 (B)** File untracked ≤256 KB: băm **nội dung** thay vì `size:mtime_ns`
  (ngân sách đọc 4 MB/lần; vượt trần thì mới rơi về `size:mtime_ns`).
  - Test `…::test_digest_stable_when_untracked_only_touched` (đổi mtime, nội dung y nguyên → digest **không** đổi),
    `…::test_digest_catches_untracked_content_change_same_size_and_mtime`.
- [x] **T1.3 (C)** Tiền tố sổ sách là chuỗi `/` cứng (git luôn in `/`), không dùng `os.path.join`.
  - Test `…::test_bookkeeping_prefixes_use_forward_slash`.
- [x] **T1.4 (F)** `UNTRACKED_STAT_CAP` đếm **số file untracked**, không đếm dòng status;
  `repo_status_paths` nâng trần 100 → 400.
  - Test `…::test_untracked_cap_counts_files_not_lines`.
- [x] **T1.5** Path untracked stat theo **repo root** (`rev-parse --show-toplevel`, cache trong process)
  thay vì `cwd`, vì porcelain in path theo root.
  - Test `…::test_digest_from_subdirectory`.

## P2 — `hooks/scripts/stop_gate.py`

- [x] **T2.1 (G)** `_snapshot` lấy dòng `turn_start` **cuối cùng** (mới nhất), không phải dòng đầu.
  - Test `test_stop_gate.py::test_last_turn_start_row_wins` (thay `test_first_turn_start_row_wins`).
- [x] **T2.2 (A)** Turn không đụng file nào (kể cả turn chỉ ghi state) → **không** chặn dù repo có file bẩn sẵn.
  - Test `…::test_readonly_turn_with_dirty_repo_not_blocked`, `…::test_state_write_only_turn_not_blocked`.
- [x] **T2.3 (C)** Bộ lọc tên file dùng chung `tdq_state.BOOKKEEPING_PATHS` (khớp theo `<p>/`).
- [x] **T2.4** Không hồi quy: toàn bộ test 0.3.1 (chặn `sed -i`, `cat >>` không chặn, non-git, malformed) vẫn xanh.

## P3 — Log service (D)

- [x] **T3.1** `_git` ghi `_warn` khi **timeout** hoặc **không chạy được git** (rc≠0 im lặng vì
  đó là "không phải repo"/chưa có HEAD, không phải lỗi).
- [x] **T3.2** `stop_gate` ghi `_info` khi ra quyết định chặn (nguồn bằng chứng + path) và
  `_warn` khi đầu turn có vân tay mà cuối turn lấy không được.
  - Test `…::test_block_logs_to_stderr`, `…::test_tdq_log_0_silences_stderr`.

## P4 — Doc & đóng gói 0.3.2

- [x] **T4.1** `references/reminder-codes.md` (skills + portable đồng bộ): nêu vùng loại trừ và giới hạn còn lại.
- [x] **T4.2** `CHANGELOG.md` mục `## 0.3.2`; `plugin.json` → `0.3.2`; `plugin validate --strict` PASS.
- [x] **T4.3** `docs/notes/user-level-install.md`: khuyến nghị `.gitignore` cho `docs/tdq/.tdq-turn.jsonl`.

## P5 — QC & report

- [x] **T5.1** `python3 -m unittest discover tests` OK (≥ 195 test) · `doc_lint.py skills portable` exit 0.
- [x] **T5.2** Dựng lại đúng 3 kịch bản audit (A read-only, A state-only, B touch untracked) → hết chặn oan.
- [x] **T5.3** Smoke lại 3 kịch bản 0.3.1 (`cat >>` không chặn / `sed -i` chặn / sửa untracked chặn) → giữ nguyên.
- [x] **T5.4** QC doc + report ≤50 dòng + working log + `graphify extract . --code-only`.

## Ngoài phạm vi (đã nêu lý do trong chat)

- **E — hook `SubagentStop`**: cố tình KHÔNG thêm. Subagent không phải nơi ghi working log;
  thêm gate ở đó là tạo chặn oan mới. Vân tay git ở Stop của phiên cha vẫn bắt được file subagent ghi.
