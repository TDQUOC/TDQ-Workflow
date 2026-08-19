# SPEC — hướng A hybrid: luật lý luận tiếng Anh, khuôn user-facing tiếng Việt

Ngày: 2026-08-19 · Bản: 1.0 · Brief: ../brief/2026-08-19-1616-huong-a-dich-hybrid.md · Lane: full
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

- Mục tiêu: viết lại bộ skill `tdq-*` theo kiểu hybrid — phần luật lý luận bằng tiếng
  Anh, phần khuôn user-facing và câu khai báo ngôn ngữ đầu ra giữ tiếng Việt — sao cho
  100% điểm neo luật còn hiệu lực, gate ngôn ngữ đầu ra xanh, và tổng token bộ skill
  giảm ít nhất 30%.
- Trong phạm vi: cả 6 skill `tdq-*` và toàn bộ `references/` của chúng.
- Trong phạm vi: dựng gate đo ngôn ngữ đầu ra (điều kiện tiền đề b).
- Trong phạm vi: dựng bảng phân loại ranh giới luật-lý-luận vs khuôn-user-facing cho
  toàn bộ 329 điểm neo `L###` (điều kiện tiền đề a).
- Trong phạm vi: dựng lại lưới khoá để nó sống sót qua bản viết lại.
- NGOÀI phạm vi: skill ngoài `tdq-*` (`mem0-memory`, skill của plugin khác).
- NGOÀI phạm vi: hướng E (router), và mọi thay đổi `hooks/` trừ khi lưới khoá đòi.
- NGOÀI phạm vi: đọc transcript trong hook — giữ nguyên quyết định cũ.
- NGOÀI phạm vi: mặt "chỉ cần chạy được" mà vòng scope loại: user chọn cả bốn mặt chất
  lượng, nên không có mặt nào bị cắt cho nhanh.

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | audit đã ba vòng, có sẵn file research 2026-08-19-0029 |
| Vòng scope | CÓ | đã chạy, user chốt bốn mặt và phạm vi toàn bộ |
| Interview chi tiết | CÓ | đã chạy năm câu, hết chỗ mơ hồ |
| spec → plan → implement | CÓ | khung bất biến |
| QC độc lập bằng agent | BỎ | cấu hình phiên: không gọi subagent trừ khi user yêu cầu |
| Review sâu `tdq-reviewer` | BỎ | cùng lý do trên |
| Điểm chốt giữa chừng | CÓ | hết phase 2 trình số đo, chờ user quyết đi hay dừng |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Rule ngôn ngữ đầu ra trong linter | `scripts/doc_lint.py` | bắt được file lẫn tiếng Anh, không báo oan trên mọi file sinh ra hiện có |
| 2 | Bảng phân loại 329 điểm neo | `docs/tdq/audit/ranh-gioi-luat.md` | mỗi mã `L###` đúng một nhãn, phủ hết 329 mã |
| 3 | Script gợi ý nhãn cho từng điểm neo | `scripts/luat_phan_loai.py` | chạy ra bảng nháp, có log bật mặc định |
| 4 | Lưới khoá sống qua bản viết lại | `docs/tdq/audit/luat-hien-co.md` | mỗi điểm neo có neo bản mới; xoá một luật khỏi skill thì lưới nêu đúng mã |
| 5 | Bộ skill hybrid | `skills/tdq-*/**` | luật lý luận tiếng Anh, khuôn user-facing tiếng Việt, không khối nào trộn |
| 6 | Báo cáo đo trước/sau | `docs/tdq/audit/do-hybrid.md` | có token từng file trước và sau, đo bằng tokenizer thật |
| 7 | Hai bản portable đồng bộ | `portable_claude/**`, `portable_codex/**` | sinh lại từ nguồn, nội dung khớp ba bản |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| M1 gate ngôn ngữ | `scripts/doc_lint.py` | không | 1 |
| M2 phân loại ranh giới | `scripts/luat_phan_loai.py`, `docs/tdq/audit/ranh-gioi-luat.md` | không | 2, 3 |
| M3 lưới khoá song ngữ | `docs/tdq/audit/luat-hien-co.md` | M2 | 4 |
| M4 viết lại bộ skill | `skills/tdq-build`, `skills/tdq-intake`, `skills/tdq-spec`, `skills/tdq-plan`, `skills/tdq-conventions`, `skills/tdq-status` | M3 | 5 |
| M5 đo và đồng bộ | `docs/tdq/audit/do-hybrid.md`, `portable_claude`, `portable_codex` | M4 | 6, 7 |

Mỗi module có test riêng nằm trong thư mục test của repo, đặt tên theo module. Đường dẫn
cụ thể của từng file test ghi ở plan, không ghi ở spec — luật R11 của linter.

## 3. Cách tiếp cận & lý do

- Chọn: tách theo LOẠI nội dung. Luật lý luận và định dạng phức tạp viết lại bằng tiếng
  Anh; khuôn user-facing, ví dụ few-shot, câu khai báo ngôn ngữ đầu ra giữ tiếng Việt và
  nằm trong khối riêng.
- Vì: audit vòng 2026-08-19 (2) dẫn nguồn cho cây quyết định này, và nêu rõ "dịch nguyên
  prompt" cho kết quả tệ hơn viết lại từ đầu.
- Chọn: làm hai điều kiện tiền đề TRƯỚC khi động vào chữ của skill, trong cùng request,
  có điểm chốt đi-hay-dừng sau khi điều kiện xong.
- Vì: lưới khoá hiện hành neo vào 40 ký tự đầu của chính câu tiếng Việt. Viết lại là 329
  điểm neo đứt một lượt, lưới an toàn chết đúng lúc cần nhất.
- Đã loại: dịch nguyên khối cả file (hướng A gốc) — xoá ranh giới hai loại nội dung và
  có nguồn nói kết quả tệ hơn.
- Đã loại: gate ngôn ngữ soi chữ model in ra chat — phải mở lại quyết định "hook không
  đọc transcript", vốn có lịch sử chặn nhầm ở bản 0.1.8.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | khung request đang chạy |
| tdq-spec | plugin:tdq-workflow | NỀN | khung request đang chạy |
| tdq-plan | plugin:tdq-workflow | NỀN | khung request đang chạy |
| tdq-build | plugin:tdq-workflow | NỀN | khung request đang chạy |
| tdq-conventions | plugin:tdq-workflow | DÙNG | vừa là luật nền vừa là đối tượng bị viết lại ở M4 |
| mem0-memory | user | DÙNG | quyết định kiến trúc, tra trước và ghi lại sau khi chốt |
| Đã xét 279 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: `scripts/luat_phan_loai.py` in log có timestamp, tắt được
  qua biến môi trường như các script cùng thư mục.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code viết ra bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md`,
  và bám rule ngôn ngữ trong `skills/tdq-build/references/rules/`.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`):

- "File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/`" — việc này chạm ở
  `scripts/luat_phan_loai.py`.
- "`skills/` chỉ được nhắc tên lệnh của `scripts/`, cấm chép nội dung script vào skill"
  — việc này chạm ở M4 khi viết lại toàn bộ skill.
- "`portable_claude/`, `portable_codex/` SINH bằng `scripts/build_portable.py`, không sửa
  tay" — việc này chạm ở M5.
- "`scripts/` không được import `hooks/`" — việc này chạm ở M1 khi thêm rule vào linter.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Lưới khoá chỉ chứng minh câu TỒN TẠI, không chứng minh NGHĨA còn nguyên | luật đổi nghĩa mà máy vẫn xanh | người soát từng điểm neo, ghi nhãn và ghi câu tương ứng vào bảng M3 |
| Không có phép đo tự động cho việc model tuân thủ bản tiếng Anh y như bản Việt | hỏng hành vi mà không ai thấy | điểm chốt đi-hay-dừng sau M3; lùi bằng git; giữ nguyên `hooks/` để hàng rào cứng không đổi |
| Gate ngôn ngữ báo oan trên đoạn trích tiếng Anh hợp lệ (nguyên văn user, output test) | lint đỏ liên miên rồi bị tắt | rule bỏ qua khối mã, bảng định danh, và đoạn đã đánh dấu trích dẫn |
| Dịch xong, 6 mô tả tiếng Việt cuối cùng của kho skill thành tiếng Anh | router lexical của hướng E mất phần đang chạy được | ghi vào báo cáo đo; hướng E vốn đã khuyến nghị chưa làm |
| Phạm vi lớn, một request ba phase | trôi việc, mệt cổng duyệt | ranh giới module ở §2b cắt sẵn; điểm chốt sau M3 |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Rule ngôn ngữ bắt đúng | file sinh ra viết lẫn tiếng Anh thì lint đỏ và nêu đúng dòng |
| Q2 | Rule ngôn ngữ không báo oan | chạy trên mọi file sinh ra hiện có, không có báo cáo sai nào |
| Q3 | Bảng phân loại phủ đủ | mỗi mã trong 329 mã có đúng một nhãn, không mã nào thiếu hoặc trùng |
| Q4 | Lưới khoá không rỗng | xoá thử một luật khỏi skill thì lưới đỏ và nêu đúng mã đó |
| Q5 | Điểm neo còn hiệu lực | 100% mã `L###` có câu tương ứng trong bản viết lại |
| Q6 | Ngôn ngữ đúng chỗ | khuôn user-facing còn tiếng Việt, không khối nào trộn hai loại |
| Q7 | Tiết kiệm token | tổng token bộ skill giảm ít nhất 30%, đo bằng tokenizer thật |
| Q8 | Ba bản đồng bộ | nội dung `skills/` và hai bản portable khớp nhau |
| Q9 | Không nới lỏng lưới cũ | không test nào bị tắt, bị đánh dấu bỏ qua, hay bị hạ ngưỡng |

DoD: cả chín hạng mục PASS; báo cáo đo trước/sau có số thật; hai bản portable sinh lại
từ nguồn; nếu bất kỳ điều kiện nào trong Q5, Q6, Q7 trượt thì lùi git và KHÔNG giữ bản
viết lại.

## 7. Câu hỏi còn mở

(rỗng)
