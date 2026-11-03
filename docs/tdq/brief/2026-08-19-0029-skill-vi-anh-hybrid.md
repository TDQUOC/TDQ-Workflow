# BRIEF — Hybrid skill: luật tiếng Anh, giao tiếp user tiếng Việt

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn
Nguyên văn user: "hãy deep sreach xem có cách nào để convert sang tiếng anh nhưng vẫn giữ
interface giao tiếp với user bằng tiếng việt nhưng đảm bảo output, rule, behavior không?
nếu vậy thì trong claude code tôi cũng đang dùng nhiều skill bằng tiếng anh thì sao, ví dụ
như superpower cũng bằng tiếng anh thì những bộ đó đang xử lí thế nào để đảm bảo quality,
hãy deep research và deep analysis và deep think và trình bày cho tôi"

Cách hiểu đầu tiên: hai câu hỏi con, cùng một chủ đề (rủi ro lệch ngôn ngữ vừa kết luận ở
request trước — 2026-08-18-2358):
1. Có cơ chế/pattern nào để dịch luật SKILL.md sang tiếng Anh (giảm token) mà VẪN giữ
   output/behavior/rule tuân thủ đúng như bản tiếng Việt, và interface với user (chat,
   câu hỏi, report) vẫn tiếng Việt không? Tức là "song ngữ có chủ đích" thay vì dịch toàn bộ.
2. Đối chứng thực tế: các bộ skill tiếng Anh user đang dùng thật trong Claude Code (vd.
   plugin `superpowers`, có thể cả các skill built-in khác) — chúng đang tuân thủ tốt dù
   toàn tiếng Anh (với user thường gõ Việt) là vì cơ chế nào? Có phải nghiên cứu 35 ngôn
   ngữ (đã trích ở request trước) không áp dụng cho trường hợp instruction-tiếng-Anh +
   user-chat-tiếng-Việt (khác với instruction ↔ content-nội-bộ lệch nhau)?

Phạm vi đoán: đây là nghiên cứu/phân tích tiếp nối trực tiếp đề án `de-an-toi-uu-context.md`
+ report `2026-08-18-2358-skill-en-vs-vi-toi-uu.md` vừa đóng — không mở lại toàn bộ đề án,
chỉ đào sâu câu hỏi mới phát sinh. Có thể dẫn tới kết luận: hướng A (dịch skill) khả thi
HƠN nếu làm đúng kiểu hybrid (luật Anh + output Việt tách biệt), hoặc vẫn giữ nguyên
khuyến nghị không làm nhưng có thêm bằng chứng đối chứng thực tế.

Chỗ chưa rõ: user chưa nói có muốn THỰC THI patch hybrid này không, hay chỉ muốn hiểu rõ
cơ chế trước khi quyết định — cần hỏi lane trước.

## Hiểu & kiến thức

### Năng lực dùng được
| Skill/công cụ | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `tdq-intake`, `tdq-spec`, `tdq-plan`, `tdq-build` | plugin:tdq-workflow | DÙNG | đang chạy phase tương ứng |
| `tdq-conventions` | plugin:tdq-workflow | NỀN | skill khung |
| `tavily-primary` (web search) | mcp | DÙNG | research 5 truy vấn ở phase này |
| Đã xét 280+ skill khác (kể cả built-in đang thấy trong context) | plugin/built-in | KHÔNG | khác lĩnh vực — đây là việc phân tích tài liệu, không chạm code |

### Phát hiện chính — có pattern hybrid thật, không phải "dịch hết hay giữ hết"

5 truy vấn tavily (chi tiết + nguồn: `docs/tdq/research/2026-08-19-0029-skill-vi-anh-hybrid.md`).
Tóm tắt theo thứ tự suy luận:

1. **Anthropic không bắt buộc viết skill bằng tiếng Anh** — nguyên tắc chính thức chỉ là
   "concise", không nói gì về ngôn ngữ. Đa số skill cộng đồng tiếng Anh là do tác giả dùng
   tiếng Anh, không phải yêu cầu kỹ thuật.

2. **"35 ngôn ngữ" (đã trích ở request trước) và nghiên cứu EMNLP mới tìm được ĐÁ NHAU** về
   hướng ảnh hưởng khi chỉ dẫn tiếng Anh xử lý nội dung ngôn ngữ khác — nhưng đá nhau vì
   khác LOẠI TÁC VỤ, không phải một bên đúng một bên sai:
   - "35 ngôn ngữ" đo tác vụ **trích xuất** (extraction) từ tài liệu cụ thể — chỉ dẫn phải
     khớp ngôn ngữ tài liệu để đọc đúng.
   - EMNLP (RAG doanh nghiệp) đo tác vụ **lý luận/sinh văn bản có luật phức tạp** — chỉ dẫn
     tiếng Anh làm MỎ NEO ổn định, cho kết quả tốt NHẤT ở các ngôn ngữ khác, không giảm.
   - TDQ SKILL.md (gate điều kiện, tick discipline, thứ tự phase) gần nhóm thứ hai hơn:
     đây là luật lý luận có điều kiện, không phải trích xuất từ một tài liệu tiếng Việt
     cụ thể nào.

3. **Nguồn giải mâu thuẫn, quan trọng nhất cả đợt research** (promptquorum.com) — cây quyết
   định tách theo LOẠI NỘI DUNG trong prompt, không phải theo "dịch hết":
   | Loại nội dung | Nên viết bằng |
   |---|---|
   | Luật lý luận/định dạng phức tạp | **Tiếng Anh** (giúp tuân thủ tốt hơn, không phải rủi ro) |
   | Sắc thái/formality | Ngôn ngữ đích |
   | Ví dụ few-shot (khuôn report, khuôn câu hỏi user thấy) | Ngôn ngữ đích — dùng ví dụ tiếng Anh cho tác vụ không-Anh giảm chính xác 15-20% |
   | Khai báo ngôn ngữ đầu ra | **LUÔN LUÔN tường minh, đứng riêng, không bị dịch/pha loãng** |

   Cảnh báo trực tiếp áp cho TDQ: "dịch nguyên prompt sang ngôn ngữ đích" (tức làm NGƯỢC —
   TDQ đang định dịch từ Việt SANG Anh, cùng cơ chế) cho kết quả tệ hơn viết lại từ đầu;
   không khai báo tường minh ngôn ngữ đầu ra thì model đoán theo ngữ cảnh và đôi khi đoán sai.

4. **Rủi ro còn lại dù làm đúng hybrid:** khai báo tường minh "trả lời bằng tiếng Việt" là
   điều kiện CẦN, không phải ĐỦ — có ca thực tế (GPT-5, cộng đồng OpenAI) model vẫn lệch dù
   đã khai báo rõ. TDQ hiện KHÔNG có gate nào tự động kiểm "output có đúng tiếng Việt" —
   đây là lỗ hổng đo lường có thật, tồn tại độc lập với việc có làm hybrid hay không.

5. **Vì sao `superpowers` và các bộ skill tiếng Anh khác "có vẻ ổn"** dù user gõ tiếng Việt:
   không phải vì đã giải bài toán khớp ngôn ngữ — mà vì (a) tác vụ của chúng là quy
   trình/tool-call (TDD cycle, debug), ít nhạy ngôn ngữ đầu ra hơn tác vụ TDQ (output tiếng
   Việt là yêu cầu cứng, có lint/report kiểm), và (b) không có gate nào đo lệch ngôn ngữ
   trong các bộ đó — lệch có xảy ra cũng không ai thấy. Không thể dùng "superpowers chạy
   tốt" làm bằng chứng an toàn cho TDQ.

### Chốt kiến thức
- Kết luận trước (hướng A dịch TOÀN BỘ skill sang Anh → rủi ro cao, không làm) **giữ
  nguyên** — dịch nguyên khối vẫn là cách làm bị cảnh báo trực tiếp ("dịch nguyên prompt"
  cho kết quả tệ hơn viết lại), và TDQ chưa có gate đo lệch ngôn ngữ đầu ra.
- Có một pattern KHÁC, cụ thể và có bằng chứng: **tách SKILL.md theo loại nội dung**, không
  dịch nguyên khối — luật lý luận/gate/điều kiện có thể viết tiếng Anh (giúp tuân thủ tốt
  hơn theo bằng chứng mục 3), còn (a) khối khai báo ngôn ngữ đầu ra, (b) mọi khuôn/mẫu
  user nhìn thấy trực tiếp (report template, câu hỏi option A/B, brief/spec/plan) phải giữ
  nguyên tiếng Việt, viết riêng biệt, không bị gộp/dịch lẫn vào phần luật.
- Đây là một patch CÓ THỂ làm, khác hẳn hướng A gốc (dịch hết) — nhưng chi phí không nhỏ:
  phải tách lại 40+ SKILL.md theo đúng ranh giới "luật lý luận" vs "khuôn user-facing", còn
  thiếu lưới khoá hành vi (đã có `luat-hien-co.md` 329 anchor từ trước, nhưng đó là khoá
  NỘI DUNG luật, không khoá được "output có đúng tiếng Việt không" — cần thêm gate mới).
- Phạm vi request này (đã hỏi, user chọn 1A+2A): CHỈ nghiên cứu + trình bày + cập nhật đề
  án, KHÔNG patch thật bất kỳ skill nào ở request này.

### Lộ trình
| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Phân tích (đang làm) | CÓ | bắt buộc |
| Spec/Plan | CÓ | bắt buộc, nhưng rất mỏng — chỉ 2 đầu ra tài liệu, không code |
| Vòng scope round | ĐÃ LÀM Ở CHAT | user đã chọn 1A+2A ngay khi tôi hỏi, không cần lặp lại |
| Interview chi tiết thêm | BỎ | không còn câu hỏi nào đổi kết quả — phạm vi, đầu ra đã chốt rõ |
| QC độc lập bằng agent | BỎ | tài liệu thuần, tự QC bằng doc_lint + grep là đủ, giống request liền trước |
| Chia subagent | BỎ | 1 module, không tách được (giống request liền trước) |
| Implement | CÓ | nối mục mới vào đề án + viết report riêng |
| Report | CÓ | bắt buộc |

## Hỏi đáp
**Hỏi (scope round):** (1) chỉ research+trình bày, cập nhật đề án, không sửa skill thật
hay research xong patch thí điểm luôn? (2) có cần file report riêng như lần trước không?
**Đáp:** user chọn "1a 2a" — chỉ research + trình bày + cập nhật đề án (KHÔNG patch skill
thật ở request này), CÓ viết report riêng theo đúng khuôn TDQ.
