# BRIEF — Đề xuất chi tiết và ước tính hiệu quả nâng cấp TDQ Workflow từ các giải thuật tinh hoa của ECC

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> "okay mở request phân tích kĩ và check xem có thể học hỏi gì từ ECC và update TDQ-Workflow để hoạt động tốt và ổn định hơn hãy phân tích và cho tôi đề xuất chi tiết và ước tính hiệu quả"

### Đọc bước đầu

- **Mục tiêu**:
  1. Phân tích chi tiết khả năng ứng dụng các phát hiện kiến trúc, tính năng và giải thuật cốt lõi từ dự án ECC (`ecc-universal` `v2.2.3`) vào mã nguồn và hệ thống quy tắc của `TDQ Workflow` (`v0.71.0`).
  2. Xây dựng bản đề xuất nâng cấp chi tiết (Proposal Roadmap) phân chia theo 5 trụ cột then chốt:
     - **Trụ cột 1 (Hooks & Latency)**: Đánh giá dispatcher và giảm nhắc/chặn sai; giữ nguyên quyền duyệt và ngữ nghĩa từng hook.
     - **Trụ cột 2 (Multi-Agent & Worktree)**: So sánh TCAS với dependency graph đã có; đánh giá fingerprint plan, vòng đời worktree và cache cô lập.
     - **Trụ cột 3 (Quality & Review)**: Đánh giá phản biện độc lập từ `orch-review`, truy vết bằng chứng và ngăn báo xanh sai.
     - **Trụ cột 4 (Shell Safety)**: Đánh giá độ phủ Bash/PowerShell, parser có ngân sách và giới hạn nhận diện; không cam kết chặn mọi lệnh nguy hiểm.
     - **Trụ cột 5 (Cross-Platform Stability)**: Xác minh vấn đề chọn shell, đường dẫn và dependency trên Windows; không mặc định TDQ mắc CVE chỉ vì ECC có bản vá.
  3. Đo đạc và ước tính định lượng hiệu quả mang lại (tiết kiệm thời gian wall-clock, giảm context token bloat, ngăn ngừa xung đột git merge, tăng tỷ lệ phát hiện lỗi thực chất).

## Hiểu & kiến thức

### Năng lực dùng được

Phân vân → DÙNG. Kiểm kê ngày 2026-10-17: 9 skill trên đĩa, cộng skill built-in trong context. Không xoá bảng này kể cả khi không có dòng DÙNG nào.

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

### Tổng hợp khảo sát và phản biện ngày 2026-10-17

Ba nhóm đã hoàn tất. Kết quả agent là đầu vào nghiên cứu, không tự động trở thành kết luận đã kiểm chứng. Các nhận định khởi đầu về startup 80–150 ms, tiết kiệm 3–5 giây, thiếu QC độc lập và TDQ mắc CVE được rút lại vì chưa đủ bằng chứng.

| Chủ đề | Bằng chứng và trạng thái | Hướng đánh giá trong báo cáo |
|---|---|---|
| Báo xanh khi thiếu artifact | Đã đọc trực tiếp `tests/test_report_kien_truc_ecc.py:211-225`: thiếu báo cáo thì assert fixture hợp lệ rồi return | Ưu tiên ngăn fallback che artifact thiếu; fixture chỉ dùng test validator, không thay sản phẩm thật; không dùng SKIP làm bằng chứng xuất bản |
| Matcher PowerShell | Đã đọc `hooks/hooks.json:58-71,104-109`: `bash_gate` và PostToolUse observer chưa bao phủ PowerShell; `bash_gate.py:2-12,89-155` chỉ observe/remind | Mở rộng parity quan sát/nhắc nhở trước; không mô tả hiện trạng là hard security gate hoặc tăng tỷ lệ chặn từ 0 lên 100 |
| Stale team map | Đã đọc `scripts/tdq_team.py:345-377`: SHA toàn file được dùng để từ chối map stale | Đánh giá fingerprint cấu trúc task, vùng file, dependency, command; tiến độ đọc riêng, không bỏ qua thay đổi phạm vi/DoD |
| Hash duyệt | `scripts/tdq_state.py:569-589` đã loại metadata; `_file_changed_since_approval:1876-1888` phục vụ nhận diện lệnh duyệt lặp | Không suy từ hàm này rằng mọi tick plan bị cổng duyệt chặn; cần trace caller và tái lập trước khi đề xuất đổi hash duyệt |
| Bằng chứng QC | Đã đọc `scripts/tdq_state.py:881-917`: tally kết quả bảng, không xác thực lệnh/output; bản thân tally không chứng minh vượt mọi cổng | Đánh giá evidence record gắn ID DoD, snapshot, lệnh, exit code và artifact, kèm tái chạy độc lập; độ dài chuỗi và số dòng PASS không chứng minh chân thực |
| Lập lịch hiện có | Nhóm team dẫn `scripts/tdq_team.py:177-332`: đã có `Cần:`, critical path và wave tránh đụng file | Không thay scheduler bằng TCAS mặc định; import coupling là tín hiệu review, không tự biến thành thứ tự task bắt buộc vì dễ tạo chu trình hoặc giảm song song vô ích |
| Vòng đời worktree | Nhóm team dẫn `scripts/tdq_team.py:640-659,1142-1252`: worktree tích hợp có thể không có ledger row | Xác minh invariant trước đề xuất đăng ký role tích hợp; không tự xóa worktree bẩn, đang dùng hoặc chưa merge |
| Cache dependency | Nhóm team dẫn `ECC/ecc2/src/worktree/mod.rs:1222-1365`: fingerprint và symlink dependency | Không chia sẻ writable node_modules/.venv/target mặc định; `VIRTUAL_ENV`/PATH vẫn có thể trỏ chung môi trường ghi được, đổi npm cache không cô lập mọi cache build |
| ECC review và shell | Nhóm nghiên cứu dẫn `ECC/workflows/orch-review.workflow.js`, `ECC/scripts/hooks/lib/shell-scan.js` và `ECC/scripts/lib/powershell-destructive-command.js` | Phải xác minh từng cơ chế và phạm vi thật; confidence không phải xác suất; không strip mọi heredoc vì nội dung có thể là chương trình đưa cho interpreter hoặc chứa expansion |
| Windows | Nhóm hooks dẫn `ECC/scripts/lib/windows-bash.js:19-46` | Chỉ đề xuất resolver khi có call-site TDQ cần nó; không đồng nhất System32 launcher với mã độc; không tự cắt ADS rồi coi đường dẫn an toàn |

### Số đo do agent báo — chưa dùng làm baseline đã tái lập

Nhóm hooks báo mẫu startup Python gồm 25 lượt, median/p95 lần lượt 23,0/27,9 ms cho tiến trình trắng và 33,8/37,7 ms khi import stdlib. Kết quả trả về chưa kèm mảng mẫu và transcript lệnh nên chỉ là dữ liệu tham khảo cần tái đo. Không suy ra tiết kiệm critical path từ tổng chi phí process, không xác nhận thông tin SSD/CPU ngoài bằng chứng thu được.

### Giải pháp bị loại hoặc cần điều kiện

- Không port toàn bộ GateGuard/TCAS, không thêm daemon hay Node runtime chỉ để gộp hook.
- Không tự hạ gate duyệt/an toàn theo số lần bị từ chối; nhắc nhở và hard gate phải phân biệt.
- Không đặt ngưỡng độ dài evidence hoặc đếm số PASS thay cho đối chiếu ID DoD và tái chạy.
- Không ép tick PASS DoD trước QC khi chính QC mới tạo bằng chứng; cần phân biệt chưa kiểm, đạt, không đạt và không áp dụng.
- Không coi chia sẻ writable dependency là an toàn chỉ vì lockfile trùng; fingerprint cần xét toolchain/platform và vòng đời invalidation.
- Không gán 100% cải thiện, overhead dưới 1–2 ms, quét graph dưới 200 ms hoặc tiết kiệm 4–6 lượt model khi chưa đo.
- TDQ đã có QC độc lập, AST vùng-chạm, R11 và R14. Phân biệt thiếu cơ chế với cơ chế sẵn có nhưng lần thực thi trước không tuân thủ.

### Phương pháp ước tính và ràng buộc

- Mỗi đề xuất có vấn đề quan sát được, bằng chứng TDQ/ECC `file:line`, thay đổi tối thiểu, phương án không làm, chi phí triển khai/duy trì, rủi ro, rollback, phép đo và tiêu chí go/no-go.
- Tiết kiệm hook dự kiến: `N_lần_gọi × số_process_bớt_được × thời_gian_startup - overhead_dispatch`. Đây là chi phí thành phần, không đồng nhất với độ trễ toàn phiên; nếu host chạy hook song song, đo critical path thay vì cộng mọi thời gian.
- Lợi ích QC: đo precision/recall trên tập lỗi có nhãn và chi phí review; confidence tự chấm không phải xác suất đúng đã hiệu chuẩn. Thiếu mẫu thì ghi chưa định lượng, không gán phần trăm.
- Cache: lợi ích = thời gian cài đặt tránh được − thời gian kiểm tra/cô lập; dự án không có dependency nặng thì có thể không đáng triển khai.
- ROI và thời gian hoàn vốn phải dùng cùng đơn vị; tách thời gian người, thời gian máy và chi phí token. Không cộng chồng lợi ích các đề xuất dùng chung một điểm nghẽn.
- Bộ hằng số cũ `docs/tdq/bench/2026-08-17-2001-smoke-test-main-vs-doi-thuc-do.json:3-19` đo trên macOS/Python 3.12.13, chỉ 3 mẫu task thật, có hằng số stub; không suy ra tốc độ Windows hiện tại hoặc tốc độ toàn bộ request.
- `docs/kien-truc.md` còn tiêu đề NHÁP nhưng có các quyết định đã chốt: giữ cổng duyệt, chỉ ghi state qua CLI, không import ngược hooks vào scripts, trọn suite ở các cổng QC; proposal không tự thay đổi quyết định đó.
- Graphify hiện có 2267 nodes; truy vấn kiến trúc bị cắt 81/184 nodes và đồ thị đã cũ. Chỉ dùng định hướng, không dùng để chứng minh không có dependency.
- ECC `LICENSE:1-13` là MIT: nếu sau này sao chép phần đáng kể mã nguồn, phải giữ notice giấy phép; quy tắc không attribution trong commit không thay thế nghĩa vụ giấy phép.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Khảo sát mã nguồn và đo nền | CÓ | Đối chiếu trực tiếp hai snapshot; phép đo chỉ đọc, không sửa runtime |
| Research web | BỎ | Đánh giá chuyển giao nội bộ từ mã nguồn; không khẳng định tình trạng CVE ngoài bằng chứng cục bộ |
| Interview | CÓ | Đã chốt `1a 2a 3b`; không cần vòng scope mới vì chỉ đề xuất cả năm trụ cột |
| Spec → plan | CÓ | Duyệt phạm vi báo cáo trước, rồi duyệt cách thực hiện |
| Implement báo cáo | CÓ | Biên soạn Markdown, bảng bằng chứng và phương pháp ước tính; không triển khai tính năng |
| QC ultra | CÓ | Trọn suite tại cổng QC, tái lập phép đo vô hại, kiểm tra nguồn, thẩm định độc lập; mục không áp dụng phải ghi rõ |
| Report | CÓ | Tóm tắt ưu tiên, giới hạn ước tính và đề nghị request triển khai riêng |

## Hỏi đáp

### Vòng 1 (2026-10-17 14:45)

1. **Phạm vi đầu ra mong muốn của bản đề xuất**:
   - A (đề xuất): Xuất bản **Báo Cáo Đề Xuất Nâng Cấp Toàn Diện & Ước Tính Hiệu Quả** (kèm ma trận định lượng ROI, công thức toán học/giải thuật chi tiết, đánh giá rủi ro và lộ trình nâng cấp phân kỳ từ v0.72.0 đến v0.75.0).
   - B: Xuất bản tài liệu đề xuất VÀ đồng thời triển khai thực nghiệm ngay 1-2 tính năng an toàn nhẹ có thể áp dụng tức thì (ví dụ: bộ quét an toàn shell và cơ chế giảm xóc Denial Dampening cho hooks).
2. **Trọng tâm ưu tiên trong các nhóm giải thuật học hỏi từ ECC**:
   - A (đề xuất): Toàn diện cả 5 trụ cột (1. Hooks & Latency; 2. TCAS & Worktree Cache; 3. Adversarial Skeptic Review; 4. scanShell & Shell Safety; 5. Windows Hardening).
   - B: Tập trung chủ yếu vào Trụ cột 1 & 2 (Tối ưu hiệu năng Hooks và cơ chế Đa Agent Worktree).
   - C: Tập trung chủ yếu vào Trụ cột 3 & 4 (Nâng cao chất lượng Review và An toàn Shell).
3. **Mức QC (chất lượng kiểm định cho request này)**:
   - A (đề xuất): `full` — DoD đầy đủ, kiểm tra tự động tính toàn vẹn số liệu và chuẩn quy ước tài liệu.
   - B: `ultra` — thẩm định chéo độc lập bằng `tdq-qc-tester`.
   - C: `lite`
4. **Bạn muốn bổ sung thêm gì không?**
   - A (đề xuất): Không, đủ rồi — làm tiếp đi.
   - B: Có — tôi nói thêm.

### Trả lời và phạm vi đã chốt

- Nguyên văn trả lời: `1a 2a 3b`.
- `1a`: Chỉ xuất bản báo cáo đề xuất chi tiết; không triển khai nâng cấp runtime trong request này. Các mốc v0.72.0–v0.75.0 là lộ trình dự kiến, không phải cam kết phát hành.
- `2a`: Phân tích cả năm trụ cột đã nêu; cho phép kết luận không nên áp dụng một kỹ thuật nếu chi phí hoặc rủi ro lớn hơn lợi ích.
- `3b`: QC `ultra`, có thẩm định độc lập. Đã ghi `muc_qc=ultra` qua CLI.
- Trả lời bổ sung nguyên văn: `4a` — không có yêu cầu bổ sung, tiếp tục theo phạm vi đã chốt `1a 2a 3b`.
- Dạng đầu ra mặc định: báo cáo Markdown có bảng bằng chứng, ma trận ưu tiên và công thức ước tính; không tự thêm dashboard HTML.
- Mốc nguồn: TDQ `5c8a9c2`, ECC `76aaa77d`; trạng thái ECC tracked sạch khi kiểm tra.
- Ba luồng khảo sát chỉ đọc: hooks/shell/Windows; team/worktree; QC/state/evidence. Không chỉnh mã nguồn hai dự án.
- Ước tính phải ghi giả định, mẫu đo, median/p95 khi có phép đo, khoảng thấp/cơ sở/cao và cách kiểm chứng. Không gán tỷ lệ cải thiện chất lượng từ confidence tự chấm của model.
- Không tự hạ gate duyệt/an toàn thành cảnh báo sau nhiều lần bị chặn; không chia sẻ dependency ghi được giữa worktree như một mặc định an toàn.
