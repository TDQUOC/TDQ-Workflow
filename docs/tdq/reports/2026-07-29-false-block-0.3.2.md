# REPORT — Vá chặn oan do vân tay repo (tdq-workflow 0.3.2)

Ngày: 2026-07-29 · Plan: ../plan/2026-07-29-false-block-0.3.2.md · QC: ../qc/2026-07-29-false-block-0.3.2.md

## Vấn đề

Audit 0.3.1 (theo yêu cầu user) cho thấy bản vá điểm mù lại đẻ ra kiểu chặn oan mới,
**nặng hơn lỗi nó vá**: vùng loại trừ `docs/tdq/` chỉ áp cho việc **đặt tên**
(`_shell_changed_path`), không áp cho **quyết định** (`_repo_changed` so vân tay toàn
repo). Chính hook append `.tdq-turn.jsonl` *sau khi* chụp baseline → vân tay gần như
luôn đổi → file bẩn có sẵn bị lôi ra làm vật tế thần, kể cả trong turn **read-only**
hay turn **chỉ ghi state**. Repo này thoát vì đã `.gitignore` sổ turn, project của
user thì không.

## Đã làm gì

- Loại trừ `docs/tdq/` + `docs/workinglog/` **ngay từ pathspec của git**
  (`:(top,exclude)`), dùng chung cho cả `status`, `diff HEAD`, digest lẫn danh sách path
  → quyết định và đặt tên không còn nhìn hai tập path khác nhau. Đẩy việc loại trừ
  **xuống git** thay vì lọc bằng Python: chỉ còn một nơi định nghĩa "cái gì không
  tính là thay đổi", nên không thể lệch lại như 0.3.1.
- File untracked lấy dấu bằng **nội dung** (≤256 KB, ngân sách đọc 4 MB) thay vì
  `size:mtime` → `touch` hết báo động giả, vẫn bắt được sửa cùng size cùng mtime.
- Tiền tố loại trừ là chuỗi `/` cứng (`os.path.join` tự tắt bộ lọc trên Windows);
  `turn_start` lấy dòng **mới nhất**; trần đếm đúng **số file** untracked; path stat
  theo **gốc repo**; danh sách path 100 → 400.
- Log service cho hook (§6): git timeout / không chạy được → ⚠️ kèm timestamp; mỗi
  quyết định chặn ghi rõ nguồn bằng chứng + path. `TDQ_LOG=0` để tắt.

## Đầu ra

| Đầu ra | Đường dẫn |
|---|---|
| Helper | `scripts/tdq_state.py` (`BOOKKEEPING_PATHS`, `repo_root`, `_untracked_mark`, `_git`) |
| Hook | `hooks/scripts/stop_gate.py` |
| Test | `test_turn_snapshot.py` (+11), `test_stop_gate.py` (+6), `helper.py` (`run_hook(env=…)`) |
| Doc | `reminder-codes.md` (skills + portable), `CHANGELOG.md`, `user-level-install.md`, `plugin.json` 0.3.2 |

## Kết quả QC

**Ran 204 tests, OK** · `doc_lint` exit 0 · `plugin validate --strict` PASS · **10/10**
vòng 1. Ba kịch bản audit hết chặn oan, ba kịch bản 0.3.1 giữ nguyên hành vi. Vân tay
repo 32 → **53 ms** (trần timeout 2 s).

## Còn lại

- **Không** thêm `SubagentStop` (có chủ ý): subagent không phải nơi ghi working log.
- Chưa commit — chờ user; cần **restart Claude Code** để hook 0.3.2 có hiệu lực. State
  vẫn trỏ request cũ `2026-07-28-instruction-hardening-7b`; `init` sẽ xoá state đó.
