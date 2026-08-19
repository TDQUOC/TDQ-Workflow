# Clean code — 5 nguyên tắc SOLID

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Clean code ở bộ workflow này KHÔNG phải một cổng hỏi và KHÔNG phải một lượt chạy linter
cuối request. Nó là hành vi thường trực: mỗi lần viết hay sửa code, tổ chức project,
script, hàm và class cho sạch nhất có thể, bám 5 nguyên tắc SOLID.

## Mục lục

- Nguồn
- Khi nào áp dụng
- Làm gì
- Tự kiểm

## Nguồn

- Wikipedia SOLID — https://en.wikipedia.org/wiki/SOLID — Robert C. Martin nêu các nguyên
  tắc trong bài *Design Principles and Design Patterns* (2000); từ viết tắt do Michael
  Feathers đặt khoảng 2004.
- Slide CSCE 315, Texas A&M —
  https://people.engr.tamu.edu/choe/choe/courses/12summer/315/lectures/slide23.pdf —
  SOLID là "a set of principles for object-oriented design (with focus on designing the
  classes)".
- Real Python — https://realpython.com/solid-principles-python — phạm vi áp dụng mà tác
  giả nêu là "when you're writing object-oriented code".
- DEV, *Do the SOLID principles apply to Functional Programming?* —
  https://dev.to/patferraggi/do-the-solid-principles-apply-to-functional-programming-56lm
  — bản đọc theo hàm và module cho SRP, OCP, ISP, DIP.
- DEV, *A Pythonic Guide to SOLID* —
  https://dev.to/ezzy1337/a-pythonic-guide-to-solid-design-principles-4c8i — phát biểu gốc
  của Barbara Liskov nói về object và subtype.

## Khi nào áp dụng

Dấu hiệu — gặp một trong các tình huống sau là luật này có mặt:

- Sắp tạo một file mã nguồn mới, một class mới, hay một hàm mới.
- Sắp sửa một hàm đã có mà thân hàm dài quá một màn hình, hoặc có quá ba nhánh `if`.
- Sắp thêm một nhánh `if`/`elif` để xử một trường hợp mới của thứ đã có.
- Sắp copy một đoạn code sang chỗ thứ hai.
- Đang ở phase `implement` hoặc đang fix một hạng mục QC.

Luật này áp cho MỌI ngôn ngữ. Ngưỡng số và rule riêng theo ngôn ngữ nằm ở
`skills/tdq-build/references/rules/` — nạp `chung.md` trước, rồi đúng một file ngôn ngữ.

## Làm gì

Repo này có 4 khai báo `class` trên 280 khai báo `def`, tức gần như thuần hàm. Nên mỗi
nguyên tắc có hai bản đọc. Tra đúng cột theo thứ bạn đang viết.

| Mã | Khi có class | Khi chỉ có hàm/module |
|---|---|---|
| SRP | Một class có đúng một lý do để đổi. Nhiều trách nhiệm thì tách class. | Một hàm làm đúng một việc; một module gom các hàm cùng một mục đích. Hàm vừa lấy dữ liệu vừa phán xét thì tách đôi. |
| OCP | Thêm hành vi mới bằng class con hoặc bản cài mới, không sửa class cũ. | Thêm trường hợp mới bằng một dòng DỮ LIỆU trong bảng hay hằng, không thêm nhánh vào thân hàm. |
| LSP | Thay đối tượng con vào chỗ đối tượng cha mà không vỡ hợp đồng. Chỉ áp nguyên văn khi có kế thừa, hoặc nhiều bản cài cùng một giao diện. | Không có kế thừa thì đọc mở rộng: mọi nhánh `return` của một hàm trả cùng kiểu và cùng hợp đồng lỗi. Đây là SUY DIỄN của repo này. |
| ISP | Không ép ai phụ thuộc phương thức họ không gọi. Giao diện to thì cắt nhỏ. | Tham số của hàm chỉ nhận đúng thứ nó dùng. Cần một đường dẫn thì nhận đường dẫn, đừng nhận cả object state. |
| DIP | Tầng cao và tầng thấp cùng phụ thuộc một trừu tượng, không phụ thuộc nhau. | Gọi qua một điểm vào chung (CLI, hàm chung), không tự cài lại chi tiết ở từng chỗ gọi. |

### SRP

ĐÚNG — `scripts/tdq_checkstatus.py`: `gom_bang_chung()` chỉ ĐỌC đĩa, `cham_ca_lech()` chỉ
PHÁN XÉT trên dữ liệu đã đọc. Đổi cách đọc không phải sửa cách chấm.

SAI — một hàm `kiem_tra()` vừa mở file, vừa so sha, vừa sinh câu chẩn đoán, vừa in bảng.
Đổi khuôn bảng in cũng phải sửa hàm đọc file.

### OCP

ĐÚNG — `scripts/doc_lint.py` hằng `SKILL_LINE_LIMITS`: thêm một skill mới chỉ cần thêm một
dòng dữ liệu, hàm `rule_r6()` không đổi một chữ.

SAI — viết `rule_r6()` thành chuỗi `if skill == "tdq-intake": ... elif skill == "tdq-spec":`
Mỗi skill mới lại phải mở thân hàm ra sửa.

### LSP

ĐÚNG — `scripts/tdq_checkstatus.py`: `doc_state_tho()` trả tuple 2 phần tử ở MỌI nhánh,
kể cả nhánh file không có và nhánh JSON hỏng. Người gọi viết đúng một cách bóc.

SAI — nhánh này `return None`, nhánh kia `return {...}`, nhánh nữa `raise`. Người gọi
phải đoán, và đoán sai thì nổ ở chỗ khác.

Nhắc lại giới hạn: LSP phát biểu gốc nói về object và subtype. Bản đọc cho hàm ở trên là
SUY DIỄN của repo này, không phải trích Liskov — đừng dẫn nó như nguyên văn.

### ISP

ĐÚNG — `scripts/tdq_checkstatus.py`: `_dem_tick(cwd, rel)` nhận đúng đường dẫn file plan.
Nó không cần biết state có gì, nên không nhận cả state.

SAI — `_dem_tick(cwd, state)` rồi bên trong tự moi `state["plan_file"]`. Muốn đếm tick của
một file plan bất kỳ thì phải dựng một state giả, kể cả trong test.

### DIP

ĐÚNG — `scripts/tdq_state.py` là điểm vào duy nhất ghi `docs/tdq/state.json`. Hook, skill
và mọi script khác đều đi qua CLI đó, không nơi nào tự mở file ra ghi.

SAI — một hook tự `json.dump` thẳng vào `docs/tdq/state.json`. Đổi định dạng state là phải
đi sửa từng nơi, và sót một nơi thì hai bản ghi lệch nhau âm thầm.

## Tự kiểm

Trả lời 5 câu này trước khi đóng một task chạm mã nguồn. Câu nào trả lời "không" thì sửa
code, đừng sửa câu trả lời. Ở phase QC, đáp án ghi vào file qc kèm chỗ đã sửa.

- SRP: mỗi hàm và mỗi class tôi vừa viết có đúng một lý do để đổi không?
- OCP: thêm một trường hợp mới nữa, tôi thêm được bằng một dòng dữ liệu hoặc một class con, mà không mở thân hàm và không sửa class cũ, đúng không?
- LSP: có kế thừa thì đối tượng con thay được vào chỗ cha mà không vỡ hợp đồng, không có kế thừa thì mọi nhánh `return` trả cùng kiểu và cùng hợp đồng lỗi, đúng không?
- ISP: mỗi tham số tôi truyền vào có được dùng thật bên trong không?
- DIP: chỗ này có đi qua điểm vào chung sẵn có, thay vì tự cài lại chi tiết không?
