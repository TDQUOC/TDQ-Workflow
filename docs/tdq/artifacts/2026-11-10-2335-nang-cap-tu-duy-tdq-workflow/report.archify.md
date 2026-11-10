# Báo cáo nghiệm thu — Nâng cấp tư duy sâu và chặn bẫy lặp tool trong TDQ Workflow {#tong-quan}

@meta locale=vi

Đã giải quyết triệt để lỗi đọc lặp 74 lần trên cùng một file: bổ sung thuật toán Range Overlap (độ phủ ≥ 70%) vào read_gate.py, phân biệt rõ hành vi đọc file dài hợp lệ với bẫy lặp 1 đoạn, định dạng cảnh báo [TDQ:DOC] nhắc AI dừng lặp, và củng cố quy chuẩn Reflective Thought trong Soul.

## Trước: Read gate bỏ sót offset/limit và thiếu phản tư {#truoc}

@workflow id=luong-truoc title="Trước: Bẫy lặp đọc file 74 lần không bị chặn"
| read_call | Agent gọi Read(offset, limit) | frontend |
| gate_check | read_gate.py: dau/cuoi != 0 nên bỏ qua kiểm tra | security |
| no_thinking | Model nhận kết quả, 0 thinking token, tự hồi quy | backend |
| repeat_loop | Lặp lại 74 lần luân phiên đọc cùng 2 đoạn code | backend |
| user_stop | Người dùng phải bấm Interrupt và hỏi sao lâu vậy | frontend |
| read_call > gate_check |
| gate_check > no_thinking |
| no_thinking > repeat_loop |
| repeat_loop > user_stop |

Đặc điểm: Cổng `read_gate.py` coi mọi lệnh có `offset/limit` là "aimed read" và thoát 0 im lặng. Attention của mô hình bị khóa vào chuỗi gọi tool liên hoàn không suy luận.

## Sau: Range Overlap ≥ 70% cảnh báo và bẻ gãy bẫy lặp {#sau}

@workflow id=luong-sau title="Sau: Phát hiện trùng lặp dải dòng và nhắc AI dừng lặp"
| read_call | Agent gọi Read(offset, limit) | frontend |
| overlap_calc | read_gate.py: tính tỉ lệ chồng lấn Range Overlap với các dải cũ | security |
| branch_eval | Overlap < 30%: Khám phá file dài hợp lệ (cho phép, im lặng) | backend |
| loop_warn | Overlap >= 70% lần 2+: Phát cảnh báo [TDQ:DOC] nhắc AI dừng lặp | security |
| ai_reflect | AI nhận cảnh báo, bẻ gãy bẫy lặp, tổng hợp giải pháp | frontend |
| read_call > overlap_calc |
| overlap_calc > branch_eval |
| overlap_calc > loop_warn |
| loop_warn > ai_reflect |

Đoạn đọc mới bị trùm lên đoạn cũ ≥ 70% từ lần thứ 2 trở lên sẽ kích hoạt nhắc nhở `[TDQ:DOC]`, cung cấp số liệu dòng và tên file cụ thể. File dài đọc các phân đoạn độc lập vẫn được phép hoàn toàn. Toàn bộ 19 bài test trong `tests/test_read_gate.py` đều xanh 100%.
