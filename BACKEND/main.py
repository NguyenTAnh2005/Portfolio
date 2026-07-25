# Handling Error 
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.exception import AppException

# CORS
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware

# Import router 
from app.routers import auth, user, info, timeline

app = FastAPI()

# =========== Cấu hình CORS =================================================================
# CORS dùng để cho phép Frontend gọi API từ Backend khi Frontend và Backend chạy khác origin.
# Origin gồm: protocol + domain + port
origins = [
    # Lấy URL của Frontend từ file cấu hình / .env
    settings.FRONTEND_URL,
]
# Thêm CORSMiddleware vào FastAPI app
# Middleware này sẽ xử lý việc cho phép hoặc chặn request từ Frontend
app.add_middleware(
    CORSMiddleware,

    # Chỉ cho phép những origin nằm trong danh sách origins được gọi API
    allow_origins=origins,
    # Cho phép gửi thông tin xác thực như cookie, token, Authorization header
    allow_credentials=True,
    # Cho phép tất cả HTTP methods: GET, POST, PUT, DELETE, PATCH,...
    allow_methods=["*"],
    # Cho phép tất cả headers từ phía Frontend gửi lên
    # Ví dụ: Content-Type, Authorization,...
    allow_headers=["*"]
)
# ========================================================================================

# Thêm Router các API vào 
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(info.router)
app.include_router(timeline.router)


# Endpoint giúp đóng gói Object được trả về là App Exception ( Từ 1 object --> JSON - ngôn ngữ giao tiếp chung giữa Front và Back)
@app.exception_handler(AppException)
async def app_exeption_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code = exc.status_code,
        content={
            "success": False,
            "error_code": exc.error_code,
            "message": exc.message,
            "data": None
        }
    )
# ===========================================================


@app.get("/")
def read_root():
    return{"message":"Welcome to Backend of Portfolio!"}
