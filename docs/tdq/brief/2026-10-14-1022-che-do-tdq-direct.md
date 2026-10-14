# BRIEF — Chế độ _tdq_direct chạy thẳng phân tích và 1 cổng duyệt mini-plan
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> hi tôi muốn mở rquest update là khi người dùng mở yêu cầu mà có "_tdq_direct" thì claude code sẽ tự động analysis và sreach và phân tích và chỉ có 1 cổng duyệt mini plan và implement nhanh ko chạy nhiều step như pipeline của tdqworkflow express và deep

**Cách hiểu ban đầu:**
- **Mục tiêu:** Khi người dùng gửi yêu cầu mới có chứa từ khóa `_tdq_direct`, Claude Code tự động chạy tìm kiếm + phân tích và trình bày mini-plan với duy nhất 1 cổng duyệt, sau đó implement nhanh mà không chạy qua nhiều bước trung gian (như hỏi chọn pipeline, phỏng vấn nhiều vòng, tách spec/plan/mode/QC nhiều chặng của express và deep).
- **Phạm vi dự đoán:**
  - `hooks/scripts/prompt_context.py`: nhận diện `_tdq_direct` trong prompt người dùng tại sự kiện `UserPromptSubmit` để phát mã nhắc nhở chỉ dẫn luồng direct ngay từ đầu turn.
  - `scripts/tdq_state.py`: hỗ trợ hoặc liên kết trạng thái lane `quick` / cờ direct để quản lý cổng duyệt duy nhất.
  - `skills/tdq-intake/SKILL.md` và tài liệu liên quan (`quick-lane.md`): quy định quy trình xử lý tự động khi có cờ `_tdq_direct`.
  - `scripts/tdq_setup.py`: cập nhật khối hướng dẫn ghim toàn cục `KHOI_HUONG_DAN` để model hiểu cơ chế `_tdq_direct`.
- **Điểm chưa rõ:** Đã được làm rõ trong vòng phỏng vấn 1.

## Hiểu & kiến thức

### Năng lực dùng được

Phân vân → DÙNG. Kiểm kê ngày 2026-10-14: 24 skill trên đĩa, cộng skill built-in trong context. Không xoá bảng này kể cả khi không có dòng DÙNG nào.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | DÙNG | quy định luồng nhận diện `_tdq_direct` bỏ qua hỏi lane, vào thẳng phân tích + mini-plan |
| tdq-setup | plugin:tdq-workflow | DÙNG | cập nhật khối hướng dẫn ghim toàn cục cho chế độ `_tdq_direct` |
| tdq-conventions | plugin:tdq-workflow | NỀN | luật nền chung cho workflow |
| tdq-spec | plugin:tdq-workflow | NỀN | viết spec cho request |
| tdq-plan | plugin:tdq-workflow | NỀN | lập kế hoạch thực thi |
| tdq-build | plugin:tdq-workflow | NỀN | thực thi và kiểm thử |
| tdq-lean | plugin:tdq-workflow | NỀN | luật gọt bớt mã thừa |
| tdq-status | plugin:tdq-workflow | NỀN | báo cáo trạng thái |
| Đã xét 16 skill khác trên đĩa và 13 skill built-in | plugin/built-in | KHÔNG | khác lĩnh vực |

### Phạm vi

Vòng scope: BỎ — Yêu cầu chỉ định rõ cơ chế kích hoạt (`_tdq_direct`) và luồng xử lý (tự động phân tích/tìm kiếm, 1 cổng duyệt mini-plan, implement nhanh), các khía cạnh kỹ thuật còn lại suy ra được từ kiến trúc hook và state hiện có.

### Quyết định đã chốt

1. **Cơ chế nhận diện:** Bắt từ khóa `_tdq_direct` (không phân biệt hoa thường, e.g. `_tdq_direct`) tại hook `UserPromptSubmit` (`hooks/scripts/prompt_context.py`) khi chưa có request mở (`state is None or not state.get("active_request")` hoặc `phase_key(state) == "idle"`).
2. **Tín hiệu phát ra:** Hook phát thông báo `[TDQ:INTAKE]` kèm chỉ dẫn rõ: Yêu cầu có `_tdq_direct` → tự động chạy setup + tìm kiếm code (LSP/graphify/grep), phân tích yêu cầu, lập mini-plan và chỉ dừng ở duy nhất 1 cổng duyệt mini-plan, tuyệt đối KHÔNG dừng hỏi chọn pipeline hay phỏng vấn nhiều vòng.
3. **Hạ tầng state:** Sử dụng lane `quick` (express) với `init <slug> quick`, tận dụng cổng duyệt `quick_approved` sẵn có trong `CONG_THEO_LANE["quick"] = ("quick",)`, không làm phình schema state.
4. **Văn bản quy định:**
   - Cập nhật `skills/tdq-intake/SKILL.md` (Part A & Part C): thêm quy tắc nhận diện `_tdq_direct`, khi có cờ này thì bỏ qua Step 2 (hỏi chọn pipeline), tự động mở lane `quick`, mở branch git `feature/...`, chạy phân tích và tạo mini-plan.
   - Cập nhật `skills/tdq-intake/references/quick-lane.md`: mô tả rõ luồng direct với 1 cổng duyệt mini-plan duy nhất.
   - Cập nhật `scripts/tdq_setup.py`: cập nhật khối ghim toàn cục `KHOI_HUONG_DAN` để hướng dẫn model nhận diện cờ `_tdq_direct`.
5. **Sau duyệt mini-plan:** Thực thi inline trong 1 turn, chạy unit test xác nhận các task và ghi nhận working log, kết thúc báo cáo kết quả và hỏi commit theo chuẩn chung.
6. **Mức QC:** Chốt `muc_qc=full`.

### Phương án bị loại & lý do

- **Chỉ sửa file hướng dẫn, không can thiệp hook:** Bị loại vì hook `UserPromptSubmit` là lớp bảo đảm phản ứng ngay khi người dùng gửi prompt. Nếu hook chỉ phát dòng nhắc chung "open tdq-intake", model có thể vẫn làm theo thói quen cũ và dừng lại hỏi chọn pipeline.
- **Tạo lane mới `direct` trong `tdq_state.py`:** Bị loại vì không cần thiết (vi phạm luật gọt rung 1). Bản chất `_tdq_direct` là một đường tắt tự động dẫn vào quy trình mini-plan của lane `quick` với đúng 1 cổng duyệt `quick_approved`. Tạo thêm lane mới đòi hỏi cập nhật nhiều bảng enum, hook gác cổng và kiểm thử không cần thiết.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| `spec` | CÓ | Đặc tả kỹ thuật chi tiết cấu trúc nhận diện, mẫu hook, và quy tắc xử lý `_tdq_direct` |
| `plan` | CÓ | Lập kế hoạch từng task có unit test đi kèm (TDD: red → green) |
| `implement` | CÓ | Thực thi mã nguồn tại `prompt_context.py`, tài liệu skill và tests |
| `qc` | CÓ | Kiểm thử hồi quy toàn bộ test suite, kiểm tra clean code per `muc_qc=full` |
| `report` | CÓ | Tổng kết nghiệm thu DoD và đóng request |
| `subagent / team` | BỎ | Khối lượng thay đổi nhỏ gọn (khoảng 3-4 file), thực thi inline an toàn và nhanh nhất |
| `research bên ngoài` | BỎ | Logic nội bộ hệ thống TDQ-Workflow, không dùng thư viện ngoài |

## Hỏi đáp

### Vòng 1 (2026-10-14 10:31)

1. **Bạn muốn cơ chế nhận diện và phát tín hiệu cho `_tdq_direct` hoạt động ở tầng nào?**
   - Đã chọn: **A (đề xuất)** — Bắt tại hook `UserPromptSubmit` (`hooks/scripts/prompt_context.py`) và quy định trong skill `tdq-intake`. Hook tự động phát hiện `_tdq_direct` trong prompt khi chưa có request mở, phát chỉ dẫn `[TDQ:INTAKE]` yêu cầu model chạy thẳng vào phân tích, tìm kiếm code và lập mini-plan mà không dừng hỏi chọn pipeline.
2. **Bạn muốn hạ tầng trạng thái và tài liệu của `_tdq_direct` được tổ chức ra sao?**
   - Đã chọn: **A (đề xuất)** — Khởi tạo lane `quick` (express) với quy trình rút gọn, gộp tài liệu trong `docs/tdq/plan/<slug>.md`.
3. **Quy trình thực thi sau khi bạn duyệt mini-plan nên diễn ra như thế nào?**
   - Đã chọn: **A (đề xuất)** — Thực thi trọn gói trong 1 turn, chạy unit test xác nhận các task và ghi nhận working log.
4. **Request này bạn muốn QC tới mức nào?**
   - Đã chọn: **A (đề xuất)** — `full` — DoD + trọn unit test + hồi quy vùng chạm + ràng buộc kiến trúc + clean code. Không chạy runtime test.
5. **Bạn muốn bổ sung thêm gì không?**
   - Đã chọn: **A (đề xuất)** — Không, đủ rồi — làm tiếp đi.
