from fastapi import status
from pydantic import EmailStr
from sqlalchemy.orm import Session
from app.models.models import User, RoleType
from app.schemas.user import UserUpdateInfo, UserResponse, UserUpdatePassword
from app.core.exception import AppException
from app.schemas import response as schemas_response
from app.core.config import settings

# Get user theo id: 
# Cập nhật email, username: 
# Cập nhật Password:
# Get user theo email: Hỗ trợ tìm kiếm user khi đăng nhập 

def get_user(db: Session, user_id: int) -> User:
    """
    Hàm trả về object user dựa trên id truyền vào. Tự động trả về lỗi nếu không tìm thấy.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise AppException(
            status_code = status.HTTP_404_NOT_FOUND,
            error_code="USER_NOT_FOUND",
            message="User không tồn tại trong hệ thống!"
        )
    return db_user

def get_user_by_email(db: Session, user_email: EmailStr) -> User:
    """
    Hàm trả về object user dựa trên email truyền vào. Hỗ trợ tìm kiếm user khi đăng nhập
    """
    db_user = db.query(User).filter(User.email == user_email).first()
    if not db_user:
        raise AppException(
            status_code = status.HTTP_404_NOT_FOUND,
            error_code="USER_NOT_FOUND",
            message="User không tồn tại trong hệ thống!"
        )
    return db_user

def update_username_email(db:Session, target_user_id: int, update_data: UserUpdateInfo):
    """
    Hàm này nhận vào db_user (Object lấy từ DB) và update_data (Schema đã qua Pydantic).
    Chỉ làm đúng việc là gán đè data mới lên data cũ và lưu lại.
    1. Biến bản thân object pydantic update_data -> dict để dễ thao tác, tách các cặp key - value
    2. Sử dụng excluse_unset = True chỉ để nhận cập nhật giá trị khác với mặc định ( tức là user không gửi lên), tránh mất oan dữ liệu. 
     - lệnh setattr(db_user, key, value) thay giá trị mới vào Object User cũ một cách tự động.
    3. Lưu xuống DB
    """
    target_user = get_user(db=db, user_id=target_user_id)

    update_data_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_data_dict.items():
        setattr(target_user, key, value)
    
    db.add(target_user)
    db.commit()
    db.refresh(target_user)

    return target_user

def update_password(db: Session, target_user_id: int, new_hashed_password: str):
    """Hàm này nhận chuỗi pass đã được hash từ bên service và cập nhật vào user được chỉ định trong đầu vào!"""
    target_user = get_user(db=db, user_id=target_user_id)
    target_user.password = new_hashed_password

    db.add(target_user)
    db.commit()
    db.refresh(target_user)

    return target_user



