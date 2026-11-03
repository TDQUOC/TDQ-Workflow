# Câu hỏi — 2026-08-08-giam-over-engineer-workflow

Request: ../requests/2026-08-08-giam-over-engineer-workflow.md · Lane: full

## Vòng 1 — 2026-08-08 21:5x

Đã tự trả lời, KHÔNG hỏi user:

- Phạm vi sửa `doc_lint`: miễn R1–R7 cho toàn bộ `docs/tdq/**` chứ không riêng `spec/`.
  Lý do: đây là output của workflow, chứa trích nguyên văn lời user và output test thật.
  Luật văn phong dành cho doc hướng dẫn không áp được lên thứ cấm sửa.
- Sửa bug `allowed()` với R5: lỗi rõ ràng, không có phương án hai.
- Không đụng lõi (hook injection, `state.json`, gate duyệt, `phases.md` tự sinh).

### Câu hỏi đã trình

1. Ngưỡng "nhẹ" đo bằng số nào?
2. Nửa tuỳ chọn xử lý ra sao?
3. `portable/` giữ hay bỏ?
4. Có gộp file output mỗi request không?
5. Được phép XOÁ test không?

### Trả lời của user

```text
1B: tôi hiện thấy có vẻ đôi khi bước QC test quá nhiều và tự hỏi liệu có cần thiết
không, và cảm giác đôi khi một task rất nhỏ nhưng lại bị làm over ra khiến tốn time
và token khá nhiều; 2. tạm thời xóa hẳn external đi; 3. B; 4.A; 5.A; 6. tôi muốn tối
ưu hơn bộ workflow, và ở mỗi dòng code hoặc mỗi bước thực thi luôn đi theo hướng
minimal, ko viết nếu không thực sự cần, không cần test quá nhiều nếu khả năng xảy ra
issue thấp, QC sẽ là test để đảm bảo output đúng expect yêu cầu chứ không phải spam
cho nhiều. tổng quan tôi muốn tối ưu độ dài, thời gian làm việc của claude khi dùng
tdq workflow, hoặc có thể tham khảo ý tưởng là khi có request sẽ nhận định xem
request này cần dùng gì, và chỉ dùng những thứ cần để giảm thiểu thời gian claude
thực thi, nhưng đảm bảo được tính năng và yêu cầu mà người dùng yêu cầu
```

Chốt lại thành luật:

- Không đặt ngưỡng số cứng. Đo trước/sau và báo cáo, không lấy con số làm cổng PASS.
- Xoá hẳn nhánh external. Các nhánh tuỳ chọn khác giữ code, chuyển sang nạp lười.
- Xoá hẳn `portable/`.
- Gộp `requests` + `knowledge` + `questions` thành một file.
- Được xoá test.
- Nguyên tắc xuyên suốt: minimal. Không viết nếu không thật sự cần.
- QC = kiểm output có đúng yêu cầu không. Không phải chạy cho nhiều hạng mục.
- Mỗi request phải tự nhận định cần dùng gì, rồi chỉ dùng đúng thứ đó.

### Vòng 2 — tự trả lời, có nêu giả định trong spec

- `search_task.py` chạy trên `agy` và `external_models.py`. Xoá external là mất engine
  của deep search. Nên deep search đi theo. Ghi rõ ở spec §1 để user phủ quyết được.
- `claude_export`, `token_audit`, `plugin_tiers`, `skill_inventory`: user không nêu tên.
  Giữ code, chỉ gỡ khỏi đường nạp mặc định. Ghi ở mục NGOÀI phạm vi.
