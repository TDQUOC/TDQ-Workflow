# Trước/Sau — Nâng cấp độ chi tiết Plan cho Model Tier thấp {#tong-quan}

@meta locale=vi

Hiện trạng: Task trong Plan chỉ có đúng một dòng tóm tắt. Subagent thi công không đọc Spec nên rơi vào bẫy đoán mò. Bản nâng cấp chuẩn hóa cấu trúc Self-Contained Task Block. Khối này chứa mục tiêu, chữ ký hàm, pseudo-code và ca góc hiểm. Nhờ vậy model tier thấp thi công chuẩn xác 100%.

## Trước: Task một dòng làm gãy cầu nối với Spec {#truoc}

@workflow id=luong-truoc title="Trước: Task một dòng khiến model tier thấp đoán mò"
| spec_deep | Spec §3c bóc tách giải thuật chi tiết | backend |
| plan_thin | Plan chỉ tóm tắt đúng một dòng cho mỗi task | frontend |
| dispatch | Dispatch chỉ gửi một dòng task cho subagent | messagebus |
| weak_ai | Model tier thấp tự bịa chữ ký và giải thuật | backend |
| broken_code | Code lỗi hoặc sai kiến trúc khi merge | security |
| spec_deep > plan_thin |
| plan_thin > dispatch |
| dispatch > weak_ai |
| weak_ai > broken_code |

Đặc điểm: Subagent thi công nhận duy nhất một dòng task trong prompt. Model tier thấp thiếu ngữ cảnh kỹ thuật nên tự bịa cấu trúc và bỏ quên ca hiểm.

## Sau: Self-Contained Task Block thi công khép kín {#sau}

@workflow id=luong-sau title="Sau: Đặc tả thi công đầy đủ giúp model tier thấp làm đúng"
| spec_deep | Spec §3c bóc tách giải thuật chi tiết | backend |
| task_block | Plan mở rộng task thành khối đặc tả khép kín | frontend |
| dispatch_rich | Dispatch gửi trọn khối đặc tả cho subagent | messagebus |
| weak_ai_ok | Model tier thấp bám sát pseudo-code và signature | backend |
| perfect_code | Code chính xác một lần, xanh ngay không đoán mò | security |
| spec_deep > task_block |
| task_block > dispatch_rich |
| dispatch_rich > weak_ai_ok |
| weak_ai_ok > perfect_code |

Đặc điểm: Task chứa đầy đủ chữ ký hàm, type hints, pseudo-code từng bước và tiêu chí TDD. Model nhỏ có thể dịch trực tiếp logic sang mã nguồn sạch mà không cần đoán.
