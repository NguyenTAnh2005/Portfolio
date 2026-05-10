pip list --not-required --format=freeze > requirements.txt

# Backend Technologies & Libraries

Dưới đây là danh sách các công cụ cốt lõi được sử dụng để xây dựng hệ thống quản lý hồ sơ năng lực:

The following core libraries power the backend of this IT student portfolio website:

- fastapi: Framework chính mạnh mẽ và hiệu suất cao giúp xây dựng các API xử lý dữ liệu.
  (The primary high-performance framework used for building robust and scalable APIs)

- uvicorn: Máy chủ (ASGI Server) hiệu năng cao dùng để chạy ứng dụng FastAPI trong môi trường phát triển. (A high-speed ASGI server implementation used to run the FastAPI application in the local environment.)

- sqlalchemy: Thư viện ORM hàng đầu giúp tương tác với cơ sở dữ liệu PostgreSQL thông qua mã Python thay vì viết các câu lệnh SQL thuần túy. (A powerful Object-Relational Mapper (ORM) that enables database interaction using Pythonic code instead of raw SQL.)

- psycopg2-binary: Trình điều khiển (driver) thiết yếu giúp kết nối và thực thi các truy vấn giữa Python và PostgreSQL. (The essential PostgreSQL adapter for Python, enabling reliable database connectivity.)

- alembic: Công cụ quản lý phiên bản cấu trúc bảng (Migration), hỗ trợ nâng cấp hoặc thay đổi database mà không làm mất dữ liệu hiện có. (A lightweight database migration tool used to manage schema changes and versioning without data loss.)

- pydantic-settings: Quản lý tập trung các cấu hình từ file .env, giúp truy cập các biến môi trường nhanh chóng và an toàn. (Manages application settings and environment variables from .env files with strong data validation.)

- python-jose[cryptography]: Thư viện chuyên dụng để tạo, ký và giải mã các chuỗi JWT (JSON Web Token) cho hệ thống xác thực.(A dedicated library for creating, signing, and verifying JSON Web Tokens (JWT) for the authentication system.)

- passlib[bcrypt] & bcrypt: Bộ công cụ bảo mật dùng để băm (hashing) và kiểm tra mật khẩu, đảm bảo an toàn tuyệt đối cho tài khoản Admin. (A robust security suite used for password hashing and verification to ensure administrative account safety.)

- httpx: Thư viện hỗ trợ gọi API bất đồng bộ đến GitHub để lấy dữ liệu các dự án thực tế. (An asynchronous HTTP client used to fetch real-time project data from the GitHub API.)

- python-multipart: Cho phép hệ thống xử lý và nhận dữ liệu từ các biểu mẫu đăng nhập (Forms) theo chuẩn OAuth2. (Provides support for parsing and handling form data, essential for OAuth2-compatible login flows.)

# Lưu ý chức năng

- trong quá trình triển khai các bước thực hiện, có thể sẽ dư thừa nhiều phần, chủ yếu là phần schemas và crud function do dự án này không yêu cầu nhiều về chức năng. Tuy nhiên cũng nên viết đầy đủ để có thể hỗ trợ mở rộng - phát triển dự án.
