# Đăng nhập
@nhánh: Tài khoản > Đăng nhập

B1 · Nhập email và mật khẩu (src/pages/login.tsx::LoginForm.onSubmit)
B2 · Kiểm tra tại chỗ trước khi gửi (src/lib/validators.ts::validateCredentials)
B2! · email sai khuôn hoặc mật khẩu ngắn thì báo lỗi tại ô nhập và dừng (src/lib/form-ui.ts::showFieldError)
B3 · Gửi yêu cầu qua kênh mã hoá (src/api/auth.ts::authApi.login)
B4 · Tra người dùng và đối chiếu băm mật khẩu (server/controllers/auth.py::AuthController.login)
B4! · không có người dùng hoặc băm sai thì trả một lỗi chung (server/controllers/auth.py::deny_login)
B5 · Phát token phiên và token làm mới (server/services/token.py::TokenService.issue_pair)
B6 · Lưu token và vào màn hình chính (?)
