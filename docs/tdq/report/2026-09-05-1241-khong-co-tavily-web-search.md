# BÁO CÁO — Máy chưa có API Tavily thì bộ workflow tra web bằng gì
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-09-05 · Lane: quick · Plan: ../plan/2026-09-05-1241-khong-co-tavily-web-search.md
Phạm vi: CHỈ điều tra và đề xuất (user chốt `3a`) — không sửa luật, cấu hình hay bundle.
Không giá trị key nào xuất hiện trong tài liệu này; chỉ nói biến CÓ đặt hay CHƯA đặt.

## 1. Trả lời thẳng hai câu hỏi

**Có, vẫn tra web được.** `WebSearch` và `WebFetch` là tool nội trú của Claude Code, không đi
qua MCP, nên chúng còn nguyên khi Tavily vắng mặt. Bằng chứng tại chỗ: cả hai có trong danh
sách tool của phiên này, và `~/.claude/settings.json` đặt `permissions.ask = ["WebSearch"]` —
một tool không tồn tại thì không có quyền để hỏi.

**Bộ workflow sẽ làm gì:** luật không dừng lại, nó tụt xuống tầng cuối. `tavily-primary` gọi
hỏng → `tavily-backup` đúng một lần → vẫn hỏng thì dùng `WebSearch`, kèm hai nghĩa vụ: nêu lỗi
một dòng, rồi XIN PHÉP user và chờ duyệt. Nguồn: `skills/tdq-conventions/references/tavily.md:5`.

Hệ quả thực tế trên máy chưa có key: mỗi lần cần tra web, agent mất một vòng hỏi–chờ, và
không có tầng nào báo cho user biết trước rằng key đang thiếu.

## 2. Chuỗi failover ba tầng — bằng chứng theo file:dòng

| Tầng | Nội dung | Nguồn |
|---|---|---|
| Luật gốc | "Web search đi qua `tavily-primary` trước, luôn luôn" | `skills/tdq-conventions/SKILL.md:147` |
| Tầng 2 | Lỗi kết nối/auth/timeout/quota/tool → gọi `tavily-backup` đúng một lần; kết quả rỗng KHÔNG phải lỗi | `skills/tdq-conventions/references/tavily.md:3` |
| Tầng 3 | Cả hai hỏng → `WebSearch` nội trú, nêu lỗi một dòng, xin phép user và chờ; `WebFetch` dùng thẳng | `skills/tdq-conventions/references/tavily.md:5` |
| Cấu hình | Hai server đều là HTTP tới `mcp.tavily.com`, header đọc `${TAVILY_API_KEY_PRIMARY}` và `${TAVILY_API_KEY_BACKUP}` | `~/.claude.json` khoá `mcpServers` |
| Thời điểm hỏng | Biến không export → server vẫn khởi động, lệnh gọi hỏng LÚC CHẠY | `scripts/build_portable.py:494-497` |
| Nơi luật được gọi | Bước B2 của lane deep và lane nhanh đều trỏ vào `tavily-primary` | `skills/tdq-intake/references/analyze-full.md:49`, `scripts/tdq_state.py:1080` |

Trạng thái máy này (chỉ kiểm CÓ/KHÔNG): `TAVILY_API_KEY_PRIMARY` và `TAVILY_API_KEY_BACKUP`
đã đặt; `TAVILY_API_KEY` chưa đặt.

## 3. Lỗ hổng phát hiện được

**Lỗ hổng 1 — luật không kể ca tool KHÔNG TỒN TẠI.** `tavily.md:3` liệt kê đúng năm dạng lỗi
(kết nối, auth, timeout, quota, tool error). Máy chưa cấu hình Tavily thì tool `tavily_*`
không hiện ra trong danh sách tool, tức không có lỗi nào để bắt — đây chính là tình huống
user hỏi, và nó rơi ra ngoài danh sách. Đọc chặt chữ, agent không có đường đi tiếp; đọc rộng
thì mỗi agent tự suy diễn một kiểu. Không script hay hook nào lấp chỗ này:
`scripts/tdq_lsp.py` bậc 2 chỉ kiểm server MCP `lsp` (`bac2_mcp`), không kiểm Tavily.

**Lỗ hổng 2 — trong ba bundle, backup không phải backup thật.** `portable_claude/.mcp.json`,
`antigravity_portable/mcp_config.json` và hàm sinh ra chúng (`scripts/tdq_checkportable.py:128`,
`scripts/build_portable.py:87`) cho cả `tavily-primary` lẫn `tavily-backup` chạy
`npx tavily-mcp@latest` với CÙNG một biến `TAVILY_API_KEY`. Cùng một key nghĩa là cùng một
hạn ngạch và cùng một trạng thái thu hồi: hết quota hoặc key hỏng thì cả hai tầng chết cùng
lúc, luật failover ở tầng 2 thành vô nghĩa. Thêm nữa, biến bundle cần (`TAVILY_API_KEY`) khác
biến mà `~/.claude.json` của máy này dùng, nên ai cài bundle trên chính máy này sẽ thấy cả
hai server im lặng dù key vẫn còn.

## 4. Đề xuất vá — CHƯA THỰC THI

**Đề xuất cho lỗ hổng 1** (một dòng vào `skills/tdq-conventions/references/tavily.md`): thêm ca
"tool `tavily_*` không có mặt trong phiên" vào cùng danh sách với năm dạng lỗi, và nói rõ ca
này bỏ qua luôn tầng backup, xuống thẳng `WebSearch` — vì thiếu cấu hình thì backup cũng
không tồn tại, thử nó chỉ tốn một lượt. Kèm một câu: lần đầu phát hiện thiếu Tavily trong một
request, báo cho user đúng một dòng "máy chưa cấu hình Tavily, tôi sẽ dùng WebSearch" thay vì
hỏi lại ở mọi truy vấn.

**Đề xuất cho lỗ hổng 2** (sửa `scripts/build_portable.py` và `scripts/tdq_checkportable.py`,
rồi dựng lại ba bundle): cho `tavily-primary` đọc `TAVILY_API_KEY_PRIMARY` và `tavily-backup`
đọc `TAVILY_API_KEY_BACKUP`, giữ `TAVILY_API_KEY` làm giá trị dự phòng cho ai chỉ có một key;
cập nhật đoạn hướng dẫn export ở `build_portable.py:494` và `:818` theo đúng hai tên mới. Việc
này chạm ba bundle nên cần một request riêng có test, không làm lén trong request điều tra này.

**Ngoài phạm vi, chỉ nêu để bạn biết:** hai key Tavily dạng chữ thường vẫn nằm trong
`docs/tdq/audit/settings-backup-2026-08-19.json` và file đó đã lên lịch sử GitHub công khai —
nên xoay key khi bạn rảnh.
