# Pilot audit — giữ case có oracle, không giảm số cho đẹp
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Phạm vi pilot: `tests/test_tdq_test.py` và `tests/test_tdq_test_receipt.py`. `python -m pytest` thu thập **206 nodeid trong 0,14s**. Đây là phép collect, không chạy test, không xác nhận 206 case đều có giá trị. `tdq-lean` audit overbuild chỉ đề xuất sau khi so oracle; trong pilot không tìm được hai case nào vừa trùng *đầu vào, oracle, rủi ro, đường đi* vừa có chứng cứ test còn lại bắt lỗi đã biết. **Quyết định: giữ nguyên, xóa 0**.

| Feature thực của TDQ | Case đại diện đã có (test file:line) | Oracle / rủi ro giữ lại | Quyết định |
|---|---|---|---|
| Chọn test theo file đổi | `tests/test_tdq_test.py:313`, `:319`, `:335` | Module liên quan chạy và sai thì trả lỗi; khi mất mapping phải fallback, không báo xanh giả | GIỮ — oracle khác nhau |
| Đường phụ thuộc/nguồn khó | `tests/test_tdq_test.py:75`, `:98`, `:178`, `:194`, `:502` | Bán kính import, tình huống nguồn thiếu và ngưỡng full có kết quả độc lập | GIỮ — tránh bỏ sót test liên module |
| Receipt source/fingerprint | `tests/test_tdq_test_receipt.py:50`, `:77`, `:97`, `:109` | Reuse chỉ trên nguồn/môi trường/manifest còn hợp lệ, phân biệt chiều đổi | GIỮ — bảo vệ fail-closed |
| Lỗi, đồng thời và phục hồi | `tests/test_tdq_test_receipt.py:171`, `:220`, `:281`, `:433`, `:487` | Receipt lỗi không thành PASS, join không biến thành lượt chạy thứ hai, failure giữ provenance | GIỮ — rủi ro an toàn dữ liệu/nguồn |
| Input giả bất hợp lệ | `tests/test_tdq_test_receipt.py:474` | Deadline NaN/Inf, ≤0, bool và string phải từ chối trước lock/hash/process | GIỮ — tổ hợp tham số khác kiểu đều đánh đúng ranh giới |

**Gap cần bổ sung:** Runner chưa có CLI chỉ *in* selector/scope/lý do và số module trước pytest; cần ca public CLI `--plan-only` ở fixture temp cho direct, fallback và rỗng, chứng minh không khởi tạo subprocess/ghi receipt. Thêm tối thiểu các ca có oracle khác nhau, không tạo ma trận Cartesian.

**Không đánh đồng:** Một case pytest parametrized là nodeid riêng; subtest trong unittest có bằng chứng con. Không gộp các case trên vào một test parent vì sẽ giảm độ rõ nguyên nhân và manifest. Chỉ rà lại tập pilot nếu mutation/negative chứng minh một ca thừa; không tính thời gian tiết kiệm từ việc giữ nguyên test.
