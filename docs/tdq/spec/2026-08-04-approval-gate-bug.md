# SPEC — 2026-08-04-approval-gate-bug

- Ngày: 2026-08-04
- Bản: 2 (sửa theo 3 góp ý `tdq-reviewer` — xem cuối file)
- Request: `docs/tdq/requests/2026-08-04-approval-gate-bug.md`
- Lane: full
- Trạng thái: ĐÃ DUYỆT (2026-08-04T19:51:46+07:00, "duyệt spec")

## 1. Mục tiêu & phạm vi

**Mục tiêu:** Khi Claude đang chờ user duyệt spec/plan/quick, nếu prompt tiếp theo của
user KHÔNG phải câu duyệt tường minh (góp ý, bổ sung, câu hỏi), phải có một nhắc nhở
mạnh, đúng thời điểm sắp phạm lỗi (ngay trước khi Claude gọi `tdq_state.py approve`)
để giảm khả năng Claude tự suy diễn là đã duyệt rồi tiến sang phase kế tiếp.

**Trong phạm vi:**
- Lưu kết quả `looks_like_approval()` (đã có sẵn trong `prompt_context.py`) vào sổ
  turn ledger để hook khác đọc lại được trong cùng turn — kể cả nhánh lệch mode
  (plan) để không bị coi nhầm là đã duyệt thật (xem §2 Đầu ra #1, mục "mode_conflict").
- Thêm logic đối chiếu trong `bash_gate.py`, bắt CẢ HAI lệnh Bash có thể dẫn tới việc
  "coi như đã duyệt rồi tiến phase" — đúng 2 con đường thật sự tồn tại trong code
  (đã xác nhận qua đọc `scripts/tdq_state.py`):
  1. `tdq_state.py approve <spec|plan|quick>` — tra tín hiệu vừa lưu của target đó.
  2. `tdq_state.py set phase=<plan|implement>` — vì `set phase=X` **không** tự kiểm
     `spec_approved`/`plan_approved` trước khi ghi (đọc `_cli_set`/`cli()` xác nhận),
     nên Claude hoàn toàn có thể bỏ qua bước `approve` và gọi thẳng lệnh này để
     "next phase" — đây chính là con đường cụ thể mà bug gốc user báo cáo có thể đi
     qua. Map đối chiếu: `set phase=plan` ↔ tín hiệu target `spec`; `set phase=implement`
     ↔ tín hiệu target `plan` (KHÔNG áp cho target `quick`: `approve quick` tự set
     `phase=implement` trong cùng lệnh — đã chặn ở nhánh 1, nhánh 2 dư thừa cho quick).
  Cả hai nhánh: nếu tín hiệu nói prompt gần nhất KHÔNG phải câu duyệt hợp lệ cho đúng
  target đó → in một nhắc nhở `[TDQ:APPROVE]` mới, rõ ràng, `permissionDecision:
  "allow"` (không chặn).
- Áp dụng cho cả 3 gate: `spec_approved`, `plan_approved`, `quick_approved`.
- Mở rộng test suite hook hiện có (`tests/test_prompt_context.py`,
  `tests/test_bash_gate.py`) cho hành vi mới.

**Ngoài phạm vi:**
- Không thêm gate cứng (`permissionDecision: "deny"`) — user đã chọn chỉ siết
  soft-reminder (xem `docs/tdq/questions/2026-08-04-approval-gate-bug.md` Q1).
- Không áp dụng cho các điểm dừng duyệt tự do khác (vd hỏi commit T4.4, hỏi mode
  implement) — chỉ 3 field `_approved` đã có sẵn dòng mời duyệt chuẩn hoá.
- Không audit/rà lại lịch sử các lần đã xảy ra trước đây (Q3) — sổ turn chỉ giữ 6
  giờ, rà xa hơn phải đọc transcript cũ (kiến trúc 0.3.0 đã từ bỏ cách đọc này).
- Không đổi hành vi `_cli_approve` trong `tdq_state.py` (vẫn ghi vô điều kiện — đây
  là chỗ cố ý theo triết lý "không phải gate" hiện tại, spec này không đổi triết lý
  đó, chỉ thêm lớp nhắc nhở trước khi lệnh đó được gọi).
- Không thêm mã reminder mới — tái dùng đúng mã `TDQ:APPROVE` đã có trong danh sách
  đóng 5 mã (`skills/tdq-conventions/references/reminder-codes.md`).

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn | Đo "xong" bằng |
|---|---|---|---|
| 1 | `prompt_context.py` lưu tín hiệu duyệt vào turn ledger | `hooks/scripts/prompt_context.py` | Khi `pending` khác `None`, mỗi lần chạy ghi đúng 1 dòng `kind="signal"` vào `.tdq-turn.jsonl` với các trường `event=approve_pending`, `target=<pending>`, `matched=<bool>`, `mode_conflict=<bool>` (chỉ `True` khi `pending=="plan"` và câu duyệt khớp nhưng nói sai mode — ghi dòng này TRƯỚC nhánh early-return cảnh báo mode ở code hiện có, để tín hiệu luôn được lưu dù hàm return sớm) |
| 2 | `bash_gate.py` đối chiếu tín hiệu khi thấy `approve <target>`, nhắc khi sai | `hooks/scripts/bash_gate.py` | Giả lập: dòng `signal` gần nhất `matched=False, target=spec` + lệnh Bash `tdq_state.py approve spec ...` → hook in `additionalContext` chứa mã `[TDQ:APPROVE]` + `permissionDecision=allow`. Case `matched=True, mode_conflict=True` cũng phải bị coi là "chưa thực sự duyệt" → vẫn nhắc. |
| 3 | `bash_gate.py` đối chiếu tín hiệu khi thấy `set phase=<plan\|implement>`, nhắc khi sai | `hooks/scripts/bash_gate.py` | Giả lập: dòng `signal` gần nhất `matched=False, target=spec` + lệnh Bash `tdq_state.py set phase=plan` → hook in nhắc `[TDQ:APPROVE]` như trên. Tương tự cho `set phase=implement` ↔ target `plan`. Không áp cho target `quick`. |
| 4 | Test hook mở rộng | `tests/test_prompt_context.py`, `tests/test_bash_gate.py` | `python3 -m pytest tests/test_prompt_context.py tests/test_bash_gate.py -q` exit 0, có ít nhất 7 test case mới: 2 (signal ghi đúng, gồm case `mode_conflict`), 2 (approve nhắc/im lặng), 2 (set phase= nhắc/im lặng), 1 (fail-open khi ledger không có dòng `signal` nào — xem §5 R3) |
| 5 | Không phá vỡ hành vi cũ | toàn bộ `tests/` | `python3 -m pytest -q` toàn bộ suite exit 0 |

## 3. Cách tiếp cận & lý do

**Chọn:** Lưu tín hiệu `looks_like_approval()` (+ cờ `mode_conflict` cho nhánh plan
lệch mode) vào turn ledger (`kind="signal"`) tại `prompt_context.py`, rồi
`bash_gate.py` tra lại tín hiệu này khi thấy lệnh `tdq_state.py approve <target>`
HOẶC `tdq_state.py set phase=<plan|implement>` sắp chạy, in nhắc nhở mới nếu lệch.

**Vì:**
- `looks_like_approval()` đọc trực tiếp `payload["prompt"]` thô của
  `UserPromptSubmit` — cùng lớp tin cậy với turn ledger/snapshot đĩa mà kiến trúc
  0.3.0 đã chấp nhận (không phải đọc transcript, tránh lặp lại lỗi khiến gate cứng
  cũ v0.1.4–0.1.6 bị bỏ ở v0.3.0 — xem git log `62b9d6f`, `5da97cb`, `8e9bc66`).
- Turn ledger (`.tdq-turn.jsonl`, qua `tdq_state.turn_log_append`/`turn_log_read`)
  là cơ chế sẵn có, đã dùng cho `observe`/`remind` — tái dùng, không cần cơ chế
  lưu trữ mới.
- Đúng nguyên tắc HITL "tách Ý ĐỊNH khỏi THỰC THI" (research §3,
  `docs/tdq/research/2026-08-04-approval-gate-bug.md`): điểm THỰC THI (`tdq_state.py
  approve`) là nơi cần một tín hiệu độc lập xác nhận trước khi chạy — không phải
  chặn cứng, nhưng nhắc đúng lúc, đúng chỗ.
- **Không có bẫy dedupe:** `prompt_context.py` in tín hiệu bằng hàm nội bộ `_emit()`
  (chỉ `print()` JSON), KHÔNG gọi `_common.remind()` — nên không ghi dòng
  `kind="remind"` nào vào ledger. `already_reminded()` (dùng trong `_common.remind()`
  của `bash_gate.py`) chỉ xét các dòng `kind=="remind"`, nên nhắc nhở mới ở
  `bash_gate.py` dùng lại mã `TDQ:APPROVE` không bị dedupe nuốt mất. (Sửa lại đánh
  giá ban đầu trong `knowledge/2026-08-04-approval-gate-bug.md` mục "Đọc code" dòng
  nói cần "né bẫy dedupe" — sau khi đọc lại chính xác `_common.py`/`prompt_context.py`,
  bẫy đó không tồn tại.)

**Đã loại:**
- *Gate cứng (`permissionDecision: "deny"`) khi tín hiệu sai* — user chọn không làm
  (Q1), chấp nhận rủi ro còn lại (§5) để tránh lặp lỗi transcript-reading của gate
  cũ đã bị bỏ ở v0.3.0.
- *Thêm mã reminder mới (`TDQ:APPROVE2` hay tương tự)* — không cần: bảng đóng 5 mã
  đã có `TDQ:APPROVE` với ngữ nghĩa tài liệu hoá đã bao trùm đúng ca này ("Đang chờ
  duyệt hoặc user vừa duyệt... Ghi nhận duyệt, hoặc HỎI nếu mơ hồ"). Thêm mã mới sẽ
  phải sửa `reminder-codes.md` (tài liệu đóng) không cần thiết.
- *Sửa `_cli_approve` trong `tdq_state.py` để validate `--by`* — đổi triết lý "không
  phải gate" hiện tại của tầng state (docstring tự nhận), ngoài phạm vi user đã chốt
  (chỉ siết reminder, không đổi cách ghi nhận).
- *Đối chiếu bằng cách đọc lại toàn bộ lịch sử transcript* — đúng cách kiến trúc
  0.3.0 đã từ bỏ vì gây bug thật (chặn nhầm/bỏ sót, v0.1.8).
- *Áp nhánh `set phase=` cho cả target `quick`* — không cần: `approve quick` đã tự
  set `phase=implement` trong cùng lệnh (đọc `_cli_approve` xác nhận), nên nhánh 1
  (`approve`) đã chặn đủ cho quick; thêm nhánh 2 cho quick chỉ trùng lặp, không thêm
  giá trị.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-build, tdq-conventions, tdq-intake, tdq-plan, tdq-spec, tdq-status | plugin:tdq-workflow | NỀN | chính workflow đang chạy |
| graphify, claude-md-improver, frontend-design, writing-hookify-rules, build-mcp-app, build-mcp-server, build-mcpb, playground, agent-development, command-development, hook-development, mcp-integration, plugin-settings, plugin-structure, skill-creator, remember, keybindings-help | user/plugin:*/built-in | KHÔNG | khác lĩnh vực (task là sửa Python hook script nội bộ của chính plugin tdq-workflow, không phải dựng hook/plugin/skill mới từ đầu) |
| update-config, tavily-best-practices, tavily-cli, tavily-crawl, tavily-dynamic-search, tavily-extract, tavily-map, tavily-research, tavily-search | built-in/plugin:tavily | KHÔNG | spec §3 đã chọn cách khác tốt hơn — đọc thẳng source `hooks/scripts/*.py` (đã đọc đủ) thay vì skill hướng dẫn generic; tavily dùng trực tiếp MCP tool `tavily-primary`, không qua skill hướng dẫn |

## 4. Yêu cầu bắt buộc

- Log service: turn ledger đã tự bật mặc định (`tdq_state.turn_log_append`), không
  cần config mới; dòng `signal` mới kế thừa cùng cơ chế bật/tắt hiện có.
- Không placeholder: cả 2 file sửa (`prompt_context.py`, `bash_gate.py`) phải chạy
  thật, có test giả lập payload thật (không stub logic chính).
- Test cho từng phần: tối thiểu 1 test xác nhận `prompt_context.py` ghi đúng dòng
  `signal`; tối thiểu 1 test xác nhận `bash_gate.py` nhắc đúng khi lệch, và 1 test
  xác nhận im lặng (không nhắc thêm) khi tín hiệu khớp đã duyệt đúng.

## 5. Ràng buộc & rủi ro

| # | Rủi ro/ràng buộc | Mức | Ứng phó |
|---|---|---|---|
| R1 | Không có gate cứng — Claude về lý thuyết vẫn có thể bỏ qua nhắc nhở đã siết và gọi `approve` sai | Trung bình, đã được user chấp nhận có ý thức (Q1) | Nhắc nhở phải đủ rõ ràng, đặt đúng thời điểm PreToolUse ngay trước lệnh `approve`, không phải nhắc chung chung đầu turn — giảm xác suất tối đa có thể trong phạm vi soft-reminder |
| R2 | Turn ledger chỉ giữ log gần (`TURN_STALE_SECONDS = 6h`) — dòng `signal` từ prompt cũ hơn 6h bị coi hết hạn | Thấp | Đây là hành vi nhất quán với cơ chế `_row_age_ok` đã có sẵn cho các `kind` khác — không cần xử lý riêng, chấp nhận: quá hạn thì không có tín hiệu để đối chiếu → không nhắc thêm (fail-open, đúng triết lý hiện tại) |
| R3 | Nếu Bash gọi `approve`/`set phase=` mà không có dòng `signal` nào trong turn (vd Claude gọi lệnh mà không qua `UserPromptSubmit` mới, hoặc test không set up) | Thấp | Fail-open: không tìm thấy tín hiệu → không nhắc gì thêm (giữ nguyên hành vi cũ), tránh false positive — có test case riêng xác nhận (§2 Đầu ra #4) |
| R4 | Không audit lịch sử — nếu lỗi này đã từng xảy ra nhiều lần trước đây, spec này không đo lường được cải thiện thực tế, chỉ ngăn tái diễn từ nay | Thấp, user đã chốt (Q3) | Không cần xử lý — ngoài phạm vi theo quyết định user |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh | Điều kiện PASS |
|---|---|---|---|
| Q1 | `prompt_context.py` ghi dòng `signal` đúng schema khi đang chờ duyệt, kể cả nhánh lệch mode | `python3 -m pytest tests/test_prompt_context.py -q` | Exit 0, gồm 2 case: (a) `kind="signal", event="approve_pending", target=<pending>, matched=<bool>, mode_conflict=False` xuất hiện trong `turn_log_read` cho câu duyệt/không-duyệt thường; (b) câu duyệt plan đúng target nhưng sai mode → dòng signal có `matched=True, mode_conflict=True` |
| Q2 | `bash_gate.py` nhắc đúng khi tín hiệu lệch lúc gọi `approve` (gồm cả case mode_conflict) | `python3 -m pytest tests/test_bash_gate.py -q` | Exit 0, gồm 2 case: (a) payload Bash `tdq_state.py approve spec ...` + ledger `signal matched=False target=spec` → output chứa `[TDQ:APPROVE]` + `permissionDecision=allow`; (b) payload Bash `tdq_state.py approve plan --mode main ...` + ledger `signal matched=True mode_conflict=True target=plan` → vẫn nhắc |
| Q3 | `bash_gate.py` im lặng (không nhắc thêm) khi tín hiệu khớp thật (`matched=True, mode_conflict=False`) lúc gọi `approve` | `python3 -m pytest tests/test_bash_gate.py -q` | Case: ledger `signal matched=True mode_conflict=False target=plan` + Bash gọi `approve plan` → không phát sinh nhắc `TDQ:APPROVE` mới từ điều kiện này |
| Q4 | `bash_gate.py` nhắc đúng khi tín hiệu lệch lúc gọi `set phase=<plan\|implement>` (đường vòng bỏ qua `approve`) | `python3 -m pytest tests/test_bash_gate.py -q` | Exit 0, gồm 2 case: (a) payload Bash `tdq_state.py set phase=plan` + ledger `signal matched=False target=spec` → nhắc `[TDQ:APPROVE]`; (b) payload Bash `tdq_state.py set phase=implement` + ledger `signal matched=False target=plan` → nhắc tương tự |
| Q5 | Fail-open khi ledger không có dòng `signal` nào (R3) | `python3 -m pytest tests/test_bash_gate.py -q` | Case: ledger rỗng (không có `kind="signal"` nào trong turn) + Bash gọi `approve spec ...` → không phát sinh nhắc mới ngoài hành vi cũ |
| Q6 | Không phá vỡ test suite hiện có | `python3 -m pytest -q` | Toàn bộ suite exit 0 |
| Q7 | doc_lint spec | `python3 scripts/doc_lint.py docs/tdq/spec/2026-08-04-approval-gate-bug.md` | Exit 0 |

**DoD:** Q1–Q7 đều PASS, `spec_approved = true`.

## 7. Câu hỏi còn mở

(rỗng — đã chốt đủ qua vòng interview `docs/tdq/questions/2026-08-04-approval-gate-bug.md`)

## Ghi chú review (agent `tdq-reviewer`, bản 1 → bản 2)

3 góp ý, đã áp dụng cả 3:
1. **[Nghiêm trọng]** Bản 1 chỉ đối chiếu lệnh `approve`, bỏ sót đường vòng
   `tdq_state.py set phase=<X>` — lệnh này không tự kiểm `*_approved` trước khi ghi,
   nên là đường thật user báo cáo bug có thể đi qua. Đã bổ sung nhánh 2 vào §1/§2/§3/§6.
2. Nhánh plan lệch mode (câu duyệt đúng đối tượng nhưng sai mode) trước đó sẽ ghi
   `matched=True` dù chưa thực sự nên approve — đã thêm cờ `mode_conflict` vào schema
   signal (§2 Đầu ra #1) và yêu cầu `bash_gate.py` vẫn nhắc khi `mode_conflict=True`.
3. Thiếu test case cho đúng kịch bản fail-open (R3) đã cam kết — đã thêm Q5 (§6) và
   cập nhật số lượng test tối thiểu ở §2 Đầu ra #4.
