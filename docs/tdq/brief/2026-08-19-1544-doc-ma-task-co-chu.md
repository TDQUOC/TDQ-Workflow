# Brief — bộ đọc plan bỏ sót mã task có chữ sau số (T2A.1, T2.4b)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

User chọn phương án A ở turn trước: commit phần vừa xong, rồi mở request quick sửa
`_TASK` nhận mã dạng `T2A.1`.

### Cách hiểu đầu tiên

Mục tiêu: mọi nơi đọc mã task trong plan phải nhận mã có chữ xen giữa hoặc đứng sau
số. Hai regex đang hẹp; sửa cả hai cùng một luật, kèm test khoá.

### Bằng chứng

Quét toàn bộ `docs/tdq/plan/*.md` bằng chính regex đang chạy: thấy 1248 task. Regex
nới rộng thấy 1254. Sáu task bị bỏ sót:

```
2026-08-19-0121-huong-c-nap-reference.md: T2A.1 T2A.2 T2A.3 T2B.1 T2B.2
2026-08-15-toi-uu-thoi-gian-phase.md:     T2.4b
```

File `huong-c` khai 14 task, `tdq_team.doc_plan` chỉ đọc ra 9.

### Gốc lỗi

Ba chỗ, cùng một giả định "mã task = chữ rồi tới số, không lẫn":

- `scripts/tdq_state.py:533` `_TASK_LINE` — `\*\*([A-Za-z]+[0-9.]*)\*\*`.
- `scripts/tdq_team.py:33` `_TASK` — cùng lớp ký tự đó.
- `scripts/tdq_team.py:37` `_TASK_REF` — `\bT\d+\.\d+\b`, dùng để đọc `Cần:`.

`[A-Za-z]+` không ăn được chữ đứng sau số, nên `T2A.1` trượt hoàn toàn.

### Ảnh hưởng

`_TASK_LINE` nuôi `plan_tick_state`: tổng số task, `has_doing`, `all_done`. Task vô
hình kéo theo hai chiều hỏng ngược nhau. Một: plan còn task chưa xong mà `all_done`
vẫn bật, cổng chống ngừng cho kết thúc turn sớm. Hai: đánh `[~]` cho đúng task đó thì
`has_doing` vẫn tắt, `edit_gate` chặn sửa file dù đã tick đúng luật.

`_TASK_REF` bỏ sót thì `Cần: T2A.1` thành phụ thuộc rỗng, `tdq_bench.py mo-phong` và
lịch chạy song song đọc sai đồ thị.

### Chỗ chưa rõ

- Có nên siết ngược lại: bắt mã task đúng khuôn `T<số>.<số>` và cho lint báo lỗi khi
  plan dùng mã lạ, thay vì nới regex.

## Hiểu & kiến thức

## Hỏi đáp
