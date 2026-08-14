# BRIEF — Chống quick-fix làm hỏng kiến trúc & sinh nợ kỹ thuật

Ngày: 2026-08-14 · Lane: <chờ user chốt>

## Nguyên văn

> okay tôi thấy agent code hay có trình trạng quick fix khiến cho refacetor hoặc add
> feature project dễ gây ảnh hưởng đến kiến trúc tổng thể project và ảnh huỏng đến những
> gì có sẵn trong project một cách vô tình/ gây nợ kĩ thuật, hãy check và sreach xem có
> cáh nào để xử lí và bổ sung vào bộ workflow này để không gây ảnh hưởng như trên không?
> yêu cầu mở request phân tích workflow hiện tại và resreach phương án và đề xuất cho tôi

### Cách hiểu đầu tiên

Mục tiêu: tìm cơ chế chặn kiểu sửa chữa chắp vá của agent, để việc refactor hay thêm
tính năng không âm thầm phá kiến trúc sẵn có và không tích nợ kỹ thuật.

Ba triệu chứng cần chặn:

1. Agent sửa cục bộ cho xanh test, bỏ qua khuôn kiến trúc đang có của project.
2. Agent thêm lớp/hàm/file mới song song với thứ đã tồn tại thay vì dùng lại.
3. Agent chạm vùng ngoài phạm vi và làm hỏng thứ đang chạy mà không ai thấy.

Phạm vi đoán: sửa bộ skill `tdq-*` (và có thể `scripts/`, `hooks/`) trong chính repo này.
Đầu ra của request: bản phân tích khoảng trống hiện tại cộng danh sách phương án có
nguồn, xếp theo chi phí và giá trị, để user chọn.

Khoảng trống thấy ngay khi soát bộ skill: toàn bộ 1.844 dòng skill hiện có **một** lần
nhắc chữ "kiến trúc", nằm ở bảng chọn lane. Không có bước lập bản đồ ràng buộc kiến
trúc, không có luật buộc dùng lại thứ có sẵn, không có hạng mục QC về hồi quy kiến trúc
hay trùng lặp. QC hiện bám đúng dòng Definition of Done, nên thiệt hại ngoài DoD không
bị bắt.

### Chỗ chưa rõ (đưa vào vòng scope)

- Request này dừng ở mức đề xuất, hay làm luôn phần đã chọn?
- Cơ chế mới áp cho cả hai pipeline hay chỉ pipeline chuyên sâu?
- Chấp nhận thêm bao nhiêu chi phí mỗi request: thêm dòng luật, thêm gate, hay thêm
  bước kiểm tự động?

## Hiểu & kiến thức

### Năng lực dùng được

Phân vân → DÙNG. Kiểm kê ngày 2026-08-14: 283 skill trên đĩa, cộng skill built-in
trong context. Không xoá bảng này kể cả khi không có dòng DÙNG nào.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| graphify | user | DÙNG | `graphify affected` và `god-nodes` cho bước bán kính ảnh hưởng |
| tavily-search | plugin:tavily | DÙNG | research phương án, đã chạy qua sub-agent |
| sonar-duplication | plugin:sonarqube | DÙNG | ứng viên cổng kiểm trùng lặp, chốt ở spec |
| mem0-memory | user | DÙNG | ghi một fact quy ước mới sau khi chốt cơ chế |
| tdq-conventions | plugin:tdq-workflow | NỀN | file luật chung, đích sửa của request |
| tdq-intake | plugin:tdq-workflow | NỀN | phase analyze, đích sửa của request |
| tdq-spec | plugin:tdq-workflow | NỀN | khuôn spec, đích sửa của request |
| tdq-plan | plugin:tdq-workflow | NỀN | khuôn plan, đích sửa của request |
| tdq-build | plugin:tdq-workflow | NỀN | implement và QC, đích sửa của request |
| Đã xét 274 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

### Khoảng trống của workflow hiện tại

Đọc hết 1.844 dòng skill `tdq-*`, 939 dòng hook, khuôn spec và khuôn plan. Bốn khoảng
trống đo được:

1. **Không có ràng buộc kiến trúc thành văn bản.** Cả bộ skill nhắc chữ "kiến trúc"
   đúng một lần, ở bảng chọn lane. Không có nơi nào ghi "project này theo khuôn nào,
   lớp nào không được gọi lớp nào". Agent không có gì để đối chiếu trước khi sửa.
2. **Không có luật dùng lại trước khi tạo mới.** Bước implement chỉ nói "thay đổi nhỏ
   nhất mà đủ thoả task. Bám style code sẵn có". Không buộc tìm thứ có sẵn, không buộc
   ghi lý do khi tạo file hay hàm mới song song thứ đã tồn tại.
3. **Không có bước bán kính ảnh hưởng.** Phase analyze có gợi ý mở đồ thị graphify khi
   câu hỏi thuộc dạng liên kết, nhưng đó là gợi ý đọc, không phải bước bắt buộc trước
   khi sửa. Plan không có chỗ khai "task này chạm tới những đâu". Lệnh
   `graphify affected "X"` và `graphify god-nodes` đã có sẵn mà workflow chưa dùng.
4. **QC không bắt được thiệt hại ngoài Definition of Done.** Luật cứng: số hạng mục QC
   bằng số dòng DoD, "không thêm hạng mục ngoài DoD". Full test suite là hàng rào duy
   nhất. Thứ không có test — trùng lặp, lớp thừa, ràng buộc kiến trúc bị phá — lọt hết.

Phần cấu trúc thì workflow đã có sẵn nhiều chỗ neo tốt: khuôn spec §3 và §5, khuôn plan
có khối hợp đồng skill 5 trường, hook `edit_gate.py` đã chặn được thao tác Edit theo
điều kiện, `doc_lint.py` đã có 8 rule kiểm tài liệu. Cơ chế mới nên gắn vào các chỗ này
thay vì dựng bộ máy song song.

### Phạm vi đã chốt

- Mặt CHỌN: ràng buộc kiến trúc thành văn bản · dùng lại trước khi tạo mới · bán kính
  ảnh hưởng · cổng QC chống hồi quy. User chọn cả bốn, không loại mặt nào.
- Mặt LOẠI: thực thi cơ chế vào workflow — chép nguyên sang spec §1 NGOÀI phạm vi.
  Request này dừng ở bản đề xuất, việc làm thật mở request riêng (user chọn 5B).
- Bối cảnh: áp cho mọi project dùng plugin, cả hai pipeline (express rút gọn), sàn chi
  phí là mức A (luật văn bản cộng tối đa một bước mới, không thêm cổng duyệt).
- Mức đầu tư suy ra: vừa — đầu ra là tài liệu, không có runtime, nhưng cơ chế sẽ áp cho
  mọi project nên đề xuất phải đủ chi tiết để request sau bắt tay làm được ngay.

### Research

Sáu hướng, đủ nguồn: `docs/tdq/research/2026-08-14-chong-no-ky-thuat.md`. Tám ứng viên
cơ chế nằm ở mục cuối file đó. Số liệu đáng chú ý: GitClear đo trên 211 triệu dòng,
năm 2024 là lần đầu tỷ lệ copy-paste vượt refactor.

## Hỏi đáp

### Vòng scope — 2026-08-14 10:2x

Chạy vòng scope vì thoả dấu hiệu 1 (yêu cầu gọi tên cả một cơ chế, không trỏ file cụ
thể) và dấu hiệu 3 (từ mở "không gây ảnh hưởng", không kèm số).

Câu hỏi đã trình: 1 câu chọn mặt, 4 câu bối cảnh, 1 câu chốt vòng.

User trả lời nguyên văn lúc 10:28: `1 A B C D 2 A 3 D nhưng min level ở A 4 A 5 B 6 A`.

Diễn giải: chọn cả bốn mặt · áp cho mọi project dùng plugin · chi phí tự gõ, sàn là mức
A · áp cả hai pipeline · dừng ở bản đề xuất · không bổ sung gì thêm.

Còn mơ hồ ở câu 3: "min level ở A" cho biết sàn, chưa cho biết trần. Đưa vào vòng chi
tiết, không tự suy.

### Vòng chi tiết — 2026-08-14 10:29

Bốn câu, đều nằm trong các mặt user đã chọn: trần chi phí, hình thù đầu ra, số gói
phương án, nguồn của file luật kiến trúc.

User trả lời nguyên văn lúc 10:33: `1A 2A 3A 4A 5A`. Diễn giải:

- Trần chi phí là mức B: luật văn bản bắt buộc, được thêm script kiểm khi cơ chế đó
  thật sự cần máy kiểm. Cấm đề xuất cổng duyệt mới.
- Đề xuất phải có bản nháp copy được: nguyên văn dòng luật, chèn vào skill nào, chỗ
  nào, kèm cách kiểm. Không kèm plan phác thảo.
- Trình 3 gói theo mức chi phí, khuyến nghị đúng một gói.
- File luật kiến trúc: agent sinh bản nháp lần đầu từ code cộng `graphify god-nodes`,
  user sửa rồi chốt.

Hết câu hỏi làm đổi kết quả. Kết thúc vòng interview.

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ | Đã chạy, 6 hướng, kết quả ở `research/<slug>.md` |
| Interview | CÓ | Đã chạy 2 vòng: scope và chi tiết, hết câu hỏi đổi kết quả |
| QC độc lập bằng agent | BỎ | Đầu ra là một tài liệu, DoD kiểm hết bằng `grep` và `doc_lint` |
| Review sâu bằng `tdq-reviewer` | BỎ | Request `2026-08-08-giam-over-engineer-workflow` đã chốt: thêm lớp review cho việc nội bộ là lặp lại đúng lỗi đang sửa |
| Chia sub-agent implement | BỎ | Một tài liệu duy nhất, tách agent làm lệch giọng và lệch tên mục |
| Spec, plan, implement, report | CÓ | Khung bất biến |

### Kiểm cổng

- Làm ra gì: một file đề xuất ở `docs/tdq/knowledge/2026-08-14-chong-no-ky-thuat.md`,
  gồm phân tích khoảng trống, 3 gói cơ chế, bản nháp copy được cho từng cơ chế.
- Có cần model, download, cài đặt gì không: không. `graphify` đã cài, `doc_lint.py` và
  bộ test đã có sẵn trong repo.
- Phạm vi QC: kiểm cấu trúc file đề xuất bằng `grep`, kiểm đường dẫn nêu trong đề xuất
  có thật, kiểm không cơ chế nào vượt trần B, cộng `doc_lint` và full test suite.
