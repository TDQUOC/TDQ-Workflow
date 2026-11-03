# RESEARCH — 2026-08-02-tdq-default-cleanup

## Truy vấn 1: enforce workflow mỗi prompt — hook vs CLAUDE.md
- Nguồn: datacamp.com/tutorial/claude-code-hooks · code.claude.com/docs/en/hooks-guide · joseparreogarcia.substack.com (Claude Code Hooks Explained) · github.com/disler/claude-code-hooks-mastery
- Rút ra: instruction trong CLAUDE.md là "guidance" model có thể quên khi context dài; hook chạy deterministic mỗi lần. Khuôn chuẩn: "skill makes Claude competent; hook makes Claude accountable". UserPromptSubmit fire trước khi model xử lý, có thể inject context nhắc bắt buộc → đây là chỗ đúng để ép intake.

## Truy vấn 2: viết description skill để luôn trigger
- Nguồn: platform.claude.com/docs/agent-skills/best-practices · code.claude.com/docs/en/skills · hidekazu-konishi.com (Skills Complete Guide) · github community #182117
- Rút ra: description là trigger, viết ngôi thứ 3, chứa nguyên văn cụm user hay gõ; muốn trigger mạnh thì nêu rõ "MỌI yêu cầu mới", liệt kê cả trường hợp dễ bị bỏ qua (câu hỏi nhỏ, check, fix nhanh). Có thể thêm `when_to_use` (cộng vào cap 1536 ký tự).

## Kết luận thiết kế
3 tầng để "always dùng TDQ": (1) CLAUDE.md §10 siết chữ "MỌI" + nêu rõ ngoại lệ (nếu có); (2) description tdq-intake liệt kê trigger phrases; (3) hook UserPromptSubmit của plugin inject nhắc "chưa có request mở → phải qua tdq-intake" khi phase idle/no_state — tầng deterministic.
