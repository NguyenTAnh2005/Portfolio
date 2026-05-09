# Danh sách công việc Chặng 1: Core Foundation (Nền tảng kiến trúc)

_Mục tiêu: Thiết lập môi trường, cấu trúc thư mục chuẩn, tạo database cơ bản._

### Backend - Database:

- Khởi tạo Backend
  - [ ] Khởi tạo cây cấu trúc thư mục.
  - [ ] Khởi tạo venv.
  - [ ] Lưu danh sách thư viện trong requirements.txt file.
  - [ ] Tạo .env và lưu các file cần thiết, tích hợp pydantic setting.
- Cơ sở dữ liệu với alembic:
  - [ ] Khởi tạo dependencies kết nối database (engine, base class, session local, function connect database,...).
  - [ ] Khởi tạo alembic, cấu hình đường dẫn database..
  - [ ] Viết models file ( Database Table ) cho User.
  - [ ] Chạy Alembic tạo database.
  - [ ] Chạy FastAPI test API Root.

### Frontend:

- Khởi tạo Frontend
  - [ ] Khởi tạo cây cấu trúc thư mục.
  - [ ] Tích hợp các thư viện (router-dom, tailwindCss, axios, ....).
  - [ ] Thiết lập các biến CSS phục vụ cho mode sáng - tối, card, button,...
- Thiết lập điều hướng website
  - [ ] Khởi tạo các components web rỗng.
  - [ ] Cấu hình routes App các page.
