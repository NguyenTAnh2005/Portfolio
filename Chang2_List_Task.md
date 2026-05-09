# Danh sách công việc Chặng 2: Module Authentication & User (Xác thực & Người dùng)

_Mục tiêu: Hoàn thiện luồng đăng nhập, bảo mật JWT, điều hướng website._

### Backend - Database:

- Error Handling, CORS:
  - [ ] Khởi tạo class xử lý lỗi tập trung
  - [ ] Khởi tạo CORS (Cross-Origin Resource Sharing) làm việc với pydantic setting
- Security files:
  - [ ] Xây dựng hàm mã hóa mật khẩu
  - [ ] Xây dựng hàm tạo access token (JWT)
  - [ ] Xây dựng hàm giải mã access token để kiếm tra quyền (get_current_user, get_current_admin)
- Auth Services:
  - [ ] Khởi tạo User Schemas, Crud user
  - [ ] Khởi tạo seed Data cho User để tiện cho testing.
  - [ ] Khởi tạo Auth API, User API
  - [ ] Chạy Backend test API, kiểm tra bằng swagger UI và postgreSQL

### Frontend:

- Điều hướng đăng nhập:
  - [ ] Khởi tạo AuthContext lưu trữ các trạng thái (đăng nhập, đăng xuất), lưu access_token trên localStorage.
  - [ ] Viết Protected Routes để quản lý điều hướng.
  - [ ] Thiết kế layout cho Admin và Client với Outlet.
  - [ ] Tinh chỉnh lại App Routes sao cho hợp với Protected Routes.
- Lưu trữ đăng nhập:
  - [ ] Viết .env lưu đường dẫn chạy backend.
  - [ ] Code service gửi req login và ứng dụng lưu access-token lên localstorage (authcontext).
  - [ ] Thiết kế UI đơn giản cho trang đăng nhập và chạy thử test đăng nhập.
