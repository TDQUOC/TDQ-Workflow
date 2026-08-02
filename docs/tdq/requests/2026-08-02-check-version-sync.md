# REQUEST — Check bump version + đồng bộ plugin repo ↔ user-level

Ngày: 2026-08-02 · Slug: 2026-08-02-check-version-sync

## Nguyên văn yêu cầu
"okay hãy check xem đã pump version và dồng bộ giữ plugin trong repo và userlevel claude chưa?"

## Cách hiểu đầu tiên
- Check: (1) version trong plugin.json của repo đã bump sau các thay đổi hôm nay chưa
  (3 request: intake-default, fix-hint, auto-pick — hiện chắc vẫn 0.6.1); (2) registry
  user-level (`claude plugin`) đang trỏ version/sha nào; (3) marketplace tdq-local nạp
  live từ repo nên code mới đã ăn, nhưng registry snapshot có thể lệch.
- Kỳ vọng output: báo cáo trạng thái + nếu chưa bump thì đề xuất bump (0.6.2 hay 0.7.0)
  và lệnh update registry.
