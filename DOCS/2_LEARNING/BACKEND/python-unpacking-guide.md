# Guide: Unpacking trong Python (`*` và `**`)

> Ghi chú kỹ thuật — dùng để tham khảo khi viết service/crud layer trong dự án portfolio.

---

## 1. Vấn đề cần giải quyết

Khi có 1 dict chứa nhiều tham số, và cần gọi 1 hàm nhận từng tham số đó dưới dạng keyword argument, có 2 cách:

```python
cfg = {"skip": 0, "limit": 6, "sort_by": "sort_order", "order": "asc"}

# Cách 1: gọi tay từng key — dài, dễ sai, khó bảo trì
get_list(db, skip=cfg["skip"], limit=cfg["limit"], sort_by=cfg["sort_by"], order=cfg["order"])

# Cách 2: unpack bằng **
get_list(db, **cfg)
```

Hai dòng trên **hoàn toàn tương đương**. `**cfg` yêu cầu Python "bung" dict thành các `key=value` rồi truyền vào hàm.

**Điều kiện bắt buộc**: key trong dict phải trùng chính xác tên tham số của hàm. Nếu dict có key thừa không khớp tham số nào → `TypeError: unexpected keyword argument`.

---

## 2. Hai loại dấu `*` — đừng nhầm lẫn

| Ký hiệu | Dùng cho | Ý nghĩa |
|---|---|---|
| `*args` | Positional arguments | Gom nhiều giá trị rời thành 1 **tuple** |
| `**kwargs` | Keyword arguments | Gom nhiều `key=value` thành 1 **dict** |

Dấu `*`/`**` xuất hiện ở **2 ngữ cảnh khác nhau**, dễ gây nhầm lẫn nếu không phân biệt rõ:

### 2.1. Khi ĐỊNH NGHĨA hàm (gom lại — packing)

```python
def get_list(db, *args, **kwargs):
    print(args)    # tuple, vd: (0, 6)
    print(kwargs)  # dict, vd: {"sort_by": "id", "order": "asc"}
```

Ở đây, `*args`/`**kwargs` cho phép hàm **nhận số lượng tham số không cố định**.

### 2.2. Khi GỌI hàm (bung ra — unpacking)

```python
values = [0, 6]
cfg = {"sort_by": "id", "order": "asc"}

get_list(db, *values, **cfg)
# tương đương: get_list(db, 0, 6, sort_by="id", order="asc")
```

Ở đây, `*`/`**` làm điều **ngược lại** — bung 1 list/dict có sẵn thành các tham số rời để truyền vào hàm.

> **Ghi nhớ**: cùng ký hiệu `*`/`**`, nhưng ở định nghĩa hàm là "gom vào", ở lời gọi hàm là "bung ra".

---

## 3. `**` trong dict literal (không liên quan đến hàm)

`**` còn dùng để **merge nhiều dict** lại với nhau — không cần gọi hàm gì cả:

```python
base_config = {"skip": 0, "limit": 10}
override = {"limit": 6, "sort_by": "id"}

final_config = {**base_config, **override}
# {"skip": 0, "limit": 6, "sort_by": "id"}
```

Quy tắc: nếu key trùng nhau, **dict bên phải ghi đè dict bên trái** (giống thứ tự đọc trái → phải).

Ứng dụng thực tế: tạo config mặc định rồi override 1 vài field mà không sửa dict gốc:

```python
DEFAULT_CFG = {"skip": 0, "limit": 10, "sort_by": "id", "order": "asc"}

project_cfg = {**DEFAULT_CFG, "limit": 6}       # chỉ đổi limit
timeline_cfg = {**DEFAULT_CFG, "limit": 10}     # giữ nguyên
```

---

## 4. Ứng dụng trực tiếp vào dự án hiện tại

### 4.1. Service layer — gọi nhiều crud với config khác nhau

```python
# app/services/index.py

INDEX_QUERY_CONFIG = {
    "project":     {"skip": 0, "limit": 6,  "sort_by": "sort_order", "order": "asc"},
    "timeline":    {"skip": 0, "limit": 10, "sort_by": "sort_order", "order": "asc"},
    "achievement": {"skip": 0, "limit": 6,  "sort_by": "sort_order", "order": "asc"},
}

def get_index_data(db: Session) -> index_schema.Response:
    return index_schema.Response(
        my_info=info_crud.get_current(db),
        list_projects=project_crud.get_list(db, **INDEX_QUERY_CONFIG["project"]),
        list_timelines=timeline_crud.get_list(db, **INDEX_QUERY_CONFIG["timeline"]),
        list_achievements=achievement_crud.get_list(db, **INDEX_QUERY_CONFIG["achievement"]),
    )
```

Thêm tham số mới cho `get_list` (vd: `filter_by`) sau này → chỉ cần thêm key vào dict, **không phải sửa dòng gọi hàm**.

### 4.2. Router → Service — truyền query params từ FE xuống

Khi endpoint có phân trang thật (nhận query param từ client), Pydantic hoặc FastAPI thường trả về object/dict — unpacking giúp code gọn:

```python
@router.get("/projects", response_model=schemas.PaginationResponse)
def list_projects(
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "id",
    order: str = "asc",
    db: Session = Depends(get_db),
):
    query_params = {"skip": skip, "limit": limit, "sort_by": sort_by, "order": order}
    return project_crud.get_all(db, **query_params)
```

### 4.3. Pydantic — convert schema thành dict rồi unpack vào model

Pattern rất phổ biến khi tạo object mới từ schema:

```python
def create_project(db: Session, payload: schemas.ProjectCreate):
    new_project = Project(**payload.model_dump())
    db.add(new_project)
    db.commit()
    return new_project
```

`payload.model_dump()` chuyển Pydantic schema thành dict, `**` bung dict đó thành các keyword argument khớp với field của SQLAlchemy model `Project`.

---

## 5. Lỗi thường gặp

### 5.1. Key dict không khớp tên tham số

```python
cfg = {"take": 6}  # sai tên, hàm cần "limit"
get_list(db, **cfg)
# TypeError: get_list() got an unexpected keyword argument 'take'
```

**Cách phòng tránh**: đặt tên key trong config dict giống hệt tên tham số hàm, không viết tắt/đổi tên tùy hứng.

### 5.2. Trùng tham số khi unpack

```python
get_list(db, skip=0, **{"skip": 5, "limit": 10})
# TypeError: get_list() got multiple values for keyword argument 'skip'
```

Khi vừa truyền `skip=0` trực tiếp, vừa unpack dict có key `skip` → xung đột.

### 5.3. Dict thiếu key bắt buộc

```python
cfg = {"skip": 0, "limit": 6}  # thiếu sort_by, order
get_list(db, **cfg)
# TypeError: missing 2 required positional arguments: 'sort_by' and 'order'
```

**Cách phòng tránh**: cho hàm có giá trị mặc định (`sort_by: str = "id"`), hoặc đảm bảo dict luôn đủ field — có thể dùng `TypedDict` (mục 6) để IDE cảnh báo sớm.

---

## 6. Nâng cao (tùy chọn — không bắt buộc phải dùng ngay)

Nếu muốn Python/IDE tự kiểm tra cấu trúc dict config thay vì chỉ là `dict[str, Any]` thông thường, có thể khai báo `TypedDict`:

```python
from typing import TypedDict

class QueryConfig(TypedDict):
    skip: int
    limit: int
    sort_by: str
    order: str

INDEX_QUERY_CONFIG: dict[str, QueryConfig] = {
    "project": {"skip": 0, "limit": 6, "sort_by": "sort_order", "order": "asc"},
    ...
}
```

Lợi ích: nếu thiếu key hoặc sai kiểu dữ liệu, IDE báo lỗi ngay lúc viết code thay vì đợi runtime. Không bắt buộc cho dự án hiện tại, nhưng đáng cân nhắc khi số lượng config tăng lên.

---

## 7. Tóm tắt nhanh

| Cú pháp | Ngữ cảnh | Tác dụng |
|---|---|---|
| `def f(*args)` | Định nghĩa hàm | Gom nhiều positional arg thành tuple |
| `def f(**kwargs)` | Định nghĩa hàm | Gom nhiều keyword arg thành dict |
| `f(*a_list)` | Gọi hàm | Bung list/tuple thành positional arg |
| `f(**a_dict)` | Gọi hàm | Bung dict thành keyword arg |
| `{**d1, **d2}` | Dict literal | Merge dict, key sau ghi đè key trước |

**Nguyên tắc chọn dùng**: mỗi khi thấy mình đang gõ lặp lại `dict["key1"]`, `dict["key2"]`... để truyền vào cùng 1 hàm → đó là dấu hiệu nên dùng `**dict` thay thế.
