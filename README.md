## Dự án Portfolio

- **Công nghệ sử dụng: ReactJS + FastAPI (Synchronous) + PostgreSQL.**
- **Mục đích cốt lõi dự án:** Tạo ra trang web lưu trữ các thông tin cá nhân cũng như các thông tin cần thiết để dùng trong việc gửi CV cho nhà tuyển dụng. Thay vì dùng CV giấy.
- **Mục tiêu học thuật:**
  - Hiểu rõ React Basic (Những cái gì nên và phải biết. Đủ để code frontend oke!)
  - Làm quen với FastAPI đồng bộ trước (Synchronous).
  - Biết được quy trình cơ bản nhất của một website.
  - Tạo nền tảng phát triển cho các dự án tiếp theo với công nghệ cũng như cách lập trình ooke hơn.

## 🚀 Kế Hoạch Phát Triển Dự Án (Modular Approach)

### 📍 Chặng 1: Core Foundation (Nền tảng kiến trúc)

- Mục tiêu: Thiết lập môi trường, cấu trúc thư mục chuẩn, tạo database cơ bản.
- Chi tiết công việc: [Chang1_List_Task.md](./DOCS/1_PHASES/Chang1_List_Task.md).

## 📍 Chặng 2: Module Authentication & User (Xác thực & Người dùng)

- Mục tiêu: Hoàn thiện luồng đăng nhập, bảo mật JWT, điều hướng website.
- Chi tiết công việc: [Chang2_List_Task.md](./DOCS/1_PHASES/Chang2_List_Task.md)

## 📍 Chặng 3: Module Pages (Các pages nội dung của website)

- Mục tiêu: Thiết kế các page bên client: Bên phía frontend thì gửi req --> backend lấy data và trả về --> frontend lấy data, mapping và hiển thị lên UI.
- Chi tiết công việc: [Chang3_List_Task.md](./DOCS/1_PHASES/Chang3_List_Task.md).

## 📍 Chặng 4: Module Managerment (Quản lý web)

- Mục tiêu: Xây dựng hệ quản lý các đối tượng (info, timeline, project, achievement ).
- Chi tiết công việc: [Chang4_List_Task.md](./DOCS/1_PHASES/Chang4_List_Task.md).

## 📍 Chặng 5: Tối ưu hóa & Triển khai (Optimization & Deployment)

- Mục tiêu: Tối ưu mã nguồn, review code hợp lý. Cắt tỉa dự án. Đưa dự án lên môi trường production.
- Chi tiết công việc: [Chang5_List_Task.md](./DOCS/1_PHASES/Chang5_List_Task.md).

## Cấu trúc thư mục (chỉ liệt kê các mục đáng chú ý):

```bash
├── 📁 BACKEND             # MÃ NGUỒN BACKEND
│   ├── 📁 alembic         # Phần kết nối database thông qua alembic
│   │   ├── 📁 versions    # Nơi quản lý các phiên bản của database
│   │   ├── 🐍 env.py      # Cấu hình đường dẫn database
│   ├── 📁 app             # Mã nguồn chính backend
│   │   ├── 📁 core        # Các code hệ thống như: Jwt, hashpassword,...
│   │   ├── 📁 crud        # Code CRUD database
│   │   ├── 📁 models      # Code model tạo bảng database
│   │   ├── 📁 routers     # Code chứa logic và các API endpoint
│   │   ├── 📁 schemas     # Các class validate cho kết quả trả về của API
│   │   └── 🐍 db_connection.py # Cấu hình kết nối đến DB
│   ├── 📝 README.md
│   ├── 🐍 main.py           # File chạy chính của Backend
│   ├── 📄 requirements.txt. # File lưu trữ phiên bản, tên các thư viện
│   └── 🐍 seed_data.py      # File chạy data ban đầu cần có (admin đầu tiên)
│
│
├── 📁 DATABASE
│   └── 📄 checking_sql.sql  # File test CRUD database (POSTGRESQL)
│
│
├── 📁 FRONTEND              # MÃ NGUỒN FRONTEND
│   ├── 📁 src               # Mã nguồn chính của Frontend
│   │   ├── 📁 assets        # Nơi chứa ảnh, audio,..
│   │   ├── 📁 components    # Các thành phần nhỏ của trang web
│   │   ├── 📁 contexts      # Nơi lưu trữ AuthContext, lưu trữ đám mây JWT
│   │   ├── 📁 hooks         # Hook nhà làm (VD: fetch data xong -> loading --> success or failed )
│   │   ├── 📁 layout        # Nơi lưu trữ khung trang web của Admin và Client
│   │   ├── 📁 pages         # Nơi chứa các page chính của Layout
│   │   │   ├── 📁 admin
│   │   │   ├── 📁 client
│   │   │   └── 📄 Login.jsx
│   │   ├── 📁 public
│   │   │   └── 🖼️ icons.svg
│   │   ├── 📁 routes                  # Nơi chứa điều hướng các page của trang web
│   │   │   ├── 📄 AdminRoutes.jsx
│   │   │   ├── 📄 AppRoutes.jsx
│   │   │   ├── 📄 ClientRoutes.jsx
│   │   │   └── 📄 ProtectedRoutes.jsx # Code bảo vệ điều hướng, checking Authorization
│   │   ├── 📁 services       # Nơi gọi API, nhét tự động JWT bằng Axios
│   │   ├── 📄 App.jsx
│   ├── 📁 utils              # Nơi chứa các code tiện ích (xử lý chuỗi, thời gian,...)
│
│
├── 📁 DOCS              # Tài liệu được note lại để phục vụ học tập
│   ├── 📁 1_PHASES
│   │   ├── 📝 Chang1_List_Task.md
│   │   ├── 📝 ..v.v.
│   └── 📁 2_LEARNING
│       ├── 📁 BACKEND
│       │   ├── 📝 fastapi-model-alembic-guide.md
│       │   ├── 📝 .v.v.
│       ├── 📁 FRONTEND
│       │   ├── 📝 axios-service-guide.md
│       │   └── 📝 .v.v.
│       └── 📁 NOTES
│           └── 📝 note-api-login.md
│           └── 📝 .v.v.
```
