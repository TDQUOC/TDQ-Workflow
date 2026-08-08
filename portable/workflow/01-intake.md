# 01 — Intake: mở request & phân tích

Phase `no_state` → `analyze`. Mọi output cho user: **tiếng Việt**.

## Phần A — Mở request (phase `no_state`)

1. **Ghi lại yêu cầu.** Tạo `docs/tdq/requests/<slug>.md` với slug
   `YYYY-MM-DD-<kebab ≤5 từ, không dấu>`: nguyên văn yêu cầu của user + cách hiểu
   đầu tiên của bạn (mục tiêu, phạm vi đoán, chỗ chưa rõ).

2. **Đề xuất lane rồi HỎI.** Trong chat: 2–3 dòng tóm tắt việc user muốn. Rồi 1 dòng đề
   xuất lane kèm lý do cho CHÍNH việc này. Rồi câu hỏi "Bạn muốn chạy lane nào?" với
   option mỗi dòng theo khuôn ở bước 4, phương án đề xuất luôn đứng ở A:

   ```
   - A (đề xuất): quick — <lý do hợp việc này>
   - B: full — <lý do hợp việc này>
   ```

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

Chỉ nạp khi lane `full` — quick không cần mục này. Đóng vai chuyên gia đúng lĩnh vực,
mục tiêu rời phase này với ZERO chỗ đoán. Làm đủ 6 bước (kiểm kê năng lực, đọc code,
research, interview, chốt kiến thức, kiểm cổng) theo
[references/analyze-full.md](references/analyze-full.md).

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
   → interview theo cách hỏi ở [references/analyze-full.md](references/analyze-full.md)
   bước 4 (kể cả ở quick, và vẫn kết thúc vòng bằng câu "Bạn muốn bổ sung thêm gì không?").
2. **Viết mini-spec/plan GỘP 1 file** `docs/tdq/plan/<slug>.md`, ≤ 40 dòng: phạm vi
   in/out, task checkbox mỗi task một test, DoD. Khuôn: [quick-lane.md](references/quick-lane.md).
3. **Trình tóm tắt ≤ 10 dòng** trong chat: sẽ làm gì, đụng file nào, validate thế nào,
   và đúng 1 dòng `Năng lực: <các skill sẽ DÙNG, hoặc "không có">` (phân vân → DÙNG).
   Giao engine ngoài (user yêu cầu hoặc bạn đề xuất) → thêm đúng 1 dòng máy-đọc
   `Thực thi external: engine=<codex|agy> · khó=<slug>`; luật chọn engine/model và
   luật cấm external cho task `(mcp)`: [quick-lane.md](references/quick-lane.md).
4. In đúng dòng: `➤ Duyệt: nhắn "duyệt quick" (giao engine ngoài: "duyệt quick external" · bỏ QC: "duyệt quick không QC") · Góp ý: nhắn trực tiếp` rồi **DỪNG**.
5. User duyệt → chạy `python3 scripts/tdq_state.py approve quick [--mode external] [--no-qc] --by "<nguyên văn>"` (`--mode external` khi user nói external; `--no-qc` CHỈ khi user nói rõ bỏ QC — user im lặng về QC thì QC vẫn BẬT).
6. Append summary mini-plan vào `docs/workinglog/<hôm nay>.md` **TRƯỚC** khi sửa code —
   quick external thì dòng `Thực thi external:` phải nằm trong working log ở bước này.
7. Implement end-to-end trong 1 turn, rồi chạy **QC 3 hạng mục** theo
   [quick-lane.md](references/quick-lane.md) mục "QC ở quick" (mặc định BẬT) và ghi bằng
   chứng vào mục `## QC` của plan. `quick_qc_skipped = true` → mục `## QC` chỉ có 1 dòng
   `BỎ theo yêu cầu user: "<nguyên văn>"`.
   Quick external: KHÔNG tự code — làm đúng "Nhánh external" của
   [04-build.md](04-build.md) (worktree `tdq-ext-<slug>`, gói task, chạy nền
   external_task.py, verify, diff-check, merge), fallback tự làm khi engine hỏng.
8. **Vòng fix — BẮT BUỘC, kể cả khi user bỏ QC.** QC FAIL hoặc thấy bug → thêm task vào
   plan dưới `## QC vòng N — fix`, fix red→green, rồi chạy lại ĐỦ 3 hạng mục.
   Có trần 3 vòng — vượt trần thì DỪNG, báo user, đề xuất chuyển lane full, giữ nguyên phase.
   Lý do trần: quá 3 vòng nghĩa là việc không còn "quick", cần phân tích lại ở lane full.
9. Append kết quả vào working log; hỏi user có commit không.

Xong khi: `quick_approved = true`, log đã ghi, mục `## QC` đã có, không còn test đỏ.
Bước kế tiếp: hỏi user về commit; hết request thì `python3 scripts/tdq_state.py set phase=idle`.
