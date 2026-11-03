# RESEARCH — skill tiếng Anh vs tiếng Việt, tối ưu bộ workflow

Ngày: 2026-08-19 · Request: 2026-08-18-2358-skill-en-vs-vi-toi-uu

Ba truy vấn qua `tavily-primary` (`search_depth: advanced`), cộng một thực nghiệm dịch
thật (không phải research web) để kiểm chứng số của request `2026-08-17-2121` trên một
mẫu lớn hơn.

## Truy vấn 1 — token/ngôn ngữ

`Claude tokenizer Vietnamese vs English tokens per word efficiency non-English languages`

- github.com/anthropics/claude-code issue #26401 (2026): non-English languages "can cost
  65%–340% more tokens than English for equivalent content"; liệt Việt vào nhóm "heavy tax
  (3–5x+)" cùng Ả Rập, Hindi, Thái.
- medium.com/@craigtrim: cùng phân loại — tiếng Việt thuộc nhóm chịu thuế token nặng nhất.
- Số đo THẬT của repo này (xem mục thực nghiệm) thấp hơn nhiều mức "3–5x" — vì văn bản
  TDQ đậm chất kỹ thuật (đường dẫn, tên hàm, bảng), không phải văn xuôi tự do; hai con số
  không mâu thuẫn, chỉ khác loại văn bản đo.

## Truy vấn 2 — ngôn ngữ chỉ dẫn có ảnh hưởng độ chính xác không (phát hiện MỚI, quan trọng)

`LLM instruction following compliance system prompt language English vs non-English research`

- **ryanstenhouse.dev**, dẫn một nghiên cứu 2025 trên 35 ngôn ngữ về tác vụ trích xuất
  (extraction): **khớp ngôn ngữ chỉ dẫn với ngôn ngữ nội dung THẮNG cách "dịch hết sang
  tiếng Anh" tới 50% độ chính xác**. Prompt tiếng Anh xử lý nội dung không phải tiếng Anh
  còn chậm hơn 25–35%.
- arxiv 2409.07054 (native vs non-native prompting): kết quả NGƯỢC LẠI ở tác vụ few-shot
  phân loại — nhãn tiếng Anh giúp mô hình English-centric làm tốt hơn; tiếng Ả Rập cho
  kết quả tệ nhất ở cả zero-shot lẫn few-shot.
- Hai nguồn trên đá nhau theo LOẠI TÁC VỤ: extraction (nội dung + chỉ dẫn cùng ngôn ngữ
  thắng) khác classification/labeling (nhãn tiếng Anh có lợi). TDQ gần tác vụ đầu hơn —
  Claude nhận chỉ dẫn RỒI tạo output tiếng Việt từ input tiếng Việt của user, không phải
  gán nhãn rời rạc.
- Tài liệu chính thức Anthropic (`platform.claude.com/.../multilingual-support`): khuyên
  NÊU RÕ ngôn ngữ input/output mong muốn trong system prompt thay vì để model tự đoán —
  không nói thẳng "chỉ dẫn nên cùng ngôn ngữ với nội dung", nhưng ủng hộ hướng khai rõ
  ngôn ngữ, đúng luật đã có sẵn của TDQ ("mọi output cho user viết tiếng Việt").
- Không có nghiên cứu nào đo TRỰC TIẾP trường hợp của TDQ (chỉ dẫn AGENT — không phải
  chỉ dẫn tác vụ một lượt) bằng tiếng khác ngôn ngữ output. Đây là khoảng trống thật,
  giống kết luận của research 2026-08-17.

## Truy vấn 3 — prompt caching / context window 2026

`Anthropic prompt caching context window management long system prompt 2026`

- Cache-read giảm tới 90% giá input, cải thiện time-to-first-token 13–31% (nhiều nguồn
  đồng thuận, số liệu 2026). Xác nhận phiên hiện tại đang dùng cache 1 giờ.
- Hệ quả cho đề án: token trong thân skill là chi phí **CỬA SỔ CONTEXT + độ trễ nhỏ**,
  không còn là chi phí TIỀN lớn nhờ cache — đúng điều `de-an-toi-uu-context.md` đã nói,
  được củng cố thêm bằng số 2026 mới hơn.
- "Context rot": hành vi model suy giảm TRƯỚC khi chạm trần cửa sổ, không phải TẠI trần —
  lý do context cost vẫn đáng cắt dù đã có cache, chỉ là ở tầng CHẤT LƯỢNG chứ không phải
  tầng TIỀN.

## Thực nghiệm dịch thật — mẫu lớn hơn `approval.md`

Dịch trọn `skills/tdq-build/SKILL.md` (99 dòng, skill lõi, nhiều luật mệnh lệnh) sang
tiếng Anh, giữ nguyên cấu trúc/code/đường dẫn, đo bằng `anthropic_tokenizer.count_tokens`
(cùng công cụ `skill_tokens.py` dùng):

| Bản | Ký tự | Token | Ký tự/token |
|---|---|---|---|
| Tiếng Việt (gốc) | 6.396 | 3.579 | 1,79 |
| Tiếng Anh (dịch) | 7.701 | 2.034 | 3,79 |

Hệ số EN/VI = **0,568** (tiết kiệm **43,2%**) — nhất quán với con số cũ (0,624 / 37,6%
trên `approval.md`), cả hai nằm trong dải **~38–43%**. Kết luận: dải tiết kiệm token của
hướng A là ổn định qua nhiều mẫu, không phải số may rủi của một file.
