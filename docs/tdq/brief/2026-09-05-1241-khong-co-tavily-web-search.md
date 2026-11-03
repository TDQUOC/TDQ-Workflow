# BRIEF — Không có API Tavily thì workflow tra web bằng gì
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

"bây giờ mở reuqest nhanh giúp tôi check xem nếu như claude code chưa có api tavily thì bộ
workflow sẽ alfm gì? có web sreach đc không?"

Đọc lần đầu: user muốn biết hành vi của bộ workflow trên một máy CHƯA cấu hình Tavily API key —
luật `tdq-conventions` mục 8 bắt "web search đi qua `tavily-primary` trước, luôn luôn", nên câu
hỏi là: luật đó có đường lùi không, và Claude Code còn tra web được bằng gì.
Phạm vi đoán: đọc luật + cấu hình MCP + khuôn failover, trả lời bằng bằng chứng, không sửa mã.
Chỗ chưa rõ: user muốn CHỈ câu trả lời, hay muốn vá luật nếu phát hiện lỗ hổng.

## Hiểu & kiến thức

Bằng chứng đã đọc (B1, không dùng key nào trong báo cáo):

- `skills/tdq-conventions/SKILL.md:147` — luật gốc: web search đi qua `tavily-primary` trước,
  luôn luôn; trỏ sang `references/tavily.md`.
- `skills/tdq-conventions/references/tavily.md:3-5` — CÓ đường lùi ba tầng: primary → backup
  một lần khi lỗi kết nối/auth/timeout/quota/tool → cuối cùng mới dùng `WebSearch` nội trú,
  nhưng phải nêu lỗi một dòng và XIN PHÉP user rồi chờ duyệt. `WebFetch` dùng thẳng, không
  cần failover.
- `~/.claude.json` — hai server `tavily-primary`/`tavily-backup` đều là HTTP tới
  `https://mcp.tavily.com/mcp/`, header `Bearer ${TAVILY_API_KEY_PRIMARY}` và
  `${TAVILY_API_KEY_BACKUP}`. Máy này ĐÃ đặt cả hai biến (chỉ kiểm tra có/không, không in giá trị).
- Ba bundle (`portable_claude/.mcp.json`, `antigravity_portable/mcp_config.json`, và
  `scripts/tdq_checkportable.py:128-137`) lại chạy `npx tavily-mcp@latest` và cả hai server
  cùng đọc MỘT biến `TAVILY_API_KEY` — biến này CHƯA đặt trên máy này.
- `scripts/build_portable.py:494-497` — chính tài liệu của repo nói: biến không export thì
  server vẫn khởi động, lệnh gọi hỏng lúc chạy chứ không hỏng lúc khởi động.
- `scripts/tdq_lsp.py` bậc 2 chỉ kiểm server MCP `lsp`, không kiểm Tavily; không có script
  hay hook nào cảnh báo khi thiếu key Tavily.
- B2 (nghiên cứu ngoài repo): `WebSearch`/`WebFetch` là tool nội trú của Claude Code, độc lập
  với MCP — bằng chứng tại chỗ: cả hai có mặt trong danh sách tool của phiên này, và
  `~/.claude/settings.json` đặt `permissions.ask = ["WebSearch"]`, tức tool tồn tại và chỉ bị
  chặn bởi một lần hỏi quyền.

Kết luận sơ bộ: KHÔNG có key Tavily thì workflow vẫn tra web được bằng `WebSearch`/`WebFetch`,
nhưng phải đi qua một lần xin phép user, và không có tầng nào báo trước cho user rằng key thiếu.
Hai lỗ hổng thật: (1) `tavily.md` liệt kê lỗi failover mà không kể trường hợp tool KHÔNG TỒN TẠI;
(2) trong ba bundle, backup dùng chung biến với primary nên nó không phải backup thật.

## Hỏi đáp

1. Cây làm việc bẩn (2 file sổ sách của chính TDQ) — user chọn `1a`: mở nhánh luôn.
2. Loại nhánh — user chọn `2a`: `docs/khong-co-tavily-tra-web`.
3. Phạm vi — user chọn `3a`: CHỈ điều tra + báo cáo bằng chứng; phát hiện lỗ hổng thì nêu
   đề xuất, chưa sửa.
