# Danh sách công việc Chặng 3: Module Pages

_Mục tiêu: Thiết kế các page bên client: Bên phía frontend thì gửi req --> backend lấy data và trả về --> frontend lấy data, mapping và hiển thị lên UI._

## Lưu ý:

- Làm các API cho **client** lẫn các API bên phía quản lý Admin, test đầy đủ!
- Seed data từng chặng dùng test thì được viết nhiều file, sau này khi viết tổng hợp thành một file duy nhất sẽ kết hợp với biến seed_data? lưu database để check và chạy seed data một lần là được.
- UI trả về danh sách nên có hỗ trợ lọc và tìm kiếm giúp hiểu rõ học tập hơn.

### 3.1 Gọi API:

- **Backend**:
  - [x] (Nếu có thể) Tìm hiểu cách liên kết với dịch vụ lưu trữ ảnh: Cloudinary, S3,... để hỗ trợ chức năng tải ảnh lên (timeline, project, achievement).
- **Frontend**:
  - [x] Thiết lập axios Config để tự động đính access_token vào header để get data từ API.

  `- [ ] Thiết lập useFetch set các trạng thái fetch dữ liệu - (loading, oke, failed). (Hiện tại ngững task này, tập làm useState + useEffect để tiếp cận dễ hơn phần này!)`

### 3.2 About me Page (Thông tin cá nhân):

- **Backend**:
  - [x] Viết code cho model Info
  - [x] Khởi tạo và chạy seed Data của đối tượng này cho testing.
  - [x] Hoàn thiện schemas - crud logic - api của model Info (chứa đầy đủ thông tin cá nhân: Họ tên, liên hệ, ...).
- **Frontend**:
  - [x] Thiết lập UI show json thông tin fetch về thông qua API response.
  - [x] Nâng cấp UI cho page About me.

### 3.3 Timelines (Tiểu sử bản thân):

- **Backend**:
  - [x] Viết code cho model Timeline
  - [x] Khởi tạo và chạy seed Data đối tượng này cho testing.
  - [x] Hoàn thiện schemas - crud logic - api của model Timelines (Tiểu sử - hành trình học tập của bản thân).
- **Frontend**:
  - [x] Thiết lập UI show json thông tin fetch về thông qua API response.
  - [x] Nâng cấp UI cho page Timelines.

### 3.4 Project (Các dự án đã làm) - Khó nhằn nhất:

- **Backend**:
  - [x] Khởi tạo dependencies fetch thông tin từ github Repo (languages, time, ...) - dùng khi tạo project hoặc update project.
  - [x] Viết code cho model Project
  - [x] Khởi tạo và chạy seed Data đối tượng này cho testing.
  - [x] Hoàn thiện schemas - crud logic - api của model Project (Các dự án bản thân đã làm).

- **Frontend**:
  - [x] Thiết lập UI show json thông tin fetch về thông qua API response.
  - [x] Nâng cấp UI cho page Project.

  ### 3.5 Achievements (Thành tích đạt được):

- **Backend**:
  - [x] Viết code cho model Achievement
  - [x] Khởi tạo và chạy seed Data đối tượng này cho testing.
  - [x] Hoàn thiện schemas - crud logic - api của model Achievement (Các thành tích).
- **Frontend**:
  - [ ] Thiết lập UI show json thông tin fetch về thông qua API response.
  - [ ] Nâng cấp UI cho page Achievements.

### 3.6 Index Page (Khó do bao quát nhiều thông tin của các models nên modules này được thực hiện ở sau cùng):

- **Backend**:
  - [ ] Viết một API gọi tất cả các thông tin cần thiết thay vì bắt Frontend phải chạy promise tổng nhiều API cùng một lúc.
- **Frontend**:
  - [ ] Thiết lập UI show json thông tin fetch về thông qua API response.
  - [ ] Nâng cấp UI cho page Index.

### 3.7 Xử lý Backend các đối tượng System Config:

- **System Config**:
  - [ ] Thiết lập quản lý models - schemas, crud, router.

### 3.8 Tinh chỉnh Seed Data:

- **Backend**:
  - [ ] Gộp các seed data thành một file duy nhất để khi chạy seed data chỉ để gọi python **seed_data.py** là được.
- **Frontend**:
  - [ ] Testing lại các page.
