# 📝 Ghi chú: Xử lý Lỗi Tập Trung & Chuẩn hóa API Response

**Mục tiêu:** Thống nhất định dạng trả về của tất cả các API (dù thành công hay thất bại) về một cấu trúc JSON duy nhất. Điều này giúp phía Frontend (React) cực kỳ nhàn nhã khi xử lý dữ liệu và thông báo lỗi.

**Note:** Tài liệu này cũng cung cấp thông tin về cấu trúc response khi backend gửi sang và cũng như cơ chế xử lý của axios đối với các response dựa trên status code (mục 3).

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

## 🛠️ 3. Cách Axios phân rã Status Code (Mặc định)

Trong Axios, cách nhận và xử lý dữ liệu được chia làm hai nhánh rõ rệt dựa trên mã trạng thái HTTP (status code). Khi lồng vào Axios Interceptor (trình chặn), việc phân tách này quyết định bạn phải viết code ở hàm nào (hàm xử lý phản hồi thành công hay hàm xử lý lỗi).

- `Status 200 (và các mã từ 200 - 299)`: Axios coi đây là Thành công. Dữ liệu sẽ được trả về dạng một đối tượng response. Bạn có thể truy cập qua .then() hoặc nhận trực tiếp từ await.
- `Status Lỗi (4xx, 5xx...)` hoặc `Lỗi mạng`: Axios coi đây là Thất bại (Reject). Axios sẽ ném ra (throw) một đối tượng error. Bạn phải hứng nó trong .catch() hoặc khối try...catch.

### Cách xử lý trong Axios Interceptor

Khi cấu hình axios.interceptors.response.use(), hàm này nhận vào hai tham số (là hai hàm callback):

1.  Hàm thứ nhất: Xử lý khi status code nằm trong khoảng 2xx (tương ứng với nhánh response).
2.  Hàm thứ hai: Xử lý khi status code nằm ngoài khoảng 2xx hoặc bị lỗi kết nối (tương ứng với nhánh error).

Cấu trúc chuẩn để bạn viết trong Interceptor như sau:

```js
import axios from "axios";

axios.interceptors.response.use(
  /**
   * NHÁNH 1: Xử lý Status thành công (200 - 299)
   * Tham số nhận vào là đối tượng `response`
   */
  (response) => {
    // Bạn có thể bóc tách sẵn data ở đây để lúc gọi API đỡ phải .data nhiều lần
    // Ví dụ: thay vì nhận cả cụm, bạn chỉ trả về data sạch từ server
    return response.data;
  },

  /**
   * NHÁNH 2: Xử lý Status lỗi (400, 401, 403, 500...) hoặc lỗi mạng
   * Tham số nhận vào là đối tượng `error`
   */
  (error) => {
    // 1. Kiểm tra xem lỗi này có phản hồi từ server không (có status code lỗi)
    if (error.response) {
      const status = error.response.status;
      const serverData = error.response.data; // Dữ liệu lỗi do backend trả về

      switch (status) {
        case 401:
          console.error("Lỗi 401: Chưa đăng nhập hoặc token hết hạn!");
          // Có thể thực hiện logic Refresh Token hoặc Redirect sang trang Login ở đây
          break;
        case 403:
          console.error("Lỗi 403: Bạn không có quyền truy cập!");
          break;
        case 500:
          console.error("Lỗi 500: Hệ thống phía Server gặp sự cố!");
          break;
        default:
          console.error(`Lỗi hệ thống: ${status}`, serverData);
      }
    }
    // 2. Lỗi do không gửi được request (mất mạng, server sập hoàn toàn)
    else if (error.request) {
      console.error(
        "Không nhận được phản hồi từ server. Vui lòng kiểm tra kết nối mạng!",
      );
    }
    // 3. Lỗi cấu hình code phát sinh trước khi gửi request
    else {
      console.error("Lỗi cấu hình Axios:", error.message);
    }

    // QUAN TRỌNG: Bạn BẮT BUỘC phải return Promise.reject(error)
    // để các hàm gọi API bên ngoài (try...catch hoặc .catch) có thể nhận biết được là có lỗi xảy ra.
    return Promise.reject(error);
  },
);
```

- Mã 200 rơi vào hàm số 1 (response). Bạn dùng response.status để xem code (nếu cần) và response.data để lấy dữ liệu.
- Mã Lỗi rơi vào hàm số 2 (error). Bạn phải truy cập sâu vào bên trong qua error.response.status và error.response.data để biết backend đang báo lỗi gì cụ thể.

### 💡Lợi ích cho Frontend

Với cấu hình trả về thành công thì việc có một class định sẵn [Xem mục 1] sẽ giúp FE làm việc dễ hơn vì đã có cấu trúc từ đầu.

Lưu ý: Vì hệ thống backend dùng chuẩn O2Auth để hỗ trợ debug cũng như lấy access_token từ response login và refresh do đó với 2 API này sẽ không trả về theo class Response Model mà là dạng raw như:

```json
{
  "access_token": "gay_lord_access_token",
  "token_type": "bearer"
}
```

Ta hình dung được nếu thành công thì cấu trúc của response sẽ là:

```js
{
  status: 200,
  statusText: "OK",
  headers: { "content-type": "application/json", ... },
  config: { ... },        // thông tin request đã gửi (url, method, headers...)
  request: XMLHttpRequest, // object request gốc (hiếm khi cần dùng tới)
  data: {                  // <-- đây mới là BODY thật sự bạn cần
    success: true,
    message: "🎉 Lấy thông tin Admin hiện tại thành công!",
    data: {
      id: 1,
      fullname: "...",
      email: "...",
      role: "ADMIN"
    }
  }
}
```

- Vói cấu hình trả về App Exception thì hơi phức tạp 1 chút, thường thì khi gửi response sẽ có 2 phần:

```js
HTTP/1.1 401 Unauthorized          ← status line (KHÔNG nằm trong JSON)
Content-Type: application/json
Content-Length: 123

{                                   ← đây mới là "body" — phần bạn viết trong content={...}
  "success": false,
  "error_code": "WRONG_PASSWORD",
  "message": "❌ Email hoặc mật khẩu chưa chính xác...",
  "data": null
}
```

Thư viện status của fastAPI sẽ biến đổi biến mình chọn thành dòng status line và qua đó bên FE khi nhận được response với Axios sẽ đọc status line đầu tiên và biết được loại lỗi. Từ đó ta sẽ hình dung được cấu trúc response khi FE nhận được như sau:

```js
{
  message: "Request failed with status code 401",  // message chung của axios, không phải của bạn
  code: "ERR_BAD_REQUEST",
  config: { ... },
  request: XMLHttpRequest,
  response: {                 // <-- object này tồn tại NẾU server có trả về response (không phải lỗi mạng)
    status: 401,
    statusText: "Unauthorized",
    headers: { ... },
    data: {                   // <-- body lỗi thật sự, đúng shape từ exception_handler
      success: false,
      error_code: "WRONG_PASSWORD",
      message: "❌ Email hoặc mật khẩu chưa chính xác. Vui lòng kiếm tra lại!",
      data: null
    }
  }
}
```

Nhờ áp dụng cấu trúc này, phía Frontend (React + Axios) chỉ cần thiết lập Interceptor response (Xử lý khi nhận response - minh họa nhé).
Xem chi tiết hơn ở file axiosConfig trong thư mục service của Frontend.

```javascript
// Riêng lỗi 401 cần gọi API cấp access_token thì để sau

// Mã giả minh họa cách Frontend xử lý
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
