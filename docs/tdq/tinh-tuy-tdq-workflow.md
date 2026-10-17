# Tinh túy TDQ Workflow — Các bất biến kiến trúc & bảo tồn hiệu năng

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Mục đích tài liệu

Tài liệu này đóng vai trò là **"Bản thiết kế Bất biến" (Architectural Invariants & Safeguards)** của TDQ Workflow. Mọi đợt nâng cấp, tái cấu trúc hoặc bổ sung tính năng trong tương lai **BẮT BUỘC** phải đối chiếu với tài liệu này để đảm bảo không làm suy giảm hiệu năng, không gây nghẽn tiến trình, không làm phình ngữ cảnh và không làm mai một những giá trị cốt lõi đã được kiểm chứng thực tế trên cả 3 nền tảng: **Windows 11, macOS Apple Silicon và Linux Ubuntu**.

---

## 6 Trụ cột Tinh túy Bất biến của TDQ Workflow

### 1. Hiệu năng Thực thi Đa nền tảng (Cross-Platform Execution Velocity)
- **Cơ chế Stop-Batching (`hooks/scripts/stop_batch_checker.py`)**:
  - *Nguyên lý*: Không bao giờ chạy các tiến trình nặng (`py_compile`, `doc_lint`, static analyzers) lặp đi lặp lại ở mỗi thao tác `Edit/Write` (tránh nghẽn process spawn 70ms trên Windows). Chỉ ghi buffer đường dẫn tạm siêu tốc (0.26ms) và gom một lượt kiểm tra duy nhất tại sự kiện `Stop`.
  - *Bất biến*: Tuyệt đối không phục hồi cơ chế kiểm tra đồng bộ dạng chặn (blocking synchronous linting) tại `PreToolUse:Edit`.
- **Liên kết NTFS Directory Junction & Symlink Sharing (`scripts/tdq_team.py`)**:
  - *Nguyên lý*: Khi khởi tạo Git Worktree cho các subagents chạy song song, luôn chia sẻ `node_modules` và `.venv` từ repo gốc thông qua `mklink /J` (trên Windows) hoặc `ln -s` (trên macOS/Linux) trong ~9ms.
  - *Bất biến*: Nghiêm cấm việc sao chép vật lý thư mục phụ thuộc hoặc chạy lại lệnh cài đặt (`npm install`, `pip install`) trong worktree mới.

---

### 2. Kỷ luật Quản trị Ngữ cảnh & Nén Chiến lược (Context Preservation & Compaction)
- **Strategic Compaction Gate (`hooks/scripts/strategic_compact_gate.py`)**:
  - *Nguyên lý*: Giám sát mức tiêu thụ ngữ cảnh theo trọng số công cụ (`WebFetch`: 10, `Read`: 5, `Edit`: 2, `Bash`: 1). Chỉ cảnh báo nén tại các ranh giới tự nhiên (`spec_approved`, `plan_approved`, `wave_transition`).
  - *Bất biến*: Không ngắt quãng giữa chừng khi subagent đang trong chu trình suy luận TDD Red $\rightarrow$ Green.
- **Khống chế Digest Payload & Cấm Dán Thô**:
  - *Nguyên lý*: Toàn bộ 6 subagents đều bị giới hạn digest output $\le 1.500$ ký tự và giao thức bàn giao JSON Schema $\le 200$ tokens (`TDQ_HANDOFF_PAYLOAD`).
  - *Bất biến*: Tuyệt đối cấm subagent dán raw output/logs vào hội thoại làm tràn bộ nhớ context của agent chính.

---

### 3. An toàn Điều phối Song song (TCAS AST Collision Prevention)
- **Thuật toán Phân tích Cú pháp AST Import (`scripts/tdq_team.py`)**:
  - *Nguyên lý*: Hệ thống phòng chống va chạm phân tích trực tiếp cây cú pháp trừu tượng (`ast.parse`) của mã nguồn. Nếu Task B import module mà Task A sửa đổi, Task B tự động bị đẩy sang Wave kế tiếp.
  - *Bất biến*: Không quay lại cơ chế so khớp đường dẫn tệp thô (string matching) thuần túy vì sẽ bỏ sót xung đột ngữ nghĩa ngầm (Semantic Collision).

---

### 4. Quản trị Tri thức Tự học Có Kiểm duyệt (Governed Continuous Learning)
- **Vùng đệm Cách ly Tri thức (`scripts/tdq_harvest.py`)**:
  - *Nguyên lý*: Tri thức và bài học sửa lỗi từ working log chỉ được trích xuất vào vùng staging `docs/tdq/knowledge/candidates/`. Bắt buộc phải qua lệnh duyệt của người dùng/lead (`tdq_harvest.py approve`) mới được nạp vào kho chính thức.
  - *Bất biến*: Tuyệt đối không cho phép AI tự động ghi đè hay nạp thẳng bài học vào bộ nhớ vĩnh viễn nhằm triệt tiêu hoàn toàn rủi ro nhiễm độc bộ nhớ (0% Memory Poisoning).

---

### 5. Kỷ luật Clean Code & Triết lý Bất biến (Clean Code Invariants & Soul)
- **Ưu tiên Tối thượng của Soul**:
  $$\text{Chất lượng} > \text{Runtime} > \text{Context Cost}$$
- **3 Quy chuẩn Mã nguồn Bất biến**:
  1. *Immutability by Default*: Ưu tiên dữ liệu bất biến, loại bỏ side-effects ngoài ý muốn.
  2. *Function Length Ceiling*: Mỗi hàm không vượt quá 50 dòng vật lý. Khi vượt quá, bắt buộc chia tách thành private helper functions.
  3. *Kỷ luật TDD Bắt buộc*: Luôn viết test kiểm chứng Red trước khi viết code triển khai Green.

---

### 6. Đội ngũ 6 Subagents Tinh hoa Phân nhiệm Nghiêm ngặt
- **Quy tắc Least Privilege (Đặc quyền Tối thiểu)**:
  - Nhóm Thẩm định (`tdq-reviewer`, `tdq-qc-tester`, `tdq-security-reviewer`): **Chỉ đọc (Strict Read-Only)**, không cấp quyền Edit/Write để đảm bảo tính khách quan tuyệt đối.
  - Nhóm Xử lý Mã nguồn (`tdq-implementer`, `tdq-build-resolver`, `tdq-refactor-cleaner`): Chỉ làm việc trong Git Worktree cô lập; `build-resolver` khống chế diff tối thiểu $< 5$ dòng; `refactor-cleaner` bắt buộc xuất Deletion Audit Log khi xóa dead code.

---

## Bảng Đối chiếu Tự kiểm tra Trước Mọi Thay đổi (Pre-Merge Regression Checklist)

Trước khi merge bất kỳ tính năng mới nào vào nhánh `dev` hoặc `main`, chạy checklist:

- [ ] 1. `python3 -m pytest tests/test_tcas_ast.py tests/test_harvest.py tests/test_agent_frontmatter.py tests/test_soul_rules.py` $\rightarrow$ 100% PASS.
- [ ] 2. `python3 scripts/tdq_setup.py --khong-log` $\rightarrow$ Đạt các bậc kiểm tra.
- [ ] 3. Kiểm tra tính tương thích đa nền tảng (POSIX paths, Windows backslashes, encoding UTF-8).
- [ ] 4. Không đưa vào các lệnh synchronous blocking gây lag cho môi trường Windows.
- [ ] 5. Không bỏ qua cổng kiểm duyệt tri thức (`tdq_harvest.py`).
- [ ] 6. Giữ vững trần digest $\le 1.500$ ký tự cho mọi subagent mới.
