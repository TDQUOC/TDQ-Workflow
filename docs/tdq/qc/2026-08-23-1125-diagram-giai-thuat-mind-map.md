# QC — báo cáo phân tích: dựng diagram giải thuật trước khi code

Ngày: 2026-08-23 · Plan: ../plan/2026-08-23-1125-diagram-giai-thuat-mind-map.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ký hiệu file: `B` = `docs/tdq/knowledge/2026-08-23-diagram-truoc-khi-code.md`,
`J` = `docs/tdq/mind-map/vi-du-login.json`, `H` = `docs/tdq/mind-map/vi-du-login.html`.

| Mã | Hạng mục | Bằng chứng | Kết quả |
|---|---|---|---|
| Q1 | sáu mục đánh số | `grep -c '^## [1-6]\.' B` → 6 | PASS |
| Q2 | mỗi kết luận có nguồn | quét từng đoạn chứa `**Kết luận:**` → 0 đoạn thiếu `http`/`suy luận` | PASS |
| Q3 | ít nhất ba điểm yếu | `grep -c '^### Điểm yếu' B` → 3 | PASS |
| Q4 | bảng đối chiếu ≥ 4 công cụ | đếm dòng dữ liệu mục đối chiếu → 5 | PASS |
| Q5 | ví dụ đủ bốn lớp | `grep -c '^### Lớp' B` → 4 | PASS |
| Q6 | mục 6 có phương án bị loại | `grep -c '^### Phương án bị loại' B` → 1, có nêu phase `diagram` bị loại | PASS |
| Q7 | không bắt buộc cài ngoài | `grep -Ec 'npm install\|pip install' B` → 0, không CDN | PASS |
| Q8 | JSON đọc được | `python3 -c "import json;json.load(open(J))"` exit 0 | PASS |
| Q9 | khoá JSON có trong lược đồ | quét 16 khoá đối chiếu mục `## Lược đồ dữ liệu` → 0 thiếu | PASS |
| Q10 | HTML không tham chiếu ngoài | `grep -c 'https\?://' H` → 0 | PASS |
| Q11 | HTML khai bản viết tay | `head -40 H \| grep -ci 'viết tay'` → 1 | PASS |
| Q12 | doc_lint sạch | `doc_lint.py` trên báo cáo + spec + plan → 0 vi phạm, exit 0 | PASS |
| Q13 | báo cáo ≤ 250 dòng | `wc -l < B` → 246 | PASS |

13/13 PASS, không hạng mục nào FAIL, không cần vòng sửa.

## Ghi chú trung thực

Phép kiểm phụ của T3.2 ghi "mở file bằng trình duyệt khi đã ngắt mạng". Tab Chrome trong
phiên này không mở được đường dẫn `file://`, nên phần đó kiểm bằng cách tĩnh: file phân tích
cú pháp sạch bằng `html.parser`, không có `<link>`, `<script src>`, `src=` hay `@import` nào,
và số tham chiếu ngoài bằng 0. Kết luận về mặt tự chứa là chắc chắn; phần bố cục hiển thị
thì chưa được nhìn tận mắt.
