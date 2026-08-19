# Brief — hướng A bản hybrid: tách luật lý luận khỏi khuôn user-facing

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

Nguyên văn user: "mở request chỵa a dịch hybrid đi" — hiểu là mở request chạy hướng A
bản hybrid trong `docs/tdq/audit/de-an-toi-uu-context.md`.

Tôi vừa nêu ở turn trước rằng hướng A đang bị khoá bởi hai điều kiện chưa có. User
chọn mở request luôn. Ghi lại để không mất dấu, không tự diễn giải thành "user muốn
làm cả hai điều kiện trước".

### Hướng A hybrid là gì

Không phải dịch nguyên khối. Audit vòng 2026-08-19 (2) chốt cây quyết định theo LOẠI
nội dung: luật lý luận và định dạng phức tạp có thể viết tiếng Anh; còn khuôn
user-facing (câu hỏi option, khuôn report, ví dụ few-shot) và khai báo ngôn ngữ đầu ra
phải giữ tiếng Việt, tách riêng, không pha vào phần luật.

### Bối cảnh bằng số đã có

- Dịch `skills/tdq-build/SKILL.md`: 3.579 token tiếng Việt → 2.034 token tiếng Anh,
  tiết kiệm 43,2%, đo bằng `anthropic_tokenizer` thật.
- Lợi ích nằm ở trục THẤP NHẤT của soul (context cost). Rủi ro lệch ngôn ngữ
  chỉ dẫn/nội dung (một nghiên cứu 35 ngôn ngữ đo giảm tới 50% độ chính xác) nằm ở
  trục CAO NHẤT (chất lượng).
- Audit khuyến nghị KHÔNG làm ở trạng thái bằng chứng hiện tại, và nêu hai điều kiện
  để mở khoá: (a) lưới khoá hành vi rà đúng ranh giới luật lý luận vs khuôn
  user-facing cho từng skill; (b) một gate đo được output có đúng tiếng Việt không.
- Hệ quả bắc cầu: dịch xong thì 6 mô tả tiếng Việt cuối cùng trong kho skill thành
  tiếng Anh, router lexical của hướng E mất nốt phần đang chạy được.

### Chỗ chưa rõ — phải hỏi trước khi lập spec

- Phạm vi dịch: cả 6 skill `tdq-*` hay chỉ một skill làm thí điểm rồi đo.
- Hai điều kiện tiền đề: làm trước trong chính request này, làm song song, hay bỏ qua
  và chấp nhận rủi ro có ghi nhận.
- Đo bằng gì để biết bản dịch không làm hỏng hành vi — cần chốt phép đo TRƯỚC khi sửa
  chữ, nếu không sẽ không có cách nào biết là đã hỏng.

## Hiểu & kiến thức

### Năng lực dùng được (B0)

| Skill | Nguồn | Phán quyết | Vì sao |
|---|---|---|---|
| tdq-intake / tdq-spec / tdq-plan / tdq-build | plugin:tdq-workflow | DÙNG | chính khung request này |
| tdq-conventions | plugin:tdq-workflow | DÙNG | vừa là luật vừa là ĐỐI TƯỢNG bị sửa |
| tdq-status | plugin:tdq-workflow | BỎ | không hỏi trạng thái |
| superpowers (built-in) | built-in | BỎ | không có bước TDD/debug nào ngoài luật TDQ sẵn có |
| mem0-memory | user | DÙNG | quyết định kiến trúc, nên tra và ghi nhớ |

### Hạ tầng liên quan đã có trên đĩa

- `docs/tdq/audit/luat-hien-co.md` — 329 điểm neo `L###` trích từ `skills/`, kèm ba giới
  hạn tự khai (luật trải nhiều dòng, luật không có dấu mệnh lệnh lọt lưới, dương tính giả).
- `tests/test_luat_skill.py` — khoá theo NỘI DUNG, không theo số dòng.
- `tests/test_skill_shape.py`, `test_skill_tokens.py`, `test_build_portable.py` — khoá
  hình dạng, trần token, và tính đồng bộ ba bản.
- `docs/kien-truc.md` — vẫn ở trạng thái NHÁP chờ user chốt; tầng `skills/` được mô tả là
  "văn bản chỉ dẫn model; không chạy được, không có trạng thái".
- `docs/tdq/research/2026-08-19-0029-skill-vi-anh-hybrid.md` — nghiên cứu nền của hướng
  hybrid, đã có, không cần research lại từ đầu.

Vòng scope: CHẠY — yêu cầu gọi tên cả một hệ thống (bộ skill), và từ 2 mặt trở lên chưa
được nói tới trong yêu cầu gốc.

### Chốt kiến thức

Cách tiếp cận đã chọn: tách theo LOẠI nội dung, không dịch nguyên khối. Luật lý luận và
định dạng phức tạp viết lại bằng tiếng Anh; khuôn user-facing, ví dụ few-shot và câu
khai báo ngôn ngữ đầu ra giữ tiếng Việt, tách thành khối riêng để không bị pha.

Phương án đã loại: dịch nguyên khối cả file (hướng A gốc) — nguồn research dẫn trong
audit nói cách này cho kết quả tệ hơn viết lại, và nó xoá luôn ranh giới hai loại nội dung.

Ràng buộc nặng nhất, phát hiện khi đọc `tests/test_luat_skill.py`: lưới khoá hiện hành
neo vào **40 ký tự đầu của chính câu tiếng Việt**. Dịch xong thì cả 329 điểm neo đứt một
lượt — lưới an toàn chết đúng lúc cần nó nhất. Nên việc dựng lại lưới cho sống qua bản
dịch là điều kiện tiên quyết, không phải việc phụ.

Giới hạn phải nói thẳng: lưới khoá dù dựng lại cũng chỉ chứng minh mỗi điểm neo CÓ một
câu tương ứng trong bản mới, không chứng minh được NGHĨA còn nguyên. Phần nghĩa do người
soát, ghi vào bảng phân loại. Không có phép đo tự động nào cho việc model có tuân thủ
bản tiếng Anh đúng như bản tiếng Việt hay không — đây là rủi ro tồn dư, giảm bằng điểm
chốt đi-hay-dừng và lùi git, không xoá được.

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | audit đã 3 vòng, có sẵn `research/2026-08-19-0029-skill-vi-anh-hybrid.md` |
| Vòng scope | CÓ | đã chạy, user chốt 4 mặt + phạm vi toàn bộ |
| Interview chi tiết | CÓ | đã chạy, 5 câu, hết mơ hồ |
| Hồ sơ kiến trúc | CÓ | đã có `docs/kien-truc.md`, đọc rồi, vẫn ở trạng thái NHÁP |
| spec → plan → implement | CÓ | khung bất biến |
| QC độc lập bằng agent | BỎ | cấu hình phiên: không gọi subagent trừ khi user yêu cầu |
| Review sâu `tdq-reviewer` | BỎ | cùng lý do trên |
| Điểm chốt giữa chừng | CÓ | hết phase 2, trình số đo rồi chờ user quyết đi hay dừng |

## Hỏi đáp

### Vòng scope (hỏi 2026-08-19 16:20) — chờ trả lời

1. Mặt cần bao quanh. 2. Phạm vi. 3. Cách lùi khi hỏng. 4. Xử lý hai điều kiện tiền đề.

User trả lời 16:24 — `1abcd 2c 3b 4b`:

- Mặt: cả bốn — độ tin cậy hành vi, ngôn ngữ giao tiếp, bảo trì, tiết kiệm context.
- Phạm vi: cả 6 skill `tdq-*` và toàn bộ `references/`.
- Lùi: thay hẳn, lùi bằng git.
- Tiền đề: làm CẢ (a) phân loại ranh giới lẫn (b) gate ngôn ngữ trước khi dịch.

Suy ra mức đầu tư: **đầy đủ** — bốn mặt, phạm vi toàn bộ bộ luật, hai điều kiện tiền đề
đều làm. Hệ quả: độ tin cậy hành vi và ngôn ngữ đầu ra thành hạng mục QC riêng có ngưỡng
số, không gộp vào một dòng DoD chung.

### Ràng buộc kiến trúc phát hiện khi đọc code

`hooks/scripts/stop_gate.py:5` và `_common.py:8` ghi rõ: hook **không đọc transcript**,
vì bản 0.1.8 từng đọc và chặn nhầm turn hợp lệ do transcript về trễ. Nên gate đo ngôn
ngữ đầu ra, nếu muốn soi chữ model in ra chat, sẽ đụng thẳng vào quyết định đã chốt đó.
Đo trên FILE sinh ra thì không đụng. Đây là câu hỏi phải chốt trước khi lập spec.

### Vòng chi tiết (hỏi 16:25, trả lời 16:27 — `5a 6a 7a 8a 9a`)

- Gate ngôn ngữ soi FILE sinh ra (`docs/tdq/`, `docs/workinglog/`) qua `doc_lint.py`.
  Không đụng quyết định "hook không đọc transcript".
- Phân loại 329 điểm neo: máy gợi ý theo dấu hiệu, người soát từng dòng, chốt vào bảng
  có test khoá.
- Bản tiếng Anh: VIẾT LẠI từ đầu theo ý luật, không dịch sát từng dòng.
- Ngưỡng ĐẠT: 100% điểm neo còn hiệu lực VÀ gate ngôn ngữ xanh VÀ tiết kiệm ≥ 30% token.
  Thiếu một điều là lùi git.
- Gói việc: MỘT request, plan ba phase, có điểm chốt đi-hay-dừng sau phase 2.

Không còn câu hỏi nào làm đổi kết quả.
