# SPEC — Đề xuất nâng cấp TDQ Workflow từ ECC và ước tính hiệu quả
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-10-17 · Bản: 1.0 · Lane: full · Ngôn ngữ: vi
Brief: `docs/tdq/brief/2026-10-17-1442-de-xuat-nang-cap-tu-ecc.md`
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

Xuất bản báo cáo giúp người dùng quyết định nên học kỹ thuật nào của ECC, cần điều chỉnh gì cho TDQ Workflow, thứ tự triển khai và hiệu quả dự kiến. Mỗi kết luận phải truy ngược được tới mã nguồn hoặc dữ liệu đo; không biến kỹ thuật có trong ECC thành lý do mặc định để thêm vào TDQ.

Mốc đối chiếu theo brief: TDQ `v0.71.0`, commit `5c8a9c2`; ECC `ecc-universal v2.2.3`, commit `76aaa77d`. Khi thực hiện, xác minh lại commit đầy đủ và ghi riêng thay đổi ngoài snapshot. Tài liệu nghiên cứu ECC đã có là bản đồ nguồn, không thay thế việc đọc mã nguồn cho kết luận quan trọng.

### Trong phạm vi

- **Hooks & Latency:** số tiến trình thực sự được kích hoạt theo matcher/sự kiện, đường găng độ trễ, dispatcher, nhắc/chặn sai; đánh giá denial dampening và trivial-edit bypass mà không làm suy yếu quyền duyệt.
- **Multi-Agent & Worktree:** dependency graph và cách chia wave hiện tại so với TCAS/proximity; fingerprint plan, vòng đời worktree, cache theo lockfile và yêu cầu cô lập.
- **Quality & Review:** phản biện độc lập kiểu `orch-review`, khả năng truy vết phát hiện đến bằng chứng, precision/recall và chi phí kiểm chứng; phòng ngừa kết luận PASS không có căn cứ.
- **Shell Safety:** độ phủ Bash/PowerShell, scanner có ngân sách, quoting/nesting/encoding, đường thất bại và những cách diễn giải nằm ngoài khả năng parser.
- **Cross-Platform Stability:** chọn shell, WSL stub, đường dẫn Windows, dependency và điều kiện liên quan các lỗi bảo mật ECC đã xử lý; phân biệt tương đồng kỹ thuật với lỗ hổng đã được chứng minh tại TDQ.
- Đề xuất chi tiết, công thức và giả mã khi giúp giải thích chuyển giao; dữ liệu đo nền không phá hoại; ma trận ưu tiên và ước tính thấp/cơ sở/cao có căn cứ.
- Lộ trình phân kỳ gắn nhãn dự kiến `v0.72.0–v0.75.0`, nêu dependency, điều kiện bắt đầu/kết thúc, go/no-go và rollback. Cho phép giữ nguyên hiện trạng hoặc hoãn một kỹ thuật.

### Ngoài phạm vi

- Không sửa hoặc triển khai runtime, hook, parser, bộ điều phối, state machine, cache hay policy của TDQ/ECC.
- Không cài sản phẩm mới, thêm dependency runtime, tích hợp dịch vụ/model/API mới; không benchmark bằng lệnh phá hoại hoặc thao tác trên dữ liệu thật của người dùng.
- Không tự động hạ gate thành cảnh báo sau nhiều lần bị chặn; không coi symlink dependency ghi được giữa các worktree là mặc định an toàn.
- Không dựng dashboard HTML, UI, biểu đồ hoặc phát hành phiên bản; các mốc phiên bản chỉ phục vụ quyết định roadmap.
- Không research web/CVE hiện hành trong request này; không kết luận TDQ mắc hoặc đã vá một CVE chỉ dựa trên lịch sử ECC.
- Không cam kết phần trăm tăng chất lượng, giảm xung đột hoặc tiết kiệm token khi chưa có tập mẫu và phương pháp đo tương ứng.

## 1b. Lộ trình

Giữ lộ trình đã chốt tại brief. Duyệt spec đồng thời duyệt lộ trình, không thay thế cổng duyệt plan hoặc lựa chọn chế độ thực thi.

| Bước/phase | Chạy? | Skill/công cụ | Vì sao |
|---|---|---|---|
| Khảo sát mã nguồn và đo nền | CÓ | LSP, tìm kiếm chính xác, phép đo cô lập | Đối chiếu hai snapshot; chỉ đọc nguồn, không sửa runtime |
| Research web | BỎ | Không dùng | Chuyển giao nội bộ từ nguồn cục bộ; không đưa khẳng định CVE ngoài bằng chứng |
| Interview | CÓ — đã xong | tdq-intake | Đã chốt `1a 2a 3b` và `4a`; không mở vòng chọn phạm vi mới |
| Spec → plan | CÓ | tdq-spec → tdq-plan | Duyệt phạm vi, rồi duyệt cách thực hiện; không chen bước giữa hai cổng |
| Implement báo cáo | CÓ | tdq-build | Biên soạn Markdown, bằng chứng, ước tính; không nâng cấp tính năng |
| QC ultra | CÓ | tdq-qc-tester và kiểm tra hiện có | Trọn suite tại cổng QC, kiểm nguồn và tái lập phép đo vô hại; thẩm định độc lập |
| Report | CÓ | tdq-build | Tóm tắt ưu tiên, giới hạn và đề nghị request triển khai riêng |
| Vision Test Loop | BỎ | Không dùng | Không có đầu ra giao diện hoặc mẫu thị giác |

Các luồng đầu ra: chứng cứ nguồn → đánh giá từng trụ cột → đo/ước tính → ưu tiên và roadmap → QC độc lập. Khảo sát ở phase spec chỉ làm rõ hợp đồng; nội dung báo cáo và phép đo đầy đủ thuộc plan được duyệt sau này.

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo “xong” bằng |
|---|---|---|---|
| O1 | Hồ sơ bằng chứng và phương pháp đo | `docs/tdq/research/2026-10-17-1442-de-xuat-nang-cap-tu-ecc.md` | Có snapshot, nguồn TDQ/ECC `file:line`, quan hệ gọi/import, dữ liệu nền, môi trường, lệnh tái lập và giới hạn |
| O2 | Báo cáo đề xuất tổng hợp | `docs/tdq/reports/2026-10-17-1442-de-xuat-nang-cap-tu-ecc.md` | Bao phủ mọi trụ cột, phiếu đề xuất chi tiết, công thức, ma trận chi phí/lợi ích/ưu tiên, roadmap và kết luận không làm/hoãn |
| O3 | Hồ sơ kiểm định độc lập | `docs/tdq/qc/2026-10-17-1442-de-xuat-nang-cap-tu-ecc.md` | Ánh xạ DoD → bằng chứng, kết quả suite/lint, kiểm chứng số liệu và nguồn, phát hiện của QC độc lập cùng xử lý |

Dữ liệu nền dạng bảng, mẫu đo và lệnh tái lập nằm trong O1; không tự thêm hệ thống benchmark hoặc tệp mã nguồn. Báo cáo O2 đồng thời làm report kết thúc request, tránh một tài liệu tổng kết lặp lại. Các file brief/spec/plan, state sinh bởi CLI và working log là hồ sơ workflow, không phải sản phẩm nâng cấp runtime.

## 2b. Ranh giới module

Đây là request tài liệu: ranh giới ghi file là chuỗi bằng chứng → tổng hợp → kiểm định, không chia quyền sửa runtime theo tên thư mục. Các trụ cột có thể khảo sát song song nhưng không cùng ghi một báo cáo.

| Module | Vùng file được ghi | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| Hồ sơ chứng cứ | `docs/tdq/research/2026-10-17-1442-de-xuat-nang-cap-tu-ecc.md` | Nguồn TDQ/ECC chỉ đọc | O1 |
| Tổng hợp quyết định | `docs/tdq/reports/2026-10-17-1442-de-xuat-nang-cap-tu-ecc.md` | Hồ sơ chứng cứ | O2 |
| Kiểm định độc lập | `docs/tdq/qc/2026-10-17-1442-de-xuat-nang-cap-tu-ecc.md` | Hồ sơ chứng cứ, tổng hợp quyết định | O3 |

Căn cứ semantic bước spec, xác minh bằng LSP trên nguồn TDQ và đối chiếu manifest:

- `scripts/tdq_state.py:1958` trong `_cli_approve` gọi `_file_changed_since_approval` tại `scripts/tdq_state.py:1876`; cổng duyệt và fingerprint không phải một vùng độc lập với state.
- `scripts/tdq_team.py:375` trong `_boi_canh` gọi `sha_file` tại `scripts/tdq_team.py:345` để kiểm plan thay đổi. TDQ đã có fingerprint plan; báo cáo phải đánh giá khoảng thiếu, không đề xuất thêm như tính năng hoàn toàn mới.
- `hooks/hooks.json:58-65` nối matcher `Bash` tới `hooks/scripts/bash_gate.py`; `hooks/hooks.json:104-112` nối `mcp__lsp__.*|Bash` tới `search_observe.py`. Đây là dependency cấu hình cần kiểm ngoài reference tĩnh; độ phủ PowerShell phải khảo sát theo từng đường tích hợp, không suy ra từ tên hook.

Quan hệ semantic đầy đủ của nguồn phải được ghi ở O1: entry point → caller/import thực tế → vùng ảnh hưởng. Không suy ra độc lập từ thư mục; LSP không có reference hoặc graph cũ không chứng minh không có liên hệ. LSP lượt này xác minh được điều hướng nội bộ file nhưng có lỗi phân giải import xuyên thư mục; các quan hệ nạp động phải kiểm thêm manifest/CLI và nguồn.

Nguồn khảo sát: snapshot `C:/Users/admin/Documents/ECC`; báo cáo trước tại `docs/tdq/reports/2026-10-17-1208-deep-research-kien-truc-ecc.md`. Vị trí snapshot lấy từ spec request trước và phải xác minh commit trước khi dùng cho O1.

## 3. Cách tiếp cận & lý do

### Phần mới so với nghiên cứu ECC hiện có

Nghiên cứu trước giải thích ECC hoạt động thế nào. Báo cáo này đối chiếu từng kỹ thuật với vấn đề thật của TDQ, phần TDQ đã có, thay đổi tối thiểu còn thiếu, chi phí và điều kiện chấp nhận. Không chép lại catalogue ECC thành roadmap.

### Quy trình bằng chứng

- Xác minh snapshot và khu vực nguồn trước khi kết luận. Tra quan hệ bằng LSP; tra tên chính xác bằng tìm kiếm văn bản. Graphify chỉ hỗ trợ định hướng nếu đồ thị còn mới; đồ thị cũ rơi xuống LSP và tìm kiếm nguồn.
- Mỗi khẳng định mang nhãn: **đã kiểm chứng**, **ước tính có giả định**, **chưa đủ dữ liệu**, hoặc **không áp dụng**. Trích dẫn tài liệu thứ cấp không được trình bày như đã xác minh trực tiếp runtime.
- Mỗi đề xuất có ID ổn định, vấn đề quan sát được, nguồn TDQ/ECC, cơ chế/giả mã, thay đổi tối thiểu và điểm tích hợp, phương án không làm, dependency, chi phí triển khai/duy trì, rủi ro, rollback, phép đo xác nhận và tiêu chí go/no-go.
- Ưu tiên theo mức nghiêm trọng của vấn đề đã xác minh, độ chắc của chứng cứ, lợi ích, công sức và phụ thuộc. Giải thích từng quyết định; không tạo điểm tổng hợp chính xác giả tạo từ nhận định chưa hiệu chuẩn.

### Ước tính và phép đo

- Hook: đo warm/cold, startup, số hook thực sự khớp sự kiện, chi phí dispatch; phân biệt tổng thời gian CPU với wall-clock/đường găng. Công thức thành phần: `số_lần_gọi × số_process_giảm × startup − overhead_dispatch`; không gọi đây là mức cải thiện đã đo của một dispatcher chưa được triển khai.
- Worktree/cache: `thời_gian_cài_tránh_được − kiểm_tra_cache − cô_lập − bảo_trì_phân_bổ`. Không có dependency nặng thì có thể kết luận chưa đáng làm; không dựng dependency giả để tạo ROI đẹp.
- Scheduling: đánh giá hành vi chia wave/dependency hiện có trên trường hợp nhỏ có oracle; tần suất xung đột thật cần lịch sử đủ tin cậy. Thiếu lịch sử thì mô tả cơ chế và điều kiện thử nghiệm, không gán tỷ lệ giảm xung đột.
- QC: precision/recall phải dựa vào nhãn độc lập và mẫu lỗi thực. Confidence model không phải xác suất đúng đã hiệu chuẩn; khi chưa có corpus, ghi chưa định lượng và mô tả phép thử cho request sau.
- Shell/Windows: dùng chuỗi đầu vào và thư mục tạm vô hại; kiểm giới hạn parser, nhánh từ chối/không hỗ trợ và false positive. Không thực thi payload có tác dụng phá hoại để chứng minh cảnh báo.
- Mỗi phép đo ghi OS, shell, Python/tool version, commit, điều kiện warm/cold, đơn vị, số mẫu, giá trị thô, cách tính median/p95 và sai lệch. Mẫu ít thì nêu độ không ổn định của p95, không dùng làm SLA.
- Kịch bản thấp/cơ sở/cao phải xuất phát từ dữ liệu hoặc giả định được công khai. Đầu vào chưa có: ghi “chưa định lượng”, nêu dữ liệu cần thu và cách quyết định tạm thời; không điền số minh họa như số thực.
- Tách giờ người, thời gian máy và token; ROI/hoàn vốn dùng đơn vị thống nhất. Chỉ quy đổi thành tiền khi có đơn giá được chỉ rõ; không cộng chồng lợi ích cùng điểm nghẽn.

Đã loại: triển khai PoC runtime ngay (ngoài phạm vi đã chọn), cam kết tốc độ Windows từ benchmark macOS cũ, tự động áp dụng TCAS/cache/dispatcher chỉ vì ECC có, và đặt confidence cố định làm bằng chứng chất lượng.

## 3b. Năng lực & công cụ

Chép kiểm kê đã chốt trong brief; tên skill không có trong danh sách khả dụng được đọc hướng dẫn cục bộ tương ứng, không đoán hoặc gọi skill chưa có.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| Agent | built-in | DÙNG | Triệu hồi subagent phân tích chi tiết từng phân hệ mã nguồn TDQ Workflow và thẩm định QC |
| tdq-intake | plugin:tdq-workflow | NỀN | mở request, phỏng vấn và chuyển phase |
| tdq-spec | plugin:tdq-workflow | NỀN | lập đặc tả kỹ thuật cho bản đề xuất nâng cấp |
| tdq-plan | plugin:tdq-workflow | NỀN | lập kế hoạch phân tách task nghiên cứu và biên soạn |
| tdq-build | plugin:tdq-workflow | NỀN | thực thi biên soạn tài liệu đề xuất và kiểm thử |
| tdq-conventions | plugin:tdq-workflow | NỀN | quy tắc workflow, ngôn ngữ 3 tầng |
| tdq-status | plugin:tdq-workflow | NỀN | kiểm tra trạng thái tiến độ |
| tdq-lean | plugin:tdq-workflow | NỀN | bảo đảm cấu trúc đề xuất tinh gọn, thực tiễn |
| tdq-setup | plugin:tdq-workflow | NỀN | kiểm tra LSP và môi trường |
| tdq-check-status | plugin:tdq-workflow | NỀN | phục hồi phiên khi có sự cố |
| Đã xét 16 skill trên đĩa ngoài bộ TDQ và các skill built-in còn lại | user/plugin/built-in | KHÔNG | khác lĩnh vực; không dựng dashboard nên không dùng dataviz |

## 4. Yêu cầu bắt buộc

- Log service: BỎ — chỉ xuất bản tài liệu, không tạo hoặc sửa runtime. Working log vẫn ghi qua công cụ kết thúc lượt; hồ sơ phép đo có timestamp và đủ đầu vào để tái lập.
- Không placeholder, TODO stub hoặc dữ liệu giả được trình bày như dữ liệu thật. “Chưa định lượng” phải đi cùng nguyên nhân và phép đo tiếp theo, không thay cho việc khảo sát khả thi trong môi trường hiện có.
- Mỗi đầu ra có kiểm tra riêng tại §6; plan quy định lệnh kiểm và người thực hiện. Không thêm unit test runtime cho một request chỉ viết tài liệu.
- Mọi trụ cột đều có kết luận, kể cả không áp dụng. Mọi đề xuất được ưu tiên đều có bằng chứng, phương án giữ nguyên hiện trạng và cách kiểm chứng hiệu quả.
- Báo cáo và trao đổi bằng tiếng Việt, giữ nguyên tên kỹ thuật. Giả mã chỉ để giải thích, không được ghi như implementation đã chạy.
- Chỉ ghi state qua `scripts/tdq_state.py`; không sửa thủ công state/mirror. Không tự duyệt spec/plan, chọn chế độ thực thi, commit, push hoặc phát hành.
- Nguồn ECC chỉ đọc. Nếu request triển khai sau sao chép phần đáng kể mã nguồn MIT, phải giữ notice giấy phép; quy tắc không attribution trong commit không thay nghĩa vụ giấy phép.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ: request này không sửa kiến trúc thực thi. Các dòng nguyên văn liên quan từ `docs/kien-truc.md`:

- Dòng 21–22: “hooks/ được gọi scripts/; scripts/ không được import hooks/ — hook chạy trong tiến trình của Claude Code, kéo ngược sẽ buộc CLI phụ thuộc môi trường hook.” Áp dụng khi đề xuất dispatcher và tái sử dụng helper.
- Dòng 25: “Chỉ scripts/tdq_state.py được ghi docs/tdq/state.json; mọi nơi khác chỉ đọc qua CLI.” Áp dụng cho fingerprint, evidence và điều phối worktree.
- Dòng 47: “2026-07-29: hook chỉ nhắc và kiểm bằng hiệu ứng thật, không trả deny vì lý do \"chưa duyệt\".” Phải phân biệt nhắc ở hook với từ chối của lệnh duyệt; không dùng denial dampening để thay đổi quyền duyệt.
- Dòng 67–68: “2026-10-03 (yêu cầu 1907): trọn bộ test chỉ chạy ở 2 cổng. QC-F1 (thay lần chạy riêng \"xong mọi task\", vì code không đổi giữa hai lần) và một lần sau vòng sửa QC CUỐI khi có sửa.” Áp dụng cho phương án kiểm định; không tăng lượt suite trùng nhau.

Quyết định tại `docs/kien-truc.md:78-81` đặt kiểm R14 tại lệnh `approve spec`, không tại hook. Quyết định tại `docs/kien-truc.md:104-105` giữ mức QC do người dùng chọn; request này đã chốt `ultra`. Mọi phương án thay đổi các quyết định kiến trúc trên chỉ là đề nghị cần request và phê duyệt riêng.

Không thêm model/dịch vụ/API runtime. Công cụ model của phiên chỉ phục vụ biên soạn/thẩm định; không ấn định model ID, đơn giá hoặc lượng token chưa đo. Không tải/cài dependency phục vụ sản phẩm; dùng snapshot và công cụ hiện có. Thiếu nguồn hoặc môi trường tái lập phải ghi giới hạn, không tải hoặc chạy mã bên ngoài một cách ngầm định.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Các mô tả sơ bộ trong brief chưa được chứng minh | Roadmap dựa trên vấn đề không có thật | Kiểm nguồn, ghi trạng thái chứng cứ; loại hoặc sửa giả thuyết khi trái mã nguồn |
| Graph cũ, reference thiếu do import động | Bỏ sót dependency/caller | LSP kết hợp manifest và nguồn; không suy luận phủ định từ kết quả rỗng |
| Cộng startup hook khi host chạy song song | Phóng đại lợi ích | Đo số tiến trình và đường găng; tách mô hình khỏi phép đo end-to-end |
| Cache dùng chung có thể bị ghi, lockfile không đủ phản ánh môi trường | Rò trạng thái và test xanh sai | Đánh giá OS/ABI/toolchain, quyền ghi, invalidation và cô lập; giữ phương án không dùng cache |
| Giảm chặn sai đồng thời giảm bảo vệ | Mất cổng duyệt/an toàn | Denial dampening không tự thay quyền quyết định; có ma trận tình huống hợp lệ và phải chặn |
| Dùng confidence để thay ground truth | Báo tăng chất lượng giả | Tập nhãn độc lập hoặc kết luận chưa định lượng; theo dõi chi phí false positive/false negative |
| Suy diễn CVE từ ECC sang TDQ | Kết luận bảo mật sai | Chỉ mô tả điều kiện đã xác minh, không nhận là lỗ hổng nếu thiếu đường thực thi tương ứng |
| Benchmark hoặc suite có side effect | Làm đổi môi trường, nguồn hoặc state thật | Thư mục tạm và môi trường kiểm thử cô lập; đối chiếu trạng thái git trước/sau |
| Roadmap có nhãn phiên bản bị hiểu là cam kết | Tự mở rộng phạm vi | Ghi rõ dự kiến, dependency và cổng quyết định; request này không phát hành |

## 6. QC & Definition of Done

Mức QC: **ultra**, có kiểm định độc lập bằng `tdq-qc-tester`. Không đặt ngưỡng hiệu năng số cho chức năng chưa triển khai; đo nền là bằng chứng để ước tính, không phải cam kết cải thiện. Lệnh kiểm cụ thể thuộc plan.

| # | Hạng mục kiểm | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |
|---|---|---|---|---|
| Q-A | O1 — nguồn và snapshot | Mỗi kết luận kỹ thuật quan trọng truy được về commit và vị trí nguồn; phân biệt nguồn trực tiếp/gián tiếp; không khẳng định quan hệ chỉ từ tên thư mục | — | — |
| Q-B | O1 — tái lập phép đo | Có môi trường, đầu vào, dữ liệu thô, cách tính và lệnh tái lập; người kiểm định tính lại được kết quả; mọi phép đo không thực hiện được đều nêu lý do và ảnh hưởng | — | — |
| Q-C | O2 — phủ phạm vi | Từng trụ cột tại §1 có hiện trạng, kỹ thuật ECC, khoảng thiếu của TDQ và kết luận áp dụng/điều chỉnh/hoãn/không làm | — | — |
| Q-D | O2 — đề xuất khả thi | Mọi đề xuất có đủ trường quy định tại §3; không bỏ phương án không làm, dependency, chi phí, rollback và go/no-go | — | — |
| Q-E | O2 — ước tính trung thực | Phân biệt số đo và dự báo; có kịch bản và giả định khi đủ dữ liệu; không cộng chồng lợi ích hoặc trộn đơn vị; mục thiếu dữ liệu ghi rõ chưa định lượng | — | — |
| Q-F | O2 — roadmap | Mỗi giai đoạn có thứ tự, phụ thuộc và điều kiện chuyển; nhãn phiên bản là dự kiến; không giả định quyền triển khai/phát hành đã được duyệt | — | — |
| Q-G | O3 — QC độc lập | Có kết luận độc lập, đối chiếu nguồn và tính toán, lỗi phát hiện và xử lý; mọi điểm chưa kiểm được được ghi rõ, không tự gọi PASS toàn bộ | — | — |
| Q-H | Toàn bộ tài liệu và hồi quy | Tài liệu qua lint; trọn suite hiện có được chạy ở cổng QC; lỗi môi trường/lỗi tồn tại từ trước có bằng chứng riêng, không che thành PASS | — | — |
| Q-I | Giữ phạm vi và quyền duyệt | Không sửa nguồn/runtime hoặc dữ liệu ECC, không nới gate, không phát hành; state thay đổi qua CLI và các thay đổi ngoài request được giữ nguyên | — | — |

### Kịch bản kiểm theo hành trình người đọc

- **Luồng chính — Given:** người dùng cần chọn đề xuất để triển khai. **When:** đọc báo cáo và lần theo một đề xuất được ưu tiên. **Then:** truy được vấn đề TDQ, kỹ thuật ECC, bằng chứng, chi phí/lợi ích, điều kiện đo lại và vị trí trong roadmap.
- **Biên thiếu dữ liệu — Given:** chưa có corpus lỗi có nhãn hoặc lịch sử xung đột đủ tin cậy. **When:** đọc mục hiệu quả QC/scheduling. **Then:** thấy “chưa định lượng”, dữ liệu cần bổ sung và quyết định tạm thời; không gặp tỷ lệ cải thiện bịa đặt.
- **Biên lợi ích không có — Given:** dependency nhẹ hoặc cơ chế tương đương đã tồn tại. **When:** đánh giá cache/TCAS. **Then:** báo cáo có thể kết luận giữ nguyên, không ép áp dụng vì ECC có kỹ thuật đó.
- **Thất bại và phục hồi — Given:** nguồn trích dẫn sai vị trí hoặc phép đo không tái lập. **When:** QC độc lập phát hiện. **Then:** sửa nguồn/tính toán hoặc rút kết luận và ghi giới hạn; kiểm lại phần bị ảnh hưởng trước khi công bố hoàn thành.

**DoD:** O1–O3 đầy đủ, ánh xạ Q-A–Q-I có bằng chứng; thẩm định độc lập đã thực hiện, lỗi còn mở hoặc kiểm tra không chạy được được nêu trung thực. Không tuyên bố hoàn tất QC khi còn lỗi chưa xử lý. Vision Test Loop không áp dụng vì không tạo UI hoặc mẫu thị giác. Duyệt spec chỉ cho phép viết plan; triển khai báo cáo đợi các cổng tiếp theo.

## 7. Câu hỏi còn mở
