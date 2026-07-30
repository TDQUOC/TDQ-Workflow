# SPEC — TDQ 0.2.0: hard gate → nhắc nhở, duyệt bằng chat tự nhiên
<!-- doc-lint: allow R8 -->  <!-- spec viết trước 0.3.3, chưa có mục 3b -->

Ngày: 2026-07-28 · Slug: `2026-07-28-soft-gates-remind` · Lane: full · Trạng thái: **CHỜ DUYỆT**
Request nguồn: [request](../requests/2026-07-28-soft-gates-remind.md) · Phiên bản đích: **0.2.0** (breaking)

## 1. Mục tiêu

1. **Không còn thao tác nào bị từ chối** vì trạng thái workflow: mọi kiểm tra cũ trở thành lời nhắc cho Claude.
2. **Duyệt bằng chat thường**: "duyệt spec", "ok plan mode main", "duyệt quick", "đồng ý, làm đi" — không cần slash command, không cần đúng cú pháp.
3. Giữ **một điểm chặn duy nhất**: Stop hook block 1 lần/turn khi repo đổi mà chưa ghi working log / chưa tick plan (thứ dễ quên nhất, và luôn tự sửa được ngay trong turn).
4. Vẫn có **dấu vết duyệt** (ai duyệt, câu gì, lúc nào, file sha256) trong state + working log.

**Không nằm trong phạm vi:** đổi cấu trúc doc `docs/tdq/`, đổi lane quick/full, đổi luồng spec→plan→implement→QC→report.

## 2. Thay đổi theo file

### 2.1 `hooks/scripts/edit_gate.py` — deny → allow + nhắc
- Luôn trả `{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow","additionalContext": …}}`; **không bao giờ** `deny`.
- `additionalContext` chỉ xuất hiện khi có lý do (tiếng Việt, 1–2 câu):
  - sửa file ngoài `docs/**` khi lane quick chưa được ghi nhận duyệt → "Nhắc: user chưa duyệt mini-plan — trình plan ≤10 dòng và chờ user nói duyệt trước khi sửa code."
  - lane full mà `plan_approved=false` → nhắc tương tự theo phase.
  - ghi trực tiếp `docs/tdq/state.json` → "Dùng `tdq_state.py` thay vì sửa tay để state không lệch."
- Không có lý do → im lặng (không in gì) để khỏi tốn token.

### 2.2 `hooks/scripts/bash_gate.py` — deny → allow + nhắc
- Cùng cơ chế: lệnh Bash ghi đè state.json / chạy `git commit|push` khi user chưa yêu cầu → chỉ **nhắc**, không chặn.

### 2.3 `hooks/scripts/approve_gate.py` + entry `UserPromptExpansion` — **xoá**
- Bỏ hẳn script và mục hook. Slash command `/tdq-workflow:tdq-approve` vẫn còn (tiện cho ai thích gõ), nhưng nay chỉ là **chỉ thị cho Claude** ghi nhận duyệt bằng CLI — không còn hook chặn, không còn "đã duyệt rồi" thành lỗi.

### 2.4 `scripts/tdq_state.py` — lệnh `approve`, bỏ PROTECTED_KEYS
- Bỏ `PROTECTED_KEYS` (không còn hook độc quyền ghi) → CLI set được mọi khoá trong schema.
- Thêm lệnh: `tdq_state.py approve <spec|plan|quick> [--mode main|subagent] [--by "<nguyên văn câu user>"]`
  - ghi `<target>_approved=true`, `<target>_approved_at`, `<target>_sha256` (tính từ file đã đăng ký, nếu có), `implement_mode` khi có `--mode`, và `<target>_approved_by` = câu user (cắt 200 ký tự).
  - **Idempotent**: đã duyệt rồi → in `ℹ️ <target> đã duyệt lúc …` và exit **0** (không phải lỗi).
  - Cảnh báo (stderr, exit 0) khi lệch: sai lane, chưa đăng ký file, duyệt plan trước spec — nêu rõ nhưng **vẫn ghi**.
- Schema thêm: `spec_approved_by`, `plan_approved_by`, `quick_approved_by` (mặc định `null`), `schema_version` → 3, `load()` bù khoá thiếu như cũ.

### 2.5 `hooks/scripts/stop_gate.py` — chỉ còn 1 lý do block
- **Giữ**: block khi turn có thay đổi repo mà `docs/workinglog/<today>.md` chưa cập nhật sau đó (kèm nhắc tick plan + graphify).
- **Bỏ**: toàn bộ `check_invite` (dòng mời duyệt) — không còn cú pháp bắt buộc nên không còn gì để kiểm. Kèm theo bỏ `INVITE_*`, `PROPOSED_RE`, `MODE_RE`, `invite_problem`; giữ `turn_assistant_texts` nếu còn dùng, không thì xoá luôn.

### 2.6 `hooks/scripts/prompt_context.py` — nhắc nhận diện câu duyệt
- Giữ dòng "Request đang mở …".
- Khi đang chờ duyệt (quick chưa duyệt / spec|plan file đã đăng ký mà chưa duyệt) → thêm 1 dòng:
  "Nếu prompt này là câu duyệt (duyệt/ok/đồng ý/chốt + spec|plan|quick, có thể kèm mode) → chạy `tdq_state.py approve <target> [--mode …] --by "<nguyên văn>"` NGAY rồi mới làm tiếp; nếu không chắc user có ý duyệt hay không thì HỎI, đừng tự suy."

### 2.7 Skills (VI cho user-facing)
- `tdq-conventions`: bỏ mục "field duyệt được bảo vệ"; thêm mục **"Ghi nhận duyệt"**: dấu hiệu duyệt (duyệt/ok/đồng ý/chốt/approve + đối tượng), phải ghi bằng `approve` kèm `--by` nguyên văn; mơ hồ → hỏi lại; không bao giờ tự duyệt thay user.
- `tdq-plan`: vẫn hỏi mode trước khi viết plan; dòng mời đổi thành `➤ Duyệt: nhắn "duyệt plan mode main" (hoặc subagent) · Góp ý: nhắn trực tiếp`; mode ghi vào state là mode user nói (nếu user chỉ nói "duyệt plan" → hỏi mode, không tự chọn).
- `tdq-start` (quick), `tdq-spec`, `tdq-approve`, `README.md`: đổi mọi dòng mời sang ngôn ngữ tự nhiên; `tdq-approve` mô tả lại là "cách gõ nhanh, tương đương nói duyệt".

## 3. Hành vi sau khi đổi (ví dụ)

| User nói | Claude làm |
|---|---|
| "duyệt spec" | `approve spec --by "duyệt spec"` → báo đã ghi, sang bước plan (turn sau) |
| "ok plan, mode main" | `approve plan --mode main --by "…"` → implement ngay trong turn |
| "duyệt quick" (đã duyệt rồi) | CLI in "đã duyệt lúc …", Claude đi tiếp, **không báo lỗi** |
| "duyệt plan" (thiếu mode) | Hỏi lại: main hay subagent? |
| "sửa file X đi" khi chưa duyệt | Tool chạy bình thường; Claude nhận nhắc và tự nói: "phần này chưa duyệt, bạn xác nhận nhé?" |

## 4. Phạm vi QC / test / validate

- **Unit (red → green):**
  - `edit_gate`/`bash_gate`: mọi kịch bản cũ (edit code chưa duyệt, ghi state.json, git commit) → `permissionDecision == "allow"`; có `additionalContext` đúng nội dung; **không còn** case nào trả `deny`.
  - `tdq_state approve`: ghi đủ 4–5 khoá + sha256 đúng; idempotent exit 0; `--mode` ghi `implement_mode`; cảnh báo khi sai lane/thiếu file nhưng vẫn exit 0 và vẫn ghi; `--by` được cắt 200 ký tự.
  - `set` nay ghi được `spec_approved=true` (không còn PROTECTED_KEYS) — test cũ về "bảo vệ" bị **xoá/đảo chiều**.
  - `stop_gate`: dòng mời duyệt sai lane → **không** block (im lặng); working log cũ + repo đổi → vẫn block.
  - `prompt_context`: đang chờ duyệt → có dòng hướng dẫn ghi nhận duyệt; không có request → im lặng.
  - `load()` bù khoá cho state schema 2 (thiếu `*_approved_by`).
  - E2E: init → set spec_file → approve spec → approve plan --mode main → phase implement, không lệnh nào exit ≠ 0.
- **Cấu hình:** `hooks/hooks.json` không còn mục `UserPromptExpansion`; `claude plugin validate . --strict` PASS.
- **Smoke bản cài thật (0.2.0):** (a) edit code khi chưa duyệt → allow + có nhắc; (b) `approve quick` hai lần → cả hai exit 0; (c) Stop hook vẫn block khi thiếu working log; (d) không còn file `approve_gate.py`.

## 5. Definition of Done

1. `cd tests && python3 -m unittest discover .` PASS 100%, không còn test nào kỳ vọng `deny`/PROTECTED.
2. `grep -r "\"deny\"" hooks/` không còn kết quả (trừ chuỗi trong doc/comment lịch sử).
3. `validate --strict` PASS; plugin user-level lên **0.2.0**.
4. Smoke 4 mục ở §4 đạt.
5. Working log + report ghi rõ: đổi triết lý, cách duyệt mới, những gì không còn được bảo vệ.
6. README + skills không còn hướng dẫn nào bắt buộc gõ slash command để duyệt.

## 6. Rủi ro & xử lý

- **Mất bảo chứng "chỉ user duyệt được"**: state giờ do Claude ghi. Giảm thiểu bằng `--by "<nguyên văn>"` (đối chiếu được với transcript), quy tắc "mơ hồ thì hỏi", và working log ghi lại mỗi lần duyệt. Đây là đánh đổi user đã chọn.
- **Claude bỏ qua lời nhắc** (không còn deny ép buộc): nhắc được đặt ở đúng thời điểm (PreToolUse ngay trước khi sửa file) + prompt_context mỗi lượt; nếu vẫn trôi, bước sau có thể siết lại bằng `permissionDecision: "ask"` (hỏi user) thay vì `deny`.
- **Test cũ dựa trên deny** khá nhiều → sửa/loại bỏ có kiểm soát, ghi rõ số test trước/sau trong report.
