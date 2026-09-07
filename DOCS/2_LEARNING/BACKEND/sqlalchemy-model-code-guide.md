# `🎯 Note về xử viết Model (SQLAlchemy)`

> Tài liệu này tập trung **100% vào việc viết code Model** — kiểu dữ liệu, cách khai báo cột, cách tối ưu, các pattern hay dùng.

## 1. Cấu trúc một Model "chuẩn" trông như thế nào?

```python
from datetime import datetime
from sqlalchemy import String, Boolean, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )
```

Nhìn qua thì rối, nhưng thực ra chỉ có vài "khối" lặp đi lặp lại: **kiểu Python** → **kiểu SQL** → **ràng buộc**. Phần dưới sẽ bóc tách từng khối.

---

## 2. Bảng tra cứu kiểu dữ liệu (loại nào dùng khi nào)

| Muốn lưu gì                                          | Kiểu Python (`Mapped[...]`) | Kiểu SQL nên dùng                             | Ghi chú                                                             |
| ---------------------------------------------------- | --------------------------- | --------------------------------------------- | ------------------------------------------------------------------- |
| Số nguyên (id, số lượng)                             | `int`                       | `Integer` (mặc định, thường không cần ghi rõ) | Dùng `BigInteger` nếu số có thể rất lớn (ví dụ view count)          |
| Chuỗi ngắn, có giới hạn (email, tên, slug)           | `str`                       | `String(n)`                                   | Luôn đặt giới hạn độ dài hợp lý, đừng để mặc định quá lớn           |
| Chuỗi dài, không giới hạn (nội dung bài viết, mô tả) | `str`                       | `Text`                                        | Không cần (và không nên) set độ dài cho `Text`                      |
| Đúng/sai                                             | `bool`                      | `Boolean`                                     | Luôn đặt `default=` rõ ràng, đừng để `None` ngầm định               |
| Ngày giờ                                             | `datetime`                  | `DateTime` (nên thêm `timezone=True`)         | Xem mục 4 về timezone                                               |
| Chỉ ngày (không giờ)                                 | `date`                      | `Date`                                        | Dùng cho ngày sinh, ngày hết hạn...                                 |
| Số thập phân (giá tiền)                              | `Decimal`                   | `Numeric(precision, scale)`                   | **Không dùng `Float` cho tiền tệ** — sai số làm tròn                |
| Số thực khoa học (tọa độ, đo lường)                  | `float`                     | `Float`                                       | Chấp nhận sai số nhỏ                                                |
| Danh sách giá trị cố định                            | `Enum` (Python enum)        | `Enum` (SQLAlchemy)                           | Xem mục 5                                                           |
| Dữ liệu dạng JSON linh hoạt                          | `dict` / `list`             | `JSON` hoặc `JSONB` (Postgres)                | Dùng khi schema không cố định, xem mục 6                            |
| File nhị phân nhỏ                                    | `bytes`                     | `LargeBinary`                                 | Thường nên lưu file ở ngoài (S3, disk) và chỉ lưu path/URL trong DB |
| Giá trị có thể `NULL`                                | `Type / None`               | thêm `nullable=True`                          | Xem mục 3                                                           |

**Nguyên tắc chọn kiểu:** chọn kiểu SQL **hẹp nhất** đáp ứng đủ nhu cầu. Không dùng `Text` cho một cột chỉ chứa mã quốc gia 2 ký tự; không dùng `String(255)` mặc định cho mọi thứ mà không suy nghĩ.

---

<blockquote>

### Lựa chọn Array hay JSON

- Dùng `ARRAY` khi nào

```python
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String

tags: Mapped[list[str]] = mapped_column(ARRAY(String(50)), default=list)
scores: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=list)
```

Điều kiện để dùng được `ARRAY`: **tất cả phần tử phải cùng một kiểu** (toàn `str`, hoặc toàn `int`...). Không lưu được list chứa object/dict phức tạp hay các phần tử khác kiểu nhau.

### - Ví dụ:

- List các giá trị đơn giản, cùng kiểu, không lồng nhau → **`ARRAY`** (nếu chắc chắn dùng Postgres luôn, không định đổi DB).
- Danh sách các object có nhiều field, hoặc cấu trúc không cố định → **`JSONB`**.
- Nếu list đó thực ra là **quan hệ 1-nhiều với một entity khác** (ví dụ: 1 User có nhiều Address, mỗi Address có id/street/city riêng) → **đừng dùng ARRAY hay JSON**, hãy tách hẳn thành bảng riêng + `relationship`. Đây là lỗi khá phổ biến: nhét cả list object phức tạp vào JSON cho "tiện" thay vì thiết kế bảng đúng chuẩn quan hệ.

</blockquote>

## 3. JSON / JSONB — khi dữ liệu không có cấu trúc cố định

```python
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import JSON

# Ưu tiên JSONB nếu chắc chắn dùng PostgreSQL
metadata: Mapped[dict] = mapped_column(JSONB, default=dict)

# Dùng JSON nếu muốn code không phụ thuộc riêng vào Postgres
settings: Mapped[dict] = mapped_column(JSON, default=dict)
```

- `JSONB` (chỉ có ở Postgres) lưu ở dạng nhị phân, cho phép **đánh index và query bên trong JSON** hiệu quả hơn `JSON` thường.
- Chỉ nên dùng JSON/JSONB cho dữ liệu thực sự không có cấu trúc rõ ràng (ví dụ: cấu hình tùy biến, metadata linh tinh). Nếu dữ liệu có cấu trúc rõ và cần query/lọc thường xuyên theo từng field → nên tách thành cột riêng hoặc bảng riêng, đừng nhét hết vào JSON cho "tiện".

---

## 4. `Mapped[Type | None]` và `nullable`

```python
# Bắt buộc phải có giá trị
full_name: Mapped[str] = mapped_column(String(100))

# Có thể để trống (NULL trong DB)
full_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
```

Khi kiểu Python có `| None`, gần như chắc chắn phải đi kèm `nullable=True`. SQLAlchemy 2.0 style thường **suy luận được** `nullable` từ `Mapped[Type | None]`, nhưng viết tường minh (`nullable=True`) vẫn là thói quen tốt cho người mới — dễ đọc, dễ review.

---

## 5. Ngày giờ (`DateTime`)

> Đọc chi tiết hơn tại [`sqlalchemy-model-time.md`](./sqlalchemy-model-time.md)

---

## 6. Enum

Dùng `Enum` khi một cột chỉ nhận một tập giá trị cố định, biết trước (trạng thái đơn hàng, vai trò user...).

```python
import enum
from sqlalchemy import Enum as SAEnum

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[OrderStatus] = mapped_column(
        SAEnum(OrderStatus, name="order_status"),
        default=OrderStatus.PENDING,
    )
```

Lưu ý quan trọng:

- Cho enum kế thừa cả `str` (`class OrderStatus(str, enum.Enum)`) — nhờ vậy khi serialize ra JSON (ví dụ trả response API), giá trị tự nhiên là string, không cần convert tay.
- Luôn đặt `name="..."` cho `SAEnum` — Postgres tạo enum như một **kiểu dữ liệu riêng** (custom type) ở tầng DB, cần tên để quản lý/migration về sau.
- Thêm giá trị mới vào enum sau này cần migration riêng (ALTER TYPE), phức tạp hơn một chút so với thêm giá trị cho cột thường — nên cân nhắc nếu tập giá trị có khả năng thay đổi thường xuyên, có thể cột `String` + validate ở tầng code sẽ linh hoạt hơn.

---

## 7. Index

Thuộc tính `index=True` trong SQLAlchemy dùng để tự động tạo một **chỉ mục (database index)** cho cột dữ liệu đó trong cơ sở dữ liệu.

<blockquote>

### Tác dụng của index

- **Tăng tốc độ tìm kiếm:** Giúp cơ sở dữ liệu tìm dữ liệu cực kỳ nhanh chóng dựa trên cột đó, tránh việc quét toàn bộ bảng (_full table scan_).
- **Hỗ trợ sắp xếp và lọc:** Tối ưu hóa hiệu năng cho các câu lệnh chứa điều kiện `WHERE`, sắp xếp `ORDER BY`, hoặc kết nối bảng `JOIN`.

### Tại sao lại cần có index:

- **Giải quyết bài toán dữ liệu lớn:** Khi bảng có từ hàng nghìn đến hàng triệu dòng, truy vấn không có chỉ mục sẽ làm hệ thống phản hồi rất chậm.
- **Đồng bộ mã nguồn và cơ sở dữ liệu:** Khai báo trực tiếp trong model Python giúp bạn không cần viết lệnh SQL thủ công như `CREATE INDEX`. SQLAlchemy sẽ tự động cấu hình khi khởi tạo bảng.

### Nhược điểm cần lưu ý:

- **Tốn dung lượng:** Chỉ mục yêu cầu không gian lưu trữ riêng trên ổ cứng.
- **Chậm thao tác ghi:** Khi thêm (`INSERT`), sửa (`UPDATE`), hoặc xóa (`DELETE`), hệ thống phải cập nhật lại cấu trúc chỉ mục, làm tăng thời gian xử lý.
</blockquote>

---

## 8. Một số pattern nên áp dụng ngay từ đầu

### 8.1 Soft delete thay vì xóa thật

Nếu dữ liệu quan trọng (đơn hàng, bài viết), cân nhắc không xóa thật khỏi DB:

```python
is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
```

Query bình thường sẽ luôn lọc thêm `WHERE is_deleted = False`. Cách này giữ được lịch sử dữ liệu, tránh mất dữ liệu do xóa nhầm.

### 8.2 `__repr__` cho dễ debug

```python
class User(Base):
    ...
    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"
```

Không ảnh hưởng gì đến database, nhưng giúp việc `print(user)` khi debug dễ đọc hơn nhiều so với mặc định `<app.models.user.User object at 0x7f...>`.

---
