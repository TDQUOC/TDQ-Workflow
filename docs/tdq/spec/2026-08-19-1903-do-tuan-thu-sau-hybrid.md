# SPEC — Đo hành vi tuân thủ luật sau khi chuyển thể lai

Ngày: 2026-08-19 · Bản: 1.0 · Brief: ../brief/2026-08-19-1903-do-tuan-thu-sau-hybrid.md · Lane: full
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

- Mục tiêu: trả lời bằng số câu hỏi "bản skill thể lai có làm model tuân thủ luật kém hơn
  bản tiếng Việt không", bằng cách chạy cùng một bộ ca trên hai nhánh `ea0cdbd` (Việt) và
  `f620094` (lai), chấm tất định trên dấu vết để lại, rồi so bằng kiểm định ghép cặp.
- Trong phạm vi:
  - Bộ chạy tự viết trên `claude -p --plugin-dir`, vì `claude plugin eval` đang khoá early access.
  - 10 ca kiểm, mỗi ca là một prompt tiếng Việt thật, chấm nhiều mã luật cùng lúc.
  - Nhóm luật hành vi cốt lõi: một-turn, cổng duyệt, ghi state, nhịp tick, red-green.
  - Chạy 10 ca × 3 lần × 2 nhánh = 60 phiên, trên Opus 5.
  - Bảng số và kết luận theo ngưỡng ĐỊNH TRƯỚC khi chạy.
  - Bộ ca giữ lâu dài trong repo, chạy lại được bằng một lệnh.
- NGOÀI phạm vi:
  - Không mặt chất lượng nào bị loại — user chọn cả bốn mặt (độ tin, phạm vi luật, chạy lại
    được, chi phí).
  - 38 mã `user-facing`: KHÔNG đo, vì chúng vẫn nguyên tiếng Việt nên không có gì đổi để đo.
  - Luật không để lại dấu vết máy đọc được: loại, vì user chốt chỉ chấm tất định.
  - Sửa luật hay lùi bản: KHÔNG làm trong request này. Có mã sụt thì mở request riêng.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | ba hướng tra đã xong ở analyze, không còn ẩn số ngoài repo |
| Interview | BỎ | đã chạy ba vòng, phạm vi chốt hết |
| Spec + plan | CÓ | khung bất biến |
| Implement | CÓ | khung bất biến |
| QC độc lập (agent) | BỎ | phiên này không gọi subagent trừ khi user yêu cầu; QC chạy trong mode chính |
| Chia việc cho nhiều subagent | BỎ | như trên |
| Vòng chạy thật 60 phiên | CÓ | là đầu ra chính, không bỏ được |
| Report | CÓ | khung bất biến |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Bộ chạy và chấm | `scripts/tdq_eval.py` | chạy được ba lệnh con: dựng nhánh, chạy ca, chấm và in bảng; log có timestamp, tắt được qua biến môi trường |
| 2 | Bộ 10 ca kiểm | `evals/tuan-thu/<ma-ca>/` | mỗi ca có prompt tiếng Việt và bảng khai mã `L###` cùng phép kiểm dấu vết; tổng phép kiểm ghép cặp ≥ 30 |
| 3 | Lưới test cho bộ chấm | thư mục test của repo, kèm transcript mẫu | mỗi phép kiểm có ít nhất một mẫu ĐẠT và một mẫu VI PHẠM, chạy không tốn tiền |
| 4 | Bảng số và kết luận | `docs/tdq/audit/do-tuan-thu.md` | có tỉ lệ tuân thủ từng mã ở hai nhánh, số cặp lệch, giá trị p, và kết luận theo ngưỡng định trước |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| chay | `scripts/tdq_eval.py` | không | 1 |
| ca-kiem | `evals/tuan-thu/` | không | 2 |
| luoi-test | thư mục test của repo (file test của bộ chấm + transcript mẫu) | chay, ca-kiem | 3 |
| bao-so | `docs/tdq/audit/do-tuan-thu.md` | chay, ca-kiem, luoi-test | 4 |

## 3. Cách tiếp cận & lý do

- Chọn: tự dựng bộ chạy mỏng trên `claude -p --plugin-dir <worktree>`, mỗi phiên chạy trong
  một thư mục tạm có git riêng, xuất `stream-json` rồi chấm bằng phép kiểm tất định trong Python.
- Vì: `claude plugin eval` trả `` `plugin eval` is currently in early access `` trên tài khoản
  này (đã kiểm, không phải lỗi cấu hình local). `--plugin-dir` cho phép nạp plugin từ một
  worktree bất kỳ, nên vẫn đo được hành vi thật của agent thật ở đúng hai commit cần so.
- Vì: chấm tất định không phụ thuộc giám khảo. Research §2 cho thấy giám khảo LLM tự mâu
  thuẫn khoảng một phần tư số ca khó, nên mọi mã luật không để lại dấu vết đều bị loại khỏi
  bộ đo thay vì đem chấm bằng cảm nhận.
- **Thiết kế thống kê, chốt TRƯỚC khi chạy:**
  - Một "phép kiểm" là một cặp (ca, mã luật). Mỗi phép kiểm chạy 3 lần ở mỗi nhánh.
  - Ghép cặp theo phép kiểm: hai nhánh gặp đúng cùng một prompt, nên nhiễu do ca khó hay dễ
    bị trừ đi. Research §3 nói thẳng thiết kế ghép cặp cần ít mẫu hơn hai nhánh độc lập.
  - Kết luận SỤT khi kiểm định dấu một phía trên các cặp lệch cho p < 0,05 — với toàn bộ cặp
    lệch nghiêng xấu thì cần ít nhất 5 cặp.
  - Báo riêng "sụt cứng": mã nào tuân thủ 3/3 lần ở nhánh Việt mà 0/3 ở nhánh lai thì nêu ra
    kể cả khi tổng thể chưa đủ p, vì đó là tín hiệu phải soi tay.
  - Độ nhạy tối thiểu phải ghi thẳng vào báo cáo: với cỡ 30-40 phép kiểm ghép cặp, phép đo
    này chỉ phát hiện được sụt lớn. Chênh lệch vài điểm phần trăm nằm trong nhiễu và báo cáo
    KHÔNG được kết luận gì về nó.
- Đã loại: `claude plugin eval` — vì đang khoá early access, không tự bật được.
- Đã loại: chấm ngoại tuyến trên transcript session cũ — vì không có nhánh đối chứng.
- Đã loại: giám khảo LLM cho luật khó — vì user chốt chỉ chấm tất định.

## 3b. Năng lực & công cụ

Chép từ brief mục `### Năng lực dùng được`. Phân vân → DÙNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake, tdq-spec, tdq-plan, tdq-build, tdq-conventions, tdq-status | plugin:tdq-workflow | NỀN | chính workflow đang chạy, và cũng là đối tượng được đem đi đo |
| test-driven-development | plugin:superpowers | DÙNG | đầu ra 3: mỗi phép kiểm viết mẫu VI PHẠM cho đỏ trước, rồi mới nối vào bộ chạy thật |
| verification-before-completion | plugin:superpowers | DÙNG | đầu ra 4: cấm tuyên bố "không sụt" khi chưa có bảng số của cả hai nhánh |
| Đã xét 277 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: timestamp, đủ chi tiết debug, tắt được qua biến môi trường.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mọi hằng số và số liệu phải đến từ lần chạy thật. Thiếu dữ kiện thì bộ chạy LỖI, cấm đặt
  số mặc định — theo đúng luật đã có của `scripts/tdq_bench.py`.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md` và rule
  ngôn ngữ trong `skills/tdq-build/references/rules/`.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`):

- "File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/`" — việc này chạm ở
  `scripts/tdq_eval.py`. Thư mục `evals/` chỉ chứa dữ liệu ca kiểm, không chứa mã chạy được.
- "`scripts/` không được import `hooks/`" — việc này chạm ở `scripts/tdq_eval.py`.
- "Chỉ `scripts/tdq_state.py` được ghi `docs/tdq/state.json`" — việc này chạm ở chỗ mỗi phiên
  đo chạy trong thư mục tạm có state riêng, tuyệt đối không ghi vào state thật của repo.
- "Thư mục test gọi được vào mọi tầng" — việc này chạm ở lưới test của bộ chấm.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Nhiễu ngẫu nhiên giữa các lần chạy | kết luận sai chiều | ghép cặp, 3 lần mỗi nhánh, ngưỡng định trước, ghi rõ độ nhạy tối thiểu |
| Tốn tiền vượt dự tính | phải dừng giữa chừng | trần số phiên và trần số lượt mỗi phiên; ghi chi phí sau mỗi ca; vượt trần thì dừng và báo |
| Phiên đo đụng vào repo thật | hỏng state hoặc lịch sử git thật | mỗi phiên một thư mục tạm có git riêng; bộ chạy từ chối chạy nếu thư mục làm việc là repo này |
| Bộ chấm sai mà không ai biết | số đẹp nhưng vô nghĩa | mỗi phép kiểm có mẫu ĐẠT và mẫu VI PHẠM, viết đỏ trước |
| Hai nhánh còn khác nhau ở chỗ khác ngoài ngôn ngữ | quy sai nguyên nhân | liệt kê trong báo cáo mọi thay đổi phụ giữa hai commit và nói rõ chúng không chạm luật hành vi |
| Phiên đo hỏng vì hạ tầng | mất cân bằng hai nhánh | phiên hỏng phải chạy lại; số lần chạy lại ghi vào báo cáo |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Bộ chấm đúng | mỗi phép kiểm có ít nhất một mẫu ĐẠT và một mẫu VI PHẠM, và bộ chấm ra đúng kết quả trên cả hai |
| Q2 | Không đụng repo thật | sau khi chạy đủ 60 phiên, cây làm việc của repo này không có file nào đổi ngoài các đầu ra §2 |
| Q3 | Chạy đủ | 60 phiên đều có kết quả; phiên hỏng đã chạy lại và số lần chạy lại được ghi |
| Q4 | Đủ độ phủ | 10 ca, mỗi ca chấm ít nhất 3 mã `L###`, tổng ít nhất 30 phép kiểm ghép cặp |
| Q5 | Bảng số đầy đủ | báo cáo có tỉ lệ tuân thủ từng mã ở hai nhánh, số cặp lệch mỗi chiều, và giá trị p |
| Q6 | Kết luận đúng luật | kết luận bám đúng ngưỡng đã ghi ở §3, và báo cáo nói rõ độ nhạy tối thiểu |
| Q7 | Log service | log có timestamp, bật mặc định, tắt được qua biến môi trường |
| Q8 | Chi phí | chi phí thật được ghi lại và không vượt trần đã đặt |
| Q9 | Chạy lại được | có một lệnh chạy lại toàn bộ phép đo, kèm tài liệu ngắn ngay trong bộ ca |

DoD: cả 9 hạng mục PASS, `docs/tdq/audit/do-tuan-thu.md` có số thật của cả hai nhánh, và
kết luận nêu rõ mã nào sụt, mã nào không, kèm giới hạn của phép đo.

## 7. Câu hỏi còn mở

(rỗng)
