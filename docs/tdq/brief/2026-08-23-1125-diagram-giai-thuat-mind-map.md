# Brief — diagram giải thuật, function flow và mind-map tổng của project
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay bây giờ tôi muốn mở request để phân tích, vấn đề tôi đang gặp là khi dùng ai coding dev
> khá dễ mất kiểm soat, không nắm được kiến trúc, thuậtt toán, gây khó khăn trong việc tracking
> debug hoặc maintain sau này, nên tôi đang có ý tưởng là khi development sẽ xử lí xây dựng
> diagram giải thuật trước, ví dụ như login -> nhập input -> check lỗi nhập (ví dụ pass <6 chữ)
> -> mã hóa -> gửi dữ liệu về server -> server gải mã -> ... -> trả response về -> set tokent ->
> báo login success. nghĩa là tôi muốn đi từ giải thuật -> giải thuật ok sẽ tiếp tục thiết kế về
> function flow ví dụ ở client thì đi qua funtion nào script nào, ở server đi qua function nào
> script nào, cái nào thuộc module nào, helper nào một cách simple nhất có thể nhưng vẫn đầy đủ
> các bước xử lí và đủ các function đi qua, tương tự như vậy xử lí các tính năng của project cũng
> sẽ có flow như vậy và sẽ có kiểu diagrame tree tổng của cả project khiến cho dev dễ nắm trước
> khi agent code hoặc lập plan, đồng thời để dev cải thiện mindset và cũng như có behavior tree
> tổng để sau này dễ maintain và track -> và behavior tổng sẽ được gom lại và view bằng html như
> kiểu sơ đồ tư duy, thu gom bằng code, tổng hợp các diagram lại và nên lưu trong tdq/mind-map và
> nó cũng cos thể là lớp layer để claude code truy vấn luồng cũng như có thể xử lí tốt hơn trong
> việc maintainer và developer. hãy resreach và báo cáo cho tôi là 1. ý tưởng của tôi có thật sự
> giúp ích và hữu hiệu cho dev trong việc kiểm soát project không. 2có hỗ trợ được claude code
> handle dự án lớn tốt ơn không. 3có nên thêm nó vào tdq-workflow khoong? 4 nếu nên thì nên thêm
> vào ở spec/plan hay sao 5 nếu nên thêm thì phương án trình bày trong chat kiểu text - diagram
> có thể trình bày ổn không. 6 đề xuất phương án tối ưu cho tôi

### Đọc lần đầu

**Vấn đề gốc user nêu:** dùng AI coding thì code ra nhanh nhưng dev mất quyền kiểm soát — không
nắm kiến trúc, không nắm giải thuật, nên tới lúc debug hay maintain thì không lần được luồng.
Đây là vấn đề về **khả năng đọc lại** của hệ thống, không phải vấn đề chất lượng code.

**Ý tưởng user đề xuất, tách thành 4 lớp:**

1. **Lớp giải thuật** — mô tả từng bước xử lý của một tính năng, ngôn ngữ nghiệp vụ, chưa nhắc
   tên file/hàm. Ví dụ user đưa: login → nhập input → check lỗi nhập → mã hoá → gửi server →
   server giải mã → … → trả response → set token → báo success. Duyệt lớp này trước.
2. **Lớp function flow** — cùng luồng đó nhưng ánh xạ sang code thật: client đi qua script nào,
   hàm nào; server đi qua script nào, hàm nào; mỗi hàm thuộc module/helper nào. Yêu cầu "simple
   nhất có thể nhưng vẫn đủ bước xử lý và đủ hàm đi qua".
3. **Lớp tree tổng của project** — mọi tính năng đều có 2 lớp trên, gom lại thành một behavior
   tree tổng để dev nắm toàn cảnh trước khi agent code hoặc lập plan.
4. **Lớp view** — thu gom bằng code, tổng hợp các diagram, render ra HTML kiểu sơ đồ tư duy,
   lưu ở `tdq/mind-map`. Đồng thời là lớp dữ liệu để Claude Code truy vấn luồng.

**Sáu câu hỏi cần trả lời:** (1) ý tưởng có thật sự giúp dev kiểm soát project không · (2) có
giúp Claude Code xử lý dự án lớn tốt hơn không · (3) có nên thêm vào tdq-workflow không · (4)
nếu nên thì chèn vào phase nào — spec, plan, hay chỗ khác · (5) trình bày trong chat dạng
text-diagram có ổn không · (6) đề xuất phương án tối ưu.

**Phạm vi đoán:** đây là request **phân tích + báo cáo**, không phải request build. Đầu ra
mong đợi là một bản nghiên cứu trả lời đủ 6 câu kèm đề xuất phương án. Việc hiện thực hoá
(nếu user duyệt phương án) là request kế tiếp, trừ khi user nói khác.

**Chỗ chưa rõ — cần hỏi:**

- Đầu ra lần này dừng ở báo cáo, hay muốn làm luôn cả phần hiện thực trong cùng request?
- Diagram áp cho **project nào**: chính repo TDQWorkflow, hay các project khác mà TDQ workflow
  sẽ chạy lên (khả năng cao là vế sau, vì repo này gần như không có luồng client-server)?
- Diagram sinh ra bằng tay (Claude viết) hay sinh tự động từ code (đã có `graphify`, `agent-lsp`
  và `lumen` trong repo — cả ba đều đọc được quan hệ hàm)?
- Áp cho tính năng MỚI thôi, hay có bước dựng ngược mind-map cho code đã tồn tại?
- Định dạng diagram: Mermaid, hay JSON/YAML rồi render, hay cả hai?

## Hiểu & kiến thức

### Năng lực dùng được

Phân vân → DÙNG. Kiểm kê ngày 2026-08-23: 220 skill trên đĩa, cộng skill built-in trong
context. Không xoá bảng này kể cả khi không có dòng DÙNG nào.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | workflow đang chạy |
| tdq-spec | plugin:tdq-workflow | NỀN | workflow đang chạy |
| tdq-plan | plugin:tdq-workflow | NỀN | workflow đang chạy |
| tdq-build | plugin:tdq-workflow | NỀN | workflow đang chạy |
| tdq-conventions | plugin:tdq-workflow | NỀN | workflow đang chạy |
| tdq-lsp-setup | plugin:tdq-workflow | DÙNG | lớp function flow phải đối chiếu code thật; LSP là cách lấy quan hệ hàm chính xác nhất |
| artifact-diagramming | built-in | DÙNG | thiết kế sơ đồ cho file HTML mind-map mẫu |
| mem0-memory | user | DÙNG | chốt xong ghi một fact ngắn về quyết định kiến trúc này |
| Đã xét 213 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

Công cụ ngoài skill đã dùng: `mcp__tavily-primary__tavily_search` (qua sub-agent research),
`graphify` (đọc đồ thị quan hệ hàm sẵn có), `scripts/doc_lint.py` (gác tài liệu).

### Phạm vi đã chốt

- Mặt CHỌN: chống lệch tài liệu · lớp truy vấn cho agent · đa nền (mọi ngôn ngữ) · trải
  nghiệm dev (HTML mind-map + text-diagram trong chat)
- Mặt LOẠI: không mặt nào bị loại — user chọn cả 4 và bỏ phương án "chỉ cần chạy được"
- Bối cảnh: project mục tiêu 50–500 file nguồn, 10–50 tính năng; áp cho mọi project, không
  khoá ngôn ngữ; phương án đề xuất phải tự chứa, chỉ python chuẩn, HTML không CDN
- Mức đầu tư suy ra: đầy đủ — vì chọn cả 4 mặt và hệ thống phải dùng lại được ở mọi project

### Quyết định đã chốt

1. **Đầu ra của request này là TÀI LIỆU, không phải tính năng.** User chọn 2a: phân tích và
   báo cáo, dừng lại để user đọc rồi mới mở request build. Spec và plan vì thế mô tả bản báo
   cáo, giữ gọn hết mức, không phình sang mô tả tính năng mind-map.
2. **Báo cáo phải có ví dụ chạy thật** (câu 1a vòng 2): vẽ đủ 4 lớp cho một luồng login mẫu,
   kèm một file HTML mind-map mở được. Lý do user nêu: nhìn thành phẩm rồi mới quyết.
3. **Tự chứa** (câu 2a vòng 2): chỉ python chuẩn, HTML tự sinh không CDN, không thêm npm/pip.
   Đổi lại phần render phải tự viết. Loại `markmap` (cần Node.js) và mọi dịch vụ ngoài.
4. **Vị trí trong workflow: TRƯỚC plan.** User nói rõ ở vòng 2: "tổ chức diagram trước khi
   lên plan viết code". Đây là câu trả lời của chính user cho câu hỏi số 4 của họ; báo cáo
   vẫn phải nêu lý do vì sao chỗ đó đúng, và nêu cả cái giá phải trả.
5. **Sinh lai** (câu 4a vòng 1): lớp giải thuật viết tay vì máy không suy ra được ý đồ nghiệp
   vụ; lớp function flow đối chiếu máy với code thật để bắt lệch. Đây chính là chỗ chống
   "documentation drift" mà research cảnh báo.
6. **Có cả dựng ngược** (câu 5a+b): áp cho tính năng mới, và có lệnh quét dựng ngược cả
   project cho code đã tồn tại.

### Phương án bị loại và lý do

- **Chỉ viết tay cả hai lớp** — loại, vì research chỉ ra tài liệu lỗi thời hại hơn không có
  tài liệu; không có bước đối chiếu máy thì lệch là chuyện chắc chắn xảy ra.
- **Sinh tự động hết từ code** — loại, vì call graph không biết bước nào là "kiểm mật khẩu
  dưới 6 ký tự"; nó thấy hàm, không thấy ý đồ. User cũng chọn 4a.
- **Dùng markmap.js render HTML** — loại theo ràng buộc tự chứa, dù research xác nhận nó
  xuất được file offline.
- **Bỏ hẳn, khuyên dùng GitHub Spec Kit hoặc Amazon Kiro** — không loại hẳn, sẽ đưa vào báo
  cáo như phương án đối chiếu, vì cả hai giải đúng bài toán này nhưng không có lớp mind-map
  tổng và không cắm được vào tdq-workflow.

### Nguồn

Chi tiết ở `docs/tdq/research/2026-08-23-1125-diagram-giai-thuat-mind-map.md`. Bốn nguồn
quan trọng nhất: LocAgent (arXiv 2503.09089) và Prometheus (arXiv 2507.19942) đo đồ thị code
giúp agent định vị lỗi tốt hơn · Aider repo map · Xia et al. 2018 (dev tốn ~58% thời gian đọc
hiểu code) · khảo sát ngành về tài liệu lỗi thời sau 6 tháng.

**Chỗ bằng chứng yếu, phải nói rõ trong báo cáo:** chưa tìm được nghiên cứu định lượng riêng
cho việc vẽ diagram giải thuật NGHIỆP VỤ trước khi code. Phần đó suy từ thực hành spec-kit và
Kiro, là suy luận chứ không phải số đo.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Research thêm | BỎ | một vòng 4 góc đã đủ nguồn cho cả 6 câu; chỗ thiếu đã khai là suy luận |
| Spec | CÓ | đầu ra và tiêu chí "báo cáo thế nào là đạt" phải được user duyệt trước |
| Plan | CÓ | giữ gọn, mỗi câu hỏi của user là một task có phép kiểm riêng |
| Implement | CÓ | viết báo cáo, vẽ ví dụ 4 lớp cho luồng login, sinh file HTML mẫu |
| Chia subagent | BỎ | đầu ra là MỘT tài liệu mạch lạc; cắt song song sẽ làm giọng văn và kết luận rời rạc |
| QC độc lập bằng agent | BỎ | tiêu chí là đếm được (6 câu có trả lời, mỗi kết luận có nguồn, HTML mở được), không cần người kiểm thứ hai |
| Deep review (tdq-reviewer) | BỎ | chỉ gọi khi user yêu cầu |
| Report | CÓ | khung bất biến, không bỏ được |

## Hỏi đáp

### Vòng 1 — vòng scope (đã gửi 2026-08-23 11:3x, chờ trả lời)

Vòng scope CHẠY, vì request gọi tên cả một hệ thống mới chứ không trỏ vào một hành vi hay một
file, và quét khung 9 mặt thì có ít nhất 4 mặt có thể áp mà request chưa nói gì.

Sáu câu đã hỏi: (1) mặt bao quanh · (2) request này dừng ở báo cáo hay build luôn · (3) diagram
áp cho project nào · (4) diagram sinh bằng tay hay tự động từ code · (5) có dựng ngược mind-map
cho code đã tồn tại không · (6) quy mô project mục tiêu tính bằng số.

Trả lời (2026-08-23 11:38): `1abcd 2a 3 áp dụng cho mọi project cần diagram, workflow,
software,... 4a 5a+b 6b`.

| # | Câu hỏi | Trả lời của user |
|---|---|---|
| 1 | Mặt bao quanh | A+B+C+D — chống lệch, lớp truy vấn cho agent, đa nền, trải nghiệm dev. Không chọn E |
| 2 | Request dừng ở đâu | A — dừng ở BÁO CÁO, không build trong request này |
| 3 | Áp cho project nào | Mọi project cần diagram/workflow/software, không giới hạn repo nào |
| 4 | Cách sinh diagram | A — lai: giải thuật viết tay, function flow đối chiếu máy với code thật |
| 5 | Dựng ngược code cũ | A+B — áp cho tính năng mới, VÀ có lệnh quét dựng ngược cả project |
| 6 | Quy mô mục tiêu | B — vừa, 50–500 file nguồn, 10–50 tính năng |

Hệ quả đáng chú ý của câu 2: đầu ra của request này là một **tài liệu phân tích**, không phải
code. Spec và plan vì thế mô tả tài liệu đó, không mô tả tính năng mind-map.

Hệ quả của câu 3: hệ thống phải **không phụ thuộc ngôn ngữ**. Mọi đề xuất khoá cứng vào Python
hay vào một framework cụ thể đều bị loại từ vòng này.

### Vòng 2 — chi tiết (2026-08-23 11:43)

Trả lời: `1a 2a toi muốn bước này nghĩa là tổ chức diagram trước khi lên plan viết code`.

| # | Câu hỏi | Trả lời của user |
|---|---|---|
| 1 | Báo cáo có ví dụ chạy thật không | A — có, vẽ đủ 4 lớp cho luồng login mẫu, kèm 1 file HTML mở được |
| 2 | Ràng buộc phụ thuộc | A — tự chứa: chỉ python chuẩn, HTML không CDN, không thêm npm/pip |

User nói thêm, không nằm trong câu hỏi nào: **bước dựng diagram nằm TRƯỚC bước lên plan viết
code**. Đây là user tự trả lời câu hỏi số 4 của chính họ. Báo cáo vẫn phải nêu vì sao vị trí đó
đúng và cái giá phải trả, chứ không chỉ chép lại ý user.

Không còn câu nào đổi được kết quả → đóng vòng hỏi.
