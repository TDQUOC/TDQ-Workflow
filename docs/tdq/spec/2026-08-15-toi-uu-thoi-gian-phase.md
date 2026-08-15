# SPEC — Tối ưu thời gian xử lý các phase của workflow

Ngày: 2026-08-15 · Bản: 1.1 · Brief: ../brief/2026-08-15-toi-uu-thoi-gian-phase.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi

- Mục tiêu: giảm **số bước model** một request phải đi, bằng cách sửa chỗ phân tầng sai
  khiến luật gộp tool call bị bỏ qua hợp lệ. Giữ nguyên soul, giữ nguyên mọi luật đang có,
  giữ nguyên mọi gate duyệt, giữ nguyên chất lượng đầu ra.
- Trong phạm vi:
  - Nâng luật gộp tool call từ tầng context cost lên tầng runtime, đặt ở chỗ luôn được nạp.
  - Bổ sung ba luật cùng họ: **hạn chế** đọc lại file khi thông tin còn đủ (luật MỀM, xem
    §4), gộp lệnh Bash độc lập, không dùng vòng `sleep` để chờ việc dài.
  - Viết kèm hàng rào chất lượng: danh sách trường hợp CẤM gộp.
  - Bổ sung mục "xếp luật vào tầng nào" cho `soul.md` (không đổi ba tầng, không đổi thứ tự).
  - Công cụ đo `scripts/step_audit.py` và sửa lỗi suy đường dẫn của `scripts/token_audit.py`.
  - Đồng bộ một dòng luật sang `portable/AGENTS.md`.
- NGOÀI phạm vi:
  - Mặt bị loại ở vòng scope: "chỉ cần chạy được" — không nhận cách làm nhanh cho xong.
  - Cắt bớt hay gộp gate duyệt (user chọn 3C: giữ nguyên behavior).
  - Cắt chữ trong SKILL.md để tiết kiệm token — đo cho thấy vô ích (5% context/turn).
  - Chặn hay nén ảnh base64 trong tool result — ưu tiên sau, để request riêng.
  - Đặt ngưỡng phần trăm cho số bước — user chọn 3C: không đặt mốc số.
  - Sửa bất kỳ file nào của project `Heineken_AppKetNoi` — nó chỉ là ca đo.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | thuần nội bộ, kết luận lấy từ transcript thật, không có ẩn số ngoài |
| Interview (vòng scope) | CÓ | đã chạy xong, user chốt 1ABC · 2A · 3C · 4A |
| Interview (vòng chi tiết) | BỎ | không còn câu nào mà đáp án khác nhau làm đổi sản phẩm |
| Chia subagent | BỎ | 7 file nhỏ phụ thuộc nhau, chia ra tốn thêm bước — trái mục tiêu |
| QC độc lập (agent) | BỎ | mọi hạng mục kiểm được bằng lệnh; gọi agent tốn thêm bước |
| Implement | CÓ | khung bất biến |
| QC chính + report | CÓ | khung bất biến |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Mục §10 của conventions đổi tên và mang luật một-lượt ở tầng runtime | `skills/tdq-conventions/SKILL.md` | `grep -n "Luật một lượt" skills/tdq-conventions/SKILL.md` ra ≥1 dòng, và mục đó có đủ ba phần `Khi nào áp dụng` / `Làm gì` / `Tự kiểm` |
| 2 | `context-budget.md` tách hai phần: chi phí bước (tầng 2) và chi phí context (tầng 3) | `skills/tdq-conventions/references/context-budget.md` | file có đúng hai tiêu đề `## Chi phí bước` và `## Chi phí context`, mỗi luật cũ vẫn còn nguyên chữ |
| 3 | Ba luật mới cùng họ: hạn chế đọc lại (mềm), gộp Bash, không vòng `sleep` | cùng file #2 | `grep -c "^- \*\*"` tăng đúng 3 so với bản cũ, và luật đọc lại có câu cho phép đọc lại khi thiếu thông tin |
| 4 | Hàng rào chất lượng: bảng CẤM gộp | cùng file #1 và #2 | bảng liệt kê đủ 4 ca: bước đỏ→xanh, khoanh vùng lỗi, lệnh phá hủy, lệnh phụ thuộc kết quả lệnh trước |
| 5 | Mục "Xếp luật vào tầng nào" trong soul | `skills/tdq-conventions/references/soul.md` | mục có bảng dấu hiệu, và ba tầng cùng thứ tự giữ nguyên từng chữ (kiểm bằng `git diff`) |
| 6 | Công cụ đo bước | `scripts/step_audit.py` | `python3 scripts/step_audit.py --help` exit 0; chạy trên transcript mẫu in đủ 5 chỉ số |
| 7 | Sửa lỗi suy đường dẫn khi tên project có `_` | `scripts/token_audit.py` | `python3 scripts/token_audit.py --project /tmp/a_b --list` tìm đúng thư mục `-tmp-a-b` |
| 8 | Test khoá hành vi mới | `tests/test_step_budget.py` | `python3 -m pytest tests/test_step_budget.py -q` xanh |
| 9 | Một dòng luật đồng bộ bản portable | `portable/AGENTS.md` | `grep -n "một lượt" portable/AGENTS.md` ra ≥1 dòng; `pytest tests/test_portable_sync.py -q` xanh |
| 10 | Mục changelog | `CHANGELOG.md` | có mục phiên bản mới, file vẫn dưới 500 dòng theo `doc_lint` R6 |

## 3. Cách tiếp cận & lý do

- Chọn: **sửa chỗ phân tầng của luật, không thêm cơ chế cưỡng chế**. Luật gộp tool call
  chuyển sang tầng runtime và nằm trong thân `tdq-conventions/SKILL.md` (file luôn nạp),
  kèm bảng CẤM gộp để không đánh đổi chất lượng.
- Vì: đo trên transcript thật của `Heineken_AppKetNoi` (phiên `0a2b58a3`, 131,5 MB) cho ra
  4.809 bước model, độ trễ trung vị 3,3 s mỗi bước, tổng 7,6 giờ; tỉ lệ tool call trên mỗi
  message của model là **1,00** trên 3.095 lượt — nghĩa là luật gộp hiện có chưa được thi
  hành lần nào. Nó nằm ở file reference ít khi nạp và được đóng khung là "tiết kiệm
  context", mà soul xếp context cost ở tầng thấp nhất, nên bỏ qua nó là hợp lệ theo đúng
  luật. Đây là lỗi phân tầng.
- Vì: cùng bộ đo cho thấy độ trễ gần như không theo kích thước context (80k → 3,0 s;
  240k → 5,1 s), còn tổng thời gian tỉ lệ thẳng với số bước. Nên đổi một ít context lấy
  ít bước hơn là đúng thứ tự soul (runtime đứng trên context cost).
- Đã loại: cắt chữ trong SKILL.md — 6 file chỉ chiếm 5% context mỗi turn, cắt xong thời
  gian gần như không đổi mà lại phá đúng thứ user muốn giữ.
- Đã loại: thêm hook chặn khi thấy nhiều tool call tuần tự — hook không phân biệt được
  hai lệnh độc lập với hai lệnh phụ thuộc nhau, sẽ chặn oan và làm chậm thêm.
- Đã loại: cắt gate duyệt — user chốt giữ nguyên behavior, và gate là thứ giữ chất lượng.

## 3b. Năng lực & công cụ

Chép từ brief mục `### Năng lực dùng được`. Phân vân → DÙNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `tdq-conventions` | plugin:tdq-workflow | DÙNG | đầu ra #1, #2, #3, #4 nằm trong chính skill này |
| `tdq-spec` | plugin:tdq-workflow | NỀN | skill khung đang chạy ở phase spec |
| `tdq-plan` | plugin:tdq-workflow | NỀN | skill khung của phase plan ngay sau khi duyệt |
| `tdq-build` | plugin:tdq-workflow | NỀN | skill khung của implement, QC, report |
| `tdq-status` | plugin:tdq-workflow | KHÔNG | khác lĩnh vực |
| Đã xét 24 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: `scripts/step_audit.py` in log có timestamp ra stderr theo
  đúng khuôn của `token_audit.py`, tắt bằng biến môi trường `TDQ_LOG=0`.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Không xoá và không rút gọn bất kỳ luật nào đang có; luật cũ chỉ được đổi chỗ và đổi
  nhãn tầng. Bản sửa phải giữ nguyên từng chữ của các gạch đầu dòng cũ.
- Ba tầng soul và thứ tự của chúng giữ nguyên tuyệt đối.
- **Luật đọc lại file là luật MỀM, cấm viết thành lệnh chặn.** User chốt 2026-08-15:
  không đổi chất lượng lấy tốc độ. Luật phải nói rõ hai chiều: còn nhớ đủ và thông tin
  còn nguyên trong context thì đừng đọc lại; **thiếu thông tin, nhớ không chắc, context
  đã bị nén, file có thể đã đổi, hoặc chỉ đọc một phần trước đó → ĐƯỢC PHÉP và NÊN đọc
  lại**. Cấm dùng từ "cấm đọc lại" hay bất kỳ cách diễn đạt chặn cứng nào. Câu chốt bắt
  buộc có trong luật: nghi ngờ thì đọc lại.
- Clean code: TẮT — user chọn B ngày 2026-08-15. Bỏ bước scan và fix cuối request; code
  viết ra VẪN tổ chức theo rule ngôn ngữ trong `skills/tdq-build/references/rules/`.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md` — bản nháp sinh cùng request này,
trình user chốt ở turn này):

- "File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/`" — việc này chạm ở
  `scripts/step_audit.py` (đặt đúng `scripts/`).
- "`skills/` chỉ được nhắc tên lệnh của `scripts/`, cấm chép nội dung script vào skill" —
  việc này chạm ở `context-budget.md` khi nhắc lệnh `step_audit.py`.
- "Chỉ `scripts/tdq_state.py` được ghi `docs/tdq/state.json`" — `step_audit.py` chỉ đọc
  transcript, không đụng state.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Gộp tool call bị hiểu thành gộp cả bước kiểm | bỏ sót test, chất lượng tụt | bảng CẤM gộp liệt kê 4 ca, kèm ví dụ ĐÚNG/SAI, và một hạng mục QC soi đúng bảng đó |
| Gộp bước đỏ→xanh làm mất bằng chứng test đỏ thật | red-green thành hình thức | ghi thẳng vào luật: bước đỏ chạy riêng một lượt, cấm gộp với bước sửa |
| Thêm chữ vào file luôn nạp làm tăng context mỗi turn | mọi request sau đắt hơn | giới hạn phần thêm ở thân SKILL.md dưới 900 ký tự, có hạng mục QC đo bằng lệnh |
| Đổi chỗ luật làm rơi mất một luật cũ | mất hành vi đang có | QC đối chiếu từng gạch đầu dòng cũ còn nguyên chữ trong bản mới |
| `step_audit.py` đọc transcript 130 MB gây treo | công cụ đo thành gánh nặng | đọc theo dòng, không nạp cả file vào bộ nhớ; có test trên file mẫu nhỏ |
| Sửa `token_audit.py` làm hỏng đường dẫn đang chạy đúng | mất công cụ đo hiện có | test giữ cả hai ca: tên có `_` và tên không có `_` |
| Sửa `soul.md` bị coi là đổi soul | phá luật gốc | chỉ THÊM mục mới; QC dùng `git diff` chứng minh phần ba tầng không đổi một ký tự |
| Bản portable lệch với `skills/` | agent ngoài đi sai bước | chạy `pytest tests/test_portable_sync.py` trong DoD |
| Luật hạn chế đọc lại bị hiểu thành chặn cứng | model suy luận trên nội dung cũ hoặc trên tóm tắt sau nén, ra kết luận sai về hiện trạng file | luật viết dạng mềm, liệt kê 5 ca BẮT BUỘC đọc lại, kết bằng câu "nghi ngờ thì đọc lại"; có hạng mục QC soi đúng câu đó |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Luật một-lượt nằm ở thân skill luôn nạp | `grep -n "Luật một lượt" skills/tdq-conventions/SKILL.md` | ra ≥1 dòng |
| Q2 | Luật mới có đủ ba mục theo soul nguyên tắc 3 | đọc mục, đối chiếu `Khi nào áp dụng` / `Làm gì` / `Tự kiểm` | đủ cả ba |
| Q3 | Luật gộp mang nhãn tầng runtime, không phải context cost | `grep -n "runtime" skills/tdq-conventions/SKILL.md` | dòng nhãn tầng nêu rõ runtime |
| Q4 | Không luật cũ nào bị mất chữ | `git diff skills/tdq-conventions/references/context-budget.md` | mọi gạch đầu dòng cũ còn nguyên văn |
| Q5 | Ba tầng soul không đổi | `git diff skills/tdq-conventions/references/soul.md` | phần "Thứ tự ưu tiên" không có dòng bị xoá hay sửa |
| Q6 | Bảng CẤM gộp đủ 4 ca | `grep -c "^|" <mục bảng>` | đủ 4 dòng ca, mỗi ca có lý do |
| Q7 | Phần thêm vào file luôn nạp dưới trần | `git diff --numstat skills/tdq-conventions/SKILL.md` và đếm ký tự phần thêm | ≤ 900 ký tự |
| Q8 | Công cụ đo chạy được | `python3 scripts/step_audit.py --help` | exit 0 |
| Q9 | Công cụ đo ra đúng số trên file mẫu | chạy trên transcript mẫu trong `scripts/samples/` | in đủ 5 chỉ số, số khớp giá trị tính tay trong test |
| Q10 | Log service bật mặc định, tắt được | chạy `step_audit.py` một lần thường và một lần `TDQ_LOG=0` | lần đầu có dòng log kèm timestamp ở stderr, lần sau không có |
| Q11 | Lỗi tên project có `_` đã hết | `python3 scripts/token_audit.py --project /tmp/a_b --list` | trỏ đúng thư mục `-tmp-a-b` |
| Q12 | Không hồi quy tên project không có `_` | test cũ của `token_audit` | xanh |
| Q13 | Test mới xanh | `python3 -m pytest tests/test_step_budget.py -q` | xanh |
| Q14 | Toàn bộ test cũ xanh | `python3 -m pytest -q` | không có test đỏ |
| Q15 | Bản portable không lệch | `python3 -m pytest tests/test_portable_sync.py -q` | xanh |
| Q16 | Tài liệu qua lint | `python3 scripts/doc_lint.py <các file vừa sửa>` | exit 0 |
| Q17 | Luật đọc được bởi model yếu | `python3 -m pytest tests/test_soul_rules.py -q` | xanh |
| Q18 | Đo được hiệu quả thật | chạy `step_audit.py` trên transcript của chính request này sau khi build xong | báo cáo có số tool call trên mỗi message, so với mốc 1,00 của ca đo cũ |

| Q19 | Luật đọc lại là luật mềm, không chặn cứng | `pytest tests/test_step_budget.py -q -k doc_lai_mem` | luật có đủ 5 ca bắt buộc đọc lại và câu "nghi ngờ thì đọc lại"; không chứa chuỗi "cấm đọc lại" |

DoD: đủ 10 đầu ra ở §2 · Q1–Q19 PASS · `pytest -q` không đỏ · `doc_lint.py` exit 0 trên
mọi file sửa · không luật cũ nào bị xoá hay rút gọn · ba tầng soul không đổi một ký tự ·
working log của mọi turn đã ghi · report ghi rõ số đo trước và sau.

## 7. Câu hỏi còn mở

(rỗng)
