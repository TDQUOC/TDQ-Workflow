# Chế độ nhanh (express) — chi tiết

Chế độ nhanh khác chế độ chuyên sâu ở chỗ **gộp tài liệu và gộp gate**, không phải ở
chỗ bỏ suy nghĩ. Phân tích, web search khi có ẩn số ngoài, và interview khi còn câu hỏi
làm đổi kết quả đều GIỮ. Chỉ bỏ khi việc thuần nội bộ hoặc đã rõ hết — và phải nói rõ
vì sao bỏ.

| Bước | Full | Quick |
|---|---|---|
| Phân tích + đọc code | có | có |
| Web search | có (2–4 truy vấn) | có khi có ẩn số bên ngoài |
| Vòng scope | có điều kiện, theo dấu hiệu kích hoạt | y hệt — cùng một bộ dấu hiệu |
| Interview | lặp đến hết mơ hồ | khi còn câu làm đổi kết quả |
| Tài liệu | brief + spec + plan | **1 file** `docs/tdq/plan/<slug>.md` |
| Gate duyệt | 2 (spec, plan) + 1 câu chọn cách chạy | **1** ("duyệt nhanh") |
| QC | file `qc/<slug>.md` | mỗi dòng DoD một phép kiểm, ghi vào mục ## QC của plan (mặc định BẬT) |
| Vòng fix khi FAIL | trần 3 vòng, ghi file qc/ | trần 3 vòng, ghi trong plan |

Vòng scope ở chế độ nhanh dùng chung luật [scope-round.md](scope-round.md): thoả một dấu
hiệu kích hoạt thì hỏi mặt + bối cảnh trước, không thoả thì ghi một dòng lý do BỎ vào
mini-plan mục `## Phạm vi` rồi đi tiếp.

## Mục lục

- Chín bước thi hành
- Luật ĐỌC đồ thị ở bước 1 (phân tích)
- Khuôn mini-spec/plan (≤ 40 dòng)
- Phạm vi
- Task
- Definition of Done
- Khối trình mini-plan cho user
- Luật tick — `[ ]` · `[~]` · `[x]`
- QC ở chế độ nhanh (express)
- QC
- QC
- Vòng fix

## Chín bước thi hành

Đây là toàn bộ Phần C của [SKILL.md](../SKILL.md) — chuyển về đây để thân skill không phải
nạp nhánh này mỗi lần gọi. Vào chế độ nhanh là **bắt buộc** đọc hết chín bước dưới đây
trước khi làm bước 1; cấm làm theo trí nhớ.

1. **Phân tích.** Đọc đúng phần code liên quan. Có ẩn số bên ngoài (thư viện, API,
   phiên bản) → web search qua `tavily-primary` TRƯỚC khi viết gì; thuần nội bộ thì bỏ
   qua và nói rõ vì sao. Còn câu hỏi làm ĐỔI kết quả → interview theo
   [interview.md](interview.md), và **vòng scope** đứng trước vòng
   chi tiết y như lane deep ([scope-round.md](scope-round.md)).
2. **Viết mini-spec/plan GỘP 1 file** `docs/tdq/plan/<slug>.md`, ≤ 40 dòng: phạm vi
   in/out, task checkbox mỗi task một test, DoD mỗi dòng kiểm được bằng lệnh.
   **Mọi task sửa file mã nguồn phải có dòng `Chạm:`** liệt kê đường dẫn trong backtick —
   ngắn không có nghĩa là không cần bản đồ vùng file. Checkbox có 4 trạng thái: `[ ]` chưa làm · `[~]` đang làm · `[>]` đã giao agent con · `[x]` xong. Lúc implement
   (bước 7) đánh `[~]` khi bắt đầu task và đổi sang `[x]` ngay khi test xanh.
3. **Trình tóm tắt ≤ 10 dòng** trong chat: sẽ làm gì, đụng file nào, validate thế nào,
   và đúng 1 dòng `Ước tính sẽ dùng skill: <các skill sẽ DÙNG, hoặc "không có">` (phân
   vân → DÙNG).
4. In đúng dòng: `➤ Duyệt: nhắn "duyệt nhanh" (bỏ QC: "duyệt nhanh không QC"; "duyệt quick" vẫn chạy — duyệt xong implement ngay) · Góp ý: nhắn trực tiếp` rồi **DỪNG**.
5. User duyệt → chạy `python3 "${CLAUDE_PROJECT_DIR}/.claude/tdq/scripts/tdq_state.py" approve quick [--no-qc] --by "<nguyên văn>"` (`--no-qc` CHỈ khi user nói rõ bỏ QC — im lặng về QC thì QC vẫn BẬT).
6. Append summary mini-plan vào `docs/workinglog/<hôm nay>.md` **TRƯỚC** khi sửa code.
7. Implement end-to-end trong 1 turn. **Trước khi gõ dòng code đầu tiên, đếm số task
   có `Chạm:` rời nhau** (không task nào trùng đường dẫn với task khác):
   - từ **3 trở lên** → giao cho agent con `tdq-implementer`, mỗi task một agent, phát
     cùng một response để chúng chạy song song; trần **4 nhánh** một lượt — cùng trần
     mà lệnh `python3 scripts/tdq_team.py cum` áp ở chế độ chuyên sâu (task thứ 5 in
     `CHỜ SLOT`). Chỉ dựng worktree cho agent THẬT SỰ ghi file; agent chỉ đọc thì
     không. Đánh `[>]` khi giao, nhận báo cáo là đổi `[x]` ngay.
   - **dưới 3** → chạy inline như cũ; dựng agent cho 1–2 task rời nhau thì phí brief
     nhiều hơn phần tiết kiệm.
   Mỗi task: đánh `[~]` TRƯỚC khi sửa code (hook
   `edit_gate` CHẶN nếu plan không có `[~]`; `tests/**` được miễn trừ), red→green, đổi
   `[x]` NGAY khi test xanh — cấm gom tick cuối turn. Rồi chạy **QC** (mặc định BẬT): mỗi dòng DoD một
   phép kiểm, ghi bằng chứng vào mục `## QC` của plan. `quick_qc_skipped = true` → mục
   `## QC` chỉ có 1 dòng `BỎ theo yêu cầu user: "<nguyên văn>"`.
   (Bản đầy đủ của luật tick ở mục `## Luật tick` và của QC ở mục `## QC ở chế độ nhanh
   (express)` cùng file này.)
8. **Vòng fix khi QC FAIL hoặc thấy bug**: thêm task vào plan dưới
   `## QC vòng N — fix`, fix red→green, chạy lại hạng mục đã FAIL cộng hạng mục mà bản
   fix có thể làm hỏng. Có trần 3 vòng — vượt trần thì DỪNG, báo user, đề xuất chuyển lane
   full, giữ nguyên phase. (Bản đầy đủ ở mục `## Vòng fix` cùng file này.)
9. Append kết quả vào working log; hỏi user có commit không.

Xong khi: `quick_approved = true`, log đã ghi, mục `## QC` đã có, không còn test đỏ.
Bước kế tiếp: hỏi user về commit; hết request thì `... set phase=idle`.

## Luật ĐỌC đồ thị ở bước 1 (phân tích)

Hỏi về **liên kết** hay **bản đồ tổng thể** ("ai gọi X", "sửa X ảnh hưởng đâu") → mở đồ thị
bằng `graphify query|path|explain|affected`. Tìm chuỗi hoặc đọc file cụ thể → grep/read.
Đồ thị chỉ có `scripts/` và `hooks/`; test và tài liệu bị `.graphifyignore` loại.

## Khuôn mini-spec/plan (≤ 40 dòng)

```markdown
# QUICK — <tên việc>

**Ngày:** YYYY-MM-DD · Brief: ../brief/<slug>.md · Lane: quick
**Trạng thái:** CHỜ DUYỆT
**Ước tính sẽ dùng skill:** <skill sẽ DÙNG, hoặc "không có">

## Phạm vi
- Trong: <gạch đầu dòng>
- NGOÀI: <gạch đầu dòng>

## Task
- [ ] **T1** <việc cụ thể> — Test: <lệnh hoặc tiêu chí pass>
- [ ] **T2** <việc cụ thể> — Test: <lệnh>

## Definition of Done
- <điều kiện đo được, có lệnh kiểm>
```

Quá 40 dòng nghĩa là việc này không còn nhanh — nói với user và đề xuất chuyển chế độ chuyên sâu (deep).

## Khối trình mini-plan cho user

Theo [user-facing-block.md](../../tdq-conventions/references/user-facing-block.md) — đủ
5 thành phần, khối duyệt nằm cuối tin nhắn, không emoji:

```
Tôi đã lên kế hoạch gọn cho yêu cầu của bạn.

**Sẽ làm:** <gạch đầu dòng ngắn>.
**Đụng tới:** <file/khu vực>.
**Kiểm thế nào:** <lệnh hoặc tiêu chí>.
**Ước tính sẽ dùng skill:** <skill sẽ DÙNG, hoặc "không có">.

Xem đầy đủ tại: `docs/tdq/plan/<slug>.md`

---

**Bạn duyệt để tôi làm luôn chứ?**

➤ Duyệt: nhắn "duyệt nhanh" (bỏ QC: "duyệt nhanh không QC"; "duyệt quick" vẫn chạy — duyệt xong tôi làm ngay) · Góp ý: nhắn trực tiếp
```

## Luật tick — `[ ]` · `[~]` · `[x]`

(nhắc lại có chủ ý — bản gốc ở mục `## Luật cứng` của `skills/tdq-build/SKILL.md`.)

Checkbox có bốn trạng thái: `[ ]` chưa làm · `[~]` đang làm · `[>]` đã giao agent con ·
`[x]` xong. Lúc implement:

1. Đánh `[~]` cho task sắp làm **TRƯỚC** khi sửa dòng mã đầu tiên. Giao cho agent con
   thì đánh `[>]` thay vì `[~]` — nhìn plan là biết ai đang cầm task.
2. Viết test (đỏ) → code → test xanh.
3. Đổi `[~]`/`[>]` → `[x]` **NGAY**, không đợi task sau.

Chỉ một task mang `[~]` tại một thời điểm; `[>]` thì được nhiều, tối đa bằng trần 4 nhánh. **Cấm gom tick vào cuối turn** — chế độ nhanh (express)
làm trọn gói trong một turn, gom tick nghĩa là plan không phản ánh gì trong suốt lúc làm.

Hàng rào: `hooks/scripts/edit_gate.py` **CHẶN** (deny) mọi lần sửa file ngoài `docs/` và
`tests/` khi phase là `implement`/`qc` mà plan không có task nào mang `[~]`. Miễn trừ
`tests/**` để còn viết được test đỏ trước. Bị chặn mà request thật ra đã đóng → chạy
`python3 scripts/tdq_state.py set phase=idle`.


## QC ở chế độ nhanh (express)

Mặc định **BẬT**. Làm ngay sau khi implement xong, **số hạng mục bằng số dòng DoD**
của mini-plan: mỗi dòng DoD đúng một phép kiểm chạy bằng lệnh, dán output thật.
Cộng thêm một hạng mục cố định: chạy đúng lệnh `Test:` của từng task trong plan.

Không thêm hạng mục ngoài DoD. Biên, đường lỗi, log, placeholder chỉ kiểm khi có dòng
DoD nói tới. Chế độ nhanh khác chế độ chuyên sâu ở chỗ không chạy full-suite toàn repo,
chỉ chạy test của từng task.

Bằng chứng append vào CHÍNH file plan, không tạo file `qc/`:

```markdown
## QC
- Q1 test từng task: PASS — `<lệnh>` → `<output thật>`
- Q2 DoD "<nguyên văn dòng DoD 1>": PASS — `<lệnh>` → `<output thật>`
- Q3 DoD "<nguyên văn dòng DoD 2>": PASS — `<lệnh>` → `<output thật>`
```

Opt-out CHỈ khi user nói rõ, ví dụ `"duyệt nhanh không QC"` → chạy approve kèm `--no-qc`.
User im lặng về QC = CÓ QC. Khi đó mục `## QC` vẫn phải có, đúng 1 dòng:

```markdown
## QC
**BỎ theo yêu cầu user:** "<nguyên văn câu user>"
```

## Vòng fix

- Chạy khi QC FAIL, hoặc khi thấy bug/test đỏ.
- Task fix ghi vào plan dưới heading `## QC vòng N — fix`, khuôn
  `- [ ] **QCn.1** <việc> — Test: <check>`. Làm red→green: `[~]` khi bắt đầu,
  đổi `[x]` ngay khi xanh.
- Fix xong chạy lại hạng mục đã FAIL cộng hạng mục mà bản fix có thể làm hỏng.
- **Trần 3 vòng.** Vượt trần → DỪNG, báo user, đề xuất chuyển chế độ chuyên sâu (deep). Giữ
  `phase=implement`, KHÔNG chạy `set phase=idle`.
