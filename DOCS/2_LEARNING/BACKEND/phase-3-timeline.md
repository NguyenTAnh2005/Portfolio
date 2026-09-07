## `🎯 Note Timeline + Upload ảnh qua Cloudinary`

## 1. Luồng hoạt động tổng quan

Ví dụ: Admin tạo mới 1 Timeline kèm ảnh.

```
[Admin - Frontend]
  1. Chọn file ảnh từ input type="file"
  2. Điền các field text khác (title, organization, desc, start_end, sort_order...)
  3. Gom tất cả vào FormData (KHÔNG dùng JSON, vì có file binary bên trong)
  4. Gửi POST, header "multipart/form-data"
        ↓
[Backend - FastAPI]
  5. Endpoint tách request thành:
     - field text  → Form(...)
     - file ảnh    → UploadFile
  6. Gọi cloudinary.uploader.upload(file) → Cloudinary trả về:
       - secure_url  (link https để hiển thị)
       - public_id   (mã định danh ảnh trên Cloudinary, dùng để xóa/update sau)
  7. Backend tạo record Timeline trong PostgreSQL:
       - các field text
       - img_url = secure_url
       - img_public_id = public_id
  8. Trả response về Frontend (bao gồm cả ảnh vừa tạo)
        ↓
[Frontend]
  9. Nhận response, cập nhật UI
```

**Khi update ảnh:** upload ảnh mới trước → cập nhật DB thành công → mới `destroy()` ảnh cũ trên Cloudinary (không fail cả request nếu bước dọn rác này lỗi, chỉ log warning — DB đã commit rồi).

**Khi xóa record:** tương tự, nên `destroy(public_id)` để dọn ảnh Cloudinary trước khi xóa record trong DB.

---

## 2. Vì sao phải tách `Form(...)` và `UploadFile` riêng?

Vì bản chất `multipart/form-data` khác hoàn toàn JSON.

- **JSON:** toàn bộ dữ liệu là 1 khối text có cấu trúc → FastAPI parse thẳng vào 1 Pydantic model qua `Body(...)`.
- **multipart/form-data:** request chia thành nhiều "phần" (parts) riêng biệt — phần là text, phần là file nhị phân. Giống 1 bưu kiện nhiều ngăn, mỗi ngăn 1 kiểu dữ liệu.

→ FastAPI không thể dùng 1 Pydantic model để nhận hết như JSON. Nó cần biết rõ field nào là `Form` (text), field nào là `File`/`UploadFile` (binary) để đọc đúng kiểu.

```python
@router.post("/timelines")
def create_timeline(
    title: str = Form(...),
    organization: str = Form(...),
    start_date: date = Form(...),
    image: UploadFile = File(...)
):
    ...
```

`Form(...)` = "lấy field text này từ form data". `UploadFile = File(...)` = "field này là file, đọc như file object (có `.file`, `.filename`, `.content_type`)".

---

## 3. So sánh Info (JSON, không ảnh) vs Timeline (multipart, có ảnh)

### Router

**Info** — nhận thẳng 1 Pydantic model qua body JSON:

```python
def update_info(info_id: int, update_data: InfoUpdate, db: Session = Depends(...)):
    info = update_info_by_id(db=db, target_info_id=info_id, update_data=update_data)
```

FastAPI tự parse JSON → Pydantic model, router không cần làm gì thêm ngoài gọi CRUD.

**Timeline** — không thể làm vậy vì multipart không map thẳng vào 1 Pydantic model được. Router phải làm 2 việc tuần tự: (1) upload ảnh trước, (2) mới gọi CRUD với url/public_id dạng string.

→ Khác biệt cốt lõi: **router Timeline "dày" hơn** vì gánh thêm bước gọi service ngoài (Cloudinary) trước khi đụng DB. Info không có bước ngoại vi này nên router mỏng, chỉ orchestrate.

### CRUD

Cả 2 CRUD giống nhau về triết lý: **chỉ biết làm việc với DB, không biết gì về nguồn gốc dữ liệu.**

- CRUD Timeline **không bao giờ nhận `UploadFile`** — chỉ nhận `img_url`/`img_public_id` dạng string thuần, y hệt như nhận `title: str`. Điểm mấu chốt: **CRUD không bao giờ nên biết Cloudinary tồn tại.**

### Bảng tóm tắt

|                       | Info                                   | Timeline/Project                                        |
| --------------------- | -------------------------------------- | ------------------------------------------------------- |
| Body request          | JSON thuần                             | multipart/form-data                                     |
| Router nhận           | 1 Pydantic model                       | `Form(...)` rời + `UploadFile` rời                      |
| Bước phụ trong router | Không có                               | Gọi Cloudinary upload/destroy trước khi đụng DB         |
| CRUD nhận gì          | Pydantic object                        | String (url, public_id) — không bao giờ nhận UploadFile |
| Độ phức tạp CRUD      | Như nhau — chỉ là gán field vào object |

---

## 4. `UploadFile`: Tìm hiểu thêm bên ngoài.

## 5. `Lỗi 422 khi field rỗng qua Form`

### 7.1. FastAPI xử lý tham số route theo thứ tự nào

Khi request tới `PUT /{timeline_id}`:

1. Đọc raw multipart form data từ request.
2. Với **mỗi tham số** trong signature của hàm route, lấy field tương ứng trong form rồi **validate qua Pydantic** theo type annotation đã khai (`Optional[int]`, `Optional[UploadFile]`...).
3. Tham số nào fail validate → gom lỗi, trả về **422 ngay**, **không gọi vào thân hàm route nữa**.
4. Chỉ khi tất cả tham số pass thì FastAPI mới thực sự gọi hàm route.

→ Lỗi `int_parsing` / `Expected UploadFile` xảy ra ở **bước 3**, tức trước khi dòng code đầu tiên trong thân hàm chạy. Sửa logic bên trong thân hàm (như trong `parse_field_text_to_pydantic_class`) là **vô ích** vì hàm đó chưa từng được gọi tới khi lỗi xảy ra.

### 7.2. Vì sao `Optional[int] = Form(None)` không cứu được chuỗi rỗng `""`

`= Form(None)` chỉ có nghĩa: "nếu client **không gửi** field này lên thì mặc định `None`". Nó **không xử lý** trường hợp client gửi field với giá trị rỗng.

Swagger UI, khi để trống ô input, vẫn **gửi field đó lên** với value `""` — không lược bỏ khỏi multipart body. FastAPI thấy field có mặt, giá trị `""`, thử ép kiểu `int("")` theo annotation `int` → lỗi.

→ `Form(None)` là **default value khi field vắng mặt**, không phải **validator xử lý giá trị rỗng**. Hai khái niệm khác nhau.

### 7.3. Vì sao `img_file` lỗi `Expected UploadFile, received: str`

Tương tự — khi không chọn file, Swagger vẫn gửi field `img_file` lên dạng text rỗng `""` chứ không bỏ hẳn phần file khỏi multipart. FastAPI mong nhận `UploadFile` (object có `.filename`, `.file`...) nhưng nhận `str` → sai kiểu → lỗi validate.

**Cách xử lý (đã áp dụng trong code hiện tại):** khai `Union[UploadFile, str, None]` — nói với FastAPI "field này có thể là UploadFile, hoặc str, hoặc None, đừng ép cứng chỉ UploadFile". Nhờ vậy không bị reject ở bước validate; việc phân biệt "đây có phải file thật hay không" tự làm bằng code **sau khi** đã lọt qua validate:

```python
img_file: Union[UploadFile, str, None] = File(None)
...
if isinstance(img_file, str) or (img_file and not img_file.filename):
    img_file = None
```

### 7.4. Cách giải quyết field số (`sort_order`) — 2 hướng

**Hướng A — `BeforeValidator` (Pydantic v2):** chèn 1 hàm chạy **trước khi** Pydantic ép kiểu theo annotation gốc.

```
raw value ""  → BeforeValidator (empty_str_to_none): "" → None  → ép kiểu Optional[int]: None hợp lệ
```

Không có `BeforeValidator` thì: `raw "" → ép kiểu Optional[int]: int("") → LỖI` ngay.

Ưu điểm: gọn, khai 1 lần dùng lại nhiều nơi, lỗi báo tự động qua Pydantic (422 chuẩn format).
Nhược điểm: cần hiểu pipeline validate của Pydantic v2, hơi "magic" nếu chưa quen.

**Hướng B — nhận `str`, tự convert trong thân hàm (cách đã chọn dùng trong code hiện tại):**

Không ép FastAPI validate kiểu `int` ngay từ đầu — nhận raw string, tự parse bằng tay qua helper riêng.

`app/services/helper.py`:

```python
from app.core.exception import AppException
from fastapi import status
from typing import Optional

def to_optional_int(value: Optional[str]) -> Optional[int]:
    if value is None or value.strip() == "":
        return None
    try:
        return int(value)
    except ValueError:
        raise AppException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=f"'{value}' không phải số nguyên hợp lệ"
        )
```

Router:

```python
sort_order: Optional[str] = Form(None),   # nhận str, không ép int ngay
...
sort_order_int = to_optional_int(sort_order)
```

Ưu điểm: code tường minh, dễ đọc, dễ debug từng bước, không cần hiểu sâu Pydantic v2 validator.
Nhược điểm: verbose hơn nếu có nhiều field số; phải tự viết try/except, tự raise lỗi.

→ **Kết luận đã áp dụng:** dùng Hướng B vì đơn giản, dễ maintain, không cần hiểu sâu `Annotated`/`BeforeValidator`. Khi nào quen Pydantic hơn có thể đổi qua Hướng A.

### 7.5. Tóm tắt tư duy quan trọng nhất

> Lỗi 422 nghĩa là request **chưa bao giờ chạm tới logic nghiệp vụ**. Nó bị FastAPI/Pydantic chặn ở tầng parse & validate tham số. Muốn sửa, phải can thiệp **đúng tại tầng đó** (khai báo tham số của route, dùng `BeforeValidator` hoặc `Union`), không phải sửa ở tầng xử lý nghiệp vụ bên trong thân hàm.

---
