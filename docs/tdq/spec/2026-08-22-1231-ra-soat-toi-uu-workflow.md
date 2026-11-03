# SPEC — Rà soát toàn bộ workflow sau đợt chuyển tiếng Anh, ra danh sách đề xuất tối ưu

Ngày: 2026-08-22 · Bản: 1.0 · Brief: ../brief/2026-08-22-1231-ra-soat-toi-uu-workflow.md · Lane: full
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

- Mục tiêu: đo lại toàn bộ bề mặt tài liệu của workflow sau đợt chuyển sang tiếng Anh, rồi
  giao một hồ sơ audit chứa đúng 10 đề xuất tối ưu đã xếp hạng. Mỗi đề xuất kèm ba con số:
  token tiết kiệm ước tính, luật gốc bị chạm, phép kiểm bắt được nếu behavior vỡ.
- Trong phạm vi — bốn mặt user chọn:
  - Context cost: đo token từng file theo tầng nạp, chỉ ra chỗ cắt được.
  - Trùng lặp và luật chồng luật: tìm đoạn văn lặp giữa các file tài liệu.
  - Runtime: đếm số step một request tiêu, chỉ ra bước thừa.
  - Chất lượng bản dịch: liệt kê câu tối nghĩa hoặc thuật ngữ lệch sinh ra ở đợt dịch.
- Trong phạm vi — vùng file quét: `skills/**`, `agents/*.md`, `docs/claude-md-mau.md`.
- NGOÀI phạm vi:
  - SỬA bất kỳ file skill, rule hay reference nào. Request này chỉ đo và đề xuất.
  - Đề xuất bỏ hoặc nới một luật. Đề xuất chỉ được đụng CÁCH VIẾT, không đụng nội dung luật.
  - Chuỗi in ra của `hooks/**` và `scripts/**` — user chọn 5A, loại vùng này.
  - `CLAUDE.md` global của user — nằm ngoài repo, sửa là đụng mọi project khác.
  - Chạy lại bộ `evals/tuan-thu` để đo behavior thật — user chọn hướng "chỉ rà soát".

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ (đã chạy) | cần đối chiếu hướng dẫn viết skill của Anthropic |
| Interview | CÓ (đã chạy) | yêu cầu ban đầu mơ hồ ở cả phạm vi lẫn định nghĩa "optimize" |
| Vòng scope | CÓ (đã chạy) | request bao cả hệ thống, dùng chữ mở không kèm số |
| Spec → plan → implement → report | CÓ | khung bất biến, không cắt |
| QC độc lập (agent) | CÓ | đầu ra là con số; cần một agent đo lại độc lập để bắt số sai |
| Deep review (tdq-reviewer) | BỎ | phạm vi đã chốt bằng 8 câu hỏi, không còn chỗ mơ hồ |
| Chia sub-agent chạy song song | BỎ | quyết ở cổng mode sau khi duyệt plan |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Công cụ dò đoạn văn trùng giữa các file tài liệu | `scripts/doc_dup.py` | chạy được, in bảng cặp file trùng kèm số dòng và số token của đoạn trùng |
| 2 | Hồ sơ audit bốn mặt | `docs/tdq/audit/2026-08-22-toi-uu-workflow.md` | có đủ bốn mục A/B/C/D, mỗi mục mở đầu bằng bảng số có nguồn là một lệnh chạy được |
| 3 | Bảng top 10 đề xuất | mục `## Top 10 đề xuất` của đầu ra #2 | đúng 10 dòng, mỗi dòng đủ 5 cột: đề xuất, token tiết kiệm, luật bị chạm, phép kiểm, hạng rủi ro |
| 4 | Bảng số nền trước khi sửa | mục `## Mốc nền` của đầu ra #2 | chép nguyên output của hai lệnh đo token, ghi rõ ngày đo |
| 5 | Report cuối request | `docs/tdq/reports/2026-08-22-1231-ra-soat-toi-uu-workflow.md` | 10–20 dòng, có bảng timing |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| do-trung-lap | `scripts/doc_dup.py` | không | 1 |
| ho-so-audit | `docs/tdq/audit/2026-08-22-toi-uu-workflow.md` | do-trung-lap | 2, 3, 4 |
| ket-so | `docs/tdq/reports/2026-08-22-1231-ra-soat-toi-uu-workflow.md` | ho-so-audit | 5 |

## 3. Cách tiếp cận & lý do

- Chọn: viết một công cụ dò trùng lặp trước, rồi mới viết hồ sơ audit dựa trên số nó in ra.
- Vì: mặt B (trùng lặp) trải trên 44 file tài liệu. Đọc bằng mắt thì con số không lặp lại
  được, mà §6 lại đòi mỗi đề xuất có token tiết kiệm đo được. Research cũng chỉ ra rủi ro
  lớn nhất của repo này là nội dung trùng giữa các file, không phải tổng token: mức 10.785
  token loaded-on-skill-call còn xa ngưỡng nguy hiểm khoảng 32.000 token.
- Vì (2): ba mặt còn lại đã có công cụ đo sẵn trong repo — `context_surface.py` và
  `skill_tokens.py` cho mặt A, `step_audit.py` cho mặt C, `i18n_check.py` cho mặt D. Chỉ
  mặt B là thiếu công cụ, nên đây là dòng code duy nhất phải viết mới.
- Đã loại: dò trùng lặp bằng một chuỗi lệnh grep viết tay — vì không lặp lại được ở lần đo
  sau, và không đếm được token của đoạn trùng.
- Đã loại: dùng thư viện dò đạo văn ngoài — vì phải cài gói mới cho một việc chạy vài lần.
- Nguồn: `docs/tdq/research/2026-08-22-1231-ra-soat-toi-uu-workflow.md`.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-spec | plugin:tdq-workflow | NỀN | skill khung viết spec này |
| tdq-plan | plugin:tdq-workflow | NỀN | skill khung viết plan |
| tdq-build | plugin:tdq-workflow | NỀN | skill khung implement, QC, report |
| tdq-conventions | plugin:tdq-workflow | NỀN | quy ước chung, nạp đầu mọi skill |
| Đã xét 281 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định cho đầu ra #1: có timestamp ISO, in ra stderr, tắt được bằng cờ
  dòng lệnh hoặc biến môi trường, bảng kết quả luôn ra stdout để pipe được. Bám đúng khuôn
  của `context_surface.py` và `token_audit.py`.
- Đếm token bằng bộ đếm thật trong `.venv-tokens/`, giống `skill_tokens.py`. Thiếu thư viện
  thì báo lỗi và dừng, CẤM lùi về ước lượng ký-tự-chia-bốn.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi con số trong hồ sơ audit phải ghi kèm lệnh sinh ra nó. Số không có lệnh là số bịa.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code viết ra bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md`,
  và bám rule ngôn ngữ trong `skills/tdq-build/references/rules/`.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`):

- "File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/`" — việc này chạm ở `scripts/doc_dup.py`.
- "`skills/` chỉ được nhắc tên lệnh của `scripts/`, cấm chép nội dung script vào skill" —
  việc này chạm ở chỗ hồ sơ audit trích dẫn tên lệnh đo.
- "2026-08-14: `soul.md` là luật gốc đứng trên mọi luật; đổi soul phải có user duyệt" —
  việc này chạm ở chỗ đề xuất nào động tới `soul.md` thì phải đánh dấu riêng.
- "2026-08-22: ngôn ngữ chia 3 tầng" — việc này chạm ở `scripts/doc_dup.py`: chú thích,
  docstring và chuỗi máy in ra đều viết tiếng Anh.

Node `Changelog`, `main()`, `cli()`, `log()`, `cmd_build()` nằm trong mục `## Hub` của
`docs/kien-truc.md`. Đầu ra #1 tạo hàm `main()` và `log()` mới nên phải có dòng DoD kiểm
hồi quy riêng cho hai node đó.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Công cụ dò trùng báo nhầm khuôn mẫu chung là trùng lặp | top 10 đề xuất chứa đề xuất vô nghĩa | đặt ngưỡng độ dài đoạn tối thiểu, và người viết audit phải loại tay từng cặp sai |
| Số token đo ở hai công cụ khác nhau không so được với nhau | cộng dồn ra tổng sai | mọi con số token trong hồ sơ dùng đúng một bộ đếm trong `.venv-tokens/` |
| Đề xuất đụng vào nội dung luật chứ không chỉ cách viết | behavior đổi mà không ai biết | mỗi dòng top 10 bắt buộc có cột luật gốc bị chạm; cột trống là dòng bị loại |
| Đo số step trên transcript của chính phiên này | số bị thổi lên vì phiên này toàn việc đo | đo trên các phiên request đã đóng, ghi rõ phiên nào được lấy |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Công cụ dò trùng chạy được | chạy trên vùng file đã khai, thoát 0, in ra bảng có ít nhất một cặp |
| Q2 | Log service của công cụ | mặc định in log có timestamp ra stderr; tắt được; bảng vẫn ra stdout |
| Q3 | Bộ đếm token | thiếu thư viện đếm thì công cụ thoát mã lỗi riêng, không tự ước lượng |
| Q4 | Unit test của công cụ | chạy một lệnh, toàn bộ xanh |
| Q5 | Hồ sơ audit đủ bốn mặt | có đủ bốn mục A, B, C, D; mục nào cũng mở đầu bằng bảng số |
| Q6 | Mọi con số có nguồn | mỗi bảng số ghi kèm lệnh sinh ra nó, chạy lại lệnh đó ra đúng số ấy |
| Q7 | Top 10 đúng khuôn | đúng 10 dòng, không dòng nào để trống cột luật bị chạm hay cột phép kiểm |
| Q8 | Không đề xuất nào đổi luật | đọc từng dòng: mọi đề xuất chỉ đụng cách viết, chỗ đặt hoặc chỗ trùng |
| Q9 | Không sửa file workflow nào | cây làm việc không có thay đổi nào trong `skills/`, `agents/`, `hooks/` |
| Q10 | Luật ngôn ngữ ba tầng | phép kiểm i18n chạy trên file mới ra 0 dòng vi phạm |
| Q11 | Luật tài liệu | phép kiểm doc_lint chạy trên spec, plan, audit, report ra 0 vi phạm |
| Q12 | Hồi quy node Hub | bộ test hiện có vẫn giữ đúng số đỏ của mốc nền, không thêm đỏ mới |

DoD:
- Q1 đến Q12 đều PASS, mỗi hạng mục có một dòng bằng chứng trong file qc.
- Đủ 5 đầu ra ở §2, mỗi đầu ra tồn tại đúng đường dẫn đã khai.
- Bảng top 10 có đúng 10 dòng, tổng token tiết kiệm ước tính được cộng lại và ghi thành một số.
- Mốc nền token được chép nguyên vào hồ sơ, kèm ngày đo.
- Không một file nào trong `skills/`, `agents/`, `hooks/` bị sửa.
- Report 10–20 dòng, có bảng timing.

## 7. Câu hỏi còn mở

(rỗng)
