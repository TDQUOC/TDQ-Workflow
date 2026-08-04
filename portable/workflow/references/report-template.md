# Khuôn report

`docs/tdq/reports/<slug>.md` — tiếng Việt, **≤ 10 dòng tổng cộng** kể cả dòng trống.
Kiểm bằng `wc -l docs/tdq/reports/<slug>.md`. Ngắn nhưng không được mất sự thật: dồn
mỗi mục thành MỘT dòng, ngăn ý bằng dấu `·`, số liệu lấy nguyên từ output thật.

```markdown
# REPORT — <tên việc> (`<slug>` · lane <lane> · mode <mode> · <n> task tick đủ)

Đã làm: <P1 …> · <P2 …> · <P3 …>
Kết quả: <chỉ số> <trước> → <sau> · <chỉ số> <trước> → <sau>
Kiểm: <lệnh test + kết quả> · <lint> · QC <PASS x/y mục DoD, defect đã sửa>
Đầu ra: <đường dẫn file chính> · Backup: <đường dẫn, nếu có sửa ngoài repo>
Giới hạn: <cái gì chưa làm, vì sao, ảnh hưởng gì>
Git: <chưa commit / commit nào đã tạo>
```

## Kiểm trước khi trình

- ≤ 10 dòng (đo bằng `wc -l`); quá thì gộp dòng, cấm bỏ mục.
- Mọi con số lấy từ output thật, không ước lượng. Phép đo có điều kiện méo thì nói rõ trong dòng "Kết quả".
- Dòng "Giới hạn" không được bỏ trống khi còn việc dang dở — nói thật, không giấu.
- Kết thúc bằng câu hỏi user có muốn commit không (hỏi trong chat, không viết trong file).
