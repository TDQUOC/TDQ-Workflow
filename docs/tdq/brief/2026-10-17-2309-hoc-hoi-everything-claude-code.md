# Yêu cầu: Nghiên cứu đối chiếu everything-claude-code và nâng cấp TDQ Workflow
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

"okay biết là project đó cũng tốt lắm hyax giúp tôi mở request và có thể spwan subagent tuỳ thích, tôi cần tìm hiểu phân tích 2 chiều từ project tdq-workflow và every thing claude code tôi muốn học hỏi tule luật subagent,... từ đó để nâng cấp toàn diện cho tdq-workflow"

"tôi muốn request này là phân tích sâu hơn , hãy mở request tạo ít nhất 5 đợt subagent cứ mỗi đợt đưa result về sẽ được ghi ra và đợt sau phản biện và phân tích sâu hơn đợt trước để tổng hợp phân tích chi tiết là có thể cập nhật gì vào tdq-workflow để có thể học hỏi được tất cả tinh tuý của everything claude code và output của request này là file tài liệu chi tiết những gì có thể học được và sau khi cập nhật đó thì ước tính tdq-workflow sẽ có sự phát triển hơn thế nào, request này chưa update chỉ nghiên cứu, phân tích và tổng hợp để lên đề xuất chi tiết"

### Đọc hiểu lần đầu & Định vị Request
- **Bản chất Request**: Request thuần túy Nghiên cứu, Phân tích Đối kháng Đa tầng & Thiết kế Đề xuất (Research & Design Blueprint). **Tuyệt đối KHÔNG sửa code hay cập nhật logic TDQ Workflow trong request này.**
- **Phương pháp thực thi**: Chạy chuỗi ít nhất 5 đợt subagent lặp đệ quy. Mỗi đợt đưa kết quả về được phân tích, ghi chép lại; đợt kế tiếp kế thừa, phản biện đối kháng và đào sâu hơn đợt trước để chắt lọc toàn bộ tinh túy từ Everything Claude Code (ECC).
- **Sản phẩm đầu ra (Deliverable)**:
  - File tài liệu đề xuất toàn diện: `docs/tdq/de-xuat-nang-cap-toan-dien-tu-everything-claude-code.md`.
  - Nội dung gồm: Báo cáo đối chiếu 2 chiều chi tiết; Danh mục toàn bộ các tinh hoa học hỏi được từ ECC; Phương án kiến trúc tích hợp chi tiết vào 4 tầng của TDQ Workflow; Báo cáo dự phóng lượng hóa sự phát triển và nhảy vọt về chất lượng của TDQ Workflow sau khi áp dụng.

## Hiểu & kiến thức

### Năng lực dùng được

Phân vân → DÙNG. Kiểm kê ngày 2026-10-17: 25 skill trên đĩa, cộng skill built-in trong context. Không xoá bảng này kể cả khi không có dòng DÙNG nào.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-conventions | plugin:tdq-workflow | NỀN | quy tắc quy trình, state, one-turn protocol |
| tdq-intake | plugin:tdq-workflow | NỀN | mở request và phân tích đệ quy |
| tdq-spec | plugin:tdq-workflow | NỀN | viết đặc tả kỹ thuật chi tiết cho tài liệu đề xuất |
| tdq-plan | plugin:tdq-workflow | NỀN | lập kế hoạch biên soạn và thẩm định tài liệu |
| tdq-build | plugin:tdq-workflow | NỀN | điều phối viết tài liệu và kiểm thử DoD tài liệu |
| tdq-lean | plugin:tdq-workflow | DÙNG | phản biện gạt bỏ over-engineering trong các đề xuất học từ ECC |
| tdq-setup | plugin:tdq-workflow | NỀN | kiểm soát bộ tìm kiếm 3 tầng LSP/graphify/grep |
| tdq-status | plugin:tdq-workflow | NỀN | kiểm tra trạng thái quy trình |
| security-review | built-in | DÙNG | đối chiếu chuẩn an ninh với security-reviewer của ECC |
| code-review | built-in | DÙNG | đối chiếu quy trình review đối kháng |
| Đã xét 20 skill khác | plugin/built-in | KHÔNG | khác lĩnh vực |

### Tiến độ và Kết quả Chuỗi 5 Đợt Subagent

#### Đợt 1: Khảo sát Tổng quan & Đối chiếu 5 Trục (Đã hoàn thành)
- Đối chiếu toàn diện giữa ECC (v2.2.3) và TDQ Workflow (v0.72.0) trên 5 trục: Kiến trúc, Subagents, Rules & Hooks, Trải nghiệm, Hiệu quả Token.
- Xác định thế mạnh vượt trội của TDQ: Gác cổng cứng Fail-Closed, 3 tầng tìm kiếm LSP/graphify/grep, QC độc lập không sửa code, Git worktree isolation.

#### Đợt 2: Bóc tách Chi tiết Kỹ thuật & Giải thuật Cốt lõi (Đã hoàn thành)
- Bóc tách Handoff Protocol (`commands/orchestrate.md`): 5 trường `Context`, `Findings`, `Files Modified`, `Open Questions`, `Recommendations`.
- Bóc tách Hook `suggest-compact.js` (đếm `Edit/Write` qua PID tạm), `pre-compact.js`, `evaluate-session.js` (đếm tin nhắn user).
- Bóc tách Verification Loop (6 bước) và Eval Harness (EDD với `pass@k` và `pass^k`).
- Nhận diện các điểm yếu của ECC: thiếu worktree isolation, đếm thiếu tool call, prompt-based không có gate enforcement.

#### Đợt 3: Phản biện Đối kháng & Phân loại "Vàng Ròng" vs "Bloat" (Đã hoàn thành)
Áp dụng triết lý Karpathy và Soul TDQ (`chất lượng > runtime > context cost`, `gạt over-engineering`), phân loại thành 3 nhóm rõ rệt:
1. **Nhóm 1: VÀNG RÒNG (Bắt buộc tiếp thu ngay)**:
   - Kiến trúc Hook Stop-Batching: Dồn format, typecheck, lint về chốt chặn `Stop` thay vì chạy giật cục ở từng `Edit` (tránh nghẽn 500-1500ms trên Windows 11).
   - Cổng Fact-Forcing Gate trước Report/Commit: Bắt buộc bằng chứng thực tế trước khi kết luận nghiệm thu.
   - Phân tầng Bất biến Context Carrier & Digest Chain.
   - Rút gọn thông báo chặn (Denial Deduplication).
2. **Nhóm 2: CẢI TẠO LẠI (Refactor to TDQ Style)**:
   - Strategic Compaction: Thay thế logic đếm `Edit/Write` ngây thơ bằng Weighted Tool Call Counter (Read=5, WebFetch=10, Edit=2, Bash=1) và **chỉ kích hoạt tại ranh giới Gate tự nhiên** (sau analyze, duyệt plan, giữa các wave).
   - Handoff Protocol: Không tạo file .md rác, chuẩn hóa payload JSON `TDQ_HANDOFF_PAYLOAD` (< 200 tokens).
   - Continuous Learning: Vứt bỏ script rỗng của ECC, viết lại thành `tdq_harvest.py` phân tích thực chất từ `workinglog`, lỗi QC và feedback user; cách ly và duyệt tay.
   - Quét Shell an toàn (Bounded Shell Scanner) chuẩn hóa cho PowerShell / Windows 11.
3. **Nhóm 3: THÙNG RÁC / TỪ CHỐI (Bloat / Over-engineering)**:
   - Từ chối daemon Rust `ecc2/`, TUI Ratatui, SQLite WAL actor.
   - Từ chối 71 subagents phân mảnh (marketing, healthcare, bengali...).
   - Từ chối việc ép 9 subagents toàn Opus (đốt token x5, trễ 15-30 phút).
   - Từ chối chạy đa agent không có git worktree isolation.
   - Từ chối 122 rules dài gần 10.000 dòng gây loãng ngữ cảnh.
   - Từ chối cơ chế tự động nạp tri thức thành luật không qua kiểm duyệt con người.

#### Đợt 4: Thiết kế Kiến trúc Tích hợp Chi tiết vào 4 Tầng TDQ (Đã hoàn thành)
- **Tầng Luật**: JSON Schema của `TDQ_HANDOFF_PAYLOAD`, subagent `tdq-security-reviewer`, luật `Adversarial Skeptic`, quy tắc Clean Code (Immutability, Fn ≤ 50 dòng, TDD).
- **Tầng Hook**: Stop-batching buffer (`.claude/tmp/edited_files.txt`), `strategic_compact_gate.py`, `doc_file_gate.py` (chặn tài liệu rác ngoài vùng quy định), Denial Deduplication.
- **Tầng CLI**: `tdq_harvest.py` (vùng cách ly `docs/tdq/knowledge/candidates/`), `tdq_team.py` nâng cấp (TCAS AST import dependency graph + NTFS Junction sharing trên Windows).
- **Tầng Dữ liệu & Trải nghiệm**: Handoff audit log, bảo toàn quy tắc chat trực tiếp, cấm popup UI.

#### Đợt 5: Đánh giá Tác động Lượng hóa & Biên soạn Master Blueprint Document (Đang chạy ngầm)
- Lượng hóa sự phát triển của TDQ Workflow sau khi nâng cấp (Before vs After).
- Xuất bản tài liệu đề xuất chính thức tại `docs/tdq/de-xuat-nang-cap-toan-dien-tu-everything-claude-code.md`.

### Lộ trình Pipeline

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| analyze (hiện tại) | CÓ | Hoàn tất chuỗi 5 đợt subagent nghiên cứu và phản biện sâu |
| spec | CÓ | Viết bản đặc tả kỹ thuật chi tiết (Master Blueprint Spec) |
| plan | CÓ | Lập kế hoạch từng task xuất bản tài liệu đề xuất chi tiết |
| implement | CÓ | Hoàn thiện tài liệu `docs/tdq/de-xuat-nang-cap-toan-dien-tu-everything-claude-code.md` |
| qc | CÓ | Thẩm định độc lập DoD của tài liệu (tính đầy đủ, không sửa code bừa bãi) |
| report | CÓ | Tổng kết kết quả và giao nộp tài liệu đề xuất |

## Hỏi đáp

### Vòng 1: Xác nhận Phạm vi & Mục tiêu Request
- Đã xác nhận: Request thuần nghiên cứu đối chiếu, không sửa code, thực thi qua chuỗi 5 đợt subagent lặp phản biện đối kháng.
- Mức QC: `full` (DoD tài liệu + kiểm tra không có file code nào bị chỉnh sửa ngoài ý muốn).
