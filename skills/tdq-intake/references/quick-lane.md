# Lane quick — chi tiết

Quick khác full ở chỗ **gộp tài liệu và gộp gate**, không phải ở chỗ bỏ suy nghĩ:
phân tích, web search khi có ẩn số ngoài, và interview khi còn câu hỏi làm đổi kết quả
đều GIỮ. Chỉ bỏ khi việc thuần nội bộ hoặc đã rõ hết — và phải nói rõ vì sao bỏ.

| Bước | Full | Quick |
|---|---|---|
| Phân tích + đọc code | có | có |
| Web search | có (2–4 truy vấn) | có khi có ẩn số bên ngoài |
| Interview | lặp đến hết mơ hồ | khi còn câu làm đổi kết quả |
| Tài liệu | brief + spec + plan | **1 file** `docs/tdq/plan/<slug>.md` |
| Gate duyệt | 2 (spec, plan) | **1** ("duyệt quick") |
| QC | file `qc/<slug>.md` | mỗi dòng DoD một phép kiểm, ghi vào mục ## QC của plan (mặc định BẬT) |
| Vòng fix khi FAIL | trần 3 vòng, ghi file qc/ | trần 3 vòng, ghi trong plan |

## Khuôn mini-spec/plan (≤ 40 dòng)

```markdown
# QUICK — <tên việc>

Ngày: YYYY-MM-DD · Brief: ../brief/<slug>.md · Lane: quick
Trạng thái: CHỜ DUYỆT
Năng lực: <skill sẽ DÙNG, hoặc "không có">

## Phạm vi
- Trong: <gạch đầu dòng>
- NGOÀI: <gạch đầu dòng>

## Task
- [ ] **T1** <việc cụ thể> — Test: <lệnh hoặc tiêu chí pass>
- [ ] **T2** <việc cụ thể> — Test: <lệnh>

## Definition of Done
- <điều kiện đo được, có lệnh kiểm>
```

Quá 40 dòng nghĩa là việc này không còn "quick" — nói với user và đề xuất chuyển full.

## Luật tick — `[ ]` · `[~]` · `[x]`

Checkbox có ba trạng thái: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong. Lúc implement:

1. Đánh `[~]` cho task sắp làm **TRƯỚC** khi sửa dòng mã đầu tiên.
2. Viết test (đỏ) → code → test xanh.
3. Đổi `[~]` → `[x]` **NGAY**, không đợi task sau.

Chỉ một task mang `[~]` tại một thời điểm. **Cấm gom tick vào cuối turn** — lane quick
làm trọn gói trong một turn, gom tick nghĩa là plan không phản ánh gì trong suốt lúc làm.

Hàng rào: `hooks/scripts/edit_gate.py` **CHẶN** (deny) mọi lần sửa file ngoài `docs/` và
`tests/` khi phase là `implement`/`qc` mà plan không có task nào mang `[~]`. Miễn trừ
`tests/**` để còn viết được test đỏ trước. Bị chặn mà request thật ra đã đóng → chạy
`python3 scripts/tdq_state.py set phase=idle`.


## QC ở quick

Mặc định **BẬT**. Làm ngay sau khi implement xong, **số hạng mục bằng số dòng DoD**
của mini-plan: mỗi dòng DoD đúng một phép kiểm chạy bằng lệnh, dán output thật.
Cộng thêm một hạng mục cố định: chạy đúng lệnh `Test:` của từng task trong plan.

Không thêm hạng mục ngoài DoD. Biên, đường lỗi, log, placeholder chỉ kiểm khi có dòng
DoD nói tới. Quick khác full ở chỗ không chạy full-suite toàn repo, chỉ chạy test của
từng task.

Bằng chứng append vào CHÍNH file plan, không tạo file `qc/`:

```markdown
## QC
- Q1 test từng task: PASS — `<lệnh>` → `<output thật>`
- Q2 DoD "<nguyên văn dòng DoD 1>": PASS — `<lệnh>` → `<output thật>`
- Q3 DoD "<nguyên văn dòng DoD 2>": PASS — `<lệnh>` → `<output thật>`
```

Opt-out CHỈ khi user nói rõ, ví dụ `"duyệt quick không QC"` → chạy approve kèm `--no-qc`.
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
- **Trần 3 vòng.** Vượt trần → DỪNG, báo user, đề xuất chuyển lane full. Giữ
  `phase=implement`, KHÔNG chạy `set phase=idle`.
