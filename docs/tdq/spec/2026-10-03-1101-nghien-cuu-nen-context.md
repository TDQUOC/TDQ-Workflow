# SPEC — Báo cáo nghiên cứu: nén context và rút thời gian máy của workflow

Ngày: 2026-10-03 · Bản: 1.0 · Brief: ../brief/2026-10-03-1101-nghien-cuu-nen-context.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: ĐÃ DUYỆT (2026-10-03, "Duyệt spec")

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

- Mục tiêu: một báo cáo cho user QUYẾT ĐỊNH hướng tối ưu tiếp theo — chỉ ra context và thời gian
  máy thực sự đi đâu, và đề xuất ít nhất 3 hướng, mỗi hướng có mức tiết kiệm đo hoặc ước lượng
  có nguồn, cái giá phải trả và mức áp dụng cho Codex.
- Trong phạm vi:
  - kiểm chéo mọi con số bên ngoài trước khi dùng (nguồn sơ cấp);
  - thử nghiệm trên bản sao tạm ngoài repo để đo mức tiết kiệm của các hướng về file luật;
  - ước lượng mức tiết kiệm của các hướng về hội thoại tích luỹ và trọn bộ test từ số đo transcript;
  - báo cáo + bảng đề xuất + thứ tự nên làm.
- NGOÀI phạm vi:
  - không sửa `skills/`, `hooks/`, `scripts/`, `tests/`, `agents/` — user chốt "chưa thay đổi gì";
  - thời gian chờ user duyệt không phải mục tiêu tối ưu (user chọn chỉ thời gian máy); hướng giảm
    cổng duyệt vẫn được đề xuất, kèm cái giá về kiểm soát;
  - không chạy runtime test, không gọi agent QC độc lập (mức `full`, không phải `ultra`).

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ (đã chạy) | 4 góc, file `docs/tdq/research/2026-10-03-1101-nghien-cuu-nen-context.md` |
| Đo nội bộ | CÓ (đã chạy) | transcript thật + tokenizer thật, file `…-do-noi-bo.md` |
| Vòng phạm vi | BỎ | user đã chốt đầu ra và ràng buộc |
| Interview chi tiết | CÓ | 6 câu, hết câu hỏi |
| Soát lỗi `code-review` / rút gọn `simplify` | BỎ | không có mã |
| QC độc lập (agent) | BỎ | mức `full` |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Bảng kiểm chéo số bên ngoài: mỗi con số dùng trong báo cáo → nguồn sơ cấp, khớp/không khớp | mục trong báo cáo | mọi số bên ngoài trong bảng đề xuất có một dòng ở bảng này |
| 2 | Kết quả thử nghiệm trên bản sao: token trước/sau cho từng hướng về file luật | mục trong báo cáo | mỗi số kèm lệnh chạy lại được |
| 3 | Bản đồ chi phí: context và thời gian máy đi đâu, xếp theo độ lớn | mục trong báo cáo | lấy từ `…-do-noi-bo.md`, có phương pháp |
| 4 | Bảng đề xuất ≥ 3 hướng: tiết kiệm (token, giây) · cái giá chất lượng/kiểm soát · công sức · rủi ro · Codex | mục trong báo cáo | đủ cột, mỗi số có nguồn hoặc lệnh |
| 5 | Thứ tự đề xuất làm + request tiếp theo nên mở | mục cuối báo cáo | có một khuyến nghị và lý do |
| 6 | Báo cáo | `docs/tdq/reports/2026-10-03-1101-nghien-cuu-nen-context.md` | doc_lint xanh |

## 2b. Ranh giới module

Không có mã. Một module tài liệu duy nhất.

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| bao-cao | `docs/tdq/reports/2026-10-03-1101-nghien-cuu-nen-context.md`, `docs/tdq/research/2026-10-03-1101-*.md` | không | 1–6 |

## 3. Cách tiếp cận & lý do

- Chọn: **xếp hướng theo nơi chi phí thật sự nằm**, không theo nơi dễ sửa nhất. Số đo nội bộ cho
  thấy file luật (sàn 53,6K) nhỏ so với context trung bình mỗi lần gọi (~491K, ~90% hội thoại tích
  luỹ), và trọn bộ test chiếm 31% thời gian máy. Nên bảng đề xuất phải phủ ít nhất ba nhóm:
  (a) hội thoại tích luỹ / cache; (b) thời gian test và vòng chạy; (c) bề mặt file luật và hook.
- Vì: tối ưu tiếp file luật — việc đã làm ở 0.54.0 (−10,7%) — chỉ chạm phần nhỏ của chi phí; báo
  cáo phải nói thẳng điều đó.
- Đã loại:
  - Đề xuất chỉ dựa vào số bên ngoài chưa kiểm chéo — vài con số trong file nghiên cứu khác điều
    đã biết (giá đọc cache 0,05×) hoặc chưa tự xác minh (hai bài arXiv 2605/2606).
  - Thử nghiệm trên chính repo — vi phạm ràng buộc "chưa thay đổi gì".

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake, tdq-spec, tdq-plan, tdq-build, tdq-conventions | plugin:tdq-workflow | NỀN | khung đang chạy |
| Đã xét 15 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service: BỎ — việc này không tạo hay sửa mã chạy được.
- Không placeholder, không số bịa: mọi con số có nguồn sơ cấp hoặc lệnh đo chạy lại được.
- Script đo tạm nằm ở `%TEMP%`, xoá sau khi dùng; không có file mới nào trong `scripts/`.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ: không chạm dòng nào — việc này không sửa mã hay luật.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Số bên ngoài sai hoặc bịa (lỗi của trợ lý tìm kiếm) | đề xuất dựa trên số sai | QC kiểm chéo từng số với nguồn sơ cấp; không xác minh được → ghi rõ, không dùng làm căn cứ |
| Số đo transcript lệch do cách cắt (chờ vs máy) | ước lượng tiết kiệm thời gian sai | ghi phương pháp; báo khoảng thay vì một điểm khi phương pháp nhạy |
| Thử nghiệm trên bản sao vô tình ghi vào repo | vi phạm ràng buộc | kiểm `git status` sạch phần `skills/ hooks/ scripts/` ở QC |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |
|---|---|---|---|---|
| Q1 | Đủ số hướng | bảng đề xuất có ít nhất 3 hướng, phủ 3 nhóm (a) (b) (c) | đã có 3 nhóm chi phí đo được: hội thoại ~491K/lần gọi, test 31% thời gian máy, file luật 53,6K | gộp hướng nhỏ thành một dòng "khác"; không bịa hướng cho đủ số |
| Q2 | Mỗi hướng có số | mỗi hướng có mức tiết kiệm (token hoặc giây) với nguồn hoặc lệnh đo | 10 số nội bộ đã có phương pháp trong `…-do-noi-bo.md` | ghi "chưa đo được" kèm cách đo, hướng đó xếp sau |
| Q3 | Số bên ngoài đã kiểm chéo | mọi số bên ngoài dùng làm căn cứ có dòng trong bảng kiểm chéo, ghi khớp/không khớp | 10 số trong bản tóm tắt nghiên cứu, ít nhất 3 cần xác minh | số không xác minh được → bỏ khỏi căn cứ, ghi lý do |
| Q4 | Thử nghiệm chạy lại được | mỗi số token trước/sau có lệnh chạy lại trên bản sao | tokenizer thật có sẵn ở `.venv-tokens` | báo số kèm phương pháp thủ công |
| Q5 | Workflow không bị sửa | `git diff main -- skills hooks scripts tests agents` rỗng | — | — |
| Q6 | Có khuyến nghị | báo cáo kết thúc bằng thứ tự nên làm và request tiếp theo | — | — |
| Q7 | Lint | `doc_lint` trên báo cáo, spec, plan exit 0 | spec này qua R14 trước khi trình | sửa câu theo luật lint |

DoD: 6 đầu ra ở §2 có thật · Q1–Q7 PASS · working log mọi lượt · không thay đổi nào trong
`skills/ hooks/ scripts/ tests/ agents/`.

## 7. Câu hỏi còn mở

(rỗng)
