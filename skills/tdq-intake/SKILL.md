---
name: tdq-intake
description: Mở request TDQ mới - ghi yêu cầu, chọn lane, init state, phân tích + interview đến hết mơ hồ. Dùng cho MỌI prompt mới, kể cả câu hỏi/check/việc nhỏ.
---

# TDQ Intake — mở request & phân tích

Nạp [tdq-conventions](../tdq-conventions/SKILL.md) trước. Mọi output cho user: **tiếng Việt**.
Skill này lo hai phase: `no_state` → `analyze`.

## Tầng nhỏ — trả lời/sửa luôn, không mở request

Vào tầng `nhỏ` khi **cả 4** điều kiện đúng:

1. Không đổi hành vi sản phẩm, hoặc chỉ đổi đúng một chỗ hiển nhiên (typo, hằng số,
   chuỗi hiển thị, số phiên bản).
2. Không thêm và không xoá file mã nguồn.
3. Không đụng hook, state, gate duyệt.
4. Xong trong một turn, không có chỗ nào cần user chốt.

Ở tầng này: trả lời hoặc sửa luôn. Không mở request, không `init` state, không plan,
không QC. Có đổi repo thì vẫn chạy `tdq_finish.py --log` như mọi turn khác.

**Luật thoát (bắt buộc).** Giữa chừng vi phạm bất kỳ điều kiện nào → DỪNG tay, nói rõ
điều kiện nào vỡ, rồi mở request bình thường từ Phần A. Cấm làm tiếp ở tầng `nhỏ`.

## Phần A — Mở request (phase `no_state`)

Định nghĩa "yêu cầu mới": MỌI prompt của user khi KHÔNG có request mở — request mở
= có `active_request` VÀ `phase != idle`. Khi phase ≠ idle, message của user thuộc
request đang chạy (duyệt, góp ý, trả lời interview), không mở request lồng.

1. **Ghi lại yêu cầu.** Tạo `docs/tdq/brief/<slug>.md` với slug
   `YYYY-MM-DD-<kebab ≤5 từ, không dấu>`. Brief là file DUY NHẤT của phase intake +
   analyze, đúng 3 mục: `## Nguyên văn` (nguyên văn yêu cầu user + cách hiểu đầu tiên
   của bạn: mục tiêu, phạm vi đoán, chỗ chưa rõ), `## Hiểu & kiến thức`, `## Hỏi đáp`.
   Ở bước này chỉ viết mục đầu; hai mục sau để trống, Phần B điền.

2. **Đề xuất lane rồi HỎI.** Trong chat: 2–3 dòng tóm tắt việc user muốn. Rồi đúng 1
   dòng tự nhận định cỡ, dạng
   `Cỡ: <nhỏ|quick|full> · Cần: <research | interview | subagent | QC độc lập | skill ngoài | không>`
   — cột `Cần` chỉ liệt kê thứ CÓ THỂ bỏ, thứ luôn chạy thì không liệt kê. Rồi 1 dòng đề
   xuất lane kèm lý do cho CHÍNH việc này. Rồi câu hỏi "Bạn muốn chạy lane nào?" với
   option mỗi dòng theo khuôn [references/interview.md](references/interview.md), phương
   án đề xuất luôn đứng ở A:
   `- A (đề xuất): chế độ nhanh (express) — <lý do>` xuống dòng `- B: chế độ chuyên sâu (deep) — <lý do>`.
   Cách chọn: [references/lane-decision.md](references/lane-decision.md).
   **DỪNG chờ user trả lời.** Không tự chọn lane.

3. **Init state** ngay khi user chốt lane:
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" init <slug> <quick|full>
   ```
   Lệnh này **xoá sạch** state cũ. Nếu đang có request khác còn dở → nói rõ slug và
   phase sẽ mất, **hỏi user trước** rồi mới chạy.

4. **Rẽ nhánh:**
   - `full` → `... set phase=analyze`, làm tiếp Phần B ngay trong turn này.
   - `quick` → làm Phần C, không qua Phần B.

Xong khi: `state.json` có `active_request` và `lane` đúng thứ user chọn.
Bước kế tiếp: Phần B (chế độ chuyên sâu (deep)) hoặc Phần C (chế độ nhanh (express)).

## Phần B — Phân tích (phase `analyze`, chỉ chế độ chuyên sâu (deep))

Chỉ nạp khi chế độ chuyên sâu (deep) — chế độ nhanh không cần mục này. Đóng vai chuyên gia đúng lĩnh vực,
mục tiêu rời phase này với ZERO chỗ đoán. Làm đủ 6 bước (kiểm kê năng lực, đọc code,
research, interview, chốt kiến thức, kiểm cổng) theo
[references/analyze-full.md](references/analyze-full.md).

Xong khi: `brief/<slug>.md` đủ 3 mục (có `### Lộ trình`) và cả 3 câu hỏi kiểm cổng đều
trả lời được.
Bước kế tiếp: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=spec`
rồi sang [tdq-spec](../tdq-spec/SKILL.md) — cùng turn nếu interview đã xong, còn phải
hỏi user thì trình câu hỏi và dừng.

## Phần C — Chế độ nhanh (express)

Chế độ nhanh = rút gọn, KHÔNG cắt bước tư duy. Chi tiết: [references/quick-lane.md](references/quick-lane.md).

1. **Phân tích.** Đọc đúng phần code liên quan. Có ẩn số bên ngoài (thư viện, API,
   phiên bản) → web search qua `tavily-primary` TRƯỚC khi viết gì; thuần nội bộ thì bỏ
   qua và nói rõ vì sao. Còn câu hỏi làm ĐỔI kết quả → interview theo
   [references/interview.md](references/interview.md).
2. **Viết mini-spec/plan GỘP 1 file** `docs/tdq/plan/<slug>.md`, ≤ 40 dòng: phạm vi
   in/out, task checkbox mỗi task một test, DoD mỗi dòng kiểm được bằng lệnh.
   Checkbox có 3 trạng thái: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong. Lúc implement
   (bước 7) đánh `[~]` khi bắt đầu task và đổi sang `[x]` ngay khi test xanh.
3. **Trình tóm tắt ≤ 10 dòng** trong chat: sẽ làm gì, đụng file nào, validate thế nào,
   và đúng 1 dòng `Năng lực: <các skill sẽ DÙNG, hoặc "không có">` (phân vân → DÙNG).
4. In đúng dòng: `➤ Duyệt: nhắn "duyệt nhanh" (bỏ QC: "duyệt nhanh không QC"; "duyệt quick" vẫn chạy — duyệt xong implement ngay) · Góp ý: nhắn trực tiếp` rồi **DỪNG**.
5. User duyệt → chạy `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" approve quick [--no-qc] --by "<nguyên văn>"` (`--no-qc` CHỈ khi user nói rõ bỏ QC — im lặng về QC thì QC vẫn BẬT).
6. Append summary mini-plan vào `docs/workinglog/<hôm nay>.md` **TRƯỚC** khi sửa code.
7. Implement end-to-end trong 1 turn. Mỗi task: đánh `[~]` TRƯỚC khi sửa code (hook
   `edit_gate` CHẶN nếu plan không có `[~]`; `tests/**` được miễn trừ), red→green, đổi
   `[x]` NGAY khi test xanh — cấm gom tick cuối turn. Rồi chạy **QC** (mặc định BẬT): mỗi dòng DoD một
   phép kiểm, ghi bằng chứng vào mục `## QC` của plan. `quick_qc_skipped = true` → mục
   `## QC` chỉ có 1 dòng `BỎ theo yêu cầu user: "<nguyên văn>"`.
8. **Vòng fix khi QC FAIL hoặc thấy bug**: thêm task vào plan dưới
   `## QC vòng N — fix`, fix red→green, chạy lại hạng mục đã FAIL cộng hạng mục mà bản
   fix có thể làm hỏng. Có trần 3 vòng — vượt trần thì DỪNG, báo user, đề xuất chuyển lane
   full, giữ nguyên phase.
9. Append kết quả vào working log; hỏi user có commit không.

Xong khi: `quick_approved = true`, log đã ghi, mục `## QC` đã có, không còn test đỏ.
Bước kế tiếp: hỏi user về commit; hết request thì `... set phase=idle`.
