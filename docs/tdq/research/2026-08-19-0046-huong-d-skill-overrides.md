# RESEARCH — Hướng D: `skillOverrides` có thật sự tiết kiệm 87,7% không

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Truy vấn — tài liệu chính thức `skillOverrides`

`Claude Code settings.json skillOverrides name-only user-invocable-only off documentation`

### Phát hiện 1 (chặn đường) — `skillOverrides` KHÔNG áp cho plugin skill

`code.claude.com/docs/en/skills`, mục "Override skill visibility from settings", nguyên văn:

> **Plugin skills are not affected by `skillOverrides`. Manage those through `/plugin` instead.**

`code.claude.com/docs/en/settings` nhắc lại ở dòng mô tả khoá: *"Does not apply to plugin
skills, which are managed through `/plugin`."* Nguồn thứ ba (thejavaguy.org) độc lập xác
nhận: *"It applies only to plain skills in `~/.claude/skills/` or `.claude/skills/`;
plugin skills are out of its reach."*

**Hệ quả trực tiếp lên đề án cũ:** file `skill-overrides-de-xuat.json` có 261 khoá, nhưng
chỉ **33 khoá là skill nguồn `user`** — 228 khoá còn lại là plugin skill, tức là **no-op**.
Con số "tiết kiệm 87,7%" trong đề án 2026-08-17 **không thực hiện được** bằng cơ chế này.

### Phát hiện 2 — bốn mức, và câu hỏi mở của đề án đã có lời giải

| Giá trị | Model thấy gì | Trong menu `/` |
|---|---|---|
| `on` (mặc định khi không khai) | tên + mô tả | có |
| `name-only` | **chỉ tên** | có |
| `user-invocable-only` | ẩn hẳn khỏi lựa chọn tự động của model | có |
| `off` | ẩn hoàn toàn (kể cả Remote Control, Agent SDK) | không |

Đề án cũ để mở câu hỏi *"`name-only` có còn cho model tự gọi skill không"* và chỉ có bằng
chứng gián tiếp từ chuỗi trong binary. **Tài liệu chính thức trả lời: CÓ** — `name-only`
vẫn được liệt kê cho model (chỉ giấu phần mô tả), model biết skill tồn tại nhưng mất phần
mô tả cho biết KHI NÀO nên dùng.

### Phát hiện 3 (rủi ro lịch sử) — cơ chế này từng hỏng hoàn toàn

- GitHub issue **#50631** (v2.1.114): `skillOverrides` ở user/project settings **không có
  tác dụng** — hàm gác `g7H()` là stub luôn trả `"on"`, resolver chỉ đọc `policySettings`
  và `flagSettings`. Menu `/skills` hiện đúng màu nhưng system prompt vẫn đủ mô tả.
- GitHub issue **#56494** ghi nhận **v2.1.129 mới có behavior thật** với ba mức.
- Máy đang chạy **v2.1.234** → đã qua ngưỡng, nhưng đây là cơ chế có tiền sử hỏng âm thầm
  (đúng kiểu lỗi không có tín hiệu), nên phải kiểm chứng bằng phiên thật, không tin suông.

### Phát hiện 4 (đòn bẩy MỚI, đề án cũ chưa biết) — hai khoá cắt được cả plugin skill

`code.claude.com/docs/en/settings` có hai khoá không xuất hiện ở đề án 2026-08-17:

- **`skillListingMaxDescChars`** (mặc định `1536`): trần ký tự cho phần `description` +
  `when_to_use` của **mỗi** skill trong listing. Dài hơn thì bị cắt. Áp cho MỌI skill, kể
  cả plugin — đây là đòn bẩy duy nhất tìm được chạm được vào 90% token đang tốn.
- **`skillListingBudgetFraction`**: ngân sách tổng cho phần listing.

## Đo lại bằng số thật (`anthropic_tokenizer`, cùng cách đo với `skill_tokens.py --mo-ta`)

284 skill đang bật · 29.788 token mô tả (khớp y hệt số đo 2026-08-17, kho skill không đổi).

**Phân rã theo nguồn — đây là con số quan trọng nhất của vòng này:**

| Nhóm | Token mô tả | `skillOverrides` áp được? |
|---|---|---|
| 33 skill nguồn `user` | 2.981 (10,0%) | CÓ |
| 251 skill nguồn `plugin` | 26.807 (90,0%) | **KHÔNG** |

Nếu đưa cả 33 skill `user` về `name-only`: 29.788 → 27.156, tiết kiệm **2.632 token
(8,8%)** — không phải 87,7%.

**Đòn bẩy `skillListingMaxDescChars` (áp cho cả plugin):**

| Trần ký tự | Token còn lại | Tiết kiệm |
|---|---|---|
| 1536 (hiện tại) | 29.788 | — |
| 800 | 29.130 | 658 (2,2%) |
| 500 | 25.758 | 4.030 (13,5%) |
| **300** | **19.974** | **9.814 (32,9%)** |
| 200 | 15.432 | 14.356 (48,2%) |
| 120 | 10.966 | 18.822 (63,2%) |

Bối cảnh chọn ngưỡng: mô tả hiện tại có trung vị **362 ký tự**, dài nhất 1.097; **65% skill
vượt 300 ký tự**. Hướng dẫn viết skill của cộng đồng (dẫn từ best practices) khuyên giữ
mô tả **dưới 300 ký tự** — nghĩa là trần 300 chủ yếu cắt đúng nhóm mô tả viết dài quá mức
khuyến nghị. **6 skill `tdq-*` dài 138-155 ký tự, không bị trần 300 chạm tới.**

**Đòn bẩy thứ ba — tắt hẳn plugin không dùng** (đường chính thức cho plugin skill).
Top tốn token mô tả:

| Plugin | Token |
|---|---|
| `data-engineering` | 3.698 |
| `huggingface-skills` | 3.224 |
| (33 skill `user`) | 2.981 |
| `hyperframes` | 2.423 |
| `figma` | 1.455 |
| `adobe-for-creativity` | 1.381 |
| `firecrawl` | 1.342 |
| `qt-development-skills` | 1.328 |

## Trạng thái hiện tại của `~/.claude/settings.json`

Đã có khoá `skillOverrides` với đúng **1 mục**: `unity-skills: user-invocable-only` (user
tự đặt trước đó). Hướng D **chưa hề được áp** — 261 khoá đề xuất vẫn nằm ngoài file.
