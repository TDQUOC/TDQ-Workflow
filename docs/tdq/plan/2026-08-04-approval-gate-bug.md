# PLAN — Sửa lỗi approval-gate (nhắc nhở khi duyệt sai)

Ngày: 2026-08-04 · Spec: ../spec/2026-08-04-approval-gate-bug.md (bản 2, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — user chốt lúc duyệt (đổi từ đề xuất ban đầu `subagent`; plan
nhỏ, 3 phase phụ thuộc tuần tự chặt, làm trực tiếp trong hội thoại này không cần
worktree riêng).
Trạng thái plan: HOÀN THÀNH (duyệt 2026-08-04T20:11:56+07:00 "duyệt plan mode main"; build xong 2026-08-04, QC 7/7 PASS)

## Năng lực → task

Spec §3b không có dòng nào phán quyết `DÙNG` (chỉ `NỀN`/`KHÔNG`) — không có khối hợp
đồng skill nào cần ánh xạ ở đây.

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo (P2 cần schema tín hiệu P1 tạo ra).
2. Mỗi task: viết test trước (đỏ) → code → test xanh → tick `[x]` NGAY vào file này.
3. Sau mỗi phase: chạy toàn bộ test suite của các file liên quan phase đó, phải xanh
   mới sang phase sau; merge worktree về trước khi giao phase kế tiếp.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên
   chính lệnh đó (áp dụng khi agent test bằng cách gọi CLI thật, không phải khi chỉ
   giả lập payload hook bằng unittest).
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến
   khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Lưu tín hiệu duyệt vào turn ledger (`prompt_context.py`)

- [x] **T1.1** Viết test `tests/test_prompt_context.py::test_signal_written_matched_and_unmatched` — giả lập payload `UserPromptSubmit` khi đang chờ duyệt `spec`, 2 case (prompt là câu duyệt hợp lệ / không phải câu duyệt), xác nhận `turn_log_read` có dòng `kind="signal", event="approve_pending", target="spec", matched=<bool>` đúng từng case — Test: `python3 -m pytest tests/test_prompt_context.py -k signal_written -q` phải FAIL trước khi code
- [x] **T1.2** Trong `main()` của `prompt_context.py`, nhánh `if pending:`: tính `matched = looks_like_approval(prompt, pending)` (đã có sẵn), thêm `tdq_state.turn_log_append(cwd, "signal", session=session_id(payload), event="approve_pending", target=pending, matched=matched, mode_conflict=False)` ngay sau khi tính `matched`, trước khi rẽ nhánh in `lines` — Test: `python3 -m pytest tests/test_prompt_context.py -k signal_written -q` xanh
- [x] **T1.3** Viết test `test_signal_mode_conflict` — `pending="plan"`, prompt là câu duyệt đúng target nhưng nói mode khác mode đã chốt trong plan (`planned`) — xác nhận dòng signal ghi được có `matched=True, mode_conflict=True` — Test: FAIL trước khi code
- [x] **T1.4** Trong nhánh mode-mismatch hiện có (trước dòng `_emit(lines); return`), ghi THÊM một dòng `signal` mới (`turn_log_append` chỉ append, không có API ghi đè) với `mode_conflict=True` — `bash_gate.py` (P2) phải luôn tra dòng `signal` GẦN NHẤT theo `target` trong sổ turn, không phải dòng đầu tiên — Test: `python3 -m pytest tests/test_prompt_context.py -k mode_conflict -q` xanh

**Xong P1 khi**: `python3 -m pytest tests/test_prompt_context.py -q` toàn bộ pass.

## P2 — Đối chiếu tín hiệu trong `bash_gate.py` (cả `approve` và `set phase=`)

**Lưu ý bẫy dedupe đã phát hiện khi review plan** (đã sửa ở thiết kế dưới, không cần
động lại spec — spec chỉ cam kết "in một nhắc nhở mới đúng lúc", không cam kết cơ chế
dedupe cụ thể): `hooks/scripts/edit_gate.py:71` cũng gọi `_common.remind(cwd, payload,
"TDQ:APPROVE", ...)` (khi Claude sửa file ngoài `docs/` lúc spec/plan/quick chưa duyệt)
và `already_reminded()` dedupe theo `(kind="remind", code)` **không phân biệt hook nào
ghi**. Nếu nhắc mới ở đây dùng lại `remind()` nguyên trạng, kịch bản thật (Claude sửa
code rồi gọi `approve`/`set phase=` cùng turn) có thể bị `edit_gate.py` "chiếm" mã
`TDQ:APPROVE` trước, khiến nhắc mới bị nuốt im lặng — đúng kịch bản lỗi cần chặn. Cách
sửa: thêm hàm `remind_force()` (T2.2) không dedupe theo mã, chỉ dùng riêng cho 2 điều
kiện mới trong phase này.

- [x] **T2.1** Viết test `tests/test_bash_gate.py::test_approve_reminds_when_signal_mismatch` — ledger có dòng `signal matched=False target=spec`, payload Bash `tdq_state.py approve spec --by "..."` → output hook chứa `[TDQ:APPROVE]` và `permissionDecision=allow` — Test: FAIL trước khi code
- [x] **T2.2** Thêm vào `_common.py` hàm `remind_force(cwd, payload, code, lines, event="PreToolUse")` — giống hệt `remind()` (in JSON, `permissionDecision: allow`, ghi `turn_log_append(cwd, "remind", code=code)` để giữ vết hậu kiểm) nhưng **KHÔNG gọi `already_reminded()` trước khi in** (không dedupe theo mã — né bẫy nêu trên). Thêm `APPROVE_CLI = re.compile(r"tdq_state\.py\s+approve\s+(spec|plan|quick)\b")` vào `bash_gate.py`; khi khớp, tra dòng `kind="signal"` **GẦN NHẤT** (duyệt ngược, phần tử cuối khớp `target`) trong turn qua `turn_rows(cwd, payload)`; nếu tìm thấy và (`matched is False` hoặc `mode_conflict is True`) → gọi `remind_force(cwd, payload, "TDQ:APPROVE", [...])` với nội dung yêu cầu Claude dừng, không chạy lệnh approve, hỏi lại user. Chèn khối kiểm tra này **TRƯỚC** 2 khối nhắc `TDQ:GIT`/`TDQ:STATE` sẵn có trong `main()` — cả `remind()` lẫn `remind_force()` đều `sys.exit()` ngay sau khi in, nghĩa là chỉ điều kiện đầu tiên khớp trong một lần gọi hook mới thực sự chạy; nhắc chặn-tiến-phase phải ưu tiên hơn nhắc git/state — Test: `python3 -m pytest tests/test_bash_gate.py -k approve_reminds -q` xanh
- [x] **T2.3** Viết test `test_approve_silent_when_signal_matched` — ledger `signal matched=True mode_conflict=False target=plan`, Bash gọi `tdq_state.py approve plan --mode main ...` → không phát sinh nhắc `TDQ:APPROVE` mới từ điều kiện T2.2 — Test: `python3 -m pytest tests/test_bash_gate.py -k approve_silent -q` xanh (dùng để xác nhận T2.2 không có false positive)
- [x] **T2.4** Viết test `tests/test_bash_gate.py::test_setphase_reminds_when_signal_mismatch` — 2 case trong cùng test: (a) ledger `signal matched=False target=spec` + Bash `tdq_state.py set phase=plan` → phải nhắc; (b) ledger `signal matched=False target=plan` + Bash `tdq_state.py set phase=implement` → phải nhắc — Test: FAIL trước khi code
- [x] **T2.5** Thêm `SETPHASE_CLI = re.compile(r"tdq_state\.py\s+set\b.*?\bphase=(\w+)")` (khớp `phase=` ở BẤT KỲ vị trí nào sau `set`, không cố định ngay sau `set`, phòng lệnh tương lai dạng `set foo=bar phase=plan`) và map `NEXT_PHASE_TARGET = {"plan": "spec", "implement": "plan"}` vào `bash_gate.py`; khi khớp và phase captured có trong map, tra dòng `signal` gần nhất (cùng luật "gần nhất" như T2.2) với `target==NEXT_PHASE_TARGET[phase]`, áp cùng điều kiện/hành động `remind_force` như T2.2 (tái dùng 1 hàm dùng chung cho cả 2 nhánh approve/set-phase, tránh trùng lặp), đặt cùng nhóm ưu tiên trước GIT/STATE như T2.2 — Test: `python3 -m pytest tests/test_bash_gate.py -k setphase_reminds -q` xanh
- [x] **T2.6** Viết test `test_setphase_silent_when_signal_matched` — ledger `signal matched=True mode_conflict=False target=spec`, Bash gọi `tdq_state.py set phase=plan` → không phát sinh nhắc `TDQ:APPROVE` mới (cặp im lặng cho nhánh `set phase=`, đối xứng T2.3 cho nhánh `approve`) — Test: `python3 -m pytest tests/test_bash_gate.py -k setphase_silent -q` xanh
- [x] **T2.7** Viết test `test_failopen_no_signal_row` — ledger KHÔNG có dòng `kind="signal"` nào trong turn, Bash gọi `tdq_state.py approve spec ...` → không phát sinh nhắc `TDQ:APPROVE` mới ngoài hành vi cũ (fail-open, đúng spec §5 R3) — Test: `python3 -m pytest tests/test_bash_gate.py -k failopen -q` pass, chứng minh hành vi mặc định đúng cam kết
- [x] **T2.8** Viết test `test_approve_not_swallowed_by_prior_edit_gate_remind` — giả lập ledger đã có SẴN 1 dòng `kind="remind", code="TDQ:APPROVE"` (mô phỏng đúng dòng `edit_gate.py` ghi khi sửa file ngoài docs/ lúc chưa duyệt) CỘNG dòng `signal matched=False target=spec`; Bash gọi `tdq_state.py approve spec ...` → hook VẪN phải in nhắc `TDQ:APPROVE` mới (chứng minh `remind_force` không bị `already_reminded()` nuốt mất — regression test trực tiếp cho bẫy dedupe đã phát hiện) — Test: `python3 -m pytest tests/test_bash_gate.py -k not_swallowed -q` xanh, và test này phải FAIL nếu T2.2 lỡ dùng `remind()` thường thay vì `remind_force()`

**Xong P2 khi**: `python3 -m pytest tests/test_bash_gate.py -q` toàn bộ pass.

## P3 — Test bắt buộc tổng hợp

- [x] **T3.1** Chạy toàn bộ test suite của repo, xác nhận không phá vỡ hành vi cũ — Test: `python3 -m pytest -q` (hoặc `python3 -m unittest discover -s tests` nếu repo dùng unittest runner) exit 0

**Xong P3 khi**: toàn bộ test suite pass.

## Definition of Done

Trỏ về spec §6 (`docs/tdq/spec/2026-08-04-approval-gate-bug.md`):

| # | Hạng mục | Lệnh | PASS khi |
|---|---|---|---|
| Q1 | Signal ghi đúng schema (thường + mode_conflict) | `python3 -m pytest tests/test_prompt_context.py -q` | Exit 0 — T1.1–T1.4 |
| Q2 | `bash_gate.py` nhắc khi lệch lúc `approve` (kể cả mode_conflict, kể cả khi `edit_gate.py` đã chiếm mã trước) | `python3 -m pytest tests/test_bash_gate.py -k "approve_reminds or not_swallowed" -q` | Exit 0 — T2.1–T2.2, T2.8 |
| Q3 | `bash_gate.py` im lặng khi khớp thật (cả `approve` lẫn `set phase=`) | `python3 -m pytest tests/test_bash_gate.py -k "approve_silent or setphase_silent" -q` | Exit 0 — T2.3, T2.6 |
| Q4 | `bash_gate.py` nhắc khi lệch lúc `set phase=` | `python3 -m pytest tests/test_bash_gate.py -k setphase_reminds -q` | Exit 0 — T2.4–T2.5 |
| Q5 | Fail-open khi ledger rỗng | `python3 -m pytest tests/test_bash_gate.py -k failopen -q` | Exit 0 — T2.7 |
| Q6 | Test suite cũ không vỡ | `python3 -m pytest -q` | Exit 0 — T3.1 |
| Q7 | doc_lint spec (đã pass ở bước spec) | `python3 scripts/doc_lint.py docs/tdq/spec/2026-08-04-approval-gate-bug.md` | Exit 0 (đã xác nhận, không cần chạy lại trừ khi sửa spec) |

## Ghi chú review (áp dụng 5 góp ý `tdq-reviewer` vòng 1)

1. **[Nghiêm trọng]** `edit_gate.py` cũng gọi `remind()` với mã `TDQ:APPROVE` (lý do
   khác) → có thể nuốt mất nhắc mới cùng mã trong cùng turn. Sửa: T2.2 đổi sang hàm
   riêng `remind_force()` (không dedupe theo mã), T2.8 thêm test regression trực tiếp.
   Không cần sửa lại spec — spec chỉ cam kết hành vi quan sát được (có nhắc mới xuất
   hiện), không cam kết cơ chế dedupe cụ thể.
2. Thiếu task "im lặng khi khớp" cho nhánh `set phase=` → thêm T2.6.
3. T1.4 làm rõ: `turn_log_append` chỉ append, không ghi đè — luôn thêm dòng signal mới,
   `bash_gate.py` phải đọc dòng GẦN NHẤT theo target (áp dụng cả T2.2, T2.5).
4. Thứ tự khối nhắc trong `bash_gate.py` quan trọng vì `remind()`/`remind_force()`
   `sys.exit()` ngay sau khi in — chỉ điều kiện đầu tiên khớp mới thực sự chạy. Đặt 2
   khối APPROVE/SETPHASE mới TRƯỚC khối GIT/STATE sẵn có (T2.2, T2.5).
5. T3.1 cũ (grep xác nhận `turn_log_append` tồn tại) không kiểm được điều nó tuyên bố
   — bỏ hẳn, vì T1.1/T1.2 đã chứng minh dòng `signal` ghi được qua log dùng chung.
