# Danh sách công việc Chặng 1: Core Foundation (Nền tảng kiến trúc)

_Mục tiêu: Thiết lập môi trường, cấu trúc thư mục chuẩn, tạo database cơ bản._

### Backend - Database:

- Khởi tạo Backend
  - [x] Khởi tạo cây cấu trúc thư mục.
  - [x] Khởi tạo venv.
  - [x] Lưu danh sách thư viện trong requirements.txt file.
  - [x] Tạo .env và lưu các biến cần thiết, tích hợp pydantic setting.
- Cơ sở dữ liệu với alembic:
  - [x] Khởi tạo dependencies kết nối database (engine, base class, session local, function connect database,...).
  - [x] Khởi tạo alembic, cấu hình đường dẫn database..
  - [x] Viết models file ( Database Table ) cho User.
  - [x] Chạy Alembic tạo database.
  - [x] Chạy FastAPI test API Root.

### Frontend:

- Khởi tạo Frontend
  - [x] Khởi tạo cây cấu trúc thư mục.
  - [x] Tích hợp các thư viện (router-dom, tailwindCss, axios, ....).
  - [x] Thiết lập các biến CSS phục vụ cho mode sáng - tối, card, button,... (Hơi copy patse do không mạnh về màu sắc cũng như chưa hiểu sâu REACT)
- Thiết lập điều hướng website
  - [x] Khởi tạo các components web rỗng.
  - [x] Cấu hình routes App các page.
