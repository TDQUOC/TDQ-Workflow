# BRIEF — Skill viết tiếng Anh có tối ưu hơn tiếng Việt không + phương án tối ưu workflow

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay toi muốn bạn phân tích cấu trúc của workflow và deepsreach cũng như deep analysiss
> check xem nếu nội dung skill được xử lí thành english thì có tối ưu hơn tiếng việt không?
> và có cách nào optimize hơn cho bộ workflow không và report lại tôi và những phương án patch

### Cách hiểu đầu tiên

Hai vế:
1. **So sánh ngôn ngữ**: nội dung skill (`skills/**/*.md`, `SKILL.md`) hiện viết tiếng Việt.
   Câu hỏi là dịch sang tiếng Anh có "tối ưu hơn" không — cần làm rõ tối ưu theo trục nào:
   số token nạp vào context (chi phí), độ chính xác model làm theo luật (chất lượng), hay
   cả hai. Cần deep research: cách tokenizer của Claude xử lý tiếng Việt có dấu so với
   tiếng Anh, và có bằng chứng nào về việc model theo luật tốt hơn khi đọc tiếng Anh không.
2. **Tối ưu cấu trúc bộ workflow nói chung**: đọc lại toàn bộ `skills/`, `scripts/`,
   `hooks/` để tìm điểm có thể tối ưu (context cost, runtime, trùng lặp) — đề bài rộng,
   không giới hạn sẵn phạm vi.

Ràng buộc cứng không được đổi: soul "chất lượng > runtime > context cost", output cho
user luôn tiếng Việt (không đổi ngôn ngữ giao tiếp, chỉ đang hỏi ngôn ngữ NỘI DUNG skill).

Đây là yêu cầu **phân tích + report phương án**, chưa phải lệnh patch — khớp câu
"report lại tôi và những phương án patch" (patch là output đề xuất, không phải hành động).

### Chỗ chưa rõ — phải hỏi user

1. Phạm vi tối ưu bộ workflow: chỉ xoay quanh chi phí NGÔN NGỮ (Việt/Anh), hay mở rộng cả
   cấu trúc file, trùng lặp luật, cách nạp skill (đã có `skill_router.py`/`skill_tokens.py`
   đo sẵn phần này)?
2. Có sẵn `scripts/skill_tokens.py` đo token của từng skill — dùng số đo đó làm nền, hay
   cần đo lại từ đầu?
3. Bối cảnh nêu trong lần trước: "chậm khi chạy ở project Heineken_Appketnoi" — lần tối ưu
   này có tiếp tục nhắm vào TRIỆU CHỨNG đó (project khác, không phải chính repo này) không,
   hay tổng quát cho mọi project dùng bộ workflow?

## Hiểu & kiến thức

### Năng lực dùng được

| Skill/công cụ | Nguồn | DÙNG? | Lý do |
|---|---|---|---|
| `tdq-intake` | plugin:tdq-workflow | CÓ | đang chạy phase này |
| `tdq-spec`, `tdq-plan`, `tdq-build` | plugin:tdq-workflow | CÓ | lane full |
| `tdq-conventions` | plugin:tdq-workflow | CÓ | vừa là luật, vừa là ĐỐI TƯỢNG phân tích |
| `scripts/skill_tokens.py` | project | CÓ | đo token thật, đã có sẵn từ request trước |
| `scripts/skill_router.py` | project | CÓ | nguyên mẫu router đã dựng, chỉ cần đọc kết quả |
| `docs/tdq/audit/*.md` | project | CÓ | đúng câu hỏi này đã được trả lời 2 ngày trước |
| `tavily-primary` | plugin (mcp) | KHÔNG cho vòng đầu | câu hỏi ngôn ngữ đã có số đo thật, không phải suy đoán cần research thêm |

### Phát hiện quan trọng nhất — việc này đã làm 2 ngày trước

Request `2026-08-17-2121-toi-uu-context-workflow` (lane full, đã QC 19/19, đã report,
CHƯA commit/áp dụng gì) trả lời gần như đúng nguyên hai câu user vừa hỏi lại hôm nay:

1. **Tiếng Anh có tối ưu hơn không** — đo thật (không suy đoán) bằng `anthropic-tokenizer`
   trên `approval.md`: hệ số **0,624** (1.070 → 668 token), tiết kiệm **37,6%**. Cùng nội
   dung, tiếng Anh **1,68 → 2,97 ký tự/token** so với tiếng Việt — lợi ích đến từ
   tokenizer, không từ viết ngắn lại. Đây là RỦI RO CAO NHẤT trong 5 hướng vì đụng thẳng
   chữ luật; đã dựng lưới an toàn 329 điểm neo (`audit/luat-hien-co.md` +
   `tests/test_luat_skill.py`) để làm trước khi dịch.
2. **Cách nào khác tối ưu hơn** — đề án 5 hướng A–E đã xếp thứ tự theo tiết kiệm/rủi ro
   (`audit/de-an-toi-uu-context.md`): **D** (`skillOverrides`, cấu hình, 87,7% tiết kiệm
   mô tả skill, rủi ro thấp nhất) → **C** (nạp reference theo nhu cầu) → **B** (cắt output
   tool, luật đã có sẵn chỉ chưa cưỡng chế) → **A** (dịch tiếng Anh, 37,6%, rủi ro cao) →
   **E** (router BM25 cho skill — ĐỀ NGHỊ KHÔNG LÀM, top-5 chỉ trúng 45,5%, và dịch sang
   tiếng Anh sẽ làm khoảng cách ngôn ngữ của router RỘNG THÊM chứ không hẹp lại).

Trạng thái áp dụng: **cả 5 hướng đều CHƯA áp dụng gì** — `~/.claude/settings.json` chỉ có
1 khoá `skillOverrides` từ trước (`unity-skills`), không phải của đề án này; không file
`skills/` nào bị sửa; `de-an-toi-uu-context.md` vẫn nằm ở trạng thái đề xuất.

### Số đo cần làm mới — codebase đã đổi từ 2026-08-17

Hai request sau đó (mode đội 0.25.0, băm nội dung 0.26.0) đã thêm nội dung skill. Đo lại
bằng `skill_tokens.py --theo-phase` hôm nay so với báo cáo cũ:

| Khối | 2026-08-17 | 2026-08-19 (hôm nay) | Chênh |
|---|---|---|---|
| luôn nạp | 6.243 (byte cũ ước) / 4.477 | 4.477 | ổn định |
| luật kèm (mọi reference) | 55.719 | 59.232 | +3.513 |
| **Trần lane full** | 70.924 | **74.846** | **+3.922 (+5,5%)** |

Chênh chủ yếu do `team-mode.md` (133 dòng, mới) nạp thêm khi plan dùng mode đội, và các
khuôn spec/plan/qc phình thêm mục ranh giới module + điều kiện PASS. Xu hướng: bộ luật
đang lớn dần theo thời gian — càng thêm request tối ưu càng cấp thiết.

### Câu hỏi mới hôm nay chưa có trong đề án cũ

User lần này hỏi thêm "phân tích cấu trúc của workflow" và "deep research" — rộng hơn
thuần câu ngôn ngữ. Đề án cũ (§2 Hiểu & kiến thức ở trên) đã trả lời phần ngôn ngữ đầy
đủ bằng số đo thật; phần "tối ưu hơn cho bộ workflow" đã có 4 hướng còn lại (B, C, D)
CHƯA thực thi — đúng nghĩa "cách nào optimize hơn" mà user hỏi.

## Hỏi đáp

**Vòng 1 (2026-08-18 23:59 → 2026-08-19 00:03)**

1. Làm gì tiếp — A (tổng hợp, không redo) / B (đào sâu thêm) / C (thực thi ngay hướng D)?
   → **B**: đào sâu — research thêm + thực nghiệm dịch trên mẫu lớn hơn trước khi kết luận.

### Việc đã làm ở vòng đào sâu

1. Ba truy vấn `tavily-primary` (nguồn đầy đủ:
   `docs/tdq/research/2026-08-18-2358-skill-en-vs-vi-toi-uu.md`):
   - Token/ngôn ngữ: xác nhận tiếng Việt tốn token hơn tiếng Anh (nhiều nguồn ngoài xếp
     Việt vào nhóm "heavy tax 3–5x"; số đo THẬT của repo thấp hơn vì văn bản kỹ thuật).
   - **Phát hiện mới, quan trọng nhất vòng này:** một nghiên cứu 35 ngôn ngữ (2025) trên
     tác vụ trích xuất cho thấy KHỚP ngôn ngữ chỉ dẫn với ngôn ngữ nội dung thắng "dịch
     hết sang tiếng Anh" tới 50% độ chính xác. TDQ gần tác vụ này hơn tác vụ phân loại
     (nơi nhãn tiếng Anh có lợi) — vì Claude nhận chỉ dẫn rồi tạo ra output tiếng Việt từ
     input tiếng Việt của user, không gán nhãn rời rạc.
   - Prompt caching 2026: cache-read giảm tới 90% giá, cải thiện TTFT 13–31% — token
     thân skill giờ chủ yếu là chi phí CỬA SỔ + độ trễ nhỏ, không còn là chi phí TIỀN lớn.
2. Thực nghiệm dịch thật trọn `skills/tdq-build/SKILL.md` (99 dòng, khác file với lần đo
   cũ) → hệ số **0,568** (tiết kiệm 43,2%), khớp dải với số cũ (0,624 / 37,6% trên
   `approval.md`). Dải tiết kiệm hướng A ổn định **~38–43%** qua 2 mẫu độc lập.

## Hiểu & kiến thức → chốt kiến thức (bổ sung sau vòng đào sâu)

### Quyết định cuối — trả lời trực tiếp câu hỏi ngôn ngữ

**Tiếng Anh tối ưu hơn tiếng Việt về TOKEN — đã đo chắc, ~40%.** Nhưng đối chiếu với
soul của chính bộ workflow (`chất lượng > runtime > context cost`): lợi ích của hướng A
nằm ở trục THẤP NHẤT (context cost, và giờ còn bị cache pha loãng thêm), còn rủi ro của
nó — bằng chứng gián tiếp mới tìm được (khớp ngôn ngữ chỉ dẫn/nội dung ảnh hưởng độ chính
xác tới 50% ở tác vụ gần giống TDQ) — nằm ở trục CAO NHẤT (chất lượng). Đánh đổi này đi
NGƯỢC thứ tự ưu tiên chính bộ luật tự đặt ra. Kết luận: **hướng A (dịch toàn bộ thân
skill sang tiếng Anh) không đáng làm**, không phải vì kỹ thuật khó mà vì rủi ro rơi đúng
vào trục bộ workflow coi trọng nhất, để đổi lấy lợi ích ở trục nó coi nhẹ nhất. Giữ
nguyên bốn hướng còn lại của đề án 2026-08-17: **D → C → B**, hướng E vẫn không làm.

### Nguồn
- `docs/tdq/audit/de-an-toi-uu-context.md`, `do-thuc-nghiem.md`, `luat-hien-co.md` (request 2026-08-17-2121)
- `docs/tdq/research/2026-08-18-2358-skill-en-vs-vi-toi-uu.md` (research mới, 3 truy vấn + 1 thực nghiệm)
- `scripts/skill_tokens.py --theo-phase` chạy lại hôm nay (trần lane full: 74.846 token)

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Research web | CÓ (đã xong) | ẩn số ngoài: ảnh hưởng ngôn ngữ chỉ dẫn tới độ chính xác |
| Thực nghiệm đo thêm | CÓ (đã xong) | kiểm chứng số cũ trên mẫu lớn hơn, khác file |
| Vòng scope | BỎ — đã chạy đủ ở request 2026-08-17-2121 cho cùng phạm vi (context hiệu năng, độ tin cậy, bảo trì, tương thích); request này chỉ làm mới kết luận, không mở phạm vi mới |
| Interview chi tiết | CÓ (đã hỏi A/B/C, user chọn B) | quyết định mức đào sâu |
| Spec + plan | CÓ | lane full, sản phẩm là tài liệu quyết định + patch đề xuất |
| Implement | CÓ | cập nhật `de-an-toi-uu-context.md` với kết luận mới + section quyết định A, viết report |
| QC | CÓ | tự QC theo DoD, không cần agent riêng — không sửa code sản phẩm, chỉ tài liệu |
| Review sâu / chia subagent | BỎ | tài liệu, một luồng, không có task tách file rời nhau |

