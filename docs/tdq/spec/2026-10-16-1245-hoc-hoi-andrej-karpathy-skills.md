# SPEC — Phân tích học hỏi từ andrej-karpathy-skills để cải tiến TDQ Workflow

Ngày: 2026-10-16 · Bản: 1.0 · Brief: ../brief/2026-10-16-1245-hoc-hoi-andrej-karpathy-skills.md · Lane: full
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

- **Mục tiêu**: Phân tích toàn diện kho tri thức và triết lý của `andrej-karpathy-skills` (`C:\Users\admin\Documents\andrej-karpathy-skills`), đối chiếu với nền tảng kiến trúc và các quy tắc của TDQ Workflow hiện tại; xuất bản một Báo cáo HTML Report chuyên sâu, độc lập (Standalone Single-File Dashboard) tại `docs/tdq/reports/2026-10-16-1245-hoc-hoi-andrej-karpathy-skills.html` với đầy đủ số liệu định lượng, biểu đồ so sánh trực quan, bằng chứng thực tế và 5 đề xuất nâng cấp khả thi; chưa can thiệp sửa code hệ thống ở lượt này.
- **Trong phạm vi**:
  1. *Khảo sát & Đối chiếu chuyên sâu*:
     - Phân tích 4 trụ cột của Karpathy (Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution) và bộ ví dụ đối chứng tại `EXAMPLES.md`.
     - Đối chiếu 1-1 với các luật tương ứng của TDQ Workflow (`soul.md`, `chung.md`, `clean-code.md`, `team-mode.md`, bộ mã cấm `ANTI-1`..`ANTI-6`, các hooks).
     - Phân tích Token Economics, Carry Cost và hiện tượng ma sát nhận thức (Cognitive Friction / LLM Fatigue).
     - Đề xuất mô hình kiến trúc lai: "Tâm thức Karpathy trong Bộ giáp TDQ" (Hybrid Architecture).
  2. *Thiết kế & Xuất bản HTML Report chuyên nghiệp*:
     - File HTML độc lập, tự chứa 100% (không phụ thuộc internet/CDN, nhúng toàn bộ CSS, inline SVG và Vanilla JS).
     - Hỗ trợ giao diện kép Dark / Light theme toggle.
     - Cấu trúc 6 Section lớn: Header KPI Summary Cards, Section 1 (Executive Comparison Matrix & Radar SVG), Section 2 (Token Economics & Waterfall SVG), Section 3 (LLM Psychology & 4 Pillars vs TDQ Guards có mẫu code WRONG/RIGHT), Section 4 (Cognitive Friction Heatmap), Section 5 (The Hybrid Architecture Proposal), Section 6 (Actionable Implementation Roadmap 3 giai đoạn).
  3. *Kiểm định chất lượng mức `ultra`*:
     - Đầy đủ tiêu chí Definition of Done, kiểm tra tính toàn vẹn cấu trúc DOM, hiển thị không lỗi cú pháp, và chạy thẩm định độc lập qua agent kiểm thử.
- **NGOÀI phạm vi**:
  - Tuyệt đối chưa sửa đổi mã nguồn hoặc rule của TDQ Workflow trong request này.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | Hai subagent đã khảo sát toàn diện mã nguồn nội bộ của cả 2 dự án |
| Interview | CÓ | Đã hoàn thành vòng 1 chốt các lựa chọn 1a 2a 3c |
| QC độc lập (agent) | CÓ | Áp dụng mức QC `ultra` theo yêu cầu của người dùng |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Báo cáo HTML Report chuyên sâu, độc lập phân tích học hỏi từ Karpathy Skills | `docs/tdq/reports/2026-10-16-1245-hoc-hoi-andrej-karpathy-skills.html` | File HTML độc lập (dung lượng ≥ 35 KB, ≥ 400 dòng), chứa đầy đủ 6 Section lớn, 2 biểu đồ SVG nội bộ, Dark/Light mode, đạt tiêu chuẩn W3C HTML5 không lỗi cú pháp |

## 2b. Ranh giới module

Xác định bằng ngữ nghĩa phụ thuộc qua LSP:

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| `html-report` | `docs/tdq/reports/2026-10-16-1245-hoc-hoi-andrej-karpathy-skills.html` | Không | 1 |

## 3. Cách tiếp cận & lý do

- **Chọn**:
  1. *Xây dựng Dashboard HTML Report độc lập (Standalone Single-File HTML)*: Tích hợp sẵn CSS, inline SVG và JavaScript nội bộ. Báo cáo có thể mở trực tiếp trên mọi trình duyệt mà không cần cài đặt server hay kết nối mạng.
  2. *Áp dụng cấu trúc 6 Section phân tích đa chiều*: Đi từ bức tranh toàn cảnh (KPI Cards, Radar Chart), phân tích kinh tế token (Waterfall), mổ xẻ tâm lý học và đối chứng code (4 Pillars vs Guards), chỉ ra điểm nghẽn thực tế (Friction Map) và đưa ra giải pháp kiến trúc lai cùng lộ trình thực thi 3 giai đoạn.
- **Vì**:
  - Thỏa mãn hoàn hảo yêu cầu của người dùng: Trực quan, chuyên sâu, giàu chứng cứ, và chuẩn bị sẵn nền tảng kiến trúc trước khi triển khai code ở các lượt tiếp theo.
- **Đã loại**:
  - *Viết báo cáo dạng Markdown phẳng thông thường*: Loại vì không thể hiện được biểu đồ tương tác, thiếu tính sinh động của bảng đối chiếu code và không đáp ứng đúng yêu cầu "expect html report" của người dùng.

## 3b. Năng lực & công cụ

Chép từ brief mục `### Năng lực dùng được`. Phân vân → DÙNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| Agent | built-in | DÙNG | Fan-out 2 subagent chạy ngầm phân tích và chạy kiểm thử độc lập ở QC ultra |
| tdq-intake | plugin:tdq-workflow | NỀN | mở request, phỏng vấn và chuyển phase |
| tdq-spec | plugin:tdq-workflow | NỀN | lập đặc tả kỹ thuật cho báo cáo HTML Report |
| tdq-plan | plugin:tdq-workflow | NỀN | lập kế hoạch phân tách task thiết kế HTML Report |
| tdq-build | plugin:tdq-workflow | NỀN | thực thi dựng file HTML Report và kiểm định QC |
| tdq-conventions | plugin:tdq-workflow | NỀN | quy tắc workflow, ngôn ngữ 3 tầng |
| tdq-status | plugin:tdq-workflow | NỀN | kiểm tra trạng thái tiến độ |
| tdq-lean | plugin:tdq-workflow | NỀN | kiểm tra tính tinh gọn của tài liệu |
| tdq-setup | plugin:tdq-workflow | NỀN | kiểm tra LSP và môi trường |
| tdq-check-status | plugin:tdq-workflow | NỀN | phục hồi phiên khi có sự cố |
| Đã xét 15 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- **Log service bật mặc định**: Ghi log tiến độ kèm timestamp ISO ra `stderr`, tắt qua `TDQ_LOG=0`.
- **Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật**.
- **Mỗi thành phần có tiêu chí kiểm tra riêng, chạy được bằng một lệnh**.
- **Tài liệu HTML tự chứa hoàn toàn**: Không link tới tài nguyên CDN bên ngoài (font, css, js).

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ:
- 2026-08-22: ngôn ngữ chia 3 tầng — văn bản tài liệu trao đổi trong dự án viết bằng tiếng Việt chuẩn mực, thuật ngữ kỹ thuật giữ nguyên bản tiếng Anh.
- Quy tắc an toàn: Không chỉnh sửa các file runtime code trong `hooks/` hoặc `scripts/` ở request này.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| File HTML nhúng quá nhiều CSS/JS phức tạp gây lỗi render | Báo cáo bị vỡ giao diện trên trình duyệt | Sử dụng thuần HTML5, CSS hiện đại và inline SVG; kiểm tra cú pháp và render trên nhiều chế độ |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |
|---|---|---|---|---|
| Q1 | File HTML Report được tạo tại đúng đường dẫn và tự chứa 100% | File tồn tại tại `docs/tdq/reports/2026-10-16-1245-hoc-hoi-andrej-karpathy-skills.html`, không chứa thẻ script/link trỏ ra CDN ngoài | Đo trước: 0 file html tồn tại (file chưa tạo), sau khi tạo có 1 file html độc lập | Nhúng trực tiếp toàn bộ CSS và SVG vào file |
| Q2 | Đầy đủ cấu trúc 6 Section lớn theo thiết kế | File HTML chứa đầy đủ 6 Section lớn (Executive Matrix, Token Waterfall, 4 Pillars vs Guards, Friction Heatmap, Hybrid Proposal, Actionable Roadmap) | Đo trước: 0 section hoàn thành, sau khi viết đạt 6/6 section | Bổ sung các section còn thiếu |
| Q3 | Tích hợp biểu đồ trực quan nội bộ (Radar Chart & Waterfall Chart bằng SVG) | File HTML chứa ít nhất 2 khối thẻ SVG biểu đồ hợp lệ hiển thị đối sánh 6 trục năng lực và thác nước token | Đo trước: 0 biểu đồ SVG, sau khi tạo có ≥ 2 biểu đồ SVG nội bộ | Hiệu chỉnh tọa độ SVG cho chuẩn xác |
| Q4 | Tính năng Dark/Light theme toggle và Responsive layout | Giao diện hỗ trợ chuyển đổi theme qua nút bấm và media query, hiển thị chuẩn trên màn hình di động và máy tính | Đo trước: 0 bộ chuyển theme, sau khi làm hoạt động ổn định 2 theme | Tối ưu hóa biến CSS căn bản |
| Q5 | Hợp đồng tài liệu và tiêu chuẩn ngôn ngữ | Toàn bộ tài liệu spec, plan, report đạt 0 vi phạm qua công cụ kiểm tra hợp đồng tài liệu | Đo trước: 0 vi phạm trên các file hiện tại | Chạy kiểm tra và hiệu chỉnh ngay |
| Q6 | Kiểm thử độc lập mức `ultra` | Agent kiểm định độc lập kiểm tra báo cáo và xác nhận đạt chất lượng chuyên sâu | Đo trước: 0 lượt kiểm định độc lập, sau khi hoàn thành có 1 biên bản QC đạt | Bổ sung phân tích theo góp ý của QC |

**DoD**:
1. File `docs/tdq/reports/2026-10-16-1245-hoc-hoi-andrej-karpathy-skills.html` hoàn thành đầy đủ 6 Section, trực quan, chuyên sâu, không phụ thuộc thư viện ngoài.
2. Kiểm tra render đạt 100% hiển thị tốt, có nút toggle Dark/Light theme, có biểu đồ Radar và Waterfall SVG.
3. Toàn bộ các tiêu chí kiểm tra QC mức `ultra` đạt PASS.

## 7. Câu hỏi còn mở

(Rỗng — toàn bộ câu hỏi đã được chốt qua phỏng vấn vòng 1.)
