# REPORT — Vá điểm mù verify-by-effect (tdq-workflow 0.3.1)

Ngày: 2026-07-29 · Spec: ../spec/2026-07-29-turn-effect-blindspot.md · Plan: ../plan/2026-07-29-turn-effect-blindspot.md · QC: ../qc/2026-07-29-turn-effect-blindspot.md

## Vấn đề

Sổ turn chỉ nhận `observe` từ **tên tool được gọi** (Edit/Write, Bash chạy `tdq_state.py`),
nên thay đổi qua shell vô hình với nó. Sai hai chiều: **chặn oan** (gặp thật lúc kết turn
0.3.0 — append log bằng `cat >>` nên không có `log_written`) và **bỏ lọt** (sửa repo hoàn
toàn bằng shell nên không có `edit`, Stop im lặng dù chưa ghi log).

## Đã làm gì

- `prompt_context` chụp trạng thái đĩa đầu turn vào một dòng `turn_start`: `sha256` working
  log hôm nay + vân tay repo + danh sách path đang bẩn.
- `stop_gate` đối chiếu thêm với đĩa: `logged` = sổ turn **hoặc** log đã đổi; `edited` = sổ
  turn **hoặc** vân tay repo đã đổi. Loại trừ `docs/tdq/` để ghi state không tự đòi ghi log.
- Vân tay repo gồm ba phần vì `git status --porcelain` đứng yên khi sửa tiếp file vốn đã
  `M` hoặc `??`: `status --porcelain -uall` + `diff HEAD` + `size:mtime` của file untracked.
- `bash_gate` **không** đổi — đoán lệnh shell bằng regex vừa không đủ vừa dễ cấp bằng chứng giả.

## Đầu ra

| Đầu ra | Đường dẫn |
|---|---|
| Helper snapshot | `scripts/tdq_state.py` (`today_log_rel`, `repo_status_digest`, `repo_status_paths`, `turn_snapshot`) |
| Hook | `hooks/scripts/prompt_context.py`, `hooks/scripts/stop_gate.py` |
| Test mới | `tests/test_turn_snapshot.py` + bổ sung `test_turn_ledger.py`, `test_stop_gate.py` |
| Doc | `references/reminder-codes.md` (skills + portable), `README.md`, `CHANGELOG.md` |

## Kết quả QC

`python3 -m unittest discover tests` → Ran 187 tests, OK ·
`python3 scripts/doc_lint.py skills portable` → exit 0. PASS 12/12 ở vòng 1 sau khi sửa **QC1.1** (bỏ lọt file untracked, phát hiện lúc smoke).
`plugin validate --strict` PASS; smoke ba kịch bản trên bản cài user-level đúng kỳ vọng.
Vân tay repo tốn **32 ms** trên repo này (trần timeout 2 s).

## Quyết định đáng chú ý

Kiểm bằng **đĩa** thay vì parse shell: cách ghi không còn quan trọng, không có mặt nào để
lách bằng cú pháp lạ. Mọi lỗi git (không phải repo, thiếu `git`, timeout) → coi như không
có bằng chứng và rơi về đúng hành vi 0.3.0, không bao giờ raise.

## Giới hạn còn lại

- Project **không phải git repo**: chiều "repo đã đổi" vẫn chỉ dựa vào sổ turn như 0.3.0.
- File bị `.gitignore` che thì vân tay repo không thấy.
- Tên file trong lời chặn là **gợi ý**: không có file mới xuất hiện thì nêu file bẩn đầu tiên.
- Chưa commit — chờ user. Cần **restart Claude Code** để hook 0.3.1 có hiệu lực.
