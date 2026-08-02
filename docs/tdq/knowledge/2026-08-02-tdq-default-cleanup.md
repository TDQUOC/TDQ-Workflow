# KNOWLEDGE — 2026-08-02-tdq-default-cleanup

## Năng lực dùng được
| Skill/công cụ | Phán quyết | Lý do |
|---|---|---|
| tdq-intake/spec/plan/build/conventions | DÙNG | chính đối tượng sửa + quy trình chạy request này |
| doc_lint.py (`--pair`) | DÙNG | validate spec/plan/SKILL.md sửa xong |
| unittest suite (367) | DÙNG | test hook + skill shape sau sửa |
| tavily-primary search | ĐÃ DÙNG | research hook vs instruction, description trigger |
| claude-md-improver | KHÔNG | sửa CLAUDE.md user-level theo yêu cầu cụ thể, không cần audit tổng |
| skill-creator/plugin-dev | KHÔNG | sửa nhỏ description + nội dung, đã nắm chuẩn từ research |

## Quyết định đã chốt (user trả lời vòng 1)
1. **Mọi prompt là yêu cầu mới → bắt buộc qua tdq-intake**, kể cả câu hỏi thuần giải đáp/đọc. Message trong luồng request đang mở (duyệt, góp ý, trả lời interview) không tính là yêu cầu mới.
2. **Bỏ trọn §5 "superpower"** khỏi `~/.claude/CLAUDE.md` — các ý giá trị (report file external, tick plan, one-turn, spec≠plan turn, hỏi commit) đã nằm trong plugin tdq-workflow.
3. **Thêm tầng hook deterministic**: hook UserPromptSubmit của plugin (prompt_context.py) khi phase idle/no_state in nhắc `[TDQ:INTAKE]` — mọi prompt lúc đó phải mở intake trước khi làm gì khác.

## Cách tiếp cận
3 tầng: (1) CLAUDE.md mục TDQ Workflow (§9 số mới) viết lại đầu mục: MỌI prompt mới (kể cả câu hỏi/check/fix nhỏ) → tdq-intake, đánh số lại sau khi xóa §5; (2) description + nội dung skill tdq-intake liệt kê trigger cả các case dễ né (câu hỏi nhỏ, check, giải thích); (3) sửa `hooks/scripts/prompt_context.py` thêm nhắc [TDQ:INTAKE] khi idle/no_state — có unit test red→green.

## Phương án đã loại
- Chỉ dùng instruction (không hook): loại — research xác nhận instruction là xác suất, hook mới deterministic.
- Giữ một phần §5: loại — trùng lặp hoàn toàn với plugin, user chốt bỏ trọn.

## Ràng buộc
- CLAUDE.md sau sửa phải pass doc_lint (R5 câu ≤40 từ áp cho file doc TDQ; CLAUDE.md chỉ cần gọn).
- Hook sửa xong phải pass suite 367 + test mới; không phá format `[TDQ:NEXT]` hiện có.
- Câu hỏi kiểm cổng: output = CLAUDE.md mới + SKILL.md intake mới + prompt_context.py mới + test; không cần model/download; QC = unittest + doc_lint + thử hook bằng lệnh thật.

## Nguồn
- research/2026-08-02-tdq-default-cleanup.md (hooks-guide, skills best-practices, hooks-mastery).
