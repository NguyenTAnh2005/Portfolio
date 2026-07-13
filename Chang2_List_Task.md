# Danh sách công việc Chặng 2: Module Authentication & User (Xác thực & Người dùng)

_Mục tiêu: Hoàn thiện luồng đăng nhập, bảo mật JWT, điều hướng website._

### Backend - Database:

- Error Handling, CORS:
  - [x] Khởi tạo class xử lý lỗi tập trung. => [[Lưu ý phần này tại đây.]](./Note_ErrorHandling.md)
  - [x] Khởi tạo CORS (Cross-Origin Resource Sharing) làm việc với pydantic setting
- Security files:
  - [x] Xây dựng hàm mã hóa mật khẩu
  - [x] Xây dựng hàm tạo access token (JWT)
  - [x] Xây dựng hàm giải mã access token để kiếm tra quyền (get_current_user, get_current_admin)
- Auth Services:
  - [x] Khởi tạo User Schemas
  - [x] Khởi tạo Crud user
  - [x] Khởi tạo seed Data cho User để tiện cho testing.
  - [x] Khởi tạo Auth API, User API
  - [x] Chạy Backend test API, kiểm tra bằng swagger UI và postgreSQL

### Frontend:

- Lưu trữ đăng nhập:
  - [x] Viết .env lưu đường dẫn chạy backend.
  - [x] Thiết kế UI đơn giản cho trang đăng nhập.
  - [x] Thiết lập Axios gọi Req và trả về Res.

- Điều hướng đăng nhập:
  - [x] Khởi tạo AuthContext lưu trữ các trạng thái (đăng nhập, đăng xuất), lưu access_token trên localStorage.
  - [x] Viết Protected Routes để quản lý điều hướng.
  - [x] Thiết kế layout cho Admin và Client với Outlet.
  - [x] Tinh chỉnh lại App Routes sao cho hợp với Protected Routes cũng như UI đăng nhập, đảm bảo responsive.
