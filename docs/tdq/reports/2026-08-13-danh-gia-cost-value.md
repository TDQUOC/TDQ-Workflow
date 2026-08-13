# BÁO CÁO — Cost/value từng cơ chế của tdq-workflow

Ngày: 2026-08-13 · Lane: quick · Plan: ../plan/2026-08-13-danh-gia-cost-value.md
Số đo lấy lại từ ../reports/2026-08-13-ra-soat-toi-uu-llm.md (đã qua QC 9/9).

## Đổi khung so với báo cáo trước

Báo cáo trước xếp hạng theo "tiết kiệm được bao nhiêu". Báo cáo này hỏi câu khác: mỗi cơ
chế TỐN gì, ĐÓNG GÓP gì cho chất lượng cuối, và cost đó có đáng không. Đơn vị phân tích
là **cơ chế**, không phải file — một luật thường nằm rải ở skill, hook và script.

Hai điều chỉnh phạm vi: `portable/` bị loại hoàn toàn (bản đóng gói cố ý để share và cài
project-level trên máy khác, không vào context Claude Code, nên trùng với `skills/` là
thiết kế chứ không phải nợ). Cơ hội #4 của báo cáo trước vì vậy bị RÚT.

## Chi phí thường trực của cả workflow

| Khoản | Số đo | Tần suất |
|---|---|---|
| Tầng luôn nạp (9 description + `claude-md-mau.md`) | 5.520 ký tự ≈ 1.380 token | mọi API call, mọi phiên |
| Thân skill khi được gọi | 449-1.904 token tuỳ skill | mỗi lần gọi skill |
| references | 160.645 ký tự, chỉ nạp file được trỏ tới | khi thân file trỏ tới |
| Hook trên đường prompt | 53,3ms (repo thật: 102ms+) | mỗi lượt gõ prompt |
| Hook trên đường tool call | 27,9-28,7ms | mỗi lần Edit/Bash |

Quy về tỷ lệ: phiên Claude Code điển hình chạy 100-200k token context, nên phần **luôn
nạp của cả workflow chiếm khoảng 1% context**. Đó là giá để có gate duyệt, working log,
QC bắt buộc và trạng thái đọc được bởi máy. Rẻ.

## Bảng cost/value theo cơ chế

| Cơ chế | Tốn gì | Đóng góp gì | Bỏ thì mất gì | Đáng? | Vì sao |
|---|---|---|---|---|---|
| 9 description luôn nạp | 2.040 ký tự ≈ 510 token/phiên | Claude biết có skill nào, định tuyến đúng | Không skill nào được gọi, workflow chết hẳn | ĐÁNG | Không có cách rẻ hơn để định tuyến |
| `docs/claude-md-mau.md` | 3.480 ký tự ≈ 870 token/phiên, 63% tầng luôn nạp | Luật "mọi prompt → intake", luật git, cấm sửa state tay | Workflow chỉ chạy khi user nhớ gọi tay | ĐÁNG | Là thứ biến workflow thành mặc định thay vì tuỳ hứng |
| Thân `SKILL.md` nạp khi gọi | 449-1.904 token, chỉ khi dùng | Luật thi hành của đúng phase đang chạy | Phải nhồi hết vào tầng luôn nạp, đắt gấp 6 | ĐÁNG | Trả tiền đúng lúc dùng |
| `references/` đọc khi cần | 160.645 ký tự nhưng ~0 chi phí thường trực | Khuôn spec/plan, luật duyệt, khuôn interview | Hoặc mất khuôn, hoặc phình tầng trên | ĐÁNG | Đúng progressive disclosure |
| Gate duyệt spec | 1 vòng chờ user + spec 2-4k ký tự | Chặn làm sai hướng trước khi tốn công code | Sai hướng phát hiện ở cuối, phải làm lại | ĐÁNG | Làm lại đắt hơn nhiều một vòng chờ |
| Gate duyệt plan + chốt mode | 1 vòng chờ user | User giữ quyền quyết cách chạy | Agent tự chọn subagent/worktree ngoài ý user | ĐÁNG | Đã gộp: duyệt spec viết plan ngay, duyệt plan hỏi mode ngay |
| Lane quick + tầng `nhỏ` | ~0 | Cho phép bỏ qua gate khi việc nhỏ | Mọi typo cũng phải qua 3 gate | ĐÁNG | Chính là van xả cho hai gate ở trên |
| `doc_lint` R5/R6/R8 | vài chục ms, cộng công viết lại câu dài | Giữ tài liệu ngắn, câu ≤ 40 từ, hợp đồng skill đủ 5 trường | Tài liệu phình dần, mỗi lần gọi skill đắt dần | ĐÁNG | Chính nó giữ phần không-phải-luật-lõi ở mức 12-19% |
| `edit_gate` chặn sửa code khi plan chưa `[~]` | 27,9ms mỗi lần Edit | Ép tick đúng nhịp, ép không code ngoài plan | Tick gom cuối turn, người ngoài không biết đang ở đâu | ĐÁNG | Dấu `[~]` là tín hiệu tiến độ duy nhất đọc được bởi máy |
| `stop_gate` chặn kết thúc turn khi chưa log | 28,2ms, cộng 1 lần chạy lại turn khi bị chặn | Working log không bao giờ hụt | Mất vết việc đã làm, turn sau phải đọc lại code để đoán | ĐÁNG | Cost hiện rõ nhưng thay thế duy nhất là mất log |
| `tdq_finish.py` gộp 4 việc | 1 tool call | Thay 4 call riêng (lint, log, phase, graphify) | 3 vòng đọc lại context thừa mỗi turn | ĐÁNG | Đúng bài toán carry-cost: ít call hơn = rẻ hơn nhiều |
| QC đếm theo số dòng DoD | 1 file + thời gian chạy lệnh | Không tuyên bố xong khi chưa chạy | Báo cáo "xong" không có bằng chứng | ĐÁNG | Đây là thứ giữ chất lượng cuối, không phải thủ tục |
| Điểm `(nN eNm)` trên task | ~12 ký tự mỗi task | ETA cho status line | Mất ETA, không mất luật nào | ĐÁNG THẤP | Rẻ, lợi nhỏ nhưng có thật |
| `turn_snapshot` git diff toàn worktree | 102,3ms và 7,07 MB mỗi prompt | Biết repo có đổi để nhắc log | Không nhắc được log | KHÔNG ĐÁNG NGUYÊN GIÁ | Cùng đóng góp đó đạt được với 9,0ms — 93ms còn lại là cost thuần |
| `graphify extract` cuối mỗi turn đổi code | Rebuild nền + `graphify-out/` bẩn suốt phiên | Đồ thị mã nguồn để truy vấn quan hệ | Chưa đo được mất gì | CHƯA CHỨNG MINH | Lần này cần dò trùng dòng thì đồ thị ký hiệu không dùng được |
| `tdq-spec` chép khối user-facing | 422 ký tự mỗi lần gọi skill spec | 0 — khối gốc đã nằm ở reference và bước 4 vẫn bắt đọc | Không mất gì | KHÔNG ĐÁNG | Trùng thuần, sửa một chỗ quên chỗ kia là lệch khuôn |

## Nghẽn thật

Chỉ ba mục dưới đây vừa tốn vừa KHÔNG đóng góp cho chất lượng cuối. Mọi thứ còn lại
trong bảng trên là cost có đối ứng, không phải nghẽn.

**1. 93ms và 7,07 MB thừa mỗi lượt prompt.** `git diff HEAD` chạy trên toàn worktree
trong khi `graphify-out/` luôn bẩn (chính `tdq_finish.py` sinh lại nó mỗi turn). Loại thư
mục đó khỏi pathspec: 102,3ms → 9,0ms, 7.072.647 byte → 0. Chất lượng cuối không giảm ở
chỗ nào: thứ bị loại là output do chính workflow sinh ra, không phải mã người viết, nên
tín hiệu "repo có đổi thật" vẫn nguyên vẹn — kiểm bằng `tests/test_turn_snapshot.py` và
một ca mới "sửa file mã khi `graphify-out/` bẩn vẫn phải bị nhắc log".

**2. 422 ký tự chép ở `tdq-spec/SKILL.md:36-49`.** Khối trình bày đã nằm nguyên ở
`tdq-conventions/references/user-facing-block.md:37-49` và bước 4 vẫn bắt đọc file đó.
Chất lượng cuối không giảm: khuôn không mất đi đâu, chỉ còn một bản duy nhất, và
`tests/test_user_facing_block.py` vẫn là thứ canh khuôn.

**3. `graphify extract` mỗi turn chưa chứng minh được giá trị.** Nó là nguyên nhân gián
tiếp của nghẽn 1, và trong chính lần rà soát này, truy vấn đồ thị trả về hàm test chứ
không trả về quan hệ giữa các đoạn tài liệu. Đây là mục cần bạn xác nhận, không phải mục
tôi tự kết luận: nếu bạn thật sự tra đồ thị khi làm việc thì cost đó đáng, còn nếu chưa
lần nào dùng thì nên hạ xuống chạy theo yêu cầu thay vì chạy mỗi turn.

## Đắt nhưng đáng — đừng cắt

- **`docs/claude-md-mau.md` (870 token mỗi phiên, dòng đắt nhất tầng luôn nạp).** Cắt nó
  đi thì tiết kiệm được nhiều token nhất, và cũng mất luôn thứ khiến workflow là mặc
  định. Hậu quả cụ thể: prompt mới không vào intake, request không được mở, không có
  brief, không có gate — tức là mất toàn bộ phần còn lại của bộ này.
- **Hai gate duyệt spec và plan.** Cost là hai vòng chờ user, không đo được bằng
  mili-giây nhưng là khoản đắt nhất về thời gian thực tế. Hậu quả nếu cắt: sai hướng chỉ
  lộ ra ở cuối, phải bỏ cả phần đã code. Van xả đã có sẵn là lane quick và tầng `nhỏ`.
- **`stop_gate` + `doc_lint`.** Cost hiện rõ và gây khó chịu: turn bị chặn phải chạy lại
  `tdq_finish.py` rồi in lại nguyên văn khối chat; câu dài quá 40 từ bị bắt viết lại.
  Hậu quả nếu cắt: working log hụt và tài liệu phình dần — mà tài liệu phình chính là thứ
  làm mỗi lần gọi skill đắt dần lên, tức là cắt nó để tiết kiệm sẽ phản tác dụng.
- **QC đếm theo số dòng DoD.** Tốn một file và một lượt chạy lệnh mỗi request. Hậu quả
  nếu cắt: quay về kiểu "báo xong mà chưa chạy", đúng thứ mà cả bộ này sinh ra để chặn.

## Kết luận

Bộ này không có vấn đề về chi phí context. Phần thường trực khoảng 1% context một phiên,
và phần không phải luật lõi trong thân skill là 12-19%, trong khi mặt bằng skill ngoài
đời là hơn 60%. Chi phí lớn nhất của bộ không nằm ở token mà ở **thời gian chờ user tại
hai gate duyệt** — và đó đúng là chỗ nó tạo ra giá trị, nên không đụng vào.

Đáng sửa: một dòng pathspec ở `turn_snapshot` (nghẽn 1) và một khối chép ở `tdq-spec`
(nghẽn 2). Đáng hỏi lại: `graphify` chạy mỗi turn (nghẽn 3). Ngoài ba mục đó, mọi cost
đo được trong bộ đều có đối ứng rõ ràng về chất lượng cuối.
