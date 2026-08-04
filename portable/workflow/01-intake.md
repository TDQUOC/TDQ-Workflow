# 01 — Intake: mở request & phân tích

Phase `no_state` → `analyze`. Mọi output cho user: **tiếng Việt**.

## Phần A — Mở request (phase `no_state`)

1. **Ghi lại yêu cầu.** Tạo `docs/tdq/requests/<slug>.md` với slug
   `YYYY-MM-DD-<kebab ≤5 từ, không dấu>`: nguyên văn yêu cầu của user + cách hiểu
   đầu tiên của bạn (mục tiêu, phạm vi đoán, chỗ chưa rõ).

2. **Đề xuất lane rồi HỎI.** Trình bày đúng khuôn này trong chat:
   - 2–3 dòng tóm tắt việc user muốn.
   - 1 dòng đề xuất lane kèm lý do cho CHÍNH việc này.
   - Câu hỏi: "Bạn muốn chạy lane nào: quick hay full?"

   Chọn lane: **quick** khi việc nhỏ, phạm vi rõ, ≤ ~3 file, không có ẩn số bên ngoài,
   hỏng thì sửa lại rẻ. **full** khi có tính năng mới, đổi kiến trúc/dữ liệu, còn câu
   hỏi chưa trả lời được, hoặc hỏng thì tốn kém. Phân vân → đề xuất full.
   **DỪNG chờ user trả lời.** Không tự chọn lane.

3. **Init state** ngay khi user chốt lane:
   ```
   python3 scripts/tdq_state.py init <slug> <quick|full>
   ```
   Lệnh này **xoá sạch** state cũ. Nếu đang có request khác còn dở → nói rõ slug và
   phase sẽ mất, **hỏi user trước** rồi mới chạy.

4. **Rẽ nhánh:**
   - `full` → `python3 scripts/tdq_state.py set phase=analyze`, làm tiếp Phần B ngay trong turn này.
   - `quick` → làm Phần C, không qua Phần B.

Xong khi: `state.json` có `active_request` và `lane` đúng thứ user chọn.
Bước kế tiếp: Phần B (full) hoặc Phần C (quick).

## Phần B — Phân tích (phase `analyze`, chỉ lane full)

Đóng vai chuyên gia đúng lĩnh vực của yêu cầu. Mục tiêu: rời phase này với **ZERO chỗ đoán**.

1. **Kiểm kê năng lực (B0).** Chạy `python3 scripts/skill_inventory.py`,
   chép thêm skill built-in đang thấy trong context, điền bảng phán quyết theo khuôn
   [references/skill-inventory.md](references/skill-inventory.md) vào
   `docs/tdq/knowledge/<slug>.md` mục `## Năng lực dùng được`. Phân vân → DÙNG.
   Agent không có skill system → liệt kê công cụ/lệnh tương đương mình có, xét như skill.

2. **Đọc code.** Tìm hết chỗ yêu cầu này chạm tới: entry point, luồng dữ liệu, config,
   test. Ghi lại phiên bản/framework đang dùng.

3. **Research nhiều hướng.** 2–4 truy vấn khác góc nhìn qua `tavily-primary`
   (harness không có tavily → dùng công cụ search sẵn có của nó; lỗi mới đổi nguồn, không
   gọi song song). Lưu `docs/tdq/research/<slug>.md` dạng: truy vấn → nguồn → điều rút ra.
   Bỏ qua chỉ khi việc thuần nội bộ, không có ẩn số bên ngoài. Đủ tiêu chí deep
   search (≥2 dấu hiệu) → theo workflow/06-deep-search.md.

4. **Vòng interview.** Liệt kê MỌI câu hỏi làm thay đổi kết quả (phạm vi, UX, dữ liệu,
   lỗi, hiệu năng, tương thích). Hỏi theo cụm 2–4 câu, mỗi câu kèm 2–4 phương án có
   đánh dấu `(Đề xuất)` và lý do một dòng. Ghi hỏi–đáp vào `docs/tdq/questions/<slug>.md`.
   **Lặp** đến khi không còn câu hỏi nào làm đổi kết quả — nhiều vòng là bình thường.
   Không lấp chỗ trống bằng phỏng đoán. **Câu cuối mỗi vòng là bắt buộc**, kể cả khi chỉ
   có 1 câu hỏi: hỏi thêm đúng câu "Bạn muốn bổ sung thêm gì không?" với hai lựa chọn
   `Không, đủ rồi — làm tiếp đi` (Đề xuất) và `Có — tôi nói thêm`, để user trả lời mở.

5. **Chốt kiến thức.** Viết `docs/tdq/knowledge/<slug>.md`: quyết định đã chốt, ràng buộc,
   cách tiếp cận đã chọn + lý do, phương án đã loại + lý do, nguồn.

5b. **Quyết lộ trình.** Thêm mục `## Lộ trình` vào knowledge: bảng `Bước/phase | CÓ-BỎ |
   Vì sao` cho từng bước còn lại (research thêm, QC độc lập bằng agent, review sâu,
   chia subagent…). Khung bất biến không được bỏ: phân tích → spec/plan → implement →
   report. Chỉ cắt bước THỪA cho chính việc này, nêu lý do; phân vân → GIỮ. Lộ trình
   này chép nguyên sang spec §1b và user duyệt spec là duyệt luôn nó.

6. **Kiểm cổng** trước khi đi tiếp:
   - Phạm vi cuối đã rõ chưa: làm ra gì, có gì mới, output cụ thể là gì?
   - Có cần model / download / cài đặt gì không?
   - Phạm vi QC/test/validate đã có chưa?
   Thiếu bất kỳ mục nào → quay lại bước 4.

Xong khi: `knowledge/<slug>.md` (có mục Lộ trình) đã viết và cả 3 câu hỏi kiểm cổng đều
trả lời được.
Bước kế tiếp: `python3 scripts/tdq_state.py set phase=spec` rồi sang
[02-spec.md](02-spec.md) — cùng turn nếu interview đã xong, còn phải
hỏi user thì trình câu hỏi và dừng.

## Phần C — Lane quick

Quick = rút gọn, KHÔNG cắt bước tư duy. Chi tiết: [quick-lane.md](references/quick-lane.md).

1. **Phân tích.** Đọc đúng phần code liên quan. Có ẩn số bên ngoài (thư viện, API,
   phiên bản, cách làm chuẩn) → web search TRƯỚC khi viết gì (công cụ search sẵn có
   của harness); thuần nội bộ thì bỏ qua và nói rõ vì sao. Còn câu hỏi làm ĐỔI kết quả
   → interview theo cách hỏi ở Phần B bước 4 (kể cả ở quick, và vẫn kết thúc vòng bằng
   câu "Bạn muốn bổ sung thêm gì không?").
2. **Viết mini-spec/plan GỘP 1 file** `docs/tdq/plan/<slug>.md`, ≤ 40 dòng: phạm vi
   in/out, task checkbox mỗi task một test, DoD. Khuôn: [quick-lane.md](references/quick-lane.md).
3. **Trình tóm tắt ≤ 10 dòng** trong chat: sẽ làm gì, đụng file nào, validate thế nào,
   và đúng 1 dòng `Năng lực: <các skill sẽ DÙNG, hoặc "không có">` (phân vân → DÙNG).
   Giao engine ngoài (user yêu cầu hoặc bạn đề xuất) → thêm đúng 1 dòng máy-đọc
   `Thực thi external: engine=<codex|agy> · khó=<slug>`; luật chọn engine/model và
   luật cấm external cho task `(mcp)`: [quick-lane.md](references/quick-lane.md).
4. In đúng dòng: `➤ Duyệt: nhắn "duyệt quick" (giao engine ngoài: "duyệt quick external") · Góp ý: nhắn trực tiếp` rồi **DỪNG**.
5. User duyệt → chạy `python3 scripts/tdq_state.py approve quick [--mode external] --by "<nguyên văn>"` (chỉ thêm `--mode external` khi user nói external).
6. Append summary mini-plan vào `docs/workinglog/<hôm nay>.md` **TRƯỚC** khi sửa code —
   quick external thì dòng `Thực thi external:` phải nằm trong working log ở bước này.
7. Implement end-to-end trong 1 turn, chạy validate, báo kết quả ngắn gọn.
   Quick external: KHÔNG tự code — làm đúng "Nhánh external" của
   [04-build.md](04-build.md) (worktree `tdq-ext-<slug>`, gói task, chạy nền
   external_task.py, verify, diff-check, merge), fallback tự làm khi engine hỏng.
8. Append kết quả vào working log; hỏi user có commit không.

Xong khi: `quick_approved = true`, log đã ghi, việc đã validate xong.
Bước kế tiếp: hỏi user về commit; hết request thì `python3 scripts/tdq_state.py set phase=idle`.
