# BRIEF — Đề xuất nâng cấp TDQ Workflow từ ECC toàn diện hơn
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

“okay vậy hãy làm giúp tooi một đề xuất nâng cấp từ ECC đầy đủ hơn”

Cách hiểu ban đầu: tạo bản đề xuất hợp nhất, kế thừa báo cáo D01–D10 tại `docs/tdq/reports/2026-10-17-1442-de-xuat-nang-cap-tu-ecc.md` và đánh giá thêm tám nhóm vừa trao đổi: quản lý ngữ cảnh; học từ lỗi có kiểm duyệt; đánh giá lặp; hậu kiểm dấu vết; định cỡ quy trình theo quy mô/rủi ro; chuyên gia theo lĩnh vực; quản lý nhiều phiên/harness; phân công model. Đây là tám nhóm khảo sát, không mặc định tám tính năng hoặc tám đề xuất độc lập.

Mục tiêu dự kiến: đối chiếu hiện trạng TDQ với nguồn ECC, phân biệt phần đã có/khoảng thiếu/chưa xác minh; gộp phần trùng; đề xuất thay đổi tối thiểu, thứ tự ưu tiên, công sức, lợi ích có điều kiện, rủi ro, phương án không làm và phép đo nghiệm thu. Chỉ phân tích và xuất bản tài liệu; chưa được phép triển khai runtime hay nới cổng duyệt. Nguồn ECC chỉ đọc. Báo cáo cũ là chỉ mục, không phải bằng chứng đủ cho mọi khẳng định hoặc tỷ lệ hiệu quả; phải xác minh lại những kết luận quyết định.

Pipeline đã chốt: chuyên sâu (`full`), theo nguyên văn người dùng “1a”. Loại request: `docs`. Đã chốt khảo sát kỹ cả tám nhóm, Windows/PowerShell trước, macOS/Linux xử lý sau, QC ultra và có thể chia nhiều subagent kiểm định độc lập theo các chiều khác nhau. Không chạy phiên eval model thật tốn phí trong request tài liệu; có thể phân tích tĩnh bộ ca, kết quả đã lưu và phép kiểm cô lập không gọi model. Đầu ra dự kiến Markdown với tóm tắt dễ đọc và phân tích có dẫn nguồn, kế thừa định dạng của hồ sơ trước; không tự thêm dashboard hoặc dịch vụ.

Ghi nhận công cụ ban đầu: đã gọi LSP Python. Tham số scope trong lần gọi đầu tạo cấu hình pyright tạm; đã khôi phục nguyên byte từ backup trùng nội dung và gỡ duy nhất backup do lần gọi tạo. Setup xác nhận ba tầng trả lời được; đồ thị graphify cũ và bằng chứng LSP module Python hết hạn, cần làm mới trước init/khảo sát sâu. Tại lần ghi đầu chưa init state hoặc chuyển nhánh. Sau lựa chọn “1a”, đã ghi bằng chứng LSP Python qua MCP: `bac6_cau_hinh_goc_import`, 7 tham chiếu; check đạt 7/8 với cảnh báo graph cũ không chặn. Đã init request `full`, `doc_lang=vi`, phase `analyze`; nhánh `docs/de-xuat-ecc-toan-dien`, nhánh gốc `docs/deep-research-kien-truc-ecc`. `graphify extract . --code-only` sau đó hoàn tất: 2267 nodes, 4538 edges, 128 communities. Các file dirty trước request được giữ nguyên, không commit/push.

## Hiểu & kiến thức

### Năng lực dùng được

Kiểm kê ngày 2026-10-17: lệnh `skill_inventory.py --loc "ECC research architecture workflow context memory eval trace model routing"` in 10 mục TDQ (header báo kept 9), ẩn 16 mục khác; đã xét thêm danh sách built-in trong context. Chỉ ghi năng lực ảnh hưởng công việc; không coi tên trên đĩa là skill user-invocable nếu danh sách phiên không có.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | Tiếp nhận, phân tích và phỏng vấn |
| tdq-conventions | plugin:tdq-workflow | NỀN | Quy tắc ngôn ngữ, state, Git, tìm kiếm và nhật ký; đọc trực tiếp, không invoke |
| tdq-spec | plugin:tdq-workflow | NỀN | Viết spec; lập plan sau khi spec được duyệt |
| tdq-build | plugin:tdq-workflow | NỀN | Biên soạn, kiểm định và bàn giao theo plan được duyệt |
| tdq-lean | plugin:tdq-workflow | NỀN | Loại đề xuất trùng, không cần thiết và chi phí kiến trúc không có căn cứ |
| Agent | built-in tool | DÙNG | Khảo sát nguồn chỉ đọc và kiểm định độc lập theo hợp đồng sau khi chốt QC |
| Đã xét các mục TDQ tra trạng thái/setup/plan/phục hồi còn lại trên đĩa và 16 skill ngoài bộ TDQ; các built-in còn lại | user/plugin/built-in | KHÔNG | khác lĩnh vực; không cần skill đổi settings, tạo dashboard, gọi API, orchestration workflow hoặc chạy ứng dụng để viết đề xuất cục bộ; phần hướng dẫn setup/plan của TDQ được đọc theo pipeline khi cần |

### Căn cứ và ràng buộc ban đầu

- TDQ HEAD lúc mở request: `1d78ca86ca5b0710f357d8436ec7d9d2d7562b54`; ECC HEAD: `76aaa77df6adc5b889e689007bf99b9a4f74af34`, working tree ECC sạch.
- Đã đọc toàn bộ `docs/kien-truc.md`: header vẫn NHÁP, không tự nâng mọi dòng thành luật đã duyệt; phân biệt các quyết định có ngày trong mục Đã chốt. Giữ các ràng buộc hiện hành về chiều import, ghi state bằng CLI, quyền duyệt và ngân sách suite.
- Báo cáo tổng quan ECC và hồ sơ D01–D10 là chỉ mục lịch sử; không mặc định số liệu, confidence heuristic hay mô tả trong tài liệu chứng minh hiệu quả runtime. Phải phân biệt guideline trong skill/command với enforcement trong code/test.
- Bản đề xuất mới cần ánh xạ D01–D10: giữ, sửa, gộp hoặc hoãn; không ghi đè hồ sơ đã nghiệm thu. Tám nhóm bổ sung có thể trùng khả năng TDQ hiện có; cần kiểm trước khi tạo ID đề xuất mới.
- Hướng học ưu tiên sơ bộ: correctness và bằng chứng trước, thêm cơ chế đo/tuân thủ trước khi tự động học hoặc điều phối phức tạp. Đây là giả thuyết cần đối chiếu, chưa là thứ tự roadmap được duyệt.
- Nghiên cứu web: dự kiến BỎ vì câu hỏi chuyển giao từ hai kho cục bộ, không hỏi giá/model/API/CVE hiện hành. Không có quyền mặc định chạy model trả phí, tải dependency, đọc dữ liệu tài khoản hoặc đưa transcript ra dịch vụ ngoài.
- Vòng scope: CÓ — cụm “đầy đủ hơn” cần chốt độ sâu của tám nhóm và môi trường ưu tiên. Việc hợp nhất D01–D10 với tám nhóm, đầu ra tài liệu và chưa triển khai đã rõ, không hỏi lại các lựa chọn đó.
- Khảo sát ban đầu qua một agent chỉ đọc nguồn đại diện đã hoàn tất, agent xác nhận hai HEAD repo chính; chưa audit toàn bộ. Lời gọi bị truyền worktree thừa; đã nhắc agent dùng tuyệt đối repo chính, không đọc snapshot cwd, không sửa gì. Không nhập thay đổi từ worktree.
- Leader đối chiếu `evals/tuan-thu/README.md:5-23,25-47`: TDQ đã có 12 ca tuân thủ, chạy lặp, lưu transcript và chấm lại tất định. Không được đề xuất “tạo eval lặp từ đầu”; request này chưa cho phép chạy các phiên eval thật tốn phí. Tập hiện có và cách chấm cần khảo sát khoảng thiếu khi triển khai báo cáo.
- Leader đối chiếu `hooks/scripts/session_start.py:239-245`: TDQ đã nhận `source=compact` và chèn `[TDQ:ANCHOR]` chứa request/phase/plan cùng anti-patterns. Kết luận sơ bộ của agent “chưa có hook phát hiện compact” bị bác; hướng khảo sát là độ đầy đủ/chính xác của bản bàn giao, không thêm hook tương tự.
- Các nhận định chưa xác minh trong digest agent (ba lane Quick/Standard/Deep; TDQ chỉ dùng Claude Code; stop gate chặn vì working tree chưa sạch; memory ECC chỉ là khai báo) không được coi là kết luận. Pipeline hiện hành là tier nhỏ và hai lane quick/full; adapter host và thực thi memory phải đối chiếu nguồn trực tiếp trước khi viết báo cáo.
- Lượt trước bị lỗi hệ thống trước khi gửi vòng phỏng vấn. Người dùng nhắn “tiếp tục” chỉ là yêu cầu phục hồi phân tích; không phải chọn các option, mức QC hoặc duyệt spec/plan.

### Phạm vi đã chốt

- Mặt CHỌN: hợp nhất D01–D10 và đối chiếu kỹ cả tám nhóm mới; correctness, độ tin cậy, bằng chứng, hiệu năng/chi phí có điều kiện, an toàn và khả năng bảo trì; chỉ xuất bản tài liệu có tóm tắt dễ đọc.
- Mặt LOẠI: triển khai runtime/PoC sản phẩm, nới gate, engine/daemon mới, chạy eval model thật tốn phí, dashboard, phát hành; triển khai/kiểm thử macOS và Linux để giai đoạn sau, không thuộc nghiệm thu hiện tại.
- Bối cảnh: máy Windows 11 và PowerShell 5.1 hiện tại là mục tiêu; không hứa số đo nền tảng khác. Người dùng cho phép nhiều subagent để QC kỹ hơn, chưa chọn mode triển khai tài liệu.
- Mức đầu tư suy ra: đầy đủ cho nghiên cứu tài liệu — vì đối chiếu nhiều nhóm, cần kiểm chứng nguồn và phản biện độc lập; không tương đương quyền xây hoặc thử sản phẩm mới.

### Lộ trình

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

## Hỏi đáp

### Chọn pipeline

- Câu hỏi: chuyên sâu (A, đề xuất) hay nhanh (B); loại request `docs`.
- Trả lời nguyên văn người dùng: “1a”.
- Ghi nhận vào state: 2026-10-17T16:24:58+07:00; `lane=full`, `phase=analyze`, `doc_lang=vi`. Không dùng lựa chọn này làm duyệt spec/plan hoặc tự đặt QC.

### Vòng phạm vi đã chốt

CLI `get muc_qc` ngày 2026-10-17T16:27 trả `full` chỉ là mặc định sau init. Sau câu trả lời thật dưới đây, CLI đã ghi `muc_qc=ultra` lúc 2026-10-17T16:37:25+07:00; không kế thừa QC request cũ.

Các câu hỏi đã gửi:

1. Độ sâu: A (đề xuất) khảo sát kỹ cả tám nhóm, chỉ lập phiếu triển khai cho khoảng thiếu có căn cứ, còn lại kết luận giữ nguyên/thử/hoãn; B tập trung sâu bốn nhóm ngữ cảnh, học từ lỗi, đánh giá lặp, dấu vết, bốn nhóm còn lại chỉ sàng lọc. D01–D10 vẫn được hợp nhất ở cả hai lựa chọn.
2. Bối cảnh ưu tiên: A (đề xuất) máy Windows/PowerShell hiện tại, giữ tương thích các host đang hỗ trợ nhưng không hứa benchmark nền tảng khác; B đánh giá ngang hàng cả Windows/Linux/macOS và nhiều harness, đánh dấu nền tảng chưa truy cập; C người dùng tự nêu nền tảng/host và số phiên đồng thời cần phục vụ.
3. QC: A (đề xuất) ultra, kiểm nguồn/tính toán độc lập cùng suite hiện có, chỉ smoke vô hại khả thi và không tạo runtime giả; B full, DoD/lint/trọn suite/ràng buộc kiến trúc nhưng không agent QC độc lập; C lite, kiểm tài liệu và vùng chạm, không trọn suite hoặc QC độc lập.
4. Bổ sung: A không, đủ rồi; B có, người dùng nói thêm.

Trả lời nguyên văn người dùng: “1a 2a trước sau này mac và linux sẽ xử lí sau (nhớ note lại) 3a có thể xử lí bằng nhiều sub agent để QC chuẩn hơn 4A”.

Diễn giải: cả tám nhóm đối chiếu kỹ; Windows/PowerShell trước, macOS/Linux ngoài nghiệm thu hiện tại và có ghi backlog; QC ultra, chia các chiều kiểm cho nhiều subagent độc lập, leader tổng hợp và xử lý mâu thuẫn bằng bằng chứng chứ không đa số. Không có yêu cầu bổ sung. Đây không phải lời duyệt spec/plan/mode hoặc cấp quyền chạy model eval trả phí.

Gate analyze: phạm vi và đầu ra rõ; dùng công cụ hiện có, không cài sản phẩm hoặc thêm dịch vụ/model; QC ultra đã ghi state; không còn câu hỏi làm thay đổi sản phẩm. Chuyển sang spec để người dùng duyệt trước khi lập plan.

Ghi nhận phát sinh từ công cụ: `graphify extract . --code-only` sửa hai artifact sinh `graphify-out/graph.json` và `graphify-out/manifest.json`; không sửa mã sản phẩm. Không tự gom các artifact này hoặc thay đổi cũ vào commit báo cáo sau này.
