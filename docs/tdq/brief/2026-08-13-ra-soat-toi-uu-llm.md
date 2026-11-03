# BRIEF — Rà soát mức tối ưu cho LLM của tdq-workflow

Ngày: 2026-08-13

## Nguyên văn

> okay tôi muốn bạn scan toàn bộ tdq-workflow để xem đã LLM optimize chưa để giữ full
> behavior và full rule nhưng optimize để save performance và context cost, hãy mở
> request để resreach và báo cáo cho tôi

### Cách hiểu đầu tiên

**Mục tiêu.** Rà soát toàn bộ plugin `tdq-workflow` dưới góc nhìn "viết cho LLM đọc":
chỗ nào tốn context vô ích, chỗ nào lặp, chỗ nào diễn đạt mơ hồ khiến model phải đoán,
chỗ nào bắt model đọc nhiều file mới ra được một luật. Ra một **báo cáo** xếp hạng cơ hội
tối ưu kèm mức tiết kiệm ước tính và rủi ro.

**Ràng buộc cứng do user nêu.** Giữ **nguyên vẹn hành vi** và **nguyên vẹn mọi luật** —
tối ưu chỉ được đụng cách diễn đạt, cách chia file, thời điểm nạp, không được bỏ luật nào.

**Phạm vi đoán (chờ chốt).** Bề mặt gồm: 6 `SKILL.md` + 20 file `references/` (1640 dòng),
19 script Python ở `hooks/scripts/` và `scripts/` (5336 dòng), 3 agent, `portable/workflow/`,
`docs/claude-md-mau.md`, `.claude-plugin/plugin.json`. Trọng tâm là phần **vào context**
(description skill, SKILL.md, output của hook, lời chặn) hơn là mã Python chạy ngoài context.

**Đầu ra đoán.** Chỉ báo cáo (research), CHƯA sửa code — user nói "research và báo cáo".
Việc sửa theo khuyến nghị sẽ là request sau, trừ khi user nói khác.

**Chỗ chưa rõ.**
- Có được đo bằng cách đếm token thật (tokenizer) không, hay ước lượng theo ký tự là đủ?
- Báo cáo dừng ở mức khuyến nghị, hay kèm luôn patch mẫu cho 1–2 chỗ nặng nhất?
- Có tính cả chi phí runtime của hook (thời gian chạy Python mỗi lượt prompt) không, hay
  chỉ chi phí context?

## Hiểu & kiến thức

### Năng lực dùng được

| Năng lực | Phán quyết | Vì sao |
|---|---|---|
| `tavily-primary` | DÙNG | Cần đối chiếu hướng dẫn ngoài về cách viết skill/prompt cho LLM |
| `graphify` | DÙNG | `graphify-out/` có sẵn, hỏi quan hệ file nhanh hơn grep tay |
| `mem0-memory` | DÙNG | Kết luận kiến trúc nên tra trước và ghi lại sau |
| `tdq-reviewer` | BỎ | Đầu ra là báo cáo, không phải spec/plan cần review sâu |
| Skill Unity/Figma/Adobe… | BỎ | Không dính lĩnh vực |

### Đã đo được ở phase này

Bề mặt tài liệu: 6 `SKILL.md` = 34.332 ký tự · 20 file `references/` = 61.512 ký tự ·
3 agent = 5.558 ký tự · 6 hook script = 41.538 ký tự.

`scripts/token_audit.py --sessions 2` (2 session gần nhất, 1.427 API call):
carry-cost tổng 696M token. Xếp hạng nhóm tốn nhất mà workflow kiểm soát được:
`Read file` 178M/179 lần · `Bash khác` 33,8M/287 lần · `tdq_state.py` 9,0M/162 lần ·
`Edit` 7,3M/363 lần · `graphify` 4,3M/15 lần · `chạy test suite` 2,8M/64 lần.
Nhóm đắt nhất (446M) là ảnh chụp canvas Excalidraw — nằm ngoài workflow này.

Đã có sẵn kỷ luật context: `references/context-budget.md` (5 luật), `token_audit.py`,
`tests/test_token_budget.py` (trần cứng cho 4 hook: SessionStart 600 ký tự,
UserPromptSubmit 240, PreToolUse 200, Stop 300) và trần tổng description skill 900 ký tự.
Nghĩa là phần "hook bơm vào context" đã bị siết; cơ hội còn lại nằm ở chỗ khác.

### Giả thuyết cần kiểm ở phase sau

1. `tdq-conventions/SKILL.md` (7.527 ký tự) bị nạp lại ở MỌI skill `tdq-*` — trùng lặp
   theo cấp số nhân khi một turn chạm nhiều skill.
2. Nội dung trùng giữa `skills/` và `portable/workflow/` — chi phí bảo trì, và tốn context
   khi tìm kiếm quét trúng cả hai bản.
3. Một luật bị chép ở nhiều file (vd luật tick, luật mode, khuôn duyệt) thay vì một nguồn.
4. Văn tiếng Việt có dấu tốn token gấp ~2 lần tiếng Anh cùng nghĩa — cần cân nhắc chỗ nào
   là văn cho user (giữ tiếng Việt) và chỗ nào là chỉ dẫn cho máy.
5. Thứ tự nạp: chỗ nào nên là "đọc khi cần" thay vì nằm sẵn trong `SKILL.md`.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Research ngoài (tavily) | CÓ | Cần đối chiếu hướng dẫn chính thức về progressive disclosure |
| Đo bằng `token_audit.py` | CÓ | Đã có công cụ, cho số thật thay vì cảm tính |
| Spec + plan | CÓ | Khung bất biến |
| Implement | Chờ user chốt | Câu hỏi 1 ở mục Hỏi đáp |
| QC độc lập bằng agent | BỎ | Đầu ra là báo cáo, DoD tự kiểm bằng lệnh đủ |
| Chia subagent | BỎ | Việc đọc tài liệu tập trung, chia ra tốn context hơn |

## Hỏi đáp

### Vòng 1 — đã chốt (user trả lời "1A 2A 3A")

1. Sau báo cáo làm gì? → **A: chỉ báo cáo**, không sửa code trong request này. Việc sửa
   theo khuyến nghị là request sau.
2. Mức chi tiết? → **A: kèm bản vá mẫu cho 2–3 chỗ nặng nhất**, để thấy trước hình hài
   bản sửa. Bản vá nằm TRONG báo cáo dưới dạng khối trích, không áp vào file thật.
3. Có đo tốc độ hook? → **A: có**, đo thời gian chạy từng hook vì nó cộng vào độ trễ
   mỗi lượt gõ.

Không còn câu hỏi nào làm đổi kết quả. Nghiên cứu ngoài đã xong, ghi ở
`docs/tdq/research/2026-08-13-ra-soat-toi-uu-llm.md`.

