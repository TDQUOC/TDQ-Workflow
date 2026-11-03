# SPEC — mind-map HTML trình bày dạng sơ đồ luồng

Ngày: 2026-08-27 · Bản: 1.0 · Brief: ../brief/2026-08-27-1628-mindmap-html-dang-so-do.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## Mục lục

- 1. Mục tiêu & phạm vi
- 1b. Lộ trình
- 2. Đầu ra cụ thể
- 2b. Ranh giới module
- 3. Cách tiếp cận & lý do
- 3b. Năng lực & công cụ
- 4. Yêu cầu bắt buộc
- 5. Ràng buộc & rủi ro
- 6. QC & Definition of Done
- 7. Câu hỏi còn mở

## 1. Mục tiêu & phạm vi

- Mục tiêu: trang `docs/tdq/mind-map/<feature>.html` mở lên là thấy ngay **một sơ đồ luồng SVG có
  hộp và mũi tên** — bước thường là hộp chữ nhật, bước có nhánh lỗi là hình thoi rẽ ngang, điểm
  vào và điểm ra là hộp viên thuốc — thay cho việc phải đọc hết danh sách bước mới hình dung được
  luồng. Trang tổng `index.html` cũng chuyển sang cùng phong cách và vẽ cây nhánh thành sơ đồ.
- Trong phạm vi:
  - Lớp nghiệp vụ của trang feature: thêm sơ đồ luồng SVG ở trên, giữ nguyên danh sách bước bên dưới.
  - Trang tổng: lưới phụ thuộc dùng chung bộ hộp/mũi tên/màu mới; cây nhánh đổi từ danh sách lồng
    nhau thành sơ đồ cây SVG, danh sách link cũ lùi xuống dưới sơ đồ.
  - Ba tầng hàm rời nhau: dựng mô hình → tính bố cục → sinh SVG.
  - Unit test cho từng tầng và cho các ca biên (bước lỗi, mô tả dài, sơ đồ chỉ 1 bước).
- NGOÀI phạm vi:
  - Hiệu năng render, bảo mật, đa nền tảng ngoài trình duyệt (in ấn/PDF, màn hình cảm ứng) —
    các mặt bị loại ở vòng scope.
  - Đổi cú pháp file sơ đồ `.md`: người dùng không phải viết thêm ký hiệu nào.
  - Đổi logic lớp chi tiết (cây lời gọi): giữ nguyên hành vi, chỉ dùng chung helper hình dạng/màu
    khi việc đó không đổi kết quả hiện tại của nó.
  - Đổi `scripts/tdq_mindmap.py` (lớp lệnh `sinh/kiem/xem/lien-he/doi-chieu`) — chỉ chạm bộ render.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| analyze | CÓ | đã chạy — 2 vòng hỏi, đã đóng |
| Research web | BỎ | việc thuần nội bộ: bộ vẽ SVG, cú pháp `.md`, CSS và test đều trong repo |
| Interview | CÓ | đã chạy 2 vòng, 8 câu, không còn câu nào đổi được kết quả |
| spec | CÓ | khung bất biến |
| diagram | CÓ | bắt buộc ở lane full — 2 luồng feature: dựng trang feature, dựng trang tổng |
| plan | CÓ | khung bất biến |
| Chọn mode chạy | CÓ | đo bằng `tdq_bench.py mo-phong` trên chính plan, không ước lượng bằng mắt |
| implement | CÓ | khung bất biến |
| qc | CÓ | tự QC theo `tdq-build`; mức đầu tư vừa nên DoD có ca biên |
| QC độc lập (agent) | BỎ | mọi hạng mục §6 kiểm được bằng lệnh test tự động, không cần mắt thứ hai |
| Review sâu (`tdq-reviewer`) | BỎ | phạm vi gọn trong 1 file code + 1 file test |
| report | CÓ | khung bất biến |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Tầng dựng mô hình luồng: từ danh sách `Step` phẳng ra mô hình node/cạnh, gom `B<n>` với `B<n>!` cùng số thành một cặp quyết định | `scripts/mindmap_render.py` | test: sơ đồ có `B2` và `B2!` cho ra 1 node quyết định, 1 node nhánh lỗi và 1 cạnh nhãn `lỗi`; tầng này trả dữ liệu thuần, không chứa ký tự HTML nào |
| 2 | Tầng bố cục: mỗi node có toạ độ và kích thước, hộp CAO theo số dòng chữ sau khi ngắt | `scripts/mindmap_render.py` | test: mô tả 20 từ cho ra node cao hơn mô tả 3 từ; không node nào chồng lấn node khác |
| 3 | Tầng sinh SVG lớp nghiệp vụ: hộp chữ nhật / hình thoi / viên thuốc, mũi tên có `<marker>`, nhãn `ok` và `lỗi` | `scripts/mindmap_render.py` | test: HTML sinh ra chứa `<polygon` cho bước có nhánh lỗi, `<rect` cho bước thường, và không mất chữ nào của mô tả |
| 4 | Trang feature: sơ đồ ở trên, `<ol class="steps">` giữ nguyên bên dưới | `docs/tdq/mind-map/<feature>.html` | test: cả hai khối cùng nằm trong `<section id="lop-nghiep-vu">`, sơ đồ đứng trước danh sách |
| 5 | Trang tổng: lưới phụ thuộc theo phong cách mới + cây nhánh vẽ thành sơ đồ cây SVG, danh sách link nằm dưới sơ đồ | `docs/tdq/mind-map/index.html` | test: phần cây nhánh có SVG với 1 node cho mỗi feature, mỗi node là một link; danh sách link cũ vẫn còn trong trang |
| 6 | CSS cho sơ đồ mới, dùng lại bộ biến màu 3 trạng thái theme sẵn có | `scripts/mindmap_render.py` (`STYLE`) | test: không khai thêm mã màu cứng ngoài bảng biến `--*` đang có |
| 7 | Bộ unit test cho 3 tầng và các ca biên | file test của bộ render mind-map | chạy một lệnh, xanh hết |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| render-core | `scripts/mindmap_render.py` | không | 1, 2, 3, 4, 5, 6 |
| test-render | file test của bộ render mind-map trong `tests/` | render-core | 7 |

Hai module không khai chung đường dẫn nào. Toàn bộ việc sinh HTML nằm trong đúng một file nguồn,
nên không tách thêm được nữa mà không tạo file mới — mà file mới trong `scripts/` sẽ kéo theo một
điểm nhập nữa cho `tdq_mindmap.py`, không đáng cho phạm vi này.

## 3. Cách tiếp cận & lý do

- Chọn: **sinh SVG tĩnh ngay trong Python**, chia làm 3 hàm rời nhau — dựng mô hình node/cạnh từ
  `steps` → tính bố cục (toạ độ, kích thước, ngắt dòng) → sinh chuỗi SVG. Quy ước hình dạng:
  bước `B<n>` **có** dòng `B<n>!` đi kèm vẽ **hình thoi** (chỗ rẽ), dòng `B<n>!` vẽ **hộp kết quả
  bên phải** hình thoi đó, bước không có nhánh lỗi vẽ hộp chữ nhật, bước đầu và các bước kết thúc
  vẽ viên thuốc. Cạnh xuống ghi `ok`, cạnh rẽ ngang ghi `lỗi`.
- Vì:
  - Trang mở bằng `file://` và preview trong VS Code — cả hai đều không đảm bảo tải được script từ
    CDN, nên mọi thứ phải nội tuyến (mặt "chạy offline" user chọn).
  - Chính file này đã có 2 bản mẫu SVG hộp + mũi tên (`render_svg` cho cây lời gọi,
    `_render_dependency_svg` cho lưới phụ thuộc) dùng `viewBox` có kích thước, `currentColor` và
    `<marker>` — tái dùng đúng cơ chế đó thì sơ đồ mới tự hợp cả 2 theme, không thêm phụ thuộc.
  - Tách 3 tầng là cách rẻ nhất đáp ứng mặt "dễ mở rộng": thêm hình dạng mới về sau chỉ chạm tầng
    sinh SVG, không đụng tầng mô hình và tầng bố cục.
  - Hình thoi đặt ở bước CHA (bước có nhánh lỗi) là cách đọc duy nhất khớp với ảnh tham chiếu:
    trong flowchart, hình thoi luôn là chỗ rẽ, còn hộp là kết quả của một nhánh.
- Đã loại:
  - Mermaid nạp từ CDN — phá tính chất offline.
  - Nhúng sẵn thư viện Mermaid vào file — phình vài trăm KB mỗi trang, vẫn là phụ thuộc ngoài phải
    nâng cấp bằng tay.
  - Đổi cú pháp `.md` để khai nhánh rõ hơn — 5 file sơ đồ đang có phải render y nguyên, và ràng
    buộc "user không viết thêm gì" có từ đầu request.
  - Cắt chữ theo số ký tự (`label[:26]` như lớp chi tiết đang làm) — user chốt hộp tự cao, không
    mất chữ nào.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-conventions | plugin:tdq-workflow | NỀN | luật gốc mọi phase |
| tdq-intake | plugin:tdq-workflow | NỀN | đã chạy phase analyze |
| tdq-spec | plugin:tdq-workflow | NỀN | phase hiện tại |
| tdq-diagram | plugin:tdq-workflow | DÙNG | vẽ 2 sơ đồ feature trước khi vào plan |
| tdq-plan | plugin:tdq-workflow | DÙNG | viết plan từ spec này |
| tdq-build | plugin:tdq-workflow | DÙNG | implement + qc + report, và rule ngôn ngữ `rules/python.md` |
| tdq-lsp-setup | plugin:tdq-workflow | DÙNG | luật tìm ký hiệu LSP + lumen trước grep, áp cho mọi lần tìm hàm trong phase implement |
| artifact-diagramming | built-in | DÙNG | cơ chế SVG chuẩn cho đầu ra 3 và 5: `viewBox` có kích thước, `currentColor`, `<marker>`, `role="img"` + `aria-label` |
| Đã xét 214 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: timestamp, đủ chi tiết debug, tắt được qua `TDQ_LOG=0` — theo đúng
  cơ chế log sẵn có của `mindmap_render.py`.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code viết ra bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md`,
  và bám rule ngôn ngữ trong `skills/tdq-build/references/rules/`.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md` — chỉ những dòng việc này chạm tới):

- "CLI | `scripts/` | mọi hành vi chạy được" — việc này chạm ở `scripts/mindmap_render.py`.
- "`scripts/` **không** được import `hooks/`" — việc này chạm ở `scripts/mindmap_render.py`,
  không thêm import nào ngoài thư viện chuẩn.
- "File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/`" — spec này không tạo file code mới,
  mọi thay đổi nằm trong file đã có.
- "2026-08-22: ngôn ngữ chia 3 tầng — chú thích/docstring của `scripts/` viết TIẾNG ANH cố định;
  chuỗi user thấy giữ nguyên từng chữ qua cụm `i18n-allow`" — việc này chạm ở mọi hằng
  `TEXT_*` mới (nhãn `ok`, `lỗi`, chú thích sơ đồ).
- "`tests/` gọi được vào mọi tầng" — việc này chạm ở file test của bộ render mind-map.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| SVG tĩnh không đo được bề rộng chữ thật, ngắt dòng chỉ ước lượng theo số ký tự | chữ có thể tràn hoặc thừa chỗ trong hộp | dùng font-size cố định và số ký tự/dòng suy từ `BOX_W`; test khoá điều kiện mỗi dòng không quá số ký tự đã tính |
| Sơ đồ dài ra khi mô tả dài (hộp tự cao) | trang phải cuộn nhiều | sơ đồ đặt trong khối `overflow-x: auto`, `max-width: 100%`; danh sách bước đầy đủ vẫn ngay bên dưới |
| Đổi trang tổng làm hỏng phần cây nhánh đang dùng để điều hướng | mất link tới trang feature | danh sách link cũ KHÔNG xoá, chỉ lùi xuống dưới sơ đồ; mỗi node trong sơ đồ cây cũng là một link |
| 5 file sơ đồ đang tồn tại render khác đi ngoài ý muốn | tài liệu cũ sai | test render lại cả 5 file thật, khoá điều kiện mọi bước và mọi cạnh phụ thuộc đều còn trong trang |
| Bước có nhiều nhánh lỗi liên tiếp, hoặc sơ đồ chỉ có 1 bước | bố cục vỡ, chia cho 0 | ca biên nằm trong DoD, có test riêng |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Tầng dựng mô hình tách thật | Hàm dựng mô hình trả dữ liệu thuần, kết quả của nó không chứa ký tự HTML/SVG nào; sơ đồ có `B<n>` kèm `B<n>!` cho ra đúng 1 node quyết định, 1 node nhánh lỗi, 1 cạnh nhãn `lỗi` |
| Q2 | Hộp cao theo chữ, không mất chữ | Mô tả dài hơn cho ra node cao hơn; mọi ký tự của mô tả đều xuất hiện trong SVG; không node nào chồng lấn node khác |
| Q3 | Đúng hình dạng theo vai | Bước có nhánh lỗi ra hình thoi, bước thường ra hộp chữ nhật, bước đầu và mỗi bước kết thúc ra viên thuốc; cạnh xuống ghi `ok`, cạnh rẽ ngang ghi `lỗi` |
| Q4 | Trang feature đủ 2 khối, đúng thứ tự | Sơ đồ và `<ol class="steps">` cùng trong `<section id="lop-nghiep-vu">`, sơ đồ đứng trước |
| Q5 | Lớp chi tiết không đổi hành vi | Test lớp chi tiết đang có vẫn xanh, không sửa kỳ vọng của chúng |
| Q6 | Trang tổng đúng phạm vi đã chốt | Cây nhánh có SVG, mỗi feature một node và là link; lưới phụ thuộc theo phong cách mới; danh sách link cũ vẫn còn trong trang |
| Q7 | Không phụ thuộc ngoài | Trang sinh ra không có thẻ `<script src>` hay `<link href>` trỏ ra ngoài; mở bằng `file://` hiển thị đủ sơ đồ |
| Q8 | Hợp 2 theme | Sơ đồ mới không khai mã màu cứng, chỉ dùng biến `--*` và `currentColor` |
| Q9 | 5 file sơ đồ thật render lại được | Cả 5 file trong `docs/tdq/mind-map/` render exit 0, mọi bước và mọi cạnh phụ thuộc còn trong trang |
| Q10 | Ca biên không vỡ | Sơ đồ 1 bước, sơ đồ mọi bước đều có nhánh lỗi, mô tả 20 từ — cả 3 ca render exit 0 và bố cục không chồng lấn |
| Q11 | Log service | Có dòng log timestamp khi render, `TDQ_LOG=0` thì im |
| Q12 | Ngôn ngữ đúng tầng | Mọi chuỗi user thấy được khai kèm cụm `i18n-allow`; docstring và chú thích viết tiếng Anh |

DoD:
- 12 hạng mục Q1–Q12 đều PASS, mỗi hạng mục có bằng chứng là kết quả lệnh thật trong file qc.
- Bộ test của `mindmap_render` xanh hết, và bộ test toàn repo không có lỗi MỚI so với trước request.
- 7 đầu ra ở §2 đều có mặt, mỗi đầu ra có ít nhất một hạng mục QC trỏ tới.
- Không còn `TODO`/`FIXME`/placeholder trong phần code đã sửa.

## 7. Câu hỏi còn mở

(rỗng)
