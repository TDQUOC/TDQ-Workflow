# Trang tổng sơ đồ mind-map
@nhánh: Sơ đồ mind-map > Trang tổng
@phụ-thuộc: mind-map-trang-feature · dùng chung bộ dựng hộp, mũi tên và bảng màu của trang feature

B1 · Người dùng chạy lệnh xem trang tổng (scripts/tdq_mindmap.py::cmd_xem)
B2 · Quét thư mục mind-map, đọc từng file sơ đồ ra tiêu đề, nhánh và phụ thuộc (scripts/mindmap_render.py::collect_total_data)
B2! · file sai hình dạng thì bỏ qua phần nhánh của nó và xếp vào nhóm chưa gắn nhánh, không làm hỏng cả trang (scripts/mindmap_render.py::_render_branch_tree)
B3 · Xếp feature theo bậc phụ thuộc để biết cột nào đứng trước (scripts/mindmap_render.py::_feature_levels)
B4 · Tính bố cục lưới phụ thuộc: toạ độ từng ô theo bậc và hàng (scripts/mindmap_render.py::_layout_grid)
B5 · Vẽ lưới phụ thuộc bằng bộ hộp và mũi tên dùng chung với trang feature (scripts/mindmap_render.py::_render_dependency_svg)
B6 · Dựng cây nhánh tổng → nhánh con → feature thành mô hình cây, mỗi lá là một feature có file (?)
B7 · Vẽ cây nhánh thành sơ đồ SVG, mỗi ô feature bọc trong một link tới trang riêng của nó (?)
B7! · feature chưa có file sơ đồ thì vẽ ô nét đứt, mờ, không gắn link (scripts/mindmap_render.py::_render_dependency_svg)
B8 · Giữ danh sách link cũ và danh sách cạnh phụ thuộc, đặt xuống dưới sơ đồ để đọc đủ lý do (scripts/mindmap_render.py::_render_edge_list)
B9 · Ghép các khối vào khung HTML kèm CSS dùng chung, ghi ra index.html (scripts/mindmap_render.py::render_total_page)
