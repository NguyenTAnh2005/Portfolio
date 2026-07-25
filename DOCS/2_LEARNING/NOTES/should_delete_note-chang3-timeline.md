Chia làm 3 phần: luồng hoạt động, cần chuẩn bị gì, và kế hoạch triển khai theo từng bước.

# 1. Luồng hoạt động chi tiết

Hình dung với ví dụ: Admin tạo mới 1 **Project** kèm ảnh screenshot.

```
[Admin - Frontend]
  1. Admin chọn file ảnh từ input type="file"
  2. Admin điền các field khác (tên project, mô tả, link github...)
  3. Frontend gom tất cả vào FormData (KHÔNG dùng JSON như bình thường,
     vì có file binary bên trong)
  4. Gửi POST request lên Backend, header là "multipart/form-data"
        ↓
[Backend - FastAPI]
  5. Endpoint nhận request, tách ra:
     - Các field text (dùng Form(...))
     - File ảnh (dùng UploadFile)
  6. Backend gọi cloudinary.uploader.upload(file)
     → Cloudinary xử lý, lưu ảnh, trả về JSON response gồm:
        - secure_url (link ảnh https để hiển thị)
        - public_id (mã định danh ảnh trên Cloudinary, dùng để xóa/update sau này)
  7. Backend tạo record Project trong PostgreSQL, lưu:
        - các field text
        - image_url = secure_url
        - image_public_id = public_id
  8. Backend trả response về cho Frontend (project vừa tạo, gồm cả link ảnh)
        ↓
[Frontend]
  9. Nhận response, cập nhật UI (hiển thị ảnh mới, thông báo thành công)
```

**Khi update ảnh (thay ảnh mới):** trước khi upload ảnh mới, gọi `cloudinary.uploader.destroy(old_public_id)` để xóa ảnh cũ trên Cloudinary trước — tránh rác tồn đọng và tốn dung lượng free tier.

**Khi xóa record:** tương tự, gọi `destroy(public_id)` để dọn ảnh trên Cloudinary trước khi xóa record trong DB.

### - Tại sao phải tách `Form(...)` và `UploadFile` riêng?

Vì bản chất của `multipart/form-data` **khác hoàn toàn** với JSON mà bạn hay dùng.

- Bình thường (JSON): toàn bộ dữ liệu là 1 khối text có cấu trúc `{ "name": "abc", "desc": "xyz" }` → FastAPI parse thẳng vào 1 Pydantic model bằng `Body(...)`.
- Với `multipart/form-data`: request được chia thành **nhiều "phần" (parts)** riêng biệt, mỗi phần có thể là kiểu dữ liệu khác nhau — phần thì là text, phần thì là file nhị phân (binary). Giống như 1 cái bưu kiện có nhiều ngăn, mỗi ngăn đóng gói kiểu khác nhau.

Vì vậy FastAPI **không thể dùng 1 Pydantic model để nhận hết** như JSON được — nó cần biết rõ: "field này là text (Form), field này là file (UploadFile)" để biết cách đọc từng phần đúng kiểu.

Ví dụ code minh họa:

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

→ `Form(...)` nói với FastAPI: "lấy field text này ra từ phần form data". `UploadFile = File(...)` nói: "field này là file, đọc nó như 1 file object (có `.file`, `.filename`, `.content_type`...)". Không tách thì FastAPI không biết parse kiểu nào cho field nào.

### - Vì sao có 2 thứ: `secure_url` và `public_id`? Nó lưu như cột thường hay khóa gì không?

Hiểu đơn giản: **2 cái này phục vụ 2 mục đích khác nhau, hoàn toàn không liên quan gì đến primary key/foreign key trong DB của bạn.**

- **`secure_url`**: là đường link https trực tiếp tới ảnh → dùng để **hiển thị** ảnh lên UI (`<img src={secure_url} />`). Đây là thứ bạn cần khi render trang.
- **`public_id`**: là "tên định danh" của ảnh **trên hệ thống Cloudinary** (không phải trên DB của bạn) → dùng để **thao tác với chính ảnh đó sau này**: xóa nó (`destroy`), thay thế nó, hoặc transform nó (resize, crop qua URL).

Ví dụ dễ hình dung: `secure_url` giống như "địa chỉ nhà" để bạn ghé thăm (xem ảnh), còn `public_id` giống như "số CMND của ngôi nhà đó" để bên Cloudinary họ tra ra chính xác ngôi nhà nào mà thao tác (xóa, sửa).

**Tại sao cần cả 2, không thể suy ra `public_id` từ `secure_url`?** Về lý thuyết có thể tách `public_id` ra từ URL, nhưng không nên vì URL có thể chứa thêm transform params, version number (`v1234567890`)... dễ parse sai. Lưu sẵn `public_id` là cách an toàn, rõ ràng, đúng chuẩn Cloudinary khuyến nghị.

**Về việc lưu trong DB**: đúng như bạn nghĩ — cả `image_url` và `image_public_id` chỉ là 2 **cột string bình thường** trong bảng Timeline/Project/Achievement, **không phải khóa chính, không phải khóa ngoại**, không liên kết bảng nào cả. Nó chỉ đơn thuần là dữ liệu text như "họ tên" hay "mô tả" thôi, chỉ khác là giá trị của nó dùng để tương tác với Cloudinary sau này.

```python
class Timeline(Base):
    __tablename__ = "timelines"
    id = Column(Integer, primary_key=True)   # đây mới là PK thật
    title = Column(String)
    organization = Column(String)
    image_url = Column(String, nullable=True)         # chỉ để hiển thị
    image_public_id = Column(String, nullable=True)   # chỉ để thao tác Cloudinary
```

# 2. Kế hoạch triển khai (theo thứ tự nên làm)

**Bước 1 — Setup Cloudinary (làm 1 lần, dùng chung mãi về sau)**

- Đăng ký Cloudinary, lấy `cloud_name`, `api_key`, `api_secret` → bỏ vào `.env`.
- Cài `pip install cloudinary python-multipart`.
- Tạo `app/core/cloudinary_config.py`, khởi tạo config đọc từ `.env`. File này chỉ viết 1 lần, Timeline/Project/Achievement sau này đều import dùng lại.

_Lý do phải làm bước này đầu tiên: mọi thao tác upload phía sau đều cần Cloudinary SDK đã được cấu hình sẵn._

**Bước 2 — Model Timeline**

- Viết class `Timeline` trong `app/models`, gồm field bình thường (title, organization, start_date, end_date, description...) + 2 field `image_url`, `image_public_id` như ở câu 2.

_Lý do thêm 2 field này ngay từ model: để khi chạy alembic migration là có đủ cột luôn, tránh phải migrate 2 lần._

**Bước 3 — Schema (Pydantic)**

- Schema `TimelineResponse` có field `image_url` (để trả về khi client GET).
- Schema tạo/sửa (`TimelineCreate`) **không cần** field ảnh trong Pydantic model, vì ảnh sẽ nhận qua `UploadFile` riêng ở router (theo cơ chế multipart đã giải thích ở câu 1), không đi qua Pydantic body như các field khác.

**Bước 4 — CRUD logic**

- Viết hàm `create_timeline(db, data, image_url, image_public_id)` — nhận sẵn URL và public_id (đã upload xong) để lưu vào DB, hàm CRUD không cần biết gì về Cloudinary, chỉ lo lưu DB.

_Lý do tách vậy: giữ CRUD "thuần" chỉ làm việc với DB, việc upload ảnh xử lý riêng ở router — dễ test, dễ tái sử dụng cho Project/Achievement sau này._

**Bước 5 — Router/API endpoint**

- Endpoint `POST /timelines`: nhận `Form(...)` cho field text + `UploadFile` cho ảnh (như câu 1) → gọi `cloudinary.uploader.upload(image.file)` → lấy `secure_url`, `public_id` → gọi hàm CRUD ở bước 4 để lưu.

**Bước 6 — Test bằng seed script hoặc Swagger UI**

- Dùng `/docs` (Swagger UI) của FastAPI để test upload trực tiếp — nó tự hỗ trợ chọn file, không cần frontend cũng test được luồng backend trước.

**Bước 7 — Frontend form Timeline**

- Sau khi backend chạy ổn, mới nối frontend: input file → `FormData` → gửi qua Axios.

Xem code Info bạn gửi, mình thấy đây đúng là hình mẫu "CRUD chuẩn không có file" — so sánh trực tiếp với luồng Cloudinary sẽ giúp bạn thấy rõ điểm khác biệt nằm ở đâu.

## So sánh Info vs Timeline/Project (có ảnh)

### Router

**Info** — nhận thẳng 1 Pydantic model qua body JSON:

```python
def update_info(info_id: int, update_data: InfoUpdate, db: Session = Depends(...)):
    info = update_info_by_id(db=db, target_info_id=info_id, update_data=update_data)
```

Vì `update_data` đã là object Pydantic hoàn chỉnh — FastAPI tự parse JSON → Pydantic model, router không cần làm gì thêm ngoài gọi CRUD.

**Timeline** — không thể làm vậy, vì multipart request không map thẳng vào 1 Pydantic model được (như đã giải thích ở note bạn upload). Router phải làm **2 việc tuần tự**:

```python
@router.post("/timelines")
def create_timeline(
    title: str = Form(...),
    organization: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(connect_db)
):
    # Việc 1: xử lý ảnh trước (gọi Cloudinary)
    upload_result = cloudinary.uploader.upload(image.file)

    # Việc 2: mới gọi CRUD, đưa string url/public_id vào — giống hệt cách Info gọi CRUD
    timeline = create_timeline_crud(
        db=db,
        title=title,
        organization=organization,
        image_url=upload_result["secure_url"],
        image_public_id=upload_result["public_id"]
    )
    return timeline
```

→ Đây là khác biệt cốt lõi: **router của Timeline "dày" hơn** vì gánh thêm bước gọi service ngoài (Cloudinary) trước khi đụng tới DB. Info không có bước ngoại vi này nên router mỏng, chỉ orchestrate.

### CRUD

Cả 2 CRUD đều giống nhau về triết lý: **chỉ biết làm việc với DB, không biết gì về nguồn gốc dữ liệu**.

- `update_info_by_id` nhận Pydantic `InfoUpdate`, dùng `exclude_unset=True` + `setattr` loop — cách này _chỉ_ hợp khi input là Pydantic model có sẵn.
- CRUD của Timeline không nhận `UploadFile` (điều này quan trọng) — nó nhận `image_url` và `image_public_id` dạng string thuần, y hệt kiểu bạn truyền `fullname: str`. Vì vậy code CRUD Timeline **không hề phức tạp hơn** Info — nó chỉ là thêm 2 cột string.

Nếu bạn muốn viết `update_timeline` theo đúng pattern `exclude_unset` như Info, hoàn toàn làm được — chỉ cần Schema `TimelineUpdate` (Pydantic) chứa các field text, còn `image` xử lý tách riêng ở router như trên rồi gộp vào dict trước khi update:

```python
def update_timeline_by_id(db: Session, target_id: int, update_data: TimelineUpdate,
                           new_image_url: str | None = None,
                           new_public_id: str | None = None):
    target = get_timeline_by_id(db, target_id)
    update_dict = update_data.model_dump(exclude_unset=True)

    if new_image_url:
        update_dict["image_url"] = new_image_url
        update_dict["image_public_id"] = new_public_id

    for key, value in update_dict.items():
        setattr(target, key, value)
    db.add(target)
    db.commit()
    db.refresh(target)
    return target
```

### Tóm tắt khác biệt

|                       | Info                                   | Timeline/Project                                            |
| --------------------- | -------------------------------------- | ----------------------------------------------------------- |
| Body request          | JSON thuần                             | multipart/form-data                                         |
| Router nhận           | 1 Pydantic model                       | Form(...) rời + UploadFile rời                              |
| Bước phụ trong router | Không có                               | Gọi Cloudinary upload/destroy trước khi đụng DB             |
| CRUD nhận gì          | Pydantic object                        | String (url, public_id) — **không bao giờ nhận UploadFile** |
| Độ phức tạp CRUD      | Như nhau — chỉ là gán field vào object |

Điểm mấu chốt cần nhớ: **CRUD không bao giờ nên biết Cloudinary tồn tại**. Nó chỉ nhận string cuối cùng, y hệt như đang nhận `fullname` hay `hometown`.

## Cấu trúc code liên quan Cloudinary — tại sao vậy

Bước 1 trong kế hoạch nói "tạo `app/core/cloudinary_config.py`" — mình giải thích rõ hơn cấu trúc và lý do:

### File `app/core/cloudinary_config.py`

```python
import cloudinary
from app.core.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)
```

**Tại sao đặt trong `app/core/`?** Vì đây là _cấu hình hạ tầng_ (infrastructure config), cùng nhóm với `config.py` (đọc `.env`), `security.py` (JWT, hash password), `db_connection.py`. Nó không phải business logic của riêng model nào — Timeline, Project, Achievement đều dùng chung 1 config này.

**Tại sao chỉ cần import 1 lần?** Vì `cloudinary.config(...)` là lệnh **set global state** cho cả SDK — gọi 1 lần lúc app khởi động (hoặc lúc module này được import lần đầu) là đủ, các lệnh `cloudinary.uploader.upload(...)` sau đó ở bất cứ đâu trong app đều tự dùng config đã set, không cần truyền lại credentials mỗi lần gọi.

### Nên có thêm 1 lớp nữa: `app/services/cloudinary_service.py`

Note gốc để router gọi thẳng `cloudinary.uploader.upload(file)` — chạy được, nhưng nếu bạn muốn giữ đúng tinh thần "tách lớp" mà bạn đang làm với CRUD, nên bọc thêm 1 lớp service:

```python
# app/services/cloudinary_service.py
import cloudinary.uploader
from app.core.exception import AppException
from fastapi import status

def upload_image(file) -> dict:
    """Upload ảnh lên Cloudinary, trả về secure_url và public_id."""
    try:
        result = cloudinary.uploader.upload(file)
        return {
            "secure_url": result["secure_url"],
            "public_id": result["public_id"]
        }
    except Exception:
        raise AppException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code="CLOUDINARY_UPLOAD_FAILED",
            message="Upload ảnh thất bại, vui lòng thử lại!"
        )

def delete_image(public_id: str) -> None:
    """Xóa ảnh cũ trên Cloudinary theo public_id."""
    if public_id:
        cloudinary.uploader.destroy(public_id)
```

**Tại sao nên tách thêm lớp này thay vì gọi thẳng ở router?**

1. **Đồng bộ kiến trúc** — bạn đã tách CRUD (chỉ lo DB) khỏi router (orchestrate). Cloudinary cũng là 1 "nguồn dữ liệu ngoài" giống DB, nên xứng đáng có lớp riêng thay vì nằm lẫn trong router.
2. **Try/except tập trung 1 chỗ** — nếu Cloudinary sập hoặc timeout, bạn xử lý lỗi ở đúng 1 nơi (`services/cloudinary_service.py`), không phải lặp lại try/except ở mọi router (Timeline, Project, Achievement).
3. **Dễ test** — muốn viết unit test cho router mà không gọi Cloudinary thật, bạn chỉ cần mock `upload_image()` — gọn hơn nhiều so với mock trực tiếp `cloudinary.uploader.upload`.
4. **Dễ đổi provider sau này** — nếu 1 ngày bạn đổi từ Cloudinary sang S3, chỉ cần sửa trong `cloudinary_service.py`, router và CRUD không đụng gì cả.

Router lúc này gọn lại:

```python
from app.services.cloudinary_service import upload_image

@router.post("/timelines")
def create_timeline(title: str = Form(...), image: UploadFile = File(...), db: Session = Depends(connect_db)):
    image_data = upload_image(image.file)
    timeline = create_timeline_crud(db=db, title=title,
                                     image_url=image_data["secure_url"],
                                     image_public_id=image_data["public_id"])
    return timeline
```

```python
@router.put("/timelines/{timeline_id}")
def update_timeline(
    timeline_id: int,
    title: str = Form(...),
    organization: str = Form(...),
    image: UploadFile | None = File(None),   # ảnh optional, không phải lúc nào update cũng đổi ảnh
    db: Session = Depends(connect_db)
):
    old_timeline = get_timeline_by_id(db, timeline_id)

    new_image_url = None
    new_public_id = None

    if image:  # chỉ xử lý Cloudinary khi user thực sự chọn ảnh mới
        # Bước 1: upload ảnh mới TRƯỚC
        image_data = upload_image(image.file)
        new_image_url = image_data["secure_url"]
        new_public_id = image_data["public_id"]

        # Bước 2: upload thành công rồi mới xóa ảnh cũ
        delete_image(old_timeline.img_public_url)

    # Bước 3: update DB
    timeline = update_timeline_by_id(
        db=db,
        target_id=timeline_id,
        title=title,
        organization=organization,
        new_image_url=new_image_url,
        new_public_id=new_public_id
    )
    return timeline
```

## 1. Thông số đầu vào cho url/public_id — dùng Optional

Đừng nhét `image_url`/`image_public_id` vào Pydantic schema `TimelineUpdate` (vì ảnh đi qua `UploadFile` ở router, không qua JSON body). Thay vào đó, CRUD nhận thêm 2 tham số optional riêng, mặc định `None`:

```python
def update_timeline(
    db: Session,
    target_id: int,
    update_data: TimelineUpdate,          # các field text, dùng exclude_unset
    new_image_url: str | None = None,
    new_public_id: str | None = None,
):
    """
    - Func nhận id target và dữ liệu cần cập nhật để cập nhật.
    - Tìm kiếm đối tượng.
    - Thực hiện cập nhật nếu có.
    - Trả về đối tượng với schema Timeline Response.
    """
    db_timeline = get_timeline_by_id(db=db, timeline_id=target_id)
    if not db_timeline:
        return None  # hoặc raise AppException 404 tùy convention của bạn
```

## 2. setattr cho field thường vs 2 field ảnh

Field trong schema thì `exclude_unset=True` + `setattr` loop như bạn đang làm với Info — cái này ổn vì Pydantic tự biết field nào client thật sự gửi lên.

Nhưng `new_image_url`/`new_public_id` **không nằm trong Pydantic model**, nên không thể dựa vào `exclude_unset`. Cách xử lý: gộp thủ công vào cùng dict trước khi loop, chỉ khi có ảnh mới:

```python
    update_dict = update_data.model_dump(exclude_unset=True)

    if new_image_url:
        update_dict["image_url"] = new_image_url
        update_dict["image_public_id"] = new_public_id

    for key, value in update_dict.items():
        setattr(db_timeline, key, value)

    db.add(db_timeline)
    db.commit()
    db.refresh(db_timeline)
    return db_timeline
```

Lý do check `if new_image_url` (không phải `is not None` cứng nhắc): chỉ khi router thực sự upload ảnh mới thành công thì 2 field này mới có giá trị — còn nếu user update mà không đổi ảnh, `new_image_url=None` thì bỏ qua, giữ nguyên `image_url`/`image_public_id` cũ trong DB.

Ok, mình hướng dẫn viết router POST cho Timeline theo đúng cấu trúc bạn đang có (service `upload_image` trong `app/services/timeline.py`, CRUD `create_timeline` trong `app/crud/timeline.py`).

**Trước tiên có 1 lỗi cần sửa ngay:** trong file router của bạn, hàm router đang đặt tên trùng với hàm CRUD đã import (`create_timeline`) — cái sau sẽ đè cái trước, Python không báo lỗi nhưng logic sẽ sai (gọi hàm router lại gọi chính nó, không gọi được CRUD). Nên đổi tên 1 trong 2 — thường thì import CRUD với alias.

```python
from app.core.config import settings
from fastapi import APIRouter, Depends, Form, UploadFile, File
from app.db_connection import connect_db
from app.schemas.response import ResponseModel
from app.core.security import get_current_admin
from sqlalchemy.orm import Session
from app.models.models import User
from app.crud.timeline import create_timeline as create_timeline_crud
from app.schemas.timeline import TimelineCreate, TimelineResponse
from app.services.timeline import upload_image

BASE_URL = settings.BASE_API_URL

router = APIRouter(
    prefix=BASE_URL + "/timeline",
    tags=["Timeline"]
)


@router.post("/", response_model=ResponseModel[TimelineResponse])
def create_timeline(
    title: str = Form(...),
    organization: str = Form(...),
    desc: str = Form(...),
    start_end: str = Form(...),
    sort_order: int = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(connect_db),
    current_admin: User = Depends(get_current_admin),
):
    """
    - Nhận field text qua Form(...) + file ảnh qua UploadFile (multipart/form-data)
    - Bước 1: upload ảnh lên Cloudinary trước
    - Bước 2: gộp field text vào TimelineCreate, gọi CRUD để lưu DB
    """
    # Bước 1 - upload ảnh
    image_data = upload_image(image.file)

    # Bước 2 - gom field text thành object TimelineCreate để khớp signature CRUD hiện tại
    data_create = TimelineCreate(
        title=title,
        organization=organization,
        desc=desc,
        start_end=start_end,
        sort_order=sort_order,
    )

    new_timeline = create_timeline_crud(
        db=db,
        data_create=data_create,
        img_url=image_data["secure_url"],
        img_public_url=image_data["public_id"],
    )

    return ResponseModel(data=new_timeline)
```

Vài điểm lưu ý khớp với code bạn đang có:

1. **`image.file`** — `UploadFile` của FastAPI có thuộc tính `.file` là file-like object, đúng cái `cloudinary.uploader.upload()` trong `services/timeline.py` cần nhận.
2. **`response_model=ResponseModel[TimelineResponse]`** — mình sửa từ `TimelineCreate` (bản gốc của bạn) thành `TimelineResponse`, vì response trả về cho client nên có `img_url`, `img_public_url`, còn `TimelineCreate` là schema _đầu vào_, không có 2 field ảnh đó — dùng nó làm response_model sẽ bị FastAPI lọc mất field ảnh khi serialize.
3. **`current_admin: User = Depends(get_current_admin)`** — giữ nguyên vì đây là API tạo mới, cần quyền admin, bạn đã có sẵn dependency này.
4. Không đổi gì bên `crud/timeline.py` hay `services/timeline.py` — router gọi thẳng đúng signature bạn đã viết sẵn.

Không sao cả, để mình làm rõ từng lớp một, chậm rãi.

## `UploadFile` là gì?

Khi bạn gửi 1 file qua `multipart/form-data`, FastAPI không đưa cho bạn file thô ngay — nó gói lại thành 1 object gọi là `UploadFile`. Object này giống như **một cái phong bì**, bên trong có nhiều thứ:

```python
img_file: UploadFile
├── img_file.filename      # tên file gốc, vd: "avatar.png"
├── img_file.content_type  # loại file, vd: "image/png"
├── img_file.file          # ← file THẬT nằm ở đây
└── img_file.read()        # hàm đọc file (nhưng là bản async)
```

Tức là `img_file` **không phải là file** — nó là cái phong bì _chứa_ file, kèm theo vài thông tin mô tả (tên, loại...).

## `img_file.file` là gì?

Đây mới là file thật sự bên trong phong bì — kiểu Python gọi là `SpooledTemporaryFile`. Đây là kiểu file object "truyền thống", giống hệt như khi bạn làm:

```python
with open("abc.png", "rb") as f:
    data = f.read()
```

`img_file.file` hoạt động y hệt `f` ở đây — gọi `.read()` là có bytes ngay, không rắc rối gì.

## Vì sao lại có 2 lớp (phong bì + file) thay vì đưa file thẳng?

Vì FastAPI được thiết kế chạy trong môi trường **bất đồng bộ** (async). Khi upload file dung lượng lớn, việc đọc file có thể tốn thời gian → FastAPI muốn bạn đọc kiểu "không chặn luồng" bằng `await img_file.read()`. Nên nó bọc file thật vào trong `UploadFile`, và cho thêm 1 hàm `read()` kiểu `async def` để hỗ trợ việc này.

Nhưng đây cũng chính là **nguồn gốc rắc rối**: `UploadFile` có 2 con đường đọc dữ liệu hoàn toàn khác nhau:

| Muốn đọc kiểu                                      | Dùng                    | Kết quả gọi `.read()`                  |
| -------------------------------------------------- | ----------------------- | -------------------------------------- |
| Bất đồng bộ (async, chuẩn FastAPI)                 | `await img_file.read()` | trả bytes thật (nhưng phải có `await`) |
| Đồng bộ (sync, kiểu thư viện ngoài như Cloudinary) | `img_file.file.read()`  | trả bytes thật ngay, không cần `await` |

Vấn đề bạn gặp là: bạn (gián tiếp, qua Cloudinary SDK) gọi `img_file.read()` (đường async) nhưng lại theo kiểu sync (không `await`) → nó không đọc gì cả, chỉ trả về "một lời hứa sẽ đọc" (coroutine) → sai kiểu dữ liệu.

## Quy tắc để nhớ

- Nếu code của **bạn** tự viết trong 1 hàm `async def` (endpoint FastAPI thường là vậy) và muốn tự đọc bytes → dùng `await img_file.read()`.
- Nếu bạn đưa file cho **thư viện bên thứ 3 không hỗ trợ async** (Cloudinary SDK, PIL, pandas, v.v.) → luôn phải đưa `img_file.file`, không đưa `img_file`.

Cloudinary SDK thuộc nhóm thứ 2 → nên luôn phải là `img_file.file`.

Bạn cứ từ từ sửa lại, có chỗ nào vẫn thấy rối thì hỏi tiếp, mình giải thích thêm.
Có, Cloudinary hỗ trợ chỉ định folder khi upload, kể cả folder lồng nhau (subfolder). Bạn chỉ cần thêm tham số `folder` khi gọi `upload()`:

```python
result = cloudinary.uploader.upload(
    file,
    folder="portfolio/timeline"   # folder cha/folder con, dùng dấu / để lồng nhau
)
```

**Một vài điểm cần biết:**

1. **Không cần tạo folder trước** — Cloudinary tự tạo folder (và các folder con) nếu chưa tồn tại, ngay khi bạn upload ảnh đầu tiên vào đó.

2. **`public_id` sẽ bao gồm cả đường dẫn folder** — ví dụ nếu bạn upload với `folder="portfolio/timeline"`, kết quả trả về `public_id` sẽ có dạng:

   ```
   portfolio/timeline/abcxyz123
   ```

   Điều này quan trọng vì bạn đang lưu `public_id` để dùng cho `destroy()` sau này — chỉ cần lưu nguyên `public_id` Cloudinary trả về (đã có sẵn path folder trong đó), lúc xóa gọi `cloudinary.uploader.destroy(public_id)` là tự xóa đúng file trong đúng folder, không cần bạn tự ghép path.

3. **Tổ chức theo từng entity** — với dự án của bạn (có Timeline, Project, Achievement...), cách hay dùng là tổ chức folder theo loại:
   ```
   portfolio/
     ├── timeline/
     ├── projects/
     └── achievements/
   ```
   Áp dụng cụ thể: trong `upload_image()`, bạn có thể truyền `folder` như một tham số để mỗi service (timeline, project...) tự chỉ định folder riêng của mình, thay vì hard-code cứng 1 folder cho tất cả.

**Ví dụ sửa hàm `upload_image` để nhận folder linh hoạt:**

```python
def upload_image(file, folder: str = "portfolio"):
    try:
        result = cloudinary.uploader.upload(file, folder=folder)
        return {
            "secure_url": result["secure_url"],
            "public_id":  result["public_id"]
        }
    except Exception as e:
        print(f"[Cloudinary upload error] {e}")
        raise AppException(...)
```

Rồi khi gọi ở router của Timeline:

```python
img_data = upload_image(img_file.file, folder="portfolio/timeline")
```

Sau này viết router cho Project thì gọi:

```python
img_data = upload_image(img_file.file, folder="portfolio/projects")
```

Cách này giúp bạn tái sử dụng đúng 1 hàm `upload_image()` cho mọi entity trong dự án, chỉ khác nhau ở tham số `folder`.

Ok, để tôi giải thích kỹ cơ chế bên dưới, không chỉ đưa code nữa.

## 1. FastAPI xử lý tham số route như thế nào (bước nào lỗi xảy ra)

Khi request tới `PUT /{timeline_id}`, FastAPI làm theo thứ tự:

1. Đọc raw multipart form data từ request.
2. Với **mỗi tham số** trong signature của `update()`, nó lấy field tương ứng trong form, rồi **validate qua Pydantic** theo type annotation bạn khai (`Optional[int]`, `Optional[UploadFile]`...).
3. Nếu tham số nào fail validate → gom lỗi lại, trả về **422** ngay, **không gọi hàm `update()` nữa**.
4. Chỉ khi tất cả tham số pass thì FastAPI mới thực sự gọi `update(target_id=..., title=..., sort_order=..., ...)`.

Vậy lỗi bạn thấy (`int_parsing`, `Expected UploadFile`) là lỗi xảy ra **ở bước 3**, tức là trước khi dòng code đầu tiên trong `update()` được chạy. Đây là lý do vì sao sửa trong `parse_field_text_to_pydantic_class` (nằm ở bước sau, trong thân hàm) là vô ích — hàm đó chưa bao giờ được gọi tới trong trường hợp lỗi.

## 2. Vì sao `Optional[int] = Form(None)` không cứu được `""`

`Optional[int] = Form(None)` có nghĩa là: **"Nếu client không gửi field `sort_order` lên thì mặc định là `None`"**. Nó không có nghĩa là "nếu client gửi giá trị rỗng thì coi như `None`".

Swagger UI, khi bạn để trống ô input, vẫn **gửi field đó lên** với value là `""` (chuỗi rỗng) — chứ không lược bỏ field khỏi multipart body. Nên FastAPI thấy field `sort_order` có mặt, giá trị là `""`, nó thử ép kiểu `int("")` theo annotation `int` bạn khai → Python/Pydantic báo lỗi vì `""` không parse được thành số.

Nói cách khác: `= Form(None)` chỉ là **default value khi field vắng mặt**, không phải là **validator xử lý giá trị rỗng**. Hai khái niệm khác nhau.

## 3. Vì sao `Annotated[Optional[int], BeforeValidator(...)]` sửa được

Pydantic v2 validate theo pipeline nhiều bước. `BeforeValidator` chèn một hàm chạy **trước khi** Pydantic ép kiểu theo annotation gốc (`int`). Nên luồng sẽ là:

```
raw value ""
  → BeforeValidator (empty_str_to_none): "" → None
  → Pydantic ép kiểu theo Optional[int]: None hợp lệ, giữ nguyên None
  → kết quả cuối: None
```

Nếu không có `BeforeValidator`, luồng là:

```
raw value ""
  → Pydantic ép kiểu theo Optional[int]: cố int("") → LỖI
```

Đó là lý do bạn phải "chặn" giá trị `""` **trước khi** Pydantic cố ép kiểu `int`, chứ không phải sau.

## 4. Vì sao `img_file` lỗi `Expected UploadFile, received: str`

Tương tự — khi bạn không chọn file, Swagger vẫn gửi field `img_file` lên nhưng dưới dạng text rỗng `""` chứ không phải bỏ hẳn phần file khỏi multipart. FastAPI mong nhận được một `UploadFile` (object có `.filename`, `.file`, `.content_type`...) nhưng nhận được `str` → không match type → lỗi validate.

Khai `Union[UploadFile, str, None]` là nói với FastAPI: "field này có thể là UploadFile, hoặc str, hoặc None — đừng ép cứng chỉ UploadFile". Nhờ vậy nó không reject ngay ở bước validate; việc phân biệt "đây có phải file thật hay không" bạn tự làm bằng code (`isinstance(img_file, str)` hoặc check `.filename`) **sau khi** đã lọt qua bước validate của FastAPI.

## 5. Vì sao sửa trong `parse_field_text_to_pydantic_class` là sai chỗ

Hàm đó bạn gọi thủ công:

```python
update_data = parse_field_text_to_pydantic_class(
    title=title, sort_order=sort_order, ...
)
```

Ở đây `sort_order` là **biến local trong `update()`**, không phải FastAPI tự bind lại từ request lần thứ hai. Nếu request đã bị chặn ở bước validate tham số của `update()` (vì `sort_order: Optional[int] = Form(None)` fail), thì biến `sort_order` này **không hề tồn tại** — hàm `update()` chưa từng chạy, nên `parse_field_text_to_pydantic_class` cũng chưa từng được gọi. Các `Form(None)` bạn khai trong signature của nó chỉ có tác dụng nếu bạn dùng `Depends(parse_field_text_to_pydantic_class)` trực tiếp ở route — mà bạn không làm vậy, nên chúng là "khai báo chết", không ai đọc tới.

**Tóm lại về mặt tư duy**: lỗi 422 nghĩa là request chưa bao giờ chạm tới logic nghiệp vụ của bạn — nó bị FastAPI/Pydantic chặn ở tầng parse & validate tham số. Muốn sửa, phải can thiệp đúng tại tầng đó (khai báo tham số của route, dùng `BeforeValidator` hoặc `Union`), không phải ở tầng xử lý nghiệp vụ bên trong hàm.

Có, còn vài cách khác đơn giản hơn `BeforeValidator` nhiều. Tôi liệt kê từ dễ hiểu nhất đến khó:

## Cách 1 (đơn giản nhất): Nhận vào là `str`, tự convert trong thân hàm

Không ép FastAPI validate kiểu `int` ngay từ đầu nữa — nhận raw string, rồi tự parse bằng tay:

```python
@router.put("/{timeline_id}", response_model=ResponseModel[TimelineResponse])
def update(
    target_id: int,
    title: Optional[str] = Form(None),
    organization: Optional[str] = Form(None),
    desc: Optional[str] = Form(None),
    start_end: Optional[str] = Form(None),
    sort_order: Optional[str] = Form(None),   # <-- đổi thành str, không ép int nữa
    img_file: Optional[UploadFile] = File(None),
    db: Session = Depends(connect_db),
    current_admin: User = Depends(get_current_admin)
):
    # tự convert, code mình kiểm soát hoàn toàn, dễ đọc
    sort_order_value: Optional[int] = None
    if sort_order is not None and sort_order.strip() != "":
        try:
            sort_order_value = int(sort_order)
        except ValueError:
            raise HTTPException(status_code=422, detail="sort_order phải là số nguyên")

    update_data = parse_field_text_to_pydantic_class(
        title=title, organization=organization,
        desc=desc, start_end=start_end,
        sort_order=sort_order_value   # <-- truyền giá trị đã convert
    )
    ...
```

**Vì sao cách này dễ hiểu hơn**: không cần biết `Annotated`/`BeforeValidator` là gì, không cần hiểu Pydantic validate pipeline. Chỉ là nhận string → tự if/try/except convert như code Python bình thường. Nhược điểm là verbose hơn nếu có nhiều field số.

## Cách 2: Viết 1 hàm helper convert, tái dùng được

Nếu sau này có nhiều field kiểu số tương tự, tránh lặp code:

```python
def to_optional_int(value: Optional[str]) -> Optional[int]:
    if value is None or value.strip() == "":
        return None
    try:
        return int(value)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"'{value}' không phải số nguyên hợp lệ")
```

Rồi trong route:

```python
sort_order: Optional[str] = Form(None),
...
sort_order_value = to_optional_int(sort_order)
```

## Cách 3: Không sửa FastAPI param, mà custom exception handler bắt lỗi 422 toàn cục

Cách này phức tạp hơn, không khuyến khích cho case đơn giản này — bỏ qua.

## So sánh với `BeforeValidator`

| Cách                      | Ưu điểm                                                                             | Nhược điểm                                               |
| ------------------------- | ----------------------------------------------------------------------------------- | -------------------------------------------------------- |
| `BeforeValidator`         | Gọn, khai 1 lần dùng lại nhiều nơi, lỗi báo tự động qua Pydantic (422 chuẩn format) | Cần hiểu Pydantic v2 pipeline, hơi "magic" nếu chưa quen |
| Nhận `str` rồi tự convert | Code tường minh, dễ đọc, dễ debug từng bước                                         | Verbose hơn, phải tự viết try/except, tự raise lỗi       |

**Khuyên dùng**: nếu bạn chưa quen Pydantic v2 validators, cứ dùng **Cách 1** (nhận `str`, tự convert). Code sẽ dài hơn một chút nhưng bạn hiểu rõ 100% nó đang làm gì, dễ maintain hơn về sau. Khi nào quen Pydantic hơn thì chuyển qua `BeforeValidator` cũng chưa muộn.
