# SPEC — công cụ sơ đồ giải thuật: script chạy được, phase bắt buộc trước plan, trang HTML hai lớp

Ngày: 2026-08-23 · Bản: 1.1 · Brief: ../brief/2026-08-23-1623-mindmap-html-hai-lop.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

Đổi so với bản 1.0: đơn vị của một sơ đồ chuyển từ REQUEST sang FEATURE · một request được phép
mang nhiều sơ đồ, duyệt từng cái một · file sơ đồ khai được quan hệ phụ thuộc giữa các feature ·
lane `quick` cũng bắt buộc có sơ đồ · feature đã có sơ đồ thì request sau vào chế độ cập nhật.

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

- Mục tiêu: biến lớp sơ đồ giải thuật từ tài liệu đề xuất thành thứ chạy được, và đặt nó làm
  DÀN Ý bắt buộc của mọi feature — mỗi feature một sơ đồ sống, duyệt trước rồi mới triển khai,
  quan hệ phụ thuộc giữa các feature khai rõ, và một trang HTML hai lớp gom cả project.
  Đo xong bằng: chạy được cả năm lệnh trên file mẫu, `tdq_state.py` từ chối sang `plan` khi còn
  sơ đồ chưa duyệt, và trang tổng mở ra thấy đủ hai lớp cùng lưới phụ thuộc.
- Trong phạm vi:
  - File mới `scripts/tdq_mindmap.py` với năm lệnh `sinh`, `kiem`, `doi-chieu`, `xem`, `lien-he`.
  - File mới `scripts/mindmap_render.py` dựng HTML: lớp nghiệp vụ, lớp chi tiết, trang tổng.
  - **Đơn vị sơ đồ là FEATURE**, không phải request: `docs/tdq/mind-map/<feature>.md` là bản
    sống duy nhất của feature đó, nhiều request lần lượt sửa nó.
  - **Nhiều sơ đồ trong một request**: state giữ một DANH SÁCH sơ đồ, duyệt từng cái một.
  - **Quan hệ phụ thuộc** giữa các feature: dòng `@phụ-thuộc:` khai tay trong file sơ đồ.
  - **Chế độ cập nhật**: gọi `sinh` trên feature đã có thì không lỗi, mà mở bản hiện tại ra sửa;
    lúc trình cho user phải nói rõ feature đã có sẵn và sau cập nhật sơ đồ sẽ thành thế nào.
  - Phase `diagram` và gate `diagram_approved` trong `scripts/tdq_state.py`, áp cho cả hai lane.
  - Luật khuôn file sơ đồ trong `scripts/doc_lint.py`, cắm vào nhánh `is_output`.
  - Skill mới `tdq-diagram`, mang khuôn mẫu chi tiết; sửa `tdq-intake` (kể cả nhánh lane
    `quick`) và `tdq-plan` để dẫn vào.
  - Test cho từng module trên.
- NGOÀI phạm vi:
  - Dựng sơ đồ ngược từ code có sẵn cho các tính năng đã viết xong — user chưa yêu cầu.
  - Dạng `sequenceDiagram` và việc đóng khung client/server — đã thử ở request
    `2026-08-23-1424-so-do-sequence-client-server` và user chốt bỏ vì khó nhìn.
  - Tầng `nhỏ` vẽ sơ đồ — tầng này theo định nghĩa không đổi hành vi sản phẩm nên không có
    luồng nào để vẽ (user chốt câu 9).
  - Bản so sánh chi tiết giữa hai phiên bản sơ đồ (diff từng bước, đánh dấu thêm/sửa/xoá) —
    user chốt câu 11 là không cần; chỉ cần báo feature đã có và trình bản sau cập nhật.
  - Luật máy bắt tên hàm phải rõ nghĩa — user chốt câu 6 là giữ ở mức con người.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | mọi ẩn số nằm trong repo, đã tự đọc `graph.json` để trả lời |
| Interview | CÓ | đã chạy ba vòng, mười hai câu, chốt hết |
| Vòng hỏi phạm vi | BỎ | user tự khai phạm vi thành ba hạng mục gọi tên rõ |
| spec | CÓ | khung bắt buộc lane full |
| plan | CÓ | khung bắt buộc lane full |
| mode | CÓ | request đụng code chạy được, user chọn cách chạy |
| implement | CÓ | khung bắt buộc |
| qc | CÓ | request đầu tiên của loạt này sinh code chạy được |
| QC độc lập (agent) | BỎ | user chưa yêu cầu dùng sub-agent; QC tự chạy, nhưng mọi dòng DoD phải chạy được thuật toán chứ không `grep` tên biến |
| Review sâu (`tdq-reviewer`) | BỎ | user chưa yêu cầu |
| report | CÓ | khung bắt buộc |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Script năm lệnh | `scripts/tdq_mindmap.py` | cả năm lệnh chạy trên file mẫu và trả mã thoát đúng bảng ở §3 |
| 2 | Bộ dựng HTML | `scripts/mindmap_render.py` | dựng ra file HTML tự chứa, không tham chiếu tài nguyên ngoài |
| 3 | Trang một feature, hai lớp | `docs/tdq/mind-map/<feature>.html` | trang chứa cả lớp nghiệp vụ lẫn lớp chi tiết, chuyển qua lại được |
| 4 | Trang tổng: nhóm + lưới phụ thuộc | `docs/tdq/mind-map/index.html` | mọi feature trong thư mục đều có mặt, gom theo `@nhánh`, và vẽ được mũi tên phụ thuộc giữa các feature |
| 5 | Phase `diagram` + gate danh sách | `scripts/tdq_state.py` | `set phase=plan` bị từ chối khi còn sơ đồ trong danh sách chưa duyệt |
| 6 | Duyệt từng sơ đồ một | `scripts/tdq_state.py` | duyệt một sơ đồ không làm các sơ đồ còn lại thành đã duyệt |
| 7 | Luật khuôn file sơ đồ | `scripts/doc_lint.py` | file sơ đồ sai khuôn bị báo vi phạm kèm mã luật |
| 8 | Skill `tdq-diagram` | `skills/tdq-diagram/` | skill mang khuôn mẫu đầy đủ, người đọc không phải đoán bước nào |
| 9 | Ba chỗ sửa để dẫn vào | `skills/tdq-intake/SKILL.md`, `skills/tdq-intake/references/quick-lane.md`, `skills/tdq-plan/SKILL.md` | mỗi file nêu phase `diagram` ở đúng chỗ nó chen vào, kể cả nhánh lane `quick` |
| 10 | Test từng module | `tests/` | mỗi module ở §2b có tệp test riêng, chạy bằng một lệnh |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| `nhan-doc` | `scripts/tdq_mindmap.py` | không | 1 |
| `dung-trang` | `scripts/mindmap_render.py` | `nhan-doc` | 2, 3, 4 |
| `phase-gate` | `scripts/tdq_state.py` | không | 5, 6 |
| `luat-lint` | `scripts/doc_lint.py` | không | 7 |
| `skill` | `skills/tdq-diagram/`, `skills/tdq-intake/SKILL.md`, `skills/tdq-intake/references/quick-lane.md`, `skills/tdq-plan/SKILL.md` | `phase-gate` | 8, 9 |

Bốn module đầu không giao đường dẫn nào. Module `skill` chỉ chứa văn bản, không chứa mã chạy.
Mỗi module mang một tệp test riêng dưới `tests/`; tên từng tệp chốt ở phase `plan`, không chốt
ở đây, vì tên tệp đổi được mà ý định không đổi.

## 3. Cách tiếp cận & lý do

- Chọn: **một nguồn sự thật viết tay MỖI FEATURE, hai lớp trình bày sinh ra từ hai nguồn khác nhau.**
  - Lớp nghiệp vụ đọc từ file `docs/tdq/mind-map/<feature>.md` do người viết và user duyệt.
  - Lớp chi tiết đọc từ `graphify-out/graph.json`, không ai viết tay, không ai duyệt, dựng lại
    mỗi lần chạy.
- Vì: hai lớp khác nhau về BẢN CHẤT NGUỒN, không chỉ khác độ chi tiết. Lớp 1 là ý định con
  người tuyên bố, phải duyệt. Lớp 2 là thứ máy quan sát được từ code, không cần duyệt và không
  bao giờ cũ vì nó dựng lại. Trộn hai bản chất vào một file viết tay thì cả hai cùng hỏng: lớp
  chi tiết lệch ngay lần refactor đầu, kéo theo cổng chặn `qc` đỏ vì lý do không có thật.
- **Khoá theo feature, không khoá theo request.** Request là đơn vị của công việc: mở ra rồi
  đóng lại. Feature sống cùng project và bị nhiều request sửa dần. Khoá theo request thì sửa
  đăng nhập ba lần sẽ có ba file rời rạc, không file nào là "sơ đồ đăng nhập hiện tại". Khoá
  theo feature thì `docs/tdq/mind-map/dang-nhap.md` là bản sống duy nhất, và câu hỏi "hiện giờ
  đăng nhập chạy thế nào" luôn có đúng một câu trả lời.
- **Một request nhiều sơ đồ, duyệt từng cái.** Một spec thường cấu tạo từ nhiều luồng feature.
  State giữ một danh sách sơ đồ của request; mỗi phần tử mang đường dẫn, trạng thái duyệt và
  câu duyệt của user. Gate sang `plan` chỉ mở khi danh sách không rỗng VÀ mọi phần tử đã duyệt.
  Duyệt một cái không đụng đến các cái còn lại.
- **Phụ thuộc khai tay.** File sơ đồ mang dòng `@phụ-thuộc: <feature> · <lý do một câu>`, lặp
  được nhiều dòng. Ví dụ thật của user: `mua-hang.md` khai `@phụ-thuộc: dang-nhap · cần token
  phiên do đăng nhập phát ra`. Quan hệ nghiệp vụ là thứ con người biết; máy nhìn `graph.json`
  chỉ thấy hai feature dùng chung một hàm, không phân biệt được "phụ thuộc" với "trùng tiện ích".
- **Cập nhật một feature đã có.** Lệnh `sinh` gặp feature đã có file thì KHÔNG báo lỗi: nó mở
  bản hiện tại ra để sửa và trả mã thoát riêng để người gọi biết đây là cập nhật chứ không phải
  tạo mới. Lúc trình cho user, skill phải nói rõ theo khuôn: feature này đã có sơ đồ rồi, sau
  cập nhật của request này nó sẽ thành như sau — rồi trình bản mới nguyên vẹn để duyệt lại.
- Dữ liệu cho lớp chi tiết đã xác minh có thật: `graphify-out/graph.json` để cạnh ở khoá `links`,
  992 cạnh `calls` cộng 62 cạnh `indirect_call`, và 1054/1054 cạnh gọi mang `source_location` là
  số dòng nơi gọi. Nhờ vậy các lời gọi trong một hàm sắp được theo thứ tự dòng.
- Giải thích cho mỗi hàm ở lớp chi tiết lấy từ dòng đầu docstring, đọc bằng `ast` của stdlib.
  Đo trước: 655 hàm trong `scripts/` và `hooks/`, 392 hàm có docstring. Hàm không có docstring
  in trơ tên hàm và tô nhạt trên trang.
- Năm lệnh và mã thoát:

| Lệnh | Việc | Mã thoát |
|---|---|---|
| `sinh <feature>` | tạo file sơ đồ mới, hoặc mở bản có sẵn để cập nhật | 0 tạo mới · 3 feature đã có, mở chế độ cập nhật · 2 slug sai khuôn |
| `kiem <file>` | kiểm khuôn, in dòng vi phạm kèm mã luật | 0 sạch · 1 có vi phạm · 2 không đọc được file |
| `doi-chieu <file>` | đối chiếu cặp `file::hàm` với đồ thị | 0 khớp hết · 1 có cặp lệch · 3 không đọc được đồ thị |
| `lien-he` | dựng lưới phụ thuộc từ mọi dòng `@phụ-thuộc` trong thư mục | 0 lưới hợp lệ · 1 trỏ tới feature không tồn tại · 3 có vòng lặp phụ thuộc |
| `xem <file>` | dựng trang HTML hai lớp; `--tong` dựng trang tổng | 0 ghi xong · 1 sơ đồ sai khuôn · 2 không ghi được file |

- Đã loại: **lớp chi tiết viết tay** — vì một luồng đăng nhập đi qua vài chục hàm, và nó lệch
  ngay lần refactor đầu tiên; người dùng sẽ học cách đi vòng qua cổng chặn thay vì sửa sơ đồ.
- Đã loại: **suy phụ thuộc bằng máy từ `graph.json`** — dùng chung một hàm tiện ích không phải
  là phụ thuộc nghiệp vụ; máy suy ra sẽ đầy quan hệ giả, người đọc mất lòng tin vào lưới.
- Đã loại: **chặn ở hook** — vì `docs/kien-truc.md` mục `Đã chốt` ngày 2026-07-29 cấm hook trả
  `deny` vì lý do chưa duyệt. Chặn đặt ở `tdq_state.py`, cùng khuôn với `_chan_worktree_con_mo`.
- Đã loại: **luật máy bắt tên hàm phải rõ nghĩa** — vì không có phép đo nào chấm được một cái
  tên là rõ hay tối; máy chỉ đếm được hàm có docstring hay không.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `tdq-intake` | plugin:tdq-workflow | NỀN | skill khung đang chạy phase analyze |
| `tdq-spec` | plugin:tdq-workflow | NỀN | skill khung viết chính file này |
| `tdq-plan` | plugin:tdq-workflow | NỀN | skill khung viết plan ở bước sau |
| `tdq-build` | plugin:tdq-workflow | NỀN | skill khung chạy implement, qc, report |
| `tdq-conventions` | plugin:tdq-workflow | NỀN | luật ngôn ngữ, working log, khối trình bày |
| `artifact-diagramming` | built-in | DÙNG | đầu ra 2, 3 và 4 — luật dựng SVG tự chứa, nhãn trên mũi tên phụ thuộc, một hình một luận điểm |
| `artifact-design` | built-in | DÙNG | đầu ra 3 và 4 — luật màu theo token, hai theme, bảng tràn phải cuộn trong khung riêng |
| `mem0-memory` | project | DÙNG | ghi lại kết luận hai lớp và luật khoá-theo-feature sau khi làm xong |
| Đã xét 213 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: timestamp, đủ chi tiết debug, tắt hoặc giảm được qua config. Áp cho
  cả `scripts/tdq_mindmap.py` lẫn `scripts/mindmap_render.py`, cùng khuôn log của các script
  `scripts/` sẵn có.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md`, và bám rule
  ngôn ngữ trong `skills/tdq-build/references/rules/`.
- Chú thích, docstring và mọi chuỗi máy in ra trong hai file script mới viết TIẾNG ANH, theo
  dòng chốt ngày 2026-08-22 của `docs/kien-truc.md`; `scripts/i18n_check.py` gác việc này.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ, chép từ `docs/kien-truc.md`:

- "Chỉ `scripts/tdq_state.py` được ghi `docs/tdq/state.json`; mọi nơi khác chỉ đọc qua CLI" —
  việc này chạm ở `scripts/tdq_mindmap.py`, nên script đó CHỈ đọc state, không bao giờ ghi.
- "File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/`" — việc này chạm ở hai file mới,
  cả hai đặt trong `scripts/`.
- "hook chỉ nhắc và kiểm bằng hiệu ứng thật, không trả `deny` vì lý do chưa duyệt" (chốt
  2026-07-29) — việc này chạm ở gate của đầu ra 5, nên chặn đặt trong `tdq_state.py`.
- "`skills/` chỉ được nhắc tên lệnh của `scripts/`, cấm chép nội dung script vào skill" — việc
  này chạm ở skill `tdq-diagram`, nên skill nêu tên lệnh và khuôn file, không chép mã.
- Ngôn ngữ ba tầng (chốt 2026-08-22) — việc này chạm ở mọi file mới, đã ghi ở §4.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Thứ tự lời gọi theo số dòng là thứ tự VIẾT, không phải thứ tự CHẠY | người đọc tưởng lớp chi tiết là vết chạy thật, tin sai vào rẽ nhánh và vòng lặp | trang HTML in một câu ngay đầu lớp chi tiết nói rõ đây là thứ tự viết; nhiều lời gọi trùng một dòng thì gom thành một hàng |
| Đồ thị cũ hơn code | lớp chi tiết vẽ theo code đã đổi | `doi-chieu` và `xem` đọc `built_at_commit`, khác `HEAD` thì in cảnh báo; không tự chạy lại graphify |
| Phase mới chen vào máy trạng thái đang chạy | request đang mở dở bị kẹt vì thiếu danh sách sơ đồ | state cũ thiếu khoá danh sách được coi là đã duyệt, chỉ request khởi tạo sau khi có phase mới mới bị chặn |
| Chặn cứng làm người dùng kẹt khi sơ đồ chưa xong | không sang được `plan`, mất việc đang làm | chặn không xoá và không bắt vẽ lại file sơ đồ; thông báo chặn liệt kê ĐÍCH DANH sơ đồ nào chưa duyệt và đường dẫn để sửa tiếp |
| Vòng lặp phụ thuộc giữa các feature | trang tổng vẽ vòng vô tận, người đọc không tìm được điểm bắt đầu | `lien-he` phát hiện vòng và trả mã thoát riêng, in đúng chuỗi feature tạo thành vòng |
| Dòng `@phụ-thuộc` trỏ tới feature chưa có sơ đồ | lưới thủng, người đọc tưởng thiếu sót | `lien-he` báo tên feature bị thiếu; trang tổng vẫn vẽ ô đó nhưng đánh dấu là chưa có sơ đồ |
| Lane `quick` giờ cũng phải vẽ sơ đồ | lane nhanh mất tính nhanh, người dùng bỏ qua lane | ở lane `quick` sơ đồ chỉ cần lớp nghiệp vụ, không bắt `doi-chieu` với đồ thị; tầng `nhỏ` vẫn miễn hoàn toàn |
| Số hàm ở lớp chi tiết nở ra quá lớn | trang HTML mất tác dụng vì quá dài | mặc định đi sâu 1 tầng, mở thêm bằng cờ `--sau <N>`; một bước in quá 20 hàm thì thu gọn và cho bấm mở |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Năm lệnh chạy được | mỗi lệnh chạy trên file mẫu và trả đúng mã thoát ghi ở §3 |
| Q2 | Lọc node hàm đúng trường | phép lọc chạy thật trên `graph.json` ra đúng số node `file_type` bằng `code`, không lẫn node tài liệu |
| Q3 | Lớp chi tiết có thứ tự | các lời gọi của một hàm hiện theo thứ tự số dòng tăng dần |
| Q4 | Giải thích hàm lấy từ docstring | hàm có docstring hiện dòng đầu của nó; hàm không có hiện trơ tên và được tô nhạt |
| Q5 | Trang HTML tự chứa | trang không tham chiếu tài nguyên ngoài nào |
| Q6 | Trang có đủ hai lớp | mở trang thấy cả lớp nghiệp vụ lẫn lớp chi tiết, chuyển qua lại được |
| Q7 | Trang tổng gom nhóm đúng | mọi feature trong thư mục có mặt, gom theo dòng `@nhánh`, xếp từ nhánh tổng xuống trang nghiệp vụ |
| Q8 | Trang tổng vẽ lưới phụ thuộc | mũi tên nối đúng cặp feature khai ở `@phụ-thuộc`, mỗi mũi tên mang lý do khai kèm |
| Q9 | Bắt vòng lặp phụ thuộc | thư mục có vòng phụ thuộc thì `lien-he` trả mã thoát riêng và in đúng chuỗi feature tạo thành vòng |
| Q10 | Bắt phụ thuộc trỏ hụt | dòng `@phụ-thuộc` trỏ tới feature không có file thì bị báo đích danh |
| Q11 | Gate chặn theo danh sách | còn một sơ đồ chưa duyệt thì `set phase=plan` bị từ chối, và thông báo gọi tên đúng sơ đồ đó |
| Q12 | Duyệt từng cái độc lập | duyệt một sơ đồ không làm sơ đồ khác trong cùng request thành đã duyệt |
| Q13 | Gate chặn cả khi danh sách rỗng | request không có sơ đồ nào thì không sang `plan` được |
| Q14 | Gate không phá state cũ | state không có khoá danh sách sơ đồ vẫn sang `plan` được |
| Q15 | Chặn không mất dữ liệu | sau khi bị chặn, file sơ đồ còn nguyên nội dung và sửa tiếp được |
| Q16 | Chế độ cập nhật | gọi `sinh` trên feature đã có file thì không lỗi, không ghi đè nội dung cũ, và trả mã thoát báo là cập nhật |
| Q17 | Luật lint chạy đúng nhánh | file sơ đồ sai khuôn bị báo vi phạm kèm mã luật; luật cắm ở nhánh `is_output` |
| Q18 | Khuôn có hai dòng bắt buộc | file sơ đồ thiếu dòng `@nhánh` bị `kiem` báo vi phạm; dòng `@phụ-thuộc` sai khuôn cũng bị báo |
| Q19 | Skill mang khuôn mẫu chi tiết | skill có khuôn file sơ đồ đầy đủ, các bước phải làm, và khuôn câu trình bản cập nhật cho user |
| Q20 | Ba chỗ cũ dẫn vào phase mới | mỗi file nêu phase `diagram` ở đúng chỗ nó chen vào, kể cả nhánh lane `quick` |
| Q21 | Test từng module | mỗi module ở §2b có tệp test riêng và toàn bộ chạy xanh |
| Q22 | Log service bật mặc định | hai script mới in log có timestamp và tắt được qua config |
| Q23 | Luật ngôn ngữ | hai file script mới qua được phép kiểm i18n |

DoD: đủ 23 hạng mục trên PASS · toàn bộ test của repo chạy xanh một lượt · file mẫu
`docs/tdq/mind-map/dang-nhap.md` được nâng lên khuôn mới và dựng ra trang HTML hai lớp mở xem
được · một feature thứ hai `docs/tdq/mind-map/mua-hang.md` khai `@phụ-thuộc: dang-nhap` để lưới
phụ thuộc có ít nhất một cạnh thật · trang tổng dựng ra từ chính thư mục đó.

## 7. Câu hỏi còn mở

(Rỗng.)
