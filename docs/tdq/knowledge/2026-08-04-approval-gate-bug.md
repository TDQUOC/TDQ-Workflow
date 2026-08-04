# Knowledge — 2026-08-04-approval-gate-bug

## Năng lực dùng được

Phân vân → DÙNG. Không xoá bảng này kể cả khi mọi dòng là KHÔNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-build, tdq-conventions, tdq-intake, tdq-plan, tdq-spec, tdq-status | plugin:tdq-workflow | NỀN | chính workflow đang chạy |
| graphify, claude-md-improver, frontend-design, writing-hookify-rules, build-mcp-app, build-mcp-server, build-mcpb, playground, agent-development, command-development, hook-development, mcp-integration, plugin-settings, plugin-structure, skill-creator, remember, keybindings-help | user/plugin:*/built-in | KHÔNG | khác lĩnh vực (task là sửa Python hook script nội bộ của chính plugin tdq-workflow, không phải dựng hook/plugin/skill mới từ đầu) |
| update-config, tavily-best-practices, tavily-cli, tavily-crawl, tavily-dynamic-search, tavily-extract, tavily-map, tavily-research, tavily-search | built-in/plugin:tavily | KHÔNG | spec §3 đã chọn cách khác tốt hơn — đọc thẳng source `hooks/scripts/*.py` (đã đọc đủ) thay vì skill hướng dẫn generic; tavily dùng trực tiếp MCP tool `tavily-primary`, không qua skill hướng dẫn |

## Đọc code (tóm tắt)

- `hooks/hooks.json`: 5 hook — SessionStart, UserPromptSubmit, PreToolUse×2 (Edit-nhóm,
  Bash), Stop.
- `hooks/scripts/prompt_context.py`: **đã có sẵn** `looks_like_approval(prompt, target)`
  — regex nhận diện câu duyệt, đọc trực tiếp `payload["prompt"]` (KHÔNG qua transcript).
  Khi đang chờ duyệt (`spec`/`plan`/`quick`), mỗi `UserPromptSubmit` tính lại và in
  `[TDQ:APPROVE]` — hoặc "chạy NGAY lệnh approve" (khớp), hoặc "KHÔNG rõ là câu duyệt →
  hỏi lại" (không khớp). Đây chỉ là gợi ý (`additionalContext`, allow) — không có gì bắt
  buộc Claude tuân theo, và kết quả tính toán này **không được lưu lại** để tra cứu sau.
- `hooks/scripts/bash_gate.py`: quan sát mọi lệnh `tdq_state.py` (kể cả `approve`, `set
  phase=`) vào sổ turn, nhưng **không hề đối chiếu** với tín hiệu `looks_like_approval()`
  đã tính ở bước UserPromptSubmit. Đây là lỗ hổng: Claude có thể gọi `approve`/`set
  phase=` bất kể prompt trước đó có phải câu duyệt hay không, hook không phản ứng gì khác
  ngoài việc ghi lại (observe) cho bằng chứng hậu kiểm ở Stop.
- `hooks/scripts/stop_gate.py`: hook DUY NHẤT có quyền `block` thật, nhưng chỉ cho đúng
  1 điều kiện (repo đổi mà working log chưa ghi) — không liên quan gate duyệt.
- `hooks/scripts/_common.py`: `remind()` luôn trả `permissionDecision: "allow"` — plugin
  **chưa từng dùng** `"deny"` ở đâu. `already_reminded()` dedupe 1 lần/mã/turn nhưng chỉ
  xét dòng `kind=="remind"` — **đã kiểm lại**: `prompt_context.py` in `[TDQ:APPROVE]` bằng
  hàm nội bộ `_emit()` (chỉ `print()`, không gọi `_common.remind()`), nên KHÔNG ghi dòng
  `kind="remind"` nào. Vì vậy nhắc lần 2 ở `bash_gate.py` (dùng lại đúng mã `TDQ:APPROVE`,
  gọi `_common.remind()` thật) không bị dedupe nuốt — không có bẫy như đánh giá ban đầu.
- `scripts/tdq_state.py` `_cli_approve`: ghi nhận duyệt vô điều kiện, luôn `exit 0`
  ("không phải gate: cảnh báo khi lệch nhưng VẪN ghi" — comment tự nhận trong code).
  Không có validation nào giữa nội dung `--by` và luật `approval.md`.

## Lịch sử liên quan (git log)

- v0.1.4–0.1.6: từng có **gate cứng** `approve_gate` (chặn bằng slash command
  `/tdq-workflow:tdq-approve`), đọc **transcript** để tìm dòng mời duyệt cuối.
- v0.3.0: **bỏ hẳn** `approve_gate`, chuyển sang triết lý "verify-by-effect" (stop_gate chỉ
  tin dữ liệu quan sát trực tiếp — turn ledger, snapshot đĩa — không đọc transcript) vì
  cách đọc transcript cũ từng gây bug thật (chặn nhầm/bỏ sót, v0.1.8).
- `looks_like_approval()` trong `prompt_context.py` (thêm sau) khác về chất: đọc payload
  thô `UserPromptSubmit`, KHÔNG phải transcript — cùng lớp tin cậy với turn ledger mà
  kiến trúc 0.3.0 chấp nhận. Điểm này quan trọng cho quyết định bên dưới.

## Research (tóm tắt, đầy đủ ở `docs/tdq/research/2026-08-04-approval-gate-bug.md`)

- MAST taxonomy (arxiv 2503.13657): "fail to follow task requirements" là lỗi phổ biến
  (~11%), thuộc nhóm lỗi THIẾT KẾ HỆ THỐNG — khuyến nghị fix ở tầng kiến trúc/state, không
  chỉ tầng prompt.
- Pattern HITL chuẩn (nhiều nguồn khớp nhau): tách Ý ĐỊNH (agent đề xuất) khỏi THỰC THI
  (hệ thống enforce) — agent tự do suy luận, nhưng hành động thực thi bị chặn bởi điều
  kiện tường minh nằm NGOÀI khả năng tự quyết của agent.

## Quyết định đã chốt (qua vòng interview)

1. **Cơ chế xử lý: CHỈ siết soft-reminder, không thêm gate cứng (deny).** User chọn
   phương án này dù đã được nêu rõ rủi ro ("đã có nhắc rồi mà Claude vẫn bỏ qua được —
   không giải quyết gốc rễ"). Hướng kỹ thuật cụ thể (chốt ở bước viết spec, không phải ở
   đây): LƯU kết quả `looks_like_approval()` vào sổ turn (thêm 1 dòng `approve_signal`);
   `bash_gate.py` khi thấy Bash gọi `tdq_state.py approve <target>` hoặc `set phase=<kế
   tiếp>` mà tín hiệu turn nói "prompt gần nhất KHÔNG phải câu duyệt" → in một nhắc nhở
   MỚI, rõ ràng, đúng ngay thời điểm sắp phạm lỗi (không phải nhắc chung chung đầu turn) —
   vẫn `permissionDecision: allow` (không chặn), nhưng nội dung phải đủ mạnh để Claude tự
   dừng và hỏi lại. Không có bẫy dedupe cần né (xem mục Đọc code — đã kiểm lại và sửa).
2. **Phạm vi: cả 3 gate chính** — `spec_approved`, `plan_approved`, `quick_approved` (đã
   có sẵn field boolean + dòng mời duyệt chuẩn hoá cho cả 3 trong `prompt_context.py`).
   KHÔNG mở rộng sang các điểm dừng tự do khác (như câu hỏi commit T4.4) — những điểm đó
   không có tín hiệu regex rõ ràng như "duyệt spec/plan/quick" nên nằm ngoài phạm vi lần
   sửa này.
3. **Không audit lịch sử.** Sổ turn chỉ giữ log 6 giờ gần nhất (`TURN_STALE_SECONDS`),
   không lưu vĩnh viễn; rà lại xa hơn nghĩa là phải đọc transcript cũ — đúng cách đọc mà
   kiến trúc 0.3.0 đã từ bỏ vì không đáng tin. Chỉ tập trung ngăn ngừa lần sau.

## Rủi ro còn lại (ghi nhận, không phải chỗ chưa rõ)

Vì không có gate cứng, về mặt lý thuyết Claude vẫn CÓ THỂ bỏ qua nhắc nhở đã siết và gọi
`approve`/`set phase=` sai — nhắc nhở mạnh hơn giảm xác suất tái diễn nhưng không loại bỏ
hoàn toàn. Đây là đánh đổi user đã chọn có ý thức (né rủi ro tái lặp lỗi transcript-reading
của gate cứng cũ) — sẽ ghi lại nguyên văn trong spec §5 (ràng buộc & rủi ro).

## Kiểm cổng

- **Phạm vi cuối rõ chưa?** Rõ: sửa `prompt_context.py` (lưu tín hiệu vào sổ turn) +
  `bash_gate.py` (thêm nhắc nhở tại điểm sắp gọi approve/set phase, né dedupe) cho 3 gate
  spec/plan/quick. Không đổi hành vi hiện có ngoài phạm vi này.
- **Cần model / download / cài đặt gì không?** Không — thuần Python stdlib, đã có sẵn
  trong `hooks/scripts/`.
- **Phạm vi QC/test đã có chưa?** Có hướng: test hook bằng cách giả lập payload
  `UserPromptSubmit` (câu không phải duyệt) → `PreToolUse`/Bash gọi `tdq_state.py approve`
  → xác nhận nhắc nhở MỚI xuất hiện (không bị dedupe nuốt) và không chặn tool. Test suite
  hook hiện có (`tests/`) sẽ mở rộng thêm case này ở bước viết plan.
