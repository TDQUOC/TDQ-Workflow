# Soul — luật gốc của TDQ Workflow

Soul là luật đứng trên mọi luật khác của bộ workflow. Luật nào mâu thuẫn với soul —
dù cũ hay mới — thì sửa luật đó, không sửa soul. Muốn đổi soul phải có user duyệt.

## Bốn nguyên tắc

### 1. Mục đích của harness

Harness tồn tại để giúp dev dùng AI làm ra kết quả tốt hơn và hoàn thiện hơn.
Chất lượng hơn số lượng: một sản phẩm chạy đúng, đọc được, giữ được lâu, đáng giá hơn
nhiều sản phẩm dở dang.

### 2. Thứ tự ưu tiên: chất lượng > runtime > context cost

- **Tầng 1 — chất lượng**: code agent làm ra phải đạt MVP thật — chạy đúng, có test,
  không nợ kỹ thuật thấy trước mà không khai.
- **Tầng 2 — runtime**: thời gian chạy của workflow và của sản phẩm. Chỉ tối ưu khi
  không hạ tầng 1.
- **Tầng 3 — context cost**: token nạp vào model. Chỉ cắt khi không hạ hai tầng trên.

**Luật phân xử** khi hai luật đá nhau:
1. Luật phục vụ tầng cao hơn thắng.
2. Hai luật cùng tầng → chọn luật có phép kiểm chạy được bằng lệnh.
3. Vẫn hoà → hỏi user, ghi phán quyết vào tài liệu request đang mở.

### 3. Viết cho model yếu nhất

Mọi rule và behavior phải đủ chi tiết để model thấp như Haiku đọc là làm đúng,
không riêng model cao như Opus. Một rule đạt chuẩn khi có đủ ba mục:
`## Khi nào áp dụng` (dấu hiệu nhận ra được bằng mắt hoặc bằng lệnh),
`## Làm gì` (các bước đánh số, mỗi bước một hành động, câu mệnh lệnh),
`## Tự kiểm` (một lệnh hoặc một câu hỏi có/không). Chỗ dễ hiểu nhầm phải kèm
ví dụ ĐÚNG/SAI.

### 4. Phạm vi áp dụng

Soul áp cho mọi skill, mọi script, mọi khuôn, và mọi tài liệu của từng request:
brief, spec, plan, qc, report — kể cả tài liệu của chính request tạo ra soul này.
Áp hồi tố cho luật đã có và áp cho mọi bổ sung về sau. Mỗi tài liệu request mở đầu
bằng dòng:

```
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
```

## Khi nào áp dụng

Dấu hiệu — gặp một trong các tình huống sau là soul có mặt:

- Sắp viết mới hoặc sửa một luật, một skill, một khuôn tài liệu, một script của workflow.
- Hai luật chỉ về hai hướng khác nhau trong cùng một việc.
- Sắp cắt bớt một bước (test, QC, log, research) để chạy nhanh hơn hoặc tiết kiệm token.
- Sắp mở một tài liệu request mới (brief, spec, plan, qc, report).

## Làm gì

1. Xếp việc đang làm vào đúng tầng: chất lượng, runtime, hay context cost.
2. Đối chiếu: thay đổi này có hạ tầng nào cao hơn không? Có → dừng, làm theo tầng cao.
3. Viết rule mới theo khuôn ba mục ở nguyên tắc 3; chỗ dễ hiểu nhầm thêm ví dụ ĐÚNG/SAI.
4. Mở tài liệu request mới → đặt dòng `Soul:` ở đầu file, ngay dưới tiêu đề.
5. Hai luật đá nhau → chạy luật phân xử ở nguyên tắc 2, ghi phán quyết lại.

Ví dụ ĐÚNG: bỏ một vòng research trùng lặp vì kết quả đã có trong brief — tiết kiệm
token mà không mất thông tin (tầng 3 phục vụ tầng 1).
Ví dụ SAI: bỏ bước viết test trước để build nhanh hơn — lấy runtime đè chất lượng.

## Tự kiểm

- Câu hỏi có/không: "Thay đổi tôi sắp làm có hạ chất lượng để đổi lấy tốc độ hoặc
  token không?" — Có → không làm.
- Câu hỏi có/không: "Rule tôi vừa viết, đưa cho Haiku không kèm giải thích miệng,
  nó làm đúng được không?" — Không → viết lại theo khuôn ba mục.
- Lệnh: `python3 -m pytest tests/test_soul_rules.py -q` phải xanh.
