# Trước/Sau — Hạn chế dừng giữa plan {#tong-quan}

@meta locale=vi

Thiết kế **planned** chỉ áp dụng Claude Code. Không giám sát lời gọi API đang treo và không tự bật `/goal` hoặc lịch chạy. TDQ chỉ trình điều kiện `/goal` để người dùng xác nhận rồi tự bật trong session; chưa bật thì không phát sinh lượt đánh giá model. Trần Stop giữ ba lần rồi hạ cấp an toàn; báo rõ việc cần làm khi quay lại.

## Luồng Stop và khôi phục {#luong}

@workflow id=truoc-stop title="Trước: nhắc ba lần, rồi hint chung"
| plan | Plan còn task mở | backend |
| stop | Stop hook nhắc làm tiếp | security |
| stuck | 3 lần không tiến triển: hint chung | backend |
| resume | Resume: chỉ doing/dispatched | frontend |
| plan > stop | còn việc |
| stop > stuck | plan không đổi |
| stuck > resume | quay lại |

@workflow id=sau-stop title="Sau: task cụ thể, vẫn có lối thoát"
| plan2 | Plan còn task mở | backend |
| stop2 | Stop nhắc task và bước tiếp | security |
| stuck2 | Lần bốn: báo kẹt và việc còn mở | backend |
| resume2 | Resume: chỉ đúng task cần kiểm | frontend |
| goal | Tùy chọn: người dùng bật /goal | frontend |
| plan2 > stop2 | còn việc |
| stop2 > stuck2 | không tiến triển |
| stuck2 > resume2 | kiểm lại trước retry |
| goal > stop2 | bổ trợ, không thay Stop |

Hiện trạng: `hooks/scripts/stop_gate.py:154-229` chặn tối đa ba lần; `hooks/scripts/session_start.py:295-337` có anchor doing/dispatched; `hooks/scripts/prompt_context.py:249-379` nhắc lúc prompt. Sau là đề xuất, chưa có bằng chứng runtime. Pause, task đang giao `[>]`, plan thiếu hoặc đã xong giữ nguyên hành vi miễn chặn.
