## `🎯 Note xử lý ảnh qua Cloudinary`

## 1. `secure_url` vs `public_id` — khác nhau chỗ nào?

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

## 2. `app/core/cloudinary_config.py`

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

## 3. Lớp service riêng — `app/services/timeline.py`

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

## 4. Tổ chức theo folder trên Cloudinary (mở rộng sau này)

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
