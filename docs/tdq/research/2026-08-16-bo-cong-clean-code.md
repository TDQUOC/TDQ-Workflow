# RESEARCH — SOLID cho luật clean code mới

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Request: 2026-08-16-1300-bo-cong-clean-code · phase analyze

## Câu hỏi cần trả lời

1. Năm luật SOLID định nghĩa chính xác thế nào, nguồn gốc ở đâu?
2. SOLID áp được cho code KHÔNG hướng đối tượng (hàm, module) không?
3. Repo này có hình dạng nào — class hay hàm?

## Nguồn

- Wikipedia SOLID — https://en.wikipedia.org/wiki/SOLID — Robert C. Martin nêu các nguyên
  tắc trong bài *Design Principles and Design Patterns* (2000); từ viết tắt SOLID do
  Michael Feathers đặt khoảng 2004. Nguyên văn: năm nguyên tắc nhằm làm mã nguồn
  "more understandable, flexible, and maintainable".
- Slide CSCE 315, Texas A&M —
  https://people.engr.tamu.edu/choe/choe/courses/12summer/315/lectures/slide23.pdf —
  xác nhận mốc lịch sử: ý tưởng xuất hiện lần đầu ở một bài newsgroup năm 1995, và SOLID
  là "a set of principles for object-oriented design (with focus on designing the classes)".
- Real Python — https://realpython.com/solid-principles-python — SOLID áp cho Python được,
  nhưng phạm vi tác giả nói rõ là "when you're writing object-oriented code".
- DEV, *Do the SOLID principles apply to Functional Programming?* —
  https://dev.to/patferraggi/do-the-solid-principles-apply-to-functional-programming-56lm
  — ánh xạ sang hàm/module: SRP đọc là "function or class or module has only one reason to
  change"; OCP đọc là "reuse and extend code without having to modify the original
  implementation"; ISP đọc là interface của module — "expose only what is necessary".
- DEV, *A Pythonic Guide to SOLID* —
  https://dev.to/ezzy1337/a-pythonic-guide-to-solid-design-principles-4c8i — LSP phát biểu
  gốc của Barbara Liskov nói về **object và subtype**, nên đây là luật duy nhất cần thật sự
  có quan hệ kế thừa mới áp được nguyên văn.
- Baeldung — https://www.baeldung.com/solid-principles — SRP: "a class should only have one
  responsibility... only one reason to change".

## Trả lời

**1. Năm luật.** SRP một lý do để đổi · OCP mở cho mở rộng, đóng với sửa đổi · LSP thay
đối tượng con vào chỗ đối tượng cha mà không vỡ · ISP không ép ai phụ thuộc thứ họ không
dùng · DIP tầng cao và tầng thấp cùng phụ thuộc trừu tượng.

**2. Áp cho code không OOP: được với 4/5 luật.** SRP, OCP, ISP, DIP đều có bản đọc theo
hàm và module (nguồn DEV functional). Riêng **LSP cần quan hệ kế thừa mới áp nguyên văn**;
không có class con thì bản đọc gần nhất là "mọi nhánh của một hàm phải trả cùng kiểu và
cùng hợp đồng lỗi" — đây là suy diễn, không phải phát biểu gốc, nên phải ghi rõ là bản
đọc mở rộng chứ không được trình bày như trích dẫn Liskov.

**3. Hình dạng repo này** (đo bằng lệnh, 2026-08-16):

| Chỉ số | Con số |
|---|---|
| File `.py` trong `scripts/` | 19 |
| Khai báo `class` cấp cao nhất | 4 |
| Khai báo `def` cấp cao nhất | 280 |

Tỷ lệ 4/280. Bộ workflow này gần như thuần hàm.

## Hệ quả lên thiết kế

Một luật chỉ chép nguyên văn năm câu SOLID kiểu OOP sẽ **không dùng được** ở đây: model
mở `scripts/tdq_state.py` ra, không thấy class nào, rồi kết luận luật không áp — đúng cái
thất bại mà soul nguyên tắc 3 ("viết cho model yếu nhất") cấm. Luật mới bắt buộc phải có
cột "đọc thế nào khi chỉ có hàm và module", và LSP phải ghi rõ giới hạn.

Mất mát cần khai: bỏ `code_rule_scan.py` là bỏ phần `## Tự kiểm` dạng **lệnh** của clean
code. Soul nguyên tắc 3 cho phép Tự kiểm là "một lệnh HOẶC một câu hỏi có/không", nên vẫn
hợp lệ, nhưng luật phân xử #2 ưu tiên luật kiểm được bằng lệnh. Cách bù: giữ phần kiểm
được bằng lệnh ở mức hình dạng tài liệu (doc_lint), còn phần phán đoán thiết kế thì dùng
checklist có/không.
