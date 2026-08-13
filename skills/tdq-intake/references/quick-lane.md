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

## Luật ĐỌC đồ thị ở bước 1 (phân tích)

Hỏi về **liên kết** hay **bản đồ tổng thể** ("ai gọi X", "sửa X ảnh hưởng đâu") → mở đồ thị
bằng `graphify query|path|explain|affected`. Tìm chuỗi hoặc đọc file cụ thể → grep/read.
Đồ thị chỉ có `scripts/` và `hooks/`; test và tài liệu bị `.graphifyignore` loại.

## Khuôn mini-spec/plan (≤ 40 dòng)

```markdown
# QUICK — <tên việc>

Ngày: YYYY-MM-DD · Brief: ../brief/<slug>.md · Lane: quick
Trạng thái: CHỜ DUYỆT
Ước tính sẽ dùng skill: <skill sẽ DÙNG, hoặc "không có">

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

Sẽ làm: <gạch đầu dòng ngắn>.
Đụng tới: <file/khu vực>.
Kiểm thế nào: <lệnh hoặc tiêu chí>.
Ước tính sẽ dùng skill: <skill sẽ DÙNG, hoặc "không có">.

Xem đầy đủ tại: docs/tdq/plan/<slug>.md

---

**Bạn duyệt để tôi làm luôn chứ?**

➤ Duyệt: nhắn "duyệt nhanh" (bỏ QC: "duyệt nhanh không QC"; "duyệt quick" vẫn chạy — duyệt xong tôi làm ngay) · Góp ý: nhắn trực tiếp
```

## Luật tick — `[ ]` · `[~]` · `[x]`

Checkbox có ba trạng thái: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong. Lúc implement:

1. Đánh `[~]` cho task sắp làm **TRƯỚC** khi sửa dòng mã đầu tiên.
2. Viết test (đỏ) → code → test xanh.
3. Đổi `[~]` → `[x]` **NGAY**, không đợi task sau.

Chỉ một task mang `[~]` tại một thời điểm. **Cấm gom tick vào cuối turn** — chế độ nhanh (express)
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
BỎ theo yêu cầu user: "<nguyên văn câu user>"
```

## Vòng fix

- Chạy khi QC FAIL, hoặc khi thấy bug/test đỏ.
- Task fix ghi vào plan dưới heading `## QC vòng N — fix`, khuôn
  `- [ ] **QCn.1** <việc> — Test: <check>`. Làm red→green: `[~]` khi bắt đầu,
  đổi `[x]` ngay khi xanh.
- Fix xong chạy lại hạng mục đã FAIL cộng hạng mục mà bản fix có thể làm hỏng.
- **Trần 3 vòng.** Vượt trần → DỪNG, báo user, đề xuất chuyển chế độ chuyên sâu (deep). Giữ
  `phase=implement`, KHÔNG chạy `set phase=idle`.
