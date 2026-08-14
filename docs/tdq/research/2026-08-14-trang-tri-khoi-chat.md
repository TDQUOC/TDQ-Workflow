# Research: Claude Code render markdown trên terminal CLI / desktop app / IDE extension

Ngày: 2026-08-14
Mục đích: xác định cấu trúc trình bày nào dùng được trong khối chat cuối turn để hiển thị đẹp và GIỐNG NHAU trên cả ba mặt (terminal CLI, desktop app Mac/Windows, IDE extension VS Code/JetBrains).

## Truy vấn 1 — Claude Code CLI markdown rendering terminal tables headings ANSI

Nguồn:
- https://github.com/anthropics/claude-code/issues/26390 (BUG, GFM ~60% được hỗ trợ)
- https://github.com/anthropics/claude-code/issues/13600 (feature request renderer)
- https://claude-code-from-source.com/ch13-terminal-ui (giải thích engine TUI tự viết dựa trên fork Ink)

Điều rút ra:
- Claude Code CLI CÓ một markdown-to-ANSI renderer riêng cho terminal (không phải in raw markdown thô hoàn toàn, nhưng cũng không phải renderer đầy đủ GFM).
- Theo issue #26390 (báo cáo kỹ, liệt kê rõ "Works" vs "Broken"):
  - Works: **bold**, *italic*, bold-italic, `inline code`, fenced code block + syntax highlight, diff block, bảng, list có thứ tự/không thứ tự, blockquote 1 cấp.
  - Broken: heading h2–h6 (tất cả render giống hệt bold, KHÔNG có phân cấp cỡ chữ/màu khác nhau), label của link (mất, chỉ còn URL thô), ~~strikethrough~~ (in ra literal `~~text~~`), task list `- [x]`/`- [ ]` (render như bullet thường, mất trạng thái check), nested blockquote (không tăng indent theo cấp), HTML entity (in thô).
- Issue này bị đóng "not planned" — Anthropic không cam kết sửa, nghĩa là hành vi này ổn định, không phải bug tạm thời.

## Truy vấn 2 — Claude Code desktop app vs terminal markdown rendering difference

Nguồn:
- https://www.mindstudio.ai/blog/claude-code-desktop-app-features
- https://www.iwoszapar.com/p/claude-code-cli-vs-desktop
- https://www.linkedin.com/posts/ant-murphy_... (bài PM so sánh 3 tháng dùng cả hai)

Điều rút ra:
- Desktop app CÓ renderer markdown riêng (khác terminal): "Headers look like headers. Lists format as lists. Code blocks get syntax highlighting." — ngụ ý heading desktop có phân cấp thị giác thật (không chỉ bold như terminal).
- Trước đây desktop app chỉ là "thin wrapper" quanh terminal (không render markdown khác gì terminal); bản cập nhật gần đây mới thêm markdown rendering riêng — xác nhận CÓ SỰ CHUYỂN ĐỔI/KHÁC BIỆT giữa hai mặt theo thời gian, không phải luôn đồng nhất.
- CLI và Desktop app dùng chung engine core (model, CLAUDE.md, settings, MCP, hooks, skills) nhưng lớp hiển thị (rendering layer) là khác nhau — theo iwoszapar.com.
- Không tìm được nguồn liệt kê chi tiết desktop app có tự resize font cho từng heading level hay không (chỉ có mô tả định tính "headers look like headers").

## Truy vấn 3 — anthropics/claude-code GitHub issue markdown table rendering terminal

Nguồn:
- https://github.com/anthropics/claude-code/issues/58983 (Terminal mode vs Native UI mode trong VS Code extension)
- https://github.com/anthropics/claude-code/issues/45111 (feature: native markdown rendering, box-drawing tables)
- https://github.com/anthropics/claude-code/issues/52731 (bug: bảng dài làm viewport để trống 80%)
- https://github.com/anthropics/claude-code/issues/14763 (bug: bảng chỉ hiện dòng cuối, Windows)
- https://github.com/anthropics/claude-code/issues/22311 (bug: bảng biến mất khi terminal full màn hình)
- https://github.com/anthropics/claude-code/issues/11274 và #13438 (bảng lệch cột khi có ký tự CJK)

Điều rút ra:
- **QUAN TRỌNG**: issue #58983 xác nhận chính thức trong VS Code extension có HAI chế độ khác nhau — "Terminal mode" (dùng renderer TUI giống CLI, bảng bị làm phẳng thành các dòng `key: value`, MẤT cấu trúc bảng) vs "Native UI mode" (renderer khác, bảng render đúng dạng cột). Đây là nguồn xác nhận rõ ràng nhất về sự KHÔNG ĐỒNG NHẤT giữa terminal-style rendering và native UI rendering, ngay trong cùng một IDE extension.
- Bảng markdown trên terminal CLI: về nguyên tắc render được, nhưng có nhiều bug đã ghi nhận (chưa chắc hết ổn định qua version): bảng rộng có thể sụp thành card key-value; bảng dài gây lỗi hiển thị viewport; bảng đôi khi mất dòng; bảng lệch cột khi terminal width thay đổi hoặc có ký tự CJK.
- Kết luận thực dụng: bảng CÓ render trên terminal nhưng RỦI RO CAO khi bảng rộng/nhiều cột — nên tránh hoặc giữ bảng hẹp, ít cột, ASCII thuần nếu cần dùng ở khối chat cuối turn.

## Truy vấn 4 — Claude Code VS Code / JetBrains markdown render output panel

Nguồn:
- https://github.com/anthropics/claude-code/issues/25234 (JetBrains: output panel render markdown nhưng không tùy biến màu được, khó đọc ở light mode)
- https://www.eesel.ai/blog/claude-code-vs-code-extension

Điều rút ra:
- JetBrains plugin output panel CÓ render markdown (heading, inline code...) nhưng theo issue là "khá khó đọc ở light mode" và không cho tùy chỉnh style/màu — nghĩa là hành vi render tồn tại nhưng chất lượng thị giác không đảm bảo đồng nhất, đặc biệt phối màu.
- VS Code extension dùng cùng `claude` binary lõi bên dưới nhưng bọc panel riêng có diff viewer trực quan — không có nguồn xác nhận riêng panel chat của VS Code extension có dùng markdown-to-HTML đầy đủ hay dùng renderer TUI giống terminal (issue #58983 gợi ý phụ thuộc "mode": Terminal mode = giống CLI, Native UI mode = renderer khác).

## Truy vấn 5 — ANSI escape code trong output, có render màu không

Nguồn:
- https://github.com/anthropics/claude-code/issues/18728 (ANSI code trong OUTPUT của lệnh bash bị strip khi hiển thị)
- https://github.com/anthropics/claude-code/issues/6635 (statusline: ANSI escape gõ tay không được render, hiện literal `\033[33m...`)
- https://github.com/anthropics/claude-code/issues/25346 (ANSI leak màu sang ký tự lân cận trên Windows Terminal — bug renderer nội bộ, không phải model tự in mã ANSI)
- https://blog.trailofbits.com/2025/04/29/deceiving-users-with-ansi-terminal-codes-in-mcp (nghiên cứu bảo mật: Claude Code KHÔNG lọc/sanitize ANSI trong tool output/description — có thể bị lợi dụng để ẩn nội dung)

Điều rút ra:
- KHÔNG tìm được nguồn trực tiếp trả lời "nếu model tự in ký tự escape ANSI (`\x1b[31m...`) trong nội dung trả lời (không phải qua tool output) thì Claude Code CLI có diễn giải thành màu hay không".
- Bằng chứng gián tiếp cho thấy XU HƯỚNG ngược lại ở 2 nơi đã kiểm chứng:
  - Statusline (nơi user tự viết script in ANSI) → hiện literal escape code, KHÔNG được render thành màu (issue #6635).
  - Output của lệnh bash chạy qua tool → ANSI bị strip khi hiển thị lại cho user (issue #18728).
  - Ngược lại, bài Trail of Bits cho thấy pipeline KHÔNG sanitize ANSI trong một số trường hợp (tool description/output từ MCP), nên có rủi ro bảo mật khi ANSI lọt qua — tức hành vi không nhất quán/không đảm bảo, tùy đường dữ liệu.
- Kết luận: KHÔNG CÓ NGUỒN xác nhận chắc chắn việc model tự in mã màu ANSI trong câu trả lời text sẽ hiển thị màu đúng ý trên cả ba mặt. Rủi ro ra ký tự rác trên desktop/IDE (vì các mặt này dùng renderer HTML/markdown, không phải terminal thô) là gần như chắc chắn — ANSI escape code không có ý nghĩa gì trong ngữ cảnh render HTML, sẽ hiện dưới dạng ký tự lạ hoặc bị strip tùy renderer.
- HTML inline (`<span style="color:...">`) trong nội dung markdown: KHÔNG TÌM ĐƯỢC NGUỒN xác nhận desktop app / IDE native UI có render HTML thô nhúng trong markdown hay không (theo thông lệ các markdown-to-HTML renderer thường sanitize/strip HTML thô vì lý do bảo mật, nhưng đây là suy luận từ thông lệ chung, KHÔNG có nguồn riêng cho Claude Code — không kết luận chắc). Trên terminal CLI thì chắc chắn KHÔNG render — hệ thống prompt nói rõ "rendered in a monospace font using the CommonMark specification" trên CLI, không có HTML renderer.

## Truy vấn 6 — Emoji / unicode box-drawing, độ rộng cột font mono

Nguồn:
- https://github.com/anthropics/claude-code/issues/13438 (bảng CJK lệch cột vì tính sai độ rộng ký tự)
- https://github.com/anthropics/claude-code/issues/4404 (box-drawing character hiện garbled trên WSL — vấn đề encoding/font terminal, không phải bug renderer)
- https://github.com/anthropics/claude-code/issues/11274 (bảng CJK lệch cột trên Claude Code web)
- https://github.com/charmbracelet/lipgloss/issues/562 (vấn đề chung của các TUI engine: tính sai độ rộng emoji/ZWJ/CJK gây lệch layout — không phải riêng Claude Code nhưng cùng lớp vấn đề kỹ thuật mà Claude Code TUI cũng gặp phải, theo cách engine của Claude Code được build tương tự — xem thêm ch13-terminal-ui)

Điều rút ra:
- Vấn đề độ rộng cột với emoji/CJK/box-drawing là XÁC NHẬN THẬT trên Claude Code cho các cấu trúc CẦN CĂN CỘT CHÍNH XÁC (bảng, box-drawing tự vẽ bằng ký tự như `┌─┬─┐`). Model tính sai độ rộng hiển thị (double-width CJK, emoji có ZWJ) → lệch cột.
- Với bullet đơn giản (•, ▸, ➤) không cần căn cột nhiều dòng, RỦI RO THẤP HƠN NHIỀU vì không đòi hỏi alignment nhiều ký tự khác độ rộng liên tiếp — nhưng KHÔNG có nguồn xác nhận trực tiếp bullet Unicode luôn an toàn 100% trên cả ba mặt (font terminal của user có thể thiếu glyph cho vài ký tự hiếm, gây tofu box □).
- Box-drawing character tự vẽ khung (không phải do renderer table sinh ra) là RỦI RO CAO nhất — vừa cần font hỗ trợ, vừa cần model tính đúng độ rộng mọi ký tự trên mọi dòng.

## Truy vấn 7 — Settings/theme/output-style liên quan tới render

Nguồn:
- https://code.claude.com/docs/en/settings (chính thức)
- https://code.claude.com/docs/en/output-styles (chính thức)
- https://code.claude.com/docs/en/terminal-config (chính thức)
- https://github.com/anthropics/claude-code/issues/26228 (feature request: cho phép tùy biến màu heading/hierarchy — chưa có, bị đóng dạng duplicate)

Điều rút ra:
- `theme` (settings.json): `"dark"` (mặc định) | `"light"` | `"auto"` | `"dark-daltonized"` | `"light-daltonized"` | `"dark-ansi"` | `"light-ansi"` | theme tùy biến qua file — CHỈ đổi bảng màu/ANSI mapping của giao diện CLI, KHÔNG thêm khả năng đổi cỡ chữ hay thêm cấu trúc markdown mới được hỗ trợ.
- `tui`: `"fullscreen"` (mặc định, renderer alt-screen có virtualized scrollback) vs `"default"` (renderer classic main-screen) — đổi qua lệnh `/tui`. Đây chính là biến ảnh hưởng tới bug bảng dài bị để trống viewport (issue #52731) — tức bug rendering PHỤ THUỘC vào chế độ `tui` đang bật.
- `outputStyle`: chỉ đổi SYSTEM PROMPT (giọng văn, độ dài, vai trò), KHÔNG đổi renderer/engine hiển thị — không giúp gì cho việc "trang trí khối chat" hiển thị đẹp hơn về mặt kỹ thuật render.
- Issue #26228 xác nhận: KHÔNG có cách nào (tính đến thời điểm bài đóng) để user tùy biến màu/hierarchy cho riêng các heading — bị đóng như duplicate của yêu cầu renderer tổng thể (#45111), tức tính năng này CHƯA CÓ, không phải do user cấu hình sai.

## Truy vấn 8 — Hệ thống prompt CLI mô tả khả năng markdown

Nguồn:
- https://blog.thepete.net/claude-code-system-prompt (bản chép lại system prompt bị rò rỉ/quan sát được — KHÔNG PHẢI tài liệu chính thức từ Anthropic, độ tin cậy thấp hơn docs.claude.com nhưng khớp với hành vi quan sát ở các issue trên)

Điều rút ra (cần hiểu đây là nguồn KHÔNG chính thức, dùng để đối chiếu chứ không phải căn cứ pháp lý):
- Câu nguyên văn được ghi lại: "Your output will be displayed on a command line interface. Your responses should be short and concise. You can use Github-flavored markdown for formatting, and will be rendered in a monospace font using the CommonMark specification."
- Điều này khớp với bằng chứng thực nghiệm ở các issue: renderer terminal dùng font monospace cố định, không có khái niệm "cỡ chữ" khác nhau theo heading — về mặt vật lý terminal, mọi ký tự cùng cỡ, không thể phóng to riêng lẻ trừ khi cả dòng terminal đổi cỡ font (điều đó là setting của terminal emulator, ngoài tầm kiểm soát của Claude Code).

## Bảng chốt

| Thành phần | Terminal (CLI) | Desktop app | IDE extension (VS Code/JetBrains) | Kết luận dùng được? |
|---|---|---|---|---|
| Heading `#`/`##`/`###` | CÓ render nhưng chỉ thành **bold**, KHÔNG phóng to, không phân biệt h2–h6 (nguồn: #26390) | CÓ, có phân cấp thị giác thật hơn theo mô tả định tính (nguồn: mindstudio blog) — KHÔNG có số liệu chính xác | TUỲ theo mode: Native UI render đúng hơn Terminal mode (nguồn: #58983); JetBrains render nhưng khó đọc ở light mode (nguồn: #25234) | KHÔNG đồng nhất — dùng heading để phân đoạn OK nhưng đừng trông cậy phân cấp cỡ chữ hiển thị giống nhau |
| **đậm**/*nghiêng*/`inline code` | CÓ, hoạt động tốt (nguồn: #26390 "Works") | CÓ (suy luận từ mindstudio, không có nguồn phủ định) | CÓ (JetBrains render markdown cơ bản — #25234) | AN TOÀN dùng cả ba mặt |
| ~~gạch ngang~~ | KHÔNG — in literal `~~text~~` (nguồn: #26390) | Không có nguồn xác nhận/phủ định trực tiếp | Không có nguồn xác nhận/phủ định trực tiếp | TRÁNH DÙNG — chắc chắn hỏng ở terminal |
| Bảng `\| … \|` | CÓ nhưng RỦI RO CAO: sụp key-value ở bảng rộng, lệch cột với CJK, mất dòng, biến mất khi resize (nguồn: #45111, #44696 nhắc tới, #14763, #22311, #13438) | Không có nguồn riêng, suy đoán tốt hơn vì có renderer HTML thật — KHÔNG XÁC NHẬN | Terminal mode = làm phẳng bảng thành từng dòng key:value, MẤT bảng; Native UI mode = render đúng (nguồn: #58983, xác nhận rõ nhất) | TRÁNH bảng rộng nhiều cột; nếu dùng, giữ bảng hẹp/ít cột và chấp nhận rủi ro terminal |
| `---` / blockquote `>` / list lồng / ```code``` | Code block + syntax highlight: CÓ, hoạt động tốt. Blockquote 1 cấp: CÓ. Blockquote lồng nhiều cấp: KHÔNG phân biệt indent (nguồn: #26390). `---`: không tìm được nguồn riêng | Không có nguồn riêng | Không có nguồn riêng | Code block AN TOÀN. Blockquote 1 cấp OK, tránh lồng nhiều cấp. `---` KHÔNG CÓ NGUỒN — cẩn trọng |
| Màu chữ qua ANSI escape tự in | KHÔNG có nguồn xác nhận model tự in ANSI được diễn giải thành màu; bằng chứng gián tiếp (statusline #6635, bash output #18728) cho thấy xu hướng bị strip/hiện literal, KHÔNG PHẢI RENDER | Chắc chắn KHÔNG (renderer không phải terminal, ANSI vô nghĩa trong HTML) | Terminal mode: giống CLI (không rõ). Native UI: chắc chắn KHÔNG | TRÁNH DÙNG — không có nguồn đảm bảo, rủi ro ra ký tự rác cao nhất trong toàn bộ khảo sát |
| HTML inline `<span style=...>` | KHÔNG (CLI dùng CommonMark monospace, không phải HTML renderer — theo system prompt không chính thức) | KHÔNG CÓ NGUỒN xác nhận/phủ định | KHÔNG CÓ NGUỒN xác nhận/phủ định | TRÁNH DÙNG — chắc chắn hỏng ở terminal, chưa xác định ở 2 mặt còn lại |
| Cỡ chữ (ngoài heading) | KHÔNG có cơ chế nào — về vật lý một terminal chỉ có 1 cỡ font cho toàn bộ dòng | KHÔNG CÓ NGUỒN xác nhận có cơ chế | KHÔNG CÓ NGUỒN xác nhận có cơ chế | KHÔNG DÙNG ĐƯỢC ở terminal; các mặt khác không xác định nhưng nhiều khả năng cũng không có cú pháp markdown thuần nào đổi cỡ chữ ngoài heading |
| Emoji / Unicode khung (─│┌╭▸➤•) | Bullet đơn giản: rủi ro thấp (không có bug report riêng). Box-drawing tự vẽ khung nhiều dòng: RỦI RO CAO, lệch cột do tính sai độ rộng CJK/emoji (nguồn: #13438, #11274, #4404) | Không có nguồn riêng | Không có nguồn riêng | Bullet đơn lẻ OK; TRÁNH tự vẽ box/bảng bằng ký tự Unicode nhiều dòng |
| Khác biệt terminal vs desktop/IDE đã ghi nhận | — | Có (desktop từng chỉ là wrapper không render markdown, mới thêm rendering riêng — mindstudio blog) | Có, xác nhận RÕ NHẤT: cùng 1 extension có 2 renderer khác nhau tùy mode (Terminal mode vs Native UI mode) trong #58983 | Kết luận chung: BA MẶT KHÔNG DÙNG CHUNG MỘT RENDERER — không có gì đảm bảo "giống nhau" tuyệt đối, nên ưu tiên cấu trúc markdown tối giản, đã xác nhận an toàn ở terminal (mặt khắt khe nhất) |
| Setting ảnh hưởng | `theme` (màu sắc/ANSI mapping), `tui` (fullscreen/default, ảnh hưởng bug bảng dài #52731) | Không có setting.json tương đương theo báo cáo PM (#linkedin) | JetBrains: không tùy biến được màu output panel (#25234) | Không có setting nào bổ sung khả năng markdown mới — chỉ đổi màu/renderer engine |
