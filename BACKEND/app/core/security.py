# Mã hóa mật khẩu 
from passlib.context import CryptContext
from datetime import datetime

# Tạo JWT
from datetime import timedelta, timezone
from jose import jwt

# Giải mã JWT
from app.core.exception import AppException
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from app.db_connection import connect_db
from app.models import models
from app.schemas.auth import TokenPayload

# Import cần thiết khác 
from typing import Optional
from app.core.config import settings



# ==========================================
# 1. MÃ HÓA MẬT KHẨU (PASSWORD HASHING)
# ==========================================
# Cấu hình thuật toán bcrypt để băm pass 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

def get_password_hash(password: str)-> str:
    """ Băm mật khẩu gốc thành chuỗi mã hóa để lưu vào DB. """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """ So sánh mật khẩu người dùng nhập với mật khẩu đã băm trong DB. """
    return pwd_context.verify(plain_password, hashed_password)

# ==========================================
# 2. TẠO ACCESS TOKEN (JWT)
# ==========================================
ALGORITHM = "HS256"
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    TẠO CHUỖI JWT.
    - data: Nội dung muốn nhét vào token ( thường sẽ là {"sub":email, "data":user_id})
    - expires_delta: Thời gian sống của token ( Nếu không truyền thì lấy mặc định từ .env)
    """
    # Tạo một bản sao data tránh làm thay đổi bản gốc
    to_encode = data.copy()
    # Tính toán thời gian hết hạn 
    if expires_delta is None:
        # Nếu không truyền thì lấy từ pydantic setting
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta
    # Nhét thêm trường expire vào payload của token 
    to_encode.update({"exp": expire})

    # Dùng hàm của thư viện jose mã hóa toàn bộ thành một chuỗi JWT
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

# ==========================================
# 3. GIẢI MÃ JWT VÀ KIỂM TRA QUYỀN 
# ==========================================

# Cho biết đường dẫn API trả về Access Token để có thể sử dụng trên Swagger UI
token_url = settings.BASE_API_URL+"/auth/login"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=token_url)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(connect_db)) -> models.User:
    """Hàm giải mã token, trả về object user hiện tại."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        # Ép thông tin payload vào một khuôn schemas để tránh lộ nhiều thông tin cũng như xác thực cấu trúc
        token_data = TokenPayload(**payload)
        # Lấy thông tin từ payload một cách an toàn hơn nhờ đã ép theo khuôn schemas
        user_id = token_data.data
        email = token_data.sub

        if user_id is None or email is None:
            raise AppException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                error_code="INVALID_TOKEN",
                message="Token không hợp lệ hoặc đã bị thay đổi!"
            )
    except JWTError:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="TOKEN_EXPIRED",
            message="Phiên đăng nhập đã kết thúc, vui lòng đăng nhập lại!"
        )
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="USER_NOT_FOUND",
            message="Tài khoản không tồn tại trong hệ thống!"
        )
    return user

def get_current_admin( current_user: models.User = Depends(get_current_user)):
    """Hàm kiểm tra quyền Admin."""
    if current_user.role != models.RoleType.ADMIN:
        raise AppException(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN_ACCESS",
            message="Bạn không có quyền quản trị viên để thực hiện hành động này!"
        )
    return current_user