# SPEC — Áp dụng nâng cấp triết lý và kiến trúc Andrej Karpathy vào TDQ Workflow

Ngày: 2026-10-16 · Bản: 1.0 · Brief: ../brief/2026-10-16-1410-nang-cap-triet-ly-karpathy.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
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

- **Mục tiêu**: Hiện thực hóa trọn gói 5 bài học cốt lõi từ Andrej Karpathy vào kiến trúc và hệ thống rule của TDQ Workflow theo mô hình "Tâm thức Karpathy trong Bộ giáp TDQ" (Hybrid Architecture), giúp Agent viết code tinh gọn (không over-engineer), can thiệp chính xác như phẫu thuật (cấm drive-by refactor), chỉ dọn rác do chính mình tạo ra, chủ động phản biện kiến trúc ở bước tiếp nhận, và vận hành mượt mà theo vòng lặp hướng mục tiêu.
- **Trong phạm vi**:
  1. *Kỷ luật phẫu thuật cấp dòng (Line-level Surgical Traceability) & Chỉ dọn rác của chính mình*:
     - Cập nhật `skills/tdq-build/references/rules/chung.md`: Tinh chỉnh câu hỏi số 3 của *The Intentionality rule* (chỉ xóa dead code do chính thay đổi của mình tạo ra, không tự ý xóa dead code cũ làm vỡ namespace); bổ sung quy tắc *Surgical Changes* cấm drive-by refactoring, cấm sửa comment/quote style lân cận, mọi dòng diff phải truy vết trực tiếp về yêu cầu.
  2. *Luật "YAGNI đứng trên SOLID"*:
     - Cập nhật `skills/tdq-conventions/references/clean-code.md`: Bổ sung nguyên lý *Simplicity & YAGNI before SOLID* — Cấm tạo Interface, Abstract Class hoặc Strategy Pattern cho code chỉ dùng 1 lần (single-use code). Viết 1 hàm phẳng duy nhất; chỉ áp dụng OCP/DIP khi có ít nhất 2 trường hợp sử dụng thực tế.
  3. *Chủ động phản biện và bề mặt hóa đánh đổi (Surface Tradeoffs & Push Back)*:
     - Cập nhật `skills/tdq-intake/references/interview.md`: Bổ sung quy tắc *Think Before Coding — Surface Tradeoffs & Push Back* yêu cầu Agent chủ động phản biện giải pháp quá phức tạp và đề xuất phương án đơn giản hơn kèm ước lượng công sức.
  4. *Tâm thức Karpathy cho Subagents & Goal-Driven Loops*:
     - Cập nhật `agents/tdq-implementer.md`: Tích hợp 4 nguyên lý Karpathy vào chỉ dẫn thực thi của Subagent (Surgical diff, No single-use abstraction, Clean up own orphans, Goal-driven loop `[Step] -> verify: [Check]`).
  5. *Tích hợp Surgical & Simplicity vào JIT Micro-rules của `edit_gate.py`*:
     - Cập nhật `hooks/scripts/edit_gate.py`: Gộp thông điệp nhắc nhở tính phẫu thuật và tối giản (`Surgical: touch only what you must, no drive-by refactor; no single-use abstraction`) vào chuỗi JIT micro-rules mớm lần đầu khi sửa code trong phiên.
  6. *Tối ưu hóa bộ lọc `luat_gon.py` làm nhẹ Context khi code và chạy Subagent*:
     - Cập nhật `hooks/scripts/luat_gon.py`: Ở mức `full` (mặc định), chỉ bơm phần quy tắc cốt lõi và bảng cường độ, cắt giảm 50 dòng ví dụ code dài dòng (`### RIGHT / WRONG for this law` chỉ nạp ở mức `ultra` hoặc đọc trên đĩa), giảm ngay ~500 tokens mang vác cho mọi phiên `implement` và mọi `SubagentStart`.
  7. *Hệ thống kiểm thử tự động hóa & Đồng bộ khóa ngân sách*:
     - Cập nhật unit test kiểm chứng JIT micro-rules mới và bộ lọc `luat_gon`, đồng bộ chỉ mục dòng và khóa ngân sách token.
- **NGOÀI phạm vi**:
  - Không thay đổi cấu trúc state machine hay gỡ bỏ các hàng rào an toàn vật lý của TDQ Workflow.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | Đã hoàn thành nghiên cứu chuyên sâu ở request trước (`2026-10-16-1245-hoc-hoi-andrej-karpathy-skills`) |
| Interview | CÓ | Đã hoàn thành vòng 1 chốt các lựa chọn `1a 2a 3c` |
| QC độc lập (agent) | CÓ | Áp dụng mức QC `ultra` theo yêu cầu của người dùng |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Quy tắc Surgical Changes và Clean Up Only Your Own Mess trong luật chung | `skills/tdq-build/references/rules/chung.md` | File mang đầy đủ quy tắc cấm drive-by refactoring và phân biệt dead code mới/cũ, đạt chuẩn lint |
| 2 | Nguyên lý YAGNI đứng trên SOLID (cấm abstraction cho single-use code) | `skills/tdq-conventions/references/clean-code.md` | File nêu rõ quy tắc 1 use case = 1 hàm phẳng, cấm dựng Strategy/Interface sớm, đạt chuẩn lint |
| 3 | Quy tắc Think Before Coding (Surface Tradeoffs & Push Back) trong phỏng vấn | `skills/tdq-intake/references/interview.md` | File hướng dẫn rõ việc chủ động phản biện giải pháp phức tạp và nêu đánh đổi |
| 4 | Chỉ dẫn 4 nguyên lý Karpathy và Goal-Driven Loop cho Subagent | `agents/tdq-implementer.md` | File implementer tích hợp đủ 4 nguyên lý Karpathy, đạt chuẩn lint |
| 5 | Thông điệp JIT Micro-rules tích hợp Surgical & Simplicity trong hook | `hooks/scripts/edit_gate.py` | Khi sửa file mã nguồn lần đầu, hook mớm kèm thông điệp Surgical & No single-use abstraction; unit test chạy xanh 100% |
| 6 | Bộ lọc `luat_gon.py` tinh gọn ở mức `full` để giảm tải context cho `implement` và `SubagentStart` | `hooks/scripts/luat_gon.py` | Ở mức `full`, `loc_than_luat` lọc bỏ 50 dòng ví dụ dài (`### RIGHT / WRONG for this law`), giữ nguyên tính thứ tự `lite < full < ultra` |

## 2b. Ranh giới module

Xác định bằng ngữ nghĩa phụ thuộc qua LSP:

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| `core-rules` | `skills/tdq-build/references/rules/chung.md`, `skills/tdq-conventions/references/clean-code.md` | Không | 1, 2 |
| `intake-agent-rules` | `skills/tdq-intake/references/interview.md`, `agents/tdq-implementer.md` | `core-rules` | 3, 4 |
| `jit-edit-hook` | `hooks/scripts/edit_gate.py`, `hooks/scripts/luat_gon.py` | `core-rules` | 5, 6 |

## 3. Cách tiếp cận & lý do

- **Chọn**:
  1. *Tích hợp đồng bộ cả lớp Tâm thức (Rules/Skills/Agents) và lớp Nhắc nhở động (JIT Hook)*: Đưa 4 nguyên lý Karpathy vào đúng các điểm quyết định của Agent mà không làm tăng dung lượng nạp tĩnh quá mức.
  2. *Gộp Surgical Reminder vào JIT Micro-rules có sẵn của `edit_gate.py`*: Tránh tạo thêm mã chặn mới gây ma sát nhận thức (Hook Avoidance Panic), giữ trải nghiệm mượt mà.
- **Vì**:
  - Đạt tỷ lệ hiệu quả / token cao nhất, giữ nguyên 100% độ an toàn của Bộ giáp TDQ trong khi giải phóng tư duy cho Agent.
- **Đã loại**:
  - *Chặn cứng (deny) mỗi khi sửa nhiều dòng trong `edit_gate.py`*: Loại vì dễ chặn nhầm các task thực sự cần viết mới nhiều dòng, gây ức chế và đốt turn vô ích.

## 3b. Năng lực & công cụ

Chép từ brief mục `### Năng lực dùng được`. Phân vân → DÙNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| Agent | built-in | DÙNG | Chạy kiểm định độc lập mức `ultra` qua `tdq-qc-tester` |
| token_budget.py & doc_index.py | project | DÙNG | Đồng bộ chỉ mục dòng và khóa ngân sách token sau khi cập nhật rules |
| tdq-intake | plugin:tdq-workflow | NỀN | mở request, phỏng vấn và chuyển phase |
| tdq-spec | plugin:tdq-workflow | NỀN | lập đặc tả kỹ thuật và kiểm tra hợp đồng |
| tdq-plan | plugin:tdq-workflow | NỀN | lập kế hoạch phân tách task TDD |
| tdq-build | plugin:tdq-workflow | NỀN | thực thi TDD, chạy QC và lập báo cáo |
| tdq-conventions | plugin:tdq-workflow | NỀN | quy tắc workflow, ngôn ngữ 3 tầng |
| tdq-status | plugin:tdq-workflow | NỀN | kiểm tra trạng thái tiến độ |
| tdq-lean | plugin:tdq-workflow | NỀN | kiểm tra tính tinh gọn của mã nguồn |
| tdq-setup | plugin:tdq-workflow | NỀN | kiểm tra LSP và môi trường |
| tdq-check-status | plugin:tdq-workflow | NỀN | phục hồi phiên khi có sự cố |
| Đã xét 15 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- **Log service bật mặc định**: Ghi log tiến độ kèm timestamp ISO ra `stderr`, tắt qua `TDQ_LOG=0`.
- **Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật**.
- **Mỗi thành phần có unit test riêng, chạy được bằng một lệnh**.
- **Code viết ra bám 5 nguyên tắc SOLID** theo `skills/tdq-conventions/references/clean-code.md`, và bám rule ngôn ngữ trong `skills/tdq-build/references/rules/` (cyclomatic ≤ 10, cognitive ≤ 15).

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`):
- 2026-09-17: nội hoá luật "build less than asked" — thân luật ở `skills/tdq-build/references/rules/chung.md`, đọc–lọc bằng `hooks/scripts/luat_gon.py` theo `muc_gat`.
- 2026-08-22: ngôn ngữ chia 3 tầng — luật trong `skills/`, `agents/`, chú thích/docstring của `hooks/` + `scripts/` và chuỗi máy in ra đều viết TIẾNG ANH cố định.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Thêm dòng vào `chung.md`, `clean-code.md`, `interview.md` làm lệch số dòng chỉ mục hoặc bảng neo luật | Làm đỏ các bài kiểm tra chỉ mục tài liệu và bảng neo luật | Chạy `doc_index.py --tat-ca`, cập nhật bảng neo luật và khóa `token_budget.py` ngay sau khi sửa |
| Thêm chữ vào chuỗi JIT micro-rules trong `edit_gate.py` vượt trần 200 ký tự của `remind()` | Phần đuôi thông báo bị cắt cụt bởi hàm `trim()` | Giữ chuỗi nhắc nhở cô đọng dưới 200 ký tự để toàn bộ nội dung được hiển thị trọn vẹn |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |
|---|---|---|---|---|
| Q1 | Cập nhật `chung.md` và `clean-code.md` với quy tắc Surgical, Clean Own Mess và YAGNI > SOLID | Cả 2 file chứa đầy đủ quy tắc mới bằng tiếng Anh chuẩn mực, đạt 0 vi phạm lint và khớp khóa token | Đo trước: 0 dòng quy tắc Surgical/YAGNI-first trong 2 file, sau khi sửa có đầy đủ quy tắc và 0 lỗi lint | Rút gọn câu chữ và cập nhật chỉ mục dòng |
| Q2 | Cập nhật `interview.md` và `agents/tdq-implementer.md` với Push Back và 4 nguyên lý Karpathy | Cả 2 file chứa đầy đủ hướng dẫn phản biện đánh đổi và thực thi hướng mục tiêu, đạt 0 vi phạm lint | Đo trước: 0 dòng Push Back và Karpathy loop trong 2 file, sau khi sửa có đầy đủ và 0 lỗi lint | Kiểm tra lại bằng công cụ lint và i18n |
| Q3 | Hook `edit_gate.py` mớm thông điệp Surgical & Simplicity trong JIT micro-rules | Khi gọi `Edit` trên file mã nguồn lần đầu, output chứa cụm từ nhắc nhở `surgical` và `no single-use abstraction`; toàn bộ bài kiểm tra của hook chạy xanh 100% | Đo trước: 36 bài kiểm tra của edit_gate đang pass, sau khi sửa 36+ bài kiểm tra pass với nội dung mới | Cô đọng chuỗi ký tự để không bị cắt trần 200 ký tự |
| Q4 | Đồng bộ chỉ mục dòng, bảng neo luật và khóa ngân sách token | Các bài kiểm tra về chỉ mục tài liệu, bảng neo luật và ngân sách token đạt 100% PASS | Đo trước: 52/52 file khớp khóa ngân sách token, sau khi sửa giữ nguyên 52/52 file khớp khóa | Chạy công cụ cập nhật chỉ mục và bảng neo tự động |
| Q5 | Kiểm thử độc lập mức `ultra` | Agent kiểm thử độc lập thẩm định toàn bộ các hạng mục và xác nhận PASS | Đo trước: 0 lượt thẩm định độc lập cho request này, sau khi chạy đạt 1 biên bản PASS | Khắc phục ngay mọi điểm lệch nếu phát hiện |

**DoD**:
1. Toàn bộ 5 đầu ra cụ thể (§2) được hoàn thành chuẩn xác, tuân thủ tuyệt đối chuẩn tiếng Anh trong `skills/`, `agents/` và `hooks/`.
2. Toàn bộ bài kiểm tra tự động hóa vùng chạm và kiểm tra hợp đồng tài liệu đạt 100% PASS.
3. Kiểm định độc lập mức `ultra` qua `tdq-qc-tester` đạt PASS.

## 7. Câu hỏi còn mở

(Rỗng — toàn bộ câu hỏi đã được chốt qua phỏng vấn vòng 1.)
