# Trang sơ đồ của một feature
@nhánh: Sơ đồ mind-map > Trang feature

B1 · Người dùng chạy lệnh xem sơ đồ của một feature (scripts/tdq_mindmap.py::cmd_xem)
B2 · Đọc file .md và kiểm hình dạng trước khi dựng trang (scripts/mindmap_render.py::render_feature_page)
B2! · sai hình dạng thì ném DiagramInvalid kèm danh sách vi phạm, không sinh trang nào (scripts/mindmap_render.py::DiagramInvalid)
B3 · Tách file thành tiêu đề, nhánh, phụ thuộc và danh sách bước phẳng (scripts/mindmap_render.py::parse_diagram)
B4 · Dựng mô hình luồng: gom B<n> với B<n>! cùng số thành cặp quyết định, sinh node và cạnh có nhãn ok/lỗi (?)
B5 · Tính bố cục: ngắt dòng mô tả, suy chiều cao hộp theo số dòng, đặt toạ độ cột chính và cột nhánh lỗi (?)
B6 · Sinh SVG lớp nghiệp vụ: hộp chữ nhật cho bước thường, hình thoi cho bước có nhánh lỗi, viên thuốc cho điểm vào và điểm ra (?)
B7 · Ghép sơ đồ lên trên, giữ nguyên danh sách bước và khối phụ thuộc bên dưới (scripts/mindmap_render.py::_render_business_layer)
B8 · Dựng lớp chi tiết từ graph.json, giữ nguyên hành vi cũ (scripts/mindmap_render.py::_render_detail_layer)
B8! · thiếu graph.json thì lớp chi tiết hạ xuống chỗ trống báo chưa đồ thị hoá, trang vẫn dựng được (scripts/mindmap_render.py::GraphIndex)
B9 · Ghép hai lớp vào khung HTML kèm CSS và script đổi lớp, ghi ra file (scripts/mindmap_render.py::render_feature_page)
