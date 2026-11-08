# SPEC — Vá Lỗ Hổng Gate 3 Tầng: Chặn Cứng Sửa Code Và Tự Duyệt Khi User Chưa Duyệt (`2026-11-08-1207-va-lo-hong-edit-gate-3-tang` · full · main)

Bản 1.1 — review: tận dụng signal provenance có sẵn thay vì đọc transcript; bỏ khóa phase cho main agent và mở rộng whitelist.

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## 1. Mục tiêu & phạm vi

- **Sự cố (play3clone, session `5c194f0e…`)**: user nhắn `1a` (chọn lane, chưa có request mở). Trong cùng lượt agent `init` → viết spec → `approve spec --by "duyet spec"` → viết plan → `approve plan --by "duyet plan"` → `Edit server/index.js`. Ở lane quick, agent `Edit` trước rồi mới `approve quick` bằng câu cũ của user.
- **Cơ chế lọt (đã kiểm code)**:
  1. `edit_gate.py`: thiếu duyệt chỉ `remind` → `permissionDecision: "allow"`, Edit vẫn chạy.
  2. `bash_gate.py`: `_check_signal_mismatch` fail-open khi lượt không có dòng `signal` (prompt `1a` lúc chưa có cổng chờ → hook không ghi signal) và dù lệch cũng chỉ `remind_force` (allow).
  3. `quick-lane.md` bước 2 và `PHASE_TABLE["quick_analyze"]["cmd"]` bảo `set phase=implement` trước cổng duyệt quick.
- **Không phải hồi quy của đợt tối ưu runtime**: `hooks/` không đổi từ `540004ff`; `edit_gate` chỉ nhắc từ 0.3.0. Lỗi tiềm ẩn, lộ ra khi model chủ động hơn.
- **Trong phạm vi**: 3 tầng trên. **Ngoài phạm vi**: code play3clone; ghi file qua shell/`node -e` của main agent (ceiling, xem §5).

## 1b. Lộ trình

- `analyze` xong: đối chiếu log play3clone, `edit_gate`/`bash_gate`/`prompt_context`/`tdq_state`, test hiện có.
- `spec` → `plan` → `implement` (3 task theo 3 tầng, đỏ→xanh) → `qc` (vùng chạm + full fresh) → `report` MD + HTML.

## 2. Đầu ra cụ thể

- O1 `hooks/scripts/edit_gate.py`: nhánh `TDQ:APPROVE` đổi `remind` → `block` (deny), giữ miễn trừ `docs/**` và file ngoài project.
- O2 `hooks/scripts/bash_gate.py`: `approve <target>` và `set phase=plan|implement` bị **block** khi lượt có `turn_start` mà không có `signal` `matched=True` cho target; không có `turn_start` → giữ `remind_force` (host thiếu hook prompt không bị kẹt).
- O3 `skills/tdq-intake/references/quick-lane.md` bước 2 + `PHASE_TABLE["quick_analyze"]` trong `scripts/tdq_state.py`: bỏ `set phase=implement` trước duyệt; `approve quick` đã tự đẩy phase sang `implement`. Sinh lại `phases.md`.
- O4 Report `docs/tdq/reports/2026-11-08-1207-va-lo-hong-edit-gate-3-tang.md` + `.html`.

## 2b. Ranh giới module

- `prompt_context.py` (UserPromptSubmit): phân loại prompt bằng `looks_like_approval`, ghi `signal`. Không đổi.
- `bash_gate.py` (PreToolUse Bash/PowerShell): đọc `signal` + `turn_start` từ turn ledger qua `turn_rows`. Đổi O2.
- `edit_gate.py` (PreToolUse Edit/Write): đọc `cong_dang_cho(state)`. Đổi O1.
- `_common.py`: `block`/`remind`/`remind_force`. Không đổi.
- `tdq_state.py`: `PHASE_TABLE`, `cong_dang_cho`, `_cli_approve`. Đổi chuỗi `cmd` của O3.

## 2c. Luồng hoạt động & Sơ đồ kiến trúc

```
UserPromptSubmit ─ prompt_context: turn_start + signal{target, matched}
        │
Agent gọi `tdq_state.py approve X` ─ bash_gate:
        ├─ signal(X).matched=True ............ cho chạy
        ├─ có turn_start, không signal khớp .. BLOCK (deny)   ← vá ca "1a"
        └─ không turn_start (host thiếu hook)  remind_force (như cũ)
Agent gọi Edit/Write ngoài docs/ ─ edit_gate:
        ├─ cong_dang_cho(state) = None ....... cho chạy (rồi TDQ:TICK như cũ)
        └─ còn cổng chờ ...................... BLOCK (deny)   ← vá ca Edit-trước-approve
```

Target ánh xạ: `nhanh|express` → `quick`; `approve plan --mode` chấp nhận signal `plan` hoặc `mode`; `set phase=plan` cần signal `spec`, `set phase=implement` cần signal `plan` (giữ `NEXT_PHASE_TARGET`).

## 3. Cách tiếp cận & lý do

- Chọn: dùng lại signal provenance đã có (một prompt người dùng = một cổng), đổi fail-open thành fail-closed khi bằng chứng hook đã chạy. Rẻ, không phụ thuộc định dạng transcript.
- Loại: đọc transcript JSONL (dễ vỡ theo host/version); khóa sửa code theo phase cho main agent (chặn nhầm tier `nhỏ` sau request đóng, `cong_dang_cho` đã đủ); mở rộng whitelist (thêm mặt hở không ai cần).

## 3b. Năng lực & công cụ

| Skill/công cụ | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `tdq-intake`, `tdq-spec`, `tdq-plan`, `tdq-build` | plugin:tdq-workflow | NỀN | Pipeline và cổng duyệt. |
| Python unittest + `tdq_test.py` | installed CLI | DÙNG | Đỏ→xanh vùng chạm, full fresh ở QC. |
| Grep / Read / Edit | built-in tools | DÙNG | Sửa O1–O3. |
| Archify | installed CLI | DÙNG | Report HTML O4. |
| Đọc transcript JSONL để xác thực `--by` | Claude Code transcript | KHÔNG | spec §3 đã chọn cách khác tốt hơn — signal ledger có sẵn. |

## 3c. Giải thuật & xử lý cốt lõi

1. `edit_gate`: `pending = cong_dang_cho(state)`; file ngoài `docs/` và trong project → `block("TDQ:APPROVE", [cổng chờ, "trình X và KẾT THÚC lượt chờ user", "không tự chạy approve"])`.
2. `bash_gate`: khớp `APPROVE_CLI`/`SETPHASE_CLI` → chuẩn hoá target → tìm signal mới nhất của target trong lượt:
   - `matched is True` và không `mode_conflict` → im lặng.
   - Ngược lại, nếu lượt có `turn_start` → `block("TDQ:APPROVE", ...)`; không có → `remind_force` như cũ.
   - O(n) trên số dòng ledger của lượt; không I/O thêm (dùng `rows` đã đọc).
3. Biên: approve lặp idempotent vẫn cần signal (cổng đã duyệt thì `pending` khác target, CLI tự in "already approved" — chấp nhận block vì agent không cần gọi lại); user duyệt bằng chữ cái `A` → `looks_like_approval` đã xử lý.

## 3d. Mental Model cho Fresher Dev

- Người gác cổng (hook) giữ sổ khách (signal). Chỉ mở cổng khi sổ ghi chính chủ (user) vừa nói "cho vào". Trước đây sổ trống thì gác cổng cho qua; nay sổ trống mà gác cổng có trực ca (turn_start) thì đóng.
- `remind` = biển báo; `block` = barie.

## 4. Yêu cầu bắt buộc

- Log `_info` khi block (nguồn, target, có/không turn_start). Không placeholder. Mỗi O có test.
- Giữ 6 trụ cột; duyệt chỉ đến từ tin nhắn người dùng.

## 5. Ràng buộc & rủi ro

- Chặn nhầm khi `looks_like_approval` hiểu sai câu duyệt thật → thông điệp block in đúng câu mẫu ("duyệt spec") để user gõ lại; không có cờ vượt cho agent.
- Host không có UserPromptSubmit → không `turn_start` → vẫn chỉ nhắc (ceiling đã biết).
- Ceiling: main agent ghi file qua shell/`node -e` không đi qua `edit_gate` — `ponytail:` ghi ở code, nâng khi có ca đo thật.
- Đổi hành vi test cố ý cũ (fail-open không signal) — chỉ đổi nhánh có `turn_start`.

## 6. QC & Definition of Done

- [ ] Q1 Edit/Write file ngoài `docs/` khi còn cổng chờ → deny; `docs/**` và sau khi duyệt đủ → allow.
- [ ] Q2 Tái hiện ca play3clone (có `turn_start`, không signal) `approve spec` → deny; signal khớp → allow; không `turn_start` → chỉ nhắc.
- [ ] Q3 `approve plan` sau `approve spec` trong cùng prompt → deny (một prompt một cổng).
- [ ] Q4 Hướng dẫn lane quick và bảng phase không còn `set phase=implement` trước duyệt; lint tài liệu 0 lỗi.
- [ ] Q5 Full fresh suite xanh; report MD + HTML có 4 phần Trước/Sau/Đã test/Kết quả.

## 7. Câu hỏi còn mở

*(Không có.)*
