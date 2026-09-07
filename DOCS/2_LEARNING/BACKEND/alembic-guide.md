# `🎯 Note về Model & Alembic trong Backend`

> Tài liệu này giải thích **bản chất** của Model (SQLAlchemy) và Alembic (migration tool),

## 1. Vấn đề

Khi code backend, bạn cần:

1. Định nghĩa **cấu trúc dữ liệu** trong Python (class) → đây là **Model**.
2. Biến cấu trúc đó thành **bảng thật** trong PostgreSQL → đây là việc **Migration**, và Alembic là công cụ làm việc đó.

Nói ngắn gọn:

- **Model** = "tôi muốn dữ liệu trông như thế nào" (khai báo trong code).
- **Alembic** = "hãy tạo/sửa bảng trong database cho khớp với khai báo đó" (thực thi).

Hai thứ này tách biệt nhau. Sửa Model không tự động sửa database — bạn phải chạy Alembic để đồng bộ.

---

## 2. SQLAlchemy Model là gì?

SQLAlchemy là **ORM** (Object-Relational Mapping) — cầu nối giữa class Python và bảng SQL.

### 2.1 Base class

Mọi model đều kế thừa từ một `Base` dùng chung trong toàn dự án:

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

`Base` này phải được **import và biết đến** ở nơi Alembic đọc metadata (sẽ nói ở phần 3). Nếu một Model không kế thừa từ đúng `Base`, Alembic sẽ **không thấy** nó.

### 2.2 Định nghĩa một Model

```python
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
```

Ý nghĩa từng phần:

- `__tablename__`: tên bảng thật trong PostgreSQL.
- `Mapped[type]`: kiểu dữ liệu Python tương ứng — giúp IDE gợi ý, type-check.
- `mapped_column(...)`: khai báo chi tiết cột (kiểu SQL, ràng buộc, mặc định...).
- `primary_key=True`, `unique=True`, `index=True`: ràng buộc quen thuộc trong SQL.

### 2.3 Quan hệ giữa các bảng (Relationship)

Ví dụ 1-nhiều (một User có nhiều Project):

```python
class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    owner: Mapped["User"] = relationship(back_populates="projects")
```

```python
class User(Base):
    ...
    projects: Mapped[list["Project"]] = relationship(back_populates="owner")
```

- `ForeignKey("users.id")`: ràng buộc khóa ngoại thật sự ở tầng database.
- `relationship(...)`: chỉ tồn tại ở tầng Python, giúp bạn viết `user.projects` thay vì tự query join — **không** tạo cột nào trong DB.

**Lưu ý quan trọng:** `ForeignKey` là thứ ảnh hưởng đến schema (Alembic sẽ tạo migration cho nó). `relationship` chỉ là tiện ích Python, Alembic **không cần quan tâm** đến nó.

---

## 3. Alembic

Alembic là công cụ **quản lý phiên bản schema database**, tương tự Git nhưng cho cấu trúc bảng.

### 3.1 Vì sao không tự chạy `Base.metadata.create_all()` cho xong?

`create_all()` chỉ tạo bảng nếu **chưa tồn tại**. Nó không biết cách:

- Sửa một cột đã tồn tại (đổi kiểu, thêm ràng buộc).
- Xóa cột.
- Đổi tên bảng/cột.
- Rollback nếu thay đổi bị lỗi.

Alembic giải quyết đúng vấn đề đó bằng cách lưu **lịch sử thay đổi schema** dưới dạng các file "revision", mỗi file là một bước thay đổi có thể tiến (`upgrade`) hoặc lùi (`downgrade`).

### 3.2 Cấu trúc thư mục Alembic

```
alembic/
├── versions/          # chứa các file migration (mỗi file = 1 revision)
├── env.py             # cấu hình cách Alembic kết nối DB và đọc Model
└── script.py.mako      # template để sinh file migration mới
alembic.ini             # cấu hình chung (connection string, logging...)
```

### 3.3 File `env.py` — phần hay bị bỏ sót

Đây là nơi Alembic biết **Model của bạn trông như thế nào**. Bạn cần import đúng `Base` chứa tất cả Model:

```python
from app.db.base import Base  # Base chứa toàn bộ metadata của các Model
target_metadata = Base.metadata
```

Nếu một Model mới được tạo nhưng **không được import** ở đâu đó dẫn đến `Base`, Alembic autogenerate sẽ **không thấy** model đó → đây là lỗi rất phổ biến với người mới.

### 3.4 Quy trình làm việc thực tế (workflow)

```
1. Sửa/thêm Model trong code (class Python)
        ↓
2. alembic revision --autogenerate -m "add users table"
        ↓
3. Mở file migration vừa tạo trong versions/, ĐỌC LẠI kỹ
        ↓
4. alembic upgrade head   → áp dụng thay đổi vào database thật
```

Các lệnh cần nhớ:

| Lệnh                                           | Ý nghĩa                                               |
| ---------------------------------------------- | ----------------------------------------------------- |
| `alembic revision --autogenerate -m "message"` | So sánh Model hiện tại với DB, tự sinh file migration |
| `alembic upgrade head`                         | Áp dụng tất cả migration chưa chạy lên DB             |
| `alembic downgrade -1`                         | Lùi lại 1 bước migration gần nhất                     |
| `alembic current`                              | Xem DB đang ở revision nào                            |
| `alembic history`                              | Xem toàn bộ lịch sử migration                         |

### 3.5 Vì sao PHẢI đọc lại file autogenerate, không được tin tưởng 100%?

`--autogenerate` chỉ là **gợi ý dựa trên so sánh**, nó thường bỏ sót hoặc hiểu sai:

- Đổi tên cột → Alembic hiểu nhầm thành "xóa cột cũ + thêm cột mới" (mất dữ liệu nếu chạy thẳng).
- Một số thay đổi ràng buộc (server_default, check constraint) không phải lúc nào cũng detect đúng.
- Thay đổi kiểu dữ liệu phức tạp (ví dụ Enum) cần chỉnh tay.

→ Luôn mở file trong `versions/` và đọc phần `upgrade()` / `downgrade()` trước khi chạy thật.

---

## 4. Một migration file trông như thế nào?

```python
"""add users table

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-07-15
"""
from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e5f6"
down_revision = None

def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, index=True),
        sa.Column("hashed_password", sa.String(255)),
    )

def downgrade():
    op.drop_table("users")
```

- `revision` / `down_revision`: tạo thành một **chuỗi liên kết** (giống linked list) để Alembic biết thứ tự chạy.
- `upgrade()`: thao tác khi tiến lên phiên bản này.
- `downgrade()`: thao tác ngược lại — **bắt buộc viết đúng**, vì đây là "nút undo" của bạn khi cần rollback.

---
