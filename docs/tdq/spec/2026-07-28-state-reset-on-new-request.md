# SPEC — Yêu cầu mới ⇒ state được đồng bộ lại theo lane user chọn

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->
<!-- doc-lint: allow R8 -->  <!-- spec viết trước 0.3.3, chưa có mục 3b -->

Ngày: 2026-07-28 · Slug: `2026-07-28-state-reset-on-new-request` · Lane: full · Trạng thái: **CHỜ DUYỆT**
Request nguồn: [request](../requests/2026-07-28-state-reset-on-new-request.md) · Phiên bản plugin đích: **0.1.7**

## 1. Vấn đề

State TDQ có thể "kẹt" ở request cũ trong khi Claude đã trình plan cho yêu cầu mới:

- Bên `insightfaceserverv2`: state = `2026-07-28-kiosk-pose-guidance` (lane full, phase implement, plan đã duyệt). User nêu yêu cầu mới (nhãn hologram), Claude trình **mini-plan lane quick** nhưng **không init lại state**. User gõ `/tdq-workflow:tdq-approve quick` → gate chặn "Sai lane: request đang ở lane full". User mất lượt, workflow bế tắc.
- Lưới an toàn đã có (stop_gate chặn dòng mời duyệt không hợp lệ) **không bắt được**: transcript tại thời điểm hook chạy chưa chứa message cuối, `last_assistant_text()` đọc phải message trước đó. Replay đúng chuỗi đó vào bản 0.1.5 thì chặn đúng ⇒ logic đúng, **cách đọc transcript sai**.

## 2. Mục tiêu

1. Chọn lane cho một yêu cầu MỚI ⇒ **mặc định state được ghi lại toàn bộ**: `active_request`, `lane`, `phase`, `spec_file`, `plan_file`, mọi field duyệt, `implement_mode`.
2. Không để dòng mời duyệt "không thể thực hiện được" tới tay user (lưới an toàn phải hoạt động kể cả khi transcript trễ).
3. Khi vẫn xảy ra lệch, thông báo phải cho biết **chính xác lệnh cần chạy** để sửa.

**Không nằm trong phạm vi:** nới lỏng gate duyệt (field duyệt vẫn chỉ do user gõ lệnh), đổi cú pháp lệnh duyệt, tự động đóng/ghi đè request đang dở mà không hỏi user.

## 3. Giải pháp

### 3.1 `scripts/tdq_state.py` — init là hành động "mở request mới"
- `init <slug> <lane>` giữ nguyên hành vi reset toàn bộ về `default_state()` (đây chính là điều user muốn), nhưng:
  - Nếu đang có `active_request` khác và request đó **chưa hoàn tất** (phase ∉ {`report`, `idle`} hoặc còn field duyệt true), in ra **stderr** dòng cảnh báo: `⚠️ Ghi đè request '<slug cũ>' (lane <lane>, phase <phase>) — mọi trạng thái duyệt của request đó bị xoá.` Exit code vẫn 0 (không chặn).
  - Ghi `previous_request` = slug cũ vào state mới (chỉ để truy vết/log).
- Schema: thêm khoá `previous_request` (mặc định `null`), `schema_version` → 2; `load()` tự bù khoá thiếu cho state cũ (không cần migrate thủ công).
- `previous_request` **không** thuộc `PROTECTED_KEYS`.

### 3.2 `hooks/scripts/stop_gate.py` — đọc transcript theo LƯỢT, không chỉ 1 message
- Thay `last_assistant_text()` bằng `turn_assistant_texts()`: quét ngược transcript, gom text của mọi assistant message cho tới khi gặp **prompt user thật** (entry `type=user`, content là chuỗi, không bắt đầu bằng `Stop hook feedback`), tối đa 8 message.
- Kiểm dòng mời duyệt trên **tất cả** text gom được ⇒ transcript trễ 1 message vẫn bắt đúng.
- Giữ nguyên quy tắc 0.1.6: chỉ dòng chứa `Để duyệt:` mới tính là lời mời (nhắc tên lệnh trong văn bản không bị chặn nhầm).
- Thông điệp chặn khi sai lane/chưa có request nêu **lệnh cụ thể**: `... tdq_state.py init <slug-mới> <quick|full>` kèm nhắc "init reset toàn bộ state cho yêu cầu mới".

### 3.3 `hooks/scripts/prompt_context.py` — nhắc request đang mở mỗi lượt
- Khi có request mở, luôn in thêm 1 dòng nhận diện: `[TDQ] Request đang mở: <slug> · lane <lane> · phase <phase>. Nếu prompt này là YÊU CẦU MỚI → chạy init <slug-mới> <lane user chọn> (reset toàn bộ state) TRƯỚC khi trình spec/plan.`
- Dòng trạng thái/nhắc duyệt hiện có giữ nguyên (tối đa 2 dòng khi có request mở, 0 dòng khi không có).

### 3.4 `hooks/scripts/approve_gate.py` — message sai lane có lệnh sửa
- "Sai lane" (cả nhánh quick và spec/plan) bổ sung: `Yêu cầu Claude chạy: python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" init <slug> <lane đúng> rồi trình lại.`

### 3.5 Skills
- `tdq-start`: init là **bắt buộc cho MỌI yêu cầu mới**, kể cả khi đang có request khác mở; nếu request cũ còn dở dang thì **hỏi user** trước khi ghi đè (nêu rõ slug/phase sẽ mất).
- `tdq-conventions`: phân biệt rõ `init` (mở request mới, reset toàn bộ — luôn được phép khi user chọn lane) vs `reset` (đóng hẳn, chỉ khi user yêu cầu).

## 4. Output cụ thể

| File | Thay đổi |
|---|---|
| `scripts/tdq_state.py` | cảnh báo ghi đè, `previous_request`, `schema_version` 2 |
| `hooks/scripts/stop_gate.py` | `turn_assistant_texts()`, message có lệnh init |
| `hooks/scripts/prompt_context.py` | dòng nhận diện request đang mở |
| `hooks/scripts/approve_gate.py` | message sai lane kèm lệnh sửa |
| `skills/tdq-start/SKILL.md`, `skills/tdq-conventions/SKILL.md` | quy tắc init cho yêu cầu mới |
| `tests/test_state.py`, `test_stop_gate.py`, `test_prompt_context.py`, `test_approve_gate.py` | test mới |
| `.claude-plugin/plugin.json` | 0.1.6 → 0.1.7 |

Không cần model, không cài thêm gói (stdlib), không đổi dữ liệu người dùng ngoài `docs/tdq/state.json`.

## 5. Phạm vi QC / test / validate

- **Unit (bắt buộc, red → green):**
  - state CLI: init đè request dở → có cảnh báo stderr + `previous_request` đúng + mọi field duyệt về false; init khi state rỗng → không cảnh báo; `previous_request` set được qua `set`, các field duyệt vẫn bị từ chối.
  - stop_gate: transcript mà message CUỐI không có dòng mời nhưng message trước đó trong cùng lượt có (mô phỏng lag) + state sai lane → **block**; dòng mời cũ ở lượt TRƯỚC (đã qua 1 prompt user thật) → **không** block; các case 0.1.6 giữ nguyên.
  - prompt_context: có request mở → có dòng "Request đang mở"; không có request → im lặng.
  - approve_gate: message sai lane chứa `init`.
- **Regression:** toàn bộ suite hiện có (67 test) phải PASS.
- **Validate đóng gói:** `claude plugin validate . --strict` PASS; `claude plugin update tdq-workflow@tdq-local` lên 0.1.7.
- **Smoke trên bản cài thật:** dựng project tạm ở lane full/phase implement → chạy stop_gate với transcript mô phỏng lag + dòng mời quick → phải block; chạy init lane quick → state reset đủ khoá → approve quick thành công.

## 6. Definition of Done

1. Toàn bộ test (cũ + mới) PASS bằng một lệnh: `cd tests && python3 -m unittest discover .`
2. `validate --strict` PASS, plugin user-level ở 0.1.7.
3. Smoke tái hiện đúng kịch bản lỗi trong ảnh: state lane full + trình mời duyệt quick → bị chặn TRƯỚC khi tới tay user; sau khi init lane quick → duyệt quick chạy được.
4. Working log ngày ghi đủ: nguyên nhân, file đổi, kết quả test/smoke.
5. Không có field duyệt nào set được ngoài approve_gate (test cũ vẫn xanh).

## 7. Rủi ro & xử lý

- **Quét nhiều message có thể chặn nhầm** dòng mời đã được xử lý trong cùng lượt → giới hạn theo ranh giới prompt user thật + tối đa 8 message; có test cho ranh giới lượt.
- **Đè mất tiến độ request cũ** → cảnh báo ở CLI + skill bắt hỏi user trước khi đè.
- **Bump schema_version** có thể làm state cũ đọc lệch → `load()` bù khoá thiếu, có test với state schema_version 1.
