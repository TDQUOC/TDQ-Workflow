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
   `YYYY-MM-DD-HHMM-<kebab ≤5 từ, không dấu>`. Brief là file DUY NHẤT của phase intake +
   analyze, đúng 3 mục: `## Nguyên văn` (nguyên văn yêu cầu user + cách hiểu đầu tiên
   của bạn: mục tiêu, phạm vi đoán, chỗ chưa rõ), `## Hiểu & kiến thức`, `## Hỏi đáp`.
   Ở bước này chỉ viết mục đầu; hai mục sau để trống, Phần B điền. Dòng 2 của brief —
   ngay dưới tiêu đề — copy nguyên văn dòng sau (spec/plan/qc/report cũng mang dòng này):

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

2. **Đề xuất lane rồi HỎI.** Trong chat: 2–3 dòng tóm tắt việc user muốn. Tự nhận định
   cỡ/nhu cầu (`Cỡ:/Cần:`) là bước NỘI BỘ — dùng để chọn phương án đề xuất, KHÔNG in dòng
   đó ra chat. Rồi câu hỏi "Bạn muốn chạy pipeline nào?" với option mỗi dòng theo khuôn
   [references/interview.md](references/interview.md), phương án đề xuất luôn đứng ở A:
   `- A (đề xuất): chế độ nhanh (express) — <lý do>` xuống dòng `- B: chế độ chuyên sâu (deep) — <lý do>`,
   theo đúng khuôn đầy đủ (gồm khối giải thích nghĩa 2 pipeline) ở
   [references/lane-decision.md](references/lane-decision.md).
   **DỪNG chờ user trả lời.** Không tự chọn lane.

3. **Init state** ngay khi user chốt lane:
   ```
   python3 "${CLAUDE_PROJECT_DIR}/.claude/tdq/scripts/tdq_state.py" init <slug> <quick|full>
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
Interview đi từ tổng quát đến chi tiết: **vòng scope** trước (mặt nào + bối cảnh bằng số,
theo [references/scope-round.md](references/scope-round.md)), rồi mới hỏi chi tiết trong
đúng các mặt user chọn. Vòng scope có điều kiện; BỎ thì ghi một dòng lý do vào brief.

Xong khi: `brief/<slug>.md` đủ 3 mục (có `### Lộ trình`) và cả 3 câu hỏi kiểm cổng đều
trả lời được.
Bước kế tiếp: `python3 "${CLAUDE_PROJECT_DIR}/.claude/tdq/scripts/tdq_state.py" set phase=spec`
rồi sang [tdq-spec](../tdq-spec/SKILL.md) — cùng turn nếu interview đã xong, còn phải
hỏi user thì trình câu hỏi và dừng.

## Phần C — Chế độ nhanh (express)

Chế độ nhanh = rút gọn, KHÔNG cắt bước tư duy. Chín bước thi hành — từ phân tích tới hỏi
commit — nằm ở [references/quick-lane.md](references/quick-lane.md) mục
`## Chín bước thi hành`. **BẮT BUỘC mở file đó và đọc hết chín bước trước khi làm bước 1;
cấm làm theo trí nhớ.** Cùng file đó có luôn khuôn mini-plan, luật tick, luật QC và vòng fix.

Xong khi: `quick_approved = true`, log đã ghi, mục `## QC` đã có, không còn test đỏ.
Bước kế tiếp: hỏi user về commit; hết request thì `... set phase=idle`.
