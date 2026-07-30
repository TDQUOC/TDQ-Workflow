# PLAN — TDQ 0.2.0: hard gate → nhắc nhở, duyệt bằng chat tự nhiên

Trạng thái: **ĐÃ DUYỆT 18:41 (mode: main) — ĐÃ IMPLEMENT** · Ngày: 2026-07-28 · Lane: full
Spec nguồn: [spec](../spec/2026-07-28-soft-gates-remind.md) (đã duyệt 18:37, sha256 `bcc682c732f6`)

## Nguyên tắc thực thi

- Red → green từng task; tick `[x]` NGAY khi test của task đó pass. Chạy test từ `tests/`: `python3 -m unittest discover .`
- Không commit/push nếu user chưa yêu cầu.
- Log: hook chỉ in nhắc bằng tiếng Việt; CLI `approve` in xác nhận + cảnh báo ra stderr (luôn bật, có timestamp trong state).
- Thứ tự bắt buộc: CLI trước (P1) vì hook và skills đều tham chiếu tới lệnh `approve`.

Mode thực thi: main — thay đổi đan chéo (bỏ PROTECTED_KEYS → CLI → 4 hook → viết lại ~15 test cũ cùng thư mục `tests/`), chia worktree sẽ conflict liên tục. (Đây là ĐỀ XUẤT; mode thật do bạn chốt khi duyệt.)

## Phase 1 — CLI ghi nhận duyệt

- [x] **1.1.** `tdq_state.py`: thêm `spec_approved_by`/`plan_approved_by`/`quick_approved_by` (default `null`), `schema_version` → 3, `load()` bù khoá cho state schema 2. — Test: `test_state.py::test_load_backfills_approved_by` (state v2 thiếu khoá → load đủ, dữ liệu cũ nguyên vẹn).
- [x] **1.2.** Bỏ `PROTECTED_KEYS`: `set` ghi được mọi khoá trong schema. — Test: `set spec_approved=true` rc 0 và state đổi; test cũ `test_cli_rejects_protected_keys` chuyển thành `test_cli_can_set_approval_keys`.
- [x] **1.3.** Lệnh `approve <spec|plan|quick> [--mode main|subagent] [--by "<câu user>"]`: ghi `*_approved`, `*_approved_at`, `*_sha256` (từ file đã đăng ký nếu có), `implement_mode` khi có `--mode`, `*_approved_by` cắt 200 ký tự. — Test: `test_approve_writes_all_fields` (sha256 khớp `sha256_file`, `--by` dài 500 → lưu 200).
- [x] **1.4.** Idempotent + cảnh báo mềm: đã duyệt → in `ℹ️ … đã duyệt lúc …`, exit 0, không ghi đè timestamp; sai lane / chưa đăng ký file / duyệt plan khi spec chưa duyệt → cảnh báo stderr nhưng **vẫn ghi**, exit 0. — Test: `test_approve_is_idempotent`, `test_approve_warns_but_records`.

## Phase 2 — Hook chỉ còn nhắc

- [x] **2.1.** `edit_gate.py`: mọi nhánh trả `permissionDecision: "allow"`; lý do cũ chuyển thành `additionalContext` (chưa duyệt mà sửa ngoài `docs/**`; ghi tay `state.json` → nhắc dùng CLI); không có lý do → im lặng. — Test: `test_edit_gate.py` — mọi case cũ assert `allow`; case chưa duyệt có `additionalContext` chứa "chưa duyệt"; **không case nào** trả `deny`.
- [x] **2.2.** `bash_gate.py`: tương tự (ghi state qua shell, `git commit|push` khi user chưa yêu cầu → nhắc, không chặn). — Test: `test_bash_gate.py` cập nhật cùng kiểu.
- [x] **2.3.** Xoá `hooks/scripts/approve_gate.py` + mục `UserPromptExpansion` trong `hooks/hooks.json`; xoá `tests/test_approve_gate.py`. — Test: `validate --strict` PASS; `grep -r '"deny"' hooks/` không còn kết quả.
- [x] **2.4.** `stop_gate.py`: bỏ `check_invite` và toàn bộ hằng/hàm liên quan (`INVITE_*`, `PROPOSED_RE`, `MODE_RE`, `invite_problem`, `turn_assistant_texts` nếu thành thừa); giữ nhánh working log. — Test: `test_stop_gate.py` — dòng mời sai lane → im lặng; repo đổi + log cũ → vẫn block; xoá/đảo các test invite cũ.
- [x] **2.5.** `prompt_context.py`: khi đang chờ duyệt → thêm dòng hướng dẫn ghi nhận duyệt (`approve <target> --by "<nguyên văn>"`, mơ hồ thì hỏi). — Test: `test_context_hooks.py` — quick chưa duyệt và full có spec_file chưa duyệt → out chứa `approve` + `--by`; không request → im lặng.

## Phase 3 — Skills & tài liệu

- [x] **3.1.** `tdq-conventions`: bỏ mục field bảo vệ; thêm mục "Ghi nhận duyệt" (dấu hiệu duyệt, bắt buộc `--by` nguyên văn, mơ hồ thì hỏi, không tự duyệt thay user, ghi working log mỗi lần duyệt). — Validate: đọc lại file, không còn chữ "protected".
- [x] **3.2.** `tdq-plan`, `tdq-spec`, `tdq-start`, `tdq-approve`, `README.md`: dòng mời chuyển sang tự nhiên (`➤ Duyệt: nhắn "duyệt plan mode main" …`); `tdq-approve` mô tả lại là phím tắt tương đương; plan thiếu mode → hỏi. — Validate: `grep -rn "tdq-approve" skills README.md` chỉ còn ngữ cảnh "phím tắt", không còn chỗ nào bắt buộc.

## Phase 4 — Nghiệm thu & đóng gói

- [x] **4.1.** Full suite PASS: `cd tests && python3 -m unittest discover .` (ghi rõ số test trước/sau). — Test: output OK.
- [x] **4.2.** E2E mới: `init → set spec_file → approve spec → set plan_file → approve plan --mode main → set phase=implement`, mọi lệnh exit 0, state đúng. — Test: `test_e2e_chain.py` viết lại theo luồng CLI.
- [x] **4.3.** Bump `0.1.8 → 0.2.0`, `validate --strict`, marketplace + plugin update. — Test: bản cài hiển thị 0.2.0.
- [x] **4.4.** Smoke bản cài 0.2.0: (a) edit code khi chưa duyệt → `allow` + có nhắc; (b) `approve quick` 2 lần → cả hai exit 0; (c) Stop hook vẫn block khi thiếu working log; (d) không còn `approve_gate.py` trong cache. — Test: dán output vào working log.
- [x] **4.5.** QC doc + report (nêu rõ điều gì không còn được bảo vệ) + working log + `graphify extract . --code-only`. — Test: file tồn tại, DoD §5 spec đủ mục.

## Definition of Done

Theo §5 spec: suite PASS 100% và không còn test kỳ vọng `deny`/PROTECTED · `grep '"deny"' hooks/` sạch · `validate --strict` PASS và plugin user-level 0.2.0 · 4 mục smoke đạt · working log + report ghi rõ đánh đổi · README/skills không còn bắt buộc slash command để duyệt.
