# BRIEF — Hướng B: cắt output tool

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> D  (chọn: commit hướng C rồi mở luôn request tiếp theo — hướng B, cắt output tool)
> tiếp

Bối cảnh: user đã chốt thứ tự làm các hướng của đề án `docs/tdq/audit/de-an-toi-uu-context.md`
là **D → C → B → A(hybrid) → E**. D xong (request `2026-08-19-0046`), C xong
(request `2026-08-19-0121`, commit `ea0cdbd`). Đây là lượt của **hướng B**.

### Cách hiểu đầu tiên

- Mục tiêu: giảm token do **output của tool** chiếm trong context giữa một request —
  đọc cả file khi chỉ cần vài chục dòng, `grep` không giới hạn, đọc lại file đã có
  trong context.
- Điểm khác biệt cốt lõi so với D và C: **luật đã có sẵn** (`tdq-conventions/references/context-budget.md`
  + §10 `tdq-conventions/SKILL.md`). Hướng B phần lớn không phải viết luật mới mà là
  làm cho luật sẵn có **được tuân thủ** — tức là bài toán gate/lưới khoá, không phải
  bài toán soạn văn bản.
- Chỗ đề án tự nhận còn thiếu, nguyên văn: *"Chưa đo được trong request này: cần log số
  token tool trả về qua vài chục request thật mới có mẫu. Đó là việc của request sau,
  và nó cần **một thước đo chưa tồn tại**."*

### Chỗ chưa rõ (phải chốt trước khi viết spec)

1. Có dựng thước đo (log token output tool) trước, hay siết luật trước rồi đo sau?
2. Siết bằng cách nào: chỉ sửa văn bản luật · thêm hook chặn thật · hay cả hai?
3. Phạm vi bản: chỉ `skills/`, hay đồng bộ cả `portable_claude/` + `portable_codex/`?

### Cảnh báo mang từ hai vòng trước sang

Đề án đã sai **hai lần liên tiếp** (D: 87,7% → thật 8,8%; C: thiếu 20% số đo vì glob
không đệ quy), cùng một nguyên nhân: không ai kiểm thước đo và tiền đề. Hướng B chưa có
số nào — nên vòng này **cấm** tuyên bố mức tiết kiệm khi chưa có phép đo tự chạy được.

## Hiểu & kiến thức

### Năng lực dùng được

| Skill/công cụ | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `tdq-intake` | plugin:tdq-workflow | DÙNG | phase này |
| `tdq-spec`, `tdq-plan`, `tdq-build` | plugin:tdq-workflow | DÙNG | các phase sau |
| `tdq-conventions` | plugin:tdq-workflow | NỀN | skill khung; §10 + `context-budget.md` chính là luật của hướng B |
| `tdq-status` | plugin:tdq-workflow | KHÔNG | không hỏi trạng thái |
| `scripts/token_audit.py` | project | DÙNG | thước đo carry-cost — đã tồn tại, xem Phát hiện 1 |
| `scripts/context_surface.py` | project | DÙNG | đo bề mặt tài liệu theo tầng nạp + tốc độ hook |
| `scripts/step_audit.py` | project | XÉT | đo chi phí BƯỚC (runtime), khác trục với carry-cost |
| `mcp__tavily-primary__*` | plugin | DÙNG | tra biến môi trường trần output |
| Đã xét 278 skill khác | plugin/built-in | KHÔNG | khác lĩnh vực |

### Phát hiện chính (chi tiết + nguồn ở `docs/tdq/research/2026-08-19-1046-huong-b-cat-output-tool.md`)

1. **Tiền đề của đề án sai lần thứ BA.** Đề án nói hướng B "cần một thước đo chưa tồn
   tại". `scripts/token_audit.py` đã có sẵn, tính đúng carry-cost, `context-budget.md`
   còn ghi sẵn lệnh chạy. Nhưng nó dùng `CHARS_PER_TOKEN = 4` thay vì `anthropic_tokenizer`
   — dụng cụ đo có sẵn nhưng chưa chuẩn, đúng loại lỗi vừa dính ở hướng C.
2. **Số thật, 5 session:** 2.474.934.200 token carry-cost. Read 35,3% · Bash 22,2% ·
   một tool MCP bên thứ ba (screenshot excalidraw) 18,1% chỉ với 13 lần gọi.
3. **64,2% lần gọi `Read` là đọc LẠI file đã đọc trong cùng session** — nhưng phần lớn
   là do CHÍNH luật TDQ bắt đọc lại ("cấm làm theo trí nhớ", năm ca bắt buộc đọc lại).
   Cắt chỗ này là cắt vào chất lượng, phải để user quyết.
4. **Luật gộp/giới hạn Bash đang được tuân thủ khá tốt:** 1.456/1.599 lệnh có `cat/head/tail`
   đã tự giới hạn bằng `| head`. Nghĩa là dư địa ở phần văn bản luật MỎNG hơn đề án tưởng.
5. **Có đòn bẩy cấu hình chưa dùng:** `BASH_MAX_OUTPUT_LENGTH` (30.000 ký tự) và
   `MAX_MCP_OUTPUT_TOKENS` (50.000). Đòn bẩy thứ hai là thứ DUY NHẤT chạm được nhóm
   18,1% kia, vì không luật văn bản nào của TDQ với tới tool của bên thứ ba.

6. **Trần cấu hình gần như KHÔNG dùng được** (đo 5 session, kích thước output thật):

   | tool | lần | trung vị | p99 | max | vượt 30.000 |
   |---|---|---|---|---|---|
   | Bash | 3.067 | 399 | 7.854 | 25.654 | **0** |
   | Read | 450 | 2.960 | 20.596 | 43.989 | 3 |

   `BASH_MAX_OUTPUT_LENGTH` (mặc định 30.000) chưa bao giờ chạm tới — hạ nó xuống chỉ
   cắt mất output thật, không cắt lãng phí. Chỗ tốn nằm ở **số lần gọi × kích thước
   trung vị**, tức hành vi. Đòn bẩy cấu hình còn lại đúng một cái: `MAX_MCP_OUTPUT_TOKENS`
   cho nhóm output khổng lồ của tool bên thứ ba.
7. **Hạ tầng để siết đã có sẵn:** `hooks/scripts/bash_gate.py` là hook PreToolUse kiểu
   "quan sát + nhắc, KHÔNG chặn" (đúng quyết định kiến trúc 2026-07-29), và
   `tests/test_token_audit.py` đã tồn tại — thêm luật vào chỗ có sẵn, không dựng mới.

### Phạm vi đã chốt

- Mặt CHỌN: hiệu năng context · bảo trì thước đo · độ tin cậy (không cắt nhầm chất lượng) · tương thích (cấu hình + 3 bản)
- Mặt LOẠI: bảo mật · trải nghiệm người dùng · an toàn dữ liệu — request chỉ chạm tài liệu, script đo và cấu hình cục bộ
- Bối cảnh: 5 session · 5.216 tool call · 2.474.934.200 token carry-cost · Bash 3.067 lần trung vị 399 ký tự · Read 450 lần 64,2% là đọc lại · 0 lệnh Bash chạm trần 30.000
- Mức đầu tư suy ra: **đầy đủ** — bộ workflow dùng hàng ngày, chạm cả cấu hình máy lẫn ba bản phát hành, nên hiệu năng và độ tin cậy thành hạng mục QC riêng có ngưỡng số

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ (xong ở analyze) | phải tra biến môi trường trần output, không đoán |
| Đo bằng số thật | CÓ (xong ở analyze) | đề án không có số nào cho hướng B |
| Vòng scope | CÓ (xong ở chat) | user chốt 1ABCD · 2A · 3A |
| Interview chi tiết thêm | BỎ | mọi câu còn lại đã trả lời được bằng số vừa đo, không câu nào đổi kết quả |
| Chia subagent | BỎ | phiên hiện tại cấm gọi AgentTool khi user không yêu cầu |
| QC độc lập (agent) | BỎ | cùng lý do trên; QC chạy bằng lệnh đo lại được, không cần agent |
| Sinh lại portable + test khoá | CÓ | user chốt 3A |

## Hỏi đáp

**Vòng scope (2026-08-19 13:52).** Hỏi 3 câu: (1) mặt nào, (2) đầu ra là gì, (3) phạm vi bản.
User trả lời nguyên văn: `1abcd 2a 3a`.

- 1ABCD — lấy cả bốn mặt: hiệu năng context, bảo trì thước đo, độ tin cậy, tương thích/cấu hình.
- 2A — patch thật vào `skills/` + `scripts/` + cấu hình, có test khoá, đo lại trước/sau.
- 3A — sửa cả ba bản, sinh lại portable bằng `build_portable.py`, có test khoá.

**Đính chính do chính vòng đo phát hiện (không hỏi user, ghi lại để spec không đi sai):**
đề xuất ban đầu của tôi có ý hạ `BASH_MAX_OUTPUT_LENGTH`. Số đo bác bỏ: 0/3.067 lệnh Bash
chạm trần. Spec vì vậy KHÔNG đụng khoá đó, chỉ dùng `MAX_MCP_OUTPUT_TOKENS`.

**Sự cố giữa phase (13:52-14:11):** mất quyền đọc thư mục project ở tầng macOS (TCC),
`ls`/`head`/`python3` đều `Operation not permitted` kể cả khi tắt sandbox. User cấp lại
quyền, phiên tiếp tục. Không mất dữ liệu — brief và research đã nằm trên đĩa.
