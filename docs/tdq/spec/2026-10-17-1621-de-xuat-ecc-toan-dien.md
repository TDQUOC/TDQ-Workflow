# SPEC — Đề xuất nâng cấp TDQ Workflow từ ECC toàn diện hơn
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-10-17 · Bản: 1.0 · Lane: full · Ngôn ngữ: vi
Brief: `docs/tdq/brief/2026-10-17-1621-de-xuat-ecc-toan-dien.md`
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

### Mục tiêu

Xuất bản đề xuất hợp nhất giúp người dùng quyết định TDQ nên học gì từ ECC, không chỉ mở rộng danh sách tính năng. Phải chỉ rõ khả năng TDQ đã có, khoảng thiếu được xác minh, thay đổi tối thiểu, phần không đáng làm, thứ tự đầu tư và cách kiểm hiệu quả. Nội dung có tóm tắt dễ hiểu và phân tích kỹ thuật truy vết được.

Kế thừa D01–D10 của hồ sơ `2026-10-17-1442-de-xuat-nang-cap-tu-ecc`, đối chiếu kỹ tám nhóm bổ sung và gộp phần trùng. Không mặc định kết quả là mười tám đề xuất, không gọi một khả năng hiện có là tính năng mới.

Snapshot ban đầu: TDQ HEAD `1d78ca86ca5b0710f357d8436ec7d9d2d7562b54`, ECC HEAD `76aaa77df6adc5b889e689007bf99b9a4f74af34`. Phải xác minh lại khi biên soạn và ghi mọi khác biệt nguồn. ECC chỉ đọc, tại `C:/Users/admin/Documents/ECC`; báo cáo tổng quan ECC cũ chỉ là chỉ mục nguồn, không đủ để khẳng định enforcement hoặc hiệu quả.

### Trong phạm vi

Giữ năm trụ cột trước: hooks/latency; multi-agent/worktree; quality/review; shell safety; ổn định nền tảng. Đối chiếu kỹ thêm các nhóm sau:

| Nhóm | Câu hỏi chuyển giao cần trả lời |
|---|---|
| G1 — Ngữ cảnh và bàn giao | TDQ đã phục hồi gì sau compact; thiếu quyết định/ràng buộc/bằng chứng nào; có thể cải thiện bàn giao hoặc nạp theo nhu cầu mà không tăng đọc lặp? |
| G2 — Học từ lỗi có kiểm duyệt | Nguồn bài học nào đáng tin, ai duyệt, phạm vi/phiên bản/thu hồi ra sao; ngăn memory poisoning và không biến quan sát thành quyền hay policy? |
| G3 — Đánh giá lặp | Bộ eval tuân thủ hiện có đo được gì; oracle có bỏ sót hoặc chấm sai không; phân biệt tìm được lời giải với độ ổn định qua lần chạy và thiết kế đối chứng ra sao? |
| G4 — Dấu vết thực thi | Tận dụng công cụ transcript và scorer hiện có thế nào để kiểm trình tự/quyền/vùng ghi; thiếu log hoặc tool output không đầy đủ được phân loại chưa xác minh ra sao? |
| G5 — Định cỡ quy trình và rủi ro | Cải thiện đề xuất lane/QC theo rủi ro mà không tự đổi lựa chọn đã duyệt; tránh heuristic chỉ dựa số file hoặc từ khóa? |
| G6 — Chuyên môn theo lĩnh vực | Nạp checklist/skill chuyên ngành có chọn lọc dựa inventory và rule ngôn ngữ đã có; kiểm trigger, xung đột, provenance và chi phí bảo trì thế nào? |
| G7 — Nhiều phiên/harness | Có nhu cầu thật nào chưa được state/team/adapter hiện tại đáp ứng; học lifecycle, timeout, phục hồi tối thiểu hay hoãn control plane/daemon? |
| G8 — Phân công model theo vai trò | TDQ đã cấu hình vai trò/model/effort gì; phần cần đo hoặc điều chỉnh là gì; giữ lựa chọn người dùng, không tự tráo model hoặc suy chi phí từ tên model? |

Mỗi nhóm có nguồn đại diện ở cả hai repo, trạng thái bằng chứng và kết luận giữ nguyên/cải tiến/thử hẹp/hoãn/không làm. Mỗi đề xuất được giữ hoặc bổ sung có phiếu chi tiết, công sức, dependency, rủi ro, rollback, phép đo và điều kiện go/no-go. Roadmap thể hiện gói ưu tiên cùng điều kiện vào/ra; không ép lấp phiên bản hoặc tự cam kết lịch phát hành.

**Mục tiêu hiện tại là Windows/PowerShell trước. macOS và Linux để giai đoạn sau theo lời người dùng**, có ghi rõ ở backlog cùng điều kiện xem xét lại; không đưa triển khai/kiểm thử hai nền tảng này vào nghiệm thu hiện tại. Không chủ động phá tương thích adapter đang có; chỉ nêu giới hạn chưa kiểm trên nền tảng khác.

### NGOÀI phạm vi

Triển khai runtime/PoC sản phẩm, nới gate, engine/daemon mới, chạy eval model thật tốn phí, dashboard, phát hành; triển khai/kiểm thử macOS và Linux để giai đoạn sau, không thuộc nghiệm thu hiện tại.

Không sửa source, test, skill, hook, state machine hoặc policy TDQ/ECC; không thêm dependency/dịch vụ/model/API mới; không gọi model trả phí để tạo dữ liệu đánh giá. Không audit web/CVE/giá model hiện hành. Không đọc kho transcript cá nhân hoặc dữ liệu tài khoản ngoài hồ sơ request và fixture/kết quả được lưu trong repo; không gửi dữ liệu ra dịch vụ ngoài. Các subagent trong phiên dùng để khảo sát và kiểm định, không phải phiên benchmark sản phẩm.

Không hứa phần trăm tăng chất lượng, giảm lỗi hay tiết kiệm token khi chưa có dữ liệu tương ứng. Không sửa báo cáo đã nghiệm thu để che kết luận lịch sử; mọi sửa nhận định cũ phải được ghi minh bạch trong hồ sơ mới.

## 1b. Lộ trình

Chép từ brief. Duyệt spec là duyệt lộ trình này; không thay cổng duyệt plan và lựa chọn cách thực hiện.

| Bước/phase | Chạy? | Skill/công cụ | Vì sao |
|---|---|---|---|
| Khảo sát nguồn cục bộ | CÓ | LSP, graphify mới, Grep/Read, agent chỉ đọc | Kiểm hiện trạng TDQ, cơ chế ECC, guideline so với enforcement; báo cáo cũ chỉ là chỉ mục |
| Research web | BỎ | Không dùng | Chuyển giao từ hai snapshot cục bộ; không hỏi giá, model/API hoặc CVE hiện hành |
| Interview | CÓ — đã xong | tdq-intake | Đã chọn full và chốt độ sâu, Windows trước, macOS/Linux sau, ultra cùng QC đa subagent |
| Spec → plan | CÓ | tdq-spec; hướng dẫn tdq-plan | Duyệt phạm vi trước, viết plan ngay sau duyệt spec; chưa thực hiện báo cáo trước duyệt plan/mode |
| Biên soạn tài liệu | CÓ | tdq-build | Hồ sơ bằng chứng và báo cáo hợp nhất, không sửa runtime |
| Phản biện theo chiều | CÓ | Các subagent chỉ đọc độc lập với tác giả | Tách nguồn/khoảng thiếu, thiết kế/an toàn, định lượng/roadmap; không bỏ phiếu thay bằng chứng |
| QC ultra cuối | CÓ | tdq-qc-tester, CLI kiểm hiện có | Tổng hợp phản biện, kiểm DoD, suite đúng cổng và smoke cô lập khả thi; không chạy suite theo số agent |
| Report | CÓ | tdq-build | Bản báo cáo hợp nhất là report kết thúc; hỏi commit khi xong |
| Vision/UI test và runtime mới | BỎ | Không dùng | Chỉ Markdown; không tạo giao diện hoặc tiến trình chỉ để điền QC |
| Eval model thật, macOS/Linux | BỎ | Không dùng trong request này | Không có ngân sách chạy model; macOS/Linux được người dùng yêu cầu xử lý sau |

Luồng đầu ra: xác minh nguồn → bản đồ khả năng/khác biệt → ánh xạ và gộp D01–D10 → đề xuất có căn cứ → ước tính và roadmap → phản biện phân chiều → QC độc lập cuối. Phần được tái sử dụng từ hồ sơ cũ phải có provenance và giới hạn, không biến kết quả kiểm cũ thành kết quả chạy mới.

## 2. Đầu ra cụ thể

| Mã | Đầu ra | Đường dẫn | Đo xong bằng |
|---|---|---|---|
| O1 | Hồ sơ bằng chứng hợp nhất | `docs/tdq/research/2026-10-17-1621-de-xuat-ecc-toan-dien.md` | Snapshot, nguồn TDQ/ECC, quan hệ thực, từng nhóm và ánh xạ bằng chứng cũ; phép kiểm vô hại khả thi, giới hạn và phương pháp đo |
| O2 | Báo cáo đề xuất toàn diện hơn | `docs/tdq/reports/2026-10-17-1621-de-xuat-ecc-toan-dien.md` | Tóm tắt dễ đọc, bản đồ hiện trạng/khoảng thiếu, ánh xạ D01–D10, phiếu đề xuất, ma trận chi phí/lợi ích và roadmap Windows trước; backlog macOS/Linux |
| O3 | Hồ sơ QC đa chiều và kiểm định cuối | `docs/tdq/qc/2026-10-17-1621-de-xuat-ecc-toan-dien.md` | Từng DoD có verdict/evidence; nguồn phản biện độc lập, lỗi/mâu thuẫn và xử lý; kết quả kiểm thực, giới hạn/N/A không bị gọi thành PASS |

Dữ liệu thô, phương pháp và lệnh tái lập nằm trong O1, không tạo một framework benchmark hoặc file code mới. O2 đồng thời là report kết thúc, không tạo báo cáo tổng kết lặp. Brief/spec/plan, working log, state qua CLI và artifact tìm kiếm sinh bởi công cụ là hồ sơ workflow, không phải nâng cấp sản phẩm. Không tự gom artifact tìm kiếm hoặc thay đổi tồn tại trước request vào commit báo cáo.

## 2b. Ranh giới module

Request chỉ viết tài liệu; đường cắt quyền ghi dựa chuỗi bằng chứng → quyết định → kiểm định, không chia quyền sửa runtime theo thư mục nguồn. Leader là chủ ghi artifact; subagent khảo sát/kiểm định trả kết quả, không ghi chung tài liệu.

| Module | Vùng file được ghi | Phụ thuộc module | Đầu ra §2 |
|---|---|---|---|
| Bằng chứng | `docs/tdq/research/2026-10-17-1621-de-xuat-ecc-toan-dien.md` | Nguồn TDQ/ECC chỉ đọc, hồ sơ cũ | O1 |
| Quyết định nâng cấp | `docs/tdq/reports/2026-10-17-1621-de-xuat-ecc-toan-dien.md` | Bằng chứng | O2 |
| Kiểm định | `docs/tdq/qc/2026-10-17-1621-de-xuat-ecc-toan-dien.md` | Bằng chứng, Quyết định nâng cấp | O3 |

Căn cứ semantic đã kiểm để tránh vẽ khoảng thiếu giả:

- LSP tìm tham chiếu `cham_phien` ở `scripts/tdq_eval.py:624` trả các vị trí trong source và test; đọc `scripts/tdq_eval.py:624-631` xác nhận scorer dùng `phan_tich(doc_transcript(...))` rồi `cham_mot_ma`. G3/G4 dùng chung luồng transcript → phân tích → oracle, không mặc định hai engine độc lập.
- `evals/tuan-thu/README.md:5-23,25-47` đã mô tả chạy lặp, chấm lại transcript và bộ ca tuân thủ; đây là tài liệu/cấu hình liên quan, không chứng minh các ca đã được thực thi trong request này.
- `hooks/scripts/session_start.py:239-245` đã xử lý `source=compact` để chèn request/phase/plan và anti-patterns. G1 phải đánh giá tính đầy đủ của bàn giao trên đường hiện có, không đề nghị thêm hook phát hiện compact từ đầu.
- Import nạp động, adapter host, quan hệ cấu hình và nội dung Markdown cần đối chiếu nguồn/manifest, không chỉ LSP. Kết quả symbol giả từ LSP trên Markdown không dùng làm quan hệ runtime. Không có reference không chứng minh không có hành vi.

## 3. Cách tiếp cận & lý do

### Khác với báo cáo cũ

Báo cáo cũ tập trung năm trụ cột và D01–D10; bản này bổ sung bản đồ tám nhóm, so sánh với công cụ TDQ hiện có, ánh xạ giữ/sửa/gộp/hoãn từng ID cũ và đánh giá lợi ích giao nhau. Báo cáo mới phải đọc được để ra quyết định mà không buộc người dùng ghép các bảng rời; chi tiết đo lịch sử có thể dẫn về O1 cũ với snapshot và giới hạn rõ.

Đối với mỗi cơ chế ECC, phân biệt: văn bản khuyến nghị; code có đường gọi thực; test kiểm hành vi; phép thực thi quan sát được; hiệu quả có dữ liệu. Không suy từ số lượng skill/agent, công thức thống kê hoặc fixture xanh thành chất lượng sử dụng thực tế. Nhận định cũ sai được sửa với nguồn và lý do, không chép tiếp.

### Hợp đồng phiếu đề xuất

Mỗi phiếu gồm ID ổn định và liên hệ D01–D10/G1–G8; vấn đề và bằng chứng; phần TDQ đã có; nguyên tắc học từ ECC; thay đổi tối thiểu/điểm tích hợp dự kiến; ví dụ trước/sau; phương án giữ nguyên; dependency; công sức triển khai/duy trì; rủi ro/rollback; phép đo và go/no-go. Các điểm chạm runtime chỉ là gợi ý cho request tương lai, không phải quyền ghi hiện tại.

Không đưa daemon, kho memory, model router hoặc framework eval mới vào roadmap chỉ vì có trong ECC. Kiểm khả năng tái sử dụng trước, phân biệt thay đổi tài liệu với CLI/hook/adapter; giữ quyền người dùng chọn lane, QC, model và phê duyệt.

### Ước tính và đo

- Công sức thấp/cơ sở/cao kèm phân rã, giả định, phần không tính, độ bất định và công duy trì. Không coi khoảng này là confidence interval.
- Tách thời gian người, thời gian máy, số bước và token. Không quy token từ độ dài văn bản hoặc model time, không dùng bảng giá chưa xác minh. Không cộng chồng lợi ích cùng điểm nghẽn giữa D08/G1/G8 hoặc D01/D04/G3/G4.
- Dùng phép kiểm cô lập không gọi model cho các entry point hiện có đã kiểm side effect, ví dụ scorer trên fixture tổng hợp hoặc đường phục hồi trên input vô hại. Ghi input/oracle, môi trường, dữ liệu thô, lệnh thật và giới hạn. Không đặt snapshot đã đọc thành benchmark đã chạy.
- Phân tích tĩnh bộ ca và kết quả đã lưu trong repo có ghi thời điểm/snapshot; không dùng lịch sử không tương thích làm đối chứng trực tiếp. Thiếu corpus gán nhãn độc lập thì precision/recall và tỷ lệ cải thiện là chưa định lượng.
- Đề xuất thiết kế đo đối chứng cho request triển khai sau: cùng nhiệm vụ, cùng quyền, cùng chất lượng yêu cầu; ghi phiên bản và yếu tố gây nhiễu. Lần chạy không độc lập không được dùng công thức giả định độc lập mà không nêu hạn chế.
- Nếu chưa đủ dữ liệu, vẫn kết luận ưu tiên tạm thời có lý do và điều kiện thu thêm dữ liệu; không hứa đo được tác động sản phẩm khi sản phẩm chưa tồn tại.

### QC nhiều subagent

Phản biện phân chiều bằng các subagent chỉ đọc khác tác giả, tập trung nguồn/khoảng thiếu, thiết kế/an toàn, định lượng/roadmap. Các lượt có thể song song nhưng không cùng ghi artifact hoặc tự chạy trọn suite. Sau khi leader xử lý findings, một `tdq-qc-tester` độc lập đối chiếu DoD và evidence cuối. Mâu thuẫn được giải bằng source/test/dữ liệu, không bỏ phiếu hoặc lấy nhiều lời đồng ý làm bằng chứng. Plan chỉ định người chạy suite và phạm vi mỗi lượt để tránh nhân đôi công việc.

## 3b. Năng lực & công cụ

Chép bảng quyết định từ brief; Agent là công cụ, không phải skill phải invoke. Skill chỉ có trên đĩa được đọc hướng dẫn theo pipeline, không tự gọi tên chưa xuất hiện trong danh sách user-invocable.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | Tiếp nhận, phân tích và phỏng vấn |
| tdq-conventions | plugin:tdq-workflow | NỀN | Quy tắc ngôn ngữ, state, Git, tìm kiếm và nhật ký; đọc trực tiếp, không invoke |
| tdq-spec | plugin:tdq-workflow | NỀN | Viết spec; lập plan sau khi spec được duyệt |
| tdq-build | plugin:tdq-workflow | NỀN | Biên soạn, kiểm định và bàn giao theo plan được duyệt |
| tdq-lean | plugin:tdq-workflow | NỀN | Loại đề xuất trùng, không cần thiết và chi phí kiến trúc không có căn cứ |
| Agent | built-in tool | DÙNG | Khảo sát nguồn chỉ đọc và kiểm định độc lập theo hợp đồng sau khi chốt QC |
| Đã xét các mục TDQ tra trạng thái/setup/plan/phục hồi còn lại trên đĩa và 16 skill ngoài bộ TDQ; các built-in còn lại | user/plugin/built-in | KHÔNG | khác lĩnh vực; không cần skill đổi settings, tạo dashboard, gọi API, orchestration workflow hoặc chạy ứng dụng để viết đề xuất cục bộ; phần hướng dẫn setup/plan của TDQ được đọc theo pipeline khi cần |

## 4. Yêu cầu bắt buộc

- Log service: BỎ — không tạo hoặc sửa runtime; working log qua công cụ kết thúc lượt, hồ sơ kiểm có timestamp và output thật.
- Unit test runtime mới: BỎ — không sửa code; mỗi artifact có lint và kiểm nội dung/ngữ nghĩa, giữ suite hiện có theo QC ultra.
- Không placeholder, dữ liệu giả làm dữ liệu thật, tự duyệt gate hoặc tự chọn mode triển khai tài liệu. Không viết plan trước khi spec được duyệt.
- O1/O2/O3 viết tiếng Việt, giữ tên kỹ thuật; giả mã và ví dụ ghi rõ chưa triển khai.
- Không sửa hồ sơ cũ để tạo lịch sử sạch. Các cập nhật state chỉ qua CLI, working log qua công cụ kết thúc; không reset thay đổi tồn tại trước request.
- Nguồn ECC chỉ đọc. Request triển khai sau nếu sao chép phần đáng kể mã MIT phải giữ notice; quy tắc không attribution trong commit không thay nghĩa vụ giấy phép.

## 5. Ràng buộc & rủi ro

`docs/kien-truc.md` còn header NHÁP; không tự chốt toàn tài liệu. Các quyết định hiện hành liên quan phải giữ:

- “hooks/ được gọi scripts/; scripts/ không được import hooks/” (`docs/kien-truc.md:21-22`) — đề xuất tái sử dụng evaluator/helper không tạo cạnh import ngược.
- “Chỉ scripts/tdq_state.py được ghi docs/tdq/state.json; mọi nơi khác chỉ đọc qua CLI.” (`docs/kien-truc.md:25`) — mọi cập nhật workflow hiện tại theo hợp đồng này.
- “hook chỉ nhắc và kiểm bằng hiệu ứng thật, không trả deny vì lý do \"chưa duyệt\".” (`docs/kien-truc.md:47`) — không chuyển đề xuất trace/risk thành gate mới trái quyền duyệt.
- “trọn bộ test chỉ chạy ở 2 cổng” (`docs/kien-truc.md:67-68`) — QC-F1 và sau vòng sửa QC cuối; không nhân suite theo số subagent.
- “mức QC là quyết định của USER” (`docs/kien-truc.md:104`) — ultra đã ghi theo câu trả lời thật; không giảm do mode main hoặc báo cáo chỉ Markdown.

Không cài thêm sản phẩm/dependency phục vụ đầu ra, không API/model runtime mới, không chạy model eval thật hoặc gọi giá hiện hành. Công cụ agent trong phiên phục vụ khảo sát/QC; không mặc định mức chi phí đó là dữ liệu benchmark hay ngân sách sản phẩm.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Catalog ECC bị coi là enforcement/hiệu quả đã chứng minh | Đầu tư sai hoặc sao chép kiến trúc nặng | Lần ngược source/caller/test; tách trạng thái chứng cứ |
| Không phát hiện khả năng TDQ đã có | Thêm engine/hook trùng lặp | Kiểm eval, compact, trace, inventory, adapter và cấu hình vai trò trước khi lập phiếu |
| Oracle không đủ hoặc trace bị thiếu | Chấm PASS/FAIL sai, nhầm tuân thủ với chất lượng | Tách confirmed/refuted/uncertain/unverified; đối chiếu oracle và giới hạn |
| Bài học chứa chỉ thị không đáng tin | Memory poisoning hoặc nới quyền ngầm | Quarantine/provenance/duyệt/thu hồi là yêu cầu đánh giá, không tự nạp bài học mới |
| Ước tính giao nhau hoặc dùng số lịch sử sai bối cảnh | ROI chính xác giả tạo | Đơn vị rõ, giả định công khai, không cộng chồng; không định lượng khi thiếu dữ liệu |
| Nhiều agent đọc lặp hoặc đồng thuận sai | Tăng công mà không tăng độ tin cậy | Chia chiều kiểm, giới hạn đọc/ghi, leader xác minh finding, kiểm cuối độc lập |
| Phạm vi lan sang đa nền tảng/daemon | Chậm quyết định Windows trước | Backlog macOS/Linux riêng, nêu điều kiện quay lại; không thử hệ thống mới |

## 6. QC & Definition of Done

Mức `ultra` theo câu trả lời thật, ghi state 2026-10-17T16:37:25+07:00. Điều kiện PASS dưới đây là nội dung cần kiểm; lệnh và phân công kiểm cụ thể thuộc plan. Không đặt mục tiêu speedup hoặc tỷ lệ chất lượng khi chưa có baseline phù hợp.

| Mã | Hạng mục kiểm | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |
|---|---|---|---|---|
| Q-A | Nguồn và provenance O1 | Snapshot, nguồn hai repo và đường gọi được đối chiếu; guideline/code/test/thực thi/hiệu quả không bị đánh đồng; nhận định cũ sai có xử lý rõ | — | Sửa hoặc rút claim không được nguồn hỗ trợ; không biến thiếu dữ liệu thành PASS |
| Q-B | Bao phủ và hiện trạng O1/O2 | Mọi nhóm bổ sung và trụ cột cũ có trạng thái TDQ đã có/khoảng thiếu/chưa xác minh cùng kết luận; không đề xuất lại khả năng đã tồn tại như mới | — | Bổ sung đối chiếu hoặc ghi chưa xác minh với tác động tới quyết định |
| Q-C | Ánh xạ và gộp O2 | Mỗi ID cũ có quyết định giữ/sửa/gộp/hoãn/không làm và lý do; đề xuất mới liên hệ nhóm/bằng chứng; không tăng số lượng chỉ để đủ danh mục | — | Gộp hoặc loại phiếu trùng, giữ truy vết quyết định cũ |
| Q-D | Phiếu nâng cấp O2 | Mọi đề xuất được chọn có đầy đủ trường §3, ví dụ dễ hiểu, phương án không làm, điểm tích hợp, rủi ro/rollback và go/no-go | — | Hoàn thiện hoặc chuyển sang khảo sát/hoãn nếu chưa đủ căn cứ |
| Q-E | Đo và ước tính O1/O2 | Dữ liệu thực, mô hình và giả định tách riêng; tính lại khớp; không cộng chồng; thiếu dữ liệu có thiết kế đo; không phát sinh phiên model eval thật | — | Sửa số/phương pháp, bỏ định lượng không có căn cứ và giữ giới hạn |
| Q-F | Roadmap và phạm vi O2 | Dependency, điều kiện vào/ra, ưu tiên Windows/PowerShell rõ; macOS/Linux ghi xử lý sau và ngoài nghiệm thu; phiên bản/lịch chỉ là dự kiến | — | Sửa roadmap, hoãn hạng mục vượt nguồn lực/quyền truy cập thay vì cam kết |
| Q-G | Phản biện đa chiều và kiểm cuối O3 | Nguồn/khoảng thiếu, thiết kế/an toàn, định lượng/roadmap được subagent độc lập kiểm; có kiểm DoD cuối khác tác giả, findings/mâu thuẫn và xử lý được ghi trung thực | — | Sửa tài liệu và tái kiểm phần ảnh hưởng; không cộng phiếu đồng thuận hoặc tự duyệt |
| Q-H | Lint và suite hiện có O3 | Artifact qua lint; suite tại cổng QC đạt, skip giữ nguyên; kết quả cũ không bị trình bày như lần chạy mới; vùng tài liệu không có module không được gọi PASS code coverage | — | Sửa lỗi tài liệu; lỗi suite ngoài phạm vi phải có bằng chứng và báo theo quy trình, không sửa runtime trái scope |
| Q-I | Smoke, biên và giới hạn O1/O3 | Các phép kiểm vô hại khả thi có input/oracle/output thật trên môi trường Windows; biên thiếu trace, dữ liệu không hợp lệ và phục hồi được xem xét; runtime mới không áp dụng có lý do, không dựng tiến trình giả | — | Ghi lỗi/giới hạn và tác động; không gọi lỗi runtime cũ đã vá; xử lý kết luận tài liệu tương ứng |
| Q-J | Quyền ghi và tính toàn vẹn O3 | Source/ECC và hồ sơ cũ không bị sửa; state/log đúng CLI; thay đổi trước request được giữ; không triển khai/commit/push/phát hành trước quyền tương ứng | — | Dừng thao tác ngoài quyền, báo nguồn thay đổi; chỉ gỡ phần do request tạo đã xác minh, không reset dữ liệu người dùng |

Nghiệm thu khi mọi DoD có quyết định rõ và bằng chứng; các lỗi tài liệu được sửa/tái kiểm, không còn finding tài liệu chưa xử lý. Thiếu bằng chứng ảnh hưởng kết luận không được ghi PASS. “Chưa định lượng” có lý do và phương pháp đo là kết luận hợp lệ của nghiên cứu, không đồng nghĩa hiệu quả đã đạt. Quy tắc lệch spec/pause của workflow vẫn áp dụng, không tự hạ tiêu chí.

## 7. Câu hỏi còn mở
