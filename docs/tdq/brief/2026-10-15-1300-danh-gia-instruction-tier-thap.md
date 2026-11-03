# BRIEF — Đánh giá độ chi tiết instruction TDQ Workflow cho model tier thấp và phương án tối ưu token context

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> "okay bây giờ mở request fan out subagent phân tích cụ thể từng phần nhỏ của tdq-workflow build và cho tôi biết liệu có đang quá ngắn gọn dẫn thới thiếu reference, template để các model tier thấp bị thiếu hướng dẫn và ngữ cảnh để tuân theo không? và phân tích thêm nếu bổ sung thì có phương án đè xuất nào để mà có thể có đầy đủ instruciton hướng dẫn chi tiết nhưng có những phương thức ứng dụng nào save token như kiểu lazy load chỉ load khi cần và release khi xong để còn context legth xử lí project mà không đốt quá nhiều context /token cho việc nạp instruction/skill/rule và output rrequest này là bảng phân tích chi tiết, chứng cứ, và đề xuất"

### Đọc bước đầu

- **Mục tiêu:** 
  1. Phân tích, mổ xẻ toàn diện từng phần nhỏ trong pipeline và instruction của TDQ Workflow (đặc biệt là phase `build`, `implement`, `qc`, `spec`, `plan`, các rules và hooks).
  2. Đánh giá xem hiện tại instruction có đang quá ngắn gọn, cô đọng dẫn đến việc các model tier thấp (như Haiku, các model mã nguồn mở nhỏ hoặc custom routers) thiếu reference, thiếu template cụ thể hoặc thiếu bối cảnh từng bước để tuân thủ không.
  3. Nghiên cứu và đề xuất các phương án kiến trúc cân bằng: vừa cung cấp đầy đủ hướng dẫn chi tiết, mẫu biểu và ràng buộc chặt chẽ cho model tier thấp, vừa tiết kiệm token tối đa (ví dụ: cơ chế lazy load chỉ nạp đúng file/section khi cần, giải phóng ngữ cảnh khi xong, nén mốc, hoặc phân cấp tier instruction động).
  4. Đầu ra của request này là một tài liệu báo cáo phân tích chi tiết toàn diện gồm: hiện trạng, chứng cứ thực tế, điểm nghẽn của model tier thấp, và bảng đề xuất các giải pháp kỹ thuật cụ thể.
- **Phạm vi dự kiến:**
  - Khảo sát toàn bộ thư mục `skills/` (59 files), `hooks/` (17 files), `agents/` (3 files), các rule references (`skills/tdq-build/references/rules/`, `vision-test-loop.md`, `team-mode.md`, `codex-mode.md`, `clean-code.md`), cơ chế prompt context injection trong `hooks/scripts/session_start.py` và `prompt_context.py`.
  - Phân tích cơ chế nạp context hiện tại của Claude Code / Codex / OpenCode đối với plugin skills.
  - Thiết kế kiến trúc Lazy Load / Context Lifecycle cho rule và reference.
- **Điểm chưa rõ:**
  - Người dùng muốn dừng ở mức báo cáo nghiên cứu và đề xuất giải pháp kiến trúc (RFC/Proposal), hay muốn triển khai nguyên mẫu (prototype) thử nghiệm ngay trong request này?

## Hiểu & kiến thức

### Năng lực dùng được

| Nguồn | Tên | Khớp chỗ nào | Quyết định | Lý do |
|---|---|---|---|---|
| 内置/MCP | `Agent` (subagent) | Fan-out subagent phân tích phase build và nghiên cứu lazy loading | **dùng** | Đã kích hoạt 2 subagent chạy ngầm song song phân tích đa chiều |
| Repo script | `scripts/context_surface.py` & `scripts/skill_tokens.py` | Đo lường chính xác dung lượng token và bề mặt ngữ cảnh các file | **dùng** | Cung cấp số liệu định lượng thực tế về carry-cost |
| Repo hook | `hooks/scripts/session_start.py` & `prompt_context.py` & `edit_gate.py` | Cơ chế bơm (inject) ngữ cảnh động và rào cản hành vi | **dùng** | Nơi hiện thực hóa cơ chế JIT Micro-injection |
| Repo skill | `skills/tdq-build/` & `skills/tdq-conventions/` | Khảo sát cấu trúc instruction, rules và templates | **dùng** | Đối tượng khảo sát và tái cấu trúc chính |
| Built-in | `Read`, `Edit`, `Write` | Đọc và lập tài liệu phân tích, đề xuất | **dùng** | Công cụ thao tác file tiêu chuẩn |

### Phân tích chi tiết & Chứng cứ định lượng (từ 2 Sub-agent)

#### 1. Định lượng bề mặt context hiện tại của TDQ Workflow
- **Tổng dung lượng văn bản hướng dẫn trên đĩa**: **~90.242 tokens** (75.953 tokens từ 45 file `references/`, 17.274 tokens từ 9 file `SKILL.md`, ~2.252 tokens từ metadata và khối ghim).
- **Điểm nóng carry-cost**: 
  - `SessionStart` hiện đang nạp tĩnh toàn bộ `chung.md` (**~2.000 tokens / 8.200 ký tự**) ngay từ đầu phiên, bất kể phiên đang ở phase `idle`, `analyze` hay `spec` chưa sửa dòng code nào.
  - Quy luật carry-cost: 10.000 tokens tài liệu nạp sớm $\times$ 20 lượt tool call = **200.000 tokens lãng phí** tái đọc lại mỗi phiên.

#### 2. Đánh giá: Có phải instruction đang quá ngắn gọn với model tier thấp?
- **Hoàn toàn chính xác**: Phong cách của TDQ Workflow hiện tại là **"Mệnh lệnh kỹ thuật cô đọng, triết lý cao (Dense Technical Commandments)"**. Model lớn (Claude 3.7 Sonnet, Opus) tự suy luận được, nhưng model nhỏ (Haiku, Qwen 2.5 Coder, Llama 3.1 8B) gặp 7 điểm gãy nghiêm trọng:
  1. *Lỗi cú pháp CLI*: Nhầm lẫn tham số (như `tdq_team.py clean T1.1` bị exit 2), lỗi escaping chuỗi nhiều dòng trên Windows PowerShell.
  2. *Quy tắc tick checkbox*: Model nhỏ không xem checkbox là hành động sửa file vật lý qua tool `Edit`, thường quên tick `[~]` hoặc tick dồn ở cuối turn.
  3. *TDD Đỏ-Xanh*: Thiếu định nghĩa cơ học về "Đỏ thật" vs "Đỏ ảo do sai đường dẫn" vs "Xanh sẵn", khiến model nhỏ viết assertion lỏng lẻo (`assert True`).
  4. *Cấu trúc trường `Chạm:`*: Thiếu chuẩn hóa cú pháp dẫn đến việc viết sai format (dùng array hoặc wildcard), khiến `tdq_team assign` xếp nhầm thành vùng khóa.
  5. *Quy trình QC (`qc.md`)*: Thiếu mẫu lệnh thực thi cho QC-F3 (kiến trúc), thiếu bảng mẫu cho 5 câu hỏi QC-F4 (SOLID), và thiếu quy tắc cắt gọt bằng chứng khiến log tràn context.
  6. *Thao tác Git ở Phase Report*: Dùng placeholder `<nhanh_goc>`, model nhỏ dễ chạy lệnh nguy hiểm (`git reset --hard`) khi working tree bị dirty.
  7. *Thư viện rules ngôn ngữ & Clean code*: Mỗi ngôn ngữ chỉ có đúng 1 ví dụ ngắn (~10 dòng); `clean-code.md` dùng ví dụ nội bộ của TDQ khiến model nhỏ không ánh xạ được sang domain dự án người dùng.
- **Hình mẫu thành công (`vision-test-loop.md`)**: File này sở hữu đầy đủ 4 yếu tố giúp model nhỏ làm việc hoàn hảo: (1) Trigger Decision Table dạng bảng `Input -> Action`; (2) Công thức hóa cơ học (`Given - When - Then`); (3) Bộ mã cấm tường minh `ANTI-1`..`ANTI-6` kèm code đối chứng WRONG/RIGHT; (4) Bảng ánh xạ Triệu chứng -> Giải pháp sửa ("Bounding box to CSS").

#### 3. Đề xuất 4 giải pháp kiến trúc: Đủ chi tiết nhưng Tiết kiệm Token Context

| STT | Trụ cột giải pháp | Cơ chế hoạt động | Hiệu quả tiết kiệm token |
|:---:|---|---|:---:|
| **G1** | **Kim tự tháp Instruction 3 tầng (Progressive Scaffolding)** | Tách tài liệu làm 3 tầng: Tầng 1 (Micro-rules &amp; Negative constraints, 50-150 tokens) luôn có sẵn; Tầng 2 (Khung xương mẫu điền chỗ trống - Fill-in Scaffold, 200-500 tokens) cho model nhỏ; Tầng 3 (Cookbook chi tiết &amp; Edge cases, 1.500-3.000 tokens) lưu tĩnh trên đĩa chỉ đọc khi gặp lỗi. | **Tiết kiệm 50% – 70%** token instruction tĩnh |
| **G2** | **Hook-driven JIT Micro-injection (Lazy load theo ngữ cảnh)** | Hook `PreToolUse:Edit` tự động mớm 3-4 dòng quy tắc vàng của ngôn ngữ khi agent sửa file `.ts`/`.py`/`.go` lần đầu; hook `prompt_context.py` chỉ mớm template DoD khi vào phase `qc`. Trì hoãn nạp `chung.md` ở `session_start.py` cho đến khi vào phase `implement`. | **Tiết kiệm 70% – 80%** carry-cost của rules |
| **G3** | **Externalized Tool Outputs &amp; Silent CLI (Chống tràn context)** | Các script kiểm thử (`tdq_test.py`, `doc_lint.py`) ghi log thô ra file tạm trên đĩa, terminal chỉ in $\le 2$ dòng tóm tắt + trích xuất dòng lỗi quyết định. Giữ conversation context luôn sạch sẽ. | **Tiết kiệm 40% – 60%** token phát sinh trong build/QC |
| **G4** | **State-Anchored Compaction &amp; Subagent Isolation** | Do state đã lưu bền vững trên đĩa (`brief`, `spec`, `plan`, `STATE.md`), context thô của phase trước có thể được nén an toàn giữa các phase lớn. Subagent thực thi trong sandbox riêng, giải phóng 100% token khi hoàn thành. | **Tiết kiệm 60% – 85%** carry-cost trên các request lớn |

### Phạm vi đã chốt

- **Trong phạm vi (In-scope):**
  1. Xây dựng Báo cáo Kiến trúc Đề xuất hoàn chỉnh (RFC / Architecture Blueprint) lưu tại `docs/kien-truc-instruction-lazy-load.md` gồm 5 phần lớn:
     - Hiện trạng & Đo đạc carry-cost định lượng thực tế (~90k tokens tài liệu).
     - Phân tích chi tiết 7 điểm gãy của model tier thấp khi gặp instruction cô đọng, triết lý cao.
     - Phân tích đối chứng các bài học thành công từ `vision-test-loop.md` (Trigger table, công thức mechanical, Anti-pattern codes, bảng Symptom -> Action).
     - Thiết kế chi tiết 4 giải pháp kiến trúc tối ưu ngữ cảnh (Kim tự tháp 3 tầng, Hook-driven JIT Micro-injection, Externalized Log & Silent CLI, State-Anchored Compaction & Session Handoff).
     - Lộ trình triển khai cụ thể từng bước cho TDQ Workflow.
  2. Triển khai ngay bước Quick-Win (G2) trong mã nguồn:
     - Tối ưu `hooks/scripts/session_start.py`: hoãn việc nạp tĩnh 8.200 ký tự `chung.md` ở đầu session khi mở phiên ở phase `idle`, `analyze`, `spec`, `plan`. Chỉ nạp tóm tắt ngắn gọn và chỉ nạp thân luật khi bước vào phase `implement` hoặc subagent.
     - Thiết kế cơ chế mẫu JIT micro-injection trong hook cho phép mớm micro-rules phù hợp ngữ cảnh mà không làm phình to context.
  3. Cập nhật và bổ sung unit test kiểm chứng cho việc nạp context có điều kiện của `session_start.py`.
- **Ngoài phạm vi (Out-of-scope):**
  - Chưa viết lại toàn bộ 18 file rules và cookbooks trong request này (sẽ làm theo lộ trình RFC ở các request tiếp theo).
- **Mức QC đã chốt:** `lite` (lựa chọn 3b).

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Research web | BỎ | Hai subagent chuyên sâu đã hoàn thành phân tích nội bộ toàn diện và đo đạc số liệu thực tế |
| Interview | CÓ | Đã hoàn thành 1 vòng phỏng vấn chốt đủ 3 câu hỏi (`1a 2a 3b`) |
| QC độc lập | BỎ | Áp dụng mức QC `lite` đã chọn |

## Hỏi đáp

### Vòng 1 (2026-10-15 13:10)

1. **Phạm vi đầu ra mong muốn cho request này**:
   - A (đề xuất): Xây dựng Báo cáo Kiến trúc Đề xuất hoàn chỉnh (RFC / Architecture Blueprint) lưu tại `docs/kien-truc-instruction-lazy-load.md` KÈM triển khai ngay bước Quick-Win (G2: hoãn nạp `chung.md` tại `session_start.py` đến phase `implement`, và thiết kế mẫu JIT micro-injection).
   - B: Chỉ lập báo cáo phân tích, chứng cứ và đề xuất thuần tài liệu (không chạm vào code thực thi).
   - C: Triển khai trọn gói toàn bộ cả 4 giải pháp và viết lại toàn bộ hệ thống file rules/cookbooks ngay trong đợt này.
   - **Người dùng chọn:** `1a`
2. **Định hướng kiến trúc tối ưu token bạn ưu tiên nhất**:
   - A (đề xuất): Kết hợp "Hook-driven JIT Micro-injection" + "Kim tự tháp 3 tầng".
   - B: Tập trung vào "Externalized Tool Outputs & Guided Compaction".
   - **Người dùng chọn:** `2a`
3. **Mức QC (chất lượng kiểm thử cho request này)**:
   - A: `full`
   - B: `lite` — DoD + unit test vùng chạm.
   - C: `ultra`
   - **Người dùng chọn:** `3b`
