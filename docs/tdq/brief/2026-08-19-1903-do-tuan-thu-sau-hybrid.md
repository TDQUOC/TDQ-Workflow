# BRIEF — Đo hành vi tuân thủ luật sau khi chuyển thể lai

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

User chọn option A của khối đề xuất cuối request `2026-08-19-1616-huong-a-dich-hybrid`:

> **A (đề xuất): đo hành vi tuân thủ sau hybrid.** Đây là rủi ro trục cao nhất mà request
> vừa rồi cố ý chưa chạm. Lưới 329 điểm neo chỉ chứng minh *chữ luật còn đó*, không chứng
> minh *model còn tuân thủ như bản Việt* — trong khi chính `de-an-toi-uu-context.md` dẫn
> nghiên cứu 35 ngôn ngữ nói lệch ngôn ngữ chỉ dẫn/nội dung làm giảm chính xác tới 50%.
> Việc: dựng bộ kịch bản chạy thật (mở request, tick sai luật, cổng duyệt mơ hồ…) trên bản
> trước/sau, đếm số lần vi phạm luật. Có số này thì hướng A mới thật sự khép.

Nguyên văn user turn này: "A".

### Cách hiểu đầu tiên

**Mục tiêu:** trả lời bằng SỐ câu hỏi "bản thể lai có làm model tuân thủ luật kém đi
không", thay vì suy đoán từ nghiên cứu chung.

**Phạm vi đoán (chờ interview chốt):**

- Đối tượng đo: bộ skill `tdq-*` bản trước (commit `ea0cdbd`) và bản sau (`f620094`).
- Đơn vị đo: một kịch bản = một prompt tiếng Việt + danh sách luật BẮT BUỘC phải thấy
  trong hành vi trả lời. Chấm: luật nào bị vi phạm, luật nào giữ.
- Đầu ra: script chạy lại được nằm trong `scripts/`, bảng số trong `docs/tdq/audit/`.

**Chỗ chưa rõ:**

- Chạy kịch bản bằng gì: agent con thật, hay dựng khung chấm ngoại tuyến trên transcript
  có sẵn. Cái đầu tốn tiền và chậm, cái sau rẻ nhưng không đo đúng "hành vi".
- Bao nhiêu kịch bản là đủ để số có nghĩa, và chấm bằng người hay bằng máy.
- Có so thêm chiều "prompt tiếng Anh" để tách tác động của ngôn ngữ user không.

## Hiểu & kiến thức

### Năng lực dùng được

Phân vân → DÙNG. Kiểm kê ngày 2026-08-19: 284 skill trên đĩa, cộng skill built-in trong
context. Không xoá bảng này kể cả khi không có dòng DÙNG nào.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake, tdq-spec, tdq-plan, tdq-build, tdq-conventions, tdq-status | plugin:tdq-workflow | NỀN | chính workflow đang chạy — và cũng là ĐỐI TƯỢNG được đem đi đo |
| test-driven-development | plugin:superpowers | DÙNG | mỗi ca kiểm viết đỏ trước: chạy grader trên transcript giả, phải rớt, rồi mới nối vào bộ chạy thật |
| verification-before-completion | plugin:superpowers | DÙNG | chốt số cuối: cấm tuyên bố "không sụt" khi chưa có bảng số của cả hai nhánh |
| Đã xét 277 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

Ngoài skill, một **lệnh có sẵn** mới là năng lực quan trọng nhất tìm được ở bước này:
`claude plugin eval` (chi tiết ở research §1) — nó đã có sẵn ca kiểm, grader, chạy lặp,
trần tiền và xuất JSON, nên phần lớn việc "dựng khung đo" có thể không cần viết mới.

### Đã đọc trong repo

- `scripts/tdq_bench.py` — tiền lệ đúng cho request này: một dụng cụ ĐO tách hẳn khỏi dụng cụ
  chạy việc thật, và có luật "mọi hằng số phải đến từ file thực đo, thiếu thì LỖI, cấm số
  mặc định". Phép đo mới nên theo đúng luật đó.
- `docs/tdq/audit/luat-hien-co.md` + `tests/test_luat_skill.py` — 329 mã luật đã có sẵn định
  danh và neo. Bộ ca kiểm nên trỏ về chính các mã `L###` này, thay vì tự đặt tên luật mới.
- `docs/tdq/audit/ranh-gioi-luat.md` — 38 mã `user-facing` / 291 mã `ly-luan`. Nhóm
  `ly-luan` chính là nhóm bị đổi ngôn ngữ, nên là nhóm cần đo.
- `docs/kien-truc.md` — file code mới bắt buộc nằm trong `scripts/` hoặc `hooks/`.
- Chưa có thư mục `evals/`; `.claude-plugin/plugin.json` chưa khai `experimental.evals`.

### Phạm vi đã chốt

- Mặt CHỌN: độ tin của phép đo · phạm vi luật đem đo · chạy lại được về sau (hồi quy) · chi phí
- Mặt LOẠI: không mặt nào bị loại — user chọn cả bốn (A B C D), không chọn E "chỉ cần chạy được"
- Bối cảnh: chạy bằng `claude plugin eval` có sẵn · ~10 ca × 3 lần × 2 nhánh = 60 phiên agent ·
  bộ ca giữ lâu dài trong repo làm lưới hồi quy
- Mức đầu tư suy ra: vừa, nghiêng đầy đủ ở mặt độ tin — vì bộ ca sống lâu dài và mặt "độ tin"
  bắt spec phải có ngưỡng số, nhưng quy mô chạy chỉ 60 phiên nên không thể đòi độ chính xác cao

### Ràng buộc đã biết

- **Nhiễu ngẫu nhiên là kẻ thù chính.** Theo research §3, thiết kế phải ghép cặp (cùng bộ ca
  cho cả hai nhánh) và chỉ được đặt mục tiêu bắt SỤT LỚN. Một bảng số chênh vài phần trăm
  không kết luận được gì.
- **Chấm phải ưu tiên tất định.** Phần lớn luật TDQ để lại dấu vết máy đọc được (gọi
  `tdq_state.py` chưa, có file spec chưa, có dừng ở cổng duyệt không).
- **Chạy thật là tốn tiền thật** — mỗi lần chạy một ca là một phiên agent trên tài khoản của
  user. Ngân sách phải do user chốt, không tự quyết.

## Hỏi đáp

### Vòng 1 — scope (2026-08-19)

| # | Hỏi | User trả lời |
|---|---|---|
| 1 | Bao quanh những mặt nào | `1abcd` — độ tin, phạm vi luật, chạy lại được, chi phí |
| 2 | Chạy ca kiểm bằng gì | `2a` — dùng `claude plugin eval` có sẵn |
| 3 | Quy mô chạy | `3b` — ~10 ca × 3 lần × 2 nhánh = 60 phiên |
| 4 | Bộ ca sống bao lâu | `4a` — giữ lâu dài trong repo làm lưới hồi quy |

### Vòng 2 — chi tiết (2026-08-19)

| # | Hỏi | User trả lời |
|---|---|---|
| 1 | Chọn luật nào trong 291 mã `ly-luan` | A — nhóm hành vi cốt lõi: một-turn, cổng duyệt, ghi state, nhịp tick, red-green |
| 2 | Chạy ca trên model nào | A — đúng model dùng thật (Opus 5) |
| 3 | Chấm thế nào | A — chỉ nhận luật chấm được tất định, loại luật không để lại dấu vết |
| 4 | Số ra rồi làm gì | A — định ngưỡng TRƯỚC khi chạy, luật nào sụt quá ngưỡng thì mở request lùi riêng phần đó |

Câu trả lời đầu đánh số `1 2 4 5` trong khi chỉ có 4 câu — đã hỏi lại thay vì tự suy, user
xác nhận `a a a a`.

### Vòng 3 — chặn kỹ thuật (2026-08-19)

`claude plugin eval` bị khoá: cả `plugin eval init --bare` lẫn `plugin eval .` đều trả
`` `plugin eval` is currently in early access ``. Cờ bật nằm phía máy chủ theo tài khoản;
đã kiểm các biến môi trường có thể chặn việc lấy cờ và không biến nào được đặt, nên không
phải lỗi cấu hình bên mình.

Phương án thay thế đã thử và có thật: `claude -p` có `--plugin-dir <path>` (nạp plugin từ
thư mục bất kỳ, chỉ cho phiên đó), cộng `--output-format stream-json`, `--model`,
`--max-turns`. Đủ để chạy đúng thiết kế đã chốt.

| # | Hỏi | User trả lời |
|---|---|---|
| 5 | Làm gì khi `plugin eval` bị khoá | A — tự dựng bộ chạy trên `claude -p --plugin-dir`, giữ nguyên mọi lựa chọn đã chốt |

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| research thêm | BỎ | ba hướng tra đã đủ: công cụ, độ tin giám khảo, cỡ mẫu. Không còn ẩn số ngoài repo |
| spec + plan | CÓ | khung bất biến |
| implement | CÓ | khung bất biến |
| QC độc lập bằng agent | BỎ | phiên này cấu hình không gọi subagent trừ khi user yêu cầu; QC chạy trong mode chính |
| chia việc cho nhiều subagent | BỎ | như trên |
| review sâu spec/plan | BỎ | phạm vi đã chốt qua ba vòng hỏi, không còn chỗ mơ hồ |
| report | CÓ | khung bất biến |
| vòng chạy thật tốn tiền | CÓ | là chính đầu ra của request, không bỏ được |
