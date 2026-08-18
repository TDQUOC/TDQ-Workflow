# RESEARCH — Hybrid skill: luật tiếng Anh, giao tiếp user tiếng Việt

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Truy vấn 1 — Anthropic có khuyến nghị viết skill bằng tiếng Anh không

`Anthropic Claude Skills authoring guide write skills in English best practice`

- `platform.claude.com/docs/.../agent-skills/best-practices` (chính chủ Anthropic): không có
  dòng nào bắt buộc viết bằng tiếng Anh. Nguyên tắc cốt lõi là "concise" (context window là
  tài nguyên chung) và mô tả phải dễ được model chọn đúng lúc — không nói gì về ngôn ngữ.
- Không tìm thấy tuyên bố chính thức "skill phải viết tiếng Anh". Thực tế đa số skill cộng
  đồng viết tiếng Anh chỉ vì tác giả + cộng đồng dùng tiếng Anh, không phải vì Anthropic yêu
  cầu.

## Truy vấn 2 — nghiên cứu học thuật: chỉ dẫn (instruction) tiếng Anh, nội dung khác ngôn ngữ

`LLM instruction language vs user query language mismatch does not affect performance multilingual`

- **aclanthology.org/2025.emnlp-industry.9** (RAG đa ngữ, doanh nghiệp): cố định
  instruction/query template bằng **tiếng Anh làm mỏ neo**, tài liệu được dịch theo từng
  ngôn ngữ — instruction tiếng Anh cho kết quả **tốt nhất** ở các ngôn ngữ không phải Anh,
  tiếng Anh vẫn ổn định. NGƯỢC hướng với nghiên cứu 35 ngôn ngữ đã trích ở request trước.
- **aclanthology.org/2024.findings-eacl.90** (instruction tuning đơn/đa ngữ): model chỉ
  tune bằng tiếng Anh là **kém ổn định ngôn ngữ nhất** — hay trả lời sai NGÔN NGỮ ĐẦU RA
  (output language) bất kể câu hỏi ngôn ngữ gì, không phải sai NỘI DUNG. Đây là loại rủi ro
  khác: "lệch ngôn ngữ output", không phải "giảm độ chính xác nội dung".
- **arxiv 2601.05366** (tool-calling đa ngữ): tiền dịch query người dùng sang tiếng Anh
  trước khi gọi tool giảm lỗi nhưng không phục hồi bằng mức tiếng Anh gốc — xác nhận có
  chi phí, nhưng đo trên tác vụ gọi tool có tham số, không giống cấu trúc skill TDQ.

**Kết luận truy vấn 2**: hai nghiên cứu đá nhau về HƯỚNG ảnh hưởng của "chỉ dẫn Anh, nội
dung khác". Khác biệt nằm ở LOẠI TÁC VỤ — xem truy vấn 4 để giải quyết mâu thuẫn.

## Truy vấn 3 — system prompt tiếng Anh, user chat ngôn ngữ khác: 2025-2026

`system prompt English user prompt non-English performance cross-lingual instruction following 2025 2026`

- **tianpan.co/blog/2026-05-07** (blog kỹ thuật, không phải paper): "system prompt không
  phải văn bản trung tính — nó là khung suy luận. Viết bằng tiếng Anh trong khi user tương
  tác tiếng Đức/Nhật/Ả Rập tạo ra lệch mà số đo hiệu năng tiếng Anh không thấy được." Đề
  xuất: đo eval riêng theo từng ngôn ngữ (tỉ lệ tuân thủ format, tỉ lệ hallucination), dùng
  few-shot bằng ngôn ngữ đích cho ngôn ngữ ít tài nguyên.
- Nghiên cứu MCQ y khoa đa ngữ: dùng **system + user prompt cùng ngôn ngữ** (Đức-Đức,
  Pháp-Pháp) để so với bản tiếng Anh trên cùng nội dung đề thi — thiết kế này gần với "35
  ngôn ngữ" đã trích trước, khác thiết kế "instruction Anh cố định" của truy vấn EMNLP.

## Truy vấn 4 — mấu chốt giải mâu thuẫn: có pattern hybrid nào không

`explicit "respond in language" directive mitigates system prompt language mismatch instruction following compliance`

**Nguồn quan trọng nhất của cả đợt research này — promptquorum.com/prompt-engineering/
prompting-across-languages**, đưa ra cây quyết định tách theo LOẠI NỘI DUNG trong prompt,
không phải tách theo "dịch hết" hay "giữ hết":

| Loại nội dung trong prompt | Nên viết bằng |
|---|---|
| Luật lý luận/định dạng phức tạp (complex reasoning/formatting rules) | **Tiếng Anh** |
| Sắc thái trang trọng (formality register) | Ngôn ngữ đích |
| Định nghĩa persona | Tiếng Anh + 1 ví dụ bằng ngôn ngữ đích |
| Khai báo ngôn ngữ đầu ra | **LUÔN LUÔN tường minh** trong system prompt: "Respond in
  formal French" — không bao giờ giả định model tự khớp ngôn ngữ user |

Ba cảnh báo sai lầm thường gặp (trích trực tiếp, quan trọng cho TDQ):
1. "Dịch nguyên prompt sang ngôn ngữ đích" cho kết quả **tệ hơn** viết lại từ đầu bằng
   ngôn ngữ đích — bản dịch máy móc tạo câu chữ gượng gạo làm model bối rối.
2. Ví dụ few-shot bằng tiếng Anh cho tác vụ không phải tiếng Anh **giảm chính xác 15-20%**.
3. KHÔNG khai báo tường minh ngôn ngữ đầu ra → model đoán theo ngữ cảnh, đôi khi đoán sai.

Đối chứng thực tế (community OpenAI, GPT-5): dù có khai báo tường minh "always reply in
user's language", model vẫn có thể lệch — khai báo tường minh LÀ điều kiện cần, không phải
điều kiện đủ 100%. Không có gate nào tự động kiểm tra "output có đúng tiếng Việt không"
trong TDQ hiện tại — đây là lỗ hổng đo lường thật, độc lập với việc có dịch skill hay không.

**Giải mâu thuẫn với "35 ngôn ngữ":** nghiên cứu đó đo tác vụ TRÍCH XUẤT (extraction) —
chỉ dẫn phải khớp ngôn ngữ TÀI LIỆU ĐANG XỬ LÝ để đọc đúng. EMNLP + promptquorum đo tác vụ
LÝ LUẬN/SINH VĂN BẢN có LUẬT PHỨC TẠP — chỉ dẫn tiếng Anh làm mỏ neo ổn định, không kéo
giảm chính xác. TDQ SKILL.md gần nhóm thứ hai hơn: luật gate/tick/phase là luật lý luận có
điều kiện (if lane=quick then..., if streak≥3 then chặn...), không phải "trích xuất từ tài
liệu tiếng Việt cụ thể".

## Truy vấn 5 — bộ skill tiếng Anh cộng đồng (vd. superpowers) dùng thế nào để đảm bảo chất lượng

`Claude Code community skills repository English only non-English speaking users quality`

- Không tìm thấy tài liệu nào của `superpowers` (hay 5 bộ skill phổ biến khác được liệt
  kê: Planning with Files, Web quality skills, HashiCorp Agent Skills…) có xử lý ngôn ngữ
  đầu ra cho user không nói tiếng Anh. Các bộ này tập trung vào ĐÚNG QUY TRÌNH/ĐÚNG TOOL
  CALL (TDD cycle, debugging, refactor pattern) — không đặt ràng buộc "output phải bằng
  ngôn ngữ X" như TDQ, nên không có bề mặt lỗi để mà đo lệch ngôn ngữ đầu ra.
- Không có gate/lint nào (kiểu `doc_lint.py`/`stop_gate.py` của TDQ) trong các bộ này kiểm
  tra output đúng ngôn ngữ — nghĩa là NẾU có lệch, không ai đo được, khác hẳn TDQ nơi lệch
  sẽ hiện ra ngay (report/spec lẫn tiếng Anh, user report ngay).

**Kết luận truy vấn 5**: các bộ skill tiếng Anh phổ biến "coi như ổn" không phải vì đã giải
quyết bài toán khớp ngôn ngữ — mà vì (1) tác vụ của họ là quy trình/tool-call, ít nhạy ngôn
ngữ hơn tác vụ TDQ (gate + output tiếng Việt bắt buộc), và (2) không có phép đo nào để lộ ra
nếu có lệch. Không thể dùng "superpowers chạy tốt" làm bằng chứng an toàn cho TDQ.
