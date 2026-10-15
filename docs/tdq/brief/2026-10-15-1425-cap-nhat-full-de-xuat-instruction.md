# BRIEF — Cập nhật đầy đủ các đề xuất kiến trúc tối ưu instruction và lazy load vào TDQ Workflow

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> "okay khoan bump version mà hãy mở request cập nhật full toàn bộ đề xuất từ bảng phân tích trên vào tdq workflow cho toi"

### Đọc bước đầu

- **Mục tiêu**: Hiện thực hóa toàn bộ các giải pháp kiến trúc đã được phân tích và đề xuất trong Báo cáo Kiến trúc `docs/kien-truc-instruction-lazy-load.md` vào hệ thống TDQ Workflow, bao gồm:
  1. Đưa bộ mã cấm cơ học tường minh (`ANTI-1` đến `ANTI-6`) kèm mẫu đối chứng WRONG/RIGHT vào các phase cốt lõi (`build`, `implement`, `qc`, `spec`, `plan`).
  2. Tái cấu trúc các rule ngôn ngữ (`python.md`, `typescript-js.md`...) và `clean-code.md` theo mô hình Kim tự tháp 3 tầng: tách Micro-rules ngắn gọn và lập các Cookbooks thực chiến trên đĩa (chỉ đọc khi gặp lỗi).
  3. Mở rộng cơ chế JIT Micro-injection qua Hook `PreToolUse` (nhận diện ngôn ngữ để mớm 3 dòng quy tắc vàng khi sửa code lần đầu) và `prompt_context.py` (mớm mẫu DoD khi vào phase `qc`).
  4. Tinh gọn đầu ra công cụ kiểm thử (`Silent CLI`): xuất log chi tiết ra đĩa, terminal chỉ in `≤ 2` dòng tóm tắt và lỗi chính để chống tràn context.
- **Phạm vi dự kiến**:
  - `skills/tdq-build/`, `skills/tdq-conventions/`, `skills/tdq-plan/`, `skills/tdq-spec/`, `skills/tdq-intake/`.
  - `hooks/scripts/edit_gate.py`, `hooks/scripts/prompt_context.py`, `scripts/tdq_test.py`.
  - Các file rules, references và cookbooks mới.

## Hiểu & kiến thức

### Năng lực dùng được

| Nguồn | Tên | Khớp chỗ nào | Quyết định | Lý do |
|---|---|---|---|---|
| 内置/MCP | `Agent` (subagent) | Điều phối các task độc lập khi cần | **dùng** | Hỗ trợ phân tích chuyên sâu |
| Repo script | `scripts/context_surface.py` & `scripts/skill_tokens.py` | Đo lường dung lượng token sau khi tái cấu trúc | **dùng** | Kiểm tra kiểm soát token và khóa ngân sách |
| Repo hook | `hooks/scripts/edit_gate.py` & `prompt_context.py` | Cài đặt JIT Micro-injection cho ngôn ngữ và phase | **dùng** | Điểm tích hợp hook của giải pháp G2 |
| Repo script | `scripts/tdq_test.py` | Bổ sung cờ silent log ra đĩa chống tràn context | **dùng** | Điểm tích hợp của giải pháp G3 |
| Repo skill | `skills/tdq-build/` & `skills/tdq-conventions/` | Cập nhật bộ mã cấm ANTI và cấu trúc Kim tự tháp | **dùng** | Nơi chứa các rule và skill cốt lõi |
| Built-in | `Read`, `Edit`, `Write` | Thao tác file code và tài liệu | **dùng** | Công cụ thao tác file tiêu chuẩn |

### Phân tích kiến trúc 4 trụ cột thực thi

1. **Bộ mã cấm tường minh (`ANTI-1`..`ANTI-6`)**:
   - `ANTI-1 (Fake Red)`: Không coi lỗi sai cú pháp / import error / sai đường dẫn file test là trạng thái ĐỎ hợp lệ của TDD.
   - `ANTI-2 (Blind Assertion)`: Không viết `assert True`, `assert len(x) >= 0` hoặc assertion rỗng.
   - `ANTI-3 (Dirty State Git)`: Không chạy lệnh Git nguy hiểm (`git checkout`, `git reset --hard`) khi working tree chưa sạch.
   - `ANTI-4 (Late Tick)`: Không gọi quá 2 lần tool `Edit` mà chưa cập nhật trạng thái `[~]` trong plan.
   - `ANTI-5 (Raw Dump)`: Không dán log test dài > 15 dòng vào chat; bắt buộc trích xuất tóm tắt và lỗi chính.
   - `ANTI-6 (Broad Area)`: Không khai báo trường `Chạm:` mang ký tự đại diện wildcard (`*`) hoặc thư mục bao trùm.
   - Bổ sung vào: `skills/tdq-build/references/team-mode.md`, `agents/tdq-implementer.md`, `skills/tdq-build/references/qc.md`, `skills/tdq-plan/references/plan-template.md`.

2. **Kim tự tháp 3 tầng & Cookbooks trên đĩa**:
   - Tầng 1: Giữ các micro-rules ngắn gọn trong `rules/*.md`.
   - Tầng 3: Tạo thư mục `skills/tdq-build/references/rules/cookbooks/` chứa cookbook thực chiến cho Python và TypeScript/JS (async/await, error handling, clean architecture patterns, edge cases).

3. **Hook-driven JIT Micro-injection**:
   - `hooks/scripts/edit_gate.py`: Khi Agent gọi tool `Edit` trên file `.py` hoặc `.ts` lần đầu trong phiên, tự động mớm 3 dòng quy tắc vàng của ngôn ngữ (dedupe bằng `already_reminded`).
   - `hooks/scripts/prompt_context.py`: Khi vào phase `qc`, tự động mớm checklist 5 câu hỏi SOLID và tiêu chí nghiệm thu DoD.

4. **Silent CLI & Externalized Logs**:
   - Cập nhật `scripts/tdq_test.py`: Hỗ trợ cờ `--silent` ghi log chi tiết ra `docs/tdq/.tdq-test.log`, terminal chỉ in tối đa 2 dòng tóm tắt và lỗi chính.

### Phạm vi dự kiến
- Triển khai đầy đủ 4 trụ cột trên.
- Đảm bảo toàn bộ test suite chạy xanh 100%, ngân sách token được cập nhật và kiểm soát chặt chẽ.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Research web | BỎ | Đã có tài liệu RFC chi tiết và phân tích nội bộ đầy đủ |
| Interview | CÓ | 1 vòng phỏng vấn chốt phạm vi ngôn ngữ cookbook và mức QC |
| QC độc lập | BỎ | Áp dụng mức QC đã chọn |

## Hỏi đáp

### Vòng 1 (2026-10-15 14:30)

1. **Phạm vi triển khai Cookbooks thực chiến (Tầng 3) ở request này**:
   - A (đề xuất): Tập trung hoàn thiện Cookbooks thực chiến cho **Python và TypeScript/JS** trước (2 ngôn ngữ chính yếu và phổ biến nhất, làm mẫu chuẩn mực cho các ngôn ngữ khác).
   - B: Viết đồng loạt Cookbooks cho toàn bộ cả 8 ngôn ngữ (Python, TS, Go, Rust, C#, C++, HTML, Bash) ngay trong đợt này.
   - **Người dùng chọn:** `1a`
2. **Cơ chế JIT Micro-injection cho ngôn ngữ trong `edit_gate.py`**:
   - A (đề xuất): Mớm đúng 1 lần đầu tiên khi sửa file của ngôn ngữ đó trong phiên (dùng `already_reminded` của `_common.py`), tránh spam lặp lại ở các turn sau.
   - B: Mớm lại mỗi khi có sự chuyển đổi qua lại giữa các file thuộc các ngôn ngữ khác nhau.
   - **Người dùng chọn:** `2a`, kèm yêu cầu bổ sung quan trọng:
     - **Cơ chế Chống mất mát ngữ cảnh sau Compaction (Compact-Resilient Anchor)**: Khi compaction xảy ra (`source == "compact"` tại `SessionStart`), hệ thống tự động reset sổ lượt `already_reminded` của micro-rules ngôn ngữ và bơm khối Neo Phục Hồi ngắn gọn (< 200 tokens) trỏ lại đúng file plan, task đang làm dở và bộ mã cấm `ANTI`, đảm bảo Agent sau khi nén context không bị mất phương hướng.
3. **Mức QC (chất lượng kiểm định cho request này)**:
   - A: `full`
   - B (đề xuất): `lite` — DoD + unit test vùng chạm.
   - C: `ultra`
   - **Người dùng chọn:** `3a` (`full`)

### Lộ trình chi tiết sau phỏng vấn

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Research web | BỎ | Phân tích nội bộ và RFC đã có sẵn đầy đủ |
| Interview | CÓ | Đã hoàn thành vòng 1 chốt phạm vi 4 trụ cột + cơ chế chống mất ngữ cảnh sau compact |
| QC độc lập | CÓ | Áp dụng mức QC `full` theo lựa chọn của người dùng |

