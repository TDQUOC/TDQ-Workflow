# SPEC — Trang HTML trạng thái setup TDQ-Workflow

Ngày: 2026-09-07 · Bản: 1.0 · Brief: ../brief/2026-09-07-0905-trang-html-trang-thai-setup.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## Mục lục

- 1. Mục tiêu & phạm vi
- 1b. Lộ trình
- 2. Đầu ra cụ thể
- 2b. Ranh giới module
- 3. Cách tiếp cận & lý do
- 3b. Năng lực & công cụ
- 4. Yêu cầu bắt buộc
- 5. Ràng buộc & rủi ro
- 6. QC & Definition of Done
- 7. Câu hỏi còn mở

## 1. Mục tiêu & phạm vi

- Mục tiêu: một lệnh sinh ra `setup_status.html` — mở bằng trình duyệt là thấy TDQ-Workflow
  đang được cài thế nào và Claude Code THỰC SỰ nhận được gì, tách bạch hai cột **khai báo**
  và **thực nhận** cho từng hạng mục có thể dò sống được.
- Trong phạm vi:
  - Khối workflow: skill trên đĩa (3 nguồn), hook đang cắm và thời gian chạy đo được, state
    hiện tại của request.
  - Khối dependency: graphify, lumen, agent-lsp, ollama — có/không, phiên bản, đường dẫn binary.
  - Khối chi tiết: lumen dùng model gì và qua endpoint nào; agent-lsp khai báo bao nhiêu
    language server và bao nhiêu cái khởi động được thật.
  - Khối MCP: server Claude Code đang nhận, kèm trạng thái kết nối, URL/lệnh đã che bí mật.
- NGOÀI phạm vi:
  - Không sửa cấu hình nào của máy (`~/.claude.json`, `~/.config/lumen/config.yaml`, settings).
  - Không tự cài, không tự pull model, không khởi động daemon.
  - Không móc vào `tdq_finish.py` hay hook (H4 chốt chạy tay).
  - Không liệt kê skill built-in của Claude Code — script không đọc được (H3 chốt ghi rõ giới hạn).
  - Không lưu lịch sử/so sánh giữa các lần chạy; mỗi lần sinh là một ảnh chụp hiện tại.

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | ẩn số đều là công cụ cài sẵn, đã kiểm bằng chạy thật thay vì tra tài liệu |
| Vòng scope | BỎ | request tự khoanh đúng 3 nhóm nội dung; 4 câu H1–H4 đã khép mơ hồ |
| Interview | CÓ | 1 vòng, 4 câu, người dùng chốt hết |
| Spec → Plan | CÓ | hai turn tách nhau theo luật |
| QC độc lập (agent `tdq-qc-tester`) | CÓ | giá trị của trang là nói thật; cần một tác nhân khác kiểm lại cột "thực nhận" |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Bộ thu số liệu, mỗi nguồn một hàm trả dữ liệu thuần | `scripts/setup_status.py` | mỗi hàm thu có unit test chạy trên fixture, không phụ thuộc máy đang chạy |
| 2 | Bộ kết xuất HTML tự chứa | `scripts/setup_status_render.py` | nhận dict cố định, trả chuỗi HTML; không tham chiếu tài nguyên ngoài |
| 3 | Trang trạng thái sinh ra | `setup_status.html` (gốc repo) | mở offline hiển thị đủ 4 khối, không phát request mạng nào |
| 4 | Che bí mật trước khi ghi file | `scripts/setup_status.py` | không chuỗi khoá nào lọt vào HTML, kể cả khi nguồn có khoá |
| 5 | Loại file sinh ra khỏi git | `.gitignore` | `git status --porcelain` không thấy `setup_status.html` sau khi sinh |
| 6 | Log service | cả 2 script | mặc định bật, có timestamp; tắt được bằng biến môi trường |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| Thu số liệu | `scripts/setup_status.py`, `.gitignore` | không | 1, 3, 4, 5, 6 |
| Kết xuất | `scripts/setup_status_render.py` | Thu số liệu (chỉ nhận dict, không gọi ngược) | 2, 6 |

Ranh giới lấy theo quan hệ gọi thật, không theo tên thư mục: module Kết xuất chỉ nhận một dict
và trả chuỗi, nên nó không import ngược module thu số liệu; nhờ vậy phần kiểm thử của Kết xuất
chạy được trên máy trắng, không cần agent-lsp/lumen/ollama. Mỗi module có vùng kiểm thử riêng,
không dùng chung file; plan sẽ đặt tên cụ thể.

## 3. Cách tiếp cận & lý do

- Chọn: **hai lớp tách rời — thu số liệu (chạm máy) và kết xuất (thuần hàm)** — CLI
  `python3 scripts/setup_status.py` gọi lớp thu rồi đưa dict sang lớp kết xuất, ghi ra một file
  HTML tự chứa (CSS nội tuyến, không JS ngoài, không font ngoài).
- Vì:
  - Lớp thu buộc phải chạm máy thật (`claude mcp list`, `agent-lsp doctor`, `ollama`,
    `git`), nên nó không thể test tất định; tách ra thì lớp kết xuất — phần dễ sai về hiển
    thị — lại test được tất định bằng fixture.
  - Đo được: 14/14 language server khởi động thật hết trong **6,0 giây**, nên dò sống là
    lựa chọn rẻ, không cần chế độ "nhanh/chậm".
  - Cột "thực nhận" chỉ trung thực khi CHẠY: request `2026-09-06-1326-them-language-server`
    đã đo được ca csharp-ls khai đủ 14 nhưng chết ngay lần hỏi đầu.
- Đã loại:
  - HTML tĩnh viết tay — số liệu chết cứng, sai ngay lần đổi model lumen (H2 loại).
  - Chỉ đọc config, không dò sống — đúng cái bẫy đã cắn hôm qua (H1 loại).
  - Sinh trang cuối mỗi turn qua `tdq_finish.py` — mỗi turn cõng thêm thời gian dò (H4 loại).

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | skill khung đang chạy request này |
| tdq-conventions | plugin:tdq-workflow | NỀN | luật chung, nạp sẵn mọi phase |
| tdq-spec | plugin:tdq-workflow | NỀN | skill khung của phase spec, không phải công cụ của việc |
| tdq-plan | plugin:tdq-workflow | NỀN | skill khung của phase plan, không phải công cụ của việc |
| tdq-build | plugin:tdq-workflow | DÙNG | chạy plan đã duyệt, đầu ra 1–6 |
| tdq-lsp-setup | plugin:tdq-workflow | DÙNG | trang lấy lại thang 7 bậc của nó làm nguồn số liệu |
| tdq-status | plugin:tdq-workflow | DÙNG | đối chiếu khối state của trang với state thật |
| Đã xét 3 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: mỗi bước thu số liệu ghi một dòng có timestamp ra stderr (nguồn
  nào, mất bao lâu, ok hay lỗi), tắt được bằng `TDQ_LOG=0` đúng như các script hiện có.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật: nguồn nào không
  đọc được thì trang ghi rõ "không đọc được" kèm lý do, cấm điền giá trị đoán.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md` và rule
  ngôn ngữ trong `skills/tdq-build/references/rules/`.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`):

- "File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/`" — việc này chạm ở
  `scripts/setup_status.py` và `scripts/setup_status_render.py`.
- "`scripts/` **không** được import `hooks/`" — lớp thu đọc CẤU HÌNH hook (file JSON), tuyệt
  đối không import module trong `hooks/`.
- "Chỉ `scripts/tdq_state.py` được ghi `docs/tdq/state.json`" — trang chỉ ĐỌC state qua CLI.
- "docstring/chú thích/chuỗi máy in trong `scripts/` viết TIẾNG ANH; tài liệu cho user theo
  `doc_lang`" — việc này chạm ở phần chữ hiển thị trong HTML (tiếng Việt) so với log và
  docstring của 2 script (tiếng Anh).

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| `claude mcp list` in nguyên khoá Tavily trong URL | rò khoá thật vào file HTML, mà repo là public | che mọi giá trị đứng sau `key=`/`apikey=`/`token=` trong URL trước khi dựng dict; có test riêng dựng chuỗi chứa khoá giả và khẳng định nó không còn trong HTML |
| `setup_status.html` chứa đường dẫn máy, IP tailnet, danh sách MCP | công bố cấu hình máy lên repo public | thêm vào `.gitignore` ngay trong cùng task sinh file; QC kiểm `git status` sạch sau khi sinh |
| Định dạng output của `claude mcp list` / `agent-lsp doctor` đổi theo phiên bản | parser vỡ, trang hiện sai hoặc rỗng | parser bám mẫu tối thiểu (tên + trạng thái), lỗi thì ghi "không phân tích được" kèm nguyên văn dòng đầu; test có fixture cho cả ca định dạng lạ |
| `omnisharp` cần `DOTNET_ROOT`, có trong khối `env` của MCP | doctor báo csharp failed dù thật ra chạy được | lớp thu truyền nguyên khối `env` của server `lsp` trong `~/.claude.json` vào tiến trình doctor |
| Dò sống khởi động 14 tiến trình language server | chiếm CPU/RAM trong vài giây | doctor tự thoát sau mỗi lần kiểm (đo: 6,0 giây cho 14 server); không giữ tiến trình nào sống sau khi sinh trang |
| Máy chưa cài một dependency (ví dụ chưa có graphify) | script chết giữa chừng, không ra trang | mọi lệnh ngoài chạy qua một hàm bọc: thiếu binary → ô "chưa cài" kèm lệnh cài gợi ý, không ném exception |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Trang tự chứa | HTML sinh ra không tham chiếu tài nguyên ngoài nào (không `http://`/`https://` trong `src`/`href` của thẻ tải tài nguyên); mở khi rút mạng vẫn hiển thị đủ |
| Q2 | Không rò bí mật | dựng nguồn giả có chứa khoá dạng `tvly-dev-…`, sinh trang, trong HTML không còn chuỗi khoá đó; phần đứng sau `key=` bị thay bằng dấu che |
| Q3 | Khai báo ≠ thực nhận | giả lập một language server chết: trang hiện đúng "khai N, sống N−1" và chỉ tên server chết, không gộp thành một con số |
| Q4 | Bốn khối đủ | trang có đủ khối workflow (skill + hook + state), dependency (4 công cụ kèm phiên bản), chi tiết (model lumen + endpoint, bảng language server), MCP (tên + trạng thái kết nối) |
| Q5 | Trung thực khi thiếu | tắt/giấu một nguồn bất kỳ → ô tương ứng ghi "không đọc được" kèm lý do, script vẫn sinh trang và thoát 0 |
| Q6 | Giới hạn skill built-in | trang có đúng một dòng nói rõ phần skill built-in của Claude Code không đọc được từ script |
| Q7 | Log service | mặc định stderr có dòng timestamp cho từng nguồn; đặt `TDQ_LOG=0` thì im hoàn toàn, nội dung HTML không đổi |
| Q8 | Không bẩn git | sau khi sinh trang, `setup_status.html` không xuất hiện trong danh sách file bẩn của git |
| Q9 | Test tất định | test của lớp kết xuất chạy được mà không cần agent-lsp/lumen/ollama/graphify trên máy |
| Q10 | Không hồi quy | toàn bộ suite không thêm ca đỏ nào so với nền trước khi làm |
| Q11 | QC độc lập | agent `tdq-qc-tester` chấm lại Q1–Q10 và kết luận PASS kèm bằng chứng |

DoD: đủ 6 đầu ra ở §2; Q1–Q11 PASS; plan tick `[x]` hết; working log của ngày có mục của
request này; không có ca đỏ mới trong suite.

## 7. Câu hỏi còn mở

(rỗng)
