# SPEC — Hoàn thiện product document trên Excalidraw

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-08-12 · Bản: 1.0 · Brief: ../brief/2026-08-12-hoan-thien-doc-excalidraw.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi

- Mục tiêu: biến canvas Excalidraw đang có 5 khối rời rạc thành **một product document
  13 chương**, xếp một cột dọc đọc từ trên xuống theo thứ tự Diátaxis, không khối nào
  chồng lấn hay tràn chữ, và export được ra `docs/diagrams/` để version cùng repo.

- Trong phạm vi:
  - Vẽ mới 8 chương còn thiếu trên canvas
  - Di chuyển 5 khối cũ về đúng vị trí chương, thêm số chương vào tiêu đề
  - Thêm mục lục (table of contents) ở đầu canvas
  - Export `.excalidraw` + PNG vào `docs/diagrams/`

- NGOÀI phạm vi:
  - Không viết lại nội dung 5 khối cũ (chỉ đổi tọa độ + số chương ở tiêu đề)
  - Không đổi bất kỳ file mã nguồn nào của plugin (`scripts/`, `hooks/`, `skills/`)
  - Không tạo bản document dạng Markdown song song — canvas là bản duy nhất
  - Không dịch sang tiếng Anh

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ (đã xong) | Cần chuẩn ngoài (Diátaxis) để chốt thứ tự chương |
| Interview | CÓ (đã xong vòng 1) | User đã chốt 1A 2A 3A 4A |
| Spec | CÓ | Khung bất biến |
| Plan | CÓ | 13 chương cần checklist tick từng chương |
| Implement | CÓ | Khung bất biến |
| Chia subagent | BỎ | Mọi thao tác đi qua một canvas dùng chung — nhiều agent ghi song song sẽ tranh z-order và tọa độ |
| QC | CÓ | Kiểm hình học bằng script trên scene JSON + screenshot |
| QC độc lập (agent `tdq-qc-tester`) | BỎ | QC là kiểm hình học chạy bằng lệnh; agent phụ không xem được canvas |
| Review sâu (`tdq-reviewer`) | BỎ | Spec ngắn, phạm vi đã chốt bằng 4 câu interview |
| Report | CÓ | Khung bất biến |

## 2. Đầu ra cụ thể

Bố cục: một cột dọc, mỗi chương là một khối có khung viền + dải tiêu đề màu, tiêu đề
mở đầu bằng `<số>. `. Thứ tự chương theo Diátaxis (overview → getting started →
concepts → how-to → architecture → reference → troubleshooting → roadmap).

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Mục lục 13 chương | Canvas, trên cùng | Có 13 dòng, mỗi dòng khớp tiêu đề chương thật |
| 2 | Ch.1 Tổng quan sản phẩm (MỚI) | Canvas | Có đủ 4 ô: vấn đề, đối tượng, giá trị, vị trí sản phẩm |
| 3 | Ch.2 Ưu điểm & lợi ích (CŨ, di chuyển) | Canvas | Tiêu đề bắt đầu bằng `2. `, nội dung 10 ô giữ nguyên |
| 4 | Ch.3 Getting Started (MỚI) | Canvas | 3 bước cài từ `docs/notes/user-level-install.md` §1 |
| 5 | Ch.4 State machine + schema (MỚI) | Canvas | 7 phase + nhánh quick, khớp `PHASE_TABLE`; bảng 18 field state.json |
| 6 | Ch.5 Flow lane quick/full (CŨ, di chuyển) | Canvas | Tiêu đề bắt đầu bằng `5. ` |
| 7 | Ch.6 Ví dụ thực tế 1 request (MỚI) | Canvas | Dùng chính request `2026-08-11-cai-tdq-project-level` (có thật trong repo) |
| 8 | Ch.7 Sequence diagram (CŨ, di chuyển) | Canvas | Tiêu đề bắt đầu bằng `7. `, giữ 19 message đã đánh số |
| 9 | Ch.8 Kiến trúc & cấu trúc thư mục (MỚI) | Canvas | Liệt kê đúng 6 hook script, 7 script, 6 skill |
| 10 | Ch.9 Manifest & Dependency (CŨ, di chuyển) | Canvas | Tiêu đề bắt đầu bằng `9. ` |
| 11 | Ch.10 Nền tảng & Test/Dev (CŨ, di chuyển) | Canvas | Tiêu đề bắt đầu bằng `10. ` |
| 12 | Ch.11 Giới hạn đã biết (MỚI) | Canvas | ≥5 giới hạn, mỗi cái trích từ report/install-notes có thật |
| 13 | Ch.12 Troubleshooting / FAQ (MỚI) | Canvas | ≥5 cặp hỏi-đáp từ mục "Lưu ý an toàn" |
| 14 | Ch.13 Roadmap & Changelog (MỚI) | Canvas | Mốc 0.11.0/0.11.1/0.11.2 đúng ngày trong CHANGELOG.md |
| 15 | File scene | `docs/diagrams/tdq-workflow-product-doc.excalidraw` | File tồn tại, JSON parse được |
| 16 | File ảnh | `docs/diagrams/tdq-workflow-product-doc.png` | File tồn tại, kích thước > 100 KB |
| 17 | Script kiểm hình học | `scripts/check_canvas_layout.py` | Chạy exit 0 trên scene đã export |

## 3. Cách tiếp cận & lý do

- Chọn: **giữ nguyên 5 khối cũ, chỉ đổi tọa độ + tiền tố số chương**; 8 chương mới vẽ
  theo đúng style đang có (khung viền ngoài trong suốt + dải tiêu đề màu + các panel con
  màu pastel + text tự do, không dùng bound label trên khối lớn).
- Vì: user chọn 2A. Style hiện tại đã qua nhiều vòng sửa lỗi tràn chữ; vẽ lại từ đầu là
  rủi ro thuần túy. Thứ tự chương theo Diátaxis + chuẩn doc CLI (nguồn: diataxis.fr,
  document360.com/blog/cli-documentation, clig.dev — chi tiết
  `docs/tdq/research/2026-08-12-hoan-thien-doc-excalidraw.md`).
- Chọn: **mọi thay đổi hình học làm bằng delete + `batch_create_elements`**, không dùng
  `update_element` cho `x`/`y`/`width`/`height`/`text`.
- Vì: trong 2 lần thử ở các turn trước, `update_element` trả về "success" kèm version
  tăng nhưng `get_element` cho thấy thuộc tính KHÔNG đổi. Đây là lỗi đã tái hiện 2 lần
  trên đúng server này, không phải suy đoán.
- Chọn: **kiểm chồng lấn bằng script Python trên scene JSON**, không chỉ nhìn screenshot.
- Vì: screenshot ở mức zoom nhỏ không phát hiện được chồng lấn vài pixel; script so
  bounding box thì đo được bằng lệnh, đúng yêu cầu "PASS đo được".
- Đã loại: vẽ lại toàn bộ từ đầu — vì user chọn 2A và rủi ro mất chi tiết đã chuẩn.
- Đã loại: bố cục lưới poster — vì user chọn 3A, một cột dọc có thứ tự đọc rõ ràng.
- Đã loại: chia subagent vẽ song song — vì tranh chấp z-order trên một canvas dùng chung.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| excalidraw-skill | user | DÙNG | Toàn bộ thao tác vẽ, di chuyển, screenshot, export (T1–T16) |
| tdq-conventions | project | NỀN | Khung lane full đang chạy |
| tdq-spec | project | NỀN | Skill đang chạy để viết spec này |
| tdq-plan | project | NỀN | Sẽ chạy ngay sau khi spec được duyệt |
| tdq-build | project | NỀN | Sẽ chạy ở phase implement/qc/report |
| mem0-memory | user | DÙNG | Lưu 1 fact: `update_element` không đáng tin cho geometry/text trên server Excalidraw này |
| graphify | user | KHÔNG | khác lĩnh vực — không đổi file mã nguồn của sản phẩm |
| Đã xét 268 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service: BỎ — việc này không tạo runtime, chỉ vẽ canvas và export ảnh; ngoại lệ
  duy nhất là `scripts/check_canvas_layout.py` (script kiểm QC dùng một lần, in kết quả
  ra stdout kèm số liệu bounding box, không phải sản phẩm chạy nền).
- Không placeholder: mọi con số/tên file trên canvas phải trích từ repo thật. Cấm ghi
  "coming soon", "TBD", hay bịa mốc roadmap chưa có trong `CHANGELOG.md`.
- Mỗi thành phần có test chạy bằng một lệnh: `scripts/check_canvas_layout.py` có unit
  test riêng `tests/test_check_canvas_layout.py` (chạy `python3 -m pytest`).

## 5. Ràng buộc & rủi ro

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| `update_element` silent-fail khi đổi tọa độ 5 khối cũ | Khối cũ không di chuyển, document sai thứ tự | Delete + `batch_create_elements`; sau mỗi khối chạy `get_element` xác minh |
| Di chuyển khối cũ làm mất phần tử con (panel, mũi tên, lifeline) | Mất nội dung đã làm | Trước khi di chuyển: `export_scene` ra file backup; đối chiếu số phần tử trước/sau |
| Tràn chữ tiếng Việt (dấu rộng hơn ước lượng) | Chữ bị cắt | Hệ số `k ≈ 0.75` cho text có dấu, label ≤ 70% bề rộng ô, chèn `\n` thủ công |
| Element mới đè lên element cũ do z-order theo thứ tự tạo | Panel bị che | Tạo nền trước, nội dung sau; đã gặp lỗi này với `m-bg2` |
| Export ảnh cần tab trình duyệt mở | Lệnh export lỗi exit 4 | Kiểm `websocket_clients` qua `/health` trước, tự mở tab nếu = 0 |
| Canvas quá cao (13 chương × ~1.400px ≈ 18.000px) → PNG khổng lồ | File nặng, khó xem | Export PNG ở scale 1, nếu > 20 MB thì giảm còn scale 0.5 và ghi rõ trong report |

Không cần model AI, không cần download gói mới: `scripts/check_canvas_layout.py` chỉ
dùng `json` + `sys` của stdlib Python 3, giữ đúng nguyên tắc "0 package ngoài" của repo.

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Đủ 13 chương | `python3 scripts/check_canvas_layout.py docs/diagrams/tdq-workflow-product-doc.excalidraw --chapters` | In ra đúng 13 tiêu đề, số chương liên tục 1→13 |
| Q2 | Không chồng lấn giữa các chương | `python3 scripts/check_canvas_layout.py <scene> --overlap` | 0 cặp khung chương giao nhau; exit 0 |
| Q3 | Mọi phần tử nằm trong khung chương của nó | `python3 scripts/check_canvas_layout.py <scene> --contain` | 0 phần tử tràn ra ngoài khung cha; exit 0 |
| Q4 | Thứ tự dọc đúng số chương | `python3 scripts/check_canvas_layout.py <scene> --order` | y của chương n < y của chương n+1 với mọi n |
| Q5 | Mục lục khớp tiêu đề thật | `python3 scripts/check_canvas_layout.py <scene> --toc` | 13/13 dòng mục lục khớp chuỗi tiêu đề chương |
| Q6 | Không tràn chữ | `get_canvas_screenshot` từng chương rồi xem ảnh | Không thấy chữ bị cắt ở chương nào |
| Q7 | Số phần tử của 5 khối cũ giữ nguyên sau di chuyển | So `--count-by-prefix` giữa scene backup và scene mới | Chênh lệch = 0 cho mọi prefix cũ |
| Q8 | File export tồn tại | `ls -la docs/diagrams/` | Có cả `.excalidraw` và `.png`, PNG > 100 KB |
| Q9 | Script kiểm có test | `python3 -m pytest tests/test_check_canvas_layout.py -q` | Toàn bộ test PASS |
| Q10 | Không hồi quy test cũ | `python3 -m pytest -q` | Không có test nào chuyển từ pass sang fail |
| Q11 | Dữ kiện trên canvas khớp repo | Đối chiếu tay 4 điểm: số phase, số hook, số skill, version | 4/4 khớp `PHASE_TABLE`, `hooks/scripts/`, `skills/`, `plugin.json` |

DoD:
- 13 chương có mặt, xếp một cột dọc đúng thứ tự, đánh số liên tục 1→13
- Q1–Q11 đều PASS, có bằng chứng dán trong `docs/tdq/qc/2026-08-12-hoan-thien-doc-excalidraw.md`
- `docs/diagrams/` có cả `.excalidraw` và `.png`
- Không có dữ kiện nào trên canvas không truy được về một file trong repo

## 7. Câu hỏi còn mở

(Rỗng.)
