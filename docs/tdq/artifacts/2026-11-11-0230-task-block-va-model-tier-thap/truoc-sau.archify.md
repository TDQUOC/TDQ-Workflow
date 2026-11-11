# Trước/Sau — Hiện thực Task Block chi tiết và Tự động gọi Model Tier thấp {#tong-quan}

@meta locale=vi

Hiện trạng: Task trong Plan chỉ có một dòng tóm tắt khiến subagent thi công phải đoán mò. Subagent implementer kế thừa model lớn tốn kém. Bản nâng cấp chuẩn hóa cấu trúc Task Block 8 trường kèm 4 chốt an toàn cơ học. Linter doc_lint tự động cưỡng chế rule R15. Đồng thời cấu hình subagent chạy model haiku giúp tăng tốc và tiết kiệm chi phí.

## Trước: Task một dòng và subagent chạy model lớn tốn kém {#truoc}

@workflow id=luong-truoc title="Trước: Task sơ sài và subagent kế thừa model lớn"
| spec_phase | Spec bóc tách giải thuật chi tiết | backend |
| plan_one_line | Plan chỉ tóm tắt đúng một dòng cho mỗi task | frontend |
| linter_pass | Linter bỏ qua không kiểm tra độ sâu kỹ thuật | security |
| dispatch_big | Dispatch task cho subagent chạy model lớn | messagebus |
| expensive_run | Tốn kém chi phí token và dễ sai sót khi thiếu hợp đồng | security |
| spec_phase > plan_one_line |
| plan_one_line > linter_pass |
| linter_pass > dispatch_big |
| dispatch_big > expensive_run |

Đặc điểm: Task chỉ có một dòng ngắn gọn. Subagent kế thừa cấu hình model của parent (Sonnet/Opus) gây tốn kém chi phí token trong khi vẫn có thể lệch hợp đồng interface.

## Sau: Task Block tự thân, Linter R15 và Subagent chạy Haiku {#sau}

@workflow id=luong-sau title="Sau: Task Block 8 trường, Rule R15 và Subagent Haiku"
| spec_phase | Spec bóc tách giải thuật chi tiết | backend |
| task_block_8 | Plan mở rộng task thành khối đặc tả 8 trường | frontend |
| linter_r15 | Linter R15 chặn cứng nếu task code thiếu logic | security |
| dispatch_haiku | Dispatch trọn khối đặc tả cho subagent Haiku | messagebus |
| fast_cheap | Thi công chuẩn xác ngay lần đầu, cực nhanh và tiết kiệm | security |
| spec_phase > task_block_8 |
| task_block_8 > linter_r15 |
| linter_r15 > dispatch_haiku |
| dispatch_haiku > fast_cheap |

Đặc điểm: Task chứa đầy đủ chữ ký hàm, pseudo-code, vị trí neo và ca góc hiểm. Rule R15 cưỡng chế chặn plan sơ sài. Subagent chạy Haiku thi công nhanh gọn, rẻ hơn 15 lần.
