# Mua hàng
@nhánh: Thương mại > Mua hàng
@phụ-thuộc: dang-nhap · cần token phiên do đăng nhập phát ra

B1 · Bấm đặt hàng trên giỏ (src/pages/cart.tsx::CartPage.onCheckout)
B2 · Đọc token phiên đang giữ (src/lib/session.ts::readSessionToken)
B2! · không có token thì đẩy sang màn đăng nhập (src/lib/session.ts::redirectToLogin)
B3 · Gửi đơn kèm token (src/api/order.ts::orderApi.create)
B4 · Xác thực token rồi khoá tồn kho (server/controllers/order.py::OrderController.create)
B4! · token hết hạn thì trả lỗi phiên và không khoá tồn kho (server/controllers/order.py::deny_order)
B5 · Ghi đơn và phát sự kiện thanh toán (server/services/order.py::OrderService.place)
B6 · Hiện màn xác nhận đơn (?)
