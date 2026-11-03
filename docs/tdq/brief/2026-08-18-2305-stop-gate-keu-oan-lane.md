# BRIEF — stop_gate kêu oan vì không xét lane

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> A

(Chọn phương án A của khối hỏi cuối request `2026-08-18-2205-spec-khong-ghi-lenh-kiem`:
"commit phần đã xong, rồi mở request nhỏ vá `stop_gate` lọc theo lane".)

### Cách hiểu đầu tiên

Mục tiêu: `stop_gate` khi nhắc `[TDQ:APPROVE]` phải nêu ĐÚNG cổng của lane đang chạy.

Hiện trạng đo được — `hooks/scripts/stop_gate.py:184`:

```python
target = next((t for t in ("spec", "plan", "quick") if not state.get(f"{t}_approved")), None)
```

Danh sách cổng cố định, không xét `lane`. Lane `quick` không có cổng `spec`/`plan` nên hai
trường đó vĩnh viễn `false`, và dòng nhắc luôn trỏ vào `spec` — kể cả khi `quick_approved`
đã `true` và request đã đóng. Đo thật: cuối request 2205 (lane quick, đã duyệt, phase idle)
vẫn ra "[TDQ:APPROVE] spec vẫn chưa được ghi nhận duyệt".

Đây đúng loại lỗi mà request 2205 vừa xử: cổng kêu vì lý do vô hại thì lúc nó kêu thật
cũng không còn ai nghe (`docs/tdq/reports/2026-08-18-2050-spec-doi-sau-khi-duyet.md`).

Phạm vi đoán: sửa đúng bước chọn `target` cho khớp lane, cộng test khoá hình dạng. Không
đụng phần chặn `TDQ:TICK` hay các mã nhắc khác của `stop_gate`.

### Chỗ chưa rõ

1. Lane `full` khi cả spec lẫn plan chưa duyệt: nêu cổng gần nhất (`spec`) hay nêu cả hai?
2. `lane` trong state rỗng/lạ (request cũ, state hỏng): im lặng hay giữ nguyên cách cũ?

## Hiểu & kiến thức

## Hỏi đáp
