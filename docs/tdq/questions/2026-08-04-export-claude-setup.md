# Questions: 2026-08-04-export-claude-setup

## Vòng 1 — 2026-08-04

**1. Bản export nên gồm những project nào (ngoài phần cấu hình global ~/.claude)?**
- a) Global + repo TDQWorkflow (Đề xuất) — copy nguyên repo vào export vì đây là project
  đang làm việc VÀ là nguồn local marketplace của plugin tdq-workflow (không có git remote).
- b) Chỉ global — không copy project nào.
- c) Global + cả 3 project từng mở (TDQWorkflow, Project01_LiveCaptionTranslate,
  insightfaceserverv2).
- **User chọn: a) "Global + repo TDQWorkflow (Đề xuất)"**

**2. 2 key TAVILY_API_KEY_PRIMARY/BACKUP hard-code trong settings.json — xử lý sao?**
- a) Placeholder rõ ràng (Đề xuất) — giữ cấu trúc, thay giá trị bằng
  `<ĐIỀN_KEY_CỦA_BẠN>`, README hướng dẫn lấy key tại tavily.com.
- b) Bỏ hẳn 2 dòng key khỏi export.
- **User chọn: a) "Placeholder rõ ràng (Đề xuất)"**

**3. Máy đích là hệ điều hành gì?**
- a) macOS khác (Đề xuất).
- b) Đa nền (macOS/Linux/Windows-WSL).
- **User chọn: b) "Đa nền (macOS/Linux/Windows-WSL)"** — KHÔNG theo đề xuất; README phải
  có nhánh hướng dẫn cài dependency riêng cho macOS (brew), Linux (apt/dnf tuỳ distro), và
  Windows qua WSL.

**4. Hình thức bản export: chỉ README thủ công, hay kèm script tự động hoá?**
- a) Manifest + README thủ công (Đề xuất) — liệt kê lệnh từng bước, user tự chạy tay.
- b) Manifest + README + script tự động (setup.sh).
- **User chọn: a) "Manifest + README thủ công (Đề xuất)"**

## Vòng 2 — 2026-08-04

**5. Vì export chứa cả bản copy repo TDQWorkflow — đặt thư mục export ở đâu để tránh lồng
   repo vào chính nó?**
- a) Thư mục riêng ngoài TDQWorkflow (Đề xuất) — ví dụ `~/Documents/claude-code-export/`.
- b) Thư mục con bên trong TDQWorkflow, cần gitignore + loại trừ khi copy.
- **User chọn: a) "Thư mục riêng ngoài TDQWorkflow (Đề xuất)"**

## Chốt (không còn câu hỏi nào làm đổi kết quả)

- Phạm vi: global `~/.claude` (đã lọc runtime/cache/secret) + toàn bộ repo TDQWorkflow
  (copy vật lý, vì không có git remote). KHÔNG gồm Project01_LiveCaptionTranslate,
  insightfaceserverv2, plugin `superpowers` (chỉ gắn project scope với Project01, ngoài
  phạm vi).
- Secret: giữ cấu trúc `env` trong settings.json export, thay 2 giá trị Tavily key bằng
  placeholder tường minh; README hướng dẫn lấy key mới + điền vào máy đích.
- OS đích: đa nền — README cần 3 nhánh hướng dẫn cài dependency (macOS/brew,
  Linux/apt-dnf, Windows/WSL).
- Hình thức: KHÔNG có script tự động; chỉ manifest (JSON/Markdown liệt kê máy-đọc-được)
  + README chi tiết từng bước lệnh thủ công.
- Vị trí: thư mục export đặt ngoài TDQWorkflow, ví dụ `~/Documents/claude-code-export/`
  (đường dẫn chính xác chốt ở bước spec/plan, không phải quyết định cần hỏi thêm).
