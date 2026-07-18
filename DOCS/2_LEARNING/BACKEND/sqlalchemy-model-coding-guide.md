# Hướng dẫn viết Model (SQLAlchemy) cho người mới bắt đầu

> Tài liệu này tập trung **100% vào việc viết code Model** — kiểu dữ liệu, cách khai báo cột, cách tối ưu, các pattern hay dùng. Phần Alembic/migration đã có ở tài liệu riêng nên không nhắc lại ở đây.

---

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

## NOTE: Lựa chọn Array hay JSON

### - Dùng `ARRAY` khi nào

```python
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String

tags: Mapped[list[str]] = mapped_column(ARRAY(String(50)), default=list)
scores: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=list)
```

Điều kiện để dùng được `ARRAY`: **tất cả phần tử phải cùng một kiểu** (toàn `str`, hoặc toàn `int`...). Không lưu được list chứa object/dict phức tạp hay các phần tử khác kiểu nhau.

### - Khác nhau giữa `ARRAY` và `JSON`

| Tiêu chí         | `ARRAY`                                                                  | `JSON` / `JSONB`                                                       |
| ---------------- | ------------------------------------------------------------------------ | ---------------------------------------------------------------------- |
| Cấu trúc dữ liệu | Chỉ là 1 mảng phẳng, cùng kiểu                                           | Cây lồng nhau tùy ý (dict trong list trong dict...)                    |
| Tốc độ đọc/ghi   | Nhanh hơn, vì Postgres lưu ở dạng native array, không cần parse          | Chậm hơn một chút, đặc biệt là `JSON` thường (không phải `JSONB`)      |
| Query bên trong  | Có toán tử riêng khá tiện: `ANY()`, `@>` (contains), `array_length()`... | `JSONB` cũng query được nhưng cú pháp phức tạp hơn (`->`, `->>`, `@>`) |
| Index            | Dùng GIN index để tìm phần tử trong mảng hiệu quả                        | Cũng dùng GIN index nhưng cho toàn bộ cấu trúc JSON                    |
| Tính linh hoạt   | Cứng — thêm field mới nghĩa là phải đổi kiểu cột                         | Rất linh hoạt — có thể thêm field mà không cần migration               |
| Hỗ trợ DB        | **Chỉ có ở PostgreSQL**, không có ở MySQL/SQLite                         | Có ở nhiều DB hơn (MySQL cũng có JSON)                                 |
| Portable code    | Khóa cứng vào Postgres                                                   | JSON phổ biến hơn, dễ đổi DB sau này hơn                               |

### - Quy tắc chọn nhanh

- List các giá trị đơn giản, cùng kiểu, không lồng nhau → **`ARRAY`** (nếu chắc chắn dùng Postgres luôn, không định đổi DB).
- Danh sách các object có nhiều field, hoặc cấu trúc không cố định → **`JSONB`**.
- Nếu list đó thực ra là **quan hệ 1-nhiều với một entity khác** (ví dụ: 1 User có nhiều Address, mỗi Address có id/street/city riêng) → **đừng dùng ARRAY hay JSON**, hãy tách hẳn thành bảng riêng + `relationship`. Đây là lỗi khá phổ biến: nhét cả list object phức tạp vào JSON cho "tiện" thay vì thiết kế bảng đúng chuẩn quan hệ.

Ví dụ: nếu Project có field `tech_stack` kiểu `["React", "FastAPI", "PostgreSQL"]` — đây là ví dụ hoàn hảo để dùng `ARRAY(String)`, vì toàn string đơn giản, không cần field phụ nào khác. Nhưng nếu sau này bạn muốn mỗi tech có thêm icon, version... thì lúc đó nên tách thành bảng `project_technologies` riêng.

## 3. `Mapped[Type | None]` và `nullable` — cặp đôi hay bị hiểu sai

```python
# Bắt buộc phải có giá trị
full_name: Mapped[str] = mapped_column(String(100))

# Có thể để trống (NULL trong DB)
full_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
```

Quy tắc: khi kiểu Python có `| None`, gần như chắc chắn phải đi kèm `nullable=True`. SQLAlchemy 2.0 style thường **suy luận được** `nullable` từ `Mapped[Type | None]`, nhưng viết tường minh (`nullable=True`) vẫn là thói quen tốt cho người mới — dễ đọc, dễ review, tránh nhầm lẫn giữa "optional ở tầng Python" và "optional ở tầng DB".

**Lỗi hay gặp:** khai báo `Mapped[str | None]` nhưng quên `nullable=True` → SQLAlchemy có thể tự suy ra đúng, nhưng nếu quên và code cũ hơn hoặc cấu hình khác, cột lại bị tạo là `NOT NULL` → insert `None` sẽ lỗi ở tầng database, không phải lỗi Python, nên rất khó debug với người mới.

---

## 4. Ngày giờ (`DateTime`) — luôn nghĩ đến timezone

```python
from sqlalchemy import DateTime
from datetime import datetime, timezone

created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    default=lambda: datetime.now(timezone.utc),
)
```

Ba điều cần nhớ:

1. **Luôn set `timezone=True`** cho `DateTime`, trừ khi bạn chắc chắn 100% không bao giờ cần so sánh giờ giữa các múi giờ khác nhau (thực tế web app hầu như luôn cần).
2. Dùng `datetime.now(timezone.utc)` thay vì `datetime.utcnow()` (hàm này đã bị coi là legacy vì trả về datetime "naive" — không gắn thông tin timezone).
3. Với cột `updated_at`, dùng thêm `onupdate=` để tự động cập nhật mỗi lần row được `UPDATE`:

```python
updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    default=lambda: datetime.now(timezone.utc),
    onupdate=lambda: datetime.now(timezone.utc),
)
```

**Phân biệt `default` vs `server_default`:**

- `default=...` → Python tính giá trị trước khi gửi câu lệnh `INSERT` xuống DB.
- `server_default=...` → giao cho chính PostgreSQL tính (ví dụ `server_default=func.now()`).

Dùng `server_default` khi có khả năng dữ liệu được insert trực tiếp bằng công cụ khác ngoài code Python của bạn (ví dụ seed script SQL thuần) — khi đó `default` ở tầng Python sẽ không có tác dụng vì Python không tham gia vào câu lệnh đó.

---

## 5. Enum — khi nào dùng, cách viết cho gọn

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

## 6. JSON / JSONB — khi dữ liệu không có cấu trúc cố định

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

## 7. Index — thêm ở đâu, khi nào

```python
email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
```

Nguyên tắc thêm `index=True`:

- Cột thường xuyên xuất hiện trong `WHERE`, `ORDER BY`, hoặc `JOIN` → nên có index.
- Cột `unique=True` thường nên đi kèm `index=True` (một số DB tự tạo index khi unique, nhưng khai báo tường minh vẫn tốt cho rõ ràng).
- **Đừng index tất cả mọi cột** — mỗi index tăng tốc độ đọc (SELECT) nhưng làm chậm ghi (INSERT/UPDATE) vì DB phải cập nhật cả index mỗi lần ghi dữ liệu.

Index nhiều cột cùng lúc (composite index) khi bạn thường query kết hợp nhiều điều kiện:

```python
from sqlalchemy import Index

class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        Index("ix_orders_user_status", "user_id", "status"),
    )
```

---

## 8. Giá trị mặc định — 3 cách và khi nào dùng cách nào

| Cách                        | Ví dụ                                        | Khi dùng                                             |
| --------------------------- | -------------------------------------------- | ---------------------------------------------------- |
| `default=giá_trị_tĩnh`      | `default=True`                               | Giá trị cố định, không đổi                           |
| `default=hàm_hoặc_lambda`   | `default=lambda: datetime.now(timezone.utc)` | Giá trị cần tính tại thời điểm insert, tính ở Python |
| `server_default=func.xxx()` | `server_default=func.now()`                  | Cần DB tự tính, không phụ thuộc code Python          |

**Lỗi hay gặp với người mới:** viết `default=datetime.now(timezone.utc)` (có gọi hàm, thiếu `lambda`) thay vì `default=lambda: datetime.now(timezone.utc)`. Nếu thiếu `lambda`, giá trị được tính **một lần duy nhất khi module Python được load**, khiến mọi row insert sau đó dùng chung một mốc thời gian cố định — một lỗi rất khó nhận ra vì code không báo lỗi gì cả, chỉ sai dữ liệu.

---

## 9. Một số pattern nên áp dụng ngay từ đầu

### 9.1 Base có sẵn các cột chung (mixin)

Thay vì lặp lại `id`, `created_at`, `updated_at` ở mọi model, tách ra một class dùng chung:

```python
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    ...
```

Giúp mọi model tự động có `created_at`/`updated_at` nhất quán mà không copy-paste.

### 9.2 Soft delete thay vì xóa thật

Nếu dữ liệu quan trọng (đơn hàng, bài viết), cân nhắc không xóa thật khỏi DB:

```python
is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
```

Query bình thường sẽ luôn lọc thêm `WHERE is_deleted = False`. Cách này giữ được lịch sử dữ liệu, tránh mất dữ liệu do xóa nhầm.

### 9.3 `__repr__` cho dễ debug

```python
class User(Base):
    ...
    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"
```

Không ảnh hưởng gì đến database, nhưng giúp việc `print(user)` khi debug dễ đọc hơn nhiều so với mặc định `<app.models.user.User object at 0x7f...>`.

---

## 10. Những lỗi tối ưu/thiết kế người mới hay mắc khi VIẾT MODEL

1. **Dùng `String(255)` cho mọi cột chuỗi mà không suy nghĩ** — nên đặt độ dài đúng với nhu cầu thực tế (email 255 là hợp lý, nhưng mã quốc gia thì không cần quá 5).
2. **Dùng `Float` để lưu tiền** — luôn dùng `Numeric(precision, scale)` cho tiền tệ để tránh sai số làm tròn.
3. **Không set `nullable` tường minh**, để mặc định rồi bất ngờ khi insert thiếu field bị lỗi (hoặc ngược lại, quên ràng buộc NOT NULL nên dữ liệu rác lọt vào).
4. **Lạm dụng JSON column** để né việc thiết kế bảng — về lâu dài rất khó query, khó thêm ràng buộc, khó tối ưu.
5. **Không đặt `default` cho cột boolean/status**, khiến giá trị `NULL` xuất hiện ngoài ý muốn và logic `if is_active:` xử lý sai.
6. **Thiếu index cho các cột dùng để tra cứu/join thường xuyên**, làm query chậm dần khi dữ liệu lớn lên dù logic code hoàn toàn đúng.
7. **Không tách `TimestampMixin` hoặc pattern dùng chung**, dẫn đến code lặp lại nhiều và dễ quên `onupdate` ở model nào đó.
8. **Đặt tên bảng/cột không nhất quán** (chỗ thì số ít, chỗ thì số nhiều; chỗ `snake_case`, chỗ `camelCase`) — nên thống nhất `snake_case` số nhiều cho tên bảng (`users`, `orders`) ngay từ đầu dự án.

---

## 11. Checklist khi viết một Model mới

- [ ] Tên bảng (`__tablename__`) đã theo đúng convention của dự án (snake_case, số nhiều) chưa?
- [ ] Mỗi cột đã chọn đúng kiểu SQL hẹp nhất, phù hợp nhu cầu (không mặc định `String(255)`/`Text` cho mọi thứ)?
- [ ] Cột nào có thể `NULL` đã khai báo `Mapped[Type | None]` + `nullable=True` chưa?
- [ ] Cột tiền tệ dùng `Numeric`, không dùng `Float`?
- [ ] Cột ngày giờ có `timezone=True` và dùng `datetime.now(timezone.utc)` (qua `lambda`) chưa?
- [ ] Cột cần tra cứu/join thường xuyên đã có `index=True` chưa?
- [ ] Có cột nào nên tách `TimestampMixin` dùng chung không?
- [ ] Enum (nếu có) đã kế thừa `str` và đặt `name=` cho `SAEnum` chưa?

---

## 12. Tài liệu tra cứu thêm

- SQLAlchemy Column & Data Types: https://docs.sqlalchemy.org/en/20/core/type_basics.html
- SQLAlchemy ORM Declarative Mapping (2.0 style): https://docs.sqlalchemy.org/en/20/orm/declarative_styles.html
- PostgreSQL JSONB: https://www.postgresql.org/docs/current/datatype-json.html
