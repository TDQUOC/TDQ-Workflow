# Báo Cáo Kiến Trúc Đề Xuất (RFC) — Tối Ưu Instruction và Lazy Loading Ngữ Cảnh Cho Model Tier Thấp

Ngày: 2026-10-15 · Bản: 1.0 · Tác giả: TDQ Workflow Core Team
Soul: chất lượng > runtime > context cost · luật gốc: `skills/tdq-conventions/references/soul.md`

## Mục lục

- 1. Tóm tắt điều hành & Hiện trạng định lượng
- 2. Phân tích 7 điểm gãy của model tier thấp
- 3. Bài học thành công từ mô hình `vision-test-loop.md`
- 4. Thiết kế chi tiết 4 giải pháp kiến trúc tối ưu ngữ cảnh
- 5. Lộ trình triển khai 3 giai đoạn cho TDQ Workflow

---

## 1. Tóm tắt điều hành & Hiện trạng định lượng

### 1.1. Nghịch lý mang vác ngữ cảnh (Context Carry-Cost)

Trong môi trường Agent tương tác đa lượt (multi-turn harness như Claude Code, Codex, OpenCode), mỗi tool call là một lượt gọi API độc lập. Mô hình phải đọc lại toàn bộ lịch sử ngữ cảnh đã tích lũy từ đầu phiên.
Chi phí mang vác thực tế được tính theo công thức:

$$\text{Tổng token tiêu thụ} = \text{Dung lượng nạp tĩnh} \times \text{Số lượt gọi công cụ (tool calls)}$$

Nếu hệ thống nạp sẵn 10.000 tokens tài liệu tĩnh ở đầu phiên, trải qua 20 tool calls trong quá trình làm việc, chi phí mang vác cộng dồn sẽ lên tới 200.000 tokens. Điều này không chỉ gây lãng phí chi phí API mà còn đẩy nhanh phiên làm việc tới ngưỡng nén ngữ cảnh (compaction), làm mất thông tin trao đổi quan trọng giữa người dùng và Agent.

Chi phí mang vác quá mức còn làm suy giảm năng lực suy luận của mô hình nhỏ. Khi context window bị chiếm dụng bởi hàng ngàn dòng tài liệu tĩnh, mô hình gặp hiện tượng "lost in the middle". Lúc đó, mô hình rất dễ bỏ sót các ràng buộc quan trọng nằm ở phần giữa ngữ cảnh.

### 1.2. Thống kê bề mặt ngữ cảnh hiện tại của TDQ Workflow

Số liệu đo đạc thực tế từ công cụ `context_surface.py` và `skill_tokens.py`:
- **Tổng dung lượng văn bản hướng dẫn tĩnh trên đĩa**: **~90.242 tokens**.
  - 45 file `references/`: 75.953 tokens (trung bình ~1.688 tokens/file).
  - 9 file `SKILL.md`: 17.274 tokens.
  - Khối ghim và metadata: ~2.252 tokens.
- **Top các file tài liệu có dung lượng lớn nhất**:

| Tên file tài liệu | Vị trí thư mục | Dung lượng ước tính | Vai trò chính |
|---|---|:---:|---|
| `plan-template.md` | `skills/tdq-plan/references/` | ~5.067 tokens | Khuôn mẫu lập kế hoạch TDD |
| `quick-lane.md` | `skills/tdq-intake/references/` | ~4.356 tokens | Quy trình luồng nhanh Express |
| `team-mode.md` | `skills/tdq-build/references/` | ~3.652 tokens | Cơ chế điều phối subagent song song |
| `uu-tien-tim-kiem.md`| `skills/tdq-setup/references/` | ~3.420 tokens | Quy tắc tìm kiếm 3 tầng LSP/Grep |
| `vision-test-loop.md` | `skills/tdq-build/references/` | ~3.150 tokens | Hướng dẫn kiểm thử giao diện & TDD |
| `codex-mode.md` | `skills/tdq-build/references/` | ~2.890 tokens | Quy chế kết nối runner Codex |
| `chung.md` | `skills/tdq-build/references/rules/` | ~2.000 tokens | Luật gọn build-less-than-asked |
| `clean-code.md` | `skills/tdq-conventions/references/` | ~1.950 tokens | 5 nguyên tắc SOLID và Clean Code |

- **Điểm nóng nạp tĩnh (Static Injection Bottleneck)**:
  - Hook `SessionStart` hiện tại nạp toàn bộ thân luật `chung.md` (**~2.000 tokens / 8.200 ký tự**) ngay khi khởi động phiên. Việc nạp này diễn ra ngay cả khi phiên đang ở phase `idle`, `analyze` hoặc `spec` mà chưa chỉnh sửa dòng code nào.

---

## 2. Phân tích 7 điểm gãy của model tier thấp

Các mô hình đầu bảng (Frontier models như Sonnet, Opus) sở hữu năng lực suy luận ngầm mạnh, dễ dàng diễn dịch các mệnh lệnh kỹ thuật cô đọng (Dense Technical Commandments). Ngược lại, các mô hình tier thấp (Haiku, Qwen 2.5 Coder, Llama 3 8B) gặp phải hiện tượng "instruction blindness" và vấp ngã ở 7 điểm gãy cụ thể:

### 2.1. Lỗi cú pháp dòng lệnh CLI (CLI Syntax Confusion)
- **Biểu hiện**: Mô hình nhỏ thường nhầm lẫn giữa subcommands và arguments. Ví dụ: gọi lệnh `tdq_team.py clean T1.1` thay vì `tdq_team.py sweep --clean` do thiếu bảng ví dụ cú pháp tường minh.
- **Hậu quả**: Lệnh văng exit 2, làm đứt mạch thực thi và đốt thêm turn để sửa sai.

### 2.2. Vi phạm quy tắc tick Checkbox trạng thái
- **Biểu hiện**: Mô hình nhỏ coi checkbox trong kế hoạch là văn bản mô tả chứ không nhận thức đó là hành động sửa file vật lý qua tool `Edit`.
- **Hậu quả**: Mô hình quên đánh dấu `[~]` khi bắt đầu task hoặc dồn việc tick `[x]` vào cuối turn, dẫn đến khóa an toàn `edit_gate` chặn thao tác ghi file.

### 2.3. Hiểu sai quy trình TDD Đỏ-Xanh (False Red / Weak Assertions)
- **Biểu hiện**: Thiếu tiêu chí phân biệt cơ học giữa 3 trạng thái kiểm thử. Đó là Đỏ thật (assert fail đúng logic nghiệp vụ), Đỏ giả (sai cú pháp hoặc sai đường dẫn), và Xanh sẵn (test rỗng).
- **Hậu quả**: Mô hình nhỏ chấp nhận assertion hời hợt (`assert True`) để nhanh chóng đạt trạng thái xanh mà không thực sự kiểm thử chức năng.

### 2.4. Sai lệch cú pháp khai báo vùng `Chạm:`
- **Biểu hiện**: Thay vì viết danh sách file phân cách bởi dấu phẩy, mô hình nhỏ dùng định dạng mảng JSON hoặc ký tự đại diện (`*`).
- **Hậu quả**: Bộ phân tích vùng làm việc `tdq_team assign` không nhận diện được khóa file, gây lỗi khóa ghi đè giữa các subagent chạy song song.

### 2.5. Thiếu định hướng thực thi ở Phase QC (`qc.md`)
- **Biểu hiện**: Thiếu mẫu câu lệnh cụ thể cho vòng kiểm định QC-F3 (kiến trúc hệ thống). Đồng thời thiếu bảng 5 câu hỏi cho QC-F4 (nguyên tắc SOLID) và thiếu quy định giới hạn độ dài bằng chứng log.
- **Hậu quả**: Log kiểm thử bị dán tràn lan hàng trăm dòng vào chat, làm kiệt quệ context window.

### 2.6. Thao tác Git nguy hiểm ở Phase Báo Cáo
- **Biểu hiện**: Gặp các placeholder mang tính trừu tượng như `<nhanh_goc>`, mô hình nhỏ dễ đoán mò và thực thi các lệnh nguy hiểm như `git reset --hard` khi nhánh làm việc chưa sạch.
- **Hậu quả**: Nguy cơ mất mã nguồn vừa viết và làm hỏng trạng thái repository.

### 2.7. Thư viện luật ngôn ngữ thiếu mẫu đối chứng thực tế
- **Biểu hiện**: Mỗi ngôn ngữ trong `skills/tdq-build/references/rules/` chỉ có đúng một đoạn code mẫu ~10 dòng. Tài liệu `clean-code.md` sử dụng ví dụ đặc thù nội bộ của TDQ Workflow thay vì bài toán miền nghiệp vụ phổ thông.
- **Hậu quả**: Mô hình nhỏ không thể ánh xạ quy tắc vào mã nguồn dự án thực tế của người dùng.

---

## 3. Bài học thành công từ mô hình `vision-test-loop.md`

Tài liệu `vision-test-loop.md` là minh chứng rõ nét cho việc hướng dẫn thành công các mô hình tier thấp nhờ 4 cơ chế cơ học:

| Thành phần cơ học | Cơ chế vận hành | Hiệu quả với model tier thấp |
|---|---|---|
| **Bảng quyết định kích hoạt (Trigger Decision Table)** | Định dạng rõ ràng: `Nếu [Điều kiện đầu vào] → Làm [Hành động]` | Loại bỏ phán đoán cảm tính; mô hình tra cứu như bảng ánh xạ trạng thái |
| **Công thức hóa quy trình (Given - When - Then)** | Mẫu kịch bản 3 bước bắt buộc cho mọi ca kiểm thử | Ngăn chặn việc viết test sơ sài hoặc bỏ qua bước chuẩn bị dữ liệu |
| **Hệ thống mã cấm tường minh (`ANTI-1`..`ANTI-6`)** | Định danh từng lỗi phổ biến kèm cặp đối chứng WRONG / RIGHT | Giúp mô hình tự soi chiếu mã nguồn trước khi gọi lệnh hoàn tất |
| **Bảng Triệu chứng → Giải pháp (Symptom to Action)** | Liệt kê lỗi thường gặp và lệnh khắc phục trực tiếp | Khắc phục sự cố nhanh chóng mà không cần suy luận nguyên nhân sâu xa |

### Bảng Mã Cấm Tường Minh (Anti-Patterns) Đề Xuất Ứng Dụng Toàn Diện

```markdown
- ANTI-1 (Fake Red): CẤM coi lỗi ImportError hay sai đường dẫn file test là trạng thái ĐỎ hợp lệ của TDD.
- ANTI-2 (Blind Assertion): CẤM viết assert True, assert len(res) >= 0 hoặc các câu khẳng định luôn đúng.
- ANTI-3 (Dirty State Git): CẤM gọi git checkout, git reset --hard khi git status còn file sửa đổi chưa stash/commit.
- ANTI-4 (Late Tick): CẤM sửa quá 2 lần tool Edit mà chưa cập nhật trạng thái [~] trên plan file.
- ANTI-5 (Raw Dump): CẤM dán log kiểm thử quá 15 dòng vào tin nhắn chat; phải trích xuất tóm tắt và lỗi chính.
- ANTI-6 (Broad Area): CẤM khai báo Chạm mang ký tự đại diện wildcard (*) hoặc thư mục bao trùm cấp cha.
```

---

## 4. Thiết kế chi tiết 4 giải pháp kiến trúc tối ưu ngữ cảnh

Để vừa cung cấp đầy đủ hướng dẫn chi tiết cho mô hình tier thấp, vừa bảo toàn ngân sách token ngữ cảnh, kiến trúc đề xuất áp dụng 4 giải pháp đồng bộ:

```
+--------------------------------------------------------------------------+
|                  KIẾN TRÚC NGỮ CẢNH ĐA TẦNG TDQ WORKFLOW                 |
+--------------------------------------------------------------------------+
| [Tầng 1: Micro-Rules] (50-150 tok)  -> Nạp sẵn trong Hook / Ghim đầu     |
| [Tầng 2: Scaffolds]   (200-500 tok) -> Hook mớm đúng lúc (JIT Injection) |
| [Tầng 3: Cookbooks]   (1.5k-3k tok) -> Lưu tĩnh trên đĩa, đọc khi lỗi   |
+--------------------------------------------------------------------------+
| Chống tràn context: Log ghi ra đĩa (.log) -> Terminal in <= 2 dòng tóm tắt|
| Nén ngữ cảnh an toàn: State lưu bền vững trên đĩa (brief, spec, plan)    |
+--------------------------------------------------------------------------+
```

### 4.1. Trụ cột 1: Kim tự tháp Instruction 3 tầng (Progressive Scaffolding)
- **Tầng 1 — Micro-rules & Negative Constraints (50 – 150 tokens)**:
  - Chứa các mệnh lệnh cốt lõi, danh sách mã cấm ngắn gọn (như `ANTI-1`, `ANTI-2`) và quy tắc vàng. Luôn hiện diện trong context hoặc được ghim ở đầu phiên.
- **Tầng 2 — Khung xương mẫu điền chỗ trống - Fill-in Scaffolds (200 – 500 tokens)**:
  - Cung cấp sẵn khung code, template file Markdown chuẩn hóa và các trường dữ liệu cần điền. Tầng này được nạp động theo pha công việc.
- **Tầng 3 — Sổ tay hướng dẫn & Ca biên - Cookbooks & Edge Cases (1.500 – 3.000 tokens)**:
  - Lưu trữ toàn bộ giải thích chi tiết, lý thuyết nền tảng, bài học kinh nghiệm và ví dụ đa ngôn ngữ. Tầng này nằm cố định trên đĩa và chỉ được Agent đọc khi gặp lỗi bế tắc.

### 4.2. Trụ cột 2: Bơm ngữ cảnh tức thời qua Hook (Hook-driven JIT Micro-injection)
- **Tối ưu hóa `SessionStart` (Bước Quick-Win)**:
  - Chỉ nạp dòng tiêu đề tóm tắt trỏ đường (< 200 tokens) ở đầu phiên khi ở các phase phân tích (`idle`, `analyze`, `spec`, `plan`).
  - Chỉ nạp toàn bộ thân luật `chung.md` khi phiên làm việc chính thức chuyển sang phase viết mã (`implement`) hoặc khi khởi tạo subagent chuyên trách.
- **Mớm quy tắc ngôn ngữ qua `PreToolUse:Edit`**:
  - Khi Agent gọi lệnh `Edit` lần đầu trên một định dạng file (ví dụ: `.ts`, `.py`, `.go`), hook sẽ tự động kiểm tra và mớm đúng 3 dòng quy tắc vàng của ngôn ngữ đó vào ngữ cảnh.
- **Mớm khung kiểm định qua `prompt_context.py`**:
  - Khi workflow chuyển sang phase `qc`, hook sẽ tự động mớm bảng mẫu 5 câu hỏi SOLID và tiêu chí nghiệm thu DoD thay vì nạp từ đầu phiên.

### 4.3. Trụ cột 3: Đưa dữ liệu thô ra tệp ngoài & CLI tinh gọn (Externalized Tool Outputs & Silent CLI)
- **Giới hạn đầu ra terminal**:
  - Các script kiểm tra và đo lường (`tdq_test.py`, `doc_lint.py`, `token_budget.py`) ghi toàn bộ kết quả thực thi chi tiết ra tệp nhật ký trên đĩa (`docs/tdq/.log`).
  - Terminal chỉ in tối đa 2 dòng tóm tắt trạng thái và trích xuất đúng dòng lỗi quyết định khi kiểm thử thất bại.
- **Hiệu quả**:
  - Loại bỏ hoàn toàn tình trạng phình to ngữ cảnh do các đoạn trace-log dài hàng trăm dòng.

### 4.4. Trụ cột 4: Nén ngữ cảnh dựa trên mốc trạng thái bền vững (State-Anchored Compaction)
- **Bảo toàn trạng thái trên đĩa**:
  - Toàn bộ thông tin quan trọng của dự án đã được lưu trữ bền vững tại `docs/tdq/STATE.md`, các file `brief`, `spec` và `plan`.
- **Cơ chế nén an toàn**:
  - Khi kết thúc mỗi phase lớn, hệ thống có thể kích hoạt nén ngữ cảnh (compaction) mà không lo mất mát dữ liệu logic. Lịch sử tìm kiếm và các đoạn code nháp tạm thời được giải phóng hoàn toàn khỏi context window.

---

## 5. Lộ trình triển khai 3 giai đoạn cho TDQ Workflow

```
+-------------------------------------------------------------------------+
| LỘ TRÌNH 3 GIAI ĐOẠN                                                    |
|                                                                         |
| Giai đoạn 1: Quick-Win Ngay (Request Hiện Tại)                          |
| - Hoãn nạp chung.md ở SessionStart theo phase                           |
| - Tiết kiệm ngay ~2.000 tokens mang vác đầu phiên                       |
|                                                                         |
| Giai đoạn 2: Chuẩn hóa Kim Tự Tháp & Cookbooks                          |
| - Tách 18 file rules và references thành Micro-rules + Cookbooks        |
| - Bổ sung mẫu đối chứng WRONG/RIGHT chuẩn cơ học                        |
|                                                                         |
| Giai đoạn 3: Tự động hóa JIT Hook & Tinh gọn CLI                        |
| - Triển khai PreToolUse JIT Micro-injection cho ngôn ngữ                |
| - Tinh gọn toàn bộ đầu ra terminal của test suite sang file log         |
+-------------------------------------------------------------------------+
```

### 5.1. Kế hoạch chi tiết từng giai đoạn

| Giai đoạn | Hạng mục thực hiện chính | Đầu ra bàn giao | Mục tiêu token đạt được |
|---|---|---|:---:|
| **Giai đoạn 1** (Ngay) | Hoãn nạp `chung.md` ở `SessionStart` theo phase; tối ưu log | Hook `session_start.py` cập nhật; test xanh | Giảm **~2.000 tokens** carry-cost ở đầu mọi session |
| **Giai đoạn 2** (Tiếp theo) | Phân rã 18 file rules và references; thiết lập mã cấm `ANTI` | Thư mục `cookbooks/` trên đĩa; `SKILL.md` rút gọn | Tiết kiệm **50% - 70%** dung lượng instruction tĩnh |
| **Giai đoạn 3** (Dài hạn) | Bật JIT Injection trên `PreToolUse`; tinh gọn toàn bộ CLI output | Hook `edit_gate.py` mở rộng; CLI wrapper | Giảm **40% - 60%** rác phát sinh trong quá trình code |

### 5.2. Giai đoạn 1: Triển khai Quick-Win trong mã nguồn (Thực hiện ngay)
- Tinh chỉnh `hooks/scripts/session_start.py` hoãn nạp thân luật `chung.md` ở các phase ngoài `implement`.
- Cập nhật bộ unit test bảo đảm độ ổn định tuyệt đối và ghi nhận log chính xác.
- **Kết quả đạt được**: Giảm ngay ~2.000 tokens carry-cost cho mọi phiên làm việc ban đầu.

### 5.3. Giai đoạn 2: Tái cấu trúc thư viện Rule và Tài liệu tham chiếu
- Tách 18 file rules và references hiện có thành 3 tầng rõ rệt: Tầng 1 (Micro-rules đặt trong `SKILL.md`), Tầng 2 (Mẫu scaffold điền chỗ trống), và Tầng 3 (Cookbooks chi tiết).
- Bổ sung bảng đối chứng WRONG/RIGHT và mã cấm tường minh theo khuôn mẫu `vision-test-loop.md`.

### 5.4. Giai đoạn 3: Hoàn thiện hệ thống Hook JIT và CLI tinh gọn
- Mở rộng hook `PreToolUse` để tự động nhận diện ngôn ngữ và mớm quy tắc biên tập phù hợp.
- Chuẩn hóa đầu ra của toàn bộ bộ công cụ CLI sang định dạng `≤ 2` dòng tóm tắt, xuất chi tiết ra log file để giải phóng 100% rác ngữ cảnh.
