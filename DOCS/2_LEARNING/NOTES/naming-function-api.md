# Naming Convention Guide — Router / Service / CRUD

Áp dụng cho kiến trúc 3 lớp: `router → service → crud`.
Mục tiêu: đọc tên hàm là biết ngay nó thuộc lớp nào, làm gì, không cần prefix thủ công như `logic_`.

---

## 0. Nguyên tắc import — nền tảng của mọi convention bên dưới

**Không** import thẳng từng hàm:

```python
from app.crud.project import get_project_by_id, create_project
from app.services.project import logic_create_project
```

**Import theo module**, dùng alias rõ vai trò:

```python
from app.crud import project as project_crud
from app.services import project as project_service
```

Lời gọi trở thành tự mô tả, không lo đụng tên giữa các layer:

```python
project_service.create_project(...)
project_crud.get_by_id(db, project_id)
```

Đây là lý do bạn không cần tiền tố `logic_` — module `services.project` đã đủ ngữ cảnh rồi.

---

## 1. Lớp CRUD — verb-only, ngắn gọn

Vì đã gọi qua `project_crud.xxx`, tên "project" trong hàm là thừa.

| Việc                                 | Tên hàm            |
| ------------------------------------ | ------------------ |
| Lấy 1 bản ghi theo id                | `get_by_id`        |
| Lấy danh sách (có phân trang/filter) | `get_all`          |
| Tạo mới                              | `create`           |
| Cập nhật field text                  | `update_text_form` |
| Cập nhật ảnh                         | `update_image`     |
| Đồng bộ dữ liệu ngoài (github,...)   | `sync`             |
| Xóa                                  | `delete`           |

**Quy tắc:**

- Verb đứng đầu, không lặp tên model.
- Đồng bộ thuật ngữ: chọn `image` hoặc `img` và dùng xuyên suốt cả 3 layer (đang bị lẫn lộn giữa `update_project_img` và schema `img_url`).

---

## 2. Lớp Service — verb + subject, mô tả nghiệp vụ

Service là nơi xử lý logic nghiệp vụ (check trùng, gọi API ngoài, upload ảnh...), nên tên hàm nên nói rõ **hành động + đối tượng nghiệp vụ**, không chỉ verb trơn như crud.

| Việc                                                  | Tên hàm                  |
| ----------------------------------------------------- | ------------------------ |
| Tạo project (kèm check trùng, fetch repo, upload ảnh) | `create_project`         |
| Cập nhật phần text                                    | `update_project_text`    |
| Cập nhật ảnh                                          | `update_project_image`   |
| Đồng bộ thông tin từ github                           | `sync_project`           |
| Xóa (kèm dọn ảnh, folder cloud)                       | `delete_project`         |
| Hàm phụ trợ dùng nội bộ (check trùng)                 | `check_project_conflict` |

**Quy tắc:**

- Bỏ hẳn tiền tố `logic_` — nó không mang thêm thông tin, chỉ để né trùng tên (đã giải quyết ở mục 0).
- Hàm phụ trợ (helper) không phải là entrypoint chính vẫn nên có tên rõ nghĩa, tránh tên chung chung như `check_conflict` khi codebase có nhiều model — đổi thành `check_project_conflict`.

---

## 3. Lớp Router — verb + subject đầy đủ, vì đây là "mặt tiền" API

Tên hàm router **map trực tiếp vào `operationId`** trong OpenAPI/Swagger. Nếu nhiều router đều đặt tên `create`, `get`, `delete`,... Swagger UI và các công cụ sinh SDK (`openapi-generator`, `orval`,...) sẽ bị đụng `operationId` hoặc phải tự thêm hậu tố → rất khó dùng ở phía frontend. Vì vậy **router luôn cần tên đầy đủ, không viết tắt**.

| HTTP method         | Việc          | Tên hàm                |
| ------------------- | ------------- | ---------------------- |
| POST `/`            | Tạo mới       | `create_project`       |
| GET `/{id}`         | Lấy 1 bản ghi | `get_project`          |
| GET `/`             | Lấy danh sách | `list_projects`        |
| PATCH `/{id}`       | Cập nhật text | `update_project_text`  |
| PATCH `/image/{id}` | Cập nhật ảnh  | `update_project_image` |
| PATCH `/sync/{id}`  | Đồng bộ       | `sync_project`         |
| DELETE `/{id}`      | Xóa           | `delete_project`       |

**Quy tắc phân biệt `get_` vs `list_`:**

- `get_` → trả về **1 bản ghi** (theo id).
- `list_` → trả về **danh sách/collection** (có phân trang).
- Đây là convention phổ biến trong REST API, giúp phân biệt ngay từ tên hàm mà không cần đọc response model.

---

## 4. Bảng so sánh tổng hợp (ví dụ module Project)

| Router                 | Service                                    | CRUD               |
| ---------------------- | ------------------------------------------ | ------------------ |
| `create_project`       | `create_project`                           | `create`           |
| `get_project`          | _(gọi crud trực tiếp nếu không cần logic)_ | `get_by_id`        |
| `list_projects`        | _(gọi crud trực tiếp nếu không cần logic)_ | `get_all`          |
| `update_project_text`  | `update_project_text`                      | `update_text_form` |
| `update_project_image` | `update_project_image`                     | `update_image`     |
| `sync_project`         | `sync_project`                             | `sync`             |
| `delete_project`       | `delete_project`                           | `delete`           |

Nhìn cột dọc: tên **tăng dần độ chi tiết** khi đi từ crud → service → router, đúng với việc mỗi layer thêm một lớp ngữ cảnh.

---
