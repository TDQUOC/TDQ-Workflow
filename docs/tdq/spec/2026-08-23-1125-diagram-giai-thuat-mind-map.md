# SPEC — báo cáo phân tích: dựng diagram giải thuật trước khi code

Ngày: 2026-08-23 · Bản: 1.0 · Brief: ../brief/2026-08-23-1125-diagram-giai-thuat-mind-map.md · Lane: full
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

- Mục tiêu: trả lời sáu câu user hỏi về ý tưởng "dựng diagram giải thuật trước khi code",
  mỗi câu một kết luận rõ ràng kèm nguồn, rồi đề xuất một phương án nên chọn. Kèm ví dụ
  chạy thật để user nhìn thấy thành phẩm trước khi quyết định có build hay không.
- Trong phạm vi:
  - Báo cáo phân tích sáu câu, có phản biện và có nêu cái giá phải trả.
  - Ví dụ đủ bốn lớp cho một luồng login mẫu.
  - Một file HTML mind-map mở được offline, và một file dữ liệu mẫu cho lược đồ.
  - Đề xuất vị trí chèn vào tdq-workflow, kèm phương án bị loại và lý do.
- NGOÀI phạm vi:
  - **Không hiện thực hoá tính năng.** User chọn dừng ở báo cáo; việc build là request sau.
  - Không viết script sinh mind-map tự động, không sửa skill nào của tdq-workflow.
  - Không có mặt nào bị loại ở vòng scope — user chọn cả bốn mặt.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | một vòng bốn góc đã đủ nguồn cho cả sáu câu; chỗ thiếu đã khai là suy luận |
| Interview | BỎ | hai vòng đã đóng, không còn câu nào đổi được kết quả |
| Spec | CÓ | tiêu chí "báo cáo thế nào là đạt" phải được user duyệt trước |
| Plan | CÓ | giữ gọn, mỗi câu hỏi của user là một task có phép kiểm riêng |
| Implement | CÓ | viết báo cáo, vẽ ví dụ bốn lớp, sinh file HTML mẫu |
| Chia subagent | BỎ | đầu ra là MỘT tài liệu mạch lạc; cắt song song làm kết luận rời rạc |
| QC độc lập (agent) | BỎ | tiêu chí đếm được bằng lệnh, không cần người kiểm thứ hai |
| Deep review (tdq-reviewer) | BỎ | chỉ gọi khi user yêu cầu |
| Report | CÓ | khung bất biến, không bỏ được |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Báo cáo phân tích sáu câu | `docs/tdq/knowledge/2026-08-23-diagram-truoc-khi-code.md` | có đúng sáu mục đánh số khớp sáu câu user hỏi |
| 2 | Mục phản biện và cái giá phải trả | cùng file đầu ra 1 | nêu ít nhất ba điểm yếu của ý tưởng, mỗi điểm kèm cách giảm |
| 3 | Mục so sánh công cụ sẵn có | cùng file đầu ra 1 | có bảng đối chiếu ít nhất bốn công cụ, mỗi dòng nói rõ vì sao không dùng thẳng |
| 4 | Ví dụ bốn lớp cho luồng login | cùng file đầu ra 1 | có đủ bốn lớp: giải thuật, flow client, flow server, vị trí trong cây tổng |
| 5 | Đề xuất phương án nên chọn | cùng file đầu ra 1 | nêu vị trí chèn trong workflow, cái giá, và ít nhất một phương án bị loại |
| 6 | File dữ liệu mind-map mẫu | `docs/tdq/mind-map/vi-du-login.json` | bộ phân tích JSON chuẩn đọc được, có đủ trường của lược đồ nêu ở đầu ra 5 |
| 7 | File HTML mind-map mẫu | `docs/tdq/mind-map/vi-du-login.html` | mở bằng trình duyệt khi đã ngắt mạng vẫn hiện đủ cây |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| bao-cao | `docs/tdq/knowledge/2026-08-23-diagram-truoc-khi-code.md` | không | 1, 2, 3, 4, 5 |
| vi-du-mind-map | `docs/tdq/mind-map/vi-du-login.json`, `docs/tdq/mind-map/vi-du-login.html` | bao-cao — lược đồ dữ liệu chốt trong báo cáo trước | 6, 7 |

## 3. Cách tiếp cận & lý do

- Chọn: viết một tài liệu phân tích duy nhất, mỗi câu hỏi của user là một mục đánh số,
  mỗi kết luận gắn nguồn hoặc gắn nhãn "suy luận". Kèm hai file mẫu đặt đúng chỗ mà user
  muốn dùng về sau, để user đánh giá bằng mắt chứ không bằng tưởng tượng.
- Vì: research cho thấy tài liệu thiết kế chỉ có ích khi đúng và còn cập nhật, còn tài
  liệu lỗi thời thì hại hơn không có. Kết luận kiểu "nên làm" mà không kèm cách chống
  lệch sẽ dẫn user vào đúng cái bẫy đó. Nguồn đầy đủ ở
  `docs/tdq/research/2026-08-23-1125-diagram-giai-thuat-mind-map.md`.
- Vì: có bằng chứng đo được rằng đồ thị code giúp agent định vị lỗi tốt hơn — LocAgent
  (arXiv 2503.09089) và Prometheus (arXiv 2507.19942). Đây là chỗ câu hỏi số hai của user
  có cơ sở thật, tách khỏi phần chỉ là suy luận.
- Đã loại: sinh báo cáo tự động từ đồ thị `graphify` — vì đồ thị thấy hàm, không thấy ý đồ
  nghiệp vụ; nó không trả lời được câu nào trong sáu câu.
- Đã loại: dùng `markmap.js` cho file HTML — vì nó cần Node.js, trái ràng buộc tự chứa
  user chốt ở vòng hai.
- Đã loại: bỏ hẳn ý tưởng và khuyên user dùng GitHub Spec Kit hoặc Amazon Kiro — không
  loại hẳn mà đưa vào bảng đối chiếu, vì cả hai giải cùng bài toán nhưng thiếu lớp cây
  tổng và không cắm được vào tdq-workflow.

## 3b. Năng lực & công cụ

Chép từ brief mục `### Năng lực dùng được`. Phân vân → DÙNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | workflow đang chạy |
| tdq-spec | plugin:tdq-workflow | NỀN | workflow đang chạy |
| tdq-plan | plugin:tdq-workflow | NỀN | workflow đang chạy |
| tdq-build | plugin:tdq-workflow | NỀN | workflow đang chạy |
| tdq-conventions | plugin:tdq-workflow | NỀN | workflow đang chạy |
| tdq-lsp-setup | plugin:tdq-workflow | DÙNG | đầu ra 4 — lấy quan hệ hàm thật khi vẽ lớp function flow |
| artifact-diagramming | built-in | DÙNG | đầu ra 7 — thiết kế cây cho file HTML mẫu |
| mem0-memory | user | DÙNG | ghi một fact ngắn khi user chốt phương án |
| Đã xét 213 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service: BỎ — request này không sinh file mã nguồn chạy được, chỉ có tài liệu và một
  file HTML tĩnh, nên không có runtime để bật log.
- Unit test: BỎ — không có mã nguồn để kiểm. Thay bằng phép kiểm tài liệu qua `doc_lint.py`
  và phép mở file HTML khi đã ngắt mạng, cả hai đều nằm ở §6.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật. File HTML mẫu
  là bản viết tay, và cả file lẫn báo cáo phải nói rõ điều đó ngay chỗ dễ thấy.
- Mọi kết luận phải có nguồn. Kết luận không có nguồn phải mang nhãn "suy luận" kèm căn cứ.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`):

- "File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/`" — việc này KHÔNG chạm, vì
  không tạo file mã nguồn nào; hai file mẫu là dữ liệu và trang tĩnh.
- "Dữ liệu request `docs/tdq/`: brief, spec, plan, qc, report, state — dữ liệu, không phải
  code" — việc này chạm ở `docs/tdq/knowledge/` và `docs/tdq/mind-map/`, đều là dữ liệu.

Không cài gói mới, không tải mô hình, không gọi dịch vụ ngoài.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Báo cáo chiều theo ý user vì user đã nói sẵn vị trí chèn | user nhận lại chính ý mình, mất giá trị phản biện | bắt buộc có mục cái giá phải trả và ít nhất ba điểm yếu |
| Thiếu bằng chứng cho diagram giải thuật nghiệp vụ | kết luận nghe chắc hơn thực tế | mọi câu không có nguồn phải mang nhãn "suy luận" |
| File HTML viết tay bị hiểu là bản sinh tự động | user tưởng tính năng đã chạy được | ghi cảnh báo trong HTML và trong báo cáo |
| Báo cáo dài quá, user không đọc hết | quyết định bị hoãn | trần 250 dòng cho file báo cáo |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Báo cáo trả lời đủ sáu câu | có đúng sáu mục đánh số, thứ tự khớp sáu câu user hỏi |
| Q2 | Kết luận có nguồn | mỗi kết luận kèm URL nguồn, hoặc mang nhãn "suy luận" kèm căn cứ |
| Q3 | Có phản biện | mục phản biện nêu ít nhất ba điểm yếu, mỗi điểm kèm cách giảm |
| Q4 | Có đối chiếu công cụ sẵn có | bảng có ít nhất bốn công cụ, mỗi dòng nói vì sao không dùng thẳng |
| Q5 | Ví dụ có đủ bốn lớp | thấy đủ giải thuật, flow client, flow server, vị trí trong cây tổng |
| Q6 | Đề xuất nêu rõ vị trí chèn | nói đúng phase, kèm cái giá, kèm ít nhất một phương án bị loại |
| Q7 | Ràng buộc tự chứa được giữ | phương án đề xuất không đòi npm, pip, hay dịch vụ ngoài |
| Q8 | File dữ liệu mẫu đọc được | bộ phân tích JSON chuẩn đọc không lỗi |
| Q9 | Lược đồ dữ liệu khớp báo cáo | mọi trường trong file mẫu đều có mô tả trong báo cáo, và ngược lại |
| Q10 | HTML chạy offline | không có tham chiếu tài nguyên ngoài; ngắt mạng mở vẫn hiện đủ cây |
| Q11 | HTML khai rõ là bản mẫu | dòng khai bản viết tay hiện ngay khi mở, không phải cuộn mới thấy |
| Q12 | Tài liệu sạch linter | `doc_lint.py` báo không vi phạm trên mọi file `.md` sinh ra |
| Q13 | Báo cáo không quá dài | file báo cáo không quá 250 dòng |

DoD:

- Bảy đầu ra ở §2 đều tồn tại đúng đường dẫn đã ghi.
- Mười ba hạng mục Q1–Q13 đều PASS, mỗi hạng mục có bằng chứng trong file QC.
- `doc_lint.py` sạch trên spec, plan, báo cáo và file QC.
- Working log của ngày đã ghi qua `tdq_finish.py`, không sửa tay.
- Report cuối nói rõ request này dừng ở báo cáo, và nêu bước tiếp theo nếu user muốn build.

## 7. Câu hỏi còn mở

(Rỗng.)
