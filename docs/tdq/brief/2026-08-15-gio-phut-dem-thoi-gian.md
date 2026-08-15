# BRIEF — Tên file document có giờ phút + đếm thời gian mỗi request/phase

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> tôi muốn tạo request bổ sung là tên file document của tdqworkflow ngoài ngày tháng năm sẽ
> có thêm giờ phút và bổ sung thêm count time để biết rõ mõi mỗi request sẽ xử lí trong bao
> lâu, mỗi phase mất bao lâu

**Cách hiểu đầu tiên.**

Mục tiêu: (1) slug của một request TDQ mang thêm giờ phút, không chỉ ngày — để hai request
cùng ngày không đè hoặc lẫn nhau, và để biết request mở lúc mấy giờ ngay từ tên file. (2) Có
số liệu thời gian: mỗi request tốn bao lâu tổng cộng, mỗi phase (analyze, spec, plan,
implement, qc, report) tốn bao lâu.

Phạm vi đoán:

- Slug đổi từ `YYYY-MM-DD-<kebab>` sang có thêm giờ phút, áp cho brief/spec/plan/qc/reports.
- Mốc thời gian ghi vào `state.json` qua `scripts/tdq_state.py` (nơi duy nhất được ghi state),
  đóng dấu khi `init` và mỗi lần `set phase=`.
- Có chỗ đọc ra kết quả: bảng thời gian trong report cuối request.

Chỗ chưa rõ (đưa vào interview):

- Định dạng chính xác của phần giờ phút và vị trí trong tên file.
- Request/file CŨ có đổi tên theo chuẩn mới không, hay chỉ áp cho request mới.
- Thời gian đo là đồng hồ treo tường (gồm cả lúc chờ user duyệt) hay chỉ thời gian máy chạy —
  hai con số này lệch rất xa vì gate duyệt có thể chờ hàng giờ.
- Số liệu hiển thị ở đâu: report, `tdq-status`, working log, hay cả ba.

## Hiểu & kiến thức

### Năng lực dùng được

| Năng lực | Nguồn | Phán quyết | Vì sao |
|---|---|---|---|
| tdq-conventions | plugin:tdq-workflow | DÙNG | chính nó định nghĩa công thức slug ở §"Slug" |
| tdq-intake / tdq-spec / tdq-plan / tdq-build | plugin:tdq-workflow | DÙNG | bốn skill này in công thức slug và khuôn header doc, đổi chuẩn là phải sửa cả bốn |
| tdq-status | plugin:tdq-workflow | DÙNG | là chỗ tự nhiên để hiển thị đồng hồ đang chạy của phase hiện tại |
| graphify | project | BỎ | câu hỏi không thuộc dạng liên kết/bản đồ; vùng chạm đã xác định bằng grep |
| tavily-primary (research ngoài) | plugin | BỎ | việc thuần nội bộ, không có ẩn số bên ngoài — chuẩn đặt tên và cách đo là quyết định của chính repo này |
| mem0-memory | plugin | DÙNG | chốt xong ghi một fact ngắn về chuẩn slug mới |

### Hiện trạng code (đã đọc)

- **Không có regex nào ép định dạng ngày trong slug** ở `scripts/` hay `hooks/` — grep
  `\d{4}-\d{2}-\d{2}` ra 0 kết quả. `tdq_state.py init` chỉ kiểm tra "có truyền slug hay
  không" (dòng ~1207). Vậy slug là **chuẩn viết trong tài liệu**, không phải ràng buộc máy.
  Hệ quả: thêm giờ phút rủi ro kỹ thuật thấp, chủ yếu là sửa chữ ở skill + tài liệu.
- Công thức hiện tại `YYYY-MM-DD-<kebab ≤5 từ, không dấu>` xuất hiện ở
  `skills/tdq-conventions/SKILL.md:77`, `references/phases.md` (2 chỗ), `tdq-intake/SKILL.md:34`,
  `tdq_state.py` (3 chỗ trong bảng `next`), `docs/tdq/STATE.md:20`.
- Kho tài liệu hiện có **269 file** mang slug (brief 35 · spec 49 · plan 66 · qc 47 ·
  reports 49 · research 23) và **142 file có tham chiếu chéo** dạng `../brief/<slug>.md`.
  Đổi tên file cũ là phải sửa cả 142 tham chiếu đó — đây là chỗ đắt nhất của request.
- Về thời gian, `state.json` đã có `updated_at`, `spec_approved_at`, `plan_approved_at`,
  `quick_approved_at`. **Chưa có** mốc mở request và **chưa có lịch sử phase**, nên hiện
  không suy ra được mỗi phase tốn bao lâu. Chỗ tự nhiên để đóng dấu là `init` và nhánh
  `set phase=` trong `tdq_state.py`.
- Đã có sẵn `scripts/step_audit.py` (làm ở request trước) đo **thời gian model chạy** từ
  transcript. Đây là con số khác hẳn thời gian treo tường: một phase chờ user duyệt 2 giờ
  thì wall-clock 2 giờ nhưng model chạy 3 phút.

### Phạm vi đã chốt

- Mặt CHỌN: chức năng · bảo trì · tương thích ngược · độ tin cậy của số đo · trải nghiệm đọc số
- Mặt LOẠI: bảo mật · hiệu năng runtime của chính phép đo · đa nền tảng
- Bối cảnh: 269 file tài liệu cũ giữ nguyên tên, workflow phải đọc được cả hai định dạng
  slug; công cụ dùng cho mọi project, một người giữ
- Mức đầu tư suy ra: vừa — vì công cụ chạy thật hằng ngày nhưng chỉ một người bảo trì; chọn
  mặt độ tin cậy nên DoD phải có ca lỗi, không chỉ luồng chính

## Hỏi đáp

**Vòng 1 — scope + chức năng cốt lõi** (2026-08-15 12:11)

| # | Hỏi | Đáp |
|---|---|---|
| 1 | Ngoài chức năng, bao quanh mặt nào | A+B+C — tương thích ngược, độ tin cậy số đo, trải nghiệm đọc số |
| 2 | Kho 269 file cũ xử lý thế nào | A — giữ nguyên, KHÔNG bổ sung giờ phút; nhưng workflow phải đọc được cả hai định dạng |
| 3 | Giờ phút đặt ở đâu | A — `YYYY-MM-DD-HHMM-<kebab>`, chèn sau ngày, sort tên = sort thời gian |
| 4 | Đếm thời gian nào | A — cả hai: đồng hồ treo tường và thời gian model chạy, hiện song song |
| 5 | Số liệu hiện ở đâu | A — bảng trong report cuối request + một dòng trong `tdq-status` |

Hệ quả rút ra từ câu 2: phải có **luật đọc slug hai định dạng** — mọi chỗ dò file theo slug
chấp nhận cả `YYYY-MM-DD-<kebab>` (cũ, chỉ đọc) lẫn `YYYY-MM-DD-HHMM-<kebab>` (mới, dùng để
ghi). Đây là ràng buộc bắt buộc vào spec, không phải tuỳ chọn.

**Vòng 2** (2026-08-15 12:13)

| # | Hỏi | Đáp |
|---|---|---|
| 6 | Lịch sử thời gian lưu ở đâu | A — `state.json` khi đang chạy, đóng request thì append một dòng vào `docs/tdq/timing.jsonl` |
| 7 | Phase chạy lại thì cộng thế nào | A — cộng dồn theo phase kèm số lần vào, ví dụ `spec: 24 phút / 2 lần` |

Hết câu hỏi làm đổi kết quả. Vòng scope: CÓ chạy (dấu hiệu 2 — nhiều mặt chưa nói tới).

### Chốt kiến thức

- **Slug mới:** `YYYY-MM-DD-HHMM-<kebab ≤5 từ, không dấu>`, giờ địa phương. Chèn sau ngày để
  sort theo tên trùng với sort theo thời gian.
- **Hai định dạng cùng sống:** slug cũ `YYYY-MM-DD-<kebab>` vẫn hợp lệ khi ĐỌC, không đổi tên
  file cũ. Chỉ khi GHI mới bắt buộc có giờ phút. Cần một hàm phân giải slug dùng chung, chấp
  nhận cả hai, trả về `(ngày, giờ hoặc None, phần chữ)`.
- **Không có chỗ nào trong code dò file theo slug**: `spec_file` và `plan_file` lưu đường dẫn
  đầy đủ trong `state.json`. Nên đổi chuẩn slug không làm gãy hook nào — rủi ro nằm ở chữ
  trong tài liệu, không nằm ở đường dẫn.
- **Hai loại thời gian, đo hai cách khác nhau.** Đồng hồ treo tường lấy từ mốc trong
  `state.json` (đóng dấu ở `init` và mỗi lần `set phase=`). Thời gian model chạy lấy từ
  transcript, cộng khoảng cách giữa các bước model nằm trong cửa sổ của từng phase — tái dùng
  `scripts/step_audit.py` (đã có sẵn `iter_events`, `_parse_time`, ngưỡng `MAX_GAP_SECONDS`).
- **Ai ghi cái gì:** chỉ `tdq_state.py` được ghi `state.json` (luật kiến trúc), nên nó đóng dấu
  `phase_history`. File `timing.jsonl` không phải state nên script mới được ghi trực tiếp.
- Phương án đã loại: đổi tên 269 file cũ (user chọn giữ nguyên — phải sửa 142 tham chiếu chéo,
  giá cao mà không thêm thông tin gì); nhét lịch sử phase vào working log (log là văn xuôi,
  không phải dữ liệu, muốn cộng số phải parse chữ).

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | việc thuần nội bộ — chuẩn đặt tên và cách đo là quyết định của chính repo này, không có ẩn số bên ngoài |
| Vòng scope | CÓ | đã chạy, dấu hiệu 2 (nhiều mặt chưa nói tới) |
| Interview chi tiết | CÓ | đã chạy 2 vòng, hết câu hỏi làm đổi kết quả |
| Spec riêng + plan checkbox | CÓ | khung bất biến của chế độ chuyên sâu |
| Chia subagent | BỎ | các task nối nhau trên cùng vài file (`tdq_state.py`, skill), tách worktree chỉ đẻ xung đột |
| QC độc lập bằng agent | BỎ | mọi hạng mục DoD đều chạy được bằng một lệnh, không cần người thứ hai phán đoán |
| Review sâu bằng `tdq-reviewer` | BỎ | spec ngắn, phạm vi đã khoá bằng 7 câu trả lời của user |
| Report | CÓ | khung bất biến |
