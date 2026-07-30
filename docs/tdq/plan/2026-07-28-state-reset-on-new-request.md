# PLAN — Yêu cầu mới ⇒ state được đồng bộ lại theo lane user chọn (0.1.7)

Trạng thái: **ĐÃ DUYỆT 18:05 (mode: main) — ĐÃ IMPLEMENT** · Ngày: 2026-07-28 · Lane: full
Spec nguồn: [spec](../spec/2026-07-28-state-reset-on-new-request.md) (đã duyệt 18:02, sha256 `bc40092cc8bb`)

## Nguyên tắc thực thi

- Không commit/push nếu user chưa yêu cầu. Không đụng `docs/tdq/state.json` bằng tay (chỉ qua `scripts/tdq_state.py`).
- Mỗi task đi red → green: viết test đỏ trước, sửa code cho xanh, tick `[x]` NGAY khi task đó pass.
- Chạy test từ trong `tests/`: `cd tests && python3 -m unittest discover .`
- Log: các hook đã in lý do chặn bằng tiếng Việt (đây chính là log service của plugin); task 1 bổ sung log cảnh báo ghi đè ra stderr, luôn bật, không cần config tắt vì chỉ in khi thật sự ghi đè.

Mode thực thi: main — plan nhỏ (~7 task) và các file đụng chéo (stop_gate/approve_gate/prompt_context/tdq_state cùng chia một suite test trong `tests/`), chia worktree tốn công merge hơn là lợi. (Đây là ĐỀ XUẤT; mode thật do bạn gõ khi duyệt.)

## Phase 1 — Core state (nền cho mọi thứ còn lại)

- [x] **1.1.** `scripts/tdq_state.py`: thêm khoá `previous_request` (default `null`) vào `default_state()`, bump `schema_version` → 2, `load()` bù khoá thiếu cho state schema cũ. — Test/Validate: `test_state.py::test_load_backfills_missing_keys` — nạp file state schema_version 1 thiếu `previous_request` → `load()` trả về dict có đủ khoá, không mất dữ liệu cũ.
- [x] **1.2.** `init <slug> <lane>`: giữ reset toàn bộ; ghi `previous_request` = slug cũ; nếu request cũ **chưa hoàn tất** (phase ∉ {`report`,`idle`} hoặc còn field duyệt true) thì in cảnh báo `⚠️ Ghi đè request '<slug>' (lane …, phase …) — mọi trạng thái duyệt bị xoá.` ra **stderr**, exit 0. — Test/Validate: `test_state.py::test_init_over_unfinished_request_warns` (stderr chứa "Ghi đè" + slug cũ, `previous_request` đúng, mọi `*_approved` False, `implement_mode` None) và `test_init_clean_state_is_silent` (state rỗng → stderr trống).
- [x] **1.3.** `previous_request` set được qua CLI `set`, các field duyệt vẫn bị `PROTECTED_KEYS` từ chối. — Test/Validate: `test_state.py` — `set previous_request=x` rc 0; vòng lặp protected-key hiện có vẫn rc 1 với "bảo vệ".

## Phase 2 — Lưới an toàn không trượt vì transcript trễ

- [x] **2.1.** `hooks/scripts/stop_gate.py`: thay `last_assistant_text()` bằng `turn_assistant_texts(path)` — quét ngược, gom text mọi assistant message tới khi gặp prompt user thật (`type=user`, content là chuỗi, không mở đầu `Stop hook feedback`), tối đa 8 message; `check_invite` duyệt tất cả text đó. — Test/Validate: `test_stop_gate.py::test_invite_in_earlier_message_of_same_turn_blocks` (message cuối không có dòng mời, message trước trong cùng lượt có + state sai lane → block).
- [x] **2.2.** Không chặn lời mời của **lượt trước**: dừng gom khi gặp prompt user thật. — Test/Validate: `test_stop_gate.py::test_invite_before_previous_user_prompt_is_ignored` → exit im lặng.
- [x] **2.3.** Message chặn của stop_gate nêu lệnh sửa cụ thể (`tdq_state.py init <slug> <quick|full>` + ghi chú "init reset toàn bộ state cho yêu cầu mới"). — Test/Validate: assert chuỗi `init` có trong reason của case 2.1; toàn bộ test stop_gate cũ (gồm 0.1.6) vẫn PASS.

## Phase 3 — Nhắc & chỉ dẫn

- [x] **3.1.** `hooks/scripts/prompt_context.py`: khi có request mở, in thêm dòng nhận diện `[TDQ] Request đang mở: <slug> · lane <lane> · phase <phase>. Nếu prompt này là YÊU CẦU MỚI → chạy init <slug-mới> <lane> (reset toàn bộ state) TRƯỚC khi trình spec/plan.` — Test/Validate: `test_prompt_context.py` — có request → stdout chứa "Request đang mở" + slug; không có request → stdout rỗng; các test cũ vẫn PASS.
- [x] **3.2.** `hooks/scripts/approve_gate.py`: mọi message "Sai lane" (nhánh quick và spec/plan) thêm lệnh sửa `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" init <slug> <lane đúng>`. — Test/Validate: `test_approve_gate.py::test_lane_mismatch_message_has_init_command`.
- [x] **3.3.** `skills/tdq-start/SKILL.md` + `skills/tdq-conventions/SKILL.md`: init là bắt buộc cho MỌI yêu cầu mới ngay khi user chọn lane, kể cả khi có request khác đang mở; request cũ còn dở → **hỏi user trước khi đè** (nêu slug/phase sẽ mất); phân biệt `init` (mở request mới) vs `reset` (đóng hẳn). — Test/Validate: đọc lại 2 file, `claude plugin validate . --strict` PASS.

## Phase 4 — Đóng gói & nghiệm thu

- [x] **4.1.** Full suite: `cd tests && python3 -m unittest discover .` → 100% PASS (67 cũ + ~8 mới). — Test/Validate: output OK, không skip.
- [x] **4.2.** Bump `.claude-plugin/plugin.json` 0.1.6 → 0.1.7, `claude plugin validate . --strict`, `marketplace update tdq-local`, `plugin update tdq-workflow@tdq-local`. — Test/Validate: version cài đặt hiển thị 0.1.7.
- [x] **4.3.** Smoke trên bản cache 0.1.7 với payload thật: (a) project tạm lane full/phase implement + transcript mô phỏng lag chứa dòng mời quick → stop_gate **block**; (b) `init <slug> quick` → state reset đủ khoá, có cảnh báo ghi đè; (c) approve quick → PASS. — Test/Validate: dán output 3 bước vào working log.
- [x] **4.4.** Working log ngày: nguyên nhân, file đổi, kết quả test + smoke; chạy `graphify extract . --code-only`. — Test/Validate: file `docs/workinglog/2026-07-28.md` có entry mới.

## Definition of Done

Theo mục 6 của spec: full suite PASS bằng một lệnh · `validate --strict` PASS và plugin user-level ở 0.1.7 · smoke tái hiện đúng kịch bản trong ảnh (mời duyệt sai lane bị chặn TRƯỚC khi tới tay user; sau init lane quick thì duyệt được) · working log đủ · không field duyệt nào set được ngoài approve_gate.
