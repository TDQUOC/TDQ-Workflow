# SPEC — Đánh giá độ chi tiết instruction TDQ Workflow cho model tier thấp và phương án tối ưu token context

Ngày: 2026-10-15 · Bản: 1.0 · Brief: ../brief/2026-10-15-1300-danh-gia-instruction-tier-thap.md · Lane: full
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

- **Mục tiêu**: Đánh giá toàn diện nguyên nhân khiến các model tier thấp gặp khó khăn khi tuân thủ instruction của TDQ Workflow; xây dựng Báo cáo Kiến trúc Đề xuất (RFC / Blueprint) chi tiết về các giải pháp Lazy Loading và quản lý vòng đời Context để cung cấp đủ tài liệu mà không làm cháy token; đồng thời triển khai ngay bước Quick-Win trong mã nguồn: hoãn nạp tĩnh 8.200 ký tự luật gọn tại `SessionStart`, tiết kiệm ~2.000 tokens ngay từ đầu phiên.
- **Trong phạm vi**:
  1. *Báo cáo Kiến trúc Đề xuất (RFC)* lưu tại `docs/kien-truc-instruction-lazy-load.md` bao gồm:
     - Hiện trạng & Đo đạc định lượng carry-cost trên toàn bộ 45 file reference và 9 file skill (~90.242 tokens).
     - Phân tích chi tiết 7 điểm gãy của model tier thấp khi gặp instruction cô đọng, triết lý cao (lỗi CLI, quên tick checkbox, test đỏ ảo, sai format `Chạm:`, lúng túng khi QC/Git, thiếu ví dụ ngôn ngữ).
     - Phân tích đối chứng các bài học thành công từ `vision-test-loop.md` (Trigger table, công thức mechanical, Anti-pattern codes, bảng Symptom -> Action).
     - Thiết kế chi tiết 4 giải pháp kiến trúc tối ưu ngữ cảnh (Kim tự tháp 3 tầng, Hook-driven JIT Micro-injection, Externalized Log & Silent CLI, State-Anchored Compaction & Session Handoff).
     - Lộ trình triển khai cụ thể từng bước cho TDQ Workflow.
  2. *Triển khai Quick-Win trong mã nguồn*:
     - Tối ưu `hooks/scripts/session_start.py`: chỉ nạp header tóm tắt (< 200 tokens) ở đầu session khi mở phiên ở phase `idle`, `analyze`, `spec`, `plan`. Chỉ nạp toàn bộ thân luật `chung.md` khi bước vào phase `implement` hoặc subagent.
  3. *Kiểm thử tự động hóa*:
     - Bổ sung các bài test kiểm chứng việc nạp context có điều kiện theo phase của hook khởi tạo phiên.
- **NGOÀI phạm vi**:
  - Chưa viết lại toàn bộ 18 file rules và cookbooks trong request này (sẽ làm theo lộ trình RFC ở các request tiếp theo).

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | Hai subagent đã hoàn thành khảo sát thực tế và phân tích kiến trúc chuyên sâu |
| Interview | CÓ | Đã hoàn thành 1 vòng phỏng vấn chốt đủ 3 câu hỏi (`1a 2a 3b`) |
| QC độc lập (agent) | BỎ | Áp dụng mức QC `lite` đã chọn |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Báo cáo Kiến trúc Đề xuất chi tiết (RFC / Blueprint) tối ưu instruction và lazy load context | `docs/kien-truc-instruction-lazy-load.md` | Tài liệu đầy đủ 5 phần lớn (đo đạc định lượng, 7 điểm gãy, bài học vision-test-loop, 4 giải pháp kỹ thuật, lộ trình triển khai), đạt tiêu chuẩn lint và ngân sách token |
| 2 | Cơ chế hoãn nạp luật gọn có điều kiện theo phase trong hook khởi tạo phiên | `hooks/scripts/session_start.py` | `SessionStart` ở phase `idle`, `analyze`, `spec`, `plan` chỉ nạp header tóm tắt (< 200 tokens); chỉ nạp full thân luật `chung.md` khi phase là `implement` |

## 2b. Ranh giới module

Xác định bằng ngữ nghĩa phụ thuộc qua LSP (`docs/` là tài liệu thiết kế, `hooks/scripts/session_start.py` là code hook khởi tạo phiên):

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| `rfc-doc` | `docs/kien-truc-instruction-lazy-load.md` | Không | 1 |
| `session-start-opt` | `hooks/scripts/session_start.py` | Không | 2 |

## 3. Cách tiếp cận & lý do

- **Chọn**:
  1. *Xây dựng Báo cáo Kiến trúc Đề xuất (RFC) đầy đủ chứng cứ*: Cung cấp bức tranh toàn cảnh, đo đạc carry-cost chính xác (~90k tokens), chỉ rõ 7 điểm gãy của model nhỏ và thiết kế 4 trụ cột kỹ thuật (Kim tự tháp 3 tầng, Hook JIT Micro-injection, Externalized Log, Guided Compaction).
  2. *Triển khai ngay Quick-Win hoãn nạp `chung.md`*: Giảm tải ngay lập tức ~2.000 tokens mang vác (carry-cost) ở đầu mọi session khi chưa bước vào phase code (`implement`).
- **Vì**:
  - Giải quyết bài toán một cách có phương pháp: vừa có tầm nhìn kiến trúc dài hạn cho toàn bộ hệ thống tài liệu, vừa có cải tiến đo đếm được ngay lập tức trên mã nguồn thực tế.
- **Đã loại**:
  - *Viết dài thêm trực tiếp vào các file `SKILL.md` và `rules/*.md` hiện có*: Loại vì sẽ làm tổng context vọt lên trên 50.000 tokens, khiến model tier thấp bị nghẽn ngữ cảnh và tăng chi phí carry-cost gấp 3 lần.

## 3b. Năng lực & công cụ

Chép từ brief mục `### Năng lực dùng được`. Phân vân → DÙNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| Agent | built-in | DÙNG | Điều phối 2 subagent chạy ngầm phân tích đa chiều |
| context_surface.py & skill_tokens.py | project | DÙNG | Đo lường chính xác dung lượng token và bề mặt ngữ cảnh |
| tdq-intake | plugin:tdq-workflow | NỀN | tiếp nhận, phân tích yêu cầu và phỏng vấn chốt phạm vi |
| tdq-spec | plugin:tdq-workflow | NỀN | viết đặc tả kỹ thuật và kiểm tra R8, R11, R14 |
| tdq-plan | plugin:tdq-workflow | NỀN | lập kế hoạch triển khai theo từng task TDD |
| tdq-build | plugin:tdq-workflow | NỀN | thực thi TDD đỏ -> xanh, chạy QC mức `lite` và lập báo cáo |
| tdq-conventions | plugin:tdq-workflow | NỀN | quy tắc workflow, ngôn ngữ 3 tầng và hợp đồng tài liệu |
| tdq-status | plugin:tdq-workflow | NỀN | kiểm tra trạng thái |
| tdq-lean | plugin:tdq-workflow | NỀN | áp dụng bậc thang build-less-than-asked (`TDQ:GON`) |
| tdq-setup | plugin:tdq-workflow | NỀN | kiểm tra môi trường công cụ và LSP |
| tdq-check-status | plugin:tdq-workflow | NỀN | phục hồi phiên khi cần |
| Đã xét 12 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- **Log service bật mặc định**: Ghi log tiến độ kèm timestamp ISO ra `stderr`, tắt qua `TDQ_LOG=0`.
- **Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật**.
- **Mỗi thành phần có unit test riêng, chạy được bằng một lệnh**.
- **Code viết ra bám 5 nguyên tắc SOLID** theo `skills/tdq-conventions/references/clean-code.md`, và bám rule ngôn ngữ trong `skills/tdq-build/references/rules/` (cyclomatic ≤ 10, cognitive ≤ 15).

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md` — chỉ những dòng việc này chạm tới):
- 2026-09-17: nội hoá luật "build less than asked" — thân luật ở `skills/tdq-build/references/rules/chung.md`, đọc–lọc bằng `hooks/scripts/luat_gon.py` theo `muc_gat`. Ba kênh bơm: `SessionStart` và `SubagentStart` mang thân luật, `UserPromptSubmit` chỉ một dòng con trỏ ở phase `implement` — việc này chạm ở `hooks/scripts/session_start.py`.
- 2026-08-22: ngôn ngữ chia 3 tầng — luật trong `skills/`, `agents/`, chú thích/docstring của `hooks/` + `scripts/` và chuỗi máy in ra đều viết TIẾNG ANH cố định — việc này chạm ở `hooks/scripts/session_start.py`.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Hoãn nạp `chung.md` ở `SessionStart` có thể làm ảnh hưởng đến các bài test kiểm tra sự xuất hiện của `TDQ:GON` | Làm đỏ các bài test kiểm tra hook `SessionStart` | Cập nhật các bài test kiểm tra `SessionStart` để truyền trạng thái phase tương ứng (`implement` khi cần kiểm tra thân luật, `idle` khi kiểm tra tóm tắt nhẹ) |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |
|---|---|---|---|---|
| Q1 | Báo cáo RFC lưu tại `docs/kien-truc-instruction-lazy-load.md` hoàn chỉnh 5 phần lớn | File tài liệu chứa đầy đủ 5 phần lớn (hiện trạng ~90k tokens, 7 điểm gãy của model nhỏ, bài học vision-test-loop, 4 giải pháp kỹ thuật, lộ trình triển khai), độ dài ≥ 200 dòng văn bản chuyên sâu | Đo trước: 0 dòng (file chưa tạo), sau khi viết đạt ≥ 200 dòng (biên 50 dòng) | Bổ sung thêm ví dụ kiến trúc và bảng số liệu phân tích |
| Q2 | Hook `session_start.py` hoãn nạp thân luật gọn khi ở phase ngoài `implement` | Khi phase là `idle`, `analyze`, `spec` hoặc `plan`, hook chỉ in dòng tóm tắt (< 200 tokens); khi phase là `implement`, hook nạp đầy đủ thân luật `chung.md` | Đo trước: 100% các lần mở phiên đều nạp 8.200 ký tự (~2.000 tokens) `chung.md`, sau khi sửa giảm 90% dung lượng nạp ở phase idle (biên 1.800 tokens) | Giữ dòng tóm tắt 1 dòng con trỏ nhắc nhở mã `[TDQ:GON]` |
| Q3 | Bộ test tự động hóa kiểm chứng cơ chế nạp context có điều kiện của `session_start.py` | Toàn bộ các bài test của hook `SessionStart` trong suite chạy xanh 100% | Đo trước: 36/36 tests hiện tại đang pass với cơ chế nạp cũ, sau khi sửa 36+ tests pass với cả 2 chế độ phase | Điều chỉnh mock state trong test fixture cho đúng phase |
| Q4 | Hợp đồng tài liệu, chuẩn ngôn ngữ 3 tầng và khóa ngân sách token | Các file tài liệu và mã nguồn thay đổi đạt 0 vi phạm với `doc_lint.py`, `i18n_check.py` và khóa ngân sách `token_budget.py` | `token-budget.json` hiện khớp 50/50 file (biên 0 file lỗi) | Chạy `token_budget.py` cập nhật khóa ngay khi sửa |

**DoD**:
1. Tài liệu `docs/kien-truc-instruction-lazy-load.md` được lập hoàn chỉnh, sâu sắc, giải quyết toàn diện bài toán của model tier thấp và tiết kiệm token.
2. `hooks/scripts/session_start.py` được tối ưu hóa hoãn nạp `chung.md` theo phase, tiết kiệm ~2.000 tokens carry-cost ngay đầu phiên.
3. Toàn bộ unit test và các kiểm định QC mức `lite` đạt 100% PASS.

## 7. Câu hỏi còn mở

(Rỗng — toàn bộ câu hỏi đã được chốt.)
