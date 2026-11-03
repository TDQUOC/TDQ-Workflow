# BRIEF — Quốc tế hoá bộ workflow TDQ

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-08-21 · Lane: full (user chỉ định) · Nguồn vào: `docs/tdq/audit/da-ngon-ngu.md`

## Nguyên văn

Turn trước (yêu cầu checklist):
> vậy hãy lên check list còn cần những gì để có thể đưa bộ workflow này trở thành một
> version "international" hóa

Turn mở request:
> tôi muốn expect output sẽ là nguyên bộ skill có rule skill reference được viết bằng
> tiếng anh nhưng có đủ behavior và soul của bộ workflow nhưng output hoạt động ví dụ như
> doc hạocw project viết ra sẽ có ngôn ngữ == ngôn ngữ của user và tôi muốn mở request full
> từ a - d để đưa bộ workflow này hoàn toàn có thể "international"

**Đọc lần đầu**

- Mục tiêu: bộ workflow không còn ràng buộc vào tiếng Việt ở BẤT KỲ tầng nào — luật viết
  bằng tiếng Anh, còn thứ user đọc/nhận thì theo ngôn ngữ của chính user.
- Hai tầng phải tách bạch:
  - **Tầng luật (đọc bởi model)**: `SKILL.md`, `references/*.md` → viết tiếng Anh, nhưng
    giữ nguyên hành vi và "soul" (chất lượng > runtime > context cost).
  - **Tầng output (đọc bởi user)**: tài liệu request sinh ra (brief/spec/plan/qc/report),
    câu hỏi, khối duyệt → ngôn ngữ = ngôn ngữ user đang dùng.
- Phạm vi: cả 4 mặt A–D đã chấm ở `docs/tdq/audit/da-ngon-ngu.md` — cổng duyệt (máy nhận
  diện), khuôn in cho user, luật ngôn ngữ nền, lưới test/eval.
- Lane: user chỉ định **full**, không cần hỏi lại.
- Chỗ chưa rõ (đưa vào vòng hỏi): dịch tới đâu (có gồm comment trong code + thông báo hook
  không) · ngôn ngữ output phát hiện tự động hay cấu hình · tài liệu tiếng Việt đã có xử lý
  ra sao · chữ cái duyệt mở tới `a-b` hay `a-d`.

## Hiểu & kiến thức

### Năng lực dùng được

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | skill khung đang chạy phase analyze |
| tdq-spec | plugin:tdq-workflow | DÙNG | viết spec; đồng thời là ĐỐI TƯỢNG bị sửa (khuôn spec phải nói ngôn ngữ theo user) |
| tdq-plan | plugin:tdq-workflow | DÙNG | viết plan; cũng là đối tượng bị sửa |
| tdq-build | plugin:tdq-workflow | DÙNG | chạy implement/QC/report; cũng là đối tượng bị sửa |
| tdq-conventions | plugin:tdq-workflow | DÙNG | giữ luật gốc về ngôn ngữ — file phải sửa đầu tiên |
| tdq-status | plugin:tdq-workflow | DÙNG | khuôn `➤ Duyệt:` nằm trong đây |
| Đã xét 280 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

### Hiện trạng đo được (đếm thật, không ước lượng)

| Tầng | File | File có tiếng Việt | Dòng | Dòng có tiếng Việt |
|---|---|---|---|---|
| `skills/**/*.md` (luật model đọc) | 44 | 42 | 3.681 | 1.105 |
| `hooks/**/*.py` | 6 | 6 | 1.021 | 331 |
| `scripts/**/*.py` | 26 | 26 | 11.392 | 2.768 |
| `tests/**/*.py` | 55 | 55 | 14.469 | 2.222 |
| `evals/**` | 24 | 24 | 643 | 239 |
| `docs/kien-truc.md` | 1 | 1 | 50 | 30 |

Bóc riêng phần mã nguồn: `hooks/` 130 dòng comment + 134 dòng có chuỗi · `scripts/` 486
dòng comment + 1.585 dòng có chuỗi. **19 file test** đang assert ký hiệu/chuỗi máy in ra
(`✅`, `➤`, `⚠️`, `❌`) — đây là chỗ vỡ nếu đổi chuỗi máy mà không sửa test cùng lượt.

`portable_claude/` và `portable_codex/` sinh lại từ `skills/`, `hooks/`, `agents/`,
`scripts/` bằng `scripts/build_portable.py` — không dịch tay, chỉ chạy lại lệnh sinh.

### Quyết định đã chốt (từ vòng hỏi)

- **Phủ tới đâu (2c)**: thân luật `skills/**/*.md` + comment/docstring trong `hooks/`,
  `scripts/` + chuỗi máy in ra cho user. Tức cả ba tầng, không chừa tầng nào.
- **Chuỗi máy (3b)**: cố định **tiếng Anh**, không dựng cơ chế i18n tra bảng. Đây là điểm
  đánh đổi có ý thức: user tiếng Việt sẽ thấy dòng hook/CLI bằng tiếng Anh.
- **Ngôn ngữ tài liệu (4a)**: nhận ra từ ngôn ngữ user viết trong request, ghi vào state
  đúng một lần lúc `init`, cả request dùng chung một giá trị — không đổi giữa chừng.
- **Tài liệu cũ (5a)**: giữ nguyên tiếng Việt, không dịch lại — chúng là hồ sơ lịch sử.
- **Chữ cái duyệt (6a)**: mở `a`–`d` để dùng chung cho cả vòng interview nhiều option.
- **Tương thích ngược**: luật bắt buộc kế thừa từ request `da-ngon-ngu` — mọi câu duyệt
  tiếng Việt cũ và mọi request cũ phải chạy y hệt; ngôn ngữ tài liệu thiếu giá trị trong
  state thì mặc định tiếng Việt.

### Cách tiếp cận chọn & lý do

- Chọn: tách đôi rõ ràng — **luật (model đọc) = tiếng Anh cố định**, **tài liệu sinh ra
  (user đọc) = biến `doc_lang` trong state**, **chuỗi máy = tiếng Anh cố định**.
- Vì: ba tầng có ba người đọc khác nhau; gộp chúng vào một luật ngôn ngữ là nguồn gốc của
  toàn bộ ràng buộc hiện tại (mã K8, K9 của `docs/tdq/audit/da-ngon-ngu.md`).
- Nhận diện ngôn ngữ: **model tự nhận rồi khai bằng cờ lúc `init`**, state lưu lại; thiếu
  cờ thì rơi về `vi`. Đã loại: viết bộ đoán ngôn ngữ bằng Python — thêm phụ thuộc và đoán
  kém hơn chính model đang đọc câu của user.
- Đã loại: bảng chuỗi i18n cho `hooks/`/`scripts/` — user chọn 3b, và nó sẽ nhân đôi số
  điểm phải bảo trì.

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Vòng scope | GỘP | request tự khai đủ 4 mặt A–D lấy từ `docs/tdq/audit/da-ngon-ngu.md`; vòng hỏi 7 câu đã phủ cả mặt lẫn bối cảnh |
| Research web | BỎ | việc nội bộ repo, không có ẩn số ngoài; thiết kế đã chốt qua vòng hỏi |
| Interview | CÓ | đã chạy 1 vòng 7 câu, không còn câu nào đổi được sản phẩm |
| Spec | CÓ | việc lớn, chạm hook + state + test |
| Plan | CÓ | phải chia đợt vì có phụ thuộc cứng giữa các tầng |
| Implement | CÓ | mode do user chốt ở cổng `mode` |
| QC độc lập (agent) | BỎ | luật phiên hiện tại cấm gọi agent khi user không yêu cầu; QC vẫn chạy đủ bằng lệnh |
| Full suite | CÓ | 1 lần ở QC, cộng 1 lần chốt sau mỗi phase đổi chuỗi máy |
| Sinh lại `portable_*` | CÓ | bản portable là bản sao của `skills/`+`hooks/`, không sinh lại là lệch |
| Report | CÓ | luật chung |

## Hỏi đáp

Vòng 1 — 2026-08-21 23:51, user trả lời `1a 2c 3b 4a 5a 6a 7a`:

| # | Câu hỏi | Đáp |
|---|---|---|
| 1 | Request cũ xử lý sao trước khi đóng | a — commit riêng, không push (đã làm: `be46372`) |
| 2 | "Viết bằng tiếng Anh" phủ tới đâu | c — luật + comment/docstring + chuỗi máy in ra |
| 3 | Chuỗi máy theo ngôn ngữ nào | b — cố định tiếng Anh |
| 4 | Ngôn ngữ output xác định thế nào | a — nhận 1 lần lúc `init`, ghi vào state |
| 5 | Tài liệu tiếng Việt đã có | a — giữ nguyên, không dịch |
| 6 | Chữ cái ở cổng duyệt | a — mở `a`–`d` |
| 7 | Bổ sung gì thêm | a — đủ rồi |
