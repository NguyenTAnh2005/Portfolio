# 📝 Ghi chú: Xử lý Lỗi Tập Trung & Chuẩn hóa API Response

**Mục tiêu:** Thống nhất định dạng trả về của tất cả các API (dù thành công hay thất bại) về một cấu trúc JSON duy nhất. Điều này giúp phía Frontend (React) cực kỳ nhàn nhã khi xử lý dữ liệu và thông báo lỗi.

**Cấu trúc JSON tiêu chuẩn:**
Mọi API trả về đều phải bám theo bộ khung 3 thành phần chính:

- `success`: `true` hoặc `false`
- `message`: Thông báo cho người dùng (Frontend có thể dùng để hiện Toast/Alert)
- `data`: Dữ liệu thực tế (nếu có)
- _(Riêng khi có lỗi sẽ có thêm `error_code` để Frontend phân loại logic)_

---

## ✅ 1. Phe Thành Công (Success) -> Dùng Pydantic Generic Schema

Khi API thực thi thành công, chúng ta **không ném lỗi** mà dùng `return`. Để Swagger UI hiểu được cấu trúc trả về, ta sử dụng `BaseModel` của Pydantic kết hợp với `Generic Type`.

### 🛠️ Code minh họa:

**Tạo file `app/schemas/response.py`:**

```python
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

# T là một biến kiểu dữ liệu động (Generic Type)
T = TypeVar("T")

class ResponseModel(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Thành công"
    data: Optional[T] = None
```

### Cách sử dụng tại file Router (VD: `routers/project.py`):

```python
from fastapi import APIRouter
from app.schemas.response import ResponseModel
from app.schemas.schemas_project import ProjectResponse # Schema của riêng project

router = APIRouter()

@router.get("/projects", response_model=ResponseModel[list[ProjectResponse]])
def get_all_projects():
    # ... logic lấy projects từ database ...

    return {
        "success": True,
        "message": "Lấy danh sách dự án thành công",
        "data": projects # Trả về mảng list các project
    }

```

---

## ❌ 2. Phe Lỗi (Thất bại) -> Dùng Custom Exception Class

Khi có lỗi xảy ra (sai password, không tìm thấy user,...), ta không dùng `return` mà dùng `raise` để "ném" lỗi đi. Hệ thống sẽ tự động giăng lưới bắt lại và ép thành định dạng chuẩn.

### 🛠️ Code minh họa:

**Bước 1: Tạo class lỗi riêng ở `app/core/exceptions.py`:**

```python
class AppException(Exception):
    def __init__(self, status_code: int, error_code: str, message: str):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message

```

**Bước 2: Giăng "lưới" bắt lỗi tại `main.py`:**

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.exceptions import AppException

app = FastAPI()

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_code": exc.error_code,
            "message": exc.message,
            "data": None
        }
    )

```

**Bước 3: Cách sử dụng tại file Router/CRUD:**

```python
from app.core.exceptions import AppException
from fastapi import status

def get_project(db: Session, project_id: int):
    # ... logic tìm project ...

    if not db_project:
        # Chỉ cần raise, hệ thống sẽ tự động trả về JSON chuẩn
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="PROJECT_NOT_FOUND",
            message="Không tìm thấy dự án này trong hệ thống!"
        )
    return db_project

```

---

## 💡 Tổng kết lợi ích cho Frontend

Nhờ áp dụng cấu trúc này, phía Frontend (React + Axios) chỉ cần thiết lập Interceptor đúng 1 lần duy nhất:

```javascript
// Mã giả minh họa cách Frontend xử lý siêu gọn
if (response.data.success === false) {
  toast.error(response.data.message); // Tự động hiện lỗi màu đỏ
  if (response.data.error_code === "TOKEN_EXPIRED") {
    logoutUser(); // Tự động đá văng ra khỏi phiên đăng nhập
  }
} else {
  toast.success(response.data.message); // Tự động hiện thông báo màu xanh
  renderUI(response.data.data); // Hiển thị dữ liệu
}
```
