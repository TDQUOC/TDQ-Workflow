# BRIEF — Quốc tế hoá bộ workflow: cổng duyệt không còn bám một ngôn ngữ

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> ko cần đo nữa. đóng request và mở request mới check xem đã đưa bộ workflow này thành international chưa, nghĩa là đổi rule để cả duyệt cũng thành như A. duyệt, B góp ý thêm,... để không bị ràng buộc vòa chỉ đúng 1 ngôn ngữ nữa

**Cách hiểu đầu tiên**

- Mục tiêu: kiểm xem bộ workflow TDQ đã thật sự "international" chưa — trọng tâm là CỔNG DUYỆT.
  Hiện luật bắt user nhắn đúng chữ tiếng Việt ("duyệt spec", "duyệt plan", "duyệt quick"),
  nên người dùng ngôn ngữ khác không qua cổng được.
- Hướng user muốn: chuyển câu mời duyệt sang dạng chọn theo CHỮ CÁI — `A. duyệt` ·
  `B. góp ý thêm` … — để câu trả lời "A"/"B" là tín hiệu chính, không phụ thuộc ngôn ngữ.
- Phạm vi đoán: `scripts/tdq_state.py` (regex nhận duyệt + các dòng `say`/`action`/`forbidden`
  của từng phase), các skill `tdq-*` (khuôn câu hỏi + khối `➤ Duyệt:`), hook nhắc việc,
  và bộ đo `scripts/tdq_eval.py` (RE_APPROVE, RE_DUYET_RO) nếu luật đổi.
- Chỗ chưa rõ: (a) đây là việc CHECK-rồi-báo hay CHECK-rồi-SỬA luôn; (b) có giữ song song
  cách cũ (gõ "duyệt spec") không, hay bỏ hẳn; (c) output cho user có còn bắt buộc tiếng Việt
  (luật `skills/tdq-conventions/SKILL.md:10`) hay cũng đa ngôn ngữ theo ngôn ngữ user nhắn.

## Hiểu & kiến thức

### Năng lực dùng được

| Skill | Nguồn | Phán quyết |
|---|---|---|
| tdq-intake / tdq-spec / tdq-plan / tdq-build | plugin:tdq-workflow | DÙNG — chính chúng in khối `➤ Duyệt:` sẽ phải đổi |
| tdq-conventions | plugin:tdq-workflow | DÙNG — `references/user-facing-block.md` giữ khuôn khối cuối turn |
| tdq-status | plugin:tdq-workflow | DÙNG — cũng in dòng `➤ Duyệt:` (SKILL.md:42) |
| superpowers:* , plugin-dev:* | plugin | BỎ — không liên quan cổng duyệt |

### Hiện trạng đã đọc trong code (nguồn: đọc trực tiếp 2026-08-21)

- `hooks/scripts/prompt_context.py:31-51` — nhận duyệt bằng **regex tiếng Việt/Anh**:
  `AGREE` (duyệt|ok|đồng ý|chốt|approve|làm đi|tiến hành), `OBJECT` (spec|plan|quick),
  `APPROVE_FAST`, `PRONOUN` (cái này/cái đó). Không có ngôn ngữ thứ ba nào.
- `hooks/scripts/prompt_context.py:48-51` — **`LETTER` regex `^(chọn )?([ab])$` ĐÃ CÓ**,
  nhưng `looks_like_approval` chỉ dùng nó khi `target == "mode"`. Cổng spec/plan/quick
  KHÔNG nhận chữ cái. Đây chính là khoảng trống user chỉ ra.
- `hooks/scripts/bash_gate.py:58,77` — chặn `approve` khi prompt gần nhất không "rõ là câu
  duyệt"; dùng lại cùng hàm trên, nên sửa một chỗ là cả hai cổng theo.
- `scripts/tdq_state.py:734,837` — dòng `say` bắt in `➤ Duyệt: nhắn "duyệt spec"`.
- Khuôn in ra user nằm ở 5 file luật: `skills/tdq-spec/SKILL.md:54`,
  `skills/tdq-plan/SKILL.md:80`, `skills/tdq-intake/references/quick-lane.md:56,135`,
  `skills/tdq-status/SKILL.md:42`, `skills/tdq-conventions/references/user-facing-block.md:110,128`.
- Luật ngôn ngữ output: mọi skill `tdq-*` mở đầu bằng "Mọi output cho user: **tiếng Việt**".
- 14 file test khoá chuỗi này (test_prompt_context, test_bash_gate, test_state,
  test_user_facing_block, test_e2e_chain, test_compliance_protocol…) → đổi luật là đổi test.
- Vòng research ngoài: **BỎ** — việc thuần nội bộ repo, không có ẩn số ngoài; phiên này
  cũng có luật cấm gọi sub-agent khi user chưa yêu cầu.

## Hỏi đáp

Vòng scope: CHẠY — request chạm cả cổng duyệt, khuôn hỏi, luật ngôn ngữ output; ≥2 mặt
chưa được yêu cầu nói tới.

### Vòng 1 (2026-08-21 23:18)

| # | Câu hỏi | User chọn (nguyên văn) | Hệ quả |
|---|---|---|---|
| 1 | Bao quanh những mặt nào | `1abcd` | Làm cả 4 mặt: cổng duyệt · khuôn khối cuối turn · ngôn ngữ output · rà tài liệu luật |
| 2 | Dừng ở đâu | `2b` | **CHỈ CHECK + báo cáo hiện trạng**, không sửa luật/code trong request này |
| 3 | Giữ cách gõ cũ | `3a` | Thiết kế đề xuất phải giữ song song câu duyệt tiếng Việt cũ |
| 4 | Ai dùng | `4b tương thích với ngôn ngữ chính của chính user, ko fix cứng một ngôn ngữ nào cả` | Cổng không được giả định ngôn ngữ nào; bám ngôn ngữ user đang nhắn |
| 5 | Bổ sung | `5 vẫn tương thích ngược để có thể work và ko hoạt động sai với những request cũ` | Ràng buộc cứng: mọi thay đổi đề xuất phải tương thích ngược, không làm sai request/transcript cũ |

Không còn câu hỏi nào đổi được kết quả → dừng phỏng vấn.

### Chốt lại

- **Đầu ra của request này là MỘT tài liệu rà soát** (`docs/tdq/audit/da-ngon-ngu.md`):
  hiện trạng từng mặt A–D kèm bằng chứng `file:dòng`, phán quyết ĐẠT/CHƯA, và đề xuất
  thiết kế cho request sửa sau. KHÔNG sửa hook, script, skill hay test trong request này.
- Tiêu chí chấm "đã international hoá": (i) cổng nhận được câu trả lời không phụ thuộc
  ngôn ngữ; (ii) không có chuỗi tiếng Việt nào là ĐƯỜNG DUY NHẤT để qua cổng;
  (iii) câu mời duyệt sinh ra theo ngôn ngữ user đang dùng; (iv) đường cũ vẫn chạy.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Research ngoài | BỎ | Thuần nội bộ repo; không có ẩn số ngoài. Phiên này cũng cấm gọi sub-agent khi user chưa yêu cầu |
| Spec | CÓ | Khung bất biến; chốt tiêu chí chấm trước khi chấm |
| Plan | CÓ | Khung bất biến; mỗi mặt A–D là một task có bằng chứng riêng |
| Implement | CÓ (dạng rà soát) | Việc thi hành là đọc code + ghi bằng chứng, không sửa file luật |
| QC bởi agent riêng | BỎ | Không đổi hành vi phần mềm; QC = tự kiểm lại từng bằng chứng `file:dòng` có thật |
| Chạy full test suite | CÓ (1 lần) | Xác nhận request này không đụng gì vào code — suite phải y hệt trước |
| Report | CÓ | Khung bất biến |
