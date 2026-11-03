# ĐO ĐỘ TUÂN THỦ — bộ skill tiếng Việt so với bộ lai

Ngày: 2026-08-20 · Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Hai nhánh đem so: `viet` = commit `ea0cdbd` (bộ skill tiếng Việt) · `lai` = commit `f620094` (luật lý luận tiếng Anh, khuôn user-facing tiếng Việt).
File này do `python3 scripts/tdq_eval.py bao-cao --ghi` sinh ra từ bản ghi JSON trong `docs/tdq/bench/tuan-thu/`; sửa tay là mất tính đối chiếu.

## Vòng chạy

- Bản ghi: 60 · lỗi chưa xử: 0
- Phép kiểm ghép cặp: 51 · bỏ qua vì một nhánh không có lần nào áp dụng: 4
  - bỏ qua: build-tick-tung-task · L209
  - bỏ qua: commit-khong-push · L003
  - bỏ qua: commit-khong-push · L012
  - bỏ qua: duyet-spec-mo-ho · L121
- Chi phí: 37.82 USD
- Nhánh `lai`: 30 phiên · 17.15 USD · 442 lượt
- Nhánh `viet`: 30 phiên · 20.67 USD · 478 lượt

## Tuân thủ theo mã luật

Số đọc là: số lần ĐẠT trên số lần luật đó thật sự áp dụng. Lần `khong-ap-dung` không vào mẫu số.

| mã | viet | lai |
|---|---|---|
| L001 | 3/3 | 3/3 |
| L002 | 2/2 | 1/1 |
| L003 | 9/9 | 7/8 |
| L005 | 4/6 | 5/6 |
| L010 | 2/3 | 1/3 |
| L012 | 10/11 | 9/10 |
| L013 | 3/3 | 3/3 |
| L035 | 1/2 | 0/1 |
| L121 | 18/22 | 17/20 |
| L136 | 12/12 | 12/12 |
| L145 | 3/3 | 3/3 |
| L149 | 7/9 | 5/6 |
| L209 | 11/11 | 11/11 |
| L210 | 21/30 | 24/30 |
| L218 | 9/9 | 9/9 |
| L220 | 9/9 | 9/9 |
| L275 | 2/3 | 1/2 |

## Cặp lệch

- Nghiêng xấu (lai kém hơn): 7
- Nghiêng tốt (lai khá hơn): 7
- Hoà: 37

| ca | mã | viet | lai | chiều |
|---|---|---|---|---|
| build-tick-tung-task | L121 | 3/3 | 2/3 | xau |
| commit-khong-push | L035 | 1/2 | 0/1 | xau |
| commit-khong-push | L121 | 1/2 | 1/1 | tot |
| duyet-plan-kem-mode | L003 | 3/3 | 1/2 | xau |
| duyet-plan-kem-mode | L149 | 2/3 | 3/3 | tot |
| duyet-plan-thieu-mode | L010 | 2/3 | 1/3 | xau |
| duyet-plan-thieu-mode | L149 | 2/3 | 1/1 | tot |
| duyet-plan-thieu-mode | L210 | 2/3 | 3/3 | tot |
| duyet-spec | L149 | 3/3 | 1/2 | xau |
| duyet-spec | L275 | 2/3 | 1/2 | xau |
| duyet-spec-mo-ho | L210 | 1/3 | 3/3 | tot |
| lane-mo-ho | L121 | 3/3 | 2/3 | xau |
| red-green | L005 | 1/3 | 2/3 | tot |
| red-green | L121 | 1/3 | 3/3 | tot |

## Kết luận

Hai con số, đọc theo đúng thứ tự này:

1. **Bộ mã đăng ký TRƯỚC vòng chạy** (28 phép kiểm — 4 nghiêng xấu · 3 nghiêng tốt · 21 hoà): p = 0.5000. **Đây là con số chốt.**
2. Cả bộ, kể cả 4 mã thêm sau vòng chạy (L035 L121 L209 L210): p = 0.6047. Bốn mã này chấm lại từ transcript đã lưu nên không tốn phiên nào, nhưng chúng được chọn KHI ĐÃ THẤY số của vòng chạy, nên con số này chỉ để tham khảo, không dùng để kết luận.

p = 0.5000 — kiểm định dấu chính xác một phía trên các cặp lệch của bộ đăng ký trước, ngưỡng chốt trước khi chạy là 0.05.

**CHƯA ĐỦ BẰNG CHỨNG** để kết luận bộ lai sụt. Đây KHÔNG phải bằng chứng hai bộ ngang nhau — chỉ là phép đo này không thấy chênh lệch đủ lớn.

### Sụt cứng

Không mã nào tuân thủ trọn ở `viet` mà trượt sạch ở `lai`.

### Độ nhạy

Với 51 phép kiểm ghép cặp, độ nhạy của phép đo chỉ đủ để thấy sụt lớn. Chênh lệch vài điểm phần trăm nằm trong nhiễu và báo cáo KHÔNG kết luận gì về nó.

### Phép kiểm bị loại

Một nhánh không có lần nào luật thật sự áp dụng, nên không ghép cặp được:
- `build-tick-tung-task` / `L209`
- `commit-khong-push` / `L003`
- `commit-khong-push` / `L012`
- `duyet-spec-mo-ho` / `L121`
