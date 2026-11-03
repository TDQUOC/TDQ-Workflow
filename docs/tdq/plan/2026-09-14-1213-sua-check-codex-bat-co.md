# QUICK — Sửa check Codex, lệnh bật cờ và CODEX_HOME tạm

**Ngày:** 2026-09-14 · Brief: ../brief/2026-09-14-1213-sua-check-codex-bat-co.md · Lane: quick
**Trạng thái:** ĐÃ DUYỆT ("duyệt nhanh")
**Ước tính sẽ dùng skill:** không có

## Phạm vi
- Trong: bốn lỗi của brief; chạy thật Q13 và Q21b; sinh lại ba bundle portable; cập nhật hàng Q13/Q21b trong QC của request `2026-09-10-2247-mode-codex-implement`.
- NGOÀI: bump phiên bản, CHANGELOG, cổng mode trong `tdq_state.py`, hook `prompt_context.py`.
- Bỏ B0, B2 và vòng scope: lý do đã ghi ở `## Hiểu & kiến thức` của brief.

## Task
- [x] **T1** `dung_codex_home` chép `model_provider` và bảng `[model_providers.<tên>]` từ config máy (đọc `$CODEX_HOME` hoặc `~/.codex`), bỏ bảng khác; gitignore `docs/tdq/.tdq-codex-home/` — Test: `python3 -m unittest discover tests -p "test_codex_run.py"`
  Chạm: `scripts/tdq_codex.py`, `.gitignore`, `tests/test_codex_run.py`
- [x] **T2** `_kiem_song` gửi một lượt say hi thật qua `CODEX_HOME` tạm (sandbox chỉ đọc, timeout 30s, đạt khi exit 0 và câu trả lời không rỗng), dọn home sau khi kiểm; `check` hỏi model trước khi kiểm sống — Test: `python3 -m unittest discover tests -p "test_codex_cli.py"` với `codex` giả sống, chết, treo
  Chạm: `scripts/tdq_codex.py`, `tests/test_codex_cli.py`
- [x] **T3a** Sửa gợi ý nguyên nhân 2 và 3 trong `check` — Test: `DongYCliTest.test_goi_y_nguyen_nhan_2_chi_lenh_dong_y`, `test_goi_y_nguyen_nhan_3_khong_con_bao_thu_codex_version`
  Chạm: `scripts/tdq_codex.py`, `tests/test_codex_cli.py`
- [x] **T3b** Lệnh `tdq_codex.py dong-y --model <tên>` (không cần manifest; thiếu `codex` thì không ghi, exit 1) — Test: `DongYCliTest` ba test `dong_y_*`/`thieu_codex_*`
  Chạm: `scripts/tdq_codex.py`, `tests/test_codex_cli.py`
- [x] **T3c** Sửa gợi ý ở `CAU_HOI_CODEX`, lời nhắn cuối `cai_tang_codex`, hàng 2 và 3 của `mode-gate.md` — Test: `python3 -m unittest discover tests -p "test_codex_cli.py"` và `-p "test_checkportable.py"`
  Chạm: `scripts/tdq_checkportable.py`, `skills/tdq-plan/references/mode-gate.md`, `tests/test_checkportable.py`
- [x] **T4** Sinh lại bundle bằng `build_portable.py` — Test: `python3 -m unittest discover tests -p "test_build_portable.py"`
  Chạm: `antigravity_portable/`, `portable_claude/`, `portable_codex/`
- [x] **T5** Chạy thật Q13 và Q21b bằng `tdq_codex.py run`, ghi kết quả vào QC cũ — Test: file ngoài repo không tồn tại; file trong repo mang đúng giá trị biến mốc
  Chạm: `docs/tdq/qc/2026-09-10-2247-mode-codex-implement.md`

## Definition of Done
- Router chết (`CODEX_HOME` trỏ cổng `127.0.0.1:1`) → `check --json` ra `chay_duoc: false` kèm lý do; router thật → `chay_duoc: true`.
- `python3 scripts/tdq_codex.py dong-y --model ag/gemini-3.8-flash-medium` ở gốc repo → exit 0, file cờ có cả hai khoá.
- `git check-ignore docs/tdq/.tdq-codex-home/x/auth.json` → bị ignore.
- Q13 thật: không có file ngoài repo, `/tmp` và `$TMPDIR`. Q21b thật: file trong repo chứa đúng giá trị biến mốc.
- Không đầu ra nào của `check` và `run` chứa `Bearer`; test của T1–T4 xanh.

## QC

Chạy 2026-09-14 12:36–12:43, mọi lệnh test dùng `env -u TDQ_LOG python3 -m unittest discover tests -p "<file>"`.

| Mục | Lệnh | Bằng chứng | Kết quả |
|---|---|---|---|
| T1 | `-p "test_codex_run.py"` | `Ran 41 tests … OK` | PASS |
| T2, T3a, T3b | `-p "test_codex_cli.py"` | `Ran 24 tests … OK` (đỏ trước: 6 fail) | PASS |
| T3c | `-p "test_checkportable.py"` | `Ran 31 tests … OK` | PASS |
| T4 | `build_portable.py` rồi `-p "test_build_portable.py"` | 13 file bundle đổi; `Ran 61 tests … OK` | PASS |
| T5 | `tdq_codex.py run` thật hai lượt | chi tiết ở QC cũ, mục "Vòng 3" | PASS |
| DoD 1 | `CODEX_HOME=<config cổng 127.0.0.1:1> tdq_codex.py check --json` / router thật | chết: `chay_duoc: false` · `say hi quá hạn 30s — model không trả lời` (30s); thật: `chay_duoc: true` · `codex-cli 0.154.0` (10s) | PASS |
| DoD 2 | `tdq_codex.py dong-y --model ag/gemini-3.8-flash-medium` ở gốc repo | exit 0; cờ `{nguoi_dung_dong_y: True, codex_model: ag/gemini-3.8-flash-medium}` | PASS |
| DoD 3 | `git check-ignore docs/tdq/.tdq-codex-home/x/auth.json` | in lại đường, exit 0 | PASS |
| DoD 4 | Q13, Q21b thật | Q13: `zsh:1: operation not permitted`, file `~/tdq-q13-probe.txt` không tồn tại; Q21b: file chứa đúng `Q21B-PROBE-124119` | PASS |
| DoD 5 | `grep -c -e Bearer -e sk-` trên đầu ra check (2) và run (2) | 0 cả bốn | PASS |
| Dọn | `tdq_codex.py cleanup` | `docs/tdq/.tdq-codex-home/` còn 0 thư mục; file thăm dò Q21b đã xoá | PASS |

**Phát hiện ngoài phạm vi:** `run` chấm `trang_thai: fail` cho cả hai lượt dù việc làm đúng — model
`ag/gemini-3.8-flash-medium` ghi `ket-qua.json` bằng câu văn thường, không theo `--output-schema`.
