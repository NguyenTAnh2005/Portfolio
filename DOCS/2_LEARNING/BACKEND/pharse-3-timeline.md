# Chương 3 — Timeline + Upload ảnh qua Cloudinary (tổng hợp)

---

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

## 3. `secure_url` vs `public_id` — khác nhau chỗ nào?

2 cái phục vụ 2 mục đích khác nhau, **không liên quan gì tới primary key / foreign key trong DB**.

|              | Mục đích                                                                                                                                            | Ví dụ ẩn dụ                                          |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| `secure_url` | Link https trực tiếp tới ảnh → dùng **hiển thị** (`<img src={secure_url} />`)                                                                       | "địa chỉ nhà" để ghé thăm                            |
| `public_id`  | "Tên định danh" ảnh **trên hệ thống Cloudinary** → dùng để **thao tác** với ảnh sau này: xóa (`destroy`), thay thế, transform (resize/crop qua URL) | "số CMND của ngôi nhà" để Cloudinary tra ra đúng ảnh |

**Vì sao lưu cả 2, không suy `public_id` từ `secure_url`?** Về lý thuyết có thể parse ngược từ URL, nhưng URL có thể chứa transform params, version number (`v1234567890`...) → dễ parse sai. Lưu sẵn `public_id` là cách an toàn, đúng chuẩn Cloudinary khuyến nghị.

**Trong DB:** `img_url` và `img_public_id` chỉ là 2 cột `String` bình thường trong bảng `TimeLine`, không phải khóa chính/khóa ngoại, không liên kết bảng nào — y hệt như cột `title` hay `desc`, chỉ khác giá trị của nó dùng để tương tác với Cloudinary về sau.

```python
class TimeLine(Base):
    __tablename__ = "timeline"
    id: Mapped[int] = mapped_column(primary_key=True)   # PK thật
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    img_url: Mapped[str] = mapped_column(String(100), nullable=True)         # chỉ để hiển thị
    img_public_id: Mapped[str] = mapped_column(String(100), nullable=True)   # chỉ để thao tác Cloudinary
```

---

## 4. Cấu trúc code liên quan Cloudinary

### 4.1. `app/core/cloudinary_config.py`

```python
import cloudinary
from app.core.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)
```

**Vì sao đặt trong `app/core/`?** Đây là cấu hình hạ tầng (infrastructure config), cùng nhóm với `config.py` (đọc `.env`), `security.py` (JWT, hash password), `db_connection.py`. Không phải business logic riêng của model nào — Timeline/Project/Achievement sau này đều import dùng chung.

**Vì sao chỉ cần import 1 lần?** `cloudinary.config(...)` set **global state** cho cả SDK — gọi 1 lần lúc app khởi động (hoặc lúc module được import lần đầu) là đủ. Mọi `cloudinary.uploader.upload(...)` sau đó ở bất cứ đâu trong app tự dùng config đã set, không cần truyền lại credentials mỗi lần gọi.

### 4.2. Lớp service riêng — `app/services/timeline.py`

Thay vì router gọi thẳng `cloudinary.uploader.upload(file)`, nên bọc thêm 1 lớp service (đúng cái đang làm trong code hiện tại):

```python
import cloudinary.uploader
from app.core import cloudinary_config
from app.core.exception import AppException
from fastapi import status

def upload_image(file):
    """Upload ảnh lên cloudinary. Trả về secure_url - url ảnh, public_id: id ảnh trên cloud"""
    try:
        result = cloudinary.uploader.upload(file)
        return {
            "secure_url": result["secure_url"],
            "public_id":  result["public_id"]
        }
    except Exception as e:
        print(f"[Cloudinary upload error] {e}")
        raise AppException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code="CLOUDINARY_UPLOAD_FAILED",
            message="Uploading image failed, please checking and try again!"
        )

def destroy_image(public_id):
    """Xóa ảnh theo public_id -> tránh rác trên bản free"""
    if public_id:
        cloudinary.uploader.destroy(public_id)
```

**Vì sao tách lớp này thay vì gọi thẳng ở router?**

1. **Đồng bộ kiến trúc** — CRUD tách khỏi router (chỉ orchestrate). Cloudinary cũng là "nguồn dữ liệu ngoài" giống DB, nên xứng đáng có lớp riêng.
2. **Try/except tập trung 1 chỗ** — Cloudinary sập/timeout thì xử lý lỗi đúng 1 nơi, không lặp lại try/except ở mọi router (Timeline, Project, Achievement).
3. **Dễ test** — muốn test router mà không gọi Cloudinary thật, chỉ cần mock `upload_image()`.
4. **Dễ đổi provider sau này** — đổi Cloudinary → S3 chỉ cần sửa file service này, router và CRUD không đụng gì.

### 4.3. Tổ chức theo folder trên Cloudinary (mở rộng sau này)

Cloudinary hỗ trợ chỉ định folder (kể cả lồng nhau) khi upload:

```python
result = cloudinary.uploader.upload(file, folder="portfolio/timeline")
```

- **Không cần tạo folder trước** — Cloudinary tự tạo folder (và folder con) khi upload ảnh đầu tiên vào đó.
- **`public_id` sẽ chứa cả path folder**, ví dụ `portfolio/timeline/abcxyz123`. Chỉ cần lưu nguyên `public_id` Cloudinary trả về, lúc `destroy(public_id)` tự xóa đúng file trong đúng folder, không cần tự ghép path.
- Tổ chức gợi ý cho dự án có nhiều entity:
  ```
  portfolio/
    ├── timeline/
    ├── projects/
    └── achievements/
  ```
- Có thể mở rộng `upload_image()` nhận thêm tham số `folder` để mỗi service (timeline, project...) tự chỉ định folder riêng thay vì hard-code:
  ```python
  def upload_image(file, folder: str = "portfolio"):
      result = cloudinary.uploader.upload(file, folder=folder)
      ...
  ```
  Gọi ở Timeline: `upload_image(img_file.file, folder="portfolio/timeline")`.
  _(Lưu ý: code hiện tại của Timeline chưa dùng tham số `folder`, đây là hướng mở rộng khi cần.)_

---

## 5. So sánh Info (JSON, không ảnh) vs Timeline (multipart, có ảnh)

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

## 6. `UploadFile` — hiểu đúng bản chất

### 6.1. `img_file` là "phong bì", `img_file.file` mới là "file thật"

```
img_file: UploadFile
├── img_file.filename      # tên file gốc, vd "avatar.png"
├── img_file.content_type  # vd "image/png"
├── img_file.file          # ← file THẬT nằm ở đây (SpooledTemporaryFile)
└── img_file.read()        # hàm đọc file, nhưng là bản ASYNC
```

`img_file.file` hoạt động y hệt kiểu file "truyền thống" (`open(...)` thường): gọi `.read()` là có bytes ngay, không cần `await`.

### 6.2. Vì sao có 2 đường đọc (sync vs async)?

FastAPI chạy trong môi trường async. Đọc file lớn có thể tốn thời gian → FastAPI cho `await img_file.read()` để không chặn luồng. Nhưng đây cũng là nguồn gốc rắc rối:

| Muốn đọc kiểu                           | Dùng                                                    | Kết quả                                |
| --------------------------------------- | ------------------------------------------------------- | -------------------------------------- |
| Bất đồng bộ (chuẩn FastAPI)             | `await img_file.read()`                                 | trả bytes thật, phải có `await`        |
| Đồng bộ (thư viện ngoài như Cloudinary) | `img_file.file.read()` (hoặc đưa thẳng `img_file.file`) | trả bytes thật ngay, không cần `await` |

**Quy tắc nhớ:**

- Tự viết code trong hàm `async def` (endpoint FastAPI) và muốn tự đọc bytes → dùng `await img_file.read()`.
- Đưa file cho thư viện bên thứ 3 không hỗ trợ async (Cloudinary SDK, PIL, pandas...) → luôn đưa `img_file.file`, **không đưa `img_file`**.

→ Cloudinary SDK thuộc nhóm 2, nên code hiện tại luôn gọi `upload_image(img_file.file)`, không phải `upload_image(img_file)`.

---

## 7. Lỗi 422 khi field rỗng qua Form — nguyên nhân sâu & cách xử lý

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

## 8. Cấu trúc code thực tế đã triển khai (final)

### 8.1. Cấu trúc thư mục liên quan

```
BACKEND/app/
├── core/
│   └── cloudinary_config.py     # set global config Cloudinary (import 1 lần)
├── models/
│   └── models.py                # class TimeLine (SQLAlchemy)
├── schemas/
│   └── timeline.py              # TimelineCreate / TimelineUpdate / TimelineResponse / TimelinePaginationResponse
├── services/
│   ├── timeline.py              # upload_image / destroy_image / parse_field_text_to_pydantic_class
│   └── helper.py                # to_optional_int
├── crud/
│   └── timeline.py              # create_timeline / get_timeline_by_id / get_all_timeline / update_timeline
└── routers/
    └── timeline.py              # POST / GET / GET all / PUT
```

### 8.2. Model (`app/models/models.py`)

```python
class TimeLine(Base):
    __tablename__ = "timeline"
    # id, title, organization, desc, start_end, sort_order, img_url, img_public_id
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    organization: Mapped[str] = mapped_column(String(30), nullable=False)
    desc: Mapped[str] = mapped_column(Text, nullable=False)
    # start_end: dùng chuỗi để gán cứng, không xử lý chuỗi thời gian → String
    start_end: Mapped[str] = mapped_column(String(20), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    img_url: Mapped[str] = mapped_column(String(100), nullable=True)
    img_public_id: Mapped[str] = mapped_column(String(100), nullable=True)
```

### 8.3. Schema (`app/schemas/timeline.py`)

- `TimelineCreate`: chỉ chứa field text (title, organization, desc, start_end, sort_order) — **không chứa field ảnh**, vì ảnh đi qua `UploadFile` riêng ở router, không qua Pydantic body.
- `TimelineUpdate`: tất cả field đều `Optional`, dùng cho `exclude_unset=True`.
- `TimelineResponse`: có `img_url`, `img_public_id` (Optional) để trả về client.
- `TimelinePaginationResponse`: bọc `total`, `skip`, `limit`, `list_data`.

### 8.4. CRUD (`app/crud/timeline.py`)

- `create_timeline(db, data_create, img_url, img_public_id)` — nhận sẵn url/public_id (đã upload xong), **không biết gì về Cloudinary**, chỉ lo lưu DB.
- `get_timeline_by_id` — raise `AppException` 404 (`TIMELINE_NOT_FOUND`) nếu không thấy.
- `get_all_timeline(db, skip, limit, sort_by, order)` — dùng `getattr(TimeLine, sort_by, TimeLine.id)` để sort động (fallback về `id` nếu `sort_by` không hợp lệ), trả `TimelinePaginationResponse`.
- `update_timeline(db, target_id, update_data, img_url=None, img_public_id=None)`:
  ```python
  update_data_dict = update_data.model_dump(exclude_unset=True)
  if img_url:
      update_data_dict["img_url"] = img_url
  if img_public_id:
      update_data_dict["img_public_id"] = img_public_id
  for key, value in update_data_dict.items():
      setattr(db_timeline, key, value)
  ```
  Chỉ ghi đè `img_url`/`img_public_id` khi thực sự có ảnh mới — nếu update mà không đổi ảnh thì giữ nguyên giá trị cũ trong DB.

### 8.5. Service (`app/services/timeline.py`)

- `upload_image(file)` — upload lên Cloudinary, tự raise `AppException` (502, `CLOUDINARY_UPLOAD_FAILED`) nếu lỗi.
- `destroy_image(public_id)` — xóa ảnh theo `public_id`, no-op nếu `public_id` rỗng.
- `parse_field_text_to_pydantic_class(...)` — gom các field text rời (đã qua `Form(...)`) thành 1 object `TimelineUpdate`, bỏ qua field `None` hoặc chuỗi rỗng `""`.

### 8.6. Router (`app/routers/timeline.py`)

**POST `/`** — tạo mới, bắt buộc phải có `img_file`, yêu cầu `current_admin`:

```python
img_data = upload_image(img_file.file)
data_create = TimelineCreate(title=..., organization=..., desc=..., start_end=..., sort_order=...)
new_timeline = create_timeline(db=db, data_create=data_create,
                                img_url=img_data["secure_url"], img_public_id=img_data["public_id"])
```

**GET `/{timeline_id}`** — lấy 1 timeline theo id.

**GET `/`** — list có phân trang, `skip`/`limit` (`limit` tối đa 30), `sort_by` (`id` | `sort_order`), `order` (`asc` | `desc`).

**PUT `/{timeline_id}`** — cập nhật, ảnh optional:

```python
sort_order_int = to_optional_int(sort_order)          # str "" → None, hợp lệ → int
if isinstance(img_file, str) or (img_file and not img_file.filename):
    img_file = None                                     # Swagger gửi "" khi không chọn file

db_timeline = None
if img_file:
    db_timeline = get_timeline_by_id(db=db, timeline_id=target_id)  # cần lấy old_public_id trước

update_data = parse_field_text_to_pydantic_class(
    title=title, organization=organization, desc=desc,
    start_end=start_end, sort_order=sort_order_int
)

new_secure_url = new_public_id = old_public_id = None
if img_file:
    new_image = upload_image(img_file.file)             # upload ảnh MỚI trước
    old_public_id = db_timeline.img_public_id
    new_secure_url = new_image["secure_url"]
    new_public_id = new_image["public_id"]

response = update_timeline(db=db, target_id=target_id, update_data=update_data,
                            img_url=new_secure_url, img_public_id=new_public_id)  # rồi mới update DB

if img_file and old_public_id:
    try:
        destroy_image(old_public_id)                    # cuối cùng mới dọn ảnh cũ, không fail request nếu lỗi
    except Exception as e:
        print(f"[WARN] Failed to destroy old image {old_public_id}: {e}")
```

**Điểm quan trọng cần nhớ ở PUT:** thứ tự luôn là **upload ảnh mới → update DB thành công → mới xóa ảnh cũ**. Không được xóa ảnh cũ trước, vì nếu bước update DB fail giữa chừng thì mất cả ảnh cũ lẫn ảnh mới.

### 8.7. Helper (`app/services/helper.py`)

```python
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

---

## 9. Bug từng gặp — nhớ để không lặp lại

1. **Đặt tên hàm router trùng tên hàm CRUD đã import** (`create_timeline` cả 2 nơi) — hàm sau đè hàm trước, Python không báo lỗi nhưng gọi sai logic (gọi lại chính router thay vì CRUD). **Cách phòng tránh:** import CRUD với alias, ví dụ `from app.crud.timeline import create_timeline as create_timeline_crud`.
2. **`response_model=TimelineCreate`** cho endpoint trả response là sai — `TimelineCreate` là schema _đầu vào_, không có `img_url`/`img_public_id`, dùng làm response_model sẽ bị FastAPI lọc mất field ảnh khi serialize. Phải dùng `TimelineResponse`.
3. **Gọi `cloudinary.uploader.upload(img_file)`** (đưa cả phong bì) thay vì `img_file.file` (file thật) → sai vì SDK Cloudinary là thư viện sync, không hiểu `UploadFile`/coroutine.
4. **`Optional[int] = Form(None)` tưởng nhầm là xử lý được input rỗng** — thực tế Swagger vẫn gửi `""` lên chứ không bỏ field, dẫn tới lỗi ép kiểu `int("")`. Phải nhận `str` rồi tự convert (hoặc dùng `BeforeValidator`).
5. **Sửa nhầm chỗ** — cố xử lý field rỗng bên trong `parse_field_text_to_pydantic_class` (thân hàm), trong khi lỗi 422 đã chặn request từ tầng khai báo tham số route, hàm đó chưa bao giờ được gọi tới.

---

## 10. Checklist triển khai (đã hoàn thành cho Timeline, áp dụng lại cho Project/Achievement)

- [x] Setup Cloudinary 1 lần: `cloud_name`, `api_key`, `api_secret` trong `.env`; `pip install cloudinary python-multipart`; tạo `app/core/cloudinary_config.py`.
- [x] Model: thêm sẵn `img_url`, `img_public_id` ngay từ đầu để migrate 1 lần.
- [x] Schema: `Create`/`Update` không chứa field ảnh; `Response` có `img_url`/`img_public_id`.
- [x] CRUD: chỉ nhận string (`img_url`, `img_public_id`), không bao giờ nhận `UploadFile`, không biết Cloudinary tồn tại.
- [x] Service riêng (`upload_image`, `destroy_image`) — tách khỏi router, try/except tập trung.
- [x] Router: field số nhận `str` rồi convert qua helper (`to_optional_int`); field file nhận `Union[UploadFile, str, None]` để không bị 422 khi Swagger gửi rỗng.
- [x] Router PUT: thứ tự upload mới → update DB → destroy ảnh cũ (không fail request nếu destroy lỗi).
- [ ] Test qua Swagger UI (`/docs`) trước khi nối Frontend.
- [ ] Frontend: input file → `FormData` → gửi qua Axios.
- [ ] (Mở rộng) Thêm tham số `folder` cho `upload_image()` khi làm thêm Project/Achievement, để tổ chức ảnh theo `portfolio/timeline`, `portfolio/projects`...
