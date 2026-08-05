# REQUEST — 2026-08-05-dat-ten-subagent

## Nguyên văn user

> okay hãy commit và xử lí tiếp vấn đè là hiện tại khi tôi thấy claude code spam
> sub-agent ko có tên model-think level ở đầu tên subagent nữa. ví dụ sonnet-low-
> resreach hoặc opus-medium-fix-doc. hãy phân tích và set đó là rule đặt tên cho
> sub-agent

(Phần "commit" đã xử lý xong ở turn trước — request này chỉ còn phần đặt luật tên subagent.)

## Cách hiểu đầu tiên

- Mục tiêu: mọi lần Claude Code gọi Agent tool (subagent) đều phải đặt tên/description
  bắt đầu bằng `<model>-<effort>-` (vd `sonnet-low-research`, `opus-medium-fix-doc`) để
  nhìn tên là biết model + effort đang chạy.
- Phát hiện ban đầu: luật này **đã tồn tại** ở `skills/tdq-conventions/SKILL.md` §9
  (`<model>-<effort>_ <mô tả>`) nhưng chỉ được nạp khi đang chạy TDQ build (agent
  `tdq-implementer`/`tdq-qc-tester`/`search-scout`…). Agent tool gọi ngoài luồng TDQ
  (research ad-hoc, `Explore`, `general-purpose` trong hội thoại thường) không nạp skill
  này nên không có luật nào áp — đây có thể là lý do user thấy "spam sub-agent không có
  tên chuẩn".
- Phạm vi đoán: cần nâng luật lên tầng toàn cục (`~/.claude/CLAUDE.md` hoặc file portable
  tương ứng) để áp cho MỌI lần gọi Agent tool, không riêng TDQ. Rủi ro: `~/.claude/CLAUDE.md`
  chỉ còn ~95 byte trống (3405/3500) — thêm luật cần rất ngắn hoặc phải cắt chỗ khác.
- Chỗ chưa rõ: định dạng chính xác (dấu `_` hay `-` sau effort), có cần áp cho agent
  built-in do harness tự gọi (không qua tay Claude, vd một số subagent nội bộ) hay chỉ
  áp cho agent do Claude chủ động gọi qua Agent tool, và có cần đồng bộ ngược lại
  `skills/tdq-conventions/SKILL.md` §9 theo định dạng mới hay giữ nguyên.
