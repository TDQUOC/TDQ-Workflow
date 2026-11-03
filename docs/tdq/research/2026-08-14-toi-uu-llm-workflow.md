# RESEARCH — Tối ưu workflow cho LLM (context cost + model yếu vẫn tuân rule)

Ngày: 2026-08-14 · Tự chạy 2 truy vấn qua `tavily-primary` (không giao sub-agent: hệ
thống phiên này cấm gọi Agent tool khi user không yêu cầu; bù lại giới hạn 5 kết quả/truy vấn).

## Truy vấn 1 — chuẩn viết skill cho agent

`Anthropic agent skills authoring best practices progressive disclosure SKILL.md token efficiency`

Điều rút ra:

- Ngưỡng khuyến nghị: thân `SKILL.md` **dưới ~500 dòng**; vượt thì tách sang file rời và
  chỉ trỏ tới. 6 skill TDQ đều dưới ngưỡng (cao nhất 120 dòng) — không phải chỗ phí.
- Chỉ metadata (`name` + `description`) của mọi skill được nạp sẵn lúc khởi động; thân
  file chỉ vào context khi skill được gọi, file `references/` chỉ vào khi được đọc. Vậy
  chi phí thật nằm ở **tầng nạp**, không phải tổng dung lượng repo.
- File reference dài hơn 100 dòng nên có mục lục ở đầu để agent nhảy đúng chỗ.
- "Mặc định agent đã thông minh": chỉ thêm thứ agent chưa biết; mỗi đoạn phải tự trả giá
  token của nó. Dùng **một thuật ngữ duy nhất** cho một khái niệm, tránh biến thể.
- Tránh câu gắn mốc thời gian trong luật ("trước tháng 8/2025…"), đẩy xuống phụ lục.

Nguồn:
- https://github.com/obra/superpowers/blob/main/skills/writing-skills/anthropic-best-practices.md
- https://generativeprogrammer.com/p/skill-authoring-patterns-from-anthropics
- https://medium.com/@nimritakoul01/anthropics-agent-skills-0ef767d72b0f

## Truy vấn 2 — model nhỏ và độ tuân thủ chỉ dẫn

`prompt engineering smaller weaker LLM instruction following reliability explicit steps checklist constraint adherence`

Điều rút ra:

- Model nhỏ cần chỉ dẫn **chi tiết hơn và định dạng đầu ra cụ thể hơn**, không phải ngắn
  hơn. Prompt gọn tới mức ngụ ý sẽ rơi rule.
- Chia nhỏ việc (decomposition): bước tuần tự, mỗi bước một hành động — model yếu hỏng ở
  chỉ dẫn dài nhiều nhánh, không hỏng ở chỉ dẫn nhiều bước ngắn.
- Checklist copy được và vòng `chạy → kiểm → sửa → lặp` là cách bù năng lực suy luận.

Nguồn:
- https://web.dev/articles/practical-prompt-engineering
- https://pub.towardsai.net/ultimate-guide-to-prompt-engineering-940d463ba0e5
- https://cameronrwolfe.substack.com/p/modern-advances-in-prompt-engineering

## Xung đột phải giải quyết ở spec

Hai mặt user chọn kéo ngược nhau. Nguồn Anthropic nói thẳng: mức chi tiết phải nhắm vào
**model yếu nhất mình định hỗ trợ** — thứ đọc là "súc tích" với Sonnet có thể là "quá
cụt" với Haiku. Vậy không thể vừa cắt tối đa token vừa tăng độ tuân thủ của model yếu
bằng cùng một thao tác. Lối ra khả dĩ, do spec chốt:

1. Cắt phần **giải thích/lý lẽ** (thứ model nào cũng suy ra được), giữ và làm dày phần
   **mệnh lệnh + định dạng đầu ra + checklist** (thứ model yếu hay rơi).
2. Đẩy chi tiết ít dùng xuống `references/` — model mạnh bỏ qua, model yếu đọc khi cần.
3. Chuẩn hoá thuật ngữ: một khái niệm một tên, cắt biến thể — vừa giảm token vừa tăng
   tuân thủ, đây là chỗ hai mặt cùng chiều.
