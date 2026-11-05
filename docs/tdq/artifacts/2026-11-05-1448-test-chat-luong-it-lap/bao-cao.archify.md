# Test ít hơn khi hợp lý, không bỏ sót lỗi quan trọng {#tong-quan}

@meta locale=vi

Cách chọn và viết test đã đổi. **Toàn bộ test trên mã mới chạy xanh**, nhưng yêu cầu **chưa hoàn tất**: chưa đánh giá được hiệu quả quy tắc mới, còn ba điểm chờ bạn quyết định. Đây là kết quả working-tree, không phải thiết kế planned. Chưa commit, push hoặc merge.

## 1. Trước request: test được tạo và chạy ra sao? {#truoc}

Mỗi tính năng bị yêu cầu ít nhất 1 ca thường, 2 ca biên và 1 ca lỗi, kể cả khi vài ca không kiểm rủi ro thực. Trước khi chạy chưa có lệnh cho xem danh sách test sẽ chọn. Số 4.161 lịch sử là số test, **không phải số tính năng**.

@workflow id=truoc-test title="Trước: tạo theo chỉ tiêu"
| feature | Tính năng đổi | backend |
| quota | Ép số ca cố định | backend |
| run | Chọn test lúc chạy | backend |
| full | Kiểm toàn bộ ở cuối | backend |
| feature > quota | Ca không rủi ro vẫn được yêu cầu |
| quota > run | Chưa xem danh sách trước |
| run > full | Kết quả cũ không đủ nghiệm thu |

## 2. Sau request: thay đổi gì? {#sau}

Chỉ thêm ca có hành vi, rủi ro và kết quả kiểm tra rõ ràng; dùng dữ liệu giả trong thư mục tạm. Vẫn giữ ca lỗi/bảo mật/mất dữ liệu có giá trị. `vung-cham --plan-only` cho xem phạm vi, số lượng, danh sách và lý do **mà không chạy test**. Nếu không rõ test liên quan, chọn rộng hoặc toàn bộ. Không xóa test cũ khi chưa chứng minh trùng; CI giữ nguyên.

@workflow id=sau-test title="Sau: chọn theo rủi ro"
| feature | Tính năng và rủi ro | backend |
| oracle | Dữ liệu giả, kết quả rõ | security |
| plan | Xem trước danh sách | backend |
| run | Chạy vùng cần kiểm | backend |
| qc | Kiểm toàn bộ cuối | security |
| feature > oracle | Không thêm ca cho đủ số |
| oracle > plan | Không bịa tính năng login |
| plan > run | Thiếu liên kết thì chọn rộng |
| run > qc | Chạy mới, không dùng lượt cũ |

**Chưa chứng minh tổng số test trong repo đã giảm.** Luật mới tránh thêm ca vô ích từ nay; chỉ xóa hoặc gộp ca cũ khi có bằng chứng trùng.

## 3. Đã test gì? {#da-test}

Kiểm xem trước khi file thay đổi, không có file thay đổi, thiếu liên kết test và thư mục test lồng nhau. Chạy bộ test kiểm quy tắc/runtime, rồi chạy toàn bộ repo từ đầu trên mã hiện tại.

@workflow id=bang-chung title="Những phép kiểm đã chạy"
| smoke | Xem trước: 2 ca đạt | backend |
| contract | Quy tắc: 41 ca đạt | backend |
| full | Toàn repo: 4.162 đạt | security |
| receipt | Kết quả có chứng cứ | security |
| smoke > contract | Dùng thư mục giả lập |
| contract > full | CI giữ nguyên |
| full > receipt | 4.169 mã ca kiểm |

## 4. Kết quả test và việc còn mở {#ket-qua}

**Test trên mã mới: ĐẠT.** Lượt chạy toàn bộ cuối: 4.162 đạt, 7 bỏ qua, 2.724 kiểm tra con (đã nằm trong ca kiểm, không cộng thêm); 4.169 mã ca, kết quả đầy đủ và cùng mã nguồn trước/sau. Chạy mới, không dùng kết quả cũ. Mất 857,25 giây: **đây là thời gian toàn bộ test, không phải smoke**. Receipt SHA256 `71dd2a235402dbff0236922e540611e45d4e45e0ea8de41cd030b8aae1df8e44`.

**Yêu cầu tổng thể: CHƯA ĐẠT CỔNG CUỐI.** (1) Hiệu quả quy tắc mới: 0 lượt đánh giá thực tế, nên chưa biết AI chọn test tốt hơn không; cổng báo cáo cuối đang chặn. (2) Chạy toàn bộ 5 lượt thay vì ngân sách 3 do phải sửa lỗi và một lượt mất hiệu lực khi nguồn đổi cùng lúc. (3) Chưa đo smoke đầy đủ mức full/ultra, nên chưa biết mốc khuyến nghị 5/10 phút có đạt không. Ba điểm Q3/Q5/Q6 chờ bạn quyết định; không tự miễn cổng.

`bo_sot=0` nhưng `radius_complete=false` **không chứng minh** không bỏ sót test. Các lượt full trước ERROR/FAIL/INCOMPLETE không tính PASS. Preview thiết kế đã cũ sau sửa; trang này gắn nguồn đang làm việc. Kiểm trình duyệt native có fallback Windows, không gọi đó là PASS native.
