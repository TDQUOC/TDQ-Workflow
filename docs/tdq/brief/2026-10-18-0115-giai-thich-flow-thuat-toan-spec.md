# Brief: Nâng cấp Spec để giải thích trực quan Flow hoạt động và Thuật toán cho Fresher Dev

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> "okay bây giờ mở request deep resreach và phân tích giúp tôi một vấn đề sau và đề xuất cho tôi hướng xử lí. Tôi muốn là khi mà dev một hệ thống/ feature, thì ở spec cũng sẽ lí giải vaf giải thích flow hoạt động của các feature trong hệ thống hoặc feature đó sau update/ refactor đang hoạt động thế nào, thuật toán xử lí ra sao, để một dev fresher cũng có thể dễ dàng nắm kiến trúc và giải thuật mà ai chuẩn bị làm, để dev có thể control nhiều hơn thông tin dự án, hãy sreach và cho tôi output request này là có cacsh nào để update tdq-workflow để làm được việc đó không?"

### Đọc hiểu ban đầu:
- **Mục tiêu**: Nghiên cứu sâu (deep research) và nâng cấp tài liệu `Spec` trong TDQ Workflow sao cho khi lập đặc tả tính năng/hệ thống, AI luôn phải giải thích rõ ràng flow hoạt động, sự thay đổi sau update/refactor, và các thuật toán xử lý một cách trực quan, mạch lạc.
- **Tiêu chuẩn đầu ra hướng tới**: Một lập trình viên fresher/mới vào dự án khi đọc vào bản Spec có thể dễ dàng nắm bắt trọn vẹn kiến trúc tổng thể, luồng dữ liệu (data flow), luồng xử lý (logic flow) và giải thuật cốt lõi mà AI chuẩn bị thực thi. Giúp dev nắm quyền kiểm soát (control) cao hơn đối với dự án.
- **Phạm vi nghiên cứu**:
  1. Rà soát cấu trúc mẫu `Spec` hiện tại trong `skills/tdq-spec/` và các tài liệu liên quan (`spec.md`, `mau-spec.md`, v.v.).
  2. Khảo sát các kỹ thuật biểu diễn kiến trúc & thuật toán tối ưu cho LLM + con người (Flowcharts, Sequence Diagrams qua Mermaid, Pseudocode / Step-by-step Algorithms, State Transition Tables, Before vs After Diff Flow).
  3. Thiết kế giải pháp cập nhật TDQ Workflow: Bổ sung các section bắt buộc trong Spec template (ví dụ: *Architectural Flow & Sequence Diagram*, *Algorithm & Logic Breakdown*, *Mental Model for Freshers*).
  4. Đảm bảo tuân thủ DocLint và không làm phình token lãng phí (cân bằng giữa chi tiết sư phạm và tính súc tích kỹ thuật).

## Hiểu & kiến thức

### 1. Phân tích hiện trạng Spec TDQ Workflow
- Hiện nay bản mẫu Spec (`skills/tdq-spec/references/spec-template.md`) tập trung chủ yếu vào: Phạm vi (§1), Lộ trình (§1b), Đầu ra (§2), Ranh giới module (§2b), Cách tiếp cận & lý do (§3), Năng lực tool (§3b), Yêu cầu bắt buộc (§4), Rủi ro (§5), QC & DoD (§6).
- **Điểm khuyết thiếu lớn**: Chưa có quy chuẩn bắt buộc về việc diễn giải **Flow hoạt động** và **Giải thuật chi tiết**. Hệ quả là khi AI lập spec, các luồng tương tác đa tầng và thuật toán cốt lõi thường bị ẩn sau các mô tả tóm tắt kỹ thuật ngắn gọn, khiến lập trình viên (nhất là fresher) khó hình dung toàn cảnh dữ liệu di chuyển thế nào, điểm khác biệt giữa Trước vs Sau khi update/refactor ra sao, và các bước logic bên trong hàm hoạt động theo trình tự nào.

### 2. Nghiên cứu giải pháp chuẩn mực công nghiệp
- **Biểu diễn Flow trực quan (Visual & Structural Flows)**:
  - *Mermaid Sequence Diagram*: Phù hợp nhất cho tương tác giữa các actor (User -> Controller -> Service -> Hook -> Database/Cache).
  - *Mermaid Flowchart*: Phù hợp cho luồng dữ liệu phân nhánh điều kiện (Decision Trees, Pipeline States).
  - *Before vs After Flow Diff*: Phù hợp cho bài toán Refactor / Performance Update (mô tả rõ thành phần nào bị gỡ bỏ, thành phần nào được thay thế).
- **Biểu diễn Giải thuật cho Fresher (Algorithm Transparency)**:
  - Trình bày dạng *Step-by-Step Execution Protocol* (Bước 1, 2, 3 tường minh) hoặc *Structured Pseudocode*.
  - Định lượng độ phức tạp thời gian/không gian $O(N)$, $O(1)$.
  - Phân tích *Edge Cases & Defensive Fallbacks*: Xử lý trường hợp ngoại lệ (null, timeout, rỗng, race condition).
- **Mô hình tư duy (Mental Model & Analogy)**:
  - Một đoạn giải thích ngắn bằng ngôn ngữ đời thường (ví dụ: Stop-batching giống như "giỏ đồ gom giặt một lần" thay vì "giặt từng chiếc áo").
  - Bảng thuật ngữ chuyên ngành (Domain Glossary).

### 3. Đề xuất kiến trúc nâng cấp TDQ Workflow
Bổ sung 3 section mới vào khuôn mẫu Spec (`spec-template.md`):
1. **`## 2c. Luồng hoạt động & Sơ đồ kiến trúc (Architecture & Flow)`**:
   - Sơ đồ Mermaid (Sequence / Flowchart) cho tính năng.
   - Bảng so sánh Before vs After (bắt buộc với yêu cầu update/refactor).
   - Từng bước tương tác tuần tự (1 -> 2 -> 3).
2. **`## 3c. Giải thuật & Xử lý cốt lõi (Algorithm & Logic Breakdown)`**:
   - Từng bước thuật toán (Step-by-step logic / Pseudocode).
   - Đánh giá độ phức tạp $O(T)$ và $O(S)$.
   - Các ca góc hiểm (Edge cases) và cơ chế phòng thủ.
3. **`## 3d. Mental Model & Thuật ngữ cho Fresher`**:
   - Mô hình tư duy trực quan (Analogy).
   - Bảng thuật ngữ chuyên ngành ngắn gọn.

Đồng thời cập nhật:
- `skills/tdq-spec/SKILL.md`: Yêu cầu kiểm tra §2c, §3c, §3d trước khi trình duyệt; bổ sung tóm tắt luồng vào tin nhắn chat.
- `skills/tdq-spec/references/spec-template-huong-dan.md`: Thêm checklist tự soát "Fresher Accessibility Check".
- `tests/test_spec_template.py`: Kiểm thử tự động đảm bảo khuôn mẫu Spec và các file spec mới luôn tuân thủ các section này.

### Năng lực dùng được

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `tdq-workflow:tdq-spec` | plugin:tdq-workflow | DÙNG | Cập nhật khuôn mẫu spec và hướng dẫn lập spec |
| `tdq-workflow:tdq-conventions` | plugin:tdq-workflow | NỀN | Quy tắc chung và user-facing-block |
| Đã xét 5 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ | Nghiên cứu các mẫu đặc tả kiến trúc dễ hiểu chuẩn quốc tế (C4 model, ADR, Sequence) |
| Interview | BỎ | Yêu cầu và bài toán của người dùng đã rất cụ thể và mạch lạc |
| QC độc lập (agent) | CÓ | Dùng `tdq-reviewer` thẩm định tính dễ hiểu và tuân thủ DocLint của template mới |

## Hỏi đáp

(Không có câu hỏi chặn; phương án kỹ thuật đã sẵn sàng trình duyệt)
