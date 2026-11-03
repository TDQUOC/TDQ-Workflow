# REPORT — cho lane nhanh một pha analyze thật

Ngày: 2026-09-01 · Plan: ../plan/2026-09-01-2103-lane-nhanh-co-pha-analyze.md · Lane: quick
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Phân tích phương án **2c** (lane nhanh có pha `analyze` thật, kèm cổng dừng chờ user duyệt
phân tích) và **3b** (phân tích đẻ file `brief/<slug>.md` riêng). Request này KHÔNG đổi dòng
code nào — chỉ đo và trình phương án để user chốt ở request sau.

## 1. Hiện trạng: lane quick khác lane full ở đâu

Lane không phải một cái nhãn — nó rẽ nhánh ở 5 chỗ trong máy state và 1 chỗ trong hook.

| Nơi | Vị trí | Lane quick hiện làm gì |
|---|---|---|
| Bảng pha | `scripts/tdq_state.py:1055` | Có nguyên một hàng `quick` riêng, gói cả 9 bước vào một ô `action` |
| Khoá tra bảng | `scripts/tdq_state.py:1181` | `phase_key` bỏ qua `phase` thật, trả về `"quick"` cho mọi pha, trừ lúc đã duyệt và về `idle` |
| Cổng duyệt theo lane | `scripts/tdq_state.py:878` | `CONG_THEO_LANE["quick"] = ("quick",)` — đúng MỘT cổng |
| Khoá state | `scripts/tdq_state.py:171` | `quick_approved`, `quick_approved_at`, `quick_approved_by`, `quick_qc_skipped` |
| Đích duyệt | `scripts/tdq_state.py:27` | `APPROVE_TARGETS = ("spec", "plan", "quick")` |
| Hook nhắc duyệt | `hooks/scripts/prompt_context.py:166` | `lane == "quick" and not quick_approved` → cổng đang chờ là `quick` |

Điểm mấu chốt: **`phase_key` nuốt pha thật của lane quick**. Dù state có ghi
`phase=implement`, mọi thứ nhìn vào workflow (bảng checklist, hook nhắc, `next`) đều thấy
`quick`. Muốn lane nhanh có pha `analyze` NHÌN THẤY ĐƯỢC thì phải sửa đúng hàm này — đó là
nút thắt của cả phương án.

Tài liệu và test đang bám theo hiện trạng: `skills/tdq-intake/references/quick-lane.md`
(9 bước, bảng so sánh 2 lane), `skills/tdq-conventions/references/phases.md` (hàng `quick`),
và 18 file test có nhắc `quick` — nặng nhất là `tests/test_state.py` (37 chỗ),
`tests/test_quick_qc.py` (36), `tests/test_lane_label.py` (19), `tests/test_phase_table.py` (13).

## 2. Thiết kế phương án 2c + 3b

### 2.1 Bảng pha tách đôi

Hàng `quick` hiện tại tách thành hai hàng: `quick_analyze` (phân tích + viết brief, dừng chờ
duyệt) và `quick` (mini-plan → duyệt → implement → QC như cũ). `phase_key`
(`scripts/tdq_state.py:1181`) đổi từ "trả `quick` cho mọi pha" thành: lane quick mà
`phase=analyze` và chưa duyệt phân tích → `quick_analyze`; còn lại giữ nguyên nhánh cũ.

### 2.2 Khoá state mới

Thêm 3 khoá vào `default_state()` (`scripts/tdq_state.py:171`): `analyze_approved`,
`analyze_approved_at`, `analyze_approved_by` — đặt tên theo đúng khuôn 3 khoá của mọi cổng
hiện có. Thêm `brief_file` để đăng ký đường dẫn brief, giống cách `spec_file`/`plan_file`
đang làm.

### 2.3 Cổng và lệnh duyệt

- `APPROVE_TARGETS` (`scripts/tdq_state.py:27`) thêm `"analyze"` → lệnh mới
  `tdq_state.py approve analyze --by "<nguyên văn>"`.
- `CONG_THEO_LANE["quick"]` (`scripts/tdq_state.py:878`) đổi từ `("quick",)` thành
  `("analyze", "quick")`. Đây là chỗ `edit_gate` và `stop_gate` cùng đọc, nên sửa một chỗ là
  cả hai hook tự hiểu cổng mới.
- Thêm hàm chặn `_chan_phan_tich_chua_duyet` cạnh `_chan_spec_chua_duyet`, gọi khi lane quick
  chuyển sang bước viết mini-plan — đúng khuôn cổng `plan` vừa vá ở 0.36.0.

### 2.4 Brief tách file (3b)

`skills/tdq-intake/references/quick-lane.md` đổi từ 9 bước thành 10: chèn bước "viết
`docs/tdq/brief/<slug>.md` rồi DỪNG chờ duyệt" trước bước viết mini spec/plan. Bảng so sánh
2 lane ở đầu file đổi ô "Documents" của cột express từ "1 file" thành "brief + 1 file
spec/plan gộp", và ô "Approval gates" từ 1 thành 2.

## 3. Rủi ro và cách chặn

| Rủi ro | Mức | Cách chặn |
|---|---|---|
| State lane quick cũ không có `analyze_approved` → cổng mới chặn oan request đang chạy dở | CAO | `_chan_phan_tich_chua_duyet` bỏ qua khi khoá vắng mặt hẳn (`None`), đúng cách `_chan_so_do_chua_duyet` cũ xử state chưa có khoá; và test khoá riêng cho state cũ |
| `stop_gate` kêu oan "chưa duyệt" cho request quick đã xong | CAO | Sửa `CONG_THEO_LANE` thay vì viết danh sách cứng trong hook — đây đúng là con bọ đã xảy ra một lần, ghi ngay trong docstring `cong_dang_cho` (`scripts/tdq_state.py:885`) |
| `edit_gate` chặn sửa code khi phân tích chưa duyệt | TRUNG BÌNH | Đúng ý muốn, nhưng phải miễn `docs/` và `tests/` như cổng hiện tại, nếu không viết brief cũng bị chặn |
| Test vỡ hàng loạt | TRUNG BÌNH | 18 file test nhắc `quick`; ước 4 file phải sửa thật (`test_state.py`, `test_phase_table.py`, `test_lane_label.py`, `test_quick_qc.py`), số còn lại chỉ nhắc chuỗi |
| Lane nhanh không còn nhanh | CAO — đây là rủi ro về sản phẩm, không phải kỹ thuật | Thấy bên dưới |

**Nói thẳng về rủi ro cuối.** Lane nhanh hiện có đúng một cổng dừng. Thêm cổng duyệt phân
tích là thành hai — user phải trả lời hai lượt cho một việc nhỏ, và khoảng cách giữa hai
lane rút lại còn: lane full có `spec` + `plan` + `mode` (3 cổng) so với lane nhanh 2 cổng.
Nếu phần lớn việc lane nhanh của bạn là việc rõ ràng, cổng thứ hai sẽ chỉ là một lượt "ok"
lấy lệ — mà một cổng ai cũng bấm qua thì không còn là cổng.

Phương án 2a (pha có tên, có file, nhưng KHÔNG thêm cổng) giữ được cái bạn muốn — phân tích
hiện rõ, có sản phẩm đọc được — mà không tốn lượt. Nếu điều bạn thực sự muốn là **thấy phần
phân tích trước khi tôi viết plan**, thì 2a + 3b đã đủ: brief nằm riêng, bạn đọc nó cùng lúc
với mini-plan trong cùng một lượt duyệt.

## 4. Ước lượng công

| Cụm | Việc | Ước |
|---|---|---|
| State | 3 khoá mới + `brief_file`, tách bảng pha, sửa `phase_key`, `CONG_THEO_LANE`, hàm chặn, đích duyệt `analyze` | ~50 phút |
| Hook | `prompt_context` nhắc cổng `analyze`; `edit_gate`/`stop_gate` ăn theo `CONG_THEO_LANE`, chỉ cần test | ~20 phút |
| Tài liệu | `quick-lane.md` 9→10 bước, `phases.md` thêm hàng, `tdq-intake/SKILL.md` Part C | ~25 phút |
| Test | 4 file sửa thật + test mới cho cổng và cho state cũ | ~40 phút |
| Phát hành | 3 bundle portable, CHANGELOG, version | ~15 phút |

Tổng khoảng **2,5 giờ**, nên chạy lane chuyên sâu vì chạm bảng pha và cổng của chính máy
state. Nếu chọn 2a (bỏ cổng) thì cụm State rút còn ~15 phút và tổng xuống khoảng 1,2 giờ.

## 5. Đề nghị

Chốt lại một câu trước khi làm: bạn muốn **thấy phân tích tách riêng** (2a + 3b, rẻ, lane
nhanh vẫn một cổng), hay muốn **chặn thật, không duyệt phân tích thì không được viết plan**
(2c + 3b, như phân tích ở trên)? Tôi đề xuất 2a + 3b, và nếu chạy vài request thấy vẫn lọt
việc thì nâng lên 2c sau — nâng thì dễ, gỡ một cổng đã quen tay thì khó.
