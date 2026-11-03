# SPEC — Chế độ _tdq_direct tự động phân tích và chỉ có 1 cổng duyệt mini-plan

Ngày: 2026-10-14 · Bản: 1.0 · Brief: ../brief/2026-10-14-1022-che-do-tdq-direct.md · Lane: full
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
- Mục tiêu: Khi người dùng mở yêu cầu mới có chứa từ khóa `_tdq_direct`, Claude Code sẽ tự động chạy toàn bộ khâu chuẩn bị, tìm kiếm mã nguồn (LSP/graphify/grep), phân tích yêu cầu và trình bày mini-plan với duy nhất `1` cổng duyệt, sau đó implement nhanh mà không chạy qua nhiều bước trung gian (như hỏi chọn pipeline, phỏng vấn nhiều vòng, tách spec/plan/mode/QC nhiều chặng).
- Trong phạm vi:
  1. Nhận diện từ khóa `_tdq_direct` (không phân biệt hoa thường) tại hook `UserPromptSubmit` (`hooks/scripts/prompt_context.py`) khi chưa có request mở.
  2. Hook phát thông báo `[TDQ:INTAKE]` chuyên biệt cho chế độ direct, chỉ dẫn model chạy thẳng khâu phân tích và lập mini-plan, chỉ dừng ở 1 cổng duyệt mini-plan duy nhất.
  3. Bổ sung hướng dẫn luồng `_tdq_direct` vào `skills/tdq-intake/SKILL.md` và `skills/tdq-intake/references/quick-lane.md`: tự động chọn lane `quick`, mở branch git `feature/...`, chạy B1 (search + read code), tổng hợp mini-plan vào `docs/tdq/plan/<slug>.md`, bỏ qua bước hỏi pipeline và phỏng vấn, chỉ dừng ở cổng duyệt mini-plan.
  4. Cập nhật khối hướng dẫn ghim toàn cục `KHOI_HUONG_DAN` trong `scripts/tdq_setup.py` và đồng bộ sang `docs/claude-md-mau.md`.
  5. Bổ sung unit test cho hook để khóa chặt hành vi nhận diện `_tdq_direct` và giới hạn độ dài ký tự của dòng nhắc.
- NGOÀI phạm vi:
  - Thêm một lane mới riêng biệt (như `lane: "direct"`) vào `scripts/tdq_state.py` (tận dụng lane `quick` sẵn có).
  - Can thiệp hoặc thay đổi hành vi của các request thông thường không có từ khóa `_tdq_direct`.
  - Thay đổi cơ chế kiểm tra DoD và fix round của lane `quick`.

## 1b. Lộ trình
Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| `spec` | CÓ | Đặc tả kỹ thuật chi tiết cấu trúc nhận diện, mẫu hook, và quy tắc xử lý `_tdq_direct` |
| `plan` | CÓ | Lập kế hoạch từng task có unit test đi kèm (TDD: red → green) |
| `implement` | CÓ | Thực thi mã nguồn tại `prompt_context.py`, tài liệu skill và tests |
| `qc` | CÓ | Kiểm thử hồi quy toàn bộ test suite, kiểm tra clean code per `muc_qc=full` |
| `report` | CÓ | Tổng kết nghiệm thu DoD và đóng request |
| `subagent / team` | BỎ | Khối lượng thay đổi nhỏ gọn (khoảng 3-4 file), thực thi inline an toàn và nhanh nhất |
| `research bên ngoài` | BỎ | Logic nội bộ hệ thống TDQ-Workflow, không dùng thư viện ngoài |

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Nhận diện `_tdq_direct` và phát dòng nhắc chuyên biệt | `hooks/scripts/prompt_context.py` | Unit test: prompt chứa `_tdq_direct` phát đúng dòng nhắc direct; prompt bình thường giữ nguyên dòng nhắc cũ |
| 2 | Quy tắc xử lý luồng `_tdq_direct` trong intake & express | `skills/tdq-intake/SKILL.md`, `skills/tdq-intake/references/quick-lane.md` | Tài liệu có mục direct rõ ràng: bỏ qua hỏi lane, vào thẳng phân tích và lập mini-plan với 1 cổng duyệt |
| 3 | Khối ghim instruction toàn cục có chỉ dẫn `_tdq_direct` | `scripts/tdq_setup.py`, `docs/claude-md-mau.md` | Kiểm thử tính nhất quán khớp nguyên văn giữa script và file mẫu |
| 4 | Bộ unit test cho `_tdq_direct` | `hooks/scripts/` (kèm test riêng) | Test xanh cho các ca: prompt có `_tdq_direct` hoa/thường, đứng đầu/giữa/cuối, không có request mở |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| Hook prompt | `hooks/scripts/prompt_context.py` (kèm test riêng) | không | 1, 4 |
| Tài liệu intake | `skills/tdq-intake/SKILL.md`, `skills/tdq-intake/references/quick-lane.md` | không | 2 |
| Hướng dẫn setup | `scripts/tdq_setup.py`, `docs/claude-md-mau.md` (kèm test riêng) | không | 3 |

Ranh giới độc lập hoàn toàn: module hook quản lý phản hồi thời gian thực khi người dùng gửi prompt; module tài liệu quy định hành vi của agent khi thực thi skill; module setup quản lý đồng bộ instruction toàn cục.

## 3. Cách tiếp cận & lý do
- Chọn: nhận diện `_tdq_direct` bằng regex tại `hooks/scripts/prompt_context.py`.
  - Vì: `prompt_context.py` chạy tại sự kiện `UserPromptSubmit`, là nơi duy nhất có thể quan sát prompt người dùng ngay tức thì trước khi model bắt đầu turn mới và kịp thời phát dòng mã `[TDQ:INTAKE]` hướng dẫn model.
- Chọn: ánh xạ `_tdq_direct` vào lane `quick` (express) có sẵn.
  - Vì: lane `quick` đã có sẵn cơ chế cổng duyệt duy nhất (`quick_approved`), quy trình mini spec/plan gộp 1 file (`docs/tdq/plan/<slug>.md`), và tương thích 100% với các hook kiểm soát (`edit_gate.py`, `stop_gate.py`). Không cần thêm trường mới vào `state.json`.
- Chọn: bổ sung hướng dẫn ghim trong `scripts/tdq_setup.py` và `docs/claude-md-mau.md`.
  - Vì: `~/.claude/CLAUDE.md` là kênh hướng dẫn toàn cục cho model ở mọi project; model cần biết rằng khi thấy `_tdq_direct` thì không được dừng hỏi chọn pipeline.
- Đã loại: tạo lane mới `direct` trong `scripts/tdq_state.py` — vi phạm luật gọt rung 1, gây phình cấu trúc state và đòi hỏi sửa đổi nhiều hook gác cổng mà không mang lại giá trị khác biệt so với việc dùng lane `quick`.
- Đã loại: chỉ sửa file tài liệu skill mà không sửa hook — nếu hook vẫn in nhắc nhở cũ, model dễ rơi vào thói quen hỏi chọn pipeline như bình thường.

## 3b. Năng lực & công cụ
Chép từ brief mục `### Năng lực dùng được`. Phân vân → DÙNG.
Một dòng cho mỗi skill DÙNG hoặc NỀN, cộng đúng một dòng tổng cho phần còn lại.
Không xoá mục này kể cả khi không có dòng DÙNG nào.
Phán quyết chỉ nhận: DÙNG / KHÔNG (+ 1 trong 4 lý do đóng) / NỀN (skill khung đang chạy).

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | DÙNG | quy định luồng nhận diện `_tdq_direct` bỏ qua hỏi lane, vào thẳng phân tích + mini-plan |
| tdq-setup | plugin:tdq-workflow | DÙNG | cập nhật khối hướng dẫn ghim toàn cục cho chế độ `_tdq_direct` |
| tdq-conventions | plugin:tdq-workflow | NỀN | quy ước pipeline, clean code |
| tdq-spec | plugin:tdq-workflow | NỀN | viết spec cho request |
| tdq-plan | plugin:tdq-workflow | NỀN | lập kế hoạch thực thi |
| tdq-build | plugin:tdq-workflow | NỀN | thực thi và kiểm thử |
| tdq-lean | plugin:tdq-workflow | NỀN | luật gọt bớt mã thừa |
| tdq-status | plugin:tdq-workflow | NỀN | báo cáo trạng thái |
| Đã xét 16 skill khác trên đĩa và 13 skill built-in | plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc
- Log service: BỎ — Việc này chỉ sửa logic kiểm tra chuỗi trong hook, cập nhật tài liệu hướng dẫn và bổ sung test, không tạo runtime service hay background process mới.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh (lệnh cụ thể ghi ở plan).
- Code viết ra bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md`.

## 5. Ràng buộc & rủi ro
Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md` — chỉ những dòng việc này chạm tới):
- "File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/`" — Không tạo file code mới ngoài vùng này.
- "`hooks/` được gọi `scripts/`; `scripts/` không được import `hooks/`" — Giữ nguyên quan hệ import hiện hữu.
- "Ngôn ngữ chia 3 tầng: docstring/comment viết tiếng Anh cố định, mã in ra/prompt hướng dẫn tuân thủ i18n."

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Regex bắt nhầm `_tdq_direct` khi là một phần của từ khác | Nhầm lẫn sang chế độ direct không mong muốn | Dùng ranh giới từ `(?:^|\s|[^\w])_tdq_direct(?:\s|[^\w]|$)` |
| Dòng nhắc direct vượt trần ký tự của hook (240 ký tự) | Bị cắt đuôi (`_truncate`) làm mất ý | Giữ thông điệp ngắn gọn (≤ 180 ký tự) |
| Lệch nội dung giữa `scripts/tdq_setup.py` và `docs/claude-md-mau.md` | Test nhất quán báo đỏ | Sửa đồng bộ cả hằng số code và file mẫu |

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |
|---|---|---|---|---|
| Q1 | Hook nhận diện `_tdq_direct` | Unit test với prompt có/không có `_tdq_direct`, case-insensitive, state None/idle đều đạt | — | — |
| Q2 | Độ dài dòng nhắc direct | Dòng nhắc `[TDQ:INTAKE]` khi có `_tdq_direct` ≤ 240 ký tự | 168 ký tự (bản nháp câu ở §2 #1), biên ±30 | rút gọn câu thông báo xuống ≤ 140 ký tự |
| Q3 | Dòng ghim instruction trong setup | Dòng chỉ dẫn direct trong `KHOI_HUONG_DAN` ≤ 300 ký tự | 210 ký tự (bản nháp câu ở §2 #3), biên ±40 | rút gọn câu |
| Q4 | Hồi quy và nhất quán template | Mọi test của hook prompt và tính nhất quán template đều xanh | — | — |
| Q5 | Hướng dẫn skill tdq-intake | Tài liệu `skills/tdq-intake/SKILL.md` và `quick-lane.md` có mục chỉ dẫn direct rõ ràng | — | — |

DoD:
- Q1–Q5 đạt.
- `doc_lint` của spec/plan xanh; drift mốc luật không tăng.
- Trọn bộ test suite hồi quy không có ca nào đỏ.

## 7. Câu hỏi còn mở
(Trống)
