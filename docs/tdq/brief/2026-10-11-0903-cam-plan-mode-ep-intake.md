# BRIEF — Cấm đổi mode, cấm popup tool, bắt buộc tdq-intake

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

User:
"Okay bây giờ nở request xử lí 1 vấn đề. Có tình trạng ghi nhận là khi yêu cầu mở request và nêu yêu cầu ra thay vì mở tdq intake và vào tdq workflow thì claude code và codex tự nhảy qua plan mode . Tôi muốn xử lí triệt để là instruction cho agent code là ko đc tự ý đổi mode hiện tại. Và khi người dùng yêu cầu mở request bắt buộc phải gọi intake và chạy theo pipeline của tdq workflow chứ không được mở plan mode, và các câu hỏi trong tdq workflow phải bắt buộc là reply trong chat để khi người dùng cần bổ sung thì có thể bổ sung, tuyệt đối ko đc trigger question ui của agent code"

**Mục tiêu:**
Xử lý triệt để tình trạng Claude Code và Codex tự ý chuyển sang Plan Mode (`EnterPlanMode`) hoặc gọi popup question UI (`AskUserQuestion`) khi người dùng nêu yêu cầu/mở request:
1. Instruction cấm tuyệt đối agent code tự ý chuyển đổi mode hiện tại (đặc biệt là cấm tự ý vào plan mode / gọi tool `EnterPlanMode`).
2. Khi người dùng yêu cầu mở request hoặc nêu task, bắt buộc phải kích hoạt `tdq-intake` và vận hành theo pipeline của TDQ Workflow (không được bypass bằng plan mode của harness).
3. Mọi câu hỏi và duyệt trong TDQ Workflow bắt buộc phải trao đổi trực tiếp trong chat (để người dùng dễ dàng bổ sung thông tin), tuyệt đối cấm trigger UI câu hỏi popup (`AskUserQuestion`) của agent code.

**Phạm vi dự kiến:**
- `skills/tdq-intake/SKILL.md`: Bổ sung chỉ dẫn chặn plan mode / `EnterPlanMode`, bắt buộc chạy luồng intake khi có request.
- `skills/tdq-conventions/SKILL.md`: Củng cố quy tắc cấm tự ý chuyển mode / cấm popup UI.
- `skills/tdq-conventions/references/approval.md`: Củng cố quy định cấm plan mode / cấm đổi mode harness.
- `skills/tdq-conventions/references/user-facing-block.md`: Nhấn mạnh chat-only, cấm popup question UI.
- `.claude-plugin/plugin.json` & `.codex-plugin/plugin.json`: Cập nhật description hoặc chỉ dẫn nếu cần thiết để harness ưu tiên intake.
- `docs/notes/user-level-install.md`: Cập nhật block instruction mẫu cho `~/.claude/CLAUDE.md`.

## Hiểu & kiến thức
- Hiện trạng: Harness của Claude Code có tool `EnterPlanMode` và system prompt khuyến khích tự vào plan mode khi gặp task triển khai mới. Điều này làm xung đột với spec-driven pipeline của TDQ Workflow (nơi plan được lập sau intake/spec và do người dùng duyệt theo gate của workflow).
- Tương tự, harness có tool `AskUserQuestion` thường tự kích hoạt dạng dialog/modal khiến người dùng bị gò bó vào các option dựng sẵn, không thể tự do gõ phản hồi hoặc bổ sung ngữ cảnh trong chat.
- Giải pháp: Đặt rào chắn instruction rõ ràng tại các điểm tiếp nhận (`SKILL.md` của `tdq-intake`, `tdq-conventions`, tài liệu hướng dẫn setup CLAUDE.md) cấm gọi `EnterPlanMode` và `AskUserQuestion`. Mọi request phải khởi đầu qua `tdq-intake`.

## Hỏi đáp
- Vòng chọn pipeline: đang thực hiện.
