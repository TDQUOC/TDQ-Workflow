# BRIEF — Thực thi D-C-B-A(hybrid)-E: bộ workflow không lệ thuộc ngôn ngữ

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn
Nguyên văn user: "okay tôi muốn mở request xử lí DCBA hybrid yêu cầu phân tích và chuyển
đổi bộ workflow này giữ đủ rule / behavior về logic và xử lí để không bị lệ thuộc ngôn ngữ
và E"

Cách hiểu đầu tiên: user muốn THỰC THI (không chỉ phân tích) cả 5 hướng đã liệt kê trong
đề án `de-an-toi-uu-context.md`:
- D — `skillOverrides` (settings.json)
- C — tách reference ra khỏi SKILL.md chính
- B — cắt output tool dư thừa
- A (hybrid) — tách skill theo loại nội dung (luật lý luận → có thể tiếng Anh, khuôn
  user-facing + khai báo ngôn ngữ đầu ra → giữ tiếng Việt), mục tiêu rõ ràng: "giữ đủ
  rule/behavior về logic và xử lí để không bị lệ thuộc ngôn ngữ"
- E — router BM25 tự động (dù đề án cũ nói CHƯA đủ điều kiện — top-5 chỉ 45,5%, cần
  embedding đa ngữ + hook UserPromptSubmit trước)

Phạm vi đoán: đây là dự án LỚN, chạm toàn bộ ~40+ file SKILL.md/references trong
`skills/`, `portable_claude/`, `portable_codex/`, có thể cả `~/.claude/settings.json`,
và với hướng A-hybrid cần thêm gate mới (đo output có đúng tiếng Việt) + lưới khoá hành vi
theo đúng ranh giới "luật lý luận" vs "khuôn user-facing" — hai điều kiện đề án cũ đã nói
là CẦN trước khi làm A. Hướng E đề án cũ khuyến nghị CHƯA đủ điều kiện.

Chỗ chưa rõ, cần hỏi trước khi lock spec:
1. Làm cả 5 hướng trong 1 request lớn, hay tách thành nhiều request nhỏ theo thứ tự
   D → C → B → A(hybrid) → E (đã có sẵn thứ tự ưu tiên trong đề án)?
2. Hướng E đề án cũ nói CHƯA đủ điều kiện (thiếu embedding đa ngữ + hook tự động) — vẫn
   muốn làm dù biết trước rủi ro, hay để lại sau khi có điều kiện?
3. Hướng A-hybrid cần 2 điều kiện tiên quyết (gate đo ngôn ngữ đầu ra + lưới khoá hành vi
   đúng ranh giới) — làm 2 điều kiện đó trước như một phase riêng, hay coi là một phần của
   cùng request?

## Hiểu & kiến thức

### Năng lực dùng được
| Skill/công cụ | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `tdq-intake`, `tdq-spec`, `tdq-plan`, `tdq-build` | plugin:tdq-workflow | DÙNG | chạy phase tương ứng |
| `tdq-conventions` | plugin:tdq-workflow | NỀN | skill khung |
| `scripts/skill_tokens.py` | project | DÙNG | đo token mô tả trước/sau, cùng một cách đo |
| `tavily-primary` | mcp | DÙNG | tra tài liệu chính thức `skillOverrides` |
| Đã xét 280+ skill khác | plugin/built-in | KHÔNG | khác lĩnh vực — việc này là sửa cấu hình |

### Phát hiện chính — đề án cũ sai ở hướng D
Chi tiết + nguồn: `docs/tdq/research/2026-08-19-0046-huong-d-skill-overrides.md`.

1. **`skillOverrides` không áp cho plugin skill** (3 nguồn độc lập, có docs chính thức).
   261 khoá đề xuất cũ chỉ có 33 khoá có tác dụng; 228 khoá là no-op.
2. **Tiết kiệm thật của hướng D gốc: 8,8%** (2.632/29.788 token), không phải 87,7%.
3. **Câu hỏi mở của đề án đã đóng**: docs xác nhận `name-only` vẫn cho model gọi skill.
4. **Hai đòn bẩy mới** đề án chưa biết: `skillListingMaxDescChars` (cắt mô tả mọi skill,
   kể cả plugin) và `skillListingBudgetFraction`.
5. **Tiền sử hỏng âm thầm**: issue #50631 — `skillOverrides` từng là stub không tác dụng ở
   v2.1.114; v2.1.129 mới chạy thật. Máy đang chạy v2.1.234 nên đã qua, nhưng phải kiểm
   chứng bằng phiên thật chứ không tin suông.

### Chốt kiến thức — chọn trần 300 ký tự, và cái giá của nó
User chốt (1A): làm D1 (`skillOverrides` cho 33 skill `user`) + D2
(`skillListingMaxDescChars`). Chốt (2A): được ghi vào `~/.claude/settings.json`, backup trước.

Trần bao nhiêu là đánh đổi giữa token và độ chính xác chọn skill:

| Trần | Tiết kiệm | Số skill mất tín hiệu kích hoạt |
|---|---|---|
| 300 | 9.814 (32,9%) | 47 |
| 400 | 6.326 (21,2%) | 30 |
| 500 | 4.030 (13,5%) | 21 |

**Chọn 300**, vì cái mất nhỏ hơn con số 47 gợi ra:
- 6 skill `tdq-*` (138-155 ký tự) **không bị chạm**.
- Đường search thật của dự án là **MCP tool `mcp__tavily-primary__*`**, không đi qua skill
  `tavily-cli`/`tavily-dynamic-search` — listing skill không ảnh hưởng tool MCP, nên luật
  "tavily-primary là lớp search mặc định" (CLAUDE.md §3) không bị đụng.
- 45/47 skill bị cắt thuộc lĩnh vực không dùng trong dự án này (adobe, huggingface, unreal,
  qt, firecrawl, hyperframes, base44). 2 skill `user` bị ảnh hưởng thuộc mảng game Unity.
- Phần bị cắt là đuôi liệt kê cụm từ kích hoạt, không phải câu đầu nói skill làm gì.
- Đảo ngược trong 10 giây: xoá một dòng trong settings, mở phiên mới.

Rủi ro còn lại không giấu: cắt mô tả LÀ đánh đổi trên trục chất lượng (chọn sai skill),
trục cao nhất theo soul. Chấp nhận vì mức thiệt đo được nằm ngoài vùng dự án dùng, và
vì đảo ngược tức thì — khác hẳn hướng A (sửa chữ của luật, không đảo ngược được).

### Lộ trình
| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Phân tích | CÓ | đã xong — research + đo lại |
| Spec/Plan | CÓ | bắt buộc |
| Vòng scope | ĐÃ LÀM Ở CHAT | user chốt 1A+2A |
| Interview chi tiết thêm | BỎ | không còn câu hỏi nào đổi kết quả |
| QC độc lập bằng agent | BỎ | sửa cấu hình + đo lại bằng lệnh, tự kiểm là đủ |
| Chia subagent | BỎ | 1 module cấu hình, không tách được |
| Implement | CÓ | backup + ghi settings + sinh lại file đề xuất đúng 33 khoá |
| Report | CÓ | bắt buộc |

## Hỏi đáp
**Hỏi 1:** làm đòn bẩy nào — D1 / D1+D2 / D1+D2+D3?
**Đáp:** "1A" — D1 + D2 (không tắt hẳn plugin nào).
**Hỏi 2:** cho phép ghi `~/.claude/settings.json` không?
**Đáp:** "2A" — có, backup trước khi ghi.
