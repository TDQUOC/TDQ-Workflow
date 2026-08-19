# RESEARCH — Hướng B: output tool đang tốn ở đâu, và cắt được bằng gì

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Phát hiện 1 (chặn đường, lần thứ BA) — "thước đo chưa tồn tại" là SAI

Đề án 2026-08-17 viết nguyên văn: *"cần log số token tool trả về qua vài chục request thật
mới có mẫu … nó cần một thước đo chưa tồn tại."*

Thước đo **đã tồn tại từ trước**: `scripts/token_audit.py` (315 dòng), đọc transcript jsonl
của Claude Code, tính đúng carry-cost (`n/4 × số API call còn lại`), gom theo nhóm tool,
có sẵn `--top` liệt kê output đắt nhất. `context-budget.md` còn ghi sẵn lệnh chạy nó.

Đây là lần thứ ba đề án sai vì không kiểm tiền đề (lần 1: hướng D 87,7%; lần 2: hướng C
glob không đệ quy).

**Nhưng thước đo có khuyết tật phải vá trước khi tin số:** `CHARS_PER_TOKEN = 4` — ước
lượng ký tự/4, KHÔNG dùng `anthropic_tokenizer` như `skill_tokens.py`. Cùng loại lỗi
"dụng cụ đo sai" đã dính ở hướng C.

## Đo thật — 5 session gần nhất của project này

`python3 scripts/token_audit.py --sessions 5 --top 15`

5.388 API call · 5.216 tool call · tổng carry-cost **2.474.934.200 token**.

| Nhóm tool | Lần gọi | Carry-cost | % tổng |
|---|---|---|---|
| Read file | 450 | 874.168.878 | 35,3% |
| Bash khác | 1.510 | 549.580.802 | 22,2% |
| `mcp__excalidraw__get_canvas_screenshot` | 13 | 446.692.541 | 18,1% |
| `tdq_state.py` (dump JSON) | 488 | 137.621.608 | 5,6% |
| graphify | 134 | 99.762.852 | 4,0% |
| Edit (echo lại diff) | 1.142 | 97.770.837 | 4,0% |
| chạy test suite | 580 | 92.421.828 | 3,7% |
| tavily search | 29 | 66.090.473 | 2,7% |
| doc_lint | 344 | 43.294.019 | 1,7% |

Đọc bảng: **13 lần** gọi screenshot excalidraw tốn hơn **1.142 lần** Edit gấp 4,5 lần —
carry-cost phạt kích thước output, không phạt số lần gọi.

## Phát hiện 2 — hành vi Read: 64% là đọc LẠI

Quét 450 lần gọi `Read` trong 5 session đó:

| Chỉ số | Số | Tỉ lệ |
|---|---|---|
| Có `offset`/`limit` (đọc vừa đủ) | 148 | 32,9% |
| **Đọc lại file đã đọc trong CÙNG session** | 289 | **64,2%** |

File bị đọc lại nhiều nhất đều là khuôn của chính bộ skill: `plan-template.md` 27 lần,
`analyze-full.md` 24, `spec-template.md` 21, `lane-decision.md` 17, `interview.md` 14.

**Đây KHÔNG hiển nhiên là vi phạm.** Chính luật TDQ bắt đọc lại: `tdq-build/SKILL.md` ghi
*"BẮT BUỘC mở file đó và đọc hết … cấm làm theo trí nhớ"*, và `context-budget.md` liệt kê
**năm ca bắt buộc đọc lại** (context bị nén, đọc thiếu, file đã đổi, sắp sửa file, nhớ
không chắc). Nên phần lớn 64% này là **luật đang chạy đúng**, và cắt nó là cắt vào chất
lượng — trục cao nhất của soul. Đây là câu hỏi phải để user quyết, không tự quyết.

## Phát hiện 3 — hành vi Bash: luật gộp/giới hạn đang được tuân thủ khá tốt

3.059 lệnh Bash: 1.599 có `cat/head/tail`, trong đó **1.456 lệnh có `| head`/`| tail`**
(tự giới hạn). `grep -A/-B/-C` chỉ 176 lần. Tool `Grep` gần như không dùng (0 lần) —
mọi việc tìm đi qua Bash.

## Phát hiện 4 (đòn bẩy cấu hình, giống kiểu hướng D) — có trần chặn ở tầng nền tảng

| Khoá | Tác dụng | Mặc định | Độ tin cậy nguồn |
|---|---|---|---|
| `BASH_MAX_OUTPUT_LENGTH` | trần ký tự output Bash, vượt thì **cắt giữa** (giữ đầu + đuôi) | 30.000 ký tự | có trong bảng env của `code.claude.com/docs/en/settings`; hành vi cắt giữa xác nhận qua issue #19901 |
| `MAX_MCP_OUTPUT_TOKENS` | trần token cho output tool MCP, vượt thì cắt kèm dấu | 50.000 (cảnh báo từ 10.000) | deepwiki đọc mã nguồn + issue #7732 |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | trần token model SINH ra, **không** phải output tool | theo model | issue #10738 |

Lưu ý độ tin cậy: hai khoá đầu đến từ deepwiki/issue chứ không từ trang tài liệu chính
thức mô tả đầy đủ — phải kiểm bằng phiên thật trước khi tin, đúng bài học của hướng D.

**Nối với số đo:** `MAX_MCP_OUTPUT_TOKENS` là đòn bẩy duy nhất chạm được nhóm tốn 18,1%
(screenshot excalidraw) — nhóm mà không luật văn bản nào của TDQ với tới, vì nó là tool
của bên thứ ba.

## Nguồn

- `code.claude.com/docs/en/settings` — bảng biến môi trường.
- github.com/anthropics/claude-code/issues/19901 — Bash 30.000 ký tự, cắt giữa.
- github.com/anthropics/claude-code/issues/7732 — `MAX_MCP_OUTPUT_TOKENS` đã tồn tại.
- github.com/anthropics/claude-code/issues/10738 — phân biệt trần output model vs tool.
- deepwiki.com/kill136/claude-code-open/14.2-token-limits — đọc từ mã nguồn.
- Số đo nội bộ: `scripts/token_audit.py --sessions 5 --top 15`, chạy 2026-08-19.
