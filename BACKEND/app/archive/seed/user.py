from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.models import User, RoleType
from BACKEND.app.core.jwt_token import get_password_hash

def seed_user(db: Session):
    """ Tạo tài khoản Amdin đầu tiên!"""
    email = settings.ST_ADMIN_EMAIL
    password = settings.ST_ADMIN_PASSWORD
    if not email or not password:
        print("⚠️ Lỗi! Không tìm thấy mật khẩu hoặc email trong pydantic settings. Vui lòng kiếm tra lại file .env!")
        return
    user = User(
        email = email,
        username = "Anh Admin",
        password = get_password_hash(password=password),
        role = RoleType.ADMIN
    )
    db.add(user)
    print("✅ Dữ liệu hàm seed_user đã sẵn sàng!")

